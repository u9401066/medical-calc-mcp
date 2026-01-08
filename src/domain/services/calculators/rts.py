"""
Revised Trauma Score (RTS) Calculator

生理性創傷評分系統，用於院前和急診創傷分流。
結合 GCS、收縮壓和呼吸速率評估生理功能。

References:
- Champion HR, et al. J Trauma. 1989;29(5):623-629. PMID: 2657085
"""

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, RiskLevel, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class RevisedTraumaScoreCalculator(BaseCalculator):
    """
    Revised Trauma Score (RTS) Calculator

    生理性創傷嚴重度評估，用於院前分流和預後預測。

    三項生理參數:
    - Glasgow Coma Scale (GCS)
    - Systolic Blood Pressure (SBP)
    - Respiratory Rate (RR)

    評分範圍: 0-7.8408 (weighted) 或 0-12 (coded)
    """

    # Coded values for each parameter
    GCS_CODE = {
        (13, 15): 4,
        (9, 12): 3,
        (6, 8): 2,
        (4, 5): 1,
        (3, 3): 0,
    }

    SBP_CODE = {
        (90, 999): 4,  # >89
        (76, 89): 3,
        (50, 75): 2,
        (1, 49): 1,
        (0, 0): 0,
    }

    RR_CODE = {
        (10, 29): 4,
        (30, 999): 3,  # >29
        (6, 9): 2,
        (1, 5): 1,
        (0, 0): 0,
    }

    # Weights for TRISS calculation (from Champion 1989)
    WEIGHTS = {
        "gcs": 0.9368,
        "sbp": 0.7326,
        "rr": 0.2908,
    }

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="rts",
                name="Revised Trauma Score (RTS)",
                purpose="Physiologic trauma severity scoring for triage and prognosis",
                input_params=["gcs", "systolic_bp", "respiratory_rate"],
                output_type="RTS (0-7.84 weighted, 0-12 coded) with survival probability",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.SURGERY,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.CRITICAL_CARE,
                    Specialty.TRAUMA,
                ),
                conditions=("Trauma", "Polytrauma", "Multiple Injuries", "Blunt Trauma", "Penetrating Trauma", "Triage"),
                clinical_contexts=(
                    ClinicalContext.EMERGENCY,
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.DISPOSITION,
                    ClinicalContext.RISK_STRATIFICATION,
                ),
                clinical_questions=(
                    "What is the physiologic trauma severity?",
                    "Should this trauma patient go to a Level I center?",
                    "What is the survival probability based on physiology?",
                    "Does this patient need immediate intervention?",
                ),
                icd10_codes=("T07", "T14.90"),
                keywords=("RTS", "Revised Trauma Score", "trauma triage", "physiologic scoring", "trauma severity", "GCS", "prehospital", "trauma center"),
            ),
            references=(
                Reference(
                    citation="Champion HR, Sacco WJ, Copes WS, et al. A revision of the Trauma Score. J Trauma. 1989;29(5):623-629.",
                    doi="10.1097/00005373-198905000-00017",
                    pmid="2657085",
                    year=1989,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def _get_coded_value(self, value: int | float, code_table: dict[tuple[int, int], int]) -> int:
        """Get coded value from lookup table."""
        for (low, high), code in code_table.items():
            if low <= value <= high:
                return code
        return 0

    def calculate(
        self,
        gcs: int,
        systolic_bp: int,
        respiratory_rate: int,
    ) -> ScoreResult:
        """
        Calculate Revised Trauma Score

        Args:
            gcs: Glasgow Coma Scale (3-15)
            systolic_bp: Systolic blood pressure (mmHg), 0 if absent
            respiratory_rate: Respiratory rate (breaths/min), 0 if absent

        Returns:
            ScoreResult with RTS scores and survival estimate
        """
        # Validate inputs
        if not 3 <= gcs <= 15:
            raise ValueError("GCS must be between 3-15")
        if systolic_bp < 0:
            raise ValueError("Systolic BP cannot be negative")
        if respiratory_rate < 0:
            raise ValueError("Respiratory rate cannot be negative")

        # Get coded values
        gcs_code = self._get_coded_value(gcs, self.GCS_CODE)
        sbp_code = self._get_coded_value(systolic_bp, self.SBP_CODE)
        rr_code = self._get_coded_value(respiratory_rate, self.RR_CODE)

        # Calculate T-RTS (for triage, simple sum)
        t_rts = gcs_code + sbp_code + rr_code

        # Calculate RTS (weighted, for TRISS)
        rts_weighted = self.WEIGHTS["gcs"] * gcs_code + self.WEIGHTS["sbp"] * sbp_code + self.WEIGHTS["rr"] * rr_code

        components = [
            f"GCS {gcs} → code {gcs_code} (×0.9368 = {gcs_code * self.WEIGHTS['gcs']:.3f})",
            f"SBP {systolic_bp} → code {sbp_code} (×0.7326 = {sbp_code * self.WEIGHTS['sbp']:.3f})",
            f"RR {respiratory_rate} → code {rr_code} (×0.2908 = {rr_code * self.WEIGHTS['rr']:.3f})",
        ]

        # Survival probability estimate (approximate from Champion 1989)
        # Note: Actual survival requires TRISS with ISS
        if t_rts == 12:
            survival_est = ">97%"
            risk_level = RiskLevel.VERY_LOW
            severity = Severity.NORMAL
        elif t_rts >= 10:
            survival_est = "~90-97%"
            risk_level = RiskLevel.LOW
            severity = Severity.MILD
        elif t_rts >= 7:
            survival_est = "~60-90%"
            risk_level = RiskLevel.INTERMEDIATE
            severity = Severity.MODERATE
        elif t_rts >= 4:
            survival_est = "~30-60%"
            risk_level = RiskLevel.HIGH
            severity = Severity.SEVERE
        else:
            survival_est = "<30%"
            risk_level = RiskLevel.VERY_HIGH
            severity = Severity.CRITICAL

        # Triage decision
        if t_rts < 11:
            triage = "Consider Level I/II Trauma Center"
        else:
            triage = "May be appropriate for lower-level facility"

        interpretation = Interpretation(
            summary=f"RTS {rts_weighted:.2f} (T-RTS {t_rts}/12): {risk_level.value}",
            detail=(
                f"Revised Trauma Score based on GCS, SBP, and RR. "
                f"T-RTS (triage) = {t_rts}/12, RTS (weighted) = {rts_weighted:.4f}/7.84. "
                f"Estimated survival probability: {survival_est}."
            ),
            severity=severity,
            risk_level=risk_level,
            stage=f"T-RTS {t_rts}",
            stage_description=survival_est,
            recommendations=(
                triage,
                "Use with ISS for TRISS calculation for better prognosis",
            ),
            next_steps=(
                "Calculate ISS for anatomic injury assessment",
                "Use TRISS for combined physiologic-anatomic prediction",
            ),
        )

        return ScoreResult(
            value=round(rts_weighted, 4),
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.metadata.references),
            tool_id=self.metadata.low_level.tool_id,
            tool_name=self.metadata.low_level.name,
            raw_inputs={
                "gcs": gcs,
                "systolic_bp": systolic_bp,
                "respiratory_rate": respiratory_rate,
            },
            calculation_details={
                "score_name": "Revised Trauma Score (RTS)",
                "t_rts": t_rts,
                "t_rts_range": "0-12",
                "rts_weighted": round(rts_weighted, 4),
                "rts_weighted_range": "0-7.8408",
                "gcs_code": gcs_code,
                "sbp_code": sbp_code,
                "rr_code": rr_code,
                "components": components,
                "survival_estimate": survival_est,
                "triage_recommendation": triage,
            },
            formula_used="RTS = 0.9368×GCS_code + 0.7326×SBP_code + 0.2908×RR_code",
            notes=[
                "T-RTS <11 suggests need for Level I/II Trauma Center",
                "RTS weighted version used in TRISS calculation",
                "For definitive prognosis, combine with ISS using TRISS",
            ],
        )
