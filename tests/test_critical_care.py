"""Tests for Critical Care Calculators"""
import pytest


class TestSofaCalculator:
    def test_sofa_basic(self):
        from src.domain.services.calculators import SofaScoreCalculator
        calc = SofaScoreCalculator()
        result = calc.calculate(
            pao2_fio2_ratio=400, platelets=150, bilirubin=1.0,
            gcs_score=15, creatinine=1.0
        )
        assert result.value >= 0
        assert result.interpretation is not None


class TestQsofaCalculator:
    def test_qsofa_basic(self):
        from src.domain.services.calculators import QsofaScoreCalculator
        calc = QsofaScoreCalculator()
        result = calc.calculate(respiratory_rate=22, systolic_bp=100, altered_mentation=True)
        assert result.value >= 0


class TestNewsCalculator:
    def test_news_basic(self):
        from src.domain.services.calculators import NewsScoreCalculator
        calc = NewsScoreCalculator()
        result = calc.calculate(
            respiratory_rate=18, spo2=96, on_supplemental_o2=False,
            temperature=37.0, systolic_bp=120, heart_rate=80, consciousness="A"
        )
        assert result.value >= 0


class TestGcsCalculator:
    def test_gcs_basic(self):
        from src.domain.services.calculators import GlasgowComaScaleCalculator
        calc = GlasgowComaScaleCalculator()
        result = calc.calculate(eye_response=4, verbal_response=5, motor_response=6)
        assert result.value == 15


class TestCamIcuCalculator:
    def test_cam_icu_basic(self):
        from src.domain.services.calculators import CamIcuCalculator
        calc = CamIcuCalculator()
        result = calc.calculate(
            rass_score=0, acute_onset_fluctuation=False,
            inattention_score=0, disorganized_thinking_errors=0
        )
        assert result.value in [0, 1]


class TestRassCalculator:
    def test_rass_basic(self):
        from src.domain.services.calculators import RassCalculator
        calc = RassCalculator()
        result = calc.calculate(rass_score=0)
        assert result.value == 0


class TestApacheIiCalculator:
    def test_apache_basic(self):
        from src.domain.services.calculators import ApacheIiCalculator
        calc = ApacheIiCalculator()
        result = calc.calculate(
            temperature=37.0, mean_arterial_pressure=80, heart_rate=80,
            respiratory_rate=16, fio2=0.21, pao2=80, arterial_ph=7.4,
            serum_sodium=140, serum_potassium=4.0, serum_creatinine=1.0,
            hematocrit=40, wbc_count=10, gcs_score=15, age=50,
            chronic_health_conditions=(), admission_type="elective_postoperative"
        )
        assert result.value >= 0
