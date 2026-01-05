from typing import Any
"""Tests for Emergency Medicine Calculators"""


class TestWellsDvtCalculator:
    def test_wells_dvt_low(self) -> None:
        from src.domain.services.calculators import WellsDvtCalculator
        calc = WellsDvtCalculator()
        result = calc.calculate(
            active_cancer=False, paralysis_paresis_or_recent_cast=False,
            bedridden_or_major_surgery=False, tenderness_along_deep_veins=False,
            entire_leg_swollen=False, calf_swelling_gt_3cm=False,
            pitting_edema=False, collateral_superficial_veins=False,
            previous_dvt=False, alternative_diagnosis_likely=True
        )
        assert result.value is not None
        assert result.value <= 0

    def test_tool_id(self) -> None:
        from src.domain.services.calculators import WellsDvtCalculator
        assert WellsDvtCalculator().tool_id == "wells_dvt"


class TestWellsPeCalculator:
    def test_wells_pe_low(self) -> None:
        from src.domain.services.calculators import WellsPeCalculator
        calc = WellsPeCalculator()
        result = calc.calculate(
            clinical_signs_dvt=False, pe_most_likely_diagnosis=False,
            heart_rate_gt_100=False, immobilization_or_surgery=False,
            previous_dvt_pe=False, hemoptysis=False, malignancy=False
        )
        assert result.value is not None
        assert result.value == 0

    def test_tool_id(self) -> None:
        from src.domain.services.calculators import WellsPeCalculator
        assert WellsPeCalculator().tool_id == "wells_pe"
