"""
Calculator DTOs

Data Transfer Objects for calculator operations.
"""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class CalculateRequest:
    """
    Request DTO for calculation.

    Attributes:
        tool_id: The calculator to use
        params: Dictionary of input parameters
    """

    tool_id: str
    params: dict[str, Any]


@dataclass
class ReferenceDTO:
    """Reference information"""

    citation: str
    doi: Optional[str] = None
    pmid: Optional[str] = None
    year: Optional[int] = None


@dataclass
class InterpretationDTO:
    """Interpretation of calculation result"""

    summary: str
    severity: Optional[str] = None
    recommendation: Optional[str] = None
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class CalculateResponse:
    """
    Response DTO for calculation.
    """

    success: bool
    tool_id: str
    score_name: str
    result: Any
    unit: str
    interpretation: Optional[InterpretationDTO] = None
    component_scores: dict[str, Any] = field(default_factory=dict)
    references: list[ReferenceDTO] = field(default_factory=list)
    error: Optional[str] = None
    guidance: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for MCP response"""
        if not self.success:
            error_result: dict[str, Any] = {
                "success": False,
                "error": self.error,
                "tool_id": self.tool_id,
            }
            if self.component_scores:
                error_result["component_scores"] = self.component_scores
            if self.guidance:
                error_result["guidance"] = self.guidance
            return error_result

        success_result: dict[str, Any] = {
            "success": True,
            "tool_id": self.tool_id,
            "score_name": self.score_name,
            "result": self.result,
            "unit": self.unit,
        }

        if self.interpretation:
            interpretation: dict[str, Any] = {
                "summary": self.interpretation.summary,
            }
            if self.interpretation.severity:
                interpretation["severity"] = self.interpretation.severity
            if self.interpretation.recommendation:
                interpretation["recommendation"] = self.interpretation.recommendation
            if self.interpretation.details:
                interpretation["details"] = self.interpretation.details
            success_result["interpretation"] = interpretation

        if self.component_scores:
            success_result["component_scores"] = self.component_scores

        if self.references:
            success_result["references"] = [
                {
                    "citation": r.citation,
                    "doi": r.doi,
                    "pmid": r.pmid,
                    "year": r.year,
                }
                for r in self.references
            ]

        if self.guidance:
            success_result["guidance"] = self.guidance

        return success_result
