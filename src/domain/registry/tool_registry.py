"""
Tool Registry

Central registry for all medical calculators.
Provides registration, lookup, and search capabilities.

Enhanced with AutoDiscoveryEngine and ToolRelationGraph for
intelligent tool discovery without ML dependencies.
"""

from collections import defaultdict
from typing import TYPE_CHECKING, Any, Optional

from ..entities.tool_metadata import ToolMetadata
from ..services.base import BaseCalculator
from ..value_objects.tool_keys import ClinicalContext, Specialty

if TYPE_CHECKING:
    from .auto_discovery import AutoDiscoveryEngine
    from .tool_graph import ToolRelationGraph


class ToolRegistry:
    """
    Central registry for all medical calculator tools.

    Features:
    - Register calculators with automatic indexing
    - Lookup by tool_id
    - Search by specialty, condition, context, keyword
    - List all tools or by category
    - Auto-discovery engine (no ML required)
    - Tool relation graph for related tools

    This is a singleton - use ToolRegistry.instance() to get the registry.
    """

    _instance: Optional["ToolRegistry"] = None

    def __init__(self) -> None:
        # Main storage
        self._calculators: dict[str, BaseCalculator] = {}

        # Indexes for fast lookup
        self._by_specialty: dict[Specialty, set[str]] = defaultdict(set)
        self._by_condition: dict[str, set[str]] = defaultdict(set)
        self._by_context: dict[ClinicalContext, set[str]] = defaultdict(set)
        self._by_keyword: dict[str, set[str]] = defaultdict(set)
        self._by_icd10: dict[str, set[str]] = defaultdict(set)

        # Auto-discovery components (lazy init)
        self._discovery_engine: Optional[AutoDiscoveryEngine] = None
        self._relation_graph: Optional[ToolRelationGraph] = None
        self._discovery_built = False

    @classmethod
    def instance(cls) -> "ToolRegistry":
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = ToolRegistry()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the registry (mainly for testing)"""
        cls._instance = None

    def register(self, calculator: BaseCalculator) -> None:
        """
        Register a calculator and build indexes.

        Args:
            calculator: The calculator instance to register
        """
        tool_id = calculator.tool_id

        if tool_id in self._calculators:
            raise ValueError(f"Calculator with tool_id '{tool_id}' already registered")

        # Store calculator
        self._calculators[tool_id] = calculator

        # Build indexes from high level key
        high_level = calculator.high_level_key

        for specialty in high_level.specialties:
            self._by_specialty[specialty].add(tool_id)

        for condition in high_level.conditions:
            self._by_condition[condition.lower()].add(tool_id)

        for context in high_level.clinical_contexts:
            self._by_context[context].add(tool_id)

        for keyword in high_level.keywords:
            self._by_keyword[keyword.lower()].add(tool_id)

        for icd10 in high_level.icd10_codes:
            self._by_icd10[icd10.upper()].add(tool_id)

    def get(self, tool_id: str) -> Optional[ToolMetadata]:
        """Get metadata for a tool by tool_id"""
        calc = self._calculators.get(tool_id)
        return calc.metadata if calc else None

    def get_calculator(self, tool_id: str) -> Optional[BaseCalculator]:
        """Get a calculator instance by tool_id"""
        return self._calculators.get(tool_id)

    def list_all(self) -> list[ToolMetadata]:
        """List metadata for all registered tools"""
        return [calc.metadata for calc in self._calculators.values()]

    def list_all_ids(self) -> list[str]:
        """List all registered tool IDs"""
        return list(self._calculators.keys())

    def count(self) -> int:
        """Get total number of registered calculators"""
        return len(self._calculators)

    # Search methods

    def search(self, query: str, limit: int = 10) -> list[ToolMetadata]:
        """
        Search for tools by free text query.

        Searches across tool names, purposes, conditions, keywords,
        clinical questions, and specialties.

        Args:
            query: Free text search query
            limit: Maximum number of results to return

        Returns:
            List of matching ToolMetadata, sorted by relevance
        """
        query_lower = query.lower()
        results: list[tuple[int, ToolMetadata]] = []

        for calc in self._calculators.values():
            score = 0
            meta = calc.metadata
            low = meta.low_level
            high = meta.high_level

            # Exact matches score higher
            if query_lower in low.tool_id.lower():
                score += 10
            if query_lower in low.name.lower():
                score += 8
            if query_lower in low.purpose.lower():
                score += 5

            # Check specialties
            for specialty in high.specialties:
                if query_lower in specialty.value.lower():
                    score += 7

            # Check conditions
            for condition in high.conditions:
                if query_lower in condition.lower():
                    score += 6

            # Check keywords
            for keyword in high.keywords:
                if query_lower in keyword.lower():
                    score += 4

            # Check clinical questions
            for question in high.clinical_questions:
                if query_lower in question.lower():
                    score += 3

            if score > 0:
                results.append((score, meta))

        # Sort by score descending
        results.sort(key=lambda x: x[0], reverse=True)
        return [meta for _, meta in results[:limit]]

    def search_by_filters(
        self,
        specialty: Optional[Specialty] = None,
        condition: Optional[str] = None,
        context: Optional[ClinicalContext] = None,
        keyword: Optional[str] = None,
        icd10: Optional[str] = None,
    ) -> list[ToolMetadata]:
        """
        Search for tools matching the given criteria.

        Multiple criteria are ANDed together.

        Args:
            specialty: Medical specialty to filter by
            condition: Condition/disease to filter by
            context: Clinical context to filter by
            keyword: Keyword to filter by
            icd10: ICD-10 code to filter by

        Returns:
            List of matching ToolMetadata
        """
        # Start with all tools
        matching_ids: Optional[set[str]] = None

        if specialty is not None:
            ids = self._by_specialty.get(specialty, set())
            matching_ids = ids if matching_ids is None else matching_ids & ids

        if condition is not None:
            ids = self._by_condition.get(condition.lower(), set())
            matching_ids = ids if matching_ids is None else matching_ids & ids

        if context is not None:
            ids = self._by_context.get(context, set())
            matching_ids = ids if matching_ids is None else matching_ids & ids

        if keyword is not None:
            ids = self._by_keyword.get(keyword.lower(), set())
            matching_ids = ids if matching_ids is None else matching_ids & ids

        if icd10 is not None:
            ids = self._by_icd10.get(icd10.upper(), set())
            matching_ids = ids if matching_ids is None else matching_ids & ids

        # If no filters, return all
        if matching_ids is None:
            matching_ids = set(self._calculators.keys())

        return [self._calculators[tid].metadata for tid in matching_ids]

    def list_by_specialty(self, specialty: Specialty) -> list[ToolMetadata]:
        """List all tools for a given specialty"""
        tool_ids = self._by_specialty.get(specialty, set())
        return [self._calculators[tid].metadata for tid in tool_ids]

    def list_by_context(self, context: ClinicalContext) -> list[ToolMetadata]:
        """List all tools for a given clinical context"""
        tool_ids = self._by_context.get(context, set())
        return [self._calculators[tid].metadata for tid in tool_ids]

    def list_specialties(self) -> list[Specialty]:
        """List all specialties that have registered tools"""
        return [s for s in self._by_specialty.keys() if self._by_specialty[s]]

    def list_contexts(self) -> list[ClinicalContext]:
        """List all clinical contexts that have registered tools"""
        return [c for c in self._by_context.keys() if self._by_context[c]]

    # ========================================
    # Auto-Discovery Features (No ML Required)
    # ========================================

    def build_discovery_indexes(self) -> None:
        """
        Build auto-discovery indexes from registered tools.

        This builds:
        1. AutoDiscoveryEngine - parameter/keyword based discovery
        2. ToolRelationGraph - graph-based related tool discovery

        Call this AFTER all tools are registered.
        No ML dependencies - pure Python algorithms.
        """
        if self._discovery_built:
            return

        # Lazy import to avoid circular deps
        from .auto_discovery import AutoDiscoveryEngine
        from .tool_graph import ToolRelationGraph

        # Build discovery engine
        self._discovery_engine = AutoDiscoveryEngine()
        self._discovery_engine.build_from_registry(self)

        # Build relation graph
        self._relation_graph = ToolRelationGraph()
        self._relation_graph.build_from_registry(self)

        self._discovery_built = True

    def get_related_tools(self, tool_id: str, limit: int = 5) -> list[tuple[str, float]]:
        """
        Get tools related to the given tool.

        Uses graph-based relationships built from:
        - Shared parameters
        - Same specialty
        - Same clinical context

        Args:
            tool_id: The tool to find related tools for
            limit: Maximum number of related tools to return

        Returns:
            List of (tool_id, similarity_score) tuples
        """
        if not self._discovery_built:
            self.build_discovery_indexes()

        if self._relation_graph:
            return self._relation_graph.get_related_tools(tool_id, limit)
        return []

    def smart_search(self, query: str, limit: int = 10, expand_related: bool = True) -> list[ToolMetadata]:
        """
        Enhanced search using auto-discovery engine.

        Combines:
        - Keyword matching (from docstrings)
        - Parameter matching
        - Related tool expansion

        Args:
            query: Search query
            limit: Maximum results
            expand_related: Whether to include related tools

        Returns:
            List of matching ToolMetadata
        """
        if not self._discovery_built:
            self.build_discovery_indexes()

        # Use discovery engine if available
        if self._discovery_engine:
            results = self._discovery_engine.search(query, limit)

            tool_ids = [r.tool_id for r in results]

            # Optionally expand with related tools
            if expand_related and self._relation_graph and tool_ids:
                for tid in tool_ids[:3]:  # Top 3 results
                    related = self._relation_graph.get_related_tools(tid, 2)
                    for rel_id, _ in related:
                        if rel_id not in tool_ids:
                            tool_ids.append(rel_id)

            return [self._calculators[tid].metadata for tid in tool_ids[:limit] if tid in self._calculators]

        # Fallback to basic search
        return self.search(query, limit)

    def find_tools_by_params(self, params: list[str]) -> list[ToolMetadata]:
        """
        Find tools that can use the given parameters.

        Useful for: "I have these lab values, what can I calculate?"

        Args:
            params: List of parameter names (e.g., ["creatinine", "age", "weight"])

        Returns:
            List of tools that use some/all of these parameters
        """
        if not self._discovery_built:
            self.build_discovery_indexes()

        if self._discovery_engine:
            tool_ids = self._discovery_engine.find_tools_by_params(params)
            return [self._calculators[tid].metadata for tid in tool_ids if tid in self._calculators]
        return []

    def get_discovery_statistics(self) -> dict[str, Any]:
        """Get auto-discovery engine statistics."""
        stats: dict[str, Any] = {
            "discovery_built": self._discovery_built,
        }

        if self._discovery_engine:
            stats["discovery_engine"] = self._discovery_engine.get_statistics()

        if self._relation_graph:
            stats["relation_graph"] = self._relation_graph.get_statistics()

        return stats

    def get_statistics(self) -> dict[str, Any]:
        """Get registry statistics"""
        return {
            "total_tools": self.count(),
            "specialties": {s.value: len(ids) for s, ids in self._by_specialty.items() if ids},
            "clinical_contexts": {c.value: len(ids) for c, ids in self._by_context.items() if ids},
        }


# Convenience function for the singleton
def get_registry() -> ToolRegistry:
    """Get the global tool registry instance"""
    return ToolRegistry.instance()
