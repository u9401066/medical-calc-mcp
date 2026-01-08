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

    def test_health_calculators_count_matches_registry(
        self, client: TestClient, server: Any
    ) -> None:
        """Test that reported calculator count matches registry"""
        response = client.get("/health")
        data = response.json()

        # Should match actual registry count
        expected_count = len(server.registry.list_all())
        assert data["calculators_loaded"] == expected_count
