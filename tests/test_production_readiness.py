"""Tests for shared production readiness checks."""

from src.shared.production_readiness import build_readiness_report


class TestProductionReadiness:
    """Validate readiness behavior across environments."""

    def test_development_profile_allows_warnings(self) -> None:
        """Development mode should stay ready when only production controls are missing."""
        report = build_readiness_report(
            service="test-service",
            environment="development",
            calculator_count=128,
            expected_calculator_count=128,
            discovery_built=True,
            formula_provenance_issues=[],
            auth_enabled=False,
            api_keys_configured=False,
            rate_limit_enabled=False,
            cors_origins="*",
            ssl_enabled=False,
        )

        assert report.ready is True
        assert report.overall_status == "ready"
        assert report.fail_count == 0
        assert report.warning_count == 4

    def test_production_profile_requires_security_controls(self) -> None:
        """Production mode should fail when core perimeter controls are missing."""
        report = build_readiness_report(
            service="test-service",
            environment="production",
            calculator_count=128,
            expected_calculator_count=128,
            discovery_built=True,
            formula_provenance_issues=[],
            auth_enabled=False,
            api_keys_configured=False,
            rate_limit_enabled=False,
            cors_origins="*",
            ssl_enabled=False,
        )

        assert report.ready is False
        assert report.overall_status == "not_ready"
        assert report.fail_count == 4
        assert report.warning_count == 0

    def test_production_profile_requires_tls_even_with_other_controls(self) -> None:
        """Production mode should remain blocked when transport security is missing."""
        report = build_readiness_report(
            service="test-service",
            environment="production",
            calculator_count=128,
            expected_calculator_count=128,
            discovery_built=True,
            formula_provenance_issues=[],
            auth_enabled=True,
            api_keys_configured=True,
            rate_limit_enabled=True,
            cors_origins="https://api.example.com",
            ssl_enabled=False,
        )

        assert report.ready is False
        assert report.overall_status == "not_ready"
        assert report.fail_count == 1
        assert report.warning_count == 0

    def test_production_profile_passes_with_required_controls(self) -> None:
        """Production mode should be ready when required controls are configured."""
        report = build_readiness_report(
            service="test-service",
            environment="production",
            calculator_count=128,
            expected_calculator_count=128,
            discovery_built=True,
            formula_provenance_issues=[],
            auth_enabled=True,
            api_keys_configured=True,
            rate_limit_enabled=True,
            cors_origins="https://api.example.com",
            ssl_enabled=True,
        )

        assert report.ready is True
        assert report.overall_status == "ready"
        assert report.fail_count == 0
        assert report.warning_count == 0
