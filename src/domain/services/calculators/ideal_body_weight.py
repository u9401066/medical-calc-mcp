"""
Ideal Body Weight Calculator

Calculates ideal body weight (IBW) using multiple formulas.
Essential for ventilator tidal volume settings (ARDSNet 6-8 mL/kg IBW).

Reference:
    Devine BJ. Gentamicin therapy. Drug Intell Clin Pharm. 1974;8:650-655.

    ARDS Network. Ventilation with lower tidal volumes as compared with
    traditional tidal volumes for acute lung injury and ARDS.
    N Engl J Med. 2000;342(18):1301-1308.
    DOI: 10.1056/NEJM200005043421801
    PMID: 10793162

    Pai MP, Paloucek FP. The origin of the "ideal" body weight equations.
    Ann Pharmacother. 2000;34(9):1066-1069.
    DOI: 10.1345/aph.19381
    PMID: 10981254
"""

from typing import Literal, Optional

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


class IdealBodyWeightCalculator(BaseCalculator):
    """
    Ideal Body Weight Calculator

    Calculates IBW using the Devine formula (most common) or alternatives.

    Formulas:
        Devine (1974) - Most commonly used:
            Male: IBW = 50 + 2.3 × (height_inches - 60)
            Female: IBW = 45.5 + 2.3 × (height_inches - 60)

        Metric conversion:
            Male: IBW = 50 + 0.91 × (height_cm - 152.4)
            Female: IBW = 45.5 + 0.91 × (height_cm - 152.4)

    Clinical Applications:
        - ARDSNet tidal volume: 6-8 mL/kg IBW
        - Drug dosing (aminoglycosides, chemotherapy)
        - Nutritional assessment
        - Obesity classification (Actual/IBW ratio)

    Adjusted Body Weight (for obesity, when actual > 120% IBW):
        ABW = IBW + 0.4 × (Actual - IBW)
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="ideal_body_weight",
                name="Ideal Body Weight (IBW)",
                purpose="Calculate ideal body weight for ventilator settings and drug dosing",
                input_params=["height_cm", "sex", "actual_weight_kg"],
                output_type="IBW (kg) with adjusted body weight and tidal volume range"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.CRITICAL_CARE,
                    Specialty.PULMONOLOGY,
                    Specialty.ANESTHESIOLOGY,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.INTERNAL_MEDICINE,
                ),
                conditions=(
                    "ARDS",
                    "Acute respiratory distress syndrome",
                    "Mechanical ventilation",
                    "Respiratory failure",
                    "Obesity",
                    "Drug dosing",
                ),
                clinical_contexts=(
                    ClinicalContext.TREATMENT_DECISION,
                    ClinicalContext.DRUG_DOSING,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "What tidal volume should I use for this patient?",
                    "What is the patient's ideal body weight?",
                    "How do I calculate ARDSNet tidal volume?",
                    "Should I use actual or ideal weight for drug dosing?",
                ),
                icd10_codes=("J80", "J96.0", "E66"),
                keywords=(
                    "ideal body weight", "IBW", "tidal volume", "ARDSNet",
                    "lung protective ventilation", "Devine formula", "ABW",
                    "adjusted body weight", "ventilator settings",
                ),
            ),
            references=self._get_references(),
        )

    def _get_references(self) -> tuple[Reference, ...]:
        return (
            Reference(
                citation="ARDS Network. Ventilation with lower tidal volumes as compared with traditional tidal volumes for acute lung injury and ARDS. N Engl J Med. 2000;342(18):1301-1308.",
                doi="10.1056/NEJM200005043421801",
                pmid="10793162",
                year=2000,
            ),
            Reference(
                citation="Devine BJ. Gentamicin therapy. Drug Intell Clin Pharm. 1974;8:650-655.",
                doi=None,
                pmid=None,
                year=1974,
            ),
            Reference(
                citation="Pai MP, Paloucek FP. The origin of the 'ideal' body weight equations. Ann Pharmacother. 2000;34(9):1066-1069.",
                doi="10.1345/aph.19381",
                pmid="10981254",
                year=2000,
            ),
        )

    def calculate(
        self,
        height_cm: float,
        sex: Literal["male", "female"],
        actual_weight_kg: Optional[float] = None,
    ) -> ScoreResult:
        """
        Calculate ideal body weight.

        Args:
            height_cm: Height in centimeters
            sex: Patient sex ('male' or 'female')
            actual_weight_kg: Actual body weight in kg (optional, for ABW calculation)

        Returns:
            ScoreResult with IBW, ABW, and tidal volume recommendations
        """
        # Validate inputs
        if height_cm < 100 or height_cm > 250:
            raise ValueError(f"Height {height_cm} cm is outside expected range (100-250 cm)")
        if sex not in ("male", "female"):
            raise ValueError(f"Sex must be 'male' or 'female', got '{sex}'")
        if actual_weight_kg is not None and (actual_weight_kg < 20 or actual_weight_kg > 500):
            raise ValueError(f"Weight {actual_weight_kg} kg is outside expected range (20-500 kg)")

        # Convert height to inches for Devine formula
        height_inches = height_cm / 2.54

        # Calculate IBW using Devine formula
        if sex == "male":
            ibw = 50 + 2.3 * (height_inches - 60)
        else:  # female
            ibw = 45.5 + 2.3 * (height_inches - 60)

        # Ensure IBW is positive (for very short patients)
        if ibw < 0:
            ibw = 0

        ibw = round(ibw, 1)

        # Calculate adjusted body weight if actual weight provided
        abw = None
        weight_ratio = None
        if actual_weight_kg is not None and ibw > 0:
            weight_ratio = actual_weight_kg / ibw
            # ABW is used when actual weight > 120% IBW
            if weight_ratio > 1.2:
                abw = ibw + 0.4 * (actual_weight_kg - ibw)
                abw = round(abw, 1)

        # Calculate tidal volume range (ARDSNet: 6-8 mL/kg IBW)
        tv_low = round(6 * ibw)
        tv_high = round(8 * ibw)

        # Generate interpretation
        interpretation = self._interpret_ibw(
            ibw, actual_weight_kg, abw, weight_ratio, tv_low, tv_high, sex
        )

        # Build calculation details
        details = {
            "Height": f"{height_cm} cm ({height_inches:.1f} inches)",
            "Sex": sex.capitalize(),
            "Formula": "Devine (1974)",
            "IBW": f"{ibw} kg",
            "Tidal_volume_range": f"{tv_low}-{tv_high} mL (6-8 mL/kg IBW)",
        }

        if actual_weight_kg is not None:
            details["Actual_weight"] = f"{actual_weight_kg} kg"
            details["Actual/IBW_ratio"] = f"{weight_ratio:.1%}" if weight_ratio else "N/A"
            if abw is not None:
                details["Adjusted_body_weight"] = f"{abw} kg (for drug dosing)"

        return ScoreResult(
            value=ibw,
            unit=Unit.KG,
            interpretation=interpretation,
            references=list(self._get_references()),
            tool_id=self.tool_id,
            tool_name=self.metadata.name,
            raw_inputs={
                "height_cm": height_cm,
                "sex": sex,
                "actual_weight_kg": actual_weight_kg,
            },
            calculation_details=details,
            formula_used=f"IBW ({'male' if sex == 'male' else 'female'}) = {50 if sex == 'male' else 45.5} + 2.3 × (height_inches - 60)",
        )

    def _interpret_ibw(
        self,
        ibw: float,
        actual_weight: Optional[float],
        abw: Optional[float],
        weight_ratio: Optional[float],
        tv_low: int,
        tv_high: int,
        sex: str,
    ) -> Interpretation:
        """Generate interpretation and recommendations."""

        summary = f"Ideal Body Weight: {ibw} kg"

        if actual_weight is not None and weight_ratio is not None:
            if weight_ratio > 1.3:
                severity = Severity.MODERATE
                risk_level = RiskLevel.INTERMEDIATE
                weight_status = "significantly above IBW (obese)"
                detail = f"Actual weight is {weight_ratio:.0%} of IBW. Use adjusted body weight (ABW = {abw} kg) for aminoglycosides and some chemotherapy dosing."
            elif weight_ratio > 1.2:
                severity = Severity.MILD
                risk_level = RiskLevel.LOW
                weight_status = "above IBW"
                detail = f"Actual weight is {weight_ratio:.0%} of IBW. Consider adjusted body weight for drug dosing."
            elif weight_ratio < 0.8:
                severity = Severity.MILD
                risk_level = RiskLevel.LOW
                weight_status = "below IBW (underweight)"
                detail = f"Actual weight is {weight_ratio:.0%} of IBW. Consider nutritional assessment."
            else:
                severity = Severity.NORMAL
                risk_level = RiskLevel.LOW
                weight_status = "near IBW"
                detail = f"Actual weight is {weight_ratio:.0%} of IBW, which is within normal range."
            summary = f"IBW: {ibw} kg, Actual: {actual_weight} kg ({weight_status})"
        else:
            severity = Severity.NORMAL
            risk_level = RiskLevel.LOW
            detail = f"IBW calculated using Devine formula for {sex}."

        recommendations = [
            f"ARDSNet tidal volume: {tv_low}-{tv_high} mL (6-8 mL/kg IBW)",
            "Use IBW for ventilator settings, not actual body weight",
            "Initial tidal volume: 8 mL/kg IBW, reduce to 6 mL/kg if plateau pressure >30 cmH₂O",
        ]

        if abw is not None:
            recommendations.append(f"Adjusted body weight for drug dosing: {abw} kg")
            recommendations.append("Use ABW for aminoglycosides, vancomycin loading")

        warnings = []
        if ibw < 30:
            warnings.append("⚠️ Very low IBW - verify height measurement")

        return Interpretation(
            summary=summary,
            detail=detail,
            severity=severity,
            risk_level=risk_level,
            recommendations=tuple(recommendations),
            warnings=tuple(warnings),
            next_steps=(
                "Set ventilator tidal volume to 6-8 mL/kg IBW",
                "Monitor plateau pressure (target <30 cmH₂O)",
                "Adjust drug doses based on IBW or ABW as appropriate",
            ),
        )
