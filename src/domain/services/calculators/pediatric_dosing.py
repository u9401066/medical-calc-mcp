"""
Pediatric Drug Dosing Calculator

Calculates weight-based drug doses for pediatric patients with safety checks.

References:
    Taketomo CK, Hodding JH, Kraus DM. Pediatric & Neonatal Dosage Handbook. 
    29th ed. Hudson, OH: Lexicomp; 2022.
    
    Neofax: A Manual of Drugs Used in Neonatal Care. 24th ed. 
    Montvale, NJ: Thomson Reuters; 2011.

    British National Formulary for Children (BNFC). London: BMJ Group and 
    Pharmaceutical Press; 2023.
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

# Import drug database from data module
from .data.pediatric_drugs import (
    PEDIATRIC_DRUGS,
    list_available_drugs as _list_drugs,
)


class PediatricDosingCalculator(BaseCalculator):
    """
    Pediatric Drug Dosing Calculator
    
    Calculates weight-based doses for common pediatric medications with:
    - Single dose calculation
    - Maximum dose enforcement
    - Age-appropriate warnings
    - Available drug database lookup
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="pediatric_dosing",
                name="Pediatric Drug Dosing Calculator",
                purpose="Calculate weight-based drug doses for pediatric patients",
                input_params=[
                    "drug_name", "weight_kg",
                    "age_years", "custom_dose_per_kg"
                ],
                output_type="Calculated dose with maximum dose check"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.PEDIATRICS,
                    Specialty.ANESTHESIOLOGY,
                    Specialty.PEDIATRIC_ANESTHESIA,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.CRITICAL_CARE,
                ),
                conditions=(
                    "Pediatric medication dosing",
                    "Weight-based dosing",
                    "Neonatal dosing",
                    "Pediatric anesthesia",
                    "Pediatric emergency",
                ),
                clinical_contexts=(
                    ClinicalContext.DRUG_DOSING,
                    ClinicalContext.PREOPERATIVE_ASSESSMENT,
                    ClinicalContext.ICU_MANAGEMENT,
                ),
                clinical_questions=(
                    "What is the correct dose for this child?",
                    "How much medication should I give based on weight?",
                    "What is the maximum dose for this drug?",
                    "What is the pediatric dose of this medication?",
                ),
                icd10_codes=(),
                keywords=(
                    "pediatric", "dosing", "weight-based", "mg/kg",
                    "child", "infant", "neonatal", "dose calculation",
                    "maximum dose", "drug dose",
                )
            ),
            references=(
                Reference(
                    citation="Taketomo CK, Hodding JH, Kraus DM. Pediatric & Neonatal "
                             "Dosage Handbook. 29th ed. Hudson, OH: Lexicomp; 2022.",
                    doi=None,
                    pmid=None,
                    year=2022
                ),
                Reference(
                    citation="British National Formulary for Children (BNFC). London: "
                             "BMJ Group and Pharmaceutical Press; 2023.",
                    doi=None,
                    pmid=None,
                    year=2023
                ),
                Reference(
                    citation="Anderson BJ, Holford NH. Getting the dose right for obese children. "
                             "Arch Dis Child. 2017;102(1):54-55.",
                    doi="10.1136/archdischild-2016-311696",
                    pmid="27831906",
                    year=2017
                ),
            ),
            version="1.0.0",
            validation_status="validated"
        )
    
    def calculate(
        self,
        weight_kg: float,
        drug_name: Optional[str] = None,
        age_years: Optional[float] = None,
        route: str = "iv",
        indication: Optional[str] = None,
        custom_dose_per_kg: Optional[float] = None,
        custom_max_dose: Optional[float] = None,
        custom_drug_name: Optional[str] = None,
    ) -> ScoreResult:
        """
        Calculate pediatric drug dose.
        
        Args:
            weight_kg: Patient weight in kg
            drug_name: Name of drug from database (optional if using custom)
            age_years: Age in years (for warnings)
            custom_dose_per_kg: Custom dose in mg/kg (if not using database)
            custom_max_dose: Custom maximum single dose (mg)
            custom_drug_name: Name for custom drug
            
        Returns:
            ScoreResult with calculated dose and warnings
        """
        # Validate weight
        if weight_kg <= 0:
            raise ValueError("Weight must be positive")
        if weight_kg > 150:
            raise ValueError("Weight exceeds typical pediatric range (>150 kg)")
        
        # Get drug info
        if drug_name and drug_name.lower() in PEDIATRIC_DRUGS:
            drug = PEDIATRIC_DRUGS[drug_name.lower()]
            dose_per_kg = drug.dose_per_kg
            max_dose = drug.max_single_dose
            drug_display_name = drug.name
            frequency = drug.frequency
            route = drug.route
            notes = drug.notes
        elif custom_dose_per_kg is not None:
            dose_per_kg = custom_dose_per_kg
            max_dose = custom_max_dose
            drug_display_name = custom_drug_name or "Custom Drug"
            frequency = "as prescribed"
            route = "as prescribed"
            notes = ""
        else:
            available = list(PEDIATRIC_DRUGS.keys())
            raise ValueError(
                f"Drug '{drug_name}' not found. Available drugs: {available}"
            )
        
        # Calculate dose
        calculated_dose = weight_kg * dose_per_kg
        
        # Apply maximum dose cap
        dose_capped = False
        if max_dose and calculated_dose > max_dose:
            final_dose = max_dose
            dose_capped = True
        else:
            final_dose = calculated_dose
        
        # Build warnings
        warnings = []
        if dose_capped:
            warnings.append(
                f"Calculated dose ({calculated_dose:.2f} mg) exceeds maximum "
                f"({max_dose:.1f} mg). Dose capped at maximum."
            )
        
        if age_years is not None:
            if age_years < 0.08:  # < 1 month
                warnings.append("NEONATAL PATIENT: Verify dose is appropriate for neonates")
            elif age_years < 1:
                warnings.append("INFANT: Consider developmental pharmacokinetics")
        
        # Determine severity
        if dose_capped:
            severity = Severity.MODERATE
        else:
            severity = Severity.NORMAL
        
        # Build interpretation
        {
            "drug_name": drug_display_name,
            "dose_per_kg": dose_per_kg,
            "weight_kg": weight_kg,
            "calculated_dose_mg": round(calculated_dose, 2),
            "final_dose_mg": round(final_dose, 2),
            "dose_capped": dose_capped,
            "max_single_dose_mg": max_dose,
            "frequency": frequency,
            "route": route,
            "notes": notes,
        }
        
        interpretation = Interpretation(
            summary=f"{drug_display_name}: {final_dose:.2f} mg ({dose_per_kg} mg/kg × {weight_kg} kg)",
            detail=f"Give {final_dose:.2f} mg {route} {frequency}. {notes}" if notes else f"Give {final_dose:.2f} mg {route} {frequency}",
            severity=severity,
            recommendations=(f"Give {final_dose:.2f} mg {route} {frequency}",),
            warnings=tuple(warnings),
        )
        
        return ScoreResult(
            tool_name="Pediatric Drug Dose",
            tool_id="pediatric_dosing",
            value=round(final_dose, 2),
            unit=Unit.MG_DOSE,  # Using proper mg/dose unit
            interpretation=interpretation,
            references=list(self.metadata.references),
            calculation_details={
                "dose_per_kg": dose_per_kg,
                "calculated_dose": round(calculated_dose, 2),
                "max_dose": max_dose,
                "dose_capped": dose_capped,
            }
        )
    
    @staticmethod
    def list_available_drugs() -> list[str]:
        """Return list of available drugs in database"""
        return _list_drugs()
