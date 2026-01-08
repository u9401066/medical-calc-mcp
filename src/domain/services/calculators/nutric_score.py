"""
NUTRIC Score (Nutrition Risk in Critically Ill)

The NUTRIC Score identifies ICU patients who will benefit from aggressive
nutritional therapy. It combines traditional nutrition risk factors with
markers of acute illness severity.

Reference (Original):
    Heyland DK, Dhaliwal R, Jiang X, Day AG. Identifying critically ill
    patients who benefit the most from nutrition therapy: the development
    and initial validation of a novel risk assessment tool.
    Crit Care. 2011;15(6):R268.
    DOI: 10.1186/cc10546
    PMID: 22085763

Reference (Modified NUTRIC without IL-6):
    Rahman A, Hasan RM, Agarwala R, et al. Identifying critically-ill
    patients who will benefit most from nutritional therapy: Further
    validation of the "modified NUTRIC" nutritional risk assessment tool.
    Clin Nutr. 2016;35(1):158-162.
    PMID: 25698099
"""

from typing import Optional

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class NUTRICScoreCalculator(BaseCalculator):
    """
    NUTRIC Score (Nutrition Risk in Critically Ill) Calculator

    Components (Modified NUTRIC without IL-6):
    - Age
    - APACHE II
    - SOFA
    - Number of comorbidities
    - Days from hospital to ICU admission
    - Mechanical ventilation

    Score interpretation:
    - 0-4 (or 0-5 with IL-6): Low nutritional risk
    - 5-9 (or 6-10 with IL-6): High nutritional risk - benefit from nutrition
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="nutric_score",
                name="NUTRIC Score (Nutrition Risk in Critically Ill)",
                purpose="Identify ICU patients who benefit most from nutritional therapy",
                input_params=["age", "apache_ii", "sofa", "comorbidities", "days_hospital_to_icu"],
                output_type="Score (0-9) with nutrition risk classification",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.CRITICAL_CARE,
                    Specialty.ANESTHESIOLOGY,
                ),
                conditions=(
                    "Critical Illness",
                    "ICU Admission",
                    "Malnutrition",
                    "Nutritional Risk",
                ),
                clinical_contexts=(
                    ClinicalContext.ICU_MANAGEMENT,
                    ClinicalContext.SCREENING,
                    ClinicalContext.TREATMENT_DECISION,
                ),
                clinical_questions=(
                    "Will this ICU patient benefit from aggressive nutrition?",
                    "What is the nutritional risk in this critically ill patient?",
                    "Should I prioritize nutrition in this ICU patient?",
                ),
                icd10_codes=("E44", "E46", "R63.4"),
                keywords=(
                    "NUTRIC",
                    "nutrition risk",
                    "ICU nutrition",
                    "critical care",
                    "malnutrition",
                    "nutritional therapy",
                    "enteral nutrition",
                ),
            ),
            references=(
                Reference(
                    citation="Heyland DK, Dhaliwal R, Jiang X, Day AG. Identifying critically "
                    "ill patients who benefit the most from nutrition therapy. "
                    "Crit Care. 2011;15(6):R268.",
                    doi="10.1186/cc10546",
                    pmid="22085763",
                    year=2011,
                ),
                Reference(
                    citation="Rahman A, Hasan RM, Agarwala R, et al. Further validation of the "
                    '"modified NUTRIC" nutritional risk assessment tool. '
                    "Clin Nutr. 2016;35(1):158-162.",
                    pmid="25698099",
                    year=2016,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        age: int,
        apache_ii: int,
        sofa: int,
        comorbidities: int,
        days_hospital_to_icu: int,
        il6: Optional[float] = None,
    ) -> ScoreResult:
        """
        Calculate NUTRIC Score.

        Args:
            age: Patient age in years
            apache_ii: APACHE II score (0-71)
            sofa: SOFA score on ICU admission (0-24)
            comorbidities: Number of comorbidities (0-2+)
            days_hospital_to_icu: Days from hospital admission to ICU admission
            il6: IL-6 level (pg/mL), optional - original NUTRIC included this

        Returns:
            ScoreResult with NUTRIC score and interpretation
        """
        # Validate inputs
        if age < 0:
            raise ValueError("Age cannot be negative")
        if apache_ii < 0 or apache_ii > 71:
            raise ValueError("APACHE II must be between 0 and 71")
        if sofa < 0 or sofa > 24:
            raise ValueError("SOFA must be between 0 and 24")
        if comorbidities < 0:
            raise ValueError("Comorbidities cannot be negative")
        if days_hospital_to_icu < 0:
            raise ValueError("Days from hospital to ICU cannot be negative")

        # Calculate component scores
        score = 0
        components: dict = {}

        # Age component
        if age < 50:
            age_score = 0
        elif age < 75:
            age_score = 1
        else:
            age_score = 2
        score += age_score
        components["age"] = {"value": age, "score": age_score}

        # APACHE II component
        if apache_ii < 15:
            apache_score = 0
        elif apache_ii < 20:
            apache_score = 1
        elif apache_ii < 28:
            apache_score = 2
        else:
            apache_score = 3
        score += apache_score
        components["apache_ii"] = {"value": apache_ii, "score": apache_score}

        # SOFA component
        if sofa < 6:
            sofa_score = 0
        elif sofa < 10:
            sofa_score = 1
        else:
            sofa_score = 2
        score += sofa_score
        components["sofa"] = {"value": sofa, "score": sofa_score}

        # Comorbidities component
        if comorbidities <= 1:
            comorbid_score = 0
        else:
            comorbid_score = 1
        score += comorbid_score
        components["comorbidities"] = {"value": comorbidities, "score": comorbid_score}

        # Days from hospital to ICU component
        if days_hospital_to_icu < 1:
            days_score = 0
        else:
            days_score = 1
        score += days_score
        components["days_hospital_to_icu"] = {"value": days_hospital_to_icu, "score": days_score}

        # IL-6 component (if available - original NUTRIC)
        use_il6 = il6 is not None
        max_score = 10 if use_il6 else 9

        if use_il6:
            if il6 < 400:
                il6_score = 0
            else:
                il6_score = 1
            score += il6_score
            components["il6"] = {"value": il6, "score": il6_score}
            high_risk_threshold = 6
        else:
            high_risk_threshold = 5

        # Determine risk category
        high_risk = score >= high_risk_threshold
        category = "High Nutritional Risk" if high_risk else "Low Nutritional Risk"

        # Get interpretation
        interpretation = self._get_interpretation(score, high_risk, high_risk_threshold, max_score, use_il6)

        return ScoreResult(
            value=score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "age": age,
                "apache_ii": apache_ii,
                "sofa": sofa,
                "comorbidities": comorbidities,
                "days_hospital_to_icu": days_hospital_to_icu,
                "il6": il6,
            },
            calculation_details={
                "version": "NUTRIC with IL-6" if use_il6 else "Modified NUTRIC (without IL-6)",
                "components": components,
                "total_score": score,
                "max_score": max_score,
                "high_risk_threshold": high_risk_threshold,
                "high_risk": high_risk,
                "category": category,
            },
            formula_used="NUTRIC = Age + APACHE II + SOFA + Comorbidities + Days to ICU" + (" + IL-6" if use_il6 else ""),
        )

    def _get_interpretation(self, score: int, high_risk: bool, threshold: int, max_score: int, with_il6: bool) -> Interpretation:
        """Get interpretation based on NUTRIC score"""

        version = "NUTRIC with IL-6" if with_il6 else "Modified NUTRIC"

        if high_risk:
            return Interpretation(
                summary=f"{version} {score}/{max_score}: High Nutritional Risk",
                detail=f"Score ≥{threshold} indicates high nutritional risk. "
                f"These patients are most likely to benefit from aggressive nutritional therapy. "
                f"Strong association between malnutrition and adverse outcomes.",
                severity=Severity.MODERATE,
                stage="High Risk",
                stage_description=f"Score ≥{threshold}: High nutritional risk",
                recommendations=(
                    "Prioritize nutritional therapy in this patient",
                    "Early enteral nutrition (within 24-48h of ICU admission)",
                    "Target protein delivery: 1.2-2.0 g/kg/day",
                    "Target energy delivery based on indirect calorimetry or 25-30 kcal/kg/day",
                    "Consider supplemental parenteral nutrition if EN targets not met by day 3-7",
                    "Daily monitoring of nutrition delivery",
                    "Involve dietitian/nutrition team",
                ),
                warnings=(
                    "High mortality risk in this population",
                    "Inadequate nutrition associated with worse outcomes",
                    "Monitor for refeeding syndrome",
                ),
                next_steps=(
                    "Initiate early enteral nutrition",
                    "Calculate protein and calorie requirements",
                    "Monitor tolerance and adjust",
                    "Daily reassessment of nutrition delivery",
                ),
            )
        else:
            return Interpretation(
                summary=f"{version} {score}/{max_score}: Low Nutritional Risk",
                detail=f"Score <{threshold} indicates lower nutritional risk. "
                f"These patients may not benefit as much from aggressive nutritional therapy. "
                f"Standard nutrition support appropriate.",
                severity=Severity.MILD,
                stage="Low Risk",
                stage_description=f"Score <{threshold}: Low nutritional risk",
                recommendations=(
                    "Standard nutritional support approach",
                    "Enteral nutrition when GI tract functional",
                    "Less benefit from aggressive supplemental parenteral nutrition",
                    "Focus on other aspects of ICU care",
                ),
                next_steps=(
                    "Standard enteral nutrition when appropriate",
                    "Reassess NUTRIC if clinical condition changes",
                ),
            )
