from typing import Any
"""
E2E Tests for A-a Gradient Calculator

Tests the Alveolar-arterial oxygen gradient calculator through the REST API.
"""
from typing import Any
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestAaGradientE2E:
    """E2E tests for A-a Gradient Calculator"""

    ENDPOINT = "/api/v1/calculate/aa_gradient"

    def test_normal_gradient_room_air(self, test_client: Any) -> None:
        """Test normal A-a gradient on room air"""
        payload = {
            "params": {
                "pao2": 95,
                "paco2": 40,
                "fio2": 0.21
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Normal A-a gradient at sea level ~5-15
        assert 0 <= data["result"]["value"] <= 20

    def test_elevated_gradient(self, test_client: Any) -> None:
        """Test elevated A-a gradient (V/Q mismatch)"""
        payload = {
            "params": {
                "pao2": 60,
                "paco2": 35,
                "fio2": 0.21
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Elevated gradient indicates lung pathology
        assert data["result"]["value"] > 20

    def test_supplemental_oxygen(self, test_client: Any) -> None:
        """Test A-a gradient on supplemental oxygen"""
        payload = {
            "params": {
                "pao2": 150,
                "paco2": 38,
                "fio2": 0.40
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Higher FiO2 increases expected gradient
        assert data["result"]["value"] > 0

    def test_high_fio2(self, test_client: Any) -> None:
        """Test A-a gradient on high FiO2"""
        payload = {
            "params": {
                "pao2": 200,
                "paco2": 40,
                "fio2": 0.60
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 0

    def test_with_age_adjustment(self, test_client: Any) -> None:
        """Test with age (expected gradient increases with age)"""
        payload = {
            "params": {
                "pao2": 80,
                "paco2": 40,
                "fio2": 0.21,
                "age": 70
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Age adjusts expected gradient
        assert data["result"]["value"] > 0

    def test_altitude_adjustment(self, test_client: Any) -> None:
        """Test with altitude adjustment"""
        payload = {
            "params": {
                "pao2": 70,
                "paco2": 35,
                "fio2": 0.21,
                "atmospheric_pressure": 630  # ~5000 ft
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 0

    def test_custom_respiratory_quotient(self, test_client: Any) -> None:
        """Test with custom respiratory quotient"""
        payload = {
            "params": {
                "pao2": 90,
                "paco2": 40,
                "fio2": 0.21,
                "respiratory_quotient": 0.85
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 0

    def test_ards_presentation(self, test_client: Any) -> None:
        """Test ARDS presentation (severely elevated gradient)"""
        payload = {
            "params": {
                "pao2": 55,
                "paco2": 45,
                "fio2": 1.0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Very elevated gradient in ARDS
        assert data["result"]["value"] > 300

    def test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "pao2": 95
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
