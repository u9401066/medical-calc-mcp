"""
Tests for Health Check Endpoint

Tests the /health endpoint for Docker/Kubernetes liveness probes.
"""

from collections.abc import Generator
from typing import Any

import pytest
from starlette.testclient import TestClient


class TestHealthEndpoint:
    """Tests for the /health endpoint"""

    @pytest.fixture
    def server(self) -> Any:
        """Create a MedicalCalculatorServer instance"""
        from src.infrastructure.mcp.config import McpServerConfig
        from src.infrastructure.mcp.server import MedicalCalculatorServer

        config = McpServerConfig(host="0.0.0.0", port=8889)
        return MedicalCalculatorServer(config=config)

    @pytest.fixture
    def client(self, server: Any) -> Generator[TestClient, None, None]:
        """Create a test client for the SSE app"""
        app = server.mcp.sse_app()
        with TestClient(app) as client:
            yield client

    def test_health_endpoint_registered(self, server: Any) -> None:
        """Test that /health endpoint is registered in the SSE app"""
        app = server.mcp.sse_app()
        routes = [route.path for route in app.routes]
        assert "/health" in routes, f"Health endpoint not found in routes: {routes}"

    def test_health_endpoint_get(self, client: TestClient) -> None:
        """Test GET /health returns healthy status"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data
        assert "calculators_loaded" in data
        assert data["calculators_loaded"] > 0

    def test_health_endpoint_head(self, client: TestClient) -> None:
        """Test HEAD /health returns 200 (for simple health checks)"""
        response = client.head("/health")
        assert response.status_code == 200

    def test_health_response_content(self, client: TestClient) -> None:
        """Test health response contains expected fields"""
        response = client.get("/health")
        data = response.json()

        # Check required fields
        assert "status" in data
        assert "service" in data
        assert "version" in data
        assert "calculators_loaded" in data

        # Check types
        assert isinstance(data["status"], str)
        assert isinstance(data["service"], str)
        assert isinstance(data["version"], str)
        assert isinstance(data["calculators_loaded"], int)

    def test_health_service_name(self, client: TestClient, server: Any) -> None:
        """Test that health response uses configured service name"""
        response = client.get("/health")
        data = response.json()

        # Should match server config name
        assert data["service"] == server._config.name

    def test_health_version_matches_config(self, client: TestClient, server: Any) -> None:
        """Test that health response uses configured version."""
        response = client.get("/health")
        data = response.json()

        assert data["version"] == server._config.version

    def test_health_calculators_count_matches_registry(self, client: TestClient, server: Any) -> None:
        """Test that reported calculator count matches registry"""
        response = client.get("/health")
        data = response.json()

        # Should match actual registry count
        expected_count = len(server.registry.list_all())
        assert data["calculators_loaded"] == expected_count


class TestReadinessEndpoint:
    """Tests for the /ready endpoint"""

    def _create_server(self) -> Any:
        from src.infrastructure.mcp.config import McpServerConfig
        from src.infrastructure.mcp.server import MedicalCalculatorServer

        config = McpServerConfig(host="0.0.0.0", port=8890)
        return MedicalCalculatorServer(config=config)

    def test_ready_endpoint_registered(self) -> None:
        """Test that /ready endpoint is registered in the SSE app"""
        server = self._create_server()
        app = server.mcp.sse_app()
        routes = [route.path for route in app.routes]
        assert "/ready" in routes, f"Readiness endpoint not found in routes: {routes}"

    def test_ready_endpoint_get_development_profile(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Development readiness should stay available with warnings."""
        monkeypatch.setenv("APP_ENV", "development")
        monkeypatch.delenv("SECURITY_AUTH_ENABLED", raising=False)
        monkeypatch.delenv("SECURITY_API_KEYS", raising=False)
        monkeypatch.delenv("SECURITY_RATE_LIMIT_ENABLED", raising=False)
        monkeypatch.setenv("TRUST_REVERSE_PROXY_SSL", "false")
        monkeypatch.setenv("CORS_ORIGINS", "*")

        server = self._create_server()
        with TestClient(server.mcp.sse_app()) as client:
            response = client.get("/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is True
        assert data["overall_status"] == "ready"
        assert data["warning_count"] >= 1

    def test_ready_endpoint_get_production_profile(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Production readiness should fail when required controls are missing."""
        monkeypatch.setenv("APP_ENV", "production")
        monkeypatch.delenv("SECURITY_AUTH_ENABLED", raising=False)
        monkeypatch.delenv("SECURITY_API_KEYS", raising=False)
        monkeypatch.delenv("SECURITY_RATE_LIMIT_ENABLED", raising=False)
        monkeypatch.setenv("TRUST_REVERSE_PROXY_SSL", "false")
        monkeypatch.setenv("CORS_ORIGINS", "*")

        server = self._create_server()
        with TestClient(server.mcp.sse_app()) as client:
            response = client.get("/ready")

        assert response.status_code == 503
        data = response.json()
        assert data["ready"] is False
        assert data["overall_status"] == "not_ready"
        assert data["fail_count"] >= 1
