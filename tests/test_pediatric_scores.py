"""
Tests for Pediatric Score Calculators

Tests for:
- APGAR Score (Newborn assessment)
- PEWS (Pediatric Early Warning Score)
- pSOFA (Pediatric SOFA)
- PIM3 (Pediatric Index of Mortality 3)
- Pediatric GCS (Age-adapted Glasgow Coma Scale)
"""

import pytest

from src.domain.services.calculators import (
    APGARScoreCalculator,
    PediatricGCSCalculator,
    PediatricSOFACalculator,
    PEWSCalculator,
    PIM3Calculator,
)


class TestAPGARScore:
    """Tests for APGAR Score Calculator."""

    def test_metadata(self) -> None:
        """Test APGAR metadata."""
        calc = APGARScoreCalculator()
        meta = calc.metadata
        assert meta.low_level.tool_id == "apgar_score"
        assert "newborn" in meta.low_level.purpose.lower()
        assert len(meta.references) >= 2

    def test_perfect_score(self) -> None:
        """Test perfect APGAR score (10)."""
        calc = APGARScoreCalculator()
        result = calc.calculate(
            appearance=2,
            pulse=2,
            grimace=2,
            activity=2,
            respiration=2,
            assessment_time="1_minute"
        )
        assert result.value is not None
        assert result.value == 10
        assert result.calculation_details is not None
        assert "Normal" in result.calculation_details["status"]

    def test_moderate_depression(self) -> None:
        """Test moderate depression (score 4-6)."""
        calc = APGARScoreCalculator()
        result = calc.calculate(
            appearance=1,
            pulse=2,
            grimace=1,
            activity=1,
            respiration=1,
            assessment_time="1_minute"
        )
        assert result.value is not None
        assert result.value == 6
        assert result.calculation_details is not None
        assert "Moderately Depressed" in result.calculation_details["status"]

    def test_severe_depression(self) -> None:
        """Test severe depression (score 0-3)."""
        calc = APGARScoreCalculator()
        result = calc.calculate(
            appearance=0,
            pulse=1,
            grimace=0,
            activity=0,
            respiration=0,
            assessment_time="5_minute"
        )
        assert result.value is not None
        assert result.value == 1
        assert result.calculation_details is not None
        assert "Severely Depressed" in result.calculation_details["status"]

    def test_invalid_score(self) -> None:
        """Test invalid score value raises error."""
        calc = APGARScoreCalculator()
        with pytest.raises(ValueError):
            calc.calculate(
                appearance=3,  # Invalid: max is 2
                pulse=2,
                grimace=2,
                activity=2,
                respiration=2
            )

    def test_invalid_time(self) -> None:
        """Test invalid assessment time raises error."""
        calc = APGARScoreCalculator()
        with pytest.raises(ValueError):
            calc.calculate(
                appearance=2,
                pulse=2,
                grimace=2,
                activity=2,
                respiration=2,
                assessment_time="3_minute"  # Invalid
            )


class TestPEWS:
    """Tests for Pediatric Early Warning Score."""

    def test_metadata(self) -> None:
        """Test PEWS metadata."""
        calc = PEWSCalculator()
        meta = calc.metadata
        assert meta.low_level.tool_id == "pews"
        assert "deterioration" in meta.low_level.purpose.lower()

    def test_low_risk(self) -> None:
        """Test low risk score (0-2)."""
        calc = PEWSCalculator()
        result = calc.calculate(
            behavior_score=0,
            cardiovascular_score=0,
            respiratory_score=0
        )
        assert result.value is not None
        assert result.value == 0
        assert result.calculation_details is not None
        assert result.calculation_details["risk_level"] == "Low Risk"

    def test_high_risk(self) -> None:
        """Test high risk score (≥5)."""
        calc = PEWSCalculator()
        result = calc.calculate(
            behavior_score=2,
            cardiovascular_score=2,
            respiratory_score=2
        )
        assert result.value is not None
        assert result.value == 6
        assert result.calculation_details is not None
        assert result.calculation_details["risk_level"] == "High Risk"

    def test_oxygen_bonus(self) -> None:
        """Test +2 for supplemental oxygen."""
        calc = PEWSCalculator()
        result = calc.calculate(
            behavior_score=1,
            cardiovascular_score=1,
            respiratory_score=1,
            supplemental_oxygen=True
        )
        assert result.value is not None
        assert result.value == 5  # 3 + 2 for O2

    def test_with_vital_signs(self) -> None:
        """Test with vital sign context."""
        calc = PEWSCalculator()
        result = calc.calculate(
            behavior_score=1,
            cardiovascular_score=2,
            respiratory_score=2,
            age_group="1-4y",
            heart_rate=160,  # Tachycardia for this age
            respiratory_rate=40,  # Tachypnea for this age
            spo2=92
        )
        assert result.value is not None
        assert result.value == 5
        # Should have vital sign concerns


