from typing import Any

"""
Tests for MCP Calculator Handlers

Tests both tool registration and execution for all handler categories.
"""


import pytest

from src.application.use_cases import CalculateUseCase
from src.domain.registry import ToolRegistry
from src.domain.services.calculators import CALCULATORS


class MockMCP:
    """Mock FastMCP for testing tool registration"""

    def __init__(self) -> None:
        self._tools: dict[str, Any] = {}

    def tool(self) -> Any:
        """Decorator to register a tool"""
        def decorator(func: Any) -> Any:
            self._tools[func.__name__] = func
            return func
        return decorator

    def get_tool(self, name: str) -> Any:
        """Get a registered tool by name"""
        return self._tools.get(name)

    @property
    def tools(self) -> dict[str, Any]:
        """Return all registered tools"""
        return self._tools


@pytest.fixture
def registry() -> Any:
    """Create a populated ToolRegistry for testing"""
    reg = ToolRegistry()
    for calc_class in CALCULATORS:
        reg.register(calc_class())
    return reg


@pytest.fixture
def use_case(registry: Any) -> Any:
    """Create a CalculateUseCase with populated registry"""
    return CalculateUseCase(registry)


@pytest.fixture
def mock_mcp() -> Any:
    """Create a MockMCP instance"""
    return MockMCP()


# =============================================================================
# Critical Care Handler Tests
# =============================================================================

class TestCriticalCareHandlers:
    """Tests for critical care calculator handlers"""

    def test_register_critical_care_tools(self, mock_mcp: Any, use_case: Any) -> None:
        """Test that critical care tools are registered correctly"""
        from src.infrastructure.mcp.handlers.calculators.critical_care import (
            register_critical_care_tools,
        )
        register_critical_care_tools(mock_mcp, use_case)

        expected_tools = [
            'calculate_apache_ii', 'calculate_sofa', 'calculate_sofa2',
            'calculate_qsofa', 'calculate_news2', 'calculate_gcs',
            'calculate_cam_icu', 'calculate_rass'
        ]
        for tool in expected_tools:
            assert tool in mock_mcp.tools, f"Tool {tool} should be registered"

    def test_calculate_gcs(self, mock_mcp: Any, use_case: Any) -> None:
        """Test GCS calculation"""
        from src.infrastructure.mcp.handlers.calculators.critical_care import (
            register_critical_care_tools,
        )
        register_critical_care_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_gcs')(
            eye_response=4,
            verbal_response=5,
            motor_response=6
        )
        assert result['success'] is True
        assert result['result'] == 15
        assert 'interpretation' in result

    def test_calculate_qsofa(self, mock_mcp: Any, use_case: Any) -> None:
        """Test qSOFA calculation"""
        from src.infrastructure.mcp.handlers.calculators.critical_care import (
            register_critical_care_tools,
        )
        register_critical_care_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_qsofa')(
            respiratory_rate=24,
            systolic_bp=95,
            altered_mentation=True
        )
        assert result['success'] is True
        assert 'result' in result
        assert result['result'] >= 2  # All three criteria met

    def test_calculate_news2(self, mock_mcp: Any, use_case: Any) -> None:
        """Test NEWS2 calculation"""
        from src.infrastructure.mcp.handlers.calculators.critical_care import (
            register_critical_care_tools,
        )
        register_critical_care_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_news2')(
            respiratory_rate=18,
            spo2=96,
            on_supplemental_o2=False,
            temperature=37.0,
            systolic_bp=120,
            heart_rate=75,
            consciousness='A'  # Alert
        )
        assert result['success'] is True
        assert 'result' in result

    def test_calculate_rass(self, mock_mcp: Any, use_case: Any) -> None:
        """Test RASS calculation"""
        from src.infrastructure.mcp.handlers.calculators.critical_care import (
            register_critical_care_tools,
        )
        register_critical_care_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_rass')(
            rass_score=0
        )
        assert result['success'] is True
        assert result['result'] == 0  # Alert and calm

    def test_calculate_cam_icu(self, mock_mcp: Any, use_case: Any) -> None:
        """Test CAM-ICU calculation"""
        from src.infrastructure.mcp.handlers.calculators.critical_care import (
            register_critical_care_tools,
        )
        register_critical_care_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_cam_icu')(
            rass_score=0,
            acute_onset_fluctuation=False,
            inattention_score=0,
            altered_loc=False,
            disorganized_thinking_errors=0
        )
        assert result['success'] is True
        assert 'result' in result


