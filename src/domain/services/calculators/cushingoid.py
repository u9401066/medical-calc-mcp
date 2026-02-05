"""
Cushingoid Score (Clinical Features Score for Cushing's Syndrome)

A clinical scoring system to assess the likelihood of hypercortisolism
based on characteristic clinical features.

Reference:
    Nieman LK, Biller BM, Findling JW, et al. The diagnosis of Cushing's
    syndrome: an Endocrine Society Clinical Practice Guideline.
    J Clin Endocrinol Metab. 2008;93(5):1526-1540.
    PMID: 18334580

Reference (Clinical Features):
    Ross EJ, Linch DC. Cushing's syndrome - killing disease: discriminatory
    value of signs and symptoms aiding early diagnosis. Lancet.
    1982;2(8299):646-649.
    PMID: 6125785
"""

from typing import Any

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import (
    ClinicalContext,
    HighLevelKey,
    LowLevelKey,
    Specialty,
)
from ...value_objects.units import Unit
from ..base import BaseCalculator


class CushingoidScoreCalculator(BaseCalculator):
    """
    Cushingoid Score Calculator

    Assesses clinical features suggestive of Cushing's syndrome
    to guide diagnostic workup.
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="cushingoid_score",
                name="Cushingoid Score (Clinical Features of Cushing's Syndrome)",
                purpose="Assess clinical likelihood of Cushing's syndrome",
                input_params=[
                    "facial_plethora",
                    "proximal_myopathy",
                    "striae_rubrae",
                    "easy_bruising",
                    "supraclavicular_fat",
                    "dorsocervical_fat",
                    "central_obesity",
                    "moon_face",
                    "hirsutism",
                    "acne",
                    "menstrual_irregularity",
                    "hypertension",
                    "hyperglycemia",
                    "osteoporosis",
                    "psychiatric_symptoms",
                ],
                output_type="Clinical feature count with likelihood assessment",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.ENDOCRINOLOGY,
                    Specialty.INTERNAL_MEDICINE,
                ),
                conditions=(
                    "Cushing's Syndrome",
                    "Hypercortisolism",
                    "Cushing's Disease",
                    "Adrenal Adenoma",
                    "Ectopic ACTH",
                ),
                clinical_contexts=(
                    ClinicalContext.SCREENING,
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.DIFFERENTIAL_DIAGNOSIS,
                ),
                clinical_questions=(
                    "Does this patient have Cushing's syndrome?",
                    "Should this patient be tested for hypercortisolism?",
                    "Assess Cushingoid features",
                    "Clinical score for Cushing's",
                ),
                keywords=(
                    "Cushingoid",
                    "Cushing's syndrome",
                    "hypercortisolism",
                    "moon face",
                    "buffalo hump",
                    "striae",
                ),
            ),
            references=(
                Reference(
                    citation="Nieman LK, Biller BM, Findling JW, et al. The diagnosis of Cushing's syndrome: an Endocrine Society Clinical Practice Guideline. J Clin Endocrinol Metab. 2008;93(5):1526-1540.",
                    pmid="18334580",
                    doi="10.1210/jc.2008-0125",
                    year=2008,
                ),
                Reference(
                    citation="Ross EJ, Linch DC. Cushing's syndrome - killing disease: discriminatory value of signs and symptoms aiding early diagnosis. Lancet. 1982;2(8299):646-649.",
                    pmid="6125785",
                    doi="10.1016/S0140-6736(82)92749-0",
                    year=1982,
                ),
            ),
        )

    def calculate(self, **params: Any) -> ScoreResult:
        """
        Calculate Cushingoid score.

        Args:
            Highly discriminatory features (strong indicators):
                facial_plethora: Facial plethora/redness
                proximal_myopathy: Proximal muscle weakness
                striae_rubrae: Wide (>1cm) violaceous striae
                easy_bruising: Easy bruising without trauma

            Moderately discriminatory features:
                supraclavicular_fat: Supraclavicular fat pads
                dorsocervical_fat: Dorsocervical fat pad (buffalo hump)
                central_obesity: Central/truncal obesity
                moon_face: Moon facies

            Less specific features:
                hirsutism: Hirsutism (females)
                acne: Acne
                menstrual_irregularity: Menstrual irregularity (females)
                hypertension: Hypertension
                hyperglycemia: Hyperglycemia/diabetes
                osteoporosis: Osteoporosis (unexplained)
                psychiatric_symptoms: Depression, mood changes, cognitive impairment

        Returns:
            ScoreResult with feature count and clinical recommendation
        """
        # Highly discriminatory features (weight 2)
        high_features = {
            "facial_plethora": bool(params.get("facial_plethora", False)),
            "proximal_myopathy": bool(params.get("proximal_myopathy", False)),
            "striae_rubrae": bool(params.get("striae_rubrae", False)),
            "easy_bruising": bool(params.get("easy_bruising", False)),
        }

        # Moderately discriminatory features (weight 1.5)
        moderate_features = {
            "supraclavicular_fat": bool(params.get("supraclavicular_fat", False)),
            "dorsocervical_fat": bool(params.get("dorsocervical_fat", False)),
            "central_obesity": bool(params.get("central_obesity", False)),
            "moon_face": bool(params.get("moon_face", False)),
        }

        # Less specific features (weight 1)
        nonspecific_features = {
            "hirsutism": bool(params.get("hirsutism", False)),
            "acne": bool(params.get("acne", False)),
            "menstrual_irregularity": bool(params.get("menstrual_irregularity", False)),
            "hypertension": bool(params.get("hypertension", False)),
            "hyperglycemia": bool(params.get("hyperglycemia", False)),
            "osteoporosis": bool(params.get("osteoporosis", False)),
            "psychiatric_symptoms": bool(params.get("psychiatric_symptoms", False)),
        }

        # Count features
        high_count = sum(high_features.values())
        moderate_count = sum(moderate_features.values())
        nonspecific_count = sum(nonspecific_features.values())
        total_features = high_count + moderate_count + nonspecific_count

        # Calculate weighted score
        weighted_score = (high_count * 2) + (moderate_count * 1.5) + (nonspecific_count * 1)

        # Identify present features
        present_high = [k for k, v in high_features.items() if v]
        present_moderate = [k for k, v in moderate_features.items() if v]
        present_nonspecific = [k for k, v in nonspecific_features.items() if v]

        # Determine likelihood
        if high_count >= 2 or (high_count >= 1 and weighted_score >= 5):
            severity = Severity.SEVERE
            likelihood = "High likelihood of Cushing's syndrome"
            stage = "High"
            recommend_testing = True
        elif weighted_score >= 4 or (high_count >= 1 and moderate_count >= 2):
            severity = Severity.MODERATE
            likelihood = "Moderate likelihood - testing recommended"
            stage = "Moderate"
            recommend_testing = True
        elif weighted_score >= 2:
            severity = Severity.MILD
            likelihood = "Low-moderate likelihood - consider testing"
            stage = "Low-moderate"
            recommend_testing = True
        else:
            severity = Severity.NORMAL
            likelihood = "Low likelihood of Cushing's syndrome"
            stage = "Low"
            recommend_testing = False

        # Recommendations (per Endocrine Society guidelines)
        recommendations = []
        if recommend_testing:
            recommendations.append("Biochemical screening recommended")
            recommendations.append("First-line tests: 24h urine free cortisol (UFC), late-night salivary cortisol, or 1mg DST")
            recommendations.append("At least 2 abnormal tests to confirm diagnosis")
        else:
            recommendations.append("Clinical features alone do not warrant screening")
            recommendations.append("Monitor if symptoms progress or additional features develop")

        if high_count >= 1:
            recommendations.append("Highly discriminatory features present - pursue workup")

        # Endocrine Society guideline indications for testing
        es_indications = []
        if bool(params.get("osteoporosis", False)):
            es_indications.append("Unexplained osteoporosis")
        if bool(params.get("hypertension", False)):
            es_indications.append("Resistant hypertension")
        if bool(params.get("hyperglycemia", False)):
            es_indications.append("Type 2 diabetes with poor control")
        if bool(params.get("adrenal_incidentaloma", False)):
            es_indications.append("Adrenal incidentaloma")

        if es_indications:
            recommendations.append(f"Endocrine Society guideline indication(s): {', '.join(es_indications)}")

        warnings = []
        if high_count >= 3:
            warnings.append("Multiple highly discriminatory features - high probability of Cushing's")
        if bool(params.get("proximal_myopathy", False)) and bool(params.get("striae_rubrae", False)):
            warnings.append("Classic combination - strongly suggestive of hypercortisolism")

        next_steps = [
            "24-hour urine free cortisol (2-3 collections)" if recommend_testing else "Clinical monitoring",
            "Late-night salivary cortisol (2 samples)" if recommend_testing else "Reassess if new features develop",
            "Overnight 1mg dexamethasone suppression test" if recommend_testing else "No further testing at this time",
        ]

        return ScoreResult(
            value=round(weighted_score, 1),
            unit=Unit.SCORE,
            interpretation=Interpretation(
                summary=f"Cushingoid Score = {round(weighted_score, 1)}: {likelihood}",
                detail=(
                    f"Clinical feature assessment shows weighted score of {round(weighted_score, 1)}. "
                    f"Highly discriminatory features: {high_count}/4 ({', '.join(present_high) if present_high else 'None'}). "
                    f"Moderately discriminatory: {moderate_count}/4 ({', '.join(present_moderate) if present_moderate else 'None'}). "
                    f"Less specific: {nonspecific_count}/7 ({', '.join(present_nonspecific) if present_nonspecific else 'None'}). "
                    f"Total {total_features}/15 features present."
                ),
                severity=severity,
                stage=stage,
                stage_description=likelihood,
                recommendations=tuple(recommendations),
                warnings=tuple(warnings),
                next_steps=tuple(next_steps),
            ),
            references=list(self.metadata.references),
            tool_id=self.metadata.low_level.tool_id,
            tool_name=self.metadata.low_level.name,
            raw_inputs=params,
            calculation_details={
                "weighted_score": round(weighted_score, 1),
                "total_features": total_features,
                "high_discriminatory_count": high_count,
                "moderate_discriminatory_count": moderate_count,
                "nonspecific_count": nonspecific_count,
                "present_high_features": present_high,
                "present_moderate_features": present_moderate,
                "present_nonspecific_features": present_nonspecific,
                "recommend_testing": recommend_testing,
                "likelihood_category": stage,
            },
        )
