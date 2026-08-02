"""
메타데이터 신뢰도 계산 모듈 (규칙 기반)

AI 자체 신뢰도 자기보고는 신호로 쓰지 않는다 - 근거 없이 메타데이터를
지어낸 바로 그 호출에게 "이거 확실해?"라고 물어봐도 똑같이 그럴듯하게
답할 위험이 크기 때문. 대신 파이프라인이 AI 호출과 독립적으로 관찰할 수
있는 신호만 사용한다:
  - developer(vendor)가 KNOWN_VENDORS와 매칭되는가
  - release_year 추출에 성공했는가 (AI 응답 또는 파일명 파싱)
  - 제품명이 너무 짧거나 일반명사에 가깝지 않은가
"""
from typing import Dict, Any

from app.core.parser import FilenameParser

# 제품명이 지나치게 일반적이어서 신뢰도를 낮춰야 하는 단어들
_GENERIC_NAME_WORDS = {
    'setup', 'install', 'installer', 'app', 'application', 'program',
    'software', 'system', 'tool', 'utility', 'update', 'patch', 'new',
}


def calculate_confidence_score(metadata: Dict[str, Any], parsed_info: Dict[str, Any]) -> float:
    """
    메타데이터 신뢰도 점수 계산 (규칙 기반, AI 자기보고 미사용)

    Args:
        metadata: AI가 생성한 메타데이터
        parsed_info: 파일명에서 파싱한 정보

    Returns:
        신뢰도 점수 (0.0 ~ 1.0)

    신호별 가중치:
        - vendor가 KNOWN_VENDORS와 매칭 (50%)
        - release_year 추출 성공 (35%)
        - 제품명이 충분히 구체적 (15%) - 3자 이하이거나 일반명사면 미부여
    """
    score = 0.0

    if _has_known_vendor(metadata, parsed_info):
        score += 0.50

    if _has_release_year(metadata, parsed_info):
        score += 0.35

    if _is_specific_name(metadata, parsed_info):
        score += 0.15

    return min(max(score, 0.0), 1.0)


def _has_known_vendor(metadata: Dict[str, Any], parsed_info: Dict[str, Any]) -> bool:
    """AI가 응답한 developer(구 vendor 필드) 또는 파일명 파싱 vendor가
    KNOWN_VENDORS에 포함되는 문자열인지 확인. 부분 문자열 매칭을 쓰는 이유는
    developer 필드가 "Autodesk, Inc." 같은 자유 텍스트로 오기 때문."""
    developer = (
        metadata.get('developer') or metadata.get('vendor')
        or parsed_info.get('vendor') or ''
    )
    developer_lower = developer.lower()
    return any(vendor in developer_lower for vendor in FilenameParser.KNOWN_VENDORS)


def _has_release_year(metadata: Dict[str, Any], parsed_info: Dict[str, Any]) -> bool:
    """AI가 응답한 release_year(검증됨) 또는 파일명 파싱 단계에서 이미
    추출된 year가 있으면 성공으로 간주."""
    ai_year = FilenameParser.parse_ai_release_year(metadata.get('release_year'))
    return bool(ai_year or parsed_info.get('year'))


def _is_specific_name(metadata: Dict[str, Any], parsed_info: Dict[str, Any]) -> bool:
    """제품명이 3자 이하로 너무 짧거나, "setup"/"installer" 같은 일반명사로만
    구성되어 있으면 신뢰할 수 있을 만큼 구체적이지 않다고 판단."""
    name = metadata.get('title') or parsed_info.get('software_name') or ''
    normalized = ' '.join(name.lower().split())
    if len(normalized.replace(' ', '')) <= 3:
        return False
    words = set(normalized.split())
    if words and words.issubset(_GENERIC_NAME_WORDS):
        return False
    return bool(normalized)


def get_confidence_level(score: float) -> str:
    """
    점수에 따른 신뢰도 레벨 반환

    Args:
        score: 신뢰도 점수 (0.0 ~ 1.0)

    Returns:
        신뢰도 레벨: "high", "medium", "low"
    """
    if score >= 0.8:
        return "high"
    elif score >= 0.5:
        return "medium"
    else:
        return "low"


def should_auto_register(score: float, threshold: float = 0.85) -> bool:
    """
    자동 등록 여부 판단

    Args:
        score: 신뢰도 점수
        threshold: 임계값 (기본값: 0.85 - vendor 매칭 + release_year 추출 성공 시 도달)

    Returns:
        자동 등록 가능 여부
    """
    return score >= threshold
