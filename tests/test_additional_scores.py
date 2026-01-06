"""
Tests for Additional Clinical Calculators (Phase 13+)

Tests TIMI STEMI, Rockall, FIB-4 and other scores.
"""

import pytest


class TestTimiStemiCalculator:
    """Tests for TIMI Risk Score for STEMI Calculator."""

    def test_low_risk_score_0(self) -> None:
        """Test TIMI STEMI score 0 - lowest risk."""
        from src.domain.services.calculators import TimiStemiCalculator

        calc = TimiStemiCalculator()
        result = calc.calculate(
            age_years=50,
            has_dm_htn_or_angina=False,
            systolic_bp_lt_100=False,
            heart_rate_gt_100=False,
            killip_class=1,
            weight_lt_67kg=False,
            anterior_ste_or_lbbb=False,
            time_to_treatment_gt_4h=False
        )

        assert result.value is not None
        assert result.value == 0
        assert result.interpretation.summary is not None
        assert "low" in result.interpretation.summary.lower()
        assert result.calculation_details is not None
        assert "0.8%" in result.calculation_details["mortality_30day"]

    def test_low_risk_score_2(self) -> None:
        """Test TIMI STEMI score 2 - still low risk."""
        from src.domain.services.calculators import TimiStemiCalculator

        calc = TimiStemiCalculator()
        result = calc.calculate(
            age_years=68,  # +2 for age 65-74
            has_dm_htn_or_angina=False,
            systolic_bp_lt_100=False,
            heart_rate_gt_100=False,
            killip_class=1,
            weight_lt_67kg=False,
            anterior_ste_or_lbbb=False,
            time_to_treatment_gt_4h=False
        )

        assert result.value is not None
        assert result.value == 2
        assert result.interpretation.summary is not None
        assert "low" in result.interpretation.summary.lower()

    def test_intermediate_risk_score_4(self) -> None:
        """Test TIMI STEMI score 4 - intermediate risk."""
        from src.domain.services.calculators import TimiStemiCalculator

        calc = TimiStemiCalculator()
        result = calc.calculate(
            age_years=68,  # +2
            has_dm_htn_or_angina=True,  # +1
            systolic_bp_lt_100=False,
            heart_rate_gt_100=False,
            killip_class=1,
            weight_lt_67kg=False,
            anterior_ste_or_lbbb=True,  # +1
            time_to_treatment_gt_4h=False
        )

        assert result.value is not None
        assert result.value == 4
        assert result.interpretation.summary is not None
        assert "intermediate" in result.interpretation.summary.lower()

    def test_high_risk_score_6(self) -> None:
        """Test TIMI STEMI score 6 - high risk."""
        from src.domain.services.calculators import TimiStemiCalculator

        calc = TimiStemiCalculator()
        result = calc.calculate(
            age_years=68,  # +2
            has_dm_htn_or_angina=True,  # +1
            systolic_bp_lt_100=False,
            heart_rate_gt_100=True,  # +2
            killip_class=1,
            weight_lt_67kg=False,
            anterior_ste_or_lbbb=True,  # +1
            time_to_treatment_gt_4h=False
        )

        assert result.value is not None
        assert result.value == 6
        assert result.interpretation.summary is not None
        assert "high" in result.interpretation.summary.lower()

    def test_very_high_risk_score_8(self) -> None:
        """Test TIMI STEMI score 8 - very high risk."""
        from src.domain.services.calculators import TimiStemiCalculator

        calc = TimiStemiCalculator()
        result = calc.calculate(
            age_years=80,  # +3 for age ≥75
            has_dm_htn_or_angina=True,  # +1
            systolic_bp_lt_100=False,
            heart_rate_gt_100=True,  # +2
            killip_class=2,  # +2 for Killip II-IV
            weight_lt_67kg=False,
            anterior_ste_or_lbbb=False,
            time_to_treatment_gt_4h=False
        )

        assert result.value is not None
        assert result.value == 8
        assert result.interpretation.summary is not None
        assert "very high" in result.interpretation.summary.lower()

    def test_hypotension_adds_3_points(self) -> None:
        """Test that SBP <100 adds 3 points."""
        from src.domain.services.calculators import TimiStemiCalculator

        calc = TimiStemiCalculator()
        result = calc.calculate(
            age_years=50,
            has_dm_htn_or_angina=False,
            systolic_bp_lt_100=True,  # +3
            heart_rate_gt_100=False,
            killip_class=1,
            weight_lt_67kg=False,
            anterior_ste_or_lbbb=False,
            time_to_treatment_gt_4h=False
        )

        assert result.value is not None
        assert result.value == 3
        assert result.calculation_details is not None
        assert result.calculation_details["component_scores"]["systolic_bp_lt_100"] == 3

    def test_killip_class_validation(self) -> None:
        """Test Killip class must be 1-4."""
        from src.domain.services.calculators import TimiStemiCalculator

        calc = TimiStemiCalculator()

        with pytest.raises(ValueError):
            calc.calculate(
                age_years=50,
                has_dm_htn_or_angina=False,
                systolic_bp_lt_100=False,
                heart_rate_gt_100=False,
                killip_class=5,  # Invalid
                weight_lt_67kg=False,
                anterior_ste_or_lbbb=False,
                time_to_treatment_gt_4h=False
            )

    def test_cardiogenic_shock_scenario(self) -> None:
        """Test typical cardiogenic shock patient (high score)."""
        from src.domain.services.calculators import TimiStemiCalculator

        calc = TimiStemiCalculator()
        result = calc.calculate(
            age_years=78,  # +3
            has_dm_htn_or_angina=True,  # +1
            systolic_bp_lt_100=True,  # +3
            heart_rate_gt_100=True,  # +2
            killip_class=4,  # +2 (cardiogenic shock)
            weight_lt_67kg=True,  # +1
            anterior_ste_or_lbbb=True,  # +1
            time_to_treatment_gt_4h=True  # +1
        )

        assert result.value is not None
        assert result.value == 14  # Maximum score
        assert result.interpretation.summary is not None
        assert "very high" in result.interpretation.summary.lower()

    def test_tool_id(self) -> None:
        """Test tool ID is correct."""
        from src.domain.services.calculators import TimiStemiCalculator

        calc = TimiStemiCalculator()
        assert calc.tool_id == "timi_stemi"

    def test_has_references(self) -> None:
        """Test that TIMI STEMI includes Morrow 2000 reference."""
        from src.domain.services.calculators import TimiStemiCalculator

        calc = TimiStemiCalculator()
        result = calc.calculate(
            age_years=50,
            has_dm_htn_or_angina=False,
            systolic_bp_lt_100=False,
            heart_rate_gt_100=False,
            killip_class=1,
            weight_lt_67kg=False,
            anterior_ste_or_lbbb=False,
            time_to_treatment_gt_4h=False
        )

        assert result.references is not None
        assert len(result.references) >= 1
        ref_text = str(result.references[0])
        assert "Morrow" in ref_text or "11044416" in ref_text


