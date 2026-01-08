"""
Domain Validation Rules

Defines validation rules for medical calculator parameters.
These rules encode domain knowledge about valid input ranges.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Optional


class ValidationRule(ABC):
    """Abstract base class for validation rules"""

    @abstractmethod
    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        """
        Validate a value.

        Returns:
            Tuple of (is_valid, error_message)
            error_message is None if valid
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of the rule"""
        pass


@dataclass
class RangeRule(ValidationRule):
    """Validates that a numeric value is within a range"""

    min_value: Optional[float] = None
    max_value: Optional[float] = None
    min_inclusive: bool = True
    max_inclusive: bool = True
    unit: str = ""

    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        if value is None:
            return True, None  # None values handled by RequiredRule

        try:
            num_value = float(value)
        except (TypeError, ValueError):
            return False, f"Value must be a number, got {type(value).__name__}"

        if self.min_value is not None:
            if self.min_inclusive:
                if num_value < self.min_value:
                    return False, f"Value {num_value} is below minimum {self.min_value}{self.unit}"
            else:
                if num_value <= self.min_value:
                    return False, f"Value {num_value} must be greater than {self.min_value}{self.unit}"

        if self.max_value is not None:
            if self.max_inclusive:
                if num_value > self.max_value:
                    return False, f"Value {num_value} exceeds maximum {self.max_value}{self.unit}"
            else:
                if num_value >= self.max_value:
                    return False, f"Value {num_value} must be less than {self.max_value}{self.unit}"

        return True, None

    @property
    def description(self) -> str:
        parts = []
        if self.min_value is not None:
            op = "≥" if self.min_inclusive else ">"
            parts.append(f"{op}{self.min_value}")
        if self.max_value is not None:
            op = "≤" if self.max_inclusive else "<"
            parts.append(f"{op}{self.max_value}")

        range_str = " and ".join(parts) if parts else "any value"
        return f"{range_str}{self.unit}"


@dataclass
class EnumRule(ValidationRule):
    """Validates that a value is one of the allowed options"""

    allowed_values: tuple[Any, ...]
    case_sensitive: bool = False

    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        if value is None:
            return True, None

        check_value = value
        check_against = self.allowed_values

        if not self.case_sensitive and isinstance(value, str):
            check_value = value.lower()
            check_against = tuple(
                v.lower() if isinstance(v, str) else v
                for v in self.allowed_values
            )

        if check_value not in check_against:
            return False, f"Value '{value}' not in allowed values: {self.allowed_values}"

        return True, None

    @property
    def description(self) -> str:
        return f"One of: {', '.join(str(v) for v in self.allowed_values)}"


@dataclass
class RequiredRule(ValidationRule):
    """Validates that a value is provided (not None)"""

    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        if value is None:
            return False, "This field is required"
        return True, None

    @property
    def description(self) -> str:
        return "Required"


@dataclass
class TypeRule(ValidationRule):
    """Validates that a value is of a specific type"""

    expected_type: type
    type_name: str = ""

    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        if value is None:
            return True, None

        # Handle numeric type conversions
        if self.expected_type in (int, float):
            try:
                if self.expected_type is int:
                    # Check if it's actually an integer value
                    if isinstance(value, float) and not value.is_integer():
                        return False, f"Expected integer, got float {value}"
                float(value)  # This will raise if not numeric
                return True, None
            except (TypeError, ValueError):
                type_name = self.type_name or self.expected_type.__name__
                return False, f"Expected {type_name}, got {type(value).__name__}"

        if not isinstance(value, self.expected_type):
            type_name = self.type_name or self.expected_type.__name__
            return False, f"Expected {type_name}, got {type(value).__name__}"

        return True, None

    @property
    def description(self) -> str:
        return self.type_name or self.expected_type.__name__


@dataclass
class CustomRule(ValidationRule):
    """Custom validation rule with a callable validator"""

    validator: Callable[[Any], tuple[bool, Optional[str]]]
    desc: str = "Custom validation"

    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        return self.validator(value)

    @property
    def description(self) -> str:
        return self.desc


# =============================================================================
# Composite Rules
# =============================================================================

@dataclass
class CompositeRule(ValidationRule):
    """Combines multiple rules with AND logic"""

    rules: list[ValidationRule]

    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        for rule in self.rules:
            is_valid, error = rule.validate(value)
            if not is_valid:
                return False, error
        return True, None

    @property
    def description(self) -> str:
        return "; ".join(r.description for r in self.rules)
