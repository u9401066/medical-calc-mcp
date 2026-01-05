"""
APGAR Score Calculator - 新生兒評估量表

Standardized assessment of newborn health at 1 and 5 minutes after birth.
Predicts need for resuscitation and short-term outcomes.

Clinical Application:
- 1-minute APGAR: Need for immediate resuscitation
- 5-minute APGAR: Response to resuscitation, prognosis
- 10-minute APGAR: For ongoing resuscitation (if 5-min <7)

Scoring (0-2 points each, total 0-10):
- Appearance (skin color)
- Pulse (heart rate)
- Grimace (reflex irritability)
- Activity (muscle tone)
- Respiration (breathing effort)

Interpretation:
- 7-10: Normal (vigorous)
- 4-6: Moderately depressed (may need intervention)
- 0-3: Severely depressed (requires immediate resuscitation)

References:
    Apgar V. A proposal for a new method of evaluation of the newborn infant.
    Curr Res Anesth Analg. 1953;32(4):260-267.

    American Academy of Pediatrics Committee on Fetus and Newborn.
    The Apgar Score. Pediatrics. 2015;136(4):819-822. PMID: 26416932

    ACOG Committee Opinion No. 644: The Apgar Score. Obstet Gynecol.
    2015;126(4):e52-e55. PMID: 26393460
"""

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class APGARScoreCalculator(BaseCalculator):
    """
    APGAR Score Calculator

    Evaluates newborn status using 5 criteria:
    - Appearance (skin color)
    - Pulse (heart rate)
    - Grimace (reflex irritability)
    - Activity (muscle tone)
    - Respiration (breathing effort)

    Each criterion scored 0-2, total 0-10.
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="apgar_score",
                name="APGAR Score",
                purpose="Newborn assessment at 1 and 5 minutes after birth",
                input_params=[
                    "appearance", "pulse", "grimace", "activity", "respiration",
                    "assessment_time"
                ],
                output_type="APGAR score (0-10) with interpretation"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.PEDIATRICS,
                    Specialty.NEONATOLOGY,
                    Specialty.OBSTETRICS,
                    Specialty.ANESTHESIOLOGY,
                ),
                conditions=(
                    "Newborn assessment",
                    "Neonatal resuscitation",
                    "Birth asphyxia",
                    "Delivery room evaluation",
                ),
                clinical_contexts=(
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.RESUSCITATION,
                ),
            ),
            references=(
                Reference(
                    citation="Apgar V. A proposal for a new method of evaluation of the newborn infant. Curr Res Anesth Analg. 1953;32(4):260-267.",
                    pmid="13083014",
                    year=1953
                ),
                Reference(
                    citation="AAP Committee on Fetus and Newborn. The Apgar Score. Pediatrics. 2015;136(4):819-822.",
                    doi="10.1542/peds.2015-2651",
                    pmid="26416932",
                    year=2015
                ),
            ),
        )

    def calculate(
        self,
        appearance: int,
        pulse: int,
        grimace: int,
        activity: int,
        respiration: int,
        assessment_time: str = "1_minute"
    ) -> ScoreResult:
        """
        Calculate APGAR score.

        Args:
            appearance: Skin color
                0 = Blue/pale all over
                1 = Pink body, blue extremities (acrocyanosis)
                2 = Completely pink
            pulse: Heart rate
                0 = Absent
                1 = <100 bpm
                2 = ≥100 bpm
            grimace: Reflex irritability (response to stimulation)
                0 = No response
                1 = Grimace/weak cry
                2 = Sneeze/cough/vigorous cry
            activity: Muscle tone
                0 = Limp/flaccid
                1 = Some flexion
                2 = Active motion
            respiration: Breathing effort
                0 = Absent
                1 = Slow/irregular/weak cry
                2 = Good/strong cry
            assessment_time: "1_minute", "5_minute", or "10_minute"

        Returns:
            ScoreResult with APGAR score and interpretation
        """
        # Validate inputs
        for name, value in [
            ("appearance", appearance),
            ("pulse", pulse),
            ("grimace", grimace),
            ("activity", activity),
            ("respiration", respiration)
        ]:
            if not isinstance(value, int) or value < 0 or value > 2:
                raise ValueError(f"{name} must be 0, 1, or 2")

        valid_times = ["1_minute", "5_minute", "10_minute"]
        if assessment_time not in valid_times:
            raise ValueError(f"assessment_time must be one of: {valid_times}")

        # Calculate total score
        total_score = appearance + pulse + grimace + activity + respiration

        # Component breakdown
        components = {
            "A (Appearance)": appearance,
            "P (Pulse)": pulse,
            "G (Grimace)": grimace,
            "A (Activity)": activity,
            "R (Respiration)": respiration,
        }

        # Determine interpretation based on score and time
        time_label = assessment_time.replace("_", "-")

        if total_score >= 7:
            severity = Severity.NORMAL
            status = "Normal/Vigorous"
            action = "Routine care, skin-to-skin contact, delayed cord clamping"
            prognosis = "Excellent prognosis"
        elif total_score >= 4:
            severity = Severity.MODERATE
            status = "Moderately Depressed"
            action = "Stimulation, clear airway, may need PPV"
            prognosis = "Usually recovers with intervention"
        else:  # 0-3
            severity = Severity.CRITICAL
            status = "Severely Depressed"
            action = "Immediate resuscitation: PPV, chest compressions if HR<60, consider epinephrine"
            prognosis = "Risk of adverse outcomes; extended monitoring required"

        # Time-specific interpretation
        if assessment_time == "1_minute":
            time_context = "Indicates need for immediate resuscitation"
        elif assessment_time == "5_minute":
            time_context = "Reflects response to resuscitation; prognostic value"
            if total_score < 7:
                action += "; Continue 10-minute assessment"
        else:  # 10_minute
            time_context = "Extended assessment during ongoing resuscitation"
            if total_score < 7:
                action += "; Consider risk of HIE, neonatal encephalopathy"

        interpretation = Interpretation(
            severity=severity,
            summary=f"{time_label} APGAR {total_score}: {status}",
            detail=(
                f"Component scores: A={appearance} P={pulse} G={grimace} "
                f"A={activity} R={respiration}\n"
                f"Status: {status}\n"
                f"{time_context}\n"
                f"Prognosis: {prognosis}"
            ),
            recommendations=(action,)
        )

        details = {
            "assessment_time": time_label,
            "component_scores": components,
            "status": status,
            "prognosis": prognosis,
            "action": action,
            "next_step": self._get_next_step(total_score, assessment_time)
        }

        return ScoreResult(
            value=total_score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "appearance": appearance,
                "pulse": pulse,
                "grimace": grimace,
                "activity": activity,
                "respiration": respiration,
                "assessment_time": assessment_time,
            },
            calculation_details=details
        )

    def _get_next_step(self, score: int, assessment_time: str) -> str:
        """Get clinical next step recommendation."""
        if score >= 7:
            return "Continue routine newborn care and monitoring"
        elif assessment_time == "1_minute":
            return "Begin NRP algorithm; reassess at 5 minutes"
        elif assessment_time == "5_minute":
            if score < 7:
                return "Continue resuscitation; assess at 10 minutes; consider NICU admission"
        else:  # 10_minute
            if score < 7:
                return "Consider therapeutic hypothermia evaluation if HIE suspected"
        return "Continue appropriate level of care based on clinical status"
