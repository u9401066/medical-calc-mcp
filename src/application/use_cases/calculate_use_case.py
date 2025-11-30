"""
Calculate Use Case

Application layer use case for executing calculations.
Provides clear error messages with valid input ranges.
Uses Domain validation for consistent parameter validation.
"""

from typing import Any, Dict, List, Optional

from ..dto import (
    CalculateRequest,
    CalculateResponse,
    ReferenceDTO,
    InterpretationDTO,
)
from ...domain.registry.tool_registry import ToolRegistry
from ...domain.validation import (
    ParameterValidator,
    ValidationResult,
    get_validation_hints,
)


class CalculateUseCase:
    """
    Use case for executing medical calculations.
    
    This use case:
    1. Validates inputs using Domain validation layer
    2. Executes the calculation
    3. Formats the response with clear error messages
    """
    
    def __init__(self, registry: ToolRegistry):
        self._registry = registry
        self._validator = ParameterValidator()
    
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
                    error=f"Calculator '{request.tool_id}' not found. "
                          f"Available calculators: {', '.join(available)}. "
                          f"Use get_calculator_info(tool_id) to see details."
                )
            
            # Pre-validate using domain validation
            validation_result = self._validate_params(request.params)
            if not validation_result.is_valid:
                return CalculateResponse(
                    success=False,
                    tool_id=request.tool_id,
                    score_name="",
                    result=None,
                    unit="",
                    error=f"Validation error: {validation_result.get_error_message()}. "
                          f"Use get_calculator_info('{request.tool_id}') to see required parameters."
                )
            
            # Execute calculation
            result = calculator.calculate(**request.params)
            
            # Convert to response
            return self._to_response(request.tool_id, result)
            
        except TypeError as e:
            error_msg = str(e)
            hint = self._get_parameter_hint_from_error(error_msg, request.params)
            return CalculateResponse(
                success=False,
                tool_id=request.tool_id,
                score_name="",
                result=None,
                unit="",
                error=f"Invalid parameters: {error_msg}. {hint}"
                      f"Use get_calculator_info('{request.tool_id}') to see required parameters."
            )
        except ValueError as e:
            error_msg = str(e)
            hint = self._get_parameter_hint_from_error(error_msg, request.params)
            return CalculateResponse(
                success=False,
                tool_id=request.tool_id,
                score_name="",
                result=None,
                unit="",
                error=f"Validation error: {error_msg}. {hint}"
            )
        except Exception as e:
            return CalculateResponse(
                success=False,
                tool_id=request.tool_id,
                score_name="",
                result=None,
                unit="",
                error=f"Calculation error: {str(e)}. "
                      f"Please check input values and try again."
            )
    
    def _validate_params(self, params: Dict[str, Any]) -> ValidationResult:
        """Pre-validate parameters using Domain validation"""
        # Get parameter names from the request
        param_names = list(params.keys())
        
        # Validate all provided parameters
        return self._validator.validate(params, optional=param_names)
    
    def _get_parameter_hint_from_error(
        self, 
        error_msg: str, 
        params: Dict[str, Any]
    ) -> str:
        """Get parameter hints based on error message using Domain hints"""
        error_lower = error_msg.lower()
        param_names = list(params.keys())
        
        # Get hints from Domain validation layer
        hints = get_validation_hints(param_names)
        
        # Find relevant hints based on error message
        relevant_hints = []
        for param, hint in hints.items():
            if hint and (param.replace("_", " ") in error_lower or param in error_lower):
                relevant_hints.append(hint)
        
        if relevant_hints:
            return " ".join(relevant_hints) + " "
        return ""
    
    def _to_response(self, tool_id: str, result) -> CalculateResponse:
        """Convert ScoreResult to CalculateResponse"""
        # Build interpretation
        interpretation = None
        if result.interpretation:
            # Combine recommendations, warnings, next_steps into a single recommendation string
            all_recommendations = []
            if result.interpretation.recommendations:
                all_recommendations.extend(result.interpretation.recommendations)
            if result.interpretation.next_steps:
                all_recommendations.extend(result.interpretation.next_steps)
            
            recommendation_text = "; ".join(all_recommendations) if all_recommendations else None
            
            # Build details dict from interpretation fields
            details = {}
            if result.interpretation.detail:
                details["detail"] = result.interpretation.detail
            if result.interpretation.stage:
                details["stage"] = result.interpretation.stage
            if result.interpretation.stage_description:
                details["stage_description"] = result.interpretation.stage_description
            if result.interpretation.warnings:
                details["warnings"] = list(result.interpretation.warnings)
            if result.interpretation.risk_level:
                details["risk_level"] = result.interpretation.risk_level.value
            
            interpretation = InterpretationDTO(
                summary=result.interpretation.summary,
                severity=result.interpretation.severity.value if result.interpretation.severity else None,
                recommendation=recommendation_text,
                details=details
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
            score_name=result.tool_name,
            result=result.value,
            unit=str(result.unit) if result.unit else "",
            interpretation=interpretation,
            component_scores=result.calculation_details or {},
            references=references
        )
