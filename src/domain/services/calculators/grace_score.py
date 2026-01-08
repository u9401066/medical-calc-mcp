"""
GRACE Score Calculator

Global Registry of Acute Coronary Events (GRACE) score for ACS risk stratification.

Reference:
    Fox KA, Dabbous OH, Goldberg RJ, et al. Prediction of risk of death and
    myocardial infarction in the six months after presentation with acute
    coronary syndrome: prospective multinational observational study (GRACE).
    BMJ. 2006;333(7578):1091.
    DOI: 10.1136/bmj.38985.646481.55
    PMID: 17032691

    Eagle KA, Lim MJ, Dabbous OH, et al. A validated prediction model for all
    forms of acute coronary syndrome: estimating the risk of 6-month postdischarge
    death in an international registry. JAMA. 2004;291(22):2727-2733.
    DOI: 10.1001/jama.291.22.2727
    PMID: 15187054

    GRACE ACS Risk Model: www.gracescore.org
"""

from typing import Literal

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


class GraceScoreCalculator(BaseCalculator):
    """
    GRACE Score Calculator

    The GRACE score estimates mortality risk in patients with Acute Coronary
    Syndrome (ACS), including STEMI, NSTEMI, and unstable angina.

    Risk Factors (8 variables):
        - Age
        - Heart rate
        - Systolic blood pressure
        - Creatinine (or renal function)
        - Killip class
        - Cardiac arrest at admission
        - ST-segment deviation
        - Elevated cardiac markers

    Outcomes Predicted:
        - In-hospital mortality
        - 6-month mortality
        - 6-month mortality + MI

    Risk Categories:
        - Low: GRACE ≤108 (in-hospital mortality <1%)
        - Intermediate: GRACE 109-140 (in-hospital mortality 1-3%)
        - High: GRACE >140 (in-hospital mortality >3%)
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="grace_score",
                name="GRACE Score",
                purpose="Stratify mortality risk in acute coronary syndrome",
                input_params=["age", "heart_rate", "systolic_bp", "creatinine", "killip_class", "cardiac_arrest", "st_deviation", "elevated_markers"],
                output_type="GRACE score with mortality risk",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.CARDIOLOGY,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.CRITICAL_CARE,
                    Specialty.INTERNAL_MEDICINE,
                ),
                conditions=(
                    "Acute coronary syndrome",
                    "ACS",
                    "STEMI",
                    "NSTEMI",
                    "Unstable angina",
                    "Myocardial infarction",
                    "Chest pain",
                ),
                clinical_contexts=(
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.TREATMENT_DECISION,
                    ClinicalContext.DISPOSITION,
                    ClinicalContext.SEVERITY_ASSESSMENT,
                ),
                clinical_questions=(
                    "What is this ACS patient's mortality risk?",
                    "Should this patient go to the cath lab urgently?",
                    "How do I risk stratify this NSTEMI?",
                    "What is the GRACE score?",
                ),
                icd10_codes=("I21", "I20.0", "I24.9"),
                keywords=(
                    "GRACE",
                    "acute coronary syndrome",
                    "ACS",
                    "STEMI",
                    "NSTEMI",
                    "unstable angina",
                    "mortality",
                    "risk stratification",
                    "myocardial infarction",
                    "MI",
                ),
            ),
            references=self._get_references(),
        )

    def _get_references(self) -> tuple[Reference, ...]:
        return (
            Reference(
                citation="Fox KA, Dabbous OH, Goldberg RJ, et al. Prediction of risk of death and myocardial infarction in the six months after presentation with acute coronary syndrome: prospective multinational observational study (GRACE). BMJ. 2006;333(7578):1091.",
                doi="10.1136/bmj.38985.646481.55",
                pmid="17032691",
                year=2006,
            ),
            Reference(
                citation="Eagle KA, Lim MJ, Dabbous OH, et al. A validated prediction model for all forms of acute coronary syndrome: estimating the risk of 6-month postdischarge death in an international registry. JAMA. 2004;291(22):2727-2733.",
                doi="10.1001/jama.291.22.2727",
                pmid="15187054",
                year=2004,
            ),
        )

    def calculate(
        self,
        age: int,
        heart_rate: int,
        systolic_bp: int,
        creatinine: float,
        killip_class: Literal[1, 2, 3, 4],
        cardiac_arrest: bool = False,
        st_deviation: bool = False,
        elevated_markers: bool = False,
    ) -> ScoreResult:
        """
        Calculate GRACE score.

        Args:
            age: Patient age (years)
            heart_rate: Heart rate (bpm)
            systolic_bp: Systolic blood pressure (mmHg)
            creatinine: Serum creatinine (mg/dL)
            killip_class: Killip class (1-4)
                1: No CHF
                2: Rales, JVD, or S3
                3: Pulmonary edema
                4: Cardiogenic shock
            cardiac_arrest: Cardiac arrest at admission
            st_deviation: ST-segment deviation (≥0.5mm depression or any elevation)
            elevated_markers: Elevated cardiac markers (troponin or CK-MB)

        Returns:
            ScoreResult with GRACE score and mortality risk
        """
        # Validate inputs
        if age < 18 or age > 120:
            raise ValueError(f"Age {age} is outside expected range (18-120)")
        if heart_rate < 20 or heart_rate > 250:
            raise ValueError(f"Heart rate {heart_rate} is outside expected range (20-250)")
        if systolic_bp < 40 or systolic_bp > 300:
            raise ValueError(f"Systolic BP {systolic_bp} is outside expected range (40-300)")
        if creatinine < 0.1 or creatinine > 20:
            raise ValueError(f"Creatinine {creatinine} is outside expected range (0.1-20)")
        if killip_class not in (1, 2, 3, 4):
            raise ValueError(f"Killip class must be 1-4, got {killip_class}")

        # Calculate GRACE score components
        # Age points
        age_points = self._get_age_points(age)

        # Heart rate points
        hr_points = self._get_hr_points(heart_rate)

        # Systolic BP points
        sbp_points = self._get_sbp_points(systolic_bp)

        # Creatinine points
        cr_points = self._get_creatinine_points(creatinine)

        # Killip class points
        killip_points = self._get_killip_points(killip_class)

        # Binary variables
        arrest_points = 39 if cardiac_arrest else 0
        st_points = 28 if st_deviation else 0
        marker_points = 14 if elevated_markers else 0

        # Total GRACE score
        grace_score = age_points + hr_points + sbp_points + cr_points + killip_points + arrest_points + st_points + marker_points

        # Generate interpretation
        interpretation = self._interpret_grace(grace_score, killip_class, cardiac_arrest)

        # Build calculation details
        details = {
            "Age": f"{age} years → {age_points} points",
            "Heart_rate": f"{heart_rate} bpm → {hr_points} points",
            "Systolic_BP": f"{systolic_bp} mmHg → {sbp_points} points",
            "Creatinine": f"{creatinine} mg/dL → {cr_points} points",
            "Killip_class": f"Class {killip_class} → {killip_points} points",
            "Cardiac_arrest": f"{'Yes' if cardiac_arrest else 'No'} → {arrest_points} points",
            "ST_deviation": f"{'Yes' if st_deviation else 'No'} → {st_points} points",
            "Elevated_markers": f"{'Yes' if elevated_markers else 'No'} → {marker_points} points",
            "Total_GRACE_score": str(grace_score),
        }

        return ScoreResult(
            value=grace_score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self._get_references()),
            tool_id=self.tool_id,
            tool_name=self.metadata.name,
            raw_inputs={
                "age": age,
                "heart_rate": heart_rate,
                "systolic_bp": systolic_bp,
                "creatinine": creatinine,
                "killip_class": killip_class,
                "cardiac_arrest": cardiac_arrest,
                "st_deviation": st_deviation,
                "elevated_markers": elevated_markers,
            },
            calculation_details=details,
            formula_used="GRACE = Σ(points for age, HR, SBP, Cr, Killip, arrest, ST, markers)",
        )

    def _get_age_points(self, age: int) -> int:
        """Get points for age."""
        if age < 30:
            return 0
        elif age < 40:
            return 8
        elif age < 50:
            return 25
        elif age < 60:
            return 41
        elif age < 70:
            return 58
        elif age < 80:
            return 75
        elif age < 90:
            return 91
        else:
            return 100

    def _get_hr_points(self, hr: int) -> int:
        """Get points for heart rate."""
        if hr < 50:
            return 0
        elif hr < 70:
            return 3
        elif hr < 90:
            return 9
        elif hr < 110:
            return 15
        elif hr < 150:
            return 24
        elif hr < 200:
            return 38
        else:
            return 46

    def _get_sbp_points(self, sbp: int) -> int:
        """Get points for systolic BP (inverse relationship)."""
        if sbp < 80:
            return 58
        elif sbp < 100:
            return 53
        elif sbp < 120:
            return 43
        elif sbp < 140:
            return 34
        elif sbp < 160:
            return 24
        elif sbp < 200:
            return 10
        else:
            return 0

    def _get_creatinine_points(self, cr: float) -> int:
        """Get points for creatinine."""
        if cr < 0.4:
            return 1
        elif cr < 0.8:
            return 4
        elif cr < 1.2:
            return 7
        elif cr < 1.6:
            return 10
        elif cr < 2.0:
            return 13
        elif cr < 4.0:
            return 21
        else:
            return 28

    def _get_killip_points(self, killip: int) -> int:
        """Get points for Killip class."""
        killip_points = {
            1: 0,  # No CHF
            2: 20,  # Rales/JVD/S3
            3: 39,  # Pulmonary edema
            4: 59,  # Cardiogenic shock
        }
        return killip_points.get(killip, 0)

    def _interpret_grace(
        self,
        grace_score: int,
        killip_class: int,
        cardiac_arrest: bool,
    ) -> Interpretation:
        """Generate interpretation and recommendations."""

        # Risk stratification
        if grace_score <= 108:
            risk_category = "Low"
            in_hospital_mortality = "<1%"
            six_month_mortality = "<3%"
            severity = Severity.MILD
            risk_level = RiskLevel.LOW
        elif grace_score <= 140:
            risk_category = "Intermediate"
            in_hospital_mortality = "1-3%"
            six_month_mortality = "3-8%"
            severity = Severity.MODERATE
            risk_level = RiskLevel.INTERMEDIATE
        else:
            risk_category = "High"
            in_hospital_mortality = ">3%"
            six_month_mortality = ">8%"
            severity = Severity.SEVERE
            risk_level = RiskLevel.HIGH

        if grace_score > 200:
            in_hospital_mortality = ">10%"
            six_month_mortality = ">20%"
            severity = Severity.CRITICAL
            risk_level = RiskLevel.VERY_HIGH

        summary = f"GRACE Score {grace_score}: {risk_category} risk"
        detail = f"Estimated in-hospital mortality: {in_hospital_mortality}. 6-month mortality: {six_month_mortality}."

        # Recommendations based on risk
        recommendations: tuple[str, ...]
        if risk_level in (RiskLevel.HIGH, RiskLevel.VERY_HIGH):
            recommendations = (
                "Early invasive strategy recommended (<24 hours)",
                "Consider immediate angiography if hemodynamically unstable",
                "Dual antiplatelet therapy + anticoagulation",
                "ICU/CCU admission",
                "Continuous telemetry monitoring",
            )
        elif risk_level == RiskLevel.INTERMEDIATE:
            recommendations = (
                "Invasive strategy within 72 hours",
                "Dual antiplatelet therapy",
                "Consider glycoprotein IIb/IIIa inhibitor",
                "CCU or step-down unit admission",
            )
        else:
            recommendations = (
                "Non-invasive risk stratification acceptable",
                "Consider stress testing if not revascularized",
                "Telemetry monitoring",
                "Early mobilization if stable",
            )

        warnings = []
        if killip_class >= 3:
            warnings.append("⚠️ Killip class ≥3: High risk of cardiogenic shock")
        if cardiac_arrest:
            warnings.append("⚠️ Cardiac arrest at presentation: Consider therapeutic hypothermia")
        if grace_score > 200:
            warnings.append("⚠️ Very high GRACE score: Consider early revascularization")

        return Interpretation(
            summary=summary,
            detail=detail,
            severity=severity,
            risk_level=risk_level,
            recommendations=recommendations,
            warnings=tuple(warnings),
            next_steps=(
                "Serial troponins",
                "ECG monitoring for dynamic changes",
                "Echocardiogram to assess LV function",
                "Cardiology consultation for revascularization planning",
            ),
        )
