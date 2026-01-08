"""
Apfel Simplified Score for Postoperative Nausea and Vomiting (PONV)

A validated 4-factor risk score for predicting PONV in adult patients
undergoing general anesthesia.

Reference:
    Apfel CC, Läärä E, Koivuranta M, Greim CA, Roewer N.
    A simplified risk score for predicting postoperative nausea and vomiting:
    conclusions from cross-validations between two centers.
    Anesthesiology. 1999 Sep;91(3):693-700.
    DOI: 10.1097/00000542-199909000-00022
    PMID: 10485781
"""

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, RiskLevel, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class ApfelPonvCalculator(BaseCalculator):
    """
    Apfel Simplified Score for PONV (Postoperative Nausea and Vomiting)

    Four risk factors (each scores 1 point):
    1. Female gender
    2. History of motion sickness or PONV
    3. Non-smoking status
    4. Use of postoperative opioids

    PONV Risk by Score:
    - 0 factors: ~10%
    - 1 factor:  ~21%
    - 2 factors: ~39%
    - 3 factors: ~61%
    - 4 factors: ~79%

    Recommendation: For patients with ≥2 risk factors, consider prophylactic
    antiemetic therapy.
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="apfel_ponv",
                name="Apfel Score for PONV",
                purpose="Predict postoperative nausea and vomiting risk",
                input_params=["female_gender", "history_motion_sickness_or_ponv", "non_smoker", "postoperative_opioids"],
                output_type="PONV risk score (0-4) with % probability",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.ANESTHESIOLOGY,
                    Specialty.SURGERY,
                    Specialty.EMERGENCY_MEDICINE,
                ),
                conditions=(
                    "Postoperative Nausea",
                    "Postoperative Vomiting",
                    "PONV",
                    "General Anesthesia",
                    "Perioperative Care",
                ),
                clinical_contexts=(
                    ClinicalContext.PREOPERATIVE_ASSESSMENT,
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.TREATMENT_DECISION,
                ),
                clinical_questions=(
                    "What is the PONV risk?",
                    "Does this patient need antiemetic prophylaxis?",
                    "Should I give ondansetron prophylactically?",
                    "What is the Apfel score?",
                    "What is the risk of postoperative nausea and vomiting?",
                ),
                icd10_codes=(
                    "R11.0",  # Nausea
                    "R11.10",  # Vomiting, unspecified
                    "R11.2",  # Nausea with vomiting, unspecified
                    "T88.59",  # Other complications of anesthesia
                ),
                keywords=(
                    "Apfel",
                    "PONV",
                    "postoperative nausea",
                    "vomiting",
                    "antiemetic",
                    "ondansetron",
                    "dexamethasone",
                    "prophylaxis",
                    "general anesthesia",
                    "perioperative",
                ),
            ),
            references=(
                Reference(
                    citation="Apfel CC, Läärä E, Koivuranta M, Greim CA, Roewer N. "
                    "A simplified risk score for predicting postoperative nausea and "
                    "vomiting: conclusions from cross-validations between two centers. "
                    "Anesthesiology. 1999;91(3):693-700.",
                    doi="10.1097/00000542-199909000-00022",
                    pmid="10485781",
                    year=1999,
                ),
                Reference(
                    citation="Gan TJ, Belani KG, Bergese S, et al. Fourth Consensus Guidelines "
                    "for the Management of Postoperative Nausea and Vomiting. "
                    "Anesth Analg. 2020;131(2):411-448.",
                    doi="10.1213/ANE.0000000000004833",
                    pmid="32467512",
                    year=2020,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(self, female_gender: bool, history_motion_sickness_or_ponv: bool, non_smoker: bool, postoperative_opioids: bool) -> ScoreResult:
        """
        Calculate Apfel PONV Risk Score.

        Args:
            female_gender: Patient is female
            history_motion_sickness_or_ponv: History of motion sickness or previous PONV
            non_smoker: Patient is a non-smoker (does NOT currently smoke)
            postoperative_opioids: Postoperative opioids are planned/anticipated

        Returns:
            ScoreResult with PONV risk score and prophylaxis recommendations
        """
        # Calculate score
        score = sum([female_gender, history_motion_sickness_or_ponv, non_smoker, postoperative_opioids])

        # Get PONV risk percentage
        ponv_risk = self._get_ponv_risk(score)

        # Get interpretation
        interpretation = self._get_interpretation(score, ponv_risk)

        # Build factor list
        present_factors = []
        if female_gender:
            present_factors.append("Female gender")
        if history_motion_sickness_or_ponv:
            present_factors.append("History of motion sickness or PONV")
        if non_smoker:
            present_factors.append("Non-smoker")
        if postoperative_opioids:
            present_factors.append("Postoperative opioids planned")

        return ScoreResult(
            value=float(score),
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "female_gender": female_gender,
                "history_motion_sickness_or_ponv": history_motion_sickness_or_ponv,
                "non_smoker": non_smoker,
                "postoperative_opioids": postoperative_opioids,
            },
            calculation_details={"score": score, "ponv_risk_percent": ponv_risk, "risk_factors_present": present_factors, "total_possible": 4},
            notes=self._get_notes(score),
        )

    def _get_ponv_risk(self, score: int) -> float:
        """Get PONV risk percentage based on score"""
        # From Apfel 1999: validated incidences
        risk_map = {0: 10.0, 1: 21.0, 2: 39.0, 3: 61.0, 4: 79.0}
        return risk_map.get(score, 0.0)

    def _get_interpretation(self, score: int, ponv_risk: float) -> Interpretation:
        """Get clinical interpretation based on score"""

        if score == 0:
            return Interpretation(
                summary=f"Very Low PONV Risk ({ponv_risk}%)",
                detail="No risk factors present. PONV risk approximately 10%.",
                severity=Severity.NORMAL,
                risk_level=RiskLevel.VERY_LOW,
                stage="Very Low Risk",
                stage_description="0 of 4 risk factors",
                recommendations=(
                    "Routine antiemetic prophylaxis not required",
                    "Rescue antiemetic if PONV occurs",
                ),
                next_steps=(
                    "No routine prophylaxis needed",
                    "Standard anesthetic technique acceptable",
                ),
            )
        elif score == 1:
            return Interpretation(
                summary=f"Low PONV Risk ({ponv_risk}%)",
                detail="One risk factor present. PONV risk approximately 21%.",
                severity=Severity.MILD,
                risk_level=RiskLevel.LOW,
                stage="Low Risk",
                stage_description="1 of 4 risk factors",
                recommendations=(
                    "Consider single-agent prophylaxis (e.g., dexamethasone 4mg)",
                    "Rescue antiemetic available",
                ),
                next_steps=(
                    "Single antiemetic prophylaxis optional",
                    "Consider TIVA if other factors favor it",
                ),
            )
        elif score == 2:
            return Interpretation(
                summary=f"Moderate PONV Risk ({ponv_risk}%)",
                detail="Two risk factors present. PONV risk approximately 39%. Prophylaxis recommended.",
                severity=Severity.MODERATE,
                risk_level=RiskLevel.INTERMEDIATE,
                stage="Moderate Risk",
                stage_description="2 of 4 risk factors",
                recommendations=(
                    "Dual antiemetic prophylaxis recommended",
                    "Consider: Ondansetron 4mg + Dexamethasone 4-8mg",
                    "Consider TIVA (propofol) over inhalational agents",
                    "Minimize opioid use if possible",
                ),
                warnings=("Without prophylaxis, ~40% will experience PONV",),
                next_steps=(
                    "Administer prophylactic antiemetics",
                    "Consider opioid-sparing multimodal analgesia",
                ),
            )
        elif score == 3:
            return Interpretation(
                summary=f"High PONV Risk ({ponv_risk}%)",
                detail="Three risk factors present. PONV risk approximately 61%. Multi-modal prophylaxis strongly recommended.",
                severity=Severity.MODERATE,
                risk_level=RiskLevel.HIGH,
                stage="High Risk",
                stage_description="3 of 4 risk factors",
                recommendations=(
                    "Multi-modal antiemetic prophylaxis (≥2 agents)",
                    "Consider: Ondansetron 4mg + Dexamethasone 4-8mg + Droperidol 0.625-1.25mg",
                    "TIVA with propofol strongly preferred",
                    "Opioid-sparing analgesia techniques",
                    "Regional anesthesia if appropriate",
                    "Avoid nitrous oxide",
                ),
                warnings=(
                    "High likelihood of PONV without prophylaxis",
                    "May significantly delay discharge",
                ),
                next_steps=(
                    "Implement multi-modal antiemetic strategy",
                    "Consider regional/local anesthesia",
                    "Plan opioid-free anesthesia if feasible",
                ),
            )
        else:  # score == 4
            return Interpretation(
                summary=f"Very High PONV Risk ({ponv_risk}%)",
                detail="All four risk factors present. PONV risk approximately 79%. Aggressive multi-modal prophylaxis essential.",
                severity=Severity.SEVERE,
                risk_level=RiskLevel.VERY_HIGH,
                stage="Very High Risk",
                stage_description="4 of 4 risk factors",
                recommendations=(
                    "Aggressive multi-modal prophylaxis (≥3 agents)",
                    "Consider: Ondansetron + Dexamethasone + Droperidol/Haloperidol + Scopolamine",
                    "TIVA with propofol essential",
                    "Avoid nitrous oxide",
                    "Opioid-free anesthesia if possible",
                    "Regional anesthesia preferred when appropriate",
                    "Consider aprepitant for high-risk patients",
                ),
                warnings=(
                    "~80% will experience PONV without prophylaxis",
                    "PONV can cause significant patient distress",
                    "May require overnight admission for outpatient surgery",
                ),
                next_steps=(
                    "Implement comprehensive PONV prevention strategy",
                    "Opioid-free anesthetic technique",
                    "Plan for prolonged PACU monitoring",
                    "Consider overnight observation",
                ),
            )

    def _get_notes(self, score: int) -> list[str]:
        """Get clinical notes based on score"""
        notes = [
            "Apfel score validated for adults undergoing general anesthesia",
            "Each risk factor adds ~20% absolute increase in PONV risk",
        ]

        if score >= 2:
            notes.extend(
                [
                    "Multi-modal prophylaxis reduces PONV by ~30-50%",
                    "TIVA with propofol reduces PONV vs inhalational agents",
                    "5-HT3 antagonists are most effective as end-of-surgery prophylaxis",
                    "Dexamethasone should be given at induction for best effect",
                ]
            )

        if score >= 3:
            notes.append("Consider adding NK-1 receptor antagonist (aprepitant) for highest-risk patients")

        return notes
