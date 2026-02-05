"""
Charlson Comorbidity Index (CCI) Calculator

Predicts 10-year mortality risk based on the number and severity of comorbid conditions.
This is one of the most widely used comorbidity indices in clinical research.

Original Reference:
    Charlson ME, Pompei P, Ales KL, MacKenzie CR.
    A new method of classifying prognostic comorbidity in longitudinal studies:
    development and validation.
    J Chronic Dis. 1987;40(5):373-383.
    doi:10.1016/0021-9681(87)90171-8. PMID: 3558716.

ICD-10 Coding Reference:
    Quan H, Sundararajan V, Halfon P, et al.
    Coding algorithms for defining comorbidities in ICD-9-CM and ICD-10
    administrative data.
    Med Care. 2005;43(11):1130-1139.
    doi:10.1097/01.mlr.0000182534.19832.83. PMID: 16224307.

Age-Adjusted CCI Reference:
    Charlson M, Szatrowski TP, Peterson J, Gold J.
    Validation of a combined comorbidity index.
    J Clin Epidemiol. 1994;47(11):1245-1251.
    doi:10.1016/0895-4356(94)90129-5. PMID: 7722560.
"""

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, RiskLevel, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import (
    ClinicalContext,
    HighLevelKey,
    LowLevelKey,
    Specialty,
)
from ...value_objects.units import Unit
from ..base import BaseCalculator


