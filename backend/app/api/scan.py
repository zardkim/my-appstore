from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path
from datetime import datetime

from app.database import get_db
from app.core.scanner import FileScanner
from app.dependencies import get_current_admin_user
from app.config import settings
from app.models.setting import Setting
from app.core.redis_cache import invalidate_cache

router = APIRouter()


class ScanRequest(BaseModel):
    path: str
    use_ai: Optional[bool] = True  # Enable AI metadata generation


class ScanResponse(BaseModel):
    new_products: int
    new_versions: int
    updated_products: int
    ai_generated: Optional[int] = 0
    icons_cached: Optional[int] = 0
    errors: list


class ScanExclusionsResponse(BaseModel):
    exclusions: List[str]


class ScanExclusionsRequest(BaseModel):
    exclusions: List[str]


@router.post("/start", response_model=ScanResponse)
async def start_scan(
    request: ScanRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """
    Start a manual scan of the specified directory
    Admin only

    Args:
        path: Directory path to scan
        use_ai: Enable AI metadata generation (requires OpenAI API key)
    """
    scanner = FileScanner(db, use_ai=request.use_ai)

    try:
        if request.use_ai:
            # Use async version with AI
            results = await scanner.scan_directory_async(request.path)
        else:
            # Use sync version without AI
            results = scanner.scan_directory(request.path)

        # 스캔 완료 후 마지막 스캔 시간을 Settings에 저장
        last_scan_time = datetime.now().isoformat()
        last_scan_setting = db.query(Setting).filter(
            Setting.key == "last_scan_time"
        ).first()

        if last_scan_setting:
            last_scan_setting.value = last_scan_time
        else:
            last_scan_setting = Setting(
                key="last_scan_time",
                value=last_scan_time,
                description="마지막 스캔 완료 시간"
            )
            db.add(last_scan_setting)

        db.commit()

        # 캐시 무효화 (새 제품이 추가되었을 수 있음)
        invalidate_cache([
            "products_list:*",
            "products_recent:*",
            "products_by_category:*",
            "search_suggestions:*",
            "stats_overview:*",
            "stats_categories:*"
        ])

        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@router.post("/regenerate-metadata/{product_id}")
async def regenerate_metadata(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """
    Regenerate metadata for a specific product using AI
    Admin only
    """
    from app.models.product import Product
    from app.core.ai_metadata import AIMetadataGeneratorV2 as AIMetadataGenerator
    from app.core.icon_cache import IconCache

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        ai_generator = AIMetadataGenerator()
        icon_cache = IconCache()

        # Get folder name from path
        folder_name = product.folder_path.split('/')[-1]

        # Generate new metadata
        metadata = await ai_generator.generate_metadata(folder_name)

        # Update product
        product.title = metadata['title']
        product.description = metadata['description']
        product.vendor = metadata['vendor']
        product.category = metadata['category']

        # Download icon if available
        if metadata.get('icon_url'):
            cached_icon = await icon_cache.download_and_cache(
                metadata['icon_url'],
                product.id
            )
            if cached_icon:
                product.icon_url = cached_icon

        db.commit()
        db.refresh(product)

        return {
            "success": True,
            "product": {
                "id": product.id,
                "title": product.title,
                "description": product.description,
                "vendor": product.vendor,
                "category": product.category,
                "icon_url": product.icon_url
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Metadata regeneration failed: {str(e)}")


@router.get("/exclusions", response_model=ScanExclusionsResponse)
async def get_scan_exclusions(
    current_user = Depends(get_current_admin_user)
):
    """
    Get current scan exclusion list
    Admin only
    """
    try:
        exclusions_file = Path(settings.SCAN_EXCLUSIONS_FILE)

        # 파일이 없으면 기본값 반환
        if not exclusions_file.exists():
            default_exclusions = [
                '.git',
                'node_modules',
                '__MACOSX',
                '$RECYCLE.BIN',
                '.Trash',
                'System Volume Information',
                '.DS_Store',
                'Thumbs.db'
            ]
            return {"exclusions": default_exclusions}

        # 파일에서 읽기
        with open(exclusions_file, 'r', encoding='utf-8') as f:
            exclusions = [
                line.strip()
                for line in f.readlines()
                if line.strip() and not line.strip().startswith('#')
            ]
            return {"exclusions": exclusions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load scan exclusions: {str(e)}")


@router.post("/exclusions")
async def save_scan_exclusions(
    request: ScanExclusionsRequest,
    current_user = Depends(get_current_admin_user)
):
    """
    Save scan exclusion list to file
    Admin only
    """
    try:
        exclusions_file = Path(settings.SCAN_EXCLUSIONS_FILE)

        # 디렉토리가 없으면 생성
        exclusions_file.parent.mkdir(parents=True, exist_ok=True)

        # 파일에 저장 (한 줄씩)
        with open(exclusions_file, 'w', encoding='utf-8') as f:
            f.write('# 스캔 예외 폴더 목록\n')
            f.write('# 한 줄에 하나씩 입력하세요\n\n')
            f.write('\n'.join(request.exclusions))

        return {"success": True, "message": "Scan exclusions saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save scan exclusions: {str(e)}")
