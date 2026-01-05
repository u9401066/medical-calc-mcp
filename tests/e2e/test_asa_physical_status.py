from typing import Any
"""
E2E Tests for ASA Physical Status Calculator

Tests the ASA Physical Status classification through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestAsaPhysicalStatusE2E:
    """E2E tests for ASA Physical Status Calculator"""

    ENDPOINT = "/api/v1/calculate/asa_physical_status"

    def test_asa_class_1(self, test_client: Any) -> None:
        """Test ASA Class 1 - Normal healthy patient"""
        payload: dict[str, Any] = {
            "params": {
                "asa_class": 1,
                "is_emergency": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 1

    def test_asa_class_2(self, test_client: Any) -> None:
        """Test ASA Class 2 - Mild systemic disease"""
        payload: dict[str, Any] = {
            "params": {
                "asa_class": 2,
                "is_emergency": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 2

    def test_asa_class_3(self, test_client: Any) -> None:
        """Test ASA Class 3 - Severe systemic disease"""
        payload: dict[str, Any] = {
            "params": {
                "asa_class": 3,
                "is_emergency": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 3

    def test_asa_class_4(self, test_client: Any) -> None:
        """Test ASA Class 4 - Life-threatening disease"""
        payload: dict[str, Any] = {
            "params": {
                "asa_class": 4,
                "is_emergency": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 4

    def test_asa_class_5(self, test_client: Any) -> None:
        """Test ASA Class 5 - Moribund patient"""
        payload: dict[str, Any] = {
            "params": {
                "asa_class": 5,
                "is_emergency": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 5

    def test_asa_class_6(self, test_client: Any) -> None:
        """Test ASA Class 6 - Brain-dead organ donor"""
        payload: dict[str, Any] = {
            "params": {
                "asa_class": 6,
                "is_emergency": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 6

    def test_emergency_modifier(self, test_client: Any) -> None:
        """Test with emergency modifier (E)"""
        payload: dict[str, Any] = {
            "params": {
                "asa_class": 3,
                "is_emergency": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Emergency should be noted in interpretation
        assert data["result"]["value"] == 3

    def test_default_non_emergency(self, test_client: Any) -> None:
        """Test default non-emergency when not specified"""
        payload: dict[str, Any] = {
            "params": {
                "asa_class": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 2

    def test_invalid_asa_class_too_low(self, test_client: Any) -> None:
        """Test invalid ASA class (too low)"""
        payload: dict[str, Any] = {
            "params": {
                "asa_class": 0,
                "is_emergency": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)

    def test_invalid_asa_class_too_high(self, test_client: Any) -> None:
        """Test invalid ASA class (too high)"""
        payload: dict[str, Any] = {
            "params": {
                "asa_class": 7,
                "is_emergency": False
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
