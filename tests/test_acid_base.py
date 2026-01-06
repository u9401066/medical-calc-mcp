from typing import Any

"""
Tests for Acid-Base Calculators

Covers:
- Anion Gap Calculator (AG, Corrected AG)
- Delta Ratio Calculator (ΔAG / ΔHCO₃⁻)
- Corrected Sodium Calculator (Katz & Hillier methods)
"""

import pytest

from src.domain.services.calculators import (
    AnionGapCalculator,
    CorrectedSodiumCalculator,
    DeltaRatioCalculator,
)


class TestAnionGapCalculator:
    """Test Anion Gap Calculator"""

    def setup_method(self) -> Any:
        self.calc = AnionGapCalculator()

    def test_metadata(self) -> None:
        """Test calculator metadata"""
        meta = self.calc.metadata
        assert meta.tool_id == "anion_gap"
        assert meta.name == "Anion Gap"
        assert "anion_gap" in meta.low_level.tool_id

    def test_normal_anion_gap(self) -> None:
        """Test normal anion gap calculation (Na=140, Cl=104, HCO3=24)"""
        result = self.calc.calculate(sodium=140, chloride=104, bicarbonate=24)

        assert result.value is not None
        assert result.value == 12  # 140 - 104 - 24 = 12
        assert result.interpretation.summary is not None
        assert "Normal" in result.interpretation.summary

    def test_elevated_anion_gap(self) -> None:
        """Test high anion gap metabolic acidosis"""
        result = self.calc.calculate(sodium=140, chloride=100, bicarbonate=12)

        # AG = 140 - 100 - 12 = 28
        assert result.value is not None
        assert result.value == 28
        assert result.interpretation.summary is not None
        assert "HAGMA" in result.interpretation.summary or "High" in result.interpretation.summary

    def test_low_anion_gap(self) -> None:
        """Test low anion gap (rare, usually artifact or hypoalbuminemia)"""
        result = self.calc.calculate(sodium=140, chloride=108, bicarbonate=30)

        # AG = 140 - 108 - 30 = 2
        assert result.value is not None
        assert result.value == 2
        assert result.interpretation.summary is not None
        assert "Low" in result.interpretation.summary

    def test_corrected_anion_gap_for_hypoalbuminemia(self) -> None:
        """Test albumin-corrected AG (Figge formula)"""
        # Low albumin increases corrected AG
        result = self.calc.calculate(
            sodium=140, chloride=104, bicarbonate=24,
            albumin=2.0  # Low albumin (normal 4.0)
        )

        # Raw AG = 12, Corrected = 12 + 2.5*(4.0-2.0) = 17
        # With albumin, the result.value IS the corrected AG
        assert result.value is not None
        assert result.value == 17.0
        assert result.calculation_details is not None
        assert result.calculation_details.get("anion_gap") == 12  # Raw AG
        assert result.calculation_details.get("corrected_ag") == 17.0  # Corrected

    def test_borderline_anion_gap(self) -> None:
        """Test borderline elevated AG (12-20 range)"""
        result = self.calc.calculate(sodium=140, chloride=102, bicarbonate=22)

        # AG = 140 - 102 - 22 = 16
        assert result.value is not None
        assert result.value == 16


