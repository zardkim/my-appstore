import re
from typing import Dict, Optional


class FilenameParser:
    """
    파일명에서 소프트웨어 정보 추출
    """

    # 제거할 일반적인 키워드 (노이즈)
    NOISE_WORDS = {
        'setup', 'installer', 'install', 'portable', 'full', 'final',
        'crack', 'keygen', 'patch', 'x64', 'x86', 'win', 'mac', 'linux',
        'multilingual', 'retail', 'incl', 'repack', 'cracked', 'pre',
        'activated', 'registered',
        'bits', 'bit', 'dvd', 'cd', 'iso', 'img', 'exe', 'msi', 'zip', 'rar',
        'ssq', 'sse', 'rg', 'tbe', 'fosi', 'xforce', 'team'  # 릴리즈 그룹
    }

    # 에디션 키워드 (제품명에 포함)
    EDITION_WORDS = {
        'pro', 'plus', 'premium', 'ultimate', 'enterprise', 'professional',
        'home', 'business', 'student', 'standard', 'deluxe', 'complete'
    }

    # 알려진 제조사 목록 (첫 단어로 등장하는 경우)
    KNOWN_VENDORS = {
        'adobe', 'microsoft', 'autodesk', 'jetbrains', 'google',
        'apple', 'oracle', 'vmware', 'docker', 'slack', 'zoom',
        'spotify', 'discord', 'steam', 'epic', 'nvidia', 'amd', 'intel',
        'ds', 'dassault', 'solidworks', 'corel', 'ashampoo', 'wondershare',
        'cyberlink', 'nero', 'pixologic', 'maxon', 'foundry', 'siemens'
    }

    @staticmethod
    def parse(filename: str, parent_folder: str = "") -> Dict[str, Optional[str]]:
        """
        파일명 또는 폴더명에서 정보 추출

        Args:
            filename: 파일명 또는 폴더명
            parent_folder: 부모 폴더명 (파일명이 모호한 경우 사용)

        Returns:
            {
                'software_name': str,
                'version': str,
                'vendor': str (추정),
                'year': str
            }
        """
        # 확장자 제거
        name_without_ext = re.sub(r'\.[^.]+$', '', filename)

        # 특수문자를 공백으로 변환
        cleaned = re.sub(r'[._\-\[\]()]', ' ', name_without_ext)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        # 버전 정보 추출
        version = FilenameParser._extract_version(cleaned)

        # 연도 추출
        year = FilenameParser._extract_year(cleaned)

        # 소프트웨어 이름 추출 (버전, 연도, 노이즈 제거)
        software_name = FilenameParser._extract_software_name(
            cleaned, version, year
        )

        # 소프트웨어 이름이 너무 짧거나 일반적인 경우 부모 폴더명 사용
        if (len(software_name) < 3 or
            software_name.lower() in FilenameParser.NOISE_WORDS) and parent_folder:
            software_name = parent_folder

        # 제조사 추정
        vendor = FilenameParser._extract_vendor(software_name)

        # 포터블 여부 감지
        is_portable = FilenameParser._is_portable(filename, parent_folder)

        return {
            'software_name': software_name.strip(),
            'version': version,
            'vendor': vendor,
            'year': year,
            'is_portable': is_portable
        }

    @staticmethod
    def _extract_version(text: str) -> Optional[str]:
        """버전 정보 추출"""
        # 버전 패턴 (우선순위 순서)
        version_patterns = [
            r'v?(\d+\.\d+\.\d+\.\d+)',  # 1.2.3.4
            r'v?(\d+\.\d+\.\d+)',        # 1.2.3
            r'v?(\d+\.\d+)',             # 1.2
            r'\b(20\d{2})\b',            # 2022 (연도 형식 버전)
            r'\bSP(\d+)\b',              # SP1, SP2 (Service Pack)
            r'\bR(\d+)\b',               # R1, R2 (Release)
            r'\bv(\d+)\b',               # v1 (단독)
        ]

        versions = []
        for pattern in version_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                versions.append(match.group(1))

        # 여러 버전 정보가 있으면 결합
        if versions:
            return ' '.join(versions[:2])  # 최대 2개까지만

        return None

    @staticmethod
    def _extract_year(text: str) -> Optional[str]:
        """연도 추출 (2000-2099)"""
        match = re.search(r'\b(20\d{2})\b', text)
        return match.group(1) if match else None

    @staticmethod
    def _extract_software_name(text: str, version: str, year: str) -> str:
        """
        소프트웨어 이름 추출 (노이즈 제거)
        """
        result = text

        # 버전 정보 제거 (더 정교하게)
        if version:
            # 공백으로 분리된 버전들 각각 제거
            for ver in version.split():
                result = re.sub(rf'\bv?{re.escape(ver)}\b', '', result, flags=re.IGNORECASE)
                # SP1, R1 같은 패턴도 제거
                result = re.sub(rf'\bSP{re.escape(ver)}\b', '', result, flags=re.IGNORECASE)
                result = re.sub(rf'\bR{re.escape(ver)}\b', '', result, flags=re.IGNORECASE)

        # 연도 제거
        if year:
            result = re.sub(rf'\b{year}\b', '', result)

        # 단어 분리
        words = result.split()

        # 노이즈 단어 필터링
        filtered_words = []
        for word in words:
            word_lower = word.lower()

            # 에디션 단어는 유지
            if word_lower in FilenameParser.EDITION_WORDS:
                filtered_words.append(word)
            # 노이즈 단어가 아니고, 숫자만으로 구성되지 않은 경우
            elif (word_lower not in FilenameParser.NOISE_WORDS and
                  not word.isdigit() and
                  len(word) > 1):
                filtered_words.append(word)

        # 최대 6단어까지만 사용
        software_name = ' '.join(filtered_words[:6])

        return software_name if software_name else text.split()[0] if text.split() else 'Unknown'

    @staticmethod
    def _extract_vendor(software_name: str) -> Optional[str]:
        """
        제조사 추정 (첫 단어 또는 알려진 제조사 기준)
        """
        words = software_name.split()
        if not words:
            return None

        # 전체 이름에서 알려진 제조사 찾기
        name_lower = software_name.lower()
        for vendor in FilenameParser.KNOWN_VENDORS:
            if vendor in name_lower:
                # 실제 단어에서 찾아서 원래 대소문자 유지
                for word in words:
                    if word.lower() == vendor:
                        return word.capitalize()
                # 못 찾았으면 제조사명 그대로 반환
                if vendor == 'ds':
                    return 'Dassault Systemes'
                return vendor.capitalize()

        first_word = words[0].lower()

        # 첫 단어가 알려진 제조사인 경우
        if first_word in FilenameParser.KNOWN_VENDORS:
            if first_word == 'ds':
                return 'Dassault Systemes'
            return words[0].capitalize()

        # 첫 단어가 대문자로 시작하고 2글자 이상인 경우
        if len(words[0]) >= 2 and words[0][0].isupper():
            return words[0]

        return None

    @staticmethod
    def clean_metadata(metadata: Dict) -> Dict:
        """
        메타데이터 정제 (AI 응답 후처리용)
        """
        cleaned = metadata.copy()

        # 제목 정제
        if 'title' in cleaned and cleaned['title']:
            # 불필요한 따옴표 제거
            cleaned['title'] = cleaned['title'].strip('"\'')

        # 설명 정제
        if 'description' in cleaned and cleaned['description']:
            # 너무 긴 설명 자르기 (200자 제한)
            if len(cleaned['description']) > 200:
                cleaned['description'] = cleaned['description'][:197] + '...'

        # 카테고리 검증 (허용된 카테고리만)
        valid_categories = {
            'Graphics', 'Office', 'Development', 'Utility',
            'Media', 'OS', 'Security', 'Network',
            'Mac', 'Mobile', 'Patch', 'Driver', 'Source',
            'Backup', 'Business', 'Engineering',
            'Theme', 'Hardware'
        }
        if 'category' in cleaned and cleaned['category'] not in valid_categories:
            cleaned['category'] = 'Utility'  # 기본값

        return cleaned

    @staticmethod
    def _is_portable(filename: str, parent_folder: str = "") -> bool:
        """
        파일명 또는 폴더명에서 포터블 여부 감지

        Args:
            filename: 파일명
            parent_folder: 부모 폴더명

        Returns:
            포터블이면 True, 아니면 False
        """
        # 포터블 키워드 패턴
        portable_patterns = [
            r'\bportable\b',
            r'\bport\b',
            r'\bportableapps\b',
            r'\bgreen\b',  # Green Edition
            r'\bnoinstall\b',
            r'\bstandalone\b',
            r'\b포터블\b',
            r'\b휴대용\b'
        ]

        # 파일명과 폴더명을 소문자로 변환하여 검사
        text_to_check = f"{filename} {parent_folder}".lower()

        for pattern in portable_patterns:
            if re.search(pattern, text_to_check, re.IGNORECASE):
                return True

        return False
