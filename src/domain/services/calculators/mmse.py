"""
MMSE (Mini-Mental State Examination)

The MMSE is the most widely used screening tool for cognitive impairment.
It assesses orientation, registration, attention, recall, and language.

Reference (Original Development):
    Folstein MF, Folstein SE, McHugh PR. "Mini-mental state". A practical
    method for grading the cognitive state of patients for the clinician.
    J Psychiatr Res. 1975;12(3):189-198.
    PMID: 1202204

Reference (Interpretation):
    Tombaugh TN, McIntyre NJ. The mini-mental state examination: a
    comprehensive review. J Am Geriatr Soc. 1992;40(9):922-935.
    PMID: 1512391
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


class MMSECalculator(BaseCalculator):
    """
    MMSE (Mini-Mental State Examination) Calculator

    30-point cognitive screening test.
    Assesses orientation, memory, attention, language, and visuospatial skills.
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="mmse",
                name="MMSE (Mini-Mental State Examination)",
                purpose="Screen for cognitive impairment",
                input_params=[
                    "orientation_time",
                    "orientation_place",
                    "registration",
                    "attention_calculation",
                    "recall",
                    "naming",
                    "repetition",
                    "three_stage_command",
                    "reading",
                    "writing",
                    "copying",
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
                    "Dementia",
                    "Cognitive Impairment",
                    "Alzheimer's Disease",
                    "Delirium",
                    "MCI",
                ),
                clinical_contexts=(
                    ClinicalContext.SCREENING,
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "Does this patient have cognitive impairment?",
                    "Calculate MMSE score",
                    "Screen for dementia",
                    "Assess cognitive function",
                ),
                keywords=(
                    "MMSE",
                    "mini-mental",
                    "cognitive screening",
                    "dementia screening",
                    "Folstein",
                ),
            ),
            references=(
                Reference(
                    citation="Folstein MF, Folstein SE, McHugh PR. Mini-mental state: A practical method for grading the cognitive state of patients. J Psychiatr Res. 1975;12(3):189-198.",
                    pmid="1202204",
                    doi="10.1016/0022-3956(75)90026-6",
                    year=1975,
                ),
                Reference(
                    citation="Tombaugh TN, McIntyre NJ. The mini-mental state examination: a comprehensive review. J Am Geriatr Soc. 1992;40(9):922-935.",
                    pmid="1512391",
                    doi="10.1111/j.1532-5415.1992.tb01992.x",
                    year=1992,
                ),
            ),
        )

    def calculate(self, **params) -> ScoreResult:
        """
        Calculate MMSE score.

        Args:
            orientation_time: Time orientation (0-5)
                Year, season, month, date, day of week
            orientation_place: Place orientation (0-5)
                Country, state/province, city, building, floor
            registration: Immediate recall of 3 words (0-3)
            attention_calculation: Serial 7s or WORLD backwards (0-5)
            recall: Delayed recall of 3 words (0-3)
            naming: Name 2 objects (pencil, watch) (0-2)
            repetition: Repeat "No ifs, ands, or buts" (0-1)
            three_stage_command: Follow 3-stage command (0-3)
                Take paper, fold in half, put on floor
            reading: Read and obey "Close your eyes" (0-1)
            writing: Write a sentence (0-1)
            copying: Copy intersecting pentagons (0-1)

        Returns:
            ScoreResult with MMSE score and cognitive classification
        """
        # Define score ranges for each domain
        domains = {
            "orientation_time": (0, 5),
            "orientation_place": (0, 5),
            "registration": (0, 3),
            "attention_calculation": (0, 5),
            "recall": (0, 3),
            "naming": (0, 2),
            "repetition": (0, 1),
            "three_stage_command": (0, 3),
            "reading": (0, 1),
            "writing": (0, 1),
            "copying": (0, 1),
        }

        scores = {}
        for domain, (min_val, max_val) in domains.items():
            value = int(params.get(domain, 0))
            if not min_val <= value <= max_val:
                raise ValueError(f"{domain} must be {min_val}-{max_val}")
            scores[domain] = value

        total_score = sum(scores.values())

        # Domain subscores
        orientation = scores["orientation_time"] + scores["orientation_place"]
        memory = scores["registration"] + scores["recall"]
        attention = scores["attention_calculation"]
        language = scores["naming"] + scores["repetition"] + scores["three_stage_command"] + scores["reading"] + scores["writing"]
        visuospatial = scores["copying"]

        # Severity classification (age/education adjusted cutoffs vary, using common cutoffs)
        if total_score >= 27:
            severity = Severity.NORMAL
            severity_text = "Normal cognition"
            stage = "Normal"
        elif total_score >= 24:
            severity = Severity.MILD
            severity_text = "Mild cognitive impairment"
            stage = "Mild impairment"
        elif total_score >= 19:
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
        if orientation < 8:
            impaired_domains.append("orientation")
        if memory < 4:
            impaired_domains.append("memory")
        if attention < 3:
            impaired_domains.append("attention")
        if language < 6:
            impaired_domains.append("language")
        if visuospatial == 0:
            impaired_domains.append("visuospatial")

        # Recommendations
        recommendations = []
        if total_score >= 27:
            recommendations.append("Normal screening - no immediate cognitive workup needed")
            recommendations.append("Consider repeat screening in 1-2 years")
        elif total_score >= 24:
            recommendations.append("Possible MCI - further cognitive testing recommended")
            recommendations.append("Consider MoCA for more sensitive assessment")
            recommendations.append("Evaluate for reversible causes")
        else:
            recommendations.append("Cognitive impairment detected - comprehensive evaluation needed")
            recommendations.append("Consider neuropsychological testing")
            recommendations.append("Brain imaging (MRI preferred)")
            recommendations.append("Laboratory workup (B12, TSH, metabolic panel)")
            if total_score < 19:
                recommendations.append("Assess functional status and safety")
                recommendations.append("Consider cholinesterase inhibitor therapy")

        warnings = []
        if total_score < 24:
            warnings.append("Score may be affected by education level, language, sensory deficits")
        if scores["recall"] == 0:
            warnings.append("Memory severely impaired - consider Alzheimer's workup")
        if total_score < 10:
            warnings.append("Severe impairment - assess for safety and supervision needs")

        next_steps = [
            "Detailed cognitive testing (MoCA, neuropsychological battery)",
            "Medication review for cognitive side effects",
            "Depression screening (depression can mimic dementia)",
            "Functional assessment (ADL/IADL)",
        ]

        return ScoreResult(
            value=total_score,
            unit=Unit.SCORE,
            interpretation=Interpretation(
                summary=f"MMSE = {total_score}/30: {severity_text}",
                detail=(
                    f"MMSE score of {total_score}/30 indicates {severity_text.lower()}. "
                    f"Domain scores: Orientation {orientation}/10, Memory {memory}/6, "
                    f"Attention {attention}/5, Language {language}/8, Visuospatial {visuospatial}/1. "
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
                "orientation_score": orientation,
                "memory_score": memory,
                "attention_score": attention,
                "language_score": language,
                "visuospatial_score": visuospatial,
                "impaired_domains": impaired_domains,
                "severity_category": stage,
                **{f"domain_{k}": v for k, v in scores.items()},
            },
        )
