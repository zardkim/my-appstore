from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from typing import List, Optional
import os

from app.database import get_db
from app.models.product import Product
from app.models.version import Version
from app.models.scan_history import ScanHistory
from app.models.filename_violation import FilenameViolation
from app.models.setting import Setting
from app.schemas.product import ProductResponse, ProductListResponse, ProductUpdateRequest, VersionUpdateRequest
from app.dependencies import get_current_user, get_current_admin_user
from app.core.ai_metadata import AIMetadataGeneratorV2 as AIMetadataGenerator
from app.core.parser import FilenameParser
from app.api.config import load_config
from app.core.redis_cache import cache_response, invalidate_cache

router = APIRouter()


@router.get("/", response_model=ProductListResponse)
@cache_response(prefix="products_list", ttl=300)
async def get_products(
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    vendor: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = Query("id", regex="^(id|title|category|vendor)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get list of products with advanced filtering and search

    Args:
        skip: Pagination offset
        limit: Number of items per page
        category: Filter by category
        vendor: Filter by vendor
        search: Search in title, description, vendor
        sort_by: Sort field (id, title, category, vendor)
        sort_order: Sort order (asc, desc)
    """
    query = db.query(Product).options(joinedload(Product.versions))

    # 카테고리 필터
    if category:
        query = query.filter(Product.category == category)

    # 제조사 필터
    if vendor:
        query = query.filter(Product.vendor.ilike(f"%{vendor}%"))

    # 검색
    if search:
        search_filter = or_(
            Product.title.ilike(f"%{search}%"),
            Product.subtitle.ilike(f"%{search}%"),
            Product.description.ilike(f"%{search}%"),
            Product.vendor.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)

    # 정렬
    sort_column = getattr(Product, sort_by)
    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    total = query.count()
    products = query.offset(skip).limit(limit).all()

    # 각 버전의 파일 존재 여부 확인
    import os
    for product in products:
        for version in product.versions:
            version.file_exists = os.path.exists(version.file_path) if version.file_path else False

    return {"total": total, "products": products}


@router.get("/recent", response_model=List[ProductResponse])
@cache_response(prefix="products_recent", ttl=60)
async def get_recent_products(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get recently added products"""
    products = db.query(Product).options(joinedload(Product.versions)).order_by(Product.id.desc()).limit(limit).all()
    return products


@router.get("/by-category", response_model=dict)
@cache_response(prefix="products_by_category", ttl=300)
async def get_products_by_category(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get products grouped by category (for Netflix-style display)

    Returns:
        {
            "Graphics": [product1, product2, ...],
            "Office": [product3, product4, ...],
            ...
        }
    """
    categories = ["Graphics", "Office", "Development", "Utility", "Media", "OS", "Security", "Game", "Network"]

    result = {}
    for category in categories:
        products = db.query(Product).options(joinedload(Product.versions)).filter(
            Product.category == category
        ).limit(10).all()

        if products:
            result[category] = [ProductResponse.from_orm(p) for p in products]

    return result


@router.get("/search/suggestions")
@cache_response(prefix="search_suggestions", ttl=300)
async def get_search_suggestions(
    q: str = Query(..., min_length=2),
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get search suggestions (autocomplete)

    Args:
        q: Search query (minimum 2 characters)
        limit: Maximum number of suggestions
    """
    products = db.query(Product.title, Product.id).filter(
        Product.title.ilike(f"%{q}%")
    ).limit(limit).all()

    return [{"id": p.id, "title": p.title} for p in products]


@router.get("/{product_id}", response_model=ProductResponse)
@cache_response(prefix="product_detail", ttl=600)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get single product by ID"""
    product = db.query(Product).options(joinedload(Product.versions)).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # 각 버전의 파일 존재 여부 확인
    import os
    for version in product.versions:
        version.file_exists = os.path.exists(version.file_path) if version.file_path else False

    return product


@router.get("/stats/overview")
@cache_response(prefix="stats_overview", ttl=60)
async def get_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get system statistics"""
    # 완료된 소프트웨어 수 (Product 수)
    total_products = db.query(Product).count()

    # 미완료된 소프트웨어 수 (미해결된 FilenameViolation 항목 수 - 검색된 목록과 동일)
    incomplete_count = db.query(FilenameViolation).filter(
        FilenameViolation.is_resolved == False
    ).count()

    # 카테고리별 통계
    category_stats = db.query(
        Product.category,
        func.count(Product.id).label('count')
    ).group_by(Product.category).all()

    # 마지막 스캔 시간 (Settings에서 가져오기)
    last_scan_setting = db.query(Setting).filter(
        Setting.key == "last_scan_time"
    ).first()

    last_scan_time = None
    if last_scan_setting and last_scan_setting.value:
        last_scan_time = last_scan_setting.value

    return {
        "total_products": total_products,
        "incomplete_count": incomplete_count,
        "category_stats": {stat.category: stat.count for stat in category_stats},
        "last_scan": last_scan_time or "Never"
    }


@router.get("/stats/categories")
@cache_response(prefix="stats_categories", ttl=300)
async def get_category_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get available categories with product counts"""
    stats = db.query(
        Product.category,
        func.count(Product.id).label('count')
    ).group_by(Product.category).all()

    return [
        {"category": stat.category, "count": stat.count}
        for stat in stats
    ]


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    update_data: ProductUpdateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """
    Update product metadata (Admin only)

    Args:
        product_id: Product ID to update
        update_data: Fields to update (all optional)
    """
    # 제품 조회
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # 허용된 카테고리 목록
    ALLOWED_CATEGORIES = [
        "Graphics", "Office", "Development", "Utility", "Media", "OS",
        "Security", "Network", "Mac", "Mobile", "Patch", "Driver",
        "Source", "Backup", "Business", "Engineering",
        "Theme", "Hardware", "Uncategorized"
    ]

    # 업데이트할 필드만 적용
    update_dict = update_data.model_dump(exclude_unset=True)

    # 카테고리 유효성 검증
    if "category" in update_dict and update_dict["category"] is not None:
        if update_dict["category"] not in ALLOWED_CATEGORIES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category. Allowed categories: {', '.join(ALLOWED_CATEGORIES)}"
            )

    # 필수 필드 검증
    if "title" in update_dict and not update_dict["title"]:
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    # patch_links 최대 5개 제한 및 딕셔너리 변환
    if "patch_links" in update_dict and update_dict["patch_links"] is not None:
        if len(update_dict["patch_links"]) > 5:
            raise HTTPException(
                status_code=400,
                detail="Maximum 5 patch links allowed"
            )
        # PatchLink 객체를 딕셔너리로 변환하여 JSON 저장
        update_dict["patch_links"] = [
            link.model_dump() if hasattr(link, 'model_dump') else link
            for link in update_dict["patch_links"]
        ]

    # 업데이트 적용
    for field, value in update_dict.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    # 캐시 무효화
    invalidate_cache([
        "products_list:*",
        "products_recent:*",
        "products_by_category:*",
        "product_detail:*",
        "search_suggestions:*",
        "stats_overview:*",
        "stats_categories:*"
    ])

    return product


@router.put("/{product_id}/versions/{version_id}")
async def update_version(
    product_id: int,
    version_id: int,
    update_data: VersionUpdateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """
    Update version metadata (Admin only)

    Args:
        product_id: Product ID
        version_id: Version ID to update
        update_data: Fields to update (all optional)
    """
    # 버전 조회 및 제품 소속 확인
    version = db.query(Version).filter(
        Version.id == version_id,
        Version.product_id == product_id
    ).first()

    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    # 업데이트할 필드만 적용
    update_dict = update_data.model_dump(exclude_unset=True)

    for field, value in update_dict.items():
        setattr(version, field, value)

    db.commit()
    db.refresh(version)

    # 캐시 무효화 (제품 상세 정보 변경)
    invalidate_cache([
        f"product_detail:*{product_id}*",
        "products_list:*",
        "products_recent:*"
    ])

    return {
        "message": "Version updated successfully",
        "version": {
            "id": version.id,
            "product_id": version.product_id,
            "version_name": version.version_name,
            "file_name": version.file_name,
            "file_path": version.file_path,
            "file_size": version.file_size,
            "release_date": version.release_date.isoformat() if version.release_date else None
        }
    }


@router.post("/{product_id}/regenerate-metadata")
async def regenerate_product_metadata(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """
    Product의 AI 메타데이터 재생성 (Admin only)

    파일명 변경 후 AI로 메타데이터를 다시 생성하여 Product를 업데이트합니다.

    Args:
        product_id: Product ID
        db: Database session
        current_user: Current admin user

    Returns:
        Updated product with new metadata
    """
    # 제품 조회
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

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
        # folder_path에서 폴더 이름 추출 (파서로 소프트웨어 이름 추출)
        folder_name = os.path.basename(product.folder_path)
        parser = FilenameParser()
        parsed_info = parser.parse_filename(folder_name)
        software_name = parsed_info.get('software_name', folder_name)

        # AI 메타데이터 생성
        generator = AIMetadataGenerator()
        generator.api_key = api_key
        generator.model = ai_model

        metadata = await generator.generate_metadata(software_name)

        # Product 업데이트
        if metadata:
            product.title = metadata.get('title', product.title)
            product.description = metadata.get('description', product.description)
            product.vendor = metadata.get('vendor', product.vendor)
            product.category = metadata.get('category', product.category)

            # icon_url이 있고 비어있지 않으면 업데이트
            if metadata.get('icon_url'):
                product.icon_url = metadata.get('icon_url')

        db.commit()
        db.refresh(product)

        # 캐시 무효화
        invalidate_cache([
            "products_list:*",
            "products_recent:*",
            "products_by_category:*",
            "product_detail:*",
            "search_suggestions:*",
            "stats_overview:*",
            "stats_categories:*"
        ])

        return {
            "success": True,
            "message": "메타데이터가 성공적으로 재생성되었습니다.",
            "product": product,
            "metadata": metadata
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"메타데이터 재생성 중 오류 발생: {str(e)}"
        )


@router.post("/cleanup-deleted")
async def cleanup_deleted_files(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """
    삭제된 파일들을 DB에서 정리 (관리자 전용)

    실제로 존재하지 않는 파일의 Version과 Product를 삭제합니다.
    """
    try:
        # 모든 Version 조회
        versions = db.query(Version).all()

        deleted_version_ids = []
        product_ids_to_check = set()

        # 파일이 존재하지 않는 Version 찾기
        for version in versions:
            if not os.path.exists(version.file_path):
                deleted_version_ids.append(version.id)
                product_ids_to_check.add(version.product_id)

        # Version 삭제
        if deleted_version_ids:
            db.query(Version).filter(Version.id.in_(deleted_version_ids)).delete(synchronize_session=False)

        # Version이 없는 Product 삭제
        deleted_product_ids = []
        for product_id in product_ids_to_check:
            version_count = db.query(Version).filter(Version.product_id == product_id).count()
            if version_count == 0:
                deleted_product_ids.append(product_id)

        if deleted_product_ids:
            db.query(Product).filter(Product.id.in_(deleted_product_ids)).delete(synchronize_session=False)

        db.commit()

        # 캐시 무효화
        invalidate_cache([
            "products:*",
            "products_recent:*",
            "products_by_category:*",
            "stats_overview:*",
            "stats_categories:*"
        ])

        return {
            "success": True,
            "message": f"{len(deleted_version_ids)}개의 버전과 {len(deleted_product_ids)}개의 제품이 삭제되었습니다.",
            "deleted_versions": len(deleted_version_ids),
            "deleted_products": len(deleted_product_ids)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"삭제된 파일 정리 중 오류 발생: {str(e)}"
        )


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """
    제품 삭제 (관리자 전용)

    제품과 연결된 모든 버전을 삭제합니다.
    """
    try:
        # 제품 확인
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다")

        # 제품에 연결된 모든 버전 삭제 (cascade로 자동 삭제되지만 명시적으로 처리)
        db.query(Version).filter(Version.product_id == product_id).delete(synchronize_session=False)

        # 제품 삭제
        db.delete(product)
        db.commit()

        # 캐시 무효화
        invalidate_cache([
            "products:*",
            "products_recent:*",
            "products_by_category:*",
            "stats_overview:*",
            "stats_categories:*"
        ])

        return {
            "success": True,
            "message": "제품이 삭제되었습니다."
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"제품 삭제 중 오류 발생: {str(e)}"
        )
