from typing import Any
"""
Comprehensive tests for Phase 9b Acid-Base Calculators:
- Winter's Formula
- Osmolar Gap
- Free Water Deficit
"""
import pytest

from src.domain.services.calculators import (
    FreeWaterDeficitCalculator,
    OsmolarGapCalculator,
    WintersFormulaCalculator,
)
from src.domain.value_objects.interpretation import RiskLevel, Severity
from src.domain.value_objects.units import Unit

# ============================================================
# Winter's Formula Calculator Tests
# ============================================================

class TestWintersFormulaCalculator:
    """Tests for Winter's Formula Calculator"""

    @pytest.fixture
    def calculator(self) -> Any:
        return WintersFormulaCalculator()

    # --- Basic Calculation Tests ---

    def test_winters_formula_hco3_10(self, calculator: Any) -> None:
        """Test expected PaCO2 for HCO3 = 10 mEq/L"""
        result = calculator.calculate(hco3=10)
        # Expected = 1.5 * 10 + 8 = 23 mmHg
        assert result.value is not None
        assert result.value == 23.0
        assert result.unit is not None
        assert result.unit == Unit.MMHG

    def test_winters_formula_hco3_15(self, calculator: Any) -> None:
        """Test expected PaCO2 for HCO3 = 15 mEq/L"""
        result = calculator.calculate(hco3=15)
        # Expected = 1.5 * 15 + 8 = 30.5 mmHg
        assert result.value is not None
        assert result.value == 30.5

    def test_winters_formula_hco3_20(self, calculator: Any) -> None:
        """Test expected PaCO2 for HCO3 = 20 mEq/L"""
        result = calculator.calculate(hco3=20)
        # Expected = 1.5 * 20 + 8 = 38 mmHg
        assert result.value is not None
        assert result.value == 38.0

    def test_winters_formula_hco3_8(self, calculator: Any) -> None:
        """Test expected PaCO2 for severe acidosis HCO3 = 8 mEq/L"""
        result = calculator.calculate(hco3=8)
        # Expected = 1.5 * 8 + 8 = 20 mmHg
        assert result.value is not None
        assert result.value == 20.0

    # --- Compensation Assessment Tests ---

    def test_appropriate_compensation(self, calculator: Any) -> None:
        """Test appropriate respiratory compensation (within ±2)"""
        result = calculator.calculate(hco3=10, actual_paco2=23)
        # Expected 23 ±2, actual 23 is within range
        assert result.interpretation.severity is not None
        assert result.interpretation.severity == Severity.NORMAL
        assert result.interpretation.summary is not None
        assert "appropriate" in result.interpretation.summary.lower()

    def test_respiratory_acidosis(self, calculator: Any) -> None:
        """Test concurrent respiratory acidosis (PaCO2 too high)"""
        result = calculator.calculate(hco3=10, actual_paco2=35)
        # Expected 21-25, actual 35 is above range
        assert result.interpretation.severity is not None
        assert result.interpretation.severity == Severity.MODERATE
        assert result.interpretation.summary is not None
        assert "RESPIRATORY ACIDOSIS" in result.interpretation.summary.upper()

    def test_respiratory_alkalosis(self, calculator: Any) -> None:
        """Test concurrent respiratory alkalosis (PaCO2 too low)"""
        result = calculator.calculate(hco3=10, actual_paco2=15)
        # Expected 21-25, actual 15 is below range
        assert result.interpretation.severity is not None
        assert result.interpretation.severity == Severity.MILD
        assert result.interpretation.summary is not None
        assert "RESPIRATORY ALKALOSIS" in result.interpretation.summary.upper()

    def test_edge_of_range_upper(self, calculator: Any) -> None:
        """Test at upper edge of expected range"""
        result = calculator.calculate(hco3=10, actual_paco2=25)
        # Expected 23 ±2 = 21-25, actual 25 is at upper edge
        assert result.interpretation.severity is not None
        assert result.interpretation.severity == Severity.NORMAL

    def test_edge_of_range_lower(self, calculator: Any) -> None:
        """Test at lower edge of expected range"""
        result = calculator.calculate(hco3=10, actual_paco2=21)
        # Expected 23 ±2 = 21-25, actual 21 is at lower edge
        assert result.interpretation.severity is not None
        assert result.interpretation.severity == Severity.NORMAL

    # --- Warning Tests ---

    def test_low_hco3_warning(self, calculator: Any) -> None:
        """Test warning for very low HCO3 <6 mEq/L"""
        result = calculator.calculate(hco3=5)
        assert result.interpretation.warnings is not None
        assert any("less reliable" in w.lower() for w in result.interpretation.warnings)

    # --- Metadata Tests ---

    def test_metadata(self, calculator: Any) -> None:
        """Test calculator metadata"""
        assert calculator.tool_id == "winters_formula"
        assert "Winter" in calculator.metadata.name
        assert len(calculator.metadata.references) >= 1

    def test_references(self, calculator: Any) -> None:
        """Test that references are valid"""
        refs = calculator.metadata.references
        assert any("1967" in str(r.year) or "1980" in str(r.year) for r in refs)

    # --- Validation Tests ---

    def test_invalid_hco3_low(self, calculator: Any) -> None:
        """Test validation for HCO3 too low"""
        with pytest.raises(ValueError):
            calculator.calculate(hco3=0)

    def test_invalid_hco3_high(self, calculator: Any) -> None:
        """Test validation for HCO3 too high"""
        with pytest.raises(ValueError):
            calculator.calculate(hco3=50)

    def test_invalid_paco2(self, calculator: Any) -> None:
        """Test validation for invalid PaCO2"""
        with pytest.raises(ValueError):
            calculator.calculate(hco3=10, actual_paco2=5)


