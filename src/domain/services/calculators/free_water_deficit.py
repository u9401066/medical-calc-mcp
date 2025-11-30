"""
Free Water Deficit Calculator

Calculates the free water deficit for treatment of hypernatremia.

Reference:
    Adrogue HJ, Madias NE. Hypernatremia. N Engl J Med. 2000;342(20):1493-1499.
    DOI: 10.1056/NEJM200005183422006
    PMID: 10816188
    
    Sterns RH. Disorders of plasma sodium--causes, consequences, and correction.
    N Engl J Med. 2015;372(1):55-65.
    DOI: 10.1056/NEJMra1404489
    PMID: 25551526
    
    Lindner G, Funk GC. Hypernatremia in critically ill patients.
    J Crit Care. 2013;28(2):216.e11-20.
    DOI: 10.1016/j.jcrc.2012.05.001
    PMID: 22762930
"""

from typing import Literal, Optional

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
    ClinicalContext,
)


class FreeWaterDeficitCalculator(BaseCalculator):
    """
    Free Water Deficit Calculator
    
    Calculates the amount of free water needed to correct hypernatremia
    to a target sodium level.
    
    Formula:
        Free Water Deficit = TBW × ((Current Na / Target Na) - 1)
        
        Where TBW = Body Weight × Water Fraction
        
        Water Fraction by patient type:
        - Adult male: 0.60
        - Adult female: 0.50
        - Elderly male: 0.50
        - Elderly female: 0.45
        - Child: 0.60
        
    Important Considerations:
        - Correct sodium slowly: 0.5 mEq/L per hour, max 10-12 mEq/L per 24 hours
        - Rapid correction can cause cerebral edema
        - Account for ongoing free water losses
        - Add maintenance fluids to replacement
        - Reassess sodium frequently (q4-6h)
        
    Fluid Options:
        - D5W: 100% free water
        - 0.45% NaCl: ~50% free water
        - 0.225% NaCl: ~75% free water
        - 5% dextrose in 0.45% NaCl: ~50% free water
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="free_water_deficit",
                name="Free Water Deficit",
                purpose="Calculate free water deficit for hypernatremia treatment",
                input_params=["current_sodium", "target_sodium", "weight_kg", "patient_type"],
                output_type="Free water deficit (L) with correction rate guidance"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.NEPHROLOGY,
                    Specialty.CRITICAL_CARE,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.GERIATRICS,
                ),
                conditions=(
                    "Hypernatremia",
                    "Dehydration",
                    "Diabetes insipidus",
                    "Hyperosmolar state",
                    "Free water loss",
                    "Altered mental status",
                ),
                clinical_contexts=(
                    ClinicalContext.TREATMENT_DECISION,
                    ClinicalContext.FLUID_MANAGEMENT,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "How much free water does this patient need?",
                    "How should I correct this hypernatremia?",
                    "What rate should I give fluids for hypernatremia?",
                    "What is the free water deficit?",
                ),
                icd10_codes=("E87.0",),
                keywords=(
                    "free water deficit", "hypernatremia", "sodium correction",
                    "dehydration", "diabetes insipidus", "hyperosmolality",
                    "fluid replacement", "D5W", "electrolyte",
                ),
            ),
            references=self._get_references(),
        )
    
    def _get_references(self) -> tuple[Reference, ...]:
        return (
            Reference(
                citation="Adrogue HJ, Madias NE. Hypernatremia. N Engl J Med. 2000;342(20):1493-1499.",
                doi="10.1056/NEJM200005183422006",
                pmid="10816188",
                year=2000,
            ),
            Reference(
                citation="Sterns RH. Disorders of plasma sodium--causes, consequences, and correction. N Engl J Med. 2015;372(1):55-65.",
                doi="10.1056/NEJMra1404489",
                pmid="25551526",
                year=2015,
            ),
            Reference(
                citation="Lindner G, Funk GC. Hypernatremia in critically ill patients. J Crit Care. 2013;28(2):216.e11-20.",
                doi="10.1016/j.jcrc.2012.05.001",
                pmid="22762930",
                year=2013,
            ),
        )
    
    def calculate(
        self,
        current_sodium: float,
        weight_kg: float,
        target_sodium: float = 140.0,
        patient_type: Literal["adult_male", "adult_female", "elderly_male", "elderly_female", "child"] = "adult_male",
        correction_time_hours: int = 24,
    ) -> ScoreResult:
        """
        Calculate free water deficit.
        
        Args:
            current_sodium: Current serum sodium (mEq/L)
            weight_kg: Body weight (kg)
            target_sodium: Target sodium (mEq/L), default 140
            patient_type: Patient category for TBW calculation
            correction_time_hours: Time over which to correct (hours)
            
        Returns:
            ScoreResult with free water deficit and infusion rate
        """
        # Validate inputs
        if current_sodium < 145 or current_sodium > 200:
            raise ValueError(f"Sodium {current_sodium} mEq/L is outside hypernatremia range. Use for Na >145 mEq/L")
        if target_sodium < 135 or target_sodium > 145:
            raise ValueError(f"Target sodium {target_sodium} mEq/L should be 135-145 mEq/L")
        if current_sodium <= target_sodium:
            raise ValueError(f"Current sodium ({current_sodium}) must be greater than target ({target_sodium})")
        if weight_kg < 2 or weight_kg > 300:
            raise ValueError(f"Weight {weight_kg} kg is outside expected range (2-300 kg)")
        if correction_time_hours < 1 or correction_time_hours > 72:
            raise ValueError(f"Correction time {correction_time_hours} hours should be 1-72 hours")
        
        # Water fraction by patient type
        water_fractions = {
            "adult_male": 0.60,
            "adult_female": 0.50,
            "elderly_male": 0.50,
            "elderly_female": 0.45,
            "child": 0.60,
        }
        
        water_fraction = water_fractions.get(patient_type, 0.60)
        
        # Calculate Total Body Water
        tbw = weight_kg * water_fraction
        
        # Calculate Free Water Deficit
        # FWD = TBW × ((Current Na / Target Na) - 1)
        free_water_deficit = tbw * ((current_sodium / target_sodium) - 1)
        free_water_deficit = round(free_water_deficit, 1)
        
        # Calculate sodium change
        sodium_change = current_sodium - target_sodium
        
        # Check rate of correction (should be ≤10-12 mEq/L per 24 hours)
        rate_per_24h = sodium_change * (24 / correction_time_hours)
        safe_correction = rate_per_24h <= 12
        
        # Calculate infusion rate
        infusion_rate_ml_hr = (free_water_deficit * 1000) / correction_time_hours
        infusion_rate_ml_hr = round(infusion_rate_ml_hr, 0)
        
        # Generate interpretation
        interpretation = self._interpret_deficit(
            current_sodium, target_sodium, free_water_deficit, 
            rate_per_24h, safe_correction, correction_time_hours
        )
        
        # Build calculation details
        details = {
            "Current_sodium": f"{current_sodium} mEq/L",
            "Target_sodium": f"{target_sodium} mEq/L",
            "Sodium_change_needed": f"{sodium_change:.1f} mEq/L",
            "Weight": f"{weight_kg} kg",
            "Patient_type": patient_type.replace("_", " ").title(),
            "Water_fraction": f"{water_fraction * 100:.0f}%",
            "Total_Body_Water": f"{tbw:.1f} L",
            "Free_water_deficit": f"{free_water_deficit:.1f} L",
            "Correction_time": f"{correction_time_hours} hours",
            "Infusion_rate_D5W": f"{infusion_rate_ml_hr:.0f} mL/hour",
            "Correction_rate": f"{rate_per_24h:.1f} mEq/L per 24 hours",
        }
        
        return ScoreResult(
            value=free_water_deficit,
            unit=Unit.L,
            interpretation=interpretation,
            references=self._get_references(),
            tool_id=self.tool_id,
            tool_name=self.metadata.name,
            raw_inputs={
                "current_sodium": current_sodium,
                "target_sodium": target_sodium,
                "weight_kg": weight_kg,
                "patient_type": patient_type,
                "correction_time_hours": correction_time_hours,
            },
            calculation_details=details,
            formula_used="FWD = TBW × ((Current Na / Target Na) - 1)",
        )
    
    def _interpret_deficit(
        self,
        current_sodium: float,
        target_sodium: float,
        free_water_deficit: float,
        rate_per_24h: float,
        safe_correction: bool,
        correction_time_hours: int,
    ) -> Interpretation:
        """Generate interpretation and recommendations."""
        
        # Assess severity of hypernatremia
        if current_sodium < 150:
            severity = Severity.MILD
            risk_level = RiskLevel.LOW
            na_severity = "mild"
        elif current_sodium < 155:
            severity = Severity.MODERATE
            risk_level = RiskLevel.INTERMEDIATE
            na_severity = "moderate"
        elif current_sodium < 160:
            severity = Severity.MODERATE
            risk_level = RiskLevel.INTERMEDIATE
            na_severity = "moderately severe"
        else:
            severity = Severity.SEVERE
            risk_level = RiskLevel.HIGH
            na_severity = "severe"
        
        summary = f"Free water deficit: {free_water_deficit:.1f} L for {na_severity} hypernatremia (Na {current_sodium})"
        
        if safe_correction:
            detail = f"Correction rate of {rate_per_24h:.1f} mEq/L per 24 hours is within safe limits (≤10-12 mEq/L per 24h)."
        else:
            detail = f"⚠️ Correction rate of {rate_per_24h:.1f} mEq/L per 24 hours may be too rapid. Recommended: ≤10-12 mEq/L per 24 hours."
        
        # Warnings
        warnings = []
        if not safe_correction:
            warnings.append("⚠️ Rate of correction may be too rapid - risk of cerebral edema")
            warnings.append(f"Consider extending correction time to ≥{int(24 * (current_sodium - target_sodium) / 12)} hours")
        
        if current_sodium >= 160:
            warnings.append("⚠️ Severe hypernatremia - high risk of neurological complications")
            warnings.append("Consider ICU admission for close monitoring")
        
        # Calculate fluid options
        d5w_volume = free_water_deficit * 1000  # mL
        half_ns_volume = free_water_deficit * 1000 * 2  # 0.45% NS is ~50% free water
        
        recommendations = [
            f"Total free water to replace: {free_water_deficit:.1f} L",
            f"If using D5W (100% free water): {d5w_volume:.0f} mL over {correction_time_hours} hours",
            f"If using 0.45% NS (~50% free water): {half_ns_volume:.0f} mL over {correction_time_hours} hours",
            "Add maintenance fluids and ongoing losses to replacement",
            "Check sodium every 4-6 hours during correction",
            "Adjust infusion rate based on repeat sodium levels",
        ]
        
        if current_sodium >= 155:
            recommendations.insert(0, "⚠️ Correct slowly: 0.5 mEq/L per hour, max 10-12 mEq/L per 24 hours")
        
        return Interpretation(
            summary=summary,
            detail=detail,
            severity=severity,
            risk_level=risk_level,
            recommendations=tuple(recommendations),
            warnings=tuple(warnings),
            next_steps=(
                "Identify and treat underlying cause of hypernatremia",
                "Monitor for neurological symptoms (lethargy, irritability, seizures)",
                "Consider central or nephrogenic diabetes insipidus if not responding",
                "Serial sodium checks every 4-6 hours",
            ),
        )
