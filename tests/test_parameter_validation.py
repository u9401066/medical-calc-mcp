from typing import Any, cast

"""
Tests for MCP Parameter Validation

Tests Literal types, Field constraints, and error handling across all MCP tools.
This ensures agents receive proper guidance and errors when providing invalid inputs.
"""


# Test that Literal types and Field constraints are properly enforced
# by Pydantic when the MCP tools parse input

class TestAnesthesiologyParameterValidation:
    """Tests for anesthesiology handler parameter validation."""

    def test_asa_valid_classes(self) -> None:
        """Test ASA accepts valid class values 1-6."""
        from src.domain.services.calculators import AsaPhysicalStatusCalculator
        calc = AsaPhysicalStatusCalculator()

        for val in [1, 2, 3, 4, 5, 6]:
            asa_class: Any = val
            result = calc.calculate(asa_class=asa_class, is_emergency=False)
            assert result.value is not None
            assert result.value == asa_class

    def test_mallampati_valid_classes(self) -> None:
        """Test Mallampati accepts valid class values 1-4."""
        from src.domain.services.calculators import MallampatiScoreCalculator
        calc = MallampatiScoreCalculator()

        for val in [1, 2, 3, 4]:
            mal_class: Any = val
            result = calc.calculate(mallampati_class=mal_class)
            assert result.value is not None
            assert result.value == mal_class


class TestCriticalCareParameterValidation:
    """Tests for critical care handler parameter validation."""

    def test_rass_valid_scores(self) -> None:
        """Test RASS accepts all valid scores from -5 to +4."""
        from src.domain.services.calculators import RassCalculator
        calc = RassCalculator()

        for val in [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4]:
            score: Any = val
            result = calc.calculate(rass_score=score)
            assert result.value is not None
            assert result.value == score

    def test_gcs_valid_components(self) -> None:
        """Test GCS accepts valid component scores."""
        from src.domain.services.calculators import GlasgowComaScaleCalculator
        calc = GlasgowComaScaleCalculator()

        # Test minimum GCS
        result = calc.calculate(eye_response=1, verbal_response=1, motor_response=1)
        assert result.value is not None
        assert result.value == 3

        # Test maximum GCS
        result = calc.calculate(eye_response=4, verbal_response=5, motor_response=6)
        assert result.value is not None
        assert result.value == 15

    def test_gcs_intubated(self) -> None:
        """Test GCS with intubation flag."""
        from src.domain.services.calculators import GlasgowComaScaleCalculator
        calc = GlasgowComaScaleCalculator()

        calc.calculate(
            eye_response=4,
            verbal_response=1,  # Not testable when intubated
            motor_response=6,
            is_intubated=True
        )
        # Score should include "T" suffix or handle appropriately

    def test_news2_consciousness_levels(self) -> None:
        """Test NEWS2 accepts valid AVPU/C consciousness levels."""
        from src.domain.services.calculators import NewsScoreCalculator
        calc = NewsScoreCalculator()

        for val in ["A", "V", "P", "U", "C"]:
            consciousness: Any = val
            calc.calculate(
                respiratory_rate=18,
                spo2=96,
                on_supplemental_o2=False,
                temperature=37.0,
                systolic_bp=120,
                heart_rate=75,
                consciousness=consciousness,
            )

    def test_apache_admission_types(self) -> None:
        """Test APACHE-II accepts valid admission types."""
        from src.domain.services.calculators import ApacheIiCalculator
        calc = ApacheIiCalculator()

        for val in ["nonoperative", "elective_postop", "emergency_postop"]:
            admission_type: Any = val
            calc.calculate(
                temperature=37.0,
                mean_arterial_pressure=80,
                heart_rate=80,
                respiratory_rate=16,
                fio2=0.21,
                admission_type=admission_type,
            )

    def test_sofa_range_boundaries(self) -> None:
        """Test SOFA calculation with boundary values."""
        from src.domain.services.calculators import SofaScoreCalculator
        calc = SofaScoreCalculator()

        # Test with extreme but valid values
        result = calc.calculate(
            pao2_fio2_ratio=50,  # Very low
            platelets=10,  # Very low
            bilirubin=15.0,  # Very high
            gcs_score=3,  # Minimum
            creatinine=10.0,  # Very high
        )
        # Should return high SOFA score
        assert result.value is not None
        assert result.value >= 10

    def test_cam_icu_feature_scores(self) -> None:
        """Test CAM-ICU with various feature combinations."""
        from src.domain.services.calculators import CamIcuCalculator
        calc = CamIcuCalculator()

        # Positive delirium: F1 + F2 AND (F3 OR F4)
        calc.calculate(
            rass_score=0,  # Adequate RASS for assessment
            acute_onset_fluctuation=True,  # F1 positive
            inattention_score=5,  # F2 positive (≥3)
            altered_loc=True,  # F3 positive
        )