class CharlsonComorbidityIndexCalculator(BaseCalculator):
    """
    Charlson Comorbidity Index (CCI)

    A weighted index that predicts mortality risk based on 17 comorbid conditions,
    with optional age adjustment.

    Conditions and Weights:

    1 Point Each:
    - Myocardial infarction (history, not ECG changes only)
    - Congestive heart failure
    - Peripheral vascular disease (includes aortic aneurysm ≥6 cm)
    - Cerebrovascular disease (CVA with mild or no residua, TIA)
    - Dementia
    - Chronic pulmonary disease
    - Connective tissue disease (rheumatologic)
    - Peptic ulcer disease
    - Mild liver disease (without portal hypertension, includes chronic hepatitis)
    - Diabetes without end-organ damage (excludes diet-controlled alone)

    2 Points Each:
    - Hemiplegia or paraplegia
    - Moderate or severe renal disease (creatinine >3 mg/dL, dialysis, transplant, uremic syndrome)
    - Diabetes with end-organ damage (retinopathy, neuropathy, nephropathy)
    - Any malignancy (including leukemia and lymphoma, except if >5 years from diagnosis)

    3 Points:
    - Moderate or severe liver disease (cirrhosis with portal hypertension ± variceal bleeding)

    6 Points Each:
    - Metastatic solid tumor
    - AIDS (not just HIV positive)

    Hierarchy Rules (only the more severe counts):
    - Liver disease: Mild (1) vs Moderate/Severe (3)
    - Diabetes: Without complications (1) vs With complications (2)
    - Cancer: Localized (2) vs Metastatic (6)

    Age Adjustment (optional, for Age-Adjusted CCI):
    - 50-59 years: +1
    - 60-69 years: +2
    - 70-79 years: +3
    - ≥80 years: +4

    Estimated 10-Year Survival:
    - CCI 0: 98%
    - CCI 1: 96%
    - CCI 2: 90%
    - CCI 3: 77%
    - CCI 4: 53%
    - CCI 5: 21%
    - CCI ≥6: 2%
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="charlson_comorbidity_index",
                name="Charlson Comorbidity Index (CCI)",
                purpose="Predict 10-year mortality based on comorbid conditions",
                input_params=[
                    "age_years",
                    "myocardial_infarction",
                    "congestive_heart_failure",
                    "peripheral_vascular_disease",
                    "cerebrovascular_disease",
                    "dementia",
                    "chronic_pulmonary_disease",
                    "connective_tissue_disease",
                    "peptic_ulcer_disease",
                    "mild_liver_disease",
                    "diabetes_uncomplicated",
                    "hemiplegia",
                    "moderate_severe_renal_disease",
                    "diabetes_with_end_organ_damage",
                    "any_malignancy",
                    "moderate_severe_liver_disease",
                    "metastatic_solid_tumor",
                    "aids",
                    "include_age_adjustment",
                ],
                output_type="CCI score with 10-year survival estimate",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.GERIATRICS,
                    Specialty.ONCOLOGY,
                    Specialty.SURGERY,
                    Specialty.CRITICAL_CARE,
                    Specialty.CARDIOLOGY,
                    Specialty.NEPHROLOGY,
                ),
                conditions=(
                    "comorbidity assessment",
                    "mortality prediction",
                    "multimorbidity",
                    "chronic disease burden",
                    "survival estimation",
                    "risk stratification",
                    "prognosis assessment",
                ),
                clinical_contexts=(
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.TREATMENT_DECISION,
                    ClinicalContext.PREOPERATIVE_ASSESSMENT,
                    ClinicalContext.ELIGIBILITY,
                ),
                clinical_questions=(
                    "What is this patient's comorbidity burden?",
                    "What is this patient's expected 10-year survival?",
                    "How do comorbidities affect this patient's prognosis?",
                    "Should comorbidity level influence treatment intensity?",
                    "Is this patient's mortality risk acceptable for surgery?",
                    "How should I risk-adjust outcomes for this population?",
                ),
                icd10_codes=(
                    "Z87.89",  # Personal history of other specified conditions
                    "R54",  # Age-related physical debility
                    "Z96.89",  # Presence of other specified functional implants
                ),
                keywords=(
                    "Charlson",
                    "CCI",
                    "comorbidity index",
                    "comorbidity score",
                    "age-adjusted CCI",
                    "mortality prediction",
                    "survival estimation",
                    "disease burden",
                    "multimorbidity score",
                    "Charlson score",
                    "10-year survival",
                    "risk adjustment",
                ),
            ),
            references=(
                Reference(
                    citation="Charlson ME, Pompei P, Ales KL, MacKenzie CR. "
                    "A new method of classifying prognostic comorbidity in longitudinal "
                    "studies: development and validation. J Chronic Dis. 1987;40(5):373-383.",
                    doi="10.1016/0021-9681(87)90171-8",
                    pmid="3558716",
                    year=1987,
                ),
                Reference(
                    citation="Quan H, Sundararajan V, Halfon P, et al. "
                    "Coding algorithms for defining comorbidities in ICD-9-CM and ICD-10 "
                    "administrative data. Med Care. 2005;43(11):1130-1139.",
                    doi="10.1097/01.mlr.0000182534.19832.83",
                    pmid="16224307",
                    year=2005,
                ),
                Reference(
                    citation="Charlson M, Szatrowski TP, Peterson J, Gold J. "
                    "Validation of a combined comorbidity index. "
                    "J Clin Epidemiol. 1994;47(11):1245-1251.",
                    doi="10.1016/0895-4356(94)90129-5",
                    pmid="7722560",
                    year=1994,
                ),
            ),
            version="1987 (with 1994 age adjustment)",
            validation_status="validated",
        )

    def calculate(
        self,
        # Age for optional adjustment
        age_years: int | None = None,
        # 1-point conditions
        myocardial_infarction: bool = False,
        congestive_heart_failure: bool = False,
        peripheral_vascular_disease: bool = False,
        cerebrovascular_disease: bool = False,
        dementia: bool = False,
        chronic_pulmonary_disease: bool = False,
        connective_tissue_disease: bool = False,
        peptic_ulcer_disease: bool = False,
        # Hierarchical conditions - liver
        mild_liver_disease: bool = False,
        moderate_severe_liver_disease: bool = False,
        # Hierarchical conditions - diabetes
        diabetes_uncomplicated: bool = False,
        diabetes_with_end_organ_damage: bool = False,
        # 2-point conditions
        hemiplegia: bool = False,
        moderate_severe_renal_disease: bool = False,
        any_malignancy: bool = False,
        # 6-point conditions
        metastatic_solid_tumor: bool = False,
        aids: bool = False,
        # Age adjustment option
        include_age_adjustment: bool = True,
    ) -> ScoreResult:
        """
        Calculate Charlson Comorbidity Index (CCI).

        Args:
            age_years: Patient age in years (required if include_age_adjustment=True)

            1-Point Conditions:
            myocardial_infarction: History of definite or probable MI (not ECG changes alone)
            congestive_heart_failure: Exertional or paroxysmal nocturnal dyspnea responding to treatment
            peripheral_vascular_disease: Claudication, bypass, AAA ≥6cm, acute arterial occlusion
            cerebrovascular_disease: CVA with mild/no residua or TIA
            dementia: Chronic cognitive deficit
            chronic_pulmonary_disease: COPD, asthma, emphysema requiring chronic treatment
            connective_tissue_disease: Lupus, polymyositis, mixed CTD, moderate-severe RA, polymyalgia rheumatica
            peptic_ulcer_disease: Requiring treatment

            Hierarchical - Liver Disease (only higher counts):
            mild_liver_disease: Chronic hepatitis, cirrhosis without portal HTN (1 point)
            moderate_severe_liver_disease: Cirrhosis with portal HTN ± variceal bleeding (3 points)

            Hierarchical - Diabetes (only higher counts):
            diabetes_uncomplicated: Requiring insulin or oral agents, not diet alone (1 point)
            diabetes_with_end_organ_damage: Retinopathy, neuropathy, nephropathy (2 points)

            2-Point Conditions:
            hemiplegia: Hemiplegia or paraplegia
            moderate_severe_renal_disease: Cr >3 mg/dL, dialysis, transplant, uremia
            any_malignancy: Including leukemia and lymphoma, except if >5 years from diagnosis

            6-Point Conditions (highest hierarchy for cancer):
            metastatic_solid_tumor: Metastatic solid cancer
            aids: Acquired immunodeficiency syndrome (not just HIV+)

            include_age_adjustment: Whether to include age adjustment (+1 per decade from 50)

        Returns:
            ScoreResult with CCI score, 10-year survival estimate, and interpretation
        """
        score = 0
        components: dict[str, int] = {}
        conditions_present: list[str] = []

        # Validate age if adjustment requested
        if include_age_adjustment and age_years is None:
            raise ValueError("age_years is required when include_age_adjustment=True")

        # 1-point conditions (non-hierarchical)
        if myocardial_infarction:
            score += 1
            components["Myocardial infarction"] = 1
            conditions_present.append("MI")
        if congestive_heart_failure:
            score += 1
            components["Congestive heart failure"] = 1
            conditions_present.append("CHF")
        if peripheral_vascular_disease:
            score += 1
            components["Peripheral vascular disease"] = 1
            conditions_present.append("PVD")
        if cerebrovascular_disease:
            score += 1
            components["Cerebrovascular disease"] = 1
            conditions_present.append("CVA/TIA")
        if dementia:
            score += 1
            components["Dementia"] = 1
            conditions_present.append("Dementia")
        if chronic_pulmonary_disease:
            score += 1
            components["Chronic pulmonary disease"] = 1
            conditions_present.append("COPD")
        if connective_tissue_disease:
            score += 1
            components["Connective tissue disease"] = 1
            conditions_present.append("CTD")
        if peptic_ulcer_disease:
            score += 1
            components["Peptic ulcer disease"] = 1
            conditions_present.append("PUD")

        # Hierarchical: Liver disease (3 > 1)
        if moderate_severe_liver_disease:
            score += 3
            components["Moderate/severe liver disease"] = 3
            conditions_present.append("Severe liver disease")
        elif mild_liver_disease:
            score += 1
            components["Mild liver disease"] = 1
            conditions_present.append("Mild liver disease")

        # Hierarchical: Diabetes (2 > 1)
        if diabetes_with_end_organ_damage:
            score += 2
            components["Diabetes with end-organ damage"] = 2
            conditions_present.append("DM with complications")
        elif diabetes_uncomplicated:
            score += 1
            components["Diabetes uncomplicated"] = 1
            conditions_present.append("DM uncomplicated")

        # 2-point conditions
        if hemiplegia:
            score += 2
            components["Hemiplegia/paraplegia"] = 2
            conditions_present.append("Hemiplegia")
        if moderate_severe_renal_disease:
            score += 2
            components["Moderate/severe renal disease"] = 2
            conditions_present.append("CKD")

        # Hierarchical: Cancer (6 > 2)
        if metastatic_solid_tumor:
            score += 6
            components["Metastatic solid tumor"] = 6
            conditions_present.append("Metastatic cancer")
        elif any_malignancy:
            score += 2
            components["Any malignancy (non-metastatic)"] = 2
            conditions_present.append("Malignancy")

        # 6-point conditions
        if aids:
            score += 6
            components["AIDS"] = 6
            conditions_present.append("AIDS")

        # Calculate base CCI (without age)
        base_cci = score

        # Age adjustment (if requested)
        age_points = 0
        if include_age_adjustment and age_years is not None:
            if age_years >= 80:
                age_points = 4
            elif age_years >= 70:
                age_points = 3
            elif age_years >= 60:
                age_points = 2
            elif age_years >= 50:
                age_points = 1

            if age_points > 0:
                score += age_points
                components[f"Age adjustment ({age_years} years)"] = age_points

        # Generate interpretation
        interpretation = self._interpret_score(
            base_cci, score, age_points, len(conditions_present), conditions_present
        )

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
        base_cci: int,
        total_score: int,
        age_points: int,
        num_conditions: int,
        conditions: list[str],
    ) -> Interpretation:
        """Generate interpretation based on CCI score."""

        # 10-year survival estimates (from Charlson 1987)
        survival_map = {
            0: (98, "98%"),
            1: (96, "96%"),
            2: (90, "90%"),
            3: (77, "77%"),
            4: (53, "53%"),
            5: (21, "21%"),
        }

        if total_score <= 5:
            survival_pct, survival_str = survival_map[total_score]
        else:
            survival_pct = 2
            survival_str = "≤2%"

        # Determine severity and risk level
        if total_score == 0:
            severity = Severity.NORMAL
            risk_level = RiskLevel.VERY_LOW
            category = "No comorbidity"
        elif total_score <= 2:
            severity = Severity.MILD
            risk_level = RiskLevel.LOW
            category = "Mild comorbidity"
        elif total_score <= 4:
            severity = Severity.MODERATE
            risk_level = RiskLevel.INTERMEDIATE
            category = "Moderate comorbidity"
        elif total_score <= 6:
            severity = Severity.SEVERE
            risk_level = RiskLevel.HIGH
            category = "Severe comorbidity"
        else:
            severity = Severity.CRITICAL
            risk_level = RiskLevel.VERY_HIGH
            category = "Very severe comorbidity"

        # Summary
        if age_points > 0:
            summary = f"Age-Adjusted CCI = {total_score} (Base CCI = {base_cci}): {category}"
        else:
            summary = f"CCI = {total_score}: {category}"

        # Detail
        conditions_str = ", ".join(conditions) if conditions else "None"
        detail = (
            f"Charlson Comorbidity Index of {total_score} indicates {category.lower()} "
            f"with estimated 10-year survival of {survival_str}. "
            f"Comorbid conditions ({num_conditions}): {conditions_str}."
        )

        # Recommendations based on score
        recommendations: list[str] = []
        if total_score == 0:
            recommendations = [
                "Low comorbidity burden - standard treatment approaches appropriate",
                "Prognosis primarily determined by primary disease",
            ]
        elif total_score <= 2:
            recommendations = [
                "Mild comorbidity - most standard treatments appropriate",
                "Consider routine monitoring of comorbid conditions",
                "Prognosis generally favorable with appropriate management",
            ]
        elif total_score <= 4:
            recommendations = [
                "Moderate comorbidity - consider treatment modifications",
                "Increased monitoring of comorbid conditions recommended",
                "May benefit from multidisciplinary care coordination",
                "Consider goals of care discussion",
            ]
        elif total_score <= 6:
            recommendations = [
                "Severe comorbidity - significant impact on prognosis",
                "Recommend multidisciplinary team involvement",
                "Consider less intensive treatment options if appropriate",
                "Goals of care discussion recommended",
                "Enhanced supportive care measures",
            ]
        else:
            recommendations = [
                "Very severe comorbidity - critically impacts prognosis",
                "Recommend palliative care consultation",
                "Focus on quality of life and symptom management",
                "Detailed goals of care discussion essential",
                "Consider hospice referral if appropriate",
            ]

        next_steps = [
            f"10-year survival estimate: {survival_str}",
            "Document CCI in medical record for risk stratification",
            "Update comorbidity assessment annually or with significant clinical change",
        ]

        warnings: tuple[str, ...] = ()
        if total_score >= 5:
            warnings = (
                "High comorbidity burden significantly affects mortality risk",
                "Consider this score when making treatment decisions",
            )
        if survival_pct <= 21:
            warnings = warnings + (
                f"Estimated 10-year survival is {survival_str} - ensure goals of care are addressed",
            )

        return Interpretation(
            summary=summary,
            severity=severity,
            detail=detail,
            stage=f"CCI = {total_score}" if age_points == 0 else f"Age-Adjusted CCI = {total_score}",
            stage_description=category,
            risk_level=risk_level,
            recommendations=tuple(recommendations),
            next_steps=tuple(next_steps),
            warnings=warnings,
        )
