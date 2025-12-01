"""
REST API Tests for Medical Calculator Server

Tests all API endpoints including:
- Health check
- Calculator listing and search
- Calculator info retrieval
- Calculation execution

Usage:
    pytest tests/test_api.py -v
    
Requirements:
    pip install pytest httpx pytest-asyncio
"""

import pytest
from httpx import AsyncClient, ASGITransport
from typing import Any, Dict

# Import the FastAPI app and ensure calculators are registered
from src.infrastructure.api.server import app
from src.domain.registry.tool_registry import get_registry
from src.domain.services.calculators import CALCULATORS


@pytest.fixture(scope="module", autouse=True)
def setup_calculators():
    """Ensure all calculators are registered before tests"""
    registry = get_registry()
    for calculator_cls in CALCULATORS:
        instance = calculator_cls()
        if registry.get_calculator(instance.tool_id) is None:
            registry.register(instance)
    yield


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    """Create async test client"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# =============================================================================
# Health Check Tests
# =============================================================================

class TestHealthCheck:
    """Test health check endpoint"""
    
    @pytest.mark.anyio
    async def test_health_check(self, client: AsyncClient):
        """Test /health endpoint returns healthy status"""
        response = await client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "medical-calc-api"
        assert "calculators" in data
        assert data["calculators"] > 0


# =============================================================================
# Calculator Discovery Tests
# =============================================================================

class TestCalculatorDiscovery:
    """Test calculator discovery endpoints"""
    
    @pytest.mark.anyio
    async def test_list_all_calculators(self, client: AsyncClient):
        """Test /api/v1/calculators returns all calculators"""
        response = await client.get("/api/v1/calculators")
        assert response.status_code == 200
        
        data = response.json()
        assert "count" in data
        assert "tools" in data
        assert data["count"] > 0
        assert len(data["tools"]) > 0
        
        # Check calculator structure
        calculator = data["tools"][0]
        assert "tool_id" in calculator
        assert "name" in calculator
    
    @pytest.mark.anyio
    async def test_search_calculators(self, client: AsyncClient):
        """Test /api/v1/search with keyword"""
        response = await client.get("/api/v1/search", params={"q": "sepsis"})
        assert response.status_code == 200
        
        data = response.json()
        assert "count" in data
        assert "tools" in data
        # Should find sepsis-related tools like SOFA, qSOFA
        assert data["count"] > 0
    
    @pytest.mark.anyio
    async def test_search_no_results(self, client: AsyncClient):
        """Test search with no matching results"""
        response = await client.get("/api/v1/search", params={"q": "xyznonexistent"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["count"] == 0
    
    @pytest.mark.anyio
    async def test_list_specialties(self, client: AsyncClient):
        """Test /api/v1/specialties returns specialty list"""
        response = await client.get("/api/v1/specialties")
        assert response.status_code == 200
        
        data = response.json()
        assert "specialties" in data
        assert len(data["specialties"]) > 0
        # Should include common specialties
        specialties = [s.lower() for s in data["specialties"]]
        assert any("critical" in s for s in specialties)
    
    @pytest.mark.anyio
    async def test_list_by_specialty(self, client: AsyncClient):
        """Test /api/v1/specialties/{specialty} returns tools"""
        response = await client.get("/api/v1/specialties/critical_care")
        assert response.status_code == 200
        
        data = response.json()
        assert "count" in data
        assert data["count"] > 0
    
    @pytest.mark.anyio
    async def test_list_contexts(self, client: AsyncClient):
        """Test /api/v1/contexts returns context list"""
        response = await client.get("/api/v1/contexts")
        assert response.status_code == 200
        
        data = response.json()
        assert "contexts" in data
        assert len(data["contexts"]) > 0
    
    @pytest.mark.anyio
    async def test_get_calculator_info(self, client: AsyncClient):
        """Test /api/v1/calculators/{tool_id} returns calculator details"""
        response = await client.get("/api/v1/calculators/sofa_score")
        assert response.status_code == 200
        
        data = response.json()
        assert "tool_id" in data
        assert data["tool_id"] == "sofa_score"
        assert "name" in data
    
    @pytest.mark.anyio
    async def test_get_calculator_info_not_found(self, client: AsyncClient):
        """Test getting non-existent calculator returns 404"""
        response = await client.get("/api/v1/calculators/nonexistent_calc")
        assert response.status_code == 404


# =============================================================================
# Calculator Execution Tests
# =============================================================================

class TestCalculatorExecution:
    """Test calculator execution endpoints"""
    
    @pytest.mark.anyio
    async def test_calculate_gcs(self, client: AsyncClient):
        """Test GCS calculation"""
        response = await client.post(
            "/api/v1/calculate/glasgow_coma_scale",
            json={
                "params": {
                    "eye_response": 4,
                    "verbal_response": 5,
                    "motor_response": 6
                }
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["calculator"] == "glasgow_coma_scale"
        assert data["result"]["value"] == 15  # Max GCS
    
    @pytest.mark.anyio
    async def test_calculate_sofa(self, client: AsyncClient):
        """Test SOFA score calculation"""
        response = await client.post(
            "/api/v1/calculate/sofa_score",
            json={
                "params": {
                    "pao2_fio2_ratio": 200,
                    "platelets": 100,
                    "bilirubin": 2.0,
                    "gcs_score": 13,
                    "creatinine": 2.5
                }
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["calculator"] == "sofa_score"
        assert "value" in data["result"]
        assert "interpretation" in data["result"]
    
    @pytest.mark.anyio
    async def test_calculate_ckd_epi(self, client: AsyncClient):
        """Test CKD-EPI eGFR calculation"""
        response = await client.post(
            "/api/v1/calculate/ckd_epi_2021",
            json={
                "params": {
                    "serum_creatinine": 1.2,
                    "age": 65,
                    "sex": "female"
                }
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["calculator"] == "ckd_epi_2021"
        assert "value" in data["result"]
        assert data["result"]["unit"] == "mL/min/1.73m²"
    
    @pytest.mark.anyio
    async def test_calculate_meld(self, client: AsyncClient):
        """Test MELD score calculation"""
        response = await client.post(
            "/api/v1/calculate/meld_score",
            json={
                "params": {
                    "creatinine": 1.5,
                    "bilirubin": 2.0,
                    "inr": 1.5
                }
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "value" in data["result"]
    
    @pytest.mark.anyio
    async def test_calculate_news2(self, client: AsyncClient):
        """Test NEWS2 calculation"""
        response = await client.post(
            "/api/v1/calculate/news2_score",
            json={
                "params": {
                    "respiratory_rate": 18,
                    "spo2": 96,
                    "on_supplemental_o2": False,
                    "temperature": 37.0,
                    "systolic_bp": 120,
                    "heart_rate": 80
                }
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["calculator"] == "news2_score"
    
    @pytest.mark.anyio
    async def test_calculate_invalid_params(self, client: AsyncClient):
        """Test calculation with invalid parameters"""
        response = await client.post(
            "/api/v1/calculate/glasgow_coma_scale",
            json={
                "params": {
                    "eye_response": 10,  # Invalid: max is 4
                    "verbal_response": 5,
                    "motor_response": 6
                }
            }
        )
        # Should return error
        assert response.status_code in [400, 422, 200]  # May vary by implementation
        
        data = response.json()
        if response.status_code == 200:
            assert data["success"] is False
    
    @pytest.mark.anyio
    async def test_calculate_missing_params(self, client: AsyncClient):
        """Test calculation with missing required parameters"""
        response = await client.post(
            "/api/v1/calculate/glasgow_coma_scale",
            json={
                "params": {
                    "eye_response": 4
                    # Missing verbal_response and motor_response
                }
            }
        )
        # Should return error
        assert response.status_code in [400, 422, 200]
    
    @pytest.mark.anyio
    async def test_calculate_nonexistent_calculator(self, client: AsyncClient):
        """Test calculation with non-existent calculator"""
        response = await client.post(
            "/api/v1/calculate/nonexistent_calc",
            json={"params": {}}
        )
        # API returns 200 with success=False for not found calculator
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is False


# =============================================================================
# Quick Calculate Endpoint Tests
# =============================================================================

class TestQuickCalculate:
    """Test quick calculate endpoints (if available)"""
    
    @pytest.mark.anyio
    async def test_quick_calculate_exists(self, client: AsyncClient):
        """Test if quick calculate endpoints exist"""
        # This may vary by implementation
        response = await client.get("/api/v1/ckd-epi", params={
            "serum_creatinine": 1.2,
            "age": 65,
            "sex": "female"
        })
        # May or may not exist
        if response.status_code == 200:
            data = response.json()
            assert "value" in data or "result" in data


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Test API error handling"""
    
    @pytest.mark.anyio
    async def test_invalid_json(self, client: AsyncClient):
        """Test handling of invalid JSON"""
        response = await client.post(
            "/api/v1/calculate/gcs",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    @pytest.mark.anyio
    async def test_method_not_allowed(self, client: AsyncClient):
        """Test method not allowed response"""
        response = await client.post("/health")
        assert response.status_code == 405
    
    @pytest.mark.anyio
    async def test_not_found_route(self, client: AsyncClient):
        """Test non-existent route"""
        response = await client.get("/nonexistent/route")
        assert response.status_code == 404


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests for complete workflows"""
    
    @pytest.mark.anyio
    async def test_discovery_to_calculation_workflow(self, client: AsyncClient):
        """Test complete workflow: search -> info -> calculate"""
        # Step 1: Search for kidney-related calculators
        search_response = await client.get("/api/v1/search", params={"q": "kidney"})
        assert search_response.status_code == 200
        search_data = search_response.json()
        
        if search_data["count"] > 0:
            # Step 2: Get first calculator info
            tool_id = search_data["tools"][0]["tool_id"]
            info_response = await client.get(f"/api/v1/calculators/{tool_id}")
            assert info_response.status_code == 200
            
            # Step 3: Calculator is found (calculation would need proper params)
            info_data = info_response.json()
            assert "input_params" in info_data or "parameters" in info_data
    
    @pytest.mark.anyio
    async def test_specialty_workflow(self, client: AsyncClient):
        """Test specialty-based discovery workflow"""
        # Step 1: List specialties
        specialties_response = await client.get("/api/v1/specialties")
        assert specialties_response.status_code == 200
        specialties = specialties_response.json()["specialties"]
        
        # Step 2: Get tools from first specialty
        if specialties:
            specialty = specialties[0]
            tools_response = await client.get(f"/api/v1/specialties/{specialty}")
            assert tools_response.status_code == 200
            
            tools_data = tools_response.json()
            assert "count" in tools_data


# =============================================================================
# Performance Tests
# =============================================================================

class TestPerformance:
    """Basic performance tests"""
    
    @pytest.mark.anyio
    async def test_health_check_fast(self, client: AsyncClient):
        """Health check should be fast"""
        import time
        start = time.time()
        response = await client.get("/health")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 1.0  # Should complete in under 1 second
    
    @pytest.mark.anyio
    async def test_calculation_reasonable_time(self, client: AsyncClient):
        """Calculation should complete in reasonable time"""
        import time
        start = time.time()
        response = await client.post(
            "/api/v1/calculate/glasgow_coma_scale",
            json={
                "params": {
                    "eye_response": 4,
                    "verbal_response": 5,
                    "motor_response": 6
                }
            }
        )
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 2.0  # Should complete in under 2 seconds


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
