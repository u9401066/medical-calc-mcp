"""
Tests for Extended Neurology Calculators (Phase 14)

Tests for:
- Hunt & Hess Scale (SAH grading)
- Fisher Grade / Modified Fisher Scale (vasospasm prediction)
- FOUR Score (coma evaluation)
- ICH Score (intracerebral hemorrhage prognosis)
"""

import pytest
from src.domain.services.calculators import (
    HuntHessCalculator,
    FisherGradeCalculator,
    FourScoreCalculator,
    IchScoreCalculator,
)


class TestHuntHessCalculator:
    """Tests for Hunt & Hess Scale"""

    @pytest.fixture
    def calculator(self):
        return HuntHessCalculator()

    def test_metadata(self, calculator):
        """Test calculator metadata"""
        assert calculator.tool_id == "hunt_hess"
        assert "Hunt" in calculator.name
        assert "Hess" in calculator.name
        assert len(calculator.references) >= 1
        assert calculator.references[0].pmid == "5635959"
        assert calculator.references[0].year == 1968

    @pytest.mark.parametrize("grade,expected_severity", [
        (1, "MILD"),
        (2, "MILD"),
        (3, "MODERATE"),
        (4, "SEVERE"),
        (5, "CRITICAL"),
    ])
    def test_grade_severity_mapping(self, calculator, grade, expected_severity):
        """Test grade to severity mapping"""
        result = calculator.calculate(grade=grade)
        assert result.value == grade
        assert result.interpretation.severity.name == expected_severity

    def test_grade_1_excellent_prognosis(self, calculator):
        """Test Grade I - minimal symptoms"""
        result = calculator.calculate(grade=1)
        assert result.value == 1
        assert "I" in result.calculation_details["grade_roman"]
        assert "Asymptomatic" in result.calculation_details["description"]
        # Check recommendations tuple instead of single recommendation
        assert any("surgery" in rec.lower() for rec in result.interpretation.recommendations)

    def test_grade_3_moderate(self, calculator):
        """Test Grade III - drowsiness/confusion"""
        result = calculator.calculate(grade=3)
        assert result.value == 3
        assert result.calculation_details["grade_roman"] == "III"
        assert "Drowsiness" in result.calculation_details["description"]

    def test_grade_5_critical(self, calculator):
        """Test Grade V - moribund"""
        result = calculator.calculate(grade=5)
        assert result.value == 5
        assert result.calculation_details["grade_roman"] == "V"
        assert "coma" in result.calculation_details["description"].lower()
        # Check recommendations tuple
        assert any("delay" in rec.lower() or "defer" in rec.lower() for rec in result.interpretation.recommendations)

    def test_invalid_grade(self, calculator):
        """Test invalid grade raises error"""
        with pytest.raises(ValueError):
            calculator.calculate(grade=0)
        with pytest.raises(ValueError):
            calculator.calculate(grade=6)


