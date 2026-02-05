"""
Systemic Inflammatory Response Syndrome (SIRS) Criteria Calculator

Identifies patients with systemic inflammatory response syndrome based on
physiological parameters. ≥2 criteria indicates SIRS.

Original Reference:
    Bone RC, Balk RA, Cerra FB, et al. Definitions for sepsis and organ failure
    and guidelines for the use of innovative therapies in sepsis.
    The ACCP/SCCM Consensus Conference Committee. American College of Chest
    Physicians/Society of Critical Care Medicine.
    Chest. 1992;101(6):1644-1655.
    doi:10.1378/chest.101.6.1644. PMID: 1303622.

Update Reference (Sepsis-3):
    Singer M, Deutschman CS, Seymour CW, et al. The Third International Consensus
    Definitions for Sepsis and Septic Shock (Sepsis-3).
    JAMA. 2016;315(8):801-810.
    doi:10.1001/jama.2016.0287. PMID: 26903338.

Note: SIRS criteria were part of Sepsis-1 and Sepsis-2 definitions.
      Sepsis-3 (2016) now uses SOFA/qSOFA instead, but SIRS remains widely used.
"""

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, RiskLevel, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import (
    ClinicalContext,
    HighLevelKey,
    LowLevelKey,
    Specialty,
)
from ...value_objects.units import Unit
from ..base import BaseCalculator


