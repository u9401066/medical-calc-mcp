"""Tests for Pulmonology Calculators"""
import pytest


class TestCurb65Calculator:
    def test_curb65_zero(self):
        from src.domain.services.calculators import Curb65Calculator
        calc = Curb65Calculator()
        result = calc.calculate(
            confusion=False, bun_gt_19_or_urea_gt_7=False,
            respiratory_rate_gte_30=False, sbp_lt_90_or_dbp_lte_60=False,
            age_gte_65=False
        )
        assert result.value == 0

    def test_curb65_max(self):
        from src.domain.services.calculators import Curb65Calculator
        calc = Curb65Calculator()
        result = calc.calculate(
            confusion=True, bun_gt_19_or_urea_gt_7=True,
            respiratory_rate_gte_30=True, sbp_lt_90_or_dbp_lte_60=True,
            age_gte_65=True
        )
        assert result.value == 5

    def test_tool_id(self):
        from src.domain.services.calculators import Curb65Calculator
        assert Curb65Calculator().tool_id == "curb65"


class TestPsiPortCalculator:
    def test_psi_port_basic(self):
        from src.domain.services.calculators import PsiPortCalculator
        calc = PsiPortCalculator()
        result = calc.calculate(age_years=50)
        assert result.value >= 0

    def test_tool_id(self):
        from src.domain.services.calculators import PsiPortCalculator
        assert PsiPortCalculator().tool_id == "psi_port"
