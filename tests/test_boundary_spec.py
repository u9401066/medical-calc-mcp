"""
Tests for BoundarySpec Module - 邊界檢查模組測試

Tests the clinical parameter boundary validation system.
"""

import pytest

from src.domain.validation.boundaries import (
    BoundaryRegistry,
    BoundarySpec,
    BoundaryReference,
    EvidenceLevel,
    ValidationSeverity,
    ValidationResult,
    CLINICAL_BOUNDARIES,
    get_boundary,
    get_boundary_registry,
    validate_param,
    HARRISON_REFERENCE,
    KDIGO_REFERENCE,
)


# =============================================================================
# BoundaryReference Tests
# =============================================================================


class TestBoundaryReference:
    """Test BoundaryReference dataclass"""

    def test_reference_creation(self):
        """Test creating a reference"""
        ref = BoundaryReference(
            source="Test Source",
            citation="Test Author. Test Journal. 2025.",
            year=2025,
            level_of_evidence=EvidenceLevel.A,
            pmid="12345678"
        )
        assert ref.source == "Test Source"
        assert ref.year == 2025
        assert ref.level_of_evidence == EvidenceLevel.A
        assert ref.pmid == "12345678"

    def test_reference_to_dict(self):
        """Test reference serialization"""
        ref = HARRISON_REFERENCE
        d = ref.to_dict()
        assert "source" in d
        assert "citation" in d
        assert "year" in d
        assert "level_of_evidence" in d

    def test_kdigo_reference_has_pmid(self):
        """Test KDIGO reference has PMID"""
        assert KDIGO_REFERENCE.pmid == "38490803"
        assert KDIGO_REFERENCE.level_of_evidence == EvidenceLevel.A


# =============================================================================
# BoundarySpec Tests
# =============================================================================


class TestBoundarySpec:
    """Test BoundarySpec dataclass and validation"""

    @pytest.fixture
    def creatinine_spec(self):
        """Sample creatinine boundary spec"""
        return CLINICAL_BOUNDARIES["serum_creatinine"]

    def test_spec_structure(self, creatinine_spec):
        """Test boundary spec has required fields"""
        assert creatinine_spec.param_name == "serum_creatinine"
        assert creatinine_spec.unit == "mg/dL"
        assert creatinine_spec.physiological_min == 0.1
        assert creatinine_spec.physiological_max == 30.0
        assert creatinine_spec.reference is not None

    def test_validate_normal_value(self, creatinine_spec):
        """Test validation of normal value"""
        result = creatinine_spec.validate(1.0)
        assert result.severity == ValidationSeverity.PASS
        assert result.is_valid

    def test_validate_warning_low(self, creatinine_spec):
        """Test validation triggers warning for unusually low value"""
        result = creatinine_spec.validate(0.25)  # Below warning_min
        assert result.severity == ValidationSeverity.WARNING
        assert result.is_valid  # Still valid, just warning
        assert "unusually low" in result.message.lower()

    def test_validate_warning_high(self, creatinine_spec):
        """Test validation triggers warning for unusually high value"""
        result = creatinine_spec.validate(18.0)  # Above warning_max
        assert result.severity == ValidationSeverity.WARNING
        assert "unusually high" in result.message.lower()

    def test_validate_critical_error(self, creatinine_spec):
        """Test validation fails for impossible value"""
        result = creatinine_spec.validate(50.0)  # Above physiological_max
        assert result.severity == ValidationSeverity.CRITICAL
        assert result.is_error
        assert not result.is_valid

    def test_validate_below_physiological_min(self, creatinine_spec):
        """Test validation fails for value below minimum"""
        result = creatinine_spec.validate(0.05)  # Below physiological_min
        assert result.severity == ValidationSeverity.CRITICAL
        assert result.is_error

    def test_validate_none_value(self, creatinine_spec):
        """Test validation of None (optional parameter)"""
        result = creatinine_spec.validate(None)
        assert result.severity == ValidationSeverity.PASS

    def test_validate_wrong_type(self, creatinine_spec):
        """Test validation fails for wrong type"""
        result = creatinine_spec.validate("high")
        assert result.severity == ValidationSeverity.ERROR

    def test_to_pydantic_field_kwargs(self, creatinine_spec):
        """Test generating Pydantic Field kwargs"""
        kwargs = creatinine_spec.to_pydantic_field_kwargs()
        assert "ge" in kwargs  # >= physiological_min
        assert "le" in kwargs  # <= physiological_max
        assert "description" in kwargs
        assert "mg/dL" in kwargs["description"]

    def test_to_markdown(self, creatinine_spec):
        """Test generating Markdown documentation"""
        md = creatinine_spec.to_markdown()
        assert "serum_creatinine" in md
        assert "mg/dL" in md
        assert "Reference" in md


# =============================================================================
# BoundaryRegistry Tests
# =============================================================================


