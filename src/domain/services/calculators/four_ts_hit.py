"""
4Ts Score for Heparin-Induced Thrombocytopenia (HIT)

Clinical prediction rule for HIT probability.

Reference:
    Lo GK, Juhl D, Warkentin TE, et al. Evaluation of pretest clinical score
    (4 T's) for the diagnosis of heparin-induced thrombocytopenia in two
    clinical settings. J Thromb Haemost. 2006;4(4):759-765.
    DOI: 10.1111/j.1538-7836.2006.01787.x
    PMID: 16634744

    Cuker A, Gimotty PA, Crowther MA, Warkentin TE. Predictive value of the
    4Ts scoring system for heparin-induced thrombocytopenia: a systematic
    review and meta-analysis. Blood. 2012;120(20):4160-4167.
    DOI: 10.1182/blood-2012-07-443051
    PMID: 22990018
"""

from typing import Literal

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


class FourTsHitCalculator(BaseCalculator):
    """
    4Ts Score for Heparin-Induced Thrombocytopenia (HIT)

    The 4Ts score is a clinical prediction rule used to estimate the pretest
    probability of HIT before confirmatory laboratory testing.

    Components (each scored 0, 1, or 2):
        - Thrombocytopenia: Degree of platelet fall
        - Timing: When did platelet fall occur after heparin exposure
        - Thrombosis: New thrombosis or other sequelae
        - oTher causes: Other causes for thrombocytopenia

    Score Interpretation:
        - 0-3: Low probability (≤5% chance of HIT)
        - 4-5: Intermediate probability (10-30% chance of HIT)
        - 6-8: High probability (40-80% chance of HIT)

    Clinical Use:
        - Low score: HIT unlikely, continue heparin if clinically indicated
        - Intermediate/High: Send HIT antibody testing, consider stopping heparin
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="4ts_hit",
                name="4Ts Score for HIT",
                purpose="Assess pretest probability of heparin-induced thrombocytopenia",
                input_params=["thrombocytopenia", "timing", "thrombosis", "other_causes"],
                output_type="4Ts score with HIT probability",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.HEMATOLOGY,
                    Specialty.CRITICAL_CARE,
                    Specialty.CARDIOLOGY,
                    Specialty.SURGERY,
                    Specialty.INTERNAL_MEDICINE,
                ),
                conditions=(
                    "Heparin-induced thrombocytopenia",
                    "HIT",
                    "Thrombocytopenia",
                    "Thrombosis",
                    "Heparin allergy",
                    "DVT",
                    "PE",
                ),
                clinical_contexts=(
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.TREATMENT_DECISION,
                ),
                clinical_questions=(
                    "Does this patient have HIT?",
                    "Should I stop heparin?",
                    "What is the 4Ts score?",
                    "Should I send a HIT panel?",
                ),
                icd10_codes=("D75.82", "T80.89"),
                keywords=(
                    "4Ts",
                    "HIT",
                    "heparin-induced thrombocytopenia",
                    "thrombocytopenia",
                    "heparin",
                    "PF4",
                    "platelet factor 4",
                    "thrombosis",
                ),
            ),
            references=self._get_references(),
        )

    def _get_references(self) -> tuple[Reference, ...]:
        return (
            Reference(
                citation="Lo GK, Juhl D, Warkentin TE, et al. Evaluation of pretest clinical score (4 T's) for the diagnosis of heparin-induced thrombocytopenia in two clinical settings. J Thromb Haemost. 2006;4(4):759-765.",
                doi="10.1111/j.1538-7836.2006.01787.x",
                pmid="16634744",
                year=2006,
            ),
            Reference(
                citation="Cuker A, Gimotty PA, Crowther MA, Warkentin TE. Predictive value of the 4Ts scoring system for heparin-induced thrombocytopenia: a systematic review and meta-analysis. Blood. 2012;120(20):4160-4167.",
                doi="10.1182/blood-2012-07-443051",
                pmid="22990018",
                year=2012,
            ),
        )

    def calculate(
        self,
        thrombocytopenia: Literal[0, 1, 2],
        timing: Literal[0, 1, 2],
        thrombosis: Literal[0, 1, 2],
        other_causes: Literal[0, 1, 2],
    ) -> ScoreResult:
        """
        Calculate 4Ts score.

        Args:
            thrombocytopenia: Platelet fall (0-2)
                2: >50% fall AND nadir ≥20,000
                1: 30-50% fall OR nadir 10,000-19,000
                0: <30% fall OR nadir <10,000

            timing: Timing of platelet fall (0-2)
                2: Days 5-10 OR ≤1 day if prior heparin exposure within 30 days
                1: >Day 10 OR timing unclear OR ≤1 day if prior exposure 30-100 days ago
                0: ≤4 days without recent exposure

            thrombosis: New thrombosis or skin necrosis (0-2)
                2: New thrombosis, skin necrosis, or acute systemic reaction
                1: Progressive/recurrent thrombosis OR non-necrotizing skin lesions
                0: None

            other_causes: Other causes of thrombocytopenia (0-2)
                2: None apparent (HIT likely)
                1: Possible other cause
                0: Definite other cause

        Returns:
            ScoreResult with 4Ts score and HIT probability
        """
        # Validate inputs
        for name, value in [
            ("thrombocytopenia", thrombocytopenia),
            ("timing", timing),
            ("thrombosis", thrombosis),
            ("other_causes", other_causes),
        ]:
            if value not in (0, 1, 2):
                raise ValueError(f"{name} must be 0, 1, or 2, got {value}")

        # Calculate total score
        total_score = thrombocytopenia + timing + thrombosis + other_causes

        # Generate interpretation
        interpretation = self._interpret_4ts(total_score, thrombosis)

        # Build calculation details
        details = {
            "Thrombocytopenia": self._describe_thrombocytopenia(thrombocytopenia),
            "Timing": self._describe_timing(timing),
            "Thrombosis": self._describe_thrombosis(thrombosis),
            "Other_causes": self._describe_other_causes(other_causes),
            "Total_4Ts_score": f"{total_score}/8",
        }

        return ScoreResult(
            value=total_score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self._get_references()),
            tool_id=self.tool_id,
            tool_name=self.metadata.name,
            raw_inputs={
                "thrombocytopenia": thrombocytopenia,
                "timing": timing,
                "thrombosis": thrombosis,
                "other_causes": other_causes,
            },
            calculation_details=details,
            formula_used="4Ts = Thrombocytopenia + Timing + Thrombosis + oTher causes",
        )

    def _describe_thrombocytopenia(self, score: int) -> str:
        descriptions = {
            2: "2 points: >50% fall AND nadir ≥20K",
            1: "1 point: 30-50% fall OR nadir 10-19K",
            0: "0 points: <30% fall OR nadir <10K",
        }
        return descriptions.get(score, str(score))

    def _describe_timing(self, score: int) -> str:
        descriptions = {
            2: "2 points: Days 5-10 (or ≤1 day with recent exposure)",
            1: "1 point: >Day 10 or timing unclear",
            0: "0 points: ≤Day 4 without recent exposure",
        }
        return descriptions.get(score, str(score))

    def _describe_thrombosis(self, score: int) -> str:
        descriptions = {
            2: "2 points: New thrombosis/skin necrosis/systemic reaction",
            1: "1 point: Progressive/recurrent thrombosis",
            0: "0 points: None",
        }
        return descriptions.get(score, str(score))

    def _describe_other_causes(self, score: int) -> str:
        descriptions = {
            2: "2 points: No other cause apparent",
            1: "1 point: Possible other cause",
            0: "0 points: Definite other cause",
        }
        return descriptions.get(score, str(score))

    def _interpret_4ts(
        self,
        score: int,
        thrombosis: int,
    ) -> Interpretation:
        """Generate interpretation and recommendations."""

        recommendations: tuple[str, ...]
        if score <= 3:
            probability = "Low (≤5%)"
            severity = Severity.MILD
            risk_level = RiskLevel.LOW
            detail = "Low pretest probability. Negative predictive value ~99.8%. HIT testing generally not needed."
            recommendations = (
                "HIT is unlikely - continue heparin if clinically indicated",
                "HIT antibody testing generally NOT indicated (high NPV)",
                "Monitor platelet counts per standard protocol",
                "Re-evaluate if clinical picture changes",
            )
        elif score <= 5:
            probability = "Intermediate (10-30%)"
            severity = Severity.MODERATE
            risk_level = RiskLevel.INTERMEDIATE
            detail = "Intermediate pretest probability. Send confirmatory HIT testing."
            recommendations = (
                "⚠️ Send HIT antibody testing (immunoassay)",
                "Consider stopping heparin and switching to non-heparin anticoagulant",
                "If immunoassay negative with OD <0.4, HIT unlikely",
                "If immunoassay positive, send serotonin release assay (SRA)",
                "Non-heparin alternatives: argatroban, bivalirudin, fondaparinux",
            )
        else:  # 6-8
            probability = "High (40-80%)"
            severity = Severity.SEVERE
            risk_level = RiskLevel.HIGH
            detail = "High pretest probability. Treat as HIT until proven otherwise."
            recommendations = (
                "🚨 STOP ALL HEPARIN immediately (including flushes, coated catheters)",
                "Start non-heparin anticoagulant NOW (argatroban, bivalirudin)",
                "Send HIT antibody testing for confirmation",
                "Do NOT give platelet transfusions unless life-threatening bleeding",
                "Do NOT give warfarin until platelets recover (risk of limb gangrene)",
                "Screen for thrombosis with Doppler ultrasound of extremities",
            )

        summary = f"4Ts Score {score}/8: {probability} probability of HIT"

        warnings = []
        if score >= 4:
            warnings.append("⚠️ Intermediate/High probability: Consider stopping heparin")
        if thrombosis == 2:
            warnings.append("⚠️ New thrombosis present - high risk of additional events")
        if score >= 6:
            warnings.append("🚨 HIGH probability: Treat as HIT pending lab confirmation")

        return Interpretation(
            summary=summary,
            detail=detail,
            severity=severity,
            risk_level=risk_level,
            recommendations=recommendations,
            warnings=tuple(warnings),
            next_steps=(
                "Review all sources of heparin (IV, flushes, coated lines)",
                "Check baseline and serial platelet counts",
                "Consider HIT panel (immunoassay ± SRA)",
                "Document heparin allergy if confirmed",
            ),
        )
