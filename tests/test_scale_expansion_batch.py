from typing import Any

import pytest

from src.domain.services.calculators import (
    BradenScaleCalculator,
    GeriatricNutritionalRiskIndexCalculator,
    MiniCogCalculator,
    PHQ2Calculator,
    PalliativePrognosticIndexCalculator,
)
from src.infrastructure.mcp.server import MedicalCalculatorServer


class TestPHQ2Calculator:
    @pytest.fixture
    def calculator(self) -> Any:
        return PHQ2Calculator()

    def test_positive_screen_threshold(self, calculator: Any) -> None:
        result = calculator.calculate(interest_pleasure=2, feeling_down=1)

        assert result.value == 3
        assert result.interpretation.stage == "Positive Screen"
        assert any(ref.pmid == "15820844" for ref in result.references)

    def test_negative_screen(self, calculator: Any) -> None:
        result = calculator.calculate(interest_pleasure=1, feeling_down=1)

        assert result.value == 2
        assert result.interpretation.stage == "Negative Screen"


class TestMiniCogCalculator:
    @pytest.fixture
    def calculator(self) -> Any:
        return MiniCogCalculator()

    def test_positive_screen_with_poor_recall_and_abnormal_clock(self, calculator: Any) -> None:
        result = calculator.calculate(word_recall=2, clock_draw_normal=False)

        assert result.value == 2
        assert result.calculation_details is not None
        assert result.calculation_details["positive_screen"] is True
        assert result.interpretation.stage == "Positive Screen"
        assert any(ref.pmid == "11113982" for ref in result.references)

    def test_negative_screen_with_good_recall(self, calculator: Any) -> None:
        result = calculator.calculate(word_recall=3, clock_draw_normal=False)

        assert result.value == 3
        assert result.interpretation.stage == "Negative Screen"


class TestBradenScaleCalculator:
    @pytest.fixture
    def calculator(self) -> Any:
        return BradenScaleCalculator()

    def test_high_risk_profile(self, calculator: Any) -> None:
        result = calculator.calculate(
            sensory_perception=1,
            moisture=2,
            activity=1,
            mobility=1,
            nutrition=2,
            friction_shear=1,
        )

        assert result.value == 8
        assert result.interpretation.stage == "Very High Risk"
        assert any(ref.pmid == "3299278" for ref in result.references)


class TestGNRICalculator:
    @pytest.fixture
    def calculator(self) -> Any:
        return GeriatricNutritionalRiskIndexCalculator()

    def test_major_risk(self, calculator: Any) -> None:
        result = calculator.calculate(serum_albumin_g_l=28.0, current_weight_kg=45.0, ideal_weight_kg=65.0)

        assert result.value < 82
        assert result.interpretation.stage == "Major Risk"
        assert any(ref.pmid == "16210706" for ref in result.references)


class TestPalliativePrognosticIndexCalculator:
    @pytest.fixture
    def calculator(self) -> Any:
        return PalliativePrognosticIndexCalculator()

    def test_limited_prognosis(self, calculator: Any) -> None:
        result = calculator.calculate(
            pps_score=20,
            oral_intake="minimal",
            edema=True,
            dyspnea_at_rest=True,
            delirium=False,
        )

        assert result.value == 11.0
        assert result.interpretation.stage == "Very Limited Prognosis"
        assert any(ref.pmid == "10335930" for ref in result.references)


def test_registry_includes_batch_expansion_tools() -> None:
    tool_ids = {meta.low_level.tool_id for meta in MedicalCalculatorServer().registry.list_all()}

    assert "phq2" in tool_ids
    assert "mini_cog" in tool_ids
    assert "palliative_prognostic_index" in tool_ids
    assert len(tool_ids) == 151