# ============================================================
# Osmolar Gap Calculator Tests
# ============================================================

class TestOsmolarGapCalculator:
    """Tests for Osmolar Gap Calculator"""

    @pytest.fixture
    def calculator(self) -> Any:
        return OsmolarGapCalculator()

    # --- Basic Calculation Tests ---

    def test_normal_osmolar_gap(self, calculator: Any) -> None:
        """Test normal osmolar gap"""
        # Calculated = 2*140 + 100/18 + 14/2.8 = 280 + 5.56 + 5 = 290.56
        result = calculator.calculate(
            measured_osm=295,
            sodium=140,
            glucose=100,
            bun=14
        )
        gap = result.value
        assert -10 <= gap <= 10
        assert result.interpretation.severity is not None
        assert result.interpretation.severity == Severity.NORMAL

    def test_elevated_osmolar_gap(self, calculator: Any) -> None:
        """Test elevated osmolar gap (10-20)"""
        # Create gap > 10
        result = calculator.calculate(
            measured_osm=315,
            sodium=140,
            glucose=100,
            bun=14
        )
        gap = result.value
        assert 10 < gap <= 25
        assert result.interpretation.summary is not None
        assert "elevated" in result.interpretation.summary.lower()

    def test_significantly_elevated_gap(self, calculator: Any) -> None:
        """Test significantly elevated osmolar gap (>20)"""
        result = calculator.calculate(
            measured_osm=340,
            sodium=140,
            glucose=100,
            bun=14
        )
        gap = result.value
        assert gap > 20
        assert result.interpretation.severity is not None
        assert result.interpretation.severity in [Severity.MODERATE, Severity.SEVERE]

    def test_with_ethanol(self, calculator: Any) -> None:
        """Test osmolar gap calculation including ethanol"""
        # Ethanol contribution = ethanol / 4.6
        result = calculator.calculate(
            measured_osm=340,
            sodium=140,
            glucose=100,
            bun=14,
            ethanol=100  # 100 mg/dL ethanol = ~21.7 mOsm contribution
        )
        assert "ethanol" in str(result.calculation_details).lower()

    def test_high_glucose(self, calculator: Any) -> None:
        """Test with high glucose (DKA scenario)"""
        result = calculator.calculate(
            measured_osm=330,
            sodium=135,
            glucose=400,
            bun=30
        )
        assert "glucose" in str(result.calculation_details).lower()

    # --- Clinical Scenario Tests ---

    def test_methanol_poisoning_scenario(self, calculator: Any) -> None:
        """Test scenario suggestive of methanol poisoning"""
        # High osmolar gap without ethanol
        result = calculator.calculate(
            measured_osm=340,
            sodium=140,
            glucose=100,
            bun=14
        )
        assert any("methanol" in r.lower() or "toxic" in r.lower()
                   for r in result.interpretation.recommendations)

    def test_ethylene_glycol_scenario(self, calculator: Any) -> None:
        """Test scenario suggestive of ethylene glycol poisoning"""
        result = calculator.calculate(
            measured_osm=350,
            sodium=138,
            glucose=120,
            bun=20
        )
        assert result.value is not None
        assert result.value > 20
        assert result.interpretation.risk_level is not None
        assert result.interpretation.risk_level in [RiskLevel.INTERMEDIATE, RiskLevel.HIGH]

    # --- Metadata Tests ---

    def test_metadata(self, calculator: Any) -> None:
        """Test calculator metadata"""
        assert calculator.tool_id == "osmolar_gap"
        assert "Osmolar" in calculator.metadata.name

    def test_specialties(self, calculator: Any) -> None:
        """Test that appropriate specialties are listed"""
        from src.domain.value_objects.tool_keys import Specialty
        specs = calculator.metadata.high_level.specialties
        assert Specialty.EMERGENCY_MEDICINE in specs
        assert Specialty.TOXICOLOGY in specs or Specialty.CRITICAL_CARE in specs

    # --- Validation Tests ---

    def test_invalid_sodium(self, calculator: Any) -> None:
        """Test validation for invalid sodium"""
        with pytest.raises(ValueError):
            calculator.calculate(measured_osm=300, sodium=50, glucose=100, bun=14)

    def test_invalid_glucose(self, calculator: Any) -> None:
        """Test validation for invalid glucose"""
        with pytest.raises(ValueError):
            calculator.calculate(measured_osm=300, sodium=140, glucose=5, bun=14)


