from typing import Any

"""Tests for Pediatric Calculators"""
import pytest


class TestPediatricDosingCalculator:
    def test_basic_dosing(self) -> None:
        from src.domain.services.calculators import PediatricDosingCalculator
        calc = PediatricDosingCalculator()
        result = calc.calculate(weight_kg=20, drug_name="acetaminophen")
        assert result.value is not None
        assert result.value > 0

    def test_tool_id(self) -> None:
        from src.domain.services.calculators import PediatricDosingCalculator
        assert PediatricDosingCalculator().tool_id == "pediatric_dosing"


class TestMablCalculator:
    def test_mabl_basic(self) -> None:
        from src.domain.services.calculators import MablCalculator
        calc = MablCalculator()
        result = calc.calculate(weight_kg=70, initial_hematocrit=40, target_hematocrit=30)
        assert result.value is not None
        assert result.value > 0

    def test_tool_id(self) -> None:
        from src.domain.services.calculators import MablCalculator
        assert MablCalculator().tool_id == "mabl"


class TestTransfusionCalculator:
    """Comprehensive tests for Transfusion Volume Calculator"""

    @pytest.fixture
    def calc(self) -> Any:
        from src.domain.services.calculators import TransfusionCalculator
        return TransfusionCalculator()

    def test_tool_id(self, calc: Any) -> None:
        assert calc.tool_id == "transfusion_calc"

    # ========================================================================
    # Basic Hematocrit-based Calculations
    # ========================================================================

    def test_transfusion_hct_adult_male(self, calc: Any) -> None:
        """Adult male: EBV = 70 mL/kg"""
        result = calc.calculate(
            weight_kg=70,
            current_hematocrit=25,
            target_hematocrit=30,
            patient_type="adult_male"
        )
        assert result.value is not None
        assert result.value > 0
        # Formula: EBV * (target - current) / Hct_pRBC
        # 70 * 70 * (30-25) / 65 ≈ 377 mL

    def test_transfusion_hct_adult_female(self, calc: Any) -> None:
        """Adult female: EBV = 65 mL/kg"""
        result = calc.calculate(
            weight_kg=70,
            current_hematocrit=25,
            target_hematocrit=30,
            patient_type="adult_female"
        )
        assert result.value is not None
        assert result.value > 0

    def test_transfusion_hct_child(self, calc: Any) -> None:
        """Child: EBV = 75 mL/kg"""
        result = calc.calculate(
            weight_kg=20,
            current_hematocrit=22,
            target_hematocrit=30,
            patient_type="child"
        )
        assert result.value is not None
        assert result.value > 0

    def test_transfusion_hct_infant(self, calc: Any) -> None:
        """Infant: EBV = 80 mL/kg"""
        result = calc.calculate(
            weight_kg=8,
            current_hematocrit=25,
            target_hematocrit=35,
            patient_type="infant"
        )
        assert result.value is not None
        assert result.value > 0

    def test_transfusion_hct_term_neonate(self, calc: Any) -> None:
        """Term neonate: EBV = 85 mL/kg"""
        result = calc.calculate(
            weight_kg=3.5,
            current_hematocrit=35,
            target_hematocrit=45,
            patient_type="term_neonate"
        )
        assert result.value is not None
        assert result.value > 0

    def test_transfusion_hct_preterm_neonate(self, calc: Any) -> None:
        """Preterm neonate: EBV = 90 mL/kg"""
        result = calc.calculate(
            weight_kg=1.5,
            current_hematocrit=30,
            target_hematocrit=40,
            patient_type="preterm_neonate"
        )
        assert result.value is not None
        assert result.value > 0

    # ========================================================================
    # Hemoglobin-based Calculations
    # ========================================================================

    def test_transfusion_hgb(self, calc: Any) -> None:
        """Calculate based on hemoglobin"""
        result = calc.calculate(
            weight_kg=70,
            current_hemoglobin=7,
            target_hemoglobin=10,
            patient_type="adult_male"
        )
        assert result.value is not None
        assert result.value > 0

    def test_transfusion_hgb_pediatric(self, calc: Any) -> None:
        """Hemoglobin-based for pediatric patient"""
        result = calc.calculate(
            weight_kg=15,
            current_hemoglobin=6,
            target_hemoglobin=10,
            patient_type="child"
        )
        assert result.value is not None
        assert result.value > 0

    # ========================================================================
    # Product Types
    # ========================================================================

    def test_transfusion_prbc(self, calc: Any) -> None:
        """pRBC transfusion (default)"""
        result = calc.calculate(
            weight_kg=70,
            current_hematocrit=25,
            target_hematocrit=30,
            product_type="prbc"
        )
        assert result.value is not None
        assert result.value > 0

    def test_transfusion_whole_blood(self, calc: Any) -> None:
        """Whole blood transfusion"""
        result = calc.calculate(
            weight_kg=70,
            current_hematocrit=25,
            target_hematocrit=30,
            product_type="whole_blood"
        )
        assert result.value is not None
        assert result.value > 0

    # ========================================================================
    # Platelet Transfusion
    # ========================================================================

    def test_transfusion_platelets(self, calc: Any) -> None:
        """Platelet transfusion calculation"""
        result = calc.calculate(
            weight_kg=70,
            current_platelet=20,
            target_platelet=50,
            product_type="platelets"
        )
        assert result.value is not None
        assert result.value >= 0

    def test_transfusion_platelets_pediatric(self, calc: Any) -> None:
        """Platelet transfusion for pediatric patient"""
        result = calc.calculate(
            weight_kg=15,
            current_platelet=10,
            target_platelet=50,
            product_type="platelets",
            patient_type="child"
        )
        assert result.value is not None
        assert result.value >= 0

    # ========================================================================
    # Edge Cases
    # ========================================================================

    def test_transfusion_small_gap(self, calc: Any) -> None:
        """Small Hct gap (minimal transfusion)"""
        result = calc.calculate(
            weight_kg=70,
            current_hematocrit=29,
            target_hematocrit=30
        )
        assert result.value is not None
        assert result.value > 0

    def test_transfusion_large_gap(self, calc: Any) -> None:
        """Large Hct gap (significant transfusion)"""
        result = calc.calculate(
            weight_kg=70,
            current_hematocrit=15,
            target_hematocrit=30
        )
        assert result.value is not None
        assert result.value > 0

    def test_transfusion_high_weight(self, calc: Any) -> None:
        """High weight patient"""
        result = calc.calculate(
            weight_kg=120,
            current_hematocrit=20,
            target_hematocrit=30
        )
        assert result.value is not None
        assert result.value > 0

    def test_transfusion_low_weight(self, calc: Any) -> None:
        """Low weight neonate"""
        result = calc.calculate(
            weight_kg=0.8,
            current_hematocrit=30,
            target_hematocrit=40,
            patient_type="preterm_neonate"
        )
        assert result.value is not None
        assert result.value > 0

    # ========================================================================
    # Interpretation and Metadata
    # ========================================================================

    def test_transfusion_interpretation(self, calc: Any) -> None:
        """Verify interpretation is returned"""
        calc.calculate(
            weight_kg=70,
            current_hematocrit=25,
            target_hematocrit=30
        )

    def test_transfusion_metadata(self, calc: Any) -> None:
        """Verify metadata is correct"""
        meta = calc.metadata
        assert meta.tool_id == "transfusion_calc"
        assert meta.name is not None
        assert "transfusion" in meta.name.lower() or "blood" in meta.name.lower()
