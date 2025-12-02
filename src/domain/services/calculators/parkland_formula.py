"""
Parkland Formula Calculator (Burn Fluid Resuscitation)

Calculates crystalloid fluid requirements for burn resuscitation
during the first 24 hours.

References:
    Baxter CR, Shires T. Physiological response to crystalloid resuscitation
    of severe burns. Ann N Y Acad Sci. 1968;150(3):874-894.
    DOI: 10.1111/j.1749-6632.1968.tb14738.x
    PMID: 4973463
    
    Baxter CR. Fluid volume and electrolyte changes of the early
    postburn period. Clin Plast Surg. 1974;1(4):693-703.
    PMID: 4609676
    
    ISBI Practice Guidelines Committee. ISBI Practice Guidelines for
    Burn Care. Burns. 2016;42(5):953-1021.
    DOI: 10.1016/j.burns.2016.05.013
    PMID: 27542292
    
    Greenhalgh DG. Burn resuscitation: The results of the ISBI/ABA
    survey. Burns. 2010;36(2):176-182.
    DOI: 10.1016/j.burns.2009.09.004
    PMID: 20018449
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
    ClinicalContext,
)


class ParklandFormulaCalculator(BaseCalculator):
    """
    Parkland Formula Calculator for Burn Resuscitation
    
    Estimates crystalloid (Lactated Ringer's) requirements for the first
    24 hours after a major burn injury.
    
    Formula (Parkland/Baxter):
        Total fluid = 4 mL × body weight (kg) × %TBSA burned
        
    Administration:
        - First 8 hours: 50% of total (from time of burn, not admission)
        - Next 16 hours: remaining 50%
        
    Goal:
        - Urine output 0.5-1.0 mL/kg/hr (adults)
        - Urine output 1.0-1.5 mL/kg/hr (children)
        - Titrate fluids to UOP, not formula
        
    Modified Formulas:
        - Modified Brooke: 2 mL × kg × %TBSA (some centers)
        - Rule of 10: For quick estimation in field
        
    TBSA Estimation:
        - Rule of 9s (adults)
        - Lund-Browder chart (more accurate, especially pediatrics)
        - Palm = ~1% TBSA
        
    Inclusion Criteria:
        - Adults: >20% TBSA burns
        - Children: >10% TBSA burns
        - Electrical or inhalation injury
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="parkland_formula",
                name="Parkland Formula (Burn Resuscitation)",
                purpose="Calculate crystalloid fluid requirements for burn resuscitation",
                input_params=["weight_kg", "tbsa_percent", "hours_since_burn"],
                output_type="Fluid volume (mL) with infusion rate (mL/hr)"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.SURGERY,
                    Specialty.CRITICAL_CARE,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.ANESTHESIOLOGY,
                    Specialty.PEDIATRICS,
                ),
                conditions=(
                    "Burns",
                    "Thermal injury",
                    "Burn resuscitation",
                    "Fluid resuscitation",
                    "Major burns",
                    "Pediatric burns",
                ),
                clinical_contexts=(
                    ClinicalContext.TREATMENT_DECISION,
                    ClinicalContext.FLUID_MANAGEMENT,
                    ClinicalContext.ICU_MANAGEMENT,
                ),
                clinical_questions=(
                    "How much fluid does this burn patient need?",
                    "What is the Parkland formula?",
                    "How do I resuscitate a burn patient?",
                    "What rate should I run fluids for burns?",
                    "How do I calculate burn fluid requirements?",
                ),
                icd10_codes=(
                    "T20-T32",  # Burns
                    "T31",      # Burns classified by extent
                ),
            ),
            references=(
                Reference(
                    citation=(
                        "Baxter CR, Shires T. Physiological response to crystalloid "
                        "resuscitation of severe burns. Ann N Y Acad Sci. 1968;150(3):874-894."
                    ),
                    doi="10.1111/j.1749-6632.1968.tb14738.x",
                    pmid="4973463",
                    year=1968,
                ),
                Reference(
                    citation=(
                        "ISBI Practice Guidelines Committee. ISBI Practice Guidelines for "
                        "Burn Care. Burns. 2016;42(5):953-1021."
                    ),
                    doi="10.1016/j.burns.2016.05.013",
                    pmid="27542292",
                    year=2016,
                ),
                Reference(
                    citation=(
                        "Greenhalgh DG. Burn resuscitation: The results of the ISBI/ABA "
                        "survey. Burns. 2010;36(2):176-182."
                    ),
                    doi="10.1016/j.burns.2009.09.004",
                    pmid="20018449",
                    year=2010,
                ),
            ),
        )
    
    def calculate(
        self,
        weight_kg: float,
        tbsa_percent: float,
        hours_since_burn: float = 0,
        is_pediatric: bool = False,
    ) -> ScoreResult:
        """
        Calculate burn fluid resuscitation using Parkland formula.
        
        Args:
            weight_kg: Body weight in kg (5-300)
            tbsa_percent: Total body surface area burned (%) (1-100)
            hours_since_burn: Hours elapsed since injury (0-24)
            is_pediatric: If True, use pediatric targets
                
        Returns:
            ScoreResult with fluid volumes and rates
            
        Raises:
            ValueError: If parameters are out of valid range
        """
        # Validate inputs
        if not 5 <= weight_kg <= 300:
            raise ValueError(f"Weight must be 5-300 kg, got {weight_kg}")
        if not 1 <= tbsa_percent <= 100:
            raise ValueError(f"TBSA must be 1-100%, got {tbsa_percent}")
        if not 0 <= hours_since_burn <= 24:
            raise ValueError(f"Hours since burn must be 0-24, got {hours_since_burn}")
        
        # Calculate total 24-hour fluid requirement
        # Parkland: 4 mL/kg/%TBSA
        total_24hr = 4.0 * weight_kg * tbsa_percent
        
        # Modified Brooke for comparison: 2 mL/kg/%TBSA
        brooke_24hr = 2.0 * weight_kg * tbsa_percent
        
        # First 8 hours: 50% of total
        first_8hr = total_24hr * 0.5
        
        # Next 16 hours: remaining 50%
        next_16hr = total_24hr * 0.5
        
        # Calculate remaining fluids based on time since burn
        if hours_since_burn < 8:
            # Still in first 8-hour period
            hours_remaining_first = 8 - hours_since_burn
            hours_remaining_second = 16
            fluid_remaining_first = first_8hr  # Assume starting fresh for calculation
            
            # Adjust if partially through first period
            if hours_since_burn > 0:
                # Calculate what should have been given by now
                expected_given = (hours_since_burn / 8) * first_8hr
                # Remaining in first 8 hours
                fluid_remaining_first = first_8hr - expected_given
                
            rate_now = fluid_remaining_first / hours_remaining_first if hours_remaining_first > 0 else first_8hr / 8
            rate_first_8 = first_8hr / 8
            rate_next_16 = next_16hr / 16
        else:
            # In second period (8-24 hours)
            hours_remaining_first = 0
            hours_remaining_second = 24 - hours_since_burn
            fluid_remaining_first = 0
            
            hours_into_second = hours_since_burn - 8
            expected_given_second = (hours_into_second / 16) * next_16hr
            fluid_remaining_second = next_16hr - expected_given_second
            
            rate_now = fluid_remaining_second / hours_remaining_second if hours_remaining_second > 0 else next_16hr / 16
            rate_first_8 = first_8hr / 8  # For reference
            rate_next_16 = next_16hr / 16
        
        # Urine output targets
        if is_pediatric:
            uop_target_low = weight_kg * 1.0  # 1.0 mL/kg/hr
            uop_target_high = weight_kg * 1.5  # 1.5 mL/kg/hr
        else:
            uop_target_low = weight_kg * 0.5  # 0.5 mL/kg/hr
            uop_target_high = weight_kg * 1.0  # 1.0 mL/kg/hr
        
        # Determine severity based on TBSA
        if tbsa_percent >= 50:
            severity_category = "Massive burn"
        elif tbsa_percent >= 30:
            severity_category = "Major burn"
        elif tbsa_percent >= 20:
            severity_category = "Moderate-major burn"
        elif tbsa_percent >= 10:
            severity_category = "Moderate burn"
        else:
            severity_category = "Minor burn"
        
        # Get interpretation
        interpretation = self._get_interpretation(
            total_24hr, tbsa_percent, weight_kg, is_pediatric
        )
        
        return ScoreResult(
            tool_id=self.tool_id,
            tool_name=self.name,
            value=round(total_24hr),
            unit=Unit.ML,
            interpretation=interpretation,
            references=self.references,
            calculation_details={
                "weight_kg": weight_kg,
                "tbsa_percent": tbsa_percent,
                "hours_since_burn": hours_since_burn,
                "is_pediatric": is_pediatric,
                "severity_category": severity_category,
                "formula": f"4 mL × {weight_kg} kg × {tbsa_percent}% = {round(total_24hr)} mL",
                "total_24hr_ml": round(total_24hr),
                "first_8hr": {
                    "volume_ml": round(first_8hr),
                    "rate_ml_hr": round(rate_first_8),
                    "note": "Give in first 8 hours FROM TIME OF BURN",
                },
                "next_16hr": {
                    "volume_ml": round(next_16hr),
                    "rate_ml_hr": round(rate_next_16),
                },
                "current_recommendation": {
                    "hours_elapsed": hours_since_burn,
                    "suggested_rate_ml_hr": round(rate_now) if hours_since_burn < 24 else 0,
                },
                "urine_output_target": {
                    "low_ml_hr": round(uop_target_low, 1),
                    "high_ml_hr": round(uop_target_high, 1),
                    "note": "TITRATE to UOP, not formula",
                },
                "comparison": {
                    "parkland_4ml": round(total_24hr),
                    "modified_brooke_2ml": round(brooke_24hr),
                },
                "fluid_type": "Lactated Ringer's (preferred) or Normal Saline",
            },
        )
    
    def _get_interpretation(
        self, 
        total_fluid: float, 
        tbsa: float, 
        weight: float,
        is_pediatric: bool
    ) -> Interpretation:
        """Generate interpretation based on burn severity and fluid needs"""
        
        # Classify severity
        if tbsa >= 50:
            burn_severity = "Massive burn (≥50% TBSA)"
            severity = Severity.CRITICAL
            transfer_note = "BURN CENTER TRANSFER ESSENTIAL"
        elif tbsa >= 30:
            burn_severity = "Major burn (30-49% TBSA)"
            severity = Severity.CRITICAL
            transfer_note = "Burn center transfer recommended"
        elif tbsa >= 20:
            burn_severity = "Moderate-major burn (20-29% TBSA)"
            severity = Severity.SEVERE
            transfer_note = "Consider burn center transfer"
        elif tbsa >= 10:
            burn_severity = "Moderate burn (10-19% TBSA)"
            severity = Severity.MODERATE
            transfer_note = "Evaluate need for transfer based on depth and location"
        else:
            burn_severity = "Minor burn (<10% TBSA)"
            severity = Severity.MILD
            transfer_note = "Usually manageable without burn center"
        
        # Build recommendations
        base_recommendations = [
            f"Total 24-hour fluid: {round(total_fluid)} mL Lactated Ringer's",
            "First 8 hours: 50% of total (from time of BURN, not admission)",
            "Next 16 hours: remaining 50%",
            f"Target UOP: {'1.0-1.5' if is_pediatric else '0.5-1.0'} mL/kg/hr",
            "TITRATE fluids to urine output, not formula",
        ]
        
        if tbsa >= 20:
            base_recommendations.extend([
                "Insert Foley catheter for strict I/O monitoring",
                "Place 2 large-bore IVs (through burn if necessary)",
                "Consider central line if peripheral access difficult",
            ])
        
        if tbsa >= 40:
            base_recommendations.extend([
                "Anticipate fluid creep - volumes often exceed Parkland",
                "Monitor for compartment syndrome (abdominal, extremity)",
                "Early intubation if inhalation injury suspected",
            ])
        
        return Interpretation(
            summary=f"Parkland: {round(total_fluid)} mL/24hr - {burn_severity}",
            detail=(
                f"{tbsa}% TBSA burn in {weight} kg patient. "
                f"Parkland formula: 4 × {weight} × {tbsa} = {round(total_fluid)} mL "
                f"crystalloid over 24 hours. {transfer_note}. "
                f"This is a STARTING POINT - titrate to urine output."
            ),
            severity=severity,
            stage=burn_severity,
            stage_description=f"{tbsa}% TBSA, {round(total_fluid)} mL/24hr",
            recommendations=tuple(base_recommendations),
            warnings=(
                "Formula is STARTING POINT only - titrate to UOP",
                "Time starts from INJURY, not hospital arrival",
                "Fluid creep is common - may need more than calculated",
                "Over-resuscitation causes pulmonary edema, compartment syndrome",
                "Under-resuscitation causes shock and organ failure",
            ),
            next_steps=(
                "Establish IV access and begin fluids immediately",
                "Insert Foley catheter for hourly UOP monitoring",
                "Contact burn center for transfer consideration",
                "Assess for inhalation injury, carbon monoxide",
                "Tetanus prophylaxis, wound care after resuscitation stable",
            ),
        )
