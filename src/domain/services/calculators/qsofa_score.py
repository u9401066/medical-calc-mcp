"""
qSOFA Score (Quick SOFA)

The qSOFA is a bedside prompt that may identify patients with suspected
infection who are at greater risk for a poor outcome outside the ICU.
It is NOT designed to be used as a diagnostic tool, but rather as a
screening tool to prompt clinicians to consider sepsis.

Reference (Sepsis-3):
    Singer M, Deutschman CS, Seymour CW, et al. The Third International Consensus 
    Definitions for Sepsis and Septic Shock (Sepsis-3). JAMA. 2016;315(8):801-810.
    DOI: 10.1001/jama.2016.0287
    PMID: 26903338

Reference (Validation):
    Seymour CW, Liu VX, Iwashyna TJ, et al. Assessment of Clinical Criteria for 
    Sepsis: For the Third International Consensus Definitions for Sepsis and 
    Septic Shock (Sepsis-3). JAMA. 2016;315(8):762-774.
    DOI: 10.1001/jama.2016.0288
    PMID: 26903335

Guideline Citation:
    Evans L, Rhodes A, Alhazzani W, et al. Surviving Sepsis Campaign: International 
    Guidelines for Management of Sepsis and Septic Shock 2021. Crit Care Med. 
    2021;49(11):e1063-e1143.
    DOI: 10.1097/CCM.0000000000005337
    PMID: 34605781

Note from SSC 2021 Guidelines:
    "We recommend against using qSOFA compared with SIRS, NEWS, or MEWS as a 
    single screening tool for sepsis or septic shock." (Strong recommendation)
    qSOFA should be used in combination with clinical judgment, not as a standalone tool.
"""

from ..base import BaseCalculator
from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.units import Unit
from ...value_objects.reference import Reference
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.tool_keys import (
    LowLevelKey,
    HighLevelKey,
    Specialty,
    ClinicalContext
)


