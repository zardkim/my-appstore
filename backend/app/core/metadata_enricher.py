"""
AI 전용 메타데이터 생성기
웹 크롤링 없이 AI만 사용
"""
from typing import Dict
from app.core.ai_metadata import AIMetadataGeneratorV2


class MetadataEnricher:
    """
    AI 전용 메타데이터 생성 (크롤링 제거)
    """

    def __init__(self, ai_provider="openai", ai_model=None, use_ai=True):
        """
        Args:
            ai_provider: 'openai' 또는 'gemini'
            ai_model: 모델명 (None이면 최신 모델 사용)
            use_ai: AI 사용 여부
        """
        self.use_ai = use_ai

        if self.use_ai:
            self.ai_generator = AIMetadataGeneratorV2(
                provider=ai_provider,
                model=ai_model
            )

    async def generate_metadata(self, filename: str, parent_folder: str = "") -> Dict:
        """
        AI로 메타데이터 생성

        Args:
            filename: 파일명
            parent_folder: 부모 폴더명

        Returns:
            상세 메타데이터 dict
        """
        if not self.use_ai or not self.ai_generator:
            # AI 없이 기본 메타데이터만
            from app.core.parser import FilenameParser
            parser = FilenameParser()
            parsed = parser.parse(filename, parent_folder)

            return {
                'title': parsed['software_name'],
                'description_short': f"{parsed['software_name']} 소프트웨어",
                'vendor': parsed.get('vendor', ''),
                'category': 'Utility',
                'icon_url': ''
            }

        # AI로 상세 메타데이터 생성
        metadata = await self.ai_generator.generate_detailed_metadata(filename, parent_folder)

        return metadata
