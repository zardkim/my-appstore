"""FilenameParser 단위 테스트.

이 라이브러리의 파일명은 대부분 **언더스코어로 구분**된다
(RaiDrive_2020.6.25.zip, HeidiSQL_12.21_64_Portable.zip …).
정규식에 `\\b` 를 쓰면 `_` 가 단어 문자라 경계가 생기지 않으므로,
구분자별 케이스를 반드시 함께 검사한다.
"""
import pytest

from app.core.parser import FilenameParser


@pytest.fixture
def parser():
    return FilenameParser()


class TestParse:
    def test_버전과_연도를_함께_뽑는다(self, parser):
        r = parser.parse("Adobe_Photoshop_2024_v25.0.iso")
        assert r["version"] == "25.0"
        assert r["year"] == "2024"

    def test_제조사는_이름에서_제거된다(self, parser):
        r = parser.parse("Adobe_Photoshop_2024_v25.0.iso")
        assert "Adobe" not in r["software_name"]

    def test_버전만_있고_연도가_없는_경우(self, parser):
        r = parser.parse("HeidiSQL_12.21_64_Portable.zip")
        assert r["software_name"] == "HeidiSQL"
        assert r["version"] == "12.21"
        assert r["year"] is None

    def test_의미없는_파일명도_깨지지_않는다(self, parser):
        r = parser.parse("setup.exe")
        assert r["version"] is None
        assert r["year"] is None


class TestReleaseYear:
    """v1.4.63 회귀: 연도/에디션이 다른 제품이 같은 제품으로 오인 매칭되던 버그.

    구조적 해결로 products.release_year 컬럼이 도입됐다(v1.4.64).
    """

    @pytest.mark.parametrize("title,folder,expected", [
        ("AutoCAD 2026", "", 2026),
        ("Office 2003", "/lib/Office_2003", 2003),
        ("7-Zip", "", None),
    ])
    def test_제목과_폴더에서_연도_추출(self, title, folder, expected):
        assert FilenameParser.extract_release_year(title, folder) == expected

    @pytest.mark.parametrize("value,expected", [
        ("2026", 2026),
        (2027, 2027),
        ("v25.0", None),   # 버전은 연도가 아니다 - 이걸 섞으면 오매칭이 난다
        ("abc", None),
        (None, None),
    ])
    def test_AI_응답의_release_year_파싱(self, value, expected):
        assert FilenameParser.parse_ai_release_year(value) == expected


class TestIsPortable:
    """구분자가 무엇이든 포터블을 감지해야 한다.

    `\\b` 만 쓰면 `_Portable` 이 걸리지 않는다 (`_` 가 단어 문자라 경계가 없다).
    이 라이브러리는 언더스코어 파일명이 대부분이라 영향이 크다.
    """

    @pytest.mark.parametrize("filename", [
        "App Portable.zip",
        "App-Portable.zip",
        "HeidiSQL_12.21_64_Portable.zip",
        "Portable_App.zip",
        "App_PortableApps.zip",
        "App_NoInstall.zip",
        "App_Standalone.zip",
    ])
    def test_포터블로_감지한다(self, filename):
        assert FilenameParser._is_portable(filename, "") is True

    @pytest.mark.parametrize("filename", [
        "Photoshop.iso",
        "RaiDrive_2020.6.25.zip",
    ])
    def test_포터블이_아니다(self, filename):
        assert FilenameParser._is_portable(filename, "") is False

    def test_한글_키워드(self):
        assert FilenameParser._is_portable("앱_포터블.zip", "") is True
        assert FilenameParser._is_portable("앱_무설치.zip", "") is True

    def test_폴더명으로도_감지한다(self):
        assert FilenameParser._is_portable("App.zip", "/library/Portable Apps") is True

    def test_단어_중간에_들어간_것은_제외(self):
        # Greenshot 은 포터블 표시가 아니다
        assert FilenameParser._is_portable("Greenshot.exe", "") is False


class TestSplitArchive:
    @pytest.mark.parametrize("filename,expected", [
        ("a.part1.rar", True),
        ("a.part01.rar", True),
        ("a.z01", True),
        ("a.r00", True),
        ("a.001", True),
        ("a.7z.001", True),
        ("a.zip", False),
        ("a.exe", False),
    ])
    def test_분할압축_판정(self, parser, filename, expected):
        assert parser.is_split_archive(filename) is expected