class TestRockallScoreCalculator:
    """Tests for Rockall Score (Upper GI Bleeding Risk) Calculator."""

    def test_low_risk_young_stable(self) -> None:
        """Test Rockall score for young stable patient - low risk."""
        from src.domain.services.calculators import RockallScoreCalculator

        calc = RockallScoreCalculator()
        result = calc.calculate(
            age_years=45,  # 0 pts (<60)
            shock_status="none",  # 0 pts
            comorbidity="none",  # 0 pts
            diagnosis="mallory_weiss_no_lesion",  # 0 pts
            stigmata_of_recent_hemorrhage="none_or_dark_spot"  # 0 pts
        )

        assert result.value is not None
        assert result.value == 0
        assert result.interpretation.summary is not None
        assert "low" in result.interpretation.summary.lower()

    def test_elderly_hypotensive_high_risk(self) -> None:
        """Test Rockall score for elderly hypotensive with malignancy - high risk."""
        from src.domain.services.calculators import RockallScoreCalculator

        calc = RockallScoreCalculator()
        result = calc.calculate(
            age_years=82,  # 2 pts (≥80)
            shock_status="hypotension",  # 2 pts
            comorbidity="renal_liver_malignancy",  # 3 pts
            diagnosis="gi_malignancy",  # 2 pts
            stigmata_of_recent_hemorrhage="blood_clot_visible_vessel"  # 2 pts
        )

        assert result.value is not None
        assert result.value == 11  # Maximum full Rockall
        assert result.interpretation.summary is not None
        assert "high" in result.interpretation.summary.lower()

    def test_typical_peptic_ulcer_moderate_risk(self) -> None:
        """Test typical peptic ulcer bleeding scenario."""
        from src.domain.services.calculators import RockallScoreCalculator

        calc = RockallScoreCalculator()
        result = calc.calculate(
            age_years=65,  # 1 pt (60-79)
            shock_status="tachycardia",  # 1 pt
            comorbidity="cardiac_major",  # 2 pts (has CHF)
            diagnosis="other_diagnosis",  # 1 pt (peptic ulcer)
            stigmata_of_recent_hemorrhage="blood_clot_visible_vessel"  # 2 pts
        )

        assert result.value is not None
        assert result.value == 7  # 1+1+2+1+2 = 7
        assert result.calculation_details is not None
        assert result.calculation_details["component_scores"]["stigmata"] == 2

    def test_mallory_weiss_low_risk(self) -> None:
        """Test Mallory-Weiss tear with no bleeding stigmata."""
        from src.domain.services.calculators import RockallScoreCalculator

        calc = RockallScoreCalculator()
        result = calc.calculate(
            age_years=35,  # 0 pts
            shock_status="none",  # 0 pts
            comorbidity="none",  # 0 pts
            diagnosis="mallory_weiss_no_lesion",  # 0 pts
            stigmata_of_recent_hemorrhage="none_or_dark_spot"  # 0 pts
        )

        assert result.value is not None
        assert result.value == 0
        assert result.calculation_details is not None
        assert "0.0%" in result.calculation_details["mortality_risk"] or "0%" in result.calculation_details["mortality_risk"]

    def test_age_scoring_60_79(self) -> None:
        """Test age 60-79 gets 1 point."""
        from src.domain.services.calculators import RockallScoreCalculator

        calc = RockallScoreCalculator()
        result = calc.calculate(
            age_years=70,  # 1 pt
            shock_status="none",
            comorbidity="none",
            diagnosis="mallory_weiss_no_lesion",
            stigmata_of_recent_hemorrhage="none_or_dark_spot"
        )

        assert result.value is not None
        assert result.value == 1
        assert result.calculation_details is not None
        assert result.calculation_details["component_scores"]["age"] == 1

    def test_age_scoring_80_plus(self) -> None:
        """Test age ≥80 gets 2 points."""
        from src.domain.services.calculators import RockallScoreCalculator

        calc = RockallScoreCalculator()
        result = calc.calculate(
            age_years=85,  # 2 pts
            shock_status="none",
            comorbidity="none",
            diagnosis="mallory_weiss_no_lesion",
            stigmata_of_recent_hemorrhage="none_or_dark_spot"
        )

        assert result.value is not None
        assert result.value == 2
        assert result.calculation_details is not None
        assert result.calculation_details["component_scores"]["age"] == 2

    def test_clinical_score_pre_endoscopy(self) -> None:
        """Test that clinical (pre-endoscopy) score is calculated."""
        from src.domain.services.calculators import RockallScoreCalculator

        calc = RockallScoreCalculator()
        result = calc.calculate(
            age_years=75,  # 1 pt
            shock_status="hypotension",  # 2 pts
            comorbidity="cardiac_major",  # 2 pts
            diagnosis="gi_malignancy",  # 2 pts
            stigmata_of_recent_hemorrhage="blood_clot_visible_vessel"  # 2 pts
        )

        # Full score = 1+2+2+2+2 = 9
        # Clinical (pre-endoscopy) = 1+2+2 = 5
        assert result.value is not None
        assert result.value == 9
        assert result.calculation_details is not None
        assert result.calculation_details["clinical_score_pre_endoscopy"] == 5

    def test_tool_id(self) -> None:
        """Test tool ID is correct."""
        from src.domain.services.calculators import RockallScoreCalculator

        calc = RockallScoreCalculator()
        assert calc.tool_id == "rockall_score"

    def test_has_references(self) -> None:
        """Test that Rockall includes Rockall 1996 reference."""
        from src.domain.services.calculators import RockallScoreCalculator

        calc = RockallScoreCalculator()
        result = calc.calculate(
            age_years=50,
            shock_status="none",
            comorbidity="none",
            diagnosis="mallory_weiss_no_lesion",
            stigmata_of_recent_hemorrhage="none_or_dark_spot"
        )

        assert result.references is not None
        assert len(result.references) >= 1
        ref_text = str(result.references[0])
        assert "Rockall" in ref_text or "8675081" in ref_text

    def test_rebleeding_risk_included(self) -> None:
        """Test that rebleeding risk is included in output."""
        from src.domain.services.calculators import RockallScoreCalculator

        calc = RockallScoreCalculator()
        result = calc.calculate(
            age_years=85,
            shock_status="hypotension",
            comorbidity="renal_liver_malignancy",
            diagnosis="other_diagnosis",
            stigmata_of_recent_hemorrhage="blood_clot_visible_vessel"
        )

        assert result.calculation_details is not None
        assert "rebleed_risk" in result.calculation_details
        assert "%" in result.calculation_details["rebleed_risk"]
        assert "mortality_risk" in result.calculation_details


