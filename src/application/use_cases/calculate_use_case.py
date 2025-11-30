"""
Calculate Use Case

Application layer use case for executing calculations.
Provides clear error messages with valid input ranges.
"""

from typing import Any

from ..dto import (
    CalculateRequest,
    CalculateResponse,
    ReferenceDTO,
    InterpretationDTO,
)
from ...domain.registry.tool_registry import ToolRegistry


# Input validation hints for common parameters
PARAMETER_HINTS = {
    "gcs_score": "Valid range: 3-15 (Eye 1-4 + Verbal 1-5 + Motor 1-6)",
    "rass_score": "Valid range: -5 to +4 (-5=unarousable, 0=calm, +4=combative)",
    "temperature": "Valid range: 30.0-45.0 °C",
    "heart_rate": "Valid range: 20-300 bpm",
    "respiratory_rate": "Valid range: 0-100 breaths/min",
    "systolic_bp": "Valid range: 40-300 mmHg",
    "mean_arterial_pressure": "Valid range: 30-200 mmHg",
    "spo2": "Valid range: 50-100 %",
    "fio2": "Valid range: 0.21-1.0 (21%-100%)",
    "pao2_fio2_ratio": "Valid range: 0-700 mmHg (normal >400)",
    "serum_creatinine": "Valid range: 0.1-30.0 mg/dL",
    "creatinine": "Valid range: 0.1-30.0 mg/dL",
    "platelets": "Valid range: 0-2000 ×10³/µL",
    "bilirubin": "Valid range: 0-50 mg/dL",
    "age": "Valid range: 0-120 years",
    "weight_kg": "Valid range: 0.5-300 kg",
    "hematocrit": "Valid range: 10-70 %",
    "hemoglobin": "Valid range: 2-25 g/dL",
    "asa_class": "Valid range: 1-6 (I=healthy, VI=brain-dead)",
    "mallampati_class": "Valid range: 1-4 (I=easiest, IV=hardest)",
    "sex": "Valid values: 'male' or 'female'",
    "consciousness": "Valid values: A (Alert), V (Voice), P (Pain), U (Unresponsive), C (Confusion)",
}


class CalculateUseCase:
    """
    Use case for executing medical calculations.
    
    This use case:
    1. Validates the tool exists
    2. Executes the calculation
    3. Formats the response with clear error messages
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
                    error=f"Calculator '{request.tool_id}' not found. "
                          f"Available calculators: {', '.join(available)}. "
                          f"Use get_calculator_info(tool_id) to see details."
                )
            
            # Execute calculation
            result = calculator.calculate(**request.params)
            
            # Convert to response
            return self._to_response(request.tool_id, result)
            
        except TypeError as e:
            error_msg = str(e)
            hint = self._get_parameter_hint(error_msg)
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
            hint = self._get_parameter_hint(error_msg)
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
    
    def _get_parameter_hint(self, error_msg: str) -> str:
        """Get parameter hints based on error message"""
        error_lower = error_msg.lower()
        hints = []
        
        for param, hint in PARAMETER_HINTS.items():
            if param.replace("_", " ") in error_lower or param in error_lower:
                hints.append(hint)
        
        if hints:
            return " ".join(hints) + " "
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