# =============================================================================
# Nephrology Handler Tests
# =============================================================================

class TestNephrologyHandlers:
    """Tests for nephrology calculator handlers"""

    def test_register_nephrology_tools(self, mock_mcp: Any, use_case: Any) -> None:
        """Test that nephrology tools are registered correctly"""
        from src.infrastructure.mcp.handlers.calculators.nephrology import register_nephrology_tools
        register_nephrology_tools(mock_mcp, use_case)

        expected_tools = ['calculate_ckd_epi_2021', 'calculate_kdigo_aki']
        for tool in expected_tools:
            assert tool in mock_mcp.tools, f"Tool {tool} should be registered"

    def test_calculate_ckd_epi_2021(self, mock_mcp: Any, use_case: Any) -> None:
        """Test CKD-EPI 2021 eGFR calculation"""
        from src.infrastructure.mcp.handlers.calculators.nephrology import register_nephrology_tools
        register_nephrology_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_ckd_epi_2021')(
            serum_creatinine=1.0,
            age=50,
            sex='male'
        )
        assert result['success'] is True
        assert 'result' in result
        assert result['result'] > 0  # eGFR should be positive

    def test_calculate_kdigo_aki(self, mock_mcp: Any, use_case: Any) -> None:
        """Test KDIGO AKI staging"""
        from src.infrastructure.mcp.handlers.calculators.nephrology import register_nephrology_tools
        register_nephrology_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_kdigo_aki')(
            current_creatinine=2.0,
            baseline_creatinine=1.0
        )
        assert result['success'] is True
        assert 'result' in result


# =============================================================================
# Cardiology Handler Tests
# =============================================================================

class TestCardiologyHandlers:
    """Tests for cardiology calculator handlers"""

    def test_register_cardiology_tools(self, mock_mcp: Any, use_case: Any) -> None:
        """Test that cardiology tools are registered correctly"""
        from src.infrastructure.mcp.handlers.calculators.cardiology import register_cardiology_tools
        register_cardiology_tools(mock_mcp, use_case)

        expected_tools = [
            'calculate_chads2_vasc', 'calculate_chads2_va',
            'calculate_heart_score', 'calculate_has_bled'
        ]
        for tool in expected_tools:
            assert tool in mock_mcp.tools, f"Tool {tool} should be registered"

    def test_calculate_chads2_vasc(self, mock_mcp: Any, use_case: Any) -> None:
        """Test CHA2DS2-VASc calculation"""
        from src.infrastructure.mcp.handlers.calculators.cardiology import register_cardiology_tools
        register_cardiology_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_chads2_vasc')(
            chf_or_lvef_lte_40=True,
            hypertension=True,
            age_gte_75=False,
            diabetes=True,
            stroke_tia_or_te_history=False,
            vascular_disease=False,
            age_65_to_74=True,
            female_sex=False
        )
        assert result['success'] is True
        assert 'result' in result

    def test_calculate_heart_score(self, mock_mcp: Any, use_case: Any) -> None:
        """Test HEART score calculation"""
        from src.infrastructure.mcp.handlers.calculators.cardiology import register_cardiology_tools
        register_cardiology_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_heart_score')(
            history_score=1,
            ecg_score=1,
            age_score=1,
            risk_factors_score=1,
            troponin_score=0
        )
        assert result['success'] is True
        assert 'result' in result


# =============================================================================
# Neurology Handler Tests
# =============================================================================

