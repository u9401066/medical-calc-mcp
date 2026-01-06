from typing import Any

"""
Tests for Phase 10 High-Priority Calculators

Tests for:
- Corrected QT (QTc) Calculator
- Alveolar-arterial (A-a) Gradient Calculator
- Shock Index (SI) Calculator
"""

import math

import pytest

from src.domain.services.calculators import (
    AaGradientCalculator,
    CorrectedQtCalculator,
    ShockIndexCalculator,
)
from src.domain.value_objects.interpretation import RiskLevel, Severity


class TestCorrectedQtCalculator:
    """Tests for Corrected QT Interval Calculator"""

    @pytest.fixture
    def calculator(self) -> Any:
        return CorrectedQtCalculator()

    # Basic formula tests
    def test_bazett_formula_normal_hr(self, calculator: Any) -> None:
        """QTc = QT / √RR with normal heart rate"""
        # QT=400ms, HR=60 → RR=1.0s → QTc=400
        result = calculator.calculate(qt_interval=400, heart_rate=60, formula="bazett")
        assert result.value is not None
        assert result.value == 400.0

    def test_bazett_formula_tachycardia(self, calculator: Any) -> None:
        """Bazett overcorrects in tachycardia"""
        # QT=350ms, HR=100 → RR=0.6s → QTc=350/√0.6 ≈ 452
        result = calculator.calculate(qt_interval=350, heart_rate=100, formula="bazett")
        expected = 350 / math.sqrt(0.6)
        assert result.value is not None
        assert abs(result.value - round(expected, 0)) < 1

    def test_fridericia_formula(self, calculator: Any) -> None:
        """QTc = QT / ∛RR (Fridericia)"""
        # QT=400ms, HR=60 → RR=1.0s → QTc=400/∛1.0=400
        result = calculator.calculate(qt_interval=400, heart_rate=60, formula="fridericia")
        assert result.value is not None
        assert result.value == 400.0

    def test_fridericia_vs_bazett_tachycardia(self, calculator: Any) -> None:
        """Fridericia less affected by tachycardia than Bazett"""
        qt = 350
        hr = 120
        60 / hr

        bazett = calculator.calculate(qt_interval=qt, heart_rate=hr, formula="bazett")
        fridericia = calculator.calculate(qt_interval=qt, heart_rate=hr, formula="fridericia")

        # Fridericia should give lower value in tachycardia
        assert fridericia.value is not None
        assert fridericia.value < bazett.value

    def test_framingham_formula(self, calculator: Any) -> None:
        """Framingham linear correction: QTc = QT + 154 × (1 - RR)"""
        # QT=400ms, HR=60 → RR=1.0s → QTc=400+154*(1-1)=400
        result = calculator.calculate(qt_interval=400, heart_rate=60, formula="framingham")
        assert result.value is not None
        assert result.value == 400.0

    # Interpretation tests
    def test_normal_qtc_male(self, calculator: Any) -> None:
        """Normal QTc for male (≤450ms)"""
        result = calculator.calculate(qt_interval=400, heart_rate=60, sex="male")
        assert result.interpretation.severity is not None
        assert result.interpretation.severity == Severity.NORMAL
        assert result.interpretation.risk_level is not None
        assert result.interpretation.risk_level == RiskLevel.VERY_LOW

    def test_normal_qtc_female(self, calculator: Any) -> None:
        """Normal QTc for female (≤460ms)"""
        result = calculator.calculate(qt_interval=420, heart_rate=60, sex="female")
        assert result.interpretation.severity is not None
        assert result.interpretation.severity == Severity.NORMAL

    def test_borderline_qtc_male(self, calculator: Any) -> None:
        """Borderline QTc for male (450-470ms)"""
        # Calculate what QT gives QTc around 460
        # At HR=60 (RR=1), QT=QTc for Bazett
        result = calculator.calculate(qt_interval=460, heart_rate=60, sex="male")
        assert result.interpretation.severity is not None
        assert result.interpretation.severity == Severity.MILD
        assert result.interpretation.risk_level is not None
        assert result.interpretation.risk_level == RiskLevel.LOW

    def test_prolonged_qtc(self, calculator: Any) -> None:
        """Prolonged QTc (>470ms male, ≤500ms)"""
        result = calculator.calculate(qt_interval=490, heart_rate=60, sex="male")
        assert result.interpretation.severity is not None
        assert result.interpretation.severity == Severity.MODERATE
        assert result.interpretation.risk_level is not None
        assert result.interpretation.risk_level == RiskLevel.INTERMEDIATE

    def test_markedly_prolonged_qtc(self, calculator: Any) -> None:
        """Markedly prolonged QTc (>500ms) - high TdP risk"""
        result = calculator.calculate(qt_interval=520, heart_rate=60, sex="male")
        assert result.interpretation.severity is not None
        assert result.interpretation.severity == Severity.SEVERE
        assert result.interpretation.risk_level is not None
        assert result.interpretation.risk_level == RiskLevel.HIGH
        assert result.interpretation.warnings is not None
        assert any("CRITICAL" in w for w in result.interpretation.warnings)

    # Edge cases and validation
    def test_invalid_qt_too_low(self, calculator: Any) -> None:
        """QT < 200ms should raise error"""
        with pytest.raises(ValueError, match="outside physiological range"):
            calculator.calculate(qt_interval=150, heart_rate=70)

    def test_invalid_qt_too_high(self, calculator: Any) -> None:
        """QT > 800ms should raise error"""
        with pytest.raises(ValueError, match="outside physiological range"):
            calculator.calculate(qt_interval=850, heart_rate=70)

    def test_invalid_hr_too_low(self, calculator: Any) -> None:
        """HR < 30 bpm should raise error"""
        with pytest.raises(ValueError, match="outside physiological range"):
            calculator.calculate(qt_interval=400, heart_rate=25)

    def test_invalid_hr_too_high(self, calculator: Any) -> None:
        """HR > 250 bpm should raise error"""
        with pytest.raises(ValueError, match="outside physiological range"):
            calculator.calculate(qt_interval=300, heart_rate=280)

    def test_invalid_formula(self, calculator: Any) -> None:
        """Unknown formula should raise error"""
        with pytest.raises(ValueError, match="Unknown formula"):
            calculator.calculate(qt_interval=400, heart_rate=70, formula="unknown")

    def test_calculation_details(self, calculator: Any) -> None:
        """Verify calculation details are present"""
        result = calculator.calculate(qt_interval=450, heart_rate=70, sex="male", formula="bazett")
        assert "QT_measured" in result.calculation_details
        assert "Heart_rate" in result.calculation_details
        assert "RR_interval" in result.calculation_details
        assert "QTc" in result.calculation_details

    def test_metadata(self, calculator: Any) -> None:
        """Verify metadata is properly set"""
        assert calculator.tool_id == "corrected_qt"
        assert "QTc" in calculator.metadata.name
        assert len(calculator.metadata.references) >= 2


