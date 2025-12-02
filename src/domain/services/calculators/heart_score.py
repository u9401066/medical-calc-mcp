"""
HEART Score Calculator

Identifies emergency department patients with chest pain at low risk for
major adverse cardiac events (MACE) to guide disposition decisions.

Original Reference:
    Six AJ, Backus BE, Kelder JC. Chest pain in the emergency room: 
    value of the HEART score. Neth Heart J. 2008;16(6):191-196.
    doi:10.1007/BF03086144. PMID: 18665203.
    
Validation Reference:
    Backus BE, Six AJ, Kelder JC, et al. A prospective validation of 
    the HEART score for chest pain patients at the emergency department. 
    Int J Cardiol. 2013;168(3):2153-2158.
    doi:10.1016/j.ijcard.2013.01.255. PMID: 23465250.
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


class HeartScoreCalculator(BaseCalculator):
    """
    HEART Score for Major Adverse Cardiac Events (MACE)
    
    Scoring criteria (each 0-2 points):
    - History: Slightly suspicious (0), Moderately suspicious (1), Highly suspicious (2)
    - ECG: Normal (0), Non-specific changes (1), Significant ST deviation (2)
    - Age: <45 (0), 45-64 (1), ≥65 (2)
    - Risk factors: None (0), 1-2 (1), ≥3 or atherosclerosis (2)
    - Troponin: Normal (0), 1-3x ULN (1), >3x ULN (2)
    
    Risk stratification (6-week MACE):
    - 0-3: Low risk (0.9-1.7%) → Consider early discharge
    - 4-6: Moderate risk (12-16.6%) → Admit for observation
    - 7-10: High risk (50-65%) → Admit for intervention
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="heart_score",
                name="HEART Score",
                purpose="Stratify risk of major adverse cardiac events in ED chest pain patients",
                input_params=[
                    "history_score",
                    "ecg_score",
                    "age_score",
                    "risk_factors_score",
                    "troponin_score",
                ],
                output_type="Score 0-10 with MACE risk and disposition recommendation"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.CARDIOLOGY,
                    Specialty.INTERNAL_MEDICINE,
                ),
                conditions=(
                    "chest pain",
                    "acute coronary syndrome",
                    "ACS",
                    "NSTEMI",
                    "unstable angina",
                    "myocardial infarction",
                    "suspected ACS",
                ),
                clinical_contexts=(
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.DISPOSITION,
                    ClinicalContext.DIAGNOSIS,
                ),
                clinical_questions=(
                    "Can this chest pain patient be safely discharged?",
                    "What is the MACE risk for this chest pain patient?",
                    "Does this patient need admission for ACS workup?",
                    "Is this chest pain patient low risk?",
                    "Should this patient go to cath lab?",
                ),
                icd10_codes=(
                    "I20",  # Angina pectoris
                    "I21",  # Acute myocardial infarction
                    "I24",  # Other acute ischemic heart diseases
                    "R07.9",  # Chest pain, unspecified
                ),
                keywords=(
                    "HEART score",
                    "chest pain risk",
                    "ACS risk stratification",
                    "MACE risk",
                    "cardiac event prediction",
                    "troponin",
                    "emergency chest pain",
                )
            ),
            references=(
                Reference(
                    citation="Six AJ, Backus BE, Kelder JC. Chest pain in the emergency room: "
                             "value of the HEART score. Neth Heart J. 2008;16(6):191-196.",
                    doi="10.1007/BF03086144",
                    pmid="18665203",
                    year=2008,
                ),
                Reference(
                    citation="Backus BE, Six AJ, Kelder JC, et al. A prospective validation of "
                             "the HEART score for chest pain patients at the emergency department. "
                             "Int J Cardiol. 2013;168(3):2153-2158.",
                    doi="10.1016/j.ijcard.2013.01.255",
                    pmid="23465250",
                    year=2013,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )
    
    def calculate(
        self,
        history_score: int,
        ecg_score: int,
        age_score: int,
        risk_factors_score: int,
        troponin_score: int,
    ) -> ScoreResult:
        """
        Calculate HEART score.
        
        Args:
            history_score: 0=slightly suspicious, 1=moderately suspicious, 2=highly suspicious
            ecg_score: 0=normal, 1=non-specific changes, 2=significant ST deviation
            age_score: 0=<45y, 1=45-64y, 2=≥65y
            risk_factors_score: 0=none, 1=1-2 factors, 2=≥3 factors or known atherosclerosis
            troponin_score: 0=normal, 1=1-3x ULN, 2=>3x ULN
            
        Returns:
            ScoreResult with HEART score, MACE risk, and disposition recommendation
        """
        # Validate inputs
        for name, val in [
            ("history_score", history_score),
            ("ecg_score", ecg_score),
            ("age_score", age_score),
            ("risk_factors_score", risk_factors_score),
            ("troponin_score", troponin_score),
        ]:
            if not 0 <= val <= 2:
                raise ValueError(f"{name} must be 0, 1, or 2")
        
        # Calculate total score
        score = history_score + ecg_score + age_score + risk_factors_score + troponin_score
        
        # Determine interpretation
        interpretation = self._interpret_score(score)
        
        # Component details
        history_desc = ["Slightly suspicious", "Moderately suspicious", "Highly suspicious"]
        ecg_desc = ["Normal", "Non-specific changes", "Significant ST deviation"]
        age_desc = ["<45 years", "45-64 years", "≥65 years"]
        rf_desc = ["No risk factors", "1-2 risk factors", "≥3 factors or atherosclerosis"]
        trop_desc = ["Normal", "1-3× ULN", ">3× ULN"]
        
        components = {
            f"H - History ({history_desc[history_score]})": history_score,
            f"E - ECG ({ecg_desc[ecg_score]})": ecg_score,
            f"A - Age ({age_desc[age_score]})": age_score,
            f"R - Risk factors ({rf_desc[risk_factors_score]})": risk_factors_score,
            f"T - Troponin ({trop_desc[troponin_score]})": troponin_score,
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
        """Generate interpretation based on HEART score"""
        
        if score <= 3:
            # Low risk
            severity = Severity.MILD
            risk_level = RiskLevel.LOW
            mace_risk = "0.9-1.7%"
            summary = f"HEART Score = {score}: Low risk ({mace_risk} 6-week MACE)"
            detail = (
                f"Low risk for major adverse cardiac events. The 6-week MACE rate for "
                f"HEART score ≤3 is approximately {mace_risk}. Early discharge may be "
                f"appropriate with proper follow-up."
            )
            recommendations = [
                "Consider early discharge if clinically appropriate",
                "Outpatient follow-up with cardiology or PCP within 72 hours",
                "Provide chest pain action plan",
                "Stress testing as outpatient may be considered",
            ]
            next_steps = [
                "Ensure serial troponins are negative",
                "Verify ECG shows no ischemic changes",
                "Assess ability to follow up reliably",
                "Provide nitroglycerin if indicated",
            ]
            
        elif score <= 6:
            # Moderate risk
            severity = Severity.MODERATE
            risk_level = RiskLevel.INTERMEDIATE
            mace_risk = "12-16.6%"
            summary = f"HEART Score = {score}: Moderate risk ({mace_risk} 6-week MACE)"
            detail = (
                f"Moderate risk for major adverse cardiac events. The 6-week MACE rate "
                f"is approximately {mace_risk}. Hospital admission for observation "
                f"and further workup is recommended."
            )
            recommendations = [
                "Admit for observation and serial troponins",
                "Continuous cardiac monitoring",
                "Consider stress testing or coronary CTA",
                "Cardiology consultation",
            ]
            next_steps = [
                "Serial troponins every 3-6 hours",
                "Repeat ECG if symptoms recur",
                "Echocardiogram if not recently performed",
                "Risk factor modification counseling",
            ]
            
        else:
            # High risk (score 7-10)
            severity = Severity.SEVERE
            risk_level = RiskLevel.HIGH
            mace_risk = "50-65%"
            summary = f"HEART Score = {score}: High risk ({mace_risk} 6-week MACE)"
            detail = (
                f"High risk for major adverse cardiac events. The 6-week MACE rate "
                f"is approximately {mace_risk}. Urgent intervention is likely needed."
            )
            recommendations = [
                "Admit to cardiac care unit",
                "Early invasive strategy strongly recommended",
                "Dual antiplatelet therapy and anticoagulation",
                "Urgent cardiology consultation for catheterization",
            ]
            next_steps = [
                "Initiate ACS protocol (aspirin, P2Y12 inhibitor, anticoagulation)",
                "Arrange coronary angiography within 24 hours",
                "Continuous telemetry monitoring",
                "Assess for hemodynamic instability",
            ]
        
        return Interpretation(
            summary=summary,
            severity=severity,
            detail=detail,
            stage=f"HEART Score = {score}",
            stage_description=f"6-week MACE risk: {mace_risk}",
            risk_level=risk_level,
            recommendations=tuple(recommendations),
            next_steps=tuple(next_steps),
            warnings=(
                "High MACE risk - urgent cardiac evaluation required",
            ) if score >= 7 else tuple(),
        )
