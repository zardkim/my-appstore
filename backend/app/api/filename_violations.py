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
    total = db.query(FilenameViolation).count()

    # 스캔된 항목 (정규식에 맞는 항목)
    scanned = db.query(FilenameViolation).filter(
        FilenameViolation.violation_type == "scanned"
    ).count()

    # 불일치 항목 (비매칭 항목)
    mismatched = db.query(FilenameViolation).filter(
        FilenameViolation.violation_type != "scanned"
    ).count()

    # 위반 유형별 통계
    violations = db.query(FilenameViolation).filter(
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

    api_key = metadata_config.get('apiKey', '')
    ai_model = metadata_config.get('aiModel', 'gpt-4o-mini')
    use_ai = metadata_config.get('useAI', False)

    if not use_ai:
        raise HTTPException(
            status_code=400,
            detail="AI 메타데이터 생성이 비활성화되어 있습니다. 설정에서 활성화해주세요."
        )

    if not api_key or not api_key.strip():
        raise HTTPException(
            status_code=400,
            detail="OpenAI API 키가 설정되지 않았습니다."
        )

    try:
        # 이미 Product가 있는지 확인
        existing_product = db.query(Product).filter(
            Product.folder_path == violation.folder_path
        ).first()

        if existing_product:
            # Product가 이미 있으면 Version만 생성
            product = existing_product
        else:
            # Product 생성: folder_path에서 폴더 이름 추출
            folder_name = os.path.basename(violation.folder_path)
            parser = FilenameParser()
            parsed_info = parser.parse_filename(folder_name)
            software_name = parsed_info.get('software_name', folder_name)

            # 포터블 여부 감지 (파일명에서)
            is_portable = False
            filename_lower = violation.file_name.lower()
            if 'portable' in filename_lower or '무설치' in violation.file_name:
                is_portable = True

            # AI 메타데이터 생성
            generator = AIMetadataGenerator()
            generator.api_key = api_key
            generator.model = ai_model

            metadata = await generator.generate_metadata(software_name)

            # Product 생성
            product = Product(
                title=metadata.get('title', software_name),
                description=metadata.get('description', f"{software_name} 소프트웨어"),
                vendor=metadata.get('vendor', ''),
                category=metadata.get('category', 'Utility'),
                icon_url=metadata.get('icon_url', ''),
                folder_path=violation.folder_path,
                is_portable=is_portable
            )

            db.add(product)
            db.flush()  # Get product ID

        # Version 생성
        file_path_str = os.path.join(violation.folder_path, violation.file_name)

        # 이미 Version이 있는지 확인
        existing_version = db.query(Version).filter(
            Version.file_path == file_path_str
        ).first()

        if not existing_version:
            # Version 생성
            parsed = parser.parse_filename(violation.file_name)
            version_name = parsed.get('version', 'Unknown')

            # 파일 크기 가져오기
            file_size = 0
            if os.path.exists(file_path_str):
                file_size = os.path.getsize(file_path_str)

            version = Version(
                product_id=product.id,
                file_name=violation.file_name,
                file_path=file_path_str,
                file_size=file_size,
                version_name=version_name
            )

            db.add(version)
            db.flush()  # Get version ID

            # Violation에 매칭 정보 저장 (재스캔 시 중복 방지용)
            violation.product_id = product.id
            violation.version_id = version.id
        else:
            # 기존 Version이 있으면 해당 정보 연결
            violation.product_id = existing_version.product_id
            violation.version_id = existing_version.id

        # Violation을 해결됨으로 표시
        violation.is_resolved = True

        db.commit()
        db.refresh(product)

        return {
            "success": True,
            "message": "Product가 성공적으로 생성되었습니다.",
            "product_id": product.id,
            "product": product
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Product 생성 중 오류 발생: {str(e)}"
        )