class TestFisherGradeCalculator:
    """Tests for Fisher Grade / Modified Fisher Scale"""

    @pytest.fixture
    def calculator(self):
        return FisherGradeCalculator()

    def test_metadata(self, calculator):
        """Test calculator metadata"""
        assert calculator.tool_id == "fisher_grade"
        assert "Fisher" in calculator.name
        assert len(calculator.references) >= 2
        # Original Fisher 1980
        assert any(r.pmid == "7354892" for r in calculator.references)
        # Modified Fisher 2006
        assert any(r.pmid == "16823296" for r in calculator.references)

    def test_modified_fisher_grade_0_no_blood(self, calculator):
        """Test Modified Fisher Grade 0 - no SAH"""
        result = calculator.calculate(thick_sah=False, no_blood=True, use_modified=True)
        assert result.value == 0
        assert result.calculation_details["scale"] == "Modified Fisher Scale"
        assert "No" in result.calculation_details["ct_findings"]

    def test_modified_fisher_grade_1_thin_no_ivh(self, calculator):
        """Test Modified Fisher Grade 1 - thin SAH, no IVH"""
        result = calculator.calculate(thick_sah=False, ivh_present=False, use_modified=True)
        assert result.value == 1

    def test_modified_fisher_grade_2_thin_with_ivh(self, calculator):
        """Test Modified Fisher Grade 2 - thin SAH with IVH"""
        result = calculator.calculate(thick_sah=False, ivh_present=True, use_modified=True)
        assert result.value == 2
        # IVH noted in CT findings or interpretation
        assert "IVH" in str(result.calculation_details) or "IVH" in result.interpretation.summary

    def test_modified_fisher_grade_3_thick_no_ivh(self, calculator):
        """Test Modified Fisher Grade 3 - thick SAH, no IVH"""
        result = calculator.calculate(thick_sah=True, ivh_present=False, use_modified=True)
        assert result.value == 3
        assert "Thick" in result.calculation_details["ct_findings"]

    def test_modified_fisher_grade_4_thick_with_ivh(self, calculator):
        """Test Modified Fisher Grade 4 - thick SAH with IVH"""
        result = calculator.calculate(thick_sah=True, ivh_present=True, use_modified=True)
        assert result.value == 4
        assert result.interpretation.severity.name == "CRITICAL"

    def test_original_fisher_scale(self, calculator):
        """Test Original Fisher Scale grading"""
        # Grade 1 - no blood
        result = calculator.calculate(thick_sah=False, no_blood=True, use_modified=False)
        assert result.value == 1
        assert result.calculation_details["scale"] == "Original Fisher Scale"

        # Grade 2 - thin SAH
        result = calculator.calculate(thick_sah=False, ivh_present=False, use_modified=False)
        assert result.value == 2

        # Grade 3 - thick SAH
        result = calculator.calculate(thick_sah=True, ivh_present=False, use_modified=False)
        assert result.value == 3

    def test_vasospasm_risk_increases_with_grade(self, calculator):
        """Test vasospasm risk increases with higher grades"""
        grade_1 = calculator.calculate(thick_sah=False, ivh_present=False, use_modified=True)
        grade_4 = calculator.calculate(thick_sah=True, ivh_present=True, use_modified=True)
        
        # Grade 4 should have higher vasospasm risk
        assert grade_4.value > grade_1.value
        assert "symptomatic_vasospasm" in grade_4.calculation_details["vasospasm_risk"]


class TestFourScoreCalculator:
    """Tests for FOUR Score (Full Outline of UnResponsiveness)"""

    @pytest.fixture
    def calculator(self):
        return FourScoreCalculator()

    def test_metadata(self, calculator):
        """Test calculator metadata"""
        assert calculator.tool_id == "four_score"
        assert "FOUR" in calculator.name
        assert len(calculator.references) >= 1
        assert calculator.references[0].pmid == "16178024"
        assert calculator.references[0].year == 2005

    def test_maximum_score_16(self, calculator):
        """Test maximum FOUR Score = 16 (fully responsive)"""
        result = calculator.calculate(
            eye_response=4,
            motor_response=4,
            brainstem_reflexes=4,
            respiration=4
        )
        assert result.value == 16
        assert result.calculation_details["notation"] == "E4M4B4R4"
        # Normal severity for fully responsive
        assert result.interpretation.severity.name in ["NORMAL", "MILD"]

    def test_minimum_score_0_brain_death(self, calculator):
        """Test FOUR Score = 0 (possible brain death)"""
        result = calculator.calculate(
            eye_response=0,
            motor_response=0,
            brainstem_reflexes=0,
            respiration=0
        )
        assert result.value == 0
        assert result.calculation_details["notation"] == "E0M0B0R0"
        assert result.calculation_details["brain_death_screening"] is True
        assert result.interpretation.severity.name == "CRITICAL"
        assert "brain death" in result.interpretation.summary.lower()

    def test_severe_brainstem_dysfunction(self, calculator):
        """Test severe brainstem dysfunction"""
        result = calculator.calculate(
            eye_response=2,
            motor_response=2,
            brainstem_reflexes=1,  # Absent pupil AND corneal
            respiration=1
        )
        assert result.value == 6
        # Brainstem dysfunction noted in summary or detail
        assert "brainstem" in result.interpretation.summary.lower() or "brainstem" in result.interpretation.detail.lower()

    def test_moderate_impairment(self, calculator):
        """Test moderate impairment"""
        result = calculator.calculate(
            eye_response=3,
            motor_response=3,
            brainstem_reflexes=4,
            respiration=2
        )
        assert result.value == 12
        assert result.interpretation.severity.name in ["MODERATE", "HIGH"]

    def test_component_descriptions(self, calculator):
        """Test component descriptions are provided"""
        result = calculator.calculate(
            eye_response=2,
            motor_response=3,
            brainstem_reflexes=4,
            respiration=1
        )
        details = result.calculation_details["components"]
        assert "description" in details["eye_response"]
        assert "description" in details["motor_response"]
        assert "description" in details["brainstem_reflexes"]
        assert "description" in details["respiration"]

    @pytest.mark.parametrize("component,value", [
        ("eye_response", 5),
        ("motor_response", -1),
        ("brainstem_reflexes", 6),
        ("respiration", 10),
    ])
    def test_invalid_inputs(self, calculator, component, value):
        """Test invalid input values raise errors"""
        valid_params = {
            "eye_response": 2,
            "motor_response": 2,
            "brainstem_reflexes": 2,
            "respiration": 2
        }
        valid_params[component] = value
        with pytest.raises(ValueError):
            calculator.calculate(**valid_params)