class TestBoundaryRegistry:
    """Test BoundaryRegistry singleton and methods"""

    def test_singleton_instance(self):
        """Test registry is singleton"""
        reg1 = get_boundary_registry()
        reg2 = get_boundary_registry()
        assert reg1 is reg2

    def test_get_boundary_by_name(self):
        """Test getting boundary by parameter name"""
        registry = get_boundary_registry()
        spec = registry.get_boundary("serum_creatinine")
        assert spec is not None
        assert spec.param_name == "serum_creatinine"

    def test_get_boundary_by_alias(self):
        """Test getting boundary by alias"""
        registry = get_boundary_registry()
        spec = registry.get_boundary("cr")  # Alias for serum_creatinine
        assert spec is not None
        assert spec.param_name == "serum_creatinine"

    def test_get_boundary_unknown(self):
        """Test getting unknown boundary returns None"""
        registry = get_boundary_registry()
        spec = registry.get_boundary("unknown_param_xyz")
        assert spec is None

    def test_validate_single_param(self):
        """Test validating single parameter"""
        result = validate_param("heart_rate", 80)
        assert result.severity == ValidationSeverity.PASS

    def test_validate_all_params(self):
        """Test validating multiple parameters"""
        registry = get_boundary_registry()
        params = {
            "serum_creatinine": 1.2,
            "age": 65,
            "heart_rate": 80,
        }
        results = registry.validate_all(params)
        assert len(results) == 3
        assert all(r.is_valid for r in results)

    def test_validate_all_with_error(self):
        """Test validate_all catches errors"""
        registry = get_boundary_registry()
        params = {
            "serum_creatinine": 1.2,
            "age": 200,  # Invalid!
            "heart_rate": 80,
        }
        results = registry.validate_all(params)
        # age=200 should be CRITICAL
        age_result = next(r for r in results if r.param_name == "age")
        assert age_result.is_error

    def test_generate_markdown_docs(self):
        """Test generating complete documentation"""
        registry = get_boundary_registry()
        docs = registry.generate_markdown_docs()
        assert "# Clinical Parameter Boundaries" in docs
        assert "Vital Signs" in docs
        assert "Reference" in docs


# =============================================================================
# Clinical Boundaries Coverage Tests
# =============================================================================


class TestClinicalBoundariesCoverage:
    """Test that key clinical parameters have boundaries defined"""

    @pytest.mark.parametrize("param_name", [
        "temperature",
        "heart_rate",
        "respiratory_rate",
        "systolic_bp",
        "mean_arterial_pressure",
        "spo2",
        "serum_creatinine",
        "hemoglobin",
        "hematocrit",
        "platelets",
        "bilirubin",
        "age",
        "weight_kg",
        "fio2",
        "pao2_fio2_ratio",
        "gcs_score",
        "rass_score",
    ])
    def test_boundary_defined(self, param_name):
        """Test that boundary is defined for key parameter"""
        spec = get_boundary(param_name)
        assert spec is not None, f"Boundary not defined for {param_name}"
        assert spec.reference is not None, f"No reference for {param_name}"

    @pytest.mark.parametrize("param_name,normal_value", [
        ("temperature", 37.0),
        ("heart_rate", 75),
        ("respiratory_rate", 16),
        ("systolic_bp", 120),
        ("serum_creatinine", 1.0),
        ("hemoglobin", 14.0),
        ("age", 50),
        ("gcs_score", 15),
    ])
    def test_normal_values_pass(self, param_name, normal_value):
        """Test that normal values pass validation"""
        result = validate_param(param_name, normal_value)
        assert result.severity == ValidationSeverity.PASS


# =============================================================================
# Integration Tests
# =============================================================================


class TestBoundaryIntegration:
    """Integration tests for boundary validation"""

    def test_complete_patient_assessment(self):
        """Test validating a complete set of patient parameters"""
        registry = get_boundary_registry()

        # Typical ICU patient
        patient_params = {
            "temperature": 38.2,
            "heart_rate": 92,
            "respiratory_rate": 20,
            "systolic_bp": 105,
            "mean_arterial_pressure": 70,
            "spo2": 95,
            "serum_creatinine": 1.4,
            "hemoglobin": 10.5,
            "hematocrit": 32,
            "platelets": 180,
            "bilirubin": 1.8,
            "age": 68,
            "weight_kg": 75,
            "fio2": 0.4,
            "gcs_score": 14,
        }

        results = registry.validate_all(patient_params)

        # All should be valid for this patient
        for result in results:
            assert result.is_valid, f"{result.param_name} failed: {result.message}"

    def test_critical_patient_triggers_warnings(self):
        """Test that critically ill patient values trigger appropriate warnings"""
        registry = get_boundary_registry()

        # Septic shock patient with values outside warning ranges
        critical_params = {
            "temperature": 39.5,       # High fever (within warning range)
            "heart_rate": 195,         # Severe tachycardia (above warning_max=180)
            "respiratory_rate": 45,    # Severe tachypnea (above warning_max=40)
            "systolic_bp": 65,         # Severe hypotension (below warning_min=70)
            "mean_arterial_pressure": 50,  # Very low MAP (below warning_min=55)
            "serum_creatinine": 18.0,  # Severe AKI (above warning_max=15)
            "platelets": 15,           # Severe thrombocytopenia (below warning_min=20)
            "bilirubin": 25.0,         # Severe hyperbilirubinemia (above warning_max=20)
        }

        results = registry.validate_all(critical_params)

        # Most should trigger warnings due to being outside typical ranges
        warning_count = sum(1 for r in results if r.severity == ValidationSeverity.WARNING)
        assert warning_count >= 3, f"Expected multiple warnings for critical patient, got {warning_count}"

    def test_impossible_values_blocked(self):
        """Test that physiologically impossible values are rejected"""
        impossible_params = [
            ("temperature", 50.0),    # Impossible
            ("heart_rate", 350),      # Impossible
            ("spo2", 105),            # > 100%
            ("age", 150),             # > 120 years
            ("fio2", 1.5),            # > 1.0
        ]

        for param_name, value in impossible_params:
            result = validate_param(param_name, value)
            assert result.is_error, f"{param_name}={value} should be rejected"
