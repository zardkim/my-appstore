import json
from typing import Dict, Optional
import httpx
from app.config import settings
from app.core.parser import FilenameParser


class AIMetadataGenerator:
    """
    다중 AI 제공자(OpenAI, Gemini, Azure, Claude)를 지원하는 메타데이터 생성기
    """

    def __init__(self, provider: str = "openai", api_key: str = None, model: str = None, endpoint: str = None):
        """
        Args:
            provider: AI 제공자 ('openai', 'gemini', 'azure', 'claude')
            api_key: API 키
            model: 모델명
            endpoint: 엔드포인트 (Azure 전용)
        """
        self.provider = provider.lower()

        # Provider에 따라 기본 API 키 설정
        if api_key:
            self.api_key = api_key
        elif self.provider == 'gemini':
            self.api_key = settings.GEMINI_API_KEY
        else:
            self.api_key = settings.OPENAI_API_KEY

        # Provider에 따라 기본 모델 설정
        if model:
            self.model = model
        elif self.provider == 'gemini':
            self.model = "gemini-2.5-pro"  # Gemini 최신 프로 버전
        else:
            self.model = "gpt-4o-mini"

        self.endpoint = endpoint  # Azure OpenAI용
        self.parser = FilenameParser()

    async def generate_metadata(
        self,
        filename: str,
        parent_folder: str = ""
    ) -> Dict:
        """
        파일명으로부터 메타데이터 생성

        Args:
            filename: 파일명 또는 폴더명
            parent_folder: 부모 폴더명 (컨텍스트)

        Returns:
            {
                'title': str,
                'description': str,
                'vendor': str,
                'category': str,
                'icon_url': str
            }
        """
        # 1단계: 파일명 파싱
        parsed = self.parser.parse(filename, parent_folder)

        # 2단계: AI에게 질의 (API 키가 있는 경우)
        if self.api_key and self.api_key.strip():
            # Provider에 따라 적절한 메서드 호출
            if self.provider == 'openai':
                metadata = await self._query_openai(parsed)
            elif self.provider == 'gemini':
                metadata = await self._query_gemini(parsed)
            elif self.provider == 'azure':
                metadata = await self._query_azure(parsed)
            elif self.provider == 'claude':
                metadata = await self._query_claude(parsed)
            else:
                print(f"Unknown provider: {self.provider}, falling back to OpenAI")
                metadata = await self._query_openai(parsed)
        else:
            # API 키가 없으면 파싱 정보만으로 fallback
            metadata = self._fallback_metadata(parsed)

        # 3단계: 메타데이터 정제
        cleaned_metadata = self.parser.clean_metadata(metadata)

        return cleaned_metadata

    async def _query_openai(self, parsed_info: Dict) -> Dict:
        """
        OpenAI API 호출하여 메타데이터 생성
        """
        software_name = parsed_info['software_name']
        version = parsed_info.get('version', '')
        year = parsed_info.get('year', '')

        # 컨텍스트 구성
        context_parts = [software_name]
        if version:
            context_parts.append(f"버전 {version}")
        if year:
            context_parts.append(f"({year})")

        software_context = ' '.join(context_parts)

        # AI 프롬프트 작성
        prompt = f"""다음 소프트웨어에 대한 정보를 JSON 형식으로 제공해주세요:

소프트웨어: {software_context}

다음 정보를 포함한 JSON 객체를 작성해주세요:
1. title: 정확한 공식 소프트웨어 이름 (예: "Adobe Photoshop", "Microsoft Office")
2. description: 50-100자 이내의 간단하고 명확한 설명 (무엇을 하는 소프트웨어인지)
3. vendor: 공식 제조사/개발사 이름 (예: "Adobe", "Microsoft")
4. category: 다음 중 하나를 선택
   - Graphics (그래픽/디자인)
   - Office (오피스/문서)
   - Development (개발도구)
   - Utility (유틸리티)
   - Media (미디어/영상/음악)
   - OS (운영체제)
   - Security (보안)
   - Network (네트워크)
   - Mac (맥 전용)
   - Mobile (모바일)
   - Patch (패치/업데이트)
   - Driver (드라이버)
   - Source (소스코드)
   - Backup (백업&복구)
   - Portable (포터블 앱)
   - Business (업무용)
   - Engineering (공학용)
   - Theme (테마&스킨)
   - Hardware (하드웨어 관련)
   - Uncategorized (미분류)
5. icon_url: 공식 아이콘 이미지 URL (PNG 또는 JPG, 찾을 수 없으면 빈 문자열)

중요:
- 응답은 반드시 유효한 JSON 형식만 작성하세요
- 추가 설명이나 코멘트를 포함하지 마세요
- 확실하지 않은 정보는 빈 문자열("")을 사용하세요

예시:
{{
  "title": "Adobe Photoshop",
  "description": "전문가용 이미지 편집 및 그래픽 디자인 소프트웨어",
  "vendor": "Adobe",
  "category": "Graphics",
  "icon_url": "https://example.com/icon.png"
}}"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
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
                                "content": "You are a software information expert. You provide accurate, concise information about software applications in JSON format only."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 500
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content'].strip()

                    # JSON 파싱 (코드 블록 제거)
                    content = self._extract_json(content)
                    metadata = json.loads(content)

                    # 필수 필드 검증
                    return self._validate_metadata(metadata, parsed_info)
                else:
                    print(f"OpenAI API error: {response.status_code} - {response.text}")
                    return self._fallback_metadata(parsed_info)

        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return self._fallback_metadata(parsed_info)
        except Exception as e:
            print(f"AI API Error: {e}")
            return self._fallback_metadata(parsed_info)

    def _extract_json(self, text: str) -> str:
        """
        텍스트에서 JSON 추출 (마크다운 코드 블록 제거)
        """
        # ```json ... ``` 형식 제거
        text = text.strip()
        if text.startswith('```'):
            # 첫 줄과 마지막 줄 제거
            lines = text.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            text = '\n'.join(lines)

        return text.strip()

    def _validate_metadata(self, metadata: Dict, parsed_info: Dict) -> Dict:
        """
        AI 응답 검증 및 누락된 필드 채우기
        """
        validated = {
            'title': metadata.get('title', '').strip(),
            'description': metadata.get('description', '').strip(),
            'vendor': metadata.get('vendor', '').strip(),
            'category': metadata.get('category', 'Utility'),
            'icon_url': metadata.get('icon_url', '').strip()
        }

        # 필수 필드가 비어있으면 파싱 정보로 대체
        if not validated['title']:
            validated['title'] = parsed_info['software_name']

        if not validated['vendor'] and parsed_info.get('vendor'):
            validated['vendor'] = parsed_info['vendor']

        # description이 비어있으면 기본 설명 생성
        if not validated['description']:
            validated['description'] = f"{validated['title']} 소프트웨어"

        return validated

    def _fallback_metadata(self, parsed_info: Dict) -> Dict:
        """
        AI 호출 실패 시 파싱 정보로 메타데이터 생성
        """
        software_name = parsed_info['software_name']
        vendor = parsed_info.get('vendor', 'Unknown')

        return {
            'title': software_name,
            'description': f"{software_name} 소프트웨어",
            'vendor': vendor,
            'category': self._guess_category(software_name),
            'icon_url': ''
        }

    def _guess_category(self, software_name: str) -> str:
        """
        소프트웨어 이름으로 카테고리 추측
        """
        name_lower = software_name.lower()

        category_keywords = {
            'Graphics': ['photoshop', 'illustrator', 'gimp', 'inkscape', 'blender', '3ds', 'maya'],
            'Office': ['office', 'word', 'excel', 'powerpoint', 'outlook', 'onenote', 'libre'],
            'Development': ['visual studio', 'pycharm', 'intellij', 'eclipse', 'vscode', 'git', 'docker', 'java', 'python', 'node'],
            'Media': ['premiere', 'after effects', 'audacity', 'vlc', 'spotify', 'itunes', 'media player'],
            'OS': ['windows', 'ubuntu', 'centos', 'macos', 'linux'],
            'Security': ['antivirus', 'vpn', 'firewall', 'kaspersky', 'norton', 'avast'],
            'Game': ['steam', 'epic', 'origin', 'game', 'ubisoft'],
            'Network': ['chrome', 'firefox', 'edge', 'safari', 'browser', 'ftp', 'ssh']
        }

        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in name_lower:
                    return category

        return 'Uncategorized'  # 기본값: 분류할 수 없는 경우 미분류

    async def _query_gemini(self, parsed_info: Dict) -> Dict:
        """
        Google Gemini API 호출하여 메타데이터 생성
        """
        software_name = parsed_info['software_name']
        version = parsed_info.get('version', '')
        year = parsed_info.get('year', '')

        # 컨텍스트 구성
        context_parts = [software_name]
        if version:
            context_parts.append(f"버전 {version}")
        if year:
            context_parts.append(f"({year})")

        software_context = ' '.join(context_parts)

        # Gemini 프롬프트
        prompt = f"""다음 소프트웨어에 대한 정보를 JSON 형식으로 제공해주세요:

