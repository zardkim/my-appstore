"""
파일명 표준화 시스템

표준 형식: [제품명] v버전 - 설명.확장자

예시:
  [Total Commander] v10.51 - Final.zip
  [ACDSee Photo Studio] v2024 - Ultimate.exe
  [Acronis True Image] v2019.exe
"""
import re
from typing import Dict, Optional, Tuple
from pathlib import Path
import logging
logger = logging.getLogger(__name__)



class FilenameStandardizer:
    """
    파일명을 표준 형식으로 변환하고 파싱
    """

    # 노이즈 단어 (제거할 단어들)
    NOISE_WORDS = {
        'final', 'with', 'key', 'crack', 'patch', 'portable', 'full',
        'setup', 'installer', 'install', 'multilingual', 'multi',
        'x86', 'x64', 'win32', 'win64', 'windows', 'macos', 'linux',
        'repack', 'by', 'cracked', 'activated', 'registered',
        'premium', 'professional', 'pro', 'ultimate', 'enterprise'
    }

    # 버전 패턴
    VERSION_PATTERNS = [
        r'v?(\d+\.[\d.]+)',  # v1.2.3 또는 1.2.3
        r'(\d{4})',          # 2024
        r'Build\s*(\d+)',    # Build 14110
    ]

    @staticmethod
    def parse_standard_filename(filename: str) -> Dict:
        """
        표준 형식의 파일명 파싱

        형식: 제품명.v버전-기타내용.확장자

        Args:
            filename: 파일명

        Returns:
            {
                'product_name': str,  # 제품명
                'version': str,       # 버전
                'description': str,   # 기타내용
                'extension': str,     # 확장자
                'is_standard': bool   # 표준 형식 여부
            }
        """
        # 확장자 분리
        path = Path(filename)
        name = path.stem
        ext = path.suffix

        # 표준 형식 체크: .v 패턴이 있는지
        # 패턴: 제품명.v버전-기타내용
        version_pattern = r'\.v([\d.]+)'
        version_match = re.search(version_pattern, name)

        if version_match:
            # 표준 형식 (버전 있음)
            version = version_match.group(1)

            # 제품명 추출 (버전 앞부분)
            product_name = name[:version_match.start()].strip()

            # 기타내용 추출 (버전 뒤, - 이후)
            remaining = name[version_match.end():].strip()
            description = ''
            if remaining.startswith('-'):
                description = remaining[1:].strip()
            elif remaining:
                description = remaining.strip()

            return {
                'product_name': product_name,
                'version': version,
                'description': description,
                'extension': ext,
                'is_standard': True
            }
        elif '-' in name:
            # 버전 없는 표준 형식: 제품명-기타내용
            parts = name.split('-', 1)
            product_name = parts[0].strip()
            description = parts[1].strip() if len(parts) > 1 else ''

            return {
                'product_name': product_name,
                'version': '',
                'description': description,
                'extension': ext,
                'is_standard': True
            }
        else:
            # 비표준 형식 - 기존 방식으로 파싱
            return FilenameStandardizer._parse_non_standard(filename)

    @staticmethod
    def _parse_non_standard(filename: str) -> Dict:
        """
        비표준 형식 파일명 파싱 (기존 방식)
        """
        path = Path(filename)
        name = path.stem
        ext = path.suffix

        # 버전 추출
        version = ''
        for pattern in FilenameStandardizer.VERSION_PATTERNS:
            match = re.search(pattern, name, re.IGNORECASE)
            if match:
                version = match.group(1)
                break

        # 노이즈 제거하여 제품명 추출
        clean_name = name
        for noise in FilenameStandardizer.NOISE_WORDS:
            clean_name = re.sub(r'\b' + noise + r'\b', '', clean_name, flags=re.IGNORECASE)

        # 버전 제거
        if version:
            clean_name = clean_name.replace(version, '')
            clean_name = re.sub(r'v?\d+\.[\d.]+', '', clean_name)

        # 특수문자를 공백으로
        clean_name = re.sub(r'[_\-\.]', ' ', clean_name)

        # 연속 공백 제거
        clean_name = re.sub(r'\s+', ' ', clean_name).strip()

        return {
            'product_name': clean_name,
            'version': version,
            'description': '',
            'extension': ext,
            'is_standard': False
        }

    @staticmethod
    def standardize_filename(filename: str, auto_detect: bool = True) -> str:
        """
        파일명을 표준 형식으로 변환

        Args:
            filename: 원본 파일명
            auto_detect: 자동으로 제품명/버전 감지

        Returns:
            표준화된 파일명
        """
        parsed = FilenameStandardizer.parse_standard_filename(filename)

        if parsed['is_standard']:
            # 이미 표준 형식
            return filename

        # 표준 형식으로 변환
        parts = []

        # 제품명 (대괄호로 감싸기)
        if parsed['product_name']:
            parts.append(f"[{parsed['product_name']}]")

        # 버전
        if parsed['version']:
            parts.append(f"v{parsed['version']}")

        # 설명
        if parsed['description']:
            parts.append(f"- {parsed['description']}")

        standard_name = ' '.join(parts)
        return f"{standard_name}{parsed['extension']}"

    @staticmethod
    def get_search_query(filename: str) -> str:
        """
        검색에 최적화된 쿼리 생성

        Args:
            filename: 파일명

        Returns:
            검색 쿼리 (제품명만, 깨끗하게)
        """
        parsed = FilenameStandardizer.parse_standard_filename(filename)
        return parsed['product_name']

    @staticmethod
    def suggest_standard_name(filename: str, vendor: str = "") -> str:
        """
        표준 파일명 제안

        Args:
            filename: 원본 파일명
            vendor: 제조사 (선택)

        Returns:
            제안된 표준 파일명
        """
        parsed = FilenameStandardizer.parse_standard_filename(filename)

        parts = []

        # 제조사가 있고 제품명에 포함되지 않은 경우 추가
        if vendor and vendor.lower() not in parsed['product_name'].lower():
            parts.append(f"[{vendor} {parsed['product_name']}]")
        else:
            parts.append(f"[{parsed['product_name']}]")

        if parsed['version']:
            parts.append(f"v{parsed['version']}")

        if parsed['description']:
            parts.append(f"- {parsed['description']}")

        return ' '.join(parts) + parsed['extension']


