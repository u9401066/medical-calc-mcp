"""
APACHE II Score Calculator

The Acute Physiology and Chronic Health Evaluation II (APACHE II) is a 
severity-of-disease classification system for ICU patients.

Reference:
    Knaus WA, Draper EA, Wagner DP, Zimmerman JE. APACHE II: a severity of 
    disease classification system. Crit Care Med. 1985;13(10):818-829.
    PMID: 3928249
    
Note:
    APACHE II has limitations and has been superseded by APACHE III, IV, and 
    other scoring systems (SOFA, SAPS, etc.) but remains widely used.
"""

from typing import Optional, Literal

from ..base import BaseCalculator
from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.units import Unit
from ...value_objects.reference import Reference
from ...value_objects.interpretation import Interpretation, Severity, RiskLevel
from ...value_objects.tool_keys import (
    LowLevelKey, 
    HighLevelKey, 
    Specialty, 
    ClinicalContext
)


ADMISSION_TYPE = Literal["nonoperative", "emergency_postoperative", "elective_postoperative"]


class ApacheIiCalculator(BaseCalculator):
    """
    APACHE II Score Calculator
    
    Estimates ICU mortality based on:
    - Acute Physiology Score (APS): 12 physiologic variables (worst in first 24h)
    - Age points
    - Chronic Health Points
    
    Score range: 0-71 (theoretical), 0-50+ in practice
    Higher scores indicate higher severity and mortality risk.
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="apache_ii",
                name="APACHE II Score",
                purpose="Estimate ICU mortality risk based on acute physiology and chronic health",
                input_params=[
                    "temperature", "mean_arterial_pressure", "heart_rate",
                    "respiratory_rate", "pao2_or_aado2", "fio2", 
                    "arterial_ph", "serum_sodium", "serum_potassium",
                    "serum_creatinine", "hematocrit", "wbc_count",
                    "gcs_score", "age", "chronic_health_conditions",
                    "admission_type", "acute_renal_failure"
                ],
                output_type="APACHE II Score (0-71) with estimated mortality risk"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.CRITICAL_CARE,
                    Specialty.ANESTHESIOLOGY,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.PULMONOLOGY,
                ),
                conditions=(
                    "ICU Mortality Prediction",
                    "Critical Illness",
                    "Severity Assessment",
                    "Acute Respiratory Failure",
                    "Sepsis",
                    "Multi-organ Failure",
                ),
                clinical_contexts=(
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.ICU_MANAGEMENT,
                    ClinicalContext.RISK_STRATIFICATION,
                ),
                clinical_questions=(
                    "How sick is this ICU patient?",
                    "What is the mortality risk?",
                    "Should we escalate care?",
                    "What is the prognosis?",
                    "Is this patient responding to treatment?",
                ),
                icd10_codes=(
                    "R65.20",  # Severe sepsis without septic shock
                    "R65.21",  # Severe sepsis with septic shock
                    "J96",     # Respiratory failure
                    "R57.0",   # Cardiogenic shock
                ),
                keywords=(
                    "APACHE", "APACHE II", "ICU", "mortality", "prognosis",
                    "severity", "critical care", "intensive care",
                    "acute physiology", "chronic health",
                )
            ),
            references=(
                Reference(
                    citation="Knaus WA, Draper EA, Wagner DP, Zimmerman JE. APACHE II: a severity of "
                             "disease classification system. Crit Care Med. 1985;13(10):818-829.",
                    pmid="3928249",
                    year=1985
                ),
            ),
            version="1.0.0",
            validation_status="validated"
        )
    
    def calculate(
        self,
        # Vital signs
        temperature: float,  # °C (rectal)
        mean_arterial_pressure: float,  # mmHg
        heart_rate: float,  # bpm
        respiratory_rate: float,  # breaths/min
        # Oxygenation
        fio2: float,  # fraction (0.21-1.0)
        pao2: Optional[float] = None,  # mmHg (use if FiO2 < 0.5)
        aado2: Optional[float] = None,  # mmHg (use if FiO2 >= 0.5)
        # Labs
        arterial_ph: float = 7.40,
        serum_sodium: float = 140.0,  # mEq/L
        serum_potassium: float = 4.0,  # mEq/L
        serum_creatinine: float = 1.0,  # mg/dL
        hematocrit: float = 40.0,  # %
        wbc_count: float = 10.0,  # ×10³/µL
        # Neurologic
        gcs_score: int = 15,  # Glasgow Coma Scale (3-15)
        # Demographics
        age: int = 50,  # years
        # Chronic health
        chronic_health_conditions: tuple = (),  # liver, cardiovascular, respiratory, renal, immunocompromised
        admission_type: ADMISSION_TYPE = "nonoperative",
        acute_renal_failure: bool = False
    ) -> ScoreResult:
        """
        Calculate APACHE II Score.
        
        Args:
            temperature: Core temperature in °C
            mean_arterial_pressure: MAP in mmHg
            heart_rate: Heart rate in bpm
            respiratory_rate: RR in breaths/min
            fio2: Fraction of inspired oxygen (0.21-1.0)
            pao2: Arterial PO2 in mmHg (use if FiO2 < 0.5)
            aado2: A-a gradient in mmHg (use if FiO2 >= 0.5)
            arterial_ph: Arterial blood pH
            serum_sodium: Sodium in mEq/L
            serum_potassium: Potassium in mEq/L
            serum_creatinine: Creatinine in mg/dL
            hematocrit: Hematocrit in %
            wbc_count: WBC count in ×10³/µL
            gcs_score: Glasgow Coma Scale (3-15)
            age: Age in years
            chronic_health_conditions: Tuple of conditions (liver, cardiovascular, 
                                       respiratory, renal, immunocompromised)
            admission_type: nonoperative, emergency_postoperative, or elective_postoperative
            acute_renal_failure: Whether patient has acute renal failure
            
        Returns:
            ScoreResult with APACHE II score and mortality estimate
        """
        # Validate inputs
        if gcs_score < 3 or gcs_score > 15:
            raise ValueError("GCS must be between 3 and 15")
        if fio2 < 0.21 or fio2 > 1.0:
            raise ValueError("FiO2 must be between 0.21 and 1.0")
        
        # Calculate component scores
        aps_breakdown = {}
        
        # Temperature
        temp_points = self._score_temperature(temperature)
        aps_breakdown["temperature"] = temp_points
        
        # MAP
        map_points = self._score_map(mean_arterial_pressure)
        aps_breakdown["map"] = map_points
        
        # Heart rate
        hr_points = self._score_heart_rate(heart_rate)
        aps_breakdown["heart_rate"] = hr_points
        
        # Respiratory rate
        rr_points = self._score_respiratory_rate(respiratory_rate)
        aps_breakdown["respiratory_rate"] = rr_points
        
        # Oxygenation
        oxy_points = self._score_oxygenation(fio2, pao2, aado2)
        aps_breakdown["oxygenation"] = oxy_points
        
        # Arterial pH
        ph_points = self._score_ph(arterial_ph)
        aps_breakdown["ph"] = ph_points
        
        # Sodium
        na_points = self._score_sodium(serum_sodium)
        aps_breakdown["sodium"] = na_points
        
        # Potassium
        k_points = self._score_potassium(serum_potassium)
        aps_breakdown["potassium"] = k_points
        
        # Creatinine
        cr_points = self._score_creatinine(serum_creatinine, acute_renal_failure)
        aps_breakdown["creatinine"] = cr_points
        
        # Hematocrit
        hct_points = self._score_hematocrit(hematocrit)
        aps_breakdown["hematocrit"] = hct_points
        
        # WBC
        wbc_points = self._score_wbc(wbc_count)
        aps_breakdown["wbc"] = wbc_points
        
        # GCS (15 - GCS)
        gcs_points = 15 - gcs_score
        aps_breakdown["gcs"] = gcs_points
        
        # Total APS
        aps_total = sum(aps_breakdown.values())
        
        # Age points
        age_points = self._score_age(age)
        
        # Chronic health points
        chronic_points = self._score_chronic_health(
            chronic_health_conditions, admission_type
        )
        
        # Total APACHE II
        total_score = aps_total + age_points + chronic_points
        
        # Get mortality estimate
        mortality_estimate = self._estimate_mortality(total_score)
        
        # Get interpretation
        interpretation = self._get_interpretation(total_score, mortality_estimate)
        
        return ScoreResult(
            value=float(total_score),
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "temperature": temperature,
                "mean_arterial_pressure": mean_arterial_pressure,
                "heart_rate": heart_rate,
                "respiratory_rate": respiratory_rate,
                "fio2": fio2,
                "pao2": pao2,
                "aado2": aado2,
                "arterial_ph": arterial_ph,
                "serum_sodium": serum_sodium,
                "serum_potassium": serum_potassium,
                "serum_creatinine": serum_creatinine,
                "hematocrit": hematocrit,
                "wbc_count": wbc_count,
                "gcs_score": gcs_score,
                "age": age,
                "chronic_health_conditions": chronic_health_conditions,
                "admission_type": admission_type,
                "acute_renal_failure": acute_renal_failure
            },
            calculation_details={
                "aps_total": aps_total,
                "aps_breakdown": aps_breakdown,
                "age_points": age_points,
                "chronic_health_points": chronic_points,
                "total_score": total_score,
                "estimated_mortality_percent": mortality_estimate
            },
            notes=[
                "Use worst values in first 24 hours of ICU admission",
                "GCS: if sedated, use estimated pre-sedation GCS or document as sedated",
                "Mortality estimates are approximate; actual outcomes vary by diagnosis",
                "APACHE II has been superseded but remains widely used",
            ]
        )
    
    def _score_temperature(self, temp: float) -> int:
        """Score temperature (°C)"""
        if temp >= 41 or temp <= 29.9:
            return 4
        elif temp >= 39 or temp <= 31.9:
            return 3 if temp >= 39 else 3
        elif temp >= 38.5 or temp <= 33.9:
            return 1 if temp >= 38.5 else (2 if temp <= 33.9 else 1)
        elif temp < 34:
            return 2
        elif temp >= 36 and temp <= 38.4:
            return 0
        elif temp >= 34 and temp <= 35.9:
            return 1
        return 0
    
    def _score_map(self, map_: float) -> int:
        """Score mean arterial pressure (mmHg)"""
        if map_ >= 160 or map_ <= 49:
            return 4
        elif map_ >= 130 or map_ <= 69:
            return 2
        elif map_ >= 110:
            return 2
        elif map_ >= 70 and map_ <= 109:
            return 0
        return 0
    
    def _score_heart_rate(self, hr: float) -> int:
        """Score heart rate (bpm)"""
        if hr >= 180 or hr <= 39:
            return 4
        elif hr >= 140 or hr <= 54:
            return 3 if hr >= 140 else 2
        elif hr >= 110 or hr <= 69:
            return 2 if hr >= 110 else 0
        elif hr >= 70 and hr <= 109:
            return 0
        return 0
    
    def _score_respiratory_rate(self, rr: float) -> int:
        """Score respiratory rate (breaths/min)"""
        if rr >= 50 or rr <= 5:
            return 4
        elif rr >= 35 or rr <= 9:
            return 3 if rr >= 35 else (2 if rr <= 9 else 1)
        elif rr >= 25 or rr == 10 or rr == 11:
            return 1
        elif rr >= 12 and rr <= 24:
            return 0
        return 0
    
    def _score_oxygenation(
        self, fio2: float, pao2: Optional[float], aado2: Optional[float]
    ) -> int:
        """Score oxygenation based on FiO2, PaO2, or A-aDO2"""
        if fio2 >= 0.5:
            # Use A-aDO2
            if aado2 is None:
                return 0  # Assume normal if not provided
            if aado2 >= 500:
                return 4
            elif aado2 >= 350:
                return 3
            elif aado2 >= 200:
                return 2
            else:
                return 0
        else:
            # Use PaO2
            if pao2 is None:
                return 0  # Assume normal if not provided
            if pao2 < 55:
                return 4
            elif pao2 < 61:
                return 3
            elif pao2 < 70:
                return 1
            else:
                return 0
    
    def _score_ph(self, ph: float) -> int:
        """Score arterial pH"""
        if ph >= 7.70 or ph < 7.15:
            return 4
        elif ph >= 7.60 or ph < 7.25:
            return 3
        elif ph >= 7.50 or ph < 7.33:
            return 2 if ph >= 7.50 else 2
        elif ph >= 7.33 and ph <= 7.49:
            return 0
        return 0
    
    def _score_sodium(self, na: float) -> int:
        """Score serum sodium (mEq/L)"""
        if na >= 180 or na <= 110:
            return 4
        elif na >= 160 or na <= 119:
            return 3
        elif na >= 155 or na <= 129:
            return 2
        elif na >= 150 or na <= 134:
            return 1
        elif na >= 130 and na <= 149:
            return 0
        return 0
    
    def _score_potassium(self, k: float) -> int:
        """Score serum potassium (mEq/L)"""
        if k >= 7.0 or k < 2.5:
            return 4
        elif k >= 6.0:
            return 3
        elif k >= 5.5 or k < 3.0:
            return 2 if k >= 5.5 else 2
        elif k >= 3.0 and k < 3.5:
            return 1
        elif k >= 3.5 and k < 5.5:
            return 0
        return 0
    
    def _score_creatinine(self, cr: float, arf: bool) -> int:
        """Score serum creatinine (mg/dL) - doubled for acute renal failure"""
        if cr >= 3.5:
            return 8 if arf else 4
        elif cr >= 2.0:
            return 6 if arf else 3
        elif cr >= 1.5:
            return 4 if arf else 2
        elif cr < 0.6:
            return 2
        else:
            return 0
    
    def _score_hematocrit(self, hct: float) -> int:
        """Score hematocrit (%)"""
        if hct >= 60 or hct < 20:
            return 4
        elif hct >= 50 or hct < 30:
            return 2
        elif hct >= 46 and hct < 50:
            return 1
        elif hct >= 30 and hct < 46:
            return 0
        return 0
    
    def _score_wbc(self, wbc: float) -> int:
        """Score WBC count (×10³/µL)"""
        if wbc >= 40 or wbc < 1:
            return 4
        elif wbc >= 20 or wbc < 3:
            return 2
        elif wbc >= 15:
            return 1
        elif wbc >= 3 and wbc < 15:
            return 0
        return 0
    
    def _score_age(self, age: int) -> int:
        """Score age in years"""
        if age < 45:
            return 0
        elif age < 55:
            return 2
        elif age < 65:
            return 3
        elif age < 75:
            return 5
        else:
            return 6
    
    def _score_chronic_health(
        self, conditions: tuple, admission_type: str
    ) -> int:
        """Score chronic health conditions"""
        if not conditions:
            return 0
        
        # Any severe chronic condition present
        if admission_type == "elective_postoperative":
            return 2
        else:  # nonoperative or emergency_postoperative
            return 5
    
    def _estimate_mortality(self, score: int) -> float:
        """Estimate hospital mortality based on APACHE II score"""
        # Approximate mortality curve from original publication
        if score <= 4:
            return 4.0
        elif score <= 9:
            return 8.0
        elif score <= 14:
            return 15.0
        elif score <= 19:
            return 25.0
        elif score <= 24:
            return 40.0
        elif score <= 29:
            return 55.0
        elif score <= 34:
            return 75.0
        else:
            return 85.0
    
    def _get_interpretation(self, score: int, mortality: float) -> Interpretation:
        """Get clinical interpretation for APACHE II score"""
        
        if score <= 9:
            severity = Severity.MILD
            risk_level = RiskLevel.LOW
            stage = "Low severity"
        elif score <= 14:
            severity = Severity.MODERATE
            risk_level = RiskLevel.INTERMEDIATE
            stage = "Moderate severity"
        elif score <= 24:
            severity = Severity.SEVERE
            risk_level = RiskLevel.HIGH
            stage = "High severity"
        else:
            severity = Severity.CRITICAL
            risk_level = RiskLevel.VERY_HIGH
            stage = "Critical severity"
        
        recommendations = [
            "Reassess APACHE II daily to track trajectory",
            "Optimize all organ support",
        ]
        warnings = []
        
        if score >= 25:
            recommendations.extend([
                "Goals of care discussion with family",
                "Consider palliative care consultation",
                "Intensive monitoring and support",
            ])
            warnings.append("Estimated mortality >50%")
        elif score >= 15:
            recommendations.extend([
                "Aggressive treatment optimization",
                "Consider escalation of care if not improving",
            ])
        
        return Interpretation(
            summary=f"APACHE II Score {score}: {stage} (estimated mortality {mortality:.0f}%)",
            detail=f"Total APACHE II score of {score} points corresponds to approximately "
                   f"{mortality:.0f}% hospital mortality risk in the original validation cohort.",
            severity=severity,
            risk_level=risk_level,
            stage=stage,
            stage_description=f"APACHE II {score} points",
            recommendations=tuple(recommendations),
            warnings=tuple(warnings) if warnings else None,
            next_steps=(
                "Continue intensive monitoring",
                "Optimize organ support",
                "Daily reassessment for trajectory",
            )
        )
