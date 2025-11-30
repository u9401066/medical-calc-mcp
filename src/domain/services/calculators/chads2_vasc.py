"""
CHA₂DS₂-VASc Score Calculator

Estimates stroke risk in patients with atrial fibrillation (AF) to guide
anticoagulation therapy decisions.

Original Reference:
    Lip GY, Nieuwlaat R, Pisters R, et al. Refining clinical risk 
    stratification for predicting stroke and thromboembolism in atrial 
    fibrillation using a novel risk factor-based approach: the euro 
    heart survey on atrial fibrillation. Chest. 2010;137(2):263-272.
    doi:10.1378/chest.09-1584. PMID: 19762550.
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


class Chads2VascCalculator(BaseCalculator):
    """
    CHA₂DS₂-VASc Score for Atrial Fibrillation Stroke Risk
    
    Scoring criteria:
    - Congestive Heart Failure: +1
    - Hypertension: +1
    - Age ≥75 years: +2
    - Diabetes mellitus: +1
    - Stroke/TIA/TE history: +2
    - Vascular disease: +1
    - Age 65-74 years: +1
    - Sex category (female): +1
    
    Maximum score: 9 (male) or 9 (female includes sex modifier)
    
    Anticoagulation recommendations (ESC 2020 guidelines):
    - 0 (male) / 1 (female): No anticoagulation needed
    - 1 (male): Consider anticoagulation (OAC preferred)
    - ≥2: Anticoagulation recommended (OAC)
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="chads2_vasc",
                name="CHA₂DS₂-VASc Score",
                purpose="Estimate annual stroke risk in atrial fibrillation for anticoagulation decisions",
                input_params=[
                    "chf_or_lvef_lte_40",
                    "hypertension",
                    "age_gte_75",
                    "diabetes",
                    "stroke_tia_or_te_history",
                    "vascular_disease",
                    "age_65_to_74",
                    "female_sex",
                ],
                output_type="Score 0-9 with annual stroke risk and anticoagulation recommendation"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.CARDIOLOGY,
                    Specialty.NEUROLOGY,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.EMERGENCY_MEDICINE,
                ),
                conditions=(
                    "atrial fibrillation",
                    "AF",
                    "Afib",
                    "atrial flutter",
                    "stroke prevention",
                    "thromboembolism",
                ),
                clinical_contexts=(
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.TREATMENT_DECISION,
                    ClinicalContext.PROGNOSIS,
                ),
                clinical_questions=(
                    "Does this AF patient need anticoagulation?",
                    "What is the stroke risk for this atrial fibrillation patient?",
                    "Should I prescribe a DOAC for this AF patient?",
                    "Is anticoagulation indicated in this patient with AF?",
                    "What is the annual stroke risk for this patient?",
                ),
                icd10_codes=(
                    "I48",  # Atrial fibrillation and flutter
                    "I48.0",  # Paroxysmal atrial fibrillation
                    "I48.1",  # Persistent atrial fibrillation
                    "I48.2",  # Chronic atrial fibrillation
                    "I48.91",  # Unspecified atrial fibrillation
                ),
                keywords=(
                    "CHA2DS2-VASc",
                    "CHADS-VASc",
                    "CHADS2",
                    "atrial fibrillation stroke risk",
                    "anticoagulation AF",
                    "stroke prevention AF",
                    "DOAC indication",
                    "warfarin indication",
                )
            ),
            references=(
                Reference(
                    citation="Lip GY, Nieuwlaat R, Pisters R, et al. Refining clinical risk "
                             "stratification for predicting stroke and thromboembolism in atrial "
                             "fibrillation using a novel risk factor-based approach: the euro "
                             "heart survey on atrial fibrillation. Chest. 2010;137(2):263-272.",
                    doi="10.1378/chest.09-1584",
                    pmid="19762550",
                    year=2010,
                ),
                Reference(
                    citation="Hindricks G, Potpara T, Dagres N, et al. 2020 ESC Guidelines for "
                             "the diagnosis and management of atrial fibrillation developed in "
                             "collaboration with EACTS. Eur Heart J. 2021;42(5):373-498.",
                    doi="10.1093/eurheartj/ehaa612",
                    pmid="32860505",
                    year=2020,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )
    
    def calculate(
        self,
        chf_or_lvef_lte_40: bool,
        hypertension: bool,
        age_gte_75: bool,
        diabetes: bool,
        stroke_tia_or_te_history: bool,
        vascular_disease: bool,
        age_65_to_74: bool,
        female_sex: bool,
    ) -> ScoreResult:
        """
        Calculate CHA₂DS₂-VASc score.
        
        Args:
            chf_or_lvef_lte_40: CHF or LVEF ≤40%
            hypertension: History of hypertension
            age_gte_75: Age ≥75 years (2 points)
            diabetes: Diabetes mellitus
            stroke_tia_or_te_history: Prior stroke, TIA, or thromboembolism (2 points)
            vascular_disease: Prior MI, PAD, or aortic plaque
            age_65_to_74: Age 65-74 years (1 point; mutually exclusive with age ≥75)
            female_sex: Female sex
            
        Returns:
            ScoreResult with score, stroke risk, and anticoagulation recommendation
        """
        # Calculate score
        score = 0
        score += 1 if chf_or_lvef_lte_40 else 0
        score += 1 if hypertension else 0
        score += 2 if age_gte_75 else 0
        score += 1 if diabetes else 0
        score += 2 if stroke_tia_or_te_history else 0
        score += 1 if vascular_disease else 0
        score += 1 if age_65_to_74 and not age_gte_75 else 0  # Only if not ≥75
        score += 1 if female_sex else 0
        
        # Determine interpretation
        interpretation = self._interpret_score(score, female_sex)
        
        # Component details
        components = {
            "C - CHF/LVEF ≤40%": 1 if chf_or_lvef_lte_40 else 0,
            "H - Hypertension": 1 if hypertension else 0,
            "A₂ - Age ≥75": 2 if age_gte_75 else 0,
            "D - Diabetes": 1 if diabetes else 0,
            "S₂ - Stroke/TIA/TE history": 2 if stroke_tia_or_te_history else 0,
            "V - Vascular disease": 1 if vascular_disease else 0,
            "A - Age 65-74": 1 if (age_65_to_74 and not age_gte_75) else 0,
            "Sc - Sex category (female)": 1 if female_sex else 0,
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
    
    def _interpret_score(self, score: int, female_sex: bool) -> Interpretation:
        """Generate interpretation based on CHA₂DS₂-VASc score"""
        
        # Annual stroke risk rates (adjusted from Lip et al. 2010 and meta-analyses)
        stroke_rates = {
            0: "0%",
            1: "1.3%",
            2: "2.2%",
            3: "3.2%",
            4: "4.0%",
            5: "6.7%",
            6: "9.8%",
            7: "9.6%",
            8: "12.5%",
            9: "15.2%",
        }
        
        annual_risk = stroke_rates.get(score, ">15%")
        
        # For females, score of 1 = no increased risk (sex modifier alone)
        adjusted_score = score - 1 if female_sex else score
        
        if adjusted_score <= 0:
            # Low risk - no anticoagulation needed
            severity = Severity.NORMAL
            risk_level = RiskLevel.LOW
            summary = f"CHA₂DS₂-VASc = {score}: Low risk ({annual_risk} annual stroke risk)"
            detail = (
                f"Low stroke risk. The annual ischemic stroke rate is approximately {annual_risk}. "
                f"{'Female sex alone does not indicate anticoagulation.' if female_sex and score == 1 else ''}"
            )
            recommendations = [
                "Anticoagulation not recommended based on CHA₂DS₂-VASc alone",
                "Consider aspirin only if other indications exist",
                "Reassess risk factors annually",
            ]
            next_steps = [
                "Address modifiable risk factors (hypertension, diabetes)",
                "Lifestyle modifications for cardiovascular health",
                "Annual reassessment of CHA₂DS₂-VASc score",
            ]
            anticoagulation = "Not indicated"
            
        elif adjusted_score == 1:
            # Intermediate risk - consider anticoagulation
            severity = Severity.MILD
            risk_level = RiskLevel.LOW
            summary = f"CHA₂DS₂-VASc = {score}: Low-moderate risk ({annual_risk} annual stroke risk)"
            detail = (
                f"Borderline stroke risk. Annual ischemic stroke rate is approximately {annual_risk}. "
                f"Anticoagulation should be considered after weighing bleeding risk."
            )
            recommendations = [
                "Consider oral anticoagulation (OAC)",
                "Assess bleeding risk with HAS-BLED score",
                "Shared decision-making with patient",
                "DOACs preferred over warfarin if OAC chosen",
            ]
            next_steps = [
                "Calculate HAS-BLED score for bleeding risk",
                "Discuss stroke vs bleeding risk with patient",
                "If anticoagulation chosen, DOAC is first-line",
                "Address modifiable bleeding risk factors",
            ]
            anticoagulation = "Consider (individualized decision)"
            
        else:
            # High risk - anticoagulation recommended
            severity = Severity.MODERATE if score <= 4 else Severity.SEVERE
            risk_level = RiskLevel.INTERMEDIATE if score <= 4 else RiskLevel.HIGH
            summary = f"CHA₂DS₂-VASc = {score}: {'High' if score > 4 else 'Moderate'} risk ({annual_risk} annual stroke risk)"
            detail = (
                f"Significant stroke risk. Annual ischemic stroke rate is approximately {annual_risk}. "
                f"Oral anticoagulation is recommended."
            )
            recommendations = [
                "Oral anticoagulation (OAC) is recommended",
                "DOACs preferred over warfarin (except mechanical valves, moderate-severe MS)",
                "Aspirin alone is not adequate for stroke prevention",
            ]
            next_steps = [
                "Assess renal function for DOAC dosing",
                "Calculate HAS-BLED to identify modifiable bleeding risks",
                "Choose appropriate DOAC based on patient factors",
                "Ensure patient education on anticoagulation",
            ]
            
            if score >= 6:
                recommendations.append("Very high stroke risk - ensure compliance with anticoagulation")
            
            anticoagulation = "Recommended"
        
        return Interpretation(
            summary=summary,
            severity=severity,
            detail=detail,
            stage=f"CHA₂DS₂-VASc = {score}",
            stage_description=f"Annual stroke risk: {annual_risk}",
            risk_level=risk_level,
            recommendations=tuple(recommendations),
            next_steps=tuple(next_steps),
            warnings=(
                "High stroke risk - anticoagulation essential",
            ) if score >= 4 else tuple(),
        )
