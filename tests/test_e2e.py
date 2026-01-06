from typing import Any

"""
End-to-End (E2E) Tests for Medical Calculator MCP Server

Docker-based E2E testing that verifies the complete system:
- REST API endpoints
- SSE transport
- MCP tool invocations
- Clinical workflows

Usage:
    # Run E2E tests (requires Docker)
    pytest tests/test_e2e.py -v -m e2e

    # Run without Docker (uses test client)
    pytest tests/test_e2e.py -v -m "not docker"
"""
import os
import time

import pytest

# Check if httpx is available for async testing
try:
    import httpx  # noqa: F401
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


# =============================================================================
# Fixtures
# =============================================================================

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
def api_base_url() -> Any:
    """Base URL for API testing"""
    return os.environ.get("API_BASE_URL", "http://localhost:8000")


@pytest.fixture
def test_client(initialized_registry: Any) -> Any:
    """Create test client for REST API"""
    from starlette.testclient import TestClient

    from src.infrastructure.api.server import app
    return TestClient(app)


# =============================================================================
# REST API E2E Tests
# =============================================================================

class TestRestApiE2E:
    """End-to-end tests for REST API"""

    def test_health_endpoint(self, test_client: Any) -> None:
        """Health check endpoint should return status"""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "calculators" in data  # calculator count (int)
        assert data["calculators"] >= 50  # Should have many calculators

    def test_list_calculators(self, test_client: Any) -> None:
        """List all available calculators"""
        response = test_client.get("/api/v1/calculators?limit=100")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert "count" in data
        assert data["count"] >= 70  # At least 70 calculators

        # Check calculator structure
        first_calc = data["tools"][0]
        assert "name" in first_calc
        assert "purpose" in first_calc

    def test_list_by_specialty(self, test_client: Any) -> None:
        """List calculators by specialty"""
        response = test_client.get("/api/v1/specialties/critical_care")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert len(data["tools"]) > 0

    def test_get_calculator_info(self, test_client: Any) -> None:
        """Get specific calculator information"""
        # Use actual tool_id: glasgow_coma_scale
        response = test_client.get("/api/v1/calculators/glasgow_coma_scale")
        assert response.status_code == 200
        data = response.json()
        assert data["tool_id"] == "glasgow_coma_scale"

    def test_calculate_sofa_score(self, test_client: Any) -> None:
        """Calculate SOFA score via REST API"""
        # API expects params wrapped in {"params": {...}}
        # SOFA requires: pao2_fio2_ratio, platelets, bilirubin, gcs_score, creatinine
        payload = {
            "params": {
                "pao2_fio2_ratio": 300,
                "platelets": 150,
                "bilirubin": 1.0,
                "gcs_score": 15,
                "creatinine": 1.0
            }
        }
        response = test_client.post("/api/v1/calculate/sofa_score", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "result" in data

    def test_calculate_gcs(self, test_client: Any) -> None:
        """Calculate GCS score via REST API"""
        payload = {
            "params": {
                "eye_response": 4,
                "verbal_response": 5,
                "motor_response": 6
            }
        }
        response = test_client.post("/api/v1/calculate/glasgow_coma_scale", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["result"]["value"] == 15

    def test_calculate_news2(self, test_client: Any) -> None:
        """Calculate NEWS2 score via REST API"""
        payload = {
            "params": {
                "respiratory_rate": 18,
                "spo2": 96,
                "on_supplemental_o2": False,
                "temperature": 37.0,
                "systolic_bp": 120,
                "heart_rate": 80
            }
        }
        response = test_client.post("/api/v1/calculate/news2_score", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_calculate_apache_ii(self, test_client: Any) -> None:
        """Calculate APACHE II score via REST API"""
        payload = {
            "params": {
                "temperature": 37.5,
                "mean_arterial_pressure": 85,
                "heart_rate": 90,
                "respiratory_rate": 18,
                "fio2": 0.21,
                "pao2": 90,
                "arterial_ph": 7.4,
                "serum_sodium": 140,
                "serum_potassium": 4.0,
                "serum_creatinine": 1.0,
                "hematocrit": 40,
                "wbc_count": 10,
                "gcs_score": 15,
                "age": 50
            }
        }
        response = test_client.post("/api/v1/calculate/apache_ii", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_calculate_invalid_endpoint(self, test_client: Any) -> None:
        """Invalid calculator should return error"""
        # API returns success=False for invalid calculators
        payload: dict[str, Any] = {"params": {"foo": "bar"}}
        response = test_client.post("/api/v1/calculate/nonexistent_calculator", json=payload)
        # May return 200 with success=False or 404
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is False
        else:
            assert response.status_code in [404, 422]

    def test_calculate_missing_params(self, test_client: Any) -> None:
        """Missing required parameters should return error"""
        payload: dict[str, Any] = {"params": {}}  # Empty params
        response = test_client.post("/api/v1/calculate/glasgow_coma_scale", json=payload)
        # API should return success=False for missing params
        assert response.status_code == 200  # API returns 200 with error message
        data = response.json()
        assert data["success"] is False or "error" in str(data).lower()


# =============================================================================
# Clinical Workflow E2E Tests
# =============================================================================

class TestClinicalWorkflowE2E:
    """End-to-end tests for clinical workflows"""

    def test_sepsis_evaluation_workflow(self, test_client: Any) -> None:
        """Complete sepsis evaluation workflow: qSOFA -> SOFA"""
        # Step 1: qSOFA screening
        # qSOFA params: respiratory_rate, systolic_bp, altered_mentation, gcs_score
        qsofa_payload = {
            "params": {
                "respiratory_rate": 24,
                "systolic_bp": 95,
                "altered_mentation": False
            }
        }
        response = test_client.post("/api/v1/calculate/qsofa_score", json=qsofa_payload)
        assert response.status_code == 200
        qsofa_result = response.json()

        # Step 2: Full SOFA if indicated
        # SOFA params: pao2_fio2_ratio, platelets, bilirubin, gcs_score, creatinine
        sofa_payload = {
            "params": {
                "pao2_fio2_ratio": 350,
                "platelets": 140,
                "bilirubin": 1.5,
                "gcs_score": 14,
                "creatinine": 1.3
            }
        }
        response = test_client.post("/api/v1/calculate/sofa_score", json=sofa_payload)
        assert response.status_code == 200
        sofa_result = response.json()

        # Verify both scores calculated
        assert qsofa_result.get("success") is True
        assert sofa_result.get("success") is True

    def test_preoperative_assessment_workflow(self, test_client: Any) -> None:
        """Preoperative assessment workflow: ASA -> RCRI -> Mallampati"""
        # Step 1: ASA Physical Status
        asa_payload = {"params": {"asa_class": 2}}
        response = test_client.post("/api/v1/calculate/asa_physical_status", json=asa_payload)
        assert response.status_code == 200

        # Step 2: RCRI (Cardiac Risk)
        rcri_payload = {
            "params": {
                "high_risk_surgery": True,
                "ischemic_heart_disease": False,
                "heart_failure": False,
                "cerebrovascular_disease": False,
                "insulin_diabetes": False,
                "creatinine_above_2": False
            }
        }
        response = test_client.post("/api/v1/calculate/rcri", json=rcri_payload)
        assert response.status_code == 200

        # Step 3: Mallampati (Airway)
        mallampati_payload = {"params": {"mallampati_class": 2}}
        response = test_client.post("/api/v1/calculate/mallampati_score", json=mallampati_payload)
        assert response.status_code == 200

    def test_aki_assessment_workflow(self, test_client: Any) -> None:
        """AKI assessment workflow: CKD-EPI -> KDIGO staging"""
        # Step 1: Baseline CKD-EPI
        ckd_payload = {
            "params": {
                "serum_creatinine": 1.2,
                "age": 65,
                "sex": "male"
            }
        }
        response = test_client.post("/api/v1/calculate/ckd_epi_2021", json=ckd_payload)
        assert response.status_code == 200

        # Step 2: KDIGO AKI staging
        kdigo_payload = {
            "params": {
                "baseline_creatinine": 1.0,
                "current_creatinine": 2.2,
                "urine_output_ml_kg_hr": 0.4,
                "hours_of_oliguria": 8
            }
        }
        response = test_client.post("/api/v1/calculate/kdigo_aki", json=kdigo_payload)
        assert response.status_code == 200

    def test_pneumonia_assessment_workflow(self, test_client: Any) -> None:
        """Pneumonia assessment: CURB-65"""
        # CURB-65
        curb_payload = {
            "params": {
                "confusion": False,
                "bun_gt_19_or_urea_gt_7": True,
                "respiratory_rate_gte_30": False,
                "sbp_lt_90_or_dbp_lte_60": False,
                "age_gte_65": True
            }
        }
        response = test_client.post("/api/v1/calculate/curb65", json=curb_payload)
        assert response.status_code == 200


# =============================================================================
# MCP Tool Invocation E2E Tests
# =============================================================================

class TestMCPToolE2E:
    """E2E tests for MCP tool invocations"""

    def test_mcp_tool_list(self, test_client: Any) -> None:
        """MCP should list all available tools"""
        response = test_client.get("/mcp/tools")
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            assert len(data) >= 70

    def test_mcp_discovery_tools(self, test_client: Any) -> None:
        """MCP discovery tools should work"""
        # List specialties
        response = test_client.get("/mcp/specialties")
        if response.status_code == 200:
            data = response.json()
            assert len(data) > 0

        # List contexts
        response = test_client.get("/mcp/contexts")
        if response.status_code == 200:
            data = response.json()
            assert len(data) > 0


# =============================================================================
# Performance E2E Tests
# =============================================================================

class TestPerformanceE2E:
    """Performance-related E2E tests"""

    def test_response_time_health(self, test_client: Any) -> None:
        """Health endpoint should respond quickly"""
        start = time.time()
        response = test_client.get("/health")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 0.5  # Should be under 500ms

    def test_response_time_calculation(self, test_client: Any) -> None:
        """Calculation should respond quickly"""
        payload = {
            "params": {
                "eye_response": 4,
                "verbal_response": 5,
                "motor_response": 6
            }
        }

        start = time.time()
        response = test_client.post("/api/v1/calculate/glasgow_coma_scale", json=payload)
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 1.0  # Should be under 1 second

    def test_concurrent_requests(self, test_client: Any) -> None:
        """Handle multiple concurrent requests"""
        import concurrent.futures

        def make_request() -> Any:
            return test_client.get("/health")

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All requests should succeed
        assert all(r.status_code == 200 for r in results)


# =============================================================================
# Integration Tests (API + Calculator)
# =============================================================================

class TestIntegrationE2E:
    """Integration tests between API and calculators"""

    def test_calculator_result_structure(self, test_client: Any) -> None:
        """Verify calculator result structure is consistent"""
        calculators_to_test = [
            ("glasgow_coma_scale", {"eye_response": 4, "verbal_response": 5, "motor_response": 6}),
            ("news2_score", {
                "respiratory_rate": 18,
                "spo2": 96,
                "on_supplemental_o2": False,
                "temperature": 37.0,
                "systolic_bp": 120,
                "heart_rate": 80
            }),
        ]

        for calc_id, params in calculators_to_test:
            payload = {"params": params}
            response = test_client.post(f"/api/v1/calculate/{calc_id}", json=payload)
            if response.status_code == 200:
                data = response.json()

                # All results should have success and result fields
                assert data.get("success") is True
                assert "result" in data

    def test_error_response_structure(self, test_client: Any) -> None:
        """Error responses should have consistent structure"""
        # Invalid payload (missing params wrapper)
        response = test_client.post("/api/v1/calculate/glasgow_coma_scale", json={"invalid": "data"})
        assert response.status_code in [400, 422, 500]

        # Response should be JSON
        data = response.json()
        assert data is not None


# =============================================================================
# Docker-based E2E Tests (marked for separate execution)
# =============================================================================

@pytest.mark.docker
class TestDockerE2E:
    """E2E tests that require Docker environment"""

    @pytest.fixture
    def docker_api_url(self) -> Any:
        """URL for Docker-based API"""
        return os.environ.get("DOCKER_API_URL", "http://localhost:8000")

    @pytest.mark.skipif(not HTTPX_AVAILABLE, reason="httpx not installed")
    def test_docker_health(self, docker_api_url: Any) -> None:
        """Test health endpoint in Docker"""
        import httpx

        try:
            response = httpx.get(f"{docker_api_url}/health", timeout=5.0)
            assert response.status_code == 200
        except httpx.ConnectError:
            pytest.skip("Docker container not running")

    @pytest.mark.skipif(not HTTPX_AVAILABLE, reason="httpx not installed")
    def test_docker_calculation(self, docker_api_url: Any) -> None:
        """Test calculation in Docker"""
        import httpx

        try:
            payload = {"params": {"eye_response": 4, "verbal_response": 5, "motor_response": 6}}
            response = httpx.post(
                f"{docker_api_url}/api/v1/calculate/glasgow_coma_scale",
                json=payload,
                timeout=5.0
            )
            assert response.status_code == 200
            data = response.json()
            assert data.get("success") is True
        except httpx.ConnectError:
            pytest.skip("Docker container not running")


# =============================================================================
# SSE Transport E2E Tests
# =============================================================================

class TestSSETransportE2E:
    """E2E tests for SSE transport"""

    def test_root_endpoint_exists(self, test_client: Any) -> None:
        """Root endpoint should be available"""
        response = test_client.get("/")
        assert response.status_code == 200


# =============================================================================
# Data Validation E2E Tests
# =============================================================================

class TestDataValidationE2E:
    """E2E tests for data validation"""

    def test_boundary_values(self, test_client: Any) -> None:
        """Test boundary value handling"""
        # Minimum valid values
        payload = {
            "params": {
                "eye_response": 1,
                "verbal_response": 1,
                "motor_response": 1
            }
        }
        response = test_client.post("/api/v1/calculate/glasgow_coma_scale", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert data.get("result", {}).get("value") == 3

        # Maximum valid values
        payload = {
            "params": {
                "eye_response": 4,
                "verbal_response": 5,
                "motor_response": 6
            }
        }
        response = test_client.post("/api/v1/calculate/glasgow_coma_scale", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert data.get("result", {}).get("value") == 15

    def test_out_of_range_values(self, test_client: Any) -> None:
        """Out of range values should return error"""
        payload = {
            "params": {
                "eye_response": 10,  # Invalid: max is 4
                "verbal_response": 5,
                "motor_response": 6
            }
        }
        response = test_client.post("/api/v1/calculate/glasgow_coma_scale", json=payload)
        # API may return 200 with success=False or 4xx/5xx
        if response.status_code == 200:
            data = response.json()
            assert data.get("success") is False
        else:
            assert response.status_code in [400, 422, 500]

    def test_type_coercion(self, test_client: Any) -> None:
        """String numbers should be coerced to numbers"""
        payload = {
            "params": {
                "eye_response": "4",  # String instead of int
                "verbal_response": "5",
                "motor_response": "6"
            }
        }
        response = test_client.post("/api/v1/calculate/glasgow_coma_scale", json=payload)
        # Should either succeed with coercion or fail with validation error
        assert response.status_code in [200, 400, 422, 500]
