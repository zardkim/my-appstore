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

from app.core.keywords import PATCH_KEYWORDS as _PATCH_KEYWORDS

# ------------------------------------------------------------------
# 키워드 정의
# ------------------------------------------------------------------

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

# "+ Fix", "with Keygen", "Incl.Patch"처럼 연결어 뒤에 패치 키워드가 오는 패턴.
# 이 경우 파일 자체가 패치가 아니라 패치/크랙/키젠이 "동봉됨"을 의미하므로
# 패치로 분류하지 않는다. 구분자는 공백/언더스코어/마침표가 없는 경우
# (예: "IncludesPatch")까지 커버하도록 0개 이상으로 허용한다.
_CONNECTOR_PATCH_PATTERN = re.compile(
    r"(?:\+|with|incl\.?|include[sd]?|bundled)[\s_.]*"
    r"(?:fix|crack|keygen|patch|serial)",
    re.IGNORECASE,
)


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
        has_patch = _has_core_patch_signal(combined, name_lower)
        has_update = _contains_any(combined, _UPDATE_KEYWORDS) or bool(_SP_PATTERN.search(combined))
        if not has_patch and not has_update:
            return "manual"

    # ── 규칙 2: 패치 키워드 ─────────────────────────────────────────
    # "+ Fix", "with Keygen"처럼 연결어를 통해 패치/크랙이 동봉되었다는
    # 표현인 경우에는 이 규칙을 건너뛰고 아래 규칙들을 계속 평가한다
    # (예: "Autodesk Maya v2026 + Fix (macOS).zip"은 patch가 아니라 product).
    if _has_core_patch_signal(combined, name_lower):
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


def _is_bundled_patch_mention(name_lower: str) -> bool:
    """파일명이 '+Fix', 'with Keygen'처럼 연결어를 통한 패치 동봉 표현을
    포함하는지 확인. 폴더명이 아니라 파일명만 검사한다 — 그렇지 않으면
    폴더명에 이런 문구가 있을 때 같은 폴더의 실제 Keygen.exe 같은 파일까지
    product로 잘못 분류될 수 있다."""
    return bool(_CONNECTOR_PATCH_PATTERN.search(name_lower))


def _has_core_patch_signal(combined: str, name_lower: str) -> bool:
    """패치 키워드가 존재하고, 그것이 연결어를 통한 동봉 표현이 아닌
    핵심 키워드인 경우에만 True."""
    if not _contains_any(combined, _PATCH_KEYWORDS):
        return False
    return not _is_bundled_patch_mention(name_lower)