class TestAaGradientCalculator:
    """Tests for Alveolar-arterial Oxygen Gradient Calculator"""

    @pytest.fixture
    def calculator(self) -> Any:
        return AaGradientCalculator()

    # Basic formula tests
    def test_room_air_calculation(self, calculator: Any) -> None:
        """A-a gradient on room air (FiO2=0.21)"""
        # PAO2 = 0.21 * (760-47) - 40/0.8 = 149.73 - 50 = 99.73
        # A-a = 99.73 - 80 = 19.73
        result = calculator.calculate(pao2=80, paco2=40, fio2=0.21)
        expected_pao2 = 0.21 * (760 - 47) - (40 / 0.8)
        expected_aa = expected_pao2 - 80
        assert result.value is not None
        assert abs(result.value - round(expected_aa, 1)) < 0.5

    def test_100_percent_oxygen(self, calculator: Any) -> None:
        """A-a gradient on 100% O2"""
        # PAO2 = 1.0 * (760-47) - 40/0.8 = 713 - 50 = 663
        result = calculator.calculate(pao2=500, paco2=40, fio2=1.0)
        expected_pao2 = 1.0 * (760 - 47) - (40 / 0.8)
        expected_aa = expected_pao2 - 500
        assert result.value is not None
        assert abs(result.value - round(expected_aa, 1)) < 0.5

    def test_altitude_adjustment(self, calculator: Any) -> None:
        """A-a gradient at high altitude (lower Patm)"""
        # Denver ~650 mmHg
        result = calculator.calculate(
            pao2=60,
            paco2=35,
            fio2=0.21,
            atmospheric_pressure=650
        )
        # PAO2 will be lower
        expected_pao2 = 0.21 * (650 - 47) - (35 / 0.8)
        expected_aa = expected_pao2 - 60
        assert result.value is not None
        assert abs(result.value - round(expected_aa, 1)) < 0.5

    # Age-adjusted interpretation
    def test_age_adjusted_normal(self, calculator: Any) -> None:
        """Age-adjusted expected A-a gradient"""
        result = calculator.calculate(pao2=85, paco2=40, fio2=0.21, age=50)
        # Expected = 2.5 + 0.21*50 = 13
        assert "Expected_A-a_gradient" in result.calculation_details

    def test_young_adult_normal_gradient(self, calculator: Any) -> None:
        """Normal A-a gradient in young adult"""
        # Young adult, PaO2=95 gives A-a ≈ 5 (truly normal)
        # PAO2 = 0.21*713 - 50 = 99.73
        # PaO2 = 95 → A-a = 4.73
        result = calculator.calculate(pao2=95, paco2=40, fio2=0.21, age=25)
        # Expected for age 25: 2.5 + 0.21*25 = 7.75
        # A-a = 4.73 which is < 7.75 (normal)
        assert result.interpretation.severity is not None
        assert result.interpretation.severity == Severity.NORMAL
        assert result.interpretation.risk_level is not None
        assert result.interpretation.risk_level == RiskLevel.VERY_LOW

    def test_elevated_gradient(self, calculator: Any) -> None:
        """Elevated A-a gradient"""
        # PaO2=60 with normal PaCO2 → A-a ≈ 40 (markedly elevated)
        result = calculator.calculate(pao2=60, paco2=40, fio2=0.21, age=50)
        assert result.value is not None
        assert result.value > 30  # Significantly elevated
        assert result.interpretation.severity is not None
        assert result.interpretation.severity in (Severity.MODERATE, Severity.SEVERE)

    def test_mildly_elevated_gradient(self, calculator: Any) -> None:
        """Mildly elevated A-a gradient"""
        # For age 30: expected = 2.5 + 0.21*30 = 8.8
        # A-a ≈ 12-15 is mildly elevated for this age
        result = calculator.calculate(pao2=86, paco2=40, fio2=0.21, age=30)
        # A-a ≈ 13.7, which should be mildly elevated (above expected 8.8)
        assert result.interpretation.severity is not None
        assert result.interpretation.severity in (Severity.MILD, Severity.MODERATE)

    # Validation tests
    def test_invalid_pao2_too_low(self, calculator: Any) -> None:
        """PaO2 < 10 should raise error"""
        with pytest.raises(ValueError, match="outside expected range"):
            calculator.calculate(pao2=5, paco2=40, fio2=0.21)

    def test_invalid_paco2_too_high(self, calculator: Any) -> None:
        """PaCO2 > 150 should raise error"""
        with pytest.raises(ValueError, match="outside expected range"):
            calculator.calculate(pao2=80, paco2=160, fio2=0.21)

    def test_invalid_fio2_too_low(self, calculator: Any) -> None:
        """FiO2 < 0.21 should raise error"""
        with pytest.raises(ValueError, match="outside valid range"):
            calculator.calculate(pao2=80, paco2=40, fio2=0.15)

    def test_invalid_fio2_too_high(self, calculator: Any) -> None:
        """FiO2 > 1.0 should raise error"""
        with pytest.raises(ValueError, match="outside valid range"):
            calculator.calculate(pao2=80, paco2=40, fio2=1.5)

    def test_invalid_age(self, calculator: Any) -> None:
        """Age > 120 should raise error"""
        with pytest.raises(ValueError, match="outside valid range"):
            calculator.calculate(pao2=80, paco2=40, fio2=0.21, age=150)

    def test_metadata(self, calculator: Any) -> None:
        """Verify metadata is properly set"""
        assert calculator.tool_id == "aa_gradient"
        assert "A-a" in calculator.metadata.name or "alveolar" in calculator.metadata.name.lower()


