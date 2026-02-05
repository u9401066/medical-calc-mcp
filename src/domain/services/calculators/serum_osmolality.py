"""
Serum Osmolality Calculator

Calculates serum osmolality from sodium, glucose, and BUN values.
Used to assess hydration status, osmolar gap, and identify toxic ingestions.

Classic Formula Reference:
    Edelman IS, Leibman J, O'Meara MP, Birkenfeld LW. Interrelations between
    serum sodium concentration, serum osmolarity and total exchangeable sodium,
    total exchangeable potassium and total body water.
    J Clin Invest. 1958;37(9):1236-1256.
    doi:10.1172/JCI103709. PMID: 13575523.

Validation Reference:
    Khajuria A, Krahn J. Osmolality revisited—deriving and validating the
    best formula for calculated osmolality.
    Clin Biochem. 2005;38(6):514-519.
    doi:10.1016/j.clinbiochem.2005.02.006. PMID: 15885229.
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


class SerumOsmolalityCalculator(BaseCalculator):
    """
    Serum Osmolality Calculator

    Calculates the estimated serum osmolality from serum sodium, glucose, and BUN.

    Classic Formula:
        Calculated Serum Osmolality = 2 × Na (mEq/L) + Glucose (mg/dL)/18 + BUN (mg/dL)/2.8

    Alternative formulas:
        - With ethanol: + Ethanol (mg/dL) / 4.6
        - SI units: 2 × Na (mmol/L) + Glucose (mmol/L) + Urea (mmol/L)

    Normal Range: 275-295 mOsm/kg

    Clinical Applications:
        - Assess hydration status
        - Calculate osmolar gap (Measured - Calculated)
        - Identify toxic alcohol ingestions (high osmolar gap)
        - Evaluate hyponatremia etiology
        - Monitor diabetic emergencies (DKA, HHS)

    Osmolar Gap:
        - Normal: <10 mOsm/kg
        - Elevated (>10): Consider toxic alcohols (methanol, ethylene glycol),
          propylene glycol, mannitol, or other unmeasured osmoles
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="serum_osmolality",
                name="Serum Osmolality (Calculated)",
                purpose="Calculate serum osmolality from sodium, glucose, and BUN",
                input_params=[
                    "sodium",
                    "glucose",
                    "bun",
                    "ethanol",
                ],
                output_type="Calculated serum osmolality in mOsm/kg",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.NEPHROLOGY,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.CRITICAL_CARE,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.TOXICOLOGY,
                ),
                conditions=(
                    "hyponatremia",
                    "hypernatremia",
                    "dehydration",
                    "toxic alcohol ingestion",
                    "methanol poisoning",
                    "ethylene glycol poisoning",
                    "diabetic ketoacidosis",
                    "DKA",
                    "hyperosmolar hyperglycemic state",
                    "HHS",
                    "osmolar gap",
                    "altered mental status",
                ),
                clinical_contexts=(
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.DIFFERENTIAL_DIAGNOSIS,
                    ClinicalContext.LABORATORY,
                    ClinicalContext.MONITORING,
                    ClinicalContext.ELECTROLYTE,
                ),
                clinical_questions=(
                    "What is this patient's calculated serum osmolality?",
                    "Is there an osmolar gap?",
                    "Could this patient have toxic alcohol ingestion?",
                    "What is causing this patient's altered mental status?",
                    "Is this hyponatremia hypo- or hyperosmolar?",
                ),
                icd10_codes=(
                    "E87.0",  # Hyperosmolality and hypernatremia
                    "E87.1",  # Hypo-osmolality and hyponatremia
                    "E87.8",  # Other disorders of electrolyte and fluid balance
                    "T51.0X1A",  # Toxic effect of ethanol
                    "T51.1X1A",  # Toxic effect of methanol
                ),
                keywords=(
                    "osmolality",
                    "osmolarity",
                    "calculated osmolality",
                    "serum osmolality",
                    "osmolar gap",
                    "osm gap",
                    "sodium",
                    "glucose",
                    "BUN",
                    "toxic alcohol",
                    "methanol",
                    "ethylene glycol",
                    "hyponatremia",
                    "hypernatremia",
                ),
            ),
            references=(
                Reference(
                    citation="Edelman IS, Leibman J, O'Meara MP, Birkenfeld LW. Interrelations "
                    "between serum sodium concentration, serum osmolarity and total exchangeable "
                    "sodium, total exchangeable potassium and total body water. "
                    "J Clin Invest. 1958;37(9):1236-1256.",
                    doi="10.1172/JCI103709",
                    pmid="13575523",
                    year=1958,
                ),
                Reference(
                    citation="Khajuria A, Krahn J. Osmolality revisited—deriving and validating "
                    "the best formula for calculated osmolality. "
                    "Clin Biochem. 2005;38(6):514-519.",
                    doi="10.1016/j.clinbiochem.2005.02.006",
                    pmid="15885229",
                    year=2005,
                ),
            ),
            version="Classic formula (1958)",
            validation_status="validated",
        )

    def calculate(
        self,
        sodium: float,
        glucose: float,
        bun: float,
        ethanol: float | None = None,
        measured_osmolality: float | None = None,
    ) -> ScoreResult:
        """
        Calculate serum osmolality.

        Args:
            sodium: Serum sodium in mEq/L (or mmol/L - same units)
                   Normal range: 136-145 mEq/L
            glucose: Serum glucose in mg/dL
                    Normal fasting: 70-100 mg/dL
                    To convert from mmol/L: multiply by 18
            bun: Blood urea nitrogen in mg/dL
                 Normal range: 7-20 mg/dL
                 To convert from urea mmol/L: multiply by 2.8
            ethanol: Serum ethanol in mg/dL (optional)
                     Legal limit ~80 mg/dL (0.08%)
                     To convert from mmol/L: multiply by 4.6
            measured_osmolality: Measured serum osmolality in mOsm/kg (optional)
                                If provided, osmolar gap will be calculated

        Returns:
            ScoreResult with calculated osmolality and interpretation

        Formula:
            Calculated Osmolality = 2×Na + Glucose/18 + BUN/2.8 [+ Ethanol/4.6]

        Raises:
            ValueError: If any input is out of physiological range
        """
        # Validate inputs
        if sodium < 100 or sodium > 180:
            raise ValueError("Sodium must be between 100 and 180 mEq/L")
        if glucose < 0 or glucose > 2000:
            raise ValueError("Glucose must be between 0 and 2000 mg/dL")
        if bun < 0 or bun > 200:
            raise ValueError("BUN must be between 0 and 200 mg/dL")
        if ethanol is not None and (ethanol < 0 or ethanol > 1000):
            raise ValueError("Ethanol must be between 0 and 1000 mg/dL")
        if measured_osmolality is not None and (
            measured_osmolality < 200 or measured_osmolality > 500
        ):
            raise ValueError("Measured osmolality must be between 200 and 500 mOsm/kg")

        # Calculate components
        sodium_contribution = 2 * sodium
        glucose_contribution = glucose / 18
        bun_contribution = bun / 2.8

        # Calculate base osmolality
        calc_osm = sodium_contribution + glucose_contribution + bun_contribution

        # Add ethanol contribution if provided
        ethanol_contribution = 0.0
        if ethanol is not None and ethanol > 0:
            ethanol_contribution = ethanol / 4.6
            calc_osm += ethanol_contribution

        # Round to 1 decimal
        calc_osm = round(calc_osm, 1)

        # Calculate osmolar gap if measured value provided
        osmolar_gap: float | None = None
        if measured_osmolality is not None:
            osmolar_gap = round(measured_osmolality - calc_osm, 1)

        # Build calculation details
        calculation_details: dict[str, float | str | None] = {
            "formula": "2×Na + Glucose/18 + BUN/2.8" + (" + EtOH/4.6" if ethanol else ""),
            "sodium_contribution": round(sodium_contribution, 1),
            "glucose_contribution": round(glucose_contribution, 1),
            "bun_contribution": round(bun_contribution, 1),
        }
        if ethanol is not None:
            calculation_details["ethanol_contribution"] = round(ethanol_contribution, 1)
        if osmolar_gap is not None:
            calculation_details["measured_osmolality"] = measured_osmolality
            calculation_details["osmolar_gap"] = osmolar_gap

        # Generate interpretation
        interpretation = self._interpret_osmolality(
            calc_osm, osmolar_gap, sodium, glucose, ethanol
        )

        return ScoreResult(
            tool_name=self.low_level_key.name,
            tool_id=self.low_level_key.tool_id,
            value=calc_osm,
            unit=Unit.MOSM_KG,
            interpretation=interpretation,
            calculation_details=calculation_details,
            references=list(self.references),
            raw_inputs={
                "sodium": sodium,
                "glucose": glucose,
                "bun": bun,
                "ethanol": ethanol,
                "measured_osmolality": measured_osmolality,
            },
            formula_used="Calculated Osmolality = 2×Na + Glucose/18 + BUN/2.8",
        )

    def _interpret_osmolality(
        self,
        calc_osm: float,
        osmolar_gap: float | None,
        sodium: float,
        glucose: float,
        ethanol: float | None,
    ) -> Interpretation:
        """Generate clinical interpretation based on osmolality."""

        # Determine osmolality status
        if calc_osm < 275:
            osm_status = "hypoosmolar"
            severity = Severity.MODERATE
            risk_level = RiskLevel.INTERMEDIATE
        elif calc_osm <= 295:
            osm_status = "normal"
            severity = Severity.NORMAL
            risk_level = RiskLevel.VERY_LOW
        elif calc_osm <= 320:
            osm_status = "mildly hyperosmolar"
            severity = Severity.MILD
            risk_level = RiskLevel.LOW
        elif calc_osm <= 350:
            osm_status = "moderately hyperosmolar"
            severity = Severity.MODERATE
            risk_level = RiskLevel.INTERMEDIATE
        else:
            osm_status = "severely hyperosmolar"
            severity = Severity.SEVERE
            risk_level = RiskLevel.HIGH

        # Build summary
        summary = f"Calculated serum osmolality: {calc_osm} mOsm/kg ({osm_status})"
        if osmolar_gap is not None:
            summary += f", Osmolar gap: {osmolar_gap} mOsm/kg"

        # Build detail
        detail_parts = [
            f"Calculated serum osmolality is {calc_osm} mOsm/kg (normal: 275-295)."
        ]

        if calc_osm < 275:
            detail_parts.append("This indicates hypoosmolality.")
            if sodium < 136:
                detail_parts.append(
                    "With hyponatremia, this suggests true hypo-osmolar hyponatremia "
                    "(e.g., SIADH, heart failure, cirrhosis, renal failure)."
                )
        elif calc_osm > 295:
            detail_parts.append("This indicates hyperosmolality.")
            if glucose > 250:
                detail_parts.append(
                    "Elevated glucose is contributing to hyperosmolality. "
                    "Consider DKA or HHS."
                )

        # Osmolar gap interpretation
        warnings: list[str] = []
        if osmolar_gap is not None:
            if osmolar_gap < 10:
                detail_parts.append(
                    f"Osmolar gap of {osmolar_gap} mOsm/kg is normal (<10)."
                )
            elif osmolar_gap < 20:
                detail_parts.append(
                    f"Osmolar gap of {osmolar_gap} mOsm/kg is mildly elevated (10-20). "
                    "Consider lactic acidosis, chronic renal failure, or early toxic ingestion."
                )
                severity = max(severity, Severity.MILD, key=lambda x: x.value)
            else:
                detail_parts.append(
                    f"Osmolar gap of {osmolar_gap} mOsm/kg is significantly elevated (>20)."
                )
                warnings.append(
                    "Elevated osmolar gap - consider toxic alcohol ingestion "
                    "(methanol, ethylene glycol), propylene glycol, or other unmeasured osmoles"
                )
                severity = Severity.SEVERE
                risk_level = RiskLevel.HIGH

        detail = " ".join(detail_parts)

        # Recommendations based on findings
        recommendations: list[str] = []
        next_steps: list[str] = []

        if calc_osm < 275:
            recommendations = [
                "Evaluate for causes of hypoosmolality",
                "Check urine osmolality and urine sodium",
                "Assess volume status",
                "Consider SIADH workup if euvolemic",
            ]
            next_steps = [
                "Urine osmolality: >100 suggests impaired water excretion",
                "Urine sodium: >30 mEq/L suggests SIADH or salt-wasting",
                "If symptomatic, consider hypertonic saline",
            ]
        elif calc_osm > 320:
            recommendations = [
                "Aggressive fluid resuscitation if hypovolemic",
                "Identify and treat underlying cause",
                "Monitor sodium correction rate (<10-12 mEq/L per 24h)",
                "Consider ICU admission if severely altered",
            ]
            if glucose > 400:
                next_steps = [
                    "Rule out DKA (ketones, pH, anion gap)",
                    "Rule out HHS (glucose >600, minimal ketosis)",
                    "Insulin therapy after initial fluid bolus",
                ]
            else:
                next_steps = [
                    "Assess for free water deficit",
                    "Consider diabetes insipidus workup",
                ]
        else:
            recommendations = [
                "Normal calculated osmolality",
                "If clinical concern remains, measure serum osmolality directly",
            ]
            next_steps = [
                "Calculate osmolar gap if toxic ingestion suspected",
            ]

        if osmolar_gap is not None and osmolar_gap > 20:
            recommendations = [
                "URGENT: Evaluate for toxic alcohol ingestion",
                "Check serum methanol and ethylene glycol levels",
                "Consider empiric fomepizole if high suspicion",
                "Nephrology and toxicology consultation",
            ]
            next_steps = [
                "Fomepizole 15 mg/kg loading dose if toxic alcohol suspected",
                "Hemodialysis may be needed for severe toxicity",
                "Check acid-base status (high anion gap metabolic acidosis)",
            ]

        return Interpretation(
            summary=summary,
            detail=detail,
            severity=severity,
            risk_level=risk_level,
            stage=f"{calc_osm} mOsm/kg",
            stage_description=osm_status.capitalize(),
            recommendations=tuple(recommendations),
            next_steps=tuple(next_steps),
            warnings=tuple(warnings),
        )
