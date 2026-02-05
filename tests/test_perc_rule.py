"""
Tests for PERC Rule (Pulmonary Embolism Rule-out Criteria) Calculator

Reference:
    Kline JA, Mitchell AM, Kabrhel C, Richman PB, Courtney DM.
    Clinical criteria to prevent unnecessary diagnostic testing in emergency
    department patients with suspected pulmonary embolism.
    J Thromb Haemost. 2004;2(8):1247-1255. PMID: 15304025.

    Kline JA, Courtney DM, Kabrhel C, et al.
    Prospective multicenter evaluation of the pulmonary embolism rule-out criteria.
    J Thromb Haemost. 2008;6(5):772-780. PMID: 18318689.
"""

import pytest

from src.domain.services.calculators.perc_rule import PERCRuleCalculator
from src.domain.value_objects.interpretation import RiskLevel, Severity


@pytest.fixture
def calculator() -> PERCRuleCalculator:
    """Provide a PERC Rule calculator instance."""
    return PERCRuleCalculator()


class TestPERCRuleBasicCriteria:
    """Test individual PERC criteria."""

    def test_all_criteria_absent_perc_negative(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """All criteria absent = PERC-negative."""
        result = calculator.calculate(
            age_50_or_older=False,
            heart_rate_100_or_higher=False,
            o2_sat_below_95=False,
            unilateral_leg_swelling=False,
            hemoptysis=False,
            recent_surgery_trauma=False,
            prior_pe_dvt=False,
            hormone_use=False,
        )
        assert result.value == 0
        assert result.calculation_details["perc_negative"] is True
        assert "PERC-Negative" in result.interpretation.summary
        assert result.interpretation.risk_level == RiskLevel.VERY_LOW

    def test_default_parameters_perc_negative(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """Default parameters (all False) = PERC-negative."""
        result = calculator.calculate()
        assert result.value == 0
        assert result.calculation_details["perc_negative"] is True

    def test_only_age_criterion_perc_positive(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """Age ≥50 alone = PERC-positive (1 criterion)."""
        result = calculator.calculate(age_50_or_older=True)
        assert result.value == 1
        assert result.calculation_details["perc_negative"] is False
        assert "PERC-Positive" in result.interpretation.summary
        assert "Age ≥50 years" in result.calculation_details["positive_criteria"]

    def test_only_heart_rate_criterion(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """HR ≥100 alone = PERC-positive."""
        result = calculator.calculate(heart_rate_100_or_higher=True)
        assert result.value == 1
        assert result.calculation_details["perc_negative"] is False
        assert "Heart rate ≥100 bpm" in result.calculation_details["positive_criteria"]

    def test_only_o2_saturation_criterion(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """O2 sat <95% alone = PERC-positive."""
        result = calculator.calculate(o2_sat_below_95=True)
        assert result.value == 1
        assert result.calculation_details["perc_negative"] is False
        assert "O2 saturation <95%" in result.calculation_details["positive_criteria"]

    def test_only_leg_swelling_criterion(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """Unilateral leg swelling alone = PERC-positive."""
        result = calculator.calculate(unilateral_leg_swelling=True)
        assert result.value == 1
        assert "Unilateral leg swelling" in result.calculation_details["positive_criteria"]

    def test_only_hemoptysis_criterion(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """Hemoptysis alone = PERC-positive."""
        result = calculator.calculate(hemoptysis=True)
        assert result.value == 1
        assert "Hemoptysis" in result.calculation_details["positive_criteria"]

    def test_only_recent_surgery_criterion(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """Recent surgery/trauma alone = PERC-positive."""
        result = calculator.calculate(recent_surgery_trauma=True)
        assert result.value == 1
        assert "Recent surgery/trauma (≤4 weeks)" in result.calculation_details["positive_criteria"]

    def test_only_prior_pe_dvt_criterion(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """Prior PE/DVT alone = PERC-positive."""
        result = calculator.calculate(prior_pe_dvt=True)
        assert result.value == 1
        assert "Prior PE or DVT" in result.calculation_details["positive_criteria"]

    def test_only_hormone_use_criterion(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """Hormone use alone = PERC-positive."""
        result = calculator.calculate(hormone_use=True)
        assert result.value == 1
        assert "Hormone use (OCP/HRT)" in result.calculation_details["positive_criteria"]


class TestPERCRuleMultipleCriteria:
    """Test combinations of PERC criteria."""

    def test_two_criteria_positive(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """Two criteria present."""
        result = calculator.calculate(
            age_50_or_older=True,
            heart_rate_100_or_higher=True,
        )
        assert result.value == 2
        assert result.calculation_details["perc_negative"] is False
        assert len(result.calculation_details["positive_criteria"]) == 2
        assert result.interpretation.severity == Severity.MILD

    def test_three_criteria_positive(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """Three criteria = moderate severity."""
        result = calculator.calculate(
            age_50_or_older=True,
            heart_rate_100_or_higher=True,
            o2_sat_below_95=True,
        )
        assert result.value == 3
        assert result.interpretation.severity == Severity.MODERATE
        assert result.interpretation.risk_level == RiskLevel.INTERMEDIATE

    def test_four_criteria_positive(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """Four criteria present."""
        result = calculator.calculate(
            age_50_or_older=True,
            heart_rate_100_or_higher=True,
            o2_sat_below_95=True,
            unilateral_leg_swelling=True,
        )
        assert result.value == 4
        assert result.interpretation.severity == Severity.MODERATE

    def test_five_or_more_criteria_high_severity(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """Five+ criteria = severe with high risk."""
        result = calculator.calculate(
            age_50_or_older=True,
            heart_rate_100_or_higher=True,
            o2_sat_below_95=True,
            unilateral_leg_swelling=True,
            hemoptysis=True,
        )
        assert result.value == 5
        assert result.interpretation.severity == Severity.SEVERE
        assert result.interpretation.risk_level == RiskLevel.HIGH

    def test_all_eight_criteria_positive(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """All 8 criteria present = maximum risk."""
        result = calculator.calculate(
            age_50_or_older=True,
            heart_rate_100_or_higher=True,
            o2_sat_below_95=True,
            unilateral_leg_swelling=True,
            hemoptysis=True,
            recent_surgery_trauma=True,
            prior_pe_dvt=True,
            hormone_use=True,
        )
        assert result.value == 8
        assert result.calculation_details["perc_negative"] is False
        assert len(result.calculation_details["positive_criteria"]) == 8
        assert result.interpretation.risk_level == RiskLevel.HIGH


class TestPERCRuleRecommendations:
    """Test PERC Rule recommendations."""

    def test_perc_negative_no_d_dimer_needed(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """PERC-negative: no D-dimer needed."""
        result = calculator.calculate()  # All criteria absent
        recommendations = result.interpretation.recommendations
        assert any("No D-dimer" in r for r in recommendations)
        assert any("No CT" in r for r in recommendations)

    def test_perc_positive_d_dimer_recommended(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """PERC-positive: D-dimer recommended."""
        result = calculator.calculate(age_50_or_older=True)
        recommendations = result.interpretation.recommendations
        assert any("D-dimer" in r for r in recommendations)

    def test_prior_pe_dvt_imaging_threshold_recommendation(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """Prior PE/DVT: lower imaging threshold."""
        result = calculator.calculate(prior_pe_dvt=True)
        recommendations = result.interpretation.recommendations
        assert any("lower threshold" in r.lower() for r in recommendations)

    def test_low_o2_oxygenation_recommendation(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """Low O2 sat: oxygenation recommendation."""
        result = calculator.calculate(o2_sat_below_95=True)
        recommendations = result.interpretation.recommendations
        assert any("oxygen" in r.lower() for r in recommendations)

    def test_leg_swelling_ultrasound_recommendation(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """Leg swelling: US recommendation."""
        result = calculator.calculate(unilateral_leg_swelling=True)
        recommendations = result.interpretation.recommendations
        assert any("ultrasound" in r.lower() for r in recommendations)


class TestPERCRuleNextSteps:
    """Test PERC Rule next steps."""

    def test_perc_negative_alternative_diagnoses(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """PERC-negative: consider alternative diagnoses."""
        result = calculator.calculate()
        next_steps = result.interpretation.next_steps
        assert any("alternative" in s.lower() for s in next_steps)

    def test_perc_positive_d_dimer_next_step(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """PERC-positive: D-dimer as next step."""
        result = calculator.calculate(heart_rate_100_or_higher=True)
        next_steps = result.interpretation.next_steps
        assert any("D-dimer" in s for s in next_steps)

    def test_perc_positive_wells_recommendation(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """PERC-positive: Wells PE Score recommendation."""
        result = calculator.calculate(hormone_use=True)
        next_steps = result.interpretation.next_steps
        assert any("Wells" in s for s in next_steps)


class TestPERCRuleWarnings:
    """Test PERC Rule warnings."""

    def test_perc_negative_low_pretest_warning(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """PERC-negative: warns about low pretest requirement."""
        result = calculator.calculate()
        warnings = result.interpretation.warnings
        assert any("low" in w.lower() and "pretest" in w.lower() for w in warnings)

    def test_multiple_criteria_high_suspicion_warning(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """Multiple criteria: warn about high suspicion."""
        result = calculator.calculate(
            age_50_or_older=True,
            heart_rate_100_or_higher=True,
            o2_sat_below_95=True,
        )
        warnings = result.interpretation.warnings
        assert len(warnings) > 0
        assert any("suspicion" in w.lower() for w in warnings)


class TestPERCRuleClinicalScenarios:
    """Test realistic clinical scenarios."""

    def test_scenario_young_healthy_patient(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """Young healthy patient with atypical chest pain."""
        result = calculator.calculate(
            age_50_or_older=False,  # 28 years old
            heart_rate_100_or_higher=False,  # HR 72
            o2_sat_below_95=False,  # SpO2 99%
            unilateral_leg_swelling=False,
            hemoptysis=False,
            recent_surgery_trauma=False,
            prior_pe_dvt=False,
            hormone_use=False,
        )
        assert result.value == 0
        assert result.calculation_details["perc_negative"] is True
        # PE can be ruled out without D-dimer

    def test_scenario_elderly_with_tachycardia(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """Elderly patient with tachycardia - needs workup."""
        result = calculator.calculate(
            age_50_or_older=True,  # 72 years old
            heart_rate_100_or_higher=True,  # HR 110
            o2_sat_below_95=False,  # SpO2 97%
            unilateral_leg_swelling=False,
            hemoptysis=False,
            recent_surgery_trauma=False,
            prior_pe_dvt=False,
            hormone_use=False,
        )
        assert result.value == 2
        assert result.calculation_details["perc_negative"] is False

    def test_scenario_postop_patient(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """Post-operative patient - automatic PERC-positive."""
        result = calculator.calculate(
            age_50_or_older=True,
            heart_rate_100_or_higher=False,
            o2_sat_below_95=False,
            unilateral_leg_swelling=False,
            hemoptysis=False,
            recent_surgery_trauma=True,  # 2 weeks post hip replacement
            prior_pe_dvt=False,
            hormone_use=False,
        )
        assert result.value == 2
        assert result.calculation_details["perc_negative"] is False

    def test_scenario_woman_on_ocp(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """Young woman on oral contraceptives."""
        result = calculator.calculate(
            age_50_or_older=False,  # 25 years old
            heart_rate_100_or_higher=False,
            o2_sat_below_95=False,
            unilateral_leg_swelling=False,
            hemoptysis=False,
            recent_surgery_trauma=False,
            prior_pe_dvt=False,
            hormone_use=True,  # On OCP
        )
        assert result.value == 1
        assert result.calculation_details["perc_negative"] is False
        # Single criterion makes PERC-positive

    def test_scenario_prior_dvt(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """Patient with prior DVT history."""
        result = calculator.calculate(
            age_50_or_older=True,  # 55 years old
            heart_rate_100_or_higher=True,  # HR 105
            o2_sat_below_95=False,
            unilateral_leg_swelling=True,  # Left leg swelling
            hemoptysis=False,
            recent_surgery_trauma=False,
            prior_pe_dvt=True,  # DVT 3 years ago
            hormone_use=False,
        )
        assert result.value == 4
        assert result.calculation_details["perc_negative"] is False
        # Multiple high-risk features including prior VTE

    def test_scenario_classic_pe_presentation(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """Classic PE presentation - many criteria positive."""
        result = calculator.calculate(
            age_50_or_older=True,  # 62 years old
            heart_rate_100_or_higher=True,  # HR 120
            o2_sat_below_95=True,  # SpO2 88%
            unilateral_leg_swelling=True,
            hemoptysis=True,  # Coughing up blood
            recent_surgery_trauma=False,
            prior_pe_dvt=False,
            hormone_use=False,
        )
        assert result.value == 5
        assert result.interpretation.severity == Severity.SEVERE
        assert result.interpretation.risk_level == RiskLevel.HIGH

    def test_scenario_hypoxic_patient(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """Hypoxic patient - oxygenation recommendation."""
        result = calculator.calculate(
            age_50_or_older=False,
            heart_rate_100_or_higher=True,
            o2_sat_below_95=True,  # SpO2 90%
            unilateral_leg_swelling=False,
            hemoptysis=False,
            recent_surgery_trauma=False,
            prior_pe_dvt=False,
            hormone_use=False,
        )
        assert result.value == 2
        recommendations = result.interpretation.recommendations
        assert any("oxygen" in r.lower() for r in recommendations)


class TestPERCRuleMetadata:
    """Test PERC Rule metadata and references."""

    def test_tool_id(self, calculator: PERCRuleCalculator) -> None:
        """Test calculator tool_id."""
        assert calculator.tool_id == "perc_rule"

    def test_metadata_name(self, calculator: PERCRuleCalculator) -> None:
        """Test metadata name."""
        assert "PERC" in calculator.metadata.low_level.name

    def test_metadata_specialties(self, calculator: PERCRuleCalculator) -> None:
        """Test specialties include emergency medicine."""
        specialties = calculator.metadata.high_level.specialties
        specialty_values = [s.value for s in specialties]
        assert "emergency_medicine" in specialty_values
        assert "pulmonology" in specialty_values

    def test_references_exist(self, calculator: PERCRuleCalculator) -> None:
        """Test that references are present."""
        refs = calculator.references
        assert len(refs) >= 2
        pmids = [ref.pmid for ref in refs]
        assert "15304025" in pmids  # Original PERC paper
        assert "18318689" in pmids  # Validation paper

    def test_result_has_references(self, calculator: PERCRuleCalculator) -> None:
        """Test result includes references."""
        result = calculator.calculate()
        assert len(result.references) >= 2

    def test_formula_description(self, calculator: PERCRuleCalculator) -> None:
        """Test formula is described."""
        result = calculator.calculate()
        assert "PERC-negative" in result.formula_used
        assert "PERC-positive" in result.formula_used


class TestPERCRuleEdgeCases:
    """Test edge cases for PERC Rule."""

    def test_explicit_false_values(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """All criteria explicitly set to False."""
        result = calculator.calculate(
            age_50_or_older=False,
            heart_rate_100_or_higher=False,
            o2_sat_below_95=False,
            unilateral_leg_swelling=False,
            hemoptysis=False,
            recent_surgery_trauma=False,
            prior_pe_dvt=False,
            hormone_use=False,
        )
        assert result.value == 0
        assert result.calculation_details["perc_negative"] is True

    def test_calculation_details_structure(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """Test calculation_details contains expected fields."""
        result = calculator.calculate(age_50_or_older=True)
        details = result.calculation_details
        assert "criteria_evaluated" in details
        assert "positive_criteria_count" in details
        assert "positive_criteria" in details
        assert "perc_negative" in details
        assert "result" in details

    def test_criteria_evaluated_dict(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """Test criteria_evaluated is a proper dict."""
        result = calculator.calculate(
            age_50_or_older=True,
            heart_rate_100_or_higher=False,
        )
        criteria = result.calculation_details["criteria_evaluated"]
        assert isinstance(criteria, dict)
        assert criteria["Age ≥50 years"] is True
        assert criteria["Heart rate ≥100 bpm"] is False

    def test_result_string_format(
        self, calculator: PERCRuleCalculator
    ) -> None:
        """Test result string formatting."""
        result_negative = calculator.calculate()
        assert "ruled out" in result_negative.calculation_details["result"].lower()

        result_positive = calculator.calculate(age_50_or_older=True)
        assert "testing needed" in result_positive.calculation_details["result"].lower()