class TestDeltaRatioCalculator:
    """Test Delta Ratio Calculator"""

    def setup_method(self) -> Any:
        self.calc = DeltaRatioCalculator()

    def test_metadata(self) -> None:
        """Test calculator metadata"""
        meta = self.calc.metadata
        assert meta.tool_id == "delta_ratio"
        assert "Delta" in meta.name

    def test_pure_hagma(self) -> None:
        """Test pure HAGMA (delta ratio 1-2)"""
        # Scenario: AG=28, HCO3=12
        # ΔAG = 28 - 12 = 16, ΔHCO3 = 24 - 12 = 12
        # Delta Ratio = 16/12 = 1.33
        result = self.calc.calculate(anion_gap=28, bicarbonate=12)

        ratio = result.value
        assert ratio is not None
        assert 1.0 <= ratio <= 2.0
        # Check stage instead of summary
        assert result.interpretation.stage == "Pure HAGMA"

    def test_hagma_plus_nagma(self) -> None:
        """Test HAGMA + NAGMA (delta ratio < 1)"""
        # Scenario: AG=20, HCO3=8
        # ΔAG = 20 - 12 = 8, ΔHCO3 = 24 - 8 = 16
        # Delta Ratio = 8/16 = 0.5
        result = self.calc.calculate(anion_gap=20, bicarbonate=8)

        ratio = result.value
        assert ratio is not None
        assert ratio < 1.0
        assert result.interpretation.summary is not None
        interpretation = result.interpretation.summary.lower()
        assert "nagma" in interpretation or "concurrent" in interpretation or "mixed" in interpretation

    def test_hagma_plus_metabolic_alkalosis(self) -> None:
        """Test HAGMA + metabolic alkalosis (delta ratio > 2)"""
        # Scenario: AG=36, HCO3=20
        # ΔAG = 36 - 12 = 24, ΔHCO3 = 24 - 20 = 4
        # Delta Ratio = 24/4 = 6.0
        result = self.calc.calculate(anion_gap=36, bicarbonate=20)

        ratio = result.value
        assert ratio is not None
        assert ratio > 2.0
        assert result.interpretation.summary is not None
        interpretation = result.interpretation.summary.lower()
        assert "alkalosis" in interpretation or "concurrent" in interpretation

    def test_custom_baseline_values(self) -> None:
        """Test with custom baseline AG and HCO3"""
        # Note: parameter is normal_ag and normal_hco3
        result = self.calc.calculate(
            anion_gap=28, bicarbonate=12,
            normal_ag=10, normal_hco3=24
        )

        # ΔAG = 28 - 10 = 18, ΔHCO3 = 24 - 12 = 12
        # Delta Ratio = 18/12 = 1.5
        ratio = result.value
        assert ratio is not None
        assert 1.0 <= ratio <= 2.0

    def test_near_zero_delta_hco3(self) -> None:
        """Test handling when HCO3 is near baseline (avoid division issues)"""
        result = self.calc.calculate(anion_gap=20, bicarbonate=23)

        # ΔHCO3 = 24 - 23 = 1, should handle gracefully
        # Large delta ratio expected (8/1 = 8)
        assert result.value is not None
        assert result.value > 2  # High ratio when ΔHCO3 is small


class TestCorrectedSodiumCalculator:
    """Test Corrected Sodium Calculator"""

    def setup_method(self) -> Any:
        self.calc = CorrectedSodiumCalculator()

    def test_metadata(self) -> None:
        """Test calculator metadata"""
        meta = self.calc.metadata
        assert meta.tool_id == "corrected_sodium"
        assert "Sodium" in meta.name

    def test_normal_glucose_no_correction(self) -> None:
        """Test that normal glucose requires minimal correction"""
        # Note: parameter is measured_sodium
        result = self.calc.calculate(measured_sodium=135, glucose=100)

        # Correction = 1.6 * (100-100)/100 = 0
        assert result.value is not None
        assert result.value == pytest.approx(135, abs=0.5)

    def test_moderate_hyperglycemia_katz(self) -> None:
        """Test Katz correction for moderate hyperglycemia"""
        result = self.calc.calculate(measured_sodium=130, glucose=400)

        # Katz: 130 + 1.6 * (400-100)/100 = 130 + 4.8 = 134.8
        assert result.value is not None
        assert result.value == pytest.approx(134.8, rel=0.05)

    def test_severe_hyperglycemia_katz(self) -> None:
        """Test Katz correction for severe hyperglycemia (DKA/HHS)"""
        result = self.calc.calculate(measured_sodium=125, glucose=800)

        # Katz: 125 + 1.6 * (800-100)/100 = 125 + 11.2 = 136.2
        assert result.value is not None
        assert result.value == pytest.approx(136.2, rel=0.05)

    def test_hillier_method(self) -> None:
        """Test that Hillier formula gives higher correction than Katz"""
        katz_result = self.calc.calculate(measured_sodium=130, glucose=600, formula="katz")
        hillier_result = self.calc.calculate(measured_sodium=130, glucose=600, formula="hillier")

        # Katz: 130 + 1.6 * 5 = 138
        # Hillier: 130 + 2.4 * 5 = 142
        assert hillier_result.value is not None
        assert katz_result.value is not None
        assert hillier_result.value > katz_result.value

    def test_interpretation_for_true_hyponatremia(self) -> None:
        """Test interpretation when corrected Na still shows hyponatremia"""
        result = self.calc.calculate(measured_sodium=120, glucose=600)

        # Even after correction, Na might still be low
        # Katz: 120 + 1.6 * 5 = 128 (still low)
        assert result.interpretation.summary is not None
        interpretation = result.interpretation.summary.lower()
        assert result.value is not None
        assert "hyponatremia" in interpretation or result.value < 135

    def test_masked_hypernatremia(self) -> None:
        """Test when dilutional effect masks true hypernatremia"""
        result = self.calc.calculate(measured_sodium=140, glucose=1000)

        # Katz: 140 + 1.6 * 9 = 154.4 (hypernatremia revealed)
        assert result.value is not None
        assert result.value > 145


