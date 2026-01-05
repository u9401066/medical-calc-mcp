"""
Discovery Use Case

Application layer use case for tool discovery operations.
"""

from typing import Optional

from ...domain.entities.tool_metadata import ToolMetadata
from ...domain.registry.tool_registry import ToolRegistry
from ...domain.value_objects.tool_keys import ClinicalContext, Specialty
from ..dto import (
    DiscoveryMode,
    DiscoveryRequest,
    DiscoveryResponse,
    ToolDetailDTO,
    ToolSummaryDTO,
)


class DiscoveryUseCase:
    """
    Use case for discovering medical calculator tools.

    This use case provides a unified interface for all discovery operations:
    - Free text search
    - Filter by specialty
    - Filter by clinical context
    - Filter by condition
    - List all tools
    - Get detailed tool info
    """

    def __init__(self, registry: ToolRegistry):
        self._registry = registry

    def execute(self, request: DiscoveryRequest) -> DiscoveryResponse:
        """
        Execute the discovery operation based on the request mode.

        Args:
            request: DiscoveryRequest with mode and parameters

        Returns:
            DiscoveryResponse with matching tools or error
        """
        try:
            if request.mode == DiscoveryMode.SEARCH:
                return self._search(request.query or "", request.limit)

            elif request.mode == DiscoveryMode.BY_SPECIALTY:
                return self._by_specialty(request.specialty, request.limit)

            elif request.mode == DiscoveryMode.BY_CONTEXT:
                return self._by_context(request.context, request.limit)

            elif request.mode == DiscoveryMode.BY_CONDITION:
                return self._by_condition(request.condition, request.limit)

            elif request.mode == DiscoveryMode.LIST_ALL:
                return self._list_all(request.limit)

            elif request.mode == DiscoveryMode.GET_INFO:
                return self._get_info(request.tool_id)

            elif request.mode == DiscoveryMode.LIST_SPECIALTIES:
                return self._list_specialties()

            elif request.mode == DiscoveryMode.LIST_CONTEXTS:
                return self._list_contexts()

            else:
                return DiscoveryResponse(
                    mode=request.mode,
                    success=False,
                    count=0,
                    error=f"Unknown discovery mode: {request.mode}"
                )

        except Exception as e:
            return DiscoveryResponse(
                mode=request.mode,
                success=False,
                count=0,
                error=str(e)
            )

    def _search(self, query: str, limit: int) -> DiscoveryResponse:
        """Free text search"""
        results = self._registry.search(query, limit=limit)
        tools = [self._to_summary(meta) for meta in results]

        return DiscoveryResponse(
            mode=DiscoveryMode.SEARCH,
            success=True,
            count=len(tools),
            tools=tools,
            query=query
        )

    def _by_specialty(self, specialty_str: Optional[str], limit: int) -> DiscoveryResponse:
        """Filter by specialty"""
        if not specialty_str:
            return DiscoveryResponse(
                mode=DiscoveryMode.BY_SPECIALTY,
                success=False,
                count=0,
                error="Specialty is required",
                available_specialties=self._get_available_specialties()
            )

        # Try to match specialty
        specialty = self._match_specialty(specialty_str)
        if specialty is None:
            return DiscoveryResponse(
                mode=DiscoveryMode.BY_SPECIALTY,
                success=False,
                count=0,
                error=f"Unknown specialty: {specialty_str}",
                available_specialties=self._get_available_specialties()
            )

        results = self._registry.list_by_specialty(specialty)
        tools = [self._to_summary(meta) for meta in results[:limit]]

        return DiscoveryResponse(
            mode=DiscoveryMode.BY_SPECIALTY,
            success=True,
            count=len(tools),
            tools=tools,
            query=specialty_str
        )

    def _by_context(self, context_str: Optional[str], limit: int) -> DiscoveryResponse:
        """Filter by clinical context"""
        if not context_str:
            return DiscoveryResponse(
                mode=DiscoveryMode.BY_CONTEXT,
                success=False,
                count=0,
                error="Context is required",
                available_contexts=self._get_available_contexts()
            )

        # Try to match context
        context = self._match_context(context_str)
        if context is None:
            return DiscoveryResponse(
                mode=DiscoveryMode.BY_CONTEXT,
                success=False,
                count=0,
                error=f"Unknown context: {context_str}",
                available_contexts=self._get_available_contexts()
            )

        results = self._registry.list_by_context(context)
        tools = [self._to_summary(meta) for meta in results[:limit]]

        return DiscoveryResponse(
            mode=DiscoveryMode.BY_CONTEXT,
            success=True,
            count=len(tools),
            tools=tools,
            query=context_str
        )

    def _by_condition(self, condition: Optional[str], limit: int) -> DiscoveryResponse:
        """Filter by condition/disease"""
        if not condition:
            return DiscoveryResponse(
                mode=DiscoveryMode.BY_CONDITION,
                success=False,
                count=0,
                error="Condition is required"
            )

        # Use search with condition as query
        results = self._registry.search(condition, limit=limit)
        tools = [self._to_summary(meta) for meta in results]

        return DiscoveryResponse(
            mode=DiscoveryMode.BY_CONDITION,
            success=True,
            count=len(tools),
            tools=tools,
            query=condition
        )

    def _list_all(self, limit: int) -> DiscoveryResponse:
        """List all tools"""
        results = self._registry.list_all()
        tools = [self._to_summary(meta) for meta in results[:limit]]

        return DiscoveryResponse(
            mode=DiscoveryMode.LIST_ALL,
            success=True,
            count=len(tools),
            tools=tools
        )

    def _get_info(self, tool_id: Optional[str]) -> DiscoveryResponse:
        """Get detailed info for specific tool"""
        if not tool_id:
            return DiscoveryResponse(
                mode=DiscoveryMode.GET_INFO,
                success=False,
                count=0,
                error="tool_id is required"
            )

        metadata = self._registry.get(tool_id)
        if metadata is None:
            available = [m.low_level.tool_id for m in self._registry.list_all()]
            return DiscoveryResponse(
                mode=DiscoveryMode.GET_INFO,
                success=False,
                count=0,
                error=f"Tool '{tool_id}' not found. Available: {available}"
            )

        detail = self._to_detail(metadata)

        return DiscoveryResponse(
            mode=DiscoveryMode.GET_INFO,
            success=True,
            count=1,
            tool_detail=detail
        )

    def _list_specialties(self) -> DiscoveryResponse:
        """List all available specialties"""
        specialties = self._get_available_specialties()

        return DiscoveryResponse(
            mode=DiscoveryMode.LIST_SPECIALTIES,
            success=True,
            count=len(specialties),
            available_specialties=specialties
        )

    def _list_contexts(self) -> DiscoveryResponse:
        """List all available clinical contexts"""
        contexts = self._get_available_contexts()

        return DiscoveryResponse(
            mode=DiscoveryMode.LIST_CONTEXTS,
            success=True,
            count=len(contexts),
            available_contexts=contexts
        )

    # Helper methods

    def _to_summary(self, metadata: ToolMetadata) -> ToolSummaryDTO:
        """Convert ToolMetadata to ToolSummaryDTO"""
        return ToolSummaryDTO(
            tool_id=metadata.low_level.tool_id,
            name=metadata.low_level.name,
            purpose=metadata.low_level.purpose,
            specialties=[s.value for s in metadata.high_level.specialties],
            input_params=metadata.low_level.input_params,
            output_type=metadata.low_level.output_type
        )

    def _to_detail(self, metadata: ToolMetadata) -> ToolDetailDTO:
        """Convert ToolMetadata to ToolDetailDTO"""
        return ToolDetailDTO(
            tool_id=metadata.low_level.tool_id,
            name=metadata.low_level.name,
            purpose=metadata.low_level.purpose,
            input_params=metadata.low_level.input_params,
            output_type=metadata.low_level.output_type,
            specialties=[s.value for s in metadata.high_level.specialties],
            conditions=list(metadata.high_level.conditions),
            clinical_contexts=[c.value for c in metadata.high_level.clinical_contexts],
            clinical_questions=list(metadata.high_level.clinical_questions),
            keywords=list(metadata.high_level.keywords),
            icd10_codes=list(metadata.high_level.icd10_codes),
            references=[
                {
                    "citation": ref.citation,
                    "doi": ref.doi,
                    "pmid": ref.pmid,
                    "year": ref.year,
                }
                for ref in metadata.references
            ],
            version=metadata.version,
            validation_status=metadata.validation_status
        )

    def _get_available_specialties(self) -> list[str]:
        """Get list of specialties that have registered tools"""
        specialties = self._registry.list_specialties()
        return [s.value for s in specialties]

    def _get_available_contexts(self) -> list[str]:
        """Get list of clinical contexts that have registered tools"""
        contexts = self._registry.list_contexts()
        return [c.value for c in contexts]

    def _match_specialty(self, specialty_str: str) -> Optional[Specialty]:
        """Match string to Specialty enum"""
        specialty_lower = specialty_str.lower().replace(" ", "_").replace("-", "_")
        for specialty in Specialty:
            if specialty.value == specialty_lower or specialty.name.lower() == specialty_lower:
                return specialty
        return None

    def _match_context(self, context_str: str) -> Optional[ClinicalContext]:
        """Match string to ClinicalContext enum"""
        context_lower = context_str.lower().replace(" ", "_").replace("-", "_")
        for context in ClinicalContext:
            if context.value == context_lower or context.name.lower() == context_lower:
                return context
        return None
