from typing import Any

import pytest

from src.domain.services.calculators import EpworthSleepinessScaleCalculator, PalliativePerformanceScaleCalculator


class TestEpworthSleepinessScaleCalculator:
    @pytest.fixture
    def calculator(self) -> Any:
        return EpworthSleepinessScaleCalculator()

    def test_metadata(self, calculator: Any) -> None:
        assert calculator.tool_id == "epworth_sleepiness_scale"
        assert "epworth" in calculator.name.lower()

    def test_low_normal_score(self, calculator: Any) -> None:
        result = calculator.calculate(0, 1, 0, 1, 1, 0, 1, 0)

        assert result.value == 4
        assert result.interpretation.summary is not None
        assert "normal" in result.interpretation.summary.lower()
        assert result.references is not None
        assert any(ref.pmid == "1798888" for ref in result.references)

    def test_abnormal_sleepiness_threshold(self, calculator: Any) -> None:
        result = calculator.calculate(2, 2, 1, 2, 2, 1, 1, 1)

        assert result.value == 12
        assert result.interpretation.summary is not None
        assert "mild excessive" in result.interpretation.summary.lower()
        assert result.calculation_details is not None
        assert result.calculation_details["sleepiness_threshold"] == 11

    def test_severe_sleepiness(self, calculator: Any) -> None:
        result = calculator.calculate(3, 3, 2, 3, 3, 2, 2, 2)

        assert result.value == 20
        assert result.interpretation.summary is not None
        assert "severe" in result.interpretation.summary.lower()

    def test_invalid_item_score_raises(self, calculator: Any) -> None:
        with pytest.raises(ValueError):
            calculator.calculate(4, 0, 0, 0, 0, 0, 0, 0)


class TestPalliativePerformanceScaleCalculator:
    @pytest.fixture
    def calculator(self) -> Any:
        return PalliativePerformanceScaleCalculator()

    def test_metadata(self, calculator: Any) -> None:
        assert calculator.tool_id == "palliative_performance_scale"
        assert "palliative" in calculator.name.lower()

    def test_preserved_function(self, calculator: Any) -> None:
        result = calculator.calculate(80)

        assert result.value == 80
        assert result.interpretation.summary is not None
        assert "preserved" in result.interpretation.summary.lower()
        assert result.references is not None
        assert any(ref.pmid == "17040144" for ref in result.references)

    def test_moderate_impairment(self, calculator: Any) -> None:
        result = calculator.calculate(50)

        assert result.value == 50
        assert result.interpretation.summary is not None
        assert "moderate functional impairment" in result.interpretation.summary.lower()

    def test_severe_impairment(self, calculator: Any) -> None:
        result = calculator.calculate(20)

        assert result.value == 20
        assert result.interpretation.summary is not None
        assert "severe functional impairment" in result.interpretation.summary.lower()

    def test_invalid_increment_raises(self, calculator: Any) -> None:
        with pytest.raises(ValueError):
            calculator.calculate(55)
