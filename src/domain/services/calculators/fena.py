"""
Fractional Excretion of Sodium (FENa) Calculator

Calculates the fractional excretion of sodium to help differentiate
prerenal azotemia from acute tubular necrosis (ATN) in oliguric patients.

Original Reference:
    Espinel CH. The FENa test. Use in the differential diagnosis of acute
    renal failure. JAMA. 1976;236(6):579-581.
    doi:10.1001/jama.1976.03270060025021. PMID: 947239.

Validation Reference:
    Miller TR, Anderson RJ, Linas SL, et al. Urinary diagnostic indices in
    acute renal failure: a prospective study. Ann Intern Med. 1978;89(1):47-50.
    doi:10.7326/0003-4819-89-1-47. PMID: 666184.
"""

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


class FENaCalculator(BaseCalculator):
    """
    Fractional Excretion of Sodium (FENa) Calculator

    FENa measures the percentage of filtered sodium that is excreted in the urine.
    It helps distinguish prerenal azotemia (where the kidney is sodium-avid)
    from intrinsic renal causes like ATN (where tubular sodium reabsorption is impaired).

    Formula:
        FENa (%) = (Urine Na × Plasma Cr) / (Plasma Na × Urine Cr) × 100

    Interpretation:
        - FENa < 1%: Prerenal azotemia (sodium-avid kidney)
        - FENa 1-2%: Indeterminate
        - FENa > 2%: Intrinsic renal disease (ATN or other intrinsic causes)

    Limitations:
        - Diuretics increase FENa regardless of underlying etiology
        - May be low (<1%) in: contrast nephropathy, rhabdomyolysis, early obstruction,
          acute glomerulonephritis, sepsis, hepatorenal syndrome
        - FEUrea is preferred if patient is on diuretics
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="fena",
                name="Fractional Excretion of Sodium (FENa)",
                purpose="Differentiate prerenal azotemia from acute tubular necrosis",
                input_params=[
                    "urine_sodium",
                    "plasma_sodium",
                    "urine_creatinine",
                    "plasma_creatinine",
                ],
                output_type="FENa percentage with interpretation",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.NEPHROLOGY,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.CRITICAL_CARE,
                    Specialty.EMERGENCY_MEDICINE,
                ),
                conditions=(
                    "acute kidney injury",
                    "prerenal azotemia",
                    "acute tubular necrosis",
                    "ATN",
                    "AKI",
                    "oliguria",
                    "renal failure",
                    "azotemia",
                ),
                clinical_contexts=(
                    ClinicalContext.DIFFERENTIAL_DIAGNOSIS,
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.MONITORING,
                    ClinicalContext.SEVERITY_ASSESSMENT,
                ),
                clinical_questions=(
                    "Is this AKI prerenal or intrinsic?",
                    "Does this patient have prerenal azotemia or ATN?",
                    "What is the cause of this patient's acute kidney injury?",
                    "Is the kidney responding appropriately to hypovolemia?",
                    "Should I give fluid or consider dialysis?",
                ),
                icd10_codes=(
                    "N17.0",  # Acute kidney failure with tubular necrosis
                    "N17.1",  # Acute kidney failure with acute cortical necrosis
                    "N17.2",  # Acute kidney failure with medullary necrosis
                    "N17.8",  # Other acute kidney failure
                    "N17.9",  # Acute kidney failure, unspecified
                    "R34",  # Anuria and oliguria
                ),
                keywords=(
                    "FENa",
                    "fractional excretion",
                    "sodium excretion",
                    "prerenal",
                    "ATN",
                    "acute tubular necrosis",
                    "AKI",
                    "acute kidney injury",
                    "oliguria",
                    "azotemia",
                    "renal failure",
                    "urinary sodium",
                ),
            ),
            references=(
                Reference(
                    citation="Espinel CH. The FENa test. Use in the differential diagnosis of "
                    "acute renal failure. JAMA. 1976;236(6):579-581.",
                    doi="10.1001/jama.1976.03270060025021",
                    pmid="947239",
                    year=1976,
                ),
                Reference(
                    citation="Miller TR, Anderson RJ, Linas SL, et al. Urinary diagnostic indices "
                    "in acute renal failure: a prospective study. Ann Intern Med. 1978;89(1):47-50.",
                    doi="10.7326/0003-4819-89-1-47",
                    pmid="666184",
                    year=1978,
                ),
            ),
            version="1976",
            validation_status="validated",
        )

    def calculate(
        self,
        urine_sodium: float,
        plasma_sodium: float,
        urine_creatinine: float,
        plasma_creatinine: float,
        on_diuretics: bool = False,
    ) -> ScoreResult:
        """
        Calculate Fractional Excretion of Sodium (FENa).

        Args:
            urine_sodium: Urine sodium concentration (mEq/L or mmol/L)
                         Normal range: 40-220 mEq/L (varies with intake)
            plasma_sodium: Plasma/serum sodium concentration (mEq/L or mmol/L)
                          Normal range: 136-145 mEq/L
            urine_creatinine: Urine creatinine concentration (mg/dL)
                             Note: Units must match plasma_creatinine
            plasma_creatinine: Plasma/serum creatinine concentration (mg/dL)
                              Normal range: 0.6-1.2 mg/dL
            on_diuretics: Whether patient is currently on diuretics
                         (affects interpretation reliability)

        Returns:
            ScoreResult with FENa percentage and clinical interpretation

        Raises:
            ValueError: If any input is out of physiological range

        Note:
            FENa = (urine_sodium × plasma_creatinine) /
                   (plasma_sodium × urine_creatinine) × 100
        """
        # Validate inputs
        if urine_sodium < 0 or urine_sodium > 300:
            raise ValueError("Urine sodium must be between 0 and 300 mEq/L")
        if plasma_sodium < 100 or plasma_sodium > 180:
            raise ValueError("Plasma sodium must be between 100 and 180 mEq/L")
        if urine_creatinine <= 0 or urine_creatinine > 500:
            raise ValueError(
                "Urine creatinine must be between 0 and 500 mg/dL"
            )
        if plasma_creatinine <= 0 or plasma_creatinine > 30:
            raise ValueError(
                "Plasma creatinine must be between 0 and 30 mg/dL"
            )

        # Calculate FENa
        # FENa (%) = (Urine Na × Plasma Cr) / (Plasma Na × Urine Cr) × 100
        fena = (urine_sodium * plasma_creatinine) / (plasma_sodium * urine_creatinine) * 100

        # Round to 2 decimal places
        fena = round(fena, 2)

        # Get interpretation
        interpretation = self._interpret_fena(fena, on_diuretics)

        # Build calculation details
        calculation_details = {
            "formula": "FENa = (UNa × PCr) / (PNa × UCr) × 100",
            "numerator": f"{urine_sodium} × {plasma_creatinine} = {urine_sodium * plasma_creatinine:.2f}",
            "denominator": f"{plasma_sodium} × {urine_creatinine} = {plasma_sodium * urine_creatinine:.2f}",
            "fena_percentage": f"{fena:.2f}%",
        }

        if on_diuretics:
            calculation_details["warning"] = "Patient on diuretics - consider FEUrea instead"

        return ScoreResult(
            tool_name=self.low_level_key.name,
            tool_id=self.low_level_key.tool_id,
            value=fena,
            unit=Unit.PERCENT,
            interpretation=interpretation,
            calculation_details=calculation_details,
            references=list(self.references),
            raw_inputs={
                "urine_sodium": urine_sodium,
                "plasma_sodium": plasma_sodium,
                "urine_creatinine": urine_creatinine,
                "plasma_creatinine": plasma_creatinine,
                "on_diuretics": on_diuretics,
            },
            formula_used="FENa (%) = (Urine Na × Plasma Cr) / (Plasma Na × Urine Cr) × 100",
        )

    def _interpret_fena(self, fena: float, on_diuretics: bool) -> Interpretation:
        """Generate clinical interpretation based on FENa value."""

        if on_diuretics:
            # When on diuretics, FENa is less reliable
            return Interpretation(
                summary=f"FENa = {fena:.2f}% (UNRELIABLE - patient on diuretics)",
                detail=f"FENa of {fena:.2f}% was calculated, but the patient is on diuretics which "
                "increase urinary sodium excretion, making FENa unreliable. Consider using "
                "Fractional Excretion of Urea (FEUrea) instead, as urea excretion is less "
                "affected by diuretics.",
                severity=Severity.MILD if fena < 1 else Severity.MODERATE,
                risk_level=RiskLevel.INTERMEDIATE,
                stage="Indeterminate (diuretics)",
                stage_description="FENa unreliable due to diuretic use",
                recommendations=(
                    "Consider FEUrea for more accurate assessment",
                    "FEUrea <35% suggests prerenal etiology, >50% suggests ATN",
                    "Clinical context and volume status assessment remain important",
                    "Review diuretic timing relative to urine collection",
                ),
                warnings=(
                    "Diuretics invalidate FENa interpretation",
                    "Do not rely on this FENa value for clinical decisions",
                ),
                next_steps=(
                    "Calculate FEUrea if urine urea is available",
                    "Assess volume status clinically",
                    "Consider renal ultrasound to rule out obstruction",
                ),
            )

        # Standard interpretation without diuretics
        if fena < 1:
            return Interpretation(
                summary=f"FENa = {fena:.2f}%: Suggests prerenal azotemia",
                detail=f"FENa of {fena:.2f}% (<1%) indicates the kidney is appropriately "
                "conserving sodium, suggesting prerenal azotemia (hypovolemia, decreased "
                "effective circulating volume). The tubular function is intact.",
                severity=Severity.MODERATE,
                risk_level=RiskLevel.INTERMEDIATE,
                stage="Prerenal (<1%)",
                stage_description="Prerenal azotemia - kidney conserving sodium",
                recommendations=(
                    "Identify and treat underlying cause of prerenal state",
                    "Consider volume resuscitation if hypovolemic",
                    "Optimize cardiac output if cardiogenic",
                    "Hold nephrotoxic medications",
                    "Monitor response to fluid challenge",
                ),
                warnings=(
                    "Low FENa can also occur in: contrast nephropathy, rhabdomyolysis, "
                    "early obstruction, acute glomerulonephritis, hepatorenal syndrome",
                    "Clinical correlation is essential",
                ),
                next_steps=(
                    "Assess volume status (JVP, peripheral edema, lung exam)",
                    "Consider fluid challenge if appropriate",
                    "Monitor urine output and creatinine response",
                    "Renal ultrasound if obstruction suspected",
                ),
            )
        elif fena <= 2:
            return Interpretation(
                summary=f"FENa = {fena:.2f}%: Indeterminate zone",
                detail=f"FENa of {fena:.2f}% (1-2%) is in the indeterminate zone. This may "
                "represent early or evolving ATN, partially reversed prerenal state, or "
                "mixed etiology. Clinical context is crucial for interpretation.",
                severity=Severity.MODERATE,
                risk_level=RiskLevel.INTERMEDIATE,
                stage="Indeterminate (1-2%)",
                stage_description="Indeterminate - may be prerenal, ATN, or transition",
                recommendations=(
                    "Use clinical context to guide management",
                    "Consider FEUrea for additional information",
                    "Reassess volume status carefully",
                    "Monitor trend over time",
                    "Avoid nephrotoxins",
                ),
                warnings=(
                    "Indeterminate result - do not rely on FENa alone",
                    "May represent evolving ATN or partially treated prerenal state",
                ),
                next_steps=(
                    "Repeat FENa in 12-24 hours to assess trend",
                    "Calculate FEUrea if available",
                    "Review urinalysis for casts (muddy brown casts suggest ATN)",
                    "Consider nephrology consultation",
                ),
            )
        else:
            return Interpretation(
                summary=f"FENa = {fena:.2f}%: Suggests intrinsic renal disease (ATN)",
                detail=f"FENa of {fena:.2f}% (>2%) indicates impaired tubular sodium "
                "reabsorption, suggesting intrinsic renal disease, most commonly acute "
                "tubular necrosis (ATN). The kidney is unable to conserve sodium normally.",
                severity=Severity.SEVERE,
                risk_level=RiskLevel.HIGH,
                stage="Intrinsic (>2%)",
                stage_description="Intrinsic renal disease - likely ATN",
                recommendations=(
                    "Identify and remove inciting cause (nephrotoxins, ischemia)",
                    "Supportive care - maintain euvolemia",
                    "Avoid further nephrotoxic exposure",
                    "Monitor for complications (hyperkalemia, metabolic acidosis, fluid overload)",
                    "Nephrology consultation recommended",
                ),
                warnings=(
                    "ATN typically requires 1-3 weeks for recovery",
                    "May require dialysis if severe",
                    "Watch for hyperkalemia, acidosis, and volume overload",
                ),
                next_steps=(
                    "Urinalysis: look for muddy brown granular casts",
                    "Review medication list for nephrotoxins",
                    "Daily creatinine and electrolyte monitoring",
                    "Consider renal replacement therapy if indicated",
                    "Assess for dialysis indications (AEIOU)",
                ),
            )
