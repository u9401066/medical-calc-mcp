"""
Calculator Resources Handler

MCP resource handlers for calculator information.
"""

from mcp.server.fastmcp import FastMCP

from ....domain.registry.tool_registry import ToolRegistry


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
        
        @self._mcp.resource("calculator://list")
        def get_calculator_list() -> str:
            """Get list of all available calculators"""
            all_tools = self._registry.list_all()
            lines = ["# Available Medical Calculators\n"]
            lines.append(f"Total: {len(all_tools)} calculators\n")
            
            # Group by specialty
            by_specialty: dict[str, list] = {}
            for meta in all_tools:
                for specialty in meta.high_level.specialties:
                    if specialty.value not in by_specialty:
                        by_specialty[specialty.value] = []
                    by_specialty[specialty.value].append(meta)
            
            for specialty, tools in sorted(by_specialty.items()):
                lines.append(f"\n## {specialty.replace('_', ' ').title()}\n")
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
            metadata = self._registry.get(tool_id)
            if metadata is None:
                return f"Calculator '{tool_id}' not found"
            
            lines = [f"# {metadata.low_level.name}\n"]
            lines.append(f"**Tool ID:** `{metadata.low_level.tool_id}`\n")
            lines.append(f"**Purpose:** {metadata.low_level.purpose}\n")
            
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
            metadata = self._registry.get(tool_id)
            if metadata is None:
                return f"Calculator '{tool_id}' not found"
            
            lines = [f"# References for {metadata.low_level.name}\n"]
            
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
            
            # Match specialty
            matched_specialty = None
            specialty_lower = specialty.lower().replace(" ", "_").replace("-", "_")
            for s in Specialty:
                if s.value == specialty_lower or s.name.lower() == specialty_lower:
                    matched_specialty = s
                    break
            
            if matched_specialty is None:
                available = [s.value for s in self._registry.list_specialties()]
                return f"Unknown specialty: {specialty}\n\nAvailable: {', '.join(available)}"
            
            tools = self._registry.list_by_specialty(matched_specialty)
            
            lines = [f"# {matched_specialty.value.replace('_', ' ').title()} Calculators\n"]
            lines.append(f"Total: {len(tools)} tools\n")
            
            for meta in tools:
                lines.append(f"## {meta.low_level.name}")
                lines.append(f"**ID:** `{meta.low_level.tool_id}`\n")
                lines.append(f"{meta.low_level.purpose}\n")
                lines.append(f"**Parameters:** {', '.join(meta.low_level.input_params)}\n")
            
            return "\n".join(lines)
