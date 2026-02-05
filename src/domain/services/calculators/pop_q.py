"""
POP-Q (Pelvic Organ Prolapse Quantification)

The POP-Q is the standardized system for quantifying pelvic organ
prolapse adopted by the International Continence Society (ICS).

Reference (ICS Standardization):
    Bump RC, Mattiasson A, Bø K, et al. The standardization of terminology
    of female pelvic organ prolapse and pelvic floor dysfunction.
    Am J Obstet Gynecol. 1996;175(1):10-17.
    PMID: 8694033

Reference (Clinical Use):
    Persu C, Chapple CR, Cauni V, et al. Pelvic Organ Prolapse
    Quantification System (POP-Q) - a new era in pelvic prolapse staging.
    J Med Life. 2011;4(1):75-81.
    PMID: 21505577
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


class POPQCalculator(BaseCalculator):
    """
    POP-Q (Pelvic Organ Prolapse Quantification) Calculator

    Standardized staging system using 6 vaginal sites measured
    relative to the hymen.
    Stages: 0-IV
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="pop_q",
                name="POP-Q (Pelvic Organ Prolapse Quantification)",
                purpose="Stage pelvic organ prolapse severity",
                input_params=[
                    "point_aa",
                    "point_ba",
                    "point_c",
                    "point_d",
                    "point_ap",
                    "point_bp",
                    "genital_hiatus",
                    "perineal_body",
                    "total_vaginal_length",
                ],
                output_type="POP-Q Stage 0-IV with compartment assessment",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.GYNECOLOGY,
                    Specialty.UROLOGY,
                ),
                conditions=(
                    "Pelvic Organ Prolapse",
                    "Cystocele",
                    "Rectocele",
                    "Uterine Prolapse",
                    "Vaginal Vault Prolapse",
                    "Enterocele",
                ),
                clinical_contexts=(
                    ClinicalContext.STAGING,
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.TREATMENT_DECISION,
                ),
                clinical_questions=(
                    "What stage is this pelvic organ prolapse?",
                    "Calculate POP-Q score",
                    "Assess prolapse severity",
                    "Which compartment is affected?",
                ),
                keywords=(
                    "POP-Q",
                    "pelvic prolapse",
                    "cystocele",
                    "rectocele",
                    "uterine prolapse",
                    "vaginal prolapse",
                ),
            ),
            references=(
                Reference(
                    citation="Bump RC, Mattiasson A, Bø K, et al. The standardization of terminology of female pelvic organ prolapse and pelvic floor dysfunction. Am J Obstet Gynecol. 1996;175(1):10-17.",
                    pmid="8694033",
                    doi="10.1016/s0002-9378(96)70243-0",
                    year=1996,
                ),
                Reference(
                    citation="Persu C, Chapple CR, Cauni V, et al. POP-Q - a new era in pelvic prolapse staging. J Med Life. 2011;4(1):75-81.",
                    pmid="21505577",
                    year=2011,
                ),
            ),
        )

    def calculate(self, **params: Any) -> ScoreResult:
        """
        Calculate POP-Q stage.

        All measurements in cm relative to hymen (negative = above, positive = below)

        Args:
            Anterior compartment:
                point_aa: Point Aa (-3 to +3), 3cm proximal to urethral meatus
                point_ba: Point Ba (-3 to +TVL), most distal anterior wall

            Apical compartment:
                point_c: Point C, cervix or vaginal cuff
                point_d: Point D, posterior fornix (if uterus present, else omit)

            Posterior compartment:
                point_ap: Point Ap (-3 to +3), 3cm proximal to hymen on posterior wall
                point_bp: Point Bp (-3 to +TVL), most distal posterior wall

            Other measurements (always positive):
                genital_hiatus: GH, measured from urethral meatus to posterior hymen
                perineal_body: PB, from posterior hymen to mid-anus
                total_vaginal_length: TVL, greatest depth with prolapse reduced

        Returns:
            ScoreResult with POP-Q stage and compartment analysis
        """
        # Extract measurements
        aa = float(params.get("point_aa", -3))
        ba = float(params.get("point_ba", -3))
        c = float(params.get("point_c", -7))
        d = params.get("point_d")  # May be None if no uterus
        ap = float(params.get("point_ap", -3))
        bp = float(params.get("point_bp", -3))
        gh = float(params.get("genital_hiatus", 0))
        pb = float(params.get("perineal_body", 0))
        tvl = float(params.get("total_vaginal_length", 9))

        if d is not None:
            d = float(d)

        # Validate ranges
        if not -3 <= aa <= 3:
            raise ValueError("point_aa must be -3 to +3")
        if not -3 <= ap <= 3:
            raise ValueError("point_ap must be -3 to +3")
        if tvl <= 0:
            raise ValueError("total_vaginal_length must be positive")

        # Determine most distal point of prolapse
        points = [aa, ba, c, ap, bp]
        if d is not None:
            points.append(d)
        most_distal = max(points)

        # POP-Q Staging (ICS criteria)
        if most_distal < -1:
            if aa <= -3 and ba <= -3 and c < -(tvl - 2) and ap <= -3 and bp <= -3:
                stage = 0
                stage_description = "No prolapse"
            else:
                stage = 1
                stage_description = "Prolapse >1cm above hymen"
        elif most_distal <= 1:
            stage = 2
            stage_description = "Prolapse within 1cm of hymen"
        elif most_distal < tvl - 2:
            stage = 3
            stage_description = "Prolapse >1cm below hymen, not complete eversion"
        else:
            stage = 4
            stage_description = "Complete eversion"

        # Determine severity
        severity_map = {
            0: Severity.NORMAL,
            1: Severity.MILD,
            2: Severity.MODERATE,
            3: Severity.SEVERE,
            4: Severity.CRITICAL,
        }
        severity = severity_map[stage]

        # Compartment analysis
        anterior_max = max(aa, ba)
        posterior_max = max(ap, bp)
        apical_max = c if d is None else max(c, d)

        compartments = []
        if anterior_max > -1:
            compartments.append(f"Anterior (Aa={aa}, Ba={ba})")
        if posterior_max > -1:
            compartments.append(f"Posterior (Ap={ap}, Bp={bp})")
        if apical_max > -(tvl - 2):
            compartments.append(f"Apical (C={c}" + (f", D={d})" if d is not None else ")"))

        # Identify predominant compartment
        max_values = {"anterior": anterior_max, "posterior": posterior_max, "apical": apical_max}
        predominant = max(max_values, key=lambda k: max_values[k])

        # Recommendations
        recommendations = []
        if stage == 0:
            recommendations.append("No prolapse - no treatment needed")
            recommendations.append("Pelvic floor exercises for prevention")
        elif stage == 1:
            recommendations.append("Mild prolapse - conservative management")
            recommendations.append("Pelvic floor muscle training (PFMT)")
            recommendations.append("Monitor symptoms")
        elif stage == 2:
            recommendations.append("Moderate prolapse - symptomatic treatment")
            recommendations.append("Pessary trial if symptomatic")
            recommendations.append("PFMT may help")
            recommendations.append("Surgical repair if pessary fails/declined")
        else:  # Stage 3-4
            recommendations.append("Advanced prolapse - active treatment needed")
            recommendations.append("Pessary trial (ring, Gellhorn)")
            recommendations.append("Surgical repair indicated if conservative fails")
            if stage == 4:
                recommendations.append("Total eversion - evaluate for concurrent vault suspension")

        warnings = []
        if stage >= 3:
            warnings.append("Advanced prolapse - evaluate for urinary retention and hydronephrosis")
        if gh >= 5:
            warnings.append("Wide genital hiatus - higher recurrence risk with surgery")
        if tvl < 6:
            warnings.append("Short vaginal length - may affect pessary fitting")

        next_steps = [
            "Symptom assessment (POP-SS questionnaire)",
            "Check post-void residual",
            "Pessary fitting if symptomatic",
            "Urogynecology referral if surgery considered",
        ]

        return ScoreResult(
            value=stage,
            unit=Unit.STAGE,
            interpretation=Interpretation(
                summary=f"POP-Q Stage {stage}: {stage_description}",
                detail=(
                    f"POP-Q staging shows Stage {stage} pelvic organ prolapse. "
                    f"Most distal point: {most_distal:+.1f} cm relative to hymen. "
                    f"Affected compartments: {', '.join(compartments) if compartments else 'None'}. "
                    f"Predominant: {predominant} compartment. "
                    f"TVL={tvl}cm, GH={gh}cm, PB={pb}cm."
                ),
                severity=severity,
                stage=f"Stage {stage}",
                stage_description=stage_description,
                recommendations=tuple(recommendations),
                warnings=tuple(warnings),
                next_steps=tuple(next_steps),
            ),
            references=list(self.metadata.references),
            tool_id=self.metadata.low_level.tool_id,
            tool_name=self.metadata.low_level.name,
            raw_inputs=params,
            calculation_details={
                "stage": stage,
                "stage_description": stage_description,
                "most_distal_point": most_distal,
                "point_aa": aa,
                "point_ba": ba,
                "point_c": c,
                "point_d": d,
                "point_ap": ap,
                "point_bp": bp,
                "genital_hiatus": gh,
                "perineal_body": pb,
                "total_vaginal_length": tvl,
                "anterior_max": anterior_max,
                "posterior_max": posterior_max,
                "apical_max": apical_max,
                "predominant_compartment": predominant,
                "affected_compartments": compartments,
            },
        )
