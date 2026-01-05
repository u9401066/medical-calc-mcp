"""
Domain Validation Module

Provides validation rules and validators for medical calculator inputs.

Architecture:
- rules.py: Base validation rules (RangeRule, EnumRule, etc.)
- parameter_specs.py: Parameter specifications with domain knowledge
- validators.py: Validator service for parameter validation

Usage:
    from src.domain.validation import validate_params, ValidationResult

    result = validate_params(
        params={"age": 65, "sex": "male", "serum_creatinine": 1.2},
        required=["age", "sex", "serum_creatinine"]
    )

    if not result.is_valid:
        print(result.get_error_message())
"""

from .parameter_specs import (
    COMMON_PARAMETERS,
    ParameterSpec,
    get_parameter_spec,
    validate_parameters,
)
from .rules import (
    CompositeRule,
    CustomRule,
    EnumRule,
    RangeRule,
    RequiredRule,
    TypeRule,
    ValidationRule,
)
from .validators import (
    ParameterValidator,
    ValidationError,
    ValidationResult,
    get_validation_hints,
    validate_params,
)

__all__ = [
    # Rules
    "ValidationRule",
    "RangeRule",
    "EnumRule",
    "RequiredRule",
    "TypeRule",
    "CustomRule",
    "CompositeRule",
    # Validators
    "ParameterValidator",
    "ValidationResult",
    "ValidationError",
    "validate_params",
    "get_validation_hints",
    # Specs
    "ParameterSpec",
    "COMMON_PARAMETERS",
    "get_parameter_spec",
    "validate_parameters",
]
