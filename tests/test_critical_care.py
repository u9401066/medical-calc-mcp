"""
Tests for Critical Care/ICU Calculators

Tests APACHE II, RASS, SOFA, qSOFA, NEWS, GCS, and CAM-ICU calculators.
"""

import pytest


class TestApacheIiCalculator:
    """Tests for APACHE II Score."""

    def test_low_acuity_patient(self):
        """Test APACHE II for low acuity patient."""
        from src.domain.services.calculators import ApacheIiCalculator
        
        calc = ApacheIiCalculator()
        result = calc.calculate(
            temperature=37.0,
            mean_arterial_pressure=85,
            heart_rate=80,
            respiratory_rate=16,
            pao2_or_aado2=80,
            fio2=0.21,
            arterial_ph=7.40,
            sodium=140,
            potassium=4.0,
            creatinine=1.0,
            acute_renal_failure=False,
            hematocrit=40,
            wbc=8,
            gcs=15,
            age=50,
            chronic_health="none",
        )
        
        assert result.value is not None
        assert result.value >= 0

    def test_high_acuity_patient(self):
        """Test APACHE II for high acuity patient."""
        from src.domain.services.calculators import ApacheIiCalculator
        
        calc = ApacheIiCalculator()
        result = calc.calculate(
            temperature=40.0,
            mean_arterial_pressure=50,
            heart_rate=150,
            respiratory_rate=40,
            pao2_or_aado2=55,
            fio2=1.0,
            arterial_ph=7.15,
            sodium=160,
            potassium=6.5,
            creatinine=4.0,
            acute_renal_failure=True,
            hematocrit=20,
            wbc=40,
            gcs=6,
            age=75,
            chronic_health="immunocompromised",
        )
        
        assert result.value is not None
        assert result.value > 20  # High severity

    def test_tool_id(self):
        """Test tool ID is correct."""
        from src.domain.services.calculators import ApacheIiCalculator
        
        calc = ApacheIiCalculator()
        assert calc.tool_id == "apache_ii"


class TestRassCalculator:
    """Tests for Richmond Agitation-Sedation Scale (RASS)."""

    def test_rass_combative(self):
        """Test RASS +4 - combative."""
        from src.domain.services.calculators import RassCalculator
        
        calc = RassCalculator()
        result = calc.calculate(score=4)
        
        assert result.value == 4

    def test_rass_alert_calm(self):
        """Test RASS 0 - alert and calm."""
        from src.domain.services.calculators import RassCalculator
        
        calc = RassCalculator()
        result = calc.calculate(score=0)
        
        assert result.value == 0
        assert "alert" in result.interpretation.summary.lower()

    def test_rass_deep_sedation(self):
        """Test RASS -4 - deep sedation."""
        from src.domain.services.calculators import RassCalculator
        
        calc = RassCalculator()
        result = calc.calculate(score=-4)
        
        assert result.value == -4

    def test_rass_unarousable(self):
        """Test RASS -5 - unarousable."""
        from src.domain.services.calculators import RassCalculator
        
        calc = RassCalculator()
        result = calc.calculate(score=-5)
        
        assert result.value == -5

    def test_tool_id(self):
        """Test tool ID is correct."""
        from src.domain.services.calculators import RassCalculator
        
        calc = RassCalculator()
        assert calc.tool_id == "rass"


class TestSofaCalculator:
    """Tests for Sequential Organ Failure Assessment (SOFA) Score."""

    def test_sofa_no_organ_failure(self):
        """Test SOFA with no organ failure."""
        from src.domain.services.calculators import SofaScoreCalculator
        
        calc = SofaScoreCalculator()
        result = calc.calculate(
            pao2_fio2_ratio=450,
            platelets=200,
            bilirubin=0.5,
            cardiovascular="no_hypotension",
            gcs=15,
            creatinine=0.8,
        )
        
        assert result.value == 0

    def test_sofa_moderate(self):
        """Test SOFA with moderate organ dysfunction."""
        from src.domain.services.calculators import SofaScoreCalculator
        
        calc = SofaScoreCalculator()
        result = calc.calculate(
            pao2_fio2_ratio=250,
            platelets=80,
            bilirubin=3.0,
            cardiovascular="dopamine_lte_5",
            gcs=12,
            creatinine=2.5,
        )
        
        assert result.value is not None
        assert result.value > 0

    def test_sofa_severe(self):
        """Test SOFA with severe organ dysfunction."""
        from src.domain.services.calculators import SofaScoreCalculator
        
        calc = SofaScoreCalculator()
        result = calc.calculate(
            pao2_fio2_ratio=100,
            platelets=20,
            bilirubin=12.0,
            cardiovascular="dopamine_gt_15_or_epi_gt_0_1",
            gcs=6,
            creatinine=5.0,
        )
        
        assert result.value is not None
        assert result.value >= 10  # High severity

    def test_tool_id(self):
        """Test tool ID is correct."""
        from src.domain.services.calculators import SofaScoreCalculator
        
        calc = SofaScoreCalculator()
        assert calc.tool_id == "sofa"


