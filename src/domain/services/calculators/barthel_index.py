"""
Barthel Index (BI)

The Barthel Index is a widely used scale to assess functional independence
in Activities of Daily Living (ADL). It evaluates 10 basic activities.

Reference (Original):
    Mahoney FI, Barthel DW. Functional Evaluation: The Barthel Index.
    Md State Med J. 1965;14:61-65.
    PMID: 14258950

Reference (Modified/Validation):
    Collin C, Wade DT, Davies S, Horne V. The Barthel ADL Index:
    a reliability study. Int Disabil Stud. 1988;10(2):61-63.
    PMID: 3403500
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


class BarthelIndexCalculator(BaseCalculator):
    """
    Barthel Index Calculator

    Assesses functional independence in 10 ADL activities.
    Score range: 0-100 (higher = more independent)
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="barthel_index",
                name="Barthel Index (ADL Assessment)",
                purpose="Assess functional independence in activities of daily living",
                input_params=[
                    "feeding",
                    "bathing",
                    "grooming",
                    "dressing",
                    "bowel_control",
                    "bladder_control",
                    "toilet_use",
                    "transfers",
                    "mobility",
                    "stairs",
                ],
                output_type="Score 0-100 with ADL independence classification",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.GERIATRICS,
                    Specialty.PHYSICAL_MEDICINE,
                    Specialty.NEUROLOGY,
                ),
                conditions=(
                    "Functional Impairment",
                    "Stroke Recovery",
                    "Frailty",
                    "Disability",
                    "Dementia",
                ),
                clinical_contexts=(
                    ClinicalContext.SCREENING,
                    ClinicalContext.MONITORING,
                    ClinicalContext.DISPOSITION,
                ),
                clinical_questions=(
                    "What is this patient's functional status?",
                    "Calculate Barthel Index",
                    "Assess ADL independence",
                    "Evaluate functional capacity",
                ),
                keywords=(
                    "Barthel Index",
                    "ADL",
                    "activities of daily living",
                    "functional status",
                    "independence",
                    "disability",
                ),
            ),
            references=(
                Reference(
                    citation="Mahoney FI, Barthel DW. Functional Evaluation: The Barthel Index. Md State Med J. 1965;14:61-65.",
                    pmid="14258950",
                    year=1965,
                ),
                Reference(
                    citation="Collin C, Wade DT, Davies S, Horne V. The Barthel ADL Index: a reliability study. Int Disabil Stud. 1988;10(2):61-63.",
                    pmid="3403500",
                    doi="10.3109/09638288809164103",
                    year=1988,
                ),
            ),
        )

    def calculate(self, **params) -> ScoreResult:
        """
        Calculate Barthel Index.

        Args (each scored 0-5, 0-10, or 0-15 depending on item):
            feeding: 0=unable, 5=needs help, 10=independent
            bathing: 0=dependent, 5=independent
            grooming: 0=needs help, 5=independent
            dressing: 0=dependent, 5=needs help, 10=independent
            bowel_control: 0=incontinent, 5=occasional accident, 10=continent
            bladder_control: 0=incontinent, 5=occasional accident, 10=continent
            toilet_use: 0=dependent, 5=needs some help, 10=independent
            transfers: 0=unable, 5=major help, 10=minor help, 15=independent
            mobility: 0=immobile, 5=wheelchair, 10=walks with help, 15=independent
            stairs: 0=unable, 5=needs help, 10=independent

        Returns:
            ScoreResult with Barthel Index (0-100) and interpretation
        """
        # Item definitions with valid values
        items = {
            "feeding": {"valid": [0, 5, 10], "max": 10},
            "bathing": {"valid": [0, 5], "max": 5},
            "grooming": {"valid": [0, 5], "max": 5},
            "dressing": {"valid": [0, 5, 10], "max": 10},
            "bowel_control": {"valid": [0, 5, 10], "max": 10},
            "bladder_control": {"valid": [0, 5, 10], "max": 10},
            "toilet_use": {"valid": [0, 5, 10], "max": 10},
            "transfers": {"valid": [0, 5, 10, 15], "max": 15},
            "mobility": {"valid": [0, 5, 10, 15], "max": 15},
            "stairs": {"valid": [0, 5, 10], "max": 10},
        }

        # Calculate score
        scores = {}
        total = 0

        for item, config in items.items():
            value = params.get(item)
            if value is None:
                raise ValueError(f"Missing required parameter: {item}")

            value = int(value)
            if value not in config["valid"]:
                raise ValueError(f"{item} must be one of {config['valid']}, got {value}")

            scores[item] = value
            total += value

        # Interpretation based on total score
        if total == 100:
            severity = Severity.NORMAL
            level = "Independent"
            detail = "Fully independent in all ADL activities"
        elif total >= 80:
            severity = Severity.MILD
            level = "Minimal dependence"
            detail = "Independent in most activities, minimal assistance needed"
        elif total >= 60:
            severity = Severity.MILD
            level = "Mild dependence"
            detail = "Needs some assistance with ADL activities"
        elif total >= 40:
            severity = Severity.MODERATE
            level = "Moderate dependence"
            detail = "Requires moderate assistance with ADL activities"
        elif total >= 20:
            severity = Severity.SEVERE
            level = "Severe dependence"
            detail = "Requires substantial assistance with most activities"
        else:
            severity = Severity.CRITICAL
            level = "Total dependence"
            detail = "Requires complete assistance with all ADL activities"

        # Identify problem areas
        problem_areas = []
        for item, value in scores.items():
            max_val = items[item]["max"]
            if value < max_val:
                pct = (value / max_val) * 100
                if pct == 0:
                    problem_areas.append(f"{item.replace('_', ' ')}: dependent")
                elif pct <= 50:
                    problem_areas.append(f"{item.replace('_', ' ')}: needs help")

        # Recommendations
        recommendations = []
        if total == 100:
            recommendations.append("Maintain current functional status")
            recommendations.append("Regular exercise to preserve independence")
        elif total >= 60:
            recommendations.append("Physical/occupational therapy to improve function")
            recommendations.append("Address specific areas of dependence")
            recommendations.append("Home safety assessment")
        elif total >= 40:
            recommendations.append("Structured rehabilitation program")
            recommendations.append("Caregiver training and support")
            recommendations.append("Consider assistive devices")
            recommendations.append("Home modification assessment")
        else:
            recommendations.append("Comprehensive rehabilitation assessment")
            recommendations.append("Long-term care planning")
            recommendations.append("Caregiver support and respite services")
            recommendations.append("Consider skilled nursing facility if appropriate")

        warnings = []
        if total < 40:
            warnings.append("High care needs - assess caregiver burden")
        if scores.get("transfers", 15) < 10 or scores.get("mobility", 15) < 10:
            warnings.append("Mobility impairment - fall risk assessment needed")
        if scores.get("bowel_control", 10) < 10 or scores.get("bladder_control", 10) < 10:
            warnings.append("Incontinence present - skin integrity monitoring")

        next_steps = [
            "Serial assessment to track progress",
            "Set specific functional goals",
            "Coordinate care team interventions",
        ]
        if problem_areas:
            next_steps.insert(0, f"Address: {', '.join(problem_areas[:3])}")

        return ScoreResult(
            value=total,
            unit=Unit.SCORE,
            interpretation=Interpretation(
                summary=f"Barthel Index = {total}/100: {level}",
                detail=(
                    f"Barthel Index score of {total} out of 100 indicates {level.lower()}. "
                    f"{detail}. "
                    f"{'Problem areas: ' + ', '.join(problem_areas[:3]) + '.' if problem_areas else 'No significant functional limitations.'}"
                ),
                severity=severity,
                stage=level,
                stage_description=detail,
                recommendations=recommendations,
                warnings=warnings,
                next_steps=next_steps,
            ),
            references=self.metadata.references,
            tool_id=self.metadata.low_level.tool_id,
            tool_name=self.metadata.low_level.name,
            raw_inputs=params,
            calculation_details={
                "total_score": total,
                "max_score": 100,
                "item_scores": scores,
                "dependence_level": level,
                "problem_areas": problem_areas,
            },
        )
