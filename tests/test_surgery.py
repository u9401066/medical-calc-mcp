"""
Tests for Surgery/Perioperative Calculators

Tests Caprini VTE Risk Score calculator.
"""

import pytest


class TestCapriniVteCalculator:
    """Tests for Caprini VTE Risk Assessment Score."""

    def test_low_risk_young_patient(self):
        """Test Caprini for low risk young patient."""
        from src.domain.services.calculators import CapriniVteCalculator
        
        calc = CapriniVteCalculator()
        result = calc.calculate(
            age=35,
            planned_surgery_type="minor_surgery",
            bmi_over_25=False,
            sepsis_within_1_month=False,
            serious_lung_disease=False,
            abnormal_pulmonary_function=False,
            current_chf=False,
            history_mi=False,
            prior_vte=False,
            family_history_vte=False,
            factor_v_leiden=False,
            prothrombin_mutation=False,
            lupus_anticoagulant=False,
            anticardiolipin_antibody=False,
            heparin_induced_thrombocytopenia=False,
            other_thrombophilia=False,
            immobility=False,
            central_venous_access=False,
        )
        
        assert result.value is not None
        assert result.value <= 2  # Low risk

    def test_moderate_risk(self):
        """Test Caprini for moderate risk patient."""
        from src.domain.services.calculators import CapriniVteCalculator
        
        calc = CapriniVteCalculator()
        result = calc.calculate(
            age=55,                                  # +2
            planned_surgery_type="major_surgery_over_45_min",  # +2
            bmi_over_25=True,                        # +1
            sepsis_within_1_month=False,
            serious_lung_disease=False,
            abnormal_pulmonary_function=False,
            current_chf=False,
            history_mi=False,
            prior_vte=False,
            family_history_vte=False,
            factor_v_leiden=False,
            prothrombin_mutation=False,
            lupus_anticoagulant=False,
            anticardiolipin_antibody=False,
            heparin_induced_thrombocytopenia=False,
            other_thrombophilia=False,
            immobility=False,
            central_venous_access=True,             # +2
        )
        
        assert result.value >= 3  # At least moderate risk

    def test_high_risk_with_prior_vte(self):
        """Test Caprini for high risk patient with prior VTE."""
        from src.domain.services.calculators import CapriniVteCalculator
        
        calc = CapriniVteCalculator()
        result = calc.calculate(
            age=65,
            planned_surgery_type="major_surgery_over_45_min",
            bmi_over_25=True,
            sepsis_within_1_month=False,
            serious_lung_disease=False,
            abnormal_pulmonary_function=False,
            current_chf=True,
            history_mi=True,
            prior_vte=True,                         # +3
            family_history_vte=True,
            factor_v_leiden=False,
            prothrombin_mutation=False,
            lupus_anticoagulant=False,
            anticardiolipin_antibody=False,
            heparin_induced_thrombocytopenia=False,
            other_thrombophilia=False,
            immobility=False,
            central_venous_access=False,
        )
        
        assert result.value >= 5  # High risk

    def test_highest_risk_thrombophilia(self):
        """Test Caprini for highest risk with thrombophilia."""
        from src.domain.services.calculators import CapriniVteCalculator
        
        calc = CapriniVteCalculator()
        result = calc.calculate(
            age=75,
            planned_surgery_type="major_surgery_over_45_min",
            bmi_over_25=True,
            sepsis_within_1_month=True,
            serious_lung_disease=True,
            abnormal_pulmonary_function=True,
            current_chf=True,
            history_mi=True,
            prior_vte=True,
            family_history_vte=True,
            factor_v_leiden=True,                   # +3
            prothrombin_mutation=True,              # +3
            lupus_anticoagulant=True,               # +3
            anticardiolipin_antibody=True,          # +3
            heparin_induced_thrombocytopenia=True,  # +3
            other_thrombophilia=True,               # +3
            immobility=True,
            central_venous_access=True,
        )
        
        assert result.value >= 9  # Highest risk

    def test_age_scoring(self):
        """Test age contribution to Caprini score."""
        from src.domain.services.calculators import CapriniVteCalculator
        
        calc = CapriniVteCalculator()
        
        base_params = dict(
            planned_surgery_type="minor_surgery",
            bmi_over_25=False,
            sepsis_within_1_month=False,
            serious_lung_disease=False,
            abnormal_pulmonary_function=False,
            current_chf=False,
            history_mi=False,
            prior_vte=False,
            family_history_vte=False,
            factor_v_leiden=False,
            prothrombin_mutation=False,
            lupus_anticoagulant=False,
            anticardiolipin_antibody=False,
            heparin_induced_thrombocytopenia=False,
            other_thrombophilia=False,
            immobility=False,
            central_venous_access=False,
        )
        
        # Age 40: 0 points
        result1 = calc.calculate(age=40, **base_params)
        
        # Age 45: +1
        result2 = calc.calculate(age=45, **base_params)
        
        # Age 65: +2
        result3 = calc.calculate(age=65, **base_params)
        
        # Age 75: +3
        result4 = calc.calculate(age=75, **base_params)
        
        # Scores should increase with age
        assert result1.value < result2.value < result3.value < result4.value

    def test_prophylaxis_recommendations(self):
        """Test that score includes prophylaxis recommendations."""
        from src.domain.services.calculators import CapriniVteCalculator
        
        calc = CapriniVteCalculator()
        result = calc.calculate(
            age=70,
            planned_surgery_type="major_surgery_over_45_min",
            bmi_over_25=True,
            sepsis_within_1_month=False,
            serious_lung_disease=False,
            abnormal_pulmonary_function=False,
            current_chf=False,
            history_mi=False,
            prior_vte=True,
            family_history_vte=False,
            factor_v_leiden=False,
            prothrombin_mutation=False,
            lupus_anticoagulant=False,
            anticardiolipin_antibody=False,
            heparin_induced_thrombocytopenia=False,
            other_thrombophilia=False,
            immobility=False,
            central_venous_access=False,
        )
        
        # High risk should have recommendations
        assert result.interpretation is not None
        # Should mention prophylaxis or anticoagulation
        interpretation_text = str(result.interpretation.summary).lower()
        assert "prophylaxis" in interpretation_text or "risk" in interpretation_text

    def test_has_references(self):
        """Test that Caprini includes proper references."""
        from src.domain.services.calculators import CapriniVteCalculator
        
        calc = CapriniVteCalculator()
        result = calc.calculate(
            age=50,
            planned_surgery_type="minor_surgery",
            bmi_over_25=False,
            sepsis_within_1_month=False,
            serious_lung_disease=False,
            abnormal_pulmonary_function=False,
            current_chf=False,
            history_mi=False,
            prior_vte=False,
            family_history_vte=False,
            factor_v_leiden=False,
            prothrombin_mutation=False,
            lupus_anticoagulant=False,
            anticardiolipin_antibody=False,
            heparin_induced_thrombocytopenia=False,
            other_thrombophilia=False,
            immobility=False,
            central_venous_access=False,
        )
        
        assert result.references is not None
        assert len(result.references) > 0
        # Should reference Caprini
        assert any("caprini" in ref.citation.lower() for ref in result.references)

    def test_tool_id(self):
        """Test tool ID is correct."""
        from src.domain.services.calculators import CapriniVteCalculator
        
        calc = CapriniVteCalculator()
        assert calc.tool_id == "caprini_vte"
