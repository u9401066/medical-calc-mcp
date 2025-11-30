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

from typing import Optional, Literal
from dataclasses import dataclass

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


@dataclass
class PediatricDrugInfo:
    """Information for a pediatric drug"""
    name: str
    dose_per_kg: float  # mg/kg
    max_single_dose: float  # mg
    frequency: str
    route: str
    notes: str = ""


# Common pediatric drug database with standard doses
PEDIATRIC_DRUGS = {
    # Analgesics / Antipyretics
    "acetaminophen": PediatricDrugInfo(
        name="Acetaminophen (Paracetamol)",
        dose_per_kg=15.0,
        max_single_dose=1000.0,
        frequency="q4-6h",
        route="PO/PR",
        notes="Max 75 mg/kg/day or 4000 mg/day"
    ),
    "ibuprofen": PediatricDrugInfo(
        name="Ibuprofen",
        dose_per_kg=10.0,
        max_single_dose=400.0,
        frequency="q6-8h",
        route="PO",
        notes="Max 40 mg/kg/day or 2400 mg/day. Avoid in infants <6 months"
    ),
    
    # Antibiotics
    "amoxicillin": PediatricDrugInfo(
        name="Amoxicillin",
        dose_per_kg=25.0,
        max_single_dose=500.0,
        frequency="q8h",
        route="PO",
        notes="High dose: 40-50 mg/kg/dose for resistant organisms"
    ),
    "amoxicillin_clavulanate": PediatricDrugInfo(
        name="Amoxicillin-Clavulanate (Augmentin)",
        dose_per_kg=25.0,
        max_single_dose=500.0,
        frequency="q8h",
        route="PO",
        notes="Based on amoxicillin component"
    ),
    "azithromycin": PediatricDrugInfo(
        name="Azithromycin",
        dose_per_kg=10.0,
        max_single_dose=500.0,
        frequency="q24h",
        route="PO",
        notes="Day 1: 10 mg/kg, Days 2-5: 5 mg/kg"
    ),
    "ceftriaxone": PediatricDrugInfo(
        name="Ceftriaxone",
        dose_per_kg=50.0,
        max_single_dose=2000.0,
        frequency="q24h",
        route="IV/IM",
        notes="Meningitis: 100 mg/kg/day divided q12h"
    ),
    "cefazolin": PediatricDrugInfo(
        name="Cefazolin",
        dose_per_kg=25.0,
        max_single_dose=1000.0,
        frequency="q8h",
        route="IV",
        notes="Surgical prophylaxis: 30 mg/kg, max 2g"
    ),
    
    # Anesthesia drugs
    "propofol": PediatricDrugInfo(
        name="Propofol (Induction)",
        dose_per_kg=2.5,
        max_single_dose=200.0,
        frequency="single dose",
        route="IV",
        notes="Induction: 2-3 mg/kg. Infants may need higher doses (3-4 mg/kg)"
    ),
    "ketamine": PediatricDrugInfo(
        name="Ketamine (IV)",
        dose_per_kg=1.5,
        max_single_dose=100.0,
        frequency="single dose",
        route="IV",
        notes="IV: 1-2 mg/kg, IM: 4-6 mg/kg"
    ),
    "fentanyl": PediatricDrugInfo(
        name="Fentanyl",
        dose_per_kg=0.001,  # 1 mcg/kg
        max_single_dose=0.1,  # 100 mcg
        frequency="prn",
        route="IV",
        notes="1-2 mcg/kg for analgesia; dose in mcg not mg"
    ),
    "morphine": PediatricDrugInfo(
        name="Morphine",
        dose_per_kg=0.1,
        max_single_dose=10.0,
        frequency="q4h prn",
        route="IV",
        notes="0.05-0.1 mg/kg IV; 0.2-0.5 mg/kg PO"
    ),
    "rocuronium": PediatricDrugInfo(
        name="Rocuronium",
        dose_per_kg=0.6,
        max_single_dose=50.0,
        frequency="single dose",
        route="IV",
        notes="RSI: 1.2 mg/kg; Maintenance: 0.1-0.2 mg/kg"
    ),
    "succinylcholine": PediatricDrugInfo(
        name="Succinylcholine",
        dose_per_kg=2.0,
        max_single_dose=150.0,
        frequency="single dose",
        route="IV",
        notes="Infants: 2-3 mg/kg; Children: 1-2 mg/kg. Contraindicated in hyperkalemia risk"
    ),
    "atropine": PediatricDrugInfo(
        name="Atropine",
        dose_per_kg=0.02,
        max_single_dose=0.5,
        frequency="single dose",
        route="IV",
        notes="Minimum dose: 0.1 mg; Max: 0.5 mg (child), 1 mg (adolescent)"
    ),
    "glycopyrrolate": PediatricDrugInfo(
        name="Glycopyrrolate",
        dose_per_kg=0.01,
        max_single_dose=0.2,
        frequency="single dose",
        route="IV",
        notes="Antisialagogue: 0.004-0.01 mg/kg"
    ),
    "ondansetron": PediatricDrugInfo(
        name="Ondansetron",
        dose_per_kg=0.15,
        max_single_dose=4.0,
        frequency="q8h",
        route="IV/PO",
        notes="PONV prophylaxis: 0.1-0.15 mg/kg"
    ),
    "dexamethasone": PediatricDrugInfo(
        name="Dexamethasone (PONV)",
        dose_per_kg=0.15,
        max_single_dose=8.0,
        frequency="single dose",
        route="IV",
        notes="PONV: 0.1-0.15 mg/kg; Croup: 0.6 mg/kg"
    ),
    
    # Emergency drugs
    "epinephrine": PediatricDrugInfo(
        name="Epinephrine (Cardiac Arrest)",
        dose_per_kg=0.01,
        max_single_dose=1.0,
        frequency="q3-5min",
        route="IV/IO",
        notes="0.01 mg/kg (0.1 mL/kg of 1:10,000); Max 1 mg. ETT: 0.1 mg/kg"
    ),
    "adenosine": PediatricDrugInfo(
        name="Adenosine",
        dose_per_kg=0.1,
        max_single_dose=6.0,
        frequency="prn",
        route="IV rapid push",
        notes="1st dose: 0.1 mg/kg (max 6 mg); 2nd dose: 0.2 mg/kg (max 12 mg)"
    ),
    "amiodarone": PediatricDrugInfo(
        name="Amiodarone",
        dose_per_kg=5.0,
        max_single_dose=300.0,
        frequency="prn",
        route="IV",
        notes="VF/pVT: 5 mg/kg; May repeat x2"
    ),
}


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
        detail_info = {
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
            unit=Unit.MG_DL,  # Using mg as closest available
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
        return list(PEDIATRIC_DRUGS.keys())
