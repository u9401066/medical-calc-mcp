"""
Wells Score for DVT Calculator

Estimates the pretest probability of deep vein thrombosis (DVT) in patients
with suspected DVT to guide diagnostic workup.

Original Reference:
    Wells PS, Anderson DR, Bormanis J, et al. Value of assessment of 
    pretest probability of deep-vein thrombosis in clinical management. 
    Lancet. 1997;350(9094):1795-1798.
    doi:10.1016/S0140-6736(97)08140-3. PMID: 9428249.

Validation Reference:
    Wells PS, Anderson DR, Rodger M, et al. Evaluation of D-dimer in 
    the diagnosis of suspected deep-vein thrombosis. N Engl J Med. 
    2003;349(13):1227-1235.
    doi:10.1056/NEJMoa023153. PMID: 14507948.
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


class WellsDvtCalculator(BaseCalculator):
    """
    Wells Score for DVT (Deep Vein Thrombosis)
    
    Scoring criteria:
    - Active cancer (treatment within 6 months or palliative): +1
    - Paralysis, paresis, or recent cast of lower extremity: +1
    - Recently bedridden >3 days or major surgery within 12 weeks: +1
    - Localized tenderness along deep venous system: +1
    - Entire leg swollen: +1
    - Calf swelling >3 cm compared to other leg: +1
    - Pitting edema in symptomatic leg: +1
    - Collateral superficial veins (non-varicose): +1
    - Previously documented DVT: +1
    - Alternative diagnosis at least as likely as DVT: -2
    
    Risk stratification:
    - ≤0: Low probability (~5% DVT)
    - 1-2: Moderate probability (~17% DVT)
    - ≥3: High probability (~53% DVT)
    
    Two-level model:
    - ≤1: Unlikely (<10% DVT)
    - ≥2: Likely (~25% DVT)
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="wells_dvt",
                name="Wells Score for DVT",
                purpose="Estimate pretest probability of DVT to guide diagnostic workup",
                input_params=[
                    "active_cancer",
                    "paralysis_paresis_or_recent_cast",
                    "bedridden_or_major_surgery",
                    "tenderness_along_deep_veins",
                    "entire_leg_swollen",
                    "calf_swelling_gt_3cm",
                    "pitting_edema",
                    "collateral_superficial_veins",
                    "previous_dvt",
                    "alternative_diagnosis_likely",
                ],
                output_type="Score with DVT probability and diagnostic recommendations"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.HEMATOLOGY,
                    Specialty.SURGERY,
                ),
                conditions=(
                    "deep vein thrombosis",
                    "DVT",
                    "venous thromboembolism",
                    "VTE",
                    "leg swelling",
                    "suspected DVT",
                    "lower extremity edema",
                ),
                clinical_contexts=(
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.RISK_STRATIFICATION,
                ),
                clinical_questions=(
                    "Does this patient have a DVT?",
                    "Should I order a D-dimer or ultrasound?",
                    "What is the probability of DVT in this patient?",
                    "Can I rule out DVT with a D-dimer?",
                    "Should this patient with leg swelling get an ultrasound?",
                ),
                icd10_codes=(
                    "I82.4",  # Acute embolism and thrombosis of deep veins of lower extremity
                    "I82.40",  # Acute embolism and thrombosis of unspecified deep veins of lower extremity
                    "I80.2",  # Phlebitis and thrombophlebitis of other deep vessels of lower extremities
                ),
                keywords=(
                    "Wells score",
                    "Wells criteria",
                    "DVT probability",
                    "deep vein thrombosis",
                    "D-dimer",
                    "leg swelling",
                    "venous ultrasound",
                    "VTE workup",
                )
            ),
            references=(
                Reference(
                    citation="Wells PS, Anderson DR, Bormanis J, et al. Value of assessment of "
                             "pretest probability of deep-vein thrombosis in clinical management. "
                             "Lancet. 1997;350(9094):1795-1798.",
                    doi="10.1016/S0140-6736(97)08140-3",
                    pmid="9428249",
                    year=1997,
                ),
                Reference(
                    citation="Wells PS, Anderson DR, Rodger M, et al. Evaluation of D-dimer in "
                             "the diagnosis of suspected deep-vein thrombosis. N Engl J Med. "
                             "2003;349(13):1227-1235.",
                    doi="10.1056/NEJMoa023153",
                    pmid="14507948",
                    year=2003,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )
    
    def calculate(
        self,
        active_cancer: bool,
        paralysis_paresis_or_recent_cast: bool,
        bedridden_or_major_surgery: bool,
        tenderness_along_deep_veins: bool,
        entire_leg_swollen: bool,
        calf_swelling_gt_3cm: bool,
        pitting_edema: bool,
        collateral_superficial_veins: bool,
        previous_dvt: bool,
        alternative_diagnosis_likely: bool,
    ) -> ScoreResult:
        """
        Calculate Wells score for DVT.
        
        Args:
            active_cancer: Active cancer (treatment ongoing, within 6 months, or palliative)
            paralysis_paresis_or_recent_cast: Paralysis, paresis, or recent plaster cast of leg
            bedridden_or_major_surgery: Recently bedridden >3 days or major surgery within 12 weeks
            tenderness_along_deep_veins: Localized tenderness along the deep venous system
            entire_leg_swollen: Entire leg swollen
            calf_swelling_gt_3cm: Calf swelling >3 cm compared to asymptomatic leg
            pitting_edema: Pitting edema confined to symptomatic leg
            collateral_superficial_veins: Collateral superficial veins (non-varicose)
            previous_dvt: Previously documented DVT
            alternative_diagnosis_likely: Alternative diagnosis at least as likely as DVT
            
        Returns:
            ScoreResult with Wells score, DVT probability, and diagnostic recommendations
        """
        # Calculate score
        score = 0
        score += 1 if active_cancer else 0
        score += 1 if paralysis_paresis_or_recent_cast else 0
        score += 1 if bedridden_or_major_surgery else 0
        score += 1 if tenderness_along_deep_veins else 0
        score += 1 if entire_leg_swollen else 0
        score += 1 if calf_swelling_gt_3cm else 0
        score += 1 if pitting_edema else 0
        score += 1 if collateral_superficial_veins else 0
        score += 1 if previous_dvt else 0
        score -= 2 if alternative_diagnosis_likely else 0
        
        # Determine interpretation
        interpretation = self._interpret_score(score)
        
        # Component details
        components = {
            "Active cancer": 1 if active_cancer else 0,
            "Paralysis/paresis/recent cast": 1 if paralysis_paresis_or_recent_cast else 0,
            "Bedridden >3d or major surgery": 1 if bedridden_or_major_surgery else 0,
            "Tenderness along deep veins": 1 if tenderness_along_deep_veins else 0,
            "Entire leg swollen": 1 if entire_leg_swollen else 0,
            "Calf swelling >3 cm difference": 1 if calf_swelling_gt_3cm else 0,
            "Pitting edema (symptomatic leg)": 1 if pitting_edema else 0,
            "Collateral superficial veins": 1 if collateral_superficial_veins else 0,
            "Previously documented DVT": 1 if previous_dvt else 0,
            "Alternative diagnosis likely": -2 if alternative_diagnosis_likely else 0,
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
    
    def _interpret_score(self, score: int) -> Interpretation:
        """Generate interpretation based on Wells DVT score"""
        
        # Two-level model (most commonly used)
        if score <= 1:
            # DVT Unlikely
            severity = Severity.MILD
            risk_level = RiskLevel.LOW
            dvt_probability = "~10%"
            category = "DVT Unlikely"
            summary = f"Wells DVT = {score}: {category} ({dvt_probability} probability)"
            detail = (
                f"Low pretest probability of DVT (approximately {dvt_probability}). "
                f"D-dimer can be used to rule out DVT if negative."
            )
            recommendations = [
                "Order high-sensitivity D-dimer",
                "If D-dimer negative: DVT effectively ruled out",
                "If D-dimer positive: Proceed to compression ultrasound",
            ]
            next_steps = [
                "Obtain D-dimer (high-sensitivity assay)",
                "Negative D-dimer excludes DVT (NPV >99%)",
                "Positive D-dimer requires ultrasound confirmation",
                "Consider alternative diagnoses (cellulitis, Baker's cyst, etc.)",
            ]
            
        else:
            # DVT Likely (score ≥2)
            if score >= 3:
                severity = Severity.SEVERE
                risk_level = RiskLevel.HIGH
                dvt_probability = "~53%"
            else:
                severity = Severity.MODERATE
                risk_level = RiskLevel.INTERMEDIATE
                dvt_probability = "~25%"
            
            category = "DVT Likely"
            summary = f"Wells DVT = {score}: {category} ({dvt_probability} probability)"
            detail = (
                f"Elevated pretest probability of DVT (approximately {dvt_probability}). "
                f"Compression ultrasound is recommended as first-line test."
            )
            recommendations = [
                "Order compression ultrasound (proximal leg veins)",
                "D-dimer alone cannot exclude DVT at this probability",
                "If ultrasound negative but clinical suspicion high, repeat in 5-7 days",
            ]
            next_steps = [
                "Proceed directly to duplex ultrasound",
                "If proximal DVT confirmed: Initiate anticoagulation",
                "If isolated distal DVT: Consider serial ultrasound vs anticoagulation",
                "If negative but suspicion remains: Repeat ultrasound in 1 week",
            ]
            
            if score >= 3:
                recommendations.insert(0, "Consider initiating empiric anticoagulation while awaiting imaging")
        
        # Three-level interpretation (for reference)
        if score <= 0:
            three_level = "Low probability (~5%)"
        elif score <= 2:
            three_level = "Moderate probability (~17%)"
        else:
            three_level = "High probability (~53%)"
        
        return Interpretation(
            summary=summary,
            severity=severity,
            detail=detail,
            stage=f"Wells DVT = {score}",
            stage_description=f"Two-level: {category} | Three-level: {three_level}",
            risk_level=risk_level,
            recommendations=tuple(recommendations),
            next_steps=tuple(next_steps),
            warnings=(
                "High probability of DVT - consider empiric anticoagulation",
            ) if score >= 3 else tuple(),
        )
