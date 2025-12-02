"""
Body Surface Area (BSA) Calculator

Calculates body surface area using multiple validated formulas.
Essential for chemotherapy dosing, fluid calculations, and burn assessment.

References:
    Du Bois D, Du Bois EF. A formula to estimate the approximate surface area
    if height and weight be known. Arch Intern Med. 1916;17(6):863-871.
    DOI: 10.1001/archinte.1916.00080130010002
    
    Mosteller RD. Simplified calculation of body-surface area.
    N Engl J Med. 1987;317(17):1098.
    DOI: 10.1056/NEJM198710223171717
    PMID: 3657876
    
    Haycock GB, Schwartz GJ, Wisotsky DH. Geometric method for measuring
    body surface area: a height-weight formula validated in infants,
    children, and adults.
    J Pediatr. 1978;93(1):62-66.
    DOI: 10.1016/S0022-3476(78)80601-5
    PMID: 650346
    
    Boyd E. The growth of the surface area of the human body.
    Minneapolis: University of Minnesota Press; 1935.
"""

from typing import Literal
import math

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


class BodySurfaceAreaCalculator(BaseCalculator):
    """
    Body Surface Area (BSA) Calculator
    
    Calculates BSA using multiple validated formulas:
    
    Formulas:
        Du Bois (1916) - Classic reference standard:
            BSA = 0.007184 × weight^0.425 × height^0.725
            
        Mosteller (1987) - Simplified, widely used:
            BSA = √(height × weight / 3600)
            
        Haycock (1978) - Validated in pediatrics:
            BSA = 0.024265 × weight^0.5378 × height^0.3964
            
        Boyd (1935) - Historical:
            BSA = 0.0003207 × weight^(0.7285 - 0.0188×log10(weight)) × height^0.3
            
    Clinical Applications:
        - Chemotherapy dosing (most drugs dosed per m²)
        - Cardiac output indexing (CI = CO/BSA)
        - Burn percentage calculation reference
        - Renal function normalization (GFR/1.73m²)
        - Pediatric drug dosing
        
    Normal BSA:
        - Adult male: ~1.9 m²
        - Adult female: ~1.6 m²
        - Newborn: ~0.25 m²
        - Child (10 yr): ~1.1 m²
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="body_surface_area",
                name="Body Surface Area (BSA)",
                purpose="Calculate BSA for chemotherapy dosing, cardiac indexing, and burn assessment",
                input_params=["height_cm", "weight_kg", "formula"],
                output_type="BSA (m²) with multiple formula results"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.ONCOLOGY,
                    Specialty.PEDIATRICS,
                    Specialty.CARDIOLOGY,
                    Specialty.CRITICAL_CARE,
                    Specialty.ANESTHESIOLOGY,
                    Specialty.SURGERY,
                    Specialty.INTERNAL_MEDICINE,
                ),
                conditions=(
                    "Cancer",
                    "Chemotherapy",
                    "Burns",
                    "Heart failure",
                    "Cardiac output",
                    "Pediatric dosing",
                    "Drug dosing",
                ),
                clinical_contexts=(
                    ClinicalContext.DRUG_DOSING,
                    ClinicalContext.TREATMENT_DECISION,
                    ClinicalContext.PHYSIOLOGIC,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "What is the patient's body surface area?",
                    "How do I calculate BSA for chemotherapy?",
                    "What BSA formula should I use?",
                    "How do I calculate cardiac index?",
                    "What is the BSA for burn calculation?",
                ),
                icd10_codes=(
                    "C00-C96",  # Malignant neoplasms
                    "T20-T32",  # Burns
                    "I50",      # Heart failure
                ),
            ),
            references=(
                Reference(
                    citation=(
                        "Du Bois D, Du Bois EF. A formula to estimate the approximate "
                        "surface area if height and weight be known. "
                        "Arch Intern Med. 1916;17(6):863-871."
                    ),
                    doi="10.1001/archinte.1916.00080130010002",
                    year=1916,
                ),
                Reference(
                    citation=(
                        "Mosteller RD. Simplified calculation of body-surface area. "
                        "N Engl J Med. 1987;317(17):1098."
                    ),
                    doi="10.1056/NEJM198710223171717",
                    pmid="3657876",
                    year=1987,
                ),
                Reference(
                    citation=(
                        "Haycock GB, Schwartz GJ, Wisotsky DH. Geometric method for "
                        "measuring body surface area: a height-weight formula validated "
                        "in infants, children, and adults. J Pediatr. 1978;93(1):62-66."
                    ),
                    doi="10.1016/S0022-3476(78)80601-5",
                    pmid="650346",
                    year=1978,
                ),
            ),
        )
    
    def calculate(
        self,
        height_cm: float,
        weight_kg: float,
        formula: Literal["mosteller", "dubois", "haycock", "boyd"] = "mosteller",
    ) -> ScoreResult:
        """
        Calculate body surface area.
        
        Args:
            height_cm: Height in centimeters (50-250)
            weight_kg: Weight in kilograms (1-500)
            formula: Formula to use (default: mosteller)
                - "mosteller": Simplified, most common
                - "dubois": Classic reference standard
                - "haycock": Validated in pediatrics
                - "boyd": Historical
                
        Returns:
            ScoreResult with BSA in m²
            
        Raises:
            ValueError: If parameters are out of valid range
        """
        # Validate inputs
        if not 50 <= height_cm <= 250:
            raise ValueError(f"Height must be 50-250 cm, got {height_cm}")
        if not 1 <= weight_kg <= 500:
            raise ValueError(f"Weight must be 1-500 kg, got {weight_kg}")
        
        # Calculate BSA using all formulas
        bsa_mosteller = math.sqrt((height_cm * weight_kg) / 3600)
        bsa_dubois = 0.007184 * (weight_kg ** 0.425) * (height_cm ** 0.725)
        bsa_haycock = 0.024265 * (weight_kg ** 0.5378) * (height_cm ** 0.3964)
        
        # Boyd formula - corrected formula
        log_weight = math.log10(weight_kg)
        bsa_boyd = 0.03330 * (weight_kg ** (0.6157 - 0.0188 * log_weight)) * (height_cm ** 0.3)
        
        # Select primary result based on chosen formula
        formula_map = {
            "mosteller": bsa_mosteller,
            "dubois": bsa_dubois,
            "haycock": bsa_haycock,
            "boyd": bsa_boyd,
        }
        
        primary_bsa = formula_map[formula]
        
        # Get interpretation
        interpretation = self._get_interpretation(primary_bsa, weight_kg)
        
        return ScoreResult(
            tool_id=self.tool_id,
            tool_name=self.name,
            value=round(primary_bsa, 4),
            unit=Unit.M2,
            interpretation=interpretation,
            references=self.references,
            calculation_details={
                "primary_formula": formula,
                "height_cm": height_cm,
                "weight_kg": weight_kg,
                "all_formulas": {
                    "mosteller": round(bsa_mosteller, 4),
                    "dubois": round(bsa_dubois, 4),
                    "haycock": round(bsa_haycock, 4),
                    "boyd": round(bsa_boyd, 4),
                },
                "formula_descriptions": {
                    "mosteller": "√(height × weight / 3600) - Simplified, most common",
                    "dubois": "0.007184 × W^0.425 × H^0.725 - Classic reference",
                    "haycock": "0.024265 × W^0.5378 × H^0.3964 - Validated in pediatrics",
                    "boyd": "0.0003207 × H^0.3 × W^(0.7285-0.0188×logW) - Historical",
                },
                "typical_applications": {
                    "chemotherapy_dosing": "Most drugs dosed as mg/m²",
                    "cardiac_index": f"CI = CO / {round(primary_bsa, 2)} m²",
                    "gfr_normalization": "eGFR standardized to 1.73 m²",
                },
            },
        )
    
    def _get_interpretation(self, bsa: float, weight_kg: float) -> Interpretation:
        """Generate interpretation based on BSA value"""
        
        # Determine category based on BSA
        if bsa < 0.5:
            category = "Infant/Small Child"
            severity = Severity.NORMAL
        elif bsa < 1.0:
            category = "Child/Small Adult"
            severity = Severity.NORMAL
        elif bsa < 1.5:
            category = "Small Adult"
            severity = Severity.NORMAL
        elif bsa < 2.0:
            category = "Average Adult"
            severity = Severity.NORMAL
        elif bsa < 2.5:
            category = "Large Adult"
            severity = Severity.NORMAL
        else:
            category = "Very Large/Obese"
            severity = Severity.MILD
        
        return Interpretation(
            summary=f"BSA: {bsa:.2f} m² - {category}",
            detail=(
                f"Body surface area: {bsa:.4f} m². "
                f"Category: {category}. "
                f"BSA is used for standardizing physiologic parameters and drug dosing. "
                f"Normal adult range: 1.5-2.0 m²."
            ),
            severity=severity,
            recommendations=(
                "Use BSA for chemotherapy dosing (most cytotoxic agents)",
                "Calculate cardiac index: CI = Cardiac Output / BSA",
                "For obese patients, consider dose capping strategies",
                "Haycock formula preferred for pediatric patients",
                "Verify formula consistency within treatment protocol",
            ),
            warnings=(
                "BSA may overestimate drug clearance in obese patients",
                "Some protocols cap BSA at 2.0 m² for dosing",
                "Different formulas may give slightly different results",
            ) if bsa > 2.0 else (),
            next_steps=(
                "Apply to chemotherapy protocol dosing",
                "Calculate cardiac index if hemodynamic assessment needed",
                "Document formula used for consistency",
            ),
        )