class TestNeurologyHandlers:
    """Tests for neurology calculator handlers"""

    def test_register_neurology_tools(self, mock_mcp: Any, use_case: Any) -> None:
        """Test that neurology tools are registered correctly"""
        from src.infrastructure.mcp.handlers.calculators.neurology import register_neurology_tools
        register_neurology_tools(mock_mcp, use_case)

        expected_tools = [
            'calculate_nihss', 'calculate_abcd2', 'calculate_modified_rankin_scale'
        ]
        for tool in expected_tools:
            assert tool in mock_mcp.tools, f"Tool {tool} should be registered"

    def test_calculate_nihss(self, mock_mcp: Any, use_case: Any) -> None:
        """Test NIHSS calculation"""
        from src.infrastructure.mcp.handlers.calculators.neurology import register_neurology_tools
        register_neurology_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_nihss')(
            loc=0, loc_questions=0, loc_commands=0,
            best_gaze=0, visual_fields=0, facial_palsy=0,
            motor_arm_left=0, motor_arm_right=0,
            motor_leg_left=0, motor_leg_right=0,
            limb_ataxia=0, sensory=0, best_language=0,
            dysarthria=0, extinction_inattention=0
        )
        assert result['success'] is True
        assert result['result'] == 0  # All normal

    def test_calculate_abcd2(self, mock_mcp: Any, use_case: Any) -> None:
        """Test ABCD2 calculation"""
        from src.infrastructure.mcp.handlers.calculators.neurology import register_neurology_tools
        register_neurology_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_abcd2')(
            age_gte_60=True,
            bp_gte_140_90=True,
            clinical_features='unilateral_weakness',
            duration_minutes='gte_60',
            diabetes=True
        )
        assert result['success'] is True
        assert 'result' in result
        assert result['result'] == 7  # Maximum score


# =============================================================================
# Anesthesiology Handler Tests
# =============================================================================

class TestAnesthesiologyHandlers:
    """Tests for anesthesiology calculator handlers"""

    def test_register_anesthesiology_tools(self, mock_mcp: Any, use_case: Any) -> None:
        """Test that anesthesiology tools are registered correctly"""
        from src.infrastructure.mcp.handlers.calculators.anesthesiology import (
            register_anesthesiology_tools,
        )
        register_anesthesiology_tools(mock_mcp, use_case)

        expected_tools = [
            'calculate_asa_physical_status', 'calculate_apfel_ponv',
            'calculate_mallampati', 'calculate_rcri', 'calculate_stop_bang',
            'calculate_aldrete_score'
        ]
        for tool in expected_tools:
            assert tool in mock_mcp.tools, f"Tool {tool} should be registered"

    def test_calculate_asa_physical_status(self, mock_mcp: Any, use_case: Any) -> None:
        """Test ASA physical status calculation"""
        from src.infrastructure.mcp.handlers.calculators.anesthesiology import (
            register_anesthesiology_tools,
        )
        register_anesthesiology_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_asa_physical_status')(
            asa_class=2,
            is_emergency=False
        )
        assert result['success'] is True
        assert result['result'] == 2

    def test_calculate_apfel_ponv(self, mock_mcp: Any, use_case: Any) -> None:
        """Test Apfel PONV score calculation"""
        from src.infrastructure.mcp.handlers.calculators.anesthesiology import (
            register_anesthesiology_tools,
        )
        register_anesthesiology_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_apfel_ponv')(
            female_gender=True,
            history_motion_sickness_or_ponv=True,
            non_smoker=True,
            postoperative_opioids=True
        )
        assert result['success'] is True
        assert result['result'] == 4  # All four risk factors

    def test_calculate_mallampati(self, mock_mcp: Any, use_case: Any) -> None:
        """Test Mallampati airway assessment"""
        from src.infrastructure.mcp.handlers.calculators.anesthesiology import (
            register_anesthesiology_tools,
        )
        register_anesthesiology_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_mallampati')(
            mallampati_class=1
        )
        assert result['success'] is True
        assert result['result'] == 1

    def test_calculate_rcri(self, mock_mcp: Any, use_case: Any) -> None:
        """Test RCRI calculation"""
        from src.infrastructure.mcp.handlers.calculators.anesthesiology import (
            register_anesthesiology_tools,
        )
        register_anesthesiology_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_rcri')(
            high_risk_surgery=True,
            ischemic_heart_disease=True,
            heart_failure=False,
            cerebrovascular_disease=False,
            insulin_diabetes=False,
            creatinine_above_2=False
        )
        assert result['success'] is True
        assert result['result'] == 2

    def test_calculate_stop_bang(self, mock_mcp: Any, use_case: Any) -> None:
        """Test STOP-BANG OSA screening"""
        from src.infrastructure.mcp.handlers.calculators.anesthesiology import (
            register_anesthesiology_tools,
        )
        register_anesthesiology_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_stop_bang')(
            snoring=True,
            tired=True,
            observed_apnea=False,
            high_blood_pressure=True,
            bmi_over_35=False,
            age_over_50=True,
            neck_over_40cm=False,
            male_gender=True
        )
        assert result['success'] is True
        assert 'result' in result


