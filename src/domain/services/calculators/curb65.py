"""
CURB-65 Score Calculator

Predicts 30-day mortality risk in community-acquired pneumonia (CAP).
Used for disposition decisions: outpatient vs inpatient vs ICU.

Original Reference:
    Lim WS, van der Eerden MM, Laing R, et al. Defining community acquired
    pneumonia severity on presentation to hospital: an international
    derivation and validation study. Thorax. 2003;58(5):377-382.
    doi:10.1136/thorax.58.5.377. PMID: 12728155.
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


class Curb65Calculator(BaseCalculator):
    """
    CURB-65 Score for Pneumonia Severity

    Scoring criteria (1 point each):
    - Confusion (new disorientation in person, place, or time)
    - Urea >7 mmol/L (or BUN >19 mg/dL)
    - Respiratory rate ≥30/min
    - Blood pressure (SBP <90 mmHg or DBP ≤60 mmHg)
    - Age ≥65 years

    Risk stratification:
    - 0-1: Low risk (0.6-2.7% mortality) → Outpatient
    - 2: Moderate risk (6.8% mortality) → Consider admission
    - 3-5: High risk (14-57% mortality) → Inpatient/ICU
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="curb65",
                name="CURB-65 Score",
                purpose="Predict 30-day mortality in community-acquired pneumonia for disposition decisions",
                input_params=[
                    "confusion",
                    "bun_gt_19_or_urea_gt_7",
                    "respiratory_rate_gte_30",
                    "sbp_lt_90_or_dbp_lte_60",
                    "age_gte_65",
                ],
                output_type="Score 0-5 with mortality risk and disposition recommendation"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.PULMONOLOGY,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.INFECTIOUS_DISEASE,
                ),
                conditions=(
                    "community-acquired pneumonia",
                    "CAP",
                    "pneumonia",
                    "respiratory infection",
                    "lower respiratory tract infection",
                    "LRTI",
                ),
                clinical_contexts=(
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.DISPOSITION,
                    ClinicalContext.RISK_STRATIFICATION,
                ),
                clinical_questions=(
                    "Should this pneumonia patient be admitted?",
                    "What is the mortality risk for this CAP patient?",
                    "Does this patient need ICU care for pneumonia?",
                    "Can this pneumonia patient be treated as outpatient?",
                    "How severe is this patient's pneumonia?",
                ),
                icd10_codes=(
                    "J18",  # Pneumonia, unspecified organism
                    "J18.9",  # Pneumonia, unspecified
                    "J15",  # Bacterial pneumonia, not elsewhere classified
                    "J13",  # Pneumonia due to Streptococcus pneumoniae
                ),
                keywords=(
                    "CURB-65",
                    "CURB65",
                    "pneumonia severity",
                    "CAP score",
                    "pneumonia mortality",
                    "respiratory infection severity",
                    "admission decision pneumonia",
                )
            ),
            references=(
                Reference(
                    citation="Lim WS, van der Eerden MM, Laing R, et al. Defining community "
                             "acquired pneumonia severity on presentation to hospital: an "
                             "international derivation and validation study. Thorax. "
                             "2003;58(5):377-382.",
                    doi="10.1136/thorax.58.5.377",
                    pmid="12728155",
                    year=2003,
                ),
                Reference(
                    citation="Mandell LA, Wunderink RG, Anzueto A, et al. Infectious Diseases "
                             "Society of America/American Thoracic Society consensus guidelines "
                             "on the management of community-acquired pneumonia in adults. "
                             "Clin Infect Dis. 2007;44 Suppl 2:S27-72.",
                    doi="10.1086/511159",
                    pmid="17278083",
                    year=2007,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        confusion: bool,
        bun_gt_19_or_urea_gt_7: bool,
        respiratory_rate_gte_30: bool,
        sbp_lt_90_or_dbp_lte_60: bool,
        age_gte_65: bool,
    ) -> ScoreResult:
        """
        Calculate CURB-65 score.

        Args:
            confusion: New mental confusion (disorientation in person, place, or time)
            bun_gt_19_or_urea_gt_7: BUN >19 mg/dL or Urea >7 mmol/L
            respiratory_rate_gte_30: Respiratory rate ≥30/min
            sbp_lt_90_or_dbp_lte_60: Systolic BP <90 mmHg OR Diastolic BP ≤60 mmHg
            age_gte_65: Age ≥65 years

        Returns:
            ScoreResult with score, mortality risk, and disposition recommendation
        """
        # Calculate score
        score = sum([
            1 if confusion else 0,
            1 if bun_gt_19_or_urea_gt_7 else 0,
            1 if respiratory_rate_gte_30 else 0,
            1 if sbp_lt_90_or_dbp_lte_60 else 0,
            1 if age_gte_65 else 0,
        ])

        # Determine risk level and recommendations
        interpretation = self._interpret_score(score)

        # Component details
        components = {
            "C - Confusion": 1 if confusion else 0,
            "U - Urea >7 mmol/L (BUN >19 mg/dL)": 1 if bun_gt_19_or_urea_gt_7 else 0,
            "R - Respiratory rate ≥30/min": 1 if respiratory_rate_gte_30 else 0,
            "B - Blood pressure (SBP <90 or DBP ≤60)": 1 if sbp_lt_90_or_dbp_lte_60 else 0,
            "65 - Age ≥65 years": 1 if age_gte_65 else 0,
        }

        return ScoreResult(
            tool_name=self.low_level_key.name,
            tool_id=self.low_level_key.tool_id,
            value=score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            calculation_details=components,
            references=list(self.references),
        )

    def _interpret_score(self, score: int) -> Interpretation:
        """Generate interpretation based on CURB-65 score"""

        # Mortality rates from original study (Lim et al. 2003)
        mortality_rates = {
            0: "0.7%",
            1: "2.1%",
            2: "9.2%",
            3: "14.5%",
            4: "40%",
            5: "57%",
        }

        mortality = mortality_rates.get(score, "N/A")

        if score <= 1:
            # Low risk
            severity = Severity.MILD
            risk_level = RiskLevel.LOW
            summary = f"CURB-65 = {score}: Low risk ({mortality} 30-day mortality)"
            detail = (
                f"Low severity pneumonia. The 30-day mortality rate for CURB-65 score "
                f"of {score} is approximately {mortality}."
            )
            recommendations = [
                "Consider outpatient treatment if clinically appropriate",
                "Oral antibiotics per local guidelines",
                "Ensure adequate oral intake and home support",
                "Provide safety-net advice and follow-up within 48 hours",
            ]
            next_steps = [
                "Assess social circumstances and ability to take oral medications",
                "Consider comorbidities that may warrant admission despite low score",
                "Prescribe appropriate oral antibiotic (e.g., amoxicillin or doxycycline)",
            ]
            disposition = "Outpatient"

        elif score == 2:
            # Moderate risk
            severity = Severity.MODERATE
            risk_level = RiskLevel.INTERMEDIATE
            summary = f"CURB-65 = {score}: Moderate risk ({mortality} 30-day mortality)"
            detail = (
                f"Moderate severity pneumonia. The 30-day mortality rate is approximately "
                f"{mortality}. Consider short hospital admission or closely monitored outpatient care."
            )
            recommendations = [
                "Consider short inpatient admission or hospital-supervised outpatient care",
                "May be suitable for Hospital at Home if available",
                "Close follow-up within 24-48 hours if discharged",
            ]
            next_steps = [
                "Assess oxygen saturation and need for supplemental O2",
                "Check for presence of complicating factors (effusion, multilobar, etc.)",
                "Consider IV antibiotics initially, step-down to oral when improving",
            ]
            disposition = "Consider admission / Close outpatient follow-up"

        else:
            # High risk (score 3-5)
            severity = Severity.SEVERE
            risk_level = RiskLevel.HIGH
            summary = f"CURB-65 = {score}: High risk ({mortality} 30-day mortality)"
            detail = (
                f"Severe pneumonia with high mortality risk ({mortality}). "
                f"Hospital admission is strongly recommended."
            )

            if score >= 4:
                recommendations = [
                    "Urgent hospital admission required",
                    "Consider ICU admission or high-dependency unit",
                    "IV broad-spectrum antibiotics",
                    "Assess for sepsis and organ dysfunction",
                ]
                next_steps = [
                    "Obtain blood cultures before antibiotics",
                    "Consider CT chest if complicated pneumonia suspected",
                    "Monitor for respiratory failure - early intubation if deteriorating",
                    "Involve critical care team early",
                ]
                disposition = "Inpatient - Consider ICU"
            else:
                recommendations = [
                    "Hospital admission recommended",
                    "IV antibiotics per local severe CAP guidelines",
                    "Supplemental oxygen to maintain SpO2 ≥92%",
                    "Regular monitoring of vital signs",
                ]
                next_steps = [
                    "Obtain blood and sputum cultures",
                    "Check for urinary Legionella and pneumococcal antigens",
                    "Reassess within 24-48 hours for clinical response",
                ]
                disposition = "Inpatient"

        return Interpretation(
            summary=summary,
            severity=severity,
            detail=detail,
            stage=f"CURB-65 = {score}",
            stage_description=f"{risk_level.value.replace('_', ' ').title()} risk - {disposition}",
            risk_level=risk_level,
            recommendations=tuple(recommendations),
            next_steps=tuple(next_steps),
            warnings=tuple() if score < 3 else (
                "High mortality risk - prompt treatment essential",
            ),
        )
