"""
STONE Score (Prediction of Ureteral Stone)

The STONE score is a clinical prediction rule for diagnosing
ureteral stones in patients presenting with flank pain.

Reference (Original Development & Validation):
    Moore CL, Bomann S, Daniels B, et al. Derivation and validation of
    a clinical prediction rule for uncomplicated ureteral stone - the
    STONE score: retrospective and prospective observational cohort studies.
    BMJ. 2014;348:g2191.
    PMID: 24671981

Reference (External Validation):
    Wang RC, Rodriguez RM, Moghadassi M, et al. External Validation of
    the STONE Score, a Clinical Prediction Rule for Ureteral Stone.
    Ann Emerg Med. 2016;67(4):423-432.
    PMID: 26747218
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


class STONEScoreCalculator(BaseCalculator):
    """
    STONE Score Calculator

    Predicts probability of ureteral stone in ED patients with flank pain.
    Score range: 0-13
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="stone_score",
                name="STONE Score (Prediction of Ureteral Stone)",
                purpose="Predict probability of ureteral stone in flank pain",
                input_params=[
                    "sex",
                    "timing_onset",
                    "origin_nonblack",
                    "nausea_vomiting",
                    "erythrocytes_in_urine",
                ],
                output_type="Score 0-13 with stone probability",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.UROLOGY,
                    Specialty.EMERGENCY_MEDICINE,
                ),
                conditions=(
                    "Ureteral Stone",
                    "Nephrolithiasis",
                    "Renal Colic",
                    "Kidney Stone",
                    "Urolithiasis",
                ),
                clinical_contexts=(
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.TREATMENT_DECISION,
                ),
                clinical_questions=(
                    "Does this patient have a ureteral stone?",
                    "Should this patient get a CT for kidney stone?",
                    "Calculate STONE score",
                    "Predict stone probability",
                ),
                keywords=(
                    "STONE score",
                    "ureteral stone",
                    "kidney stone",
                    "renal colic",
                    "flank pain",
                    "nephrolithiasis",
                ),
            ),
            references=(
                Reference(
                    citation="Moore CL, Bomann S, Daniels B, et al. Derivation and validation of a clinical prediction rule for uncomplicated ureteral stone - the STONE score. BMJ. 2014;348:g2191.",
                    pmid="24671981",
                    doi="10.1136/bmj.g2191",
                    year=2014,
                ),
                Reference(
                    citation="Wang RC, Rodriguez RM, Moghadassi M, et al. External Validation of the STONE Score. Ann Emerg Med. 2016;67(4):423-432.",
                    pmid="26747218",
                    doi="10.1016/j.annemergmed.2015.11.011",
                    year=2016,
                ),
            ),
        )

    def calculate(self, **params) -> ScoreResult:
        """
        Calculate STONE score.

        Args:
            sex: Patient sex ("male" = 2 points, "female" = 0 points)
            timing_onset: Duration of pain
                "6_24_hours" = 3 points (pain onset 6-24 hours ago)
                "less_than_6_hours" = 1 point
                "more_than_24_hours" = 0 points
            origin_nonblack: Non-Black race (True = 3 points)
            nausea_vomiting: Nausea or vomiting alone (True = 1 point),
                            or "both" for nausea AND vomiting (2 points)
            erythrocytes_in_urine: RBC in urine
                "none" = 0 points
                "trace_to_moderate" = 2 points (trace to <50 RBC/hpf)
                "many" = 3 points (≥50 RBC/hpf or gross hematuria)

        Returns:
            ScoreResult with STONE score and stone probability
        """
        score = 0
        details = {}

        # Sex (S)
        sex = str(params.get("sex", "")).lower()
        if sex == "male":
            sex_points = 2
        elif sex == "female":
            sex_points = 0
        else:
            raise ValueError("sex must be 'male' or 'female'")
        score += sex_points
        details["sex_points"] = sex_points

        # Timing/duration of pain (T)
        timing = str(params.get("timing_onset", "")).lower()
        if timing in ["6_24_hours", "6-24 hours", "6-24h"]:
            timing_points = 3
        elif timing in ["less_than_6_hours", "<6 hours", "<6h"]:
            timing_points = 1
        elif timing in ["more_than_24_hours", ">24 hours", ">24h"]:
            timing_points = 0
        else:
            raise ValueError("timing_onset must be '6_24_hours', 'less_than_6_hours', or 'more_than_24_hours'")
        score += timing_points
        details["timing_points"] = timing_points

        # Origin/race (O)
        nonblack = bool(params.get("origin_nonblack", True))
        origin_points = 3 if nonblack else 0
        score += origin_points
        details["origin_points"] = origin_points

        # Nausea/vomiting (N)
        nausea_param = params.get("nausea_vomiting", False)
        if isinstance(nausea_param, str):
            if nausea_param.lower() == "both":
                nausea_points = 2
            elif nausea_param.lower() in ["true", "yes", "one"]:
                nausea_points = 1
            else:
                nausea_points = 0
        elif nausea_param is True:
            nausea_points = 1
        else:
            nausea_points = 0
        score += nausea_points
        details["nausea_points"] = nausea_points

        # Erythrocytes in urine (E)
        rbc = str(params.get("erythrocytes_in_urine", "none")).lower()
        if rbc in ["none", "0", "negative"]:
            rbc_points = 0
        elif rbc in ["trace_to_moderate", "trace", "moderate", "1-49", "<50"]:
            rbc_points = 2
        elif rbc in ["many", "gross", ">=50", "50+"]:
            rbc_points = 3
        else:
            raise ValueError("erythrocytes_in_urine must be 'none', 'trace_to_moderate', or 'many'")
        score += rbc_points
        details["erythrocytes_points"] = rbc_points

        # Determine probability category
        if score <= 5:
            severity = Severity.MILD
            probability = "Low (~10%)"
            stage = "Low"
            stone_likely = False
        elif score <= 9:
            severity = Severity.MODERATE
            probability = "Moderate (~50%)"
            stage = "Moderate"
            stone_likely = True
        else:
            severity = Severity.SEVERE
            probability = "High (~90%)"
            stage = "High"
            stone_likely = True

        # Recommendations
        recommendations = []
        if score <= 5:
            recommendations.append("Low probability - consider alternative diagnoses")
            recommendations.append("May avoid CT if clinical suspicion low")
            recommendations.append("Consider ultrasound as first-line imaging")
        elif score <= 9:
            recommendations.append("Moderate probability - CT recommended if diagnosis uncertain")
            recommendations.append("Low-dose CT protocol can reduce radiation")
        else:
            recommendations.append("High probability - stone very likely")
            recommendations.append("CT to confirm and determine stone size/location")
            recommendations.append("Consider empiric treatment while awaiting imaging")

        # General management
        recommendations.append("Adequate analgesia (NSAIDs first-line)")
        if stone_likely:
            recommendations.append("Alpha-blocker (tamsulosin) for medical expulsive therapy if stone <10mm")

        warnings = []
        if score >= 10:
            warnings.append("Very high probability of stone - ensure appropriate imaging")
        if rbc_points == 0 and score >= 6:
            warnings.append("No hematuria but moderate risk - consider CT")

        next_steps = [
            "CT KUB (non-contrast) if moderate-high probability",
            "Renal ultrasound as alternative (less sensitive)",
            "Urinalysis and serum creatinine",
            "Pain management",
        ]

        return ScoreResult(
            value=score,
            unit=Unit.SCORE,
            interpretation=Interpretation(
                summary=f"STONE Score = {score}/13: {probability} probability of ureteral stone",
                detail=(
                    f"STONE score of {score}/13 indicates {probability.lower()} probability of ureteral stone. "
                    f"Components: Sex {sex_points}, Timing {timing_points}, Origin {origin_points}, "
                    f"Nausea {nausea_points}, Erythrocytes {rbc_points}. "
                    f"{'Stone is likely - imaging recommended.' if stone_likely else 'Stone less likely - consider alternatives.'}"
                ),
                severity=severity,
                stage=stage,
                stage_description=f"{probability} probability",
                recommendations=recommendations,
                warnings=warnings,
                next_steps=next_steps,
            ),
            references=self.metadata.references,
            tool_id=self.metadata.low_level.tool_id,
            tool_name=self.metadata.low_level.name,
            raw_inputs=params,
            calculation_details={
                "total_score": score,
                "probability_category": stage,
                "stone_probability": probability,
                "stone_likely": stone_likely,
                **details,
            },
        )
