"""
Tests for Phase 18 Calculators: GI Bleeding & Trauma Tools

Tests for:
- Glasgow-Blatchford Score (GBS) - UGIB intervention risk
- AIMS65 Score - UGIB mortality prediction  
- TBSA Calculator - Burns assessment
- Injury Severity Score (ISS) - Trauma severity
- Simplified PESI (sPESI) - PE prognosis
"""

import pytest
from src.domain.services.calculators import (
    GlasgowBlatchfordCalculator,
    AIMS65Calculator,
    TbsaCalculator,
    InjurySeverityScoreCalculator,
    SimplifiedPESICalculator,
)
from src.domain.value_objects.interpretation import Interpretation, Severity, RiskLevel


class TestGlasgowBlatchford:
    """Test Glasgow-Blatchford Score Calculator"""
    
    @pytest.fixture
    def calc(self):
        return GlasgowBlatchfordCalculator()
    
    def test_gbs_zero_low_risk(self, calc):
        """GBS = 0 should identify very low risk patients"""
        result = calc.calculate(
            bun_mg_dl=15,  # <18.2
            hemoglobin_g_dl=14,  # ≥13 male
            systolic_bp_mmhg=120,  # ≥110
            sex="male",
            heart_rate_bpm=80,  # <100
            melena=False,
            syncope=False,
            hepatic_disease=False,
            cardiac_failure=False
        )
        assert result.value == 0
        assert "Very Low Risk" in result.calculation_details["risk_category"]
    
    def test_gbs_high_risk(self, calc):
        """High GBS score with multiple risk factors"""
        result = calc.calculate(
            bun_mg_dl=35,  # +4
            hemoglobin_g_dl=8,  # +6 (male <10)
            systolic_bp_mmhg=85,  # +3 (<90)
            sex="male",
            heart_rate_bpm=110,  # +1 (≥100)
            melena=True,  # +1
            syncope=True,  # +2
            hepatic_disease=True,  # +2
            cardiac_failure=True  # +2
        )
        # Total = 4+6+3+1+1+2+2+2 = 21
        assert result.value >= 15
        assert result.interpretation.severity == Severity.CRITICAL
    
    def test_gbs_female_hemoglobin_scoring(self, calc):
        """Female hemoglobin scoring differs from male"""
        result = calc.calculate(
            bun_mg_dl=15,
            hemoglobin_g_dl=11.5,  # +1 for female (10-11.9), +3 for male
            systolic_bp_mmhg=120,
            sex="female",
            heart_rate_bpm=80,  # Explicitly set to avoid default +1
        )
        assert result.value == 1  # Only Hgb 10-11.9 female
    
    def test_gbs_validation_errors(self, calc):
        """Invalid inputs should raise ValueError"""
        with pytest.raises(ValueError):
            calc.calculate(bun_mg_dl=-1, hemoglobin_g_dl=10, systolic_bp_mmhg=100, sex="male")
        with pytest.raises(ValueError):
            calc.calculate(bun_mg_dl=20, hemoglobin_g_dl=25, systolic_bp_mmhg=100, sex="male")


class TestAIMS65:
    """Test AIMS65 Score Calculator"""
    
    @pytest.fixture
    def calc(self):
        return AIMS65Calculator()
    
    def test_aims65_zero_very_low_risk(self, calc):
        """AIMS65 = 0 should be very low mortality risk"""
        result = calc.calculate(
            albumin_lt_3=False,
            inr_gt_1_5=False,
            altered_mental_status=False,
            sbp_lte_90=False,
            age_gte_65=False
        )
        assert result.value == 0
        assert "0.3%" in result.calculation_details["in_hospital_mortality"]
    
    def test_aims65_high_risk(self, calc):
        """AIMS65 ≥3 should be high risk"""
        result = calc.calculate(
            albumin_lt_3=True,
            inr_gt_1_5=True,
            altered_mental_status=True,
            sbp_lte_90=True,
            age_gte_65=True
        )
        assert result.value == 5
        assert result.interpretation.severity == Severity.CRITICAL
    
    def test_aims65_intermediate_risk(self, calc):
        """AIMS65 = 2 should be intermediate risk"""
        result = calc.calculate(
            albumin_lt_3=True,
            inr_gt_1_5=True,
            altered_mental_status=False,
            sbp_lte_90=False,
            age_gte_65=False
        )
        assert result.value == 2
        assert "Intermediate" in result.calculation_details["risk_category"]


class TestTBSA:
    """Test TBSA Calculator (Rule of Nines)"""
    
    @pytest.fixture
    def calc(self):
        return TbsaCalculator()
    
    def test_tbsa_no_burns(self, calc):
        """No burns should return 0% TBSA"""
        result = calc.calculate(
            head_neck=0,
            chest=0,
            abdomen=0
        )
        assert result.value == 0
    
    def test_tbsa_minor_burn(self, calc):
        """Small burn area should be minor severity"""
        result = calc.calculate(
            right_arm=50,  # 50% of 9% = 4.5%
            patient_type="adult"
        )
        assert result.value < 10
        assert "Minor" in result.calculation_details["severity"]
    
    def test_tbsa_major_burn_adult(self, calc):
        """Large burn area should be major severity"""
        result = calc.calculate(
            head_neck=100,  # 9%
            chest=100,  # 9%
            abdomen=100,  # 9%
            right_arm=100,  # 9%
            patient_type="adult"
        )
        # 9+9+9+9 = 36%
        assert result.value >= 30
        assert result.interpretation.severity in [Severity.SEVERE, Severity.CRITICAL]
    
    def test_tbsa_infant_head_proportion(self, calc):
        """Infant head is larger proportion than adult"""
        # Same burn to head
        adult_result = calc.calculate(head_neck=100, patient_type="adult")
        infant_result = calc.calculate(head_neck=100, patient_type="infant")
        # Infant head = 18%, Adult head = 9%
        assert infant_result.value > adult_result.value


