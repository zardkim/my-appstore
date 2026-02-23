import httpx
from typing import List, Dict
import logging
logger = logging.getLogger(__name__)


class BingImageSearcher:
    """
    Bing Image Search API를 사용한 이미지 검색
    (Azure Cognitive Services - 월 1,000건 무료)
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.bing.microsoft.com/v7.0/images/search"

    async def search_logo(self, query: str, limit: int = 5, offset: int = 0) -> List[Dict[str, str]]:
        filters = {
            "imageType": "Clipart",
            "size": "Medium",
            "safeSearch": "Moderate"
        }
        return await self._make_request(query, filters, limit, offset)

    async def search_screenshots(self, query: str, limit: int = 10, offset: int = 0) -> List[Dict[str, str]]:
        filters = {
            "imageType": "Photo",
            "size": "Large",
            "safeSearch": "Moderate"
        }
        return await self._make_request(query, filters, limit, offset)

    async def _make_request(
        self,
        query: str,
        filters: Dict[str, str],
        limit: int,
        offset: int = 0
    ) -> List[Dict[str, str]]:
        try:
            logger.debug(f"Bing Search] Query: '{query}', limit={limit}, offset={offset}")
            logger.debug(f"Bing Search] Filters: {filters}")

            params = {
                "q": query,
                "count": min(limit, 150),
                "offset": offset,
                **filters
            }
            headers = {
                "Ocp-Apim-Subscription-Key": self.api_key
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.base_url, params=params, headers=headers)
                logger.debug(f"Bing Search] Response status: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    items = data.get("value", [])
                    total = data.get("totalEstimatedMatches", 0)
                    logger.debug(f"Bing Search] Found {len(items)} results (totalEstimatedMatches={total})")

                    return [
                        {
                            "url": item.get("contentUrl", ""),
                            "title": item.get("name", ""),
                            "thumbnail": item.get("thumbnailUrl", ""),
                            "context_link": item.get("hostPageUrl", "")
                        }
                        for item in items
                    ]

                elif response.status_code == 401:
                    raise Exception("Bing API 키가 잘못되었습니다. 설정에서 API 키를 확인해주세요.")
                elif response.status_code == 403:
                    raise Exception("Bing API 접근이 거부되었습니다. API 키와 Azure 구독 상태를 확인해주세요.")
                elif response.status_code == 429:
                    raise Exception("Bing API 월간 한도에 도달했습니다. (무료 한도: 월 1,000건)")
                else:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", {}).get("message", f"HTTP {response.status_code}")
                    except Exception:
                        error_msg = f"HTTP {response.status_code}"
                    logger.error(f"Bing Search] ERROR: {error_msg}, body: {response.text[:200]}")
                    raise Exception(f"Bing API 오류: {error_msg}")

        except httpx.TimeoutException:
            logger.debug(f"Bing Search] Timeout for query: {query}")
            return []
        except Exception as e:
            logger.error(f"Bing Search] Exception: {e}")
            raise

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())
