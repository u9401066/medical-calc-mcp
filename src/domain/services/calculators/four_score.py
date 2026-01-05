"""
FOUR Score (Full Outline of UnResponsiveness Score)

The FOUR Score is a clinical scale to assess coma and impaired consciousness.
It was developed as a more detailed alternative to the Glasgow Coma Scale,
particularly for intubated patients where verbal response cannot be assessed.

Reference (Original):
    Wijdicks EF, Bamlet WR, Maramattom BV, Manno EM, McClelland RL.
    Validation of a new coma scale: The FOUR score.
    Ann Neurol. 2005;58(4):585-593.
    DOI: 10.1002/ana.20611
    PMID: 16178024

Clinical Notes:
- Total score range: 0-16 (vs GCS 3-15)
- Designed for ICU patients, especially intubated patients
- Assesses brainstem reflexes not included in GCS
- FOUR Score of 0 = possible brain death (requires formal testing)
- Components: Eye, Motor, Brainstem, Respiration
"""


from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class FourScoreCalculator(BaseCalculator):
    """
    FOUR Score (Full Outline of UnResponsiveness) Calculator

    A 16-point coma scale assessing four components:

    Eye Response (E): 0-4
    - E4: Eyelids open or opened, tracking or blinking to command
    - E3: Eyelids open but not tracking
    - E2: Eyelids closed, open to loud voice
    - E1: Eyelids closed, open to pain
    - E0: Eyelids remain closed with pain

    Motor Response (M): 0-4
    - M4: Thumbs up, fist, or peace sign to command
    - M3: Localizing to pain
    - M2: Flexion response to pain
    - M1: Extension response to pain
    - M0: No response to pain or generalized myoclonus status

    Brainstem Reflexes (B): 0-4
    - B4: Pupil and corneal reflexes present
    - B3: One pupil wide and fixed
    - B2: Pupil OR corneal reflexes absent
    - B1: Pupil AND corneal reflexes absent
    - B0: Absent pupil, corneal, and cough reflexes

    Respiration (R): 0-4
    - R4: Not intubated, regular breathing pattern
    - R3: Not intubated, Cheyne-Stokes breathing pattern
    - R2: Not intubated, irregular breathing
    - R1: Breathes above ventilator rate
    - R0: Breathes at ventilator rate or apnea

    Advantages over GCS:
    - Provides detailed brainstem assessment
    - Includes respiratory pattern (herniation indicator)
    - Score of 0 has clear meaning (potential brain death)
    - Better interrater reliability
    - Applicable to intubated patients
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="four_score",
                name="FOUR Score (Full Outline of UnResponsiveness)",
                purpose="Assess coma severity with detailed brainstem and respiratory evaluation",
                input_params=["eye_response", "motor_response", "brainstem_reflexes", "respiration"],
                output_type="FOUR Score (0-16) with coma severity classification"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.NEUROLOGY,
                    Specialty.CRITICAL_CARE,
                    Specialty.NEUROSURGERY,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.ANESTHESIOLOGY,
                ),
                conditions=(
                    "Coma",
                    "Altered Mental Status",
                    "Traumatic Brain Injury",
                    "TBI",
                    "Brain Death Evaluation",
                    "Stroke",
                    "Intracranial Hemorrhage",
                    "Status Epilepticus",
                    "Encephalopathy",
                ),
                clinical_contexts=(
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.MONITORING,
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.SEDATION_ASSESSMENT,
                ),
                clinical_questions=(
                    "What is this comatose patient's FOUR score?",
                    "Can this patient be assessed for brain death?",
                    "Is there evidence of brainstem dysfunction?",
                    "How does consciousness compare to GCS?",
                    "What is the respiratory pattern?",
                ),
                icd10_codes=("R40.2", "R40.20", "G93.1", "S06", "I61", "I63"),
                keywords=(
                    "FOUR score", "Full Outline UnResponsiveness", "coma",
                    "brain death", "brainstem", "consciousness",
                    "intubated", "ICU", "neuro-ICU", "Wijdicks",
                )
            ),
            references=(
                Reference(
                    citation="Wijdicks EF, Bamlet WR, Maramattom BV, Manno EM, McClelland RL. "
                             "Validation of a new coma scale: The FOUR score. "
                             "Ann Neurol. 2005;58(4):585-593.",
                    doi="10.1002/ana.20611",
                    pmid="16178024",
                    year=2005
                ),
            ),
            version="1.0.0",
            validation_status="validated"
        )

    def calculate(
        self,
        eye_response: int,
        motor_response: int,
        brainstem_reflexes: int,
        respiration: int,
    ) -> ScoreResult:
        """
        Calculate FOUR Score.

        Args:
            eye_response: Eye response (0-4)
                4 = Eyelids open, tracking or blinking to command
                3 = Eyelids open but not tracking
                2 = Eyelids closed, open to loud voice
                1 = Eyelids closed, open to pain
                0 = Eyelids remain closed with pain

            motor_response: Motor response (0-4)
                4 = Thumbs up, fist, or peace sign to command
                3 = Localizing to pain
                2 = Flexion response to pain
                1 = Extension response to pain
                0 = No response to pain or myoclonus status

            brainstem_reflexes: Brainstem reflexes (0-4)
                4 = Pupil AND corneal reflexes present
                3 = One pupil wide and fixed
                2 = Pupil OR corneal reflexes absent
                1 = Pupil AND corneal reflexes absent
                0 = Absent pupil, corneal, AND cough reflexes

            respiration: Respiratory pattern (0-4)
                4 = Not intubated, regular breathing
                3 = Not intubated, Cheyne-Stokes pattern
                2 = Not intubated, irregular breathing
                1 = Intubated, breathes above ventilator rate
                0 = Intubated, breathes at vent rate OR apnea

        Returns:
            ScoreResult with FOUR Score and interpretation
        """
        # Validate inputs
        if not 0 <= eye_response <= 4:
            raise ValueError("Eye response must be between 0 and 4")
        if not 0 <= motor_response <= 4:
            raise ValueError("Motor response must be between 0 and 4")
        if not 0 <= brainstem_reflexes <= 4:
            raise ValueError("Brainstem reflexes must be between 0 and 4")
        if not 0 <= respiration <= 4:
            raise ValueError("Respiration must be between 0 and 4")

        # Calculate total score
        total_score = eye_response + motor_response + brainstem_reflexes + respiration

        # Format FOUR notation (e.g., "E4M4B4R4 = 16")
        four_notation = f"E{eye_response}M{motor_response}B{brainstem_reflexes}R{respiration}"

        # Get interpretation
        interpretation = self._get_interpretation(
            total_score, eye_response, motor_response, brainstem_reflexes, respiration
        )

        return ScoreResult(
            value=total_score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "eye_response": eye_response,
                "motor_response": motor_response,
                "brainstem_reflexes": brainstem_reflexes,
                "respiration": respiration,
            },
            calculation_details={
                "total_score": total_score,
                "notation": four_notation,
                "components": {
                    "eye_response": {
                        "score": eye_response,
                        "description": self._get_eye_description(eye_response)
                    },
                    "motor_response": {
                        "score": motor_response,
                        "description": self._get_motor_description(motor_response)
                    },
                    "brainstem_reflexes": {
                        "score": brainstem_reflexes,
                        "description": self._get_brainstem_description(brainstem_reflexes)
                    },
                    "respiration": {
                        "score": respiration,
                        "description": self._get_respiration_description(respiration)
                    },
                },
                "brain_death_screening": total_score == 0,
            },
        )

    def _get_eye_description(self, score: int) -> str:
        """Get eye response description"""
        descriptions = {
            4: "Eyelids open or opened, tracking or blinking to command",
            3: "Eyelids open but not tracking",
            2: "Eyelids closed but open to loud voice",
            1: "Eyelids closed but open to pain",
            0: "Eyelids remain closed with pain",
        }
        return descriptions.get(score, "Unknown")

    def _get_motor_description(self, score: int) -> str:
        """Get motor response description"""
        descriptions = {
            4: "Thumbs up, fist, or peace sign to command",
            3: "Localizing to pain",
            2: "Flexion response to pain (decorticate)",
            1: "Extension response to pain (decerebrate)",
            0: "No response to pain or generalized myoclonus status",
        }
        return descriptions.get(score, "Unknown")

    def _get_brainstem_description(self, score: int) -> str:
        """Get brainstem reflexes description"""
        descriptions = {
            4: "Pupil AND corneal reflexes present",
            3: "One pupil wide and fixed",
            2: "Pupil OR corneal reflexes absent",
            1: "Pupil AND corneal reflexes absent",
            0: "Absent pupil, corneal, AND cough reflexes",
        }
        return descriptions.get(score, "Unknown")

    def _get_respiration_description(self, score: int) -> str:
        """Get respiration pattern description"""
        descriptions = {
            4: "Not intubated, regular breathing pattern",
            3: "Not intubated, Cheyne-Stokes breathing",
            2: "Not intubated, irregular breathing",
            1: "Intubated, breathes above ventilator rate",
            0: "Breathes at ventilator rate or apnea",
        }
        return descriptions.get(score, "Unknown")

    def _get_interpretation(
        self,
        total_score: int,
        eye: int,
        motor: int,
        brainstem: int,
        respiration: int
    ) -> Interpretation:
        """Generate interpretation based on score"""

        # Check for brain death criteria (FOUR = 0)
        if total_score == 0:
            return Interpretation(
                summary="FOUR Score 0 - Possible Brain Death",
                detail="FOUR Score of 0 indicates absence of all responses and "
                       "absent brainstem reflexes. This meets screening criteria for "
                       "brain death evaluation.",
                severity=Severity.CRITICAL,
                stage="Score 0",
                stage_description="All responses absent - brain death screening positive",
                recommendations=(
                    "Formal brain death evaluation if clinically appropriate",
                    "Rule out confounders before brain death testing",
                    "Check core temperature (>36°C required)",
                    "Exclude sedation and neuromuscular blockade",
                    "Rule out severe metabolic or endocrine derangement",
                ),
                warnings=(
                    "FOUR Score 0 meets screening criteria for brain death",
                    "Exclude confounders: hypothermia, drugs, metabolic causes",
                    "Formal testing required for brain death determination",
                ),
                next_steps=(
                    "Exclude confounders",
                    "Formal brain death examination",
                    "Apnea testing if appropriate",
                    "Consider ancillary testing",
                ),
            )

        # Check for severe brainstem dysfunction
        if brainstem <= 1:
            return Interpretation(
                summary=f"FOUR Score {total_score} - Severe Brainstem Dysfunction",
                detail="Severe brainstem dysfunction with loss of protective reflexes. "
                       "High mortality risk even if not meeting brain death criteria.",
                severity=Severity.CRITICAL,
                stage=f"Score {total_score}",
                stage_description="Severe brainstem dysfunction",
                recommendations=(
                    "Ensure airway protection",
                    "Consider repeat neuroimaging",
                    "Monitor for herniation",
                    "Rule out reversible causes",
                ),
                warnings=(
                    "Brainstem reflexes severely compromised",
                    "High herniation risk",
                    "Very poor prognosis if no reversible cause",
                ),
                next_steps=(
                    "Neuroimaging to assess for progression",
                    "Serial FOUR Score monitoring",
                    "Goals of care discussion",
                ),
            )

        # Classify by total score
        if total_score <= 4:
            return Interpretation(
                summary=f"FOUR Score {total_score} - Severe Coma",
                detail="Severe impairment of consciousness. ICU monitoring required. "
                       "Approximate GCS equivalent: 3-5.",
                severity=Severity.CRITICAL,
                stage=f"Score {total_score}",
                stage_description="Severe coma",
                recommendations=(
                    "ICU monitoring essential",
                    "Assess for herniation signs",
                    "Protect airway if not already secured",
                    "Serial neurological examinations",
                    "Neuroimaging if not already done",
                ),
                warnings=(
                    "High mortality risk",
                    "May require emergent intervention",
                ),
                next_steps=(
                    "Identify and treat underlying cause",
                    "Frequent FOUR Score reassessment",
                    "Consider ICP monitoring",
                ),
            )
        elif total_score <= 8:
            return Interpretation(
                summary=f"FOUR Score {total_score} - Moderate-Severe Coma",
                detail="Significant impairment with some preserved responses. "
                       "Approximate GCS equivalent: 5-8.",
                severity=Severity.SEVERE,
                stage=f"Score {total_score}",
                stage_description="Moderate-severe coma",
                recommendations=(
                    "Continue ICU monitoring",
                    "Serial FOUR Score assessments",
                    "Identify and treat reversible causes",
                    "Maintain airway protection",
                ),
                next_steps=(
                    "Monitor for improvement or deterioration",
                    "Reassess every 4-6 hours",
                    "Plan for rehabilitation if improving",
                ),
            )
        elif total_score <= 12:
            return Interpretation(
                summary=f"FOUR Score {total_score} - Moderate Impairment",
                detail="Moderate impairment with preserved brainstem function. "
                       "Approximate GCS equivalent: 9-12.",
                severity=Severity.MODERATE,
                stage=f"Score {total_score}",
                stage_description="Moderate impairment",
                recommendations=(
                    "Continue monitoring for improvement or deterioration",
                    "Assess for underlying cause",
                    "Consider rehabilitation planning",
                    "Brainstem function preserved",
                ),
                next_steps=(
                    "Serial neurological assessments",
                    "Address underlying etiology",
                    "Early rehabilitation evaluation",
                ),
            )
        else:  # 13-16
            return Interpretation(
                summary=f"FOUR Score {total_score} - Mild Impairment or Normal",
                detail="Minimal to no impairment of consciousness. "
                       "Good brainstem and respiratory function. GCS equivalent: 13-15.",
                severity=Severity.MILD,
                stage=f"Score {total_score}",
                stage_description="Mild impairment or normal",
                recommendations=(
                    "Continue to monitor if acute brain injury",
                    "Good brainstem and respiratory function noted",
                    "Routine neurological monitoring",
                ),
                next_steps=(
                    "Continue routine care",
                    "Monitor for any changes",
                    "Good prognosis expected",
                ),
            )
