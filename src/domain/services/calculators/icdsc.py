"""
ICDSC (Intensive Care Delirium Screening Checklist)

The ICDSC is an 8-item delirium screening checklist designed for ICU patients.
It can be completed based on information from medical records and nursing
observations over an 8-24 hour period, making it practical for routine ICU use.

Reference (Original):
    Bergeron N, Dubois MJ, Cormier M, et al. Intensive Care Delirium
    Screening Checklist: evaluation of a new screening tool.
    Intensive Care Med. 2001;27(5):859-864.
    DOI: 10.1007/s001340100909
    PMID: 11430542

Reference (Validation):
    Gusmao-Flores D, Salluh JI, Chalhub RA, et al. The confusion assessment
    method for the intensive care unit (CAM-ICU) and intensive care delirium
    screening checklist (ICDSC) for the diagnosis of delirium: a systematic
    review and meta-analysis of clinical studies.
    Crit Care. 2012;16(4):R115.
    DOI: 10.1186/cc11407
    PMID: 22759376

Guideline:
    Devlin JW, Skrobik Y, Gélinas C, et al. Clinical Practice Guidelines
    for the Prevention and Management of Pain, Agitation/Sedation,
    Delirium, Immobility, and Sleep Disruption in Adult Patients in the
    ICU. Crit Care Med. 2018;46(9):e825-e873.
    PMID: 30113379
"""

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class ICDSCCalculator(BaseCalculator):
    """
    ICDSC (Intensive Care Delirium Screening Checklist) Calculator

    The ICDSC evaluates 8 items observed over 8-24 hours:
    1. Altered level of consciousness (A-E on sedation scale)
    2. Inattention
    3. Disorientation
    4. Hallucination/delusion/psychosis
    5. Psychomotor agitation or retardation
    6. Inappropriate speech or mood
    7. Sleep/wake cycle disturbance
    8. Symptom fluctuation

    Score Interpretation:
    - 0: No delirium
    - 1-3: Subsyndromal delirium
    - ≥4: Clinical delirium
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="icdsc",
                name="ICDSC (Intensive Care Delirium Screening Checklist)",
                purpose="Screen for delirium in ICU patients over 8-24 hour observation period",
                input_params=[
                    "altered_consciousness",
                    "inattention",
                    "disorientation",
                    "hallucination_psychosis",
                    "psychomotor_abnormality",
                    "inappropriate_speech_mood",
                    "sleep_wake_disturbance",
                    "symptom_fluctuation",
                ],
                output_type="Score (0-8) with delirium classification",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.CRITICAL_CARE,
                    Specialty.ANESTHESIOLOGY,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.NEUROLOGY,
                ),
                conditions=(
                    "Delirium",
                    "ICU Delirium",
                    "Acute Confusional State",
                    "Encephalopathy",
                    "Altered Mental Status",
                    "Subsyndromal Delirium",
                ),
                clinical_contexts=(
                    ClinicalContext.DELIRIUM_ASSESSMENT,
                    ClinicalContext.ICU_MANAGEMENT,
                    ClinicalContext.SEDATION_ASSESSMENT,
                    ClinicalContext.MONITORING,
                    ClinicalContext.SCREENING,
                ),
                clinical_questions=(
                    "Does this ICU patient have delirium?",
                    "What is the delirium severity?",
                    "Is there subsyndromal delirium?",
                    "Should we screen for ICU delirium?",
                ),
                icd10_codes=("F05", "R41.0", "R41.82"),
                keywords=(
                    "ICDSC",
                    "delirium",
                    "ICU delirium",
                    "screening checklist",
                    "altered consciousness",
                    "inattention",
                    "disorientation",
                    "subsyndromal delirium",
                    "PADIS",
                ),
            ),
            references=(
                Reference(
                    citation="Bergeron N, Dubois MJ, Cormier M, et al. Intensive Care Delirium "
                    "Screening Checklist: evaluation of a new screening tool. "
                    "Intensive Care Med. 2001;27(5):859-864.",
                    doi="10.1007/s001340100909",
                    pmid="11430542",
                    year=2001,
                ),
                Reference(
                    citation="Gusmao-Flores D, Salluh JI, Chalhub RA, et al. The confusion "
                    "assessment method for the intensive care unit (CAM-ICU) and "
                    "intensive care delirium screening checklist (ICDSC) for the "
                    "diagnosis of delirium. Crit Care. 2012;16(4):R115.",
                    doi="10.1186/cc11407",
                    pmid="22759376",
                    year=2012,
                ),
                Reference(
                    citation="Devlin JW, Skrobik Y, Gélinas C, et al. Clinical Practice Guidelines "
                    "for the Prevention and Management of Pain, Agitation/Sedation, "
                    "Delirium, Immobility, and Sleep Disruption in Adult Patients in the "
                    "ICU. Crit Care Med. 2018;46(9):e825-e873.",
                    pmid="30113379",
                    year=2018,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        altered_consciousness: bool = False,
        inattention: bool = False,
        disorientation: bool = False,
        hallucination_psychosis: bool = False,
        psychomotor_abnormality: bool = False,
        inappropriate_speech_mood: bool = False,
        sleep_wake_disturbance: bool = False,
        symptom_fluctuation: bool = False,
    ) -> ScoreResult:
        """
        Calculate ICDSC score.

        Args:
            altered_consciousness: Item 1 - Level of consciousness other than
                "Alert" (SAS ≠4, RASS ≠0) or easily aroused with verbal stimulation
            inattention: Item 2 - Difficulty in following commands or
                easily distracted by external stimuli
            disorientation: Item 3 - Any obvious mistake in time, place, or person
            hallucination_psychosis: Item 4 - Clinical manifestation of
                hallucination or behavior probably due to hallucination,
                or gross impairment in reality testing
            psychomotor_abnormality: Item 5 - Hyperactivity requiring sedatives
                or restraints, or hypoactivity/clinical withdrawal
            inappropriate_speech_mood: Item 6 - Inappropriate, disorganized,
                or incoherent speech, or inappropriate mood
            sleep_wake_disturbance: Item 7 - Sleeping <4h or waking frequently
                at night, or sleeping during most of the day
            symptom_fluctuation: Item 8 - Fluctuation of any item or symptoms
                over 24 hours (e.g., from different shift to shift)

        Returns:
            ScoreResult with ICDSC score and interpretation
        """
        # Calculate individual item scores
        items = {
            "altered_consciousness": altered_consciousness,
            "inattention": inattention,
            "disorientation": disorientation,
            "hallucination_psychosis": hallucination_psychosis,
            "psychomotor_abnormality": psychomotor_abnormality,
            "inappropriate_speech_mood": inappropriate_speech_mood,
            "sleep_wake_disturbance": sleep_wake_disturbance,
            "symptom_fluctuation": symptom_fluctuation,
        }

        # Total score
        score = sum(1 for v in items.values() if v)

        # Determine category
        if score >= 4:
            category = "Clinical Delirium"
        elif score >= 1:
            category = "Subsyndromal Delirium"
        else:
            category = "No Delirium"

        # Get interpretation
        interpretation = self._get_interpretation(score, category, items)

        return ScoreResult(
            value=score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs=items,
            calculation_details={
                "items": {
                    "1_altered_consciousness": {"present": altered_consciousness, "description": "Level of consciousness abnormal (not alert/calm)"},
                    "2_inattention": {"present": inattention, "description": "Difficulty following commands or easily distracted"},
                    "3_disorientation": {"present": disorientation, "description": "Mistake in time, place, or person"},
                    "4_hallucination_psychosis": {"present": hallucination_psychosis, "description": "Hallucination or impaired reality testing"},
                    "5_psychomotor_abnormality": {"present": psychomotor_abnormality, "description": "Hyperactivity or hypoactivity"},
                    "6_inappropriate_speech_mood": {"present": inappropriate_speech_mood, "description": "Inappropriate speech or mood"},
                    "7_sleep_wake_disturbance": {"present": sleep_wake_disturbance, "description": "Sleep-wake cycle disturbance"},
                    "8_symptom_fluctuation": {"present": symptom_fluctuation, "description": "Fluctuation of symptoms over 24h"},
                },
                "total_score": score,
                "max_score": 8,
                "category": category,
            },
            formula_used="ICDSC = sum of 8 binary items (each 0 or 1)",
        )

    def _get_interpretation(self, score: int, category: str, items: dict) -> Interpretation:
        """Get interpretation based on ICDSC score"""

        positive_items = [k.replace("_", " ").title() for k, v in items.items() if v]
        items_text = ", ".join(positive_items) if positive_items else "None"

        if score >= 4:
            return Interpretation(
                summary=f"ICDSC {score}/8: Clinical Delirium",
                detail=f"Score of {score} indicates clinical delirium (≥4 points). "
                f"Present features: {items_text}. "
                f"Sensitivity 99%, Specificity 64% at cutoff ≥4.",
                severity=Severity.MODERATE,
                stage="Clinical Delirium",
                stage_description="Score ≥4: Delirium present",
                recommendations=(
                    "Confirm delirium and identify underlying causes",
                    "Review medications (sedatives, anticholinergics, opioids)",
                    "Rule out infection, metabolic disturbances, hypoxia",
                    "Implement ABCDEF bundle interventions",
                    "Minimize sedation, prefer dexmedetomidine if needed",
                    "Early mobilization when safe",
                    "Maintain sleep-wake cycle",
                    "Reassess ICDSC daily",
                ),
                warnings=(
                    "Delirium associated with increased mortality",
                    "Each day of delirium increases mortality risk",
                    "Associated with long-term cognitive impairment",
                    "May require 1:1 monitoring for patient safety",
                ),
                next_steps=(
                    "Identify and treat precipitating causes",
                    "Non-pharmacologic interventions first",
                    "Consider antipsychotics only if safety concern",
                    "Family involvement for reorientation",
                    "Daily reassessment",
                ),
            )
        elif score >= 1:
            return Interpretation(
                summary=f"ICDSC {score}/8: Subsyndromal Delirium",
                detail=f"Score of {score} indicates subsyndromal delirium (1-3 points). "
                f"Present features: {items_text}. "
                f"Patient at increased risk for progression to clinical delirium.",
                severity=Severity.MILD,
                stage="Subsyndromal Delirium",
                stage_description="Score 1-3: At risk for delirium",
                recommendations=(
                    "Increased surveillance for delirium development",
                    "Implement delirium prevention strategies",
                    "Review potentially deliriogenic medications",
                    "Optimize sleep hygiene",
                    "Early mobilization",
                    "Cognitive stimulation and reorientation",
                    "Family involvement",
                ),
                warnings=(
                    "Subsyndromal delirium may progress to clinical delirium",
                    "Associated with worse outcomes than no delirium",
                ),
                next_steps=(
                    "Continue ICDSC screening every shift",
                    "Reinforce prevention bundle",
                    "Monitor for symptom progression",
                ),
            )
        else:
            return Interpretation(
                summary="ICDSC 0/8: No Delirium Detected",
                detail="Score of 0 indicates no delirium features currently present. Continue routine screening as delirium can develop at any time.",
                severity=Severity.NORMAL,
                stage="No Delirium",
                stage_description="Score 0: No delirium features",
                recommendations=(
                    "Continue routine ICDSC screening (at least daily)",
                    "Maintain delirium prevention strategies",
                    "Minimize sedation",
                    "Promote early mobilization",
                    "Maintain sleep-wake cycle",
                ),
                next_steps=(
                    "Continue daily ICDSC screening",
                    "Maintain prevention bundle",
                ),
            )
