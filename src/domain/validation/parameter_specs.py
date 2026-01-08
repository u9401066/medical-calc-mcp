"""
Parameter Specifications

Defines common medical parameter specifications with validation rules.
This is domain knowledge about valid ranges for clinical measurements.
"""

from dataclasses import dataclass, field
from typing import Any, Optional

from .rules import EnumRule, RangeRule, ValidationRule


@dataclass
class ParameterSpec:
    """
    Specification for a medical calculator parameter.

    Attributes:
        name: Parameter name (snake_case)
        display_name: Human-readable name (中英文)
        description: Full description with clinical context
        param_type: Expected Python type
        rules: List of validation rules
        unit: Unit of measurement
        default: Default value (None = required)
        examples: Example values for documentation
    """

    name: str
    display_name: str
    description: str
    param_type: type
    rules: list[ValidationRule] = field(default_factory=list)
    unit: str = ""
    default: Any = None
    examples: tuple[Any, ...] = ()

    @property
    def is_required(self) -> bool:
        return self.default is None

    def validate(self, value: Any) -> tuple[bool, list[str]]:
        """
        Validate a value against all rules.

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        # Check required
        if value is None:
            if self.is_required:
                errors.append(f"{self.display_name} is required")
            return len(errors) == 0, errors

        # Check all rules
        for rule in self.rules:
            is_valid, error = rule.validate(value)
            if not is_valid and error:
                errors.append(error)

        return len(errors) == 0, errors

    def to_hint(self) -> str:
        """Generate a hint string for error messages"""
        parts = [self.display_name]

        for rule in self.rules:
            if isinstance(rule, RangeRule):
                if rule.min_value is not None and rule.max_value is not None:
                    parts.append(f"({rule.min_value}-{rule.max_value}{rule.unit})")
                elif rule.min_value is not None:
                    parts.append(f"(≥{rule.min_value}{rule.unit})")
                elif rule.max_value is not None:
                    parts.append(f"(≤{rule.max_value}{rule.unit})")
            elif isinstance(rule, EnumRule):
                parts.append(f"({', '.join(str(v) for v in rule.allowed_values)})")

        return " ".join(parts)


# =============================================================================
# Common Medical Parameters
# =============================================================================

COMMON_PARAMETERS: dict[str, ParameterSpec] = {
    # Vital Signs
    "temperature": ParameterSpec(
        name="temperature",
        display_name="體溫 Temperature",
        description="Body temperature in Celsius",
        param_type=float,
        rules=[RangeRule(min_value=30.0, max_value=45.0, unit="°C")],
        unit="°C",
        examples=(36.5, 37.0, 38.5),
    ),
    "heart_rate": ParameterSpec(
        name="heart_rate",
        display_name="心率 Heart Rate",
        description="Heart rate in beats per minute",
        param_type=int,
        rules=[RangeRule(min_value=20, max_value=300, unit=" bpm")],
        unit="bpm",
        examples=(60, 80, 100),
    ),
    "respiratory_rate": ParameterSpec(
        name="respiratory_rate",
        display_name="呼吸速率 Respiratory Rate",
        description="Respiratory rate in breaths per minute",
        param_type=int,
        rules=[RangeRule(min_value=0, max_value=100, unit=" breaths/min")],
        unit="breaths/min",
        examples=(12, 16, 22),
    ),
    "systolic_bp": ParameterSpec(
        name="systolic_bp",
        display_name="收縮壓 Systolic BP",
        description="Systolic blood pressure in mmHg",
        param_type=int,
        rules=[RangeRule(min_value=40, max_value=300, unit=" mmHg")],
        unit="mmHg",
        examples=(90, 120, 140),
    ),
    "mean_arterial_pressure": ParameterSpec(
        name="mean_arterial_pressure",
        display_name="平均動脈壓 MAP",
        description="Mean arterial pressure in mmHg",
        param_type=float,
        rules=[RangeRule(min_value=30, max_value=200, unit=" mmHg")],
        unit="mmHg",
        examples=(65, 80, 95),
    ),
    "spo2": ParameterSpec(
        name="spo2",
        display_name="血氧飽和度 SpO2",
        description="Peripheral oxygen saturation percentage",
        param_type=int,
        rules=[RangeRule(min_value=50, max_value=100, unit="%")],
        unit="%",
        examples=(92, 96, 99),
    ),
    # Oxygenation
    "fio2": ParameterSpec(
        name="fio2",
        display_name="吸入氧濃度 FiO2",
        description="Fraction of inspired oxygen (0.21-1.0)",
        param_type=float,
        rules=[RangeRule(min_value=0.21, max_value=1.0)],
        unit="",
        examples=(0.21, 0.4, 1.0),
    ),
    "pao2_fio2_ratio": ParameterSpec(
        name="pao2_fio2_ratio",
        display_name="PaO2/FiO2 比值",
        description="PaO2/FiO2 ratio in mmHg (normal >400)",
        param_type=float,
        rules=[RangeRule(min_value=0, max_value=700, unit=" mmHg")],
        unit="mmHg",
        examples=(100, 200, 400),
    ),
    # Laboratory Values
    "serum_creatinine": ParameterSpec(
        name="serum_creatinine",
        display_name="血清肌酐 Creatinine",
        description="Serum creatinine in mg/dL",
        param_type=float,
        rules=[RangeRule(min_value=0.1, max_value=30.0, unit=" mg/dL")],
        unit="mg/dL",
        examples=(0.8, 1.2, 2.5),
    ),
    "creatinine": ParameterSpec(
        name="creatinine",
        display_name="肌酐 Creatinine",
        description="Creatinine in mg/dL",
        param_type=float,
        rules=[RangeRule(min_value=0.1, max_value=30.0, unit=" mg/dL")],
        unit="mg/dL",
        examples=(0.8, 1.2, 2.5),
    ),
    "platelets": ParameterSpec(
        name="platelets",
        display_name="血小板 Platelets",
        description="Platelet count in ×10³/µL",
        param_type=float,
        rules=[RangeRule(min_value=0, max_value=2000, unit=" ×10³/µL")],
        unit="×10³/µL",
        examples=(50, 150, 300),
    ),
    "bilirubin": ParameterSpec(
        name="bilirubin",
        display_name="膽紅素 Bilirubin",
        description="Total bilirubin in mg/dL",
        param_type=float,
        rules=[RangeRule(min_value=0, max_value=50, unit=" mg/dL")],
        unit="mg/dL",
        examples=(0.5, 1.2, 5.0),
    ),
    "hematocrit": ParameterSpec(
        name="hematocrit",
        display_name="血球容積比 Hematocrit",
        description="Hematocrit percentage",
        param_type=float,
        rules=[RangeRule(min_value=10, max_value=70, unit="%")],
        unit="%",
        examples=(30, 40, 45),
    ),
    "hemoglobin": ParameterSpec(
        name="hemoglobin",
        display_name="血紅素 Hemoglobin",
        description="Hemoglobin in g/dL",
        param_type=float,
        rules=[RangeRule(min_value=2, max_value=25, unit=" g/dL")],
        unit="g/dL",
        examples=(8, 12, 15),
    ),
    # Demographics
    "age": ParameterSpec(
        name="age",
        display_name="年齡 Age",
        description="Patient age in years",
        param_type=int,
        rules=[RangeRule(min_value=0, max_value=120, unit=" years")],
        unit="years",
        examples=(25, 50, 75),
    ),
    "weight_kg": ParameterSpec(
        name="weight_kg",
        display_name="體重 Weight",
        description="Patient weight in kilograms",
        param_type=float,
        rules=[RangeRule(min_value=0.5, max_value=500, unit=" kg")],
        unit="kg",
        examples=(10, 70, 100),
    ),
    "sex": ParameterSpec(
        name="sex",
        display_name="性別 Sex",
        description="Patient biological sex",
        param_type=str,
        rules=[EnumRule(allowed_values=("male", "female"), case_sensitive=False)],
        unit="",
        examples=("male", "female"),
    ),
    # Scores
    "gcs_score": ParameterSpec(
        name="gcs_score",
        display_name="GCS 昏迷指數",
        description="Glasgow Coma Scale (Eye + Verbal + Motor)",
        param_type=int,
        rules=[RangeRule(min_value=3, max_value=15)],
        unit="",
        examples=(3, 8, 15),
    ),
    "rass_score": ParameterSpec(
        name="rass_score",
        display_name="RASS 鎮靜評估",
        description="Richmond Agitation-Sedation Scale",
        param_type=int,
        rules=[RangeRule(min_value=-5, max_value=4)],
        unit="",
        examples=(-5, 0, 4),
    ),
    # Classification
    "asa_class": ParameterSpec(
        name="asa_class",
        display_name="ASA 分級",
        description="ASA Physical Status Classification",
        param_type=int,
        rules=[RangeRule(min_value=1, max_value=6)],
        unit="",
        examples=(1, 2, 3),
    ),
    "mallampati_class": ParameterSpec(
        name="mallampati_class",
        display_name="Mallampati 分級",
        description="Mallampati airway classification",
        param_type=int,
        rules=[RangeRule(min_value=1, max_value=4)],
        unit="",
        examples=(1, 2, 3, 4),
    ),
    "consciousness": ParameterSpec(
        name="consciousness",
        display_name="意識狀態 AVPU",
        description="Level of consciousness (AVPU scale)",
        param_type=str,
        rules=[EnumRule(allowed_values=("A", "V", "P", "U", "C"), case_sensitive=False)],
        unit="",
        examples=("A", "V", "P", "U"),
    ),
}


def get_parameter_spec(param_name: str) -> Optional[ParameterSpec]:
    """Get the specification for a common parameter"""
    return COMMON_PARAMETERS.get(param_name)


def validate_parameters(params: dict[str, Any], specs: dict[str, ParameterSpec]) -> tuple[bool, dict[str, list[str]]]:
    """
    Validate multiple parameters against their specifications.

    Args:
        params: Dictionary of parameter name -> value
        specs: Dictionary of parameter name -> ParameterSpec

    Returns:
        Tuple of (all_valid, dict of param_name -> list of errors)
    """
    all_errors: dict[str, list[str]] = {}

    for name, spec in specs.items():
        value = params.get(name, spec.default)
        is_valid, errors = spec.validate(value)
        if not is_valid:
            all_errors[name] = errors

    return len(all_errors) == 0, all_errors
