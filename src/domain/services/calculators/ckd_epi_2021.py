"""
CKD-EPI 2021 Calculator

Calculates estimated glomerular filtration rate (eGFR) using the 2021 CKD-EPI
equation without race coefficient.

Reference:
    Inker LA, Eneanya ND, Coresh J, et al. New Creatinine- and Cystatin C-Based 
    Equations to Estimate GFR without Race. N Engl J Med. 2021;385(19):1737-1749.
    DOI: 10.1056/NEJMoa2102953
    PMID: 34554658
"""

import math
from typing import Literal

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


class CkdEpi2021Calculator(BaseCalculator):
    """
    CKD-EPI 2021 eGFR Calculator (without race)
    
    The 2021 CKD-EPI equation estimates GFR using serum creatinine,
    age, and sex, without the race coefficient that was present in
    the 2009 equation.
    
    Formula:
        eGFR = 142 × min(Scr/κ, 1)^α × max(Scr/κ, 1)^-1.200 × 0.9938^Age × (1.012 if female)
        
        Where:
        - κ = 0.7 (female) or 0.9 (male)
        - α = -0.241 (female) or -0.302 (male)
        - Scr = serum creatinine in mg/dL
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="ckd_epi_2021",
                name="CKD-EPI 2021 (Creatinine, without race)",
                purpose="Calculate estimated glomerular filtration rate (eGFR)",
                input_params=["age", "sex", "serum_creatinine"],
                output_type="eGFR (mL/min/1.73m²)"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.NEPHROLOGY,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.CRITICAL_CARE,
                    Specialty.ANESTHESIOLOGY,
                ),
                conditions=(
                    "Chronic Kidney Disease",
                    "CKD",
                    "Acute Kidney Injury",
                    "AKI",
                    "Renal Insufficiency",
                    "Kidney Disease",
                ),
                clinical_contexts=(
                    ClinicalContext.STAGING,
                    ClinicalContext.DRUG_DOSING,
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.MONITORING,
                    ClinicalContext.PREOPERATIVE_ASSESSMENT,
                ),
                clinical_questions=(
                    "What is the patient's kidney function?",
                    "What stage of CKD does the patient have?",
                    "Does this patient need renal dose adjustment?",
                    "Is the kidney function stable?",
                ),
                icd10_codes=("N18.1", "N18.2", "N18.3", "N18.4", "N18.5", "N18.6", "N18.9"),
                keywords=(
                    "GFR", "eGFR", "creatinine", "kidney", "renal",
                    "CKD", "chronic kidney disease", "kidney function",
                )
            ),
            references=(
                Reference(
                    citation="Inker LA, Eneanya ND, Coresh J, et al. New Creatinine- and "
                             "Cystatin C-Based Equations to Estimate GFR without Race. "
                             "N Engl J Med. 2021;385(19):1737-1749.",
                    doi="10.1056/NEJMoa2102953",
                    pmid="34554658",
                    year=2021
                ),
            ),
            version="1.0.0",
            validation_status="validated"
        )
    
    def calculate(
        self,
        age: int,
        sex: Literal["male", "female"],
        serum_creatinine: float
    ) -> ScoreResult:
        """
        Calculate eGFR using CKD-EPI 2021 equation.
        
        Args:
            age: Patient age in years (18-120)
            sex: Patient sex ("male" or "female")
            serum_creatinine: Serum creatinine in mg/dL (0.1-30)
            
        Returns:
            ScoreResult with eGFR value and CKD staging
        """
        # Validate inputs
        if not 18 <= age <= 120:
            raise ValueError("Age must be between 18 and 120 years")
        if sex not in ("male", "female"):
            raise ValueError("Sex must be 'male' or 'female'")
        if not 0.1 <= serum_creatinine <= 30:
            raise ValueError("Serum creatinine must be between 0.1 and 30 mg/dL")
        
        # CKD-EPI 2021 parameters
        if sex == "female":
            kappa = 0.7
            alpha = -0.241
            sex_coefficient = 1.012
        else:
            kappa = 0.9
            alpha = -0.302
            sex_coefficient = 1.0
        
        # Calculate eGFR
        scr_kappa = serum_creatinine / kappa
        
        egfr = (
            142 
            * (min(scr_kappa, 1) ** alpha)
            * (max(scr_kappa, 1) ** -1.200)
            * (0.9938 ** age)
            * sex_coefficient
        )
        
        # Round to 1 decimal place
        egfr = round(egfr, 1)
        
        # Determine CKD stage and interpretation
        interpretation = self._get_interpretation(egfr)
        
        return ScoreResult(
            value=egfr,
            unit=Unit.ML_MIN_1_73M2,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "age": age,
                "sex": sex,
                "serum_creatinine": serum_creatinine
            },
            calculation_details={
                "equation": "CKD-EPI 2021 (without race)",
                "kappa": kappa,
                "alpha": alpha,
                "sex_coefficient": sex_coefficient
            },
            formula_used="eGFR = 142 × min(Scr/κ, 1)^α × max(Scr/κ, 1)^-1.200 × 0.9938^Age × sex_coef"
        )
    
    def _get_interpretation(self, egfr: float) -> Interpretation:
        """Get CKD staging and clinical interpretation"""
        
        if egfr >= 90:
            return Interpretation(
                summary="Normal or high kidney function (G1)",
                detail="eGFR ≥90 indicates normal kidney function. "
                       "If no other markers of kidney damage, CKD is not present.",
                severity=Severity.NORMAL,
                stage="G1",
                stage_description="Normal or high GFR",
                recommendations=(
                    "No specific renal intervention needed",
                    "Monitor annually if risk factors present",
                    "Most medications can be dosed normally",
                ),
                next_steps=(
                    "Check for other markers of kidney damage (proteinuria, hematuria)",
                    "Address cardiovascular risk factors",
                )
            )
        elif egfr >= 60:
            return Interpretation(
                summary="Mildly decreased kidney function (G2)",
                detail="eGFR 60-89 indicates mildly decreased kidney function. "
                       "CKD diagnosis requires additional markers of kidney damage.",
                severity=Severity.MILD,
                stage="G2",
                stage_description="Mildly decreased GFR",
                recommendations=(
                    "Monitor kidney function annually",
                    "Control blood pressure and diabetes if present",
                    "Avoid nephrotoxic medications when possible",
                ),
                next_steps=(
                    "Check urine albumin-to-creatinine ratio",
                    "Review medication list for nephrotoxins",
                )
            )
        elif egfr >= 45:
            return Interpretation(
                summary="Mildly to moderately decreased kidney function (G3a)",
                detail="eGFR 45-59 indicates CKD Stage G3a. "
                       "Referral to nephrology may be considered.",
                severity=Severity.MILD,
                stage="G3a",
                stage_description="Mildly to moderately decreased GFR",
                recommendations=(
                    "Monitor kidney function every 6 months",
                    "Adjust renally-excreted medications",
                    "Avoid NSAIDs and nephrotoxic agents",
                    "Consider nephrology referral",
                ),
                warnings=(
                    "Some medications require dose adjustment",
                ),
                next_steps=(
                    "Calculate drug doses based on eGFR",
                    "Check for anemia and mineral bone disease",
                )
            )
        elif egfr >= 30:
            return Interpretation(
                summary="Moderately to severely decreased kidney function (G3b)",
                detail="eGFR 30-44 indicates CKD Stage G3b. "
                       "Nephrology referral is recommended.",
                severity=Severity.MODERATE,
                stage="G3b",
                stage_description="Moderately to severely decreased GFR",
                recommendations=(
                    "Nephrology referral recommended",
                    "Monitor kidney function every 3-6 months",
                    "Dose adjust all renally-excreted medications",
                    "Screen for CKD complications",
                ),
                warnings=(
                    "Significant drug dose adjustments needed",
                    "Increased cardiovascular risk",
                ),
                next_steps=(
                    "Refer to nephrology",
                    "Check PTH, calcium, phosphorus, vitamin D",
                    "Check hemoglobin for anemia",
                )
            )
        elif egfr >= 15:
            return Interpretation(
                summary="Severely decreased kidney function (G4)",
                detail="eGFR 15-29 indicates CKD Stage G4. "
                       "Prepare for possible renal replacement therapy.",
                severity=Severity.SEVERE,
                stage="G4",
                stage_description="Severely decreased GFR",
                recommendations=(
                    "Nephrology co-management essential",
                    "Prepare for renal replacement therapy",
                    "Avoid IV contrast if possible",
                    "Careful medication dosing required",
                ),
                warnings=(
                    "High risk of progression to kidney failure",
                    "Many medications contraindicated or need major dose adjustment",
                    "Avoid metformin, NSAIDs",
                ),
                next_steps=(
                    "Discuss dialysis and transplant options",
                    "Consider AV fistula creation if hemodialysis planned",
                    "Vaccinate for hepatitis B",
                )
            )
        else:
            return Interpretation(
                summary="Kidney failure (G5)",
                detail="eGFR <15 indicates kidney failure. "
                       "Renal replacement therapy may be needed.",
                severity=Severity.CRITICAL,
                stage="G5",
                stage_description="Kidney failure",
                recommendations=(
                    "Urgent nephrology consultation",
                    "Evaluate for dialysis initiation",
                    "Consider transplant evaluation",
                    "Strict medication review",
                ),
                warnings=(
                    "Kidney failure - dialysis or transplant may be needed",
                    "Most renally-excreted drugs contraindicated",
                    "High risk of uremic complications",
                ),
                next_steps=(
                    "Initiate dialysis if symptomatic uremia",
                    "Complete transplant workup if candidate",
                    "Optimize conservative management if not dialysis candidate",
                )
            )
