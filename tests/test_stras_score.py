"""Tests for Stroke after Surgery (STRAS) Score."""

from typing import Any

import pytest

from src.domain.value_objects.interpretation import RiskLevel


class TestStrasScoreCalculator:
    @pytest.fixture
    def calc(self) -> Any:
        from src.domain.services.calculators import StrasScoreCalculator

        return StrasScoreCalculator()

    def test_tool_id(self, calc: Any) -> None:
        assert calc.tool_id == "stras_score"

    def test_low_risk_baseline(self, calc: Any) -> None:
        result = calc.calculate(age_years=45)

        assert result.value == 0
        assert result.interpretation.risk_level == RiskLevel.LOW
        assert result.interpretation.stage == "Low risk"

    def test_age_and_hypertension_score(self, calc: Any) -> None:
        result = calc.calculate(age_years=72, hypertension=True)

        assert result.value == 2
        assert result.interpretation.risk_level == RiskLevel.INTERMEDIATE
        assert result.calculation_details is not None
        assert result.calculation_details["point_assignments"]["age_70_or_older"] == 1
        assert result.calculation_details["point_assignments"]["hypertension"] == 1

    def test_prior_stroke_and_renal_failure_weight_two_points(self, calc: Any) -> None:
        result = calc.calculate(age_years=60, prior_stroke_or_tia=True, acute_renal_failure=True)

        assert result.value == 4
        assert result.interpretation.risk_level == RiskLevel.HIGH

    def test_very_high_risk(self, calc: Any) -> None:
        result = calc.calculate(
            age_years=80,
            prior_stroke_or_tia=True,
            acute_renal_failure=True,
            asa_class_4_or_5=True,
            urgent_or_emergency_surgery=True,
            hypertension=True,
        )

        assert result.value == 8
        assert result.interpretation.risk_level == RiskLevel.VERY_HIGH
        assert result.interpretation.stage == "Very high risk"

    def test_invalid_age_raises(self, calc: Any) -> None:
        with pytest.raises(ValueError, match="age_years"):
            calc.calculate(age_years=17)

    def test_metadata_and_references(self, calc: Any) -> None:
        meta = calc.metadata

        assert meta.tool_id == "stras_score"
        assert "Stroke after Surgery" in meta.name
        assert any(ref.pmid == "28051777" for ref in meta.references)
        assert any(ref.doi == "10.1097/ALN.0000000000001534" for ref in meta.references)
