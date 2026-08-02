import os
import re
from typing import Dict, Optional

from app.core.keywords import PATCH_KEYWORDS


class FilenameParser:
    """
    파일명에서 소프트웨어 정보 추출
    """

    # 제거할 일반적인 키워드 (노이즈)
    # 패치/크랙 관련 키워드는 classifier.py와 공유하는 app.core.keywords.PATCH_KEYWORDS를
    # 그대로 합쳐서, 두 모듈이 서로 다른 키워드 세트를 관리하다 생기는 불일치
    # (예: "fix"가 classifier에는 있지만 parser에는 없던 문제)를 방지한다.
    NOISE_WORDS = {
        # 설치 관련
        'setup', 'installer', 'install', 'portable', 'full', 'final', 'with',
        # 크랙/인증 관련
        'crack', 'keygen', 'patch', 'serial', 'key', 'keys', 'cracked',
        'activation', 'activator', 'activated', 'registered', 'licensed',
        # 아키텍처
        'x64', 'x86', 'ia64', 'x32', 'win', 'mac', 'macos', 'linux', 'bits', 'bit',
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
        'readme', 'instructions', 'screenshot', 'preview', 'info', 'dlm'
    } | PATCH_KEYWORDS

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

        # 제조사명이 소프트웨어 이름에 중복으로 남아있으면 제거
        # (예: "Autodesk AutoCAD" + vendor "Autodesk" → "AutoCAD")
        if vendor:
            software_name = FilenameParser._remove_vendor_from_name(software_name, vendor)

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
            # 아래 패턴들은 원래 \b를 썼으나, '_'가 단어 문자로 취급되어
            # 'v2026'/'_2024_'처럼 문자·언더스코어에 바로 붙은 경우 매치되지
            # 않는 문제가 있었음. 숫자 경계는 (?<!\d)/(?!\d)로, 'v'/'SP'/'R'
            # 앞 경계는 영숫자만 배제하는 방식으로 교체.
            r'(?<!\d)(365|360|2024|2023|2022|2021|2020|2019|2018|2017|2016)(?!\d)',  # Office 365, 2021 등 특수 버전
            r'(?<!\d)(20\d{2})(?!\d)',       # 2022 (연도 형식 버전)
            r'(?<![A-Za-z0-9])SP(\d+)(?!\d)',  # SP1, SP2 (Service Pack)
            r'(?<![A-Za-z0-9])R(\d+)(?!\d)',   # R1, R2 (Release)
            r'(?<![A-Za-z0-9])v(\d+)(?!\d)',   # v1 (단독)
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
        r"""연도 추출 (1900-2099)

        \b는 '_'를 단어 문자로 취급하므로 'v2026', '_2024_'처럼 연도가
        영문자/언더스코어에 바로 붙어있으면 \b(20\d{2})\b가 매치되지 않는다.
        숫자가 아닌 문자 경계를 직접 확인해 이 문제를 회피한다.
        """
        match = re.search(r'(?<!\d)((?:19|20)\d{2})(?!\d)', text)
        return match.group(1) if match else None

    @staticmethod
    def extract_release_year(title: str, folder_path: str = None) -> Optional[int]:
        """title에서 연도를 추출하고, 없으면 folder_path의 폴더명에서 재시도.

        AI가 title을 생성할 때 연도를 생략하는 경우가 있어(예: "AutoCAD 2026"
        폴더 → title "AutoCAD"), 원본 폴더명으로 폴백해 Product.release_year를
        계산한다. auto_matcher.py의 버전 분리 가드와 동일한 폴백 순서를 따른다.
        """
        year = FilenameParser._extract_year(title or "")
        if not year and folder_path:
            folder_name = os.path.basename(folder_path.rstrip('/\\'))
            year = FilenameParser._extract_year(folder_name)
        return int(year) if year else None

    @staticmethod
    def parse_ai_release_year(value) -> Optional[int]:
        """AI 응답의 release_year 필드 값을 검증된 int로 변환.

        AI가 "", "N/A", 잘못된 자릿수 등을 반환할 수 있으므로 1900-2099
        범위의 4자리 숫자 문자열만 허용하고, 그 외에는 None을 반환해
        호출측이 title/folder_path 정규식 폴백을 타도록 한다.
        """
        if value in (None, ''):
            return None
        text = str(value).strip()
        match = re.fullmatch(r'(?:19|20)\d{2}', text)
        return int(match.group(0)) if match else None

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

        # KNOWN_VENDORS에 없으면 확인되지 않은 추정이므로 반환하지 않음
        # (예전에는 대문자로 시작하는 첫 단어를 제조사로 추정했으나,
        #  이는 검증되지 않은 추측이라 오탐이 많아 제거함)
        return None

    @staticmethod
    def _remove_vendor_from_name(software_name: str, vendor: str) -> str:
        """
        소프트웨어 이름에서 제조사명을 제거 (중복 방지)
        예: "Autodesk AutoCAD" + vendor "Autodesk" → "AutoCAD"
        """
        cleaned = re.sub(rf'\b{re.escape(vendor)}\b', '', software_name, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        # 제조사명이 이름 전체였던 경우(제거 시 빈 문자열)에는 원본 유지
        return cleaned if cleaned else software_name

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
        # 포터블 키워드 패턴 (영문, 단어 경계 기준)
        portable_patterns_en = [
            r'\bportable\b',
            r'\bportableapps\b',
            r'\bgreen\b',           # Green Edition
            r'\bnoinstall\b',
            r'\bno[_\-]install\b',
            r'\bstandalone\b',
            r'\bstand[_\-]alone\b',
        ]

        # 포터블 키워드 (한국어 - 원문 포함 검사)
        portable_keywords_ko = [
            '포터블',
            '휴대용',
            '무설치',
            '단일실행',
            '이식가능',
        ]

        combined = f"{filename} {parent_folder}"
        combined_lower = combined.lower()

        for pattern in portable_patterns_en:
            if re.search(pattern, combined_lower):
                return True

        for keyword in portable_keywords_ko:
            if keyword in combined:
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

