"""
Parameter Matcher Service

Intelligent parameter matching for calculator inputs.
Handles mismatches between user-provided param names and actual function signatures.

Features:
- Exact match
- Alias matching (creatinine → serum_creatinine)
- Suffix/prefix matching (cr → creatinine)
- Unit stripping (creatinine_mg_dl → creatinine)
- Fuzzy matching for typos

This enables a more forgiving API where users don't need to know exact param names.
"""

from __future__ import annotations

import inspect
import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Any, Optional

from ..services.base import BaseCalculator

# =============================================================================
# Parameter Aliases
# =============================================================================

# Common parameter aliases: canonical_name → [aliases]
# NOTE: Each alias should only appear once to avoid conflicts
PARAM_ALIASES: dict[str, list[str]] = {
    # Renal
    "serum_creatinine": ["creatinine", "cr", "scr", "serum_cr"],
    # NOTE: "creatinine" removed as separate entry - it's an alias of serum_creatinine
    "urine_output_24h": ["urine_output", "urine_24h", "uo_24h", "daily_urine"],
    # Cardiovascular
    "map_value": ["map", "mean_arterial_pressure", "mabp"],
    "systolic_bp": ["sbp", "systolic", "sys_bp"],
    "diastolic_bp": ["dbp", "diastolic", "dia_bp"],
    "heart_rate": ["hr", "pulse", "pulse_rate"],
    # Respiratory
    "pao2_fio2_ratio": ["pao2_fio2", "pf_ratio", "p_f_ratio", "pao2fio2"],
    "fio2": ["fio2_fraction", "oxygen_fraction", "fi_o2"],
    "respiratory_rate": ["rr", "resp_rate", "breaths_per_min"],
    "spo2": ["oxygen_saturation", "o2_sat", "sao2"],
    # Neurological
    "gcs_score": ["gcs", "glasgow_coma_scale", "glasgow_score"],
    "eye": ["eye_response", "eye_opening", "gcs_eye"],
    "verbal": ["verbal_response", "gcs_verbal"],
    "motor": ["motor_response", "gcs_motor"],
    # Laboratory
    "bilirubin": ["total_bilirubin", "bili", "tbili"],
    "platelets": ["platelet_count", "plt", "plts"],
    "hemoglobin": ["hgb", "hb"],
    "hematocrit": ["hct"],
    "wbc": ["white_blood_cells", "leukocytes", "wbc_count"],
    "sodium": ["na", "serum_sodium"],
    "potassium": ["k", "serum_potassium"],
    "chloride": ["cl", "serum_chloride"],
    "bicarbonate": ["hco3", "bicarb", "serum_bicarbonate"],
    "bun": ["blood_urea_nitrogen", "urea_nitrogen"],
    "glucose": ["blood_glucose", "serum_glucose", "bg"],
    "lactate": ["lactic_acid", "serum_lactate"],
    "albumin": ["serum_albumin", "alb"],
    "inr": ["pt_inr", "prothrombin_inr"],
    # Demographics
    "age": ["age_years", "patient_age"],
    "weight": ["body_weight", "weight_kg"],
    "height": ["body_height", "height_cm"],
    "sex": ["gender", "patient_sex"],
    # Medications
    "dopamine_dose": ["dopamine", "dopa_dose"],
    "dobutamine_any": ["dobutamine", "dobu"],
    "epinephrine_dose": ["epinephrine", "epi_dose", "adrenaline"],
    "norepinephrine_dose": ["norepinephrine", "norepi_dose", "noradrenaline"],
    # Ventilation
    "is_mechanically_ventilated": ["on_ventilator", "mechanical_ventilation", "intubated"],
    "peep": ["positive_end_expiratory_pressure"],
    "tidal_volume": ["vt", "tv"],
}

# Build reverse lookup: alias → canonical_name
_ALIAS_TO_CANONICAL: dict[str, str] = {}
for canonical, aliases in PARAM_ALIASES.items():
    for alias in aliases:
        if alias not in _ALIAS_TO_CANONICAL:
            _ALIAS_TO_CANONICAL[alias] = canonical
    # Also map canonical to itself
    _ALIAS_TO_CANONICAL[canonical] = canonical


# =============================================================================
# Unit Suffixes to Strip
# =============================================================================

UNIT_SUFFIXES = [
    "_mg_dl",
    "_mg/dl",
    "_mgdl",
    "_mmol_l",
    "_mmol/l",
    "_mmoll",
    "_g_dl",
    "_g/dl",
    "_gdl",
    "_mmhg",
    "_mm_hg",
    "_bpm",
    "_beats_per_min",
    "_ml",
    "_ml_min",
    "_ml/min",
    "_kg",
    "_cm",
    "_m",
    "_inches",
    "_mg_kg",
    "_mg/kg",  # dose per weight
    "_percent",
    "_pct",
    "_%",
    "_score",
    "_value",
    "_level",
    "_count",
    "_24h",
    "_24hr",
]


# =============================================================================
# Match Result
# =============================================================================


