"""
MoCA (Montreal Cognitive Assessment)

The MoCA is a sensitive screening tool for mild cognitive impairment,
more sensitive than MMSE for detecting early cognitive decline.

Reference (Original Development):
    Nasreddine ZS, Phillips NA, Bédirian V, et al. The Montreal Cognitive
    Assessment, MoCA: a brief screening tool for mild cognitive impairment.
    J Am Geriatr Soc. 2005;53(4):695-699.
    PMID: 15817019

Reference (Validation):
    Luis CA, Keegan AP, Mullan M. Cross validation of the Montreal
    Cognitive Assessment in community dwelling older adults residing
    in the Southeastern US. Int J Geriatr Psychiatry. 2009;24(2):197-201.
    PMID: 18850670
"""

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


class MoCACalculator(BaseCalculator):
    """
    MoCA (Montreal Cognitive Assessment) Calculator

    30-point cognitive screening test, more sensitive than MMSE
    for mild cognitive impairment (MCI).
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="moca",
                name="MoCA (Montreal Cognitive Assessment)",
                purpose="Screen for mild cognitive impairment",
                input_params=[
                    "visuospatial_executive",
                    "naming",
                    "attention_digits",
                    "attention_letter",
                    "attention_serial7",
                    "language_repetition",
                    "language_fluency",
                    "abstraction",
                    "delayed_recall",
                    "orientation",
                    "education_years",
                ],
                output_type="Score 0-30 with cognitive impairment classification",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.GERIATRICS,
                    Specialty.NEUROLOGY,
                    Specialty.PSYCHIATRY,
                ),
                conditions=(
                    "Mild Cognitive Impairment",
                    "MCI",
                    "Dementia",
                    "Alzheimer's Disease",
                    "Vascular Dementia",
                ),
                clinical_contexts=(
                    ClinicalContext.SCREENING,
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "Does this patient have MCI?",
                    "Calculate MoCA score",
                    "Screen for cognitive impairment",
                    "Is cognition normal?",
                ),
                keywords=(
                    "MoCA",
                    "Montreal cognitive",
                    "MCI screening",
                    "cognitive assessment",
                    "Nasreddine",
                ),
            ),
            references=(
                Reference(
                    citation="Nasreddine ZS, Phillips NA, Bédirian V, et al. The Montreal Cognitive Assessment, MoCA: a brief screening tool for mild cognitive impairment. J Am Geriatr Soc. 2005;53(4):695-699.",
                    pmid="15817019",
                    doi="10.1111/j.1532-5415.2005.53221.x",
                    year=2005,
                ),
                Reference(
                    citation="Luis CA, Keegan AP, Mullan M. Cross validation of the Montreal Cognitive Assessment in community dwelling older adults. Int J Geriatr Psychiatry. 2009;24(2):197-201.",
                    pmid="18850670",
                    doi="10.1002/gps.2101",
                    year=2009,
                ),
            ),
        )

    def calculate(self, **params) -> ScoreResult:
        """
        Calculate MoCA score.

        Args:
            visuospatial_executive: Visuospatial/Executive (0-5)
                Trail making (1), cube copy (1), clock drawing (3)
            naming: Naming animals (0-3)
                Lion, rhinoceros, camel
            attention_digits: Digit span forward/backward (0-2)
            attention_letter: Vigilance - tap at letter A (0-1)
            attention_serial7: Serial 7 subtraction (0-3)
            language_repetition: Sentence repetition (0-2)
            language_fluency: Verbal fluency - F words (0-1)
            abstraction: Abstraction - similarities (0-2)
            delayed_recall: Delayed recall of 5 words (0-5)
            orientation: Orientation - date, month, year, day, place, city (0-6)
            education_years: Years of education (for +1 adjustment if ≤12 years)

        Returns:
            ScoreResult with MoCA score and cognitive classification
        """
        # Define domain ranges
        domains = {
            "visuospatial_executive": (0, 5),
            "naming": (0, 3),
            "attention_digits": (0, 2),
            "attention_letter": (0, 1),
            "attention_serial7": (0, 3),
            "language_repetition": (0, 2),
            "language_fluency": (0, 1),
            "abstraction": (0, 2),
            "delayed_recall": (0, 5),
            "orientation": (0, 6),
        }

        scores = {}
        for domain, (min_val, max_val) in domains.items():
            value = int(params.get(domain, 0))
            if not min_val <= value <= max_val:
                raise ValueError(f"{domain} must be {min_val}-{max_val}")
            scores[domain] = value

        # Calculate raw total
        raw_total = sum(scores.values())

        # Education adjustment (+1 if ≤12 years education, max 30)
        education_years = params.get("education_years")
        education_adjustment = 0
        if education_years is not None:
            education_years = int(education_years)
            if education_years <= 12:
                education_adjustment = 1

        total_score = min(raw_total + education_adjustment, 30)

        # Domain subscores
        visuospatial = scores["visuospatial_executive"]
        attention = scores["attention_digits"] + scores["attention_letter"] + scores["attention_serial7"]
        language = scores["language_repetition"] + scores["language_fluency"]
        memory = scores["delayed_recall"]
        orientation = scores["orientation"]

        # Severity classification
        if total_score >= 26:
            severity = Severity.NORMAL
            severity_text = "Normal cognition"
            stage = "Normal"
        elif total_score >= 22:
            severity = Severity.MILD
            severity_text = "Mild cognitive impairment (MCI)"
            stage = "MCI"
        elif total_score >= 17:
            severity = Severity.MODERATE
            severity_text = "Mild dementia"
            stage = "Mild dementia"
        elif total_score >= 10:
            severity = Severity.SEVERE
            severity_text = "Moderate dementia"
            stage = "Moderate dementia"
        else:
            severity = Severity.CRITICAL
            severity_text = "Severe dementia"
            stage = "Severe dementia"

        # Identify impaired domains
        impaired_domains = []
        if visuospatial < 4:
            impaired_domains.append("visuospatial/executive")
        if scores["naming"] < 3:
            impaired_domains.append("naming")
        if attention < 5:
            impaired_domains.append("attention")
        if language < 2:
            impaired_domains.append("language")
        if memory < 3:
            impaired_domains.append("memory")
        if orientation < 6:
            impaired_domains.append("orientation")

        # Recommendations
        recommendations = []
        if total_score >= 26:
            recommendations.append("Normal cognition - no immediate workup needed")
            recommendations.append("Consider periodic rescreening")
        elif total_score >= 22:
            recommendations.append("MCI detected - comprehensive evaluation recommended")
            recommendations.append("Neuropsychological testing for detailed assessment")
            recommendations.append("Evaluate for reversible causes")
            recommendations.append("Lifestyle modifications (exercise, cognitive engagement)")
        else:
            recommendations.append("Dementia likely - full dementia workup indicated")
            recommendations.append("Brain imaging (MRI preferred)")
            recommendations.append("Laboratory evaluation (B12, TSH, metabolic panel)")
            recommendations.append("Consider cholinesterase inhibitor therapy")
            recommendations.append("Assess functional status and safety")

        warnings = []
        if total_score < 26:
            warnings.append("Score can be affected by education, language, depression, sensory deficits")
        if memory == 0:
            warnings.append("Zero delayed recall - significant memory impairment")
        if total_score < 17:
            warnings.append("Moderate-severe impairment - assess for safety and supervision needs")

        next_steps = [
            "Comprehensive neuropsychological evaluation" if total_score < 26 else "Routine follow-up",
            "Functional assessment (ADL/IADL)",
            "Depression screening",
            "Caregiver assessment if impaired",
        ]

        return ScoreResult(
            value=total_score,
            unit=Unit.SCORE,
            interpretation=Interpretation(
                summary=f"MoCA = {total_score}/30: {severity_text}" + (" (+1 education adjustment)" if education_adjustment else ""),
                detail=(
                    f"MoCA score of {total_score}/30 (raw: {raw_total}) indicates {severity_text.lower()}. "
                    f"Domain scores: Visuospatial/Executive {visuospatial}/5, Naming {scores['naming']}/3, "
                    f"Attention {attention}/6, Language {language}/3, Abstraction {scores['abstraction']}/2, "
                    f"Memory {memory}/5, Orientation {orientation}/6. "
                    f"Impaired domains: {', '.join(impaired_domains) if impaired_domains else 'None'}."
                ),
                severity=severity,
                stage=stage,
                stage_description=severity_text,
                recommendations=recommendations,
                warnings=warnings,
                next_steps=next_steps,
            ),
            references=self.metadata.references,
            tool_id=self.metadata.low_level.tool_id,
            tool_name=self.metadata.low_level.name,
            raw_inputs=params,
            calculation_details={
                "total_score": total_score,
                "raw_score": raw_total,
                "education_adjustment": education_adjustment,
                "visuospatial_executive": visuospatial,
                "naming": scores["naming"],
                "attention": attention,
                "language": language,
                "abstraction": scores["abstraction"],
                "memory": memory,
                "orientation": orientation,
                "impaired_domains": impaired_domains,
                "severity_category": stage,
            },
        )
