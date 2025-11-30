"""
Parameter Validators

Provides validation services for calculator inputs.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .rules import ValidationRule
from .parameter_specs import ParameterSpec, COMMON_PARAMETERS


@dataclass
class ValidationError:
    """Represents a single validation error"""
    param_name: str
    message: str
    value: Any = None
    hint: str = ""
    
    def to_dict(self) -> dict:
        return {
            "param": self.param_name,
            "message": self.message,
            "value": self.value,
            "hint": self.hint,
        }


@dataclass
class ValidationResult:
    """Result of validating parameters"""
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "valid": self.is_valid,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": self.warnings,
        }
    
    def get_error_message(self) -> str:
        """Get a formatted error message for all errors"""
        if not self.errors:
            return ""
        
        messages = []
        for error in self.errors:
            msg = f"{error.param_name}: {error.message}"
            if error.hint:
                msg += f" ({error.hint})"
            messages.append(msg)
        
        return "; ".join(messages)


class ParameterValidator:
    """
    Validates calculator input parameters.
    
    This validator can be used at the Application layer to validate
    inputs before passing to Domain calculators.
    """
    
    def __init__(self, specs: Optional[Dict[str, ParameterSpec]] = None):
        """
        Initialize validator with parameter specifications.
        
        Args:
            specs: Custom specs, or None to use COMMON_PARAMETERS
        """
        self._specs = specs or COMMON_PARAMETERS
    
    def validate(
        self,
        params: Dict[str, Any],
        required: Optional[List[str]] = None,
        optional: Optional[List[str]] = None,
    ) -> ValidationResult:
        """
        Validate parameters against specifications.
        
        Args:
            params: Dictionary of parameter values
            required: List of required parameter names
            optional: List of optional parameter names
            
        Returns:
            ValidationResult with errors and warnings
        """
        errors: List[ValidationError] = []
        warnings: List[str] = []
        
        # Validate required parameters
        if required:
            for param_name in required:
                if param_name not in params or params[param_name] is None:
                    spec = self._specs.get(param_name)
                    hint = spec.to_hint() if spec else ""
                    errors.append(ValidationError(
                        param_name=param_name,
                        message="This parameter is required",
                        value=None,
                        hint=hint,
                    ))
                    continue
                
                # Validate against spec if available
                error = self._validate_param(param_name, params[param_name])
                if error:
                    errors.append(error)
        
        # Validate optional parameters (only if provided)
        if optional:
            for param_name in optional:
                if param_name in params and params[param_name] is not None:
                    error = self._validate_param(param_name, params[param_name])
                    if error:
                        errors.append(error)
        
        # Validate any other provided parameters
        all_specified = set(required or []) | set(optional or [])
        for param_name, value in params.items():
            if param_name not in all_specified and value is not None:
                error = self._validate_param(param_name, value)
                if error:
                    errors.append(error)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )
    
    def _validate_param(
        self,
        param_name: str,
        value: Any
    ) -> Optional[ValidationError]:
        """Validate a single parameter"""
        spec = self._specs.get(param_name)
        
        if spec is None:
            # No spec available, skip validation
            return None
        
        is_valid, error_messages = spec.validate(value)
        
        if not is_valid and error_messages:
            return ValidationError(
                param_name=param_name,
                message=error_messages[0],  # Take first error
                value=value,
                hint=spec.to_hint(),
            )
        
        return None
    
    def get_hint(self, param_name: str) -> str:
        """Get a hint string for a parameter"""
        spec = self._specs.get(param_name)
        if spec:
            return spec.to_hint()
        return ""
    
    def get_all_hints(self, param_names: List[str]) -> Dict[str, str]:
        """Get hints for multiple parameters"""
        return {name: self.get_hint(name) for name in param_names}


# =============================================================================
# Convenience Functions
# =============================================================================

def validate_params(
    params: Dict[str, Any],
    required: Optional[List[str]] = None,
    optional: Optional[List[str]] = None,
) -> ValidationResult:
    """
    Quick validation using common parameters.
    
    Args:
        params: Parameter values
        required: Required parameter names
        optional: Optional parameter names
        
    Returns:
        ValidationResult
    """
    validator = ParameterValidator()
    return validator.validate(params, required, optional)


def get_validation_hints(param_names: List[str]) -> Dict[str, str]:
    """Get validation hints for a list of parameters"""
    validator = ParameterValidator()
    return validator.get_all_hints(param_names)
