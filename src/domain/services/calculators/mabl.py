"""
Maximum Allowable Blood Loss (MABL) Calculator

Calculates the maximum amount of blood that can be lost before transfusion
is required, based on the patient's estimated blood volume and acceptable
hematocrit levels.

References:
    Gross JB. Estimating allowable blood loss: corrected for dilution. 
    Anesthesiology. 1983;58(3):277-280.
    DOI: 10.1097/00000542-198303000-00016
    PMID: 6829965

    Butterworth JF, Mackey DC, Wasnick JD. Morgan & Mikhail's Clinical 
    Anesthesiology. 7th ed. New York: McGraw-Hill; 2022.

    Miller RD, et al. Miller's Anesthesia. 9th ed. Philadelphia: Elsevier; 2020.
"""

from typing import Optional, Literal

from ..base import BaseCalculator
from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.units import Unit
from ...value_objects.reference import Reference
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.clinical_constants import EBV_ML_PER_KG, get_ebv_per_kg
from ...value_objects.tool_keys import (
    LowLevelKey,
    HighLevelKey,
    Specialty,
    ClinicalContext
)


class MablCalculator(BaseCalculator):
    """
    Maximum Allowable Blood Loss (MABL) Calculator
    
    MABL represents the maximum blood loss tolerated before transfusion
    is indicated. It accounts for:
    - Patient's estimated blood volume (EBV)
    - Starting hematocrit
    - Minimum acceptable hematocrit
    
    Formula (Gross method):
        MABL = EBV × (Hi - Hf) / Hav
        
        Where:
        - EBV = Estimated Blood Volume (weight × blood volume per kg)
        - Hi = Initial hematocrit
        - Hf = Final (minimum acceptable) hematocrit
        - Hav = Average hematocrit = (Hi + Hf) / 2
    
    Alternative simpler formula:
        MABL = EBV × (Hi - Hf) / Hi
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="mabl",
                name="Maximum Allowable Blood Loss (MABL)",
                purpose="Calculate maximum blood loss before transfusion required",
                input_params=[
                    "weight_kg", "initial_hematocrit", "target_hematocrit",
                    "patient_type", "estimated_blood_volume_ml"
                ],
                output_type="MABL in mL"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.ANESTHESIOLOGY,
                    Specialty.SURGERY,
                    Specialty.CRITICAL_CARE,
                    Specialty.PEDIATRIC_ANESTHESIA,
                    Specialty.CARDIAC_ANESTHESIA,
                    Specialty.HEMATOLOGY,
                ),
                conditions=(
                    "Surgical blood loss",
                    "Intraoperative bleeding",
                    "Hemorrhage",
                    "Blood transfusion threshold",
                    "Pediatric surgery",
                    "Major surgery",
                ),
                clinical_contexts=(
                    ClinicalContext.PREOPERATIVE_ASSESSMENT,
                    ClinicalContext.TRANSFUSION_DECISION,
                    ClinicalContext.FLUID_MANAGEMENT,
                    ClinicalContext.ICU_MANAGEMENT,
                ),
                clinical_questions=(
                    "How much blood can this patient lose before needing transfusion?",
                    "What is the maximum allowable blood loss?",
                    "When should I transfuse this patient?",
                    "What is the transfusion trigger for this patient?",
                    "How do I calculate MABL?",
                ),
                icd10_codes=("D62", "T81.0"),
                keywords=(
                    "MABL", "blood loss", "transfusion", "allowable blood loss",
                    "EBV", "estimated blood volume", "hematocrit", "hemorrhage",
                    "surgical bleeding", "blood management",
                )
            ),
            references=(
                Reference(
                    citation="Gross JB. Estimating allowable blood loss: corrected for dilution. "
                             "Anesthesiology. 1983;58(3):277-280.",
                    doi="10.1097/00000542-198303000-00016",
                    pmid="6829965",
                    year=1983
                ),
                Reference(
                    citation="Butterworth JF, Mackey DC, Wasnick JD. Morgan & Mikhail's Clinical "
                             "Anesthesiology. 7th ed. New York: McGraw-Hill; 2022. Chapter 51: "
                             "Fluid Management & Blood Component Therapy.",
                    doi=None,
                    pmid=None,
                    year=2022
                ),
                Reference(
                    citation="Miller RD, et al. Miller's Anesthesia. 9th ed. Philadelphia: "
                             "Elsevier; 2020. Chapter 49: Blood Therapy.",
                    doi=None,
                    pmid=None,
                    year=2020
                ),
                Reference(
                    citation="Cote CJ, Lerman J, Anderson BJ. A Practice of Anesthesia for "
                             "Infants and Children. 6th ed. Philadelphia: Elsevier; 2019.",
                    doi=None,
                    pmid=None,
                    year=2019
                ),
            ),
            version="1.0.0",
            validation_status="validated"
        )
    
    def calculate(
        self,
        weight_kg: float,
        initial_hematocrit: float,
        target_hematocrit: float = 21.0,
        patient_type: str = "adult_male",
        estimated_blood_volume_ml: Optional[float] = None,
        use_gross_method: bool = True,
    ) -> ScoreResult:
        """
        Calculate Maximum Allowable Blood Loss.
        
        Args:
            weight_kg: Patient weight in kg
            initial_hematocrit: Starting hematocrit (%)
            target_hematocrit: Lowest acceptable hematocrit (%)
                Default 21% for healthy patients, adjust for comorbidities
            patient_type: Patient category for EBV estimation
                Options: preterm_neonate, term_neonate, infant, child,
                         adolescent, adult_male, adult_female, obese_adult, elderly
            estimated_blood_volume_ml: Override calculated EBV (mL)
            use_gross_method: Use Gross formula with average Hct (more accurate)
            
        Returns:
            ScoreResult with MABL and related calculations
        """
        # Validate inputs
        if weight_kg <= 0:
            raise ValueError("Weight must be positive")
        if not 10 <= initial_hematocrit <= 70:
            raise ValueError("Initial hematocrit must be between 10-70%")
        if not 10 <= target_hematocrit <= 70:
            raise ValueError("Target hematocrit must be between 10-70%")
        if target_hematocrit >= initial_hematocrit:
            raise ValueError("Target hematocrit must be less than initial hematocrit")
        
        # Calculate or use provided EBV
        if estimated_blood_volume_ml is not None:
            ebv = estimated_blood_volume_ml
            ebv_source = "provided"
        else:
            ebv_per_kg = get_ebv_per_kg(patient_type)
            if ebv_per_kg == 70 and patient_type.lower() not in EBV_ML_PER_KG:
                raise ValueError(
                    f"Unknown patient type: {patient_type}. "
                    f"Available types: {list(EBV_ML_PER_KG.keys())}"
                )
            ebv = weight_kg * ebv_per_kg
            ebv_source = f"{ebv_per_kg} mL/kg × {weight_kg} kg"
        
        # Calculate MABL
        hi = initial_hematocrit
        hf = target_hematocrit
        
        if use_gross_method:
            # Gross method: accounts for dilutional coagulopathy
            hav = (hi + hf) / 2  # Average hematocrit
            mabl = ebv * (hi - hf) / hav
            method = "Gross (dilution-corrected)"
        else:
            # Simple method
            mabl = ebv * (hi - hf) / hi
            method = "Simple"
        
        # Calculate percentage of blood volume
        mabl_percent = (mabl / ebv) * 100
        
        # Determine clinical guidance
        warnings = []
        if mabl_percent > 40:
            severity = Severity.MODERATE
            warnings.append("MABL >40% of blood volume: significant hemorrhage risk")
        elif mabl_percent > 30:
            severity = Severity.MILD
            warnings.append("MABL >30% of blood volume: prepare blood products")
        else:
            severity = Severity.NORMAL
        
        # Transfusion threshold guidance
        if target_hematocrit < 21:
            warnings.append("Target Hct <21%: Consider only for healthy patients with good reserve")
        if target_hematocrit < 24 and patient_type in ("elderly", "cardiac"):
            warnings.append("Consider higher transfusion threshold (Hct 24-30%) for cardiac/elderly patients")
        
        # Build interpretation
        interpretation = Interpretation(
            summary=f"MABL = {mabl:.0f} mL ({mabl_percent:.1f}% of blood volume)",
            detail=f"EBV: {ebv:.0f} mL. Hct drop from {hi:.1f}% to {hf:.1f}%. Method: {method}",
            severity=severity,
            recommendations=(f"Transfusion should be considered when blood loss approaches {mabl:.0f} mL",),
            warnings=tuple(warnings),
        )
        
        return ScoreResult(
            tool_name="Maximum Allowable Blood Loss",
            tool_id="mabl",
            value=round(mabl, 0),
            unit=Unit.ML,  # Using proper mL unit
            interpretation=interpretation,
            references=list(self.metadata.references),
            calculation_details={
                "ebv_ml": round(ebv, 0),
                "hematocrit_drop": round(hi - hf, 1),
                "percent_blood_volume": round(mabl_percent, 1),
            }
        )
    
    @staticmethod
    def get_ebv_reference() -> dict[str, int]:
        """Return the EBV reference table"""
        return EBV_ML_PER_KG.copy()
