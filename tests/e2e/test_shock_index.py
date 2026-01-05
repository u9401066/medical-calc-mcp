from typing import Any
"""
E2E Tests for Shock Index Calculator

Tests the Shock Index calculator through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestShockIndexE2E:
    """E2E tests for Shock Index Calculator"""

    ENDPOINT = "/api/v1/calculate/shock_index"

    def test_normal_shock_index(self, test_client: Any) -> None:
        """Test normal shock index (0.5-0.7)"""
        payload = {
            "params": {
                "heart_rate": 70,
                "systolic_bp": 120
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # SI = 70/120 = 0.58
        assert 0.5 <= data["result"]["value"] <= 0.7

    def test_elevated_shock_index(self, test_client: Any) -> None:
        """Test elevated shock index (>0.9)"""
        payload = {
            "params": {
                "heart_rate": 110,
                "systolic_bp": 100
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # SI = 110/100 = 1.1
        assert data["result"]["value"] > 0.9

    def test_critically_elevated(self, test_client: Any) -> None:
        """Test critically elevated shock index (>1.4)"""
        payload = {
            "params": {
                "heart_rate": 140,
                "systolic_bp": 80
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # SI = 140/80 = 1.75
        assert data["result"]["value"] > 1.4

    def test_borderline_shock_index(self, test_client: Any) -> None:
        """Test borderline shock index (0.7-0.9)"""
        payload = {
            "params": {
                "heart_rate": 90,
                "systolic_bp": 110
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # SI = 90/110 = 0.82
        assert 0.7 <= data["result"]["value"] <= 1.0

    def test_with_diastolic_bp(self, test_client: Any) -> None:
        """Test with diastolic BP (modified shock index)"""
        payload = {
            "params": {
                "heart_rate": 100,
                "systolic_bp": 100,
                "diastolic_bp": 60
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 0

    def test_pediatric_patient(self, test_client: Any) -> None:
        """Test pediatric patient (different thresholds)"""
        payload = {
            "params": {
                "heart_rate": 120,
                "systolic_bp": 90,
                "patient_type": "pediatric"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 0

    def test_elderly_patient(self, test_client: Any) -> None:
        """Test elderly patient"""
        payload = {
            "params": {
                "heart_rate": 80,
                "systolic_bp": 140,
                "patient_type": "elderly"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # SI = 80/140 = 0.57
        assert data["result"]["value"] < 0.7

    def test_hypotensive_tachycardia(self, test_client: Any) -> None:
        """Test hypotensive patient with tachycardia (shock)"""
        payload = {
            "params": {
                "heart_rate": 150,
                "systolic_bp": 70
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # SI = 150/70 = 2.14 (severe shock)
        assert data["result"]["value"] > 2.0

    def test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "heart_rate": 100
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
