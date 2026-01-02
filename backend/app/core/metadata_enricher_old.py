"""
AI + 웹 크롤링 통합 메타데이터 생성기

전략:
1. 파일명 표준화 및 파싱
2. AI (Gemini/OpenAI): 기본 메타데이터 (제목, 간단한 설명, 제조사, 카테고리, 아이콘 URL)
3. 웹 크롤링: 상세 정보 (시스템 요구사양, 주요 기능, 지원 포맷, 릴리즈 정보 등)
"""
from typing import Dict, Optional
from datetime import datetime
from app.core.ai_metadata import AIMetadataGenerator
from app.core.web_crawler import WebCrawler
from app.core.filename_standardizer import FilenameStandardizer


class MetadataEnricher:
    """
    AI와 웹 크롤링을 결합한 통합 메타데이터 생성기
    """

    def __init__(
        self,
        ai_provider: str = "gemini",
        ai_model: str = "gemini-2.5-flash",
        use_ai: bool = True,
        use_web_crawling: bool = True
    ):
        """
        Args:
            ai_provider: AI 제공자 (gemini, openai, claude, azure)
            ai_model: AI 모델명
            use_ai: AI 사용 여부
            use_web_crawling: 웹 크롤링 사용 여부
        """
        self.use_ai = use_ai
        self.use_web_crawling = use_web_crawling

        # AI 메타데이터 생성기
        if self.use_ai:
            self.ai_generator = AIMetadataGenerator(
                provider=ai_provider,
                model=ai_model
            )
        else:
            self.ai_generator = None

        # 웹 크롤러
        if self.use_web_crawling:
            self.web_crawler = WebCrawler()
        else:
            self.web_crawler = None

    async def generate_metadata(
        self,
        filename: str,
        parent_folder: str = ""
    ) -> Dict:
        """
        AI + 웹 크롤링을 결합하여 완전한 메타데이터 생성

        Args:
            filename: 파일명
            parent_folder: 부모 폴더명

        Returns:
            {
                # AI 생성 기본 정보
                'title': str,
                'description': str,
                'vendor': str,
                'category': str,
                'icon_url': str,

                # 웹 크롤링 상세 정보
                'official_website': str,
                'license_type': str,
                'platform': str,
                'detailed_description': str,
                'features': List[str],
                'system_requirements': Dict,
                'supported_formats': Dict,
                'release_notes': str,
                'release_date': str,
                'crawled_from': Dict,
                'last_crawled_at': datetime
            }
        """
        metadata = {}

        # 1단계: AI로 기본 메타데이터 생성
        if self.use_ai and self.ai_generator:
            print(f"🤖 AI 메타데이터 생성 중: {filename}")
            try:
                ai_metadata = await self.ai_generator.generate_metadata(
                    filename=filename,
                    parent_folder=parent_folder
                )
                metadata.update(ai_metadata)
                print(f"✅ AI 메타데이터 생성 완료: {metadata.get('title', 'Unknown')}")
            except Exception as e:
                print(f"⚠️ AI 메타데이터 생성 실패: {e}")
                # AI 실패 시 파싱만으로 기본 정보 생성
                from app.core.parser import FilenameParser
                parser = FilenameParser()
                parsed = parser.parse(filename, parent_folder)
                metadata = {
                    'title': parsed.get('software_name', filename),
                    'description': f"{parsed.get('software_name', filename)} 소프트웨어",
                    'vendor': parsed.get('vendor', ''),
                    'category': 'Utility',
                    'icon_url': ''
                }

        # 2단계: 웹 크롤링으로 상세 정보 수집
        if self.use_web_crawling and self.web_crawler:
            # 파일명 표준화로 깨끗한 검색 쿼리 생성
            search_query = FilenameStandardizer.get_search_query(filename)

            print(f"🌐 웹 크롤링 시작: {search_query}")
            print(f"   (원본: {metadata.get('title', filename)})")

            try:
                # 표준화된 검색 쿼리 사용

                # 웹 크롤링 실행
                web_metadata = await self.web_crawler.search_web(search_query)

                # 웹 크롤링 결과 병합
                if web_metadata:
                    # 공식 웹사이트
                    if web_metadata.get('official_website'):
                        metadata['official_website'] = web_metadata['official_website']

                    # 상세 설명 (웹에서 가져온 것이 더 상세함)
                    if web_metadata.get('additional_info'):
                        metadata['detailed_description'] = web_metadata['additional_info']

                    # 스크린샷 수집
                    if web_metadata.get('screenshots'):
                        metadata['screenshots'] = web_metadata['screenshots']
                        # 첫 번째 스크린샷을 아이콘으로 활용 (AI가 아이콘을 못 찾은 경우)
                        if not metadata.get('icon_url'):
                            metadata['icon_url'] = web_metadata['screenshots'][0]

                    # 다운로드 URL
                    if web_metadata.get('download_url'):
                        metadata['download_url'] = web_metadata['download_url']

                    # 웹 소스 정보
                    if web_metadata.get('web_sources'):
                        metadata['crawled_from'] = {
                            source: True for source in web_metadata['web_sources']
                        }

                    print(f"✅ 웹 크롤링 완료: {len(web_metadata.get('web_sources', []))}개 소스")

            except Exception as e:
                print(f"⚠️ 웹 크롤링 실패: {e}")
                metadata['crawled_from'] = {'error': str(e)}

        # 크롤링 시간 기록
        metadata['last_crawled_at'] = datetime.now()

        return metadata

    async def enrich_existing_metadata(
        self,
        existing_metadata: Dict,
        force_recrawl: bool = False
    ) -> Dict:
        """
        기존 메타데이터를 보강

        Args:
            existing_metadata: 기존 메타데이터
            force_recrawl: 강제 재크롤링 여부

        Returns:
            보강된 메타데이터
        """
        # 기존 데이터를 유지하면서 보강
        enriched = existing_metadata.copy()

        # 이미 크롤링된 경우 force_recrawl이 아니면 스킵
        if not force_recrawl and existing_metadata.get('last_crawled_at'):
            print("📦 이미 크롤링된 데이터 존재, 스킵")
            return enriched

        # 웹 크롤링으로 상세 정보만 추가
        if self.use_web_crawling and self.web_crawler:
            software_name = existing_metadata.get('title', '')
            vendor = existing_metadata.get('vendor', '')

            if software_name:
                search_query = f"{vendor} {software_name}".strip()
                web_metadata = await self.web_crawler.search_web(search_query)

                if web_metadata:
                    # 없는 정보만 추가 (기존 정보 우선)
                    for key, value in web_metadata.items():
                        if key not in enriched or not enriched[key]:
                            enriched[key] = value

                    enriched['last_crawled_at'] = datetime.now()

        return enriched


# 편의 함수
async def generate_full_metadata(
    filename: str,
    parent_folder: str = "",
    use_ai: bool = True,
    use_web: bool = True
) -> Dict:
    """
    완전한 메타데이터 생성 (AI + 웹 크롤링)

    Args:
        filename: 파일명
        parent_folder: 부모 폴더명
        use_ai: AI 사용 여부
        use_web: 웹 크롤링 사용 여부

    Returns:
        완전한 메타데이터
    """
    enricher = MetadataEnricher(
        ai_provider="gemini",
        ai_model="gemini-2.5-flash",
        use_ai=use_ai,
        use_web_crawling=use_web
    )

    return await enricher.generate_metadata(filename, parent_folder)