def analyze_filename(filename: str) -> None:
    """
    파일명 분석 및 표준화 제안 출력 (디버그용)
    """
    print("=" * 80)
    logger.debug(f"원본 파일명: {filename}")
    print("=" * 80)

    parsed = FilenameStandardizer.parse_standard_filename(filename)

    logger.debug(f"\n📊 파싱 결과:")
    logger.debug(f"  제품명: {parsed['product_name']}")
    logger.debug(f"  버전: {parsed['version'] or 'N/A'}")
    logger.debug(f"  설명: {parsed['description'] or 'N/A'}")
    logger.debug(f"  확장자: {parsed['extension']}")
    logger.debug(f"  표준 형식: {'✅ 예' if parsed['is_standard'] else '❌ 아니오'}")

    if not parsed['is_standard']:
        standard = FilenameStandardizer.standardize_filename(filename)
        logger.debug(f"\n💡 표준 형식 제안:")
        logger.debug(f"  {standard}")

    search_query = FilenameStandardizer.get_search_query(filename)
    logger.debug(f"\n🔍 검색 쿼리:")
    logger.debug(f"  {search_query}")
    print()


# 테스트
if __name__ == "__main__":
    test_files = [
        "Total Commander 10.51 Final with Key.zip",
        "ACDSee 2024 Ultimate v17.1.1.3800.exe",
        "Acronis True Image 2019 Build 14110.exe",
        "[Total Commander] v10.51 - Final.zip",
        "Adobe_Photoshop_CC_2023_v24.0.1_x64.exe",
        "EaseUS Partition Master 15.8 Multilingual.zip",
    ]

    for filename in test_files:
        analyze_filename(filename)
