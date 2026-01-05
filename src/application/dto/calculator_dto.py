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

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for MCP response"""
        if not self.success:
            return {
                "success": False,
                "error": self.error,
                "tool_id": self.tool_id,
            }

        result: dict[str, Any] = {
            "success": True,
            "tool_id": self.tool_id,
            "score_name": self.score_name,
            "result": self.result,
            "unit": self.unit,
        }

        if self.interpretation:
            result["interpretation"] = {
                "summary": self.interpretation.summary,
            }
            if self.interpretation.severity:
                result["interpretation"]["severity"] = self.interpretation.severity
            if self.interpretation.recommendation:
                result["interpretation"]["recommendation"] = self.interpretation.recommendation
            if self.interpretation.details:
                result["interpretation"]["details"] = self.interpretation.details

        if self.component_scores:
            result["component_scores"] = self.component_scores

        if self.references:
            result["references"] = [
                {
                    "citation": r.citation,
                    "doi": r.doi,
                    "pmid": r.pmid,
                    "year": r.year,
                }
                for r in self.references
            ]

        return result
