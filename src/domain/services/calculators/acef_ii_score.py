"""
ACEF II Score Calculator

Age, Creatinine, Ejection Fraction score for cardiac surgery mortality prediction.

Reference:
    Ranucci M, Pistuddi V, Scolletta S, et al. The ACEF II Risk Score for 
    cardiac surgery: updated but still parsimonious. Eur Heart J. 
    2018;39(23):2183-2189.
    DOI: 10.1093/eurheartj/ehx228
    PMID: 28498904
    
    Nashef SA, Roques F, Sharples LD, et al. EuroSCORE II. Eur J Cardiothorac 
    Surg. 2012;41(4):734-744.
    DOI: 10.1093/ejcts/ezs043
    PMID: 22378855
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
    ClinicalContext,
)


class AcefIiScoreCalculator(BaseCalculator):
    """
    ACEF II Score Calculator
    
    The ACEF II score is a parsimonious (simple) risk prediction model for
    30-day mortality after cardiac surgery. It uses only 3 variables but
    achieves discrimination similar to more complex scores.
    
    Formula:
        ACEF II = Age / LVEF + 2 (if creatinine >2.0 mg/dL)
        
        Where:
        - Age in years
        - LVEF as percentage (not decimal)
        - Emergency surgery doubles the score
        
    Risk Categories:
        - ACEF II <1.0: Low risk (~1% mortality)
        - ACEF II 1.0-2.0: Intermediate risk (2-5% mortality)
        - ACEF II 2.0-3.0: High risk (5-10% mortality)
        - ACEF II >3.0: Very high risk (>10% mortality)
        
    Advantages:
        - Only 3 variables (vs 18+ in EuroSCORE II)
        - Easy bedside calculation
        - Well-validated in multiple cohorts
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="acef_ii",
                name="ACEF II Score",
                purpose="Predict cardiac surgery mortality risk",
                input_params=["age", "lvef", "creatinine", "emergency"],
                output_type="ACEF II score with mortality risk"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.CARDIOLOGY,
                    Specialty.SURGERY,
                    Specialty.ANESTHESIOLOGY,
                    Specialty.CRITICAL_CARE,
                ),
                conditions=(
                    "Cardiac surgery",
                    "CABG",
                    "Valve surgery",
                    "Aortic surgery",
                    "Heart failure",
                    "Coronary artery disease",
                ),
                clinical_contexts=(
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.PREOPERATIVE_ASSESSMENT,
                    ClinicalContext.TREATMENT_DECISION,
                ),
                clinical_questions=(
                    "What is this patient's cardiac surgery mortality risk?",
                    "Should we operate on this high-risk cardiac patient?",
                    "What is the ACEF score?",
                    "How does this compare to EuroSCORE?",
                ),
                icd10_codes=("Z95.1", "I25.1", "I35.0"),
                keywords=(
                    "ACEF", "ACEF II", "cardiac surgery", "mortality", "risk",
                    "CABG", "valve", "EuroSCORE", "STS score",
                    "preoperative", "risk stratification",
                ),
            ),
            references=self._get_references(),
        )
    
    def _get_references(self) -> tuple[Reference, ...]:
        return (
            Reference(
                citation="Ranucci M, Pistuddi V, Scolletta S, et al. The ACEF II Risk Score for cardiac surgery: updated but still parsimonious. Eur Heart J. 2018;39(23):2183-2189.",
                doi="10.1093/eurheartj/ehx228",
                pmid="28498904",
                year=2018,
            ),
            Reference(
                citation="Original ACEF: Ranucci M, et al. Cardiac surgery operative mortality risk: a Bayesian approach. Ann Thorac Surg. 2009;87(3):878-884.",
                doi="10.1016/j.athoracsur.2008.11.001",
                pmid="19231409",
                year=2009,
            ),
        )
    
    def calculate(
        self,
        age: int,
        lvef: float,
        creatinine: float,
        emergency: bool = False,
    ) -> ScoreResult:
        """
        Calculate ACEF II score.
        
        Args:
            age: Patient age (years)
            lvef: Left ventricular ejection fraction (%, e.g., 55 for 55%)
            creatinine: Serum creatinine (mg/dL)
            emergency: Emergency surgery (doubles the score)
            
        Returns:
            ScoreResult with ACEF II score and mortality risk
        """
        # Validate inputs
        if age < 18 or age > 100:
            raise ValueError(f"Age {age} is outside expected range (18-100)")
        if lvef < 5 or lvef > 80:
            raise ValueError(f"LVEF {lvef}% is outside expected range (5-80%)")
        if creatinine < 0.3 or creatinine > 15:
            raise ValueError(f"Creatinine {creatinine} is outside expected range (0.3-15 mg/dL)")
        
        # Calculate ACEF II score
        # Base: Age / LVEF
        base_score = age / lvef
        
        # Add 2 if creatinine > 2.0 mg/dL
        creatinine_adjustment = 2 if creatinine > 2.0 else 0
        
        acef_score = base_score + creatinine_adjustment
        
        # Double if emergency
        if emergency:
            acef_score = acef_score * 2
        
        acef_score = round(acef_score, 2)
        
        # Estimate mortality
        mortality_estimate = self._estimate_mortality(acef_score)
        
        # Generate interpretation
        interpretation = self._interpret_acef(acef_score, mortality_estimate, lvef, creatinine, emergency)
        
        # Build calculation details
        details = {
            "Age": f"{age} years",
            "LVEF": f"{lvef}%",
            "Base_score": f"{age}/{lvef} = {base_score:.2f}",
            "Creatinine": f"{creatinine} mg/dL",
            "Creatinine_adjustment": f"+{creatinine_adjustment}" if creatinine > 2.0 else "0 (Cr ≤2.0)",
            "Emergency_surgery": "Yes (×2)" if emergency else "No",
            "ACEF_II_score": f"{acef_score}",
            "Estimated_mortality": f"{mortality_estimate}%",
        }
        
        return ScoreResult(
            value=acef_score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=self._get_references(),
            tool_id=self.tool_id,
            tool_name=self.metadata.name,
            raw_inputs={
                "age": age,
                "lvef": lvef,
                "creatinine": creatinine,
                "emergency": emergency,
            },
            calculation_details=details,
            formula_used="ACEF II = (Age / LVEF) + 2 (if Cr >2.0) × 2 (if emergency)",
        )
    
    def _estimate_mortality(self, acef_score: float) -> float:
        """Estimate 30-day mortality based on ACEF II score."""
        # Based on calibration data from Ranucci 2018
        if acef_score < 1.0:
            return round(0.5 + acef_score * 0.5, 1)
        elif acef_score < 2.0:
            return round(1.0 + (acef_score - 1.0) * 3, 1)
        elif acef_score < 3.0:
            return round(4.0 + (acef_score - 2.0) * 6, 1)
        elif acef_score < 4.0:
            return round(10.0 + (acef_score - 3.0) * 10, 1)
        else:
            return round(min(20.0 + (acef_score - 4.0) * 5, 50), 1)
    
    def _interpret_acef(
        self,
        acef_score: float,
        mortality: float,
        lvef: float,
        creatinine: float,
        emergency: bool,
    ) -> Interpretation:
        """Generate interpretation and recommendations."""
        
        # Risk stratification
        if acef_score < 1.0:
            risk_category = "Low risk"
            severity = Severity.MILD
            risk_level = RiskLevel.LOW
        elif acef_score < 2.0:
            risk_category = "Intermediate risk"
            severity = Severity.MODERATE
            risk_level = RiskLevel.INTERMEDIATE
        elif acef_score < 3.0:
            risk_category = "High risk"
            severity = Severity.SEVERE
            risk_level = RiskLevel.HIGH
        else:
            risk_category = "Very high risk"
            severity = Severity.CRITICAL
            risk_level = RiskLevel.VERY_HIGH
        
        summary = f"ACEF II Score {acef_score}: {risk_category} (Est. mortality {mortality}%)"
        detail = f"Predicted 30-day mortality: approximately {mortality}%. ACEF II provides similar discrimination to EuroSCORE II with fewer variables."
        
        # Recommendations
        if acef_score < 1.0:
            recommendations = (
                "Low operative risk - proceed with surgery",
                "Standard preoperative optimization",
                "Routine postoperative care",
            )
        elif acef_score < 2.0:
            recommendations = (
                "Intermediate operative risk",
                "Optimize modifiable risk factors preoperatively",
                "Consider renal protection strategies if Cr elevated",
                "Ensure adequate postoperative monitoring",
            )
        elif acef_score < 3.0:
            recommendations = (
                "High operative risk - careful consideration needed",
                "Multidisciplinary heart team discussion recommended",
                "Consider less invasive alternatives if available (TAVR, PCI)",
                "Optimize heart failure therapy preoperatively",
                "ICU bed reservation",
            )
        else:
            recommendations = (
                "⚠️ Very high operative risk",
                "Heart team discussion mandatory",
                "Consider palliative/conservative management",
                "If surgery proceeds, prepare for complex ICU course",
                "Detailed informed consent with realistic expectations",
                "Consider ECMO/mechanical support availability",
            )
        
        warnings = []
        if lvef < 30:
            warnings.append("⚠️ Severely reduced LVEF (<30%): Higher risk of low cardiac output syndrome")
        if creatinine > 2.0:
            warnings.append("⚠️ Elevated creatinine (>2.0): Higher risk of postoperative AKI")
        if emergency:
            warnings.append("⚠️ Emergency surgery: Mortality risk significantly elevated")
        if acef_score >= 3.0:
            warnings.append("🚨 ACEF II ≥3: Very high mortality risk, consider alternatives")
        
        return Interpretation(
            summary=summary,
            detail=detail,
            severity=severity,
            risk_level=risk_level,
            recommendations=recommendations,
            warnings=tuple(warnings),
            next_steps=(
                "Complete preoperative cardiac evaluation",
                "Optimize GDMT for heart failure if applicable",
                "Check creatinine clearance, consider nephrology if CKD",
                "Heart team conference for high-risk patients",
            ),
        )
