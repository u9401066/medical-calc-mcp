from typing import Any

"""
E2E Tests for Aldrete Score Calculator

Tests the Aldrete Score for Post-Anesthesia Recovery through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestAldreteScoreE2E:
    """E2E tests for Aldrete Score Calculator"""

    ENDPOINT = "/api/v1/calculate/aldrete_score"

    def test_fully_recovered_patient(self, test_client: Any) -> None:
        """Test fully recovered patient (score 10)"""
        payload = {
            "params": {
                "activity": 2,
                "respiration": 2,
                "circulation": 2,
                "consciousness": 2,
                "oxygen_saturation": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 10

    def test_discharge_ready_score_9(self, test_client: Any) -> None:
        """Test patient ready for discharge (score ≥9)"""
        payload = {
            "params": {
                "activity": 2,
                "respiration": 2,
                "circulation": 2,
                "consciousness": 2,
                "oxygen_saturation": 1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 9

    def test_intermediate_recovery(self, test_client: Any) -> None:
        """Test intermediate recovery status"""
        payload = {
            "params": {
                "activity": 1,
                "respiration": 2,
                "circulation": 2,
                "consciousness": 1,
                "oxygen_saturation": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 8

    def test_poor_recovery(self, test_client: Any) -> None:
        """Test poor recovery status"""
        payload = {
            "params": {
                "activity": 0,
                "respiration": 1,
                "circulation": 1,
                "consciousness": 0,
                "oxygen_saturation": 1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 3

    def test_minimum_score(self, test_client: Any) -> None:
        """Test minimum possible score (0)"""
        payload = {
            "params": {
                "activity": 0,
                "respiration": 0,
                "circulation": 0,
                "consciousness": 0,
                "oxygen_saturation": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 0

    def test_respiratory_depression(self, test_client: Any) -> None:
        """Test patient with respiratory depression"""
        payload = {
            "params": {
                "activity": 2,
                "respiration": 0,
                "circulation": 2,
                "consciousness": 2,
                "oxygen_saturation": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 6

    def test_hemodynamic_instability(self, test_client: Any) -> None:
        """Test patient with hemodynamic instability"""
        payload = {
            "params": {
                "activity": 2,
                "respiration": 2,
                "circulation": 0,
                "consciousness": 2,
                "oxygen_saturation": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 8

    def test_decreased_consciousness(self, test_client: Any) -> None:
        """Test patient with decreased consciousness"""
        payload = {
            "params": {
                "activity": 1,
                "respiration": 2,
                "circulation": 2,
                "consciousness": 0,
                "oxygen_saturation": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 7

    def test_limited_mobility(self, test_client: Any) -> None:
        """Test patient with limited mobility"""
        payload = {
            "params": {
                "activity": 0,
                "respiration": 2,
                "circulation": 2,
                "consciousness": 2,
                "oxygen_saturation": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 8

    def _skip_test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "activity": 2,
                "respiration": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
