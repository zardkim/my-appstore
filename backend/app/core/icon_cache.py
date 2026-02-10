import httpx
import logging
logger = logging.getLogger(__name__)
from pathlib import Path
from typing import Optional, List, Dict
import hashlib
import re
from urllib.parse import urlparse


class IconCache:
    """
    아이콘 이미지 다운로드 및 로컬 캐싱
    """

    def __init__(self, cache_dir: str = None, screenshot_cache_dir: str = None):
        # cache_dir이 None이면 settings에서 가져오기
        if cache_dir is None:
            from app.config import settings
            cache_dir = settings.ICON_CACHE_DIR
            screenshot_cache_dir = settings.SCREENSHOT_CACHE_DIR

        self.cache_dir = Path(cache_dir)

        # 스크린샷 전용 캐시 디렉토리
        if screenshot_cache_dir:
            self.screenshot_cache_dir = Path(screenshot_cache_dir)
        else:
            self.screenshot_cache_dir = self.cache_dir

        # 폴더 생성 (에러 처리 강화)
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Icon cache directory ensured: {self.cache_dir}")
        except Exception as e:
            logger.warning(f"Could not create icon cache directory {self.cache_dir}: {e}")

        try:
            self.screenshot_cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Screenshot cache directory ensured: {self.screenshot_cache_dir}")
        except Exception as e:
            logger.warning(f"Could not create screenshot cache directory {self.screenshot_cache_dir}: {e}")

    @staticmethod
    def _sanitize_title(title: str, max_length: int = 50) -> str:
        """제품 타이틀을 파일명으로 사용할 수 있도록 정리"""
        sanitized = re.sub(r'[^\w\s-]', '', title)
        sanitized = re.sub(r'[\s]+', '_', sanitized)
        sanitized = sanitized.strip('_')
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length].rstrip('_')
        return sanitized if sanitized else 'unnamed'

    def _make_icon_filename(self, product_id: int, ext: str, product_title: str = None) -> str:
        """로고 파일명 생성: {title}_{id}{ext}"""
        if product_title:
            safe_title = self._sanitize_title(product_title)
            return f"{safe_title}_{product_id}{ext}"
        return f"{product_id}{ext}"

    async def download_and_cache(
        self,
        url: str,
        product_id: int,
        product_title: str = None
    ) -> Optional[str]:
        """
        URL에서 아이콘 다운로드 후 로컬에 저장

        Args:
            url: 아이콘 이미지 URL
            product_id: 제품 ID
            product_title: 제품 타이틀 (파일명에 사용)

        Returns:
            로컬 파일 경로 (예: /static/icons/Adobe_Photoshop_1.png) 또는 None
        """
        if not url or not url.strip():
            return None

        # URL 유효성 검증
        if not self._is_valid_url(url):
            logger.error(f"Invalid URL: {url}")
            return None

        try:
            logger.debug(f" Downloading from URL: {url}")

            async with httpx.AsyncClient(timeout=15.0) as client:
                # 헤더 설정 (일부 서버는 User-Agent 필요)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': url,
                }

                response = await client.get(url, headers=headers, follow_redirects=True)

                logger.debug(f" Response status: {response.status_code}")
                logger.debug(f" Response content-type: {response.headers.get('content-type', 'unknown')}")

                if response.status_code == 200:
                    # Content-Type 검증 (이미지인지 확인)
                    content_type = response.headers.get('content-type', '').lower()

                    # Content-Type이 없거나 이미지가 아니면 content 시작 바이트로 판단
                    if not self._is_image_content(content_type):
                        # 이미지 시그니처 검사 (PNG, JPEG, GIF, WebP 등)
                        content_start = response.content[:16] if len(response.content) >= 16 else response.content
                        if not self._is_image_by_signature(content_start):
                            logger.debug(f" Not an image - content-type: {content_type}, signature: {content_start[:4].hex() if len(content_start) >= 4 else 'too short'}")
                            return None

                    # 파일 확장자 결정
                    ext = self._get_extension(url, content_type, response.content)

                    # 파일명 생성 (제품명_ID 기반)
                    filename = self._make_icon_filename(product_id, ext, product_title)
                    file_path = self.cache_dir / filename

                    # 파일 저장
                    with open(file_path, 'wb') as f:
                        f.write(response.content)

                    # 파일 크기 검증 (너무 작거나 크면 제외)
                    file_size = file_path.stat().st_size
                    logger.debug(f" Downloaded file size: {file_size} bytes")

                    if file_size < 100:  # 100 bytes 미만
                        file_path.unlink()  # 삭제
                        logger.debug(f" Icon too small: {file_size} bytes")
                        return None

                    if file_size > 5 * 1024 * 1024:  # 5MB 초과
                        file_path.unlink()
                        logger.debug(f" Icon too large: {file_size} bytes")
                        return None

                    # 상대 경로 반환 (웹에서 접근 가능한 경로)
                    logger.debug(f" Successfully saved to: /static/icons/{filename}")
                    return f"/static/icons/{filename}"

                else:
                    logger.debug(f" Failed to download icon: HTTP {response.status_code}")
                    logger.debug(f" Response text: {response.text[:200] if response.text else 'empty'}")
                    return None

        except httpx.TimeoutException:
            logger.debug(f" Timeout downloading icon from {url}")
            return None
        except Exception as e:
            logger.debug(f" Icon download error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _is_valid_url(self, url: str) -> bool:
        """URL 유효성 검증"""
        try:
            result = urlparse(url)
            return all([result.scheme in ('http', 'https'), result.netloc])
        except:
            return False

    def _is_image_content(self, content_type: str) -> bool:
        """Content-Type이 이미지인지 확인"""
        image_types = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/svg+xml', 'image/webp', 'image/avif']
        return any(img_type in content_type for img_type in image_types)

    def _is_image_by_signature(self, content_start: bytes) -> bool:
        """파일 시그니처로 이미지 형식 확인"""
        if len(content_start) < 4:
            return False

        # PNG: 89 50 4E 47
        if content_start[:4] == b'\x89PNG':
            return True

        # JPEG: FF D8 FF
        if content_start[:3] == b'\xff\xd8\xff':
            return True

        # GIF: 47 49 46 38
        if content_start[:4] in (b'GIF8', b'GIF9'):
            return True

        # WebP: 52 49 46 46 ... 57 45 42 50
        if len(content_start) >= 12 and content_start[:4] == b'RIFF' and content_start[8:12] == b'WEBP':
            return True

        # SVG (XML 시작)
        if content_start[:5] in (b'<?xml', b'<svg ', b'<SVG '):
            return True

        return False

    def _get_extension(self, url: str, content_type: str, content: bytes = None) -> str:
        """파일 확장자 결정"""
        # 1. Content 바이트 시그니처로 확인 (가장 확실한 방법)
        if content and len(content) >= 12:
            if content[:4] == b'\x89PNG':
                return '.png'
            elif content[:3] == b'\xff\xd8\xff':
                return '.jpg'
            elif content[:4] in (b'GIF8', b'GIF9'):
                return '.gif'
            elif content[:4] == b'RIFF' and content[8:12] == b'WEBP':
                return '.webp'
            elif content[:5] in (b'<?xml', b'<svg ', b'<SVG '):
                return '.svg'

        # 2. Content-Type 기반
        if 'png' in content_type:
            return '.png'
        elif 'jpeg' in content_type or 'jpg' in content_type:
            return '.jpg'
        elif 'gif' in content_type:
            return '.gif'
        elif 'svg' in content_type:
            return '.svg'
        elif 'webp' in content_type:
            return '.webp'

        # 3. URL 확장자 기반
        url_lower = url.lower()
        if url_lower.endswith('.png'):
            return '.png'
        elif url_lower.endswith('.jpg') or url_lower.endswith('.jpeg'):
            return '.jpg'
        elif url_lower.endswith('.gif'):
            return '.gif'
        elif url_lower.endswith('.svg'):
            return '.svg'
        elif url_lower.endswith('.webp'):
            return '.webp'

        # 4. 기본값
        return '.png'

    def delete_icon(self, product_id: int) -> bool:
        """
        제품 아이콘 삭제

        Args:
            product_id: 제품 ID

        Returns:
            삭제 성공 여부
        """
        deleted = False

        # 패턴 1: {product_id}{ext} (레거시 숫자 패턴)
        extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.avif']
        for ext in extensions:
            file_path = self.cache_dir / f"{product_id}{ext}"
            if file_path.exists():
                file_path.unlink()
                deleted = True

        # 패턴 2: *_{product_id}{ext} (이름 기반 패턴: Title_ID.ext)
        for file_path in self.cache_dir.glob(f"*_{product_id}.*"):
            if file_path.is_file():
                file_path.unlink()
                deleted = True

        # 패턴 3: {product_id}_*_icon{ext} (이전 패턴 - 하위 호환성)
        for file_path in self.cache_dir.glob(f"{product_id}_*_icon.*"):
            if file_path.is_file():
                file_path.unlink()
                deleted = True

        return deleted

    def get_icon_path(self, product_id: int) -> Optional[str]:
        """
        제품의 캐시된 아이콘 경로 조회

        Args:
            product_id: 제품 ID

        Returns:
            아이콘 경로 또는 None
        """
        # 이름 기반 패턴 우선: *_{product_id}.*
        for file_path in self.cache_dir.glob(f"*_{product_id}.*"):
            if file_path.is_file():
                return f"/static/icons/{file_path.name}"

        # 레거시 숫자 패턴: {product_id}{ext}
        extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.avif']
        for ext in extensions:
            file_path = self.cache_dir / f"{product_id}{ext}"
            if file_path.exists():
                return f"/static/icons/{product_id}{ext}"

        return None

    def cleanup_orphaned_icons(self, valid_product_ids: set) -> int:
        """
        사용되지 않는 아이콘 파일 정리

        Args:
            valid_product_ids: 유효한 제품 ID 집합

        Returns:
            삭제된 파일 수
        """
        deleted_count = 0

        for file_path in self.cache_dir.iterdir():
            if file_path.is_file():
                # 파일명에서 product_id 추출
                try:
                    product_id = int(file_path.stem)
                    if product_id not in valid_product_ids:
                        file_path.unlink()
                        deleted_count += 1
                except ValueError:
                    # 숫자가 아닌 파일은 건너뛰기
                    pass

        return deleted_count

    async def download_screenshots(
        self,
        urls: List[str],
        product_id: int,
        max_screenshots: int = 5
    ) -> Dict[str, List[str]]:
        """
        여러 스크린샷 다운로드 (하이브리드 전략)

        Args:
            urls: 스크린샷 URL 리스트
            product_id: 제품 ID
            max_screenshots: 최대 저장 개수

        Returns:
            {
                "local": ["/static/screenshots/123_screenshot_0.png", ...],
                "external": ["https://...", ...]
            }
        """
        local_screenshots = []
        external_screenshots = []
        local_count = 0

        for i, url in enumerate(urls):
            if local_count >= max_screenshots:
                # 최대 개수 도달 시 나머지는 external로
                external_screenshots.append(url)
                continue

            # 다운로드 시도
            local_path = await self._download_screenshot(url, product_id, local_count)

            if local_path:
                local_screenshots.append(local_path)
                local_count += 1
            else:
                # 다운로드 실패 시 외부 URL 사용
                external_screenshots.append(url)

        return {
            "local": local_screenshots,
            "external": external_screenshots
        }

    async def _download_screenshot(
        self,
        url: str,
        product_id: int,
        index: int
    ) -> Optional[str]:
        """
        단일 스크린샷 다운로드

        Args:
            url: 스크린샷 URL
            product_id: 제품 ID
            index: 스크린샷 인덱스 (0부터 시작)

        Returns:
            로컬 파일 경로 또는 None
        """
        if not url or not url.strip():
            return None

        if not self._is_valid_url(url):
            logger.error(f"Invalid screenshot URL: {url}")
            return None

        try:
            logger.debug(f" Downloading screenshot {index} from: {url}")

            async with httpx.AsyncClient(timeout=15.0) as client:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': url,
                }

                response = await client.get(url, headers=headers, follow_redirects=True)

                logger.debug(f" Screenshot {index} response status: {response.status_code}")

                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()

                    # Content-Type 또는 시그니처로 이미지 검증
                    if not self._is_image_content(content_type):
                        content_start = response.content[:16] if len(response.content) >= 16 else response.content
                        if not self._is_image_by_signature(content_start):
                            logger.debug(f" Screenshot {index} not an image - content-type: {content_type}")
                            return None

                    ext = self._get_extension(url, content_type, response.content)
                    filename = f"{product_id}_screenshot_{index}{ext}"
                    file_path = self.screenshot_cache_dir / filename

                    with open(file_path, 'wb') as f:
                        f.write(response.content)

                    file_size = file_path.stat().st_size
                    logger.debug(f" Screenshot {index} saved, size: {file_size} bytes")

                    if file_size < 100:
                        file_path.unlink()
                        logger.debug(f" Screenshot {index} too small: {file_size} bytes")
                        return None

                    if file_size > 5 * 1024 * 1024:
                        file_path.unlink()
                        logger.debug(f" Screenshot {index} too large: {file_size} bytes")
                        return None

                    return f"/static/screenshots/{filename}"

                else:
                    logger.debug(f" Failed to download screenshot {index}: HTTP {response.status_code}")
                    return None

        except Exception as e:
            logger.debug(f" Screenshot {index} download error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def delete_screenshots(self, product_id: int) -> int:
        """
        제품의 모든 스크린샷 삭제

        Args:
            product_id: 제품 ID

        Returns:
            삭제된 파일 수
        """
        deleted_count = 0

        # 패턴 1: {product_id}_screenshot_* (현재 표준 패턴)
        pattern1 = f"{product_id}_screenshot_*"
        for file_path in self.screenshot_cache_dir.glob(pattern1):
            if file_path.is_file():
                file_path.unlink()
                deleted_count += 1

        # 패턴 2: {product_id}_*_screenshot_* (이전 패턴 - 하위 호환성)
        pattern2 = f"{product_id}_*_screenshot_*"
        for file_path in self.screenshot_cache_dir.glob(pattern2):
            if file_path.is_file():
                file_path.unlink()
                deleted_count += 1

        return deleted_count

    def get_screenshot_paths(self, product_id: int) -> List[str]:
        """
        제품의 캐시된 스크린샷 경로 조회

        Args:
            product_id: 제품 ID

        Returns:
            스크린샷 경로 리스트
        """
        screenshots = []
        pattern = f"{product_id}_screenshot_*"

        for file_path in sorted(self.screenshot_cache_dir.glob(pattern)):
            if file_path.is_file():
                screenshots.append(f"/static/screenshots/{file_path.name}")

        return screenshots
