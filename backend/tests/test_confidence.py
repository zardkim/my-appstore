"""규칙 기반 신뢰도 스코어링 (v1.4.64 도입).

AI 결과를 자동 등록해도 되는지 판단하는 데 쓰인다.
"""
from app.core import confidence as cf


class TestScore:
    def test_구체적인_메타데이터는_높은_점수(self):
        score = cf.calculate_confidence_score(
            {"title": "Adobe Photoshop 2024", "vendor": "Adobe", "release_year": 2024},
            {"software_name": "Photoshop"},
        )
        assert score >= 0.85
        assert cf.get_confidence_level(score) == "high"
        assert cf.should_auto_register(score) is True

    def test_빈약한_메타데이터는_낮은_점수(self):
        score = cf.calculate_confidence_score(
            {"title": "setup", "vendor": "", "release_year": None},
            {"software_name": "setup"},
        )
        assert score <= 0.3
        assert cf.get_confidence_level(score) == "low"
        assert cf.should_auto_register(score) is False

    def test_점수는_0과_1_사이(self):
        for meta in (
            {"title": "", "vendor": "", "release_year": None},
            {"title": "X" * 300, "vendor": "V", "release_year": 2024},
        ):
            s = cf.calculate_confidence_score(meta, {"software_name": "x"})
            assert 0.0 <= s <= 1.0


class TestThreshold:
    def test_임계값_경계(self):
        assert cf.should_auto_register(0.85, threshold=0.85) is True
        assert cf.should_auto_register(0.84, threshold=0.85) is False

    def test_임계값을_바꿀_수_있다(self):
        assert cf.should_auto_register(0.5, threshold=0.4) is True
