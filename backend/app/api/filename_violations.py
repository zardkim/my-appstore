"""
파일명 규칙 위반 항목 관리 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime
import os
from pathlib import Path

from app.database import get_db
from app.models.filename_violation import FilenameViolation
from app.models.version import Version
from app.models.product import Product
from app.models.user import User
from app.dependencies import get_current_admin_user
from app.core.ai_metadata import AIMetadataGeneratorV2 as AIMetadataGenerator
from app.core.parser import FilenameParser
from app.api.config import load_config
from app.core.redis_cache import invalidate_cache
from app.core.auto_matcher import match_violations_to_products


router = APIRouter(prefix="/api/filename-violations", tags=["filename-violations"])


class FilenameViolationResponse(BaseModel):
    id: int
    folder_path: str
    file_name: str
    violation_type: str
    violation_details: Optional[str] = None
    suggestion: Optional[str] = None
    created_at: Optional[datetime] = None
    is_resolved: bool
    product_id: Optional[int] = None  # 매칭된 Product ID (재스캔 시 중복 방지용)
    version_id: Optional[int] = None  # 매칭된 Version ID (재스캔 시 중복 방지용)

    class Config:
        from_attributes = True


class RenameFileRequest(BaseModel):
    new_filename: str


class BatchRenameRequest(BaseModel):
    violation_ids: List[int]


class CreateProductWithMetadataRequest(BaseModel):
    metadata: Dict


@router.get("/", response_model=List[FilenameViolationResponse])
async def get_violations(
    resolved: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    파일명 규칙 위반 목록 조회 (관리자 전용)

    Args:
        resolved: True면 해결된 항목만, False면 미해결 항목만 조회
        db: Database session
        current_user: Current admin user

    Returns:
        List of filename violations
    """
    violations = db.query(FilenameViolation).filter(
        FilenameViolation.is_resolved == resolved
    ).order_by(FilenameViolation.created_at.desc()).all()

    return violations


@router.get("/stats", response_model=Dict)
async def get_violation_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    파일명 규칙 위반 통계 조회 (관리자 전용)
    미해결 항목만 집계 (목록 표시와 일치)

    Returns:
        {
            "total": int,
            "scanned": int,
            "mismatched": int,
            "by_type": {
                "underscore_overuse": int,
                "bracket_usage": int,
                ...
            }
        }
    """
    # 미해결 항목만 집계 (목록 표시와 일치하도록)
    base_query = db.query(FilenameViolation).filter(
        FilenameViolation.is_resolved == False
    )

    total = base_query.count()

    # 스캔된 항목 (정규식에 맞는 항목)
    scanned = base_query.filter(
        FilenameViolation.violation_type == "scanned"
    ).count()

    # 불일치 항목 (비매칭 항목)
    mismatched = base_query.filter(
        FilenameViolation.violation_type != "scanned"
    ).count()

    # 위반 유형별 통계
    violations = db.query(FilenameViolation).filter(
        FilenameViolation.is_resolved == False,
        FilenameViolation.violation_type != "scanned"
    ).all()

    by_type = {}
    for v in violations:
        by_type[v.violation_type] = by_type.get(v.violation_type, 0) + 1

    return {
        "total": total,
        "scanned": scanned,
        "mismatched": mismatched,
        "by_type": by_type
    }


@router.put("/{violation_id}/resolve")
async def resolve_violation(
    violation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    파일명 규칙 위반 항목을 해결됨으로 표시 (관리자 전용)

    Args:
        violation_id: Violation ID
        db: Database session
        current_user: Current admin user

    Returns:
        Updated violation
    """
    violation = db.query(FilenameViolation).filter(
        FilenameViolation.id == violation_id
    ).first()

    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")

    violation.is_resolved = True
    db.commit()
    db.refresh(violation)

    return {"message": "Violation resolved", "violation_id": violation_id}


