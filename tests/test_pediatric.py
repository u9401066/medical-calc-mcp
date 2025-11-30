"""Tests for Pediatric Calculators"""
import pytest


class TestPediatricDosingCalculator:
    def test_basic_dosing(self):
        from src.domain.services.calculators import PediatricDosingCalculator
        calc = PediatricDosingCalculator()
        result = calc.calculate(weight_kg=20, drug_name="acetaminophen")
        assert result.value > 0

    def test_tool_id(self):
        from src.domain.services.calculators import PediatricDosingCalculator
        assert PediatricDosingCalculator().tool_id == "pediatric_dosing"


class TestMablCalculator:
    def test_mabl_basic(self):
        from src.domain.services.calculators import MablCalculator
        calc = MablCalculator()
        result = calc.calculate(weight_kg=70, initial_hematocrit=40, target_hematocrit=30)
        assert result.value > 0

    def test_tool_id(self):
        from src.domain.services.calculators import MablCalculator
        assert MablCalculator().tool_id == "mabl"


class TestTransfusionCalculator:
    def test_transfusion_basic(self):
        from src.domain.services.calculators import TransfusionCalculator
        calc = TransfusionCalculator()
        result = calc.calculate(
            weight_kg=70, current_hematocrit=25, target_hematocrit=30
        )
        assert result.value > 0

    def test_tool_id(self):
        from src.domain.services.calculators import TransfusionCalculator
        assert TransfusionCalculator().tool_id == "transfusion_calc"
