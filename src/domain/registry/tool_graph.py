"""
Lightweight Tool Relation Graph

Pure Python graph implementation using networkx.
Builds tool relationships from shared parameters and metadata.

No ML dependencies - just graph algorithms.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any

HAS_NETWORKX = False
nx: Any = None

try:
    import networkx

    nx = networkx
    HAS_NETWORKX = True
except ImportError:
    pass

if TYPE_CHECKING:
    from .tool_registry import ToolRegistry


class RelationType(str, Enum):
    """Types of relationships between tools."""

    SHARED_PARAM = "shared_param"  # Share input parameters
    SAME_SPECIALTY = "same_specialty"  # Same medical specialty
    SAME_CONTEXT = "same_context"  # Same clinical context
    SAME_CONDITION = "same_condition"  # Same target condition
    WORKFLOW_NEXT = "workflow_next"  # Often used together (A → B)


@dataclass
class GraphEdge:
    """Represents an edge in the tool graph."""

    source: str
    target: str
    relation_type: RelationType
    weight: float
    metadata: dict[str, str]


class ToolRelationGraph:
    """
    Lightweight graph-based tool relationship manager.

    Uses networkx (pure Python) for graph operations.
    Provides:
    - Related tool discovery
    - Path finding between tools
    - Cluster detection (tool groups)

    Falls back to dict-based implementation if networkx unavailable.
    """

    def __init__(self) -> None:
        if HAS_NETWORKX:
            self._graph: Any = nx.Graph()
        else:
            # Fallback: simple adjacency list
            self._adjacency: dict[str, list[tuple[str, float, RelationType]]] = defaultdict(list)

        self._is_built = False

    @property
    def has_networkx(self) -> bool:
        """Check if networkx is available."""
        return HAS_NETWORKX

    def build_from_registry(self, registry: ToolRegistry) -> None:
        """Build the relationship graph from registry."""
        if HAS_NETWORKX:
            self._build_with_networkx(registry)
        else:
            self._build_fallback(registry)

        self._is_built = True

    def _build_with_networkx(self, registry: ToolRegistry) -> None:
        """Build graph using networkx."""
        self._graph.clear()

        tool_ids = registry.list_all_ids()

        # Add all tools as nodes
        for tool_id in tool_ids:
            calc = registry.get_calculator(tool_id)
            if calc is None:
                continue

            self._graph.add_node(
                tool_id,
                name=calc.metadata.low_level.name,
                specialties=list(calc.high_level_key.specialties),
                contexts=list(calc.high_level_key.clinical_contexts),
            )

        # Build parameter index
        param_to_tools: dict[str, set[str]] = defaultdict(set)
        for tool_id in tool_ids:
            calc = registry.get_calculator(tool_id)
            if calc is None:
                continue
            for param in calc.metadata.low_level.input_params:
                norm_param = self._normalize_param(param)
                param_to_tools[norm_param].add(tool_id)

        # Add edges for shared parameters
        for param, tools in param_to_tools.items():
            if len(tools) < 2:
                continue

            tools_list = list(tools)
            for i, tool1 in enumerate(tools_list):
                for tool2 in tools_list[i + 1 :]:
                    # Update or create edge
                    if self._graph.has_edge(tool1, tool2):
                        # Increase weight
                        self._graph[tool1][tool2]["weight"] += 0.2
                        self._graph[tool1][tool2]["shared_params"].append(param)
                    else:
                        self._graph.add_edge(
                            tool1,
                            tool2,
                            weight=0.2,
                            relation_type=RelationType.SHARED_PARAM.value,
                            shared_params=[param],
                        )

        # Add edges for same specialty
        specialty_to_tools: dict[str, set[str]] = defaultdict(set)
        for tool_id in tool_ids:
            calc = registry.get_calculator(tool_id)
            if calc is None:
                continue
            for spec in calc.high_level_key.specialties:
                specialty_to_tools[spec.value].add(tool_id)

        for spec_value, tools in specialty_to_tools.items():
            if len(tools) < 2:
                continue

            tools_list = list(tools)
            for i, tool1 in enumerate(tools_list):
                for tool2 in tools_list[i + 1 :]:
                    if self._graph.has_edge(tool1, tool2):
                        self._graph[tool1][tool2]["weight"] += 0.3
                    else:
                        self._graph.add_edge(
                            tool1,
                            tool2,
                            weight=0.3,
                            relation_type=RelationType.SAME_SPECIALTY.value,
                            shared_params=[],
                        )

        # Add edges for same context
        context_to_tools: dict[str, set[str]] = defaultdict(set)
        for tool_id in tool_ids:
            calc = registry.get_calculator(tool_id)
            if calc is None:
                continue
            for ctx in calc.high_level_key.clinical_contexts:
                context_to_tools[ctx.value].add(tool_id)

        for ctx_value, tools in context_to_tools.items():
            if len(tools) < 2:
                continue

            tools_list = list(tools)
            for i, tool1 in enumerate(tools_list):
                for tool2 in tools_list[i + 1 :]:
                    if self._graph.has_edge(tool1, tool2):
                        self._graph[tool1][tool2]["weight"] += 0.2
                    else:
                        self._graph.add_edge(
                            tool1,
                            tool2,
                            weight=0.2,
                            relation_type=RelationType.SAME_CONTEXT.value,
                            shared_params=[],
                        )

    def _build_fallback(self, registry: ToolRegistry) -> None:
        """Build using simple adjacency list (no networkx)."""
        self._adjacency.clear()

        # Same logic but store in adjacency list
        tool_ids = registry.list_all_ids()

        # Build parameter index
        param_to_tools: dict[str, set[str]] = defaultdict(set)
        for tool_id in tool_ids:
            calc = registry.get_calculator(tool_id)
            if calc is None:
                continue
            for param in calc.metadata.low_level.input_params:
                norm_param = self._normalize_param(param)
                param_to_tools[norm_param].add(tool_id)

        # Build adjacency from shared params
        edge_weights: dict[tuple[str, str], float] = defaultdict(float)

        for tools in param_to_tools.values():
            if len(tools) < 2:
                continue
            tools_list = list(tools)
            for i, tool1 in enumerate(tools_list):
                for tool2 in tools_list[i + 1 :]:
                    key = tuple(sorted([tool1, tool2]))
                    edge_weights[key] += 0.2  # type: ignore

        # Build specialty connections
        specialty_to_tools: dict[str, set[str]] = defaultdict(set)
        for tool_id in tool_ids:
            calc = registry.get_calculator(tool_id)
            if calc is None:
                continue
            for spec in calc.high_level_key.specialties:
                specialty_to_tools[spec.value].add(tool_id)

        for tools in specialty_to_tools.values():
            if len(tools) < 2:
                continue
            tools_list = list(tools)
            for i, tool1 in enumerate(tools_list):
                for tool2 in tools_list[i + 1 :]:
                    key = tuple(sorted([tool1, tool2]))
                    edge_weights[key] += 0.3  # type: ignore

        # Store in adjacency list
        for (tool1, tool2), weight in edge_weights.items():
            self._adjacency[tool1].append((tool2, weight, RelationType.SHARED_PARAM))
            self._adjacency[tool2].append((tool1, weight, RelationType.SHARED_PARAM))

    def _normalize_param(self, param: str) -> str:
        """Normalize parameter name."""
        import re

        param = re.sub(r"_(mg_dl|mmhg|bpm|kg|cm|ml|min|h|score|value|level)$", "", param.lower())
        param = re.sub(r"\d+", "", param)
        return param.strip("_")

    def get_related_tools(self, tool_id: str, limit: int = 5, min_weight: float = 0.2) -> list[tuple[str, float]]:
        """
        Get tools related to the given tool.

        Returns list of (tool_id, weight) sorted by weight descending.
        """
        if not self._is_built:
            return []

        if HAS_NETWORKX:
            if tool_id not in self._graph:
                return []

            neighbors = [
                (neighbor, self._graph[tool_id][neighbor]["weight"])
                for neighbor in self._graph.neighbors(tool_id)
                if self._graph[tool_id][neighbor]["weight"] >= min_weight
            ]
        else:
            neighbors = [(neighbor, weight) for neighbor, weight, _ in self._adjacency.get(tool_id, []) if weight >= min_weight]

        # Sort by weight
        neighbors.sort(key=lambda x: x[1], reverse=True)
        return neighbors[:limit]

    def find_path(self, source: str, target: str) -> list[str] | None:
        """
        Find shortest path between two tools.

        Returns list of tool_ids or None if no path exists.
        """
        if not self._is_built:
            return None

        if HAS_NETWORKX:
            try:
                path: list[str] = nx.shortest_path(self._graph, source, target)
                return path
            except Exception:
                return None
        else:
            # Simple BFS fallback
            return self._bfs_path(source, target)

    def _bfs_path(self, source: str, target: str) -> list[str] | None:
        """BFS path finding without networkx."""
        if source not in self._adjacency or target not in self._adjacency:
            return None

        visited = {source}
        queue = [(source, [source])]

        while queue:
            node, path = queue.pop(0)

            for neighbor, _, _ in self._adjacency.get(node, []):
                if neighbor == target:
                    return path + [neighbor]

                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    def get_tool_clusters(self, min_cluster_size: int = 3) -> list[set[str]]:
        """
        Find clusters of related tools.

        Returns list of tool_id sets.
        """
        if not self._is_built:
            return []

        if HAS_NETWORKX:
            # Use connected components
            clusters = [component for component in nx.connected_components(self._graph) if len(component) >= min_cluster_size]
            return sorted(clusters, key=len, reverse=True)
        else:
            # Simple DFS-based clustering
            return self._find_clusters_fallback(min_cluster_size)

    def _find_clusters_fallback(self, min_size: int) -> list[set[str]]:
        """Find clusters without networkx using DFS."""
        visited: set[str] = set()
        clusters: list[set[str]] = []

        for start in self._adjacency:
            if start in visited:
                continue

            # DFS to find component
            cluster: set[str] = set()
            stack = [start]

            while stack:
                node = stack.pop()
                if node in visited:
                    continue
                visited.add(node)
                cluster.add(node)

                for neighbor, _, _ in self._adjacency.get(node, []):
                    if neighbor not in visited:
                        stack.append(neighbor)

            if len(cluster) >= min_size:
                clusters.append(cluster)

        return sorted(clusters, key=len, reverse=True)

    def get_statistics(self) -> dict[str, Any]:
        """Get graph statistics."""
        if not self._is_built:
            return {"is_built": False}

        if HAS_NETWORKX:
            return {
                "nodes": self._graph.number_of_nodes(),
                "edges": self._graph.number_of_edges(),
                "density": nx.density(self._graph),
                "components": nx.number_connected_components(self._graph),
                "is_built": True,
                "backend": "networkx",
            }
        else:
            nodes = len(self._adjacency)
            edges = sum(len(neighbors) for neighbors in self._adjacency.values()) // 2
            return {
                "nodes": nodes,
                "edges": edges,
                "density": 2 * edges / (nodes * (nodes - 1)) if nodes > 1 else 0,
                "is_built": True,
                "backend": "fallback",
            }


# Singleton
_relation_graph: ToolRelationGraph | None = None


def get_relation_graph() -> ToolRelationGraph:
    """Get the global relation graph instance."""
    global _relation_graph
    if _relation_graph is None:
        _relation_graph = ToolRelationGraph()
    return _relation_graph
