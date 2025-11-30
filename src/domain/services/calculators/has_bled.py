"""
HAS-BLED Score Calculator

Estimates bleeding risk in patients with atrial fibrillation on anticoagulation.
Used alongside CHA₂DS₂-VASc to balance stroke prevention vs bleeding risk.

Original Reference:
    Pisters R, Lane DA, Nieuwlaat R, et al. A novel user-friendly score 
    (HAS-BLED) to assess 1-year risk of major bleeding in patients with 
    atrial fibrillation: the Euro Heart Survey. Chest. 2010;138(5):1093-1100.
    doi:10.1378/chest.10-0134. PMID: 20299623.

2024 ESC AF Guidelines recommend using HAS-BLED alongside CHA₂DS₂-VA for
anticoagulation decision-making:
    Van Gelder IC, et al. Eur Heart J. 2024;45(36):3314-3414.
    doi:10.1093/eurheartj/ehae176. PMID: 39217497.
"""

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


class HasBledCalculator(BaseCalculator):
    """
    HAS-BLED Score for Bleeding Risk in Atrial Fibrillation
    
    Scoring criteria (each 1 point):
    - H: Hypertension (uncontrolled, SBP >160 mmHg)
    - A: Abnormal renal and/or liver function (1 point each, max 2)
    - S: Stroke history
    - B: Bleeding history or predisposition
    - L: Labile INR (TTR <60%, if on warfarin)
    - E: Elderly (age >65 years)
    - D: Drugs (antiplatelet agents, NSAIDs) and/or alcohol (≥8 drinks/week)
         (1 point each, max 2)
    
    Maximum score: 9
    
    Risk stratification:
    - 0-2: Low bleeding risk
    - ≥3: High bleeding risk - address modifiable risk factors
    
    IMPORTANT: High HAS-BLED score is NOT a contraindication to anticoagulation.
    Rather, it identifies patients needing closer monitoring and modification
    of reversible bleeding risk factors.
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="has_bled",
                name="HAS-BLED Score",
                purpose="Assess 1-year major bleeding risk in AF patients on anticoagulation",
                input_params=[
                    "hypertension_uncontrolled",
                    "renal_disease",
                    "liver_disease",
                    "stroke_history",
                    "bleeding_history",
                    "labile_inr",
                    "elderly_gt_65",
                    "drugs_antiplatelet_nsaid",
                    "alcohol_excess",
                ],
                output_type="Score 0-9 with annual major bleeding risk and recommendations"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.CARDIOLOGY,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.HEMATOLOGY,
                ),
                conditions=(
                    "atrial fibrillation",
                    "AF",
                    "Afib",
                    "anticoagulation",
                    "bleeding risk",
                    "warfarin",
                    "DOAC",
                ),
                clinical_contexts=(
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.TREATMENT_DECISION,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "What is the bleeding risk for this AF patient on anticoagulation?",
                    "Is anticoagulation safe for this patient?",
                    "Should I adjust anticoagulation due to bleeding risk?",
                    "How do I balance stroke and bleeding risk in AF?",
                    "What modifiable bleeding risk factors should I address?",
                ),
                icd10_codes=(
                    "I48",  # Atrial fibrillation and flutter
                    "D68.9",  # Coagulation defect, unspecified
                    "Z79.01",  # Long term (current) use of anticoagulants
                ),
                keywords=(
                    "HAS-BLED",
                    "HASBLED",
                    "bleeding risk AF",
                    "anticoagulation bleeding",
                    "major bleeding risk",
                    "warfarin bleeding",
                    "DOAC bleeding",
                    "stroke vs bleeding",
                )
            ),
            references=(
                Reference(
                    citation="Pisters R, Lane DA, Nieuwlaat R, et al. A novel user-friendly "
                             "score (HAS-BLED) to assess 1-year risk of major bleeding in "
                             "patients with atrial fibrillation: the Euro Heart Survey. "
                             "Chest. 2010;138(5):1093-1100.",
                    doi="10.1378/chest.10-0134",
                    pmid="20299623",
                    year=2010,
                ),
                Reference(
                    citation="Van Gelder IC, Rienstra M, Bunting KV, et al. 2024 ESC "
                             "Guidelines for the management of atrial fibrillation developed "
                             "in collaboration with EACTS. Eur Heart J. 2024;45(36):3314-3414.",
                    doi="10.1093/eurheartj/ehae176",
                    pmid="39217497",
                    year=2024,
                ),
                Reference(
                    citation="Lip GYH, Lane DA. Assessing bleeding risk in atrial fibrillation "
                             "with the HAS-BLED score: balancing simplicity, practicality, and "
                             "predictive value in bleeding-risk assessment. Clin Cardiol. "
                             "2010;33(9):E4-E5.",
                    doi="10.1002/clc.20823",
                    pmid="20842654",
                    year=2010,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )
    
    def calculate(
        self,
        hypertension_uncontrolled: bool,
        renal_disease: bool,
        liver_disease: bool,
        stroke_history: bool,
        bleeding_history: bool,
        labile_inr: bool = False,
        elderly_gt_65: bool = False,
        drugs_antiplatelet_nsaid: bool = False,
        alcohol_excess: bool = False,
    ) -> ScoreResult:
        """
        Calculate HAS-BLED score.
        
        Args:
            hypertension_uncontrolled: Uncontrolled hypertension (SBP >160 mmHg)
            renal_disease: Chronic dialysis, renal transplant, or Cr >2.26 mg/dL (200 μmol/L)
            liver_disease: Chronic hepatic disease (cirrhosis) or biochemical evidence
                          (bilirubin >2x ULN with AST/ALT/ALP >3x ULN)
            stroke_history: Previous stroke (ischemic or hemorrhagic)
            bleeding_history: Previous major bleeding or predisposition (anemia, bleeding diathesis)
            labile_inr: Unstable/high INRs, TTR <60% (only if on warfarin)
            elderly_gt_65: Age >65 years
            drugs_antiplatelet_nsaid: Concomitant antiplatelet agents or NSAIDs
            alcohol_excess: Alcohol excess (≥8 drinks/week)
            
        Returns:
            ScoreResult with score, bleeding risk, and management recommendations
        """
        # Calculate score
        score = 0
        score += 1 if hypertension_uncontrolled else 0
        score += 1 if renal_disease else 0
        score += 1 if liver_disease else 0
        score += 1 if stroke_history else 0
        score += 1 if bleeding_history else 0
        score += 1 if labile_inr else 0
        score += 1 if elderly_gt_65 else 0
        score += 1 if drugs_antiplatelet_nsaid else 0
        score += 1 if alcohol_excess else 0
        
        # Determine interpretation
        interpretation = self._interpret_score(
            score,
            hypertension_uncontrolled,
            renal_disease,
            liver_disease,
            labile_inr,
            drugs_antiplatelet_nsaid,
            alcohol_excess,
        )
        
        # Component details
        components = {
            "H - Hypertension (uncontrolled)": 1 if hypertension_uncontrolled else 0,
            "A - Abnormal renal function": 1 if renal_disease else 0,
            "A - Abnormal liver function": 1 if liver_disease else 0,
            "S - Stroke history": 1 if stroke_history else 0,
            "B - Bleeding history/predisposition": 1 if bleeding_history else 0,
            "L - Labile INR (if on warfarin)": 1 if labile_inr else 0,
            "E - Elderly (>65 years)": 1 if elderly_gt_65 else 0,
            "D - Drugs (antiplatelet/NSAID)": 1 if drugs_antiplatelet_nsaid else 0,
            "D - Alcohol excess (≥8 drinks/wk)": 1 if alcohol_excess else 0,
        }
        
        return ScoreResult(
            tool_name=self.low_level_key.name,
            tool_id=self.low_level_key.tool_id,
            value=score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            calculation_details=components,
            references=list(self.references),
        )
    
    def _interpret_score(
        self,
        score: int,
        hypertension: bool,
        renal: bool,
        liver: bool,
        labile_inr: bool,
        drugs: bool,
        alcohol: bool,
    ) -> Interpretation:
        """Generate interpretation based on HAS-BLED score"""
        
        # Annual major bleeding risk rates from Pisters et al. 2010
        bleeding_rates = {
            0: "1.13%",
            1: "1.02%",
            2: "1.88%",
            3: "3.74%",
            4: "8.70%",
            5: "12.50%",
        }
        
        annual_risk = bleeding_rates.get(score, ">12.5%")
        
        # Identify modifiable risk factors
        modifiable_factors = []
        if hypertension:
            modifiable_factors.append("Uncontrolled hypertension - optimize BP control")
        if labile_inr:
            modifiable_factors.append("Labile INR - consider DOAC instead of warfarin, or improve TTR")
        if drugs:
            modifiable_factors.append("Concomitant drugs - review need for antiplatelet agents/NSAIDs")
        if alcohol:
            modifiable_factors.append("Alcohol excess - counsel on alcohol reduction")
        
        if score <= 2:
            # Low bleeding risk
            severity = Severity.NORMAL if score <= 1 else Severity.MILD
            risk_level = RiskLevel.LOW
            summary = f"HAS-BLED = {score}: Low bleeding risk ({annual_risk} annual major bleeding)"
            detail = (
                f"Low risk of major bleeding. Annual major bleeding rate is approximately {annual_risk}. "
                f"Anticoagulation generally well tolerated in this risk category."
            )
            recommendations = [
                "Low bleeding risk supports anticoagulation if indicated by CHA₂DS₂-VASc",
                "Standard anticoagulation monitoring appropriate",
                "Periodic reassessment of bleeding risk factors",
            ]
            next_steps = [
                "Calculate CHA₂DS₂-VASc for stroke risk if not done",
                "Choose anticoagulant based on patient factors",
                "Standard follow-up schedule",
            ]
            
        else:
            # High bleeding risk (≥3)
            if score == 3:
                severity = Severity.MODERATE
                risk_level = RiskLevel.INTERMEDIATE
            elif score == 4:
                severity = Severity.SEVERE
                risk_level = RiskLevel.HIGH
            else:  # ≥5
                severity = Severity.CRITICAL
                risk_level = RiskLevel.VERY_HIGH
            
            summary = f"HAS-BLED = {score}: High bleeding risk ({annual_risk} annual major bleeding)"
            detail = (
                f"Elevated risk of major bleeding. Annual major bleeding rate is approximately {annual_risk}. "
                f"This does NOT contraindicate anticoagulation, but requires careful risk-benefit analysis "
                f"and modification of reversible risk factors."
            )
            recommendations = [
                "High HAS-BLED is NOT a contraindication to anticoagulation",
                "Identify and address modifiable bleeding risk factors",
                "Consider DOAC over warfarin (generally lower ICH risk)",
                "More frequent clinical monitoring recommended",
                "Ensure patient education on bleeding signs and symptoms",
            ]
            
            if modifiable_factors:
                recommendations.extend([
                    "Modifiable risk factors identified:",
                    *[f"  • {f}" for f in modifiable_factors],
                ])
            
            next_steps = [
                "Address all modifiable bleeding risk factors",
                "Review concurrent medications for bleeding risk",
                "Optimize blood pressure control if hypertensive",
                "Consider GI protection (PPI) if indicated",
                "Schedule more frequent follow-up visits",
            ]
            
            if labile_inr:
                next_steps.append("Consider switching from warfarin to DOAC for better TTR equivalent")
        
        # Warnings for very high risk
        warnings = []
        if score >= 4:
            warnings.append(
                f"Very high bleeding risk (HAS-BLED {score}). Requires careful benefit-risk discussion "
                f"and close monitoring. Address all modifiable factors before/during anticoagulation."
            )
        if renal or liver:
            warnings.append(
                "Renal or hepatic dysfunction present - may affect anticoagulant choice and dosing."
            )
        
        return Interpretation(
            summary=summary,
            severity=severity,
            detail=detail,
            stage=f"HAS-BLED = {score}",
            stage_description=f"Annual major bleeding risk: {annual_risk}",
            risk_level=risk_level,
            recommendations=tuple(recommendations),
            next_steps=tuple(next_steps),
            warnings=tuple(warnings),
        )
