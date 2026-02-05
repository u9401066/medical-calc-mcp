"""
ICIQ-SF (International Consultation on Incontinence Questionnaire - Short Form)

The ICIQ-SF is a validated brief questionnaire for assessing urinary
incontinence symptoms and impact on quality of life.

Reference (Original Validation):
    Avery K, Donovan J, Peters TJ, et al. ICIQ: a brief and robust measure
    for evaluating the symptoms and impact of urinary incontinence.
    Neurourol Urodyn. 2004;23(4):322-330.
    PMID: 15227649

Reference (ICS Recommendation):
    Abrams P, Cardozo L, Wagg A, Wein A (eds). Incontinence 6th Edition.
    International Continence Society. 2017.
"""

from typing import Any

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import (
    ClinicalContext,
    HighLevelKey,
    LowLevelKey,
    Specialty,
)
from ...value_objects.units import Unit
from ..base import BaseCalculator


class ICIQSFCalculator(BaseCalculator):
    """
    ICIQ-SF (ICIQ-Urinary Incontinence Short Form) Calculator

    3-item scored questionnaire (+ 1 diagnostic item).
    Score range: 0-21
    Higher scores = more severe incontinence impact.
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="iciq_sf",
                name="ICIQ-SF (International Consultation on Incontinence Questionnaire)",
                purpose="Assess urinary incontinence severity and impact",
                input_params=[
                    "leak_frequency",
                    "leak_amount",
                    "qol_interference",
                    "leak_situations",
                ],
                output_type="Score 0-21 with incontinence severity",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.UROLOGY,
                    Specialty.GYNECOLOGY,
                    Specialty.INTERNAL_MEDICINE,
                ),
                conditions=(
                    "Urinary Incontinence",
                    "Stress Incontinence",
                    "Urge Incontinence",
                    "Mixed Incontinence",
                    "Overactive Bladder",
                ),
                clinical_contexts=(
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.SCREENING,
                    ClinicalContext.MONITORING,
                    ClinicalContext.TREATMENT_DECISION,
                ),
                clinical_questions=(
                    "How severe is this patient's urinary incontinence?",
                    "Calculate ICIQ score",
                    "Assess incontinence severity",
                    "What type of incontinence does this patient have?",
                ),
                keywords=(
                    "ICIQ",
                    "ICIQ-SF",
                    "urinary incontinence",
                    "stress incontinence",
                    "urge incontinence",
                    "bladder leakage",
                ),
            ),
            references=(
                Reference(
                    citation="Avery K, Donovan J, Peters TJ, et al. ICIQ: a brief and robust measure for evaluating the symptoms and impact of urinary incontinence. Neurourol Urodyn. 2004;23(4):322-330.",
                    pmid="15227649",
                    doi="10.1002/nau.20041",
                    year=2004,
                ),
                Reference(
                    citation="Abrams P, Cardozo L, Wagg A, Wein A (eds). Incontinence 6th Edition. International Continence Society. 2017.",
                    url="https://www.ics.org/publications/ici_6",
                    year=2017,
                ),
            ),
        )

    def calculate(self, **params: Any) -> ScoreResult:
        """
        Calculate ICIQ-SF score.

        Args:
            leak_frequency: How often do you leak urine? (0-5)
                0 = Never
                1 = About once a week or less often
                2 = Two or three times a week
                3 = About once a day
                4 = Several times a day
                5 = All the time

            leak_amount: How much urine do you usually leak? (0, 2, 4, 6)
                0 = None
                2 = A small amount
                4 = A moderate amount
                6 = A large amount

            qol_interference: How much does leaking urine interfere with daily life? (0-10)
                0 = Not at all ... 10 = A great deal

            leak_situations: When does urine leak? (list of situations, for diagnostic purposes)
                Options: "never", "before_toilet", "cough_sneeze", "asleep",
                        "physical_activity", "finished_urinating", "no_reason", "all_the_time"

        Returns:
            ScoreResult with ICIQ-SF score and incontinence type
        """
        # Extract and validate scores
        frequency = int(params.get("leak_frequency", 0))
        if not 0 <= frequency <= 5:
            raise ValueError("leak_frequency must be 0-5")

        amount = int(params.get("leak_amount", 0))
        if amount not in [0, 2, 4, 6]:
            raise ValueError("leak_amount must be 0, 2, 4, or 6")

        qol = int(params.get("qol_interference", 0))
        if not 0 <= qol <= 10:
            raise ValueError("qol_interference must be 0-10")

        # Calculate total score (0-21)
        total_score = frequency + amount + qol

        # Get leak situations for diagnostic purposes
        situations_raw = params.get("leak_situations", [])
        if isinstance(situations_raw, str):
            situations = [s.strip().lower() for s in situations_raw.split(",")]
        else:
            situations = [str(s).lower() for s in situations_raw] if situations_raw else []

        # Determine incontinence type based on situations
        stress_indicators = {"cough_sneeze", "physical_activity", "finished_urinating"}
        urge_indicators = {"before_toilet", "no_reason", "all_the_time"}

        has_stress = bool(stress_indicators & set(situations))
        has_urge = bool(urge_indicators & set(situations))

        if has_stress and has_urge:
            incontinence_type = "Mixed incontinence"
        elif has_stress:
            incontinence_type = "Stress incontinence"
        elif has_urge:
            incontinence_type = "Urge incontinence"
        elif "asleep" in situations:
            incontinence_type = "Nocturnal enuresis"
        elif frequency == 0 and amount == 0:
            incontinence_type = "No incontinence"
        else:
            incontinence_type = "Unclassified incontinence"

        # Classify severity
        if total_score == 0:
            severity = Severity.NORMAL
            severity_text = "No incontinence"
            stage = "None"
        elif total_score <= 5:
            severity = Severity.MILD
            severity_text = "Slight incontinence"
            stage = "Slight"
        elif total_score <= 12:
            severity = Severity.MODERATE
            severity_text = "Moderate incontinence"
            stage = "Moderate"
        elif total_score <= 18:
            severity = Severity.SEVERE
            severity_text = "Severe incontinence"
            stage = "Severe"
        else:
            severity = Severity.CRITICAL
            severity_text = "Very severe incontinence"
            stage = "Very severe"

        # Recommendations based on type and severity
        recommendations = []
        if total_score == 0:
            recommendations.append("No incontinence - no intervention needed")
        elif total_score <= 5:
            recommendations.append("Mild symptoms - conservative management")
            recommendations.append("Pelvic floor muscle training (Kegel exercises)")
            recommendations.append("Bladder training and fluid management")
        else:
            if "stress" in incontinence_type.lower():
                recommendations.append("Stress incontinence - pelvic floor exercises first-line")
                recommendations.append("Consider pessary or surgical options if conservative fails")
                recommendations.append("Weight loss if overweight")
            elif "urge" in incontinence_type.lower():
                recommendations.append("Urge incontinence - bladder training")
                recommendations.append("Anticholinergics or beta-3 agonists")
                recommendations.append("Avoid bladder irritants (caffeine, alcohol)")
            else:
                recommendations.append("Mixed incontinence - treat predominant symptom first")
                recommendations.append("Combination of pelvic floor training + pharmacotherapy")

            if total_score > 12:
                recommendations.append("Significant impact - consider referral to specialist")

        warnings = []
        if total_score >= 15:
            warnings.append("Severe incontinence - significant QoL impact")
        if qol >= 7:
            warnings.append("High QoL interference - psychosocial impact likely")

        next_steps = [
            "Bladder diary for 3 days",
            "Pelvic examination",
            "Post-void residual measurement",
            "Urinalysis to exclude UTI",
        ]

        return ScoreResult(
            value=total_score,
            unit=Unit.SCORE,
            interpretation=Interpretation(
                summary=f"ICIQ-SF = {total_score}/21: {severity_text} | {incontinence_type}",
                detail=(
                    f"ICIQ-SF score of {total_score}/21 indicates {severity_text.lower()}. "
                    f"Components: Frequency {frequency}/5, Amount {amount}/6, QoL impact {qol}/10. "
                    f"Pattern suggests {incontinence_type.lower()}."
                ),
                severity=severity,
                stage=stage,
                stage_description=f"{severity_text} - {incontinence_type}",
                recommendations=tuple(recommendations),
                warnings=tuple(warnings),
                next_steps=tuple(next_steps),
            ),
            references=list(self.metadata.references),
            tool_id=self.metadata.low_level.tool_id,
            tool_name=self.metadata.low_level.name,
            raw_inputs=params,
            calculation_details={
                "total_score": total_score,
                "frequency_score": frequency,
                "amount_score": amount,
                "qol_score": qol,
                "incontinence_type": incontinence_type,
                "severity_category": stage,
                "leak_situations": situations,
            },
        )