class TestShockIndexCalculator:
    """Tests for Shock Index Calculator"""

    @pytest.fixture
    def calculator(self) -> Any:
        return ShockIndexCalculator()

    # Basic formula tests
    def test_basic_calculation(self, calculator: Any) -> None:
        """SI = HR / SBP"""
        result = calculator.calculate(heart_rate=100, systolic_bp=120)
        assert result.value is not None
        assert result.value == pytest.approx(100/120, abs=0.01)

    def test_normal_shock_index(self, calculator: Any) -> None:
        """Normal SI (0.5-0.7)"""
        result = calculator.calculate(heart_rate=70, systolic_bp=120)
        assert result.value is not None
        assert 0.5 <= result.value <= 0.7
        assert result.interpretation.severity is not None
        assert result.interpretation.severity == Severity.NORMAL

    def test_low_shock_index(self, calculator: Any) -> None:
        """Low SI (<0.5) - hemodynamically stable"""
        result = calculator.calculate(heart_rate=50, systolic_bp=140)
        assert result.value is not None
        assert result.value < 0.5
        assert result.interpretation.severity is not None
        assert result.interpretation.severity == Severity.NORMAL
        assert result.interpretation.risk_level is not None
        assert result.interpretation.risk_level == RiskLevel.VERY_LOW

    def test_borderline_shock_index(self, calculator: Any) -> None:
        """Borderline SI (0.7-1.0)"""
        result = calculator.calculate(heart_rate=90, systolic_bp=100)
        assert result.value is not None
        assert 0.7 < result.value <= 1.0
        assert result.interpretation.severity is not None
        assert result.interpretation.severity == Severity.MILD

    def test_elevated_shock_index(self, calculator: Any) -> None:
        """Elevated SI (>1.0) - hemodynamic instability"""
        result = calculator.calculate(heart_rate=110, systolic_bp=90)
        assert result.value is not None
        assert result.value > 1.0
        assert result.interpretation.severity is not None
        assert result.interpretation.severity in (Severity.MODERATE, Severity.SEVERE)

    def test_severely_elevated_shock_index(self, calculator: Any) -> None:
        """Severely elevated SI (≥1.4) - high mortality"""
        result = calculator.calculate(heart_rate=140, systolic_bp=80)
        assert result.value is not None
        assert result.value >= 1.4
        assert result.interpretation.severity is not None
        assert result.interpretation.severity == Severity.SEVERE
        assert result.interpretation.risk_level is not None
        assert result.interpretation.risk_level == RiskLevel.HIGH
        assert result.interpretation.warnings is not None
        assert any("CRITICAL" in w or "massive transfusion" in w for w in result.interpretation.warnings)

    # Modified Shock Index
    def test_modified_shock_index(self, calculator: Any) -> None:
        """MSI = HR / MAP when diastolic provided"""
        result = calculator.calculate(
            heart_rate=100,
            systolic_bp=120,
            diastolic_bp=80
        )
        # MAP = (120 + 2*80) / 3 = 93.33
        # MSI = 100 / 93.33 ≈ 1.07
        assert "Modified_Shock_Index" in result.calculation_details
        assert "MAP" in result.calculation_details

    # Patient type adjustments
    def test_obstetric_patient(self, calculator: Any) -> None:
        """Obstetric patients have different thresholds"""
        result = calculator.calculate(
            heart_rate=90,
            systolic_bp=100,
            patient_type="obstetric"
        )
        # SI=0.9 which is borderline for obstetric
        assert result.interpretation.severity is not None
        assert result.interpretation.severity in (Severity.NORMAL, Severity.MILD)

    def test_pediatric_patient(self, calculator: Any) -> None:
        """Pediatric patients have higher baseline HR"""
        result = calculator.calculate(
            heart_rate=110,
            systolic_bp=100,
            patient_type="pediatric"
        )
        # SI=1.1 - different interpretation for children
        assert result.calculation_details is not None
        assert "Pediatric" in result.calculation_details["Patient_type"]

    # Validation tests
    def test_invalid_hr_too_low(self, calculator: Any) -> None:
        """HR < 20 should raise error"""
        with pytest.raises(ValueError, match="outside expected range"):
            calculator.calculate(heart_rate=15, systolic_bp=120)

    def test_invalid_hr_too_high(self, calculator: Any) -> None:
        """HR > 300 should raise error"""
        with pytest.raises(ValueError, match="outside expected range"):
            calculator.calculate(heart_rate=350, systolic_bp=120)

    def test_invalid_sbp_too_low(self, calculator: Any) -> None:
        """SBP < 30 should raise error"""
        with pytest.raises(ValueError, match="outside expected range"):
            calculator.calculate(heart_rate=100, systolic_bp=20)

    def test_invalid_dbp_out_of_range(self, calculator: Any) -> None:
        """DBP out of range should raise error"""
        with pytest.raises(ValueError, match="outside expected range"):
            calculator.calculate(heart_rate=100, systolic_bp=120, diastolic_bp=250)

    def test_metadata(self, calculator: Any) -> None:
        """Verify metadata is properly set"""
        assert calculator.tool_id == "shock_index"
        assert "Shock" in calculator.metadata.name
        assert len(calculator.metadata.references) >= 2

    def test_calculation_details(self, calculator: Any) -> None:
        """Verify calculation details are present"""
        result = calculator.calculate(heart_rate=100, systolic_bp=120)
        assert "Heart_rate" in result.calculation_details
        assert "Systolic_BP" in result.calculation_details
        assert "Shock_Index" in result.calculation_details


