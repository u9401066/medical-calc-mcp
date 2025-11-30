"""
Tests for Emergency Medicine Calculators

Tests Wells DVT and Wells PE calculators.
"""

import pytest


class TestWellsDvtCalculator:
    """Tests for Wells Score for DVT."""

    def test_low_probability(self):
        """Test Wells DVT with low probability."""
        from src.domain.services.calculators import WellsDvtCalculator
        
        calc = WellsDvtCalculator()
        result = calc.calculate(
            active_cancer=False,
            paralysis_or_immobilization=False,
            bedridden_or_major_surgery=False,
            localized_tenderness=False,
            entire_leg_swollen=False,
            calf_swelling_3cm=False,
            pitting_edema=False,
            collateral_superficial_veins=False,
            previously_documented_dvt=False,
            alternative_diagnosis_likely=True,  # -2 points
        )
        
        assert result.value == -2
        assert "low" in result.interpretation.summary.lower() or "unlikely" in result.interpretation.summary.lower()

    def test_moderate_probability(self):
        """Test Wells DVT with moderate probability."""
        from src.domain.services.calculators import WellsDvtCalculator
        
        calc = WellsDvtCalculator()
        result = calc.calculate(
            active_cancer=False,
            paralysis_or_immobilization=False,
            bedridden_or_major_surgery=True,   # +1
            localized_tenderness=True,          # +1
            entire_leg_swollen=False,
            calf_swelling_3cm=True,             # +1
            pitting_edema=False,
            collateral_superficial_veins=False,
            previously_documented_dvt=False,
            alternative_diagnosis_likely=False,
        )
        
        assert result.value == 3

    def test_high_probability(self):
        """Test Wells DVT with high probability."""
        from src.domain.services.calculators import WellsDvtCalculator
        
        calc = WellsDvtCalculator()
        result = calc.calculate(
            active_cancer=True,                 # +1
            paralysis_or_immobilization=True,   # +1
            bedridden_or_major_surgery=True,    # +1
            localized_tenderness=True,          # +1
            entire_leg_swollen=True,            # +1
            calf_swelling_3cm=True,             # +1
            pitting_edema=True,                 # +1
            collateral_superficial_veins=True,  # +1
            previously_documented_dvt=True,     # +1
            alternative_diagnosis_likely=False,
        )
        
        assert result.value == 9
        assert "high" in result.interpretation.summary.lower() or "likely" in result.interpretation.summary.lower()

    def test_alternative_diagnosis_subtracts_two(self):
        """Test that alternative diagnosis likely subtracts 2 points."""
        from src.domain.services.calculators import WellsDvtCalculator
        
        calc = WellsDvtCalculator()
        
        # Without alternative diagnosis
        result1 = calc.calculate(
            active_cancer=True,
            paralysis_or_immobilization=False,
            bedridden_or_major_surgery=False,
            localized_tenderness=False,
            entire_leg_swollen=False,
            calf_swelling_3cm=False,
            pitting_edema=False,
            collateral_superficial_veins=False,
            previously_documented_dvt=False,
            alternative_diagnosis_likely=False,
        )
        
        # With alternative diagnosis
        result2 = calc.calculate(
            active_cancer=True,
            paralysis_or_immobilization=False,
            bedridden_or_major_surgery=False,
            localized_tenderness=False,
            entire_leg_swollen=False,
            calf_swelling_3cm=False,
            pitting_edema=False,
            collateral_superficial_veins=False,
            previously_documented_dvt=False,
            alternative_diagnosis_likely=True,
        )
        
        assert result1.value - result2.value == 2

    def test_tool_id(self):
        """Test tool ID is correct."""
        from src.domain.services.calculators import WellsDvtCalculator
        
        calc = WellsDvtCalculator()
        assert calc.tool_id == "wells_dvt"


class TestWellsPeCalculator:
    """Tests for Wells Score for PE."""

    def test_low_probability(self):
        """Test Wells PE with low probability."""
        from src.domain.services.calculators import WellsPeCalculator
        
        calc = WellsPeCalculator()
        result = calc.calculate(
            clinical_signs_dvt=False,
            pe_most_likely_diagnosis=False,
            heart_rate_over_100=False,
            immobilization_or_surgery=False,
            previous_dvt_pe=False,
            hemoptysis=False,
            malignancy=False,
        )
        
        assert result.value == 0
        assert "low" in result.interpretation.summary.lower() or "unlikely" in result.interpretation.summary.lower()

    def test_moderate_probability(self):
        """Test Wells PE with moderate probability."""
        from src.domain.services.calculators import WellsPeCalculator
        
        calc = WellsPeCalculator()
        result = calc.calculate(
            clinical_signs_dvt=False,
            pe_most_likely_diagnosis=False,
            heart_rate_over_100=True,      # +1.5
            immobilization_or_surgery=True, # +1.5
            previous_dvt_pe=True,           # +1.5
            hemoptysis=False,
            malignancy=False,
        )
        
        assert result.value == 4.5

    def test_high_probability(self):
        """Test Wells PE with high probability."""
        from src.domain.services.calculators import WellsPeCalculator
        
        calc = WellsPeCalculator()
        result = calc.calculate(
            clinical_signs_dvt=True,         # +3
            pe_most_likely_diagnosis=True,   # +3
            heart_rate_over_100=True,        # +1.5
            immobilization_or_surgery=True,  # +1.5
            previous_dvt_pe=True,            # +1.5
            hemoptysis=True,                 # +1
            malignancy=True,                 # +1
        )
        
        assert result.value == 12.5
        assert "high" in result.interpretation.summary.lower() or "likely" in result.interpretation.summary.lower()

    def test_pe_likely_threshold(self):
        """Test PE likely/unlikely threshold (>4 = likely)."""
        from src.domain.services.calculators import WellsPeCalculator
        
        calc = WellsPeCalculator()
        
        # Score = 4 (unlikely)
        result1 = calc.calculate(
            clinical_signs_dvt=False,
            pe_most_likely_diagnosis=False,
            heart_rate_over_100=True,       # +1.5
            immobilization_or_surgery=True,  # +1.5
            previous_dvt_pe=False,
            hemoptysis=True,                 # +1
            malignancy=False,
        )
        assert result1.value == 4
        
        # Score = 4.5 (likely)
        result2 = calc.calculate(
            clinical_signs_dvt=False,
            pe_most_likely_diagnosis=False,
            heart_rate_over_100=True,       # +1.5
            immobilization_or_surgery=True,  # +1.5
            previous_dvt_pe=True,            # +1.5
            hemoptysis=False,
            malignancy=False,
        )
        assert result2.value == 4.5

    def test_tool_id(self):
        """Test tool ID is correct."""
        from src.domain.services.calculators import WellsPeCalculator
        
        calc = WellsPeCalculator()
        assert calc.tool_id == "wells_pe"
