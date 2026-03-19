"""
Epworth Sleepiness Scale (ESS)

The Epworth Sleepiness Scale is an 8-item self-administered questionnaire
that measures a person's average daytime sleep propensity in common
situations. Each item is scored from 0 to 3, with a total score from 0 to 24.

Reference (Original Development):
    Johns MW. A new method for measuring daytime sleepiness: the Epworth
    sleepiness scale. Sleep. 1991;14(6):540-545.
    PMID: 1798888

Reference (Psychometric Review):
    Goncalves MT, Malafaia S, Moutinho Dos Santos J, Roth T, Marques DR.
    Epworth sleepiness scale: A meta-analytic study on the internal consistency.
    Sleep Med. 2023;109:261-269.
    PMID: 37487279
"""

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class EpworthSleepinessScaleCalculator(BaseCalculator):
    """Epworth Sleepiness Scale calculator."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="epworth_sleepiness_scale",
                name="Epworth Sleepiness Scale (ESS)",
                purpose="Screen for excessive daytime sleepiness and quantify symptom burden",
                input_params=[
                    "sitting_reading",
                    "watching_tv",
                    "sitting_inactive_public_place",
                    "passenger_in_car_for_hour",
                    "lying_down_afternoon",
                    "sitting_talking_to_someone",
                    "sitting_quietly_after_lunch",
                    "in_car_stopped_in_traffic",
                ],
                output_type="Score 0-24 with daytime sleepiness severity",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.SLEEP_MEDICINE,
                    Specialty.PULMONOLOGY,
                    Specialty.NEUROLOGY,
                    Specialty.FAMILY_MEDICINE,
                ),
                conditions=(
                    "Excessive Daytime Sleepiness",
                    "Obstructive Sleep Apnea",
                    "Narcolepsy",
                    "Hypersomnia",
                    "Sleep Disorder",
                ),
                clinical_contexts=(
                    ClinicalContext.SCREENING,
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.MONITORING,
                    ClinicalContext.FOLLOW_UP,
                ),
                clinical_questions=(
                    "Does this patient have excessive daytime sleepiness?",
                    "How severe is this patient's daytime sleepiness?",
                    "Should I quantify sleepiness symptoms before sleep evaluation?",
                    "How is daytime sleepiness changing over time?",
                ),
                keywords=(
                    "Epworth",
                    "ESS",
                    "daytime sleepiness",
                    "sleepiness scale",
                    "sleep apnea screening",
                    "somnolence",
                ),
            ),
            references=(
                Reference(
                    citation="Johns MW. A new method for measuring daytime sleepiness: the Epworth sleepiness scale. Sleep. 1991;14(6):540-545.",
                    pmid="1798888",
                    doi="10.1093/sleep/14.6.540",
                    year=1991,
                ),
                Reference(
                    citation="Goncalves MT, Malafaia S, Moutinho Dos Santos J, Roth T, Marques DR. Epworth sleepiness scale: A meta-analytic study on the internal consistency. Sleep Med. 2023;109:261-269.",
                    pmid="37487279",
                    doi="10.1016/j.sleep.2023.07.008",
                    year=2023,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        sitting_reading: int,
        watching_tv: int,
        sitting_inactive_public_place: int,
        passenger_in_car_for_hour: int,
        lying_down_afternoon: int,
        sitting_talking_to_someone: int,
        sitting_quietly_after_lunch: int,
        in_car_stopped_in_traffic: int,
    ) -> ScoreResult:
        """Calculate Epworth Sleepiness Scale score."""
        items = {
            "sitting_reading": sitting_reading,
            "watching_tv": watching_tv,
            "sitting_inactive_public_place": sitting_inactive_public_place,
            "passenger_in_car_for_hour": passenger_in_car_for_hour,
            "lying_down_afternoon": lying_down_afternoon,
            "sitting_talking_to_someone": sitting_talking_to_someone,
            "sitting_quietly_after_lunch": sitting_quietly_after_lunch,
            "in_car_stopped_in_traffic": in_car_stopped_in_traffic,
        }

        for name, value in items.items():
            if not isinstance(value, int) or value < 0 or value > 3:
                raise ValueError(f"{name} must be an integer between 0 and 3")

        total_score = sum(items.values())
        interpretation = self._get_interpretation(total_score)

        return ScoreResult(
            value=total_score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs=items,
            calculation_details={
                "total_score": total_score,
                "max_score": 24,
                "item_scores": items,
                "sleepiness_threshold": 11,
            },
            formula_used="ESS total = sum of 8 item scores (each 0-3)",
        )

    def _get_interpretation(self, score: int) -> Interpretation:
        if score <= 5:
            return Interpretation(
                summary=f"ESS {score}/24: Lower Normal Daytime Sleepiness",
                detail="Score 0-5 is generally consistent with lower normal daytime sleep propensity.",
                severity=Severity.NORMAL,
                stage="Lower Normal",
                stage_description="ESS 0-5",
                recommendations=(
                    "No significant daytime sleepiness signal on ESS",
                    "Interpret together with sleep history and clinical context",
                ),
                next_steps=(
                    "Reassess if symptoms change",
                ),
            )
        if score <= 10:
            return Interpretation(
                summary=f"ESS {score}/24: Higher Normal Daytime Sleepiness",
                detail="Score 6-10 is often considered within the upper end of normal, but symptoms may still warrant review.",
                severity=Severity.MILD,
                stage="Higher Normal",
                stage_description="ESS 6-10",
                recommendations=(
                    "Review sleep duration, sleep quality, and sedating medications",
                    "Consider repeat assessment if symptoms persist",
                ),
                next_steps=(
                    "Correlate with snoring, witnessed apneas, or hypersomnia symptoms",
                ),
            )
        if score <= 12:
            return Interpretation(
                summary=f"ESS {score}/24: Mild Excessive Daytime Sleepiness",
                detail="Score 11-12 suggests clinically relevant daytime sleepiness.",
                severity=Severity.MODERATE,
                stage="Mild Excessive Sleepiness",
                stage_description="ESS 11-12",
                recommendations=(
                    "Evaluate for obstructive sleep apnea, insufficient sleep, and medication effects",
                    "Consider formal sleep assessment if symptoms are persistent",
                ),
                warnings=(
                    "ESS >10 is commonly used as an abnormal threshold",
                ),
                next_steps=(
                    "Obtain focused sleep history",
                    "Consider sleep medicine referral based on overall risk",
                ),
            )
        if score <= 15:
            return Interpretation(
                summary=f"ESS {score}/24: Moderate Excessive Daytime Sleepiness",
                detail="Score 13-15 is consistent with moderate excessive daytime sleepiness and warrants further evaluation.",
                severity=Severity.SEVERE,
                stage="Moderate Excessive Sleepiness",
                stage_description="ESS 13-15",
                recommendations=(
                    "Arrange diagnostic evaluation for sleep disorder causes",
                    "Counsel regarding driving and safety-sensitive activities",
                ),
                warnings=(
                    "Moderate daytime sleepiness may impair concentration and driving safety",
                ),
                next_steps=(
                    "Consider polysomnography or specialty referral",
                ),
            )
        return Interpretation(
            summary=f"ESS {score}/24: Severe Excessive Daytime Sleepiness",
            detail="Score 16-24 indicates severe daytime sleepiness and a high symptom burden.",
            severity=Severity.CRITICAL,
            stage="Severe Excessive Sleepiness",
            stage_description="ESS 16-24",
            recommendations=(
                "Urgent comprehensive sleep evaluation is recommended",
                "Assess for high-risk causes such as severe sleep apnea or central hypersomnolence disorders",
                "Address safety risks immediately",
            ),
            warnings=(
                "Severe daytime sleepiness may create substantial accident risk",
            ),
            next_steps=(
                "Expedite sleep medicine assessment",
                "Review driving and occupational safety restrictions",
            ),
        )