소프트웨어: {software_context}

다음 정보를 포함한 JSON 객체를 작성해주세요:
1. title: 정확한 공식 소프트웨어 이름
2. description: 50-100자 이내의 간단하고 명확한 설명
3. vendor: 공식 제조사/개발사 이름
4. category: Graphics, Office, Development, Utility, Media, OS, Security, Network, Mac, Mobile, Patch, Driver, Source, Backup, Portable, Business, Engineering, Theme, Hardware, Font, Uncategorized 중 하나
5. icon_url: 공식 아이콘 이미지 URL (찾을 수 없으면 빈 문자열)

중요:
- 응답은 반드시 유효한 JSON 형식만 작성하세요
- 추가 설명이나 코멘트를 포함하지 마세요
- 확실하지 않은 정보는 빈 문자열("")을 사용하세요

예시:
{{
  "title": "Adobe Photoshop",
  "description": "전문가용 이미지 편집 및 그래픽 디자인 소프트웨어",
  "vendor": "Adobe",
  "category": "Graphics",
  "icon_url": "https://example.com/icon.png"
}}"""

        try:
            # Gemini API 엔드포인트 (v1beta 사용)
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    api_url,
                    headers={
                        "Content-Type": "application/json"
                    },
                    json={
                        "contents": [{
                            "parts": [{
                                "text": prompt
                            }]
                        }],
                        "generationConfig": {
                            "temperature": 0.3,
                            "maxOutputTokens": 500
                        }
                    }
                )

                if response.status_code == 200:
                    result = response.json()

                    # Gemini 응답 구조: candidates[0].content.parts[0].text
                    if 'candidates' in result and len(result['candidates']) > 0:
                        content = result['candidates'][0]['content']['parts'][0]['text'].strip()

                        # JSON 파싱
                        content = self._extract_json(content)
                        metadata = json.loads(content)

                        return self._validate_metadata(metadata, parsed_info)
                    else:
                        print(f"Gemini API unexpected response: {result}")
                        return self._fallback_metadata(parsed_info)
                else:
                    print(f"Gemini API error: {response.status_code} - {response.text}")
                    return self._fallback_metadata(parsed_info)

        except json.JSONDecodeError as e:
            print(f"JSON parsing error (Gemini): {e}")
            return self._fallback_metadata(parsed_info)
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return self._fallback_metadata(parsed_info)

    async def _query_azure(self, parsed_info: Dict) -> Dict:
        """
        Azure OpenAI API 호출하여 메타데이터 생성
        """
        if not self.endpoint:
            print("Azure endpoint not configured, falling back")
            return self._fallback_metadata(parsed_info)

        software_name = parsed_info['software_name']
        version = parsed_info.get('version', '')
        year = parsed_info.get('year', '')

        # 컨텍스트 구성
        context_parts = [software_name]
        if version:
            context_parts.append(f"버전 {version}")
        if year:
            context_parts.append(f"({year})")

        software_context = ' '.join(context_parts)

        # Azure OpenAI 프롬프트 (OpenAI와 동일)
        prompt = f"""다음 소프트웨어에 대한 정보를 JSON 형식으로 제공해주세요:

소프트웨어: {software_context}

다음 정보를 포함한 JSON 객체를 작성해주세요:
1. title: 정확한 공식 소프트웨어 이름
2. description: 50-100자 이내의 간단하고 명확한 설명
3. vendor: 공식 제조사/개발사 이름
4. category: Graphics, Office, Development, Utility, Media, OS, Security, Network, Mac, Mobile, Patch, Driver, Source, Backup, Portable, Business, Engineering, Theme, Hardware, Font, Uncategorized 중 하나
5. icon_url: 공식 아이콘 이미지 URL (찾을 수 없으면 빈 문자열)

중요:
- 응답은 반드시 유효한 JSON 형식만 작성하세요
- 추가 설명이나 코멘트를 포함하지 마세요
- 확실하지 않은 정보는 빈 문자열("")을 사용하세요

예시:
{{
  "title": "Adobe Photoshop",
  "description": "전문가용 이미지 편집 및 그래픽 디자인 소프트웨어",
  "vendor": "Adobe",
  "category": "Graphics",
  "icon_url": "https://example.com/icon.png"
}}"""

        try:
            # Azure OpenAI 엔드포인트: {endpoint}/openai/deployments/{model}/chat/completions?api-version=2024-02-15-preview
            api_version = "2024-08-01-preview"
            api_url = f"{self.endpoint}/openai/deployments/{self.model}/chat/completions?api-version={api_version}"

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    api_url,
                    headers={
                        "api-key": self.api_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a software information expert. You provide accurate, concise information about software applications in JSON format only."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 500
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content'].strip()

                    # JSON 파싱
                    content = self._extract_json(content)
                    metadata = json.loads(content)

                    return self._validate_metadata(metadata, parsed_info)
                else:
                    print(f"Azure OpenAI API error: {response.status_code} - {response.text}")
                    return self._fallback_metadata(parsed_info)

        except json.JSONDecodeError as e:
            print(f"JSON parsing error (Azure): {e}")
            return self._fallback_metadata(parsed_info)
        except Exception as e:
            print(f"Azure OpenAI API Error: {e}")
            return self._fallback_metadata(parsed_info)

    async def _query_claude(self, parsed_info: Dict) -> Dict:
        """
        Anthropic Claude API 호출하여 메타데이터 생성
        """
        software_name = parsed_info['software_name']
        version = parsed_info.get('version', '')
        year = parsed_info.get('year', '')

        # 컨텍스트 구성
        context_parts = [software_name]
        if version:
            context_parts.append(f"버전 {version}")
        if year:
            context_parts.append(f"({year})")

        software_context = ' '.join(context_parts)

        # Claude 프롬프트
        prompt = f"""다음 소프트웨어에 대한 정보를 JSON 형식으로 제공해주세요:

소프트웨어: {software_context}

다음 정보를 포함한 JSON 객체를 작성해주세요:
1. title: 정확한 공식 소프트웨어 이름
2. description: 50-100자 이내의 간단하고 명확한 설명
3. vendor: 공식 제조사/개발사 이름
4. category: Graphics, Office, Development, Utility, Media, OS, Security, Network, Mac, Mobile, Patch, Driver, Source, Backup, Portable, Business, Engineering, Theme, Hardware, Font, Uncategorized 중 하나
5. icon_url: 공식 아이콘 이미지 URL (찾을 수 없으면 빈 문자열)

중요:
- 응답은 반드시 유효한 JSON 형식만 작성하세요
- 추가 설명이나 코멘트를 포함하지 마세요
- 확실하지 않은 정보는 빈 문자열("")을 사용하세요

예시:
{{
  "title": "Adobe Photoshop",
  "description": "전문가용 이미지 편집 및 그래픽 디자인 소프트웨어",
  "vendor": "Adobe",
  "category": "Graphics",
  "icon_url": "https://example.com/icon.png"
}}"""

        try:
            # Anthropic Claude API 엔드포인트
            api_url = "https://api.anthropic.com/v1/messages"

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    api_url,
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "max_tokens": 500,
                        "temperature": 0.3,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    }
                )

                if response.status_code == 200:
                    result = response.json()

                    # Claude 응답 구조: content[0].text
                    if 'content' in result and len(result['content']) > 0:
                        content = result['content'][0]['text'].strip()

                        # JSON 파싱
                        content = self._extract_json(content)
                        metadata = json.loads(content)

                        return self._validate_metadata(metadata, parsed_info)
                    else:
                        print(f"Claude API unexpected response: {result}")
                        return self._fallback_metadata(parsed_info)
                else:
                    print(f"Claude API error: {response.status_code} - {response.text}")
                    return self._fallback_metadata(parsed_info)

        except json.JSONDecodeError as e:
            print(f"JSON parsing error (Claude): {e}")
            return self._fallback_metadata(parsed_info)
        except Exception as e:
            print(f"Claude API Error: {e}")
            return self._fallback_metadata(parsed_info)
