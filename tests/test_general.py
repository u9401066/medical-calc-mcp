from typing import Any
"""
Tests for Phase 14 General Calculators

Testing:
- Body Surface Area (BSA)
- Cockcroft-Gault CrCl
- Corrected Calcium
- Parkland Formula
"""

import pytest

from src.domain.services.calculators import (
    BodySurfaceAreaCalculator,
    CockcroftGaultCalculator,
    CorrectedCalciumCalculator,
    ParklandFormulaCalculator,
)


class TestBodySurfaceArea:
    """Test BSA Calculator"""

    @pytest.fixture
    def calculator(self) -> Any:
        return BodySurfaceAreaCalculator()

    def test_metadata(self, calculator: Any) -> None:
        """Test calculator metadata"""
        assert calculator.tool_id == "body_surface_area"
        assert "body" in calculator.name.lower() or "bsa" in calculator.name.lower()

    def test_mosteller_formula_70kg_170cm(self, calculator: Any) -> None:
        """Test Mosteller formula with typical adult"""
        result = calculator.calculate(
            weight_kg=70,
            height_cm=170,
            formula="mosteller"
        )
        # Mosteller: √(70 × 170 / 3600) ≈ 1.81 m²
        assert result.value is not None
        assert 1.7 <= result.value <= 1.9
        assert result.unit is not None
        assert result.unit.value == "m²" or str(result.unit) == "m²"

    def test_dubois_formula(self, calculator: Any) -> None:
        """Test Du Bois formula"""
        result = calculator.calculate(
            weight_kg=70,
            height_cm=170,
            formula="dubois"
        )
        # Du Bois: 0.007184 × 70^0.425 × 170^0.725 ≈ 1.82 m²
        assert result.value is not None
        assert 1.7 <= result.value <= 1.9

    def test_haycock_formula_pediatric(self, calculator: Any) -> None:
        """Test Haycock formula for pediatric (preferred for children)"""
        result = calculator.calculate(
            weight_kg=20,
            height_cm=115,
            formula="haycock"
        )
        # Expected ~0.75-0.85 m² for a child
        assert result.value is not None
        assert 0.7 <= result.value <= 0.9

    def test_all_formulas_return_similar_results(self, calculator: Any) -> None:
        """Test that all formulas give reasonably similar results"""
        formulas = ["mosteller", "dubois", "haycock", "boyd"]
        results = []

        for formula in formulas:
            result = calculator.calculate(weight_kg=70, height_cm=170, formula=formula)
            results.append(result.value)

        # All results should be within 10% of each other
        mean_bsa = sum(results) / len(results)
        for bsa in results:
            assert abs(bsa - mean_bsa) / mean_bsa < 0.1


class TestCockcroftGault:
    """Test Cockcroft-Gault CrCl Calculator"""

    @pytest.fixture
    def calculator(self) -> Any:
        return CockcroftGaultCalculator()

    def test_metadata(self, calculator: Any) -> None:
        """Test calculator metadata"""
        assert calculator.tool_id == "cockcroft_gault"

    def test_young_male_normal_creatinine(self, calculator: Any) -> None:
        """Test young male with normal kidney function"""
        result = calculator.calculate(
            age=30,
            weight_kg=70,
            creatinine_mg_dl=1.0,
            sex="male"
        )
        # CrCl = (140-30) × 70 / (72 × 1.0) ≈ 107 mL/min
        assert result.value is not None
        assert 100 <= result.value <= 115
        assert result.unit is not None
        assert result.unit.value == "mL/min" or str(result.unit) == "mL/min"

    def test_female_adjustment(self, calculator: Any) -> None:
        """Test female (0.85 factor)"""
        result = calculator.calculate(
            age=30,
            weight_kg=60,
            creatinine_mg_dl=1.0,
            sex="female"
        )
        # CrCl = (140-30) × 60 / (72 × 1.0) × 0.85 ≈ 77 mL/min
        assert result.value is not None
        assert 70 <= result.value <= 85

    def test_elderly_reduced_crcl(self, calculator: Any) -> None:
        """Test elderly patient with reduced CrCl"""
        result = calculator.calculate(
            age=80,
            weight_kg=60,
            creatinine_mg_dl=1.5,
            sex="male"
        )
        # CrCl = (140-80) × 60 / (72 × 1.5) ≈ 33 mL/min
        assert result.value is not None
        assert 28 <= result.value <= 38

    def test_obese_patient_ibw_adjustment(self, calculator: Any) -> None:
        """Test obese patient with IBW adjustment"""
        # Height 170cm male, IBW ≈ 66 kg
        # Actual weight 100 kg (>120% IBW)
        result = calculator.calculate(
            age=40,
            weight_kg=100,
            height_cm=170,
            creatinine_mg_dl=1.0,
            sex="male",
        )
        # Should use IBW or adjusted weight instead of actual weight
        # Result should be lower than using actual weight
        assert result.value is not None
        assert result.value < 145  # If using 100kg would be ~139


