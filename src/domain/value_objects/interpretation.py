"""
Interpretation Value Object

Represents clinical interpretation of calculation results.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class Severity(Enum):
    """Severity levels for clinical interpretation"""

    NORMAL = "normal"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


class RiskLevel(Enum):
    """Risk stratification levels"""

    VERY_LOW = "very_low"
    LOW = "low"
    INTERMEDIATE = "intermediate"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass(frozen=True)
class Interpretation:
    """
    Clinical interpretation of a calculation result.

    Provides structured clinical meaning of the calculated score/value.
    All interpretation text must be original content.

    Attributes:
        summary: Brief interpretation (1-2 sentences)
        detail: Detailed explanation
        severity: Optional severity classification
        risk_level: Optional risk level classification
        stage: Optional staging (e.g., "CKD Stage 3b")
        stage_description: Description of the stage
        recommendations: Clinical recommendations based on result
        warnings: Important warnings or caveats
        next_steps: Suggested next clinical steps
    """

    summary: str
    detail: Optional[str] = None
    severity: Optional[Severity] = None
    risk_level: Optional[RiskLevel] = None
    stage: Optional[str] = None
    stage_description: Optional[str] = None
    recommendations: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    next_steps: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "detail": self.detail,
            "severity": self.severity.value if self.severity else None,
            "risk_level": self.risk_level.value if self.risk_level else None,
            "stage": self.stage,
            "stage_description": self.stage_description,
            "recommendations": list(self.recommendations),
            "warnings": list(self.warnings),
            "next_steps": list(self.next_steps)
        }
