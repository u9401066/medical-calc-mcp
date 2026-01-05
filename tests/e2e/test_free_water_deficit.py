from typing import Any
"""
E2E Tests for Free Water Deficit Calculator

Tests the Free Water Deficit calculator through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestFreeWaterDeficitE2E:
    """E2E tests for Free Water Deficit Calculator"""

    ENDPOINT = "/api/v1/calculate/free_water_deficit"

    def test_mild_hypernatremia(self, test_client: Any) -> None:
        """Test mild hypernatremia (Na 146-150)"""
        payload = {
            "params": {
                "current_sodium": 148,
                "weight_kg": 70,
                "patient_type": "adult_male"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Mild deficit expected
        assert 0 < data["result"]["value"] < 5

    def test_moderate_hypernatremia(self, test_client: Any) -> None:
        """Test moderate hypernatremia (Na 151-159)"""
        payload = {
            "params": {
                "current_sodium": 155,
                "weight_kg": 70,
                "patient_type": "adult_male"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Moderate deficit expected
        assert 2 < data["result"]["value"] < 8

    def test_severe_hypernatremia(self, test_client: Any) -> None:
        """Test severe hypernatremia (Na ≥160)"""
        payload = {
            "params": {
                "current_sodium": 165,
                "weight_kg": 70,
                "patient_type": "adult_male"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Large deficit expected
        assert data["result"]["value"] > 5

    def test_adult_female(self, test_client: Any) -> None:
        """Test adult female (lower TBW fraction)"""
        payload = {
            "params": {
                "current_sodium": 155,
                "weight_kg": 60,
                "patient_type": "adult_female"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Female has lower TBW (0.5 vs 0.6)
        assert data["result"]["value"] > 0

    def test_elderly_patient(self, test_client: Any) -> None:
        """Test elderly patient (lower TBW)"""
        payload = {
            "params": {
                "current_sodium": 155,
                "weight_kg": 65,
                "patient_type": "elderly"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 0

    def test_pediatric_patient(self, test_client: Any) -> None:
        """Test pediatric patient (higher TBW)"""
        payload = {
            "params": {
                "current_sodium": 152,
                "weight_kg": 20,
                "patient_type": "pediatric"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 0

    def test_custom_target_sodium(self, test_client: Any) -> None:
        """Test with custom target sodium"""
        payload = {
            "params": {
                "current_sodium": 160,
                "weight_kg": 70,
                "target_sodium": 145,
                "patient_type": "adult_male"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 0

    def test_with_correction_time(self, test_client: Any) -> None:
        """Test with correction time (rate calculation)"""
        payload = {
            "params": {
                "current_sodium": 158,
                "weight_kg": 70,
                "patient_type": "adult_male",
                "correction_time_hours": 48
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Should include rate information
        assert data["result"]["value"] > 0

    def test_borderline_hypernatremia(self, test_client: Any) -> None:
        """Test borderline hypernatremia (Na 146) - minimal deficit"""
        payload = {
            "params": {
                "current_sodium": 146,
                "weight_kg": 70,
                "patient_type": "adult_male"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Small deficit for borderline hypernatremia
        assert data["result"]["value"] > 0
        assert data["result"]["value"] < 5  # Relatively small deficit

    def test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "current_sodium": 155
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
