from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Body
from sqlalchemy.orm import Session
from typing import List, Dict
from pathlib import Path
import io
import re
import hashlib
from datetime import datetime
import httpx
import logging
logger = logging.getLogger(__name__)


from app.database import get_db
from app.dependencies import get_current_admin_user, get_current_user
from app.models.user import User
from app.models.product import Product
from app.schemas.image import (
    GoogleImageSearchRequest,
    GoogleImageSearchResponse,
    GoogleImageResult,
    ImageUploadResponse,
    ImageDeleteResponse
)
from app.core.google_image_search import GoogleImageSearcher
from app.core.icon_cache import IconCache
from app.config import settings
import json

# PIL/Pillow for image validation
try:
    from PIL import Image
except ImportError:
    Image = None

router = APIRouter(tags=["images"])

# 허용되는 이미지 MIME 타입
ALLOWED_MIME_TYPES = [
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/gif",
    "image/svg+xml",
    "image/webp"
]

# 파일 크기 제한 (100 bytes ~ 5 MB)
MIN_FILE_SIZE = 100
MAX_FILE_SIZE = 5 * 1024 * 1024


def sanitize_filename(name: str, max_length: int = 50) -> str:
    """
    파일명으로 사용할 수 있도록 문자열을 정리

    Args:
        name: 정리할 문자열
        max_length: 최대 길이

    Returns:
        정리된 파일명
    """
    # 특수문자 제거, 공백을 언더스코어로 변환
    sanitized = re.sub(r'[^\w\s-]', '', name)
    sanitized = re.sub(r'[\s]+', '_', sanitized)
    sanitized = sanitized.strip('_')

    # 최대 길이 제한
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    # 빈 문자열이면 기본값 반환
    return sanitized if sanitized else 'unnamed'


def get_google_searcher() -> GoogleImageSearcher:
    """Google Image Searcher 인스턴스 생성"""
    # config.json에서 Google API 설정 읽기
    config_path = Path(settings.CONFIG_DATA_DIR) / "config.json"
    google_api_key = settings.GOOGLE_CUSTOM_SEARCH_API_KEY
    google_search_engine_id = settings.GOOGLE_SEARCH_ENGINE_ID

    try:
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                metadata_config = config.get('metadata', {})
                # config.json에 설정이 있으면 우선 사용
                if metadata_config.get('googleApiKey'):
                    google_api_key = metadata_config['googleApiKey']
                if metadata_config.get('googleSearchEngineId'):
                    google_search_engine_id = metadata_config['googleSearchEngineId']
    except Exception as e:
        logger.debug(f"Error reading Google API config: {e}")

    return GoogleImageSearcher(
        api_key=google_api_key,
        search_engine_id=google_search_engine_id
    )


def get_icon_cache() -> IconCache:
    """Icon Cache 인스턴스 생성"""
    return IconCache(settings.ICON_CACHE_DIR, settings.SCREENSHOT_CACHE_DIR)


def validate_image_file(file: UploadFile) -> None:
    """
    이미지 파일 유효성 검증

    Args:
        file: 업로드된 파일

    Raises:
        HTTPException: 검증 실패 시
    """
    # MIME 타입 확인
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Allowed: {', '.join(ALLOWED_MIME_TYPES)}"
        )

    # 파일 크기 확인 (파일 읽기)
    file.file.seek(0, 2)  # 파일 끝으로 이동
    file_size = file.file.tell()
    file.file.seek(0)  # 파일 시작으로 되돌림

    if file_size < MIN_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too small: {file_size} bytes (min: {MIN_FILE_SIZE} bytes)"
        )

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large: {file_size} bytes (max: {MAX_FILE_SIZE} bytes)"
        )

    # PIL로 이미지 유효성 확인 (설치되어 있는 경우)
    if Image:
        try:
            img = Image.open(file.file)
            img.verify()
            file.file.seek(0)  # 검증 후 파일 포인터 리셋
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid or corrupted image file: {str(e)}"
            )


