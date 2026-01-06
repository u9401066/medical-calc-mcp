#!/usr/bin/env python
"""
Basic Usage Examples for Medical Calculator MCP Server

This script demonstrates how to use the medical calculators directly
in Python without going through the MCP protocol.

For MCP integration, see the README.md for VS Code Copilot or Claude Desktop setup.
"""

import sys
from pathlib import Path
from typing import Any

# Add project root to path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


# =============================================================================
# Example 1: CKD-EPI 2021 (eGFR Calculation)
# =============================================================================

def example_ckd_epi() -> None:
    """Calculate eGFR using CKD-EPI 2021 equation"""
    from src.domain.services.calculators import CkdEpi2021Calculator

    calc = CkdEpi2021Calculator()

    # 65-year-old female with creatinine 1.2 mg/dL
    result: Any = calc.calculate(
        serum_creatinine=1.2,
        age=65,
        sex="female"
    )

    print("=" * 60)
    print("CKD-EPI 2021 Example")
    print("=" * 60)
    print(f"eGFR: {result.value:.1f} {result.unit}")
    print(f"Stage: {result.interpretation.stage}")
    print(f"Summary: {result.interpretation.summary}")
    print()


# =============================================================================
# Example 2: SOFA Score (Sepsis Assessment)
# =============================================================================

def example_sofa() -> None:
    """Calculate SOFA score for sepsis assessment"""
    from src.domain.services.calculators import SofaScoreCalculator

    calc = SofaScoreCalculator()

    # ICU patient with moderate organ dysfunction
    result: Any = calc.calculate(
        pao2_fio2_ratio=200,      # Respiratory: 2 points
        platelets=80,              # Coagulation: 2 points
        bilirubin=2.5,             # Liver: 1 point
        dopamine_dose=5.0,         # Cardiovascular: 2 points
        gcs_score=13,              # Neurological: 1 point
        creatinine=2.0             # Renal: 1 point
    )

    print("=" * 60)
    print("SOFA Score Example (Sepsis-3)")
    print("=" * 60)
    print(f"SOFA Score: {int(result.value)}")
    print(f"Severity: {result.interpretation.severity.value}")
    print(f"Summary: {result.interpretation.summary}")
    print()


# =============================================================================
# Example 3: RCRI (Cardiac Risk for Non-Cardiac Surgery)
# =============================================================================

def example_rcri() -> None:
    """Calculate RCRI for preoperative cardiac risk"""
    from src.domain.services.calculators import RcriCalculator

    calc = RcriCalculator()

    # Patient undergoing major surgery with cardiac history
    result: Any = calc.calculate(
        high_risk_surgery=True,
        ischemic_heart_disease=True,
        heart_failure=False,
        cerebrovascular_disease=False,
        insulin_diabetes=True,
        creatinine_above_2=False
    )

    print("=" * 60)
    print("RCRI (Revised Cardiac Risk Index) Example")
    print("=" * 60)
    print(f"RCRI Score: {int(result.value)}")
    print(f"Summary: {result.interpretation.summary}")
    print("Recommendations:")
    for rec in result.interpretation.recommendations[:3]:
        print(f"  • {rec}")
    print()


# =============================================================================
# Example 4: CHA₂DS₂-VASc (AF Stroke Risk)
# =============================================================================

def example_chads2_vasc() -> None:
    """Calculate CHA₂DS₂-VASc for atrial fibrillation"""
    from src.domain.services.calculators import Chads2VascCalculator

    calc = Chads2VascCalculator()

    # 70-year-old male with hypertension and diabetes
    result: Any = calc.calculate(
        chf_or_lvef_lte_40=False,
        hypertension=True,
        age_gte_75=False,
        diabetes=True,
        stroke_tia_or_te_history=False,
        vascular_disease=False,
        age_65_to_74=True,
        female_sex=False
    )

    print("=" * 60)
    print("CHA₂DS₂-VASc Example (AF Stroke Risk)")
    print("=" * 60)
    print(f"Score: {int(result.value)}")
    print(f"Summary: {result.interpretation.summary}")
    print("Recommendations:")
    for rec in result.interpretation.recommendations[:2]:
        print(f"  • {rec}")
    print()


# =============================================================================
# Example 5: Wells PE Score
# =============================================================================

def example_wells_pe() -> None:
    """Calculate Wells score for PE probability"""
    from src.domain.services.calculators import WellsPeCalculator

    calc = WellsPeCalculator()

    # Patient with suspected PE
    result: Any = calc.calculate(
        clinical_signs_dvt=True,
        pe_most_likely_diagnosis=True,
        heart_rate_gt_100=True,
        immobilization_or_surgery=False,
        previous_dvt_pe=False,
        hemoptysis=False,
        malignancy=False
    )

    print("=" * 60)
    print("Wells PE Score Example")
    print("=" * 60)
    print(f"Score: {result.value}")
    print(f"Summary: {result.interpretation.summary}")
    print("Next Steps:")
    for step in result.interpretation.next_steps[:2]:
        print(f"  • {step}")
    print()


# =============================================================================
# Example 6: Tool Discovery
# =============================================================================

def example_discovery() -> None:
    """Demonstrate tool discovery capabilities"""
    from src.domain.registry.tool_registry import get_registry

    registry = get_registry()

    print("=" * 60)
    print("Tool Discovery Example")
    print("=" * 60)

    # List all available calculators
    all_tools = registry.list_all()
    print(f"Total calculators available: {len(all_tools)}")

    # Search by keyword
    sepsis_tools = registry.search("sepsis")
    print(f"\nTools matching 'sepsis': {len(sepsis_tools)}")
    for tool in sepsis_tools:
        print(f"  • {tool.tool_id}: {tool.name}")

    # List by specialty
    from src.domain.value_objects.tool_keys import Specialty
    cardio_tools = registry.list_by_specialty(Specialty.CARDIOLOGY)
    print(f"\nCardiology tools: {len(cardio_tools)}")
    for tool in cardio_tools[:3]:
        print(f"  • {tool.tool_id}: {tool.name}")

    print()


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Medical Calculator MCP Server - Usage Examples")
    print("=" * 60 + "\n")

    example_ckd_epi()
    example_sofa()
    example_rcri()
    example_chads2_vasc()
    example_wells_pe()
    example_discovery()

    print("=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)
