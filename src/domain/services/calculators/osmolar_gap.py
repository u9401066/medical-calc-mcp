"""
Osmolar Gap Calculator

Calculates the difference between measured and calculated serum osmolality.
Used to detect presence of unmeasured osmoles, particularly toxic alcohols.

Reference:
    Purssell RA, Pudek M, Brubacher J, Abu-Laban RB. Derivation and validation
    of a formula to calculate the contribution of ethanol to the osmolal gap.
    Ann Emerg Med. 2001;38(6):653-659.
    DOI: 10.1067/mem.2001.119455
    PMID: 11719745
    
    Kraut JA, Xing SX. Approach to the evaluation of a patient with an increased
    serum osmolal gap and high-anion-gap metabolic acidosis.
    Am J Kidney Dis. 2011;58(3):480-484.
    DOI: 10.1053/j.ajkd.2011.05.018
    PMID: 21794966
    
    Lynd LD, Richardson KJ, Purssell RA, et al. An evaluation of the osmole
    gap as a screening test for toxic alcohol poisoning.
    BMC Emerg Med. 2008;8:5.
    DOI: 10.1186/1471-227X-8-5
    PMID: 18442409
"""

from typing import Optional

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


class OsmolarGapCalculator(BaseCalculator):
    """
    Osmolar Gap (Osmolal Gap) Calculator
    
    The osmolar gap is the difference between measured serum osmolality
    and calculated osmolality. An elevated gap suggests the presence of
    unmeasured osmotically active substances.
    
    Formula:
        Calculated Osmolality = 2 × Na⁺ + (Glucose / 18) + (BUN / 2.8)
        
        With ethanol adjustment:
        Calculated Osm = 2 × Na⁺ + (Glucose / 18) + (BUN / 2.8) + (Ethanol / 4.6)
        
        Osmolar Gap = Measured Osmolality - Calculated Osmolality
        
        Normal range: -10 to +10 mOsm/kg (some sources: <10)
        
    Clinical Significance:
        Elevated osmolar gap (>10) suggests:
        - Toxic alcohols: methanol, ethylene glycol, isopropanol
        - Propylene glycol (IV lorazepam, phenytoin)
        - Acetone (ketoacidosis)
        - Mannitol
        - Glycine (TURP syndrome)
        - Contrast media
        - Severe hypertriglyceridemia
        - Hyperproteinemia
        
    Important Notes:
        - Methanol: 3.2 mg/dL per mOsm/kg
        - Ethylene glycol: 6.2 mg/dL per mOsm/kg
        - A normal osmolar gap does NOT rule out toxic alcohol ingestion
          (may have been metabolized already)
        - Use with anion gap for complete assessment
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="osmolar_gap",
                name="Osmolar Gap (Osmolal Gap)",
                purpose="Calculate difference between measured and calculated osmolality",
                input_params=["measured_osm", "sodium", "glucose", "bun", "ethanol"],
                output_type="Osmolar gap (mOsm/kg) with interpretation"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.TOXICOLOGY,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.CRITICAL_CARE,
                    Specialty.NEPHROLOGY,
                ),
                conditions=(
                    "Toxic alcohol ingestion",
                    "Methanol poisoning",
                    "Ethylene glycol poisoning",
                    "Isopropanol poisoning",
                    "Propylene glycol toxicity",
                    "Altered mental status",
                    "High anion gap metabolic acidosis",
                    "HAGMA",
                ),
                clinical_contexts=(
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.SCREENING,
                    ClinicalContext.SEVERITY_ASSESSMENT,
                ),
                clinical_questions=(
                    "Is there a toxic alcohol ingestion?",
                    "What is causing this high anion gap acidosis?",
                    "Is the osmolar gap elevated?",
                    "Should I give fomepizole empirically?",
                    "Is this methanol or ethylene glycol poisoning?",
                ),
                icd10_codes=("T51.1", "T51.8", "T52.3", "E87.0"),
                keywords=(
                    "osmolar gap", "osmolal gap", "osmolality", "toxic alcohol",
                    "methanol", "ethylene glycol", "isopropanol", "poisoning",
                    "HAGMA", "fomepizole", "antidote",
                ),
            ),
            references=self._get_references(),
        )
    
    def _get_references(self) -> tuple[Reference, ...]:
        return (
            Reference(
                citation="Purssell RA, Pudek M, Brubacher J, Abu-Laban RB. Derivation and validation of a formula to calculate the contribution of ethanol to the osmolal gap. Ann Emerg Med. 2001;38(6):653-659.",
                doi="10.1067/mem.2001.119455",
                pmid="11719745",
                year=2001,
            ),
            Reference(
                citation="Kraut JA, Xing SX. Approach to the evaluation of a patient with an increased serum osmolal gap and high-anion-gap metabolic acidosis. Am J Kidney Dis. 2011;58(3):480-484.",
                doi="10.1053/j.ajkd.2011.05.018",
                pmid="21794966",
                year=2011,
            ),
            Reference(
                citation="Lynd LD, Richardson KJ, Purssell RA, et al. An evaluation of the osmole gap as a screening test for toxic alcohol poisoning. BMC Emerg Med. 2008;8:5.",
                doi="10.1186/1471-227X-8-5",
                pmid="18442409",
                year=2008,
            ),
        )
    
    def calculate(
        self,
        measured_osm: float,
        sodium: float,
        glucose: float,
        bun: float,
        ethanol: Optional[float] = None,
    ) -> ScoreResult:
        """
        Calculate osmolar gap.
        
        Args:
            measured_osm: Measured serum osmolality (mOsm/kg)
            sodium: Serum sodium (mEq/L)
            glucose: Serum glucose (mg/dL)
            bun: Blood urea nitrogen (mg/dL)
            ethanol: Serum ethanol level (mg/dL), optional
            
        Returns:
            ScoreResult with osmolar gap and interpretation
        """
        # Validate inputs
        if measured_osm < 200 or measured_osm > 500:
            raise ValueError(f"Measured osmolality {measured_osm} mOsm/kg is outside expected range (200-500)")
        if sodium < 100 or sodium > 180:
            raise ValueError(f"Sodium {sodium} mEq/L is outside expected range (100-180)")
        if glucose < 20 or glucose > 2000:
            raise ValueError(f"Glucose {glucose} mg/dL is outside expected range (20-2000)")
        if bun < 1 or bun > 200:
            raise ValueError(f"BUN {bun} mg/dL is outside expected range (1-200)")
        if ethanol is not None and ethanol < 0:
            raise ValueError(f"Ethanol {ethanol} mg/dL cannot be negative")
        
        # Calculate osmolality
        # Calculated Osm = 2 × Na + (Glucose / 18) + (BUN / 2.8)
        calculated_osm = (2 * sodium) + (glucose / 18) + (bun / 2.8)
        
        # Add ethanol contribution if provided
        # Ethanol contribution = Ethanol / 4.6
        ethanol_contribution = 0
        if ethanol is not None and ethanol > 0:
            ethanol_contribution = ethanol / 4.6
            calculated_osm += ethanol_contribution
        
        # Calculate osmolar gap
        osmolar_gap = measured_osm - calculated_osm
        osmolar_gap = round(osmolar_gap, 1)
        
        # Generate interpretation
        interpretation = self._interpret_osmolar_gap(osmolar_gap, ethanol)
        
        # Build calculation details
        details = {
            "Measured_osmolality": f"{measured_osm} mOsm/kg",
            "Sodium": f"{sodium} mEq/L",
            "Glucose": f"{glucose} mg/dL",
            "BUN": f"{bun} mg/dL",
            "Calculated_osmolality": f"{calculated_osm:.1f} mOsm/kg",
            "Osmolar_gap": f"{osmolar_gap:.1f} mOsm/kg",
        }
        
        if ethanol is not None:
            details["Ethanol"] = f"{ethanol} mg/dL"
            details["Ethanol_contribution"] = f"{ethanol_contribution:.1f} mOsm/kg"
        
        formula = "Osm gap = Measured - (2×Na + Glucose/18 + BUN/2.8"
        if ethanol is not None:
            formula += " + Ethanol/4.6)"
        else:
            formula += ")"
        
        return ScoreResult(
            value=osmolar_gap,
            unit=Unit.NONE,  # mOsm/kg is dimensionless ratio
            interpretation=interpretation,
            references=self._get_references(),
            tool_id=self.tool_id,
            tool_name=self.metadata.name,
            raw_inputs={
                "measured_osm": measured_osm,
                "sodium": sodium,
                "glucose": glucose,
                "bun": bun,
                "ethanol": ethanol,
            },
            calculation_details=details,
            formula_used=formula,
        )
    
    def _interpret_osmolar_gap(
        self,
        osmolar_gap: float,
        ethanol: Optional[float],
    ) -> Interpretation:
        """Generate interpretation based on osmolar gap value."""
        
        # Normal range is typically -10 to +10
        if osmolar_gap <= 10:
            if osmolar_gap >= -10:
                severity = Severity.NORMAL
                risk_level = RiskLevel.VERY_LOW
                summary = f"Normal osmolar gap ({osmolar_gap:.1f} mOsm/kg)"
                detail = "The osmolar gap is within normal limits (-10 to +10 mOsm/kg)."
                recommendations = (
                    "Low suspicion for significant toxic alcohol ingestion",
                    "Consider other causes of presentation",
                    "Re-check if clinical suspicion remains high",
                )
                warnings = (
                    "A normal osmolar gap does NOT definitively rule out toxic alcohol poisoning",
                    "Toxic alcohols may have been metabolized to organic acids already",
                )
            else:  # < -10
                severity = Severity.NORMAL
                risk_level = RiskLevel.VERY_LOW
                summary = f"Low osmolar gap ({osmolar_gap:.1f} mOsm/kg)"
                detail = "Negative or very low osmolar gap. May be due to lab error, hyponatremia, hypoalbuminemia, or other factors."
                recommendations = (
                    "Consider sources of error in measurement",
                    "Check for hyperlipidemia or hyperproteinemia (pseudohyponatremia)",
                    "Repeat measurement if clinically discordant",
                )
                warnings = ()
        elif osmolar_gap <= 25:
            severity = Severity.MILD
            risk_level = RiskLevel.LOW
            summary = f"Mildly elevated osmolar gap ({osmolar_gap:.1f} mOsm/kg)"
            detail = "Osmolar gap is mildly elevated. This may be due to unmeasured osmoles or normal variation."
            recommendations = (
                "Consider causes of elevated osmolar gap:",
                "- Early toxic alcohol ingestion (before metabolism)",
                "- Propylene glycol (IV meds)",
                "- Acetone (ketoacidosis)",
                "- Recent contrast administration",
                "Check anion gap for concomitant HAGMA",
                "Consider toxic alcohol levels if clinical suspicion",
            )
            warnings = (
                "Borderline elevated - may indicate early toxic ingestion",
            )
        elif osmolar_gap <= 50:
            severity = Severity.MODERATE
            risk_level = RiskLevel.INTERMEDIATE
            summary = f"Elevated osmolar gap ({osmolar_gap:.1f} mOsm/kg) - SUSPECT TOXIC ALCOHOL"
            detail = "Significantly elevated osmolar gap strongly suggests presence of unmeasured osmoles, most commonly toxic alcohols (methanol, ethylene glycol, isopropanol)."
            recommendations = (
                "🚨 HIGH SUSPICION for toxic alcohol ingestion",
                "Send methanol and ethylene glycol levels",
                "Consider empiric fomepizole if:",
                "  - Elevated osmolar gap + HAGMA",
                "  - History of ingestion",
                "  - Altered mental status",
                "Contact Poison Control Center",
                "Prepare for possible hemodialysis",
            )
            warnings = (
                "⚠️ Elevated osmolar gap - evaluate for toxic alcohol poisoning",
                "Do not wait for levels before starting fomepizole if high suspicion",
            )
        else:  # > 50
            severity = Severity.SEVERE
            risk_level = RiskLevel.HIGH
            summary = f"Markedly elevated osmolar gap ({osmolar_gap:.1f} mOsm/kg) - HIGH RISK TOXIC INGESTION"
            detail = f"Osmolar gap >50 mOsm/kg is highly suggestive of significant toxic alcohol ingestion. Estimated concentrations: Methanol ~{osmolar_gap * 3.2:.0f} mg/dL, Ethylene glycol ~{osmolar_gap * 6.2:.0f} mg/dL."
            recommendations = (
                "🚨 IMMEDIATE ACTION REQUIRED",
                "Start fomepizole 15 mg/kg IV NOW (do not wait for levels)",
                "Or give ethanol if fomepizole unavailable",
                "Urgent hemodialysis consultation",
                "Send stat methanol, ethylene glycol, isopropanol levels",
                "Check arterial blood gas, lactate, urinalysis (crystals)",
                "Contact Poison Control Center",
                "ICU admission",
            )
            warnings = (
                "🚨 CRITICAL: Markedly elevated osmolar gap - likely toxic alcohol poisoning",
                "Immediate treatment required - do not delay for lab confirmation",
            )
        
        next_steps = [
            "Calculate anion gap - HAGMA + elevated osmolar gap is classic for methanol/ethylene glycol",
            "Methanol → formic acid → blindness, basal ganglia hemorrhage",
            "Ethylene glycol → glycolic/oxalic acid → renal failure, calcium oxalate crystals",
            "Isopropanol → acetone (ketosis without acidosis)",
        ]
        
        return Interpretation(
            summary=summary,
            detail=detail,
            severity=severity,
            risk_level=risk_level,
            recommendations=recommendations,
            warnings=warnings,
            next_steps=tuple(next_steps),
        )