# =============================================================================
# Acid-Base Handler Tests
# =============================================================================

class TestAcidBaseHandlers:
    """Tests for acid-base calculator handlers"""

    def test_register_acid_base_tools(self, mock_mcp: Any, use_case: Any) -> None:
        """Test that acid-base tools are registered correctly"""
        from src.infrastructure.mcp.handlers.calculators.acid_base import register_acid_base_tools
        register_acid_base_tools(mock_mcp, use_case)

        expected_tools = [
            'calculate_anion_gap', 'calculate_delta_ratio',
            'calculate_corrected_sodium', 'calculate_free_water_deficit',
            'calculate_osmolar_gap'
        ]
        for tool in expected_tools:
            assert tool in mock_mcp.tools, f"Tool {tool} should be registered"

    def test_calculate_anion_gap(self, mock_mcp: Any, use_case: Any) -> None:
        """Test anion gap calculation"""
        from src.infrastructure.mcp.handlers.calculators.acid_base import register_acid_base_tools
        register_acid_base_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_anion_gap')(
            sodium=140.0,
            chloride=105.0,
            bicarbonate=24.0
        )
        assert result['success'] is True
        assert 'result' in result

    def test_calculate_delta_ratio(self, mock_mcp: Any, use_case: Any) -> None:
        """Test delta ratio calculation"""
        from src.infrastructure.mcp.handlers.calculators.acid_base import register_acid_base_tools
        register_acid_base_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_delta_ratio')(
            anion_gap=20.0,
            bicarbonate=14.0
        )
        assert result['success'] is True
        assert 'result' in result

    def test_calculate_corrected_sodium(self, mock_mcp: Any, use_case: Any) -> None:
        """Test corrected sodium calculation"""
        from src.infrastructure.mcp.handlers.calculators.acid_base import register_acid_base_tools
        register_acid_base_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_corrected_sodium')(
            measured_sodium=130.0,
            glucose=400.0
        )
        assert result['success'] is True
        assert 'result' in result


# =============================================================================
# Pulmonology Handler Tests
# =============================================================================

class TestPulmonologyHandlers:
    """Tests for pulmonology calculator handlers"""

    def test_register_pulmonology_tools(self, mock_mcp: Any, use_case: Any) -> None:
        """Test that pulmonology tools are registered correctly"""
        from src.infrastructure.mcp.handlers.calculators.pulmonology import (
            register_pulmonology_tools,
        )
        register_pulmonology_tools(mock_mcp, use_case)

        # Check for tools that actually exist in pulmonology module
        expected_tools = [
            'calculate_aa_gradient', 'calculate_pf_ratio',
            'calculate_curb65', 'calculate_psi_port', 'calculate_rox_index'
        ]
        for tool in expected_tools:
            assert tool in mock_mcp.tools, f"Tool {tool} should be registered"

    def test_calculate_curb65(self, mock_mcp: Any, use_case: Any) -> None:
        """Test CURB-65 calculation with correct parameter names"""
        from src.infrastructure.mcp.handlers.calculators.pulmonology import (
            register_pulmonology_tools,
        )
        register_pulmonology_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_curb65')(
            confusion=False,
            bun_gt_19_or_urea_gt_7=False,
            respiratory_rate_gte_30=False,
            sbp_lt_90_or_dbp_lte_60=False,
            age_gte_65=True
        )
        assert result['success'] is True
        assert result['result'] == 1


# =============================================================================
# Hepatology Handler Tests
# =============================================================================

class TestHepatologyHandlers:
    """Tests for hepatology calculator handlers"""

    def test_register_hepatology_tools(self, mock_mcp: Any, use_case: Any) -> None:
        """Test that hepatology tools are registered correctly"""
        from src.infrastructure.mcp.handlers.calculators.hepatology import register_hepatology_tools
        register_hepatology_tools(mock_mcp, use_case)

        expected_tools = [
            'calculate_child_pugh', 'calculate_meld_score', 'calculate_fib4_index'
        ]
        for tool in expected_tools:
            assert tool in mock_mcp.tools, f"Tool {tool} should be registered"

    def test_calculate_child_pugh(self, mock_mcp: Any, use_case: Any) -> None:
        """Test Child-Pugh score calculation with correct parameter names"""
        from src.infrastructure.mcp.handlers.calculators.hepatology import register_hepatology_tools
        register_hepatology_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_child_pugh')(
            bilirubin=1.5,
            albumin=3.8,
            inr=1.2,
            ascites='none',
            encephalopathy_grade=0
        )
        assert result['success'] is True
        assert 'result' in result

    def test_calculate_meld_score(self, mock_mcp: Any, use_case: Any) -> None:
        """Test MELD score calculation"""
        from src.infrastructure.mcp.handlers.calculators.hepatology import register_hepatology_tools
        register_hepatology_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_meld_score')(
            bilirubin=2.0,
            inr=1.5,
            creatinine=1.0,
            sodium=140.0
        )
        assert result['success'] is True
        assert 'result' in result