class QsofaScoreCalculator(BaseCalculator):
    """
    qSOFA (Quick SOFA) Score Calculator
    
    The qSOFA is a simplified screening tool for identifying patients
    with suspected infection who are at greater risk for poor outcomes
    in out-of-hospital, emergency department, or general ward settings.
    
    Criteria (1 point each):
    - Respiratory rate ≥ 22/min
    - Altered mentation (GCS < 15)
    - Systolic blood pressure ≤ 100 mmHg
    
    qSOFA ≥ 2: Associated with poor outcome typical of sepsis
    
    Important: Per SSC 2021, qSOFA should NOT be used as a single screening
    tool. It should be used alongside clinical judgment and other assessment tools.
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="qsofa_score",
                name="qSOFA Score (Quick SOFA)",
                purpose="Bedside screening for patients at risk of poor outcomes from sepsis",
                input_params=["respiratory_rate", "systolic_bp", "altered_mentation"],
                output_type="qSOFA score (0-3) with risk assessment"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.CRITICAL_CARE,
                    Specialty.ANESTHESIOLOGY,
                ),
                conditions=(
                    "Sepsis",
                    "Infection",
                    "Suspected Sepsis",
                    "Fever",
                    "Altered Mental Status",
                    "Hypotension",
                ),
                clinical_contexts=(
                    ClinicalContext.SCREENING,
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.DISPOSITION,
                    ClinicalContext.SEVERITY_ASSESSMENT,
                ),
                clinical_questions=(
                    "Is this patient at risk for sepsis?",
                    "Should I escalate care for this infected patient?",
                    "Does this patient need ICU admission?",
                    "Is this infection severe?",
                ),
                icd10_codes=("A41", "R65.20", "R65.21"),
                keywords=(
                    "qSOFA", "quick SOFA", "sepsis screening", "sepsis",
                    "infection", "early warning", "bedside", "Sepsis-3",
                    "triage", "emergency", "ward",
                )
            ),
            references=(
                Reference(
                    citation="Singer M, Deutschman CS, Seymour CW, et al. The Third International "
                             "Consensus Definitions for Sepsis and Septic Shock (Sepsis-3). "
                             "JAMA. 2016;315(8):801-810.",
                    doi="10.1001/jama.2016.0287",
                    pmid="26903338",
                    year=2016
                ),
                Reference(
                    citation="Seymour CW, Liu VX, Iwashyna TJ, et al. Assessment of Clinical "
                             "Criteria for Sepsis: For the Third International Consensus "
                             "Definitions for Sepsis and Septic Shock (Sepsis-3). "
                             "JAMA. 2016;315(8):762-774.",
                    doi="10.1001/jama.2016.0288",
                    pmid="26903335",
                    year=2016
                ),
                Reference(
                    citation="Evans L, Rhodes A, Alhazzani W, et al. Surviving Sepsis Campaign: "
                             "International Guidelines for Management of Sepsis and Septic Shock 2021. "
                             "Crit Care Med. 2021;49(11):e1063-e1143.",
                    doi="10.1097/CCM.0000000000005337",
                    pmid="34605781",
                    year=2021
                ),
            ),
            version="1.0.0",
            validation_status="validated"
        )
    
    def calculate(
        self,
        respiratory_rate: int,
        systolic_bp: int,
        altered_mentation: bool = False,
        gcs_score: int = 15,
    ) -> ScoreResult:
        """
        Calculate qSOFA score.
        
        Args:
            respiratory_rate: Respiratory rate (breaths/min)
            systolic_bp: Systolic blood pressure (mmHg)
            altered_mentation: Whether patient has altered mental status
                               (True if GCS < 15 or any acute change in mental status)
            gcs_score: Glasgow Coma Scale score (3-15), used if altered_mentation not specified
            
        Returns:
            ScoreResult with qSOFA score and recommendations
        """
        # Validate inputs
        if not 0 <= respiratory_rate <= 100:
            raise ValueError("Respiratory rate must be between 0 and 100")
        if not 0 <= systolic_bp <= 300:
            raise ValueError("Systolic BP must be between 0 and 300 mmHg")
        if not 3 <= gcs_score <= 15:
            raise ValueError("GCS must be between 3 and 15")
        
        # Calculate individual criteria
        rr_criteria = respiratory_rate >= 22
        sbp_criteria = systolic_bp <= 100
        
        # Altered mentation: use explicit flag or infer from GCS
        ams_criteria = altered_mentation or gcs_score < 15
        
        # Calculate total score
        score = int(rr_criteria) + int(sbp_criteria) + int(ams_criteria)
        
        # Get interpretation
        interpretation = self._get_interpretation(
            score, rr_criteria, sbp_criteria, ams_criteria
        )
        
        return ScoreResult(
            value=score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "respiratory_rate": respiratory_rate,
                "systolic_bp": systolic_bp,
                "altered_mentation": altered_mentation,
                "gcs_score": gcs_score,
            },
            calculation_details={
                "respiratory_rate_criteria": f"≥22/min: {'Met' if rr_criteria else 'Not met'} ({respiratory_rate}/min)",
                "systolic_bp_criteria": f"≤100 mmHg: {'Met' if sbp_criteria else 'Not met'} ({systolic_bp} mmHg)",
                "altered_mentation_criteria": f"GCS <15: {'Met' if ams_criteria else 'Not met'} (GCS {gcs_score})",
                "total_score": score,
            },
            formula_used="qSOFA = (RR ≥22) + (SBP ≤100) + (Altered mentation)"
        )
    
    def _get_interpretation(
        self, 
        score: int,
        rr_met: bool,
        sbp_met: bool,
        ams_met: bool
    ) -> Interpretation:
        """Get interpretation based on qSOFA score"""
        
        criteria_met = []
        if rr_met:
            criteria_met.append("Respiratory rate ≥22/min")
        if sbp_met:
            criteria_met.append("Systolic BP ≤100 mmHg")
        if ams_met:
            criteria_met.append("Altered mentation")
        
        criteria_text = ", ".join(criteria_met) if criteria_met else "None"
        
        if score >= 2:
            return Interpretation(
                summary=f"qSOFA {score}/3: Positive - High risk for poor outcome",
                detail=f"Criteria met: {criteria_text}. "
                       f"qSOFA ≥2 in suspected infection is associated with increased "
                       f"mortality. However, per SSC 2021 guidelines, qSOFA should NOT be "
                       f"used as a single screening tool. Further evaluation with full SOFA "
                       f"and clinical assessment is recommended.",
                severity=Severity.MODERATE if score == 2 else Severity.SEVERE,
                stage=f"qSOFA {score}",
                stage_description="Positive screen for sepsis risk",
                recommendations=(
                    "Do not use qSOFA as sole screening tool (SSC 2021 recommendation)",
                    "Calculate full SOFA score if in ICU",
                    "Consider NEWS or MEWS as complementary tools",
                    "Initiate Hour-1 Bundle if sepsis is suspected",
                    "Consider ICU admission or close monitoring",
                ),
                warnings=(
                    "qSOFA ≥2 is associated with 3-14x higher mortality",
                    "May indicate need for ICU-level care",
                    "Low sensitivity means qSOFA <2 does NOT rule out sepsis",
                ),
                next_steps=(
                    "Measure serum lactate",
                    "Obtain blood cultures",
                    "Administer antibiotics within 1 hour if sepsis suspected",
                    "Begin fluid resuscitation (30 mL/kg crystalloid)",
                    "Reassess frequently",
                )
            )
        elif score == 1:
            return Interpretation(
                summary=f"qSOFA {score}/3: Borderline - Monitor closely",
                detail=f"Criteria met: {criteria_text}. "
                       f"A single qSOFA criterion does not meet threshold, but patient "
                       f"should be monitored for clinical deterioration. Consider other "
                       f"screening tools (NEWS, MEWS) and clinical judgment.",
                severity=Severity.MILD,
                stage=f"qSOFA {score}",
                stage_description="Below threshold but abnormal",
                recommendations=(
                    "Continue close monitoring",
                    "Consider using NEWS or MEWS for additional assessment",
                    "Reassess qSOFA if clinical condition changes",
                    "Maintain high clinical suspicion for infection",
                ),
                warnings=(
                    "Single criterion abnormal - watch for deterioration",
                ),
                next_steps=(
                    "Repeat vital signs in 1-2 hours",
                    "Consider lactate if infection suspected",
                    "Document clinical trajectory",
                )
            )
        else:  # score == 0
            return Interpretation(
                summary=f"qSOFA {score}/3: Negative - Low risk by this score",
                detail="No qSOFA criteria met. Low risk for poor outcome by this score. "
                       "However, qSOFA has LOW SENSITIVITY and should not be used to rule "
                       "out sepsis. Clinical judgment and other assessment tools remain essential.",
                severity=Severity.NORMAL,
                stage=f"qSOFA {score}",
                stage_description="No criteria met",
                recommendations=(
                    "qSOFA is NOT a rule-out tool for sepsis",
                    "Maintain clinical vigilance if infection suspected",
                    "Consider NEWS or MEWS as complementary assessment",
                    "Re-evaluate if clinical condition changes",
                ),
                warnings=(
                    "Low qSOFA does NOT rule out sepsis (low sensitivity)",
                ),
                next_steps=(
                    "Continue routine monitoring",
                    "Reassess if clinical concern persists",
                )
            )