class TestClinicalScenarios:
    """Integration tests with realistic clinical scenarios"""

    def test_qtc_drug_monitoring(self) -> None:
        """Scenario: Monitoring patient on sotalol"""
        calc = CorrectedQtCalculator()

        # Baseline: normal
        baseline = calc.calculate(qt_interval=380, heart_rate=65, sex="male")
        assert baseline.interpretation.severity is not None
        assert baseline.interpretation.severity == Severity.NORMAL

        # After drug: prolonged
        on_drug = calc.calculate(qt_interval=520, heart_rate=60, sex="male")
        assert on_drug.interpretation.severity is not None
        assert on_drug.interpretation.severity == Severity.SEVERE
        assert on_drug.value is not None
        assert on_drug.value > 500

    def test_aa_gradient_copd_exacerbation(self) -> None:
        """Scenario: COPD patient with hypoxemia"""
        calc = AaGradientCalculator()

        # CO2 retention with V/Q mismatch
        # With higher CO2, PAO2 is lower: PAO2 = 0.21*(760-47) - 60/0.8 = 99.73 - 75 = 24.73
        # No wait, let's calculate: PAO2 = 0.21*713 - 75 = 149.73 - 75 = 74.73
        # A-a = 74.73 - 55 = 19.73 ≈ 20
        result = calc.calculate(
            pao2=50,  # Lower PaO2 for more severe hypoxemia
            paco2=60,  # Hypercapnia
            fio2=0.21,
            age=70
        )
        # Elevated A-a indicates V/Q mismatch
        assert result.value is not None
        assert result.value > 15  # Should be elevated

    def test_shock_index_trauma(self) -> None:
        """Scenario: Trauma patient with occult hemorrhage"""
        calc = ShockIndexCalculator()

        # Initial vital signs look "OK" but SI elevated
        result = calc.calculate(heart_rate=115, systolic_bp=95)
        assert result.value is not None
        assert result.value > 1.0
        assert "transfusion" in str(result.interpretation.recommendations).lower()

    def test_shock_index_postpartum(self) -> None:
        """Scenario: Postpartum hemorrhage"""
        calc = ShockIndexCalculator()

        result = calc.calculate(
            heart_rate=120,
            systolic_bp=85,
            patient_type="obstetric"
        )
        assert result.value is not None
        assert result.value > 1.3
        assert result.interpretation.severity is not None
        assert result.interpretation.severity == Severity.SEVERE
