"""
Alveolar-arterial (A-a) Oxygen Gradient Calculator

Calculates the difference between alveolar and arterial oxygen partial pressures.
Essential for evaluating hypoxemia etiology and oxygenation efficiency.

References:
    West JB. Respiratory Physiology: The Essentials. 10th ed.
    Lippincott Williams & Wilkins; 2016.

    Kanber GJ, King FW, Eshchar YR, Sharp JT. The alveolar-arterial oxygen
    gradient in young and elderly men during air and oxygen breathing.
    Am Rev Respir Dis. 1968;97(3):376-381.
    DOI: 10.1164/arrd.1968.97.3.376
    PMID: 5638666

    Mellemgaard K. The alveolar-arterial oxygen difference: its size and
    components in normal man. Acta Physiol Scand. 1966;67(1):10-20.
    DOI: 10.1111/j.1748-1716.1966.tb03281.x
    PMID: 5962685
"""

from typing import Optional

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


class AaGradientCalculator(BaseCalculator):
    """
    Alveolar-arterial (A-a) Oxygen Gradient Calculator

    The A-a gradient is the difference between alveolar oxygen tension (PAO₂)
    and arterial oxygen tension (PaO₂). It helps differentiate causes of hypoxemia.

    Formula:
        A-a Gradient = PAO₂ - PaO₂

        Where PAO₂ = (FiO₂ × (Patm - PH₂O)) - (PaCO₂ / RQ)

        Standard values:
            Patm = 760 mmHg (at sea level)
            PH₂O = 47 mmHg (water vapor pressure at 37°C)
            RQ = 0.8 (respiratory quotient)

    Age-adjusted Normal:
        Expected A-a gradient = 2.5 + (0.21 × Age)

        Alternative: (Age / 4) + 4

        Upper limit of normal (on room air):
            < 40 years: < 20 mmHg
            ≥ 40 years: Approximately (Age/4) + 4

    Clinical Interpretation:
        Normal A-a gradient with hypoxemia:
            - Hypoventilation (CNS depression, neuromuscular disease)
            - Low inspired O₂ (high altitude)

        Elevated A-a gradient with hypoxemia:
            - V/Q mismatch (COPD, asthma, PE)
            - Shunt (ARDS, pneumonia, atelectasis, AVM)
            - Diffusion impairment (ILD, pulmonary edema)
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="aa_gradient",
                name="Alveolar-arterial (A-a) Oxygen Gradient",
                purpose="Calculate A-a gradient to evaluate hypoxemia etiology",
                input_params=["pao2", "paco2", "fio2", "age", "atmospheric_pressure"],
                output_type="A-a gradient (mmHg) with interpretation"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.PULMONOLOGY,
                    Specialty.CRITICAL_CARE,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.ANESTHESIOLOGY,
                ),
                conditions=(
                    "Hypoxemia",
                    "Respiratory failure",
                    "ARDS",
                    "Pneumonia",
                    "Pulmonary embolism",
                    "COPD",
                    "Interstitial lung disease",
                    "V/Q mismatch",
                    "Shunt",
                    "Hypoventilation",
                ),
                clinical_contexts=(
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "What is the cause of this patient's hypoxemia?",
                    "Is the A-a gradient elevated?",
                    "Is this hypoventilation or a parenchymal problem?",
                    "Does the patient have a V/Q mismatch or shunt?",
                    "How efficient is the patient's gas exchange?",
                ),
                icd10_codes=("R09.02", "J96.90", "J96.00"),
                keywords=(
                    "A-a gradient", "alveolar-arterial gradient", "PAO2", "PaO2",
                    "hypoxemia", "oxygen gradient", "gas exchange", "respiratory failure",
                    "ABG", "arterial blood gas", "V/Q mismatch", "shunt",
                ),
            ),
            references=self._get_references(),
        )

    def _get_references(self) -> tuple[Reference, ...]:
        return (
            Reference(
                citation="West JB. Respiratory Physiology: The Essentials. 10th ed. Lippincott Williams & Wilkins; 2016.",
                doi=None,
                pmid=None,
                year=2016,
            ),
            Reference(
                citation="Kanber GJ, King FW, Eshchar YR, Sharp JT. The alveolar-arterial oxygen gradient in young and elderly men during air and oxygen breathing. Am Rev Respir Dis. 1968;97(3):376-381.",
                doi="10.1164/arrd.1968.97.3.376",
                pmid="5638666",
                year=1968,
            ),
            Reference(
                citation="Mellemgaard K. The alveolar-arterial oxygen difference: its size and components in normal man. Acta Physiol Scand. 1966;67(1):10-20.",
                doi="10.1111/j.1748-1716.1966.tb03281.x",
                pmid="5962685",
                year=1966,
            ),
        )

    def calculate(
        self,
        pao2: float,
        paco2: float,
        fio2: float,
        age: Optional[int] = None,
        atmospheric_pressure: float = 760.0,
        respiratory_quotient: float = 0.8,
    ) -> ScoreResult:
        """
        Calculate the A-a oxygen gradient.

        Args:
            pao2: Arterial oxygen partial pressure (mmHg)
            paco2: Arterial carbon dioxide partial pressure (mmHg)
            fio2: Fraction of inspired oxygen (0.21-1.0)
            age: Patient age in years (optional, for expected normal calculation)
            atmospheric_pressure: Atmospheric pressure in mmHg (default 760 at sea level)
            respiratory_quotient: RQ value (default 0.8)

        Returns:
            ScoreResult with A-a gradient and interpretation
        """
        # Validate inputs
        if pao2 < 10 or pao2 > 700:
            raise ValueError(f"PaO₂ {pao2} mmHg is outside expected range (10-700 mmHg)")
        if paco2 < 10 or paco2 > 150:
            raise ValueError(f"PaCO₂ {paco2} mmHg is outside expected range (10-150 mmHg)")
        if fio2 < 0.21 or fio2 > 1.0:
            raise ValueError(f"FiO₂ {fio2} is outside valid range (0.21-1.0)")
        if age is not None and (age < 0 or age > 120):
            raise ValueError(f"Age {age} is outside valid range (0-120 years)")

        # Water vapor pressure at 37°C
        ph2o = 47.0

        # Calculate alveolar oxygen tension (PAO₂)
        # PAO₂ = FiO₂ × (Patm - PH₂O) - (PaCO₂ / RQ)
        pao2_alveolar = fio2 * (atmospheric_pressure - ph2o) - (paco2 / respiratory_quotient)

        # Calculate A-a gradient
        aa_gradient = pao2_alveolar - pao2
        aa_gradient = round(aa_gradient, 1)

        # Calculate expected A-a gradient based on age
        if age is not None:
            expected_aa = 2.5 + (0.21 * age)
            expected_aa_alt = (age / 4) + 4
        else:
            expected_aa = None
            expected_aa_alt = None

        # Generate interpretation
        interpretation = self._interpret_aa_gradient(aa_gradient, age, fio2, expected_aa)

        # Build calculation details
        details = {
            "PaO₂": f"{pao2} mmHg",
            "PaCO₂": f"{paco2} mmHg",
            "FiO₂": f"{fio2:.2f} ({fio2 * 100:.0f}%)",
            "PAO₂_calculated": f"{pao2_alveolar:.1f} mmHg",
            "A-a_gradient": f"{aa_gradient:.1f} mmHg",
        }

        if age is not None:
            details["Age"] = f"{age} years"
            details["Expected_A-a_gradient"] = f"{expected_aa:.1f} mmHg"
            details["Upper_limit_normal"] = f"~{expected_aa_alt:.0f} mmHg"

        return ScoreResult(
            value=aa_gradient,
            unit=Unit.MMHG,
            interpretation=interpretation,
            references=list(self._get_references()),
            tool_id=self.tool_id,
            tool_name=self.metadata.name,
            raw_inputs={
                "pao2": pao2,
                "paco2": paco2,
                "fio2": fio2,
                "age": age,
                "atmospheric_pressure": atmospheric_pressure,
                "respiratory_quotient": respiratory_quotient,
            },
            calculation_details=details,
            formula_used="A-a gradient = PAO₂ - PaO₂, where PAO₂ = FiO₂ × (Patm - PH₂O) - (PaCO₂ / RQ)",
        )

    def _interpret_aa_gradient(
        self,
        aa_gradient: float,
        age: Optional[int],
        fio2: float,
        expected_aa: Optional[float]
    ) -> Interpretation:
        """Generate interpretation based on A-a gradient."""
        recommendations: tuple[str, ...]
        warnings: tuple[str, ...]

        # Determine if gradient is elevated
        # On room air, normal is < 15-20 mmHg in young adults
        # Expected = 2.5 + 0.21 × Age

        if age is not None and expected_aa is not None:
            # Use age-adjusted interpretation
            margin = expected_aa * 0.5  # Allow 50% above expected as upper limit
            upper_limit = expected_aa + margin

            if aa_gradient <= expected_aa:
                is_elevated = False
                elevation_status = "normal"
            elif aa_gradient <= upper_limit:
                is_elevated = True
                elevation_status = "mildly elevated"
            elif aa_gradient <= expected_aa * 2:
                is_elevated = True
                elevation_status = "moderately elevated"
            else:
                is_elevated = True
                elevation_status = "markedly elevated"
        else:
            # Use absolute thresholds
            if fio2 <= 0.21:
                # Room air
                if aa_gradient <= 15:
                    is_elevated = False
                    elevation_status = "normal"
                elif aa_gradient <= 25:
                    is_elevated = True
                    elevation_status = "mildly elevated"
                elif aa_gradient <= 40:
                    is_elevated = True
                    elevation_status = "moderately elevated"
                else:
                    is_elevated = True
                    elevation_status = "markedly elevated"
            else:
                # On supplemental O₂, gradient widens
                # A-a gradient increases ~5-7 mmHg for each 10% increase in FiO₂
                adjusted_limit = 15 + (fio2 - 0.21) * 70
                if aa_gradient <= adjusted_limit:
                    is_elevated = False
                    elevation_status = "normal for FiO₂"
                else:
                    is_elevated = True
                    elevation_status = "elevated"

        # Determine severity and recommendations
        if not is_elevated:
            severity = Severity.NORMAL
            risk_level = RiskLevel.VERY_LOW
            summary = f"Normal A-a gradient ({aa_gradient:.1f} mmHg)"
            detail = "Gas exchange is efficient. If hypoxemia is present, consider hypoventilation or low inspired O₂."
            recommendations = (
                "If hypoxemic: check for hypoventilation (CNS, neuromuscular)",
                "Consider high altitude if applicable",
                "Review respiratory mechanics and effort",
            )
            warnings = ()
            ddx_category = "Normal A-a: Hypoventilation or low FiO₂"
        else:
            if elevation_status == "mildly elevated":
                severity = Severity.MILD
                risk_level = RiskLevel.LOW
            elif elevation_status == "moderately elevated":
                severity = Severity.MODERATE
                risk_level = RiskLevel.INTERMEDIATE
            else:
                severity = Severity.SEVERE
                risk_level = RiskLevel.HIGH

            summary = f"Elevated A-a gradient ({aa_gradient:.1f} mmHg) - {elevation_status}"
            detail = "Indicates impaired gas exchange. Consider V/Q mismatch, shunt, or diffusion impairment."

            recommendations = (
                "Evaluate for V/Q mismatch: COPD, asthma, PE",
                "Evaluate for shunt: pneumonia, ARDS, atelectasis, AVM",
                "Evaluate for diffusion impairment: ILD, pulmonary edema",
                "Consider CT chest if etiology unclear",
                "Obtain complete ABG with lactate if not done",
            )

            if severity in (Severity.MODERATE, Severity.SEVERE):
                recommendations = recommendations + (
                    "Consider ICU admission if respiratory failure",
                    "Evaluate need for advanced respiratory support",
                )

            warnings = (
                "Elevated A-a gradient indicates parenchymal lung disease or V/Q abnormality",
            )
            ddx_category = "Elevated A-a: V/Q mismatch, Shunt, or Diffusion defect"

        return Interpretation(
            summary=summary,
            detail=detail,
            severity=severity,
            risk_level=risk_level,
            recommendations=recommendations,
            warnings=warnings,
            next_steps=(
                "Correlate with clinical presentation and imaging",
                "Consider cause-specific workup based on clinical context",
                ddx_category,
            ),
        )
