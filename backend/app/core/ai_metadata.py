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
            # 커스텀 프롬프트의 변수 치환 (소문자/대문자/괄더형 모두 지원)
            prompt = custom_prompt.replace('{software_name}', software_context)
            prompt = prompt.replace('{SOFTWARE_NAME}', software_context)
            prompt = prompt.replace('[SOFTWARE_NAME]', software_context)
        else:
            # 상세 메타데이터 프롬프트 (영어 - 더 나은 성능)
            prompt = f"""Provide detailed metadata for the software: {software_context}

Return a JSON object with the following fields. ALL fields are REQUIRED - use empty strings "" or empty arrays [] if information is unknown.

**Basic Information:**
- title: Official software name
- version: Version number (if known)
- platform: Windows, macOS, Linux, or Cross-platform
- developer: Official developer/vendor name
- category: Choose the BEST match based on PRIMARY function:
  * Graphics: Image editing, graphic design, 3D modeling
  * Media: Video/audio editing, media playback, screen recording
  * Office: Documents, spreadsheets, presentations
  * Business: Accounting, ERP, CRM, business management
  * Development: Programming, IDE, development tools
  * Utility: System utilities, optimization tools
  * Security, Network, OS, Engineering, Hardware, or Uncategorized for others
- official_website: Official website URL (full URL with https://)
- icon_url: Official logo/icon image URL (leave "" if unknown)
- license_type: Free, Freemium, Trial, Commercial, or Open Source
- language: Supported languages (e.g., "English, Korean, Japanese" or "Multilingual")

**Descriptions:**
- description_short: 50-100 character brief description (one sentence)
- description_detailed: 200-300 character detailed description (main features and purpose)

**Features (5-10 items):**
- features: Array of key features (e.g., ["Virtual machine management", "Snapshot support"])

**File Formats:**
- supported_formats: Array of supported file formats (e.g., [".vmdk", ".iso", ".ova"])

**System Requirements (object):**
- system_requirements: {{
    "os": "Operating system requirements (specific)",
    "cpu": "CPU requirements",
    "ram": "RAM requirements (minimum/recommended)",
    "disk_space": "Disk space needed",
    "gpu": "GPU requirements (if any)",
    "additional": "Additional requirements (if any)"
  }}

**Installation Info (object):**
- installation_info: {{
    "installer_type": "Installation method (e.g., EXE installer, DMG mount, Archive extraction)",
    "file_size": "Approximate file size (e.g., about 500MB)",
    "internet_required": "Internet requirement (e.g., Required for activation, Not required)"
  }}

**Release Notes:**
- release_notes: Major release notes or version history (2-3 lines if known)

**Example Output:**
{{
  "title": "VMware Workstation Pro",
  "version": "12.0.1",
  "platform": "Windows",
  "developer": "VMware, Inc.",
  "category": "Utility",
  "official_website": "https://www.vmware.com/products/workstation-pro.html",
  "icon_url": "",
  "license_type": "Commercial",
  "language": "다국어 지원 (영어, 한국어, 일본어, 중국어 등)",
  "description_short": "단일 PC에서 여러 운영체제를 가상 머신으로 실행할 수 있는 전문 가상화 소프트웨어",
  "description_detailed": "VMware Workstation Pro는 IT 전문가와 개발자가 Windows 또는 Linux PC 한 대에서 여러 운영체제를 실행, 테스트, 배포할 수 있도록 하는 업계 표준 하이퍼바이저 솔루션입니다. 고급 3D 그래픽 지원, 고해상도 디스플레이, 강력한 가상 네트워킹 기능을 제공합니다.",
  "features": [
    "하나의 PC에서 여러 운영체제 동시 실행",
    "DirectX 10 및 OpenGL 3.3 지원으로 3D 그래픽 구현",
    "4K UHD 디스플레이 지원",
    "가상 네트워크 구성 기능",
    "스냅샷 및 복제 기능",
    "vSphere/ESXi 원격 연결",
    "USB 3.0 장치 지원"
  ],
  "supported_formats": [".vmx", ".vmdk", ".ovf", ".ova", ".iso"],
  "system_requirements": {{
    "os": "Windows 7 이상 (64비트)",
    "cpu": "1.3GHz 이상의 64비트 Intel 또는 AMD 멀티코어 프로세서",
    "ram": "최소 2GB (4GB 이상 권장)",
    "disk_space": "설치용 1.2GB (가상 머신용 추가 공간 필요)",
    "gpu": "DirectX 10 호환 그래픽 카드",
    "additional": "BIOS에서 하드웨어 가상화(Intel VT-x 또는 AMD-V) 활성화 필요"
  }},
  "installation_info": {{
    "installer_type": "EXE 실행 파일",
    "file_size": "약 300-600MB",
    "internet_required": "라이선스 인증 및 업데이트 시 필요"
  }},
  "release_notes": "버전 12.0.1: Windows 10 안정성 개선, Intel Skylake 호환성 향상, USB 3.0 수정 및 보안 패치 포함"
}}

**CRITICAL RULES:**
1. Return ONLY valid JSON - no markdown, no comments, no explanations
2. Include ALL fields listed above - this is MANDATORY
3. Use empty strings "" or empty arrays [] for unknown information
4. Be specific and detailed - provide comprehensive information
5. For well-known software, fill in as much detail as possible

**LANGUAGE REQUIREMENT:**
- Provide ALL text content (descriptions, features, notes, etc.) in KOREAN language
- Keep technical terms and proper nouns in their original form
- Examples: "가상 머신 관리", "스냅샷 및 복제 기능", "Windows 10 안정성 개선"
- Field names remain in English, but all VALUES must be in Korean"""

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
                                "content": "You are an expert software analyst. You provide comprehensive, accurate metadata about software applications in JSON format. Always include ALL required fields in your response, even if you need to use empty strings or arrays for unknown information. Your responses are detailed, well-structured, and factually correct."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.2,
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
            # 커스텀 프롬프트의 변수 치환 (소문자/대문자/괄더형 모두 지원)
            prompt = custom_prompt.replace('{software_name}', software_context)
            prompt = prompt.replace('{SOFTWARE_NAME}', software_context)
            prompt = prompt.replace('[SOFTWARE_NAME]', software_context)
        else:
            # Gemini용 영어 프롬프트 (더 나은 성능)
            prompt = f"""Provide detailed metadata for the software: {software_context}

Return a JSON object with the following fields. ALL fields are REQUIRED - use empty strings "" or empty arrays [] if information is unknown.

**Basic Information:**
- title: Official software name
- version: Version number (if known)
- platform: Windows, macOS, Linux, or Cross-platform
- developer: Official developer/vendor name
- category: Choose the BEST match based on PRIMARY function:
  * Graphics: Image editing, graphic design, 3D modeling
  * Media: Video/audio editing, media playback, screen recording
  * Office: Documents, spreadsheets, presentations
  * Business: Accounting, ERP, CRM, business management
  * Development: Programming, IDE, development tools
  * Utility: System utilities, optimization tools
  * Security, Network, OS, Engineering, Hardware, or Uncategorized for others
- official_website: Official website URL (full URL with https://)
- icon_url: Official logo/icon image URL (leave "" if unknown)
- license_type: Free, Freemium, Trial, Commercial, or Open Source
- language: Supported languages (e.g., "English, Korean, Japanese" or "Multilingual")

**Descriptions:**
- description_short: 50-100 character brief description (one sentence)
- description_detailed: 200-300 character detailed description (main features and purpose)

**Features (5-10 items):**
- features: Array of key features (e.g., ["Virtual machine management", "Snapshot support"])

**File Formats:**
- supported_formats: Array of supported file formats (e.g., [".vmdk", ".iso", ".ova"])

**System Requirements (object):**
- system_requirements: {{
    "os": "Operating system requirements (specific)",
    "cpu": "CPU requirements",
    "ram": "RAM requirements (minimum/recommended)",
    "disk_space": "Disk space needed",
    "gpu": "GPU requirements (if any)",
    "additional": "Additional requirements (if any)"
  }}

**Installation Info (object):**
- installation_info: {{
    "installer_type": "Installation method (e.g., EXE installer, DMG mount, Archive extraction)",
    "file_size": "Approximate file size (e.g., about 500MB)",
    "internet_required": "Internet requirement (e.g., Required for activation, Not required)"
  }}

**Release Notes:**
- release_notes: Major release notes or version history (2-3 lines if known)

**Example Output:**
{{
  "title": "VMware Workstation Pro",
  "version": "12.0.1",
  "platform": "Windows",
  "developer": "VMware, Inc.",
  "category": "Utility",
  "official_website": "https://www.vmware.com/products/workstation-pro.html",
  "icon_url": "",
  "license_type": "Commercial",
  "language": "다국어 지원 (영어, 한국어, 일본어, 중국어 등)",
  "description_short": "단일 PC에서 여러 운영체제를 가상 머신으로 실행할 수 있는 전문 가상화 소프트웨어",
  "description_detailed": "VMware Workstation Pro는 IT 전문가와 개발자가 Windows 또는 Linux PC 한 대에서 여러 운영체제를 실행, 테스트, 배포할 수 있도록 하는 업계 표준 하이퍼바이저 솔루션입니다. 고급 3D 그래픽 지원, 고해상도 디스플레이, 강력한 가상 네트워킹 기능을 제공합니다.",
  "features": [
    "하나의 PC에서 여러 운영체제 동시 실행",
    "DirectX 10 및 OpenGL 3.3 지원으로 3D 그래픽 구현",
    "4K UHD 디스플레이 지원",
    "가상 네트워크 구성 기능",
    "스냅샷 및 복제 기능",
    "vSphere/ESXi 원격 연결",
    "USB 3.0 장치 지원"
  ],
  "supported_formats": [".vmx", ".vmdk", ".ovf", ".ova", ".iso"],
  "system_requirements": {{
    "os": "Windows 7 이상 (64비트)",
    "cpu": "1.3GHz 이상의 64비트 Intel 또는 AMD 멀티코어 프로세서",
    "ram": "최소 2GB (4GB 이상 권장)",
    "disk_space": "설치용 1.2GB (가상 머신용 추가 공간 필요)",
    "gpu": "DirectX 10 호환 그래픽 카드",
    "additional": "BIOS에서 하드웨어 가상화(Intel VT-x 또는 AMD-V) 활성화 필요"
  }},
  "installation_info": {{
    "installer_type": "EXE 실행 파일",
    "file_size": "약 300-600MB",
    "internet_required": "라이선스 인증 및 업데이트 시 필요"
  }},
  "release_notes": "버전 12.0.1: Windows 10 안정성 개선, Intel Skylake 호환성 향상, USB 3.0 수정 및 보안 패치 포함"
}}

**CRITICAL RULES:**
1. Return ONLY valid JSON - no markdown, no comments, no explanations
2. Include ALL fields listed above - this is MANDATORY
3. Use empty strings "" or empty arrays [] for unknown information
4. Be specific and detailed - provide comprehensive information
5. For well-known software, fill in as much detail as possible

**LANGUAGE REQUIREMENT:**
- Provide ALL text content (descriptions, features, notes, etc.) in KOREAN language
- Keep technical terms and proper nouns in their original form
- Examples: "가상 머신 관리", "스냅샷 및 복제 기능", "Windows 10 안정성 개선"
- Field names remain in English, but all VALUES must be in Korean"""

        try:
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

            # System instruction을 별도로 추가
            system_instruction = "You are an expert software analyst. Provide comprehensive, accurate metadata about software applications in JSON format. Always include ALL required fields, even if you need to use empty strings or arrays for unknown information. Be thorough and detailed."

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    api_url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "system_instruction": {
                            "parts": [{"text": system_instruction}]
                        },
                        "contents": [{
                            "parts": [{"text": prompt}]
                        }],
                        "generationConfig": {
                            "temperature": 0.2,
                            "maxOutputTokens": 8192,
                            "topP": 0.95,
                            "topK": 40
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

    async def is_filename_clear_for_matching(
        self,
        filename: str,
        parent_folder: str = ""
    ) -> bool:
        """
        AI를 사용하여 파일명이 자동 매칭에 충분히 명확한지 판단

        Args:
            filename: 파일명
            parent_folder: 부모 폴더명

        Returns:
            True: 명확한 파일명 (자동 AI 매칭 가능)
            False: 불명확한 파일명 (검색된 목록에 표시)
        """
        # API 키가 없으면 기본적으로 True 반환 (기존 동작 유지)
        if not self.api_key or not self.api_key.strip():
            return True

        # 파일명 파싱
        parsed = self.parser.parse(filename, parent_folder)
        software_name = parsed['software_name']
        version = parsed.get('version', '')

        # 컨텍스트 구성
        context = f"파일명: {filename}"
        if parent_folder:
            context += f"\n폴더명: {parent_folder}"
        context += f"\n파싱 결과: {software_name}"
        if version:
            context += f" (버전: {version})"

        # 간단한 프롬프트 (Yes/No 답변만 요청)
        prompt = f"""{context}

위 파일명이 소프트웨어를 명확하게 식별할 수 있는지 판단해주세요.

**명확한 파일명의 조건:**
- 소프트웨어의 정확한 이름을 포함
- 제조사나 브랜드명이 포함되어 있으면 더 좋음
- 버전 정보가 있으면 더 명확함
- 예: "Adobe Photoshop 2024 v25.0.iso", "Visual Studio Code 1.85.exe"

**불명확한 파일명의 예:**
- 너무 일반적인 이름: "setup.exe", "installer.zip", "patch.exe"
- 의미 없는 숫자/문자 조합: "abc123.exe", "tmp_file.zip"
- 파일명만으로는 어떤 소프트웨어인지 알 수 없는 경우

다음 중 하나로만 답변해주세요:
- CLEAR: 파일명이 명확하여 자동 AI 매칭 가능
- UNCLEAR: 파일명이 불명확하여 사용자 확인 필요

답변:"""

        try:
            if self.provider == 'openai':
                return await self._judge_clarity_openai(prompt)
            elif self.provider == 'gemini':
                return await self._judge_clarity_gemini(prompt)
            else:
                # 알 수 없는 제공자는 기본값 True
                return True
        except Exception as e:
            logger.debug(f"파일명 명확성 판단 실패: {e}")
            # 에러 시 안전하게 True 반환 (기존 동작 유지)
            return True

    async def _judge_clarity_openai(self, prompt: str) -> bool:
        """OpenAI로 파일명 명확성 판단"""
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
                                "content": "You are a software filename analyzer. Answer only with CLEAR or UNCLEAR."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.1,
                        "max_tokens": 10
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    answer = result['choices'][0]['message']['content'].strip().upper()
                    is_clear = 'CLEAR' in answer
                    logger.debug(f"파일명 명확성 판단 (OpenAI): {answer} → {is_clear}")
                    return is_clear
                else:
                    logger.debug(f"OpenAI clarity check failed: {response.status_code}")
                    return True
        except Exception as e:
            logger.debug(f"OpenAI clarity check error: {e}")
            return True

    async def _judge_clarity_gemini(self, prompt: str) -> bool:
        """Gemini로 파일명 명확성 판단"""
        try:
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    api_url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{
                            "parts": [{"text": prompt}]
                        }],
                        "generationConfig": {
                            "temperature": 0.1,
                            "maxOutputTokens": 10
                        }
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    if 'candidates' in result and len(result['candidates']) > 0:
                        answer = result['candidates'][0]['content']['parts'][0]['text'].strip().upper()
                        is_clear = 'CLEAR' in answer
                        logger.debug(f"파일명 명확성 판단 (Gemini): {answer} → {is_clear}")
                        return is_clear
                    else:
                        logger.debug(f"Gemini clarity check: unexpected response")
                        return True
                else:
                    logger.debug(f"Gemini clarity check failed: {response.status_code}")
                    return True
        except Exception as e:
            logger.debug(f"Gemini clarity check error: {e}")
            return True

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
