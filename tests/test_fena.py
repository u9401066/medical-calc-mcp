"""
Tests for Fractional Excretion of Sodium (FENa) Calculator

Testing:
- FENa calculation accuracy
- Prerenal vs ATN differentiation
- Diuretic effect warning
- Edge cases and validation

Reference:
    Espinel CH. JAMA. 1976;236(6):579-581. PMID: 947239
    Miller TR, et al. Ann Intern Med. 1978;89(1):47-50. PMID: 666184
"""

from typing import Any

import pytest

from src.domain.services.calculators.fena import FENaCalculator


class TestFENaCalculator:
    """Test Fractional Excretion of Sodium Calculator"""

    @pytest.fixture
    def calculator(self) -> Any:
        return FENaCalculator()

    # === Metadata Tests ===

    def test_metadata(self, calculator: Any) -> None:
        """Test calculator metadata"""
        assert calculator.tool_id == "fena"
        assert "FENa" in calculator.name or "Fractional Excretion" in calculator.name
        assert len(calculator.references) >= 2  # Espinel + Miller

    def test_references_have_pmids(self, calculator: Any) -> None:
        """Test that references include proper PMIDs"""
        pmids = [ref.pmid for ref in calculator.references if ref.pmid]
        assert "947239" in pmids  # Espinel 1976
        assert "666184" in pmids  # Miller 1978

    # === Basic Calculation Tests ===

    def test_fena_formula_simple(self, calculator: Any) -> None:
        """Test FENa formula with simple values"""
        # FENa = (UNa × PCr) / (PNa × UCr) × 100
        # FENa = (10 × 1.0) / (140 × 100) × 100 = 0.071%
        result = calculator.calculate(
            urine_sodium=10,
            plasma_sodium=140,
            urine_creatinine=100,
            plasma_creatinine=1.0,
            on_diuretics=False,
        )
        expected = (10 * 1.0) / (140 * 100) * 100
        assert abs(result.value - expected) < 0.01

    def test_fena_formula_prerenal_classic(self, calculator: Any) -> None:
        """Test classic prerenal values"""
        # Classic prerenal: low urine Na, concentrated urine
        result = calculator.calculate(
            urine_sodium=8,  # Low - kidney conserving sodium
            plasma_sodium=140,
            urine_creatinine=150,  # Concentrated urine
            plasma_creatinine=2.5,  # Elevated
            on_diuretics=False,
        )
        # FENa = (8 × 2.5) / (140 × 150) × 100 = 0.095%
        assert result.value < 1  # Should be prerenal
        assert "prerenal" in result.interpretation.summary.lower()

    def test_fena_formula_atn_classic(self, calculator: Any) -> None:
        """Test classic ATN values"""
        # Classic ATN: high urine Na, dilute urine
        result = calculator.calculate(
            urine_sodium=60,  # High - kidney cannot conserve sodium
            plasma_sodium=140,
            urine_creatinine=30,  # Dilute urine (impaired concentration)
            plasma_creatinine=3.0,  # Elevated
            on_diuretics=False,
        )
        # FENa = (60 × 3.0) / (140 × 30) × 100 = 4.29%
        assert result.value > 2  # Should be ATN
        assert "intrinsic" in result.interpretation.summary.lower() or "ATN" in result.interpretation.summary

    # === Clinical Interpretation Tests ===

    def test_prerenal_interpretation_under_1_percent(self, calculator: Any) -> None:
        """Test FENa < 1% interpretation (prerenal)"""
        result = calculator.calculate(
            urine_sodium=5,
            plasma_sodium=140,
            urine_creatinine=200,
            plasma_creatinine=1.5,
            on_diuretics=False,
        )
        # FENa = (5 × 1.5) / (140 × 200) × 100 = 0.027%
        assert result.value < 1
        assert "prerenal" in result.interpretation.stage.lower()
        assert result.interpretation.severity.value == "moderate"

    def test_indeterminate_interpretation_1_to_2_percent(self, calculator: Any) -> None:
        """Test FENa 1-2% interpretation (indeterminate)"""
        result = calculator.calculate(
            urine_sodium=40,
            plasma_sodium=140,
            urine_creatinine=100,
            plasma_creatinine=5.0,  # High Cr to get FENa ~1.4%
            on_diuretics=False,
        )
        # FENa = (40 × 5.0) / (140 × 100) × 100 = 1.43%
        assert 1 <= result.value <= 2
        assert "indeterminate" in result.interpretation.stage.lower()

    def test_intrinsic_interpretation_over_2_percent(self, calculator: Any) -> None:
        """Test FENa > 2% interpretation (intrinsic renal)"""
        result = calculator.calculate(
            urine_sodium=80,
            plasma_sodium=140,
            urine_creatinine=50,
            plasma_creatinine=4.0,
            on_diuretics=False,
        )
        # FENa = (80 × 4.0) / (140 × 50) × 100 = 4.57%
        assert result.value > 2
        assert "intrinsic" in result.interpretation.stage.lower()
        assert result.interpretation.severity.value == "severe"

    # === Diuretic Effect Tests ===

    def test_diuretic_warning(self, calculator: Any) -> None:
        """Test that diuretic use triggers unreliable warning"""
        result = calculator.calculate(
            urine_sodium=60,
            plasma_sodium=140,
            urine_creatinine=80,
            plasma_creatinine=2.0,
            on_diuretics=True,
        )
        assert "unreliable" in result.interpretation.summary.lower()
        assert "diuretic" in result.interpretation.summary.lower()
        assert len(result.interpretation.warnings) > 0

    def test_diuretic_recommends_feurea(self, calculator: Any) -> None:
        """Test that FEUrea is recommended when on diuretics"""
        result = calculator.calculate(
            urine_sodium=60,
            plasma_sodium=140,
            urine_creatinine=80,
            plasma_creatinine=2.0,
            on_diuretics=True,
        )
        recommendations = " ".join(result.interpretation.recommendations)
        assert "FEUrea" in recommendations or "urea" in recommendations.lower()

    # === Input Validation Tests ===

    def test_invalid_urine_sodium_high(self, calculator: Any) -> None:
        """Test validation for urine sodium > 300"""
        with pytest.raises(ValueError, match="[Uu]rine sodium"):
            calculator.calculate(
                urine_sodium=350,  # Invalid
                plasma_sodium=140,
                urine_creatinine=100,
                plasma_creatinine=1.0,
            )

    def test_invalid_plasma_sodium_low(self, calculator: Any) -> None:
        """Test validation for plasma sodium < 100"""
        with pytest.raises(ValueError, match="[Pp]lasma sodium"):
            calculator.calculate(
                urine_sodium=50,
                plasma_sodium=90,  # Invalid
                urine_creatinine=100,
                plasma_creatinine=1.0,
            )

    def test_invalid_plasma_sodium_high(self, calculator: Any) -> None:
        """Test validation for plasma sodium > 180"""
        with pytest.raises(ValueError, match="[Pp]lasma sodium"):
            calculator.calculate(
                urine_sodium=50,
                plasma_sodium=190,  # Invalid
                urine_creatinine=100,
                plasma_creatinine=1.0,
            )

    def test_invalid_urine_creatinine_zero(self, calculator: Any) -> None:
        """Test validation for urine creatinine = 0"""
        with pytest.raises(ValueError, match="[Uu]rine creatinine"):
            calculator.calculate(
                urine_sodium=50,
                plasma_sodium=140,
                urine_creatinine=0,  # Invalid
                plasma_creatinine=1.0,
            )

    def test_invalid_plasma_creatinine_zero(self, calculator: Any) -> None:
        """Test validation for plasma creatinine = 0"""
        with pytest.raises(ValueError, match="[Pp]lasma creatinine"):
            calculator.calculate(
                urine_sodium=50,
                plasma_sodium=140,
                urine_creatinine=100,
                plasma_creatinine=0,  # Invalid
            )

    # === Edge Cases ===

    def test_very_low_urine_sodium(self, calculator: Any) -> None:
        """Test very low urine sodium (severely prerenal)"""
        result = calculator.calculate(
            urine_sodium=1,  # Very low
            plasma_sodium=140,
            urine_creatinine=200,
            plasma_creatinine=2.0,
            on_diuretics=False,
        )
        # FENa = (1 × 2.0) / (140 × 200) × 100 = 0.007%
        assert result.value < 0.1
        assert "prerenal" in result.interpretation.summary.lower()

    def test_high_plasma_creatinine(self, calculator: Any) -> None:
        """Test with very high plasma creatinine (severe AKI)"""
        result = calculator.calculate(
            urine_sodium=40,
            plasma_sodium=140,
            urine_creatinine=50,
            plasma_creatinine=10.0,  # Very high
            on_diuretics=False,
        )
        # FENa = (40 × 10.0) / (140 × 50) × 100 = 5.71%
        assert result.value > 2
        assert "intrinsic" in result.interpretation.stage.lower()

    def test_calculation_details_present(self, calculator: Any) -> None:
        """Test that calculation details are provided"""
        result = calculator.calculate(
            urine_sodium=50,
            plasma_sodium=140,
            urine_creatinine=100,
            plasma_creatinine=2.0,
            on_diuretics=False,
        )
        assert "formula" in result.calculation_details
        assert "numerator" in result.calculation_details
        assert "denominator" in result.calculation_details
        assert "fena_percentage" in result.calculation_details

    def test_raw_inputs_stored(self, calculator: Any) -> None:
        """Test that raw inputs are stored"""
        result = calculator.calculate(
            urine_sodium=50,
            plasma_sodium=140,
            urine_creatinine=100,
            plasma_creatinine=2.0,
            on_diuretics=False,
        )
        assert result.raw_inputs["urine_sodium"] == 50
        assert result.raw_inputs["plasma_sodium"] == 140
        assert result.raw_inputs["urine_creatinine"] == 100
        assert result.raw_inputs["plasma_creatinine"] == 2.0
        assert result.raw_inputs["on_diuretics"] is False

    # === Clinical Scenario Tests ===

    def test_scenario_dehydration(self, calculator: Any) -> None:
        """Test typical dehydration scenario"""
        # Elderly patient with vomiting/diarrhea
        result = calculator.calculate(
            urine_sodium=8,  # Low - appropriate sodium retention
            plasma_sodium=142,
            urine_creatinine=180,  # Concentrated urine
            plasma_creatinine=1.8,  # Mildly elevated
            on_diuretics=False,
        )
        # FENa = (8 × 1.8) / (142 × 180) × 100 = 0.056%
        assert result.value < 1
        assert "prerenal" in result.interpretation.stage.lower()
        # Should recommend volume resuscitation
        recs = " ".join(result.interpretation.recommendations)
        assert "volume" in recs.lower() or "fluid" in recs.lower()

    def test_scenario_atn_post_surgery(self, calculator: Any) -> None:
        """Test post-surgical ATN scenario"""
        # Patient after major surgery with hypotension episode
        result = calculator.calculate(
            urine_sodium=70,  # High - tubular damage
            plasma_sodium=138,
            urine_creatinine=35,  # Low - cannot concentrate
            plasma_creatinine=4.5,  # Elevated
            on_diuretics=False,
        )
        # FENa = (70 × 4.5) / (138 × 35) × 100 = 6.52%
        assert result.value > 2
        assert "intrinsic" in result.interpretation.stage.lower()
        # Should mention nephrology consultation
        recs = " ".join(result.interpretation.recommendations)
        assert "nephrology" in recs.lower()

    def test_scenario_heart_failure_on_diuretics(self, calculator: Any) -> None:
        """Test heart failure patient on diuretics"""
        result = calculator.calculate(
            urine_sodium=45,  # Elevated due to diuretics
            plasma_sodium=134,
            urine_creatinine=60,
            plasma_creatinine=2.2,
            on_diuretics=True,
        )
        # Should warn about unreliable result
        assert "unreliable" in result.interpretation.summary.lower()
        assert "diuretic" in result.interpretation.detail.lower()

    # === Unit Tests ===

    def test_unit_is_percent(self, calculator: Any) -> None:
        """Test that result unit is percentage"""
        result = calculator.calculate(
            urine_sodium=50,
            plasma_sodium=140,
            urine_creatinine=100,
            plasma_creatinine=2.0,
            on_diuretics=False,
        )
        assert result.unit.value == "%"

    def test_value_rounded_to_two_decimals(self, calculator: Any) -> None:
        """Test that FENa is rounded to 2 decimal places"""
        result = calculator.calculate(
            urine_sodium=47,
            plasma_sodium=141,
            urine_creatinine=93,
            plasma_creatinine=1.7,
            on_diuretics=False,
        )
        # Check that value has at most 2 decimal places
        assert result.value == round(result.value, 2)
