"""
AI 전용 메타데이터 생성기 v2
- OpenAI GPT-4.5+ 지원
- Gemini 2.5+ 지원
- 상세한 메타데이터 생성 (메타데이터 예제 수준)
"""
import json
from typing import Dict, Optional
import httpx
from app.config import settings
from app.core.parser import FilenameParser
import logging
logger = logging.getLogger(__name__)



class AIMetadataGeneratorV2:
    """
    상세한 메타데이터를 생성하는 AI 생성기
    OpenAI GPT-4.5+, Gemini 2.5+ 지원
    """

    def __init__(self, provider: str = "openai", api_key: str = None, model: str = None):
        """
        Args:
            provider: AI 제공자 ('openai', 'gemini')
            api_key: API 키
            model: 모델명 (지정하지 않으면 최신 모델 사용)
        """
        self.provider = provider.lower()

        # API 키 설정
        if api_key:
            self.api_key = api_key
        elif self.provider == 'gemini':
            self.api_key = settings.GEMINI_API_KEY
        else:
            self.api_key = settings.OPENAI_API_KEY

        # 모델 설정 (최신 버전 우선)
        if model:
            self.model = model
        elif self.provider == 'gemini':
            # Gemini 2.5 이상
            self.model = "gemini-2.5-flash"  # 또는 gemini-2.5-pro
        else:
            # OpenAI GPT-4.5 이상
            self.model = "gpt-4o"  # gpt-4o는 GPT-4 Turbo 최신 버전

        self.parser = FilenameParser()

    async def generate_detailed_metadata(
        self,
        filename: str,
        parent_folder: str = "",
        custom_prompt: str = None
    ) -> Dict:
        """
        상세한 메타데이터 생성

        메타데이터 예제.md 수준의 상세 정보 포함:
        - 기본 정보 (제목, 버전, 플랫폼, 개발사, 카테고리, 라이선스 등)
        - 프로그램 설명 (짧은 요약, 상세 설명)
        - 주요 기능 리스트
        - 지원 파일 포맷
        - 시스템 요구 사양
        - 릴리즈 정보

        Args:
            filename: 파일명
            parent_folder: 상위 폴더명
            custom_prompt: 사용자 정의 프롬프트 (None이면 기본 프롬프트 사용)
        """
        # 1단계: 파일명 파싱
        parsed = self.parser.parse(filename, parent_folder)

        # 2단계: AI 질의
        if self.api_key and self.api_key.strip():
            if self.provider == 'openai':
                metadata = await self._query_openai_detailed(parsed, custom_prompt)
            elif self.provider == 'gemini':
                metadata = await self._query_gemini_detailed(parsed, custom_prompt)
            else:
                logger.debug(f"Unknown provider: {self.provider}, falling back")
                metadata = self._fallback_metadata(parsed)
        else:
            metadata = self._fallback_metadata(parsed)

        return metadata

    async def _query_openai_detailed(self, parsed_info: Dict, custom_prompt: str = None) -> Dict:
        """OpenAI GPT-4.5+ API로 상세 메타데이터 생성"""
        software_name = parsed_info['software_name']
        version = parsed_info.get('version', '')
        year = parsed_info.get('year', '')

        context_parts = [software_name]
        if version:
            context_parts.append(f"버전 {version}")
        if year:
            context_parts.append(f"({year})")

        software_context = ' '.join(context_parts)

        # 커스텀 프롬프트가 있으면 사용, 없으면 기본 프롬프트 사용
        if custom_prompt:
            prompt = custom_prompt
        else:
            # 상세 메타데이터 프롬프트
            prompt = f"""다음 소프트웨어에 대한 상세한 메타데이터를 JSON 형식으로 제공해주세요:

소프트웨어: {software_context}

다음 정보를 포함한 JSON 객체를 작성해주세요:

**기본 정보:**
- title: 정확한 공식 소프트웨어 이름
- version: 버전 정보 (알려진 경우)
- platform: 플랫폼 (예: Windows, macOS, Linux, Cross-platform)
- developer: 개발사/제조사 공식 이름
- category: 소프트웨어의 **주요 기능**을 기준으로 가장 적합한 카테고리 선택
  * Graphics: 이미지 편집, 그래픽 디자인, 3D 모델링
  * Media: 비디오/오디오 편집, 미디어 재생, 영상 제작, 화면 녹화
  * Office: 문서 작성, 스프레드시트, 프레젠테이션
  * Business: 회계, ERP, CRM, 업무 관리 (미디어 제작 도구는 Media)
  * Development: 프로그래밍, IDE, 개발 도구
  * Utility: 시스템 유틸리티, 최적화 도구
  * 기타: Security, Network, OS, Engineering, Hardware, Uncategorized 등
- official_website: 공식 웹사이트 URL (알려진 경우)
- icon_url: 공식 로고/아이콘 이미지 URL (PNG, SVG, ICO 등)
  * 공식 웹사이트의 파비콘, 로고 이미지, 앱 아이콘 등
  * 찾을 수 없으면 빈 문자열 ""
- license_type: 라이선스 종류 (Free, Freemium, Trial, Commercial, Open Source 등)
- language: 지원 언어 (예: "영어, 한국어, 일본어" 또는 "다국어")

**프로그램 설명:**
- description_short: 50-100자 이내의 간결한 설명 (한 문장)
- description_detailed: 200-300자 이내의 상세 설명 (소프트웨어의 주요 특징과 용도를 자세히)

**주요 기능:** (최대 5-10개)
- features: 주요 기능 리스트 배열 (예: ["사진 라이브러리 관리 (태그/평점/카테고리)", "RAW 이미지 지원", "비파괴 편집"])

**지원 파일 포맷:** (해당되는 경우)
- supported_formats: 지원 파일 포맷 배열 (예: ["JPEG", "PNG", "PSD", "RAW"])

**시스템 요구 사양:**
- system_requirements: {{
    "os": "운영체제 요구사항 (구체적으로)",
    "cpu": "CPU 요구사항",
    "ram": "RAM 요구사항 (최소/권장)",
    "disk_space": "디스크 공간",
    "gpu": "GPU 요구사항 (있는 경우)",
    "additional": "추가 요구사항 (있는 경우)"
  }}

**설치 정보:**
- installation_info: {{
    "installer_type": "설치 방식 (예: DMG 마운트 → Applications 복사, EXE 실행, 압축 해제)",
    "file_size": "예상 파일 크기 (예: 약 500MB)",
    "internet_required": "인터넷 필요 여부 (예: 라이선스 인증 시 필요, 불필요)"
  }}

**릴리즈 정보:**
- release_notes: 주요 릴리즈 노트 또는 버전 히스토리 (알려진 경우, 2-3줄)

**중요:**
- 응답은 반드시 유효한 JSON 형식만 작성하세요
- 추가 설명이나 코멘트를 포함하지 마세요
- 확실하지 않은 정보는 빈 문자열("") 또는 빈 배열([])을 사용하세요
- 모든 필드를 반드시 포함해야 합니다
- 상세하고 구체적인 정보를 제공하세요

예시:
{{
  "title": "ACDSee Photo Studio",
  "version": "7.1",
  "platform": "macOS",
  "developer": "ACD Systems International Inc.",
  "category": "Graphics",
  "official_website": "https://www.acdsee.com",
  "icon_url": "",
  "license_type": "Commercial",
  "language": "영어 (기본), 다국어 인터페이스 가능",
  "description_short": "사진을 빠르게 관리·정리하고, 색보정 및 편집까지 가능한 전문 사진 관리 소프트웨어",
  "description_detailed": "ACDSee Photo Studio for Mac은 대용량 사진 라이브러리를 빠르게 탐색하고, RAW 파일을 포함한 다양한 이미지 포맷을 지원합니다. 비파괴 편집 워크플로우로 색상 보정, 노출 조절, 디테일 보정이 가능하며, 태그, 카테고리, 평점 기반 사진 관리 기능을 제공합니다. Adobe Lightroom 대안으로 자주 사용됩니다.",
  "features": [
    "사진 라이브러리 관리 (태그/평점/카테고리)",
    "RAW 이미지 지원",
    "색상 보정/화이트밸런스/노출 조절",
    "비파괴 편집 (Undo/Redo 자유)",
    "고속 이미지 뷰어",
    "메타데이터(EXIF/IPTC) 편집",
    "일괄(Batch) 처리"
  ],
  "supported_formats": ["JPEG", "PNG", "TIFF", "BMP", "RAW (Canon, Nikon, Sony 등)", "PSD (부분 지원)"],
  "system_requirements": {{
    "os": "macOS 10.15 (Catalina) 이상",
    "cpu": "Intel Mac / Apple Silicon (M1 이상, Rosetta 지원)",
    "ram": "최소 4GB (8GB 이상 권장)",
    "disk_space": "설치용 약 2GB 이상",
    "gpu": "Metal 지원 GPU 권장",
    "additional": ""
  }},
  "installation_info": {{
    "installer_type": "DMG 마운트 → Applications 폴더로 복사",
    "file_size": "약 500MB 내외",
    "internet_required": "설치 후 라이선스 인증 시 필요"
  }},
  "release_notes": "7.0 버전: macOS 버전 주요 UI 개선. 7.1 버전: 안정성 개선 및 버그 수정, Apple Silicon 최적화 강화"
}}"""

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert software analyst. You provide comprehensive, accurate metadata about software applications in JSON format. Your responses are detailed, well-structured, and factually correct."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 4096
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content'].strip()

                    # JSON 추출 및 파싱
                    extracted_json = self._extract_json(content)
                    metadata = json.loads(extracted_json)

                    # AI 원본 응답 저장 (디버깅용)
                    metadata['ai_raw_response'] = content
                    metadata['ai_provider'] = 'openai'

                    logger.debug(f"✅ OpenAI 상세 메타데이터 생성 완료: {metadata.get('title')}")
                    return metadata
                else:
                    error_text = response.text
                    logger.debug(f"OpenAI API error: {response.status_code} - {error_text}")
                    return self._fallback_metadata(parsed_info)

        except json.JSONDecodeError as e:
            logger.debug(f"JSON parsing error (OpenAI): {e}")
            return self._fallback_metadata(parsed_info)
        except Exception as e:
            logger.debug(f"OpenAI API Error: {e}")
            return self._fallback_metadata(parsed_info)

    async def _query_gemini_detailed(self, parsed_info: Dict, custom_prompt: str = None) -> Dict:
        """Gemini 2.5+ API로 상세 메타데이터 생성"""
        software_name = parsed_info['software_name']
        version = parsed_info.get('version', '')
        year = parsed_info.get('year', '')

        context_parts = [software_name]
        if version:
            context_parts.append(f"버전 {version}")
        if year:
            context_parts.append(f"({year})")

        software_context = ' '.join(context_parts)

        # 커스텀 프롬프트가 있으면 사용, 없으면 기본 프롬프트 사용
        if custom_prompt:
            prompt = custom_prompt
        else:
            # Gemini용 상세 프롬프트 (OpenAI와 동일)
            prompt = f"""다음 소프트웨어에 대한 상세한 메타데이터를 JSON 형식으로 제공해주세요:

소프트웨어: {software_context}

다음 정보를 포함한 JSON 객체를 작성해주세요:

**기본 정보:**
- title: 정확한 공식 소프트웨어 이름
- version: 버전 정보 (알려진 경우)
- platform: 플랫폼 (예: Windows, macOS, Linux, Cross-platform)
- developer: 개발사/제조사 공식 이름
- category: 소프트웨어의 **주요 기능**을 기준으로 가장 적합한 카테고리 선택
  * Graphics: 이미지 편집, 그래픽 디자인, 3D 모델링
  * Media: 비디오/오디오 편집, 미디어 재생, 영상 제작, 화면 녹화
  * Office: 문서 작성, 스프레드시트, 프레젠테이션
  * Business: 회계, ERP, CRM, 업무 관리 (미디어 제작 도구는 Media)
  * Development: 프로그래밍, IDE, 개발 도구
  * Utility: 시스템 유틸리티, 최적화 도구
  * 기타: Security, Network, OS, Engineering, Hardware, Uncategorized 등
- official_website: 공식 웹사이트 URL (알려진 경우)
- icon_url: 공식 로고/아이콘 이미지 URL (PNG, SVG, ICO 등)
  * 공식 웹사이트의 파비콘, 로고 이미지, 앱 아이콘 등
  * 찾을 수 없으면 빈 문자열 ""
- license_type: 라이선스 종류 (Free, Freemium, Trial, Commercial, Open Source 등)
- language: 지원 언어 (예: "영어, 한국어, 일본어" 또는 "다국어")

**프로그램 설명:**
- description_short: 50-100자 이내의 간결한 설명 (한 문장)
- description_detailed: 200-300자 이내의 상세 설명 (소프트웨어의 주요 특징과 용도를 자세히)

**주요 기능:** (최대 5-10개)
- features: 주요 기능 리스트 배열 (예: ["사진 라이브러리 관리 (태그/평점/카테고리)", "RAW 이미지 지원"])

**지원 파일 포맷:** (해당되는 경우)
- supported_formats: 지원 파일 포맷 배열 (예: ["JPEG", "PNG", "PSD"])

**시스템 요구 사양:**
- system_requirements: {{
    "os": "운영체제 요구사항 (구체적으로)",
    "cpu": "CPU 요구사항",
    "ram": "RAM 요구사항 (최소/권장)",
    "disk_space": "디스크 공간",
    "gpu": "GPU 요구사항 (있는 경우)",
    "additional": "추가 요구사항 (있는 경우)"
  }}

**설치 정보:**
- installation_info: {{
    "installer_type": "설치 방식 (예: DMG 마운트 → Applications 복사, EXE 실행, 압축 해제)",
    "file_size": "예상 파일 크기 (예: 약 500MB)",
    "internet_required": "인터넷 필요 여부 (예: 라이선스 인증 시 필요, 불필요)"
  }}

**릴리즈 정보:**
- release_notes: 주요 릴리즈 노트 또는 버전 히스토리 (알려진 경우, 2-3줄)

**중요:**
- 응답은 반드시 유효한 JSON 형식만 작성하세요
- 추가 설명이나 코멘트를 포함하지 마세요
- 확실하지 않은 정보는 빈 문자열("") 또는 빈 배열([])을 사용하세요
- 모든 필드를 반드시 포함해야 합니다
- 상세하고 구체적인 정보를 제공하세요"""

        try:
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    api_url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{
                            "parts": [{"text": prompt}]
                        }],
                        "generationConfig": {
                            "temperature": 0.3,
                            "maxOutputTokens": 8192
                        }
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.debug(f"📥 Gemini 원본 응답: {result}")

                    if 'candidates' in result and len(result['candidates']) > 0:
                        content = result['candidates'][0]['content']['parts'][0]['text'].strip()
                        logger.debug(f"📄 Gemini 텍스트 응답 (첫 500자): {content[:500]}")

                        # JSON 추출 및 파싱
                        extracted_json = self._extract_json(content)
                        logger.debug(f"🔍 추출된 JSON (첫 500자): {extracted_json[:500]}")

                        metadata = json.loads(extracted_json)

                        # AI 원본 응답 저장 (디버깅용)
                        metadata['ai_raw_response'] = content
                        metadata['ai_provider'] = 'gemini'

                        logger.debug(f"✅ Gemini 상세 메타데이터 생성 완료: {metadata.get('title')}")
                        return metadata
                    else:
                        logger.debug(f"❌ Gemini API unexpected response: {result}")
                        return self._fallback_metadata(parsed_info)
                else:
                    logger.debug(f"❌ Gemini API error: {response.status_code} - {response.text}")
                    return self._fallback_metadata(parsed_info)

        except json.JSONDecodeError as e:
            logger.debug(f"❌ JSON parsing error (Gemini): {e}")
            logger.debug(f"   파싱 시도한 텍스트: {extracted_json if 'extracted_json' in locals() else 'N/A'}")
            return self._fallback_metadata(parsed_info)
        except Exception as e:
            logger.debug(f"❌ Gemini API Error: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_metadata(parsed_info)

    def _extract_json(self, text: str) -> str:
        """텍스트에서 JSON 추출 (마크다운 코드 블록 제거)"""
        text = text.strip()
        if text.startswith('```'):
            lines = text.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            text = '\n'.join(lines)

        return text.strip()

    def _fallback_metadata(self, parsed_info: Dict) -> Dict:
        """AI 실패 시 기본 메타데이터"""
        software_name = parsed_info['software_name']

        return {
            'title': software_name,
            'version': parsed_info.get('version', ''),
            'platform': 'Windows',
            'developer': parsed_info.get('vendor', ''),
            'category': 'Utility',
            'official_website': '',
            'license_type': '',
            'language': '',
            'description_short': f"{software_name} 소프트웨어",
            'description_detailed': '',
            'features': [],
            'supported_formats': [],
            'system_requirements': {
                'os': '',
                'cpu': '',
                'ram': '',
                'disk_space': '',
                'gpu': '',
                'additional': ''
            },
            'installation_info': {
                'installer_type': '',
                'file_size': '',
                'internet_required': ''
            },
            'release_notes': ''
        }
