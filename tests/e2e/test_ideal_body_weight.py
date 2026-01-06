from typing import Any

"""
E2E Tests for Ideal Body Weight Calculator

Tests the Ideal Body Weight calculator through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestIdealBodyWeightE2E:
    """E2E tests for Ideal Body Weight Calculator"""

    ENDPOINT = "/api/v1/calculate/ideal_body_weight"

    def test_male_average_height(self, test_client: Any) -> None:
        """Test IBW for male with average height"""
        payload = {
            "params": {
                "height_cm": 175,
                "sex": "male"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Devine formula: 50 + 2.3 * (inches over 60)
        assert 60 <= data["result"]["value"] <= 80

    def test_female_average_height(self, test_client: Any) -> None:
        """Test IBW for female with average height"""
        payload = {
            "params": {
                "height_cm": 165,
                "sex": "female"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Devine formula: 45.5 + 2.3 * (inches over 60)
        assert 50 <= data["result"]["value"] <= 70

    def test_tall_male(self, test_client: Any) -> None:
        """Test IBW for tall male"""
        payload = {
            "params": {
                "height_cm": 190,
                "sex": "male"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 75

    def test_short_female(self, test_client: Any) -> None:
        """Test IBW for short female"""
        payload = {
            "params": {
                "height_cm": 150,
                "sex": "female"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] < 55

    def test_with_actual_weight_obese(self, test_client: Any) -> None:
        """Test with actual weight (obese patient)"""
        payload = {
            "params": {
                "height_cm": 170,
                "sex": "male",
                "actual_weight_kg": 120
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Should also calculate adjusted body weight
        assert data["result"]["value"] < 120

    def test_with_actual_weight_underweight(self, test_client: Any) -> None:
        """Test with actual weight (underweight patient)"""
        payload = {
            "params": {
                "height_cm": 175,
                "sex": "male",
                "actual_weight_kg": 55
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 55

    def _skip_test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "height_cm": 170
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
