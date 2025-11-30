"""Tests for Critical Care Calculators"""
import pytest


class TestSofaCalculator:
    def test_sofa_basic(self):
        from src.domain.services.calculators import SofaScoreCalculator
        calc = SofaScoreCalculator()
        result = calc.calculate(
            pao2_fio2_ratio=400, platelets=150, bilirubin=1.0,
            gcs_score=15, creatinine=1.0
        )
        assert result.value >= 0
        assert result.interpretation is not None


class TestSofa2Calculator:
    """Test SOFA-2 Score (JAMA 2025 Update)"""
    
    def test_sofa2_all_normal(self):
        """Test SOFA-2 with completely normal values = 0"""
        from src.domain.services.calculators import Sofa2ScoreCalculator
        calc = Sofa2ScoreCalculator()
        result = calc.calculate(
            gcs_score=15,
            pao2_fio2_ratio=400,  # > 300
            bilirubin=0.8,         # ≤ 1.2
            creatinine=0.9,        # ≤ 1.2
            platelets=200,         # > 150
            map_value=75,          # ≥ 70
        )
        assert result.value == 0
        assert "SOFA-2" in result.tool_name
        assert result.calculation_details["sofa_version"] == "SOFA-2 (2025)"
    
    def test_sofa2_mild_dysfunction(self):
        """Test SOFA-2 with mild dysfunction in each system"""
        from src.domain.services.calculators import Sofa2ScoreCalculator
        calc = Sofa2ScoreCalculator()
        result = calc.calculate(
            gcs_score=14,          # Score 1 (13-14)
            pao2_fio2_ratio=280,   # Score 1 (≤ 300)
            bilirubin=2.0,         # Score 1 (≤ 3.0)
            creatinine=1.5,        # Score 1 (≤ 2.0)
            platelets=120,         # Score 1 (≤ 150)
            map_value=65,          # Score 1 (< 70)
        )
        assert result.value == 6  # All organs score 1
        assert result.calculation_details["brain"] == 1
        assert result.calculation_details["respiratory"] == 1
        assert result.calculation_details["liver"] == 1
        assert result.calculation_details["kidney"] == 1
        assert result.calculation_details["hemostasis"] == 1
        assert result.calculation_details["cardiovascular"] == 1
    
    def test_sofa2_respiratory_with_pf_thresholds(self):
        """Test SOFA-2 new P/F ratio thresholds: 300, 225, 150, 75"""
        from src.domain.services.calculators import Sofa2ScoreCalculator
        calc = Sofa2ScoreCalculator()
        
        # P/F > 300 = 0
        result = calc.calculate(gcs_score=15, pao2_fio2_ratio=350, bilirubin=1.0, creatinine=1.0, platelets=200)
        assert result.calculation_details["respiratory"] == 0
        
        # P/F ≤ 300 = 1
        result = calc.calculate(gcs_score=15, pao2_fio2_ratio=300, bilirubin=1.0, creatinine=1.0, platelets=200)
        assert result.calculation_details["respiratory"] == 1
        
        # P/F ≤ 225 = 2
        result = calc.calculate(gcs_score=15, pao2_fio2_ratio=200, bilirubin=1.0, creatinine=1.0, platelets=200)
        assert result.calculation_details["respiratory"] == 2
        
        # P/F ≤ 150 with advanced support = 3
        result = calc.calculate(gcs_score=15, pao2_fio2_ratio=120, bilirubin=1.0, creatinine=1.0, platelets=200, advanced_ventilatory_support=True)
        assert result.calculation_details["respiratory"] == 3
        
        # P/F ≤ 75 with advanced support = 4
        result = calc.calculate(gcs_score=15, pao2_fio2_ratio=60, bilirubin=1.0, creatinine=1.0, platelets=200, advanced_ventilatory_support=True)
        assert result.calculation_details["respiratory"] == 4
    
    def test_sofa2_ecmo_scores_4(self):
        """Test that ECMO automatically scores respiratory = 4"""
        from src.domain.services.calculators import Sofa2ScoreCalculator
        calc = Sofa2ScoreCalculator()
        result = calc.calculate(
            gcs_score=15,
            pao2_fio2_ratio=300,  # Even with P/F 300
            bilirubin=1.0,
            creatinine=1.0,
            platelets=200,
            on_ecmo=True
        )
        assert result.calculation_details["respiratory"] == 4
    
    def test_sofa2_platelet_thresholds(self):
        """Test SOFA-2 updated platelet thresholds: 150, 100, 80, 50"""
        from src.domain.services.calculators import Sofa2ScoreCalculator
        calc = Sofa2ScoreCalculator()
        
        # > 150 = 0
        result = calc.calculate(gcs_score=15, pao2_fio2_ratio=400, bilirubin=1.0, creatinine=1.0, platelets=160)
        assert result.calculation_details["hemostasis"] == 0
        
        # ≤ 150 = 1
        result = calc.calculate(gcs_score=15, pao2_fio2_ratio=400, bilirubin=1.0, creatinine=1.0, platelets=150)
        assert result.calculation_details["hemostasis"] == 1
        
        # ≤ 100 = 2
        result = calc.calculate(gcs_score=15, pao2_fio2_ratio=400, bilirubin=1.0, creatinine=1.0, platelets=100)
        assert result.calculation_details["hemostasis"] == 2
        
        # ≤ 80 = 3
        result = calc.calculate(gcs_score=15, pao2_fio2_ratio=400, bilirubin=1.0, creatinine=1.0, platelets=80)
        assert result.calculation_details["hemostasis"] == 3
        
        # ≤ 50 = 4
        result = calc.calculate(gcs_score=15, pao2_fio2_ratio=400, bilirubin=1.0, creatinine=1.0, platelets=50)
        assert result.calculation_details["hemostasis"] == 4
    
    def test_sofa2_cardiovascular_ne_epi_dosing(self):
        """Test SOFA-2 combined NE+Epi dose thresholds"""
        from src.domain.services.calculators import Sofa2ScoreCalculator
        calc = Sofa2ScoreCalculator()
        
        # MAP ≥ 70, no vasopressor = 0
        result = calc.calculate(gcs_score=15, pao2_fio2_ratio=400, bilirubin=1.0, creatinine=1.0, platelets=200, map_value=75)
        assert result.calculation_details["cardiovascular"] == 0
        
        # MAP < 70, no vasopressor = 1
        result = calc.calculate(gcs_score=15, pao2_fio2_ratio=400, bilirubin=1.0, creatinine=1.0, platelets=200, map_value=65)
        assert result.calculation_details["cardiovascular"] == 1
        
        # NE+Epi ≤ 0.2 = 2
        result = calc.calculate(gcs_score=15, pao2_fio2_ratio=400, bilirubin=1.0, creatinine=1.0, platelets=200, norepinephrine_epinephrine_dose=0.15)
        assert result.calculation_details["cardiovascular"] == 2
        
        # NE+Epi > 0.2 to ≤ 0.4 = 3
        result = calc.calculate(gcs_score=15, pao2_fio2_ratio=400, bilirubin=1.0, creatinine=1.0, platelets=200, norepinephrine_epinephrine_dose=0.35)
        assert result.calculation_details["cardiovascular"] == 3
        
        # NE+Epi > 0.4 = 4
        result = calc.calculate(gcs_score=15, pao2_fio2_ratio=400, bilirubin=1.0, creatinine=1.0, platelets=200, norepinephrine_epinephrine_dose=0.6)
        assert result.calculation_details["cardiovascular"] == 4
    
    def test_sofa2_brain_with_sedation(self):
        """Test brain scoring with sedation consideration"""
        from src.domain.services.calculators import Sofa2ScoreCalculator
        calc = Sofa2ScoreCalculator()
        
        # GCS 15 without sedation = 0
        result = calc.calculate(gcs_score=15, pao2_fio2_ratio=400, bilirubin=1.0, creatinine=1.0, platelets=200)
        assert result.calculation_details["brain"] == 0
        
        # GCS 15 with sedation = 1
        result = calc.calculate(gcs_score=15, pao2_fio2_ratio=400, bilirubin=1.0, creatinine=1.0, platelets=200, receiving_sedation_or_delirium_drugs=True)
        assert result.calculation_details["brain"] == 1
    
    def test_sofa2_kidney_with_rrt(self):
        """Test kidney scoring with RRT"""
        from src.domain.services.calculators import Sofa2ScoreCalculator
        calc = Sofa2ScoreCalculator()
        
        # RRT = 4 regardless of creatinine
        result = calc.calculate(gcs_score=15, pao2_fio2_ratio=400, bilirubin=1.0, creatinine=1.0, platelets=200, on_rrt=True)
        assert result.calculation_details["kidney"] == 4
    
    def test_sofa2_kidney_urine_output(self):
        """Test kidney scoring with urine output"""
        from src.domain.services.calculators import Sofa2ScoreCalculator
        calc = Sofa2ScoreCalculator()
        
        # UO < 0.5 for 6h = 1
        result = calc.calculate(gcs_score=15, pao2_fio2_ratio=400, bilirubin=1.0, creatinine=1.0, platelets=200, urine_output_6h=0.4)
        assert result.calculation_details["kidney"] == 1
        
        # UO < 0.5 for 12h = 2
        result = calc.calculate(gcs_score=15, pao2_fio2_ratio=400, bilirubin=1.0, creatinine=1.0, platelets=200, urine_output_12h=0.4)
        assert result.calculation_details["kidney"] == 2
        
        # UO < 0.3 for 24h = 3
        result = calc.calculate(gcs_score=15, pao2_fio2_ratio=400, bilirubin=1.0, creatinine=1.0, platelets=200, urine_output_24h=0.25)
        assert result.calculation_details["kidney"] == 3
    
    def test_sofa2_severe_case(self):
        """Test severe multi-organ failure case"""
        from src.domain.services.calculators import Sofa2ScoreCalculator
        calc = Sofa2ScoreCalculator()
        result = calc.calculate(
            gcs_score=5,            # Score 4 (3-5)
            pao2_fio2_ratio=60,     # Score 4 with advanced support
            bilirubin=15.0,         # Score 4 (> 12)
            creatinine=4.0,         # Score 3 (> 3.5)
            platelets=40,           # Score 4 (≤ 50)
            norepinephrine_epinephrine_dose=0.6,  # Score 4 (> 0.4)
            advanced_ventilatory_support=True,
        )
        assert result.value == 23  # 4+4+4+3+4+4
        assert result.interpretation.severity.value == "critical"
    
    def test_sofa2_metadata(self):
        """Test SOFA-2 metadata includes 2025 reference"""
        from src.domain.services.calculators import Sofa2ScoreCalculator
        calc = Sofa2ScoreCalculator()
        
        assert calc.tool_id == "sofa2_score"
        assert "2025" in calc.name
        assert calc.references[0].year == 2025
        assert "JAMA" in calc.references[0].citation
        assert calc.references[0].doi == "10.1001/jama.2025.20516"