class TestIchScoreCalculator:
    """Tests for ICH Score (Intracerebral Hemorrhage Score)"""

    @pytest.fixture
    def calculator(self):
        return IchScoreCalculator()

    def test_metadata(self, calculator):
        """Test calculator metadata"""
        assert calculator.tool_id == "ich_score"
        assert "ICH" in calculator.name
        assert len(calculator.references) >= 1
        assert calculator.references[0].pmid == "11283388"
        assert calculator.references[0].year == 2001

    def test_score_0_excellent_prognosis(self, calculator):
        """Test ICH Score 0 - excellent prognosis (0% mortality)"""
        result = calculator.calculate(
            gcs_score=15,
            ich_volume_ml=10,
            ivh_present=False,
            infratentorial=False,
            age=50
        )
        assert result.value == 0
        assert result.calculation_details["mortality_30_day"] == "0%"
        # Normal or Mild severity for excellent prognosis
        assert result.interpretation.severity.name in ["NORMAL", "MILD"]

    def test_score_6_maximum(self, calculator):
        """Test ICH Score 6 - maximum score"""
        result = calculator.calculate(
            gcs_score=3,      # 2 points
            ich_volume_ml=50, # 1 point (≥30mL)
            ivh_present=True, # 1 point
            infratentorial=True, # 1 point
            age=85            # 1 point (≥80)
        )
        assert result.value == 6
        assert "100%" in result.calculation_details["mortality_30_day"]
        assert result.interpretation.severity.name == "CRITICAL"

    def test_gcs_scoring(self, calculator):
        """Test GCS component scoring"""
        # GCS 3-4 = 2 points
        result = calculator.calculate(
            gcs_score=4, ich_volume_ml=10, ivh_present=False,
            infratentorial=False, age=50
        )
        assert result.calculation_details["components"]["gcs"]["points"] == 2

        # GCS 5-12 = 1 point
        result = calculator.calculate(
            gcs_score=10, ich_volume_ml=10, ivh_present=False,
            infratentorial=False, age=50
        )
        assert result.calculation_details["components"]["gcs"]["points"] == 1

        # GCS 13-15 = 0 points
        result = calculator.calculate(
            gcs_score=14, ich_volume_ml=10, ivh_present=False,
            infratentorial=False, age=50
        )
        assert result.calculation_details["components"]["gcs"]["points"] == 0

    def test_volume_threshold(self, calculator):
        """Test ICH volume threshold at 30mL"""
        # Below threshold
        result = calculator.calculate(
            gcs_score=15, ich_volume_ml=29.9, ivh_present=False,
            infratentorial=False, age=50
        )
        assert result.calculation_details["components"]["ich_volume"]["points"] == 0

        # At threshold
        result = calculator.calculate(
            gcs_score=15, ich_volume_ml=30.0, ivh_present=False,
            infratentorial=False, age=50
        )
        assert result.calculation_details["components"]["ich_volume"]["points"] == 1

    def test_age_threshold(self, calculator):
        """Test age threshold at 80 years"""
        # Below threshold
        result = calculator.calculate(
            gcs_score=15, ich_volume_ml=10, ivh_present=False,
            infratentorial=False, age=79
        )
        assert result.calculation_details["components"]["age"]["points"] == 0

        # At/above threshold
        result = calculator.calculate(
            gcs_score=15, ich_volume_ml=10, ivh_present=False,
            infratentorial=False, age=80
        )
        assert result.calculation_details["components"]["age"]["points"] == 1

    def test_ivh_and_infratentorial(self, calculator):
        """Test IVH and infratentorial components"""
        result = calculator.calculate(
            gcs_score=15, ich_volume_ml=10, ivh_present=True,
            infratentorial=True, age=50
        )
        assert result.calculation_details["components"]["ivh"]["points"] == 1
        assert result.calculation_details["components"]["infratentorial"]["points"] == 1
        assert result.value == 2

    @pytest.mark.parametrize("score,mortality", [
        (0, "0%"),
        (1, "13%"),
        (2, "26%"),
        (3, "72%"),
        (4, "97%"),
    ])
    def test_mortality_by_score(self, calculator, score, mortality):
        """Test 30-day mortality by ICH score"""
        # Create inputs to achieve specific score
        params = {
            "gcs_score": 15,
            "ich_volume_ml": 10,
            "ivh_present": False,
            "infratentorial": False,
            "age": 50
        }
        
        # Adjust to get target score
        points_needed = score
        if points_needed >= 1:
            params["ivh_present"] = True
            points_needed -= 1
        if points_needed >= 1:
            params["infratentorial"] = True
            points_needed -= 1
        if points_needed >= 1:
            params["ich_volume_ml"] = 50  # +1 point
            points_needed -= 1
        if points_needed >= 1:
            params["age"] = 85  # +1 point
            points_needed -= 1
        
        result = calculator.calculate(**params)
        assert result.calculation_details["mortality_30_day"] == mortality

    def test_invalid_gcs(self, calculator):
        """Test invalid GCS values"""
        with pytest.raises(ValueError):
            calculator.calculate(
                gcs_score=2, ich_volume_ml=10, ivh_present=False,
                infratentorial=False, age=50
            )
        with pytest.raises(ValueError):
            calculator.calculate(
                gcs_score=16, ich_volume_ml=10, ivh_present=False,
                infratentorial=False, age=50
            )


