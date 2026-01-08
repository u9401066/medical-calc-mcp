"""
MASCC Score Calculator (Multinational Association for Supportive Care in Cancer)

Identifies low-risk febrile neutropenia patients who may be candidates for
outpatient management with oral antibiotics.

Original Reference:
    Klastersky J, Paesmans M, Rubenstein EB, et al. The Multinational
    Association for Supportive Care in Cancer Risk Index: A Multinational
    Scoring System for Identifying Low-Risk Febrile Neutropenic Cancer Patients.
    J Clin Oncol. 2000;18(16):3038-3051.
    doi:10.1200/JCO.2000.18.16.3038. PMID: 10944139.
"""

from typing import Any

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, RiskLevel, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import (
    ClinicalContext,
    HighLevelKey,
    LowLevelKey,
    Specialty,
)
from ...value_objects.units import Unit
from ..base import BaseCalculator


class MasccScoreCalculator(BaseCalculator):
    """
    MASCC Risk Index for Febrile Neutropenia

    Scoring criteria (maximum 26 points):
    - Burden of illness (choose one):
      - None or mild symptoms: +5
      - Moderate symptoms: +3
      - Severe symptoms: +0
    - No hypotension (SBP ≥90 mmHg): +5
    - No COPD: +4
    - Solid tumor or hematologic malignancy without previous fungal infection: +4
    - No dehydration requiring IV fluids: +3
    - Outpatient status at onset of fever: +3
    - Age <60 years: +2

    Risk stratification:
    - ≥21: Low risk (~5% serious complications) → Consider outpatient therapy
    - <21: High risk (~40% serious complications) → Inpatient therapy
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="mascc_score",
                name="MASCC Risk Index",
                purpose="Identify low-risk febrile neutropenia patients for potential outpatient management",
                input_params=[
                    "burden_of_illness",
                    "no_hypotension",
                    "no_copd",
                    "solid_tumor_or_no_fungal_hx",
                    "no_dehydration",
                    "outpatient_status",
                    "age_lt_60",
                ],
                output_type="Score 0-26 with risk classification and management recommendation",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.ONCOLOGY,
                    Specialty.INFECTIOUS_DISEASE,
                    Specialty.HEMATOLOGY,
                    Specialty.EMERGENCY_MEDICINE,
                ),
                conditions=(
                    "febrile neutropenia",
                    "neutropenic fever",
                    "chemotherapy-induced neutropenia",
                    "cancer fever",
                    "oncologic emergency",
                ),
                clinical_contexts=(
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.DISPOSITION,
                    ClinicalContext.TREATMENT_DECISION,
                ),
            ),
            references=(
                Reference(
                    citation="Klastersky J, et al. J Clin Oncol. 2000;18(16):3038-3051.",
                    pmid="10944139",
                    doi="10.1200/JCO.2000.18.16.3038",
                ),
                Reference(
                    citation="Taplitz RA, et al. J Clin Oncol. 2018;36(14):1443-1453. (IDSA/ASCO Febrile Neutropenia Guideline)",
                    pmid="29461916",
                    doi="10.1200/JCO.2017.77.6211",
                ),
            ),
        )

    def calculate(
        self,
        burden_of_illness: str,  # "none_mild", "moderate", "severe"
        no_hypotension: bool,
        no_copd: bool,
        solid_tumor_or_no_fungal_hx: bool,
        no_dehydration: bool,
        outpatient_status: bool,
        age_lt_60: bool,
    ) -> ScoreResult:
        """
        Calculate MASCC Risk Index.

        Args:
            burden_of_illness: Symptom severity ("none_mild", "moderate", "severe")
            no_hypotension: No hypotension (SBP ≥90 mmHg)
            no_copd: No history of COPD
            solid_tumor_or_no_fungal_hx: Solid tumor OR heme malignancy without prior fungal infection
            no_dehydration: No dehydration requiring IV fluids
            outpatient_status: Outpatient at fever onset
            age_lt_60: Age <60 years

        Returns:
            ScoreResult with MASCC score and risk classification
        """
        # Calculate score
        score = 0
        components: dict[str, Any] = {}

        # Burden of illness (mutually exclusive)
        if burden_of_illness == "none_mild":
            score += 5
            components["burden_of_illness"] = "None/Mild symptoms (+5)"
        elif burden_of_illness == "moderate":
            score += 3
            components["burden_of_illness"] = "Moderate symptoms (+3)"
        else:  # severe
            components["burden_of_illness"] = "Severe symptoms (+0)"

        # No hypotension
        if no_hypotension:
            score += 5
            components["blood_pressure"] = "No hypotension (+5)"
        else:
            components["blood_pressure"] = "Hypotension present (+0)"

        # No COPD
        if no_copd:
            score += 4
            components["copd"] = "No COPD (+4)"
        else:
            components["copd"] = "COPD present (+0)"

        # Tumor type
        if solid_tumor_or_no_fungal_hx:
            score += 4
            components["tumor_type"] = "Solid tumor or no fungal history (+4)"
        else:
            components["tumor_type"] = "Heme malignancy with fungal history (+0)"

        # No dehydration
        if no_dehydration:
            score += 3
            components["hydration"] = "No dehydration (+3)"
        else:
            components["hydration"] = "Dehydration present (+0)"

        # Outpatient status
        if outpatient_status:
            score += 3
            components["setting"] = "Outpatient at onset (+3)"
        else:
            components["setting"] = "Inpatient at onset (+0)"

        # Age
        if age_lt_60:
            score += 2
            components["age"] = "Age <60 years (+2)"
        else:
            components["age"] = "Age ≥60 years (+0)"

        # Generate interpretation
        interpretation = self._interpret_score(score)

        return ScoreResult(
            tool_name=self.low_level_key.name,
            tool_id=self.low_level_key.tool_id,
            value=score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            calculation_details=components,
            references=list(self.references),
        )

    def _interpret_score(self, score: int) -> Interpretation:
        """Generate interpretation based on MASCC score"""

        if score >= 21:
            severity = Severity.MILD
            risk_level = RiskLevel.LOW
            summary = f"MASCC Score {score}/26: Low risk (~5% serious complications)"
            detail = (
                "Low-risk febrile neutropenia. Patient may be candidate for outpatient "
                "management with oral fluoroquinolone + amoxicillin-clavulanate. "
                "Requires: reliable access to care, ability to take oral medications, no organ dysfunction."
            )
            recommendations = [
                "Consider outpatient oral antibiotics if criteria met",
                "Fluoroquinolone + amoxicillin-clavulanate is standard oral regimen",
                "Ensure patient has 24/7 access to medical care",
                "Patient must be able to take oral medications",
            ]
            next_steps = [
                "Verify outpatient criteria: reliable, can take PO, no organ dysfunction",
                "Provide clear fever precautions and return instructions",
                "Arrange follow-up within 24-48 hours",
            ]
        else:
            severity = Severity.SEVERE
            risk_level = RiskLevel.HIGH
            summary = f"MASCC Score {score}/26: High risk (~40% serious complications)"
            detail = (
                "High-risk febrile neutropenia. Recommend hospital admission with IV "
                "broad-spectrum antibiotics (anti-pseudomonal β-lactam). "
                "Consider adding vancomycin if catheter infection, skin/soft tissue infection, or hemodynamic instability."
            )
            recommendations = [
                "Admit for IV broad-spectrum antibiotics",
                "Anti-pseudomonal β-lactam (e.g., piperacillin-tazobactam, cefepime)",
                "Add vancomycin if catheter/skin infection or hemodynamic instability",
                "Obtain cultures before starting antibiotics",
            ]
            next_steps = [
                "Initiate empiric IV antibiotics within 1 hour",
                "Blood cultures (peripheral and central line if present)",
                "Assess for source of infection",
                "Consider G-CSF if prolonged neutropenia expected",
            ]

        return Interpretation(
            summary=summary,
            detail=detail,
            severity=severity,
            risk_level=risk_level,
            recommendations=tuple(recommendations),
            next_steps=tuple(next_steps),
        )
