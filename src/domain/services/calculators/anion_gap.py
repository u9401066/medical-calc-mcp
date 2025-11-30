"""
Anion Gap Calculator

Calculates the serum anion gap for differential diagnosis of metabolic acidosis.
Includes albumin-corrected anion gap calculation.

Reference:
    Kraut JA, Madias NE. Serum anion gap: its uses and limitations in clinical 
    medicine. Clin J Am Soc Nephrol. 2007;2(1):162-174.
    DOI: 10.2215/CJN.03020906
    PMID: 17699401
    
    Figge J, Jabor A, Kazda A, Fencl V. Anion gap and hypoalbuminemia.
    Crit Care Med. 1998;26(11):1807-1810.
    PMID: 9824071
"""

from typing import Optional, Tuple

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


class AnionGapCalculator(BaseCalculator):
    """
    Anion Gap Calculator
    
    The anion gap (AG) is the difference between measured cations and anions
    in serum, used to classify metabolic acidosis.
    
    Formula:
        AG = Na⁺ - (Cl⁻ + HCO₃⁻)
        
        Normal range: 8-12 mEq/L (without K⁺)
        
    Corrected AG (for hypoalbuminemia):
        Corrected AG = AG + 2.5 × (4.0 - Albumin)
        
        Where albumin is in g/dL
    
    Clinical Application:
        - High AG (>12): MUDPILES (Methanol, Uremia, DKA, Propylene glycol,
                         INH/Iron, Lactic acidosis, Ethylene glycol, Salicylates)
        - Normal AG: GI or renal HCO₃⁻ loss, RTA
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="anion_gap",
                name="Anion Gap",
                purpose="Calculate serum anion gap for metabolic acidosis differential diagnosis",
                input_params=["sodium", "chloride", "bicarbonate", "albumin (optional)"],
                output_type="Anion Gap (mEq/L) with differential diagnosis"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.CRITICAL_CARE,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.NEPHROLOGY,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.ANESTHESIOLOGY,
                ),
                conditions=(
                    "Metabolic Acidosis",
                    "Diabetic Ketoacidosis",
                    "DKA",
                    "Lactic Acidosis",
                    "Toxic Ingestion",
                    "Uremia",
                    "Renal Tubular Acidosis",
                    "RTA",
                    "Acid-Base Disorder",
                ),
                clinical_contexts=(
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.ICU_MANAGEMENT,
                    ClinicalContext.MONITORING,
                    ClinicalContext.SEVERITY_ASSESSMENT,
                ),
                clinical_questions=(
                    "What type of metabolic acidosis does the patient have?",
                    "Is this a high anion gap or normal anion gap acidosis?",
                    "Should I suspect toxic ingestion?",
                    "What is causing the metabolic acidosis?",
                ),
                icd10_codes=("E87.2", "E10.10", "E11.10", "E87.4"),
                keywords=(
                    "anion gap", "AG", "metabolic acidosis", "HAGMA", "NAGMA",
                    "DKA", "lactic acidosis", "acid-base", "MUDPILES",
                )
            ),
            references=(
                Reference(
                    citation="Kraut JA, Madias NE. Serum anion gap: its uses and limitations "
                             "in clinical medicine. Clin J Am Soc Nephrol. 2007;2(1):162-174.",
                    doi="10.2215/CJN.03020906",
                    pmid="17699401",
                    year=2007
                ),
                Reference(
                    citation="Figge J, Jabor A, Kazda A, Fencl V. Anion gap and hypoalbuminemia. "
                             "Crit Care Med. 1998;26(11):1807-1810.",
                    pmid="9824071",
                    year=1998
                ),
            ),
            version="1.0.0",
            validation_status="validated"
        )
    
    def calculate(
        self,
        sodium: float,
        chloride: float,
        bicarbonate: float,
        albumin: Optional[float] = None,
        include_potassium: bool = False,
        potassium: Optional[float] = None,
    ) -> ScoreResult:
        """
        Calculate the anion gap.
        
        Args:
            sodium: Serum sodium in mEq/L (120-160)
            chloride: Serum chloride in mEq/L (80-120)
            bicarbonate: Serum bicarbonate (HCO₃⁻) in mEq/L (5-40)
            albumin: Serum albumin in g/dL (optional, for corrected AG)
            include_potassium: Whether to include K⁺ in calculation (rarely used)
            potassium: Serum potassium in mEq/L (if including K⁺)
            
        Returns:
            ScoreResult with anion gap and interpretation
        """
        # Validate inputs
        if not 120 <= sodium <= 160:
            raise ValueError("Sodium must be between 120 and 160 mEq/L")
        if not 80 <= chloride <= 120:
            raise ValueError("Chloride must be between 80 and 120 mEq/L")
        if not 5 <= bicarbonate <= 40:
            raise ValueError("Bicarbonate must be between 5 and 40 mEq/L")
        if albumin is not None and not 0.5 <= albumin <= 6.0:
            raise ValueError("Albumin must be between 0.5 and 6.0 g/dL")
        if include_potassium:
            if potassium is None:
                raise ValueError("Potassium required when include_potassium=True")
            if not 2.0 <= potassium <= 8.0:
                raise ValueError("Potassium must be between 2.0 and 8.0 mEq/L")
        
        # Calculate anion gap
        if include_potassium and potassium is not None:
            anion_gap = (sodium + potassium) - (chloride + bicarbonate)
            normal_range = (12, 20)  # Normal with K+
            formula_used = "AG = (Na⁺ + K⁺) - (Cl⁻ + HCO₃⁻)"
        else:
            anion_gap = sodium - (chloride + bicarbonate)
            normal_range = (8, 12)  # Normal without K+
            formula_used = "AG = Na⁺ - (Cl⁻ + HCO₃⁻)"
        
        anion_gap = round(anion_gap, 1)
        
        # Calculate corrected AG if albumin provided
        corrected_ag = None
        if albumin is not None:
            # Each 1 g/dL decrease in albumin from 4.0 decreases AG by 2.5
            corrected_ag = anion_gap + 2.5 * (4.0 - albumin)
            corrected_ag = round(corrected_ag, 1)
        
        # Determine interpretation
        ag_for_interpretation = corrected_ag if corrected_ag is not None else anion_gap
        interpretation = self._get_interpretation(
            ag_for_interpretation, 
            normal_range,
            corrected_ag is not None
        )
        
        # Build calculation details
        calc_details = {
            "anion_gap": anion_gap,
            "normal_range": f"{normal_range[0]}-{normal_range[1]} mEq/L",
            "include_potassium": include_potassium,
        }
        if corrected_ag is not None:
            calc_details["corrected_ag"] = corrected_ag
            calc_details["albumin_correction"] = round(2.5 * (4.0 - albumin), 1)
        
        return ScoreResult(
            value=corrected_ag if corrected_ag is not None else anion_gap,
            unit=Unit.MEQ_L,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "sodium": sodium,
                "chloride": chloride,
                "bicarbonate": bicarbonate,
                "albumin": albumin,
                "include_potassium": include_potassium,
                "potassium": potassium,
            },
            calculation_details=calc_details,
            formula_used=formula_used
        )
    
    def _get_interpretation(
        self, 
        ag: float, 
        normal_range: Tuple[int, int],
        is_corrected: bool
    ) -> Interpretation:
        """Get clinical interpretation based on anion gap value"""
        
        ag_type = "Corrected AG" if is_corrected else "Anion Gap"
        
        if ag > normal_range[1]:
            # High Anion Gap Metabolic Acidosis (HAGMA)
            if ag > 30:
                severity = Severity.CRITICAL
                severity_desc = "Severely elevated"
            elif ag > 20:
                severity = Severity.SEVERE
                severity_desc = "Significantly elevated"
            else:
                severity = Severity.MODERATE
                severity_desc = "Elevated"
            
            return Interpretation(
                summary=f"High Anion Gap Metabolic Acidosis (HAGMA) - {ag_type}: {ag} mEq/L",
                detail=f"{severity_desc} anion gap suggests accumulation of unmeasured anions. "
                       f"Consider MUDPILES: Methanol, Uremia, DKA/Ketoacidosis, "
                       f"Propylene glycol, INH/Iron, Lactic acidosis, Ethylene glycol, Salicylates.",
                severity=severity,
                stage="HAGMA",
                stage_description="High Anion Gap Metabolic Acidosis",
                recommendations=(
                    "Check lactate level",
                    "Check blood glucose and ketones",
                    "Check BUN/Creatinine for uremia",
                    "Consider toxicology screen if indicated",
                    "Calculate osmolar gap if toxic alcohol suspected",
                ),
                warnings=(
                    "High AG may indicate serious underlying condition",
                    "Urgent workup and treatment may be needed",
                ) if ag > 20 else None,
                next_steps=(
                    "Calculate Delta Ratio (ΔAG/ΔHCO₃⁻) to detect mixed disorders",
                    "Obtain arterial blood gas if not already done",
                    "Address underlying cause",
                )
            )
        elif ag < normal_range[0]:
            # Low anion gap
            return Interpretation(
                summary=f"Low Anion Gap - {ag_type}: {ag} mEq/L",
                detail="Low anion gap may be seen with hypoalbuminemia (if not corrected), "
                       "paraproteinemia (multiple myeloma), lithium toxicity, or laboratory error.",
                severity=Severity.MILD,
                stage="Low AG",
                stage_description="Low Anion Gap",
                recommendations=(
                    "Check serum albumin if not already done",
                    "Consider serum protein electrophoresis if paraprotein suspected",
                    "Verify lithium level if applicable",
                    "Repeat electrolytes to rule out lab error",
                ),
                next_steps=(
                    "Investigate cause of low anion gap",
                    "Use albumin-corrected AG if hypoalbuminemia present",
                )
            )
        else:
            # Normal anion gap
            return Interpretation(
                summary=f"Normal Anion Gap - {ag_type}: {ag} mEq/L",
                detail="Normal anion gap. If metabolic acidosis is present, consider "
                       "Normal Anion Gap Metabolic Acidosis (NAGMA) causes: "
                       "GI bicarbonate loss (diarrhea), renal tubular acidosis (RTA), "
                       "or dilutional acidosis (large volume NS resuscitation).",
                severity=Severity.NORMAL,
                stage="Normal",
                stage_description="Normal Anion Gap",
                recommendations=(
                    "If acidosis present, consider NAGMA causes",
                    "Check urine anion gap to differentiate GI vs renal cause",
                    "Monitor acid-base status",
                ),
                next_steps=(
                    "If HCO₃⁻ low with normal AG: calculate urine anion gap",
                    "UAG positive (>0): RTA",
                    "UAG negative (<0): GI loss (diarrhea)",
                )
            )