class TestQsofaCalculator:
    """Tests for Quick SOFA (qSOFA) Score."""

    def test_qsofa_zero(self):
        """Test qSOFA with no criteria met."""
        from src.domain.services.calculators import QsofaScoreCalculator
        
        calc = QsofaScoreCalculator()
        result = calc.calculate(
            respiratory_rate_22_or_higher=False,
            altered_mental_status=False,
            systolic_bp_100_or_less=False,
        )
        
        assert result.value == 0

    def test_qsofa_two_positive(self):
        """Test qSOFA with 2 criteria met - high risk."""
        from src.domain.services.calculators import QsofaScoreCalculator
        
        calc = QsofaScoreCalculator()
        result = calc.calculate(
            respiratory_rate_22_or_higher=True,
            altered_mental_status=True,
            systolic_bp_100_or_less=False,
        )
        
        assert result.value == 2

    def test_qsofa_three_positive(self):
        """Test qSOFA with all criteria met."""
        from src.domain.services.calculators import QsofaScoreCalculator
        
        calc = QsofaScoreCalculator()
        result = calc.calculate(
            respiratory_rate_22_or_higher=True,
            altered_mental_status=True,
            systolic_bp_100_or_less=True,
        )
        
        assert result.value == 3

    def test_tool_id(self):
        """Test tool ID is correct."""
        from src.domain.services.calculators import QsofaScoreCalculator
        
        calc = QsofaScoreCalculator()
        assert calc.tool_id == "qsofa"


class TestNewsCalculator:
    """Tests for National Early Warning Score (NEWS)."""

    def test_news_zero(self):
        """Test NEWS with all normal values."""
        from src.domain.services.calculators import NewsScoreCalculator
        
        calc = NewsScoreCalculator()
        result = calc.calculate(
            respiratory_rate=16,
            oxygen_saturation=97,
            supplemental_oxygen=False,
            temperature=37.0,
            systolic_bp=120,
            heart_rate=75,
            consciousness="alert",
        )
        
        assert result.value == 0

    def test_news_elevated(self):
        """Test NEWS with elevated score."""
        from src.domain.services.calculators import NewsScoreCalculator
        
        calc = NewsScoreCalculator()
        result = calc.calculate(
            respiratory_rate=25,
            oxygen_saturation=92,
            supplemental_oxygen=True,
            temperature=39.0,
            systolic_bp=90,
            heart_rate=120,
            consciousness="confused",
        )
        
        assert result.value is not None
        assert result.value > 5  # High score

    def test_tool_id(self):
        """Test tool ID is correct."""
        from src.domain.services.calculators import NewsScoreCalculator
        
        calc = NewsScoreCalculator()
        assert calc.tool_id == "news"


class TestGcsCalculator:
    """Tests for Glasgow Coma Scale (GCS)."""

    def test_gcs_full_score(self):
        """Test GCS with full consciousness (15)."""
        from src.domain.services.calculators import GlasgowComaScaleCalculator
        
        calc = GlasgowComaScaleCalculator()
        result = calc.calculate(
            eye_response=4,
            verbal_response=5,
            motor_response=6,
        )
        
        assert result.value == 15

    def test_gcs_minimal(self):
        """Test GCS with minimal response (3)."""
        from src.domain.services.calculators import GlasgowComaScaleCalculator
        
        calc = GlasgowComaScaleCalculator()
        result = calc.calculate(
            eye_response=1,
            verbal_response=1,
            motor_response=1,
        )
        
        assert result.value == 3

    def test_gcs_moderate(self):
        """Test GCS with moderate impairment."""
        from src.domain.services.calculators import GlasgowComaScaleCalculator
        
        calc = GlasgowComaScaleCalculator()
        result = calc.calculate(
            eye_response=3,
            verbal_response=3,
            motor_response=4,
        )
        
        assert result.value == 10

    def test_tool_id(self):
        """Test tool ID is correct."""
        from src.domain.services.calculators import GlasgowComaScaleCalculator
        
        calc = GlasgowComaScaleCalculator()
        assert calc.tool_id == "gcs"


class TestCamIcuCalculator:
    """Tests for CAM-ICU (Confusion Assessment Method for ICU)."""

    def test_cam_icu_negative(self):
        """Test CAM-ICU negative - no delirium."""
        from src.domain.services.calculators import CamIcuCalculator
        
        calc = CamIcuCalculator()
        result = calc.calculate(
            rass_score=0,
            feature1_acute_onset=False,
            feature2_inattention=False,
            feature3_altered_loc=False,
            feature4_disorganized_thinking=False,
        )
        
        assert result.value == 0 or "negative" in str(result.interpretation.summary).lower()

    def test_cam_icu_positive(self):
        """Test CAM-ICU positive - delirium present."""
        from src.domain.services.calculators import CamIcuCalculator
        
        calc = CamIcuCalculator()
        result = calc.calculate(
            rass_score=0,
            feature1_acute_onset=True,
            feature2_inattention=True,
            feature3_altered_loc=False,
            feature4_disorganized_thinking=True,
        )
        
        # Feature 1 + Feature 2 + (Feature 3 OR Feature 4) = Positive
        assert "positive" in str(result.interpretation.summary).lower() or result.value == 1

    def test_cam_icu_unarousable(self):
        """Test CAM-ICU with unarousable patient (RASS -4 or -5)."""
        from src.domain.services.calculators import CamIcuCalculator
        
        calc = CamIcuCalculator()
        result = calc.calculate(
            rass_score=-5,
            feature1_acute_onset=True,
            feature2_inattention=True,
            feature3_altered_loc=False,
            feature4_disorganized_thinking=False,
        )
        
        # Should indicate unable to assess
        assert result.interpretation is not None

    def test_tool_id(self):
        """Test tool ID is correct."""
        from src.domain.services.calculators import CamIcuCalculator
        
        calc = CamIcuCalculator()
        assert calc.tool_id == "cam_icu"
