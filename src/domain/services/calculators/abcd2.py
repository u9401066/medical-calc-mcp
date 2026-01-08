"""
ABCD2 Score for TIA Stroke Risk

Predicts 2-, 7-, and 90-day risk of stroke after transient ischemic attack (TIA).

Reference:
    Johnston SC, Rothwell PM, Nguyen-Huynh MN, et al.
    Validation and refinement of scores to predict very early stroke risk after
    transient ischaemic attack.
    Lancet. 2007;369(9558):283-292.
    DOI: 10.1016/S0140-6736(07)60150-0
    PMID: 17258668
"""

from typing import Literal

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, RiskLevel, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class Abcd2Calculator(BaseCalculator):
    """
    ABCD2 Score for TIA Stroke Risk

    Predicts short-term stroke risk after TIA:

    A - Age ≥60 years: 1 point
    B - Blood pressure ≥140/90 mmHg: 1 point
    C - Clinical features:
        - Unilateral weakness: 2 points
        - Speech disturbance without weakness: 1 point
    D - Duration of symptoms:
        - ≥60 minutes: 2 points
        - 10-59 minutes: 1 point
    D - Diabetes: 1 point

    Total: 0-7 points

    2-day stroke risk:
    - 0-3: Low risk (1.0%)
    - 4-5: Moderate risk (4.1%)
    - 6-7: High risk (8.1%)

    7-day stroke risk:
    - 0-3: Low risk (1.2%)
    - 4-5: Moderate risk (5.9%)
    - 6-7: High risk (11.7%)
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="abcd2",
                name="ABCD2 Score",
                purpose="Predict stroke risk after TIA at 2, 7, and 90 days",
                input_params=["age_gte_60", "bp_gte_140_90", "clinical_features", "duration_minutes", "diabetes"],
                output_type="ABCD2 score (0-7) with stroke risk percentages",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.NEUROLOGY,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.INTERNAL_MEDICINE,
                ),
                conditions=(
                    "TIA",
                    "Transient Ischemic Attack",
                    "Mini-stroke",
                    "Cerebrovascular Disease",
                    "Stroke Risk",
                ),
                clinical_contexts=(
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.DISPOSITION,
                    ClinicalContext.TREATMENT_DECISION,
                ),
                clinical_questions=(
                    "What is the stroke risk after TIA?",
                    "Should this TIA patient be admitted?",
                    "How urgent is the workup for this TIA?",
                    "What is the 7-day stroke risk?",
                    "Is this high-risk TIA?",
                ),
                icd10_codes=(
                    "G45.9",  # TIA, unspecified
                    "G45.0",  # Vertebro-basilar artery syndrome
                    "G45.1",  # Carotid artery syndrome
                    "G45.8",  # Other TIA
                ),
                keywords=(
                    "ABCD2",
                    "TIA",
                    "transient ischemic attack",
                    "stroke risk",
                    "mini-stroke",
                    "cerebrovascular",
                    "amaurosis fugax",
                    "admission decision",
                ),
            ),
            references=(
                Reference(
                    citation="Johnston SC, Rothwell PM, Nguyen-Huynh MN, et al. "
                    "Validation and refinement of scores to predict very early stroke risk "
                    "after transient ischaemic attack. "
                    "Lancet. 2007;369(9558):283-292.",
                    doi="10.1016/S0140-6736(07)60150-0",
                    pmid="17258668",
                    year=2007,
                ),
                Reference(
                    citation="Giles MF, Rothwell PM. "
                    "Risk of stroke early after transient ischaemic attack: "
                    "a systematic review and meta-analysis. "
                    "Lancet Neurol. 2007;6(12):1063-1072.",
                    doi="10.1016/S1474-4422(07)70274-0",
                    pmid="17993293",
                    year=2007,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        age_gte_60: bool,
        bp_gte_140_90: bool,
        clinical_features: Literal["none", "speech_only", "unilateral_weakness"],
        duration_minutes: Literal["lt_10", "10_to_59", "gte_60"],
        diabetes: bool,
    ) -> ScoreResult:
        """
        Calculate ABCD2 Score.

        Args:
            age_gte_60: Age ≥60 years
            bp_gte_140_90: Blood pressure ≥140/90 mmHg at initial evaluation
            clinical_features: Clinical presentation
                - "none": No focal weakness or speech disturbance
                - "speech_only": Speech disturbance without weakness
                - "unilateral_weakness": Unilateral weakness (with or without speech)
            duration_minutes: Duration of TIA symptoms
                - "lt_10": <10 minutes
                - "10_to_59": 10-59 minutes
                - "gte_60": ≥60 minutes
            diabetes: History of diabetes mellitus

        Returns:
            ScoreResult with ABCD2 score and stroke risk stratification
        """
        # Calculate component scores
        age_points = 1 if age_gte_60 else 0
        bp_points = 1 if bp_gte_140_90 else 0

        # Clinical features
        if clinical_features == "unilateral_weakness":
            clinical_points = 2
        elif clinical_features == "speech_only":
            clinical_points = 1
        else:
            clinical_points = 0

        # Duration
        if duration_minutes == "gte_60":
            duration_points = 2
        elif duration_minutes == "10_to_59":
            duration_points = 1
        else:
            duration_points = 0

        diabetes_points = 1 if diabetes else 0

        # Total score
        score = age_points + bp_points + clinical_points + duration_points + diabetes_points

        # Get stroke risks
        risk_2day, risk_7day, risk_90day = self._get_stroke_risks(score)

        # Get interpretation
        interpretation = self._get_interpretation(score, risk_2day, risk_7day)

        return ScoreResult(
            value=float(score),
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "age_gte_60": age_gte_60,
                "bp_gte_140_90": bp_gte_140_90,
                "clinical_features": clinical_features,
                "duration_minutes": duration_minutes,
                "diabetes": diabetes,
            },
            calculation_details={
                "total_score": score,
                "max_possible": 7,
                "component_scores": {
                    "A_age": age_points,
                    "B_blood_pressure": bp_points,
                    "C_clinical_features": clinical_points,
                    "D1_duration": duration_points,
                    "D2_diabetes": diabetes_points,
                },
                "stroke_risk_2day": f"{risk_2day}%",
                "stroke_risk_7day": f"{risk_7day}%",
                "stroke_risk_90day": f"{risk_90day}%",
            },
            notes=self._get_notes(score),
        )

    def _get_stroke_risks(self, score: int) -> tuple[float, float, float]:
        """
        Get stroke risks at 2, 7, and 90 days based on score.

        Returns:
            Tuple of (2-day risk %, 7-day risk %, 90-day risk %)
        """
        # Risk data from Johnston 2007
        if score <= 3:
            return (1.0, 1.2, 3.1)
        elif score <= 5:
            return (4.1, 5.9, 9.8)
        else:  # 6-7
            return (8.1, 11.7, 17.8)

    def _get_interpretation(self, score: int, risk_2day: float, risk_7day: float) -> Interpretation:
        """Get clinical interpretation based on score"""

        if score <= 3:
            return Interpretation(
                summary=f"Low Risk TIA (ABCD2 = {score})",
                detail=f"2-day stroke risk: {risk_2day}%. 7-day stroke risk: {risk_7day}%.",
                severity=Severity.MILD,
                risk_level=RiskLevel.LOW,
                stage="Low Risk",
                stage_description="ABCD2 0-3",
                recommendations=(
                    "Outpatient workup may be appropriate if rapid follow-up available",
                    "Complete TIA workup within 24-48 hours",
                    "Brain imaging (MRI with DWI preferred)",
                    "Vascular imaging (carotid ultrasound, CTA, or MRA)",
                    "Cardiac evaluation (ECG, echocardiogram)",
                    "Start antiplatelet therapy (aspirin 81-325mg)",
                ),
                next_steps=(
                    "Ensure rapid outpatient follow-up (24-48h)",
                    "Patient education on stroke warning signs",
                    "Risk factor modification counseling",
                ),
            )
        elif score <= 5:
            return Interpretation(
                summary=f"Moderate Risk TIA (ABCD2 = {score})",
                detail=f"2-day stroke risk: {risk_2day}%. 7-day stroke risk: {risk_7day}%.",
                severity=Severity.MODERATE,
                risk_level=RiskLevel.INTERMEDIATE,
                stage="Moderate Risk",
                stage_description="ABCD2 4-5",
                recommendations=(
                    "Consider hospital admission or observation unit",
                    "Expedited workup within 24 hours",
                    "Urgent brain MRI with DWI",
                    "Vascular imaging (carotid ultrasound + intracranial)",
                    "Cardiac monitoring for atrial fibrillation",
                    "Dual antiplatelet therapy consideration (aspirin + clopidogrel x 21 days)",
                    "Statin initiation for LDL goal <70 mg/dL",
                ),
                warnings=(
                    "Do not discharge without rapid follow-up plan",
                    "Consider admission if imaging not immediately available",
                ),
                next_steps=(
                    "Neurology consultation recommended",
                    "Complete workup before discharge",
                    "Arrange follow-up within 48-72 hours",
                ),
            )
        else:  # 6-7
            return Interpretation(
                summary=f"High Risk TIA (ABCD2 = {score})",
                detail=f"2-day stroke risk: {risk_2day}%. 7-day stroke risk: {risk_7day}%.",
                severity=Severity.SEVERE,
                risk_level=RiskLevel.HIGH,
                stage="High Risk",
                stage_description="ABCD2 6-7",
                recommendations=(
                    "Hospital admission strongly recommended",
                    "Emergent brain imaging (CT immediately, MRI within hours)",
                    "Urgent vascular imaging",
                    "Continuous cardiac monitoring",
                    "Neurology consultation",
                    "Dual antiplatelet therapy (DAPT): aspirin + clopidogrel",
                    "High-intensity statin therapy",
                    "Aggressive blood pressure management",
                ),
                warnings=(
                    "High immediate stroke risk - do not delay workup",
                    "Consider stroke unit admission",
                    "Evaluate for carotid revascularization if stenosis >50%",
                ),
                next_steps=(
                    "Admit to stroke unit or monitored bed",
                    "Complete workup within 24 hours",
                    "Consider CEA/CAS if symptomatic carotid stenosis",
                ),
            )

    def _get_notes(self, score: int) -> list[str]:
        """Get clinical notes"""
        notes = [
            "ABCD2 is most useful for 2-day and 7-day stroke risk prediction",
            "Consider imaging findings (DWI lesion) to refine risk (ABCD2-I score)",
            "Dual antiplatelet therapy (DAPT) reduces recurrent stroke in high-risk TIA",
        ]

        if score >= 4:
            notes.append("POINT trial: DAPT (aspirin + clopidogrel x 21 days) reduces 90-day stroke risk")

        if score <= 3:
            notes.append("Low ABCD2 does not exclude stroke - clinical judgment remains essential")

        notes.append("Etiology-specific treatment (e.g., anticoagulation for AF) may be needed")

        return notes
