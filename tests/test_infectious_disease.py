from typing import Any

"""
Tests for Infectious Disease Calculators

Phase 16: MASCC Score, Pitt Bacteremia, Centor Score, CPIS
"""

import pytest


class TestMasccScoreCalculator:
    """Tests for MASCC (Febrile Neutropenia Risk) Score Calculator"""

    @pytest.fixture
    def calculator(self) -> Any:
        from src.domain.services.calculators.mascc_score import MasccScoreCalculator
        return MasccScoreCalculator()

    def test_low_risk_all_favorable(self, calculator: Any) -> None:
        """Test maximum score = low risk"""
        result = calculator.calculate(
            burden_of_illness="none_mild",
            no_hypotension=True,
            no_copd=True,
            solid_tumor_or_no_fungal_hx=True,
            no_dehydration=True,
            outpatient_status=True,
            age_lt_60=True,
        )
        assert result.value is not None
        assert result.value == 26  # Maximum score
        assert result.interpretation.risk_level is not None
        assert result.interpretation.risk_level.value == "low"
        assert result.interpretation.summary is not None
        assert "outpatient" in result.interpretation.summary.lower() or "low risk" in result.interpretation.summary.lower()

    def test_high_risk_severe_illness(self, calculator: Any) -> None:
        """Test high risk with severe symptoms"""
        result = calculator.calculate(
            burden_of_illness="severe",
            no_hypotension=False,
            no_copd=False,
            solid_tumor_or_no_fungal_hx=False,
            no_dehydration=False,
            outpatient_status=False,
            age_lt_60=False,
        )
        assert result.value is not None
        assert result.value == 0  # Minimum score
        assert result.interpretation.risk_level is not None
        assert result.interpretation.risk_level.value == "high"
        assert result.interpretation.detail is not None
        assert "admit" in result.interpretation.detail.lower() or "high risk" in result.interpretation.summary.lower()

    def test_threshold_at_21(self, calculator: Any) -> None:
        """Test threshold at score 21"""
        # Score = 21 (low risk)
        result = calculator.calculate(
            burden_of_illness="none_mild",  # +5
            no_hypotension=True,  # +5
            no_copd=True,  # +4
            solid_tumor_or_no_fungal_hx=True,  # +4
            no_dehydration=True,  # +3
            outpatient_status=False,  # +0
            age_lt_60=False,  # +0
        )
        assert result.value is not None
        assert result.value == 21
        assert result.interpretation.risk_level is not None
        assert result.interpretation.risk_level.value == "low"

    def test_threshold_at_20(self, calculator: Any) -> None:
        """Test high risk at score 20"""
        # Score = 20 (high risk)
        result = calculator.calculate(
            burden_of_illness="none_mild",  # +5
            no_hypotension=True,  # +5
            no_copd=True,  # +4
            solid_tumor_or_no_fungal_hx=True,  # +4
            no_dehydration=False,  # +0
            outpatient_status=False,  # +0
            age_lt_60=True,  # +2
        )
        assert result.value is not None
        assert result.value == 20
        assert result.interpretation.risk_level is not None
        assert result.interpretation.risk_level.value == "high"

    def test_calculation_details_fields(self, calculator: Any) -> None:
        """Test required calculation_details fields exist"""
        result = calculator.calculate(
            burden_of_illness="moderate",
            no_hypotension=True,
            no_copd=True,
            solid_tumor_or_no_fungal_hx=True,
            no_dehydration=True,
            outpatient_status=True,
            age_lt_60=True,
        )
        assert "burden_of_illness" in result.calculation_details
        assert "blood_pressure" in result.calculation_details
        assert len(result.interpretation.next_steps) > 0

    def test_interpretation_has_recommendations(self, calculator: Any) -> None:
        """Test interpretation includes recommendations"""
        result = calculator.calculate(
            burden_of_illness="none_mild",
            no_hypotension=True,
            no_copd=True,
            solid_tumor_or_no_fungal_hx=True,
            no_dehydration=True,
            outpatient_status=True,
            age_lt_60=True,
        )
        assert len(result.interpretation.recommendations) > 0


