"""
Palliative Performance Scale (PPS)

The Palliative Performance Scale version 2 (PPSv2) is a functional status
tool widely used in palliative care for prognosis, communication, and care
planning. Scores range from 0 to 100 in 10-point increments.

Reference (Foundational Prognostic Study):
    Lau F, Downing GM, Lesperance M, et al. Use of Palliative Performance
    Scale in end-of-life prognostication. J Palliat Med. 2006;9(5):1066-1075.
    PMID: 17040144

Reference (Psychometric Validation):
    Dzierzanowski T, Gradalski T, Kozlowski M. Palliative Performance Scale:
    cross cultural adaptation and psychometric validation for Polish hospice
    setting. BMC Palliat Care. 2020;19(1):52.
    PMID: 32321494
"""

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class PalliativePerformanceScaleCalculator(BaseCalculator):
    """Palliative Performance Scale calculator."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="palliative_performance_scale",
                name="Palliative Performance Scale (PPS)",
                purpose="Assess functional status and prognosis in palliative care",
                input_params=["pps_score"],
                output_type="Score 0-100% in 10-point increments with palliative functional interpretation",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.PALLIATIVE_CARE,
                    Specialty.ONCOLOGY,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.GERIATRICS,
                ),
                conditions=(
                    "Serious Illness",
                    "Advanced Cancer",
                    "End of Life Care",
                    "Palliative Care",
                    "Functional Decline",
                ),
                clinical_contexts=(
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.MONITORING,
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.TREATMENT_DECISION,
                ),
                clinical_questions=(
                    "What is this patient's functional status in palliative care?",
                    "How limited is this patient by advanced illness?",
                    "What is the prognosis associated with this PPS score?",
                    "Should goals-of-care and hospice planning be escalated?",
                ),
                keywords=(
                    "PPS",
                    "Palliative Performance Scale",
                    "palliative functional status",
                    "hospice",
                    "end of life prognosis",
                    "performance status",
                ),
            ),
            references=(
                Reference(
                    citation="Lau F, Downing GM, Lesperance M, Karlson N, Kuziemsky C, Bernard S, Hanson L, Olajide L, Head B, Ritchie C, Harrold J, Casarett D. Use of Palliative Performance Scale in end-of-life prognostication. J Palliat Med. 2006;9(5):1066-1075.",
                    pmid="17040144",
                    doi="10.1089/jpm.2006.9.1066",
                    year=2006,
                ),
                Reference(
                    citation="Dzierzanowski T, Gradalski T, Kozlowski M. Palliative Performance Scale: cross cultural adaptation and psychometric validation for Polish hospice setting. BMC Palliat Care. 2020;19(1):52.",
                    pmid="32321494",
                    doi="10.1186/s12904-020-00563-8",
                    year=2020,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(self, pps_score: int) -> ScoreResult:
        """Calculate PPS interpretation from a 0-100 score in 10-point increments."""
        if pps_score < 0 or pps_score > 100:
            raise ValueError("PPS score must be between 0 and 100")
        if pps_score % 10 != 0:
            raise ValueError("PPS score must be in increments of 10")

        descriptions = {
            100: "Full ambulation; normal activity and work; no evidence of disease; full self-care; normal intake; full consciousness",
            90: "Full ambulation; normal activity; some evidence of disease; full self-care; normal intake; full consciousness",
            80: "Full ambulation; normal activity with effort; some evidence of disease; full self-care; normal or reduced intake; full consciousness",
            70: "Reduced ambulation; unable normal job or work; significant disease; full self-care; normal or reduced intake; full consciousness",
            60: "Reduced ambulation; unable hobby or house work; significant disease; occasional assistance necessary; normal or reduced intake; full consciousness or confusion",
            50: "Mainly sit or lie; unable to do any work; extensive disease; considerable assistance required; normal or reduced intake; full consciousness or confusion",
            40: "Mainly in bed; unable to do most activity; extensive disease; mainly assistance required; normal or reduced intake; full consciousness or drowsy or confusion",
            30: "Totally bed bound; unable to do any activity; extensive disease; total care required; reduced intake; full consciousness or drowsy or confusion",
            20: "Totally bed bound; unable to do any activity; extensive disease; total care required; minimal sips; full consciousness or drowsy or confusion",
            10: "Totally bed bound; unable to do any activity; extensive disease; total care required; mouth care only; drowsy or coma",
            0: "Death",
        }

        interpretation = self._get_interpretation(pps_score, descriptions[pps_score])

        return ScoreResult(
            value=pps_score,
            unit=Unit.PERCENT,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={"pps_score": pps_score},
            calculation_details={
                "pps_score": pps_score,
                "description": descriptions[pps_score],
                "all_descriptions": descriptions,
            },
            formula_used="PPS functional status assigned as standardized 0-100% 10-point scale",
        )

    def _get_interpretation(self, score: int, description: str) -> Interpretation:
        if score >= 80:
            return Interpretation(
                summary=f"PPS {score}%: Preserved Functional Status",
                detail=f"{description}. Functional reserve remains relatively preserved in the palliative context.",
                severity=Severity.MILD if score < 100 else Severity.NORMAL,
                stage=f"PPS {score}",
                stage_description="Preserved functional status",
                recommendations=(
                    "Continue disease-directed and supportive care according to goals",
                    "Reassess function serially as decline may change prognosis and care planning",
                ),
                next_steps=("Document baseline PPS for longitudinal follow-up",),
            )
        if score >= 50:
            return Interpretation(
                summary=f"PPS {score}%: Moderate Functional Impairment",
                detail=f"{description}. Patient has clear functional decline and increasing need for support.",
                severity=Severity.MODERATE,
                stage=f"PPS {score}",
                stage_description="Moderate functional impairment",
                recommendations=(
                    "Review symptom burden, caregiver needs, and care setting suitability",
                    "Use PPS trend alongside diagnosis and trajectory for prognostic discussions",
                    "Consider early hospice or specialist palliative review if not already involved",
                ),
                warnings=("Declining PPS is associated with shorter survival in advanced illness",),
                next_steps=(
                    "Update goals-of-care discussion",
                    "Assess equipment and home support needs",
                ),
            )
        if score >= 10:
            return Interpretation(
                summary=f"PPS {score}%: Severe Functional Impairment",
                detail=f"{description}. Functional status is profoundly limited and prognosis is often poor.",
                severity=Severity.SEVERE,
                stage=f"PPS {score}",
                stage_description="Severe functional impairment",
                recommendations=(
                    "Prioritize comfort-focused care and aggressive symptom management",
                    "Ensure goals-of-care, code status, and hospice planning are reviewed",
                    "Support family and caregiver decision-making",
                ),
                warnings=("Low PPS scores are associated with limited survival and high care needs",),
                next_steps=(
                    "Escalate palliative or hospice support as appropriate",
                    "Review swallowing, intake, and pressure injury prevention needs",
                ),
            )
        return Interpretation(
            summary="PPS 0%: Death",
            detail="PPS 0% indicates death.",
            severity=Severity.CRITICAL,
            stage="PPS 0",
            stage_description="Death",
            recommendations=("Use only for retrospective documentation",),
            next_steps=("Complete required documentation and family support processes",),
        )