# =============================================================================
# Surgery Handler Tests
# =============================================================================

class TestSurgeryHandlers:
    """Tests for surgery calculator handlers"""

    def test_register_surgery_tools(self, mock_mcp: Any, use_case: Any) -> None:
        """Test that surgery tools are registered correctly"""
        from src.infrastructure.mcp.handlers.calculators.surgery import register_surgery_tools
        register_surgery_tools(mock_mcp, use_case)

        # surgery.py only has calculate_caprini_vte
        expected_tools = ['calculate_caprini_vte']
        for tool in expected_tools:
            assert tool in mock_mcp.tools, f"Tool {tool} should be registered"

    def test_calculate_caprini_vte(self, mock_mcp: Any, use_case: Any) -> None:
        """Test Caprini VTE risk calculation with all required params"""
        from src.infrastructure.mcp.handlers.calculators.surgery import register_surgery_tools
        register_surgery_tools(mock_mcp, use_case)

        # Caprini has many boolean parameters, all with defaults
        # But they need to be passed explicitly in handler
        result = mock_mcp.get_tool('calculate_caprini_vte')(
            age_years=50,
            minor_surgery=True,
            major_surgery=False,
            laparoscopic_surgery_gt_45min=False,
            arthroscopic_surgery=False,
            prior_major_surgery_lt_1mo=False,
            varicose_veins=False,
            inflammatory_bowel_disease=False,
            swollen_legs=False,
            obesity_bmi_gt_25=False,
            acute_mi=False,
            chf_lt_1mo=False,
            sepsis_lt_1mo=False,
            lung_disease=False,
            copd=False,
            bed_rest_medical=False,
            bed_confined_gt_72hr=False,
            leg_cast_or_brace=False,
            immobilizing_cast_lt_1mo=False,
            central_venous_access=False,
            malignancy=False,
            history_dvt_pe=False,
            family_history_thrombosis=False,
            factor_v_leiden=False,
            prothrombin_20210a=False,
            elevated_homocysteine=False,
            lupus_anticoagulant=False,
            anticardiolipin_antibodies=False,
            hit_history=False,
            other_thrombophilia=False,
            stroke_lt_1mo=False,
            elective_arthroplasty=False,
            hip_pelvis_leg_fracture_lt_1mo=False,
            spinal_cord_injury_lt_1mo=False,
            female=False,
            oral_contraceptives_or_hrt=False,
            pregnancy_or_postpartum=False,
            pregnancy_loss_history=False
        )
        assert result['success'] is True
        assert 'result' in result


# =============================================================================
# Emergency Handler Tests
# =============================================================================

class TestEmergencyHandlers:
    """Tests for emergency calculator handlers"""

    def test_register_emergency_tools(self, mock_mcp: Any, use_case: Any) -> None:
        """Test that emergency tools are registered correctly"""
        from src.infrastructure.mcp.handlers.calculators.emergency import register_emergency_tools
        register_emergency_tools(mock_mcp, use_case)

        # emergency.py has wells_dvt, wells_pe, shock_index
        expected_tools = [
            'calculate_wells_dvt', 'calculate_wells_pe', 'calculate_shock_index'
        ]
        for tool in expected_tools:
            assert tool in mock_mcp.tools, f"Tool {tool} should be registered"

    def test_calculate_shock_index(self, mock_mcp: Any, use_case: Any) -> None:
        """Test shock index calculation"""
        from src.infrastructure.mcp.handlers.calculators.emergency import register_emergency_tools
        register_emergency_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_shock_index')(
            heart_rate=100,
            systolic_bp=100
        )
        assert result['success'] is True
        assert result['result'] == 1.0  # 100/100 = 1.0

    def test_calculate_wells_dvt(self, mock_mcp: Any, use_case: Any) -> None:
        """Test Wells DVT calculation"""
        from src.infrastructure.mcp.handlers.calculators.emergency import register_emergency_tools
        register_emergency_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_wells_dvt')(
            active_cancer=False,
            paralysis_paresis_or_recent_cast=False,
            bedridden_or_major_surgery=False,
            tenderness_along_deep_veins=True,
            entire_leg_swollen=True,
            calf_swelling_gt_3cm=True,
            pitting_edema=False,
            collateral_superficial_veins=False,
            previous_dvt=False,
            alternative_diagnosis_likely=False
        )
        assert result['success'] is True
        assert 'result' in result


