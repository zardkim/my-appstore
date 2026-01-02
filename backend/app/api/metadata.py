"""
Metadata API for testing AI metadata generation
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.dependencies import get_current_user, get_current_admin_user, get_db
from app.core.ai_metadata import AIMetadataGeneratorV2 as AIMetadataGenerator
from app.core.confidence import calculate_confidence_score, get_confidence_level, should_auto_register
from app.api.config import load_config
from app.models.product import Product
import logging
logger = logging.getLogger(__name__)


router = APIRouter()


class MetadataTestRequest(BaseModel):
    """메타데이터 테스트 요청"""
    software_name: str
    # 선택적 설정 (제공되지 않으면 config 파일에서 로드)
    ai_provider: Optional[str] = None
    ai_model: Optional[str] = None
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    use_custom_prompt: Optional[bool] = False
    custom_prompt: Optional[str] = None


class MetadataTestResponse(BaseModel):
    """메타데이터 테스트 응답"""
    success: bool
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.post("/test", response_model=MetadataTestResponse)
async def test_metadata_generation(
    request: MetadataTestRequest,
    current_user = Depends(get_current_admin_user)
):
    """
    메타데이터 생성 테스트 (관리자 전용)

    소프트웨어 이름을 입력받아 AI가 생성한 메타데이터를 반환합니다.
    실제 DB에 저장하지 않고 결과만 확인할 수 있습니다.

    Args:
        request: 소프트웨어 이름 및 옵션

    Returns:
        생성된 메타데이터
    """
    try:
        # 요청에서 제공된 설정 사용, 없으면 config 파일에서 로드
        if request.ai_provider and request.ai_model:
            # 프론트엔드에서 제공한 현재 설정 사용
            ai_provider = request.ai_provider
            ai_model = request.ai_model

            # Provider별 API 키 선택
            if ai_provider == 'gemini':
                api_key = request.gemini_api_key or ''
            elif ai_provider == 'openai':
                api_key = request.openai_api_key or ''
            else:
                api_key = ''

            logger.debug(f"📋 프론트엔드 설정 사용: provider={ai_provider}, model={ai_model}, hasKey={bool(api_key)}")
        else:
            # config 파일에서 로드 (하위 호환성)
            config = load_config()
            metadata_config = config.get('metadata', {})

            ai_provider = metadata_config.get('aiProvider', 'gemini')
            ai_model = metadata_config.get('aiModel', 'gemini-2.5-flash')

            # Provider별 API 키 선택
            if ai_provider == 'gemini':
                api_key = metadata_config.get('geminiApiKey', '')
            elif ai_provider == 'openai':
                api_key = metadata_config.get('openaiApiKey', '')
            else:
                api_key = ''

            logger.debug(f"📋 Config 파일 설정 사용: provider={ai_provider}, model={ai_model}, hasKey={bool(api_key)}")

        if not api_key or not api_key.strip():
            return MetadataTestResponse(
                success=False,
                error=f"{ai_provider.upper()} API 키가 설정되지 않았습니다. 설정 > 메타데이터 설정에서 API 키를 입력하세요."
            )

        # AI 메타데이터 생성기 초기화
        generator = AIMetadataGenerator(
            provider=ai_provider,
            api_key=api_key,
            model=ai_model
        )

        # 파일명/폴더명 파싱 (예: "Adobe_Photoshop_2024.zip" → "Adobe Photoshop 2024")
        parsed_info = generator.parser.parse(request.software_name)
        software_display_name = parsed_info.get('software_name', request.software_name)

        logger.debug(f"원본 입력: {request.software_name}")
        logger.debug(f"파싱 결과: {parsed_info}")
        logger.debug(f"표시 이름: {software_display_name}")

        # 커스텀 프롬프트 처리
        custom_prompt = None
        if request.use_custom_prompt and request.custom_prompt:
            custom_prompt = request.custom_prompt.replace('{software_name}', software_display_name)
            logger.debug(f"🎨 커스텀 프롬프트 사용 (길이: {len(custom_prompt)}자)")

        # 기본 메타데이터 생성
        metadata = await generator.generate_detailed_metadata(
            software_display_name,
            custom_prompt=custom_prompt
        )

        # 파싱 정보 추가
        metadata['parsed_info'] = {
            'original_input': request.software_name,
            'parsed_name': software_display_name,
            'version': parsed_info.get('version'),
            'year': parsed_info.get('year'),
            'vendor': parsed_info.get('vendor')
        }

        # 정확도 점수 계산
        confidence_score = calculate_confidence_score(metadata, parsed_info)
        confidence_level = get_confidence_level(confidence_score)
        auto_register = should_auto_register(confidence_score)

        metadata['confidence'] = {
            'score': round(confidence_score, 3),  # 0.0 ~ 1.0
            'percentage': round(confidence_score * 100, 1),  # 0% ~ 100%
            'level': confidence_level,  # "high", "medium", "low"
            'auto_register': auto_register,  # True if score >= 0.9
            'threshold': 0.9
        }

        return MetadataTestResponse(
            success=True,
            metadata=metadata
        )

    except Exception as e:
        logger.debug(f"Metadata generation error: {e}")
        return MetadataTestResponse(
            success=False,
            error=str(e)
        )


async def generate_extended_metadata(
    generator: AIMetadataGenerator,
    software_name: str,
    config: Dict
) -> Dict[str, Any]:
    """
    확장 메타데이터 생성

    Args:
        generator: AI 메타데이터 생성기
        software_name: 소프트웨어 이름
        config: 메타데이터 설정

    Returns:
        확장 메타데이터
    """
    # 설정에서 수집할 필드 확인
    extended_fields = config.get('extendedFields', {})

    # 수집할 필드가 하나도 없으면 기본 메타데이터만 반환
    if not any(extended_fields.values()):
        return await generator.generate_metadata(software_name)

    # 확장 프롬프트 생성
    prompt = build_extended_prompt(software_name, extended_fields)

    # AI 쿼리
    metadata = await query_ai_extended(generator, prompt)

    return metadata


def build_extended_prompt(software_name: str, fields: Dict[str, bool]) -> str:
    """확장 메타데이터 프롬프트 생성"""

    requested_fields = []

    if fields.get('official_website', False):
        requested_fields.append("  - official_website: 공식 웹사이트 URL (문자열)")

    if fields.get('system_requirements', False):
        requested_fields.append("""  - system_requirements: 시스템 요구사항 (JSON 객체)
    {
      "minimum": {"os": "...", "processor": "...", "memory": "...", "graphics": "...", "storage": "..."},
      "recommended": {"os": "...", "processor": "...", "memory": "...", "graphics": "...", "storage": "..."}
    }""")

    if fields.get('supported_os', False):
        requested_fields.append('  - supported_os: 지원 운영체제 배열 (예: ["Windows 10", "macOS 12+"])')

    if fields.get('video_url', False):
        requested_fields.append("  - video_url: 공식 소개 영상 YouTube URL (문자열, 없으면 null)")

    if fields.get('license_type', False):
        requested_fields.append('  - license_type: 라이선스 타입 ("Free", "Trial", "Paid", "Open Source" 중 하나)')

    if fields.get('tags', False):
        requested_fields.append('  - tags: 검색용 태그 배열 (최대 5개, 한글)')

    fields_list = "\n".join(requested_fields) if requested_fields else "  (없음)"

    prompt = f"""다음 소프트웨어에 대한 상세 정보를 JSON 형식으로 제공해주세요:

소프트웨어: {software_name}

필수 정보:
  - title: 정확한 공식 제품명 (문자열)
  - description: 100-200자 이내의 상세 설명 (문자열)
  - vendor: 공식 제조사/개발사 이름 (문자열)
  - category: 카테고리 (Graphics, Office, Development, Utility, Media, OS, Security, Network, Mac, Mobile, Patch, Driver, Source, Backup, Portable, Business, Engineering, Theme, Hardware, Uncategorized 중 하나)
  - icon_url: 공식 아이콘 이미지 URL (문자열, 없으면 빈 문자열)

확장 정보:
{fields_list}

중요 사항:
1. 응답은 반드시 유효한 JSON만 작성하세요
2. 추가 설명이나 코멘트를 포함하지 마세요
3. 확실하지 않은 정보는 null 또는 빈 배열 [] 사용
4. system_requirements는 반드시 minimum과 recommended 모두 포함
5. supported_os는 구체적인 버전 포함 (예: "Windows 10", "macOS 12+")
6. tags는 핵심 키워드만 5개 이내로 한글로 작성
7. video_url은 YouTube 공식 채널 영상 우선

응답 예시:
{{
  "title": "Adobe Photoshop 2024",
  "description": "전문가용 이미지 편집 및 그래픽 디자인 소프트웨어. 사진 보정, 합성, 디지털 페인팅, 3D 디자인 등 다양한 창작 기능을 제공하는 업계 표준 그래픽 툴",
  "vendor": "Adobe Inc.",
  "category": "Graphics",
  "icon_url": "https://www.adobe.com/content/dam/cc/icons/photoshop.svg",
  "official_website": "https://www.adobe.com/products/photoshop.html",
  "system_requirements": {{
    "minimum": {{
      "os": "Windows 10 64-bit (버전 1809) 이상",
      "processor": "Intel 또는 AMD 프로세서 (64-bit 지원, 2GHz 이상)",
      "memory": "8 GB RAM",
      "graphics": "DirectX 12 지원 GPU, 1.5 GB VRAM",
      "storage": "4 GB 여유 공간"
    }},
    "recommended": {{
      "os": "Windows 11 64-bit 최신 버전",
      "processor": "Intel Core i7 또는 AMD Ryzen 7 이상",
      "memory": "16 GB RAM 이상",
      "graphics": "NVIDIA GeForce RTX 3060 (6 GB VRAM)",
      "storage": "20 GB SSD 여유 공간"
    }}
  }},
  "supported_os": ["Windows 10 (64-bit)", "Windows 11", "macOS 12 Monterey", "macOS 13 Ventura"],
  "video_url": "https://www.youtube.com/watch?v=example",
  "license_type": "Paid",
  "tags": ["이미지편집", "그래픽디자인", "사진보정", "포토샵", "크리에이티브"]
}}"""

    return prompt


async def query_ai_extended(generator: AIMetadataGenerator, prompt: str) -> Dict[str, Any]:
    """AI에게 확장 프롬프트 질의 (provider에 따라 다른 API 사용)"""
    import httpx
    import json

    try:
        software_name = prompt.split('\n')[2].replace('소프트웨어: ', '')

        # OpenAI
        if generator.provider == 'openai':
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {generator.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": generator.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a software information expert. You provide accurate, detailed information about software applications in JSON format only. Always respond in Korean for descriptions and tags."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 1500
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content'].strip()
                    content = extract_json(content)
                    return json.loads(content)
                else:
                    logger.debug(f"OpenAI API error: {response.status_code}")
                    return await generator.generate_metadata(software_name)

        # Gemini
        elif generator.provider == 'gemini':
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{generator.model}:generateContent?key={generator.api_key}"

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    api_url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{
                            "parts": [{"text": prompt}]
                        }],
                        "generationConfig": {
                            "temperature": 0.3,
                            "maxOutputTokens": 1500
                        }
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    if 'candidates' in result and len(result['candidates']) > 0:
                        content = result['candidates'][0]['content']['parts'][0]['text'].strip()
                        content = extract_json(content)
                        return json.loads(content)
                    else:
                        logger.debug(f"Gemini API unexpected response: {result}")
                        return await generator.generate_metadata(software_name)
                else:
                    logger.debug(f"Gemini API error: {response.status_code}")
                    return await generator.generate_metadata(software_name)

        else:
            logger.debug(f"Unknown provider: {generator.provider}")
            return await generator.generate_metadata(software_name)

    except Exception as e:
        logger.debug(f"Extended metadata error: {e}")
        software_name = prompt.split('\n')[2].replace('소프트웨어: ', '')
        return await generator.generate_metadata(software_name)


def extract_json(text: str) -> str:
    """텍스트에서 JSON 추출"""
    text = text.strip()
    if text.startswith('```'):
        lines = text.split('\n')
        if lines[0].startswith('```'):
            lines = lines[1:]
        if lines and lines[-1].strip() == '```':
            lines = lines[:-1]
        text = '\n'.join(lines)
    return text.strip()


class RegisterMetadataRequest(BaseModel):
    """메타데이터 등록 요청"""
    metadata: Dict[str, Any]


class RegisterMetadataResponse(BaseModel):
    """메타데이터 등록 응답"""
    success: bool
    product_id: Optional[int] = None
    error: Optional[str] = None


@router.post("/register", response_model=RegisterMetadataResponse)
async def register_metadata(
    request: RegisterMetadataRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """
    선택된 메타데이터로 Product 생성 (관리자 전용)

    Args:
        request: 메타데이터
        db: 데이터베이스 세션

    Returns:
        생성된 Product ID
    """
    try:
        metadata = request.metadata

        # 필수 필드 확인
        title = metadata.get('title')
        if not title:
            return RegisterMetadataResponse(
                success=False,
                error="제품명이 필요합니다."
            )

        # 가상 폴더 경로 생성 (실제 파일이 없으므로 /virtual/ 프리픽스 사용)
        import re
        safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
        folder_path = f"/virtual/{safe_title}"

        # 중복 확인
        existing = db.query(Product).filter(Product.folder_path == folder_path).first()
        if existing:
            # 고유한 경로 생성
            import time
            folder_path = f"/virtual/{safe_title}_{int(time.time())}"

        # Product 생성
        product = Product(
            title=title,
            description=metadata.get('description', ''),
            vendor=metadata.get('vendor', ''),
            icon_url=metadata.get('icon_url', ''),
            category=metadata.get('category', 'Uncategorized'),
            folder_path=folder_path
        )

        db.add(product)
        db.commit()
        db.refresh(product)

        logger.debug(f"✅ Product 생성 완료: {product.id} - {product.title}")

        return RegisterMetadataResponse(
            success=True,
            product_id=product.id
        )

    except Exception as e:
        logger.debug(f"❌ Product 등록 오류: {e}")
        db.rollback()
        return RegisterMetadataResponse(
            success=False,
            error=str(e)
        )
