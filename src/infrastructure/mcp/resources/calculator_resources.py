"""
Calculator Resources Handler

MCP resource handlers for calculator information.
"""

from mcp.server.fastmcp import FastMCP

from src.infrastructure.mcp.guidance import TOOL_USAGE_SEQUENCE, get_tool_usage_playbook_markdown

from ....domain.entities.tool_metadata import ToolMetadata
from ....domain.registry.tool_registry import ToolRegistry
from ....shared.smart_input import ResolutionResult, resolve_identifier


class CalculatorResourceHandler:
    """
    Handler for calculator-related MCP resources.

    Resources provide static information about calculators
    that can be loaded by AI agents.
    """

    def __init__(self, mcp: FastMCP, registry: ToolRegistry):
        self._mcp = mcp
        self._registry = registry

        # Register resources
        self._register_resources()

    def _register_resources(self) -> None:
        """Register all resources with MCP"""

        @self._mcp.resource("guide://tool-usage-playbook")
        def get_tool_usage_playbook_resource() -> str:
            """Get the recommended start-here SOP for smaller models."""
            return get_tool_usage_playbook_markdown()

        @self._mcp.resource("calculator://list")
        def get_calculator_list() -> str:
            """Get list of all available calculators"""
            all_tools = self._registry.list_all()
            lines = ["# Available Medical Calculators\n"]
            lines.append(f"Total: {len(all_tools)} calculators\n")
            lines.append("## Start Here\n")
            lines.append("For weaker models, read the SOP before choosing any tool.\n")
            lines.append("- Preferred resource: `guide://tool-usage-playbook`")
            lines.append("- Preferred prompt: `tool_usage_playbook()`")
            lines.append(f"- Safe sequence: `{TOOL_USAGE_SEQUENCE}`\n")

            # Group by specialty
            by_specialty: dict[str, list[ToolMetadata]] = {}
            for meta in all_tools:
                for specialty in meta.high_level.specialties:
                    spec_name = specialty.value
                    if spec_name not in by_specialty:
                        by_specialty[spec_name] = []
                    by_specialty[spec_name].append(meta)

            for spec_name, tools in sorted(by_specialty.items()):
                lines.append(f"\n## {spec_name.replace('_', ' ').title()}\n")
                seen = set()
                for meta in tools:
                    if meta.low_level.tool_id in seen:
                        continue
                    seen.add(meta.low_level.tool_id)
                    lines.append(f"- **{meta.low_level.name}** (`{meta.low_level.tool_id}`)")
                    lines.append(f"  - {meta.low_level.purpose}")
                    lines.append("")

            return "\n".join(lines)

        @self._mcp.resource("calculator://{tool_id}/info")
        def get_calculator_info_resource(tool_id: str) -> str:
            """Get detailed info for a specific calculator"""
            resolution = resolve_identifier(tool_id, self._registry.list_all_ids())
            resolved_tool_id = resolution.resolved_value or tool_id
            metadata = self._registry.get(resolved_tool_id)
            if metadata is None:
                return _build_tool_not_found_resource(tool_id, resolution)

            lines = [f"# {metadata.low_level.name}\n"]
            if resolved_tool_id != tool_id:
                lines.append(f"**Resolved Tool ID:** `{resolved_tool_id}` (from `{tool_id}`)\n")
            lines.append(f"**Tool ID:** `{metadata.low_level.tool_id}`\n")
            lines.append(f"**Purpose:** {metadata.low_level.purpose}\n")
            lines.append(f"**Formula Source Type:** `{metadata.formula_source_type}`\n")
            lines.append("**Start Here Resource:** `guide://tool-usage-playbook`\n")
            lines.append("**Recommended Sequence:** `discover(...)` → `get_tool_schema(tool_id)` → `calculate(tool_id, params)`\n")

            lines.append("\n## Input Parameters\n")
            for param in metadata.low_level.input_params:
                lines.append(f"- `{param}`")

            lines.append(f"\n**Output:** {metadata.low_level.output_type}\n")

            lines.append("\n## Clinical Use\n")
            lines.append(f"**Specialties:** {', '.join(s.value for s in metadata.high_level.specialties)}\n")
            lines.append(f"**Contexts:** {', '.join(c.value for c in metadata.high_level.clinical_contexts)}\n")

            if metadata.high_level.conditions:
                lines.append(f"**Conditions:** {', '.join(metadata.high_level.conditions)}\n")

            if metadata.high_level.clinical_questions:
                lines.append("\n### Clinical Questions\n")
                for q in metadata.high_level.clinical_questions:
                    lines.append(f"- {q}")

            return "\n".join(lines)

        @self._mcp.resource("calculator://{tool_id}/references")
        def get_calculator_references(tool_id: str) -> str:
            """Get paper references for a specific calculator"""
            resolution = resolve_identifier(tool_id, self._registry.list_all_ids())
            resolved_tool_id = resolution.resolved_value or tool_id
            metadata = self._registry.get(resolved_tool_id)
            if metadata is None:
                return _build_tool_not_found_resource(tool_id, resolution)

            lines = [f"# References for {metadata.low_level.name}\n"]
            if resolved_tool_id != tool_id:
                lines.append(f"**Resolved Tool ID:** `{resolved_tool_id}` (from `{tool_id}`)\n")

            for i, ref in enumerate(metadata.references, 1):
                lines.append(f"## Reference {i}")
                lines.append(f"**Citation:** {ref.citation}")
                if ref.doi:
                    lines.append(f"**DOI:** https://doi.org/{ref.doi}")
                if ref.pmid:
                    lines.append(f"**PubMed:** https://pubmed.ncbi.nlm.nih.gov/{ref.pmid}/")
                if ref.year:
                    lines.append(f"**Year:** {ref.year}")
                lines.append("")

            return "\n".join(lines)

        @self._mcp.resource("specialty://{specialty}/tools")
        def get_specialty_tools(specialty: str) -> str:
            """Get all tools for a specific specialty"""
            from ....domain.value_objects.tool_keys import Specialty

            specialty_candidates = [s.value for s in self._registry.list_specialties()]
            resolution = resolve_identifier(specialty, specialty_candidates)
            matched_specialty = None
            if resolution.resolved_value is not None:
                for s in Specialty:
                    if s.value == resolution.resolved_value:
                        matched_specialty = s
                        break

            if matched_specialty is None:
                available = [s.value for s in self._registry.list_specialties()]
                lines = [f"Unknown specialty: {specialty}"]
                if resolution.suggestions:
                    lines.append(f"Did you mean: {', '.join(resolution.suggestions)}?")
                lines.append(f"Available: {', '.join(available)}")
                lines.append("Use calculator://list to browse all tools first.")
                return "\n\n".join(lines)

            tools = self._registry.list_by_specialty(matched_specialty)

            lines = [f"# {matched_specialty.value.replace('_', ' ').title()} Calculators\n"]
            if resolution.resolved_value and resolution.resolved_value != specialty:
                lines.append(f"**Resolved Specialty:** `{matched_specialty.value}` (from `{specialty}`)\n")
            lines.append(f"Total: {len(tools)} tools\n")

            for meta in tools:
                lines.append(f"## {meta.low_level.name}")
                lines.append(f"**ID:** `{meta.low_level.tool_id}`\n")
                lines.append(f"{meta.low_level.purpose}\n")
                lines.append(f"**Parameters:** {', '.join(meta.low_level.input_params)}\n")

            return "\n".join(lines)


def _build_tool_not_found_resource(tool_id: str, resolution: ResolutionResult) -> str:
    lines = [f"Calculator '{tool_id}' not found"]
    if resolution.suggestions:
        lines.append(f"Did you mean: {', '.join(resolution.suggestions)}?")
    lines.append("Read `guide://tool-usage-playbook` first if you are unsure which tool to use.")
    lines.append("Recommended sequence: discover(by='keyword', value='關鍵字') → get_tool_schema(tool_id) → calculate(tool_id, params)")
    return "\n\n".join(lines)
