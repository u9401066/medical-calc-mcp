"""
Tool Metadata Entity

Contains all metadata about a medical calculator tool.
Used for tool registration and discovery.
"""

from dataclasses import dataclass, field
from typing import Any

from ..value_objects.reference import Reference
from ..value_objects.tool_keys import HighLevelKey, LowLevelKey


@dataclass(frozen=True)
class ToolMetadata:
    """
    Complete metadata for a medical calculator tool.

    This is used for:
    - Tool registration in the registry
    - Tool discovery by AI agents
    - Documentation generation

    Attributes:
        low_level: Precise identification key
        high_level: Discovery/exploration key
        references: Original paper citations
        version: Calculator version
        last_updated: When the calculator was last updated
        validation_status: Whether validated against original paper
    """

    low_level: LowLevelKey
    high_level: HighLevelKey
    references: tuple[Reference, ...] = field(default_factory=tuple)
    version: str = "1.0.0"
    last_updated: str = ""
    validation_status: str = "pending"  # pending, validated, needs_review

    @property
    def tool_id(self) -> str:
        return self.low_level.tool_id

    @property
    def name(self) -> str:
        return self.low_level.name

    @property
    def purpose(self) -> str:
        return self.low_level.purpose

    def to_dict(self) -> dict[str, Any]:
        return {
            "low_level": self.low_level.to_dict(),
            "high_level": self.high_level.to_dict(),
            "references": [ref.to_dict() for ref in self.references],
            "version": self.version,
            "last_updated": self.last_updated,
            "validation_status": self.validation_status,
        }

    def to_discovery_dict(self) -> dict[str, Any]:
        """
        Minimal dict for tool discovery responses.
        Used when listing/searching tools.
        """
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "purpose": self.purpose,
            "input_params": self.low_level.input_params,
            "output_type": self.low_level.output_type,
            "specialties": [s.value for s in self.high_level.specialties],
            "conditions": list(self.high_level.conditions),
            "clinical_contexts": [c.value for c in self.high_level.clinical_contexts],
        }