# =============================================================================
# Hematology Handler Tests
# =============================================================================

class TestHematologyHandlers:
    """Tests for hematology calculator handlers"""

    def test_register_hematology_tools(self, mock_mcp: Any, use_case: Any) -> None:
        """Test that hematology tools are registered correctly"""
        from src.infrastructure.mcp.handlers.calculators.hematology import register_hematology_tools
        register_hematology_tools(mock_mcp, use_case)

        expected_tools = [
            'calculate_4ts_hit'
        ]
        for tool in expected_tools:
            assert tool in mock_mcp.tools, f"Tool {tool} should be registered"

    def test_calculate_4ts_hit(self, mock_mcp: Any, use_case: Any) -> None:
        """Test 4Ts HIT score calculation - internal tool_id is 4ts_hit"""
        from src.infrastructure.mcp.handlers.calculators.hematology import register_hematology_tools
        register_hematology_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_4ts_hit')(
            thrombocytopenia_score=2,
            timing_score=2,
            thrombosis_score=1,
            other_causes_score=1
        )
        # The result should be successful
        assert result['success'] is True
        assert result['result'] == 6


# =============================================================================
# Pediatrics Handler Tests
# =============================================================================

class TestPediatricsHandlers:
    """Tests for pediatrics calculator handlers"""

    def test_register_pediatric_tools(self, mock_mcp: Any, use_case: Any) -> None:
        """Test that pediatric tools are registered correctly"""
        from src.infrastructure.mcp.handlers.calculators.pediatric import register_pediatric_tools
        register_pediatric_tools(mock_mcp, use_case)

        # pediatric.py has drug_dose, mabl, transfusion_volume
        expected_tools = [
            'calculate_pediatric_drug_dose', 'calculate_mabl', 'calculate_transfusion_volume'
        ]
        for tool in expected_tools:
            assert tool in mock_mcp.tools, f"Tool {tool} should be registered"

    def test_calculate_mabl(self, mock_mcp: Any, use_case: Any) -> None:
        """Test MABL calculation"""
        from src.infrastructure.mcp.handlers.calculators.pediatric import register_pediatric_tools
        register_pediatric_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_mabl')(
            weight_kg=70.0,
            initial_hematocrit=40.0,
            target_hematocrit=30.0
        )
        assert result['success'] is True
        assert 'result' in result


# =============================================================================
# Pediatric Scores Handler Tests
# =============================================================================

class TestPediatricScoresHandlers:
    """Tests for pediatric scores calculator handlers"""

    def test_register_pediatric_score_tools(self, mock_mcp: Any, use_case: Any) -> None:
        """Test that pediatric score tools are registered correctly"""
        from src.infrastructure.mcp.handlers.calculators.pediatric_scores import (
            register_pediatric_score_tools,
        )
        register_pediatric_score_tools(mock_mcp, use_case)  # Takes mcp and use_case

        expected_tools = [
            'calculate_apgar_score', 'calculate_pews'
        ]
        for tool in expected_tools:
            assert tool in mock_mcp.tools, f"Tool {tool} should be registered"

    def test_calculate_apgar_score(self, mock_mcp: Any, use_case: Any) -> None:
        """Test APGAR score calculation

        Note: pediatric_scores handlers call calculators directly (not through use_case),
        so they return ScoreResult.to_dict() format with 'value' instead of 'success'/'result'.
        """
        from src.infrastructure.mcp.handlers.calculators.pediatric_scores import (
            register_pediatric_score_tools,
        )
        register_pediatric_score_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_apgar_score')(
            appearance=2,
            pulse=2,
            grimace=2,
            activity=2,
            respiration=2
        )
        # This handler returns CalculateResponse.to_dict() format
        assert result['result'] == 10  # Perfect APGAR score
        assert result['success'] is True
        assert result['tool_id'] == 'apgar_score'
        assert 'component_scores' in result