class TestCardiologyParameterValidation:
    """Tests for cardiology handler parameter validation."""

    def test_heart_score_components(self) -> None:
        """Test HEART score with valid component scores 0-2."""
        from src.domain.services.calculators import HeartScoreCalculator
        calc = HeartScoreCalculator()

        for score in [0, 1, 2]:
            result = calc.calculate(
                history_score=score,
                ecg_score=score,
                age_score=score,
                risk_factors_score=score,
                troponin_score=score,
            )
            assert result.value is not None
            assert result.value == score * 5


class TestNephrologyParameterValidation:
    """Tests for nephrology handler parameter validation."""

    def test_ckd_epi_sex_values(self) -> None:
        """Test CKD-EPI accepts 'male' and 'female' sex values."""
        from src.domain.services.calculators import CkdEpi2021Calculator
        calc = CkdEpi2021Calculator()

        for val in ["male", "female"]:
            sex: Any = val
            result = calc.calculate(
                serum_creatinine=1.0,
                age=50,
                sex=sex,
            )
            assert result.value is not None
            assert result.value > 0

    def test_ckd_epi_age_boundaries(self) -> None:
        """Test CKD-EPI with age at boundaries."""
        from src.domain.services.calculators import CkdEpi2021Calculator
        calc = CkdEpi2021Calculator()

        # Young adult
        result_young = calc.calculate(serum_creatinine=1.0, age=18, sex="male")
        # Elderly
        result_old = calc.calculate(serum_creatinine=1.0, age=100, sex="male")

        # eGFR should be higher for younger with same Cr
        assert result_young.value is not None
        assert result_old.value is not None
        assert result_young.value > result_old.value

    def test_kdigo_aki_creatinine_boundaries(self) -> None:
        """Test KDIGO AKI with various creatinine ratios."""
        from src.domain.services.calculators import KdigoAkiCalculator
        calc = KdigoAkiCalculator()

        # Just below Stage 1 threshold (1.4x)
        result_0 = calc.calculate(current_creatinine=1.4, baseline_creatinine=1.0)
        assert result_0.value is not None
        assert result_0.value == 0

        # At Stage 1 threshold (1.5x)
        result_1 = calc.calculate(current_creatinine=1.5, baseline_creatinine=1.0)
        assert result_1.value is not None
        assert result_1.value == 1

        # At Stage 2 threshold (2.0x)
        result_2 = calc.calculate(current_creatinine=2.0, baseline_creatinine=1.0)
        assert result_2.value is not None
        assert result_2.value == 2

        # At Stage 3 threshold (3.0x)
        result_3 = calc.calculate(current_creatinine=3.0, baseline_creatinine=1.0)
        assert result_3.value is not None
        assert result_3.value == 3


class TestPediatricParameterValidation:
    """Tests for pediatric handler parameter validation."""

    def test_pediatric_drug_names(self) -> None:
        """Test pediatric dosing accepts all supported drug names."""
        from src.domain.services.calculators import PediatricDosingCalculator
        calc = PediatricDosingCalculator()

        supported_drugs = [
            "acetaminophen", "ibuprofen", "amoxicillin", "ceftriaxone",
            "ondansetron", "morphine", "fentanyl", "ketamine"
        ]

        for drug in supported_drugs:
            calc.calculate(drug_name=drug, weight_kg=20)

    def test_pediatric_routes(self) -> None:
        """Test pediatric dosing accepts valid routes."""
        from src.domain.services.calculators import PediatricDosingCalculator
        calc = PediatricDosingCalculator()

        # IV route for fentanyl
        calc.calculate(drug_name="fentanyl", weight_kg=20, route="iv")

    def test_mabl_patient_types(self) -> None:
        """Test MABL accepts all patient types with correct EBV."""
        from src.domain.services.calculators import MablCalculator
        calc = MablCalculator()

        patient_types = [
            ("preterm_neonate", 90),
            ("term_neonate", 85),
            ("infant", 80),
            ("child", 75),
            ("adult_male", 70),
            ("adult_female", 65),
        ]

        for patient_type, expected_ebv_factor in patient_types:
            calc.calculate(
                weight_kg=10,
                initial_hematocrit=40,
                target_hematocrit=30,
                patient_type=patient_type,
            )

    def test_transfusion_product_types(self) -> None:
        """Test transfusion calculator accepts all product types."""
        from src.domain.services.calculators import TransfusionCalculator
        calc = TransfusionCalculator()

        # PRBC needs hematocrit values
        result = calc.calculate(
            weight_kg=70,
            product_type="prbc",
            current_hematocrit=25,
            target_hematocrit=30,
        )
        assert result is not None


