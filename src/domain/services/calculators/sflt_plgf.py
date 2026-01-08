"""
sFlt-1/PlGF Ratio (Preeclampsia Biomarker)

The sFlt-1/PlGF ratio is a validated biomarker for ruling in/out
preeclampsia in women with suspected disease.

Reference (PROGNOSIS Study):
    Zeisler H, Llurba E, Chantraine F, et al. Predictive Value of the
    sFlt-1:PlGF Ratio in Women with Suspected Preeclampsia.
    N Engl J Med. 2016;374(1):13-22.
    PMID: 26735990

Reference (NICE Guidelines):
    National Institute for Health and Care Excellence. PlGF-based testing
    to help diagnose suspected pre-eclampsia. DG49. 2022.
    https://www.nice.org.uk/guidance/dg49
"""

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


class SFltPlGFRatioCalculator(BaseCalculator):
    """
    sFlt-1/PlGF Ratio Calculator

    Biomarker ratio for preeclampsia prediction and diagnosis.
    Key cutoffs:
    - Ratio ≤38: Rules out preeclampsia for 1 week (high NPV)
    - Ratio >38: Requires clinical correlation
    - Ratio >85 (early) or >110 (late): High risk of preeclampsia
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="sflt_plgf_ratio",
                name="sFlt-1/PlGF Ratio (Preeclampsia Biomarker)",
                purpose="Predict and diagnose preeclampsia",
                input_params=[
                    "sflt1",
                    "plgf",
                    "gestational_weeks",
                ],
                output_type="Ratio with preeclampsia risk assessment",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.GYNECOLOGY,
                    Specialty.INTERNAL_MEDICINE,
                ),
                conditions=(
                    "Preeclampsia",
                    "Hypertensive Disorders of Pregnancy",
                    "HELLP Syndrome",
                    "Gestational Hypertension",
                    "Eclampsia",
                ),
                clinical_contexts=(
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.SCREENING,
                ),
                clinical_questions=(
                    "Does this patient have preeclampsia?",
                    "What is the sFlt-1/PlGF ratio?",
                    "Rule out preeclampsia",
                    "Predict preeclampsia risk",
                ),
                keywords=(
                    "sFlt-1",
                    "PlGF",
                    "preeclampsia",
                    "angiogenic factors",
                    "PROGNOSIS",
                    "hypertensive pregnancy",
                ),
            ),
            references=(
                Reference(
                    citation="Zeisler H, Llurba E, Chantraine F, et al. Predictive Value of the sFlt-1:PlGF Ratio in Women with Suspected Preeclampsia. N Engl J Med. 2016;374(1):13-22.",
                    pmid="26735990",
                    doi="10.1056/NEJMoa1414838",
                    year=2016,
                ),
                Reference(
                    citation="NICE. PlGF-based testing to help diagnose suspected pre-eclampsia. DG49. 2022.",
                    url="https://www.nice.org.uk/guidance/dg49",
                    year=2022,
                ),
            ),
        )

    def calculate(self, **params) -> ScoreResult:
        """
        Calculate sFlt-1/PlGF ratio.

        Args:
            sflt1: Soluble fms-like tyrosine kinase-1 (pg/mL)
            plgf: Placental growth factor (pg/mL)
            gestational_weeks: Gestational age in weeks

        Returns:
            ScoreResult with ratio and preeclampsia risk
        """
        sflt1 = float(params.get("sflt1", 0))
        plgf = float(params.get("plgf", 0))
        ga_weeks = float(params.get("gestational_weeks", 0))

        # Validation
        if sflt1 <= 0:
            raise ValueError("sflt1 must be positive")
        if plgf <= 0:
            raise ValueError("plgf must be positive (use lowest detectable if very low)")
        if not 20 <= ga_weeks <= 42:
            raise ValueError("gestational_weeks must be 20-42")

        # Calculate ratio
        ratio = sflt1 / plgf

        # Determine gestational period (affects cutoffs)
        is_early = ga_weeks < 34  # Early-onset preeclampsia threshold

        # Risk categorization (PROGNOSIS study cutoffs)
        # Rule-out: ≤38 (NPV >99% for 1 week)
        # Intermediate: 38-85 (early) or 38-110 (late)
        # Rule-in: >85 (early) or >110 (late)

        if ratio <= 38:
            severity = Severity.NORMAL
            risk_text = "Preeclampsia ruled out for 1 week"
            stage = "Low risk"
            preeclampsia_likely = False
        elif is_early:
            if ratio <= 85:
                severity = Severity.MODERATE
                risk_text = "Intermediate risk (early gestation)"
                stage = "Intermediate"
                preeclampsia_likely = None  # Uncertain
            else:
                severity = Severity.SEVERE
                risk_text = "High risk - preeclampsia likely (early-onset)"
                stage = "High risk"
                preeclampsia_likely = True
        else:  # Late gestation
            if ratio <= 110:
                severity = Severity.MODERATE
                risk_text = "Intermediate risk (late gestation)"
                stage = "Intermediate"
                preeclampsia_likely = None
            else:
                severity = Severity.SEVERE
                risk_text = "High risk - preeclampsia likely (late-onset)"
                stage = "High risk"
                preeclampsia_likely = True

        # Very high ratios
        if ratio > 655:
            severity = Severity.CRITICAL
            risk_text = "Very high risk - imminent adverse outcome"
            stage = "Very high risk"

        # Recommendations (per NICE DG49)
        recommendations = []
        if ratio <= 38:
            recommendations.append("Preeclampsia unlikely in next week")
            recommendations.append("Repeat testing if symptoms recur or worsen")
            recommendations.append("Standard antenatal care appropriate")
        elif stage == "Intermediate":
            recommendations.append("Cannot exclude preeclampsia - clinical correlation needed")
            recommendations.append("Consider repeat testing in 1-2 weeks")
            recommendations.append("Increased surveillance recommended")
            recommendations.append("Assess for clinical preeclampsia criteria")
        else:
            recommendations.append("High probability of preeclampsia")
            recommendations.append("Full preeclampsia workup (BP, proteinuria, labs)")
            recommendations.append("Consider admission for monitoring")
            recommendations.append("Corticosteroids if <34 weeks and delivery likely")
            if ratio > 655:
                recommendations.append("Very high risk of adverse outcome within days")

        # Interpretation of individual markers
        marker_interpretation = []
        if sflt1 > 5500:
            marker_interpretation.append("sFlt-1 markedly elevated")
        if plgf < 100:
            marker_interpretation.append("PlGF significantly low")
        elif plgf < 12:
            marker_interpretation.append("PlGF very low - concerning")

        warnings = []
        if ratio > 85 and is_early:
            warnings.append("Early-onset pattern - higher maternal/fetal morbidity risk")
        if ratio > 655:
            warnings.append("Very high ratio - consider expedited delivery")
        if ga_weeks < 32 and ratio > 85:
            warnings.append("Very preterm with high ratio - involves complex decision-making")

        next_steps = [
            "BP monitoring (serial measurements)",
            "Urinalysis/spot protein:creatinine ratio",
            "CBC, LFTs, creatinine (to assess for HELLP/end-organ damage)",
            "Fetal assessment (CTG, growth scan, dopplers)",
        ]

        period_text = "early (<34w)" if is_early else "late (≥34w)"

        return ScoreResult(
            value=round(ratio, 1),
            unit=Unit.RATIO,
            interpretation=Interpretation(
                summary=f"sFlt-1/PlGF Ratio = {ratio:.1f}: {risk_text}",
                detail=(
                    f"sFlt-1/PlGF ratio of {ratio:.1f} at {ga_weeks:.0f} weeks ({period_text}) indicates {risk_text.lower()}. "
                    f"sFlt-1: {sflt1:.0f} pg/mL, PlGF: {plgf:.1f} pg/mL. "
                    f"{'Ratio ≤38 rules out preeclampsia for 1 week with >99% NPV.' if ratio <= 38 else ''} "
                    f"{' '.join(marker_interpretation)}"
                ),
                severity=severity,
                stage=stage,
                stage_description=risk_text,
                recommendations=recommendations,
                warnings=warnings,
                next_steps=next_steps,
            ),
            references=self.metadata.references,
            tool_id=self.metadata.low_level.tool_id,
            tool_name=self.metadata.low_level.name,
            raw_inputs=params,
            calculation_details={
                "ratio": round(ratio, 2),
                "sflt1_pg_ml": sflt1,
                "plgf_pg_ml": plgf,
                "gestational_weeks": ga_weeks,
                "is_early_onset_period": is_early,
                "risk_category": stage,
                "preeclampsia_likely": preeclampsia_likely,
                "cutoff_used": 85 if is_early else 110,
            },
        )
