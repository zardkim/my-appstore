"""
파일 자동 분류 모듈

파일명과 폴더명의 키워드를 분석하여 스캔된 파일을 아래 5가지 중 하나로 분류한다.
  - product       : 소프트웨어 설치 본체 (기본값)
  - patch         : 패치, 크랙, 키젠 등
  - language_pack : 언어팩, 번역팩
  - manual        : 메뉴얼, 설명서, 가이드
  - update        : 업데이트, 서비스팩

분류 판별 우선순위:
  1. 메뉴얼 확장자 우선 (.pdf/.doc/.docx/.chm/.txt + patch/update 키워드 없음)
  2. 패치 키워드
  3. 언어팩 키워드
  4. 메뉴얼 키워드
  5. 업데이트 키워드 / 패턴
  6. 제품 (기본값)
"""

import re
from pathlib import Path

# ------------------------------------------------------------------
# 키워드 정의
# ------------------------------------------------------------------

_PATCH_KEYWORDS = {
    "patch", "hotfix", "fix", "crack", "keygen", "keygenerator",
    "serial", "key", "reg", "loader", "activator", "unlocker", "bypass",
}

_LANGPACK_KEYWORDS = {
    "lang", "language", "locale", "translation", "multilingual", "multi_lang",
    "langpack", "kor_patch", "korpatch", "언어팩",
    "ko_kr", "en_us", "ja_jp", "zh_cn", "zh_tw", "de_de", "fr_fr",
}

_MANUAL_KEYWORDS = {
    "manual", "guide", "readme", "read_me", "help", "doc", "documentation",
    "tutorial", "handbook", "reference", "instructions",
}

_UPDATE_KEYWORDS = {
    "update", "upgrade", "service_pack", "cumulative", "rollup", "release", "build",
}

# 메뉴얼 전용 확장자 (패치/업데이트 키워드가 없을 때 메뉴얼로 분류)
_MANUAL_EXTENSIONS = {".pdf", ".doc", ".docx", ".chm", ".txt"}

# sp1, sp2, sp3 ... 패턴
_SP_PATTERN = re.compile(r"\bsp\d+\b")


# ------------------------------------------------------------------
# 분류 함수
# ------------------------------------------------------------------

def classify_file(file_name: str, folder_name: str = "") -> str:
    """파일명 + 폴더명을 분석하여 분류 문자열 반환.

    Args:
        file_name:   파일명 (확장자 포함)
        folder_name: 부모 폴더명 (선택). 파일명이 'setup.exe' 등 의미 없는 경우에도
                     폴더명 키워드를 함께 확인한다.

    Returns:
        "product" | "patch" | "language_pack" | "manual" | "update"
    """
    name_lower = file_name.lower()
    folder_lower = folder_name.lower()

    # 파일명 + 폴더명을 합쳐 키워드를 한 번에 검색
    combined = f"{name_lower} {folder_lower}"

    ext = Path(file_name).suffix.lower()

    # ── 규칙 1: 메뉴얼 전용 확장자 ──────────────────────────────────
    # .pdf/.doc/.docx/.chm/.txt 이면서 patch/update 키워드가 없으면 메뉴얼
    if ext in _MANUAL_EXTENSIONS:
        has_patch = _contains_any(combined, _PATCH_KEYWORDS)
        has_update = _contains_any(combined, _UPDATE_KEYWORDS) or bool(_SP_PATTERN.search(combined))
        if not has_patch and not has_update:
            return "manual"

    # ── 규칙 2: 패치 키워드 ─────────────────────────────────────────
    if _contains_any(combined, _PATCH_KEYWORDS):
        return "patch"

    # ── 규칙 3: 언어팩 키워드 ───────────────────────────────────────
    if _contains_any(combined, _LANGPACK_KEYWORDS):
        return "language_pack"

    # ── 규칙 4: 메뉴얼 키워드 ───────────────────────────────────────
    if _contains_any(combined, _MANUAL_KEYWORDS):
        return "manual"

    # ── 규칙 5: 업데이트 키워드 / sp 패턴 ───────────────────────────
    if _contains_any(combined, _UPDATE_KEYWORDS):
        return "update"
    if _SP_PATTERN.search(combined):
        return "update"

    # ── 규칙 6: 기본값 ──────────────────────────────────────────────
    return "product"


def _contains_any(text: str, keywords: set) -> bool:
    """text 내에 keywords 중 하나라도 포함되어 있으면 True."""
    for kw in keywords:
        if kw in text:
            return True
    return False
