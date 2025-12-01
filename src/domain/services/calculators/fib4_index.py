"""
FIB-4 Index for Liver Fibrosis

Non-invasive assessment of liver fibrosis using age and routine lab values.

Reference:
    Sterling RK, Lissen E, Clumeck N, et al.
    Development of a simple noninvasive index to predict significant fibrosis
    in patients with HIV/HCV coinfection.
    Hepatology. 2006;43(6):1317-1325.
    DOI: 10.1002/hep.21178
    PMID: 16729309
"""

from typing import Literal

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
    ClinicalContext
)


class Fib4IndexCalculator(BaseCalculator):
    """
    FIB-4 Index for Liver Fibrosis Assessment
    
    Simple, validated non-invasive tool to assess hepatic fibrosis.
    
    Formula: FIB-4 = (Age × AST) / (Platelets × √ALT)
    
    Interpretation (Sterling 2006, revised):
    - <1.30: Low risk of advanced fibrosis (F0-F1), NPV ~90%
    - 1.30-2.67: Indeterminate, consider further testing
    - >2.67: High risk of advanced fibrosis (F3-F4), PPV ~65%
    
    Age-adjusted cutoffs (for age >65):
    - <2.0: Low risk
    - 2.0-3.25: Indeterminate
    - >3.25: High risk
    
    Note: Best validated in HCV, useful in NAFLD/NASH
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="fib4_index",
                name="FIB-4 Index",
                purpose="Non-invasive assessment of liver fibrosis",
                input_params=[
                    "age_years",
                    "ast",
                    "alt",
                    "platelet_count"
                ],
                output_type="FIB-4 index value with fibrosis stage prediction"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.HEPATOLOGY,
                    Specialty.GASTROENTEROLOGY,
                    Specialty.INTERNAL_MEDICINE,
                ),
                conditions=(
                    "Chronic Hepatitis C",
                    "Chronic Hepatitis B",
                    "NAFLD",
                    "NASH",
                    "Alcoholic Liver Disease",
                    "Liver Fibrosis",
                    "Cirrhosis Screening",
                ),
                clinical_contexts=(
                    ClinicalContext.SCREENING,
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.MONITORING,
                    ClinicalContext.DIAGNOSIS,
                ),
                clinical_questions=(
                    "Does this patient have advanced liver fibrosis?",
                    "Should I refer this patient for elastography or biopsy?",
                    "What is the likelihood of cirrhosis?",
                    "Is further workup for fibrosis needed?",
                ),
                icd10_codes=(
                    "K74.0",   # Hepatic fibrosis
                    "K74.6",   # Other and unspecified cirrhosis of liver
                    "K76.0",   # Fatty liver
                    "K75.81",  # Nonalcoholic steatohepatitis
                    "B18.2",   # Chronic viral hepatitis C
                ),
                keywords=(
                    "FIB-4", "fibrosis", "cirrhosis", "liver", "hepatitis",
                    "NAFLD", "NASH", "HCV", "non-invasive",
                    "elastography", "platelet", "AST", "ALT",
                )
            ),
            references=(
                Reference(
                    citation="Sterling RK, Lissen E, Clumeck N, et al. "
                             "Development of a simple noninvasive index to predict "
                             "significant fibrosis in patients with HIV/HCV coinfection. "
                             "Hepatology. 2006;43(6):1317-1325.",
                    doi="10.1002/hep.21178",
                    pmid="16729309",
                    year=2006
                ),
                Reference(
                    citation="McPherson S, Hardy T, Dufour JF, et al. "
                             "Age as a Confounding Factor for the Accurate Non-Invasive "
                             "Diagnosis of Advanced NAFLD Fibrosis. "
                             "Am J Gastroenterol. 2017;112(5):740-751.",
                    doi="10.1038/ajg.2016.453",
                    pmid="27725647",
                    year=2017
                ),
            ),
            version="1.0.0",
            validation_status="validated"
        )

    def calculate(
        self,
        age_years: int,
        ast: float,
        alt: float,
        platelet_count: float
    ) -> ScoreResult:
        """
        Calculate FIB-4 Index.
        
        Args:
            age_years: Patient age in years (typically 18-90)
            ast: AST (SGOT) in U/L
            alt: ALT (SGPT) in U/L
            platelet_count: Platelet count in 10^9/L (K/µL)
            
        Returns:
            ScoreResult with FIB-4 index and fibrosis risk interpretation
        """
        # Validate inputs
        if age_years < 18 or age_years > 100:
            raise ValueError("Age must be between 18 and 100 years")
        if ast <= 0 or ast > 5000:
            raise ValueError("AST must be between 0 and 5000 U/L")
        if alt <= 0 or alt > 5000:
            raise ValueError("ALT must be between 0 and 5000 U/L")
        if platelet_count <= 0 or platelet_count > 1000:
            raise ValueError("Platelet count must be between 0 and 1000 × 10^9/L")
        
        # Calculate FIB-4
        import math
        fib4 = (age_years * ast) / (platelet_count * math.sqrt(alt))
        
        # Round to 2 decimal places
        fib4 = round(fib4, 2)
        
        # Determine cutoffs based on age
        if age_years > 65:
            # Age-adjusted cutoffs for elderly
            low_cutoff = 2.0
            high_cutoff = 3.25
            using_age_adjusted = True
        else:
            # Standard cutoffs
            low_cutoff = 1.30
            high_cutoff = 2.67
            using_age_adjusted = False
        
        # Get interpretation
        interpretation = self._get_interpretation(
            fib4, low_cutoff, high_cutoff, using_age_adjusted
        )
        
        # Build result
        return ScoreResult(
            value=fib4,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "age_years": age_years,
                "ast": ast,
                "alt": alt,
                "platelet_count": platelet_count
            },
            calculation_details={
                "fib4_index": fib4,
                "formula": "(Age × AST) / (Platelets × √ALT)",
                "component_values": {
                    "age_component": age_years * ast,
                    "platelet_alt_component": round(platelet_count * math.sqrt(alt), 2)
                },
                "low_cutoff": low_cutoff,
                "high_cutoff": high_cutoff,
                "using_age_adjusted_cutoffs": using_age_adjusted,
                "fibrosis_prediction": self._get_fibrosis_prediction(fib4, low_cutoff, high_cutoff),
                "confidence": self._get_confidence(fib4, low_cutoff, high_cutoff)
            },
            formula_used=f"FIB-4 = ({age_years} × {ast}) / ({platelet_count} × √{alt}) = {fib4}",
            notes=self._get_notes(fib4, low_cutoff, high_cutoff, using_age_adjusted)
        )
    
    def _get_fibrosis_prediction(
        self, fib4: float, low_cutoff: float, high_cutoff: float
    ) -> str:
        """Get predicted fibrosis stage."""
        if fib4 < low_cutoff:
            return "F0-F1 (No to minimal fibrosis)"
        elif fib4 > high_cutoff:
            return "F3-F4 (Advanced fibrosis/cirrhosis)"
        else:
            return "Indeterminate (F2 possible)"
    
    def _get_confidence(
        self, fib4: float, low_cutoff: float, high_cutoff: float
    ) -> str:
        """Get confidence level of prediction."""
        if fib4 < low_cutoff:
            return "High NPV (~90%) - can rule out advanced fibrosis"
        elif fib4 > high_cutoff:
            return "Moderate PPV (~65%) - further testing recommended"
        else:
            return "Indeterminate - cannot reliably stage fibrosis"
    
    def _get_interpretation(
        self,
        fib4: float,
        low_cutoff: float,
        high_cutoff: float,
        using_age_adjusted: bool
    ) -> Interpretation:
        """Get clinical interpretation."""
        if fib4 < low_cutoff:
            return Interpretation(
                summary=f"FIB-4 = {fib4}: Low Risk of Advanced Fibrosis",
                detail=f"FIB-4 <{low_cutoff} suggests F0-F1 (no/minimal fibrosis). "
                       f"NPV ~90% for excluding advanced fibrosis.",
                severity=Severity.MILD,
                risk_level=RiskLevel.LOW,
                stage="Low Risk",
                stage_description="Likely no advanced fibrosis",
                recommendations=(
                    "Advanced fibrosis unlikely",
                    "Continue standard monitoring",
                    "Repeat FIB-4 in 1-3 years if risk factors persist",
                    "Address underlying cause (HCV treatment, NAFLD lifestyle)",
                ),
                warnings=None,
                next_steps=(
                    "No immediate need for elastography or biopsy",
                    "Manage underlying liver disease",
                    "Routine surveillance appropriate",
                )
            )
        elif fib4 > high_cutoff:
            return Interpretation(
                summary=f"FIB-4 = {fib4}: High Risk of Advanced Fibrosis",
                detail=f"FIB-4 >{high_cutoff} suggests F3-F4 (advanced fibrosis/cirrhosis). "
                       f"PPV ~65% for advanced fibrosis. Confirm with elastography or biopsy.",
                severity=Severity.SEVERE,
                risk_level=RiskLevel.HIGH,
                stage="High Risk",
                stage_description="Likely advanced fibrosis/cirrhosis",
                recommendations=(
                    "High likelihood of advanced fibrosis (F3-F4)",
                    "Confirm with transient elastography (FibroScan) or biopsy",
                    "Screen for varices if cirrhosis confirmed",
                    "HCC surveillance every 6 months",
                    "Hepatology referral recommended",
                ),
                warnings=(
                    "High risk for cirrhosis complications",
                    "Consider variceal screening",
                    "Monitor for hepatic decompensation",
                ),
                next_steps=(
                    "Transient elastography for confirmation",
                    "EGD for variceal screening if cirrhosis",
                    "Initiate HCC surveillance (US ± AFP q6mo)",
                    "Hepatology evaluation",
                )
            )
        else:
            return Interpretation(
                summary=f"FIB-4 = {fib4}: Indeterminate Risk",
                detail=f"FIB-4 between {low_cutoff} and {high_cutoff} is indeterminate. "
                       f"Cannot reliably exclude or confirm advanced fibrosis. Further testing needed.",
                severity=Severity.MODERATE,
                risk_level=RiskLevel.INTERMEDIATE,
                stage="Indeterminate",
                stage_description="Cannot reliably classify fibrosis stage",
                recommendations=(
                    "Indeterminate result - further testing needed",
                    "Consider transient elastography (FibroScan)",
                    "Alternative: ELF test, APRI, or liver biopsy",
                    "Address modifiable risk factors",
                ),
                warnings=(
                    "FIB-4 cannot reliably classify fibrosis in this range",
                    "Do not use alone for clinical decisions",
                ),
                next_steps=(
                    "Transient elastography recommended",
                    "Consider ELF test or APRI as adjunct",
                    "Liver biopsy if non-invasive tests discordant",
                    "Repeat FIB-4 in 6-12 months if choosing watchful waiting",
                )
            )
    
    def _get_notes(
        self,
        fib4: float,
        low_cutoff: float,
        high_cutoff: float,
        using_age_adjusted: bool
    ) -> list[str]:
        """Get additional clinical notes."""
        notes = []
        
        if using_age_adjusted:
            notes.append("Age-adjusted cutoffs applied (patient >65 years)")
            notes.append(f"Low cutoff: <{low_cutoff}, High cutoff: >{high_cutoff}")
        else:
            notes.append(f"Standard cutoffs: Low <{low_cutoff}, High >{high_cutoff}")
        
        notes.append("Best validated in HCV; also useful in NAFLD/NASH")
        notes.append("Combine with transient elastography for best accuracy")
        
        if fib4 < low_cutoff:
            notes.append("High NPV (~90%) can rule out advanced fibrosis")
        elif fib4 > high_cutoff:
            notes.append("Moderate PPV (~65%) - confirm with elastography")
        else:
            notes.append("Consider ELF, APRI, or elastography for clarification")
        
        return notes
