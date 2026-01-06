from typing import Any

"""
Pytest Configuration for Medical Calculator MCP Tests

Provides shared fixtures and configuration for all tests.
Compatible with VS Code Python Test Explorer and Copilot.
"""

import sys
from pathlib import Path

import pytest

# Ensure src is in path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@pytest.fixture
def registry() -> Any:
    """Provide a configured ToolRegistry with all calculators."""
    from src.domain.registry import ToolRegistry
    from src.domain.services.calculators import CALCULATORS

    reg = ToolRegistry()
    for calc_class in CALCULATORS:
        calc = calc_class()
        reg.register(calc)
    return reg


@pytest.fixture
def calculator_classes() -> Any:
    """Provide list of all calculator classes."""
    from src.domain.services.calculators import CALCULATORS
    return CALCULATORS


@pytest.fixture
def sample_params() -> Any:
    """Provide sample valid parameters for each calculator."""
    return {
        # Nephrology
        "ckd_epi_2021": {
            "creatinine": 1.2,
            "age": 65,
            "sex": "male",
        },
        # Anesthesiology
        "asa_physical_status": {
            "classification": 2,
        },
        "mallampati": {
            "grade": 2,
        },
        "rcri": {
            "high_risk_surgery": True,
            "ischemic_heart_disease": False,
            "congestive_heart_failure": False,
            "cerebrovascular_disease": False,
            "diabetes_on_insulin": True,
            "creatinine_greater_than_2": False,
        },
        # Critical Care
        "apache_ii": {
            "temperature": 38.5,
            "mean_arterial_pressure": 70,
            "heart_rate": 110,
            "respiratory_rate": 24,
            "pao2_or_aado2": 70,
            "fio2": 0.4,
            "arterial_ph": 7.35,
            "sodium": 140,
            "potassium": 4.0,
            "creatinine": 1.5,
            "acute_renal_failure": False,
            "hematocrit": 35,
            "wbc": 12,
            "gcs": 14,
            "age": 65,
            "chronic_health": "none",
        },
        "rass": {
            "score": 0,
        },
        "sofa": {
            "pao2_fio2_ratio": 300,
            "platelets": 100,
            "bilirubin": 2.0,
            "cardiovascular": "map_less_than_70",
            "gcs": 14,
            "creatinine": 1.5,
            "urine_output_24h": 500,
        },
        "qsofa": {
            "respiratory_rate_22_or_higher": True,
            "altered_mental_status": False,
            "systolic_bp_100_or_less": True,
        },
        "news": {
            "respiratory_rate": 22,
            "oxygen_saturation": 94,
            "supplemental_oxygen": True,
            "temperature": 38.5,
            "systolic_bp": 110,
            "heart_rate": 95,
            "consciousness": "alert",
        },
        "gcs": {
            "eye_response": 4,
            "verbal_response": 5,
            "motor_response": 6,
        },
        "cam_icu": {
            "rass_score": 0,
            "feature1_acute_onset": True,
            "feature2_inattention": True,
            "feature3_altered_loc": False,
            "feature4_disorganized_thinking": True,
        },
        # Pediatric
        "pediatric_dosing": {
            "weight_kg": 25,
            "drug_name": "amoxicillin",
        },
        "mabl": {
            "weight_kg": 70,
            "starting_hematocrit": 40,
            "minimum_hematocrit": 25,
        },
        "transfusion": {
            "weight_kg": 70,
            "current_hematocrit": 25,
            "target_hematocrit": 35,
        },
        # Pulmonology
        "curb65": {
            "confusion": True,
            "bun_greater_than_19": True,
            "respiratory_rate_30_or_more": False,
            "systolic_bp_less_than_90": False,
            "diastolic_bp_60_or_less": False,
            "age_65_or_older": True,
        },
        "psi_port": {
            "age": 70,
            "sex": "male",
            "nursing_home_resident": False,
            "neoplastic_disease": False,
            "liver_disease": False,
            "congestive_heart_failure": False,
            "cerebrovascular_disease": False,
            "renal_disease": False,
            "altered_mental_status": True,
            "respiratory_rate_30_or_higher": False,
            "systolic_bp_less_than_90": False,
            "temperature_less_than_35_or_40_plus": False,
            "pulse_125_or_higher": False,
            "arterial_ph_less_than_7_35": False,
            "bun_30_or_higher": False,
            "sodium_less_than_130": False,
            "glucose_250_or_higher": False,
            "hematocrit_less_than_30": False,
            "pao2_less_than_60": False,
            "pleural_effusion": False,
        },
        # Cardiology
        "chads2_vasc": {
            "congestive_heart_failure": True,
            "hypertension": True,
            "age": 75,
            "diabetes": False,
            "stroke_tia_thromboembolism": False,
            "vascular_disease": True,
            "sex": "female",
        },
        "chads2_va": {
            "congestive_heart_failure": True,
            "hypertension": True,
            "age": 75,
            "diabetes": False,
            "stroke_tia_thromboembolism": False,
            "vascular_disease": True,
        },
        "heart_score": {
            "history": 1,
            "ecg": 1,
            "age": 55,
            "risk_factors": 1,
            "troponin": 1,
        },
        # Emergency Medicine
        "wells_dvt": {
            "active_cancer": False,
            "paralysis_or_immobilization": False,
            "bedridden_or_major_surgery": True,
            "localized_tenderness": True,
            "entire_leg_swollen": False,
            "calf_swelling_3cm": True,
            "pitting_edema": True,
            "collateral_superficial_veins": False,
            "previously_documented_dvt": False,
            "alternative_diagnosis_likely": False,
        },
        "wells_pe": {
            "clinical_signs_dvt": True,
            "pe_most_likely_diagnosis": True,
            "heart_rate_over_100": False,
            "immobilization_or_surgery": False,
            "previous_dvt_pe": False,
            "hemoptysis": False,
            "malignancy": False,
        },
        # Hepatology
        "meld": {
            "bilirubin": 2.0,
            "inr": 1.5,
            "creatinine": 1.2,
            "sodium": 135,
            "dialysis_twice_in_past_week": False,
        },
        # Surgery
        "caprini_vte": {
            "age": 55,
            "planned_surgery_type": "major_surgery_over_45_min",
            "bmi_over_25": True,
            "sepsis_within_1_month": False,
            "serious_lung_disease": False,
            "abnormal_pulmonary_function": False,
            "current_chf": False,
            "history_mi": False,
            "prior_vte": False,
            "family_history_vte": False,
            "factor_v_leiden": False,
            "prothrombin_mutation": False,
            "lupus_anticoagulant": False,
            "anticardiolipin_antibody": False,
            "heparin_induced_thrombocytopenia": False,
            "other_thrombophilia": False,
            "immobility": False,
            "central_venous_access": False,
        },
    }