class TestQsofaCalculator:
    def test_qsofa_basic(self):
        from src.domain.services.calculators import QsofaScoreCalculator
        calc = QsofaScoreCalculator()
        result = calc.calculate(respiratory_rate=22, systolic_bp=100, altered_mentation=True)
        assert result.value >= 0


class TestNewsCalculator:
    def test_news_basic(self):
        from src.domain.services.calculators import NewsScoreCalculator
        calc = NewsScoreCalculator()
        result = calc.calculate(
            respiratory_rate=18, spo2=96, on_supplemental_o2=False,
            temperature=37.0, systolic_bp=120, heart_rate=80, consciousness="A"
        )
        assert result.value >= 0


class TestGcsCalculator:
    def test_gcs_basic(self):
        from src.domain.services.calculators import GlasgowComaScaleCalculator
        calc = GlasgowComaScaleCalculator()
        result = calc.calculate(eye_response=4, verbal_response=5, motor_response=6)
        assert result.value == 15


class TestCamIcuCalculator:
    def test_cam_icu_basic(self):
        from src.domain.services.calculators import CamIcuCalculator
        calc = CamIcuCalculator()
        result = calc.calculate(
            rass_score=0, acute_onset_fluctuation=False,
            inattention_score=0, disorganized_thinking_errors=0
        )
        assert result.value in [0, 1]


class TestRassCalculator:
    def test_rass_basic(self):
        from src.domain.services.calculators import RassCalculator
        calc = RassCalculator()
        result = calc.calculate(rass_score=0)
        assert result.value == 0


class TestApacheIiCalculator:
    def test_apache_basic(self):
        from src.domain.services.calculators import ApacheIiCalculator
        calc = ApacheIiCalculator()
        result = calc.calculate(
            temperature=37.0, mean_arterial_pressure=80, heart_rate=80,
            respiratory_rate=16, fio2=0.21, pao2=80, arterial_ph=7.4,
            serum_sodium=140, serum_potassium=4.0, serum_creatinine=1.0,
            hematocrit=40, wbc_count=10, gcs_score=15, age=50,
            chronic_health_conditions=(), admission_type="elective_postoperative"
        )
        assert result.value >= 0
