"""
파일명 표준 규칙 검증기
"""
import re
from typing import Dict, List, Optional, Tuple


class FilenameValidator:
    """파일명 표준 규칙 검증"""

    # 위반 유형
    VIOLATION_UNDERSCORE_OVERUSE = "underscore_overuse"
    VIOLATION_BRACKET_USAGE = "bracket_usage"
    VIOLATION_VERSION_FORMAT = "version_format"
    VIOLATION_LOWERCASE_NAME = "lowercase_name"
    VIOLATION_COMPLEX_NAME = "complex_name"
    VIOLATION_INVALID_CHARS = "invalid_chars"

    @staticmethod
    def validate_filename(filename: str) -> Dict:
        """
        파일명이 표준 규칙을 따르는지 검증

        Args:
            filename: 검증할 파일명 (확장자 포함)

        Returns:
            {
                "is_valid": bool,
                "violations": [
                    {
                        "type": str,
                        "details": str,
                        "suggestion": str
                    }
                ]
            }
        """
        violations = []

        # 확장자 분리
        base_name = filename
        extension = ""
        if "." in filename:
            parts = filename.rsplit(".", 1)
            base_name = parts[0]
            extension = "." + parts[1]

        # 1. 언더스코어 과다 사용 (3개 이상)
        underscore_count = base_name.count("_")
        if underscore_count >= 3:
            violations.append({
                "type": FilenameValidator.VIOLATION_UNDERSCORE_OVERUSE,
                "details": f"언더스코어가 {underscore_count}개 사용되었습니다. 띄어쓰기를 사용해주세요.",
                "suggestion": FilenameValidator._suggest_underscore_fix(base_name) + extension
            })

        # 2. 대괄호 사용 금지
        if "[" in filename or "]" in filename:
            violations.append({
                "type": FilenameValidator.VIOLATION_BRACKET_USAGE,
                "details": "대괄호 []를 사용하지 마세요. 제품명에 직접 포함시키거나 제거해주세요.",
                "suggestion": filename.replace("[", "").replace("]", "").replace("  ", " ").strip()
            })

        # 3. 버전 형식 검증 (.v 누락)
        # 버전처럼 보이는 패턴 찾기 (숫자.숫자 형태, 공백/언더스코어/점 뒤)
        # 전체 버전 번호를 찾기 위해 패턴 개선
        version_pattern = re.compile(r'(?:[\s\._]|^)(\d+(?:\.\d+)+)(?:\s|_|\.|\-|$)', re.IGNORECASE)
        matches = version_pattern.findall(base_name)

        # .v 형식이 있는지 확인
        has_v_format = re.search(r'[\s\._]v\d+', base_name, re.IGNORECASE)

        if matches and not has_v_format:
            # 버전처럼 보이는데 .v 형식이 아님 (가장 긴 버전 번호 선택)
            version_num = max(matches, key=len)
            violations.append({
                "type": FilenameValidator.VIOLATION_VERSION_FORMAT,
                "details": f"버전 '{version_num}'이 .v 형식이 아닙니다.",
                "suggestion": FilenameValidator._suggest_version_fix(base_name, version_num) + extension
            })

        # 4. 소문자로만 된 제품명 (파일명 전체가 소문자)
        if base_name.islower() and len(base_name) > 5:  # 너무 짧은 파일명은 제외
            violations.append({
                "type": FilenameValidator.VIOLATION_LOWERCASE_NAME,
                "details": "파일명이 모두 소문자입니다. 제품명은 공식 표기법을 사용해주세요.",
                "suggestion": FilenameValidator._suggest_title_case(base_name) + extension
            })

        # 5. 복잡한 파일명 (너무 긴 경우)
        if len(base_name) > 100:
            violations.append({
                "type": FilenameValidator.VIOLATION_COMPLEX_NAME,
                "details": f"파일명이 너무 깁니다 ({len(base_name)}자). 간결하게 작성해주세요.",
                "suggestion": "파일명을 '제품명.v버전-기타내용' 형식으로 단순화하세요."
            })

        # 6. 특수문자 검증 (허용: . - _ 공백)
        invalid_chars = set()
        for char in base_name:
            if not (char.isalnum() or char in ['.', '-', '_', ' ']):
                invalid_chars.add(char)

        if invalid_chars:
            violations.append({
                "type": FilenameValidator.VIOLATION_INVALID_CHARS,
                "details": f"허용되지 않는 특수문자 사용: {', '.join(invalid_chars)}",
                "suggestion": FilenameValidator._remove_invalid_chars(filename, invalid_chars)
            })

        return {
            "is_valid": len(violations) == 0,
            "violations": violations
        }

    @staticmethod
    def _suggest_underscore_fix(base_name: str) -> str:
        """언더스코어를 띄어쓰기로 변환"""
        # 연속된 언더스코어는 하나의 공백으로
        fixed = re.sub(r'_+', ' ', base_name)
        # 앞뒤 공백 제거
        return fixed.strip()

    @staticmethod
    def _suggest_version_fix(base_name: str, version_num: str) -> str:
        """버전 형식을 .v로 수정"""
        # 버전 번호 앞의 구분자와 함께 .v로 교체
        # 예: VMware Workstation Pro 16.0.0 → VMware Workstation Pro v16.0.0
        # 예: Total_Commander_10.51 → Total Commander v10.51

        # 버전 앞의 구분자 패턴 (공백, 언더스코어, 점)
        patterns = [
            (f"_{version_num}", f" v{version_num}"),  # 언더스코어 → 공백 v
            (f".{version_num}", f" v{version_num}"),  # 점 → 공백 v
            (f" {version_num}", f" v{version_num}"),  # 공백 → 공백 v
        ]

        fixed = base_name
        for old_pattern, new_pattern in patterns:
            if old_pattern in fixed:
                fixed = fixed.replace(old_pattern, new_pattern)
                break

        return fixed

    @staticmethod
    def _suggest_title_case(base_name: str) -> str:
        """제목 형식으로 변환 (각 단어의 첫 글자 대문자)"""
        words = base_name.replace("_", " ").replace("-", " - ").split()
        title_words = []
        for word in words:
            if word and word not in ["-", "."]:
                # 약어나 특수 케이스 처리
                if word in ["cc", "ui", "ux", "api", "sdk", "ide"]:
                    title_words.append(word.upper())
                else:
                    title_words.append(word.capitalize())
            else:
                title_words.append(word)
        return " ".join(title_words)

    @staticmethod
    def _remove_invalid_chars(filename: str, invalid_chars: set) -> str:
        """허용되지 않는 특수문자 제거"""
        fixed = filename
        for char in invalid_chars:
            fixed = fixed.replace(char, '')
        return fixed.strip()

    @staticmethod
    def get_standard_format_example() -> str:
        """표준 형식 예시 반환"""
        return """
표준 파일명 형식:
1. 완전한 형식: 제품명.v버전-기타내용.확장자
   예: Total Commander.v10.51-Final.zip

2. 버전 없음: 제품명-기타내용.확장자
   예: Adobe Photoshop-Portable.exe

3. 기본 형식: 제품명.v버전.확장자
   예: Microsoft Office.v2021.iso

4. 최소 형식: 제품명.확장자
   예: Notepad++.exe

규칙:
- 제품명: 공식 명칭 사용, 띄어쓰기 허용
- 버전: .v 접두사 필수 (예: .v10.51, .v2024)
- 기타내용: - 구분자 사용 (예: -Final, -Portable)
- 확장자: 소문자 권장
- 특수문자: 언더스코어(_) 대신 띄어쓰기, 대괄호([]) 사용 금지
        """
