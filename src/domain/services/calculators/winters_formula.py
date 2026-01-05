"""
Winter's Formula Calculator

Predicts the expected PaCO₂ in metabolic acidosis to assess respiratory compensation.

Reference:
    Albert MS, Dell RB, Winters RW. Quantitative displacement of acid-base
    equilibrium in metabolic acidosis. Ann Intern Med. 1967;66(2):312-322.
    DOI: 10.7326/0003-4819-66-2-312
    PMID: 6016545

    Narins RG, Emmett M. Simple and mixed acid-base disorders: a practical
    approach. Medicine (Baltimore). 1980;59(3):161-187.
    PMID: 6774200
"""


from typing import Any, Optional

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


class WintersFormulaCalculator(BaseCalculator):
    """
    Winter's Formula Calculator

    Predicts the expected PaCO₂ for a given HCO₃⁻ in primary metabolic acidosis.
    Used to determine if respiratory compensation is appropriate or if a
    mixed acid-base disorder exists.

    Formula:
        Expected PaCO₂ = 1.5 × HCO₃⁻ + 8 ± 2

        Or: Expected PaCO₂ = (1.5 × HCO₃⁻) + 8
        Range: ±2 mmHg

    Alternative mnemonic:
        Expected PaCO₂ ≈ Last 2 digits of pH × 100
        (e.g., pH 7.25 → expected PaCO₂ ≈ 25 mmHg)

    Interpretation:
        - Actual PaCO₂ within expected range: Appropriate compensation
        - Actual PaCO₂ > expected upper limit: Concomitant respiratory acidosis
        - Actual PaCO₂ < expected lower limit: Concomitant respiratory alkalosis

    Limitations:
        - Only applicable in primary metabolic acidosis
        - Assumes respiratory system is functioning normally
        - Takes 12-24 hours for full respiratory compensation
        - Not valid if HCO₃⁻ < 6 mEq/L (formula less reliable)
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="winters_formula",
                name="Winter's Formula",
                purpose="Predict expected PaCO₂ in metabolic acidosis",
                input_params=["hco3", "actual_paco2"],
                output_type="Expected PaCO₂ range with compensation assessment"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.CRITICAL_CARE,
                    Specialty.PULMONOLOGY,
                    Specialty.NEPHROLOGY,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.INTERNAL_MEDICINE,
                ),
                conditions=(
                    "Metabolic acidosis",
                    "Mixed acid-base disorder",
                    "Respiratory compensation",
                    "DKA",
                    "Lactic acidosis",
                    "Renal tubular acidosis",
                    "Sepsis",
                ),
                clinical_contexts=(
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.MONITORING,
                    ClinicalContext.SEVERITY_ASSESSMENT,
                ),
                clinical_questions=(
                    "Is respiratory compensation appropriate?",
                    "Is there a mixed acid-base disorder?",
                    "Is there a concurrent respiratory acidosis or alkalosis?",
                    "What should the PaCO₂ be in this metabolic acidosis?",
                ),
                icd10_codes=("E87.2", "R79.89"),
                keywords=(
                    "Winter's formula", "Winters", "expected PaCO2", "respiratory compensation",
                    "metabolic acidosis", "mixed disorder", "ABG", "acid-base",
                ),
            ),
            references=self._get_references(),
        )

    def _get_references(self) -> tuple[Reference, ...]:
        return (
            Reference(
                citation="Albert MS, Dell RB, Winters RW. Quantitative displacement of acid-base equilibrium in metabolic acidosis. Ann Intern Med. 1967;66(2):312-322.",
                doi="10.7326/0003-4819-66-2-312",
                pmid="6016545",
                year=1967,
            ),
            Reference(
                citation="Narins RG, Emmett M. Simple and mixed acid-base disorders: a practical approach. Medicine (Baltimore). 1980;59(3):161-187.",
                doi=None,
                pmid="6774200",
                year=1980,
            ),
        )

    def calculate(
        self,
        hco3: float,
        actual_paco2: Optional[float] = None,
    ) -> ScoreResult:
        """
        Calculate expected PaCO₂ using Winter's formula.

        Args:
            hco3: Serum bicarbonate level (mEq/L)
            actual_paco2: Measured PaCO₂ (mmHg), optional for comparison

        Returns:
            ScoreResult with expected PaCO₂ range and compensation assessment
        """
        # Validate inputs
        if hco3 < 1 or hco3 > 45:
            raise ValueError(f"HCO₃⁻ {hco3} mEq/L is outside expected range (1-45 mEq/L)")
        if actual_paco2 is not None and (actual_paco2 < 10 or actual_paco2 > 120):
            raise ValueError(f"PaCO₂ {actual_paco2} mmHg is outside expected range (10-120 mmHg)")

        # Calculate expected PaCO₂ using Winter's formula
        # Expected PaCO₂ = 1.5 × HCO₃⁻ + 8 ± 2
        expected_paco2 = 1.5 * hco3 + 8
        expected_lower = expected_paco2 - 2
        expected_upper = expected_paco2 + 2

        # Ensure physiological minimum
        if expected_lower < 10:
            expected_lower = 10

        # Generate interpretation
        interpretation = self._interpret_compensation(
            hco3, expected_paco2, expected_lower, expected_upper, actual_paco2
        )

        # Build calculation details
        details = {
            "HCO₃⁻": f"{hco3} mEq/L",
            "Formula": "PaCO₂ = 1.5 × HCO₃⁻ + 8 ± 2",
            "Expected_PaCO₂": f"{expected_paco2:.1f} mmHg",
            "Expected_range": f"{expected_lower:.1f} - {expected_upper:.1f} mmHg",
        }

        if actual_paco2 is not None:
            details["Actual_PaCO₂"] = f"{actual_paco2} mmHg"
            if actual_paco2 < expected_lower:
                details["Difference"] = f"{expected_lower - actual_paco2:.1f} mmHg below expected"
            elif actual_paco2 > expected_upper:
                details["Difference"] = f"{actual_paco2 - expected_upper:.1f} mmHg above expected"
            else:
                details["Difference"] = "Within expected range"

        return ScoreResult(
            value=expected_paco2,
            unit=Unit.MMHG,
            interpretation=interpretation,
            references=list(self._get_references()),
            tool_id=self.tool_id,
            tool_name=self.metadata.name,
            raw_inputs={
                "hco3": hco3,
                "actual_paco2": actual_paco2,
            },
            calculation_details=details,
            formula_used="Expected PaCO₂ = 1.5 × HCO₃⁻ + 8 ± 2",
        )

    def _interpret_compensation(
        self,
        hco3: float,
        expected_paco2: float,
        expected_lower: float,
        expected_upper: float,
        actual_paco2: Optional[float] = None,
    ) -> Interpretation:
        """Generate interpretation based on compensation assessment."""

        # Warning for very low HCO3
        warnings: list[str] = []
        if hco3 < 6:
            warnings.append("⚠️ HCO₃⁻ <6 mEq/L: Winter's formula may be less reliable")

        recommendations: tuple[str, ...]
        if actual_paco2 is None:
            # Only provide expected range
            summary = f"Expected PaCO₂: {expected_lower:.0f}-{expected_upper:.0f} mmHg"
            detail = f"For HCO₃⁻ of {hco3} mEq/L, appropriate respiratory compensation would result in PaCO₂ between {expected_lower:.0f} and {expected_upper:.0f} mmHg."
            severity = Severity.NORMAL
            risk_level = RiskLevel.LOW
            recommendations = (
                "Measure ABG to obtain actual PaCO₂",
                "Compare actual PaCO₂ to expected range",
                "If outside range, consider mixed acid-base disorder",
            )
        else:
            # Compare actual to expected
            if expected_lower <= actual_paco2 <= expected_upper:
                severity = Severity.NORMAL
                risk_level = RiskLevel.LOW
                summary = f"Appropriate respiratory compensation (PaCO₂ {actual_paco2} mmHg within {expected_lower:.0f}-{expected_upper:.0f})"
                detail = "The respiratory compensation is appropriate for this degree of metabolic acidosis. This is a simple (non-mixed) metabolic acidosis."
                recommendations = (
                    "Continue treatment of underlying metabolic acidosis",
                    "Monitor acid-base status",
                    "No additional respiratory disorder present",
                )
            elif actual_paco2 > expected_upper:
                severity = Severity.MODERATE
                risk_level = RiskLevel.INTERMEDIATE
                summary = f"Concurrent RESPIRATORY ACIDOSIS (PaCO₂ {actual_paco2} > expected {expected_upper:.0f} mmHg)"
                detail = "PaCO₂ is higher than expected, indicating inadequate respiratory compensation. This represents a MIXED metabolic acidosis + respiratory acidosis."
                recommendations = (
                    "Evaluate for cause of respiratory acidosis:",
                    "- Respiratory depression (opioids, sedatives)",
                    "- Airway obstruction",
                    "- Neuromuscular weakness",
                    "- COPD exacerbation",
                    "- Fatigue in severe metabolic acidosis",
                    "Consider ventilatory support if severe",
                )
                warnings.append("Mixed acid-base disorder: Metabolic acidosis + Respiratory acidosis")
            else:  # actual_paco2 < expected_lower
                severity = Severity.MILD
                risk_level = RiskLevel.LOW
                summary = f"Concurrent RESPIRATORY ALKALOSIS (PaCO₂ {actual_paco2} < expected {expected_lower:.0f} mmHg)"
                detail = "PaCO₂ is lower than expected, indicating more hyperventilation than needed for compensation. This represents a MIXED metabolic acidosis + respiratory alkalosis."
                recommendations = (
                    "Evaluate for cause of respiratory alkalosis:",
                    "- Pain or anxiety",
                    "- Sepsis (early)",
                    "- Pulmonary embolism",
                    "- Salicylate toxicity (classic mixed pattern)",
                    "- CNS disease",
                    "- Liver failure",
                )
                warnings.append("Mixed acid-base disorder: Metabolic acidosis + Respiratory alkalosis")

        return Interpretation(
            summary=summary,
            detail=detail,
            severity=severity,
            risk_level=risk_level,
            recommendations=recommendations,
            warnings=tuple(warnings),
            next_steps=(
                "Consider delta ratio if high anion gap acidosis",
                "Address underlying cause of metabolic acidosis",
                "Serial ABGs to monitor response to treatment",
            ),
        )
