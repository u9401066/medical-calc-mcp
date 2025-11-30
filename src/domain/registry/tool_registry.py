"""
Tool Registry

Central registry for all medical calculators.
Provides registration, lookup, and search capabilities.
"""

from typing import Dict, List, Optional, Set
from collections import defaultdict

from ..services.base import BaseCalculator
from ..entities.tool_metadata import ToolMetadata
from ..value_objects.tool_keys import Specialty, ClinicalContext


class ToolRegistry:
    """
    Central registry for all medical calculator tools.
    
    Features:
    - Register calculators with automatic indexing
    - Lookup by tool_id
    - Search by specialty, condition, context, keyword
    - List all tools or by category
    
    This is a singleton - use ToolRegistry.instance() to get the registry.
    """
    
    _instance: Optional["ToolRegistry"] = None
    
    def __init__(self):
        # Main storage
        self._calculators: Dict[str, BaseCalculator] = {}
        
        # Indexes for fast lookup
        self._by_specialty: Dict[Specialty, Set[str]] = defaultdict(set)
        self._by_condition: Dict[str, Set[str]] = defaultdict(set)
        self._by_context: Dict[ClinicalContext, Set[str]] = defaultdict(set)
        self._by_keyword: Dict[str, Set[str]] = defaultdict(set)
        self._by_icd10: Dict[str, Set[str]] = defaultdict(set)
    
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
    
    def list_all(self) -> List[ToolMetadata]:
        """List metadata for all registered tools"""
        return [calc.metadata for calc in self._calculators.values()]
    
    def list_all_ids(self) -> List[str]:
        """List all registered tool IDs"""
        return list(self._calculators.keys())
    
    def count(self) -> int:
        """Get total number of registered calculators"""
        return len(self._calculators)
    
    # Search methods
    
    def search(
        self,
        query: str,
        limit: int = 10
    ) -> List[ToolMetadata]:
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
        results: List[tuple[int, ToolMetadata]] = []
        
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
    ) -> List[ToolMetadata]:
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
        matching_ids: Optional[Set[str]] = None
        
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
    
    def list_by_specialty(self, specialty: Specialty) -> List[ToolMetadata]:
        """List all tools for a given specialty"""
        tool_ids = self._by_specialty.get(specialty, set())
        return [self._calculators[tid].metadata for tid in tool_ids]
    
    def list_by_context(self, context: ClinicalContext) -> List[ToolMetadata]:
        """List all tools for a given clinical context"""
        tool_ids = self._by_context.get(context, set())
        return [self._calculators[tid].metadata for tid in tool_ids]
    
    def list_specialties(self) -> List[Specialty]:
        """List all specialties that have registered tools"""
        return [s for s in self._by_specialty.keys() if self._by_specialty[s]]
    
    def list_contexts(self) -> List[ClinicalContext]:
        """List all clinical contexts that have registered tools"""
        return [c for c in self._by_context.keys() if self._by_context[c]]
    
    def get_statistics(self) -> Dict:
        """Get registry statistics"""
        return {
            "total_tools": self.count(),
            "specialties": {
                s.value: len(ids) for s, ids in self._by_specialty.items() if ids
            },
            "clinical_contexts": {
                c.value: len(ids) for c, ids in self._by_context.items() if ids
            },
        }


# Convenience function for the singleton
def get_registry() -> ToolRegistry:
    """Get the global tool registry instance"""
    return ToolRegistry.instance()
