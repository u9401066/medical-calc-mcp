"""
Tests for Serum Osmolality Calculator

Testing:
- Osmolality calculation accuracy
- Osmolar gap calculation
- Clinical interpretation
- Edge cases

Reference:
    Edelman IS, et al. J Clin Invest. 1958;37(9):1236-1256. PMID: 13575523
    Khajuria A, Krahn J. Clin Biochem. 2005;38(6):514-519. PMID: 15885229
"""

from typing import Any

import pytest

from src.domain.services.calculators.serum_osmolality import SerumOsmolalityCalculator


class TestSerumOsmolalityCalculator:
    """Test Serum Osmolality Calculator"""

    @pytest.fixture
    def calculator(self) -> Any:
        return SerumOsmolalityCalculator()

    # === Metadata Tests ===

    def test_metadata(self, calculator: Any) -> None:
        """Test calculator metadata"""
        assert calculator.tool_id == "serum_osmolality"
        assert "osmolality" in calculator.name.lower()
        assert len(calculator.references) >= 2

    def test_references_have_pmids(self, calculator: Any) -> None:
        """Test that references include proper PMIDs"""
        pmids = [ref.pmid for ref in calculator.references if ref.pmid]
        assert "13575523" in pmids  # Edelman 1958
        assert "15885229" in pmids  # Khajuria 2005

    # === Basic Calculation Tests ===

    def test_formula_basic(self, calculator: Any) -> None:
        """Test basic formula: 2*Na + Glucose/18 + BUN/2.8"""
        # Calculated = 2*140 + 90/18 + 14/2.8 = 280 + 5 + 5 = 290
        result = calculator.calculate(
            sodium=140,
            glucose=90,
            bun=14,
        )
        expected = 2 * 140 + 90 / 18 + 14 / 2.8
        assert abs(result.value - expected) < 0.2

    def test_formula_with_ethanol(self, calculator: Any) -> None:
        """Test formula with ethanol: + EtOH/4.6"""
        result = calculator.calculate(
            sodium=140,
            glucose=90,
            bun=14,
            ethanol=100,  # 100 mg/dL
        )
        # Base: 2*140 + 90/18 + 14/2.8 = 290
        # + Ethanol: 100/4.6 ≈ 21.7
        # Total ≈ 311.7
        expected = 2 * 140 + 90 / 18 + 14 / 2.8 + 100 / 4.6
        assert abs(result.value - expected) < 0.2

    def test_contributions_in_details(self, calculator: Any) -> None:
        """Test that individual contributions are recorded"""
        result = calculator.calculate(
            sodium=140,
            glucose=180,
            bun=28,
        )
        assert "sodium_contribution" in result.calculation_details
        assert "glucose_contribution" in result.calculation_details
        assert "bun_contribution" in result.calculation_details
        # Sodium contribution = 2*140 = 280
        assert result.calculation_details["sodium_contribution"] == 280.0
        # Glucose contribution = 180/18 = 10
        assert result.calculation_details["glucose_contribution"] == 10.0
        # BUN contribution = 28/2.8 = 10
        assert result.calculation_details["bun_contribution"] == 10.0

    # === Osmolar Gap Tests ===

    def test_osmolar_gap_normal(self, calculator: Any) -> None:
        """Test normal osmolar gap (<10)"""
        result = calculator.calculate(
            sodium=140,
            glucose=90,
            bun=14,
            measured_osmolality=295,  # Measured
        )
        # Calculated ≈ 290, Gap = 295-290 = 5
        assert result.calculation_details["osmolar_gap"] < 10
        assert "normal" in result.interpretation.detail.lower()

    def test_osmolar_gap_elevated(self, calculator: Any) -> None:
        """Test elevated osmolar gap (>20)"""
        result = calculator.calculate(
            sodium=140,
            glucose=90,
            bun=14,
            measured_osmolality=330,  # High measured
        )
        # Calculated ≈ 290, Gap = 330-290 = 40
        assert result.calculation_details["osmolar_gap"] > 20
        assert len(result.interpretation.warnings) > 0
        assert "toxic" in " ".join(result.interpretation.warnings).lower()

    def test_osmolar_gap_mildly_elevated(self, calculator: Any) -> None:
        """Test mildly elevated osmolar gap (10-20)"""
        result = calculator.calculate(
            sodium=140,
            glucose=90,
            bun=14,
            measured_osmolality=305,  # Gap = 15
        )
        gap = result.calculation_details["osmolar_gap"]
        assert 10 <= gap <= 20

    # === Clinical Interpretation Tests ===

    def test_normal_osmolality(self, calculator: Any) -> None:
        """Test normal osmolality interpretation (275-295)"""
        result = calculator.calculate(
            sodium=140,
            glucose=90,
            bun=14,
        )
        # Result ≈ 290
        assert 275 <= result.value <= 295
        assert result.interpretation.severity.value == "normal"
        assert "normal" in result.interpretation.stage_description.lower()

    def test_hypoosmolality(self, calculator: Any) -> None:
        """Test hypoosmolality (<275)"""
        result = calculator.calculate(
            sodium=125,  # Low sodium
            glucose=80,
            bun=10,
        )
        # 2*125 + 80/18 + 10/2.8 = 250 + 4.4 + 3.6 = 258
        assert result.value < 275
        assert result.interpretation.severity.value == "moderate"
        assert "hypoosmolar" in result.interpretation.stage_description.lower()

    def test_mild_hyperosmolality(self, calculator: Any) -> None:
        """Test mild hyperosmolality (295-320)"""
        result = calculator.calculate(
            sodium=150,  # High sodium
            glucose=100,
            bun=20,
        )
        # 2*150 + 100/18 + 20/2.8 = 300 + 5.6 + 7.1 = 312.7
        assert 295 < result.value <= 320
        assert result.interpretation.severity.value == "mild"

    def test_severe_hyperosmolality(self, calculator: Any) -> None:
        """Test severe hyperosmolality (>350)"""
        result = calculator.calculate(
            sodium=160,  # Very high sodium
            glucose=500,  # High glucose
            bun=50,
        )
        # 2*160 + 500/18 + 50/2.8 = 320 + 27.8 + 17.9 = 365.7
        assert result.value > 350
        assert result.interpretation.severity.value == "severe"

    # === Clinical Scenario Tests ===

    def test_scenario_dka(self, calculator: Any) -> None:
        """Test DKA scenario (high glucose)"""
        result = calculator.calculate(
            sodium=132,  # Pseudohyponatremia
            glucose=450,  # High
            bun=25,
        )
        # 2*132 + 450/18 + 25/2.8 = 264 + 25 + 8.9 = 297.9
        assert "glucose" in result.interpretation.detail.lower()
        assert "dka" in result.interpretation.detail.lower() or "hhs" in result.interpretation.detail.lower()

    def test_scenario_hhs(self, calculator: Any) -> None:
        """Test HHS scenario (very high glucose)"""
        result = calculator.calculate(
            sodium=145,
            glucose=800,
            bun=40,
        )
        # 2*145 + 800/18 + 40/2.8 = 290 + 44.4 + 14.3 = 348.7
        assert result.value > 320
        # Should mention DKA/HHS in recommendations
        recs = " ".join(result.interpretation.next_steps)
        assert "dka" in recs.lower() or "hhs" in recs.lower()

    def test_scenario_siadh(self, calculator: Any) -> None:
        """Test SIADH scenario (low sodium, low osmolality)"""
        result = calculator.calculate(
            sodium=120,
            glucose=90,
            bun=15,
        )
        # 2*120 + 90/18 + 15/2.8 = 240 + 5 + 5.4 = 250.4
        assert result.value < 275
        assert "siadh" in " ".join(result.interpretation.recommendations).lower()

    def test_scenario_toxic_alcohol(self, calculator: Any) -> None:
        """Test toxic alcohol ingestion (high osmolar gap)"""
        result = calculator.calculate(
            sodium=140,
            glucose=100,
            bun=15,
            measured_osmolality=350,  # Very high measured
        )
        # Calculated ≈ 291, Gap = 350-291 = 59
        gap = result.calculation_details["osmolar_gap"]
        assert gap > 20
        # Should warn about toxic alcohols
        warnings = " ".join(result.interpretation.warnings)
        assert "methanol" in warnings.lower() or "ethylene glycol" in warnings.lower()
        # Should recommend fomepizole
        recs = " ".join(result.interpretation.recommendations)
        assert "fomepizole" in recs.lower() or "toxic" in recs.lower()

    def test_scenario_intoxicated_normal_gap(self, calculator: Any) -> None:
        """Test ethanol intoxication with normal osmolar gap"""
        result = calculator.calculate(
            sodium=140,
            glucose=90,
            bun=14,
            ethanol=200,  # Significant ethanol
            measured_osmolality=335,  # High but expected with ethanol
        )
        # Calculated with ethanol ≈ 290 + 43.5 = 333.5
        # Gap ≈ 335 - 333.5 = 1.5 (small, as expected)
        gap = result.calculation_details["osmolar_gap"]
        assert gap < 10  # Normal gap when accounting for ethanol

    # === Input Validation Tests ===

    def test_invalid_sodium_low(self, calculator: Any) -> None:
        """Test validation for sodium < 100"""
        with pytest.raises(ValueError, match="[Ss]odium"):
            calculator.calculate(sodium=90, glucose=100, bun=15)

    def test_invalid_sodium_high(self, calculator: Any) -> None:
        """Test validation for sodium > 180"""
        with pytest.raises(ValueError, match="[Ss]odium"):
            calculator.calculate(sodium=190, glucose=100, bun=15)

    def test_invalid_glucose_negative(self, calculator: Any) -> None:
        """Test validation for negative glucose"""
        with pytest.raises(ValueError, match="[Gg]lucose"):
            calculator.calculate(sodium=140, glucose=-10, bun=15)

    def test_invalid_bun_negative(self, calculator: Any) -> None:
        """Test validation for negative BUN"""
        with pytest.raises(ValueError, match="BUN"):
            calculator.calculate(sodium=140, glucose=100, bun=-5)

    def test_invalid_ethanol_high(self, calculator: Any) -> None:
        """Test validation for ethanol > 1000"""
        with pytest.raises(ValueError, match="[Ee]thanol"):
            calculator.calculate(sodium=140, glucose=100, bun=15, ethanol=1500)

    def test_invalid_measured_osmolality(self, calculator: Any) -> None:
        """Test validation for measured osmolality out of range"""
        with pytest.raises(ValueError, match="[Mm]easured"):
            calculator.calculate(
                sodium=140, glucose=100, bun=15, measured_osmolality=100
            )

    # === Edge Cases ===

    def test_zero_glucose(self, calculator: Any) -> None:
        """Test with zero glucose (hypoglycemia)"""
        result = calculator.calculate(
            sodium=140,
            glucose=0,
            bun=14,
        )
        # 2*140 + 0/18 + 14/2.8 = 280 + 0 + 5 = 285
        assert abs(result.value - 285) < 1

    def test_very_high_glucose(self, calculator: Any) -> None:
        """Test with very high glucose"""
        result = calculator.calculate(
            sodium=140,
            glucose=1500,
            bun=20,
        )
        # 2*140 + 1500/18 + 20/2.8 = 280 + 83.3 + 7.1 = 370.4
        assert result.value > 350

    def test_ethanol_zero(self, calculator: Any) -> None:
        """Test with ethanol = 0"""
        result = calculator.calculate(
            sodium=140,
            glucose=100,
            bun=15,
            ethanol=0,
        )
        # Should be same as without ethanol
        result_no_eth = calculator.calculate(
            sodium=140,
            glucose=100,
            bun=15,
        )
        assert abs(result.value - result_no_eth.value) < 0.1

    def test_raw_inputs_stored(self, calculator: Any) -> None:
        """Test that raw inputs are stored"""
        result = calculator.calculate(
            sodium=140,
            glucose=100,
            bun=15,
            ethanol=50,
            measured_osmolality=300,
        )
        assert result.raw_inputs["sodium"] == 140
        assert result.raw_inputs["glucose"] == 100
        assert result.raw_inputs["bun"] == 15
        assert result.raw_inputs["ethanol"] == 50
        assert result.raw_inputs["measured_osmolality"] == 300

    def test_unit_is_mosm_kg(self, calculator: Any) -> None:
        """Test that result unit is mOsm/kg"""
        result = calculator.calculate(sodium=140, glucose=100, bun=15)
        assert result.unit.value == "mOsm/kg"
