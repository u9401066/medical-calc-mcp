"""
Calculate Use Case

Application layer use case for executing calculations.
"""

from typing import Any

from ..dto import (
    CalculateRequest,
    CalculateResponse,
    ReferenceDTO,
    InterpretationDTO,
)
from ...domain.registry.tool_registry import ToolRegistry


class CalculateUseCase:
    """
    Use case for executing medical calculations.
    
    This use case:
    1. Validates the tool exists
    2. Executes the calculation
    3. Formats the response
    """
    
    def __init__(self, registry: ToolRegistry):
        self._registry = registry
    
    def execute(self, request: CalculateRequest) -> CalculateResponse:
        """
        Execute a calculation.
        
        Args:
            request: CalculateRequest with tool_id and params
            
        Returns:
            CalculateResponse with result or error
        """
        try:
            # Get calculator
            calculator = self._registry.get_calculator(request.tool_id)
            if calculator is None:
                available = self._registry.list_all_ids()
                return CalculateResponse(
                    success=False,
                    tool_id=request.tool_id,
                    score_name="",
                    result=None,
                    unit="",
                    error=f"Calculator '{request.tool_id}' not found. Available: {available}"
                )
            
            # Execute calculation
            result = calculator.calculate(**request.params)
            
            # Convert to response
            return self._to_response(request.tool_id, result)
            
        except TypeError as e:
            return CalculateResponse(
                success=False,
                tool_id=request.tool_id,
                score_name="",
                result=None,
                unit="",
                error=f"Invalid parameters: {str(e)}"
            )
        except ValueError as e:
            return CalculateResponse(
                success=False,
                tool_id=request.tool_id,
                score_name="",
                result=None,
                unit="",
                error=f"Validation error: {str(e)}"
            )
        except Exception as e:
            return CalculateResponse(
                success=False,
                tool_id=request.tool_id,
                score_name="",
                result=None,
                unit="",
                error=f"Calculation error: {str(e)}"
            )
    
    def _to_response(self, tool_id: str, result) -> CalculateResponse:
        """Convert ScoreResult to CalculateResponse"""
        # Build interpretation
        interpretation = None
        if result.interpretation:
            interpretation = InterpretationDTO(
                summary=result.interpretation.summary,
                severity=result.interpretation.severity.value if result.interpretation.severity else None,
                recommendation=result.interpretation.recommendation,
                details=result.interpretation.details or {}
            )
        
        # Build references
        references = [
            ReferenceDTO(
                citation=ref.citation,
                doi=ref.doi,
                pmid=ref.pmid,
                year=ref.year
            )
            for ref in (result.references or [])
        ]
        
        return CalculateResponse(
            success=True,
            tool_id=tool_id,
            score_name=result.score_name,
            result=result.value,
            unit=str(result.unit) if result.unit else "",
            interpretation=interpretation,
            component_scores=result.component_scores or {},
            references=references
        )
