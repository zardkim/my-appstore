import httpx
from typing import List, Dict, Optional
import json
import logging
logger = logging.getLogger(__name__)



class GoogleImageSearcher:
    """
    Google Custom Search API를 사용한 이미지 검색
    """

    def __init__(self, api_key: str, search_engine_id: str):
        """
        Args:
            api_key: Google Custom Search API 키
            search_engine_id: Programmable Search Engine ID
        """
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"

    async def search_logo(self, query: str, limit: int = 5, offset: int = 0) -> List[Dict[str, str]]:
        """
        로고/아이콘 이미지 검색

        Args:
            query: 검색어 (예: "Adobe Photoshop logo" 또는 "Adobe Photoshop 로고")
                   프론트엔드에서 언어에 맞는 키워드를 포함해서 전달
            limit: 최대 결과 개수
            offset: 시작 위치 (0부터 시작, 최대 91)

        Returns:
            [{"url": str, "title": str, "thumbnail": str}, ...]
        """
        filters = {
            "imgType": "clipart",  # 로고/클립아트 우선
            "imgSize": "medium",
            "safe": "active"
        }

        return await self._make_request(query, filters, limit, offset)

    async def search_screenshots(self, query: str, limit: int = 10, offset: int = 0) -> List[Dict[str, str]]:
        """
        스크린샷 이미지 검색

        Args:
            query: 검색어 (예: "Adobe Photoshop screenshot" 또는 "Adobe Photoshop 스크린샷")
                   프론트엔드에서 언어에 맞는 키워드를 포함해서 전달
            limit: 최대 결과 개수
            offset: 시작 위치 (0부터 시작, 최대 91)

        Returns:
            [{"url": str, "title": str, "thumbnail": str}, ...]
        """
        filters = {
            "imgSize": "large",  # 큰 이미지 선호
            "safe": "active"
        }

        return await self._make_request(query, filters, limit, offset)

    async def _make_request(
        self,
        query: str,
        filters: Dict[str, str],
        limit: int,
        offset: int = 0
    ) -> List[Dict[str, str]]:
        """
        Google Custom Search API 요청 (최대 20개까지 2번 요청)

        Args:
            query: 검색어
            filters: 이미지 필터 (imgType, imgSize 등)
            limit: 최대 결과 개수
            offset: 시작 위치 (0부터 시작, 최대 91)

        Returns:
            검색 결과 리스트
        """
        try:
            logger.debug(f"Google Search] Query: '{query}'")
            logger.debug(f"Google Search] API Key: {self.api_key[:10]}...{self.api_key[-4:] if len(self.api_key) > 10 else ''}")
            logger.debug(f"Google Search] Search Engine ID: {self.search_engine_id}")
            logger.debug(f"Google Search] Filters: {filters}")
            logger.debug(f"Google Search] Requested limit: {limit}, offset: {offset}")

            # Google API는 start가 1부터 시작하고 최대 91까지만 가능
            # offset을 start로 변환: offset=0 → start=1, offset=20 → start=21
            start_index = offset + 1

            # start가 91을 넘으면 검색 불가
            if start_index > 91:
                logger.debug(f"Google Search] Start index {start_index} exceeds maximum (91)")
                return []

            all_results = []

            async with httpx.AsyncClient(timeout=10.0) as client:
                # Google API는 한 번에 최대 10개까지
                # 20개를 원하면 2번 요청 (start=offset+1, start=offset+11)
                batches = []
                if limit <= 10:
                    batches = [{"start": start_index, "num": min(limit, 10)}]
                else:
                    # 첫 번째 10개
                    batches.append({"start": start_index, "num": 10})
                    # 두 번째 10개 (또는 남은 개수)
                    remaining = min(limit - 10, 10)
                    next_start = start_index + 10
                    if remaining > 0 and next_start <= 91:
                        batches.append({"start": next_start, "num": remaining})

                for batch in batches:
                    params = {
                        "key": self.api_key,
                        "cx": self.search_engine_id,
                        "q": query,
                        "searchType": "image",
                        "start": batch["start"],
                        "num": batch["num"],
                        **filters
                    }

                    logger.debug(f"Google Search] Requesting batch: start={batch['start']}, num={batch['num']}")
                    logger.debug(f"Google Search] Full request params: {params}")
                    logger.debug(f"Google Search] Request URL: {self.base_url}")
                    response = await client.get(self.base_url, params=params)
                    logger.debug(f"Google Search] Response status: {response.status_code}")

                    if response.status_code == 200:
                        data = response.json()
                        items = data.get("items", [])
                        logger.debug(f"Google Search] Found {len(items)} results in this batch")

                        for item in items:
                            all_results.append({
                                "url": item.get("link", ""),
                                "title": item.get("title", ""),
                                "thumbnail": item.get("image", {}).get("thumbnailLink", ""),
                                "context_link": item.get("image", {}).get("contextLink", "")
                            })
                    elif response.status_code == 403:
                        error_data = response.json()
                        error_reason = error_data.get("error", {}).get("errors", [{}])[0].get("reason", "unknown")
                        logger.error(f"Google Search] ERROR 403: {error_reason}")
                        logger.error(f"Google Search] Response: {response.text}")

                        # 403 오류 시 예외 발생하여 상세 메시지 전달
                        if "quotaExceeded" in error_reason or "dailyLimitExceeded" in error_reason:
                            raise Exception("Google API 일일 할당량이 초과되었습니다.")
                        elif "keyInvalid" in error_reason:
                            raise Exception("Google API Key가 잘못되었습니다. 설정을 확인해주세요.")
                        else:
                            raise Exception(f"Google API 오류: {error_reason}")
                    elif response.status_code == 400:
                        error_data = response.json()
                        error_message = error_data.get("error", {}).get("message", "Invalid request")
                        logger.error(f"Google Search] ERROR 400: {error_message}")
                        logger.error(f"Google Search] Response: {response.text}")
                        raise Exception(f"Google API 요청 오류: {error_message}")
                    else:
                        logger.debug(f"Google Search] ERROR {response.status_code}")
                        logger.debug(f"Google Search] Response: {response.text}")
                        break

                logger.debug(f"Google Search] Total results: {len(all_results)}")
                return all_results

        except httpx.TimeoutException:
            logger.debug(f"Google Search] Timeout for query: {query}")
            return []

        except Exception as e:
            logger.error(f"Google Search] Exception: {e}")
            raise

    def is_configured(self) -> bool:
        """
        API 키와 Search Engine ID가 설정되어 있는지 확인

        Returns:
            설정 완료 여부
        """
        if not self.api_key or not self.search_engine_id:
            return False

        # Search Engine ID 형식 검증
        # OAuth 클라이언트 ID 형식 감지 (xxxxx.apps.googleusercontent.com)
        if '.apps.googleusercontent.com' in self.search_engine_id:
            logger.error(f"Invalid Search Engine ID format: {self.search_engine_id}")
            logger.error("This looks like an OAuth Client ID, not a Programmable Search Engine ID")
            logger.error("Please create a Programmable Search Engine at: https://programmablesearchengine.google.com/")
            return False

        return True
