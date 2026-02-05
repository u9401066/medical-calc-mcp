"""
Tests for Systemic Inflammatory Response Syndrome (SIRS) Criteria Calculator

Testing:
- SIRS criteria count
- Each criterion individually
- Clinical interpretation
- Edge cases

Reference:
    Bone RC, et al. Chest. 1992;101(6):1644-1655. PMID: 1303622
"""

from typing import Any

import pytest

from src.domain.services.calculators.sirs import SIRSCriteriaCalculator


class TestSIRSCriteriaCalculator:
    """Test SIRS Criteria Calculator"""

    @pytest.fixture
    def calculator(self) -> Any:
        return SIRSCriteriaCalculator()

    # === Metadata Tests ===

    def test_metadata(self, calculator: Any) -> None:
        """Test calculator metadata"""
        assert calculator.tool_id == "sirs_criteria"
        assert "SIRS" in calculator.name
        assert len(calculator.references) >= 2

    def test_references_have_pmids(self, calculator: Any) -> None:
        """Test that references include proper PMIDs"""
        pmids = [ref.pmid for ref in calculator.references if ref.pmid]
        assert "1303622" in pmids  # Bone 1992
        assert "26903338" in pmids  # Singer 2016 (Sepsis-3)

    # === Individual Criteria Tests ===

    def test_temperature_criterion_fever(self, calculator: Any) -> None:
        """Test temperature >38°C meets criterion"""
        result = calculator.calculate(temperature=38.5)
        assert result.value == 1
        assert "Temperature" in result.calculation_details["criteria_met"]

    def test_temperature_criterion_hypothermia(self, calculator: Any) -> None:
        """Test temperature <36°C meets criterion"""
        result = calculator.calculate(temperature=35.5)
        assert result.value == 1
        assert "Temperature" in result.calculation_details["criteria_met"]

    def test_temperature_normal(self, calculator: Any) -> None:
        """Test normal temperature does not meet criterion"""
        result = calculator.calculate(temperature=37.0)
        assert result.value == 0
        assert "Temperature" not in result.calculation_details["criteria_met"]

    def test_heart_rate_criterion(self, calculator: Any) -> None:
        """Test heart rate >90 meets criterion"""
        result = calculator.calculate(heart_rate=95)
        assert result.value == 1
        assert "Heart rate" in result.calculation_details["criteria_met"]

    def test_heart_rate_normal(self, calculator: Any) -> None:
        """Test normal heart rate does not meet criterion"""
        result = calculator.calculate(heart_rate=80)
        assert result.value == 0

    def test_respiratory_rate_criterion(self, calculator: Any) -> None:
        """Test respiratory rate >20 meets criterion"""
        result = calculator.calculate(respiratory_rate=24)
        assert result.value == 1
        assert "Respiratory" in result.calculation_details["criteria_met"]

    def test_paco2_criterion(self, calculator: Any) -> None:
        """Test PaCO2 <32 meets respiratory criterion"""
        result = calculator.calculate(paco2=28)
        assert result.value == 1
        assert "Respiratory" in result.calculation_details["criteria_met"]

    def test_respiratory_both_abnormal_counts_once(self, calculator: Any) -> None:
        """Test RR >20 AND PaCO2 <32 only counts as one criterion"""
        result = calculator.calculate(respiratory_rate=24, paco2=28)
        assert result.value == 1  # Not 2
        assert "Respiratory" in result.calculation_details["criteria_met"]

    def test_wbc_criterion_leukocytosis(self, calculator: Any) -> None:
        """Test WBC >12 meets criterion"""
        result = calculator.calculate(wbc=15.0)
        assert result.value == 1
        assert "WBC/Bands" in result.calculation_details["criteria_met"]

    def test_wbc_criterion_leukopenia(self, calculator: Any) -> None:
        """Test WBC <4 meets criterion"""
        result = calculator.calculate(wbc=3.0)
        assert result.value == 1
        assert "WBC/Bands" in result.calculation_details["criteria_met"]

    def test_bands_criterion(self, calculator: Any) -> None:
        """Test bands >10% meets criterion"""
        result = calculator.calculate(bands_percent=12.0)
        assert result.value == 1
        assert "WBC/Bands" in result.calculation_details["criteria_met"]

    def test_wbc_and_bands_abnormal_counts_once(self, calculator: Any) -> None:
        """Test both WBC abnormal AND bands >10% only counts as one criterion"""
        result = calculator.calculate(wbc=15.0, bands_percent=12.0)
        assert result.value == 1  # Not 2

    # === SIRS Positive/Negative Tests ===

    def test_sirs_negative_zero_criteria(self, calculator: Any) -> None:
        """Test 0/4 criteria = SIRS negative"""
        result = calculator.calculate(
            temperature=37.0,
            heart_rate=80,
            respiratory_rate=16,
            wbc=8.0,
        )
        assert result.value == 0
        assert result.calculation_details["sirs_positive"] is False
        assert "negative" in result.interpretation.summary.lower()

    def test_sirs_negative_one_criterion(self, calculator: Any) -> None:
        """Test 1/4 criteria = SIRS negative"""
        result = calculator.calculate(
            temperature=39.0,  # Only this meets criterion
            heart_rate=80,
            respiratory_rate=16,
            wbc=8.0,
        )
        assert result.value == 1
        assert result.calculation_details["sirs_positive"] is False
        assert "negative" in result.interpretation.summary.lower()

    def test_sirs_positive_two_criteria(self, calculator: Any) -> None:
        """Test 2/4 criteria = SIRS positive"""
        result = calculator.calculate(
            temperature=39.0,  # 1
            heart_rate=100,    # 2
        )
        assert result.value == 2
        assert result.calculation_details["sirs_positive"] is True
        assert "positive" in result.interpretation.summary.lower()

    def test_sirs_positive_three_criteria(self, calculator: Any) -> None:
        """Test 3/4 criteria = SIRS positive"""
        result = calculator.calculate(
            temperature=39.0,  # 1
            heart_rate=100,    # 2
            respiratory_rate=24,  # 3
        )
        assert result.value == 3
        assert result.calculation_details["sirs_positive"] is True

    def test_sirs_positive_four_criteria(self, calculator: Any) -> None:
        """Test 4/4 criteria = SIRS positive"""
        result = calculator.calculate(
            temperature=39.0,  # 1
            heart_rate=100,    # 2
            respiratory_rate=24,  # 3
            wbc=15.0,  # 4
        )
        assert result.value == 4
        assert result.calculation_details["sirs_positive"] is True

    # === Interpretation Tests ===

    def test_interpretation_severity_levels(self, calculator: Any) -> None:
        """Test severity increases with criteria count"""
        # 0 criteria - normal
        r0 = calculator.calculate(temperature=37.0)
        assert r0.interpretation.severity.value == "normal"

        # 1 criterion - mild
        r1 = calculator.calculate(temperature=39.0)
        assert r1.interpretation.severity.value == "mild"

        # 2 criteria - moderate
        r2 = calculator.calculate(temperature=39.0, heart_rate=100)
        assert r2.interpretation.severity.value == "moderate"

        # 3 criteria - severe
        r3 = calculator.calculate(temperature=39.0, heart_rate=100, respiratory_rate=24)
        assert r3.interpretation.severity.value == "severe"

        # 4 criteria - critical
        r4 = calculator.calculate(temperature=39.0, heart_rate=100, respiratory_rate=24, wbc=15.0)
        assert r4.interpretation.severity.value == "critical"

    def test_recommendations_present(self, calculator: Any) -> None:
        """Test recommendations are provided"""
        result = calculator.calculate(temperature=39.0, heart_rate=100)
        assert len(result.interpretation.recommendations) > 0

    def test_warnings_for_high_score(self, calculator: Any) -> None:
        """Test warnings are provided for high scores"""
        result = calculator.calculate(
            temperature=39.0,
            heart_rate=120,
            respiratory_rate=28,
            wbc=18.0,
        )
        assert result.value == 4
        assert len(result.interpretation.warnings) > 0

    # === Clinical Scenario Tests ===

    def test_scenario_sepsis_suspected(self, calculator: Any) -> None:
        """Test typical sepsis presentation"""
        result = calculator.calculate(
            temperature=38.8,
            heart_rate=110,
            respiratory_rate=22,
            wbc=16.5,
        )
        assert result.value == 4
        # Check that sepsis-related recommendations are present
        warnings_str = " ".join(result.interpretation.warnings)
        assert "septic" in warnings_str.lower() or "shock" in warnings_str.lower()

    def test_scenario_post_surgical_fever(self, calculator: Any) -> None:
        """Test post-surgical fever with mild tachycardia"""
        result = calculator.calculate(
            temperature=38.2,
            heart_rate=95,
            respiratory_rate=16,
            wbc=10.0,
        )
        assert result.value == 2
        assert result.calculation_details["sirs_positive"] is True

    def test_scenario_healthy_tachycardia(self, calculator: Any) -> None:
        """Test isolated tachycardia (anxiety, exercise)"""
        result = calculator.calculate(
            temperature=36.8,
            heart_rate=105,
            respiratory_rate=18,
            wbc=7.0,
        )
        assert result.value == 1
        assert result.calculation_details["sirs_positive"] is False

    def test_scenario_hyperventilation(self, calculator: Any) -> None:
        """Test hyperventilation with low PaCO2"""
        result = calculator.calculate(
            temperature=37.0,
            heart_rate=85,
            paco2=25,  # Hyperventilation
            wbc=8.0,
        )
        assert result.value == 1
        assert "Respiratory" in result.calculation_details["criteria_met"]

    def test_scenario_leukopenia(self, calculator: Any) -> None:
        """Test leukopenia (immunocompromised patient)"""
        result = calculator.calculate(
            temperature=35.2,  # Hypothermia
            heart_rate=88,
            wbc=2.5,  # Leukopenia
        )
        assert result.value == 2
        assert result.calculation_details["sirs_positive"] is True

    # === Edge Cases ===

    def test_boundary_temperature_high(self, calculator: Any) -> None:
        """Test exact boundary for high temperature"""
        # Exactly 38°C should NOT meet criterion
        result_38 = calculator.calculate(temperature=38.0)
        assert "Temperature" not in result_38.calculation_details["criteria_met"]

        # 38.01°C should meet criterion
        result_38_1 = calculator.calculate(temperature=38.1)
        assert "Temperature" in result_38_1.calculation_details["criteria_met"]

    def test_boundary_temperature_low(self, calculator: Any) -> None:
        """Test exact boundary for low temperature"""
        # Exactly 36°C should NOT meet criterion
        result_36 = calculator.calculate(temperature=36.0)
        assert "Temperature" not in result_36.calculation_details["criteria_met"]

        # 35.9°C should meet criterion
        result_35_9 = calculator.calculate(temperature=35.9)
        assert "Temperature" in result_35_9.calculation_details["criteria_met"]

    def test_boundary_heart_rate(self, calculator: Any) -> None:
        """Test exact boundary for heart rate"""
        # Exactly 90 should NOT meet criterion
        result_90 = calculator.calculate(heart_rate=90)
        assert "Heart rate" not in result_90.calculation_details["criteria_met"]

        # 91 should meet criterion
        result_91 = calculator.calculate(heart_rate=91)
        assert "Heart rate" in result_91.calculation_details["criteria_met"]

    def test_boundary_respiratory_rate(self, calculator: Any) -> None:
        """Test exact boundary for respiratory rate"""
        # Exactly 20 should NOT meet criterion
        result_20 = calculator.calculate(respiratory_rate=20)
        assert "Respiratory" not in result_20.calculation_details["criteria_met"]

        # 21 should meet criterion
        result_21 = calculator.calculate(respiratory_rate=21)
        assert "Respiratory" in result_21.calculation_details["criteria_met"]

    def test_boundary_wbc_high(self, calculator: Any) -> None:
        """Test exact boundary for high WBC"""
        # Exactly 12 should NOT meet criterion
        result_12 = calculator.calculate(wbc=12.0)
        assert "WBC/Bands" not in result_12.calculation_details["criteria_met"]

        # 12.1 should meet criterion
        result_12_1 = calculator.calculate(wbc=12.1)
        assert "WBC/Bands" in result_12_1.calculation_details["criteria_met"]

    def test_boundary_wbc_low(self, calculator: Any) -> None:
        """Test exact boundary for low WBC"""
        # Exactly 4 should NOT meet criterion
        result_4 = calculator.calculate(wbc=4.0)
        assert "WBC/Bands" not in result_4.calculation_details["criteria_met"]

        # 3.9 should meet criterion
        result_3_9 = calculator.calculate(wbc=3.9)
        assert "WBC/Bands" in result_3_9.calculation_details["criteria_met"]

    def test_partial_parameters(self, calculator: Any) -> None:
        """Test calculation with only some parameters"""
        result = calculator.calculate(temperature=39.0, heart_rate=100)
        assert result.value == 2
        # Should not have respiratory or WBC in details
        assert "Respiratory rate" not in result.calculation_details["parameter_details"]
        assert "WBC" not in result.calculation_details["parameter_details"]

    def test_all_parameters_normal(self, calculator: Any) -> None:
        """Test with all parameters provided but all normal"""
        result = calculator.calculate(
            temperature=37.0,
            heart_rate=75,
            respiratory_rate=14,
            paco2=40,
            wbc=7.5,
            bands_percent=3.0,
        )
        assert result.value == 0
        assert len(result.calculation_details["criteria_met"]) == 0
