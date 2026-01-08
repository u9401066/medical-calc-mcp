"""
TRISS (Trauma and Injury Severity Score) Calculator

結合生理評分 (RTS) 和解剖評分 (ISS) 的創傷存活預測模型。
是創傷照護品質評估的國際標準。

References:
- Boyd CR, et al. J Trauma. 1987;27(4):370-378. PMID: 3106646
- Champion HR, et al. J Trauma. 1990;30(11):1356-1365.
"""

import math

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, RiskLevel, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class TRISSCalculator(BaseCalculator):
    """
    TRISS (Trauma and Injury Severity Score) Calculator

    計算創傷患者的存活機率，結合：
    - RTS (Revised Trauma Score) - 生理評估
    - ISS (Injury Severity Score) - 解剖評估
    - Age - 年齡修正
    - Injury type - 鈍傷 vs 穿刺傷

    輸出: 存活機率 Ps (0-100%)
    """

    # TRISS coefficients (MTOS database)
    # Format: (b0, b1_rts, b2_iss, b3_age)
    COEFFICIENTS = {
        "blunt": (-0.4499, 0.8085, -0.0835, -1.7430),
        "penetrating": (-2.5355, 0.9934, -0.0651, -1.1360),
    }

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="triss",
                name="TRISS (Trauma and Injury Severity Score)",
                purpose="Calculate trauma survival probability combining RTS and ISS",
                input_params=["rts", "iss", "age", "injury_type", "gcs", "systolic_bp", "respiratory_rate"],
                output_type="Survival probability (Ps) 0-100%",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.SURGERY,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.CRITICAL_CARE,
                    Specialty.TRAUMA,
                ),
                conditions=("Trauma", "Polytrauma", "Multiple Injuries", "Blunt Trauma", "Penetrating Trauma"),
                clinical_contexts=(
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.QUALITY_IMPROVEMENT,
                    ClinicalContext.RISK_STRATIFICATION,
                ),
                clinical_questions=(
                    "What is the survival probability for this trauma patient?",
                    "Is this patient outcome expected or unexpected?",
                    "How does this outcome compare to predicted?",
                    "What is the TRISS score for quality benchmarking?",
                ),
                icd10_codes=("T07", "T14.90"),
                keywords=("TRISS", "trauma survival", "ISS", "RTS", "survival probability", "trauma prognosis", "Major Trauma Outcome Study", "MTOS"),
            ),
            references=(
                Reference(
                    citation="Boyd CR, Tolson MA, Copes WS. Evaluating trauma care: the TRISS method. J Trauma. 1987;27(4):370-378.", pmid="3106646", year=1987
                ),
                Reference(
                    citation="Champion HR, Copes WS, Sacco WJ, et al. The Major Trauma Outcome Study: establishing national norms for trauma care. J Trauma. 1990;30(11):1356-1365.",
                    pmid="2231804",
                    year=1990,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def _calculate_rts(self, gcs: int, systolic_bp: int, respiratory_rate: int) -> float:
        """Calculate RTS from components if not provided directly."""
        # Coded values
        gcs_codes = [(13, 15, 4), (9, 12, 3), (6, 8, 2), (4, 5, 1), (3, 3, 0)]
        sbp_codes = [(90, 999, 4), (76, 89, 3), (50, 75, 2), (1, 49, 1), (0, 0, 0)]
        rr_codes = [(10, 29, 4), (30, 999, 3), (6, 9, 2), (1, 5, 1), (0, 0, 0)]

        def get_code(value: int, table: list[tuple[int, int, int]]) -> int:
            for low, high, code in table:
                if low <= value <= high:
                    return code
            return 0

        gcs_code = get_code(gcs, gcs_codes)
        sbp_code = get_code(systolic_bp, sbp_codes)
        rr_code = get_code(respiratory_rate, rr_codes)

        return 0.9368 * gcs_code + 0.7326 * sbp_code + 0.2908 * rr_code

    def calculate(
        self,
        iss: int,
        age: int,
        injury_type: str,
        rts: float | None = None,
        gcs: int | None = None,
        systolic_bp: int | None = None,
        respiratory_rate: int | None = None,
    ) -> ScoreResult:
        """
        Calculate TRISS survival probability.

        Args:
            iss: Injury Severity Score (1-75)
            age: Patient age in years
            injury_type: "blunt" or "penetrating"
            rts: Revised Trauma Score (weighted, 0-7.84). If not provided,
                 will calculate from gcs, systolic_bp, respiratory_rate
            gcs: Glasgow Coma Scale (3-15) - required if rts not provided
            systolic_bp: Systolic BP (mmHg) - required if rts not provided
            respiratory_rate: Respiratory rate - required if rts not provided

        Returns:
            ScoreResult with survival probability (Ps)
        """
        # Validate inputs
        if not 1 <= iss <= 75:
            raise ValueError("ISS must be between 1-75")
        if age < 0:
            raise ValueError("Age cannot be negative")

        injury_type_lower = injury_type.lower()
        if injury_type_lower not in ["blunt", "penetrating"]:
            raise ValueError("injury_type must be 'blunt' or 'penetrating'")

        # Get or calculate RTS
        if rts is not None:
            rts_value = rts
            rts_source = "provided"
        elif gcs is not None and systolic_bp is not None and respiratory_rate is not None:
            rts_value = self._calculate_rts(gcs, systolic_bp, respiratory_rate)
            rts_source = "calculated"
        else:
            raise ValueError("Either 'rts' or all of (gcs, systolic_bp, respiratory_rate) must be provided")

        # Age coefficient (0 if <55, 1 if ≥55)
        age_coef = 1 if age >= 55 else 0

        # Get coefficients for injury type
        b0, b1, b2, b3 = self.COEFFICIENTS[injury_type_lower]

        # Calculate b (logit)
        b = b0 + b1 * rts_value + b2 * iss + b3 * age_coef

        # Calculate survival probability
        ps = 1 / (1 + math.exp(-b))
        ps_percent = ps * 100

        # Components breakdown
        components = [
            f"b0 (intercept) = {b0}",
            f"b1 × RTS = {b1} × {rts_value:.4f} = {b1 * rts_value:.4f}",
            f"b2 × ISS = {b2} × {iss} = {b2 * iss:.4f}",
            f"b3 × Age = {b3} × {age_coef} = {b3 * age_coef:.4f}",
            f"b (logit) = {b:.4f}",
            f"Ps = 1/(1+e^(-b)) = {ps:.4f} = {ps_percent:.1f}%",
        ]

        # Interpretation
        if ps_percent >= 90:
            risk_level = RiskLevel.VERY_LOW
            severity = Severity.NORMAL
            outcome = "Expected survival"
        elif ps_percent >= 75:
            risk_level = RiskLevel.LOW
            severity = Severity.MILD
            outcome = "Favorable prognosis"
        elif ps_percent >= 50:
            risk_level = RiskLevel.INTERMEDIATE
            severity = Severity.MODERATE
            outcome = "Uncertain prognosis"
        elif ps_percent >= 25:
            risk_level = RiskLevel.HIGH
            severity = Severity.SEVERE
            outcome = "Poor prognosis"
        else:
            risk_level = RiskLevel.VERY_HIGH
            severity = Severity.CRITICAL
            outcome = "Very poor prognosis"

        interpretation = Interpretation(
            summary=f"TRISS Ps = {ps_percent:.1f}%: {outcome}",
            detail=(
                f"Predicted survival probability based on RTS ({rts_value:.2f}), "
                f"ISS ({iss}), age ({age}), and injury type ({injury_type}). "
                f"{'Age ≥55 penalty applied.' if age_coef else ''}"
            ),
            severity=severity,
            risk_level=risk_level,
            stage=f"Ps {ps_percent:.0f}%",
            stage_description=outcome,
            recommendations=(
                f"{'High' if ps_percent < 50 else 'Moderate' if ps_percent < 75 else 'Low'} mortality risk - plan care accordingly",
                "Use for quality benchmarking (compare actual vs predicted outcomes)",
            ),
            next_steps=(
                "Document for trauma registry",
                "Compare outcome to prediction for quality assessment",
            ),
        )

        raw_inputs: dict[str, int | float | str | None] = {
            "iss": iss,
            "age": age,
            "injury_type": injury_type,
            "rts": rts,
        }
        if gcs is not None:
            raw_inputs["gcs"] = gcs
            raw_inputs["systolic_bp"] = systolic_bp
            raw_inputs["respiratory_rate"] = respiratory_rate

        return ScoreResult(
            value=round(ps_percent, 1),
            unit=Unit.PERCENT,
            interpretation=interpretation,
            references=list(self.metadata.references),
            tool_id=self.metadata.low_level.tool_id,
            tool_name=self.metadata.low_level.name,
            raw_inputs=raw_inputs,
            calculation_details={
                "score_name": "TRISS (Trauma and Injury Severity Score)",
                "survival_probability_ps": round(ps_percent, 1),
                "survival_probability_decimal": round(ps, 4),
                "rts_value": round(rts_value, 4),
                "rts_source": rts_source,
                "iss": iss,
                "age_coefficient": age_coef,
                "injury_type": injury_type_lower,
                "logit_b": round(b, 4),
                "coefficients_used": self.COEFFICIENTS[injury_type_lower],
                "components": components,
            },
            formula_used="Ps = 1/(1+e^(-b)), b = b0 + b1×RTS + b2×ISS + b3×Age",
            notes=[
                "Based on Major Trauma Outcome Study (MTOS) database",
                "Age coefficient = 0 if <55 years, 1 if ≥55 years",
                "Used for trauma care quality benchmarking (W/M/Z statistics)",
            ],
        )
