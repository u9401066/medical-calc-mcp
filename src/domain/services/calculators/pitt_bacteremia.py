"""
Pitt Bacteremia Score Calculator

Predicts mortality in patients with gram-negative bacteremia.
Higher scores associated with increased mortality risk.

Original Reference:
    Paterson DL, Ko WC, Von Gottberg A, et al. International prospective
    study of Klebsiella pneumoniae bacteremia: implications of extended-spectrum
    beta-lactamase production in nosocomial Infections. Ann Intern Med.
    2004;140(1):26-32. doi:10.7326/0003-4819-140-1-200401060-00008. PMID: 14706969.

Earlier version reference:
    Chow JW, Fine MJ, Shlaes DM, et al. Enterobacter bacteremia: clinical
    features and emergence of antibiotic resistance during therapy.
    Ann Intern Med. 1991;115(8):585-590. PMID: 1892329.
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


class PittBacteremiaCalculator(BaseCalculator):
    """
    Pitt Bacteremia Score

    Scoring criteria (within 48h before or on day of positive culture):

    Temperature:
    - ≤35.0°C or ≥40.0°C: +2
    - 35.1-36.0°C or 39.0-39.9°C: +1
    - 36.1-38.9°C: +0

    Blood Pressure:
    - Acute hypotension with SBP drop ≥30 mmHg and SBP <90 mmHg,
      OR vasopressors required, OR MAP <60 mmHg: +2

    Mechanical Ventilation: +2

    Cardiac Arrest: +4

    Mental Status:
    - Disoriented: +1
    - Stuporous: +2
    - Comatose: +4

    Risk stratification:
    - 0-3: Low risk (~5-10% mortality)
    - 4-7: Moderate risk (~30-50% mortality)
    - ≥8: High risk (>50% mortality)
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="pitt_bacteremia",
                name="Pitt Bacteremia Score",
                purpose="Predict mortality in gram-negative bacteremia patients",
                input_params=[
                    "temperature_category",
                    "hypotension",
                    "mechanical_ventilation",
                    "cardiac_arrest",
                    "mental_status",
                ],
                output_type="Score 0-14 with mortality risk stratification"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.INFECTIOUS_DISEASE,
                    Specialty.CRITICAL_CARE,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.EMERGENCY_MEDICINE,
                ),
                conditions=(
                    "bacteremia",
                    "gram-negative bacteremia",
                    "bloodstream infection",
                    "BSI",
                    "sepsis",
                    "Klebsiella bacteremia",
                    "E. coli bacteremia",
                    "Pseudomonas bacteremia",
                ),
                clinical_contexts=(
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.RISK_STRATIFICATION,
                ),
            ),
            references=(
                Reference(
                    citation="Paterson DL, et al. Ann Intern Med. 2004;140(1):26-32.",
                    pmid="14706969",
                    doi="10.7326/0003-4819-140-1-200401060-00008",
                ),
                Reference(
                    citation="Chow JW, et al. Ann Intern Med. 1991;115(8):585-590. (Original derivation)",
                    pmid="1892329",
                ),
            ),
        )

    def calculate(
        self,
        temperature_category: str,  # "normal", "low_mild", "extreme"
        hypotension: bool,
        mechanical_ventilation: bool,
        cardiac_arrest: bool,
        mental_status: str,  # "alert", "disoriented", "stuporous", "comatose"
    ) -> ScoreResult:
        """
        Calculate Pitt Bacteremia Score.

        Args:
            temperature_category: Temperature range
                - "normal": 36.1-38.9°C (0 points)
                - "low_mild": 35.1-36.0°C or 39.0-39.9°C (1 point)
                - "extreme": ≤35.0°C or ≥40.0°C (2 points)
            hypotension: Acute hypotension with SBP drop ≥30 mmHg and SBP <90,
                        OR vasopressors, OR MAP <60 mmHg
            mechanical_ventilation: On mechanical ventilation
            cardiac_arrest: Cardiac arrest within 24 hours
            mental_status: Mental status category
                - "alert": Normal mentation (0 points)
                - "disoriented": Disoriented (1 point)
                - "stuporous": Stuporous (2 points)
                - "comatose": Comatose (4 points)

        Returns:
            ScoreResult with Pitt score and mortality risk
        """
        score = 0
        components: dict[str, Any] = {}

        # Temperature
        if temperature_category == "extreme":
            score += 2
            components["temperature"] = "≤35.0°C or ≥40.0°C (+2)"
        elif temperature_category == "low_mild":
            score += 1
            components["temperature"] = "35.1-36.0°C or 39.0-39.9°C (+1)"
        else:  # normal
            components["temperature"] = "36.1-38.9°C (+0)"

        # Hypotension
        if hypotension:
            score += 2
            components["hypotension"] = "Acute hypotension/vasopressors (+2)"
        else:
            components["hypotension"] = "Normotensive (+0)"

        # Mechanical ventilation
        if mechanical_ventilation:
            score += 2
            components["ventilation"] = "Mechanical ventilation (+2)"
        else:
            components["ventilation"] = "No mechanical ventilation (+0)"

        # Cardiac arrest
        if cardiac_arrest:
            score += 4
            components["cardiac_arrest"] = "Cardiac arrest (+4)"
        else:
            components["cardiac_arrest"] = "No cardiac arrest (+0)"

        # Mental status
        mental_scores = {
            "alert": (0, "Alert (+0)"),
            "disoriented": (1, "Disoriented (+1)"),
            "stuporous": (2, "Stuporous (+2)"),
            "comatose": (4, "Comatose (+4)"),
        }
        ms_score, ms_desc = mental_scores.get(mental_status, (0, "Alert (+0)"))
        score += ms_score
        components["mental_status"] = ms_desc

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
        """Generate interpretation based on Pitt Bacteremia Score"""

        if score <= 3:
            severity = Severity.MILD
            risk_level = RiskLevel.LOW
            summary = f"Pitt Bacteremia Score {score}: Low risk (5-10% mortality)"
            detail = (
                "Low Pitt Score. Continue appropriate antibiotic therapy based on cultures/sensitivities. "
                "Monitor for clinical improvement within 48-72 hours."
            )
            recommendations = [
                "Continue appropriate antibiotic therapy",
                "Monitor for clinical improvement",
                "Reassess at 48-72 hours",
            ]
            next_steps = [
                "Adjust antibiotics based on culture and sensitivity results",
                "Identify and address source of bacteremia",
                "Consider de-escalation if clinically stable",
            ]
        elif score <= 7:
            severity = Severity.MODERATE
            risk_level = RiskLevel.INTERMEDIATE
            summary = f"Pitt Bacteremia Score {score}: Moderate risk (30-50% mortality)"
            detail = (
                "Moderate Pitt Score indicates significant risk. "
                "Ensure source control, optimize antibiotic therapy, consider ICU if not already admitted. "
                "Close monitoring for clinical deterioration required."
            )
            recommendations = [
                "Ensure source control if applicable",
                "Optimize antibiotic therapy",
                "Consider ICU admission if not already there",
                "Close monitoring for deterioration",
            ]
            next_steps = [
                "Infectious disease consultation if not already involved",
                "Repeat blood cultures to document clearance",
                "Consider echocardiogram if persistent bacteremia",
            ]
        else:
            severity = Severity.SEVERE
            risk_level = RiskLevel.HIGH
            summary = f"Pitt Bacteremia Score {score}: High risk (>50% mortality)"
            detail = (
                "High Pitt Score indicates severe bacteremia with high mortality risk. "
                "Aggressive management required: source control, ICU care, infectious disease consultation, "
                "consider combination antibiotic therapy."
            )
            recommendations = [
                "ICU-level care required",
                "Aggressive source control",
                "Consider combination antibiotic therapy",
                "Infectious disease consultation",
            ]
            next_steps = [
                "Ensure adequate resuscitation and hemodynamic support",
                "Urgent source control procedures if indicated",
                "Goals of care discussion may be appropriate",
            ]

        return Interpretation(
            summary=summary,
            detail=detail,
            severity=severity,
            risk_level=risk_level,
            recommendations=tuple(recommendations),
            next_steps=tuple(next_steps),
        )
