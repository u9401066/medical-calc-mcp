"""
STOP-BANG Questionnaire for Obstructive Sleep Apnea Screening

A validated 8-item screening tool for OSA risk in surgical patients.
Each item scores 0 or 1 point.

Reference:
    Chung F, Yegneswaran B, Liao P, et al.
    STOP questionnaire: a tool to screen patients for obstructive sleep apnea.
    Anesthesiology. 2008;108(5):812-821.
    DOI: 10.1097/ALN.0b013e31816d83e4
    PMID: 18431116

    Chung F, Abdullah HR, Liao P.
    STOP-Bang Questionnaire: A Practical Approach to Screen for Obstructive Sleep Apnea.
    Chest. 2016;149(3):631-638.
    DOI: 10.1378/chest.15-0903
    PMID: 26378880
"""

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, RiskLevel, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class StopBangCalculator(BaseCalculator):
    """
    STOP-BANG Questionnaire for OSA Screening

    STOP criteria (symptoms):
    - S: Snoring loudly
    - T: Tired/sleepy during daytime
    - O: Observed apnea during sleep
    - P: Pressure (high blood pressure)

    BANG criteria (physical findings):
    - B: BMI > 35 kg/m²
    - A: Age > 50 years
    - N: Neck circumference > 40 cm (16 inches)
    - G: Gender = Male

    Risk Stratification:
    - 0-2: Low risk of OSA
    - 3-4: Intermediate risk of OSA
    - 5-8: High risk of OSA

    High risk also if:
    - Score ≥2 + Male gender
    - Score ≥2 + BMI > 35
    - Score ≥2 + Neck > 40 cm
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="stop_bang",
                name="STOP-BANG Questionnaire",
                purpose="Screen for obstructive sleep apnea risk in surgical patients",
                input_params=[
                    "snoring", "tired", "observed_apnea", "high_blood_pressure",
                    "bmi_over_35", "age_over_50", "neck_over_40cm", "male_gender"
                ],
                output_type="OSA risk score (0-8) with risk stratification"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.ANESTHESIOLOGY,
                    Specialty.PULMONOLOGY,
                    Specialty.SURGERY,
                    Specialty.INTERNAL_MEDICINE,
                ),
                conditions=(
                    "Obstructive Sleep Apnea",
                    "OSA",
                    "Sleep Apnea",
                    "Sleep Disordered Breathing",
                    "Preoperative Assessment",
                    "Perioperative Risk",
                ),
                clinical_contexts=(
                    ClinicalContext.PREOPERATIVE_ASSESSMENT,
                    ClinicalContext.SCREENING,
                    ClinicalContext.RISK_STRATIFICATION,
                ),
                clinical_questions=(
                    "Does this patient have OSA?",
                    "What is the STOP-BANG score?",
                    "Is this patient high risk for sleep apnea?",
                    "Should I order a sleep study?",
                    "Is this patient safe for outpatient surgery?",
                ),
                icd10_codes=(
                    "G47.33",  # Obstructive sleep apnea
                    "G47.30",  # Sleep apnea, unspecified
                    "R06.83",  # Snoring
                ),
                keywords=(
                    "STOP-BANG", "OSA", "sleep apnea", "snoring", "apnea",
                    "preoperative", "screening", "BMI", "neck circumference",
                    "obstructive", "hypopnea", "AHI",
                )
            ),
            references=(
                Reference(
                    citation="Chung F, Yegneswaran B, Liao P, et al. "
                             "STOP questionnaire: a tool to screen patients for obstructive sleep apnea. "
                             "Anesthesiology. 2008;108(5):812-821.",
                    doi="10.1097/ALN.0b013e31816d83e4",
                    pmid="18431116",
                    year=2008
                ),
                Reference(
                    citation="Chung F, Abdullah HR, Liao P. "
                             "STOP-Bang Questionnaire: A Practical Approach to Screen for "
                             "Obstructive Sleep Apnea. Chest. 2016;149(3):631-638.",
                    doi="10.1378/chest.15-0903",
                    pmid="26378880",
                    year=2016
                ),
            ),
            version="1.0.0",
            validation_status="validated"
        )

    def calculate(
        self,
        snoring: bool,
        tired: bool,
        observed_apnea: bool,
        high_blood_pressure: bool,
        bmi_over_35: bool,
        age_over_50: bool,
        neck_over_40cm: bool,
        male_gender: bool
    ) -> ScoreResult:
        """
        Calculate STOP-BANG Score.

        Args:
            snoring: Do you SNORE loudly?
            tired: Do you often feel TIRED, fatigued, or sleepy during daytime?
            observed_apnea: Has anyone OBSERVED you stop breathing during sleep?
            high_blood_pressure: Do you have or are you being treated for high blood PRESSURE?
            bmi_over_35: BMI > 35 kg/m²?
            age_over_50: Age > 50 years old?
            neck_over_40cm: Neck circumference > 40 cm (16 inches)?
            male_gender: Gender = Male?

        Returns:
            ScoreResult with OSA risk stratification
        """
        # Calculate score
        score = sum([
            snoring,
            tired,
            observed_apnea,
            high_blood_pressure,
            bmi_over_35,
            age_over_50,
            neck_over_40cm,
            male_gender
        ])

        # Check for high-risk BANG criteria
        bang_criteria_met = sum([bmi_over_35, neck_over_40cm, male_gender])
        stop_score = sum([snoring, tired, observed_apnea, high_blood_pressure])

        # Determine risk level with special high-risk criteria
        high_risk_by_criteria = (stop_score >= 2 and
                                 (male_gender or bmi_over_35 or neck_over_40cm))

        # Get interpretation
        interpretation = self._get_interpretation(score, high_risk_by_criteria)

        # Build criteria list
        criteria_present = []
        if snoring:
            criteria_present.append("S: Snoring")
        if tired:
            criteria_present.append("T: Tired")
        if observed_apnea:
            criteria_present.append("O: Observed apnea")
        if high_blood_pressure:
            criteria_present.append("P: High blood Pressure")
        if bmi_over_35:
            criteria_present.append("B: BMI > 35")
        if age_over_50:
            criteria_present.append("A: Age > 50")
        if neck_over_40cm:
            criteria_present.append("N: Neck > 40 cm")
        if male_gender:
            criteria_present.append("G: Male Gender")

        return ScoreResult(
            value=float(score),
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "snoring": snoring,
                "tired": tired,
                "observed_apnea": observed_apnea,
                "high_blood_pressure": high_blood_pressure,
                "bmi_over_35": bmi_over_35,
                "age_over_50": age_over_50,
                "neck_over_40cm": neck_over_40cm,
                "male_gender": male_gender
            },
            calculation_details={
                "score": score,
                "stop_score": stop_score,
                "bang_criteria_count": bang_criteria_met,
                "criteria_present": criteria_present,
                "high_risk_by_bang_criteria": high_risk_by_criteria
            },
            notes=self._get_notes(score, high_risk_by_criteria)
        )

    def _get_interpretation(self, score: int, high_risk_by_criteria: bool) -> Interpretation:
        """Get clinical interpretation based on score"""

        if score <= 2 and not high_risk_by_criteria:
            return Interpretation(
                summary="Low Risk for OSA",
                detail=f"STOP-BANG score {score}/8. Low probability of moderate-to-severe OSA.",
                severity=Severity.NORMAL,
                risk_level=RiskLevel.LOW,
                stage="Low Risk",
                stage_description="0-2 points without high-risk BANG criteria",
                recommendations=(
                    "Routine preoperative management",
                    "No specific OSA precautions required",
                    "Standard anesthetic plan appropriate",
                ),
                next_steps=(
                    "Proceed with standard perioperative care",
                    "No routine sleep study needed",
                )
            )
        elif score <= 4 and not high_risk_by_criteria:
            return Interpretation(
                summary="Intermediate Risk for OSA",
                detail=f"STOP-BANG score {score}/8. Moderate probability of OSA.",
                severity=Severity.MILD,
                risk_level=RiskLevel.INTERMEDIATE,
                stage="Intermediate Risk",
                stage_description="3-4 points",
                recommendations=(
                    "Consider OSA precautions perioperatively",
                    "Avoid excessive sedation/opioids",
                    "Consider CPAP evaluation if symptomatic",
                    "Extended PACU monitoring may be beneficial",
                ),
                next_steps=(
                    "Discuss OSA risks with patient",
                    "Consider sleep medicine referral if symptomatic",
                    "Plan for careful postoperative monitoring",
                )
            )
        else:
            # High risk (score ≥5 OR score ≥2 with BANG criteria)
            osa_probability = self._get_osa_probability(score)
            return Interpretation(
                summary=f"High Risk for OSA ({osa_probability}% probability of moderate-severe OSA)",
                detail=f"STOP-BANG score {score}/8. High probability of moderate-to-severe OSA. "
                       f"Perioperative precautions strongly recommended.",
                severity=Severity.MODERATE,
                risk_level=RiskLevel.HIGH,
                stage="High Risk",
                stage_description="≥5 points OR ≥2 with high-risk BANG criteria",
                recommendations=(
                    "Preoperative CPAP evaluation if not already on therapy",
                    "Consider formal polysomnography if time permits",
                    "OSA-specific anesthetic precautions essential",
                    "Minimize opioids - use multimodal analgesia",
                    "Avoid deep sedation; prefer regional anesthesia if possible",
                    "Plan for continuous SpO2 monitoring postoperatively",
                    "CPAP/BiPAP availability in PACU and on ward",
                    "Consider monitored bed or ICU for high-risk surgeries",
                ),
                warnings=(
                    "Increased risk of difficult airway",
                    "Higher risk of postoperative respiratory depression",
                    "May require overnight observation for outpatient procedures",
                ),
                next_steps=(
                    "Sleep medicine consultation if feasible",
                    "Ensure CPAP compliance if already diagnosed",
                    "Document OSA risk in anesthetic plan",
                    "Alert postoperative nursing staff",
                )
            )

    def _get_osa_probability(self, score: int) -> int:
        """Estimate probability of moderate-severe OSA based on score"""
        # Based on Chung et al. validation studies
        probability_map = {
            0: 10, 1: 15, 2: 25,
            3: 35, 4: 50,
            5: 60, 6: 70, 7: 80, 8: 90
        }
        return probability_map.get(score, 50)

    def _get_notes(self, score: int, high_risk: bool) -> list[str]:
        """Get clinical notes based on score"""
        notes = [
            "STOP-BANG validated in preoperative surgical patients",
            "Sensitivity increases with OSA severity (highest for severe OSA)",
        ]

        if score >= 3 or high_risk:
            notes.extend([
                "High-risk patients: consider CPAP trial preoperatively",
                "Outpatient surgery may require extended observation period",
                "Regional anesthesia preferred when feasible",
            ])

        if score >= 5:
            notes.extend([
                "Score ≥5: 60-70% probability of moderate-severe OSA (AHI ≥15)",
                "Consider formal sleep study if major surgery planned",
            ])

        return notes
