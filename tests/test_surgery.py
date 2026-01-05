from typing import Any
"""Tests for Surgery/Perioperative Calculators"""
import pytest


class TestCapriniVteCalculator:
    """Comprehensive tests for Caprini VTE Risk Assessment Score"""

    @pytest.fixture
    def calc(self) -> Any:
        from src.domain.services.calculators import CapriniVteCalculator
        return CapriniVteCalculator()

    def test_tool_id(self, calc: Any) -> None:
        assert calc.tool_id == "caprini_vte"

    # ========================================================================
    # Age Scoring Tests (1 point each threshold)
    # ========================================================================

    def test_age_under_41(self, calc: Any) -> None:
        """Age < 41: 0 points"""
        result = calc.calculate(age_years=30)
        assert result.value is not None
        assert result.value == 0

    def test_age_41_to_60(self, calc: Any) -> None:
        """Age 41-60: 1 point"""
        result = calc.calculate(age_years=50)
        assert result.value is not None
        assert result.value == 1

    def test_age_61_to_74(self, calc: Any) -> None:
        """Age 61-74: 2 points"""
        result = calc.calculate(age_years=65)
        assert result.value is not None
        assert result.value == 2

    def test_age_75_plus(self, calc: Any) -> None:
        """Age >= 75: 3 points"""
        result = calc.calculate(age_years=80)
        assert result.value is not None
        assert result.value == 3

    # ========================================================================
    # 1-Point Risk Factors
    # ========================================================================

    def test_minor_surgery(self, calc: Any) -> None:
        """Minor surgery: +1 point"""
        result = calc.calculate(age_years=30, minor_surgery=True)
        assert result.value is not None
        assert result.value == 1

    def test_varicose_veins(self, calc: Any) -> None:
        """Varicose veins: +1 point"""
        result = calc.calculate(age_years=30, varicose_veins=True)
        assert result.value is not None
        assert result.value == 1

    def test_ibd(self, calc: Any) -> None:
        """Inflammatory bowel disease: +1 point"""
        result = calc.calculate(age_years=30, inflammatory_bowel_disease=True)
        assert result.value is not None
        assert result.value == 1

    def test_swollen_legs(self, calc: Any) -> None:
        """Swollen legs: +1 point"""
        result = calc.calculate(age_years=30, swollen_legs=True)
        assert result.value is not None
        assert result.value == 1

    def test_obesity(self, calc: Any) -> None:
        """BMI > 25: +1 point"""
        result = calc.calculate(age_years=30, obesity_bmi_gt_25=True)
        assert result.value is not None
        assert result.value == 1

    def test_acute_mi(self, calc: Any) -> None:
        """Acute MI: +1 point"""
        result = calc.calculate(age_years=30, acute_mi=True)
        assert result.value is not None
        assert result.value == 1

    def test_chf(self, calc: Any) -> None:
        """CHF < 1 month: +1 point"""
        result = calc.calculate(age_years=30, chf_lt_1mo=True)
        assert result.value is not None
        assert result.value == 1

    def test_sepsis(self, calc: Any) -> None:
        """Sepsis < 1 month: +1 point"""
        result = calc.calculate(age_years=30, sepsis_lt_1mo=True)
        assert result.value is not None
        assert result.value == 1

    def test_lung_disease(self, calc: Any) -> None:
        """Serious lung disease: +1 point"""
        result = calc.calculate(age_years=30, lung_disease=True)
        assert result.value is not None
        assert result.value == 1

    def test_copd(self, calc: Any) -> None:
        """COPD: +1 point"""
        result = calc.calculate(age_years=30, copd=True)
        assert result.value is not None
        assert result.value == 1

    def test_bed_rest_medical(self, calc: Any) -> None:
        """Medical patient bed rest: +1 point"""
        result = calc.calculate(age_years=30, bed_rest_medical=True)
        assert result.value is not None
        assert result.value == 1

    def test_leg_cast_or_brace(self, calc: Any) -> None:
        """Leg cast or brace: +1 point"""
        result = calc.calculate(age_years=30, leg_cast_or_brace=True)
        assert result.value is not None
        assert result.value == 1

    def test_central_venous_access(self, calc: Any) -> None:
        """Central venous access: +1 point"""
        result = calc.calculate(age_years=30, central_venous_access=True)
        assert result.value is not None
        assert result.value == 1

    # ========================================================================
    # 2-Point Risk Factors
    # ========================================================================

    def test_major_surgery(self, calc: Any) -> None:
        """Major surgery > 45 min: +2 points"""
        result = calc.calculate(age_years=30, major_surgery=True)
        assert result.value is not None
        assert result.value == 2

    def test_laparoscopic_surgery(self, calc: Any) -> None:
        """Laparoscopic surgery > 45 min: +2 points"""
        result = calc.calculate(age_years=30, laparoscopic_surgery_gt_45min=True)
        assert result.value is not None
        assert result.value == 2

    def test_arthroscopic_surgery(self, calc: Any) -> None:
        """Arthroscopic surgery: +2 points"""
        result = calc.calculate(age_years=30, arthroscopic_surgery=True)
        assert result.value is not None
        assert result.value == 2

    def test_bed_confined(self, calc: Any) -> None:
        """Bed confined > 72 hours: +2 points"""
        result = calc.calculate(age_years=30, bed_confined_gt_72hr=True)
        assert result.value is not None
        assert result.value == 2

    def test_immobilizing_cast(self, calc: Any) -> None:
        """Immobilizing cast < 1 month: +2 points"""
        result = calc.calculate(age_years=30, immobilizing_cast_lt_1mo=True)
        assert result.value is not None
        assert result.value == 2

    def test_malignancy(self, calc: Any) -> None:
        """Malignancy: +2 points"""
        result = calc.calculate(age_years=30, malignancy=True)
        assert result.value is not None
        assert result.value == 2

    # ========================================================================
    # 3-Point Risk Factors
    # ========================================================================

    def test_history_dvt_pe(self, calc: Any) -> None:
        """History of DVT/PE: +3 points"""
        result = calc.calculate(age_years=30, history_dvt_pe=True)
        assert result.value is not None
        assert result.value == 3

    def test_family_history(self, calc: Any) -> None:
        """Family history of thrombosis: +3 points"""
        result = calc.calculate(age_years=30, family_history_thrombosis=True)
        assert result.value is not None
        assert result.value == 3

    def test_factor_v_leiden(self, calc: Any) -> None:
        """Factor V Leiden: +3 points"""
        result = calc.calculate(age_years=30, factor_v_leiden=True)
        assert result.value is not None
        assert result.value == 3

    def test_prothrombin_mutation(self, calc: Any) -> None:
        """Prothrombin 20210A mutation: +3 points"""
        result = calc.calculate(age_years=30, prothrombin_20210a=True)
        assert result.value is not None
        assert result.value == 3

    def test_lupus_anticoagulant(self, calc: Any) -> None:
        """Lupus anticoagulant: +3 points"""
        result = calc.calculate(age_years=30, lupus_anticoagulant=True)
        assert result.value is not None
        assert result.value == 3

    def test_anticardiolipin(self, calc: Any) -> None:
        """Anticardiolipin antibodies: +3 points"""
        result = calc.calculate(age_years=30, anticardiolipin_antibodies=True)
        assert result.value is not None
        assert result.value == 3

    def test_elevated_homocysteine(self, calc: Any) -> None:
        """Elevated homocysteine: +3 points"""
        result = calc.calculate(age_years=30, elevated_homocysteine=True)
        assert result.value is not None
        assert result.value == 3

    def test_hit_history(self, calc: Any) -> None:
        """HIT history: +3 points"""
        result = calc.calculate(age_years=30, hit_history=True)
        assert result.value is not None
        assert result.value == 3

    def test_other_thrombophilia(self, calc: Any) -> None:
        """Other thrombophilia: +3 points"""
        result = calc.calculate(age_years=30, other_thrombophilia=True)
        assert result.value is not None
        assert result.value == 3

    # ========================================================================
    # 5-Point Risk Factors
    # ========================================================================

    def test_stroke(self, calc: Any) -> None:
        """Stroke < 1 month: +5 points"""
        result = calc.calculate(age_years=30, stroke_lt_1mo=True)
        assert result.value is not None
        assert result.value == 5

    def test_elective_arthroplasty(self, calc: Any) -> None:
        """Elective arthroplasty: +5 points"""
        result = calc.calculate(age_years=30, elective_arthroplasty=True)
        assert result.value is not None
        assert result.value == 5

    def test_hip_fracture(self, calc: Any) -> None:
        """Hip/pelvis/leg fracture < 1 month: +5 points"""
        result = calc.calculate(age_years=30, hip_pelvis_leg_fracture_lt_1mo=True)
        assert result.value is not None
        assert result.value == 5

    def test_spinal_cord_injury(self, calc: Any) -> None:
        """Spinal cord injury < 1 month: +5 points"""
        result = calc.calculate(age_years=30, spinal_cord_injury_lt_1mo=True)
        assert result.value is not None
        assert result.value == 5

    # ========================================================================
    # Female-Specific Risk Factors (+1 each)
    # ========================================================================

    def test_female_oral_contraceptives(self, calc: Any) -> None:
        """Female on oral contraceptives/HRT: +1 point"""
        result = calc.calculate(age_years=30, female=True, oral_contraceptives_or_hrt=True)
        assert result.value is not None
        assert result.value == 1

    def test_female_pregnant(self, calc: Any) -> None:
        """Female pregnant or postpartum: +1 point"""
        result = calc.calculate(age_years=30, female=True, pregnancy_or_postpartum=True)
        assert result.value is not None
        assert result.value == 1

    def test_female_pregnancy_loss(self, calc: Any) -> None:
        """Female with pregnancy loss history: +1 point"""
        result = calc.calculate(age_years=30, female=True, pregnancy_loss_history=True)
        assert result.value is not None
        assert result.value == 1

    # ========================================================================
    # Risk Category Tests
    # ========================================================================

    def test_very_low_risk(self, calc: Any) -> None:
        """Score 0 = Very low risk"""
        result = calc.calculate(age_years=30)
        assert result.value is not None
        assert result.value == 0
        assert result.interpretation.summary is not None
        assert "very low" in result.interpretation.summary.lower() or "low" in result.interpretation.summary.lower()

    def test_low_risk(self, calc: Any) -> None:
        """Score 1-2 = Low risk"""
        result = calc.calculate(age_years=50)  # Age 41-60 = 1 point
        assert result.value is not None
        assert result.value == 1

    def test_moderate_risk(self, calc: Any) -> None:
        """Score 3-4 = Moderate risk"""
        result = calc.calculate(age_years=30, history_dvt_pe=True)  # 3 points
        assert result.value is not None
        assert result.value == 3

    def test_high_risk(self, calc: Any) -> None:
        """Score >= 5 = High risk"""
        result = calc.calculate(age_years=30, stroke_lt_1mo=True)  # 5 points
        assert result.value is not None
        assert result.value == 5

    # ========================================================================
    # Complex Combinations
    # ========================================================================

    def test_multiple_1_point_factors(self, calc: Any) -> None:
        """Multiple 1-point factors accumulate"""
        result = calc.calculate(
            age_years=30,
            minor_surgery=True,  # +1
            varicose_veins=True,  # +1
            obesity_bmi_gt_25=True,  # +1
        )
        assert result.value is not None
        assert result.value == 3

    def test_combined_surgery_patient(self, calc: Any) -> None:
        """Typical surgical patient with multiple risk factors"""
        result = calc.calculate(
            age_years=65,  # 2 points
            major_surgery=True,  # 2 points
            malignancy=True,  # 2 points
            bed_confined_gt_72hr=True,  # 2 points
        )
        assert result.value is not None
        assert result.value == 8

    def test_thrombophilia_patient(self, calc: Any) -> None:
        """Patient with thrombophilia"""
        result = calc.calculate(
            age_years=45,  # 1 point
            factor_v_leiden=True,  # 3 points
            history_dvt_pe=True,  # 3 points
        )
        assert result.value is not None
        assert result.value == 7

    def test_high_risk_orthopedic(self, calc: Any) -> None:
        """High-risk orthopedic surgery patient"""
        result = calc.calculate(
            age_years=75,  # 3 points
            elective_arthroplasty=True,  # 5 points
            obesity_bmi_gt_25=True,  # 1 point
        )
        assert result.value is not None
        assert result.value == 9

    def test_metadata(self, calc: Any) -> None:
        """Verify metadata is correct"""
        meta = calc.metadata
        assert meta.tool_id == "caprini_vte"
        assert meta.name is not None
        assert "VTE" in meta.name or "Caprini" in meta.name
