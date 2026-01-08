"""
Discovery DTOs

Data Transfer Objects for tool discovery operations.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class DiscoveryMode(Enum):
    """Discovery mode enumeration for structured API"""

    SEARCH = "search"  # Free text search
    BY_SPECIALTY = "by_specialty"  # Filter by specialty
    BY_CONTEXT = "by_context"  # Filter by clinical context
    BY_CONDITION = "by_condition"  # Filter by condition
    LIST_ALL = "list_all"  # List all tools
    GET_INFO = "get_info"  # Get specific tool info
    LIST_SPECIALTIES = "list_specialties"  # List available specialties
    LIST_CONTEXTS = "list_contexts"  # List available contexts


@dataclass(frozen=True)
class DiscoveryRequest:
    """
    Request DTO for tool discovery.

    This unified request supports multiple discovery modes:
    - search: Free text search across all metadata
    - by_specialty: Filter by medical specialty
    - by_context: Filter by clinical context
    - by_condition: Filter by condition/disease
    - list_all: Get all available tools
    - get_info: Get detailed info for specific tool
    """

    mode: DiscoveryMode
    query: Optional[str] = None
    specialty: Optional[str] = None
    context: Optional[str] = None
    condition: Optional[str] = None
    tool_id: Optional[str] = None
    limit: int = 10
    include_params: bool = True
    include_references: bool = False


@dataclass
class ToolSummaryDTO:
    """Summary information for a single tool"""

    tool_id: str
    name: str
    purpose: str
    specialties: list[str]
    input_params: list[str]
    output_type: str


@dataclass
class ToolDetailDTO:
    """Detailed information for a single tool"""

    tool_id: str
    name: str
    purpose: str
    input_params: list[str]
    output_type: str
    specialties: list[str]
    conditions: list[str]
    clinical_contexts: list[str]
    clinical_questions: list[str]
    keywords: list[str]
    icd10_codes: list[str]
    references: list[dict[str, Any]]
    version: str
    validation_status: str


@dataclass
class DiscoveryResponse:
    """
    Response DTO for tool discovery.

    Contains either a list of tool summaries or a single detailed tool info.
    """

    mode: DiscoveryMode
    success: bool
    count: int
    tools: list[ToolSummaryDTO] = field(default_factory=list)
    tool_detail: Optional[ToolDetailDTO] = None
    available_specialties: list[str] = field(default_factory=list)
    available_contexts: list[str] = field(default_factory=list)
    query: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for MCP response"""
        result: dict[str, Any] = {
            "mode": self.mode.value,
            "success": self.success,
            "count": self.count,
        }

        if self.query:
            result["query"] = self.query

        if self.error:
            result["error"] = self.error
            return result

        if self.tools:
            result["tools"] = [
                {
                    "tool_id": t.tool_id,
                    "name": t.name,
                    "purpose": t.purpose,
                    "specialties": t.specialties,
                    "input_params": t.input_params,
                    "output_type": t.output_type,
                }
                for t in self.tools
            ]

        if self.tool_detail:
            result["tool"] = {
                "tool_id": self.tool_detail.tool_id,
                "name": self.tool_detail.name,
                "purpose": self.tool_detail.purpose,
                "input_params": self.tool_detail.input_params,
                "output_type": self.tool_detail.output_type,
                "specialties": self.tool_detail.specialties,
                "conditions": self.tool_detail.conditions,
                "clinical_contexts": self.tool_detail.clinical_contexts,
                "clinical_questions": self.tool_detail.clinical_questions,
                "keywords": self.tool_detail.keywords,
                "references": self.tool_detail.references,
                "version": self.tool_detail.version,
            }

        if self.available_specialties:
            result["available_specialties"] = self.available_specialties

        if self.available_contexts:
            result["available_contexts"] = self.available_contexts

        return result
