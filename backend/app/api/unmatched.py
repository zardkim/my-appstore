"""
불일치 항목 관리 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.dependencies import get_current_admin_user
from app.models.unmatched_item import UnmatchedItem
from app.models.product import Product
from app.models.metadata_cache import MetadataCache
from app.schemas.unmatched import (
    UnmatchedItemResponse,
    UnmatchedListResponse,
    ApproveRequest,
    ManualMetadataRequest,
    SearchRequest
)
from app.core.redis_cache import invalidate_cache
from app.core.ai_metadata import AIMetadataGeneratorV2 as AIMetadataGenerator
from app.core.confidence import calculate_confidence_score, normalize_software_name
from app.api.config import load_config

router = APIRouter()


@router.get("/", response_model=UnmatchedListResponse)
async def get_unmatched_items(
    status: Optional[str] = Query(None, description="필터: pending, approved, manual, ignored"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """
    불일치 항목 목록 조회

    Args:
        status: 상태 필터
        skip: 건너뛸 항목 수
        limit: 조회할 최대 항목 수
    """
    query = db.query(UnmatchedItem)

    # 상태 필터링
    if status:
        query = query.filter(UnmatchedItem.status == status)

    # 총 개수
    total = query.count()

    # 페이지네이션
    items = query.order_by(UnmatchedItem.created_at.desc()).offset(skip).limit(limit).all()

    return UnmatchedListResponse(
        total=total,
        items=items
    )


@router.get("/{item_id}", response_model=UnmatchedItemResponse)
async def get_unmatched_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """불일치 항목 상세 조회"""
    item = db.query(UnmatchedItem).filter(UnmatchedItem.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="항목을 찾을 수 없습니다.")

    return item


@router.post("/{item_id}/approve")
async def approve_suggestion(
    item_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """
    AI 제안 승인 및 Product 등록

    제안된 메타데이터로 Product를 생성하고 불일치 항목 상태를 'approved'로 변경
    """
    item = db.query(UnmatchedItem).filter(UnmatchedItem.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="항목을 찾을 수 없습니다.")

    if not item.suggested_metadata:
        raise HTTPException(status_code=400, detail="제안된 메타데이터가 없습니다.")

    try:
        metadata = item.suggested_metadata

        # 필수 필드 검증
        if not metadata.get('title'):
            raise HTTPException(status_code=400, detail="제품명이 없습니다.")

        # 같은 folder_path로 Product가 이미 있는지 확인
        existing_product = db.query(Product).filter(Product.folder_path == item.folder_path).first()
        if existing_product:
            raise HTTPException(status_code=400, detail=f"이미 등록된 제품입니다: {existing_product.title}")

        # Product 생성
        product = Product(
            title=metadata.get('title'),
            description=metadata.get('description'),
            vendor=metadata.get('vendor'),
            category=metadata.get('category'),
            icon_url=metadata.get('icon_url', ''),
            folder_path=item.folder_path
        )

        db.add(product)

        # 불일치 항목 상태 업데이트
        item.status = "approved"
        item.reviewed_at = datetime.utcnow()
        item.reviewed_by = current_user.id

        # 메타데이터 캐시 저장
        normalized_name = normalize_software_name(item.parsed_name or item.file_name)
        cache = MetadataCache(
            software_name=normalized_name,
            metadata_json=metadata,
            confidence_score=item.confidence_score,
            source="ai"
        )
        db.add(cache)

        db.commit()

        # 캐시 무효화 (새 제품 생성됨)
        invalidate_cache([
            "products_list:*",
            "products_recent:*",
            "products_by_category:*",
            "search_suggestions:*",
            "stats_overview:*",
            "stats_categories:*"
        ])

        return {
            "success": True,
            "message": "승인되었습니다.",
            "product_id": product.id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"승인 중 오류 발생: {str(e)}")


@router.post("/{item_id}/manual")
async def save_manual_metadata(
    item_id: int,
    request: ManualMetadataRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """
    수동 입력 메타데이터 저장 및 Product 등록
    """
    item = db.query(UnmatchedItem).filter(UnmatchedItem.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="항목을 찾을 수 없습니다.")

    try:
        # 수동 메타데이터 구성
        manual_metadata = {
            "title": request.title,
            "vendor": request.vendor,
            "category": request.category,
            "description": request.description,
            "official_website": request.official_website,
            "icon_url": request.icon_url or ""
        }

        # Product 생성
        product = Product(
            title=request.title,
            description=request.description,
            vendor=request.vendor,
            category=request.category,
            icon_url=request.icon_url or "",
            folder_path=item.folder_path
        )

        db.add(product)

        # 불일치 항목 업데이트
        item.manual_metadata = manual_metadata
        item.status = "manual"
        item.reviewed_at = datetime.utcnow()
        item.reviewed_by = current_user.id

        # 메타데이터 캐시 저장 (수동 입력은 높은 정확도로 저장)
        normalized_name = normalize_software_name(item.parsed_name or item.file_name)
        cache = MetadataCache(
            software_name=normalized_name,
            metadata_json=manual_metadata,
            confidence_score=1.0,  # 수동 입력은 100% 신뢰
            source="manual"
        )
        db.add(cache)

        db.commit()

        # 캐시 무효화 (새 제품 생성됨)
        invalidate_cache([
            "products_list:*",
            "products_recent:*",
            "products_by_category:*",
            "search_suggestions:*",
            "stats_overview:*",
            "stats_categories:*"
        ])

        return {
            "success": True,
            "message": "수동 메타데이터가 저장되었습니다.",
            "product_id": product.id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"저장 중 오류 발생: {str(e)}")


@router.post("/{item_id}/search")
async def search_metadata(
    item_id: int,
    request: SearchRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """
    수동 검색 (AI 재쿼리)

    사용자가 다른 소프트웨어 이름으로 다시 검색
    """
    item = db.query(UnmatchedItem).filter(UnmatchedItem.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="항목을 찾을 수 없습니다.")

    try:
        # 설정 로드
        config = load_config()
        metadata_config = config.get('metadata', {})

        api_key = metadata_config.get('apiKey', '')
        ai_model = metadata_config.get('aiModel', 'gpt-4o-mini')

        if not api_key or not api_key.strip():
            raise HTTPException(
                status_code=400,
                detail="OpenAI API 키가 설정되지 않았습니다."
            )

        # AI 메타데이터 생성
        generator = AIMetadataGenerator()
        generator.api_key = api_key
        generator.model = ai_model

        if request.collect_extended:
            from app.api.metadata import generate_extended_metadata
            metadata = await generate_extended_metadata(
                generator,
                request.software_name,
                metadata_config
            )
        else:
            metadata = await generator.generate_metadata(request.software_name)

        # 정확도 계산
        parsed_info = {'software_name': request.software_name}
        confidence_score = calculate_confidence_score(metadata, parsed_info)

        # 새로운 제안으로 업데이트
        item.suggested_metadata = metadata
        item.confidence_score = confidence_score
        item.parsed_name = request.software_name

        db.commit()

        return {
            "success": True,
            "metadata": metadata,
            "confidence_score": confidence_score,
            "confidence_percentage": round(confidence_score * 100, 1)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"검색 중 오류 발생: {str(e)}")


@router.delete("/{item_id}")
async def ignore_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """불일치 항목 무시"""
    item = db.query(UnmatchedItem).filter(UnmatchedItem.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="항목을 찾을 수 없습니다.")

    try:
        item.status = "ignored"
        item.reviewed_at = datetime.utcnow()
        item.reviewed_by = current_user.id

        db.commit()

        return {
            "success": True,
            "message": "항목이 무시되었습니다."
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"무시 처리 중 오류 발생: {str(e)}")


@router.get("/stats/summary")
async def get_unmatched_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """불일치 항목 통계"""
    total = db.query(UnmatchedItem).count()
    pending = db.query(UnmatchedItem).filter(UnmatchedItem.status == "pending").count()
    approved = db.query(UnmatchedItem).filter(UnmatchedItem.status == "approved").count()
    manual = db.query(UnmatchedItem).filter(UnmatchedItem.status == "manual").count()
    ignored = db.query(UnmatchedItem).filter(UnmatchedItem.status == "ignored").count()

    return {
        "total": total,
        "pending": pending,
        "approved": approved,
        "manual": manual,
        "ignored": ignored
    }