class TestPediatricSOFA:
    """Tests for Pediatric SOFA (pSOFA)."""

    def test_metadata(self) -> None:
        """Test pSOFA metadata."""
        calc = PediatricSOFACalculator()
        meta = calc.metadata
        assert meta.low_level.tool_id == "pediatric_sofa"
        assert "organ dysfunction" in meta.low_level.purpose.lower()

    def test_normal_values(self) -> None:
        """Test with normal values (low score)."""
        calc = PediatricSOFACalculator()
        result = calc.calculate(
            age_group="5-12y",
            pao2_fio2_ratio=450,
            platelets=200,
            bilirubin=0.5,
            gcs_score=15,
            creatinine=0.5,
            map_value=75
        )
        assert result.value is not None
        assert result.value <= 2
        assert result.calculation_details is not None
        assert "<5%" in result.calculation_details["estimated_mortality"]

    def test_multi_organ_dysfunction(self) -> None:
        """Test multi-organ dysfunction (high score)."""
        calc = PediatricSOFACalculator()
        result = calc.calculate(
            age_group="1-2y",
            pao2_fio2_ratio=120,  # Severe hypoxemia
            platelets=40,  # Severe thrombocytopenia
            bilirubin=8.0,  # Elevated
            gcs_score=6,  # Impaired
            creatinine=2.0,  # Elevated for age
            vasopressor_type="epinephrine",
            vasopressor_dose=0.15,
            on_mechanical_ventilation=True
        )
        assert result.value is not None
        assert result.value >= 10
        # Multiple organs should be affected
        assert result.calculation_details is not None
        assert len(result.calculation_details.get("worst_organs", [])) >= 1

    def test_invalid_age_group(self) -> None:
        """Test invalid age group raises error."""
        calc = PediatricSOFACalculator()
        with pytest.raises(ValueError):
            calc.calculate(
                age_group="invalid",
                pao2_fio2_ratio=400,
                platelets=200,
                bilirubin=1.0,
                gcs_score=15,
                creatinine=0.5
            )


class TestPIM3:
    """Tests for Pediatric Index of Mortality 3."""

    def test_metadata(self) -> None:
        """Test PIM3 metadata."""
        calc = PIM3Calculator()
        meta = calc.metadata
        assert meta.low_level.tool_id == "pim3"
        assert "mortality" in meta.low_level.purpose.lower()

    def test_low_risk(self) -> None:
        """Test low risk patient."""
        calc = PIM3Calculator()
        result = calc.calculate(
            systolic_bp=100,
            pupillary_reaction="both_react",
            mechanical_ventilation=False,
            base_excess=0,
            elective_admission=True,
            recovery_post_procedure=True,
            low_risk_diagnosis=True
        )
        # Elective, post-procedure, low-risk dx should be low mortality
        assert result.value is not None
        assert result.value < 5  # Less than 5% predicted mortality
        assert result.calculation_details is not None
        assert result.calculation_details["risk_category"] in ["Low Risk", "Low-Moderate Risk"]

    def test_high_risk(self) -> None:
        """Test high risk patient."""
        calc = PIM3Calculator()
        result = calc.calculate(
            systolic_bp=50,  # Hypotension
            pupillary_reaction="both_fixed",  # Both fixed
            mechanical_ventilation=True,
            base_excess=-15,  # Severe acidosis
            very_high_risk_diagnosis=True
        )
        # Should be high predicted mortality
        assert result.value is not None
        assert result.value > 30
        assert result.calculation_details is not None
        assert "High" in result.calculation_details["risk_category"] or "Critical" in result.calculation_details["risk_category"]

    def test_invalid_pupil(self) -> None:
        """Test invalid pupillary reaction raises error."""
        calc = PIM3Calculator()
        with pytest.raises(ValueError):
            calc.calculate(
                systolic_bp=100,
                pupillary_reaction="invalid",
                mechanical_ventilation=False,
                base_excess=0
            )

    def test_multiple_dx_categories(self) -> None:
        """Test multiple diagnosis categories raises error."""
        calc = PIM3Calculator()
        with pytest.raises(ValueError):
            calc.calculate(
                systolic_bp=100,
                pupillary_reaction="both_react",
                mechanical_ventilation=False,
                base_excess=0,
                high_risk_diagnosis=True,
                low_risk_diagnosis=True  # Can't be both
            )