class TestNeurologyIntegration:
    """Integration tests for neurology calculator suite"""

    def test_sah_complete_workup(self):
        """Test complete SAH evaluation workflow"""
        hunt_hess = HuntHessCalculator()
        fisher = FisherGradeCalculator()
        
        # Patient with Grade III SAH and Modified Fisher 4
        hh_result = hunt_hess.calculate(grade=3)
        fisher_result = fisher.calculate(thick_sah=True, ivh_present=True)
        
        assert hh_result.value == 3
        assert fisher_result.value == 4
        
        # Both should indicate significant risk
        assert hh_result.interpretation.severity.name in ["MODERATE", "HIGH"]
        assert fisher_result.interpretation.severity.name == "CRITICAL"

    def test_coma_evaluation_comparison(self):
        """Test FOUR Score for detailed coma evaluation"""
        four_calc = FourScoreCalculator()
        
        # Moderate coma patient
        result = four_calc.calculate(
            eye_response=1,
            motor_response=2,
            brainstem_reflexes=4,
            respiration=1
        )
        
        assert result.value == 8
        assert result.calculation_details["brain_death_screening"] is False
        # Brainstem intact despite severe motor/eye findings
        assert result.calculation_details["components"]["brainstem_reflexes"]["score"] == 4

    def test_ich_prognosis_documentation(self):
        """Test ICH Score includes ethical documentation"""
        ich_calc = IchScoreCalculator()
        
        # High score patient
        result = ich_calc.calculate(
            gcs_score=4,
            ich_volume_ml=60,
            ivh_present=True,
            infratentorial=False,
            age=85
        )
        
        # Score should be 5 (2+1+1+1)
        assert result.value == 5
        
        # Should include ethical guidance in recommendations or warnings
        all_guidance = " ".join(result.interpretation.recommendations + result.interpretation.warnings)
        assert "not" in all_guidance.lower() or "should" in all_guidance.lower()
