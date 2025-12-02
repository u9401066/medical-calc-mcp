"""
Transfusion Volume Calculator

Calculates the required volume of blood products (PRBC, whole blood, platelets)
to achieve a target hematocrit or platelet count.

References:
    Roseff SD, Luban NL, Manno CS. Guidelines for assessing appropriateness of 
    pediatric transfusion. Transfusion. 2002;42(11):1398-1413.
    DOI: 10.1046/j.1537-2995.2002.00208.x
    PMID: 12421212

    New HV, Berryman J, Bolton-Maggs PH, et al. Guidelines on transfusion for 
    fetuses, neonates and older children. Br J Haematol. 2016;175(5):784-828.
    DOI: 10.1111/bjh.14233
    PMID: 27861734

    Carson JL, Stanworth SJ, Dennis JA, et al. Transfusion thresholds for guiding 
    red blood cell transfusion. Cochrane Database Syst Rev. 2021;12(12):CD002042.
    DOI: 10.1002/14651858.CD002042.pub5
    PMID: 34932836
"""

from typing import Optional

from ..base import BaseCalculator
from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.units import Unit
from ...value_objects.reference import Reference
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.clinical_constants import (
    BLOOD_PRODUCTS, 
    get_ebv_per_kg,
)
from ...value_objects.tool_keys import (
    LowLevelKey,
    HighLevelKey,
    Specialty,
    ClinicalContext
)


