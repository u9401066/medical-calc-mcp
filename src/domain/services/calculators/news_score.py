"""
NEWS Score (National Early Warning Score)

The National Early Warning Score (NEWS) is a standardized assessment tool
developed by the Royal College of Physicians to improve detection and response
to clinical deterioration in adult patients. NEWS2 is the updated version.

NEWS is recommended by the SSC 2021 guidelines alongside other tools for
sepsis screening, though NOT as a single standalone tool.

Reference (NEWS):
    Royal College of Physicians. National Early Warning Score (NEWS):
    Standardising the assessment of acute-illness severity in the NHS.
    Report of a working party. London: RCP, 2012.

Reference (NEWS2):
    Royal College of Physicians. National Early Warning Score (NEWS) 2:
    Standardising the assessment of acute-illness severity in the NHS.
    Updated report of a working party. London: RCP, 2017.

Validation Study:
    Smith GB, Prytherch DR, Meredith P, et al. The ability of the National
    Early Warning Score (NEWS) to discriminate patients at risk of early
    cardiac arrest, unanticipated intensive care unit admission, and death.
    Resuscitation. 2013;84(4):465-470.
    DOI: 10.1016/j.resuscitation.2012.12.016
    PMID: 23295778
"""

from typing import Literal

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class NewsScoreCalculator(BaseCalculator):
    """
    NEWS2 (National Early Warning Score 2) Calculator

    NEWS2 is a scoring system used to assess clinical deterioration in
    adult patients. It uses 7 physiological parameters plus an adjustment
    for supplemental oxygen.

    Parameters (each scored 0-3):
    - Respiratory rate
    - Oxygen saturation (Scale 1 or Scale 2)
    - Supplemental oxygen use
    - Temperature
    - Systolic blood pressure
    - Heart rate
    - Level of consciousness (AVPU)

    Scale 2 (SpO2 Scale 2) is used for patients with hypercapnic respiratory
    failure who have a prescribed oxygen saturation target of 88-92%.
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="news2_score",
                name="NEWS2 (National Early Warning Score 2)",
                purpose="Detect clinical deterioration and trigger appropriate clinical response",
                input_params=[
                    "respiratory_rate", "spo2", "on_supplemental_o2",
                    "temperature", "systolic_bp", "heart_rate", "consciousness"
                ],
                output_type="NEWS2 score (0-20) with clinical response recommendations"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.CRITICAL_CARE,
                    Specialty.ANESTHESIOLOGY,
                ),
                conditions=(
                    "Clinical Deterioration",
                    "Sepsis",
                    "Acute Illness",
                    "Respiratory Failure",
                    "Shock",
                    "Infection",
                ),
                clinical_contexts=(
                    ClinicalContext.SCREENING,
                    ClinicalContext.MONITORING,
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.DISPOSITION,
                ),
                clinical_questions=(
                    "Is this patient deteriorating?",
                    "Does this patient need escalation of care?",
                    "How frequently should I monitor this patient?",
                    "Should this patient be transferred to higher level of care?",
                    "Is this patient at risk for cardiac arrest?",
                ),
                icd10_codes=("R65.10", "R65.11", "R65.20", "R65.21"),
                keywords=(
                    "NEWS", "NEWS2", "early warning score", "deterioration",
                    "track and trigger", "vital signs", "monitoring",
                    "clinical response", "escalation", "sepsis screening",
                )
            ),
            references=(
                Reference(
                    citation="Royal College of Physicians. National Early Warning Score (NEWS) 2: "
                             "Standardising the assessment of acute-illness severity in the NHS. "
                             "Updated report of a working party. London: RCP, 2017.",
                    doi=None,
                    pmid=None,
                    year=2017
                ),
                Reference(
                    citation="Smith GB, Prytherch DR, Meredith P, et al. The ability of the National "
                             "Early Warning Score (NEWS) to discriminate patients at risk of early "
                             "cardiac arrest, unanticipated intensive care unit admission, and death. "
                             "Resuscitation. 2013;84(4):465-470.",
                    doi="10.1016/j.resuscitation.2012.12.016",
                    pmid="23295778",
                    year=2013
                ),
            ),
            version="2.0.0",
            validation_status="validated"
        )

    def calculate(
        self,
        respiratory_rate: int,
        spo2: int,
        on_supplemental_o2: bool,
        temperature: float,
        systolic_bp: int,
        heart_rate: int,
        consciousness: Literal["A", "V", "P", "U", "C"] = "A",
        use_scale_2: bool = False,
    ) -> ScoreResult:
        """
        Calculate NEWS2 score.

        Args:
            respiratory_rate: Respiratory rate (breaths/min)
            spo2: Oxygen saturation (%)
            on_supplemental_o2: Whether patient is receiving supplemental oxygen
            temperature: Temperature (°C)
            systolic_bp: Systolic blood pressure (mmHg)
            heart_rate: Heart rate (beats/min)
            consciousness: AVPU scale:
                - "A": Alert
                - "V": Responds to Voice
                - "P": Responds to Pain
                - "U": Unresponsive
                - "C": Confusion (new in NEWS2)
            use_scale_2: Use SpO2 Scale 2 for patients with hypercapnic
                        respiratory failure (target SpO2 88-92%)

        Returns:
            ScoreResult with NEWS2 score and clinical response recommendations
        """
        # Validate inputs
        if not 0 <= respiratory_rate <= 100:
            raise ValueError("Respiratory rate must be between 0 and 100")
        if not 0 <= spo2 <= 100:
            raise ValueError("SpO2 must be between 0 and 100")
        if not 25.0 <= temperature <= 45.0:
            raise ValueError("Temperature must be between 25 and 45°C")
        if not 0 <= systolic_bp <= 300:
            raise ValueError("Systolic BP must be between 0 and 300 mmHg")
        if not 0 <= heart_rate <= 300:
            raise ValueError("Heart rate must be between 0 and 300 bpm")
        if consciousness not in ("A", "V", "P", "U", "C"):
            raise ValueError("Consciousness must be one of: A, V, P, U, C")

        # Calculate individual scores
        rr_score = self._respiratory_rate_score(respiratory_rate)
        spo2_score = self._spo2_score(spo2, use_scale_2)
        air_score = 2 if on_supplemental_o2 else 0
        temp_score = self._temperature_score(temperature)
        sbp_score = self._systolic_bp_score(systolic_bp)
        hr_score = self._heart_rate_score(heart_rate)
        avpu_score = self._consciousness_score(consciousness)

        # Total score
        total_score = rr_score + spo2_score + air_score + temp_score + sbp_score + hr_score + avpu_score

        # Check for "3 in one" parameter (any single parameter with score of 3)
        extreme_single_parameter = max(rr_score, spo2_score, temp_score, sbp_score, hr_score, avpu_score) >= 3

        # Get interpretation
        interpretation = self._get_interpretation(total_score, extreme_single_parameter)

        return ScoreResult(
            value=total_score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "respiratory_rate": respiratory_rate,
                "spo2": spo2,
                "on_supplemental_o2": on_supplemental_o2,
                "temperature": temperature,
                "systolic_bp": systolic_bp,
                "heart_rate": heart_rate,
                "consciousness": consciousness,
                "use_scale_2": use_scale_2,
            },
            calculation_details={
                "respiratory_rate": {"value": respiratory_rate, "score": rr_score},
                "spo2": {"value": spo2, "score": spo2_score, "scale": 2 if use_scale_2 else 1},
                "supplemental_o2": {"value": on_supplemental_o2, "score": air_score},
                "temperature": {"value": temperature, "score": temp_score},
                "systolic_bp": {"value": systolic_bp, "score": sbp_score},
                "heart_rate": {"value": heart_rate, "score": hr_score},
                "consciousness": {"value": consciousness, "score": avpu_score},
                "total": total_score,
                "extreme_single_parameter": extreme_single_parameter,
            },
            formula_used="NEWS2 = RR + SpO2 + Air + Temp + SBP + HR + AVPU"
        )

    def _respiratory_rate_score(self, rr: int) -> int:
        if rr <= 8:
            return 3
        elif rr <= 11:
            return 1
        elif rr <= 20:
            return 0
        elif rr <= 24:
            return 2
        else:  # >= 25
            return 3

    def _spo2_score(self, spo2: int, use_scale_2: bool) -> int:
        if use_scale_2:
            # Scale 2 for hypercapnic respiratory failure
            if spo2 <= 83:
                return 3
            elif spo2 <= 85:
                return 2
            elif spo2 <= 87:
                return 1
            elif spo2 <= 92:
                return 0  # Target range 88-92%
            elif spo2 <= 94:
                return 1
            elif spo2 <= 96:
                return 2
            else:  # >= 97
                return 3
        else:
            # Scale 1 (default)
            if spo2 <= 91:
                return 3
            elif spo2 <= 93:
                return 2
            elif spo2 <= 95:
                return 1
            else:  # >= 96
                return 0

    def _temperature_score(self, temp: float) -> int:
        if temp <= 35.0:
            return 3
        elif temp <= 36.0:
            return 1
        elif temp <= 38.0:
            return 0
        elif temp <= 39.0:
            return 1
        else:  # >= 39.1
            return 2

    def _systolic_bp_score(self, sbp: int) -> int:
        if sbp <= 90:
            return 3
        elif sbp <= 100:
            return 2
        elif sbp <= 110:
            return 1
        elif sbp <= 219:
            return 0
        else:  # >= 220
            return 3

    def _heart_rate_score(self, hr: int) -> int:
        if hr <= 40:
            return 3
        elif hr <= 50:
            return 1
        elif hr <= 90:
            return 0
        elif hr <= 110:
            return 1
        elif hr <= 130:
            return 2
        else:  # >= 131
            return 3

    def _consciousness_score(self, avpu: str) -> int:
        if avpu == "A":
            return 0
        else:  # V, P, U, or C (Confusion)
            return 3

    def _get_interpretation(self, score: int, extreme_single: bool) -> Interpretation:
        """Get interpretation based on NEWS2 score"""

        if score == 0:
            return Interpretation(
                summary="NEWS2 0: Low clinical risk",
                detail="All vital signs are within normal range. Continue routine care.",
                severity=Severity.NORMAL,
                stage="Low",
                stage_description="Low clinical risk",
                recommendations=(
                    "Continue routine NEWS monitoring",
                    "Minimum 12-hourly monitoring",
                ),
                next_steps=(
                    "Document observations",
                    "Continue current care plan",
                )
            )
        elif score <= 4:
            severity = Severity.MODERATE if extreme_single else Severity.MILD
            return Interpretation(
                summary=f"NEWS2 {score}: {'Low-Medium' if not extreme_single else 'Medium'} clinical risk",
                detail=f"Score indicates {'mild' if not extreme_single else 'concerning'} deviation from normal. "
                       f"{'A single parameter is at extreme value, requiring urgent review.' if extreme_single else ''}",
                severity=severity,
                stage="Low-Medium" if not extreme_single else "Medium",
                stage_description="Low-medium clinical risk" if not extreme_single else "Single parameter extreme",
                recommendations=(
                    "Inform registered nurse who must assess patient",
                    "Increase monitoring frequency to minimum 4-6 hourly",
                    "Urgent review if single extreme parameter" if extreme_single else "Consider if escalation needed",
                ),
                warnings=(
                    "Single extreme parameter detected - requires urgent review",
                ) if extreme_single else (),
                next_steps=(
                    "Registered nurse to decide if escalation of care needed",
                    "Consider ward-based urgent response if extreme single parameter",
                )
            )
        elif score <= 6:
            return Interpretation(
                summary=f"NEWS2 {score}: Medium clinical risk",
                detail="Score indicates significant physiological abnormality. Urgent response required.",
                severity=Severity.MODERATE,
                stage="Medium",
                stage_description="Medium clinical risk - urgent response",
                recommendations=(
                    "Urgent review by clinician with core competencies in acute illness",
                    "Consider if patient needs higher level of care",
                    "Continuous monitoring",
                    "Clinician to decide if escalation of care needed",
                ),
                warnings=(
                    "Patient at risk of deterioration",
                ),
                next_steps=(
                    "Urgent clinical review within 30 minutes",
                    "Clinician to assess and determine escalation",
                    "Consider sepsis if infection suspected",
                )
            )
        else:  # score >= 7
            return Interpretation(
                summary=f"NEWS2 {score}: High clinical risk - EMERGENCY",
                detail="Score indicates critical physiological abnormality. Emergency response required.",
                severity=Severity.CRITICAL,
                stage="High",
                stage_description="High clinical risk - emergency response",
                recommendations=(
                    "Emergency response - immediate review by critical care team",
                    "Consider transfer to higher-dependency care area",
                    "Continuous monitoring of vital signs",
                    "Activate critical care outreach or equivalent",
                ),
                warnings=(
                    "High mortality risk without intervention",
                    "Patient may require ICU admission",
                    "Consider sepsis, cardiac arrest risk",
                ),
                next_steps=(
                    "Immediate emergency assessment",
                    "Alert critical care/outreach team",
                    "Prepare for possible resuscitation",
                    "Consider ICU transfer",
                )
            )