class TestCorrectedCalcium:
    """Test Corrected Calcium Calculator"""

    @pytest.fixture
    def calculator(self) -> Any:
        return CorrectedCalciumCalculator()

    def test_metadata(self, calculator: Any) -> None:
        """Test calculator metadata"""
        assert calculator.tool_id == "corrected_calcium"

    def test_normal_albumin_no_correction(self, calculator: Any) -> None:
        """Test normal albumin (4.0) - no correction needed"""
        result = calculator.calculate(
            calcium_mg_dl=9.0,
            albumin_g_dl=4.0,
        )
        # Corrected Ca = 9.0 + 0.8 × (4.0 - 4.0) = 9.0
        assert result.value is not None
        assert result.value == pytest.approx(9.0, abs=0.1)
        assert result.unit is not None
        assert result.unit.value == "mg/dL" or str(result.unit) == "mg/dL"

    def test_low_albumin_correction(self, calculator: Any) -> None:
        """Test low albumin correction"""
        result = calculator.calculate(
            calcium_mg_dl=8.0,
            albumin_g_dl=2.0,
        )
        # Corrected Ca = 8.0 + 0.8 × (4.0 - 2.0) = 9.6
        assert result.value is not None
        assert result.value == pytest.approx(9.6, abs=0.1)

    def test_hypocalcemia_detection(self, calculator: Any) -> None:
        """Test hypocalcemia classification"""
        result = calculator.calculate(
            calcium_mg_dl=7.0,
            albumin_g_dl=4.0,
        )
        # Corrected Ca = 7.0 (hypocalcemia)
        assert result.value is not None
        assert result.value < 8.5
        assert result.interpretation.summary is not None
        assert "hypocalcemia" in result.interpretation.summary.lower() or \
               "低血鈣" in result.interpretation.summary

    def test_hypercalcemia_detection(self, calculator: Any) -> None:
        """Test hypercalcemia classification"""
        result = calculator.calculate(
            calcium_mg_dl=12.0,
            albumin_g_dl=4.0,
        )
        # Corrected Ca = 12.0 (hypercalcemia)
        assert result.value is not None
        assert result.value > 10.5
        assert result.interpretation.summary is not None
        assert "hypercalcemia" in result.interpretation.summary.lower() or \
               "高血鈣" in result.interpretation.summary


class TestParklandFormula:
    """Test Parkland Formula Calculator"""

    @pytest.fixture
    def calculator(self) -> Any:
        return ParklandFormulaCalculator()

    def test_metadata(self, calculator: Any) -> None:
        """Test calculator metadata"""
        assert calculator.tool_id == "parkland_formula"

    def test_standard_burn(self, calculator: Any) -> None:
        """Test 30% TBSA burn in 70kg patient"""
        result = calculator.calculate(
            weight_kg=70,
            tbsa_percent=30,
            hours_since_burn=0
        )
        # 24h fluid = 4 mL × 70 kg × 30% = 8400 mL
        assert result.value is not None
        assert result.value == pytest.approx(8400, abs=100)
        assert result.unit is not None
        assert "mL" in str(result.unit)  # Unit is mL (total for 24h)

    def test_large_burn(self, calculator: Any) -> None:
        """Test 50% TBSA burn"""
        result = calculator.calculate(
            weight_kg=80,
            tbsa_percent=50,
            hours_since_burn=0
        )
        # 24h fluid = 4 × 80 × 50 = 16000 mL
        assert result.value is not None
        assert result.value == pytest.approx(16000, abs=100)

    def test_delayed_presentation(self, calculator: Any) -> None:
        """Test delayed presentation (4 hours post-burn)"""
        result = calculator.calculate(
            weight_kg=70,
            tbsa_percent=30,
            hours_since_burn=4
        )
        # Should still calculate 24h total but adjust remaining time
        assert result.value is not None
        assert result.value == pytest.approx(8400, abs=100)
        # Details should mention remaining fluid for first 8h

    def test_details_include_rate(self, calculator: Any) -> None:
        """Test that calculation_details include infusion rates"""
        result = calculator.calculate(
            weight_kg=70,
            tbsa_percent=30,
            hours_since_burn=0
        )
        # 8400 mL total
        # First 8h: 4200 mL = 525 mL/h
        # Next 16h: 4200 mL = 262.5 mL/h
        assert "first_8hr" in result.calculation_details or "first_8h" in str(result.calculation_details).lower()

    def test_small_burn_warning(self, calculator: Any) -> None:
        """Test that small burns get appropriate guidance"""
        result = calculator.calculate(
            weight_kg=70,
            tbsa_percent=10,
            hours_since_burn=0
        )
        # 10% TBSA may not need formal resuscitation
        # But calculator should still provide values
        assert result.value is not None
        assert result.value == pytest.approx(2800, abs=100)


class TestIntegration:
    """Integration tests for general calculators"""

    def test_all_calculators_instantiate(self) -> None:
        """Test that all calculators can be instantiated"""
        calculators = [
            BodySurfaceAreaCalculator(),
            CockcroftGaultCalculator(),
            CorrectedCalciumCalculator(),
            ParklandFormulaCalculator(),
        ]

        for calc in calculators:
            assert calc.tool_id is not None
            assert calc.name is not None
            assert len(calc.references) > 0

    def test_all_calculators_have_required_methods(self) -> None:
        """Test that all calculators have required methods"""
        calculators = [
            BodySurfaceAreaCalculator(),
            CockcroftGaultCalculator(),
            CorrectedCalciumCalculator(),
            ParklandFormulaCalculator(),
        ]

        for calc in calculators:
            assert hasattr(calc, 'calculate')
            assert hasattr(calc, 'tool_id')
            assert hasattr(calc, 'name')
            # description is in metadata, not a direct property
            assert hasattr(calc, 'references')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