class TestPediatricGCS:
    """Tests for Pediatric Glasgow Coma Scale."""

    def test_metadata(self) -> None:
        """Test Pediatric GCS metadata."""
        calc = PediatricGCSCalculator()
        meta = calc.metadata
        assert meta.low_level.tool_id == "pediatric_gcs"
        assert "consciousness" in meta.low_level.purpose.lower()

    def test_normal_score(self) -> None:
        """Test normal GCS (15)."""
        calc = PediatricGCSCalculator()
        result = calc.calculate(
            eye_response=4,
            verbal_response=5,
            motor_response=6,
            age_group="child"
        )
        assert result.value is not None
        assert result.value == 15
        assert result.calculation_details is not None
        assert "Mild" in result.calculation_details["impairment_level"]

    def test_infant_verbal_scale(self) -> None:
        """Test infant verbal scale interpretation."""
        calc = PediatricGCSCalculator()
        result = calc.calculate(
            eye_response=4,
            verbal_response=5,  # Coos, babbles
            motor_response=6,
            age_group="infant"
        )
        assert result.value is not None
        assert result.value == 15
        assert result.calculation_details is not None
        assert "infant" in result.calculation_details["age_group"]

    def test_severe_impairment(self) -> None:
        """Test severe impairment (≤8)."""
        calc = PediatricGCSCalculator()
        result = calc.calculate(
            eye_response=1,
            verbal_response=2,
            motor_response=3,
            age_group="child"
        )
        assert result.value is not None
        assert result.value == 6
        assert result.calculation_details is not None
        assert "Severe" in result.calculation_details["impairment_level"]
        assert result.calculation_details is not None
        assert result.calculation_details["airway_concern"] is True

    def test_intubated_notation(self) -> None:
        """Test intubated patient notation."""
        calc = PediatricGCSCalculator()
        result = calc.calculate(
            eye_response=2,
            verbal_response=1,
            motor_response=4,
            age_group="child",
            intubated=True
        )
        assert result.calculation_details is not None
        assert "T" in result.calculation_details["gcs_notation"]
        assert result.calculation_details is not None
        assert result.calculation_details["intubated"] is True

    def test_invalid_motor(self) -> None:
        """Test invalid motor score raises error."""
        calc = PediatricGCSCalculator()
        with pytest.raises(ValueError):
            calc.calculate(
                eye_response=4,
                verbal_response=5,
                motor_response=7,  # Invalid: max is 6
                age_group="child"
            )


class TestIntegration:
    """Integration tests for pediatric calculators."""

    def test_all_calculators_have_metadata(self) -> None:
        """All pediatric score calculators should have complete metadata."""
        calculators = [
            APGARScoreCalculator(),
            PEWSCalculator(),
            PediatricSOFACalculator(),
            PIM3Calculator(),
            PediatricGCSCalculator(),
        ]

        for calc in calculators:
            meta = calc.metadata
            assert meta.low_level.tool_id is not None
            assert meta.low_level.name is not None
            assert meta.low_level.purpose is not None
            assert len(meta.references) >= 1

    def test_all_results_have_next_step(self) -> None:
        """All results should include next_step guidance."""
        # APGAR
        apgar = APGARScoreCalculator()
        result = apgar.calculate(2, 2, 2, 2, 2)
        assert result.calculation_details is not None
        assert "next_step" in result.calculation_details

        # PEWS
        pews = PEWSCalculator()
        result = pews.calculate(0, 0, 0)
        assert result.calculation_details is not None
        assert "next_step" in result.calculation_details

        # pSOFA
        psofa = PediatricSOFACalculator()
        result = psofa.calculate("5-12y", 400, 200, 0.5, 15, 0.5)
        assert result.calculation_details is not None
        assert "next_step" in result.calculation_details

        # Pediatric GCS
        pgcs = PediatricGCSCalculator()
        result = pgcs.calculate(4, 5, 6)
        assert result.calculation_details is not None
        assert "next_step" in result.calculation_details
