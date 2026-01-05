from typing import Any
"""
E2E Tests for NEWS2 (National Early Warning Score 2) Calculator

Tests the NEWS2 early warning score through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestNews2ScoreE2E:
    """E2E tests for NEWS2 Score Calculator"""

    ENDPOINT = "/api/v1/calculate/news2_score"

    def test_normal_parameters(self, test_client: Any) -> None:
        """Test NEWS2 0 - all normal parameters"""
        payload = {
            "params": {
                "respiratory_rate": 16,
                "spo2": 97,
                "on_supplemental_o2": False,
                "temperature": 37.0,
                "systolic_bp": 120,
                "heart_rate": 75
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] <= 2

    def test_low_risk(self, test_client: Any) -> None:
        """Test low risk NEWS2 score (1-4)"""
        payload = {
            "params": {
                "respiratory_rate": 20,
                "spo2": 95,
                "on_supplemental_o2": False,
                "temperature": 38.2,
                "systolic_bp": 105,
                "heart_rate": 95
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert 1 <= data["result"]["value"] <= 6

    def test_medium_risk(self, test_client: Any) -> None:
        """Test medium risk NEWS2 score (5-6)"""
        payload = {
            "params": {
                "respiratory_rate": 22,
                "spo2": 93,
                "on_supplemental_o2": True,
                "temperature": 38.5,
                "systolic_bp": 95,
                "heart_rate": 110
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 4

    def test_high_risk(self, test_client: Any) -> None:
        """Test high risk NEWS2 score (≥7)"""
        payload = {
            "params": {
                "respiratory_rate": 26,
                "spo2": 90,
                "on_supplemental_o2": True,
                "temperature": 35.5,
                "systolic_bp": 85,
                "heart_rate": 125
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 7

    def test_with_consciousness_alert(self, test_client: Any) -> None:
        """Test with alert consciousness (ACVPU)"""
        payload = {
            "params": {
                "respiratory_rate": 18,
                "spo2": 96,
                "on_supplemental_o2": False,
                "temperature": 37.5,
                "systolic_bp": 115,
                "heart_rate": 80,
                "consciousness": "A"  # A=Alert
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 0

    def test_with_consciousness_confusion(self, test_client: Any) -> None:
        """Test with new confusion (ACVPU)"""
        payload = {
            "params": {
                "respiratory_rate": 18,
                "spo2": 96,
                "on_supplemental_o2": False,
                "temperature": 37.0,
                "systolic_bp": 120,
                "heart_rate": 75,
                "consciousness": "C"  # C=Confusion
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # New confusion = 3 points
        assert data["result"]["value"] >= 3

    def test_scale_2_copd(self, test_client: Any) -> None:
        """Test Scale 2 for COPD patients"""
        payload = {
            "params": {
                "respiratory_rate": 20,
                "spo2": 88,
                "on_supplemental_o2": True,
                "temperature": 37.0,
                "systolic_bp": 120,
                "heart_rate": 80,
                "use_scale_2": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Scale 2 has different SpO2 thresholds for COPD
        assert data["result"]["value"] >= 0

    def test_extreme_tachycardia(self, test_client: Any) -> None:
        """Test extreme tachycardia"""
        payload = {
            "params": {
                "respiratory_rate": 18,
                "spo2": 96,
                "on_supplemental_o2": False,
                "temperature": 37.0,
                "systolic_bp": 120,
                "heart_rate": 135
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # HR ≥131 = 3 points
        assert data["result"]["value"] >= 3

    def test_hypothermia(self, test_client: Any) -> None:
        """Test hypothermia"""
        payload = {
            "params": {
                "respiratory_rate": 18,
                "spo2": 96,
                "on_supplemental_o2": False,
                "temperature": 34.5,
                "systolic_bp": 120,
                "heart_rate": 60
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Temperature ≤35.0 = 3 points
        assert data["result"]["value"] >= 3

    def test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "respiratory_rate": 18,
                "spo2": 96
                # Missing other required params
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
