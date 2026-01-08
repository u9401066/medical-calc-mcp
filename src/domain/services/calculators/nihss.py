"""
NIH Stroke Scale (NIHSS)

A 15-item neurological examination scale for assessing stroke severity.
Scores range from 0 (no deficit) to 42 (maximum deficit).

Reference:
    Brott T, Adams HP Jr, Olinger CP, et al.
    Measurements of acute cerebral infarction: a clinical examination scale.
    Stroke. 1989;20(7):864-870.
    DOI: 10.1161/01.str.20.7.864
    PMID: 2749846

    Lyden P, Brott T, Tilley B, et al.
    Improved reliability of the NIH Stroke Scale using video training.
    Stroke. 1994;25(11):2220-2226.
    PMID: 7974549
"""

from typing import Literal

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, RiskLevel, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class NihssCalculator(BaseCalculator):
    """
    NIH Stroke Scale (NIHSS)

    A 15-item neurological examination for stroke severity:

    1a. Level of Consciousness (LOC): 0-3
    1b. LOC Questions (month, age): 0-2
    1c. LOC Commands (open/close eyes, grip/release): 0-2
    2. Best Gaze: 0-2
    3. Visual Fields: 0-3
    4. Facial Palsy: 0-3
    5a. Motor Arm - Left: 0-4
    5b. Motor Arm - Right: 0-4
    6a. Motor Leg - Left: 0-4
    6b. Motor Leg - Right: 0-4
    7. Limb Ataxia: 0-2
    8. Sensory: 0-2
    9. Best Language: 0-3
    10. Dysarthria: 0-2
    11. Extinction/Inattention: 0-2

    Total: 0-42 points

    Severity:
    - 0: No stroke symptoms
    - 1-4: Minor stroke
    - 5-15: Moderate stroke
    - 16-20: Moderate to severe stroke
    - 21-42: Severe stroke
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="nihss",
                name="NIH Stroke Scale (NIHSS)",
                purpose="Quantify stroke severity and track neurological changes",
                input_params=[
                    "loc",
                    "loc_questions",
                    "loc_commands",
                    "best_gaze",
                    "visual_fields",
                    "facial_palsy",
                    "motor_arm_left",
                    "motor_arm_right",
                    "motor_leg_left",
                    "motor_leg_right",
                    "limb_ataxia",
                    "sensory",
                    "best_language",
                    "dysarthria",
                    "extinction_inattention",
                ],
                output_type="NIHSS score (0-42) with severity classification",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.NEUROLOGY,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.CRITICAL_CARE,
                    Specialty.INTERNAL_MEDICINE,
                ),
                conditions=(
                    "Stroke",
                    "Ischemic Stroke",
                    "Hemorrhagic Stroke",
                    "TIA",
                    "Cerebrovascular Accident",
                    "CVA",
                    "Acute Neurological Deficit",
                ),
                clinical_contexts=(
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.MONITORING,
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.TREATMENT_DECISION,
                ),
                clinical_questions=(
                    "What is the NIHSS score?",
                    "How severe is this stroke?",
                    "Is this patient eligible for thrombolytics?",
                    "What is the stroke severity?",
                    "Is there neurological improvement?",
                ),
                icd10_codes=(
                    "I63",  # Cerebral infarction
                    "I61",  # Intracerebral hemorrhage
                    "G45.9",  # TIA, unspecified
                ),
                keywords=(
                    "NIHSS",
                    "stroke",
                    "NIH Stroke Scale",
                    "CVA",
                    "ischemic",
                    "hemorrhagic",
                    "thrombolysis",
                    "tPA",
                    "neurological",
                    "deficit",
                    "severity",
                ),
            ),
            references=(
                Reference(
                    citation="Brott T, Adams HP Jr, Olinger CP, et al. "
                    "Measurements of acute cerebral infarction: a clinical examination scale. "
                    "Stroke. 1989;20(7):864-870.",
                    doi="10.1161/01.str.20.7.864",
                    pmid="2749846",
                    year=1989,
                ),
                Reference(
                    citation="Lyden P, Brott T, Tilley B, et al. "
                    "Improved reliability of the NIH Stroke Scale using video training. "
                    "Stroke. 1994;25(11):2220-2226.",
                    pmid="7974549",
                    year=1994,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        loc: Literal[0, 1, 2, 3],
        loc_questions: Literal[0, 1, 2],
        loc_commands: Literal[0, 1, 2],
        best_gaze: Literal[0, 1, 2],
        visual_fields: Literal[0, 1, 2, 3],
        facial_palsy: Literal[0, 1, 2, 3],
        motor_arm_left: Literal[0, 1, 2, 3, 4],
        motor_arm_right: Literal[0, 1, 2, 3, 4],
        motor_leg_left: Literal[0, 1, 2, 3, 4],
        motor_leg_right: Literal[0, 1, 2, 3, 4],
        limb_ataxia: Literal[0, 1, 2],
        sensory: Literal[0, 1, 2],
        best_language: Literal[0, 1, 2, 3],
        dysarthria: Literal[0, 1, 2],
        extinction_inattention: Literal[0, 1, 2],
    ) -> ScoreResult:
        """
        Calculate NIH Stroke Scale.

        Args:
            loc: Level of Consciousness (0=Alert, 1=Drowsy, 2=Stuporous, 3=Coma)
            loc_questions: LOC Questions (0=Both correct, 1=One correct, 2=Neither)
            loc_commands: LOC Commands (0=Both correct, 1=One correct, 2=Neither)
            best_gaze: Best Gaze (0=Normal, 1=Partial gaze palsy, 2=Forced deviation)
            visual_fields: Visual Fields (0=No loss, 1=Partial hemianopia, 2=Complete hemianopia, 3=Bilateral)
            facial_palsy: Facial Palsy (0=Normal, 1=Minor, 2=Partial, 3=Complete)
            motor_arm_left: Left Arm Motor (0=No drift, 1=Drift, 2=Some effort, 3=No effort, 4=No movement)
            motor_arm_right: Right Arm Motor (0=No drift, 1=Drift, 2=Some effort, 3=No effort, 4=No movement)
            motor_leg_left: Left Leg Motor (0=No drift, 1=Drift, 2=Some effort, 3=No effort, 4=No movement)
            motor_leg_right: Right Leg Motor (0=No drift, 1=Drift, 2=Some effort, 3=No effort, 4=No movement)
            limb_ataxia: Limb Ataxia (0=Absent, 1=Present in one limb, 2=Present in two limbs)
            sensory: Sensory (0=Normal, 1=Mild-moderate loss, 2=Severe-total loss)
            best_language: Best Language (0=No aphasia, 1=Mild-moderate, 2=Severe, 3=Mute/global)
            dysarthria: Dysarthria (0=Normal, 1=Mild-moderate, 2=Severe/mute)
            extinction_inattention: Extinction/Inattention (0=None, 1=One modality, 2=Profound)

        Returns:
            ScoreResult with NIHSS score and severity classification
        """
        # Calculate total score
        score = (
            loc
            + loc_questions
            + loc_commands
            + best_gaze
            + visual_fields
            + facial_palsy
            + motor_arm_left
            + motor_arm_right
            + motor_leg_left
            + motor_leg_right
            + limb_ataxia
            + sensory
            + best_language
            + dysarthria
            + extinction_inattention
        )

        # Component breakdown
        component_scores = {
            "1a_loc": loc,
            "1b_loc_questions": loc_questions,
            "1c_loc_commands": loc_commands,
            "2_best_gaze": best_gaze,
            "3_visual_fields": visual_fields,
            "4_facial_palsy": facial_palsy,
            "5a_motor_arm_left": motor_arm_left,
            "5b_motor_arm_right": motor_arm_right,
            "6a_motor_leg_left": motor_leg_left,
            "6b_motor_leg_right": motor_leg_right,
            "7_limb_ataxia": limb_ataxia,
            "8_sensory": sensory,
            "9_best_language": best_language,
            "10_dysarthria": dysarthria,
            "11_extinction_inattention": extinction_inattention,
        }

        # Identify lateralization
        left_motor = motor_arm_left + motor_leg_left
        right_motor = motor_arm_right + motor_leg_right
        lateralization = None
        if left_motor > right_motor:
            lateralization = "Left hemiparesis (Right hemisphere stroke)"
        elif right_motor > left_motor:
            lateralization = "Right hemiparesis (Left hemisphere stroke)"

        # Get interpretation
        interpretation = self._get_interpretation(score, best_language)

        return ScoreResult(
            value=float(score),
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "loc": loc,
                "loc_questions": loc_questions,
                "loc_commands": loc_commands,
                "best_gaze": best_gaze,
                "visual_fields": visual_fields,
                "facial_palsy": facial_palsy,
                "motor_arm_left": motor_arm_left,
                "motor_arm_right": motor_arm_right,
                "motor_leg_left": motor_leg_left,
                "motor_leg_right": motor_leg_right,
                "limb_ataxia": limb_ataxia,
                "sensory": sensory,
                "best_language": best_language,
                "dysarthria": dysarthria,
                "extinction_inattention": extinction_inattention,
            },
            calculation_details={
                "total_score": score,
                "max_possible": 42,
                "component_scores": component_scores,
                "lateralization": lateralization,
                "left_motor_total": left_motor,
                "right_motor_total": right_motor,
            },
            notes=self._get_notes(score, best_language > 0),
        )

    def _get_interpretation(self, score: int, language_score: int) -> Interpretation:
        """Get clinical interpretation based on score"""

        if score == 0:
            return Interpretation(
                summary="No Stroke Symptoms (NIHSS 0)",
                detail="No measurable neurological deficit on NIHSS examination.",
                severity=Severity.NORMAL,
                risk_level=RiskLevel.LOW,
                stage="No Deficit",
                stage_description="NIHSS = 0",
                recommendations=(
                    "Continue evaluation for possible TIA or stroke mimic",
                    "Consider MRI with DWI if clinical suspicion remains",
                ),
                next_steps=(
                    "Complete stroke workup if clinically indicated",
                    "Risk factor assessment",
                ),
            )
        elif score <= 4:
            return Interpretation(
                summary=f"Minor Stroke (NIHSS {score})",
                detail="Minor neurological deficit. Generally good prognosis.",
                severity=Severity.MILD,
                risk_level=RiskLevel.LOW,
                stage="Minor Stroke",
                stage_description="NIHSS 1-4",
                recommendations=(
                    "Consider IV thrombolytics if within window and no contraindications",
                    "Aspirin 325mg if tPA not given",
                    "Admit to stroke unit for monitoring",
                    "Early PT/OT evaluation",
                ),
                next_steps=(
                    "Complete stroke workup (imaging, labs, cardiac)",
                    "Secondary prevention initiation",
                    "Early mobilization",
                ),
            )
        elif score <= 15:
            return Interpretation(
                summary=f"Moderate Stroke (NIHSS {score})",
                detail="Moderate neurological deficit. Significant disability likely without treatment.",
                severity=Severity.MODERATE,
                risk_level=RiskLevel.INTERMEDIATE,
                stage="Moderate Stroke",
                stage_description="NIHSS 5-15",
                recommendations=(
                    "IV thrombolytics if within 4.5h window",
                    "Consider mechanical thrombectomy if LVO suspected",
                    "Strict blood pressure management",
                    "Admit to stroke unit or ICU",
                    "NPO pending swallow evaluation",
                    "DVT prophylaxis",
                ),
                warnings=(
                    "Risk of hemorrhagic transformation",
                    "Monitor for neurological deterioration",
                ),
                next_steps=(
                    "Urgent neurology consultation",
                    "Consider endovascular evaluation",
                    "Plan rehabilitation assessment",
                ),
            )
        elif score <= 20:
            return Interpretation(
                summary=f"Moderate-Severe Stroke (NIHSS {score})",
                detail="Moderate to severe deficit. High risk of disability and complications.",
                severity=Severity.MODERATE,
                risk_level=RiskLevel.HIGH,
                stage="Moderate-Severe Stroke",
                stage_description="NIHSS 16-20",
                recommendations=(
                    "Emergent reperfusion therapy evaluation",
                    "Consider mechanical thrombectomy strongly",
                    "ICU admission for close monitoring",
                    "Aggressive blood pressure control",
                    "Consider intubation if airway compromise",
                    "ICP monitoring consideration",
                ),
                warnings=(
                    "High risk of malignant edema",
                    "Aspiration risk - strict NPO",
                    "Monitor for herniation signs",
                ),
                next_steps=(
                    "Emergent neurovascular consultation",
                    "Serial NIHSS monitoring",
                    "Early goals of care discussion",
                ),
            )
        else:
            return Interpretation(
                summary=f"Severe Stroke (NIHSS {score})",
                detail="Severe neurological deficit. Very high morbidity and mortality risk.",
                severity=Severity.SEVERE,
                risk_level=RiskLevel.VERY_HIGH,
                stage="Severe Stroke",
                stage_description="NIHSS 21-42",
                recommendations=(
                    "Consider all reperfusion options if within window",
                    "ICU admission mandatory",
                    "Airway protection likely needed",
                    "Aggressive edema management",
                    "Early neurosurgical consultation for decompression",
                    "Family meeting for goals of care",
                ),
                warnings=(
                    "Very high mortality risk",
                    "High risk of herniation",
                    "Consider comfort-focused care if prognosis poor",
                ),
                next_steps=(
                    "Multidisciplinary team involvement",
                    "Goals of care discussion with family",
                    "Consider palliative care consultation",
                ),
            )

    def _get_notes(self, score: int, has_aphasia: bool) -> list[str]:
        """Get clinical notes"""
        notes = [
            "NIHSS should be performed serially to track progression",
            "Score can be artificially low in posterior circulation strokes",
        ]

        if has_aphasia:
            notes.append("Aphasia present - consider left hemisphere involvement")

        if score >= 6:
            notes.append("NIHSS ≥6: Strong consideration for thrombectomy if LVO present")

        if score >= 25:
            notes.append("Very high NIHSS: Discuss prognosis and goals of care early")

        return notes