# =============================================================================
# General Handler Tests
# =============================================================================

class TestGeneralHandlers:
    """Tests for general calculator handlers"""

    def test_register_general_tools(self, mock_mcp: Any, use_case: Any) -> None:
        """Test that general tools are registered correctly"""
        from src.infrastructure.mcp.handlers.calculators.general import register_general_tools
        register_general_tools(mock_mcp, use_case)

        expected_tools = [
            'calculate_bsa', 'calculate_cockcroft_gault'
        ]
        for tool in expected_tools:
            assert tool in mock_mcp.tools, f"Tool {tool} should be registered"

    def test_calculate_bsa(self, mock_mcp: Any, use_case: Any) -> None:
        """Test BSA calculation"""
        from src.infrastructure.mcp.handlers.calculators.general import register_general_tools
        register_general_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_bsa')(
            weight_kg=70.0,
            height_cm=170.0
        )
        assert result['success'] is True
        assert 'result' in result


# =============================================================================
# Edge Case Tests
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""

    def test_gcs_minimum_values(self, mock_mcp: Any, use_case: Any) -> None:
        """Test GCS with minimum values"""
        from src.infrastructure.mcp.handlers.calculators.critical_care import (
            register_critical_care_tools,
        )
        register_critical_care_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_gcs')(
            eye_response=1,
            verbal_response=1,
            motor_response=1
        )
        assert result['success'] is True
        assert result['result'] == 3  # Minimum GCS

    def test_qsofa_all_negative(self, mock_mcp: Any, use_case: Any) -> None:
        """Test qSOFA with all criteria negative"""
        from src.infrastructure.mcp.handlers.calculators.critical_care import (
            register_critical_care_tools,
        )
        register_critical_care_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_qsofa')(
            respiratory_rate=16,
            systolic_bp=120,
            altered_mentation=False
        )
        assert result['success'] is True
        assert result['result'] == 0

    def test_chads2_vasc_maximum_score(self, mock_mcp: Any, use_case: Any) -> None:
        """Test CHA2DS2-VASc with maximum score"""
        from src.infrastructure.mcp.handlers.calculators.cardiology import register_cardiology_tools
        register_cardiology_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_chads2_vasc')(
            chf_or_lvef_lte_40=True,
            hypertension=True,
            age_gte_75=True,
            diabetes=True,
            stroke_tia_or_te_history=True,
            vascular_disease=True,
            age_65_to_74=False,  # Not applicable if >=75
            female_sex=True
        )
        assert result['success'] is True
        assert result['result'] == 9  # Maximum score


# =============================================================================
# Integration Tests
# =============================================================================

class TestHandlerIntegration:
    """Integration tests for multiple handlers working together"""

    def test_multiple_handlers_registration(self, mock_mcp: Any, use_case: Any) -> None:
        """Test registering multiple handler categories"""
        from src.infrastructure.mcp.handlers.calculators.cardiology import register_cardiology_tools
        from src.infrastructure.mcp.handlers.calculators.critical_care import (
            register_critical_care_tools,
        )
        from src.infrastructure.mcp.handlers.calculators.nephrology import register_nephrology_tools

        register_critical_care_tools(mock_mcp, use_case)
        register_nephrology_tools(mock_mcp, use_case)
        register_cardiology_tools(mock_mcp, use_case)

        # All tools should be registered
        assert 'calculate_gcs' in mock_mcp.tools
        assert 'calculate_ckd_epi_2021' in mock_mcp.tools
        assert 'calculate_chads2_vasc' in mock_mcp.tools

    def test_handler_response_structure(self, mock_mcp: Any, use_case: Any) -> None:
        """Test that all handlers return consistent response structure"""
        from src.infrastructure.mcp.handlers.calculators.critical_care import (
            register_critical_care_tools,
        )
        register_critical_care_tools(mock_mcp, use_case)

        result = mock_mcp.get_tool('calculate_gcs')(
            eye_response=4,
            verbal_response=5,
            motor_response=6
        )

        # Check response structure
        assert 'success' in result
        assert 'result' in result
        assert 'tool_id' in result
        assert 'interpretation' in result
