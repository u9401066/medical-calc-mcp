"""
Tests for Charlson Comorbidity Index (CCI) Calculator

Testing:
- CCI scoring logic (17 conditions with weights 1, 2, 3, 6)
- Hierarchical rules (liver, diabetes, cancer)
- Age adjustment
- 10-year survival estimation
- Edge cases

Reference:
    Charlson ME, et al. J Chronic Dis. 1987;40(5):373-383. PMID: 3558716
"""

from typing import Any

import pytest

from src.domain.services.calculators.charlson_comorbidity import (
    CharlsonComorbidityIndexCalculator,
)


class TestCharlsonComorbidityIndex:
    """Test Charlson Comorbidity Index Calculator"""

    @pytest.fixture
    def calculator(self) -> Any:
        return CharlsonComorbidityIndexCalculator()

    # === Metadata Tests ===

    def test_metadata(self, calculator: Any) -> None:
        """Test calculator metadata"""
        assert calculator.tool_id == "charlson_comorbidity_index"
        assert "charlson" in calculator.name.lower()
        assert len(calculator.references) >= 2  # Original + Quan

    def test_references_have_pmids(self, calculator: Any) -> None:
        """Test that references include proper PMIDs"""
        pmids = [ref.pmid for ref in calculator.references if ref.pmid]
        assert "3558716" in pmids  # Original Charlson 1987
        assert "16224307" in pmids  # Quan 2005 (ICD-10)

    # === Basic Scoring Tests ===

    def test_no_comorbidity(self, calculator: Any) -> None:
        """Test patient with no comorbidities"""
        result = calculator.calculate(include_age_adjustment=False)
        assert result.value == 0
        assert "no comorbidity" in result.interpretation.stage_description.lower()

    def test_single_1point_condition(self, calculator: Any) -> None:
        """Test single 1-point condition (MI)"""
        result = calculator.calculate(
            myocardial_infarction=True,
            include_age_adjustment=False
        )
        assert result.value == 1
        assert "Myocardial infarction" in result.calculation_details

    def test_all_1point_conditions(self, calculator: Any) -> None:
        """Test all non-hierarchical 1-point conditions"""
        result = calculator.calculate(
            myocardial_infarction=True,
            congestive_heart_failure=True,
            peripheral_vascular_disease=True,
            cerebrovascular_disease=True,
            dementia=True,
            chronic_pulmonary_disease=True,
            connective_tissue_disease=True,
            peptic_ulcer_disease=True,
            include_age_adjustment=False
        )
        # 8 × 1 point = 8
        assert result.value == 8

    def test_2point_conditions(self, calculator: Any) -> None:
        """Test 2-point conditions"""
        result = calculator.calculate(
            hemiplegia=True,  # 2
            moderate_severe_renal_disease=True,  # 2
            include_age_adjustment=False
        )
        assert result.value == 4

    def test_6point_conditions(self, calculator: Any) -> None:
        """Test 6-point conditions"""
        result = calculator.calculate(
            metastatic_solid_tumor=True,  # 6
            aids=True,  # 6
            include_age_adjustment=False
        )
        assert result.value == 12

    # === Hierarchical Rules Tests ===

    def test_liver_hierarchy_mild_only(self, calculator: Any) -> None:
        """Test mild liver disease scores 1 point"""
        result = calculator.calculate(
            mild_liver_disease=True,
            include_age_adjustment=False
        )
        assert result.value == 1
        assert "Mild liver disease" in result.calculation_details

    def test_liver_hierarchy_severe_only(self, calculator: Any) -> None:
        """Test moderate/severe liver disease scores 3 points"""
        result = calculator.calculate(
            moderate_severe_liver_disease=True,
            include_age_adjustment=False
        )
        assert result.value == 3
        assert "Moderate/severe liver disease" in result.calculation_details

    def test_liver_hierarchy_both_severe_wins(self, calculator: Any) -> None:
        """Test that when both liver conditions present, only severe counts"""
        result = calculator.calculate(
            mild_liver_disease=True,
            moderate_severe_liver_disease=True,
            include_age_adjustment=False
        )
        # Should be 3, not 1+3=4
        assert result.value == 3
        assert "Mild liver disease" not in result.calculation_details

    def test_diabetes_hierarchy_uncomplicated_only(self, calculator: Any) -> None:
        """Test diabetes without complications scores 1 point"""
        result = calculator.calculate(
            diabetes_uncomplicated=True,
            include_age_adjustment=False
        )
        assert result.value == 1

    def test_diabetes_hierarchy_complicated_only(self, calculator: Any) -> None:
        """Test diabetes with complications scores 2 points"""
        result = calculator.calculate(
            diabetes_with_end_organ_damage=True,
            include_age_adjustment=False
        )
        assert result.value == 2

    def test_diabetes_hierarchy_both_complicated_wins(self, calculator: Any) -> None:
        """Test that when both diabetes conditions present, complicated wins"""
        result = calculator.calculate(
            diabetes_uncomplicated=True,
            diabetes_with_end_organ_damage=True,
            include_age_adjustment=False
        )
        # Should be 2, not 1+2=3
        assert result.value == 2
        assert "Diabetes uncomplicated" not in result.calculation_details

    def test_cancer_hierarchy_localized_only(self, calculator: Any) -> None:
        """Test localized malignancy scores 2 points"""
        result = calculator.calculate(
            any_malignancy=True,
            include_age_adjustment=False
        )
        assert result.value == 2

    def test_cancer_hierarchy_metastatic_only(self, calculator: Any) -> None:
        """Test metastatic tumor scores 6 points"""
        result = calculator.calculate(
            metastatic_solid_tumor=True,
            include_age_adjustment=False
        )
        assert result.value == 6

    def test_cancer_hierarchy_both_metastatic_wins(self, calculator: Any) -> None:
        """Test that when both cancer conditions present, metastatic wins"""
        result = calculator.calculate(
            any_malignancy=True,
            metastatic_solid_tumor=True,
            include_age_adjustment=False
        )
        # Should be 6, not 2+6=8
        assert result.value == 6
        assert "non-metastatic" not in str(result.calculation_details).lower()

    # === Age Adjustment Tests ===

    def test_age_adjustment_under_50(self, calculator: Any) -> None:
        """Test no age adjustment for patients under 50"""
        result = calculator.calculate(
            age_years=45,
            include_age_adjustment=True
        )
        assert result.value == 0

    def test_age_adjustment_50_to_59(self, calculator: Any) -> None:
        """Test +1 age adjustment for 50-59 years"""
        result = calculator.calculate(
            age_years=55,
            include_age_adjustment=True
        )
        assert result.value == 1
        assert "Age adjustment" in str(result.calculation_details)

    def test_age_adjustment_60_to_69(self, calculator: Any) -> None:
        """Test +2 age adjustment for 60-69 years"""
        result = calculator.calculate(
            age_years=65,
            include_age_adjustment=True
        )
        assert result.value == 2

    def test_age_adjustment_70_to_79(self, calculator: Any) -> None:
        """Test +3 age adjustment for 70-79 years"""
        result = calculator.calculate(
            age_years=75,
            include_age_adjustment=True
        )
        assert result.value == 3

    def test_age_adjustment_80_plus(self, calculator: Any) -> None:
        """Test +4 age adjustment for ≥80 years"""
        result = calculator.calculate(
            age_years=85,
            include_age_adjustment=True
        )
        assert result.value == 4

    def test_age_adjustment_disabled(self, calculator: Any) -> None:
        """Test that age adjustment can be disabled"""
        result = calculator.calculate(
            age_years=75,
            congestive_heart_failure=True,  # 1 point
            include_age_adjustment=False
        )
        assert result.value == 1  # Only CHF, no age points

    def test_age_required_when_adjustment_enabled(self, calculator: Any) -> None:
        """Test that age is required when age adjustment is enabled"""
        with pytest.raises(ValueError, match="age_years is required"):
            calculator.calculate(include_age_adjustment=True)

    # === Clinical Scenario Tests ===

    def test_typical_elderly_patient(self, calculator: Any) -> None:
        """Test typical elderly patient with multiple comorbidities"""
        # 75-year-old with CHF, COPD, DM2 with nephropathy, CKD
        result = calculator.calculate(
            age_years=75,
            congestive_heart_failure=True,  # 1
            chronic_pulmonary_disease=True,  # 1
            diabetes_with_end_organ_damage=True,  # 2
            moderate_severe_renal_disease=True,  # 2
            include_age_adjustment=True  # +3
        )
        # 1+1+2+2+3 = 9
        assert result.value == 9
        assert result.interpretation.risk_level.value in ["high", "very_high"]

    def test_cancer_patient(self, calculator: Any) -> None:
        """Test cancer patient with metastatic disease"""
        result = calculator.calculate(
            age_years=65,
            metastatic_solid_tumor=True,  # 6
            include_age_adjustment=True  # +2
        )
        # 6+2 = 8
        assert result.value == 8

    def test_aids_patient(self, calculator: Any) -> None:
        """Test AIDS patient"""
        result = calculator.calculate(
            age_years=45,
            aids=True,  # 6
            include_age_adjustment=True  # 0 (under 50)
        )
        assert result.value == 6

    def test_healthy_middle_aged(self, calculator: Any) -> None:
        """Test healthy middle-aged patient"""
        result = calculator.calculate(
            age_years=55,
            include_age_adjustment=True  # +1
        )
        assert result.value == 1
        assert "98%" in result.interpretation.detail or "96%" in result.interpretation.detail

    # === Survival Estimation Tests ===

    def test_survival_estimation_cci_0(self, calculator: Any) -> None:
        """Test 10-year survival for CCI 0"""
        result = calculator.calculate(include_age_adjustment=False)
        assert "98%" in result.interpretation.detail

    def test_survival_estimation_cci_5(self, calculator: Any) -> None:
        """Test 10-year survival for CCI 5"""
        result = calculator.calculate(
            metastatic_solid_tumor=True,  # 6 points, but we need 5
            include_age_adjustment=False
        )
        # Actually this gives 6, let's use different conditions
        result = calculator.calculate(
            congestive_heart_failure=True,  # 1
            chronic_pulmonary_disease=True,  # 1
            diabetes_with_end_organ_damage=True,  # 2
            myocardial_infarction=True,  # 1
            include_age_adjustment=False
        )
        assert result.value == 5
        assert "21%" in result.interpretation.detail

    def test_survival_estimation_cci_high(self, calculator: Any) -> None:
        """Test 10-year survival for CCI ≥6"""
        result = calculator.calculate(
            metastatic_solid_tumor=True,  # 6
            include_age_adjustment=False
        )
        assert result.value == 6
        assert "2%" in result.interpretation.detail or "≤2%" in result.interpretation.detail

    # === Edge Cases ===

    def test_maximum_possible_score(self, calculator: Any) -> None:
        """Test maximum possible CCI score"""
        result = calculator.calculate(
            age_years=90,
            myocardial_infarction=True,  # 1
            congestive_heart_failure=True,  # 1
            peripheral_vascular_disease=True,  # 1
            cerebrovascular_disease=True,  # 1
            dementia=True,  # 1
            chronic_pulmonary_disease=True,  # 1
            connective_tissue_disease=True,  # 1
            peptic_ulcer_disease=True,  # 1
            moderate_severe_liver_disease=True,  # 3
            diabetes_with_end_organ_damage=True,  # 2
            hemiplegia=True,  # 2
            moderate_severe_renal_disease=True,  # 2
            metastatic_solid_tumor=True,  # 6
            aids=True,  # 6
            include_age_adjustment=True  # +4
        )
        # 8×1 + 3 + 2 + 2 + 2 + 6 + 6 + 4 = 33
        assert result.value == 33

    def test_all_hierarchies_severe(self, calculator: Any) -> None:
        """Test all hierarchical conditions at severe level"""
        result = calculator.calculate(
            mild_liver_disease=True,  # ignored
            moderate_severe_liver_disease=True,  # 3
            diabetes_uncomplicated=True,  # ignored
            diabetes_with_end_organ_damage=True,  # 2
            any_malignancy=True,  # ignored
            metastatic_solid_tumor=True,  # 6
            include_age_adjustment=False
        )
        # Only severe counts: 3+2+6 = 11
        assert result.value == 11

    # === Interpretation Tests ===

    def test_interpretation_severity_levels(self, calculator: Any) -> None:
        """Test that interpretation severity matches score"""
        # No comorbidity
        result0 = calculator.calculate(include_age_adjustment=False)
        assert result0.interpretation.severity.value == "normal"

        # Mild (1-2)
        result1 = calculator.calculate(
            myocardial_infarction=True,
            include_age_adjustment=False
        )
        assert result1.interpretation.severity.value == "mild"

        # Moderate (3-4)
        result3 = calculator.calculate(
            myocardial_infarction=True,
            diabetes_with_end_organ_damage=True,
            include_age_adjustment=False
        )
        assert result3.value == 3
        assert result3.interpretation.severity.value == "moderate"

        # Severe (5-6)
        result5 = calculator.calculate(
            metastatic_solid_tumor=True,
            include_age_adjustment=False
        )
        assert result5.value == 6
        assert result5.interpretation.severity.value in ["severe", "critical"]

    def test_recommendations_present(self, calculator: Any) -> None:
        """Test that recommendations are provided"""
        result = calculator.calculate(
            age_years=75,
            congestive_heart_failure=True,
            include_age_adjustment=True
        )
        assert len(result.interpretation.recommendations) > 0
        assert len(result.interpretation.next_steps) > 0

    def test_warnings_for_high_score(self, calculator: Any) -> None:
        """Test that warnings are provided for high scores"""
        result = calculator.calculate(
            metastatic_solid_tumor=True,
            aids=True,
            include_age_adjustment=False
        )
        assert result.value == 12
        assert len(result.interpretation.warnings) > 0