class TestPittBacteremiaCalculator:
    """Tests for Pitt Bacteremia Score Calculator"""

    @pytest.fixture
    def calculator(self) -> Any:
        from src.domain.services.calculators.pitt_bacteremia import PittBacteremiaCalculator
        return PittBacteremiaCalculator()

    def test_low_risk_normal_values(self, calculator: Any) -> None:
        """Test low risk with all normal values"""
        result = calculator.calculate(
            temperature_category="normal",
            hypotension=False,
            mechanical_ventilation=False,
            cardiac_arrest=False,
            mental_status="alert",
        )
        assert result.value is not None
        assert result.value == 0
        assert result.interpretation.risk_level is not None
        assert result.interpretation.risk_level.value == "low"
        # Low mortality risk
        assert result.interpretation.summary is not None
        assert "low" in result.interpretation.summary.lower()

    def test_high_risk_cardiac_arrest(self, calculator: Any) -> None:
        """Test high risk with cardiac arrest"""
        result = calculator.calculate(
            temperature_category="normal",
            hypotension=False,
            mechanical_ventilation=False,
            cardiac_arrest=True,  # +4
            mental_status="comatose",  # +4
        )
        assert result.value is not None
        assert result.value == 8
        assert result.interpretation.risk_level is not None
        assert result.interpretation.risk_level.value in ["high", "very_high"]

    def test_moderate_risk(self, calculator: Any) -> None:
        """Test moderate risk calculation"""
        result = calculator.calculate(
            temperature_category="extreme",  # +2
            hypotension=True,  # +2
            mechanical_ventilation=False,
            cardiac_arrest=False,
            mental_status="alert",
        )
        assert result.value is not None
        assert result.value == 4
        assert result.interpretation.risk_level is not None
        assert result.interpretation.risk_level.value in ["intermediate", "high"]

    def test_temperature_scoring(self, calculator: Any) -> None:
        """Test temperature category scoring"""
        # Extreme temperature
        result = calculator.calculate(
            temperature_category="extreme",
            hypotension=False,
            mechanical_ventilation=False,
            cardiac_arrest=False,
            mental_status="alert",
        )
        assert result.value is not None
        assert result.value == 2

        # Low/mild temperature
        result = calculator.calculate(
            temperature_category="low_mild",
            hypotension=False,
            mechanical_ventilation=False,
            cardiac_arrest=False,
            mental_status="alert",
        )
        assert result.value is not None
        assert result.value == 1

    def test_mental_status_scoring(self, calculator: Any) -> None:
        """Test mental status scoring"""
        statuses = [
            ("alert", 0),
            ("disoriented", 1),
            ("stuporous", 2),
            ("comatose", 4),
        ]
        for status, expected_score in statuses:
            result = calculator.calculate(
                temperature_category="normal",
                hypotension=False,
                mechanical_ventilation=False,
                cardiac_arrest=False,
                mental_status=status,
            )
            assert result.value is not None
            assert result.value == expected_score


class TestCentorScoreCalculator:
    """Tests for Centor Score Calculator"""

    @pytest.fixture
    def calculator(self) -> Any:
        from src.domain.services.calculators.centor_score import CentorScoreCalculator
        return CentorScoreCalculator()

    def test_score_0_no_testing(self, calculator: Any) -> None:
        """Test score 0 - no testing recommended"""
        result = calculator.calculate(
            tonsillar_exudates=False,
            tender_anterior_cervical_nodes=False,
            fever=False,
            absence_of_cough=False,
        )
        assert result.value is not None
        assert result.value == 0
        # Check that no testing/low risk indicated
        assert result.interpretation.summary is not None
        assert result.interpretation.risk_level is not None
        assert result.interpretation.summary is not None
        assert result.interpretation.summary is not None
        assert "no testing" in result.interpretation.summary.lower() or result.interpretation.risk_level.value == "very_low"

    def test_score_4_original_centor(self, calculator: Any) -> None:
        """Test maximum original Centor score"""
        result = calculator.calculate(
            tonsillar_exudates=True,
            tender_anterior_cervical_nodes=True,
            fever=True,
            absence_of_cough=True,
        )
        assert result.value is not None
        assert result.value == 4
        # Score 4 = 51-53% GAS probability - intermediate risk level
        assert result.interpretation.risk_level is not None
        assert result.interpretation.risk_level.value == "intermediate"
        assert result.interpretation.summary is not None
        assert "51-53%" in result.interpretation.summary

    def test_mcisaac_pediatric_adjustment(self, calculator: Any) -> None:
        """Test McIsaac pediatric age adjustment (+1)"""
        result = calculator.calculate(
            tonsillar_exudates=True,
            tender_anterior_cervical_nodes=True,
            fever=True,
            absence_of_cough=True,
            age_group="pediatric",
        )
        assert result.value is not None
        assert result.value == 5  # 4 + 1 for pediatric
        # Check calculation details mention McIsaac

    def test_mcisaac_older_adult_adjustment(self, calculator: Any) -> None:
        """Test McIsaac older adult age adjustment (-1)"""
        result = calculator.calculate(
            tonsillar_exudates=True,
            tender_anterior_cervical_nodes=True,
            fever=True,
            absence_of_cough=True,
            age_group="older_adult",
        )
        assert result.value is not None
        assert result.value == 3  # 4 - 1 for older adult

    def test_score_2_testing_recommended(self, calculator: Any) -> None:
        """Test score 2 - testing may be recommended"""
        result = calculator.calculate(
            tonsillar_exudates=True,
            tender_anterior_cervical_nodes=True,
            fever=False,
            absence_of_cough=False,
        )
        assert result.value is not None
        assert result.value == 2
        # Moderate risk

    def test_next_step_includes_guidance(self, calculator: Any) -> None:
        """Test next step includes clinical guidance"""
        result = calculator.calculate(
            tonsillar_exudates=True,
            tender_anterior_cervical_nodes=True,
            fever=True,
            absence_of_cough=True,
        )
        assert len(result.interpretation.next_steps) > 0


