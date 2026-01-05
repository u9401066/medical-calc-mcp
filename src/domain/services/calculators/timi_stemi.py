"""
TIMI Risk Score for STEMI

Predicts 30-day mortality in patients with ST-elevation myocardial infarction.

Reference:
    Morrow DA, Antman EM, Charlesworth A, et al.
    TIMI risk score for ST-elevation myocardial infarction:
    A convenient, bedside, clinical score for risk assessment at presentation.
    An Intravenous nPA for Treatment of Infarcting Myocardium Early II Trial substudy.
    Circulation. 2000;102(17):2031-2037.
    DOI: 10.1161/01.cir.102.17.2031
    PMID: 11044416
"""

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, RiskLevel, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class TimiStemiCalculator(BaseCalculator):
    """
    TIMI Risk Score for STEMI

    Predicts 30-day mortality in ST-elevation myocardial infarction.

    Risk Factors (each worth 1-3 points):
    - Age 65-74: 2 points; ≥75: 3 points
    - Diabetes, Hypertension, or Angina: 1 point
    - Systolic BP <100 mmHg: 3 points
    - Heart rate >100 bpm: 2 points
    - Killip class II-IV: 2 points
    - Weight <67 kg: 1 point
    - Anterior ST elevation or LBBB: 1 point
    - Time to treatment >4 hours: 1 point

    Total: 0-14 points

    30-day mortality by score:
    - 0: 0.8%
    - 1: 1.6%
    - 2: 2.2%
    - 3: 4.4%
    - 4: 7.3%
    - 5: 12.4%
    - 6: 16.1%
    - 7: 23.4%
    - 8: 26.8%
    - >8: 35.9%
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="timi_stemi",
                name="TIMI Risk Score for STEMI",
                purpose="Predict 30-day mortality in STEMI patients",
                input_params=[
                    "age_years",
                    "has_dm_htn_or_angina",
                    "systolic_bp_lt_100",
                    "heart_rate_gt_100",
                    "killip_class",
                    "weight_lt_67kg",
                    "anterior_ste_or_lbbb",
                    "time_to_treatment_gt_4h"
                ],
                output_type="TIMI STEMI score (0-14) with 30-day mortality risk"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.CARDIOLOGY,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.CRITICAL_CARE,
                    Specialty.INTERNAL_MEDICINE,
                ),
                conditions=(
                    "STEMI",
                    "ST-elevation Myocardial Infarction",
                    "Myocardial Infarction",
                    "Heart Attack",
                    "Acute Coronary Syndrome",
                    "ACS",
                ),
                clinical_contexts=(
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.TREATMENT_DECISION,
                ),
                clinical_questions=(
                    "What is the 30-day mortality risk for this STEMI?",
                    "What is the TIMI score for this heart attack?",
                    "Should this STEMI patient go to ICU?",
                    "How high risk is this MI?",
                ),
                icd10_codes=(
                    "I21.0",   # STEMI of anterior wall
                    "I21.1",   # STEMI of inferior wall
                    "I21.2",   # STEMI of other sites
                    "I21.3",   # STEMI of unspecified site
                ),
                keywords=(
                    "TIMI", "STEMI", "ST-elevation", "myocardial infarction",
                    "heart attack", "MI", "mortality", "risk score",
                    "reperfusion", "thrombolysis", "PCI",
                )
            ),
            references=(
                Reference(
                    citation="Morrow DA, Antman EM, Charlesworth A, et al. "
                             "TIMI risk score for ST-elevation myocardial infarction: "
                             "A convenient, bedside, clinical score for risk assessment at presentation. "
                             "Circulation. 2000;102(17):2031-2037.",
                    doi="10.1161/01.cir.102.17.2031",
                    pmid="11044416",
                    year=2000
                ),
            ),
            version="1.0.0",
            validation_status="validated"
        )

    def calculate(
        self,
        age_years: int,
        has_dm_htn_or_angina: bool,
        systolic_bp_lt_100: bool,
        heart_rate_gt_100: bool,
        killip_class: int,
        weight_lt_67kg: bool,
        anterior_ste_or_lbbb: bool,
        time_to_treatment_gt_4h: bool
    ) -> ScoreResult:
        """
        Calculate TIMI Risk Score for STEMI.

        Args:
            age_years: Patient age in years
            has_dm_htn_or_angina: Diabetes, hypertension, or angina history
            systolic_bp_lt_100: Systolic BP <100 mmHg
            heart_rate_gt_100: Heart rate >100 bpm
            killip_class: Killip classification (1-4)
                - 1: No heart failure
                - 2: Rales, JVD, or S3
                - 3: Pulmonary edema
                - 4: Cardiogenic shock
            weight_lt_67kg: Body weight <67 kg
            anterior_ste_or_lbbb: Anterior STE or LBBB on ECG
            time_to_treatment_gt_4h: Time to treatment >4 hours

        Returns:
            ScoreResult with TIMI STEMI score and 30-day mortality risk
        """
        # Validate inputs
        if killip_class < 1 or killip_class > 4:
            raise ValueError("Killip class must be 1-4")

        # Calculate age points
        if age_years >= 75:
            age_points = 3
        elif age_years >= 65:
            age_points = 2
        else:
            age_points = 0

        # Calculate other component points
        dm_htn_angina_points = 1 if has_dm_htn_or_angina else 0
        sbp_points = 3 if systolic_bp_lt_100 else 0
        hr_points = 2 if heart_rate_gt_100 else 0
        killip_points = 2 if killip_class >= 2 else 0
        weight_points = 1 if weight_lt_67kg else 0
        anterior_lbbb_points = 1 if anterior_ste_or_lbbb else 0
        time_points = 1 if time_to_treatment_gt_4h else 0

        # Total score
        score = (
            age_points + dm_htn_angina_points + sbp_points +
            hr_points + killip_points + weight_points +
            anterior_lbbb_points + time_points
        )

        # Get mortality risk
        mortality_30day = self._get_mortality_risk(score)

        # Get interpretation
        interpretation = self._get_interpretation(score, mortality_30day)

        return ScoreResult(
            value=float(score),
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "age_years": age_years,
                "has_dm_htn_or_angina": has_dm_htn_or_angina,
                "systolic_bp_lt_100": systolic_bp_lt_100,
                "heart_rate_gt_100": heart_rate_gt_100,
                "killip_class": killip_class,
                "weight_lt_67kg": weight_lt_67kg,
                "anterior_ste_or_lbbb": anterior_ste_or_lbbb,
                "time_to_treatment_gt_4h": time_to_treatment_gt_4h
            },
            calculation_details={
                "total_score": score,
                "max_possible": 14,
                "component_scores": {
                    "age": age_points,
                    "dm_htn_angina": dm_htn_angina_points,
                    "systolic_bp_lt_100": sbp_points,
                    "heart_rate_gt_100": hr_points,
                    "killip_class": killip_points,
                    "weight_lt_67kg": weight_points,
                    "anterior_ste_or_lbbb": anterior_lbbb_points,
                    "time_to_treatment_gt_4h": time_points
                },
                "mortality_30day": f"{mortality_30day}%",
                "killip_class": killip_class
            },
            notes=self._get_notes(score, killip_class)
        )

    def _get_mortality_risk(self, score: int) -> float:
        """
        Get 30-day mortality risk based on score.

        Data from InTIME-II trial substudy (Morrow 2000).
        """
        mortality_table = {
            0: 0.8,
            1: 1.6,
            2: 2.2,
            3: 4.4,
            4: 7.3,
            5: 12.4,
            6: 16.1,
            7: 23.4,
            8: 26.8
        }

        if score > 8:
            return 35.9
        return mortality_table.get(score, 35.9)

    def _get_interpretation(
        self,
        score: int,
        mortality: float
    ) -> Interpretation:
        """Get clinical interpretation based on score"""

        if score <= 2:
            return Interpretation(
                summary=f"Low Risk STEMI (TIMI {score})",
                detail=f"30-day mortality: {mortality}%. Favorable prognosis with reperfusion.",
                severity=Severity.MILD,
                risk_level=RiskLevel.LOW,
                stage="Low Risk",
                stage_description=f"TIMI STEMI {score}",
                recommendations=(
                    "Emergent reperfusion (primary PCI preferred)",
                    "Standard STEMI protocol",
                    "Dual antiplatelet therapy (DAPT)",
                    "Anticoagulation",
                    "Telemetry monitoring",
                ),
                next_steps=(
                    "Cardiac catheterization",
                    "Post-MI risk stratification",
                    "Cardiac rehabilitation referral",
                )
            )
        elif score <= 4:
            return Interpretation(
                summary=f"Intermediate Risk STEMI (TIMI {score})",
                detail=f"30-day mortality: {mortality}%. Moderate risk requiring close monitoring.",
                severity=Severity.MODERATE,
                risk_level=RiskLevel.INTERMEDIATE,
                stage="Intermediate Risk",
                stage_description=f"TIMI STEMI {score}",
                recommendations=(
                    "Emergent primary PCI",
                    "Consider CCU admission",
                    "DAPT + anticoagulation",
                    "Hemodynamic monitoring",
                    "Assess for mechanical complications",
                ),
                warnings=(
                    "Higher complication risk",
                    "Close monitoring for arrhythmias",
                ),
                next_steps=(
                    "Urgent cardiac catheterization",
                    "Echocardiography to assess LV function",
                    "Optimize medical therapy",
                )
            )
        elif score <= 6:
            return Interpretation(
                summary=f"High Risk STEMI (TIMI {score})",
                detail=f"30-day mortality: {mortality}%. High risk with significant mortality.",
                severity=Severity.MODERATE,
                risk_level=RiskLevel.HIGH,
                stage="High Risk",
                stage_description=f"TIMI STEMI {score}",
                recommendations=(
                    "Emergent primary PCI - do not delay",
                    "CCU/ICU admission mandatory",
                    "Consider mechanical circulatory support",
                    "Invasive hemodynamic monitoring",
                    "IABP or Impella consideration",
                ),
                warnings=(
                    "Significant 30-day mortality risk",
                    "High risk for cardiogenic shock",
                    "Monitor for ventricular arrhythmias",
                ),
                next_steps=(
                    "Multidisciplinary team (cardiology, cardiac surgery)",
                    "Early goals of care discussion if deteriorating",
                    "Family notification of serious condition",
                )
            )
        else:  # score > 6
            return Interpretation(
                summary=f"Very High Risk STEMI (TIMI {score})",
                detail=f"30-day mortality: {mortality}%. Very high mortality risk.",
                severity=Severity.SEVERE,
                risk_level=RiskLevel.VERY_HIGH,
                stage="Very High Risk",
                stage_description=f"TIMI STEMI {score}",
                recommendations=(
                    "Emergent primary PCI with hemodynamic support",
                    "ICU admission with continuous monitoring",
                    "Mechanical circulatory support (IABP, Impella, ECMO)",
                    "Vasopressor/inotrope support as needed",
                    "Early cardiac surgery consultation if needed",
                    "Goals of care discussion with family",
                ),
                warnings=(
                    "Very high mortality >20%",
                    "High probability of cardiogenic shock",
                    "Consider futility if multiple organ failure",
                ),
                next_steps=(
                    "Aggressive resuscitation if appropriate",
                    "Palliative care consultation if prognosis poor",
                    "Document advance directives",
                )
            )

    def _get_notes(self, score: int, killip_class: int) -> list[str]:
        """Get clinical notes"""
        notes = [
            "TIMI STEMI score validated in fibrinolytic-treated patients",
            "May underestimate risk in primary PCI era",
        ]

        if killip_class >= 3:
            notes.append(
                "Killip III-IV: Consider mechanical circulatory support"
            )

        if score >= 5:
            notes.append(
                "High-risk: Multidisciplinary approach recommended"
            )

        notes.append(
            "Door-to-balloon time <90 min remains critical"
        )

        return notes