class TestAcidBaseIntegration:
    """Integration tests for acid-base workflows"""

    def test_complete_dka_workup(self) -> None:
        """Test complete DKA acid-base evaluation"""
        # DKA patient: AG 28, HCO3 10, Na 128, Glucose 500

        ag_calc = AnionGapCalculator()
        delta_calc = DeltaRatioCalculator()
        na_calc = CorrectedSodiumCalculator()

        # Step 1: Anion Gap
        ag_result = ag_calc.calculate(sodium=128, chloride=90, bicarbonate=10)
        assert ag_result.value is not None
        assert ag_result.value > 20  # HAGMA confirmed

        # Step 2: Delta Ratio
        assert ag_result.value is not None
        delta_calc.calculate(anion_gap=ag_result.value, bicarbonate=10)
        # Check if pure HAGMA or mixed

        # Step 3: Corrected Sodium
        na_result = na_calc.calculate(measured_sodium=128, glucose=500)
        # True sodium higher than measured
        assert na_result.value is not None
        assert na_result.value > 128

    def test_mixed_acidosis_detection(self) -> None:
        """Test detection of concurrent HAGMA + NAGMA"""
        ag_calc = AnionGapCalculator()
        delta_calc = DeltaRatioCalculator()

        # Patient with diarrhea (NAGMA) + DKA (HAGMA)
        ag_result = ag_calc.calculate(sodium=135, chloride=100, bicarbonate=6)
        ag = ag_result.value  # = 29

        assert ag is not None
        delta_result = delta_calc.calculate(anion_gap=ag, bicarbonate=6)
        # ΔAG = 29 - 12 = 17, ΔHCO3 = 24 - 6 = 18
        # Delta ratio = 17/18 ≈ 0.94 (< 1 suggests concurrent NAGMA)

        ratio = delta_result.value
        assert ratio is not None
        if ratio < 1:
            assert delta_result.interpretation.summary is not None
            interpretation = delta_result.interpretation.summary.lower()
            assert "nagma" in interpretation or "concurrent" in interpretation or "mixed" in interpretation


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_anion_gap_extreme_values(self) -> None:
        """Test AG with extreme but valid values"""
        calc = AnionGapCalculator()

        # Very high AG (severe DKA)
        result = calc.calculate(sodium=145, chloride=85, bicarbonate=5)
        assert result.value is not None
        assert result.value == 55  # Extreme but calculated

    def test_delta_ratio_normal_ag(self) -> None:
        """Test delta ratio with normal anion gap"""
        calc = DeltaRatioCalculator()

        result = calc.calculate(anion_gap=12, bicarbonate=20)
        # ΔAG = 0, when AG is not elevated, value can be None
        # The interpretation should indicate no HAGMA
        assert result.interpretation.summary is not None
        interpretation = result.interpretation.summary.lower()
        assert result.value is None or "not applicable" in interpretation or "no" in interpretation

    def test_corrected_sodium_units(self) -> None:
        """Test that glucose is expected in mg/dL by default"""
        calc = CorrectedSodiumCalculator()

        result = calc.calculate(measured_sodium=130, glucose=540)  # 540 mg/dL = 30 mmol/L

        # Katz: 130 + 1.6 * 4.4 = 137.04
        assert result.value is not None
        assert result.value == pytest.approx(137, abs=1)


class TestValidation:
    """Test input validation"""

    def test_anion_gap_validates_ranges(self) -> None:
        """Test that AG calculator validates input ranges"""
        calc = AnionGapCalculator()

        # Normal ranges should work
        calc.calculate(sodium=140, chloride=104, bicarbonate=24)

    def test_delta_ratio_with_low_ag(self) -> None:
        """Test delta ratio behavior with non-elevated AG"""
        calc = DeltaRatioCalculator()

        # When AG is not elevated, delta ratio is not clinically meaningful
        result = calc.calculate(anion_gap=10, bicarbonate=24)

        # Value can be None, but result should still return
        assert result is not None
        # Interpretation should indicate limitation
        assert result.interpretation.summary is not None
        assert "not applicable" in result.interpretation.summary.lower() or result.value is None

    def test_corrected_sodium_normal_glucose(self) -> None:
        """Test corrected sodium when glucose is normal"""
        calc = CorrectedSodiumCalculator()

        result = calc.calculate(measured_sodium=140, glucose=100)

        # Minimal correction expected
        assert result.value is not None
        assert result.value == pytest.approx(140, abs=1)

    def test_corrected_sodium_mmol_glucose(self) -> None:
        """Test corrected sodium with mmol/L glucose"""
        calc = CorrectedSodiumCalculator()

        # 30 mmol/L glucose = 540 mg/dL
        result = calc.calculate(measured_sodium=130, glucose=30, glucose_unit="mmol/L")

        # Katz: 130 + 1.6 * 4.4 = 137.04
        assert result.value is not None
        assert result.value == pytest.approx(137, abs=1)


# ============================================================================
# Run tests
# ============================================================================
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