class TransfusionCalculator(BaseCalculator):
    """
    Transfusion Volume Calculator
    
    Calculates the volume of blood products needed to achieve target levels:
    
    For PRBC/Whole Blood:
        Volume (mL) = EBV ? (Target Hct - Current Hct) / Product Hct
        
    For Pediatric PRBC (simplified):
        Volume (mL) = Weight (kg) ? (Target Hb - Current Hb) ? 3
        or
        Volume (mL) = Weight (kg) ? (Target Hct - Current Hct) / Hct of PRBC ? 100
        
    General rule: 10-15 mL/kg of PRBC raises Hgb by ~2-3 g/dL
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="transfusion_calc",
                name="Transfusion Volume Calculator",
                purpose="Calculate blood product volume needed for target Hct/Hgb/Plt",
                input_params=[
                    "weight_kg", "current_hematocrit", "target_hematocrit",
                    "product_type", "patient_type"
                ],
                output_type="Required transfusion volume in mL"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.ANESTHESIOLOGY,
                    Specialty.SURGERY,
                    Specialty.CRITICAL_CARE,
                    Specialty.PEDIATRIC_ANESTHESIA,
                    Specialty.HEMATOLOGY,
                    Specialty.PEDIATRICS,
                ),
                conditions=(
                    "Anemia",
                    "Blood transfusion",
                    "Surgical blood loss",
                    "Hemorrhage",
                    "Thrombocytopenia",
                    "Coagulopathy",
                ),
                clinical_contexts=(
                    ClinicalContext.TRANSFUSION_DECISION,
                    ClinicalContext.FLUID_MANAGEMENT,
                    ClinicalContext.ICU_MANAGEMENT,
                    ClinicalContext.PREOPERATIVE_ASSESSMENT,
                ),
                clinical_questions=(
                    "How much blood should I transfuse?",
                    "How many units of PRBC are needed?",
                    "What volume of blood products to reach target Hct?",
                    "How do I calculate transfusion volume for a child?",
                    "How much will the hematocrit rise with transfusion?",
                ),
                icd10_codes=("D62", "D64.9", "D69.6"),
                keywords=(
                    "transfusion", "PRBC", "packed red cells", "blood products",
                    "hematocrit", "hemoglobin", "platelets", "FFP",
                    "transfusion volume", "blood transfusion",
                )
            ),
            references=(
                Reference(
                    citation="Roseff SD, Luban NL, Manno CS. Guidelines for assessing appropriateness "
                             "of pediatric transfusion. Transfusion. 2002;42(11):1398-1413.",
                    doi="10.1046/j.1537-2995.2002.00208.x",
                    pmid="12421212",
                    year=2002
                ),
                Reference(
                    citation="New HV, Berryman J, Bolton-Maggs PH, et al. Guidelines on transfusion "
                             "for fetuses, neonates and older children. Br J Haematol. 2016;175(5):784-828.",
                    doi="10.1111/bjh.14233",
                    pmid="27861734",
                    year=2016
                ),
                Reference(
                    citation="Carson JL, Stanworth SJ, Dennis JA, et al. Transfusion thresholds for "
                             "guiding red blood cell transfusion. Cochrane Database Syst Rev. 2021;12:CD002042.",
                    doi="10.1002/14651858.CD002042.pub5",
                    pmid="34932836",
                    year=2021
                ),
                Reference(
                    citation="Cote CJ, Lerman J, Anderson BJ. A Practice of Anesthesia for "
                             "Infants and Children. 6th ed. Philadelphia: Elsevier; 2019. "
                             "Chapter 10: Blood Conservation.",
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
        current_hematocrit: Optional[float] = None,
        target_hematocrit: Optional[float] = None,
        current_hemoglobin: Optional[float] = None,
        target_hemoglobin: Optional[float] = None,
        product_type: str = "prbc",
        patient_type: str = "adult_male",
        current_platelet: Optional[float] = None,
        target_platelet: Optional[float] = None,
    ) -> ScoreResult:
        """
        Calculate required transfusion volume.
        
        Args:
            weight_kg: Patient weight in kg
            current_hematocrit: Current Hct (%)
            target_hematocrit: Target Hct (%)
            current_hemoglobin: Current Hgb (g/dL) - alternative to Hct
            target_hemoglobin: Target Hgb (g/dL)
            product_type: Blood product type (prbc, whole_blood, platelets, ffp)
            patient_type: Patient category for EBV calculation
            current_platelet: Current platelet count (?10??L)
            target_platelet: Target platelet count (?10??L)
            
        Returns:
            ScoreResult with calculated transfusion volume
        """
        # Validate weight
        if weight_kg <= 0:
            raise ValueError("Weight must be positive")
        
        product_type_lower = product_type.lower()
        
        # Handle RBC transfusion
        if product_type_lower in ("prbc", "whole_blood"):
            return self._calculate_rbc_transfusion(
                weight_kg=weight_kg,
                current_hematocrit=current_hematocrit,
                target_hematocrit=target_hematocrit,
                current_hemoglobin=current_hemoglobin,
                target_hemoglobin=target_hemoglobin,
                product_type=product_type_lower,
                patient_type=patient_type,
            )
        
        # Handle platelet transfusion
        elif product_type_lower in ("platelets", "platelet_concentrate"):
            return self._calculate_platelet_transfusion(
                weight_kg=weight_kg,
                current_platelet=current_platelet,
                target_platelet=target_platelet,
                product_type=product_type_lower,
                patient_type=patient_type,
            )
        
        # Handle FFP
        elif product_type_lower == "ffp":
            return self._calculate_ffp_dose(weight_kg=weight_kg)
        
        # Handle Cryoprecipitate
        elif product_type_lower == "cryoprecipitate":
            return self._calculate_cryo_dose(weight_kg=weight_kg)
        
        else:
            raise ValueError(
                f"Unknown product type: {product_type}. "
                f"Available: prbc, whole_blood, platelets, platelet_concentrate, ffp, cryoprecipitate"
            )
    
    def _calculate_rbc_transfusion(
        self,
        weight_kg: float,
        current_hematocrit: Optional[float],
        target_hematocrit: Optional[float],
        current_hemoglobin: Optional[float],
        target_hemoglobin: Optional[float],
        product_type: str,
        patient_type: str,
    ) -> ScoreResult:
        """Calculate PRBC or whole blood transfusion volume"""
        
        # Convert Hgb to Hct if needed (Hct ??Hgb ? 3)
        if current_hematocrit is None and current_hemoglobin is not None:
            current_hematocrit = current_hemoglobin * 3
        if target_hematocrit is None and target_hemoglobin is not None:
            target_hematocrit = target_hemoglobin * 3
        
        if current_hematocrit is None or target_hematocrit is None:
            raise ValueError("Must provide current and target hematocrit (or hemoglobin)")
        
        if not 5 <= current_hematocrit <= 70:
            raise ValueError("Current hematocrit must be between 5-70%")
        if not 5 <= target_hematocrit <= 70:
            raise ValueError("Target hematocrit must be between 5-70%")
        if target_hematocrit <= current_hematocrit:
            raise ValueError("Target hematocrit must be greater than current")
        
        # Get product info
        product = BLOOD_PRODUCTS[product_type]
        product_hct = product["hematocrit"]
        
        # Get EBV using helper function
        ebv_per_kg = get_ebv_per_kg(patient_type, default=70)
        ebv = weight_kg * ebv_per_kg
        
        # Calculate transfusion volume
        # Formula: Volume = EBV ? (Target Hct - Current Hct) / Product Hct
        hct_deficit = target_hematocrit - current_hematocrit
        volume_needed = ebv * hct_deficit / product_hct
        
        # Calculate number of units
        volume_per_unit = product["volume_per_unit_ml"]
        units_needed = volume_needed / volume_per_unit
        
        # Pediatric rule of thumb check: 10-15 mL/kg raises Hgb ~2-3 g/dL
        expected_hgb_rise = (volume_needed / weight_kg) / 5  # ~5 mL/kg per 1 g/dL
        
        warnings = []
        if volume_needed > 2000:
            warnings.append("Large volume transfusion: consider massive transfusion protocol")
        if weight_kg < 10 and volume_needed > weight_kg * 20:
            warnings.append("Volume >20 mL/kg in small infant: transfuse slowly, monitor for overload")
        
        # Convert Hct to Hgb for display
        current_hgb = current_hematocrit / 3
        target_hgb = target_hematocrit / 3
        
        interpretation = Interpretation(
            summary=f"Transfuse {volume_needed:.0f} mL {product['name']} (~{units_needed:.1f} units)",
            detail=f"Raise Hct from {current_hematocrit:.1f}% to {target_hematocrit:.1f}%. EBV: {ebv:.0f} mL. {volume_needed/weight_kg:.1f} mL/kg.",
            severity=Severity.NORMAL,
            recommendations=(f"Give {volume_needed:.0f} mL to raise Hct from {current_hematocrit:.1f}% to {target_hematocrit:.1f}%",),
            warnings=tuple(warnings),
        )
        
        return ScoreResult(
            tool_name="Transfusion Volume",
            tool_id="transfusion_calc",
            value=round(volume_needed, 0),
            unit=Unit.ML,
            interpretation=interpretation,
            references=list(self.metadata.references),
            calculation_details={
                "volume_ml": round(volume_needed, 0),
                "units_needed": round(units_needed, 1),
                "ml_per_kg": round(volume_needed / weight_kg, 1),
            }
        )
    
    def _calculate_platelet_transfusion(
        self,
        weight_kg: float,
        current_platelet: Optional[float],
        target_platelet: Optional[float],
        product_type: str,
        patient_type: str,
    ) -> ScoreResult:
        """Calculate platelet transfusion"""
        
        if current_platelet is None or target_platelet is None:
            # Default pediatric dosing: 10-15 mL/kg of apheresis platelets
            volume = weight_kg * 10  # 10 mL/kg
            
            return ScoreResult(
                tool_name="Platelet Transfusion Volume",
                tool_id="transfusion_calc",
                value=round(volume, 0),
                unit=Unit.ML,
                interpretation=Interpretation(
                    summary=f"Transfuse {volume:.0f} mL platelets (10 mL/kg)",
                    detail="Standard pediatric dose: 10-15 mL/kg. Expected rise: 50-100 ?10??L",
                    severity=Severity.NORMAL,
                    recommendations=("Use standard pediatric dose: 10-15 mL/kg",),
                ),
                references=list(self.metadata.references),
            )
        
        if target_platelet <= current_platelet:
            raise ValueError("Target platelet must be greater than current")
        
        # Get EBV using helper function
        ebv_per_kg = get_ebv_per_kg(patient_type, default=70)
        ebv = weight_kg * ebv_per_kg
        
        # Calculate platelet increment needed
        plt_deficit = target_platelet - current_platelet
        
        # Estimated platelet yield per unit
        product = BLOOD_PRODUCTS[product_type]
        
        if product_type == "platelets":
            # Apheresis unit: ~3?10¹¹ platelets per unit
            # Expected increment = (Platelets transfused ? 10¹¹) / (Blood volume in L ? 10)
            # Simplified: 1 apheresis unit raises PLT by ~30-60 ?10??L in 70kg adult
            expected_rise_per_unit = product["expected_plt_rise_per_unit"]
            correction_factor = 70 / weight_kg  # Adjust for weight
            units_needed = plt_deficit / (expected_rise_per_unit * correction_factor)
            volume = units_needed * product["volume_per_unit_ml"]
        else:
            # Random donor platelets
            expected_rise_per_unit = product["expected_plt_rise_per_unit"]
            correction_factor = 70 / weight_kg
            units_needed = plt_deficit / (expected_rise_per_unit * correction_factor)
            volume = units_needed * product["volume_per_unit_ml"]
        
        interpretation = Interpretation(
            summary=f"Transfuse {volume:.0f} mL platelets (~{units_needed:.1f} units)",
            detail=f"Raise platelets from {current_platelet:.0f} to {target_platelet:.0f} ?10??L. Deficit: {plt_deficit:.0f}",
            severity=Severity.NORMAL,
            recommendations=(f"Give to raise platelets from {current_platelet:.0f} to {target_platelet:.0f} ?10??L",),
        )
        
        return ScoreResult(
            tool_name="Platelet Transfusion Volume",
            tool_id="transfusion_calc",
            value=round(volume, 0),
            unit=Unit.ML,
            interpretation=interpretation,
            references=list(self.metadata.references),
        )
    
    def _calculate_ffp_dose(self, weight_kg: float) -> ScoreResult:
        """Calculate FFP dose"""
        product = BLOOD_PRODUCTS["ffp"]
        dose_ml_per_kg = product["dose_ml_per_kg"]
        volume = weight_kg * dose_ml_per_kg
        units = volume / product["volume_per_unit_ml"]
        
        interpretation = Interpretation(
            summary=f"FFP dose: {volume:.0f} mL ({dose_ml_per_kg} mL/kg)",
            detail=f"Give {volume:.0f} mL FFP (~{units:.1f} units). Expected to increase factors by 20-30%",
            severity=Severity.NORMAL,
            recommendations=(f"Give {volume:.0f} mL FFP (~{units:.1f} units)",),
        )
        
        return ScoreResult(
            tool_name="FFP Volume",
            tool_id="transfusion_calc",
            value=round(volume, 0),
            unit=Unit.ML,
            interpretation=interpretation,
            references=list(self.metadata.references),
        )
    
    def _calculate_cryo_dose(self, weight_kg: float) -> ScoreResult:
        """Calculate cryoprecipitate dose"""
        product = BLOOD_PRODUCTS["cryoprecipitate"]
        units = weight_kg / 10  # 1 unit per 10 kg
        if units < 1:
            units = 1
        volume = units * product["volume_per_unit_ml"]
        fibrinogen = units * product["fibrinogen_per_unit_mg"]
        
        interpretation = Interpretation(
            summary=f"Cryoprecipitate dose: {units:.0f} units ({volume:.0f} mL)",
            detail=f"Give {units:.0f} units cryoprecipitate. Estimated fibrinogen: {fibrinogen:.0f} mg. Each unit contains ~250 mg fibrinogen.",
            severity=Severity.NORMAL,
            recommendations=(f"Give {units:.0f} units cryoprecipitate",),
        )
        
        return ScoreResult(
            tool_name="Cryoprecipitate Dose",
            tool_id="transfusion_calc",
            value=round(units, 0),
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.metadata.references),
        )
