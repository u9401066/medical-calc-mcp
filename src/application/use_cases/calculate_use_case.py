"""Application layer use case for executing calculations with smart recovery hints."""

from typing import Any

from ...domain.entities.score_result import ScoreResult
from ...domain.registry.tool_registry import ToolRegistry
from ...domain.services.param_matcher import (
    generate_param_template,
    get_param_matcher,
)
from ...domain.validation import (
    ParameterValidator,
    ValidationResult,
    get_validation_hints,
)
from ...domain.validation.boundaries import (
    ValidationSeverity,
    get_boundary_registry,
)
from ...shared.smart_input import ResolutionResult, resolve_identifier
from ..dto import (
    CalculateRequest,
    CalculateResponse,
    InterpretationDTO,
    ReferenceDTO,
)


class CalculateUseCase:
    """
    Use case for executing medical calculations.

    This use case:
    1. Intelligently matches provided params to expected params
    2. Validates inputs using Domain validation layer
    3. Executes the calculation
    4. Formats the response with clear error messages

    Parameter Matching:
    - Exact match: "creatinine" → "creatinine"
    - Alias match: "cr" → "serum_creatinine"
    - Suffix match: "creatinine" → "serum_creatinine"
    - Fuzzy match: "creatnine" → "creatinine" (typo tolerance)
    """

    def __init__(self, registry: ToolRegistry):
        self._registry = registry
        self._validator = ParameterValidator()
        self._param_matcher = get_param_matcher()
        self._boundary_registry = get_boundary_registry()

    def execute(self, request: CalculateRequest) -> CalculateResponse:
        """
        Execute a calculation with intelligent parameter matching.

        Args:
            request: CalculateRequest with tool_id and params

        Returns:
            CalculateResponse with result or detailed error
        """
        resolved_tool_id = request.tool_id
        try:
            tool_resolution = resolve_identifier(request.tool_id, self._registry.list_all_ids())
            resolved_tool_id = tool_resolution.resolved_value or request.tool_id

            # Get calculator
            calculator = self._registry.get_calculator(resolved_tool_id)
            if calculator is None:
                return self._tool_not_found_response(request.tool_id, tool_resolution)

            if not request.params:
                return self._empty_params_response(
                    resolved_tool_id,
                    calculator,
                    supplied_tool_id=request.tool_id,
                )

            # Step 1: Intelligent parameter matching
            match_result = self._param_matcher.match(
                provided_params=request.params,
                calculator=calculator,
            )

            if not match_result.success:
                return self._param_mismatch_response(
                    resolved_tool_id,
                    match_result,
                    calculator,
                    supplied_tool_id=request.tool_id,
                )

            # Use matched params
            matched_params = match_result.matched_params

            # Step 2: Boundary validation (clinical range check)
            boundary_warnings = self._validate_boundaries(matched_params)

            # Step 3: Pre-validate using domain validation
            validation_result = self._validate_params(matched_params)
            if not validation_result.is_valid:
                return CalculateResponse(
                    success=False,
                    tool_id=resolved_tool_id,
                    score_name="",
                    result=None,
                    unit="",
                    error=(f"Validation error: {validation_result.get_error_message()}. Use get_tool_schema('{resolved_tool_id}') for parameters."),
                    component_scores={
                        "param_template": generate_param_template(calculator),
                        "expected_params": self._get_expected_params(calculator),
                    },
                    guidance=self._build_guidance(
                        resolved_tool_id,
                        calculator,
                        supplied_tool_id=request.tool_id,
                    ),
                )

            # Step 4: Execute calculation with matched params
            result = calculator.calculate(**matched_params)

            # Step 5: Convert to response (include match details if aliases were used)
            response = self._to_response(resolved_tool_id, result, boundary_warnings)

            # Add match details if any aliasing occurred
            if match_result.match_details:
                aliased = {k: v for k, v in match_result.match_details.items() if k != v}
                if aliased and response.component_scores is not None:
                    response.component_scores["_param_mapping"] = aliased

            if resolved_tool_id != request.tool_id and response.component_scores is not None:
                response.component_scores["_tool_resolved_from"] = request.tool_id
                response.guidance = self._build_guidance(
                    resolved_tool_id,
                    calculator,
                    supplied_tool_id=request.tool_id,
                )

            return response

        except TypeError as e:
            return self._type_error_response(request, str(e))
        except ValueError as e:
            return self._value_error_response(request, str(e))
        except Exception as e:
            return CalculateResponse(
                success=False,
                tool_id=resolved_tool_id,
                score_name="",
                result=None,
                unit="",
                error=f"Calculation error: {str(e)}. Please check input values and try again.",
            )

    def _tool_not_found_response(self, tool_id: str, resolution: ResolutionResult) -> CalculateResponse:
        """Generate response for tool not found."""
        error = f"Calculator '{tool_id}' not found."
        if resolution.ambiguous_matches:
            error += f" Ambiguous input. Possible matches: {', '.join(resolution.ambiguous_matches)}."
        elif resolution.suggestions:
            error += f" Did you mean: {', '.join(resolution.suggestions)}?"
        error += " Use discover(by='keyword', value='...') or discover(by='tools') to find available tools. Legacy aliases: search_calculators('...') or list_calculators()."

        return CalculateResponse(
            success=False,
            tool_id=tool_id,
            score_name="",
            result=None,
            unit="",
            error=error,
            guidance={
                "normalized_input": resolution.normalized_value,
                "suggestions": list(resolution.suggestions),
                "next_actions": [
                    "discover(by='keyword', value='關鍵字')",
                    "discover(by='tools')",
                    "search_calculators('關鍵字')",
                    "list_calculators()",
                ],
            },
        )

    def _empty_params_response(
        self,
        tool_id: str,
        calculator: Any,
        *,
        supplied_tool_id: str,
    ) -> CalculateResponse:
        """Generate a dedicated empty-input response with fillable guidance."""
        template = generate_param_template(calculator)
        error = f"No parameters provided for '{tool_id}'. Fill the required fields before calculating."
        if supplied_tool_id != tool_id:
            error += f" Resolved requested tool '{supplied_tool_id}' to '{tool_id}'."

        return CalculateResponse(
            success=False,
            tool_id=tool_id,
            score_name="",
            result=None,
            unit="",
            error=error,
            component_scores={
                "param_template": template,
                "expected_params": self._get_expected_params(calculator),
                "required_params": self._get_required_params(calculator),
            },
            guidance=self._build_guidance(tool_id, calculator, supplied_tool_id=supplied_tool_id),
        )

    def _param_mismatch_response(
        self,
        tool_id: str,
        match_result: Any,
        calculator: Any,
        *,
        supplied_tool_id: str | None = None,
    ) -> CalculateResponse:
        """Generate detailed response for parameter mismatch."""
        # Generate param template
        template = generate_param_template(calculator)

        error_parts = []

        if match_result.missing_required:
            error_parts.append(f"Missing required parameters: {', '.join(match_result.missing_required)}")

        if match_result.unmatched_provided:
            unmatched_str = ", ".join(match_result.unmatched_provided)
            error_parts.append(f"Unknown parameters: {unmatched_str}")

            # Add suggestions
            for param, suggestions in match_result.suggestions.items():
                if suggestions:
                    error_parts.append(f"  '{param}' → did you mean: {', '.join(suggestions)}?")

        error_msg = ". ".join(error_parts)
        if supplied_tool_id and supplied_tool_id != tool_id:
            error_msg = f"Resolved tool '{supplied_tool_id}' to '{tool_id}'. {error_msg}"

        return CalculateResponse(
            success=False,
            tool_id=tool_id,
            score_name="",
            result=None,
            unit="",
            error=error_msg,
            component_scores={
                "param_template": template,
                "expected_params": list(template.keys()),
                "provided_params": list(match_result.match_details.keys()) + match_result.unmatched_provided,
                "hint": f"Use get_tool_schema('{tool_id}') to see full parameter documentation.",
            },
            guidance=self._build_guidance(
                tool_id,
                calculator,
                supplied_tool_id=supplied_tool_id,
                unmatched_params=match_result.unmatched_provided,
                missing_required=match_result.missing_required,
            ),
        )

    def _type_error_response(
        self,
        request: CalculateRequest,
        error_msg: str,
    ) -> CalculateResponse:
        """Generate response for type errors."""
        hint = self._get_parameter_hint_from_error(error_msg, request.params)

        # Try to get param template
        calculator = self._registry.get_calculator(request.tool_id)
        template = {}
        if calculator:
            template = generate_param_template(calculator)
        guidance = self._build_guidance(request.tool_id, calculator) if calculator else {}

        return CalculateResponse(
            success=False,
            tool_id=request.tool_id,
            score_name="",
            result=None,
            unit="",
            error=f"Invalid parameters: {error_msg}. {hint}",
            component_scores={
                "param_template": template,
                "hint": f"Use get_tool_schema('{request.tool_id}') to see required parameters.",
            },
            guidance=guidance,
        )

    def _value_error_response(
        self,
        request: CalculateRequest,
        error_msg: str,
    ) -> CalculateResponse:
        """Generate response for value errors."""
        hint = self._get_parameter_hint_from_error(error_msg, request.params)
        calculator = self._registry.get_calculator(request.tool_id)
        return CalculateResponse(
            success=False,
            tool_id=request.tool_id,
            score_name="",
            result=None,
            unit="",
            error=f"Validation error: {error_msg}. {hint}",
            component_scores={
                "param_template": generate_param_template(calculator) if calculator else {},
            },
            guidance=self._build_guidance(request.tool_id, calculator) if calculator else {},
        )

    def _get_expected_params(self, calculator: Any) -> list[str]:
        return self._param_matcher._get_expected_params(calculator)

    def _get_required_params(self, calculator: Any) -> list[str]:
        return self._param_matcher._get_required_params(calculator)

    def _build_guidance(
        self,
        tool_id: str,
        calculator: Any | None,
        *,
        supplied_tool_id: str | None = None,
        unmatched_params: list[str] | None = None,
        missing_required: list[str] | None = None,
    ) -> dict[str, Any]:
        """Build structured next-step guidance for MCP clients and agents."""
        guidance: dict[str, Any] = {
            "next_actions": [
                f"get_tool_schema('{tool_id}')",
                f"calculate('{tool_id}', {{...}})",
            ]
        }
        if supplied_tool_id and supplied_tool_id != tool_id:
            guidance["resolved_tool_id"] = tool_id
            guidance["supplied_tool_id"] = supplied_tool_id
        if calculator is not None:
            guidance["required_params"] = self._get_required_params(calculator)
        if unmatched_params:
            guidance["unmatched_params"] = unmatched_params
        if missing_required:
            guidance["missing_required"] = missing_required
        return guidance

    def _validate_boundaries(
        self,
        params: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Validate parameters against clinical boundaries.

        Returns a list of warnings/errors for values outside expected ranges.
        Each warning includes the parameter name, value, severity, message,
        and literature reference.

        This provides automatic "sanity check" for common clinical parameters
        based on physiological limits and literature-backed normal ranges.
        """
        warnings: list[dict[str, Any]] = []

        results = self._boundary_registry.validate_all(params)

        for boundary_result in results:
            if boundary_result.severity in (ValidationSeverity.WARNING, ValidationSeverity.ERROR):
                warning_entry: dict[str, Any] = {
                    "parameter": boundary_result.param_name,
                    "value": boundary_result.value,
                    "severity": boundary_result.severity.value,
                    "message": boundary_result.message,
                }
                # Add reference if available from boundary_spec
                if boundary_result.boundary_spec and boundary_result.boundary_spec.reference:
                    ref = boundary_result.boundary_spec.reference
                    warning_entry["reference"] = {
                        "source": ref.source,
                        "citation": ref.citation,
                    }
                    if ref.pmid:
                        warning_entry["reference"]["pmid"] = ref.pmid
                warnings.append(warning_entry)
            elif boundary_result.severity == ValidationSeverity.CRITICAL:
                # Critical values get special treatment
                warnings.append(
                    {
                        "parameter": boundary_result.param_name,
                        "value": boundary_result.value,
                        "severity": "CRITICAL",
                        "message": f"⚠️ CRITICAL: {boundary_result.message}",
                        "action_required": True,
                    }
                )

        return warnings

    def _validate_params(self, params: dict[str, Any]) -> ValidationResult:
        """Pre-validate parameters using Domain validation

        Only validates parameters that are defined in COMMON_PARAMETERS.
        Calculator-specific parameters with the same name but different
        types (e.g., consciousness in Aldrete vs NEWS2) are handled by
        the calculator's own type checking.
        """
        from ...domain.validation.parameter_specs import COMMON_PARAMETERS

        # Only validate parameters that are in COMMON_PARAMETERS
        # and have matching expected types/rules
        known_params = [p for p in params.keys() if p in COMMON_PARAMETERS]

        # For parameters with potential type conflicts (like 'consciousness'),
        # check if the value matches the expected type before validating
        safe_params = []
        for param in known_params:
            spec = COMMON_PARAMETERS[param]
            value = params[param]
            # Skip validation if the value type doesn't match the spec type
            # This allows calculator-specific overrides
            if spec.param_type is str and not isinstance(value, str):
                continue
            if spec.param_type is int and not isinstance(value, (int, bool)):
                continue
            if spec.param_type is float and not isinstance(value, (int, float)):
                continue
            safe_params.append(param)

        # Validate only safe parameters
        return self._validator.validate(params, optional=safe_params)

    def _get_parameter_hint_from_error(self, error_msg: str, params: dict[str, Any]) -> str:
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

    def _to_response(
        self,
        tool_id: str,
        result: ScoreResult,
        boundary_warnings: list[dict[str, Any]] | None = None,
    ) -> CalculateResponse:
        """Convert ScoreResult to CalculateResponse with optional boundary warnings"""
        # Build interpretation
        interpretation = None
        if result.interpretation:
            # Combine recommendations, warnings, next_steps into a single recommendation string
            all_recommendations: list[str] = []
            if result.interpretation.recommendations:
                all_recommendations.extend(result.interpretation.recommendations)
            if result.interpretation.next_steps:
                all_recommendations.extend(result.interpretation.next_steps)

            recommendation_text = "; ".join(all_recommendations) if all_recommendations else None

            # Build details dict from interpretation fields
            details: dict[str, Any] = {}
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
                details=details,
            )

        # Build references
        references = [ReferenceDTO(citation=ref.citation, doi=ref.doi, pmid=ref.pmid, year=ref.year) for ref in (result.references or [])]

        # Build component_scores with boundary warnings
        component_scores = result.calculation_details.copy() if result.calculation_details else {}
        if boundary_warnings:
            component_scores["_boundary_warnings"] = boundary_warnings

        return CalculateResponse(
            success=True,
            tool_id=tool_id,
            score_name=result.tool_name,
            result=result.value,
            unit=str(result.unit) if result.unit else "",
            interpretation=interpretation,
            component_scores=component_scores,
            references=references,
        )
