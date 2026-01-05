from typing import Any
"""
E2E Tests for Mallampati Score Calculator

Tests the Mallampati airway classification through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestMallampatiScoreE2E:
    """E2E tests for Mallampati Score Calculator"""

    ENDPOINT = "/api/v1/calculate/mallampati_score"

    def test_mallampati_class_1(self, test_client: Any) -> None:
        """Test Mallampati Class 1 - Easy intubation"""
        payload: dict[str, Any] = {
            "params": {
                "mallampati_class": 1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 1

    def test_mallampati_class_2(self, test_client: Any) -> None:
        """Test Mallampati Class 2"""
        payload: dict[str, Any] = {
            "params": {
                "mallampati_class": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 2

    def test_mallampati_class_3(self, test_client: Any) -> None:
        """Test Mallampati Class 3 - Difficult intubation likely"""
        payload: dict[str, Any] = {
            "params": {
                "mallampati_class": 3
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 3

    def test_mallampati_class_4(self, test_client: Any) -> None:
        """Test Mallampati Class 4 - Most difficult intubation"""
        payload: dict[str, Any] = {
            "params": {
                "mallampati_class": 4
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 4

    def test_invalid_class_too_low(self, test_client: Any) -> None:
        """Test invalid class (too low)"""
        payload: dict[str, Any] = {
            "params": {
                "mallampati_class": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)

    def test_invalid_class_too_high(self, test_client: Any) -> None:
        """Test invalid class (too high)"""
        payload: dict[str, Any] = {
            "params": {
                "mallampati_class": 5
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)

    def test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload: dict[str, Any] = {
            "params": {}
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
