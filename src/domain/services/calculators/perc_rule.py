"""
PERC Rule (Pulmonary Embolism Rule-out Criteria) Calculator

The PERC Rule is used to rule out pulmonary embolism in low-risk patients
without the need for D-dimer testing or imaging.

Original Reference:
    Kline JA, Mitchell AM, Kabrhel C, Richman PB, Courtney DM.
    Clinical criteria to prevent unnecessary diagnostic testing in emergency
    department patients with suspected pulmonary embolism.
    J Thromb Haemost. 2004;2(8):1247-1255.
    doi:10.1111/j.1538-7836.2004.00772.x. PMID: 15304025.

Validation Reference:
    Kline JA, Courtney DM, Kabrhel C, et al.
    Prospective multicenter evaluation of the pulmonary embolism rule-out criteria.
    J Thromb Haemost. 2008;6(5):772-780.
    doi:10.1111/j.1538-7836.2008.02944.x. PMID: 18318689.
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


class PERCRuleCalculator(BaseCalculator):
    """
    PERC Rule (Pulmonary Embolism Rule-out Criteria) Calculator

    The PERC Rule is a clinical decision rule used to exclude pulmonary embolism
    in low-risk patients presenting to the emergency department.

    If a patient is PERC-negative (all 8 criteria are absent), the probability
    of PE is <2%, and no further testing (including D-dimer) is needed.

    PERC Criteria (all must be ABSENT to be PERC-negative):
        1. Age ≥50 years
        2. Heart rate ≥100 bpm
        3. Oxygen saturation <95% on room air
        4. Unilateral leg swelling
        5. Hemoptysis
        6. Recent surgery or trauma (within 4 weeks)
        7. Prior PE or DVT
        8. Hormone use (oral contraceptives or hormone replacement therapy)

    Prerequisites:
        - Patient must have LOW pretest probability for PE
        - Not for use in moderate or high pretest probability patients
        - Clinician must have considered PE as a diagnosis (the test is triggered)

    If ANY criterion is present → PERC-positive → Proceed to D-dimer or imaging
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="perc_rule",
                name="PERC Rule (Pulmonary Embolism Rule-out Criteria)",
                purpose="Rule out pulmonary embolism in low-risk patients",
                input_params=[
                    "age_50_or_older",
                    "heart_rate_100_or_higher",
                    "o2_sat_below_95",
                    "unilateral_leg_swelling",
                    "hemoptysis",
                    "recent_surgery_trauma",
                    "prior_pe_dvt",
                    "hormone_use",
                ],
                output_type="PERC result (positive or negative) with recommendation",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.PULMONOLOGY,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.CRITICAL_CARE,
                ),
                conditions=(
                    "pulmonary embolism",
                    "PE",
                    "venous thromboembolism",
                    "VTE",
                    "chest pain",
                    "dyspnea",
                    "shortness of breath",
                    "pleuritic chest pain",
                ),
                clinical_contexts=(
                    ClinicalContext.SCREENING,
                    ClinicalContext.DIFFERENTIAL_DIAGNOSIS,
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.TRIAGE,
                ),
                clinical_questions=(
                    "Can I rule out PE without D-dimer?",
                    "Does this patient need a D-dimer test?",
                    "Is this patient's PE risk low enough to discharge?",
                    "Should I order a CT PE for this patient?",
                    "Can I safely rule out PE in this low-risk patient?",
                ),
                icd10_codes=(
                    "I26.0",  # Pulmonary embolism with acute cor pulmonale
                    "I26.9",  # Pulmonary embolism without acute cor pulmonale
                    "I26.99",  # Other pulmonary embolism
                    "R06.02",  # Shortness of breath
                    "R07.89",  # Other chest pain
                ),
                keywords=(
                    "PERC",
                    "PERC rule",
                    "pulmonary embolism",
                    "PE rule out",
                    "PE exclusion",
                    "D-dimer",
                    "chest pain",
                    "shortness of breath",
                    "dyspnea",
                    "VTE",
                    "low risk PE",
                ),
            ),
            references=(
                Reference(
                    citation="Kline JA, Mitchell AM, Kabrhel C, Richman PB, Courtney DM. "
                    "Clinical criteria to prevent unnecessary diagnostic testing in emergency "
                    "department patients with suspected pulmonary embolism. "
                    "J Thromb Haemost. 2004;2(8):1247-1255.",
                    doi="10.1111/j.1538-7836.2004.00772.x",
                    pmid="15304025",
                    year=2004,
                ),
                Reference(
                    citation="Kline JA, Courtney DM, Kabrhel C, et al. Prospective multicenter "
                    "evaluation of the pulmonary embolism rule-out criteria. "
                    "J Thromb Haemost. 2008;6(5):772-780.",
                    doi="10.1111/j.1538-7836.2008.02944.x",
                    pmid="18318689",
                    year=2008,
                ),
            ),
            version="2004 (Kline)",
            validation_status="validated",
        )

    def calculate(
        self,
        age_50_or_older: bool = False,
        heart_rate_100_or_higher: bool = False,
        o2_sat_below_95: bool = False,
        unilateral_leg_swelling: bool = False,
        hemoptysis: bool = False,
        recent_surgery_trauma: bool = False,
        prior_pe_dvt: bool = False,
        hormone_use: bool = False,
    ) -> ScoreResult:
        """
        Evaluate PERC Rule criteria.

        Args:
            age_50_or_older: Is the patient age ≥50 years?
            heart_rate_100_or_higher: Is heart rate ≥100 bpm?
            o2_sat_below_95: Is oxygen saturation <95% on room air?
            unilateral_leg_swelling: Is there unilateral leg swelling?
            hemoptysis: Is there hemoptysis (coughing up blood)?
            recent_surgery_trauma: Surgery or trauma within the past 4 weeks?
            prior_pe_dvt: History of PE or DVT?
            hormone_use: Current use of oral contraceptives or HRT?

        Returns:
            ScoreResult with PERC status and recommendation

        Note:
            PERC should ONLY be applied to patients with LOW pretest probability.
            A PERC-negative result in a low-risk patient indicates PE can be
            ruled out without further testing (including D-dimer).
        """
        criteria: dict[str, bool] = {
            "Age ≥50 years": age_50_or_older,
            "Heart rate ≥100 bpm": heart_rate_100_or_higher,
            "O2 saturation <95%": o2_sat_below_95,
            "Unilateral leg swelling": unilateral_leg_swelling,
            "Hemoptysis": hemoptysis,
            "Recent surgery/trauma (≤4 weeks)": recent_surgery_trauma,
            "Prior PE or DVT": prior_pe_dvt,
            "Hormone use (OCP/HRT)": hormone_use,
        }

        # Count positive criteria
        positive_criteria = [name for name, value in criteria.items() if value]
        criteria_count = len(positive_criteria)

        # PERC-negative means ALL criteria are absent
        is_perc_negative = criteria_count == 0

        # Generate interpretation
        interpretation = self._interpret_result(
            is_perc_negative, criteria_count, positive_criteria
        )

        # Build calculation details
        calculation_details: dict[str, bool | int | list[str] | str] = {
            "criteria_evaluated": criteria,
            "positive_criteria_count": criteria_count,
            "positive_criteria": positive_criteria,
            "perc_negative": is_perc_negative,
            "result": "PERC-negative (PE ruled out)" if is_perc_negative else "PERC-positive (further testing needed)",
        }

        return ScoreResult(
            tool_name=self.low_level_key.name,
            tool_id=self.low_level_key.tool_id,
            value=criteria_count,
            unit=Unit.SCORE,
            interpretation=interpretation,
            calculation_details=calculation_details,
            references=list(self.references),
            formula_used="PERC-negative if 0/8 criteria present, PERC-positive if ≥1 criterion present",
        )

    def _interpret_result(
        self,
        is_perc_negative: bool,
        criteria_count: int,
        positive_criteria: list[str],
    ) -> Interpretation:
        """Generate clinical interpretation based on PERC result."""

        if is_perc_negative:
            return Interpretation(
                summary="PERC-Negative: Pulmonary embolism can be ruled out",
                detail="All 8 PERC criteria are absent. In a patient with LOW pretest "
                "probability for PE, a PERC-negative result indicates that PE can be "
                "safely ruled out without further testing. The probability of PE is <2%.",
                severity=Severity.NORMAL,
                risk_level=RiskLevel.VERY_LOW,
                stage="PERC-Negative",
                stage_description="PE ruled out (no testing needed)",
                recommendations=(
                    "No D-dimer testing needed",
                    "No CT pulmonary angiography needed",
                    "Consider alternative diagnoses",
                    "Safe to discharge if no other concerns",
                    "Return precautions for worsening symptoms",
                ),
                next_steps=(
                    "Evaluate for alternative causes of symptoms",
                    "Provide discharge instructions",
                    "Ensure patient understands when to return",
                ),
                warnings=(
                    "PERC only valid in LOW pretest probability patients",
                    "Do not use PERC in moderate or high risk patients",
                ),
            )
        else:
            criteria_str = ", ".join(positive_criteria)

            if criteria_count == 1:
                detail = (
                    f"1 PERC criterion is present: {criteria_str}. "
                    "The patient is PERC-positive, and PE cannot be ruled out by clinical "
                    "criteria alone. Further testing is recommended."
                )
            else:
                detail = (
                    f"{criteria_count} PERC criteria are present: {criteria_str}. "
                    "The patient is PERC-positive, and PE cannot be ruled out by clinical "
                    "criteria alone. Further testing is recommended."
                )

            # Determine severity based on criteria count
            if criteria_count <= 2:
                severity = Severity.MILD
                risk_level = RiskLevel.LOW
            elif criteria_count <= 4:
                severity = Severity.MODERATE
                risk_level = RiskLevel.INTERMEDIATE
            else:
                severity = Severity.SEVERE
                risk_level = RiskLevel.HIGH

            # Specific recommendations based on which criteria are positive
            recommendations: list[str] = [
                "Proceed with D-dimer testing",
                "If D-dimer elevated, CT pulmonary angiography indicated",
                "Consider age-adjusted D-dimer threshold if applicable",
            ]

            if "Prior PE or DVT" in positive_criteria:
                recommendations.append(
                    "High risk due to prior VTE - lower threshold for imaging"
                )
            if "O2 saturation <95%" in positive_criteria:
                recommendations.append("Ensure adequate oxygenation while evaluating")
            if "Unilateral leg swelling" in positive_criteria:
                recommendations.append(
                    "Consider lower extremity ultrasound for DVT"
                )

            next_steps: list[str] = [
                "Check D-dimer level",
                "If D-dimer positive, proceed to CTPA",
                "Calculate Wells PE Score for risk stratification",
            ]

            warnings: tuple[str, ...] = ()
            if criteria_count >= 3:
                warnings = (
                    "Multiple risk factors present - maintain high suspicion for PE",
                    "Consider empiric anticoagulation while awaiting imaging if high clinical suspicion",
                )

            return Interpretation(
                summary=f"PERC-Positive ({criteria_count}/8 criteria): Further testing needed",
                detail=detail,
                severity=severity,
                risk_level=risk_level,
                stage="PERC-Positive",
                stage_description="PE not excluded - testing required",
                recommendations=tuple(recommendations),
                next_steps=tuple(next_steps),
                warnings=warnings,
            )