class TestCpisCalculator:
    """Tests for CPIS (VAP Diagnosis) Calculator"""

    @pytest.fixture
    def calculator(self) -> Any:
        from src.domain.services.calculators.cpis import CpisCalculator
        return CpisCalculator()

    def test_low_cpis_no_vap(self, calculator: Any) -> None:
        """Test CPIS ≤6 suggests no VAP"""
        result = calculator.calculate(
            temperature_category="normal",  # +0
            wbc_category="normal",  # +0
            band_forms_gte_50=False,
            secretions="none",  # +0
            pao2_fio2_lte_240_no_ards=False,  # +0
            chest_xray="no_infiltrate",  # +0
            culture_growth="none_light",  # +0
            gram_stain_matches=False,
        )
        assert result.value is not None
        assert result.value == 0
        assert result.interpretation.risk_level is not None
        assert result.interpretation.risk_level.value in ["low", "very_low"]

    def test_high_cpis_likely_vap(self, calculator: Any) -> None:
        """Test CPIS >6 suggests VAP"""
        result = calculator.calculate(
            temperature_category="high",  # +2
            wbc_category="abnormal",  # +1
            band_forms_gte_50=True,  # +1
            secretions="purulent",  # +2
            pao2_fio2_lte_240_no_ards=True,  # +2
            chest_xray="localized",  # +2
            culture_growth="moderate_heavy",  # +1
            gram_stain_matches=True,  # +1
        )
        assert result.value is not None
        assert result.value == 12  # Maximum
        assert result.interpretation.risk_level is not None
        assert result.interpretation.risk_level.value in ["high", "very_high"]

    def test_threshold_at_6(self, calculator: Any) -> None:
        """Test threshold exactly at 6"""
        result = calculator.calculate(
            temperature_category="high",  # +2
            wbc_category="abnormal",  # +1
            band_forms_gte_50=False,
            secretions="moderate",  # +1
            pao2_fio2_lte_240_no_ards=True,  # +2
            chest_xray="no_infiltrate",  # +0
            culture_growth="none_light",  # +0
            gram_stain_matches=False,
        )
        assert result.value is not None
        assert result.value == 6
        # At threshold - should be low/borderline
        assert result.interpretation.risk_level is not None
        assert result.interpretation.risk_level.value in ["low", "intermediate"]

    def test_threshold_at_7(self, calculator: Any) -> None:
        """Test threshold at 7"""
        result = calculator.calculate(
            temperature_category="high",  # +2
            wbc_category="abnormal",  # +1
            band_forms_gte_50=True,  # +1
            secretions="moderate",  # +1
            pao2_fio2_lte_240_no_ards=True,  # +2
            chest_xray="no_infiltrate",  # +0
            culture_growth="none_light",  # +0
            gram_stain_matches=False,
        )
        assert result.value is not None
        assert result.value == 7
        assert result.interpretation.risk_level is not None
        assert result.interpretation.risk_level.value in ["high", "intermediate"]

    def test_band_forms_only_with_abnormal_wbc(self, calculator: Any) -> None:
        """Test band forms only add points with abnormal WBC"""
        # Normal WBC with bands - bands shouldn't add points
        result1 = calculator.calculate(
            temperature_category="normal",
            wbc_category="normal",
            band_forms_gte_50=True,  # Should not add
            secretions="none",
            pao2_fio2_lte_240_no_ards=False,
            chest_xray="no_infiltrate",
            culture_growth="none_light",
            gram_stain_matches=False,
        )
        assert result1.value is not None
        assert result1.value == 0

        # Abnormal WBC with bands - bands should add
        result2 = calculator.calculate(
            temperature_category="normal",
            wbc_category="abnormal",
            band_forms_gte_50=True,
            secretions="none",
            pao2_fio2_lte_240_no_ards=False,
            chest_xray="no_infiltrate",
            culture_growth="none_light",
            gram_stain_matches=False,
        )
        assert result2.value is not None
        assert result2.value == 2  # 1 for abnormal WBC + 1 for bands

    def test_references_exist(self, calculator: Any) -> None:
        """Test calculator has proper references"""
        metadata = calculator.metadata
        assert len(metadata.references) >= 2
        assert any("Pugin" in ref.citation for ref in metadata.references)


class TestInfectiousDiseaseCalculatorRegistration:
    """Test that all Phase 16 calculators are properly registered"""

    def test_calculators_in_registry(self) -> None:
        """Test all Phase 16 calculators are in CALCULATORS list"""
        from src.domain.services.calculators import CALCULATORS

        calculator_names = [c.__name__ for c in CALCULATORS]

        assert "MasccScoreCalculator" in calculator_names
        assert "PittBacteremiaCalculator" in calculator_names
        assert "CentorScoreCalculator" in calculator_names
        assert "CpisCalculator" in calculator_names

    def test_calculator_count_is_91(self) -> None:
        """Test total calculator count after Phase 23 (CV Prevention & Bone Health)"""
        from src.domain.services.calculators import CALCULATORS
        assert len(CALCULATORS) == 91
