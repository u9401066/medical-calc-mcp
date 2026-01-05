from typing import Any
"""
Shared fixtures for E2E calculator tests.
"""
from typing import Any, Optional

import pytest
from starlette.testclient import TestClient


@pytest.fixture(scope="module")
def initialized_registry() -> Any:
    """Initialize the registry with all calculators"""
    from src.domain.registry.tool_registry import ToolRegistry, get_registry
    from src.domain.services.calculators import CALCULATORS

    # Reset and initialize
    ToolRegistry.reset()
    registry = get_registry()
    for calculator_cls in CALCULATORS:
        instance = calculator_cls()
        if registry.get_calculator(instance.tool_id) is None:
            registry.register(instance)

    return registry


@pytest.fixture
def test_client(initialized_registry: Any) -> TestClient:
    """Create test client for REST API"""
    from src.infrastructure.api.server import app
    return TestClient(app)


def assert_successful_calculation(response: Any, expected_keys: Optional[list[str]] = None) -> Any:
    """Helper to assert successful calculation response"""
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "result" in data
    result = data["result"]
    assert "value" in result or "score" in result or "interpretation" in result

    if expected_keys:
        for key in expected_keys:
            assert key in result, f"Expected key '{key}' not found in result"

    return data


def assert_calculation_error(response: Any) -> Any:
    """Helper to assert calculation error response"""
    if response.status_code == 200:
        data = response.json()
        assert data["success"] is False
        assert "error" in data
        return data
    else:
        assert response.status_code in (400, 422, 500)
        return response.json()
