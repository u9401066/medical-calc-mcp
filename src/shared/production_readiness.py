"""Production readiness helpers for runtime endpoints and deployment gates."""

from __future__ import annotations

from dataclasses import dataclass


READINESS_PASS = "pass"
READINESS_WARN = "warn"
READINESS_FAIL = "fail"


def is_production_environment(environment: str) -> bool:
    """Return True when the supplied environment should be treated as production."""
    return environment.strip().lower() in {"prod", "production", "live"}


@dataclass(frozen=True)
class ReadinessCheck:
    """Single production-readiness check result."""

    name: str
    status: str
    detail: str
    recommendation: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "status": self.status,
            "detail": self.detail,
            "recommendation": self.recommendation,
        }


@dataclass(frozen=True)
class ReadinessReport:
    """Structured readiness report used by endpoints and deployment gates."""

    service: str
    environment: str
    overall_status: str
    fail_count: int
    warning_count: int
    checks: tuple[ReadinessCheck, ...]

    @property
    def ready(self) -> bool:
        return self.fail_count == 0

    def to_dict(self) -> dict[str, object]:
        return {
            "service": self.service,
            "environment": self.environment,
            "overall_status": self.overall_status,
            "ready": self.ready,
            "fail_count": self.fail_count,
            "warning_count": self.warning_count,
            "checks": [check.to_dict() for check in self.checks],
        }


def build_readiness_report(
    *,
    service: str,
    environment: str,
    calculator_count: int,
    expected_calculator_count: int,
    discovery_built: bool,
    formula_provenance_issues: list[str],
    auth_enabled: bool,
    api_keys_configured: bool,
    rate_limit_enabled: bool,
    cors_origins: str,
    ssl_enabled: bool,
) -> ReadinessReport:
    """Build a readiness report from runtime and deployment settings."""
    production = is_production_environment(environment)
    checks: list[ReadinessCheck] = []

    calculator_status = READINESS_PASS if calculator_count >= expected_calculator_count else READINESS_FAIL
    checks.append(
        ReadinessCheck(
            name="calculator_registry",
            status=calculator_status,
            detail=(
                f"Loaded {calculator_count} calculators; expected at least {expected_calculator_count}."
            ),
            recommendation="Ensure all calculator classes are registered during startup.",
        )
    )

    checks.append(
        ReadinessCheck(
            name="discovery_indexes",
            status=READINESS_PASS if discovery_built else READINESS_FAIL,
            detail="Auto-discovery indexes are built." if discovery_built else "Auto-discovery indexes are not built.",
            recommendation="Build discovery indexes during startup before serving traffic.",
        )
    )

    checks.append(
        ReadinessCheck(
            name="formula_provenance",
            status=READINESS_PASS if not formula_provenance_issues else READINESS_FAIL,
            detail="Formula provenance manifest is complete." if not formula_provenance_issues else "; ".join(formula_provenance_issues[:3]),
            recommendation="Fix manifest coverage and reference metadata before production deployment.",
        )
    )

    auth_status = READINESS_PASS if auth_enabled and api_keys_configured else (READINESS_FAIL if production else READINESS_WARN)
    checks.append(
        ReadinessCheck(
            name="api_authentication",
            status=auth_status,
            detail=(
                "Authentication is enabled with API keys configured."
                if auth_enabled and api_keys_configured
                else "Authentication is disabled or API keys are missing."
            ),
            recommendation="Enable API authentication and provision non-empty API keys for production.",
        )
    )

    rate_limit_status = READINESS_PASS if rate_limit_enabled else (READINESS_FAIL if production else READINESS_WARN)
    checks.append(
        ReadinessCheck(
            name="rate_limiting",
            status=rate_limit_status,
            detail="Rate limiting is enabled." if rate_limit_enabled else "Rate limiting is disabled.",
            recommendation="Enable request throttling before exposing the service publicly.",
        )
    )

    wildcard_cors = cors_origins.strip() == "*"
    cors_status = READINESS_PASS if not wildcard_cors else (READINESS_FAIL if production else READINESS_WARN)
    checks.append(
        ReadinessCheck(
            name="cors_policy",
            status=cors_status,
            detail=f"CORS origins configured as: {cors_origins}",
            recommendation="Use explicit origins instead of '*' in production deployments.",
        )
    )

    ssl_status = READINESS_PASS if ssl_enabled else READINESS_WARN
    checks.append(
        ReadinessCheck(
            name="transport_security",
            status=ssl_status,
            detail="TLS/SSL is configured for direct serving." if ssl_enabled else "Direct TLS/SSL is not configured.",
            recommendation="Terminate TLS either directly in the service or at a trusted reverse proxy.",
        )
    )

    fail_count = sum(1 for check in checks if check.status == READINESS_FAIL)
    warning_count = sum(1 for check in checks if check.status == READINESS_WARN)
    overall_status = "ready" if fail_count == 0 else "not_ready"

    return ReadinessReport(
        service=service,
        environment=environment,
        overall_status=overall_status,
        fail_count=fail_count,
        warning_count=warning_count,
        checks=tuple(checks),
    )