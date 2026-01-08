"""
CAS (Clinical Activity Score) for Graves' Ophthalmopathy

The CAS is the European Group on Graves' Orbitopathy (EUGOGO)
recommended tool for assessing inflammatory activity in thyroid
eye disease (Graves' ophthalmopathy).

Reference (Original Development):
    Mourits MP, Koornneef L, Wiersinga WM, et al. Clinical criteria for
    the assessment of disease activity in Graves' ophthalmopathy: a novel
    approach. Br J Ophthalmol. 1989;73(8):639-644.
    PMID: 2765444

Reference (EUGOGO Guidelines):
    Bartalena L, Baldeschi L, Boboridis K, et al. The 2016 European
    Thyroid Association/European Group on Graves' Orbitopathy Guidelines
    for the Management of Graves' Orbitopathy. Eur Thyroid J. 2016;5(1):9-26.
    PMID: 27099835
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


class CASCalculator(BaseCalculator):
    """
    CAS (Clinical Activity Score) Calculator

    Assesses inflammatory activity in Graves' ophthalmopathy.
    7-item scale (initial visit) or 10-item scale (follow-up).
    CAS ≥3 indicates active disease suitable for immunosuppression.
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="cas_graves",
                name="CAS (Clinical Activity Score for Graves' Ophthalmopathy)",
                purpose="Assess inflammatory activity in thyroid eye disease",
                input_params=[
                    "spontaneous_orbital_pain",
                    "gaze_evoked_pain",
                    "eyelid_swelling",
                    "eyelid_erythema",
                    "conjunctival_redness",
                    "chemosis",
                    "caruncle_swelling",
                    "proptosis_increase",
                    "motility_decrease",
                    "visual_acuity_decrease",
                ],
                output_type="Score 0-10 with activity classification",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.ENDOCRINOLOGY,
                    Specialty.OPHTHALMOLOGY,
                ),
                conditions=(
                    "Graves' Ophthalmopathy",
                    "Thyroid Eye Disease",
                    "TED",
                    "Graves' Orbitopathy",
                    "GO",
                ),
                clinical_contexts=(
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.TREATMENT_DECISION,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "Is this Graves' ophthalmopathy active?",
                    "Should this patient receive immunosuppression for GO?",
                    "Calculate CAS score",
                    "Assess thyroid eye disease activity",
                ),
                keywords=(
                    "CAS",
                    "clinical activity score",
                    "Graves ophthalmopathy",
                    "thyroid eye disease",
                    "TED",
                    "orbitopathy",
                ),
            ),
            references=(
                Reference(
                    citation="Mourits MP, Koornneef L, Wiersinga WM, et al. Clinical criteria for the assessment of disease activity in Graves' ophthalmopathy. Br J Ophthalmol. 1989;73(8):639-644.",
                    pmid="2765444",
                    doi="10.1136/bjo.73.8.639",
                    year=1989,
                ),
                Reference(
                    citation="Bartalena L, Baldeschi L, Boboridis K, et al. The 2016 ETA/EUGOGO Guidelines for the Management of Graves' Orbitopathy. Eur Thyroid J. 2016;5(1):9-26.",
                    pmid="27099835",
                    doi="10.1159/000443828",
                    year=2016,
                ),
            ),
        )

    def calculate(self, **params) -> ScoreResult:
        """
        Calculate CAS score.

        Args:
            Initial assessment (7 items):
                spontaneous_orbital_pain: Spontaneous retrobulbar pain
                gaze_evoked_pain: Pain on eye movement
                eyelid_swelling: Eyelid swelling (attributable to GO)
                eyelid_erythema: Eyelid redness
                conjunctival_redness: Conjunctival injection
                chemosis: Conjunctival edema
                caruncle_swelling: Swelling of caruncle or plica

            Follow-up assessment (additional 3 items):
                proptosis_increase: Increase in proptosis ≥2mm in last 1-3 months
                motility_decrease: Decrease in eye movement ≥8° in last 1-3 months
                visual_acuity_decrease: Decrease in visual acuity ≥1 Snellen line in last 1-3 months

        Returns:
            ScoreResult with CAS score and activity classification
        """
        # Initial 7 items (always applicable)
        initial_items = [
            bool(params.get("spontaneous_orbital_pain", False)),
            bool(params.get("gaze_evoked_pain", False)),
            bool(params.get("eyelid_swelling", False)),
            bool(params.get("eyelid_erythema", False)),
            bool(params.get("conjunctival_redness", False)),
            bool(params.get("chemosis", False)),
            bool(params.get("caruncle_swelling", False)),
        ]

        # Follow-up items (3 additional, may be missing on initial visit)
        proptosis_increase = params.get("proptosis_increase")
        motility_decrease = params.get("motility_decrease")
        va_decrease = params.get("visual_acuity_decrease")

        # Calculate initial CAS (7-point)
        initial_score = sum(initial_items)

        # Calculate full CAS (10-point) if follow-up data available
        followup_items = []
        is_followup = False
        if proptosis_increase is not None:
            followup_items.append(bool(proptosis_increase))
            is_followup = True
        if motility_decrease is not None:
            followup_items.append(bool(motility_decrease))
            is_followup = True
        if va_decrease is not None:
            followup_items.append(bool(va_decrease))
            is_followup = True

        followup_score = sum(followup_items)
        total_score = initial_score + followup_score
        max_score = 7 + len(followup_items)

        # Determine activity (CAS ≥3 = active disease)
        is_active = total_score >= 3

        if total_score < 3:
            severity = Severity.NORMAL
            severity_text = "Inactive disease"
            stage = "Inactive"
        elif total_score < 5:
            severity = Severity.MODERATE
            severity_text = "Active disease (mild-moderate)"
            stage = "Active (mild-moderate)"
        else:
            severity = Severity.SEVERE
            severity_text = "Active disease (moderate-severe)"
            stage = "Active (moderate-severe)"

        # Identify present findings
        finding_names = [
            "spontaneous orbital pain",
            "gaze-evoked pain",
            "eyelid swelling",
            "eyelid erythema",
            "conjunctival redness",
            "chemosis",
            "caruncle swelling",
        ]
        present_findings = [name for name, present in zip(finding_names, initial_items) if present]

        if is_followup:
            if proptosis_increase is not None and bool(proptosis_increase):
                present_findings.append("proptosis increase")
            if motility_decrease is not None and bool(motility_decrease):
                present_findings.append("motility decrease")
            if va_decrease is not None and bool(va_decrease):
                present_findings.append("visual acuity decrease")

        # Recommendations (EUGOGO guidelines)
        recommendations = []
        if not is_active:
            recommendations.append("Inactive GO - immunosuppression not indicated")
            recommendations.append("Rehabilitative surgery may be considered")
            recommendations.append("Continue supportive measures (lubricants, sunglasses)")
        elif total_score < 5:
            recommendations.append("Active GO - consider IV corticosteroids")
            recommendations.append("First-line: IV methylprednisolone per EUGOGO protocol")
            recommendations.append("Optimize thyroid function (maintain euthyroidism)")
        else:
            recommendations.append("Highly active GO - urgent treatment needed")
            recommendations.append("IV methylprednisolone (high-dose pulse therapy)")
            recommendations.append("Consider orbital radiotherapy if steroid-refractory")
            recommendations.append("Teprotumumab may be considered")

        warnings = []
        if bool(params.get("visual_acuity_decrease", False)):
            warnings.append("Visual acuity loss - rule out dysthyroid optic neuropathy (DON)")
        if total_score >= 5:
            warnings.append("Highly active disease - early aggressive treatment recommended")
        if bool(params.get("spontaneous_orbital_pain", False)) and bool(params.get("gaze_evoked_pain", False)):
            warnings.append("Significant orbital inflammation - consider urgent ophthalmology review")

        next_steps = [
            "Ophthalmology assessment for visual function",
            "Ensure euthyroid state maintained",
            "Smoking cessation if applicable (worsens GO)",
            "Repeat CAS at follow-up to assess treatment response",
        ]

        return ScoreResult(
            value=total_score,
            unit=Unit.SCORE,
            interpretation=Interpretation(
                summary=f"CAS = {total_score}/{max_score}: {'Active' if is_active else 'Inactive'} Graves' ophthalmopathy",
                detail=(
                    f"CAS score of {total_score}/{max_score} indicates {severity_text.lower()}. "
                    f"{'CAS ≥3 = active disease suitable for immunosuppression. ' if is_active else 'CAS <3 = inactive disease. '}"
                    f"Present findings: {', '.join(present_findings) if present_findings else 'None'}. "
                    f"{'Full 10-item assessment.' if is_followup else '7-item initial assessment.'}"
                ),
                severity=severity,
                stage=stage,
                stage_description=severity_text,
                recommendations=recommendations,
                warnings=warnings,
                next_steps=next_steps,
            ),
            references=self.metadata.references,
            tool_id=self.metadata.low_level.tool_id,
            tool_name=self.metadata.low_level.name,
            raw_inputs=params,
            calculation_details={
                "total_score": total_score,
                "max_score": max_score,
                "initial_score": initial_score,
                "followup_score": followup_score,
                "is_followup_assessment": is_followup,
                "is_active_disease": is_active,
                "present_findings": present_findings,
                "activity_classification": stage,
            },
        )