class SIRSCriteriaCalculator(BaseCalculator):
    """
    Systemic Inflammatory Response Syndrome (SIRS) Criteria Calculator

    SIRS is defined by the presence of ≥2 of the following criteria:

    1. Temperature: >38°C (100.4°F) or <36°C (96.8°F)
    2. Heart rate: >90 beats/minute
    3. Respiratory rate: >20 breaths/minute OR PaCO2 <32 mmHg
    4. White blood cell count: >12,000/mm³ OR <4,000/mm³ OR >10% immature bands

    Clinical Context:
    - SIRS ≥2 + suspected infection = Sepsis (per Sepsis-1/2 definitions)
    - Now largely replaced by Sepsis-3 criteria (SOFA/qSOFA)
    - Still useful for identifying inflammatory states

    Limitations:
    - Low specificity for infection
    - Many non-infectious causes (trauma, surgery, burns, pancreatitis)
    - Does not predict mortality as well as SOFA
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="sirs_criteria",
                name="SIRS Criteria (Systemic Inflammatory Response Syndrome)",
                purpose="Identify systemic inflammatory response syndrome",
                input_params=[
                    "temperature",
                    "heart_rate",
                    "respiratory_rate",
                    "paco2",
                    "wbc",
                    "bands_percent",
                ],
                output_type="SIRS criteria count (0-4) with interpretation",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.CRITICAL_CARE,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.INFECTIOUS_DISEASE,
                    Specialty.SURGERY,
                ),
                conditions=(
                    "systemic inflammatory response syndrome",
                    "SIRS",
                    "sepsis",
                    "infection",
                    "inflammation",
                    "fever",
                    "leukocytosis",
                    "leukopenia",
                    "tachycardia",
                    "tachypnea",
                ),
                clinical_contexts=(
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.SCREENING,
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.TRIAGE,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "Does this patient have SIRS?",
                    "Is this patient at risk for sepsis?",
                    "How many SIRS criteria are met?",
                    "Should I be concerned about systemic inflammation?",
                    "Is this fever infectious or non-infectious?",
                ),
                icd10_codes=(
                    "R65.10",  # SIRS of non-infectious origin without organ dysfunction
                    "R65.11",  # SIRS of non-infectious origin with organ dysfunction
                    "R65.20",  # Severe sepsis without septic shock
                    "R65.21",  # Severe sepsis with septic shock
                    "A41.9",  # Sepsis, unspecified organism
                ),
                keywords=(
                    "SIRS",
                    "systemic inflammatory response",
                    "sepsis",
                    "infection",
                    "fever",
                    "tachycardia",
                    "tachypnea",
                    "leukocytosis",
                    "leukopenia",
                    "bands",
                    "left shift",
                    "inflammation",
                ),
            ),
            references=(
                Reference(
                    citation="Bone RC, Balk RA, Cerra FB, et al. Definitions for sepsis and "
                    "organ failure and guidelines for the use of innovative therapies in sepsis. "
                    "The ACCP/SCCM Consensus Conference Committee. "
                    "Chest. 1992;101(6):1644-1655.",
                    doi="10.1378/chest.101.6.1644",
                    pmid="1303622",
                    year=1992,
                ),
                Reference(
                    citation="Singer M, Deutschman CS, Seymour CW, et al. The Third International "
                    "Consensus Definitions for Sepsis and Septic Shock (Sepsis-3). "
                    "JAMA. 2016;315(8):801-810.",
                    doi="10.1001/jama.2016.0287",
                    pmid="26903338",
                    year=2016,
                ),
            ),
            version="1992 (ACCP/SCCM Consensus)",
            validation_status="validated",
        )

    def calculate(
        self,
        temperature: float | None = None,
        heart_rate: int | None = None,
        respiratory_rate: int | None = None,
        paco2: float | None = None,
        wbc: float | None = None,
        bands_percent: float | None = None,
    ) -> ScoreResult:
        """
        Calculate SIRS criteria count.

        Args:
            temperature: Body temperature in °C (normal 36-38°C)
                        SIRS criterion: >38°C or <36°C
            heart_rate: Heart rate in beats per minute (normal 60-100)
                       SIRS criterion: >90 bpm
            respiratory_rate: Respiratory rate in breaths per minute (normal 12-20)
                             SIRS criterion: >20/min
            paco2: Arterial CO2 partial pressure in mmHg (normal 35-45)
                   SIRS criterion: <32 mmHg (if respiratory_rate not provided)
            wbc: White blood cell count in thousands/mm³ (normal 4-12)
                 SIRS criterion: >12 or <4 × 10³/mm³
            bands_percent: Immature neutrophils (bands) as % of WBC (normal <10%)
                          SIRS criterion: >10% immature (band) forms

        Returns:
            ScoreResult with SIRS criteria count (0-4) and interpretation

        Notes:
            - At least some parameters must be provided
            - Respiratory criterion: either RR >20 OR PaCO2 <32 (one criterion)
            - WBC criterion: either WBC abnormal OR bands >10% (one criterion)
            - ≥2 criteria = SIRS positive
        """
        criteria_met: list[str] = []
        criteria_details: dict[str, str] = {}

        # Temperature criterion: >38°C or <36°C
        if temperature is not None:
            if temperature > 38 or temperature < 36:
                criteria_met.append("Temperature")
                if temperature > 38:
                    criteria_details["Temperature"] = f"{temperature}°C (>38°C)"
                else:
                    criteria_details["Temperature"] = f"{temperature}°C (<36°C)"
            else:
                criteria_details["Temperature"] = f"{temperature}°C (normal)"

        # Heart rate criterion: >90 bpm
        if heart_rate is not None:
            if heart_rate > 90:
                criteria_met.append("Heart rate")
                criteria_details["Heart rate"] = f"{heart_rate} bpm (>90)"
            else:
                criteria_details["Heart rate"] = f"{heart_rate} bpm (normal)"

        # Respiratory criterion: RR >20 OR PaCO2 <32 (counts as one criterion)
        respiratory_met = False
        if respiratory_rate is not None:
            if respiratory_rate > 20:
                respiratory_met = True
                criteria_details["Respiratory rate"] = f"{respiratory_rate}/min (>20)"
            else:
                criteria_details["Respiratory rate"] = f"{respiratory_rate}/min (normal)"

        if paco2 is not None:
            if paco2 < 32:
                if not respiratory_met:  # Only add if not already met by RR
                    respiratory_met = True
                criteria_details["PaCO2"] = f"{paco2} mmHg (<32)"
            else:
                criteria_details["PaCO2"] = f"{paco2} mmHg (normal)"

        if respiratory_met:
            criteria_met.append("Respiratory")

        # WBC criterion: >12,000 OR <4,000 OR >10% bands (counts as one criterion)
        wbc_met = False
        if wbc is not None:
            if wbc > 12 or wbc < 4:
                wbc_met = True
                if wbc > 12:
                    criteria_details["WBC"] = f"{wbc}×10³/mm³ (>12)"
                else:
                    criteria_details["WBC"] = f"{wbc}×10³/mm³ (<4)"
            else:
                criteria_details["WBC"] = f"{wbc}×10³/mm³ (normal)"

        if bands_percent is not None:
            if bands_percent > 10:
                if not wbc_met:  # Only add if not already met by WBC
                    wbc_met = True
                criteria_details["Bands"] = f"{bands_percent}% (>10%)"
            else:
                criteria_details["Bands"] = f"{bands_percent}% (normal)"

        if wbc_met:
            criteria_met.append("WBC/Bands")

        # Calculate score
        score = len(criteria_met)

        # Generate interpretation
        interpretation = self._interpret_score(score, criteria_met)

        # Build calculation details
        calculation_details = {
            "criteria_met_count": score,
            "criteria_met": criteria_met,
            "parameter_details": criteria_details,
            "sirs_positive": score >= 2,
        }

        return ScoreResult(
            tool_name=self.low_level_key.name,
            tool_id=self.low_level_key.tool_id,
            value=score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            calculation_details=calculation_details,
            references=list(self.references),
            formula_used="SIRS positive if ≥2 of 4 criteria met",
        )

    def _interpret_score(
        self, score: int, criteria_met: list[str]
    ) -> Interpretation:
        """Generate clinical interpretation based on SIRS criteria count."""

        criteria_str = ", ".join(criteria_met) if criteria_met else "None"

        if score == 0:
            return Interpretation(
                summary="SIRS Negative: 0/4 criteria met",
                detail="No SIRS criteria are met. The patient does not have systemic "
                "inflammatory response syndrome based on these parameters. "
                "Continue monitoring if clinical concern persists.",
                severity=Severity.NORMAL,
                risk_level=RiskLevel.VERY_LOW,
                stage="0/4 criteria",
                stage_description="No SIRS",
                recommendations=(
                    "Continue routine monitoring",
                    "Reassess if clinical status changes",
                    "SIRS alone does not rule out infection",
                ),
                next_steps=(
                    "If infection suspected, obtain cultures and imaging",
                    "Consider other causes of symptoms",
                ),
            )
        elif score == 1:
            return Interpretation(
                summary=f"SIRS Negative: 1/4 criteria met ({criteria_str})",
                detail=f"Only 1 SIRS criterion is met: {criteria_str}. "
                "This does not meet SIRS definition (≥2 criteria required). "
                "However, close monitoring is recommended if infection is suspected.",
                severity=Severity.MILD,
                risk_level=RiskLevel.LOW,
                stage="1/4 criteria",
                stage_description="Partial SIRS (not met)",
                recommendations=(
                    "Monitor closely for progression",
                    "Evaluate for underlying cause",
                    "Repeat assessment in 4-6 hours if concerned",
                ),
                warnings=(
                    "One criterion met - patient may be at early stage",
                    "Clinical judgment should guide management",
                ),
                next_steps=(
                    "Identify and address the abnormal parameter",
                    "Consider infection workup if clinically indicated",
                ),
            )
        elif score == 2:
            return Interpretation(
                summary=f"SIRS Positive: 2/4 criteria met ({criteria_str})",
                detail=f"SIRS is present with 2 criteria met: {criteria_str}. "
                "If infection is suspected, this meets Sepsis-1/2 criteria for sepsis. "
                "Note: Sepsis-3 criteria (SOFA/qSOFA) are now preferred.",
                severity=Severity.MODERATE,
                risk_level=RiskLevel.INTERMEDIATE,
                stage="2/4 criteria",
                stage_description="SIRS Present",
                recommendations=(
                    "Evaluate for source of infection",
                    "Obtain blood cultures before antibiotics if possible",
                    "Consider early antibiotics if sepsis suspected",
                    "Assess for organ dysfunction (check SOFA score)",
                    "IV fluid resuscitation if hypotensive",
                ),
                warnings=(
                    "SIRS + suspected infection = Sepsis (Sepsis-1/2)",
                    "Consider Sepsis-3 criteria (SOFA/qSOFA) for severity assessment",
                ),
                next_steps=(
                    "Calculate SOFA or qSOFA score",
                    "Obtain lactate level",
                    "Start sepsis workup if infection suspected",
                ),
            )
        elif score == 3:
            return Interpretation(
                summary=f"SIRS Positive: 3/4 criteria met ({criteria_str})",
                detail=f"SIRS is present with 3 criteria met: {criteria_str}. "
                "This indicates significant systemic inflammatory response. "
                "Urgent evaluation for infection and organ dysfunction is needed.",
                severity=Severity.SEVERE,
                risk_level=RiskLevel.HIGH,
                stage="3/4 criteria",
                stage_description="SIRS Present (significant)",
                recommendations=(
                    "Urgent evaluation for infection source",
                    "Obtain cultures (blood, urine, sputum as indicated)",
                    "Start empiric antibiotics promptly",
                    "Aggressive IV fluid resuscitation",
                    "Monitor for organ dysfunction",
                    "Consider ICU admission",
                ),
                warnings=(
                    "High likelihood of serious infection or inflammation",
                    "Risk of progression to severe sepsis/septic shock",
                    "Early goal-directed therapy may improve outcomes",
                ),
                next_steps=(
                    "Calculate SOFA score for organ dysfunction",
                    "Obtain lactate - if >2 mmol/L, indicates severe sepsis",
                    "ICU consultation if hemodynamically unstable",
                ),
            )
        else:  # score == 4
            return Interpretation(
                summary=f"SIRS Positive: 4/4 criteria met ({criteria_str})",
                detail=f"All 4 SIRS criteria are met: {criteria_str}. "
                "This indicates severe systemic inflammatory response. "
                "Urgent and aggressive management is required.",
                severity=Severity.CRITICAL,
                risk_level=RiskLevel.VERY_HIGH,
                stage="4/4 criteria",
                stage_description="SIRS Present (all criteria)",
                recommendations=(
                    "Immediate aggressive resuscitation",
                    "Obtain cultures and start broad-spectrum antibiotics immediately",
                    "IV fluid bolus (30 mL/kg crystalloid)",
                    "Vasopressors if MAP <65 despite fluids",
                    "ICU admission strongly recommended",
                    "Continuous monitoring",
                ),
                warnings=(
                    "All SIRS criteria met - high severity",
                    "High risk of septic shock and multi-organ failure",
                    "Mortality increases with delayed treatment",
                    "Time to antibiotics is critical",
                ),
                next_steps=(
                    "Activate sepsis protocol if available",
                    "Source control (drain abscess, remove infected device)",
                    "Monitor lactate clearance",
                    "Frequent reassessment of response to therapy",
                ),
            )
