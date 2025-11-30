#!/usr/bin/env python
"""
Clinical Workflow Examples for Medical Calculator MCP Server

This script demonstrates multi-calculator workflows for common clinical scenarios,
similar to what an AI agent would do when using MCP tools.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


# =============================================================================
# Workflow 1: Sepsis Evaluation (Sepsis-3 Guidelines)
# =============================================================================

def workflow_sepsis_evaluation():
    """
    Complete sepsis workup following Sepsis-3 guidelines.
    
    Flow: qSOFA → SOFA → RASS → CAM-ICU
    """
    from src.domain.services.calculators import (
        QsofaScoreCalculator,
        SofaScoreCalculator,
        RassCalculator,
        CamIcuCalculator,
    )
    
    print("=" * 70)
    print("WORKFLOW: Sepsis Evaluation (Sepsis-3)")
    print("=" * 70)
    print("\nPatient: 68M with pneumonia, fever, altered mental status\n")
    
    # Step 1: qSOFA (bedside screening)
    print("Step 1: qSOFA (Quick SOFA) - Bedside Screening")
    print("-" * 50)
    qsofa = QsofaScoreCalculator()
    qsofa_result = qsofa.calculate(
        respiratory_rate=24,
        systolic_bp=95,
        altered_mentation=True
    )
    print(f"  Score: {int(qsofa_result.value)}/3")
    print(f"  Result: {qsofa_result.interpretation.summary}")
    
    if qsofa_result.value >= 2:
        print("  ⚠️  qSOFA ≥2: Proceed with full SOFA assessment\n")
        
        # Step 2: Full SOFA
        print("Step 2: SOFA Score - Organ Dysfunction Assessment")
        print("-" * 50)
        sofa = SofaScoreCalculator()
        sofa_result = sofa.calculate(
            pao2_fio2_ratio=250,
            platelets=120,
            bilirubin=1.5,
            gcs_score=14,
            creatinine=1.8
        )
        print(f"  Score: {int(sofa_result.value)}/24")
        print(f"  Result: {sofa_result.interpretation.summary}")
        
        if sofa_result.value >= 2:
            print("  ⚠️  SOFA ≥2: If infection suspected, SEPSIS CONFIRMED\n")
    
    # Step 3: RASS (sedation assessment)
    print("Step 3: RASS - Sedation/Agitation Assessment")
    print("-" * 50)
    rass = RassCalculator()
    rass_result = rass.calculate(rass_score=0)
    print(f"  Score: {int(rass_result.value)}")
    print(f"  Result: {rass_result.interpretation.summary}")
    
    # Step 4: CAM-ICU (delirium screening)
    print("\nStep 4: CAM-ICU - Delirium Screening")
    print("-" * 50)
    cam_icu = CamIcuCalculator()
    cam_result = cam_icu.calculate(
        rass_score=0,
        acute_onset_fluctuation=True,
        inattention_score=4,
        disorganized_thinking_errors=1
    )
    print(f"  Result: {'POSITIVE (Delirium)' if cam_result.value == 1 else 'NEGATIVE'}")
    print(f"  Summary: {cam_result.interpretation.summary}")
    
    print("\n" + "=" * 70 + "\n")


# =============================================================================
# Workflow 2: Preoperative Risk Assessment
# =============================================================================

def workflow_preoperative_assessment():
    """
    Complete preoperative risk evaluation.
    
    Flow: ASA → RCRI → Mallampati → MABL
    """
    from src.domain.services.calculators import (
        AsaPhysicalStatusCalculator,
        RcriCalculator,
        MallampatiScoreCalculator,
        MablCalculator,
    )
    
    print("=" * 70)
    print("WORKFLOW: Preoperative Risk Assessment")
    print("=" * 70)
    print("\nPatient: 72F with DM, HTN, scheduled for hip replacement\n")
    
    # Step 1: ASA Physical Status
    print("Step 1: ASA Physical Status Classification")
    print("-" * 50)
    asa = AsaPhysicalStatusCalculator()
    asa_result = asa.calculate(asa_class=3, is_emergency=False)
    print(f"  Classification: ASA {int(asa_result.value)}")
    print(f"  Summary: {asa_result.interpretation.summary}")
    
    # Step 2: RCRI
    print("\nStep 2: RCRI - Cardiac Risk Assessment")
    print("-" * 50)
    rcri = RcriCalculator()
    rcri_result = rcri.calculate(
        high_risk_surgery=True,  # Hip replacement
        ischemic_heart_disease=False,
        heart_failure=False,
        cerebrovascular_disease=False,
        insulin_diabetes=True,
        creatinine_above_2=False
    )
    print(f"  Score: {int(rcri_result.value)}/6")
    print(f"  Summary: {rcri_result.interpretation.summary}")
    
    # Step 3: Mallampati
    print("\nStep 3: Mallampati - Airway Assessment")
    print("-" * 50)
    mallampati = MallampatiScoreCalculator()
    mallampati_result = mallampati.calculate(mallampati_class=2)
    print(f"  Classification: Mallampati {int(mallampati_result.value)}")
    print(f"  Summary: {mallampati_result.interpretation.summary}")
    
    # Step 4: MABL
    print("\nStep 4: MABL - Maximum Allowable Blood Loss")
    print("-" * 50)
    mabl = MablCalculator()
    mabl_result = mabl.calculate(
        weight_kg=65,
        initial_hematocrit=38,
        target_hematocrit=25,
        patient_type="adult_female"
    )
    print(f"  MABL: {int(mabl_result.value)} mL")
    print(f"  Summary: {mabl_result.interpretation.summary}")
    
    print("\n" + "=" * 70 + "\n")


# =============================================================================
# Workflow 3: Chest Pain Evaluation (ED)
# =============================================================================

def workflow_chest_pain_ed():
    """
    Emergency department chest pain workup.
    
    Flow: HEART Score → (if needed) Wells PE
    """
    from src.domain.services.calculators import (
        HeartScoreCalculator,
        WellsPeCalculator,
    )
    
    print("=" * 70)
    print("WORKFLOW: ED Chest Pain Evaluation")
    print("=" * 70)
    print("\nPatient: 55M with acute chest pain, diaphoresis\n")
    
    # Step 1: HEART Score
    print("Step 1: HEART Score - MACE Risk Stratification")
    print("-" * 50)
    heart = HeartScoreCalculator()
    heart_result = heart.calculate(
        history_score=2,        # Highly suspicious
        ecg_score=1,            # Non-specific changes
        age_score=1,            # 45-64 years
        risk_factors_score=2,   # ≥3 risk factors
        troponin_score=1        # 1-3x ULN
    )
    print(f"  Score: {int(heart_result.value)}/10")
    print(f"  Summary: {heart_result.interpretation.summary}")
    print(f"  Recommendations:")
    for rec in heart_result.interpretation.recommendations[:2]:
        print(f"    • {rec}")
    
    # Step 2: Consider PE if atypical presentation
    print("\nStep 2: Wells PE Score (if PE suspected)")
    print("-" * 50)
    wells_pe = WellsPeCalculator()
    wells_result = wells_pe.calculate(
        clinical_signs_dvt=False,
        pe_most_likely_diagnosis=False,
        heart_rate_gt_100=True,
        immobilization_or_surgery=False,
        previous_dvt_pe=False,
        hemoptysis=False,
        malignancy=False
    )
    print(f"  Score: {wells_result.value}")
    print(f"  Summary: {wells_result.interpretation.summary}")
    
    print("\n" + "=" * 70 + "\n")


# =============================================================================
# Workflow 4: AF Anticoagulation Decision
# =============================================================================

def workflow_af_anticoagulation():
    """
    Atrial fibrillation anticoagulation decision.
    
    Uses: CHA₂DS₂-VASc (stroke risk)
    """
    from src.domain.services.calculators import Chads2VascCalculator
    
    print("=" * 70)
    print("WORKFLOW: AF Anticoagulation Decision")
    print("=" * 70)
    print("\nPatient: 78F with new AF, HTN, prior stroke\n")
    
    # CHA₂DS₂-VASc Score
    print("CHA₂DS₂-VASc Score - Stroke Risk")
    print("-" * 50)
    chads = Chads2VascCalculator()
    result = chads.calculate(
        chf_or_lvef_lte_40=False,
        hypertension=True,
        age_gte_75=True,           # +2 points
        diabetes=False,
        stroke_tia_or_te_history=True,  # +2 points
        vascular_disease=False,
        age_65_to_74=False,        # Not applicable (≥75)
        female_sex=True            # +1 point
    )
    print(f"  Score: {int(result.value)}/9")
    print(f"  Summary: {result.interpretation.summary}")
    print(f"  Recommendations:")
    for rec in result.interpretation.recommendations:
        print(f"    • {rec}")
    
    print("\n" + "=" * 70 + "\n")


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Medical Calculator MCP Server - Clinical Workflow Examples")
    print("=" * 70 + "\n")
    
    workflow_sepsis_evaluation()
    workflow_preoperative_assessment()
    workflow_chest_pain_ed()
    workflow_af_anticoagulation()
    
    print("=" * 70)
    print("All workflows completed successfully!")
    print("=" * 70)
