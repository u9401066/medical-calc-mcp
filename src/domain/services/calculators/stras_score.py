"""
Stroke after Surgery (STRAS) Score Calculator

Estimates postoperative stroke risk after non-cardiac surgery using
preoperative clinical risk factors.

Reference:
    Mashour GA, Shanks AM, Kheterpal S, Campbell DA, Engoren MC. Development
    and validation of a score to predict postoperative stroke after noncardiac
    surgery. Anesthesiology. 2017;127(4):673-683.
    DOI: 10.1097/ALN.0000000000001534
    PMID: 28051777
"""

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, RiskLevel, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class StrasScoreCalculator(BaseCalculator):
    """Stroke after Surgery (STRAS) perioperative stroke risk score."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="stras_score",
                name="Stroke after Surgery (STRAS) Score",
                purpose="Estimate postoperative stroke risk after non-cardiac surgery",
                input_params=[
                    "age_years",
                    "prior_stroke_or_tia",
                    "acute_renal_failure",
                    "asa_class_4_or_5",
                    "urgent_or_emergency_surgery",
                    "hypertension",
                ],
                output_type="STRAS score (0-8 points) with perioperative stroke risk category",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.ANESTHESIOLOGY,
                    Specialty.SURGERY,
                    Specialty.NEUROLOGY,
                    Specialty.INTERNAL_MEDICINE,
                ),
                conditions=(
                    "Postoperative Stroke",
                    "Perioperative Stroke",
                    "Non-cardiac Surgery Risk",
                    "Cerebrovascular Disease",
                ),
                clinical_contexts=(
                    ClinicalContext.PREOPERATIVE_ASSESSMENT,
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.NEUROLOGIC_ASSESSMENT,
                ),
                clinical_questions=(
                    "What is this patient's stroke risk after surgery?",
                    "Does this surgical patient need enhanced neurologic monitoring?",
                    "How should I counsel this patient about perioperative stroke risk?",
                    "Is this patient high risk for postoperative stroke?",
                ),
                icd10_codes=(
                    "I63",
                    "G45",
                    "I10",
                    "N17",
                ),
                keywords=(
                    "STRAS",
                    "stroke after surgery",
                    "postoperative stroke",
                    "perioperative stroke",
                    "noncardiac surgery",
                    "preoperative risk",
                    "cerebrovascular",
                    "surgical risk",
                ),
            ),
            references=(
                Reference(
                    citation="Mashour GA, Shanks AM, Kheterpal S, Campbell DA, Engoren MC. Development and validation of a score to predict postoperative stroke after noncardiac surgery. Anesthesiology. 2017;127(4):673-683.",
                    doi="10.1097/ALN.0000000000001534",
                    pmid="28051777",
                    year=2017,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        age_years: int,
        prior_stroke_or_tia: bool = False,
        acute_renal_failure: bool = False,
        asa_class_4_or_5: bool = False,
        urgent_or_emergency_surgery: bool = False,
        hypertension: bool = False,
    ) -> ScoreResult:
        """
        Calculate the STRAS score.

        Args:
            age_years: Patient age in years; age >=70 adds 1 point.
            prior_stroke_or_tia: Prior stroke or transient ischemic attack; adds 2 points.
            acute_renal_failure: Acute renal failure, dialysis, or severe renal dysfunction; adds 2 points.
            asa_class_4_or_5: ASA physical status class 4 or 5; adds 1 point.
            urgent_or_emergency_surgery: Urgent or emergent surgical case; adds 1 point.
            hypertension: History of hypertension; adds 1 point.

        Returns:
            ScoreResult with STRAS score and risk category.
        """
        if age_years < 18 or age_years > 120:
            raise ValueError("age_years must be between 18 and 120")

        score = 0
        risk_factors: list[str] = []

        if age_years >= 70:
            score += 1
            risk_factors.append("Age ≥70 years")
        if prior_stroke_or_tia:
            score += 2
            risk_factors.append("Prior stroke or TIA")
        if acute_renal_failure:
            score += 2
            risk_factors.append("Acute renal failure / severe renal dysfunction")
        if asa_class_4_or_5:
            score += 1
            risk_factors.append("ASA physical status class 4 or 5")
        if urgent_or_emergency_surgery:
            score += 1
            risk_factors.append("Urgent or emergency surgery")
        if hypertension:
            score += 1
            risk_factors.append("Hypertension")

        return ScoreResult(
            value=float(score),
            unit=Unit.SCORE,
            interpretation=self._get_interpretation(score),
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "age_years": age_years,
                "prior_stroke_or_tia": prior_stroke_or_tia,
                "acute_renal_failure": acute_renal_failure,
                "asa_class_4_or_5": asa_class_4_or_5,
                "urgent_or_emergency_surgery": urgent_or_emergency_surgery,
                "hypertension": hypertension,
            },
            calculation_details={
                "score": score,
                "risk_factors_present": risk_factors,
                "risk_factors_count": len(risk_factors),
                "point_assignments": {
                    "age_70_or_older": 1 if age_years >= 70 else 0,
                    "prior_stroke_or_tia": 2 if prior_stroke_or_tia else 0,
                    "acute_renal_failure": 2 if acute_renal_failure else 0,
                    "asa_class_4_or_5": 1 if asa_class_4_or_5 else 0,
                    "urgent_or_emergency_surgery": 1 if urgent_or_emergency_surgery else 0,
                    "hypertension": 1 if hypertension else 0,
                },
            },
            notes=[
                "Intended for adult patients undergoing non-cardiac surgery.",
                "Use as an adjunct to clinical judgment; absolute risk should be interpreted with local case mix and perioperative context.",
                "Consider perioperative optimization of modifiable vascular risk factors when feasible.",
            ],
        )

    def _get_interpretation(self, score: int) -> Interpretation:
        """Return clinical interpretation for STRAS score."""
        if score <= 1:
            return Interpretation(
                summary="Low postoperative stroke risk by STRAS score.",
                detail="Few STRAS risk factors are present. Continue routine perioperative stroke prevention and monitoring appropriate to the procedure.",
                severity=Severity.NORMAL,
                risk_level=RiskLevel.LOW,
                stage="Low risk",
                stage_description="0-1 points",
                recommendations=(
                    "Continue standard perioperative assessment",
                    "Optimize routine vascular risk factors such as blood pressure and antithrombotic management",
                ),
                next_steps=(
                    "Proceed with usual perioperative monitoring unless other clinical concerns exist",
                    "Document baseline neurologic status when clinically appropriate",
                ),
            )
        if score <= 3:
            return Interpretation(
                summary="Intermediate postoperative stroke risk by STRAS score.",
                detail="Multiple STRAS risk factors are present. Perioperative planning should address hemodynamics, antithrombotic therapy, and postoperative neurologic surveillance.",
                severity=Severity.MODERATE,
                risk_level=RiskLevel.INTERMEDIATE,
                stage="Intermediate risk",
                stage_description="2-3 points",
                recommendations=(
                    "Review antiplatelet or anticoagulant interruption and restart plan",
                    "Optimize blood pressure and perfusion targets",
                    "Consider enhanced postoperative neurologic checks",
                ),
                next_steps=(
                    "Discuss perioperative stroke risk during informed consent",
                    "Coordinate anesthesia, surgical, and medical teams for risk mitigation",
                ),
            )
        if score <= 5:
            return Interpretation(
                summary="High postoperative stroke risk by STRAS score.",
                detail="Several important STRAS risk factors are present. Enhanced perioperative planning and postoperative surveillance are recommended.",
                severity=Severity.SEVERE,
                risk_level=RiskLevel.HIGH,
                stage="High risk",
                stage_description="4-5 points",
                recommendations=(
                    "Consider multidisciplinary preoperative optimization",
                    "Plan close hemodynamic management and postoperative neurologic monitoring",
                    "Evaluate whether urgent surgery timing can be optimized when clinically safe",
                ),
                warnings=(
                    "High-risk features may justify escalation of postoperative monitoring level",
                    "Do not use this score as the sole reason to delay urgent or lifesaving surgery",
                ),
                next_steps=(
                    "Confirm baseline neurologic deficits and communicate them to the perioperative team",
                    "Consider neurology or perioperative medicine consultation when results will change management",
                ),
            )
        return Interpretation(
            summary="Very high postoperative stroke risk by STRAS score.",
            detail="A very high STRAS score indicates multiple major risk factors for postoperative stroke. Intensive planning and monitoring should be considered.",
            severity=Severity.CRITICAL,
            risk_level=RiskLevel.VERY_HIGH,
            stage="Very high risk",
            stage_description="6-8 points",
            recommendations=(
                "Use multidisciplinary decision-making for surgical timing and perioperative strategy",
                "Consider monitored or ICU-level postoperative care when appropriate",
                "Ensure explicit neurologic monitoring and rapid stroke-response plan",
            ),
            warnings=(
                "Very high risk of perioperative neurologic complication relative to baseline surgical patients",
                "Balance stroke prevention against bleeding, urgency, and surgical risks",
            ),
            next_steps=(
                "Discuss individualized risks, benefits, and alternatives with patient or surrogate",
                "Coordinate antithrombotic, hemodynamic, and postoperative monitoring plans before surgery",
            ),
        )