# ============================================================
# Free Water Deficit Calculator Tests
# ============================================================

class TestFreeWaterDeficitCalculator:
    """Tests for Free Water Deficit Calculator"""

    @pytest.fixture
    def calculator(self) -> Any:
        return FreeWaterDeficitCalculator()

    # --- Basic Calculation Tests ---

    def test_mild_hypernatremia(self, calculator: Any) -> None:
        """Test free water deficit for mild hypernatremia (Na 150)"""
        result = calculator.calculate(
            current_sodium=150,
            weight_kg=70,
            target_sodium=140
        )
        # TBW = 70 * 0.6 = 42 L
        # FWD = 42 * ((150/140) - 1) = 42 * 0.0714 = 3.0 L
        assert result.value is not None
        assert abs(result.value - 3.0) < 0.5
        assert result.unit is not None
        assert result.unit == Unit.L

    def test_moderate_hypernatremia(self, calculator: Any) -> None:
        """Test free water deficit for moderate hypernatremia (Na 160)"""
        result = calculator.calculate(
            current_sodium=160,
            weight_kg=70,
            target_sodium=140
        )
        # TBW = 70 * 0.6 = 42 L
        # FWD = 42 * ((160/140) - 1) = 42 * 0.143 = 6.0 L
        assert result.value is not None
        assert abs(result.value - 6.0) < 0.5

    def test_severe_hypernatremia(self, calculator: Any) -> None:
        """Test free water deficit for severe hypernatremia (Na 170)"""
        result = calculator.calculate(
            current_sodium=170,
            weight_kg=70,
            target_sodium=140
        )
        # TBW = 70 * 0.6 = 42 L
        # FWD = 42 * ((170/140) - 1) = 42 * 0.214 = 9.0 L
        assert result.value is not None
        assert abs(result.value - 9.0) < 0.5
        assert result.interpretation.severity is not None
        assert result.interpretation.severity == Severity.SEVERE

    # --- Patient Type Tests ---

    def test_adult_female(self, calculator: Any) -> None:
        """Test with adult female (50% TBW)"""
        result = calculator.calculate(
            current_sodium=160,
            weight_kg=70,
            target_sodium=140,
            patient_type="adult_female"
        )
        # TBW = 70 * 0.5 = 35 L
        # FWD = 35 * 0.143 = 5.0 L
        assert result.value is not None
        assert abs(result.value - 5.0) < 0.5

    def test_elderly_female(self, calculator: Any) -> None:
        """Test with elderly female (45% TBW)"""
        result = calculator.calculate(
            current_sodium=160,
            weight_kg=70,
            target_sodium=140,
            patient_type="elderly_female"
        )
        # TBW = 70 * 0.45 = 31.5 L
        # FWD = 31.5 * 0.143 = 4.5 L
        assert result.value is not None
        assert abs(result.value - 4.5) < 0.5

    def test_child(self, calculator: Any) -> None:
        """Test with child (60% TBW)"""
        result = calculator.calculate(
            current_sodium=150,
            weight_kg=20,
            target_sodium=140,
            patient_type="child"
        )
        # TBW = 20 * 0.6 = 12 L
        # FWD = 12 * 0.0714 = 0.86 L
        assert result.value is not None
        assert abs(result.value - 0.9) < 0.2

    # --- Correction Rate Tests ---

    def test_safe_correction_rate(self, calculator: Any) -> None:
        """Test safe correction rate (≤12 mEq/L per 24h)"""
        result = calculator.calculate(
            current_sodium=150,
            weight_kg=70,
            target_sodium=140,
            correction_time_hours=24
        )
        # 10 mEq/L change over 24h = 10 mEq/L per 24h (safe)
        # Check that the interpretation mentions "within safe limits"
        assert result.interpretation.detail is not None
        assert "safe limits" in result.interpretation.detail.lower() or \
               len(result.interpretation.warnings) == 0

    def test_rapid_correction_warning(self, calculator: Any) -> None:
        """Test warning for too rapid correction"""
        result = calculator.calculate(
            current_sodium=170,
            weight_kg=70,
            target_sodium=140,
            correction_time_hours=12
        )
        # 30 mEq/L over 12h = 60 mEq/L per 24h (too fast)
        assert any("rapid" in w.lower() or "slow" in w.lower()
                   for w in result.interpretation.warnings)

    # --- Infusion Rate Tests ---

    def test_infusion_rate_calculation(self, calculator: Any) -> None:
        """Test that infusion rate is calculated"""
        result = calculator.calculate(
            current_sodium=160,
            weight_kg=70,
            target_sodium=140,
            correction_time_hours=24
        )
        details = result.calculation_details
        assert "Infusion_rate" in str(details)

    # --- Metadata Tests ---

    def test_metadata(self, calculator: Any) -> None:
        """Test calculator metadata"""
        assert calculator.tool_id == "free_water_deficit"
        assert "Free Water" in calculator.metadata.name

    def test_references(self, calculator: Any) -> None:
        """Test that references include Adrogue or Sterns"""
        refs = calculator.metadata.references
        ref_text = " ".join([r.citation for r in refs])
        assert "Adrogue" in ref_text or "Sterns" in ref_text

    # --- Validation Tests ---

    def test_normal_sodium_rejected(self, calculator: Any) -> None:
        """Test that normal sodium is rejected (not hypernatremia)"""
        with pytest.raises(ValueError):
            calculator.calculate(current_sodium=140, weight_kg=70)

    def test_low_sodium_rejected(self, calculator: Any) -> None:
        """Test that low sodium is rejected"""
        with pytest.raises(ValueError):
            calculator.calculate(current_sodium=130, weight_kg=70)

    def test_invalid_target(self, calculator: Any) -> None:
        """Test that target below normal is rejected"""
        with pytest.raises(ValueError):
            calculator.calculate(current_sodium=160, weight_kg=70, target_sodium=130)

    def test_current_less_than_target(self, calculator: Any) -> None:
        """Test that current < target is rejected"""
        with pytest.raises(ValueError):
            calculator.calculate(current_sodium=150, weight_kg=70, target_sodium=155)


