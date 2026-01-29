import re
from typing import Dict, Optional


class FilenameParser:
    """
    파일명에서 소프트웨어 정보 추출
    """

    # 제거할 일반적인 키워드 (노이즈)
    NOISE_WORDS = {
        # 설치 관련
        'setup', 'installer', 'install', 'portable', 'full', 'final', 'with',
        # 크랙/인증 관련
        'crack', 'keygen', 'patch', 'serial', 'key', 'keys', 'cracked',
        'activation', 'activator', 'activated', 'registered', 'licensed',
        # 아키텍처
        'x64', 'x86', 'ia64', 'x32', 'win', 'mac', 'linux', 'bits', 'bit',
        # 에디션 타입
        'multilingual', 'retail', 'oem', 'vlsc', 'vol', 'trial',
        # 패키징
        'repack', 'repacked', 'incl', 'pre', 'extras', 'addon', 'addons',
        'custom', 'embedded', 'delta', 'winpe',
        # 빌드 관련 (ltsc 제거 - Office 버전 구분에 중요)
        'build', 'sp1', 'sp2', 'sp3', 'r1', 'r2',
        # 파일 확장자
        'dvd', 'cd', 'iso', 'img', 'exe', 'msi', 'zip', 'rar', '7z', 'cab',
        # 릴리즈 그룹/사이트
        'sadeempc', 'downloadly', 'tryroom', 'koreacrack', 'kpojiuk',
        'xetrin', 'yaschir', 'ssq', 'sse', 'rg', 'tbe', 'fosi', 'xforce', 'team',
        # 한글 노이즈
        '한국어판', '설치법', '인증방법', '스크린샷', '포터블', '휴대용',
        # 기타
        'readme', 'instructions', 'screenshot', 'preview', 'info'
    }

    # 에디션 키워드 (제품명에 포함)
    EDITION_WORDS = {
        'pro', 'plus', 'premium', 'ultimate', 'enterprise', 'professional',
        'home', 'business', 'student', 'standard', 'deluxe', 'complete',
        'technician', 'server', 'advanced', 'workstation', 'edition',
        'master', 'suite', 'studio', 'creative', 'cloud'
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

        # 버전 정보를 먼저 추출 (노이즈 제거 전)
        version = FilenameParser._extract_version(name_without_ext)

        # 연도 추출 (노이즈 제거 전)
        year = FilenameParser._extract_year(name_without_ext)

        # 릴리즈 그룹 패턴 제거 (by xxx, [xxx])
        name_without_ext = re.sub(r'\bby\s+\w+', '', name_without_ext, flags=re.IGNORECASE)
        name_without_ext = re.sub(r'\[.*?\]', '', name_without_ext)

        # ===== TOP 2: x64/x86 아키텍처 제거 (빈도: 4.5%) =====
        # 패턴: _x64_, .x86., (x64) 등
        name_without_ext = re.sub(r'[._\s](x64|x86|32bit|64bit)[._\s]', ' ', name_without_ext, flags=re.IGNORECASE)
        name_without_ext = re.sub(r'\((x64|x86|32bit|64bit|win|portable)\)', '', name_without_ext, flags=re.IGNORECASE)

        # Build 번호 패턴 제거 (빈도: 1.4%)
        name_without_ext = re.sub(r'\bbuild[_\s]*\d+', '', name_without_ext, flags=re.IGNORECASE)

        # 웹사이트 도메인 제거 (.ir, .com 등)
        name_without_ext = re.sub(r'\.\w{2,3}($|\s)', ' ', name_without_ext)

        # 특수문자를 공백으로 변환
        cleaned = re.sub(r'[._\-\[\]()]', ' ', name_without_ext)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

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
        # 버전 패턴 (우선순위 순서 - v 접두사 우선)
        version_patterns = [
            r'v(\d+\.\d+\.\d+\.\d+)',        # v1.2.3.4 (v 접두사 우선)
            r'v(\d+\.\d+\.\d+)',             # v1.2.3 (v 접두사 우선)
            r'v(\d+\.\d+)',                  # v1.2 (v 접두사 우선)
            r'(\d+\.\d+\.\d+\.\d+\.\d+)',    # 1.2.3.4.5 (매우 복잡한 버전)
            r'(\d+\.\d+\.\d+\.\d+)',         # 1.2.3.4
            r'(\d+\.\d+\.\d+)',              # 1.2.3
            r'[\s_](\d+\.\d+)[\s_]',         # 공백/언더스코어로 둘러싸인 1.2
            r'\b(365|360|2024|2023|2022|2021|2020|2019|2018|2017|2016)\b',  # Office 365, 2021 등 특수 버전
            r'\b(20\d{2})\b',                # 2022 (연도 형식 버전)
            r'\bSP(\d+)\b',                  # SP1, SP2 (Service Pack)
            r'\bR(\d+)\b',                   # R1, R2 (Release)
            r'\bv(\d+)\b',                   # v1 (단독)
        ]

        versions = []
        for pattern in version_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                ver = match.group(1)
                # 너무 긴 버전은 첫 3-4단계만 사용
                if ver.count('.') > 3:
                    parts = ver.split('.')
                    ver = '.'.join(parts[:3])
                versions.append(ver)

        # 여러 버전 정보가 있으면 첫 번째만 사용
        if versions:
            return versions[0]

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

    @staticmethod
    def is_split_archive(filename: str) -> bool:
        """
        분할 압축 파일 여부 확인

        Args:
            filename: 파일명

        Returns:
            분할 압축 파일이면 True, 아니면 False
        """
        # 분할 압축 파일 패턴
        split_patterns = [
            r'\.part\d+\.rar$',      # .part01.rar, .part001.rar
            r'\.part\d+$',           # .part01, .part02
            r'\.z\d{2,3}$',          # .z01, .z02, .z001
            r'\.r\d{2,3}$',          # .r00, .r01, .r02 (WinRAR old format)
            r'\.\d{3}$',             # .001, .002, .003
            r'\.7z\.\d{3}$',         # .7z.001, .7z.002
        ]

        filename_lower = filename.lower()
        for pattern in split_patterns:
            if re.search(pattern, filename_lower):
                return True

        return False

