"""
CFS (Clinical Frailty Scale)

The CFS is a judgment-based frailty tool that evaluates specific
domains including mobility, energy, physical activity, and function.

Reference (Original Development):
    Rockwood K, Song X, MacKnight C, et al. A global clinical measure
    of fitness and frailty in elderly people. CMAJ. 2005;173(5):489-495.
    PMID: 16129869

Reference (9-point Scale Update):
    Rockwood K, Theou O. Using the Clinical Frailty Scale in Allocating
    Scarce Health Care Resources. Can Geriatr J. 2020;23(3):210-215.
    PMID: 32904824
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


class ClinicalFrailtyScaleCalculator(BaseCalculator):
    """
    CFS (Clinical Frailty Scale) Calculator

    9-point scale assessing frailty in older adults.
    Score 1-9 based on functional status and dependence.
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="cfs",
                name="CFS (Clinical Frailty Scale)",
                purpose="Assess frailty in older adults",
                input_params=["frailty_level"],
                output_type="Score 1-9 with frailty classification",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.GERIATRICS,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.CRITICAL_CARE,
                ),
                conditions=(
                    "Frailty",
                    "Geriatric Syndrome",
                    "Functional Decline",
                    "Sarcopenia",
                ),
                clinical_contexts=(
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.TREATMENT_DECISION,
                ),
                clinical_questions=(
                    "How frail is this patient?",
                    "Calculate CFS score",
                    "Assess frailty level",
                    "Is this patient fit for surgery?",
                ),
                keywords=(
                    "CFS",
                    "clinical frailty scale",
                    "frailty",
                    "Rockwood",
                    "geriatric assessment",
                ),
            ),
            references=(
                Reference(
                    citation="Rockwood K, Song X, MacKnight C, et al. A global clinical measure of fitness and frailty in elderly people. CMAJ. 2005;173(5):489-495.",
                    pmid="16129869",
                    doi="10.1503/cmaj.050051",
                    year=2005,
                ),
                Reference(
                    citation="Rockwood K, Theou O. Using the Clinical Frailty Scale in Allocating Scarce Health Care Resources. Can Geriatr J. 2020;23(3):210-215.",
                    pmid="32904824",
                    doi="10.5770/cgj.23.463",
                    year=2020,
                ),
            ),
        )

    def calculate(self, **params) -> ScoreResult:
        """
        Calculate CFS score.

        Args:
            frailty_level: CFS level (1-9)
                1 = Very fit (robust, active, energetic, well-motivated)
                2 = Fit (no active disease, less fit than category 1)
                3 = Managing well (medical problems well controlled)
                4 = Living with very mild frailty (not dependent but slowed down)
                5 = Living with mild frailty (need help with higher ADLs)
                6 = Living with moderate frailty (need help with all outside activities, housekeeping)
                7 = Living with severe frailty (completely dependent for personal care)
                8 = Very severely frail (completely dependent, approaching end of life)
                9 = Terminally ill (life expectancy <6 months, may not be frail)

        Returns:
            ScoreResult with CFS score and frailty classification
        """
        level = int(params.get("frailty_level", 1))

        if not 1 <= level <= 9:
            raise ValueError("frailty_level must be 1-9")

        # CFS descriptions
        descriptions = {
            1: ("Very fit", "Robust, active, energetic and motivated. Exercise regularly and are among the fittest for their age."),
            2: ("Fit", "No active disease symptoms but less fit than category 1. Often exercise or are very active occasionally."),
            3: ("Managing well", "Medical problems are well controlled. Not regularly active beyond routine walking."),
            4: ("Living with very mild frailty", "Not dependent on others but often symptoms limit activities. 'Slowing up'."),
            5: ("Living with mild frailty", "More evident slowing, need help with high order IADLs (finances, transportation, heavy housework)."),
            6: ("Living with moderate frailty", "Need help with all outside activities and with housekeeping. Problems with stairs, bathing."),
            7: ("Living with severe frailty", "Completely dependent for personal care. However, seem stable and not at high risk of dying."),
            8: ("Very severely frail", "Completely dependent for personal care, approaching end of life. Could not recover from minor illness."),
            9: ("Terminally ill", "Approaching end of life. Life expectancy <6 months. Not otherwise evidently frail."),
        }

        category, description = descriptions[level]

        # Determine severity
        if level <= 3:
            severity = Severity.NORMAL
            frailty_status = "Not frail"
        elif level == 4:
            severity = Severity.MILD
            frailty_status = "Pre-frail / Very mild frailty"
        elif level == 5:
            severity = Severity.MILD
            frailty_status = "Mild frailty"
        elif level == 6:
            severity = Severity.MODERATE
            frailty_status = "Moderate frailty"
        elif level == 7:
            severity = Severity.SEVERE
            frailty_status = "Severe frailty"
        else:  # 8-9
            severity = Severity.CRITICAL
            frailty_status = "Very severe frailty / Terminal"

        # Recommendations
        recommendations = []
        if level <= 3:
            recommendations.append("Not frail - standard care appropriate")
            recommendations.append("Encourage continued physical activity")
        elif level <= 5:
            recommendations.append("Mild frailty - comprehensive geriatric assessment recommended")
            recommendations.append("Exercise program (resistance + balance training)")
            recommendations.append("Nutritional optimization")
            recommendations.append("Medication review for polypharmacy")
        elif level == 6:
            recommendations.append("Moderate frailty - multidisciplinary geriatric care")
            recommendations.append("Falls prevention program")
            recommendations.append("Consider goals of care discussion")
            recommendations.append("Evaluate home support needs")
        else:
            recommendations.append("Severe frailty - focus on quality of life")
            recommendations.append("Advance care planning essential")
            recommendations.append("Consider palliative care involvement")
            recommendations.append("Minimize unnecessary interventions")

        warnings = []
        if level >= 5:
            warnings.append("Increased mortality risk with major surgery or ICU admission")
        if level >= 7:
            warnings.append("High 1-year mortality risk - consider goals of care")
        if level == 9:
            warnings.append("Terminal illness - comfort-focused care recommended")

        next_steps = [
            "Comprehensive geriatric assessment" if level >= 4 else "Routine follow-up",
            "Functional assessment (ADL/IADL evaluation)",
            "Nutritional screening",
            "Falls risk assessment" if level >= 4 else "Preventive health maintenance",
        ]

        return ScoreResult(
            value=level,
            unit=Unit.SCORE,
            interpretation=Interpretation(
                summary=f"CFS {level}/9: {category} - {frailty_status}",
                detail=(f"Clinical Frailty Scale score of {level}/9 indicates {category.lower()}. {description}"),
                severity=severity,
                stage=category,
                stage_description=frailty_status,
                recommendations=recommendations,
                warnings=warnings,
                next_steps=next_steps,
            ),
            references=self.metadata.references,
            tool_id=self.metadata.low_level.tool_id,
            tool_name=self.metadata.low_level.name,
            raw_inputs=params,
            calculation_details={
                "cfs_score": level,
                "category": category,
                "frailty_status": frailty_status,
                "description": description,
            },
        )