@dataclass
class ParamMatchResult:
    """Result of parameter matching."""

    success: bool
    matched_params: dict[str, Any] = field(default_factory=dict)
    unmatched_provided: list[str] = field(default_factory=list)
    missing_required: list[str] = field(default_factory=list)
    match_details: dict[str, str] = field(default_factory=dict)  # provided → matched
    suggestions: dict[str, list[str]] = field(default_factory=dict)  # unmatched → suggestions

    def to_error_dict(self) -> dict[str, Any]:
        """Convert to error response dict."""
        return {
            "success": False,
            "unmatched_params": self.unmatched_provided,
            "missing_required": self.missing_required,
            "match_details": self.match_details,
            "suggestions": self.suggestions,
        }


# =============================================================================
# Parameter Matcher
# =============================================================================


class ParamMatcher:
    """
    Intelligent parameter matcher for calculators.

    Matching strategies (in order):
    1. Exact match
    2. Alias lookup
    3. Suffix stripping (remove unit suffixes)
    4. Prefix/suffix partial match
    5. Fuzzy match (for typos)

    Usage:
        matcher = ParamMatcher()
        result = matcher.match(
            provided_params={"creatinine": 1.2, "age": 65},
            calculator=ckd_epi_calculator
        )
        if result.success:
            calculator.calculate(**result.matched_params)
    """

    def __init__(
        self,
        fuzzy_threshold: float = 0.8,
        allow_fuzzy: bool = True,
        strict_mode: bool = False,
    ):
        """
        Initialize matcher.

        Args:
            fuzzy_threshold: Minimum similarity for fuzzy matching (0-1)
            allow_fuzzy: Whether to allow fuzzy matching
            strict_mode: If True, fail on any unmatched param
        """
        self.fuzzy_threshold = fuzzy_threshold
        self.allow_fuzzy = allow_fuzzy
        self.strict_mode = strict_mode

    def match(
        self,
        provided_params: dict[str, Any],
        calculator: BaseCalculator,
    ) -> ParamMatchResult:
        """
        Match provided params to calculator's expected params.

        Args:
            provided_params: User-provided parameter dict
            calculator: Target calculator instance

        Returns:
            ParamMatchResult with matched params or error details
        """
        # Get expected params from calculator's calculate method signature
        expected_params = self._get_expected_params(calculator)
        required_params = self._get_required_params(calculator)

        matched: dict[str, Any] = {}
        match_details: dict[str, str] = {}
        unmatched: list[str] = []
        suggestions: dict[str, list[str]] = {}

        # Track which expected params have been matched
        matched_expected: set[str] = set()

        for provided_name, value in provided_params.items():
            matched_name = self._find_match(
                provided_name,
                expected_params,
                matched_expected,
            )

            if matched_name:
                matched[matched_name] = value
                match_details[provided_name] = matched_name
                matched_expected.add(matched_name)
            else:
                unmatched.append(provided_name)
                # Find suggestions
                sugg = self._find_suggestions(provided_name, expected_params)
                if sugg:
                    suggestions[provided_name] = sugg

        # Check for missing required params
        missing = [p for p in required_params if p not in matched_expected]

        # Determine success
        success = len(missing) == 0
        if self.strict_mode and unmatched:
            success = False

        return ParamMatchResult(
            success=success,
            matched_params=matched,
            unmatched_provided=unmatched,
            missing_required=missing,
            match_details=match_details,
            suggestions=suggestions,
        )

    def _get_expected_params(self, calculator: BaseCalculator) -> list[str]:
        """Get all parameter names from calculator's calculate method."""
        sig = inspect.signature(calculator.calculate)
        return [name for name, param in sig.parameters.items() if name != "self"]

    def _get_required_params(self, calculator: BaseCalculator) -> list[str]:
        """Get required (non-default) parameters."""
        sig = inspect.signature(calculator.calculate)
        return [name for name, param in sig.parameters.items() if name != "self" and param.default is inspect.Parameter.empty]

    def _find_match(
        self,
        provided_name: str,
        expected_params: list[str],
        already_matched: set[str],
    ) -> Optional[str]:
        """
        Find a match for provided_name in expected_params.

        Tries matching strategies in order of preference.
        """
        available = [p for p in expected_params if p not in already_matched]
        if not available:
            return None

        normalized = self._normalize(provided_name)

        # Strategy 1: Exact match
        if normalized in available:
            return normalized

        # Strategy 2: Alias lookup
        canonical = _ALIAS_TO_CANONICAL.get(normalized)
        if canonical and canonical in available:
            return canonical

        # Also check if any expected param is an alias of provided
        for expected in available:
            if expected in _ALIAS_TO_CANONICAL:
                if _ALIAS_TO_CANONICAL[expected] == normalized:
                    return expected
            # Check if provided is in expected's aliases
            if expected in PARAM_ALIASES:
                if normalized in PARAM_ALIASES[expected]:
                    return expected

        # Strategy 3: Strip unit suffixes
        stripped = self._strip_units(normalized)
        if stripped != normalized:
            if stripped in available:
                return stripped
            # Check aliases of stripped
            canonical = _ALIAS_TO_CANONICAL.get(stripped)
            if canonical and canonical in available:
                return canonical

        # Strategy 4: Prefix/suffix partial match
        for expected in available:
            exp_normalized = self._normalize(expected)
            # provided is suffix of expected (e.g., "creatinine" in "serum_creatinine")
            if exp_normalized.endswith(f"_{normalized}") or exp_normalized.endswith(normalized):
                return expected
            # provided is prefix of expected
            if exp_normalized.startswith(f"{normalized}_") or exp_normalized.startswith(normalized):
                return expected
            # expected is suffix of provided
            if normalized.endswith(f"_{exp_normalized}") or normalized.endswith(exp_normalized):
                return expected

        # Strategy 5: Fuzzy match
        if self.allow_fuzzy:
            best_match = None
            best_score = 0.0
            for expected in available:
                score = SequenceMatcher(None, normalized, self._normalize(expected)).ratio()
                if score > best_score and score >= self.fuzzy_threshold:
                    best_score = score
                    best_match = expected
            if best_match:
                return best_match

        return None

    def _find_suggestions(
        self,
        provided_name: str,
        expected_params: list[str],
        limit: int = 3,
    ) -> list[str]:
        """Find similar parameter names as suggestions."""
        normalized = self._normalize(provided_name)
        scored = []

        for expected in expected_params:
            score = SequenceMatcher(None, normalized, self._normalize(expected)).ratio()
            if score > 0.4:  # Minimum threshold for suggestions
                scored.append((expected, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [name for name, _ in scored[:limit]]

    def _normalize(self, name: str) -> str:
        """Normalize parameter name for matching."""
        # Lowercase
        name = name.lower()
        # Replace common separators
        name = name.replace("-", "_").replace(" ", "_")
        # Remove multiple underscores
        name = re.sub(r"_+", "_", name)
        # Strip leading/trailing underscores
        name = name.strip("_")
        return name

    def _strip_units(self, name: str) -> str:
        """Strip unit suffixes from parameter name."""
        for suffix in UNIT_SUFFIXES:
            if name.endswith(suffix):
                return name[: -len(suffix)]
        return name


# =============================================================================
# Parameter Template Generator
# =============================================================================


@dataclass
class ParamSpec:
    """Parameter specification for template generation."""

    name: str
    param_type: str
    required: bool
    default: Any = None
    description: str = ""
    unit: str = ""
    valid_range: Optional[tuple[float, float]] = None
    valid_options: Optional[list[str]] = None


def generate_param_template(calculator: BaseCalculator) -> dict[str, str]:
    """
    Generate a parameter template for a calculator.

    Returns a dict where keys are param names and values are
    type hints that agents can use to fill in values.

    Example:
        {
            "serum_creatinine": "<number: mg/dL, range 0.1-20>",
            "age": "<integer: years, range 18-120>",
            "sex": "<'male' | 'female'>"
        }
    """
    template: dict[str, str] = {}
    sig = inspect.signature(calculator.calculate)

    # Get type hints if available
    hints = {}
    try:
        hints = calculator.calculate.__annotations__
    except AttributeError:
        pass

    for name, param in sig.parameters.items():
        if name == "self":
            continue

        # Determine type string
        type_hint = hints.get(name)
        type_str = _get_type_string(type_hint, param.default)

        # Check if required
        is_required = param.default is inspect.Parameter.empty

        # Build template string
        if is_required:
            template[name] = f"<{type_str}> (required)"
        else:
            default_val = param.default
            if default_val is None:
                template[name] = f"<{type_str}> (optional)"
            else:
                template[name] = f"<{type_str}> (default: {default_val})"

    return template


def _get_type_string(type_hint: Any, default: Any) -> str:
    """Convert type hint to readable string."""
    if type_hint is not None:
        if type_hint is bool:
            return "true | false"
        elif type_hint is int:
            return "integer"
        elif type_hint is float:
            return "number"
        elif type_hint is str:
            return "string"
        elif hasattr(type_hint, "__origin__"):
            # Handle Optional, Union, etc.
            origin = type_hint.__origin__
            if origin is type(None):
                return "null"
            # For Optional[X], return X
            args = getattr(type_hint, "__args__", ())
            if args:
                non_none = [a for a in args if a is not type(None)]
                if non_none:
                    return _get_type_string(non_none[0], default)

    # Infer from default value
    if default is not None and default is not inspect.Parameter.empty:
        if isinstance(default, bool):
            return "true | false"
        elif isinstance(default, int):
            return "integer"
        elif isinstance(default, float):
            return "number"
        elif isinstance(default, str):
            return "string"

    return "any"


# =============================================================================
# Singleton / Convenience
# =============================================================================

_param_matcher: Optional[ParamMatcher] = None


def get_param_matcher() -> ParamMatcher:
    """Get singleton ParamMatcher instance."""
    global _param_matcher
    if _param_matcher is None:
        _param_matcher = ParamMatcher()
    return _param_matcher