# ============================================================
# Integration Tests
# ============================================================

class TestPhase9bIntegration:
    """Integration tests for Phase 9b calculators"""

    def test_all_calculators_have_metadata(self) -> None:
        """Test that all Phase 9b calculators have proper metadata"""
        calculators = [
            WintersFormulaCalculator(),
            OsmolarGapCalculator(),
            FreeWaterDeficitCalculator(),
        ]

        for calc in calculators:
            assert calc.tool_id is not None
            assert calc.metadata.name is not None
            assert len(calc.metadata.references) >= 1

    def test_all_calculators_return_score_result(self) -> None:
        """Test that all calculators return ScoreResult"""
        from src.domain.entities.score_result import ScoreResult

        winters = WintersFormulaCalculator()
        osmolar = OsmolarGapCalculator()
        fwd = FreeWaterDeficitCalculator()

        assert isinstance(winters.calculate(hco3=10), ScoreResult)
        assert isinstance(osmolar.calculate(measured_osm=300, sodium=140, glucose=100, bun=14), ScoreResult)
        assert isinstance(fwd.calculate(current_sodium=160, weight_kg=70), ScoreResult)

    def test_clinical_workflow_metabolic_acidosis(self) -> None:
        """Test clinical workflow for metabolic acidosis evaluation"""
        # Scenario: Patient with DKA (low HCO3, high AG, need to check compensation)

        # Step 1: Calculate expected PaCO2
        winters = WintersFormulaCalculator()
        result = winters.calculate(hco3=12, actual_paco2=28)
        # Expected = 1.5*12 + 8 = 26 ±2 = 24-28
        # Actual 28 is within range = appropriate compensation
        assert result.interpretation.severity is not None
        assert result.interpretation.severity == Severity.NORMAL

    def test_clinical_workflow_toxic_ingestion(self) -> None:
        """Test clinical workflow for toxic alcohol screening"""
        osmolar = OsmolarGapCalculator()
        result = osmolar.calculate(
            measured_osm=340,
            sodium=140,
            glucose=100,
            bun=14
        )
        # High osmolar gap = screen positive for toxic alcohols
        assert result.value is not None
        assert result.value > 20

    def test_clinical_workflow_hypernatremia(self) -> None:
        """Test clinical workflow for hypernatremia treatment"""
        fwd = FreeWaterDeficitCalculator()
        result = fwd.calculate(
            current_sodium=160,
            weight_kg=70,
            target_sodium=145,
            correction_time_hours=48
        )
        # Safe, gradual correction over 48 hours
        assert result.value is not None
        assert result.value > 0
        # Check correction rate is safe
        assert result.calculation_details is not None
        details = result.calculation_details
        assert details is not None
        rate = float(details["Correction_rate"].split()[0])
        assert rate <= 12  # ≤12 mEq/L per 24h