class TestFib4IndexCalculator:
    """Tests for FIB-4 Index (Liver Fibrosis) Calculator."""

    def test_low_risk_normal_values(self) -> None:
        """Test FIB-4 with normal values - low risk."""
        from src.domain.services.calculators import Fib4IndexCalculator

        calc = Fib4IndexCalculator()
        result = calc.calculate(
            age_years=40,
            ast=25,  # Normal
            alt=30,  # Normal
            platelet_count=250  # Normal
        )

        # FIB-4 = (40 × 25) / (250 × √30) = 1000 / 1369.3 ≈ 0.73
        assert result.value is not None
        assert result.value < 1.30
        assert result.interpretation.summary is not None
        assert "low" in result.interpretation.summary.lower()
        assert result.calculation_details is not None
        assert result.calculation_details["fibrosis_prediction"] == "F0-F1 (No to minimal fibrosis)"

    def test_high_risk_cirrhotic(self) -> None:
        """Test FIB-4 with cirrhotic pattern - high risk."""
        from src.domain.services.calculators import Fib4IndexCalculator

        calc = Fib4IndexCalculator()
        result = calc.calculate(
            age_years=55,
            ast=85,  # Elevated
            alt=60,  # Elevated
            platelet_count=90  # Low (cirrhosis)
        )

        # FIB-4 = (55 × 85) / (90 × √60) = 4675 / 697.1 ≈ 6.71
        assert result.value is not None
        assert result.value > 2.67
        assert result.interpretation.summary is not None
        assert "high" in result.interpretation.summary.lower()
        assert result.calculation_details is not None
        assert "F3-F4" in result.calculation_details["fibrosis_prediction"]

    def test_indeterminate_zone(self) -> None:
        """Test FIB-4 in indeterminate zone."""
        from src.domain.services.calculators import Fib4IndexCalculator

        calc = Fib4IndexCalculator()
        result = calc.calculate(
            age_years=50,
            ast=45,
            alt=50,
            platelet_count=180
        )

        # FIB-4 = (50 × 45) / (180 × √50) = 2250 / 1272.8 ≈ 1.77
        assert result.value is not None
        assert 1.30 <= result.value <= 2.67
        assert result.interpretation.summary is not None
        assert "indeterminate" in result.interpretation.summary.lower()

    def test_age_adjusted_cutoffs_elderly(self) -> None:
        """Test that age-adjusted cutoffs are used for age >65."""
        from src.domain.services.calculators import Fib4IndexCalculator

        calc = Fib4IndexCalculator()
        result = calc.calculate(
            age_years=70,
            ast=35,
            alt=30,
            platelet_count=150
        )

        # Verify age-adjusted cutoffs are used
        assert result.calculation_details is not None
        assert result.calculation_details["using_age_adjusted_cutoffs"] is True
        assert result.calculation_details is not None
        assert result.calculation_details["low_cutoff"] == 2.0
        assert result.calculation_details is not None
        assert result.calculation_details["high_cutoff"] == 3.25

    def test_standard_cutoffs_younger(self) -> None:
        """Test that standard cutoffs are used for age ≤65."""
        from src.domain.services.calculators import Fib4IndexCalculator

        calc = Fib4IndexCalculator()
        result = calc.calculate(
            age_years=45,
            ast=30,
            alt=35,
            platelet_count=200
        )

        assert result.calculation_details is not None
        assert result.calculation_details["using_age_adjusted_cutoffs"] is False
        assert result.calculation_details is not None
        assert result.calculation_details["low_cutoff"] == 1.30
        assert result.calculation_details is not None
        assert result.calculation_details["high_cutoff"] == 2.67

    def test_formula_calculation(self) -> None:
        """Test the FIB-4 formula calculation."""
        import math

        from src.domain.services.calculators import Fib4IndexCalculator

        calc = Fib4IndexCalculator()
        result = calc.calculate(
            age_years=50,
            ast=40,
            alt=36,  # Perfect square for easy calculation
            platelet_count=200
        )

        # FIB-4 = (50 × 40) / (200 × √36) = 2000 / (200 × 6) = 2000 / 1200 = 1.67
        expected = round((50 * 40) / (200 * math.sqrt(36)), 2)
        assert result.value is not None
        assert result.value == expected

    def test_nafld_typical_case(self) -> None:
        """Test typical NAFLD patient scenario."""
        from src.domain.services.calculators import Fib4IndexCalculator

        calc = Fib4IndexCalculator()
        result = calc.calculate(
            age_years=52,
            ast=48,
            alt=62,  # ALT > AST typical for NAFLD
            platelet_count=195
        )

        # Result should be in determinate range
        assert result.value is not None
        assert result.value > 0
        assert result.calculation_details is not None
        assert "fibrosis_prediction" in result.calculation_details

    def test_hcv_high_risk(self) -> None:
        """Test HCV patient with advanced fibrosis."""
        from src.domain.services.calculators import Fib4IndexCalculator

        calc = Fib4IndexCalculator()
        result = calc.calculate(
            age_years=58,
            ast=95,  # AST > ALT typical for cirrhosis
            alt=65,
            platelet_count=75  # Low platelets
        )

        assert result.value is not None
        assert result.value > 2.67
        assert result.interpretation.risk_level is not None
        assert RiskLevel.HIGH.value in str(result.interpretation.risk_level.value)

    def test_tool_id(self) -> None:
        """Test tool ID is correct."""
        from src.domain.services.calculators import Fib4IndexCalculator

        calc = Fib4IndexCalculator()
        assert calc.tool_id == "fib4_index"

    def test_has_references(self) -> None:
        """Test that FIB-4 includes Sterling 2006 reference."""
        from src.domain.services.calculators import Fib4IndexCalculator

        calc = Fib4IndexCalculator()
        result = calc.calculate(
            age_years=45,
            ast=30,
            alt=35,
            platelet_count=220
        )

        assert result.references is not None
        assert len(result.references) >= 1
        ref_text = str(result.references[0])
        assert "Sterling" in ref_text or "16729309" in ref_text


# Import needed for test
from src.domain.value_objects.interpretation import RiskLevel

