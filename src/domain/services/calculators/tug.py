"""
TUG (Timed Up and Go Test)

The TUG is a simple, quick, and widely used clinical test to assess
mobility, balance, and fall risk in older adults.

Reference (Original Development):
    Podsiadlo D, Richardson S. The timed "Up & Go": a test of basic
    functional mobility for frail elderly persons.
    J Am Geriatr Soc. 1991;39(2):142-148.
    PMID: 1991946

Reference (Fall Risk Prediction):
    Shumway-Cook A, Brauer S, Woollacott M. Predicting the probability
    for falls in community-dwelling older adults using the Timed Up & Go Test.
    Phys Ther. 2000;80(9):896-903.
    PMID: 10960937
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


class TUGCalculator(BaseCalculator):
    """
    TUG (Timed Up and Go Test) Calculator

    Measures time to rise from chair, walk 3 meters, turn, walk back, sit down.
    Normal: <10 seconds; Fall risk increases >12-14 seconds.
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="tug",
                name="TUG (Timed Up and Go Test)",
                purpose="Assess mobility, balance, and fall risk",
                input_params=["time_seconds", "assistive_device"],
                output_type="Time in seconds with fall risk classification",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.GERIATRICS,
                    Specialty.PHYSICAL_MEDICINE,
                    Specialty.ORTHOPEDICS,
                ),
                conditions=(
                    "Fall Risk",
                    "Mobility Impairment",
                    "Balance Disorder",
                    "Frailty",
                    "Gait Disorder",
                ),
                clinical_contexts=(
                    ClinicalContext.SCREENING,
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "Is this patient at risk for falls?",
                    "Calculate TUG score",
                    "Assess mobility",
                    "Evaluate fall risk",
                ),
                keywords=(
                    "TUG",
                    "timed up and go",
                    "fall risk",
                    "mobility assessment",
                    "balance test",
                    "gait speed",
                ),
            ),
            references=(
                Reference(
                    citation="Podsiadlo D, Richardson S. The timed 'Up & Go': a test of basic functional mobility for frail elderly persons. J Am Geriatr Soc. 1991;39(2):142-148.",
                    pmid="1991946",
                    doi="10.1111/j.1532-5415.1991.tb01616.x",
                    year=1991,
                ),
                Reference(
                    citation="Shumway-Cook A, Brauer S, Woollacott M. Predicting the probability for falls using the Timed Up & Go Test. Phys Ther. 2000;80(9):896-903.",
                    pmid="10960937",
                    year=2000,
                ),
            ),
        )

    def calculate(self, **params) -> ScoreResult:
        """
        Calculate TUG result.

        Args:
            time_seconds: Time to complete test in seconds
            assistive_device: Assistive device used (optional)
                "none", "cane", "walker", "wheelchair" (cannot perform)

        Returns:
            ScoreResult with TUG time and fall risk assessment
        """
        time_sec = float(params.get("time_seconds", 0))
        device = str(params.get("assistive_device", "none")).lower()

        if time_sec <= 0:
            raise ValueError("time_seconds must be positive")

        valid_devices = ["none", "cane", "walker", "wheelchair", "unable"]
        if device not in valid_devices:
            raise ValueError(f"assistive_device must be one of {valid_devices}")

        # Unable to perform
        if device in ["wheelchair", "unable"]:
            return ScoreResult(
                value=999,
                unit=Unit.SECONDS,
                interpretation=Interpretation(
                    summary="TUG: Unable to perform - severe mobility impairment",
                    detail="Patient unable to complete TUG test, indicating severe mobility impairment and very high fall risk.",
                    severity=Severity.CRITICAL,
                    stage="Unable",
                    stage_description="Severe mobility impairment",
                    recommendations=[
                        "High fall risk - intensive fall prevention measures",
                        "Physical therapy evaluation",
                        "Home safety assessment",
                        "Consider assistive devices or mobility aids",
                    ],
                    warnings=["Unable to complete TUG - very high fall risk"],
                    next_steps=["Comprehensive mobility assessment", "PT/OT evaluation"],
                ),
                references=self.metadata.references,
                tool_id=self.metadata.low_level.tool_id,
                tool_name=self.metadata.low_level.name,
                raw_inputs=params,
                calculation_details={
                    "time_seconds": None,
                    "assistive_device": device,
                    "unable_to_complete": True,
                    "fall_risk": "Very high",
                },
            )

        # Risk classification
        if time_sec < 10:
            severity = Severity.NORMAL
            risk_text = "Normal mobility - low fall risk"
            stage = "Normal"
            fall_risk = "Low"
        elif time_sec < 14:
            severity = Severity.MILD
            risk_text = "Mildly impaired mobility"
            stage = "Mild impairment"
            fall_risk = "Moderate"
        elif time_sec < 20:
            severity = Severity.MODERATE
            risk_text = "Moderate mobility impairment - increased fall risk"
            stage = "Moderate impairment"
            fall_risk = "High"
        elif time_sec < 30:
            severity = Severity.SEVERE
            risk_text = "Severe mobility impairment - high fall risk"
            stage = "Severe impairment"
            fall_risk = "Very high"
        else:
            severity = Severity.CRITICAL
            risk_text = "Very severe mobility impairment"
            stage = "Very severe"
            fall_risk = "Very high"

        # Device considerations
        device_note = ""
        if device == "cane":
            device_note = " (with cane)"
        elif device == "walker":
            device_note = " (with walker)"
            if time_sec < 14:
                fall_risk = "Moderate"  # Walker use suggests underlying impairment

        # Recommendations
        recommendations = []
        if time_sec < 10:
            recommendations.append("Normal mobility - maintain activity level")
            recommendations.append("Continue regular exercise")
        elif time_sec < 14:
            recommendations.append("Mild impairment - fall prevention education")
            recommendations.append("Balance and strength exercises")
            recommendations.append("Review medications for fall risk")
        elif time_sec < 20:
            recommendations.append("Moderate impairment - comprehensive fall assessment")
            recommendations.append("Physical therapy referral")
            recommendations.append("Home safety evaluation")
            recommendations.append("Consider assistive device if not already using")
        else:
            recommendations.append("Severe impairment - intensive fall prevention")
            recommendations.append("Physical therapy essential")
            recommendations.append("Home modification assessment")
            recommendations.append("May need supervision for ambulation")
            recommendations.append("Consider occupational therapy evaluation")

        warnings = []
        if time_sec >= 14:
            warnings.append("Increased fall risk - implement fall precautions")
        if time_sec >= 20:
            warnings.append("High fall risk - avoid unsupervised ambulation")
        if device == "walker" and time_sec >= 20:
            warnings.append("Significant impairment even with walker")

        next_steps = [
            "Comprehensive geriatric assessment" if time_sec >= 14 else "Annual reassessment",
            "Medication review for fall-risk drugs",
            "Vision and hearing assessment",
            "Footwear evaluation",
        ]

        return ScoreResult(
            value=round(time_sec, 1),
            unit=Unit.SECONDS,
            interpretation=Interpretation(
                summary=f"TUG = {time_sec:.1f} seconds{device_note}: {risk_text}",
                detail=(
                    f"Timed Up and Go completed in {time_sec:.1f} seconds{device_note}. "
                    f"This indicates {risk_text.lower()}. "
                    f"Fall risk category: {fall_risk}. "
                    f"{'<10s = normal, 10-14s = mild impairment, >14s = increased fall risk.' if time_sec < 20 else '>20s indicates significant functional limitation.'}"
                ),
                severity=severity,
                stage=stage,
                stage_description=risk_text,
                recommendations=recommendations,
                warnings=warnings,
                next_steps=next_steps,
            ),
            references=self.metadata.references,
            tool_id=self.metadata.low_level.tool_id,
            tool_name=self.metadata.low_level.name,
            raw_inputs=params,
            calculation_details={
                "time_seconds": round(time_sec, 1),
                "assistive_device": device,
                "fall_risk_category": fall_risk,
                "mobility_category": stage,
            },
        )
