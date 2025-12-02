"""
Delta Ratio (Delta Gap) Calculator

Calculates the delta ratio to identify mixed acid-base disorders in patients
with high anion gap metabolic acidosis.

Reference:
    Wrenn K. The delta (delta) gap: an approach to mixed acid-base disorders.
    Ann Emerg Med. 1990;19(11):1310-1313.
    DOI: 10.1016/s0196-0644(05)82292-9
    PMID: 2240729
    
    Rastegar A. Use of the DeltaAG/DeltaHCO3- ratio in the diagnosis of 
    mixed acid-base disorders. J Am Soc Nephrol. 2007;18(9):2429-2431.
    DOI: 10.1681/ASN.2006121408
    PMID: 17656478
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
    ClinicalContext
)


class DeltaRatioCalculator(BaseCalculator):
    """
    Delta Ratio (Delta Gap) Calculator
    
    The delta ratio compares the change in anion gap to the change in 
    bicarbonate to detect mixed acid-base disorders.
    
    Formula:
        Delta AG (ΔAG) = Measured AG - Normal AG (typically 12)
        Delta HCO₃⁻ (ΔHCO₃⁻) = Normal HCO₃⁻ (24) - Measured HCO₃⁻
        Delta Ratio = ΔAG / ΔHCO₃⁻
    
    Interpretation:
        - <1: Concurrent NAGMA (HCO₃⁻ loss > AG gain)
        - 1-2: Pure HAGMA (AG gain = HCO₃⁻ loss)
        - >2: Concurrent metabolic alkalosis (AG gain > HCO₃⁻ loss)
    
    Clinical Use:
        Only valid when anion gap is elevated (HAGMA present)
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="delta_ratio",
                name="Delta Ratio (Delta Gap)",
                purpose="Identify mixed acid-base disorders in high anion gap metabolic acidosis",
                input_params=["anion_gap", "bicarbonate", "normal_ag (optional)", "normal_hco3 (optional)"],
                output_type="Delta Ratio with mixed disorder interpretation"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.CRITICAL_CARE,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.NEPHROLOGY,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.PULMONOLOGY,
                    Specialty.ANESTHESIOLOGY,
                ),
                conditions=(
                    "Mixed Acid-Base Disorder",
                    "Metabolic Acidosis",
                    "High Anion Gap Metabolic Acidosis",
                    "HAGMA",
                    "Metabolic Alkalosis",
                    "Normal Anion Gap Metabolic Acidosis",
                    "NAGMA",
                ),
                clinical_contexts=(
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.ICU_MANAGEMENT,
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "Is there a mixed acid-base disorder?",
                    "Does this patient have concurrent metabolic alkalosis?",
                    "Is there a concurrent normal anion gap acidosis?",
                    "Is this a pure high anion gap metabolic acidosis?",
                ),
                icd10_codes=("E87.2", "E87.4", "E87.3"),
                keywords=(
                    "delta ratio", "delta gap", "mixed acid-base", "HAGMA", "NAGMA",
                    "metabolic alkalosis", "acid-base analysis", "anion gap",
                )
            ),
            references=(
                Reference(
                    citation="Wrenn K. The delta (delta) gap: an approach to mixed acid-base "
                             "disorders. Ann Emerg Med. 1990;19(11):1310-1313.",
                    doi="10.1016/s0196-0644(05)82292-9",
                    pmid="2240729",
                    year=1990
                ),
                Reference(
                    citation="Rastegar A. Use of the DeltaAG/DeltaHCO3- ratio in the diagnosis "
                             "of mixed acid-base disorders. J Am Soc Nephrol. 2007;18(9):2429-2431.",
                    doi="10.1681/ASN.2006121408",
                    pmid="17656478",
                    year=2007
                ),
            ),
            version="1.0.0",
            validation_status="validated"
        )
    
    def calculate(
        self,
        anion_gap: float,
        bicarbonate: float,
        normal_ag: float = 12.0,
        normal_hco3: float = 24.0,
    ) -> ScoreResult:
        """
        Calculate the delta ratio (delta gap).
        
        Args:
            anion_gap: Measured anion gap in mEq/L (use corrected AG if available)
            bicarbonate: Measured serum bicarbonate (HCO₃⁻) in mEq/L
            normal_ag: Normal anion gap baseline (default 12 mEq/L)
            normal_hco3: Normal bicarbonate baseline (default 24 mEq/L)
            
        Returns:
            ScoreResult with delta ratio and interpretation
        """
        # Validate inputs
        if not 0 <= anion_gap <= 50:
            raise ValueError("Anion gap must be between 0 and 50 mEq/L")
        if not 5 <= bicarbonate <= 40:
            raise ValueError("Bicarbonate must be between 5 and 40 mEq/L")
        if not 6 <= normal_ag <= 14:
            raise ValueError("Normal AG should be between 6 and 14 mEq/L")
        if not 22 <= normal_hco3 <= 26:
            raise ValueError("Normal HCO₃⁻ should be between 22 and 26 mEq/L")
        
        # Calculate delta values
        delta_ag = anion_gap - normal_ag
        delta_hco3 = normal_hco3 - bicarbonate
        
        # Check if HAGMA is present
        if delta_ag <= 0:
            # No elevated anion gap - delta ratio not applicable
            return ScoreResult(
                value=None,
                unit=Unit.RATIO,
                interpretation=Interpretation(
                    summary="Delta Ratio not applicable - No elevated anion gap",
                    detail=f"Anion gap ({anion_gap}) is not elevated above normal ({normal_ag}). "
                           f"Delta ratio is only meaningful when HAGMA is present.",
                    severity=Severity.NORMAL,
                    stage="N/A",
                    stage_description="Not applicable",
                    recommendations=(
                        "If metabolic acidosis present, this is NAGMA",
                        "Calculate urine anion gap to differentiate cause",
                        "Consider GI loss vs RTA",
                    ),
                    next_steps=(
                        "Check urine anion gap if acidosis present",
                        "Review clinical context for acidosis cause",
                    )
                ),
                references=list(self.references),
                tool_id=self.tool_id,
                tool_name=self.name,
                raw_inputs={
                    "anion_gap": anion_gap,
                    "bicarbonate": bicarbonate,
                    "normal_ag": normal_ag,
                    "normal_hco3": normal_hco3,
                },
                calculation_details={
                    "delta_ag": round(delta_ag, 1),
                    "delta_hco3": round(delta_hco3, 1),
                    "valid": False,
                    "reason": "Anion gap not elevated",
                },
                formula_used="Delta Ratio = ΔAG / ΔHCO₃⁻ (not applicable - AG not elevated)"
            )
        
        # Check for division issues
        if delta_hco3 <= 0:
            # Bicarbonate not decreased - unusual scenario
            return ScoreResult(
                value=None,
                unit=Unit.RATIO,
                interpretation=Interpretation(
                    summary="Delta Ratio not calculable - Bicarbonate not decreased",
                    detail=f"Bicarbonate ({bicarbonate}) is not decreased below normal ({normal_hco3}). "
                           f"This suggests metabolic alkalosis may be present.",
                    severity=Severity.MILD,
                    stage="Possible Met Alk",
                    stage_description="Possible metabolic alkalosis",
                    recommendations=(
                        "Elevated AG without low HCO₃⁻ suggests metabolic alkalosis",
                        "Check for vomiting, NG suction, diuretics",
                        "Review complete ABG for respiratory component",
                    ),
                    next_steps=(
                        "Obtain arterial blood gas",
                        "Check urine chloride",
                    )
                ),
                references=list(self.references),
                tool_id=self.tool_id,
                tool_name=self.name,
                raw_inputs={
                    "anion_gap": anion_gap,
                    "bicarbonate": bicarbonate,
                    "normal_ag": normal_ag,
                    "normal_hco3": normal_hco3,
                },
                calculation_details={
                    "delta_ag": round(delta_ag, 1),
                    "delta_hco3": round(delta_hco3, 1),
                    "valid": False,
                    "reason": "HCO₃⁻ not decreased",
                },
                formula_used="Delta Ratio = ΔAG / ΔHCO₃⁻ (not applicable - HCO₃⁻ not decreased)"
            )
        
        # Calculate delta ratio
        delta_ratio = delta_ag / delta_hco3
        delta_ratio = round(delta_ratio, 2)
        
        # Get interpretation
        interpretation = self._get_interpretation(delta_ratio, delta_ag, delta_hco3)
        
        return ScoreResult(
            value=delta_ratio,
            unit=Unit.RATIO,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "anion_gap": anion_gap,
                "bicarbonate": bicarbonate,
                "normal_ag": normal_ag,
                "normal_hco3": normal_hco3,
            },
            calculation_details={
                "delta_ag": round(delta_ag, 1),
                "delta_hco3": round(delta_hco3, 1),
                "delta_ratio": delta_ratio,
            },
            formula_used="Delta Ratio = ΔAG / ΔHCO₃⁻ = (AG - 12) / (24 - HCO₃⁻)"
        )
    
    def _get_interpretation(
        self, 
        delta_ratio: float, 
        delta_ag: float, 
        delta_hco3: float
    ) -> Interpretation:
        """Get clinical interpretation based on delta ratio value"""
        
        if delta_ratio < 1:
            # Concurrent NAGMA
            return Interpretation(
                summary=f"Mixed disorder: HAGMA + NAGMA (Delta Ratio: {delta_ratio})",
                detail=f"Delta ratio <1 indicates bicarbonate loss exceeds anion gap increase. "
                       f"This suggests concurrent Normal Anion Gap Metabolic Acidosis (NAGMA) "
                       f"in addition to HAGMA. ΔAG: {delta_ag:.1f}, ΔHCO₃⁻: {delta_hco3:.1f}",
                severity=Severity.MODERATE,
                stage="HAGMA + NAGMA",
                stage_description="Mixed HAGMA and NAGMA",
                recommendations=(
                    "Address the HAGMA cause (DKA, lactic acidosis, toxins, etc.)",
                    "Also investigate NAGMA component",
                    "Check urine anion gap to identify NAGMA cause",
                    "Consider: diarrhea, RTA, early renal failure, dilutional acidosis",
                ),
                warnings=(
                    "Mixed disorder - may require addressing multiple causes",
                ),
                next_steps=(
                    "Calculate urine anion gap",
                    "UAG positive: RTA",
                    "UAG negative: GI loss (diarrhea)",
                    "Review IV fluids for dilutional component",
                )
            )
        elif delta_ratio <= 2:
            # Pure HAGMA
            return Interpretation(
                summary=f"Pure High Anion Gap Metabolic Acidosis (Delta Ratio: {delta_ratio})",
                detail=f"Delta ratio 1-2 indicates a pure HAGMA where the increase in anion gap "
                       f"matches the decrease in bicarbonate. ΔAG: {delta_ag:.1f}, ΔHCO₃⁻: {delta_hco3:.1f}",
                severity=Severity.MODERATE,
                stage="Pure HAGMA",
                stage_description="Pure High Anion Gap Metabolic Acidosis",
                recommendations=(
                    "Focus on identifying the single HAGMA cause",
                    "Check: lactate, ketones, BUN, toxin screen",
                    "Treat underlying cause",
                ),
                next_steps=(
                    "Identify HAGMA etiology using MUDPILES mnemonic",
                    "Methanol, Uremia, DKA, Propylene glycol",
                    "INH/Iron, Lactic acidosis, Ethylene glycol, Salicylates",
                    "Calculate osmolar gap if toxic alcohol suspected",
                )
            )
        else:
            # Delta ratio > 2: Concurrent metabolic alkalosis
            return Interpretation(
                summary=f"Mixed disorder: HAGMA + Metabolic Alkalosis (Delta Ratio: {delta_ratio})",
                detail=f"Delta ratio >2 indicates the anion gap has increased more than bicarbonate "
                       f"has decreased. This suggests a concurrent metabolic alkalosis is raising "
                       f"the HCO₃⁻. ΔAG: {delta_ag:.1f}, ΔHCO₃⁻: {delta_hco3:.1f}",
                severity=Severity.MODERATE,
                stage="HAGMA + Met Alk",
                stage_description="Mixed HAGMA and Metabolic Alkalosis",
                recommendations=(
                    "Address the HAGMA cause",
                    "Also identify and treat metabolic alkalosis cause",
                    "Check for: vomiting, NG suction, diuretics, hypokalemia",
                    "Consider contraction alkalosis",
                ),
                warnings=(
                    "Mixed disorder - HCO₃⁻ is higher than expected for the AG elevation",
                ),
                next_steps=(
                    "Check urine chloride to classify metabolic alkalosis",
                    "UCl <20: Saline-responsive (vomiting, NG suction)",
                    "UCl >20: Saline-resistant (hyperaldo, Bartter, diuretics)",
                    "Correct underlying causes of both disorders",
                )
            )
