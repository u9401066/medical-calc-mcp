"""
Lille Model Calculator

評估酒精性肝炎患者對類固醇治療7天後的反應。
用於決定是否繼續或停止類固醇治療。

References:
- Louvet A, et al. Hepatology. 2007;45(6):1348-1354. PMID: 17518367
"""

import math

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, RiskLevel, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class LilleModelCalculator(BaseCalculator):
    """
    Lille Model Calculator

    計算酒精性肝炎患者對類固醇治療7天後的反應。

    輸出:
    - Lille score 0-1
    - Lille < 0.45: 響應者 (繼續類固醇)
    - Lille ≥ 0.45: 非響應者 (停止類固醇)
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="lille_model",
                name="Lille Model (Alcoholic Hepatitis Steroid Response)",
                purpose="Assess response to corticosteroid therapy in alcoholic hepatitis",
                input_params=["age", "albumin", "bilirubin_day0", "bilirubin_day7", "creatinine", "pt"],
                output_type="Lille score (0-1)",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.HEPATOLOGY,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.CRITICAL_CARE,
                    Specialty.GASTROENTEROLOGY,
                ),
                conditions=("Alcoholic Hepatitis", "Severe Alcoholic Hepatitis", "Alcohol-Associated Hepatitis", "Steroid Treatment Response"),
                clinical_contexts=(
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.MONITORING,
                    ClinicalContext.SEVERITY_ASSESSMENT,
                ),
                clinical_questions=(
                    "Should I continue or stop steroids for this patient?",
                    "Is this patient responding to corticosteroid therapy?",
                    "What is the prognosis at day 7 of treatment?",
                    "Is this patient a steroid responder or non-responder?",
                ),
                icd10_codes=("K70.10", "K70.11", "K70.40", "K70.41"),
                keywords=(
                    "Lille",
                    "alcoholic hepatitis",
                    "steroid response",
                    "prednisolone",
                    "corticosteroid",
                    "treatment response",
                    "non-responder",
                    "hepatology",
                ),
            ),
            references=(
                Reference(
                    citation="Louvet A, Naveau S, Abdelnour M, et al. The Lille model: a new tool for therapeutic strategy in patients with severe alcoholic hepatitis treated with steroids. Hepatology. 2007;45(6):1348-1354.",
                    pmid="17518367",
                    doi="10.1002/hep.21607",
                    year=2007,
                ),
                Reference(
                    citation="Thursz MR, Richardson P, Allison M, et al. Prednisolone or pentoxifylline for alcoholic hepatitis (STOPAH trial). N Engl J Med. 2015;372(17):1619-1628.",
                    pmid="25901427",
                    doi="10.1056/NEJMoa1412278",
                    year=2015,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        age: int,
        albumin: float,
        bilirubin_day0: float,
        bilirubin_day7: float,
        creatinine: float,
        pt: float,
        albumin_unit: str = "g/dL",
        bilirubin_unit: str = "mg/dL",
        creatinine_unit: str = "mg/dL",
    ) -> ScoreResult:
        """
        Calculate Lille Model score.

        Args:
            age: Patient age in years
            albumin: Serum albumin (g/dL or g/L)
            bilirubin_day0: Total bilirubin at day 0 (before steroids)
            bilirubin_day7: Total bilirubin at day 7 (after steroids)
            creatinine: Serum creatinine (mg/dL or μmol/L)
            pt: Prothrombin time in seconds OR INR (if <10 treated as INR)
            albumin_unit: "g/dL" (default) or "g/L"
            bilirubin_unit: "mg/dL" (default) or "umol/L"
            creatinine_unit: "mg/dL" (default) or "umol/L"

        Returns:
            ScoreResult with Lille score and interpretation
        """
        # Validate inputs
        if age <= 0:
            raise ValueError("Age must be positive")
        if albumin <= 0:
            raise ValueError("Albumin must be positive")
        if bilirubin_day0 <= 0:
            raise ValueError("Bilirubin day 0 must be positive")
        if bilirubin_day7 <= 0:
            raise ValueError("Bilirubin day 7 must be positive")
        if creatinine <= 0:
            raise ValueError("Creatinine must be positive")
        if pt <= 0:
            raise ValueError("PT must be positive")

        # Unit conversions
        # Albumin: if g/L, convert to g/dL
        if albumin_unit.lower() == "g/l":
            albumin_gdl = albumin / 10
        else:
            albumin_gdl = albumin

        # Bilirubin: convert to μmol/L (model uses μmol/L)
        if bilirubin_unit.lower() in ["mg/dl", "mg"]:
            bili_day0_umol = bilirubin_day0 * 17.1
            bili_day7_umol = bilirubin_day7 * 17.1
        else:
            bili_day0_umol = bilirubin_day0
            bili_day7_umol = bilirubin_day7

        # Creatinine: if μmol/L, convert to mg/dL
        if creatinine_unit.lower() in ["umol/l", "μmol/l", "umol"]:
            creatinine_mgdl = creatinine / 88.4
        else:
            creatinine_mgdl = creatinine

        # PT: if looks like INR (<10), convert to estimated PT seconds
        if pt < 10:
            # Assuming control PT of 12 seconds, PT = INR × control
            pt_seconds = pt * 12
            pt_type = "INR (converted)"
        else:
            pt_seconds = pt
            pt_type = "seconds"

        # Bilirubin evolution (can be negative if improving)
        bilirubin_evolution = bili_day7_umol - bili_day0_umol

        # Lille model formula coefficients
        # R = 3.19 - 0.101×age + 0.147×albumin(g/L) + 0.0165×(bili_diff)
        #     - 0.206×renal - 0.0065×bili_day0 - 0.0096×PT
        # Lille = exp(-R)/(1 + exp(-R))

        # Note: Original paper uses albumin in g/L
        albumin_gl = albumin_gdl * 10

        # Renal failure term (1 if Cr > 1.3 mg/dL, else 0)
        renal = 1 if creatinine_mgdl > 1.3 else 0

        r_value = 3.19 - 0.101 * age + 0.147 * albumin_gl + 0.0165 * bilirubin_evolution - 0.206 * renal - 0.0065 * bili_day0_umol - 0.0096 * pt_seconds

        # Calculate Lille score
        lille = math.exp(-r_value) / (1 + math.exp(-r_value))

        # Components
        components = [
            f"Age term: -0.101 × {age} = {-0.101 * age:.3f}",
            f"Albumin term: 0.147 × {albumin_gl:.1f} g/L = {0.147 * albumin_gl:.3f}",
            f"Δ Bilirubin: {bili_day7_umol:.0f} - {bili_day0_umol:.0f} = {bilirubin_evolution:.0f} μmol/L",
            f"Δ Bilirubin term: 0.0165 × {bilirubin_evolution:.0f} = {0.0165 * bilirubin_evolution:.3f}",
            f"Renal term: -0.206 × {renal} = {-0.206 * renal:.3f}",
            f"Bilirubin D0 term: -0.0065 × {bili_day0_umol:.0f} = {-0.0065 * bili_day0_umol:.3f}",
            f"PT term: -0.0096 × {pt_seconds:.1f} = {-0.0096 * pt_seconds:.3f}",
            f"R = {r_value:.4f}",
            f"Lille = e^(-R)/(1+e^(-R)) = {lille:.4f}",
        ]

        # Interpretation based on Lille score
        # Complete responders: < 0.16
        # Partial responders: 0.16-0.56
        # Null responders: > 0.56
        # Simple cutoff for steroids: 0.45

        if lille < 0.16:
            risk_level = RiskLevel.VERY_LOW
            severity = Severity.MILD
            response_category = "Complete responder"
            recommendation = "Continue corticosteroids for full 28-day course"
            survival_6mo = "85%"
        elif lille < 0.45:
            risk_level = RiskLevel.LOW
            severity = Severity.MODERATE
            response_category = "Partial responder"
            recommendation = "Continue corticosteroids for full 28-day course"
            survival_6mo = "65%"
        elif lille < 0.56:
            risk_level = RiskLevel.INTERMEDIATE
            severity = Severity.SEVERE
            response_category = "Partial non-responder"
            recommendation = "Consider stopping steroids; limited benefit expected"
            survival_6mo = "30-50%"
        else:
            risk_level = RiskLevel.HIGH
            severity = Severity.CRITICAL
            response_category = "Null responder"
            recommendation = "Stop corticosteroids; no benefit and potential harm"
            survival_6mo = "25%"

        is_responder = lille < 0.45
        bilirubin_improved = bilirubin_evolution < 0

        interpretation = Interpretation(
            summary=f"Lille = {lille:.3f}: {response_category}",
            detail=(
                f"Lille score of {lille:.3f} at day 7 indicates {response_category.lower()}. "
                f"Bilirubin {'decreased' if bilirubin_improved else 'increased/stable'} from day 0 to day 7. "
                f"6-month survival approximately {survival_6mo}."
            ),
            severity=severity,
            risk_level=risk_level,
            stage=response_category,
            stage_description=(f"{'Responder (Lille < 0.45)' if is_responder else 'Non-responder (Lille ≥ 0.45)'}"),
            recommendations=(
                recommendation,
                "Continue alcohol abstinence",
                "Nutritional support",
                "Consider early transplant evaluation if non-responder",
            ),
            next_steps=(
                "Complete 28-day steroid course" if is_responder else "Stop steroids and reassess",
                "Monitor for complications (infection, hepatorenal syndrome)",
            ),
        )

        return ScoreResult(
            value=round(lille, 3),
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.metadata.references),
            tool_id=self.metadata.low_level.tool_id,
            tool_name=self.metadata.low_level.name,
            raw_inputs={
                "age": age,
                "albumin": albumin,
                "albumin_unit": albumin_unit,
                "bilirubin_day0": bilirubin_day0,
                "bilirubin_day7": bilirubin_day7,
                "bilirubin_unit": bilirubin_unit,
                "creatinine": creatinine,
                "creatinine_unit": creatinine_unit,
                "pt": pt,
            },
            calculation_details={
                "score_name": "Lille Model",
                "lille_score": round(lille, 4),
                "response_category": response_category,
                "is_responder": is_responder,
                "threshold": 0.45,
                "bilirubin_day0_umol": round(bili_day0_umol, 1),
                "bilirubin_day7_umol": round(bili_day7_umol, 1),
                "bilirubin_evolution_umol": round(bilirubin_evolution, 1),
                "albumin_gl": round(albumin_gl, 1),
                "creatinine_mgdl": round(creatinine_mgdl, 2),
                "renal_failure": renal == 1,
                "pt_seconds": round(pt_seconds, 1),
                "pt_type": pt_type,
                "R_value": round(r_value, 4),
                "estimated_6mo_survival": survival_6mo,
                "components": components,
            },
            formula_used="Lille = exp(-R)/(1+exp(-R)); R = 3.19 - 0.101×age + 0.147×albumin(g/L) + 0.0165×Δbili - 0.206×renal - 0.0065×bili₀ - 0.0096×PT",
            notes=[
                "Calculate at day 7 of corticosteroid therapy",
                "Lille < 0.45 indicates steroid responder - continue treatment",
                "Lille ≥ 0.45 indicates non-responder - consider stopping steroids",
                "Early bilirubin improvement (Δbili < 0) is key predictor of response",
            ],
        )
