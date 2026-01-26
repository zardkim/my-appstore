from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path
from datetime import datetime
import os

from app.database import get_db
from app.core.scanner import FileScanner
from app.dependencies import get_current_admin_user
from app.config import settings
from app.models.setting import Setting
from app.core.redis_cache import invalidate_cache
from app.models.filename_violation import FilenameViolation
from app.models.product import Product
from app.models.version import Version
from app.core.ai_metadata import AIMetadataGeneratorV2 as AIMetadataGenerator
from app.core.parser import FilenameParser
from app.api.config import load_config
from app.core.auto_matcher import match_violations_to_products

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
    folders: Optional[List[str]] = []
    patterns: Optional[List[str]] = []
    paths: Optional[List[str]] = []
    # 하위 호환성을 위해 유지
    exclusions: Optional[List[str]] = []


class ScanExclusionsRequest(BaseModel):
    folders: Optional[List[str]] = []
    patterns: Optional[List[str]] = []
    paths: Optional[List[str]] = []


async def auto_match_scanned_files(db: Session) -> dict:
    """
    스캔된 파일들에 대해 자동으로 AI 매칭 수행
    통합 매칭 로직(auto_matcher.py) 사용

    Returns:
        {"matched": int, "failed": int, "errors": list}
    """
    # config에서 autoMatch 설정 확인
    config = load_config()
    metadata_config = config.get('metadata', {})
    auto_match = metadata_config.get('autoMatch', False)

    if not auto_match:
        return {"matched": 0, "failed": 0, "errors": [], "message": "Auto-match is disabled"}

    use_ai = metadata_config.get('useAI', False)
    ai_provider = metadata_config.get('aiProvider', 'openai')
    ai_model = metadata_config.get('aiModel', 'gpt-4o-mini')

    if not use_ai:
        return {"matched": 0, "failed": 0, "errors": [], "message": "AI is disabled"}

    # AI Provider에 따라 적절한 API key 가져오기
    if ai_provider == 'gemini':
        api_key = metadata_config.get('geminiApiKey', '')
    elif ai_provider == 'openai':
        api_key = metadata_config.get('openaiApiKey', '')
    else:
        return {"matched": 0, "failed": 0, "errors": [f"Unsupported AI provider: {ai_provider}"]}

    if not api_key or not api_key.strip():
        return {"matched": 0, "failed": 0, "errors": ["API key not configured"]}

    # violation_type이 "scanned"이고 is_resolved가 False인 항목들 조회
    unmatched_violations = db.query(FilenameViolation).filter(
        FilenameViolation.violation_type == "scanned",
        FilenameViolation.is_resolved == False
    ).all()

    # 통합 매칭 로직 호출 (자동 매칭 모드: 명확성 검사 수행)
    results = await match_violations_to_products(
        db=db,
        violations=unmatched_violations,
        ai_provider=ai_provider,
        ai_model=ai_model,
        api_key=api_key,
        skip_clarity_check=False,  # 자동 매칭: 명확성 검사 수행
        provided_metadata=None  # 자동 매칭: AI가 메타데이터 생성
    )

    return results


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

        # 스캔 완료 후 자동 매칭 수행
        match_results = await auto_match_scanned_files(db)

        # 매칭 결과를 results에 반영
        if match_results.get("matched", 0) > 0:
            results["new_products"] = match_results["matched"]
            if match_results.get("errors"):
                results["errors"].extend(match_results["errors"])

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
    import json

    try:
        exclusions_file = Path(settings.SCAN_EXCLUSIONS_FILE)

        # 파일이 없으면 기본값 반환
        if not exclusions_file.exists():
            return {
                "folders": ['.git', 'node_modules', '__MACOSX', '$RECYCLE.BIN', '.Trash',
                           'System Volume Information', '.DS_Store', 'Thumbs.db',
                           'desktop.ini', '._.DS_Store', 'Icon\r', '@eaDir'],
                "patterns": ['*.txt', '*.log', 'thumbs.db', 'desktop.ini'],
                "paths": [],
                "exclusions": []  # 하위 호환성
            }

        # JSON 파일에서 읽기
        with open(exclusions_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                # 빈 파일인 경우 기본값 반환
                return {
                    "folders": ['.git', 'node_modules', '__MACOSX', '$RECYCLE.BIN', '.Trash'],
                    "patterns": ['*.txt', '*.log', 'thumbs.db', 'desktop.ini'],
                    "paths": [],
                    "exclusions": []
                }

            try:
                data = json.loads(content)
                return {
                    "folders": data.get("folders", []),
                    "patterns": data.get("patterns", []),
                    "paths": data.get("paths", []),
                    "exclusions": data.get("folders", [])  # 하위 호환성
                }
            except json.JSONDecodeError:
                # 구 형식(줄바꿈으로 구분)인 경우 폴더 목록으로 간주
                exclusions = [
                    line.strip()
                    for line in content.split('\n')
                    if line.strip() and not line.strip().startswith('#')
                ]
                return {
                    "folders": exclusions,
                    "patterns": ['*.txt', '*.log', 'thumbs.db', 'desktop.ini'],
                    "paths": [],
                    "exclusions": exclusions
                }
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
    import json

    try:
        exclusions_file = Path(settings.SCAN_EXCLUSIONS_FILE)

        # 디렉토리가 없으면 생성
        exclusions_file.parent.mkdir(parents=True, exist_ok=True)

        # JSON 형식으로 저장
        data = {
            "folders": request.folders or [],
            "patterns": request.patterns or [],
            "paths": request.paths or []
        }

        with open(exclusions_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return {"success": True, "message": "Scan exclusions saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save scan exclusions: {str(e)}")
