"""
Centor Score Calculator (Modified/McIsaac)

Estimates probability of Group A Streptococcal pharyngitis in patients with sore throat.
Guides decision for rapid strep testing and empiric antibiotic therapy.

Original Reference:
    Centor RM, Witherspoon JM, Dalton HP, Brody CE, Link K. 
    The diagnosis of strep throat in adults in the emergency room. 
    Med Decis Making. 1981;1(3):239-246.
    doi:10.1177/0272989X8100100304. PMID: 6763125.

McIsaac Modification (age adjustment):
    McIsaac WJ, White D, Tannenbaum D, Low DE. 
    A clinical score to reduce unnecessary antibiotic use in patients with sore throat.
    CMAJ. 1998;158(1):75-83. PMID: 9475915.
"""

from typing import Optional
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


class CentorScoreCalculator(BaseCalculator):
    """
    Centor Score (Modified/McIsaac) for Strep Pharyngitis
    
    Original Centor Criteria (1 point each):
    - Tonsillar exudates
    - Tender anterior cervical lymphadenopathy
    - Fever (history or measured >38°C)
    - Absence of cough
    
    McIsaac Modification (age adjustment):
    - Age 3-14 years: +1
    - Age 15-44 years: 0
    - Age ≥45 years: -1
    
    Management recommendations:
    - 0-1: No testing or antibiotics needed (1-10% probability)
    - 2-3: Rapid strep test, treat if positive (11-35% probability)
    - 4-5: Consider empiric treatment or test-and-treat (52% probability)
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="centor_score",
                name="Centor Score (Modified/McIsaac)",
                purpose="Estimate probability of GAS pharyngitis and guide testing/treatment decisions",
                input_params=[
                    "tonsillar_exudates",
                    "tender_anterior_cervical_nodes",
                    "fever",
                    "absence_of_cough",
                    "age_group",
                ],
                output_type="Score -1 to 5 with GAS probability and management recommendation"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.INFECTIOUS_DISEASE,
                    Specialty.PEDIATRICS,
                ),
                conditions=(
                    "pharyngitis",
                    "sore throat",
                    "strep throat",
                    "streptococcal pharyngitis",
                    "GAS pharyngitis",
                    "tonsillitis",
                    "upper respiratory infection",
                ),
                clinical_contexts=(
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.TREATMENT_DECISION,
                    ClinicalContext.RISK_STRATIFICATION,
                ),
            ),
            references=[
                Reference(
                    citation="Centor RM, et al. Med Decis Making. 1981;1(3):239-246.",
                    pmid="6763125",
                    doi="10.1177/0272989X8100100304",
                ),
                Reference(
                    citation="McIsaac WJ, et al. CMAJ. 1998;158(1):75-83. (McIsaac modification)",
                    pmid="9475915",
                ),
                Reference(
                    citation="Shulman ST, et al. Clin Infect Dis. 2012;55(10):e86-e102. (IDSA Guidelines)",
                    pmid="22965026",
                    doi="10.1093/cid/cis629",
                ),
            ],
        )
    
    def calculate(
        self,
        tonsillar_exudates: bool,
        tender_anterior_cervical_nodes: bool,
        fever: bool,
        absence_of_cough: bool,
        age_group: Optional[str] = None,  # "pediatric", "adult", "older_adult"
    ) -> ScoreResult:
        """
        Calculate Centor/McIsaac Score.
        
        Args:
            tonsillar_exudates: Tonsillar exudates present
            tender_anterior_cervical_nodes: Tender anterior cervical lymphadenopathy
            fever: History of fever or measured temperature >38°C (100.4°F)
            absence_of_cough: Patient does NOT have cough
            age_group: Age category for McIsaac modification
                - "pediatric": 3-14 years (+1)
                - "adult": 15-44 years (0)
                - "older_adult": ≥45 years (-1)
                - None: Use original Centor score (no age adjustment)
            
        Returns:
            ScoreResult with Centor/McIsaac score and management recommendation
        """
        score = 0
        components = {}
        
        # Original Centor criteria
        if tonsillar_exudates:
            score += 1
            components["exudates"] = "Tonsillar exudates (+1)"
        else:
            components["exudates"] = "No tonsillar exudates (+0)"
        
        if tender_anterior_cervical_nodes:
            score += 1
            components["lymphadenopathy"] = "Tender anterior cervical nodes (+1)"
        else:
            components["lymphadenopathy"] = "No tender lymphadenopathy (+0)"
        
        if fever:
            score += 1
            components["fever"] = "Fever history or >38°C (+1)"
        else:
            components["fever"] = "No fever (+0)"
        
        if absence_of_cough:
            score += 1
            components["cough"] = "Absence of cough (+1)"
        else:
            components["cough"] = "Cough present (+0)"
        
        # McIsaac age modification
        score_type = "Original Centor"
        if age_group:
            score_type = "Modified Centor (McIsaac)"
            if age_group == "pediatric":
                score += 1
                components["age"] = "Age 3-14 years (+1)"
            elif age_group == "adult":
                components["age"] = "Age 15-44 years (+0)"
            elif age_group == "older_adult":
                score -= 1
                components["age"] = "Age ≥45 years (-1)"
        
        # Generate interpretation
        interpretation = self._interpret_score(score, score_type)
        
        return ScoreResult(
            tool_name=self.low_level_key.name,
            tool_id=self.low_level_key.tool_id,
            value=score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            calculation_details=components,
            references=list(self.references),
        )
    
    def _interpret_score(self, score: int, score_type: str) -> Interpretation:
        """Generate interpretation based on Centor/McIsaac score"""
        
        if score <= 0:
            severity = Severity.NORMAL
            risk_level = RiskLevel.VERY_LOW
            probability = "1-2.5%"
            summary = f"{score_type} Score {score}: Very low probability of GAS ({probability})"
            detail = (
                "Very low probability of GAS pharyngitis. "
                "No testing or antibiotics indicated. Symptomatic treatment only. "
                "Consider alternative diagnoses (viral pharyngitis, mononucleosis)."
            )
            recommendations = [
                "No testing or antibiotics needed",
                "Symptomatic treatment only",
                "Consider alternative diagnoses",
            ]
            next_steps = [
                "Provide symptomatic care (analgesics, fluids)",
                "Return precautions if worsening",
            ]
        elif score == 1:
            severity = Severity.MILD
            risk_level = RiskLevel.LOW
            probability = "5-10%"
            summary = f"{score_type} Score {score}: Low probability of GAS ({probability})"
            detail = (
                "Low probability of GAS pharyngitis. "
                "Testing and antibiotics generally not recommended unless high-risk setting. "
                "Symptomatic treatment appropriate."
            )
            recommendations = [
                "Testing generally not recommended",
                "Symptomatic treatment appropriate",
                "Consider testing in high-risk settings",
            ]
            next_steps = [
                "Provide symptomatic care",
                "Return if worsening or no improvement in 3-5 days",
            ]
        elif score == 2:
            severity = Severity.MILD
            risk_level = RiskLevel.LOW
            probability = "11-17%"
            summary = f"{score_type} Score {score}: Low-moderate probability of GAS ({probability})"
            detail = (
                "Low-moderate probability of GAS. "
                "Rapid antigen detection test (RADT) recommended. "
                "Treat if RADT positive; consider throat culture backup for children if RADT negative."
            )
            recommendations = [
                "Rapid antigen detection test (RADT) recommended",
                "Treat if RADT positive",
                "For children: backup throat culture if RADT negative",
            ]
            next_steps = [
                "Perform RADT",
                "If positive: treat with penicillin/amoxicillin",
                "If negative in child: send throat culture",
            ]
        elif score == 3:
            severity = Severity.MODERATE
            risk_level = RiskLevel.INTERMEDIATE
            probability = "28-35%"
            summary = f"{score_type} Score {score}: Moderate probability of GAS ({probability})"
            detail = (
                "Moderate probability of GAS pharyngitis. "
                "Rapid strep test strongly recommended. Treat if positive. "
                "For children: if RADT negative, send throat culture before ruling out GAS."
            )
            recommendations = [
                "Rapid strep test strongly recommended",
                "Treat if positive",
                "Children: throat culture if RADT negative",
            ]
            next_steps = [
                "Perform RADT",
                "If positive: Penicillin V or Amoxicillin x10 days",
                "Children with negative RADT: await culture results",
            ]
        else:  # score >= 4
            severity = Severity.MODERATE
            risk_level = RiskLevel.INTERMEDIATE
            probability = "51-53%"
            summary = f"{score_type} Score {score}: High probability of GAS ({probability})"
            detail = (
                "High probability of GAS pharyngitis. "
                "IDSA recommends testing before treatment (to avoid unnecessary antibiotics). "
                "Some guidelines allow empiric treatment in high-prevalence settings. "
                "If treating: Penicillin V or Amoxicillin x10 days."
            )
            recommendations = [
                "Test before treatment (IDSA recommendation)",
                "Some guidelines allow empiric treatment",
                "First-line: Penicillin V or Amoxicillin x10 days",
            ]
            next_steps = [
                "Perform RADT or empiric treatment per local guidelines",
                "If treating: Penicillin V 500mg BID or Amoxicillin 500mg BID x10 days",
                "Penicillin allergic: Cephalexin, Azithromycin, or Clindamycin",
            ]
        
        return Interpretation(
            summary=summary,
            detail=detail,
            severity=severity,
            risk_level=risk_level,
            recommendations=tuple(recommendations),
            next_steps=tuple(next_steps),
        )
