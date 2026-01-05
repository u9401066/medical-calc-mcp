from typing import Any
"""
E2E Tests for Body Surface Area (BSA) Calculator

Tests the BSA Calculator through the REST API.

Parameters:
    height_cm: float - Height in centimeters
    weight_kg: float - Weight in kilograms
    formula: str - Formula to use ("mosteller", "dubois", "haycock", "boyd")
             Default: "mosteller"
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestBodySurfaceAreaE2E:
    """E2E tests for BSA Calculator"""

    ENDPOINT = "/api/v1/calculate/body_surface_area"

    def test_average_adult(self, test_client: Any) -> None:
        """Test average adult BSA"""
        payload = {
            "params": {
                "height_cm": 170,
                "weight_kg": 70
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Average adult BSA is ~1.7-1.9 m²
        assert 1.5 <= data["result"]["value"] <= 2.2

    def test_tall_heavy_adult(self, test_client: Any) -> None:
        """Test tall, heavy adult"""
        payload = {
            "params": {
                "height_cm": 190,
                "weight_kg": 100
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Larger BSA
        assert data["result"]["value"] > 2.0

    def test_short_light_adult(self, test_client: Any) -> None:
        """Test short, light adult"""
        payload = {
            "params": {
                "height_cm": 150,
                "weight_kg": 45
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Smaller BSA
        assert data["result"]["value"] < 1.5

    def test_pediatric_toddler(self, test_client: Any) -> None:
        """Test toddler BSA"""
        payload = {
            "params": {
                "height_cm": 90,
                "weight_kg": 13
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Toddler BSA ~0.5-0.6 m²
        assert 0.4 <= data["result"]["value"] <= 0.8

    def test_pediatric_school_age(self, test_client: Any) -> None:
        """Test school-age child BSA"""
        payload = {
            "params": {
                "height_cm": 120,
                "weight_kg": 25
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # School-age child BSA ~0.9-1.0 m²
        assert 0.8 <= data["result"]["value"] <= 1.2

    def test_obese_patient(self, test_client: Any) -> None:
        """Test obese patient"""
        payload = {
            "params": {
                "height_cm": 165,
                "weight_kg": 120
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Higher BSA in obese patients
        assert data["result"]["value"] > 2.0

    def test_cachectic_patient(self, test_client: Any) -> None:
        """Test cachectic/underweight patient"""
        payload = {
            "params": {
                "height_cm": 170,
                "weight_kg": 40
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Lower BSA in underweight patients
        assert data["result"]["value"] < 1.4

    def test_infant(self, test_client: Any) -> None:
        """Test infant BSA"""
        payload = {
            "params": {
                "height_cm": 60,
                "weight_kg": 6
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Infant BSA ~0.25-0.35 m²
        assert 0.2 <= data["result"]["value"] <= 0.5

    def test_very_tall_adult(self, test_client: Any) -> None:
        """Test very tall adult"""
        payload = {
            "params": {
                "height_cm": 200,
                "weight_kg": 85
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Taller individuals have higher BSA
        assert data["result"]["value"] > 2.0

    def _skip_test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "height_cm": 170
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