@router.delete("/{violation_id}")
async def delete_violation(
    violation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    파일명 규칙 위반 항목 삭제 (관리자 전용)

    Args:
        violation_id: Violation ID
        db: Database session
        current_user: Current admin user

    Returns:
        Success message
    """
    violation = db.query(FilenameViolation).filter(
        FilenameViolation.id == violation_id
    ).first()

    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")

    db.delete(violation)
    db.commit()

    return {"message": "Violation deleted", "violation_id": violation_id}


@router.delete("/")
async def clear_violations(
    resolved_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    파일명 규칙 위반 항목 일괄 삭제 (관리자 전용)

    Args:
        resolved_only: True면 해결된 항목만 삭제, False면 모든 항목 삭제
        db: Database session
        current_user: Current admin user

    Returns:
        Deletion result
    """
    query = db.query(FilenameViolation)

    if resolved_only:
        query = query.filter(FilenameViolation.is_resolved == True)

    deleted_count = query.delete()
    db.commit()

    return {
        "message": f"Deleted {deleted_count} violations",
        "deleted_count": deleted_count
    }


@router.put("/{violation_id}/rename")
async def rename_file(
    violation_id: int,
    request: RenameFileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    파일명 변경 (관리자 전용)

    실제 파일 시스템의 파일명을 변경하고, DB의 Version 레코드도 업데이트합니다.

    Args:
        violation_id: Violation ID
        request: 새로운 파일명
        db: Database session
        current_user: Current admin user

    Returns:
        Success message with new filename
    """
    # 위반 항목 조회
    violation = db.query(FilenameViolation).filter(
        FilenameViolation.id == violation_id
    ).first()

    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")

    # 기존 파일 경로
    old_file_path = os.path.join(violation.folder_path, violation.file_name)
    new_file_path = os.path.join(violation.folder_path, request.new_filename)

    # 파일 존재 여부 확인
    if not os.path.exists(old_file_path):
        raise HTTPException(
            status_code=404,
            detail=f"파일을 찾을 수 없습니다: {old_file_path}"
        )

    # 새 파일명이 이미 존재하는지 확인
    if os.path.exists(new_file_path):
        raise HTTPException(
            status_code=409,
            detail=f"동일한 이름의 파일이 이미 존재합니다: {request.new_filename}"
        )

    try:
        # 파일명 변경
        os.rename(old_file_path, new_file_path)

        # DB의 Version 레코드 업데이트
        version = db.query(Version).filter(
            Version.file_path == old_file_path
        ).first()

        product_id = None
        if version:
            version.file_name = request.new_filename
            version.file_path = new_file_path
            product_id = version.product_id

        # 위반 항목을 해결됨으로 표시
        violation.is_resolved = True

        db.commit()

        return {
            "message": "파일명이 성공적으로 변경되었습니다",
            "old_filename": violation.file_name,
            "new_filename": request.new_filename,
            "file_path": new_file_path,
            "product_id": product_id  # AI 매칭을 위해 product_id 반환
        }

    except PermissionError:
        db.rollback()
        raise HTTPException(
            status_code=403,
            detail="파일명을 변경할 권한이 없습니다"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"파일명 변경 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/batch-rename")
async def batch_rename_files(
    request: BatchRenameRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    제안된 파일명으로 일괄 변경 (관리자 전용)

    Args:
        request: 변경할 violation ID 목록
        db: Database session
        current_user: Current admin user

    Returns:
        성공/실패 결과
    """
    results = {
        "success": [],
        "failed": []
    }

    for violation_id in request.violation_ids:
        # 위반 항목 조회
        violation = db.query(FilenameViolation).filter(
            FilenameViolation.id == violation_id
        ).first()

        if not violation:
            results["failed"].append({
                "id": violation_id,
                "error": "Violation not found"
            })
            continue

        if not violation.suggestion:
            results["failed"].append({
                "id": violation_id,
                "filename": violation.file_name,
                "error": "제안된 파일명이 없습니다"
            })
            continue

        # 기존 파일 경로
        old_file_path = os.path.join(violation.folder_path, violation.file_name)
        new_file_path = os.path.join(violation.folder_path, violation.suggestion)

        # 파일 존재 여부 확인
        if not os.path.exists(old_file_path):
            results["failed"].append({
                "id": violation_id,
                "filename": violation.file_name,
                "error": f"파일을 찾을 수 없습니다: {old_file_path}"
            })
            continue

        # 새 파일명이 이미 존재하는지 확인
        if os.path.exists(new_file_path):
            results["failed"].append({
                "id": violation_id,
                "filename": violation.file_name,
                "error": f"동일한 이름의 파일이 이미 존재합니다: {violation.suggestion}"
            })
            continue

        try:
            # 파일명 변경
            os.rename(old_file_path, new_file_path)

            # DB의 Version 레코드 업데이트
            version = db.query(Version).filter(
                Version.file_path == old_file_path
            ).first()

            product_id = None
            if version:
                version.file_name = violation.suggestion
                version.file_path = new_file_path
                product_id = version.product_id

            # 위반 항목을 해결됨으로 표시
            violation.is_resolved = True

            db.commit()

            results["success"].append({
                "id": violation_id,
                "old_filename": violation.file_name,
                "new_filename": violation.suggestion,
                "product_id": product_id  # AI 매칭을 위해 product_id 반환
            })

        except PermissionError:
            db.rollback()
            results["failed"].append({
                "id": violation_id,
                "filename": violation.file_name,
                "error": "파일명을 변경할 권한이 없습니다"
            })
        except Exception as e:
            db.rollback()
            results["failed"].append({
                "id": violation_id,
                "filename": violation.file_name,
                "error": str(e)
            })

    return {
        "message": f"성공: {len(results['success'])}개, 실패: {len(results['failed'])}개",
        "results": results
    }


@router.post("/{violation_id}/create-product")
async def create_product_from_violation(
    violation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    스캔된 파일로부터 Product 생성 (AI 매칭)
    통합 매칭 로직(auto_matcher.py) 사용

    Args:
        violation_id: Violation ID
        db: Database session
        current_user: Current admin user

    Returns:
        Created product with ID
    """
    # 위반 항목 조회
    violation = db.query(FilenameViolation).filter(
        FilenameViolation.id == violation_id
    ).first()

    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")

    # 설정 로드
    config = load_config()
    metadata_config = config.get('metadata', {})

    use_ai = metadata_config.get('useAI', False)
    ai_provider = metadata_config.get('aiProvider', 'openai')
    ai_model = metadata_config.get('aiModel', 'gpt-4o-mini')

    if not use_ai:
        raise HTTPException(
            status_code=400,
            detail="AI 메타데이터 생성이 비활성화되어 있습니다. 설정에서 활성화해주세요."
        )

    # AI Provider에 따라 적절한 API key 가져오기
    if ai_provider == 'gemini':
        api_key = metadata_config.get('geminiApiKey', '')
        if not api_key or not api_key.strip():
            raise HTTPException(
                status_code=400,
                detail="Gemini API 키가 설정되지 않았습니다. 설정 페이지에서 API 키를 입력해주세요."
            )
    elif ai_provider == 'openai':
        api_key = metadata_config.get('openaiApiKey', '')
        if not api_key or not api_key.strip():
            raise HTTPException(
                status_code=400,
                detail="OpenAI API 키가 설정되지 않았습니다. 설정 페이지에서 API 키를 입력해주세요."
            )
    else:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 AI Provider입니다: {ai_provider}"
        )

    try:
        # 통합 매칭 로직 호출 (수동 매칭 모드: 명확성 검사 건너뜀, AI가 메타데이터 생성)
        results = await match_violations_to_products(
            db=db,
            violations=[violation],
            ai_provider=ai_provider,
            ai_model=ai_model,
            api_key=api_key,
            skip_clarity_check=True,  # 수동 매칭: 명확성 검사 건너뜀
            provided_metadata=None  # AI가 메타데이터 생성
        )

        if results["matched"] > 0 and results["products"]:
            product_info = results["products"][0]
            return {
                "success": True,
                "message": "Product가 성공적으로 생성되었습니다.",
                "product_id": product_info["id"],
                "violation_id": violation_id,
                "product": product_info
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Product 생성 실패: {', '.join(results['errors']) if results['errors'] else 'Unknown error'}"
            )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Product 생성 중 오류 발생: {str(e)}"
        )


@router.post("/{violation_id}/create-product-with-metadata")
async def create_product_from_violation_with_metadata(
    violation_id: int,
    request: CreateProductWithMetadataRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    스캔된 파일로부터 AI 메타데이터와 함께 Product 생성
    통합 매칭 로직(auto_matcher.py) 사용

    Args:
        violation_id: Violation ID
        request: Request body with metadata
        db: Database session
        current_user: Current admin user

    Returns:
        Created product with ID
    """
    # 위반 항목 조회
    violation = db.query(FilenameViolation).filter(
        FilenameViolation.id == violation_id
    ).first()

    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")

    metadata = request.metadata

    # 설정 로드 (API key는 필요 없지만 provider와 model 정보는 필요)
    config = load_config()
    metadata_config = config.get('metadata', {})
    ai_provider = metadata_config.get('aiProvider', 'gemini')
    ai_model = metadata_config.get('aiModel', 'gemini-2.5-flash')

    try:
        # 통합 매칭 로직 호출 (수동 매칭 모드: 사용자 제공 메타데이터 사용)
        results = await match_violations_to_products(
            db=db,
            violations=[violation],
            ai_provider=ai_provider,
            ai_model=ai_model,
            api_key="",  # 사용자 제공 메타데이터 사용 시 API key 불필요
            skip_clarity_check=True,  # 수동 매칭: 명확성 검사 건너뜀
            provided_metadata=metadata  # 사용자가 검토한 메타데이터 사용
        )

        if results["matched"] > 0 and results["products"]:
            product_info = results["products"][0]
            return {
                "success": True,
                "message": "Product가 성공적으로 생성되었습니다.",
                "product_id": product_info["id"],
                "violation_id": violation_id,
                "product": product_info
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Product 생성 실패: {', '.join(results['errors']) if results['errors'] else 'Unknown error'}"
            )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Product 생성 중 오류 발생: {str(e)}"
        )
