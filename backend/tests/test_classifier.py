"""classify_file 단위 테스트.

파일명 + 폴더명으로 product / patch / language_pack / manual / update 를 판정한다.
구분자(공백 / 하이픈 / 언더스코어)에 따라 결과가 달라지면 안 된다.
"""
import pytest

from app.core.classifier import classify_file


class TestBasicClassification:
    @pytest.mark.parametrize("filename,folder,expected", [
        ("setup.exe", "App", "product"),
        ("installer.msi", "App", "product"),
        ("manual.pdf", "App", "manual"),
        ("crack.exe", "App", "patch"),
        ("Korean_LangPack.zip", "App", "language_pack"),
    ])
    def test_기본_분류(self, filename, folder, expected):
        assert classify_file(filename, folder) == expected

    def test_동봉된_패치_언급은_product_로_둔다(self):
        # "+ Fix" 는 패치가 동봉됐다는 표현이지 그 파일이 패치인 건 아니다
        assert classify_file("Autodesk Maya v2026 + Fix (macOS).zip", "App") == "product"


class TestServicePack:
    """sp1/sp2 같은 서비스팩 표기는 update 로 분류돼야 한다.

    `\\bsp\\d+\\b` 만 쓰면 `_sp2` 가 걸리지 않는다 (`_` 가 단어 문자).
    """

    @pytest.mark.parametrize("filename", [
        "app sp2.exe",
        "app-sp2.exe",
        "app_sp2.exe",
        "Office_2003_SP3.iso",
    ])
    def test_서비스팩은_update(self, filename):
        assert classify_file(filename, "App") == "update"

    def test_sp_가_단어_일부면_update_가_아니다(self):
        # "spring", "sparrow" 등이 걸리면 안 된다
        assert classify_file("spring_boot_3.zip", "App") != "update"


class TestFolderContext:
    def test_폴더명도_판정에_쓰인다(self):
        # 파일명만으로는 알 수 없는 경우 폴더명이 문맥이 된다
        assert classify_file("readme.pdf", "App") == "manual"
