from typing import Any
"""
E2E Tests for Delta Ratio Calculator

Tests the Delta Ratio calculator through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestDeltaRatioE2E:
    """E2E tests for Delta Ratio Calculator"""

    ENDPOINT = "/api/v1/calculate/delta_ratio"

    def test_pure_high_ag_acidosis(self, test_client: Any) -> None:
        """Test pure high AG metabolic acidosis (delta ratio 1-2)"""
        payload = {
            "params": {
                "anion_gap": 24,
                "bicarbonate": 12
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Delta AG = 24 - 12 = 12
        # Delta HCO3 = 24 - 12 = 12
        # Ratio = 12/12 = 1.0
        assert 1.0 <= data["result"]["value"] <= 2.0

    def test_combined_high_and_normal_ag(self, test_client: Any) -> None:
        """Test combined high AG and normal AG acidosis (delta ratio <1)"""
        payload = {
            "params": {
                "anion_gap": 20,
                "bicarbonate": 8,
                "normal_ag": 12,
                "normal_hco3": 24
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Delta AG = 20 - 12 = 8
        # Delta HCO3 = 24 - 8 = 16
        # Ratio = 8/16 = 0.5
        assert data["result"]["value"] < 1.0

    def test_metabolic_alkalosis_component(self, test_client: Any) -> None:
        """Test high AG acidosis with metabolic alkalosis (delta ratio >2)"""
        payload = {
            "params": {
                "anion_gap": 28,
                "bicarbonate": 20,
                "normal_ag": 12,
                "normal_hco3": 24
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Delta AG = 28 - 12 = 16
        # Delta HCO3 = 24 - 20 = 4
        # Ratio = 16/4 = 4.0
        assert data["result"]["value"] > 2.0

    def test_default_normal_values(self, test_client: Any) -> None:
        """Test with default normal AG and HCO3"""
        payload = {
            "params": {
                "anion_gap": 22,
                "bicarbonate": 14
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 0

    def test_custom_normal_values(self, test_client: Any) -> None:
        """Test with custom normal values"""
        payload = {
            "params": {
                "anion_gap": 20,
                "bicarbonate": 16,
                "normal_ag": 10,
                "normal_hco3": 26
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Delta AG = 20 - 10 = 10
        # Delta HCO3 = 26 - 16 = 10
        # Ratio = 10/10 = 1.0
        assert data["result"]["value"] == 1.0

    def test_severe_dka(self, test_client: Any) -> None:
        """Test severe DKA presentation"""
        payload = {
            "params": {
                "anion_gap": 35,
                "bicarbonate": 5
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Delta AG = 35 - 12 = 23
        # Delta HCO3 = 24 - 5 = 19
        # Ratio ≈ 1.2
        assert 1.0 <= data["result"]["value"] <= 2.0

    def test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "anion_gap": 20
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
