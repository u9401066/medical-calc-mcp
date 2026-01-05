"""
Score Result Entity

Represents the complete result of a medical calculation.
"""

from dataclasses import dataclass, field
from typing import Any, Optional

from ..value_objects.interpretation import Interpretation
from ..value_objects.reference import Reference
from ..value_objects.units import Unit


@dataclass
class ScoreResult:
    """
    The complete result of a medical score calculation.

    This is the primary output entity from all calculators.
    It contains the calculated value along with full clinical context.

    Attributes:
        value: The calculated numeric result
        unit: Unit of measurement
        interpretation: Clinical interpretation
        references: Original paper citations
        calculation_details: Step-by-step calculation info (optional)
        raw_inputs: The inputs used for calculation
        tool_id: Identifier of the calculator used
        tool_name: Human-readable name of the calculator
    """

    # Core result
    value: Optional[float]
    unit: Unit
    interpretation: Interpretation

    # Attribution
    references: list[Reference] = field(default_factory=list)

    # Metadata
    tool_id: str = ""
    tool_name: str = ""

    # Transparency
    raw_inputs: dict[str, Any] = field(default_factory=dict)
    calculation_details: Optional[dict[str, Any]] = None

    # Additional context
    formula_used: Optional[str] = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API/MCP response"""
        return {
            # Core result
            "value": self.value,
            "unit": str(self.unit),

            # Interpretation
            "interpretation": self.interpretation.to_dict(),

            # Tool info
            "tool_id": self.tool_id,
            "tool_name": self.tool_name,

            # Transparency
            "raw_inputs": self.raw_inputs,
            "calculation_details": self.calculation_details,
            "formula_used": self.formula_used,

            # References
            "references": [ref.to_dict() for ref in self.references],

            # Notes
            "notes": self.notes
        }

    def to_mcp_response(self) -> dict[str, Any]:
        """
        Format for MCP tool response.
        Optimized for AI agent consumption.
        """
        response: dict[str, Any] = {
            # Primary result (what the agent needs most)
            "result": self.value,
            "unit": str(self.unit),
            "summary": self.interpretation.summary,

            # Clinical guidance
            "stage": self.interpretation.stage,
            "severity": self.interpretation.severity.value if self.interpretation.severity else None,
            "risk_level": self.interpretation.risk_level.value if self.interpretation.risk_level else None,

            # Detailed interpretation
            "detail": self.interpretation.detail,
            "recommendations": list(self.interpretation.recommendations) if self.interpretation.recommendations else [],
            "warnings": list(self.interpretation.warnings) if self.interpretation.warnings else [],
            "next_steps": list(self.interpretation.next_steps) if self.interpretation.next_steps else [],

            # Calculation transparency
            "inputs_used": self.raw_inputs,
            "calculation_details": self.calculation_details,
            "formula": self.formula_used,

            # Attribution
            "references": [
                {
                    "citation": ref.citation,
                    "doi": ref.doi,
                    "url": ref.doi_url or ref.pubmed_url or ref.url
                }
                for ref in self.references
            ],

            # Metadata
            "tool_id": self.tool_id,
            "tool_name": self.tool_name
        }

        # Remove None values for cleaner output
        return {k: v for k, v in response.items() if v is not None}