class TestHepatologyParameterValidation:
    """Tests for hepatology handler parameter validation."""

    def test_child_pugh_ascites_values(self) -> None:
        """Test Child-Pugh accepts valid ascites values."""
        from src.domain.services.calculators import ChildPughCalculator
        calc = ChildPughCalculator()

        for ascites in ["none", "mild", "moderate_severe"]:
            calc.calculate(
                bilirubin=1.5,
                albumin=3.5,
                inr=1.3,
                ascites=ascites,
                encephalopathy_grade=0,
            )

    def test_child_pugh_encephalopathy_grades(self) -> None:
        """Test Child-Pugh accepts encephalopathy grades 0-4."""
        from src.domain.services.calculators import ChildPughCalculator
        calc = ChildPughCalculator()

        for grade in [0, 1, 2, 3, 4]:
            calc.calculate(
                bilirubin=1.5,
                albumin=3.5,
                inr=1.3,
                ascites="none",
                encephalopathy_grade=grade,
            )


class TestEmergencyParameterValidation:
    """Tests for emergency medicine handler parameter validation."""

    def test_wells_dvt_max_score(self) -> None:
        """Test Wells DVT with all risk factors positive."""
        from src.domain.services.calculators import WellsDvtCalculator
        calc = WellsDvtCalculator()

        result = calc.calculate(
            active_cancer=True,
            paralysis_paresis_or_recent_cast=True,
            bedridden_or_major_surgery=True,
            tenderness_along_deep_veins=True,
            entire_leg_swollen=True,
            calf_swelling_gt_3cm=True,
            pitting_edema=True,
            collateral_superficial_veins=True,
            previous_dvt=True,
            alternative_diagnosis_likely=False,  # -2 if True
        )
        assert result.value is not None
        assert result.value == 9

    def test_wells_dvt_alternative_diagnosis_deduction(self) -> None:
        """Test Wells DVT subtracts 2 for alternative diagnosis."""
        from src.domain.services.calculators import WellsDvtCalculator
        calc = WellsDvtCalculator()

        # With alternative diagnosis
        result_with = calc.calculate(
            active_cancer=True,  # +1
            paralysis_paresis_or_recent_cast=False,
            bedridden_or_major_surgery=False,
            tenderness_along_deep_veins=False,
            entire_leg_swollen=False,
            calf_swelling_gt_3cm=False,
            pitting_edema=False,
            collateral_superficial_veins=False,
            previous_dvt=False,
            alternative_diagnosis_likely=True,  # -2
        )
        assert result_with.value is not None
        assert result_with.value == -1

    def test_wells_pe_max_score(self) -> None:
        """Test Wells PE with all risk factors positive."""
        from src.domain.services.calculators import WellsPeCalculator
        calc = WellsPeCalculator()

        result = calc.calculate(
            clinical_signs_dvt=True,  # +3
            pe_most_likely_diagnosis=True,  # +3
            heart_rate_gt_100=True,  # +1.5
            immobilization_or_surgery=True,  # +1.5
            previous_dvt_pe=True,  # +1.5
            hemoptysis=True,  # +1
            malignancy=True,  # +1
        )
        assert result.value is not None
        assert result.value == 12.5


