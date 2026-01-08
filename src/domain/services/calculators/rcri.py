"""
Revised Cardiac Risk Index (RCRI) Calculator

The RCRI (Lee Index) estimates the risk of major cardiac complications
after non-cardiac surgery.

Reference:
    Lee TH, Marcantonio ER, Mangione CM, et al. Derivation and prospective
    validation of a simple index for prediction of cardiac risk of major
    noncardiac surgery. Circulation. 1999;100(10):1043-1049.
    DOI: 10.1161/01.cir.100.10.1043
    PMID: 10477528
"""

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, RiskLevel, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class RcriCalculator(BaseCalculator):
    """
    Revised Cardiac Risk Index (Lee Index)

    A validated index for predicting major cardiac complications after
    non-cardiac surgery. Uses 6 independent predictors.

    Risk Factors (1 point each):
        1. High-risk surgery (intraperitoneal, intrathoracic, suprainguinal vascular)
        2. History of ischemic heart disease
        3. History of congestive heart failure
        4. History of cerebrovascular disease
        5. Preoperative insulin therapy for diabetes
        6. Preoperative creatinine >2 mg/dL (177 µmol/L)

    Major Cardiac Complications include:
        - Myocardial infarction
        - Pulmonary edema
        - Ventricular fibrillation or primary cardiac arrest
        - Complete heart block
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="rcri",
                name="Revised Cardiac Risk Index (Lee Index)",
                purpose="Estimate risk of major cardiac complications after non-cardiac surgery",
                input_params=[
                    "high_risk_surgery",
                    "ischemic_heart_disease",
                    "heart_failure",
                    "cerebrovascular_disease",
                    "insulin_diabetes",
                    "creatinine_above_2",
                ],
                output_type="RCRI Score (0-6) with cardiac complication risk percentage",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.ANESTHESIOLOGY,
                    Specialty.CARDIAC_ANESTHESIA,
                    Specialty.CARDIOLOGY,
                    Specialty.SURGERY,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.CRITICAL_CARE,
                ),
                conditions=(
                    "Preoperative Cardiac Risk",
                    "Perioperative MI",
                    "Surgical Cardiac Complications",
                    "Non-cardiac Surgery Risk",
                    "Ischemic Heart Disease",
                    "Heart Failure",
                ),
                clinical_contexts=(
                    ClinicalContext.PREOPERATIVE_ASSESSMENT,
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.CARDIAC_ASSESSMENT,
                    ClinicalContext.PROGNOSIS,
                ),
                clinical_questions=(
                    "What is the cardiac risk for this surgery?",
                    "Does this patient need cardiac clearance?",
                    "Should we delay surgery for cardiac optimization?",
                    "What is the perioperative MI risk?",
                    "Is this patient high risk for surgery?",
                ),
                icd10_codes=(
                    "I21",  # Acute myocardial infarction
                    "I50",  # Heart failure
                    "I25",  # Chronic ischemic heart disease
                    "I63",  # Cerebral infarction
                ),
                keywords=(
                    "RCRI",
                    "Lee index",
                    "cardiac risk",
                    "preoperative",
                    "perioperative",
                    "non-cardiac surgery",
                    "cardiac complications",
                    "MI risk",
                    "heart failure",
                    "ischemic heart disease",
                ),
            ),
            references=(
                Reference(
                    citation="Lee TH, Marcantonio ER, Mangione CM, et al. Derivation and prospective "
                    "validation of a simple index for prediction of cardiac risk of major "
                    "noncardiac surgery. Circulation. 1999;100(10):1043-1049.",
                    doi="10.1161/01.cir.100.10.1043",
                    pmid="10477528",
                    year=1999,
                ),
                Reference(
                    citation="Fleisher LA, Fleischmann KE, Auerbach AD, et al. 2014 ACC/AHA Guideline "
                    "on Perioperative Cardiovascular Evaluation and Management of Patients "
                    "Undergoing Noncardiac Surgery. Circulation. 2014;130(24):e278-e333.",
                    doi="10.1161/CIR.0000000000000106",
                    pmid="25085961",
                    year=2014,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        high_risk_surgery: bool = False,
        ischemic_heart_disease: bool = False,
        heart_failure: bool = False,
        cerebrovascular_disease: bool = False,
        insulin_diabetes: bool = False,
        creatinine_above_2: bool = False,
    ) -> ScoreResult:
        """
        Calculate Revised Cardiac Risk Index.

        Args:
            high_risk_surgery: Intraperitoneal, intrathoracic, or suprainguinal vascular surgery
            ischemic_heart_disease: History of MI, positive stress test, angina, nitrate use,
                                   or ECG with Q waves
            heart_failure: History of CHF, pulmonary edema, PND, bilateral rales, S3,
                          or CXR with pulmonary vascular redistribution
            cerebrovascular_disease: History of TIA or stroke
            insulin_diabetes: Diabetes requiring preoperative insulin therapy
            creatinine_above_2: Preoperative creatinine >2.0 mg/dL (177 µmol/L)

        Returns:
            ScoreResult with RCRI score and cardiac complication risk
        """
        # Calculate score
        score = sum([high_risk_surgery, ischemic_heart_disease, heart_failure, cerebrovascular_disease, insulin_diabetes, creatinine_above_2])

        # Get risk percentage
        risk_percentage = self._get_risk_percentage(score)

        # Get interpretation
        interpretation = self._get_interpretation(score)

        # Risk factors present
        risk_factors = []
        if high_risk_surgery:
            risk_factors.append("High-risk surgery")
        if ischemic_heart_disease:
            risk_factors.append("Ischemic heart disease")
        if heart_failure:
            risk_factors.append("Congestive heart failure")
        if cerebrovascular_disease:
            risk_factors.append("Cerebrovascular disease")
        if insulin_diabetes:
            risk_factors.append("Insulin-dependent diabetes")
        if creatinine_above_2:
            risk_factors.append("Creatinine >2 mg/dL")

        return ScoreResult(
            value=float(score),
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "high_risk_surgery": high_risk_surgery,
                "ischemic_heart_disease": ischemic_heart_disease,
                "heart_failure": heart_failure,
                "cerebrovascular_disease": cerebrovascular_disease,
                "insulin_diabetes": insulin_diabetes,
                "creatinine_above_2": creatinine_above_2,
            },
            calculation_details={
                "score": score,
                "risk_percentage": risk_percentage,
                "risk_factors_present": risk_factors,
                "risk_factors_count": len(risk_factors),
            },
            notes=[
                "Major cardiac complications: MI, pulmonary edema, VF/cardiac arrest, complete heart block",
                "Risk percentages from original derivation cohort",
                "Consider functional capacity (METs) in addition to RCRI",
            ],
        )

    def _get_risk_percentage(self, score: int) -> float:
        """Get estimated risk of major cardiac complications"""
        # From original Lee et al. derivation cohort
        risk_map = {
            0: 0.4,  # Class I: 0.4%
            1: 0.9,  # Class II: 0.9%
            2: 6.6,  # Class III: 6.6%
        }
        # 3 or more: Class IV: 11%
        return risk_map.get(score, 11.0)

    def _get_interpretation(self, score: int) -> Interpretation:
        """Get clinical interpretation for RCRI score"""

        risk_percentage = self._get_risk_percentage(score)

        if score == 0:
            return Interpretation(
                summary=f"RCRI Class I: Very low cardiac risk ({risk_percentage}%)",
                detail="No RCRI risk factors present. Very low risk of major adverse cardiac events (MACE). No further cardiac testing generally needed.",
                severity=Severity.NORMAL,
                risk_level=RiskLevel.VERY_LOW,
                stage="Class I",
                stage_description="0 risk factors - Very low risk",
                recommendations=(
                    "Proceed with surgery without cardiac testing",
                    "Routine perioperative care sufficient",
                    "Continue beta-blockers if already taking",
                ),
                next_steps=(
                    "Assess functional capacity (METs)",
                    "No preoperative cardiac testing needed",
                    "Standard perioperative monitoring",
                ),
            )
        elif score == 1:
            return Interpretation(
                summary=f"RCRI Class II: Low cardiac risk ({risk_percentage}%)",
                detail="One RCRI risk factor present. Low but measurable risk of MACE. Consider functional capacity before testing.",
                severity=Severity.MILD,
                risk_level=RiskLevel.LOW,
                stage="Class II",
                stage_description="1 risk factor - Low risk",
                recommendations=(
                    "Assess functional capacity (≥4 METs good)",
                    "Cardiac testing rarely changes management",
                    "Optimize medical therapy (beta-blockers, statins)",
                ),
                next_steps=(
                    "Evaluate functional capacity",
                    "Optimize medications if not already done",
                    "Proceed with surgery if functional capacity adequate",
                ),
            )
        elif score == 2:
            return Interpretation(
                summary=f"RCRI Class III: Elevated cardiac risk ({risk_percentage}%)",
                detail="Two RCRI risk factors present. Elevated risk of MACE. Functional capacity assessment critical; consider testing if poor or unknown.",
                severity=Severity.MODERATE,
                risk_level=RiskLevel.INTERMEDIATE,
                stage="Class III",
                stage_description="2 risk factors - Elevated risk",
                recommendations=(
                    "Assess functional capacity carefully",
                    "Consider cardiology consultation",
                    "Pharmacologic stress test if functional capacity <4 METs or unknown",
                    "Optimize beta-blocker and statin therapy",
                    "Consider whether surgery can be delayed for optimization",
                ),
                warnings=(
                    "Elevated perioperative MACE risk",
                    "Poor functional capacity further increases risk",
                ),
                next_steps=(
                    "Functional capacity assessment",
                    "Cardiology consultation if indicated",
                    "Consider preoperative stress testing",
                ),
            )
        else:  # score >= 3
            return Interpretation(
                summary=f"RCRI Class IV: High cardiac risk ({risk_percentage}%)",
                detail=f"{score} RCRI risk factors present. High risk of major adverse cardiac events. Multidisciplinary decision-making recommended.",
                severity=Severity.SEVERE,
                risk_level=RiskLevel.HIGH,
                stage="Class IV",
                stage_description=f"{score} risk factors - High risk",
                recommendations=(
                    "Cardiology consultation strongly recommended",
                    "Consider non-invasive cardiac testing",
                    "Assess if surgery can be delayed or modified",
                    "Optimize all cardiac medications",
                    "Consider if coronary revascularization indicated first",
                    "Intensive perioperative monitoring needed",
                ),
                warnings=(
                    "High risk of perioperative MI, heart failure, or death",
                    "Careful risk-benefit discussion with patient essential",
                    "Consider ICU admission postoperatively",
                ),
                next_steps=(
                    "Cardiology consultation",
                    "Functional or pharmacologic stress testing",
                    "Multidisciplinary surgical planning",
                    "Detailed informed consent discussion",
                ),
            )
