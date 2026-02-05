"""
SCORAD (SCORing Atopic Dermatitis)

The SCORAD index is a validated tool for assessing atopic dermatitis
severity, combining extent of disease, intensity of lesions, and
subjective symptoms.

Reference (Original Development):
    European Task Force on Atopic Dermatitis. Severity scoring of atopic
    dermatitis: the SCORAD index. Consensus Report of the European Task
    Force on Atopic Dermatitis. Dermatology. 1993;186(1):23-31.
    PMID: 8435513

Reference (Validation):
    Kunz B, Oranje AP, Labrèze L, et al. Clinical validation and guidelines
    for the SCORAD index: consensus report of the European Task Force on
    Atopic Dermatitis. Dermatology. 1997;195(1):10-19.
    PMID: 9267730
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


class SCORADCalculator(BaseCalculator):
    """
    SCORAD (SCORing Atopic Dermatitis) Calculator

    Assesses atopic dermatitis severity using three components:
    A = Extent (0-100% BSA)
    B = Intensity (6 items, each 0-3)
    C = Subjective symptoms (itch + sleep loss, each 0-10)

    Formula: SCORAD = A/5 + 7B/2 + C
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="scorad",
                name="SCORAD (SCORing Atopic Dermatitis)",
                purpose="Assess atopic dermatitis severity",
                input_params=[
                    "extent_bsa",
                    "erythema",
                    "edema_papulation",
                    "oozing_crusting",
                    "excoriation",
                    "lichenification",
                    "dryness",
                    "pruritus_vas",
                    "sleep_loss_vas",
                ],
                output_type="Score 0-103 with severity classification",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.DERMATOLOGY,
                    Specialty.ALLERGY_IMMUNOLOGY,
                    Specialty.PEDIATRICS,
                ),
                conditions=(
                    "Atopic Dermatitis",
                    "Eczema",
                    "Atopic Eczema",
                    "Childhood Eczema",
                ),
                clinical_contexts=(
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.TREATMENT_DECISION,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "How severe is this patient's atopic dermatitis?",
                    "Is this eczema mild, moderate, or severe?",
                    "Does this patient need systemic therapy?",
                    "Calculate SCORAD index",
                ),
                keywords=(
                    "SCORAD",
                    "atopic dermatitis",
                    "eczema severity",
                    "AD scoring",
                    "eczema assessment",
                ),
            ),
            references=(
                Reference(
                    citation="European Task Force on Atopic Dermatitis. Severity scoring of atopic dermatitis: the SCORAD index. Dermatology. 1993;186(1):23-31.",
                    pmid="8435513",
                    doi="10.1159/000247298",
                    year=1993,
                ),
                Reference(
                    citation="Kunz B, Oranje AP, Labrèze L, et al. Clinical validation and guidelines for the SCORAD index. Dermatology. 1997;195(1):10-19.",
                    pmid="9267730",
                    doi="10.1159/000245677",
                    year=1997,
                ),
            ),
        )

    def calculate(self, **params: Any) -> ScoreResult:
        """
        Calculate SCORAD index.

        Args:
            extent_bsa: Body surface area affected (0-100%)
            erythema: Erythema intensity (0=none, 1=mild, 2=moderate, 3=severe)
            edema_papulation: Edema/papulation intensity (0-3)
            oozing_crusting: Oozing/crusting intensity (0-3)
            excoriation: Excoriation intensity (0-3)
            lichenification: Lichenification intensity (0-3)
            dryness: Dryness of uninvolved skin (0-3)
            pruritus_vas: Pruritus VAS score (0-10)
            sleep_loss_vas: Sleep loss VAS score (0-10)

        Returns:
            ScoreResult with SCORAD index and severity classification
        """
        # Extract parameters
        extent = float(params.get("extent_bsa", 0))
        erythema = int(params.get("erythema", 0))
        edema = int(params.get("edema_papulation", 0))
        oozing = int(params.get("oozing_crusting", 0))
        excoriation = int(params.get("excoriation", 0))
        lichenification = int(params.get("lichenification", 0))
        dryness = int(params.get("dryness", 0))
        pruritus = float(params.get("pruritus_vas", 0))
        sleep_loss = float(params.get("sleep_loss_vas", 0))

        # Validation
        if not 0 <= extent <= 100:
            raise ValueError("extent_bsa must be 0-100")

        for score, name in [
            (erythema, "erythema"),
            (edema, "edema_papulation"),
            (oozing, "oozing_crusting"),
            (excoriation, "excoriation"),
            (lichenification, "lichenification"),
            (dryness, "dryness"),
        ]:
            if not 0 <= score <= 3:
                raise ValueError(f"{name} must be 0-3")

        if not 0 <= pruritus <= 10:
            raise ValueError("pruritus_vas must be 0-10")
        if not 0 <= sleep_loss <= 10:
            raise ValueError("sleep_loss_vas must be 0-10")

        # Calculate components
        # A = Extent (0-100)
        a_extent = extent

        # B = Intensity sum (0-18)
        b_intensity = erythema + edema + oozing + excoriation + lichenification + dryness

        # C = Subjective symptoms (0-20)
        c_subjective = pruritus + sleep_loss

        # SCORAD = A/5 + 7B/2 + C (max theoretical = 20 + 63 + 20 = 103)
        total_scorad = (a_extent / 5) + (7 * b_intensity / 2) + c_subjective

        # Objective SCORAD (without subjective symptoms)
        objective_scorad = (a_extent / 5) + (7 * b_intensity / 2)

        # Determine severity (European guidelines)
        if total_scorad < 25:
            severity = Severity.MILD
            severity_text = "Mild atopic dermatitis"
            stage = "Mild"
        elif total_scorad < 50:
            severity = Severity.MODERATE
            severity_text = "Moderate atopic dermatitis"
            stage = "Moderate"
        else:
            severity = Severity.SEVERE
            severity_text = "Severe atopic dermatitis"
            stage = "Severe"

        # Treatment recommendations
        recommendations = []
        if total_scorad < 25:
            recommendations.append("Emollients and topical corticosteroids as needed")
            recommendations.append("Focus on skin barrier repair")
        elif total_scorad < 50:
            recommendations.append("Regular topical corticosteroids or calcineurin inhibitors")
            recommendations.append("Consider proactive maintenance therapy")
        else:
            recommendations.append("Consider systemic therapy (dupilumab, JAK inhibitors)")
            recommendations.append("Phototherapy may be appropriate")
            recommendations.append("Referral to dermatology specialist recommended")

        warnings = []
        if pruritus >= 7:
            warnings.append("Severe pruritus - consider aggressive itch management")
        if sleep_loss >= 7:
            warnings.append("Significant sleep impairment - impacts quality of life")

        next_steps = [
            "Assess for triggers and allergens",
            "Evaluate quality of life with DLQI",
            "Monitor SCORAD at follow-up visits",
        ]

        return ScoreResult(
            value=round(total_scorad, 1),
            unit=Unit.SCORE,
            interpretation=Interpretation(
                summary=f"SCORAD = {round(total_scorad, 1)}: {severity_text}",
                detail=(
                    f"SCORAD {round(total_scorad, 1)} indicates {severity_text.lower()}. "
                    f"Components: Extent (A) = {extent}% BSA, Intensity (B) = {b_intensity}/18, "
                    f"Subjective (C) = {c_subjective}/20 (pruritus {pruritus}, sleep loss {sleep_loss}). "
                    f"Objective SCORAD (without subjective): {round(objective_scorad, 1)}."
                ),
                severity=severity,
                stage=stage,
                stage_description=severity_text,
                recommendations=tuple(recommendations),
                warnings=tuple(warnings),
                next_steps=tuple(next_steps),
            ),
            references=list(self.metadata.references),
            tool_id=self.metadata.low_level.tool_id,
            tool_name=self.metadata.low_level.name,
            raw_inputs=params,
            calculation_details={
                "total_scorad": round(total_scorad, 1),
                "objective_scorad": round(objective_scorad, 1),
                "extent_component": round(a_extent / 5, 1),
                "intensity_component": round(7 * b_intensity / 2, 1),
                "subjective_component": c_subjective,
                "intensity_sum": b_intensity,
                "severity_classification": stage,
            },
        )
