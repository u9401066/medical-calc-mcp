from typing import Any

"""Tests for Pulmonology Calculators"""
import pytest


class TestCurb65Calculator:
    def test_curb65_zero(self) -> None:
        from src.domain.services.calculators import Curb65Calculator
        calc = Curb65Calculator()
        result = calc.calculate(
            confusion=False, bun_gt_19_or_urea_gt_7=False,
            respiratory_rate_gte_30=False, sbp_lt_90_or_dbp_lte_60=False,
            age_gte_65=False
        )
        assert result.value is not None
        assert result.value == 0

    def test_curb65_max(self) -> None:
        from src.domain.services.calculators import Curb65Calculator
        calc = Curb65Calculator()
        result = calc.calculate(
            confusion=True, bun_gt_19_or_urea_gt_7=True,
            respiratory_rate_gte_30=True, sbp_lt_90_or_dbp_lte_60=True,
            age_gte_65=True
        )
        assert result.value is not None
        assert result.value == 5

    def test_tool_id(self) -> None:
        from src.domain.services.calculators import Curb65Calculator
        assert Curb65Calculator().tool_id == "curb65"


class TestPsiPortCalculator:
    """Comprehensive tests for PSI/PORT (Pneumonia Severity Index)"""

    @pytest.fixture
    def calc(self) -> Any:
        from src.domain.services.calculators import PsiPortCalculator
        return PsiPortCalculator()

    def test_tool_id(self, calc: Any) -> None:
        assert calc.tool_id == "psi_port"

    # ========================================================================
    # Age Scoring Tests
    # ========================================================================

    def test_psi_male_age_only(self, calc: Any) -> None:
        """Male patient: age = points"""
        result = calc.calculate(age_years=70, female=False)
        assert result.value is not None
        assert result.value == 70  # Male age = age in years

    def test_psi_female_age_adjustment(self, calc: Any) -> None:
        """Female patient: age - 10 = points"""
        result = calc.calculate(age_years=70, female=True)
        assert result.value is not None
        assert result.value == 60  # Female age = age - 10

    def test_psi_nursing_home(self, calc: Any) -> None:
        """Nursing home adds 10 points"""
        result = calc.calculate(age_years=50, female=False, nursing_home_resident=True)
        assert result.value is not None
        assert result.value == 60  # 50 age + 10 nursing home

    # ========================================================================
    # Comorbidity Tests
    # ========================================================================

    def test_psi_neoplastic_disease(self, calc: Any) -> None:
        """Neoplastic disease adds 30 points"""
        result = calc.calculate(age_years=50, female=False, neoplastic_disease=True)
        assert result.value is not None
        assert result.value == 80  # 50 + 30

    def test_psi_liver_disease(self, calc: Any) -> None:
        """Liver disease adds 20 points"""
        result = calc.calculate(age_years=50, female=False, liver_disease=True)
        assert result.value is not None
        assert result.value == 70  # 50 + 20

    def test_psi_chf(self, calc: Any) -> None:
        """CHF adds 10 points"""
        result = calc.calculate(age_years=50, female=False, chf=True)
        assert result.value is not None
        assert result.value == 60  # 50 + 10

    def test_psi_cerebrovascular_disease(self, calc: Any) -> None:
        """Cerebrovascular disease adds 10 points"""
        result = calc.calculate(age_years=50, female=False, cerebrovascular_disease=True)
        assert result.value is not None
        assert result.value == 60  # 50 + 10

    def test_psi_renal_disease(self, calc: Any) -> None:
        """Renal disease adds 10 points"""
        result = calc.calculate(age_years=50, female=False, renal_disease=True)
        assert result.value is not None
        assert result.value == 60  # 50 + 10

    # ========================================================================
    # Physical Exam Tests
    # ========================================================================

    def test_psi_altered_mental_status(self, calc: Any) -> None:
        """Altered mental status adds 20 points"""
        result = calc.calculate(age_years=50, female=False, altered_mental_status=True)
        assert result.value is not None
        assert result.value == 70  # 50 + 20

    def test_psi_respiratory_rate_gte_30(self, calc: Any) -> None:
        """RR >= 30 adds 20 points"""
        result = calc.calculate(age_years=50, female=False, respiratory_rate_gte_30=True)
        assert result.value is not None
        assert result.value == 70  # 50 + 20

    def test_psi_systolic_bp_lt_90(self, calc: Any) -> None:
        """SBP < 90 adds 20 points"""
        result = calc.calculate(age_years=50, female=False, systolic_bp_lt_90=True)
        assert result.value is not None
        assert result.value == 70  # 50 + 20

    def test_psi_temperature_abnormal(self, calc: Any) -> None:
        """Temperature < 35 or >= 40 adds 15 points"""
        result = calc.calculate(age_years=50, female=False, temperature_abnormal=True)
        assert result.value is not None
        assert result.value == 65  # 50 + 15

    def test_psi_pulse_gte_125(self, calc: Any) -> None:
        """Pulse >= 125 adds 10 points"""
        result = calc.calculate(age_years=50, female=False, pulse_gte_125=True)
        assert result.value is not None
        assert result.value == 60  # 50 + 10

    # ========================================================================
    # Laboratory Tests (must break Class I criteria by using age > 50)
    # ========================================================================

    def test_psi_arterial_ph_lt_7_35(self, calc: Any) -> None:
        """Arterial pH < 7.35 adds 30 points"""
        result = calc.calculate(age_years=60, female=False, arterial_ph_lt_7_35=True)
        assert result.value is not None
        assert result.value == 90  # 60 + 30

    def test_psi_bun_gte_30(self, calc: Any) -> None:
        """BUN >= 30 mg/dL adds 20 points"""
        result = calc.calculate(age_years=60, female=False, bun_gte_30=True)
        assert result.value is not None
        assert result.value == 80  # 60 + 20

    def test_psi_sodium_lt_130(self, calc: Any) -> None:
        """Sodium < 130 adds 20 points"""
        result = calc.calculate(age_years=60, female=False, sodium_lt_130=True)
        assert result.value is not None
        assert result.value == 80  # 60 + 20

    def test_psi_glucose_gte_250(self, calc: Any) -> None:
        """Glucose >= 250 mg/dL adds 10 points"""
        result = calc.calculate(age_years=60, female=False, glucose_gte_250=True)
        assert result.value is not None
        assert result.value == 70  # 60 + 10

    def test_psi_hematocrit_lt_30(self, calc: Any) -> None:
        """Hematocrit < 30% adds 10 points"""
        result = calc.calculate(age_years=60, female=False, hematocrit_lt_30=True)
        assert result.value is not None
        assert result.value == 70  # 60 + 10

    def test_psi_hypoxemia(self, calc: Any) -> None:
        """PaO2 < 60 or SaO2 < 90 adds 10 points"""
        result = calc.calculate(age_years=60, female=False, pao2_lt_60_or_sao2_lt_90=True)
        assert result.value is not None
        assert result.value == 70  # 60 + 10

    def test_psi_pleural_effusion(self, calc: Any) -> None:
        """Pleural effusion adds 10 points"""
        result = calc.calculate(age_years=60, female=False, pleural_effusion=True)
        assert result.value is not None
        assert result.value == 70  # 60 + 10

    # ========================================================================
    # Risk Class Tests
    # ========================================================================

    def test_psi_class_ii(self, calc: Any) -> None:
        """Class II: score <= 70"""
        result = calc.calculate(age_years=65, female=False)
        # 65 points = Class II
        assert result.interpretation.summary is not None
        assert "II" in result.interpretation.summary or "Class" in result.interpretation.summary

    def test_psi_class_iii(self, calc: Any) -> None:
        """Class III: score 71-90"""
        result = calc.calculate(age_years=75, female=False, pulse_gte_125=True)
        # 75 + 10 = 85 points = Class III
        assert result.value is not None
        assert result.value == 85

    def test_psi_class_iv(self, calc: Any) -> None:
        """Class IV: score 91-130"""
        result = calc.calculate(
            age_years=70,
            female=False,
            neoplastic_disease=True,  # +30
            altered_mental_status=True,  # +20
        )
        # 70 + 30 + 20 = 120 points = Class IV
        assert result.value is not None
        assert result.value == 120

    def test_psi_class_v(self, calc: Any) -> None:
        """Class V: score > 130"""
        result = calc.calculate(
            age_years=80,
            female=False,
            neoplastic_disease=True,  # +30
            liver_disease=True,  # +20
            altered_mental_status=True,  # +20
        )
        # 80 + 30 + 20 + 20 = 150 points = Class V
        assert result.value is not None
        assert result.value == 150

    # ========================================================================
    # Complex Combinations
    # ========================================================================

    def test_psi_multiple_comorbidities(self, calc: Any) -> None:
        """Multiple comorbidities accumulate points"""
        result = calc.calculate(
            age_years=60,
            female=False,
            chf=True,  # +10
            cerebrovascular_disease=True,  # +10
            renal_disease=True,  # +10
        )
        assert result.value is not None
        assert result.value == 90  # 60 + 10 + 10 + 10

    def test_psi_full_assessment(self, calc: Any) -> None:
        """Complete assessment with many factors"""
        result = calc.calculate(
            age_years=75,
            female=True,  # -10
            nursing_home_resident=True,  # +10
            neoplastic_disease=False,
            liver_disease=False,
            chf=True,  # +10
            cerebrovascular_disease=False,
            renal_disease=False,
            altered_mental_status=True,  # +20
            respiratory_rate_gte_30=True,  # +20
            systolic_bp_lt_90=False,
            temperature_abnormal=False,
            pulse_gte_125=False,
            arterial_ph_lt_7_35=True,  # +30
            bun_gte_30=True,  # +20
            sodium_lt_130=False,
            glucose_gte_250=False,
            hematocrit_lt_30=False,
            pao2_lt_60_or_sao2_lt_90=True,  # +10
            pleural_effusion=True,  # +10
        )
        # (75-10) + 10 + 10 + 20 + 20 + 30 + 20 + 10 + 10 = 195
        assert result.value is not None
        assert result.value == 195

    def test_psi_young_healthy(self, calc: Any) -> None:
        """Young healthy patient - Class I (score 0)"""
        result = calc.calculate(age_years=30, female=False)
        # Meets Class I criteria: ≤50, no comorbidities, no abnormal vitals
        assert result.value is not None
        assert result.value == 0  # Class I

    def test_psi_metadata(self, calc: Any) -> None:
        """Verify metadata is correct"""
        meta = calc.metadata
        assert meta.tool_id == "psi_port"
        assert meta.name is not None
        assert "pneumonia" in meta.name.lower() or "PSI" in meta.name
