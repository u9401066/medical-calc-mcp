"""
Pediatric Early Warning Score (PEWS) Calculator

Identifies children at risk of clinical deterioration on hospital wards.
Validated for children 0-18 years. Triggers escalation when score threshold reached.

Clinical Application:
- Rapid assessment tool for hospitalized children
- Identifies children at risk of deterioration before critical events
- Guides escalation to higher level of care

Components (0-3 points each):
1. Behavior/Neurological status
2. Cardiovascular status (color, capillary refill, heart rate)
3. Respiratory status (effort, rate, SpO2)

Score Interpretation:
- 0-2: Low risk, routine monitoring
- 3-4: Moderate risk, increase monitoring frequency
- ≥5: High risk, immediate physician evaluation
- ≥7: Critical, consider PICU transfer

References:
    Parshuram CS, Hutchison J, Middaugh K. Development and initial validation
    of the Bedside Paediatric Early Warning System score.
    Crit Care. 2009;13(4):R135. PMID: 19678924
    
    Chapman SM, Wray J, Oulton K, Peters MJ. The value of paediatric early
    warning scores: A systematic review.
    Pediatrics. 2017;140(6):e20164154. PMID: 29167378
    
    NICE Guideline NG51: Sepsis: recognition, diagnosis and early management.
    National Institute for Health and Care Excellence. 2016 (updated 2024).
"""

from typing import Optional
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


