# Tool Registry - Calculator Registration and Indexing

from .auto_discovery import (
    AutoDiscoveryEngine,
    DiscoveryResult,
    EnrichedHighLevelKey,
    get_discovery_engine,
)
from .taxonomy import (
    CONTEXT_DESCRIPTIONS,
    RELATED_SPECIALTIES,
    SPECIALTY_GROUPS,
    get_context_display_name,
    get_specialty_display_name,
)
from .tool_graph import (
    RelationType,
    ToolRelationGraph,
    get_relation_graph,
)
from .tool_registry import ToolRegistry, get_registry

__all__ = [
    # Core Registry
    "ToolRegistry",
    "get_registry",
    # Auto Discovery (no ML required, zero external deps)
    "AutoDiscoveryEngine",
    "DiscoveryResult",
    "EnrichedHighLevelKey",
    "get_discovery_engine",
    # Tool Relation Graph (networkx or fallback)
    "ToolRelationGraph",
    "RelationType",
    "get_relation_graph",
    # Taxonomy
    "SPECIALTY_GROUPS",
    "RELATED_SPECIALTIES",
    "CONTEXT_DESCRIPTIONS",
    "get_specialty_display_name",
    "get_context_display_name",
]