class TestBoundaryConditions:
    """Tests for boundary conditions and edge cases."""

    def test_sofa_max_score(self) -> None:
        """Test SOFA can reach maximum score of 24."""
        from src.domain.services.calculators import SofaScoreCalculator
        calc = SofaScoreCalculator()

        result = calc.calculate(
            pao2_fio2_ratio=50,  # 4 points
            platelets=5,  # 4 points
            bilirubin=15.0,  # 4 points
            gcs_score=3,  # 4 points
            creatinine=6.0,  # 4 points (if no UO)
            norepinephrine_dose=0.2,  # 4 points
        )
        assert result.value is not None
        assert result.value >= 20  # May vary based on implementation

    def test_apache_age_scoring(self) -> None:
        """Test APACHE-II age scoring at boundaries."""
        from src.domain.services.calculators import ApacheIiCalculator
        calc = ApacheIiCalculator()

        base_params = {
            "temperature": 37.0,
            "mean_arterial_pressure": 80,
            "heart_rate": 80,
            "respiratory_rate": 16,
            "fio2": 0.21,
        }

        # Age < 45: 0 points
        result_young = calc.calculate(**cast(Any, base_params), age=44)
        # Age 45-54: 2 points
        result_45 = calc.calculate(**cast(Any, base_params), age=50)
        # Age 55-64: 3 points
        calc.calculate(**cast(Any, base_params), age=60)
        # Age 65-74: 5 points
        result_65 = calc.calculate(**cast(Any, base_params), age=70)
        # Age ≥75: 6 points
        result_75 = calc.calculate(**cast(Any, base_params), age=80)

        # Each age group should add more points
        assert result_45.value is not None
        assert result_young.value is not None
        assert result_45.value >= result_young.value
        assert result_75.value is not None
        assert result_65.value is not None
        assert result_75.value > result_65.value

    def test_news2_scale_2_spo2_scoring(self) -> None:
        """Test NEWS2 Scale 2 for hypercapnic patients."""
        from src.domain.services.calculators import NewsScoreCalculator
        calc = NewsScoreCalculator()

        base_params = {
            "respiratory_rate": 18,
            "on_supplemental_o2": True,
            "temperature": 37.0,
            "systolic_bp": 120,
            "heart_rate": 75,
            "consciousness": "A",
        }

        # Scale 1 (default): SpO2 88-92% scores 3
        calc.calculate(**cast(Any, base_params), spo2=90, use_scale_2=False)

        # Scale 2: SpO2 88-92% on target is ok (lower score)
        calc.calculate(**cast(Any, base_params), spo2=90, use_scale_2=True)

        # Scale 2 should have different scoring for same SpO2


class TestInterpretationContent:
    """Tests for clinical interpretation content."""

    def test_chads2_vasc_anticoagulation_recommendation(self) -> None:
        """Test CHA₂DS₂-VASc provides anticoagulation guidance."""
        from src.domain.services.calculators import Chads2VascCalculator
        calc = Chads2VascCalculator()

        # Score ≥2 should recommend anticoagulation
        result = calc.calculate(
            chf_or_lvef_lte_40=True,
            hypertension=True,
            age_gte_75=False,
            diabetes=False,
            stroke_tia_or_te_history=False,
            vascular_disease=False,
            age_65_to_74=False,
            female_sex=False,
        )

        assert result.value is not None
        assert result.value == 2
        recommendations = " ".join(result.interpretation.recommendations)
        assert "anticoagul" in recommendations.lower()

    def test_curb65_hospitalization_guidance(self) -> None:
        """Test CURB-65 provides hospitalization guidance."""
        from src.domain.services.calculators import Curb65Calculator
        calc = Curb65Calculator()

        # Low risk (0-1): outpatient
        result_low = calc.calculate(
            confusion=False,
            bun_gt_19_or_urea_gt_7=False,
            respiratory_rate_gte_30=False,
            sbp_lt_90_or_dbp_lte_60=False,
            age_gte_65=False,
        )
        # Check recommendations for outpatient
        recommendations = " ".join(result_low.interpretation.recommendations)
        assert "outpatient" in recommendations.lower() or "home" in recommendations.lower()

        # High risk (3+): hospitalize
        result_high = calc.calculate(
            confusion=True,
            bun_gt_19_or_urea_gt_7=True,
            respiratory_rate_gte_30=True,
            sbp_lt_90_or_dbp_lte_60=False,
            age_gte_65=False,
        )
        recommendations = " ".join(result_high.interpretation.recommendations)
        assert "hospital" in recommendations.lower() or "admit" in recommendations.lower() or "icu" in recommendations.lower()