@router.post("/search-logo", response_model=GoogleImageSearchResponse)
async def search_logo(
    request: GoogleImageSearchRequest,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Google Custom Search API로 로고 검색

    Args:
        request: 검색 요청 (query, limit)
        current_user: 현재 관리자 사용자

    Returns:
        검색 결과
    """
    logger.debug(f"\n[Images API] Logo search request received")
    logger.debug(f"Images API] Query: '{request.query}'")
    logger.debug(f"Images API] Limit: {request.limit}, Offset: {request.offset}")

    searcher = get_google_searcher()

    if not searcher.is_configured():
        # OAuth 클라이언트 ID 형식 감지
        if '.apps.googleusercontent.com' in searcher.search_engine_id:
            error_msg = "❌ Search Engine ID가 잘못되었습니다.\n\n현재 입력된 값은 OAuth 클라이언트 ID입니다.\n\n올바른 설정:\n1. https://programmablesearchengine.google.com 방문\n2. 새 검색엔진 생성 (이미지 검색 활성화 필수)\n3. 생성된 검색엔진 ID를 복사하여 입력\n\n예시: 017576662512468239146:omuauf_lfve"
        else:
            error_msg = "Google Custom Search API가 설정되지 않았습니다. Settings → Metadata에서 API Key와 Search Engine ID를 설정해주세요."

        logger.error(f"Images API] ERROR: {error_msg}")
        return GoogleImageSearchResponse(
            success=False,
            images=[],
            error=error_msg
        )

    try:
        logger.debug(f"Images API] Calling searcher.search_logo()...")
        results = await searcher.search_logo(request.query, request.limit, request.offset)
        logger.debug(f"Images API] Search completed, found {len(results)} results")

        if len(results) == 0:
            return GoogleImageSearchResponse(
                success=True,
                images=[],
                error="검색 결과가 없습니다. 다른 검색어를 시도해보세요."
            )

        return GoogleImageSearchResponse(
            success=True,
            images=[GoogleImageResult(**r) for r in results]
        )

    except Exception as e:
        error_msg = f"검색 중 오류 발생: {str(e)}"
        logger.debug(f"Images API] ERROR: {error_msg}")
        import traceback
        traceback.print_exc()
        return GoogleImageSearchResponse(
            success=False,
            images=[],
            error=error_msg
        )


@router.post("/search-screenshots", response_model=GoogleImageSearchResponse)
async def search_screenshots(
    request: GoogleImageSearchRequest,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Google Custom Search API로 스크린샷 검색

    Args:
        request: 검색 요청 (query, limit)
        current_user: 현재 관리자 사용자

    Returns:
        검색 결과
    """
    logger.debug(f"\n[Images API] Screenshot search request received")
    logger.debug(f"Images API] Query: '{request.query}'")
    logger.debug(f"Images API] Limit: {request.limit}, Offset: {request.offset}")

    searcher = get_google_searcher()

    if not searcher.is_configured():
        # OAuth 클라이언트 ID 형식 감지
        if '.apps.googleusercontent.com' in searcher.search_engine_id:
            error_msg = "❌ Search Engine ID가 잘못되었습니다.\n\n현재 입력된 값은 OAuth 클라이언트 ID입니다.\n\n올바른 설정:\n1. https://programmablesearchengine.google.com 방문\n2. 새 검색엔진 생성 (이미지 검색 활성화 필수)\n3. 생성된 검색엔진 ID를 복사하여 입력\n\n예시: 017576662512468239146:omuauf_lfve"
        else:
            error_msg = "Google Custom Search API가 설정되지 않았습니다. Settings → Metadata에서 API Key와 Search Engine ID를 설정해주세요."

        logger.error(f"Images API] ERROR: {error_msg}")
        return GoogleImageSearchResponse(
            success=False,
            images=[],
            error=error_msg
        )

    try:
        logger.debug(f"Images API] Calling searcher.search_screenshots()...")
        results = await searcher.search_screenshots(request.query, request.limit, request.offset)
        logger.debug(f"Images API] Search completed, found {len(results)} results")

        if len(results) == 0:
            return GoogleImageSearchResponse(
                success=True,
                images=[],
                error="검색 결과가 없습니다. 다른 검색어를 시도해보세요."
            )

        return GoogleImageSearchResponse(
            success=True,
            images=[GoogleImageResult(**r) for r in results]
        )

    except Exception as e:
        error_msg = f"검색 중 오류 발생: {str(e)}"
        logger.debug(f"Images API] ERROR: {error_msg}")
        import traceback
        traceback.print_exc()
        return GoogleImageSearchResponse(
            success=False,
            images=[],
            error=error_msg
        )


@router.post("/upload-logo/{product_id}", response_model=ImageUploadResponse)
async def upload_logo(
    product_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    제품 로고 업로드

    Args:
        product_id: 제품 ID
        file: 업로드할 이미지 파일
        db: 데이터베이스 세션
        current_user: 현재 관리자 사용자

    Returns:
        업로드된 로고 URL
    """
    # 제품 존재 확인
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # 파일 유효성 검증
    validate_image_file(file)

    try:
        icon_cache = get_icon_cache()

        # 기존 로고 삭제
        icon_cache.delete_icon(product_id)

        # 파일 저장
        content = await file.read()
        file_ext = Path(file.filename).suffix.lower()
        if not file_ext:
            # content_type에서 확장자 추정
            if "png" in file.content_type:
                file_ext = ".png"
            elif "jpeg" in file.content_type or "jpg" in file.content_type:
                file_ext = ".jpg"
            elif "gif" in file.content_type:
                file_ext = ".gif"
            elif "svg" in file.content_type:
                file_ext = ".svg"
            elif "webp" in file.content_type:
                file_ext = ".webp"
            else:
                file_ext = ".png"

        # 제품명을 포함한 파일명 생성
        title_part = sanitize_filename(product.title, max_length=30)
        filename = f"{product_id}_{title_part}_icon{file_ext}"
        file_path = Path(settings.ICON_CACHE_DIR) / filename

        with open(file_path, 'wb') as f:
            f.write(content)

        # 상대 경로만 저장 (프론트엔드에서 동적으로 백엔드 URL 추가)
        local_path = f"/static/icons/{filename}"

        # DB 업데이트 (상대 경로만 저장)
        product.icon_url = local_path
        db.commit()

        # 응답에는 전체 URL 반환 (API 응답용)
        full_url = f"{settings.get_backend_url()}{local_path}"

        return ImageUploadResponse(
            success=True,
            url=full_url
        )

    except Exception as e:
        db.rollback()
        return ImageUploadResponse(
            success=False,
            error=str(e)
        )


@router.post("/upload-screenshots/{product_id}", response_model=ImageUploadResponse)
async def upload_screenshots(
    product_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    제품 스크린샷 업로드 (최대 10개)

    Args:
        product_id: 제품 ID
        files: 업로드할 이미지 파일 리스트
        db: 데이터베이스 세션
        current_user: 현재 관리자 사용자

    Returns:
        업로드된 스크린샷 URL 리스트
    """
    # 제품 존재 확인
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # 파일 개수 제한
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 screenshots allowed")

    # 모든 파일 유효성 검증
    for file in files:
        validate_image_file(file)

    try:
        icon_cache = get_icon_cache()

        # 기존 스크린샷 삭제
        icon_cache.delete_screenshots(product_id)

        # 파일 저장
        screenshot_urls = []

        for i, file in enumerate(files):
            content = await file.read()
            file_ext = Path(file.filename).suffix.lower()
            if not file_ext:
                if "png" in file.content_type:
                    file_ext = ".png"
                elif "jpeg" in file.content_type or "jpg" in file.content_type:
                    file_ext = ".jpg"
                elif "gif" in file.content_type:
                    file_ext = ".gif"
                elif "svg" in file.content_type:
                    file_ext = ".svg"
                elif "webp" in file.content_type:
                    file_ext = ".webp"
                else:
                    file_ext = ".png"

            # 제품명을 포함한 파일명 생성
            title_part = sanitize_filename(product.title, max_length=30)
            filename = f"{product_id}_{title_part}_screenshot_{i}{file_ext}"
            file_path = Path(settings.SCREENSHOT_CACHE_DIR) / filename

            # 디렉토리 생성 (없으면)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'wb') as f:
                f.write(content)

            # 전체 URL 생성 (프론트엔드가 다른 포트에서 실행되므로 백엔드 URL 포함)
            local_path = f"/static/screenshots/{filename}"
            full_url = f"{settings.BACKEND_URL}{local_path}"
            screenshot_urls.append(full_url)

        # DB 업데이트 (JSON 배열로 저장)
        screenshots_data = [{"type": "local", "url": url} for url in screenshot_urls]
        product.screenshots = screenshots_data
        db.commit()

        return ImageUploadResponse(
            success=True,
            urls=screenshot_urls
        )

    except Exception as e:
        db.rollback()
        return ImageUploadResponse(
            success=False,
            error=str(e)
        )


@router.post("/download-logo/{product_id}", response_model=ImageUploadResponse)
async def download_logo_from_url(
    product_id: int,
    url: str = Query(..., description="Image URL to download"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    URL에서 로고 다운로드 후 저장

    Args:
        product_id: 제품 ID
        url: 다운로드할 이미지 URL
        db: 데이터베이스 세션
        current_user: 현재 관리자 사용자

    Returns:
        저장된 로고 URL
    """
    logger.debug(f"\n[Download Logo] Request received")
    logger.debug(f"Download Logo] Product ID: {product_id}")
    logger.debug(f"Download Logo] URL: {url}")

    try:
        icon_cache = get_icon_cache()

        # 기존 로고 삭제
        icon_cache.delete_icon(product_id)

        # URL에서 다운로드
        local_path = await icon_cache.download_and_cache(url, product_id)

        if local_path:
            logger.debug(f"Download Logo] Local path: {local_path}")

            # 제품이 존재하면 DB 업데이트 (상대 경로만 저장)
            product = db.query(Product).filter(Product.id == product_id).first()
            if product:
                product.icon_url = local_path
                db.commit()
                logger.debug(f"Download Logo] DB updated for product {product_id}")
            else:
                logger.debug(f"Download Logo] Product {product_id} not found in DB (test mode), skipping DB update")

            # 응답에는 전체 URL 반환 (API 응답용)
            full_url = f"{settings.get_backend_url()}{local_path}"
            logger.debug(f"Download Logo] Full URL: {full_url}")

            return ImageUploadResponse(
                success=True,
                url=full_url
            )
        else:
            return ImageUploadResponse(
                success=False,
                error="Failed to download image from URL"
            )

    except Exception as e:
        logger.debug(f"Download Logo] Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return ImageUploadResponse(
            success=False,
            error=str(e)
        )


@router.post("/download-screenshots/{product_id}", response_model=ImageUploadResponse)
async def download_screenshots_from_urls(
    product_id: int,
    urls: List[str] = Query(..., description="Image URLs to download"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    URL에서 스크린샷 다운로드 후 저장 (최대 4개)
    기존 스크린샷을 삭제하고 새로운 스크린샷으로 완전히 교체

    Args:
        product_id: 제품 ID
        urls: 다운로드할 이미지 URL 리스트 (최대 4개)
        db: 데이터베이스 세션
        current_user: 현재 관리자 사용자

    Returns:
        저장된 스크린샷 URL 리스트
    """
    logger.debug(f"\n[Download Screenshots] Request received")
    logger.debug(f"Download Screenshots] Product ID: {product_id}")
    logger.debug(f"Download Screenshots] URLs count: {len(urls)}")

    # URL 개수 제한 (최대 4개)
    if len(urls) > 4:
        raise HTTPException(status_code=400, detail="Maximum 4 screenshots allowed")

    try:
        icon_cache = get_icon_cache()

        # 기존 제품 정보 가져오기
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # 기존 스크린샷 URL 목록
        existing_screenshots = product.screenshots or []
        existing_urls = [s['url'] if isinstance(s, dict) else s for s in existing_screenshots]

        # 요청받은 URL 중 유지할 로컬 URL 목록
        keep_urls = set()
        for url in urls:
            if url.startswith(settings.BACKEND_URL) or url.startswith('/static/'):
                keep_urls.add(url)

        # 기존 스크린샷 중 삭제할 파일만 삭제
        screenshot_dir = Path(settings.SCREENSHOT_CACHE_DIR)
        for old_url in existing_urls:
            if old_url not in keep_urls:
                try:
                    # URL에서 파일명 추출
                    if '/static/screenshots/' in old_url:
                        filename = old_url.split('/static/screenshots/')[-1]
                        file_path = screenshot_dir / filename
                        if file_path.exists():
                            file_path.unlink()
                            logger.debug(f"Download Screenshots] Deleted old screenshot: {filename}")
                except Exception as e:
                    logger.debug(f"Download Screenshots] Failed to delete old screenshot {old_url}: {e}")

        # 새로운 스크린샷 다운로드
        downloaded_local_urls = []
        failed_external_urls = []

        for i, url in enumerate(urls):
            logger.debug(f"Download Screenshots] Processing URL {i+1}/{len(urls)}: {url}")

            # 이미 로컬 파일인 경우 (재사용)
            if url.startswith(settings.BACKEND_URL) or url.startswith('/static/'):
                # 기존 로컬 URL 그대로 사용
                downloaded_local_urls.append(url)
                logger.debug(f"Download Screenshots] - Keeping existing local screenshot")
            else:
                # 외부 URL 다운로드
                local_path = await icon_cache._download_screenshot(url, product_id, i)

                if local_path:
                    full_url = f"{settings.BACKEND_URL}{local_path}"
                    downloaded_local_urls.append(full_url)
                    logger.debug(f"Download Screenshots] Downloaded: {local_path} → {full_url}")
                else:
                    # 다운로드 실패 시 원본 외부 URL 사용
                    failed_external_urls.append(url)
                    logger.debug(f"Download Screenshots] Failed to download, using external URL: {url}")

        # 최종 스크린샷 리스트
        screenshots_data = []

        # 다운로드된 로컬 스크린샷 추가
        for url in downloaded_local_urls:
            screenshots_data.append({"type": "local", "url": url})

        # 다운로드 실패한 외부 URL 추가
        for url in failed_external_urls:
            screenshots_data.append({"type": "external", "url": url})

        # DB 업데이트
        product.screenshots = screenshots_data
        db.commit()
        logger.debug(f"Download Screenshots] DB updated for product {product_id}")
        logger.debug(f"Download Screenshots] Total screenshots: {len(screenshots_data)}")

        # 모든 URL 반환
        all_urls = downloaded_local_urls + failed_external_urls

        return ImageUploadResponse(
            success=True,
            urls=all_urls
        )

    except Exception as e:
        logger.debug(f"Download Screenshots] Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return ImageUploadResponse(
            success=False,
            error=str(e)
        )


@router.delete("/{product_id}", response_model=ImageDeleteResponse)
async def delete_images(
    product_id: int,
    image_type: str = Query(..., description="logo, screenshots, or all"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    제품 이미지 삭제

    Args:
        product_id: 제품 ID
        image_type: 삭제할 이미지 유형 (logo, screenshots, all)
        db: 데이터베이스 세션
        current_user: 현재 관리자 사용자

    Returns:
        삭제된 파일 개수
    """
    # 제품 존재 확인
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # image_type 검증
    if image_type not in ["logo", "screenshots", "all"]:
        raise HTTPException(
            status_code=400,
            detail="image_type must be 'logo', 'screenshots', or 'all'"
        )

    try:
        icon_cache = get_icon_cache()
        deleted_count = 0

        # 로고 삭제
        if image_type in ["logo", "all"]:
            if icon_cache.delete_icon(product_id):
                deleted_count += 1
                product.icon_url = None

        # 스크린샷 삭제
        if image_type in ["screenshots", "all"]:
            count = icon_cache.delete_screenshots(product_id)
            deleted_count += count
            product.screenshots = []

        db.commit()

        return ImageDeleteResponse(
            success=True,
            deleted_count=deleted_count
        )

    except Exception as e:
        db.rollback()
        return ImageDeleteResponse(
            success=False,
            deleted_count=0,
            error=str(e)
        )


@router.post("/process-post-content")
async def process_post_content(
    content: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    게시글 내용에서 외부 이미지를 찾아 로컬로 다운로드하고 URL 교체

    Args:
        content: HTML 형식의 게시글 내용
        current_user: 현재 사용자

    Returns:
        {
            "content": "업데이트된 HTML 내용",
            "images": ["다운로드된 이미지 로컬 경로 리스트"]
        }
    """
    logger.debug(f"\n[Process Post Content] Request received")
    logger.debug(f"Process Post Content] User: {current_user.username}")

    # 외부 이미지 디렉토리 생성
    eximage_dir = Path(settings.EXIMAGE_DIR)
    eximage_dir.mkdir(parents=True, exist_ok=True)

    # HTML에서 이미지 URL 추출 (img 태그의 src 속성)
    img_pattern = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)
    img_matches = img_pattern.findall(content)

    logger.debug(f"Process Post Content] Found {len(img_matches)} images")

    downloaded_images = []
    updated_content = content

    for img_url in img_matches:
        # 이미 로컬 이미지인 경우 스킵
        if img_url.startswith('/static/eximage/') or img_url.startswith(f'{settings.BACKEND_URL}/static/eximage/'):
            logger.debug(f"Process Post Content] Skipping local image: {img_url}")
            continue

        # data: URL (base64 인코딩 이미지)인 경우 스킵
        if img_url.startswith('data:'):
            logger.debug(f"Process Post Content] Skipping base64 image")
            continue

        # 상대 경로인 경우 스킵 (로컬 파일로 간주)
        if not img_url.startswith('http://') and not img_url.startswith('https://'):
            logger.debug(f"Process Post Content] Skipping relative path: {img_url}")
            continue

        logger.debug(f"Process Post Content] Downloading external image: {img_url}")

        try:
            # 외부 이미지 다운로드
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(img_url)
                response.raise_for_status()

                # 파일 확장자 추출
                content_type = response.headers.get('content-type', '')
                if 'png' in content_type:
                    ext = '.png'
                elif 'jpeg' in content_type or 'jpg' in content_type:
                    ext = '.jpg'
                elif 'gif' in content_type:
                    ext = '.gif'
                elif 'webp' in content_type:
                    ext = '.webp'
                elif 'svg' in content_type:
                    ext = '.svg'
                else:
                    # URL에서 확장자 추출 시도
                    url_path = Path(img_url.split('?')[0])  # 쿼리 스트링 제거
                    ext = url_path.suffix.lower() if url_path.suffix else '.jpg'

                # 고유한 파일명 생성 (타임스탬프 + 해시)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                url_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
                filename = f"{timestamp}_{url_hash}{ext}"

                # 파일 저장
                file_path = eximage_dir / filename
                with open(file_path, 'wb') as f:
                    f.write(response.content)

                # 로컬 URL 생성
                local_url = f"/static/eximage/{filename}"
                full_local_url = f"{settings.BACKEND_URL}{local_url}"

                # HTML에서 외부 URL을 로컬 URL로 교체
                updated_content = updated_content.replace(img_url, full_local_url)

                downloaded_images.append(local_url)
                logger.debug(f"Process Post Content] Downloaded: {filename}")

        except Exception as e:
            logger.debug(f"Process Post Content] Failed to download {img_url}: {e}")
            # 다운로드 실패 시 원본 URL 유지
            continue

    logger.debug(f"Process Post Content] Successfully downloaded {len(downloaded_images)} images")

    return {
        "content": updated_content,
        "images": downloaded_images
    }


@router.post("/upload-tinymce")
async def upload_tinymce_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    TinyMCE에서 업로드한 이미지를 eximage 폴더에 저장

    Args:
        file: 업로드할 이미지 파일
        current_user: 현재 사용자

    Returns:
        {"location": "저장된 이미지 URL"}
    """
    logger.debug(f"\n[Upload TinyMCE Image] Request received")
    logger.debug(f"Upload TinyMCE Image] User: {current_user.username}")
    logger.debug(f"Upload TinyMCE Image] Filename: {file.filename}")

    try:
        # 외부 이미지 디렉토리 생성
        eximage_dir = Path(settings.EXIMAGE_DIR)
        eximage_dir.mkdir(parents=True, exist_ok=True)

        # 파일 확장자 추출
        file_ext = Path(file.filename).suffix.lower() if file.filename else '.jpg'
        if not file_ext:
            file_ext = '.jpg'

        # 고유한 파일명 생성 (타임스탬프 + 랜덤)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        import random
        random_str = ''.join(random.choices('0123456789abcdef', k=8))
        filename = f"{timestamp}_{random_str}{file_ext}"

        # 파일 저장
        file_path = eximage_dir / filename
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)

        # 로컬 URL 생성
        local_url = f"/static/eximage/{filename}"
        full_local_url = f"{settings.BACKEND_URL}{local_url}"

        logger.debug(f"Upload TinyMCE Image] Saved: {filename}")

        return {
            "location": full_local_url
        }

    except Exception as e:
        logger.debug(f"Upload TinyMCE Image] Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