class PEWSCalculator(BaseCalculator):
    """
    Pediatric Early Warning Score (PEWS) Calculator
    
    Evaluates risk of clinical deterioration using 3 domains:
    1. Behavior/Neurological
    2. Cardiovascular
    3. Respiratory
    
    Age-specific vital sign thresholds are incorporated.
    """

    # Age-specific normal ranges for heart rate
    HR_RANGES = {
        "0-3m": (100, 180),
        "3-12m": (100, 160),
        "1-4y": (90, 140),
        "4-12y": (70, 120),
        "12-18y": (60, 100),
    }
    
    # Age-specific normal ranges for respiratory rate
    RR_RANGES = {
        "0-3m": (30, 50),
        "3-12m": (25, 45),
        "1-4y": (20, 30),
        "4-12y": (15, 25),
        "12-18y": (12, 20),
    }

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="pews",
                name="Pediatric Early Warning Score (PEWS)",
                purpose="Identify hospitalized children at risk of clinical deterioration",
                input_params=[
                    "behavior_score", "cardiovascular_score", "respiratory_score",
                    "age_group", "heart_rate", "respiratory_rate", "spo2"
                ],
                output_type="PEWS score (0-9) with escalation guidance"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.PEDIATRICS,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.CRITICAL_CARE,
                    Specialty.NURSING,
                ),
                conditions=(
                    "Clinical deterioration",
                    "Pediatric hospitalization",
                    "Ward monitoring",
                    "Early warning",
                    "Sepsis screening",
                ),
                clinical_contexts=(
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.SCREENING,
                    ClinicalContext.MONITORING,
                ),
            ),
            references=(
                Reference(
                    citation="Parshuram CS, et al. Development and initial validation of the Bedside PEWS. Crit Care. 2009;13(4):R135.",
                    doi="10.1186/cc7998",
                    pmid="19678924",
                    year=2009
                ),
                Reference(
                    citation="Chapman SM, et al. The value of paediatric early warning scores: A systematic review. Pediatrics. 2017;140(6):e20164154.",
                    doi="10.1542/peds.2016-4154",
                    pmid="29167378",
                    year=2017
                ),
            ),
        )

    def calculate(
        self,
        behavior_score: int,
        cardiovascular_score: int,
        respiratory_score: int,
        age_group: Optional[str] = None,
        heart_rate: Optional[int] = None,
        respiratory_rate: Optional[int] = None,
        spo2: Optional[float] = None,
        supplemental_oxygen: bool = False
    ) -> ScoreResult:
        """
        Calculate PEWS score.
        
        Args:
            behavior_score: Neurological/behavior status (0-3)
                0 = Playing/appropriate
                1 = Sleeping
                2 = Irritable/confused
                3 = Reduced response to pain / Lethargy
            cardiovascular_score: Cardiovascular status (0-3)
                0 = Pink, CRT ≤2s, normal HR
                1 = Pale or CRT 3s
                2 = Gray/mottled, CRT 4s, tachycardia
                3 = Gray/cyanotic, CRT ≥5s, tachy/bradycardia
            respiratory_score: Respiratory status (0-3)
                0 = Normal rate, no distress, SpO2 >94%
                1 = Mild increased WOB, mild tachypnea
                2 = Moderate WOB, moderate tachypnea, SpO2 90-94%
                3 = Severe WOB, severe tachypnea, SpO2 <90%, apnea
            age_group: Optional age category for context
                "0-3m", "3-12m", "1-4y", "4-12y", "12-18y"
            heart_rate: Optional actual heart rate (bpm)
            respiratory_rate: Optional actual RR (breaths/min)
            spo2: Optional oxygen saturation (%)
            supplemental_oxygen: Whether child is on supplemental O2
        
        Returns:
            ScoreResult with PEWS score and escalation guidance
        """
        # Validate component scores
        for name, value in [
            ("behavior_score", behavior_score),
            ("cardiovascular_score", cardiovascular_score),
            ("respiratory_score", respiratory_score)
        ]:
            if not isinstance(value, int) or value < 0 or value > 3:
                raise ValueError(f"{name} must be 0, 1, 2, or 3")

        # Calculate total score
        total_score = behavior_score + cardiovascular_score + respiratory_score

        # Add 2 points if on supplemental oxygen
        if supplemental_oxygen:
            total_score += 2

        # Component breakdown
        components = {
            "Behavior/Neurological": behavior_score,
            "Cardiovascular": cardiovascular_score,
            "Respiratory": respiratory_score,
            "Supplemental O2 (+2)": "Yes" if supplemental_oxygen else "No",
        }

        # Determine severity and action
        if total_score <= 2:
            severity = Severity.NORMAL
            risk_level = "Low Risk"
            monitoring = "Routine q4h monitoring"
            escalation = "No escalation required"
            action = "Continue standard care; reassess per protocol"
        elif total_score <= 4:
            severity = Severity.MILD
            risk_level = "Moderate Risk"
            monitoring = "Increase to q2h monitoring"
            escalation = "Notify charge nurse"
            action = "Increase monitoring frequency; consider physician review within 1 hour"
        elif total_score <= 6:
            severity = Severity.MODERATE
            risk_level = "High Risk"
            monitoring = "Continuous or q1h monitoring"
            escalation = "Immediate physician evaluation"
            action = "Urgent physician review; consider rapid response team activation"
        else:  # ≥7
            severity = Severity.CRITICAL
            risk_level = "Critical"
            monitoring = "Continuous monitoring"
            escalation = "Activate rapid response / PICU consult"
            action = "Immediate senior physician review; consider PICU transfer; activate RRT"

        # Build vital sign context if provided
        vs_context = []
        if heart_rate and age_group and age_group in self.HR_RANGES:
            hr_range = self.HR_RANGES[age_group]
            if heart_rate < hr_range[0]:
                vs_context.append(f"Bradycardia: HR {heart_rate} bpm (normal {hr_range[0]}-{hr_range[1]})")
            elif heart_rate > hr_range[1]:
                vs_context.append(f"Tachycardia: HR {heart_rate} bpm (normal {hr_range[0]}-{hr_range[1]})")
        
        if respiratory_rate and age_group and age_group in self.RR_RANGES:
            rr_range = self.RR_RANGES[age_group]
            if respiratory_rate > rr_range[1]:
                vs_context.append(f"Tachypnea: RR {respiratory_rate} (normal {rr_range[0]}-{rr_range[1]})")

        if spo2:
            if spo2 < 90:
                vs_context.append(f"Severe hypoxemia: SpO2 {spo2}%")
            elif spo2 < 94:
                vs_context.append(f"Hypoxemia: SpO2 {spo2}%")

        interpretation = Interpretation(
            severity=severity,
            summary=f"PEWS {total_score}: {risk_level}",
            detail=(
                f"Component scores: Behavior={behavior_score}, CV={cardiovascular_score}, "
                f"Resp={respiratory_score}" +
                (f", +2 for O2" if supplemental_oxygen else "") +
                (f"\nVital sign concerns: {'; '.join(vs_context)}" if vs_context else "")
            ),
            recommendations=(f"{escalation}. {action}",)
        )

        details = {
            "total_score": total_score,
            "component_scores": components,
            "risk_level": risk_level,
            "monitoring_frequency": monitoring,
            "escalation_action": escalation,
            "vital_sign_concerns": vs_context if vs_context else None,
            "age_group": age_group,
            "next_step": self._get_next_step(total_score)
        }

        return ScoreResult(
            value=total_score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "behavior_score": behavior_score,
                "cardiovascular_score": cardiovascular_score,
                "respiratory_score": respiratory_score,
                "age_group": age_group,
                "heart_rate": heart_rate,
                "respiratory_rate": respiratory_rate,
                "spo2": spo2,
                "supplemental_oxygen": supplemental_oxygen,
            },
            calculation_details=details
        )

    def _get_next_step(self, score: int) -> str:
        """Get clinical next step recommendation."""
        if score <= 2:
            return "Continue routine monitoring; reassess if clinical concern"
        elif score <= 4:
            return "Increase monitoring; physician review within 60 minutes"
        elif score <= 6:
            return "Urgent physician review; consider rapid response team"
        else:
            return "Activate rapid response team; prepare for possible PICU transfer"