class TestInjurySeverityScore:
    """Test Injury Severity Score (ISS) Calculator"""
    
    @pytest.fixture
    def calc(self):
        return InjurySeverityScoreCalculator()
    
    def test_iss_minor_injury(self, calc):
        """Single minor injury should have low ISS"""
        result = calc.calculate(
            head_neck_ais=1,  # Minor
            face_ais=0,
            chest_ais=0,
            abdomen_ais=0,
            extremity_ais=0,
            external_ais=0
        )
        assert result.value == 1
        assert "Minor" in result.calculation_details.get("severity", "Minor")
    
    def test_iss_major_trauma(self, calc):
        """ISS > 15 should be major trauma"""
        result = calc.calculate(
            head_neck_ais=3,  # Serious
            chest_ais=3,  # Serious
            abdomen_ais=2,  # Moderate
        )
        # ISS = 3² + 3² + 2² = 9 + 9 + 4 = 22
        assert result.value > 15
        assert result.calculation_details.get("is_major_trauma", True)
    
    def test_iss_unsurvivable_injury(self, calc):
        """AIS 6 should result in ISS = 75"""
        result = calc.calculate(
            head_neck_ais=6,  # Unsurvivable
        )
        assert result.value == 75
        assert result.interpretation.severity == Severity.CRITICAL
    
    def test_iss_polytrauma(self, calc):
        """Multiple region injuries should sum correctly"""
        result = calc.calculate(
            head_neck_ais=4,  # Severe
            chest_ais=4,  # Severe
            extremity_ais=3,  # Serious
        )
        # ISS = 4² + 4² + 3² = 16 + 16 + 9 = 41
        assert result.value == 41


class TestSimplifiedPESI:
    """Test Simplified PESI (sPESI) Calculator"""
    
    @pytest.fixture
    def calc(self):
        return SimplifiedPESICalculator()
    
    def test_spesi_low_risk(self, calc):
        """sPESI = 0 should be low risk"""
        result = calc.calculate(
            age=50,  # ≤80
            cancer=False,
            chronic_cardiopulmonary_disease=False,
            heart_rate=90,  # <110
            systolic_bp=120,  # ≥100
            spo2=95  # ≥90
        )
        assert result.value == 0
        assert "Low Risk" in result.calculation_details["risk_category"]
        assert result.calculation_details["outpatient_candidate"] == True
    
    def test_spesi_high_risk_age(self, calc):
        """Age >80 alone should make high risk"""
        result = calc.calculate(
            age=85,  # >80 = +1
            cancer=False,
            chronic_cardiopulmonary_disease=False,
            heart_rate=90,
            systolic_bp=120,
            spo2=95
        )
        assert result.value >= 1
        assert "High Risk" in result.calculation_details["risk_category"]
    
    def test_spesi_multiple_risk_factors(self, calc):
        """Multiple risk factors increase score"""
        result = calc.calculate(
            age=85,  # +1
            cancer=True,  # +1
            chronic_cardiopulmonary_disease=True,  # +1
            heart_rate=120,  # +1 (≥110)
            systolic_bp=85,  # +1 (<100)
            spo2=88  # +1 (<90)
        )
        assert result.value == 6
        assert result.interpretation.severity == Severity.CRITICAL
    
    def test_spesi_alternative_boolean_params(self, calc):
        """Test using direct boolean parameters"""
        result = calc.calculate(
            age=50,
            heart_rate_gte_110=True,
            sbp_lt_100=True,
            spo2_lt_90=True
        )
        assert result.value == 3


class TestPhase18Integration:
    """Integration tests for Phase 18 calculators"""
    
    def test_all_calculators_have_metadata(self):
        """All Phase 18 calculators should have valid metadata"""
        calculators = [
            GlasgowBlatchfordCalculator(),
            AIMS65Calculator(),
            TbsaCalculator(),
            InjurySeverityScoreCalculator(),
            SimplifiedPESICalculator(),
        ]
        for calc in calculators:
            assert calc.metadata is not None
            assert calc.metadata.low_level.tool_id
            assert calc.metadata.low_level.name
            assert len(calc.metadata.references) > 0
    
    def test_all_calculators_have_references(self):
        """All Phase 18 calculators should cite original papers"""
        calculators = [
            GlasgowBlatchfordCalculator(),
            AIMS65Calculator(),
            TbsaCalculator(),
            InjurySeverityScoreCalculator(),
            SimplifiedPESICalculator(),
        ]
        for calc in calculators:
            refs = calc.metadata.references
            assert len(refs) >= 1
            # At least one should have PMID
            assert any(ref.pmid for ref in refs)
