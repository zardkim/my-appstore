"""
메타데이터 정확도 계산 모듈

AI가 생성한 메타데이터의 신뢰도를 측정하여 자동 등록 여부 결정
"""
from typing import Dict, Any
from difflib import SequenceMatcher


def calculate_confidence_score(metadata: Dict[str, Any], parsed_info: Dict[str, Any]) -> float:
    """
    메타데이터 정확도 점수 계산

    Args:
        metadata: AI가 생성한 메타데이터
        parsed_info: 파일명에서 파싱한 정보

    Returns:
        정확도 점수 (0.0 ~ 1.0)

    점수 기준:
        - 제목 유사도 (30%)
        - Vendor 존재 (15%)
        - Description 적정성 (15%)
        - Category 유효성 (15%)
        - Icon URL 존재 (10%)
        - Official website 존재 (15%)
    """
    score = 0.0

    # 1. 제목 유사도 (0.3)
    title_score = calculate_title_similarity(
        metadata.get('title', ''),
        parsed_info.get('software_name', '')
    )
    score += title_score * 0.3

    # 2. Vendor 존재 여부 (0.15)
    vendor = metadata.get('vendor', '')
    if vendor and vendor.lower() not in ['unknown', 'n/a', '']:
        score += 0.15

    # 3. Description 적정성 (0.15)
    description = metadata.get('description', '')
    desc_len = len(description)
    if 100 <= desc_len <= 500:
        # 적정 길이
        score += 0.15
    elif 50 <= desc_len < 100 or 500 < desc_len <= 1000:
        # 짧거나 긴 경우 부분 점수
        score += 0.08

    # 4. Category 유효성 (0.15)
    category = metadata.get('category', '')
    valid_categories = [
        'Graphics', 'Office', 'Development', 'Utility', 'Media',
        'OS', 'Security', 'Network', 'Mac', 'Mobile', 'Patch',
        'Driver', 'Source', 'Backup', 'Business',
        'Engineering', 'Theme', 'Hardware', 'Font'
    ]
    if category in valid_categories:
        score += 0.15

    # 5. Icon URL 존재 (0.10)
    icon_url = metadata.get('icon_url', '')
    if icon_url and icon_url.startswith('http'):
        score += 0.10

    # 6. Official website 존재 (0.15)
    official_website = metadata.get('official_website', '')
    if official_website and official_website.startswith('http'):
        score += 0.15

    # 점수 범위 제한 (0.0 ~ 1.0)
    return min(max(score, 0.0), 1.0)


def calculate_title_similarity(title: str, parsed_name: str) -> float:
    """
    제목 유사도 계산

    Args:
        title: AI가 생성한 제목
        parsed_name: 파싱된 소프트웨어 이름

    Returns:
        유사도 점수 (0.0 ~ 1.0)
    """
    if not title or not parsed_name:
        return 0.0

    # 대소문자 무시, 공백 정규화
    title_normalized = ' '.join(title.lower().split())
    parsed_normalized = ' '.join(parsed_name.lower().split())

    # SequenceMatcher로 유사도 계산
    similarity = SequenceMatcher(None, title_normalized, parsed_normalized).ratio()

    # 핵심 단어 포함 여부 추가 점수
    parsed_words = set(parsed_normalized.split())
    title_words = set(title_normalized.split())

    # 파싱된 이름의 단어가 제목에 포함되어 있으면 보너스
    if parsed_words and title_words:
        word_overlap = len(parsed_words & title_words) / len(parsed_words)
        # 유사도와 단어 중복률의 가중 평균
        similarity = (similarity * 0.7) + (word_overlap * 0.3)

    return similarity


def normalize_software_name(name: str) -> str:
    """
    소프트웨어 이름 정규화 (캐시 키로 사용)

    Args:
        name: 원본 소프트웨어 이름

    Returns:
        정규화된 이름 (소문자, 공백 제거, 특수문자 제거)
    """
    import re

    # 소문자 변환
    normalized = name.lower()

    # 버전 정보 제거 (예: "2024", "v1.0", "24.5")
    normalized = re.sub(r'\b(v?\d+\.?\d*\.?\d*)\b', '', normalized)

    # 특수문자 제거 (알파벳, 숫자, 공백만 유지)
    normalized = re.sub(r'[^a-z0-9\s]', ' ', normalized)

    # 연속된 공백을 하나로
    normalized = ' '.join(normalized.split())

    return normalized.strip()


def get_confidence_level(score: float) -> str:
    """
    점수에 따른 신뢰도 레벨 반환

    Args:
        score: 정확도 점수 (0.0 ~ 1.0)

    Returns:
        신뢰도 레벨: "high", "medium", "low"
    """
    if score >= 0.9:
        return "high"
    elif score >= 0.7:
        return "medium"
    else:
        return "low"


def should_auto_register(score: float, threshold: float = 0.9) -> bool:
    """
    자동 등록 여부 판단

    Args:
        score: 정확도 점수
        threshold: 임계값 (기본값: 0.9)

    Returns:
        자동 등록 가능 여부
    """
    return score >= threshold
