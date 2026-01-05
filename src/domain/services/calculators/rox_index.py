"""
ROX Index Calculator

Predicts high-flow nasal cannula (HFNC) failure in acute hypoxemic respiratory failure.

Reference:
    Roca O, Messika J, Caralt B, et al. Predicting success of high-flow nasal
    cannula in pneumonia patients with hypoxemic respiratory failure: The utility
    of the ROX index. J Crit Care. 2016;35:200-205.
    DOI: 10.1016/j.jcrc.2016.05.022
    PMID: 27481760

    Roca O, Caralt B, Messika J, et al. An Index Combining Respiratory Rate and
    Oxygenation to Predict Outcome of Nasal High-Flow Therapy.
    Am J Respir Crit Care Med. 2019;199(11):1368-1376.
    DOI: 10.1164/rccm.201803-0589OC
    PMID: 30576221
"""

from typing import Any, Optional

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


class RoxIndexCalculator(BaseCalculator):
    """
    ROX Index Calculator

    The ROX index (Respiratory rate-OXygenation) predicts whether a patient
    on high-flow nasal cannula (HFNC) will require intubation.

    Formula:
        ROX Index = (SpO2 / FiO2) / Respiratory Rate

    Interpretation (at 2, 6, and 12 hours on HFNC):
        - ROX ≥4.88: Low risk of HFNC failure (intubation unlikely)
        - ROX 3.85-4.87: Intermediate risk, reassess frequently
        - ROX <3.85: High risk of HFNC failure (consider intubation)

    Best assessed at:
        - 2 hours after HFNC initiation
        - 6 hours after HFNC initiation
        - 12 hours after HFNC initiation

    Clinical Use:
        - Pneumonia with hypoxemic respiratory failure
        - COVID-19 respiratory failure
        - Avoiding delayed intubation
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="rox_index",
                name="ROX Index",
                purpose="Predict high-flow nasal cannula failure and need for intubation",
                input_params=["spo2", "fio2", "respiratory_rate"],
                output_type="ROX index with HFNC failure risk"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.CRITICAL_CARE,
                    Specialty.PULMONOLOGY,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.INTERNAL_MEDICINE,
                ),
                conditions=(
                    "Hypoxemic respiratory failure",
                    "Pneumonia",
                    "COVID-19",
                    "ARDS",
                    "Acute respiratory failure",
                    "High-flow nasal cannula",
                ),
                clinical_contexts=(
                    ClinicalContext.MONITORING,
                    ClinicalContext.TREATMENT_DECISION,
                    ClinicalContext.PROGNOSIS,
                ),
                clinical_questions=(
                    "Should I intubate this patient on HFNC?",
                    "Is high-flow nasal cannula working?",
                    "What is the ROX index?",
                    "Will this patient need intubation?",
                ),
                icd10_codes=("J96.0", "J18.9", "U07.1"),
                keywords=(
                    "ROX index", "HFNC", "high-flow nasal cannula", "intubation",
                    "respiratory failure", "hypoxemia", "oxygenation",
                    "non-invasive", "NIV failure",
                ),
            ),
            references=self._get_references(),
        )

    def _get_references(self) -> tuple[Reference, ...]:
        return (
            Reference(
                citation="Roca O, Messika J, Caralt B, et al. Predicting success of high-flow nasal cannula in pneumonia patients with hypoxemic respiratory failure: The utility of the ROX index. J Crit Care. 2016;35:200-205.",
                doi="10.1016/j.jcrc.2016.05.022",
                pmid="27481760",
                year=2016,
            ),
            Reference(
                citation="Roca O, Caralt B, Messika J, et al. An Index Combining Respiratory Rate and Oxygenation to Predict Outcome of Nasal High-Flow Therapy. Am J Respir Crit Care Med. 2019;199(11):1368-1376.",
                doi="10.1164/rccm.201803-0589OC",
                pmid="30576221",
                year=2019,
            ),
        )

    def calculate(
        self,
        spo2: float,
        fio2: float,
        respiratory_rate: int,
        hours_on_hfnc: Optional[float] = None,
    ) -> ScoreResult:
        """
        Calculate ROX Index.

        Args:
            spo2: Oxygen saturation (%, typically 70-100)
            fio2: Fraction of inspired oxygen (0.21-1.0 or 21-100%)
            respiratory_rate: Respiratory rate (breaths/min)
            hours_on_hfnc: Hours on HFNC (for context, helps interpretation)

        Returns:
            ScoreResult with ROX index and intubation risk assessment
        """
        # Validate and normalize inputs
        if spo2 < 50 or spo2 > 100:
            raise ValueError(f"SpO2 {spo2}% is outside expected range (50-100%)")

        # Handle FiO2 as percentage if > 1
        if fio2 > 1:
            fio2 = fio2 / 100

        if fio2 < 0.21 or fio2 > 1.0:
            raise ValueError(f"FiO2 {fio2} is outside expected range (0.21-1.0)")

        if respiratory_rate < 8 or respiratory_rate > 60:
            raise ValueError(f"Respiratory rate {respiratory_rate} is outside expected range (8-60)")

        if hours_on_hfnc is not None and (hours_on_hfnc < 0 or hours_on_hfnc > 168):
            raise ValueError(f"Hours on HFNC {hours_on_hfnc} is outside expected range (0-168)")

        # Calculate ROX index
        # ROX = (SpO2 / FiO2) / RR
        # SpO2 is in %, FiO2 as decimal would give SpO2/FiO2 in range 21-476
        # We use SpO2 as % and FiO2 as decimal (original formula)
        spo2 / (fio2 * 100)  # Normalize to ratio
        rox_index = (spo2 / fio2) / respiratory_rate
        rox_index = round(rox_index, 2)

        # Generate interpretation
        interpretation = self._interpret_rox(rox_index, hours_on_hfnc, spo2, fio2, respiratory_rate)

        # Build calculation details
        details = {
            "SpO2": f"{spo2}%",
            "FiO2": f"{fio2:.0%}",
            "Respiratory_rate": f"{respiratory_rate} breaths/min",
            "SpO2/FiO2": f"{spo2/fio2:.1f}",
            "ROX_Index": f"{rox_index}",
        }

        if hours_on_hfnc is not None:
            details["Time_on_HFNC"] = f"{hours_on_hfnc} hours"

        return ScoreResult(
            value=rox_index,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self._get_references()),
            tool_id=self.tool_id,
            tool_name=self.metadata.name,
            raw_inputs={
                "spo2": spo2,
                "fio2": fio2,
                "respiratory_rate": respiratory_rate,
                "hours_on_hfnc": hours_on_hfnc,
            },
            calculation_details=details,
            formula_used="ROX = (SpO2 / FiO2) / Respiratory Rate",
        )

    def _interpret_rox(
        self,
        rox_index: float,
        hours_on_hfnc: Optional[float],
        spo2: float,
        fio2: float,
        rr: int,
    ) -> Interpretation:
        """Generate interpretation and recommendations."""

        # Risk stratification based on ROX index
        if rox_index >= 4.88:
            risk_category = "Low risk"
            severity = Severity.NORMAL
            risk_level = RiskLevel.LOW
            detail = "ROX ≥4.88 suggests HFNC is likely to succeed. Continue current therapy and monitor."
        elif rox_index >= 3.85:
            risk_category = "Intermediate risk"
            severity = Severity.MODERATE
            risk_level = RiskLevel.INTERMEDIATE
            detail = "ROX 3.85-4.87 is indeterminate. Reassess frequently (every 1-2 hours). Consider escalation if not improving."
        else:
            risk_category = "High risk"
            severity = Severity.SEVERE
            risk_level = RiskLevel.HIGH
            detail = "ROX <3.85 suggests high risk of HFNC failure. Strongly consider intubation to avoid delayed intubation which worsens outcomes."

        summary = f"ROX Index {rox_index}: {risk_category} of HFNC failure"

        # Time-specific guidance
        time_note = ""
        if hours_on_hfnc is not None:
            if hours_on_hfnc <= 2:
                time_note = " (assessed at 2-hour mark)"
            elif hours_on_hfnc <= 6:
                time_note = " (assessed at 6-hour mark)"
            elif hours_on_hfnc <= 12:
                time_note = " (assessed at 12-hour mark)"
            else:
                time_note = f" (assessed at {hours_on_hfnc} hours)"

        # Recommendations based on risk
        recommendations: tuple[str, ...]
        if rox_index >= 4.88:
            recommendations = (
                "Continue HFNC therapy",
                "Monitor for clinical deterioration",
                "Reassess ROX index at 6 and 12 hours",
                "Watch for signs of fatigue or distress",
            )
        elif rox_index >= 3.85:
            recommendations = (
                "Close monitoring required (reassess every 1-2 hours)",
                "Prepare for possible escalation",
                "Consider trial of higher FiO2 or flow",
                "Have intubation equipment ready",
                "Discuss with senior/ICU if not improving",
            )
        else:
            recommendations = (
                "⚠️ HIGH RISK: Strongly consider intubation",
                "Delayed intubation associated with worse outcomes",
                "Prepare for emergent intubation if needed",
                "If continuing HFNC, reassess within 1 hour",
                "Consider NIV as bridge if available",
            )

        warnings = []
        if rox_index < 3.85:
            warnings.append("⚠️ ROX <3.85: High risk of HFNC failure - consider intubation")
        if rr >= 30:
            warnings.append("⚠️ Tachypnea (RR ≥30) suggests increased work of breathing")
        if fio2 >= 0.8:
            warnings.append("⚠️ High FiO2 requirement (≥80%) - limited room for escalation")

        return Interpretation(
            summary=summary + time_note,
            detail=detail,
            severity=severity,
            risk_level=risk_level,
            recommendations=recommendations,
            warnings=tuple(warnings),
            next_steps=(
                "Reassess ROX at 2, 6, and 12 hours on HFNC",
                "Monitor for signs of respiratory fatigue",
                "Trend ROX over time (decreasing ROX = concerning)",
                "If intubating, use lung-protective ventilation",
            ),
        )
