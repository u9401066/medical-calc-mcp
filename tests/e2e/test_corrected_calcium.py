from typing import Any
"""
E2E Tests for Corrected Calcium Calculator

Tests the Corrected Calcium for Albumin through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestCorrectedCalciumE2E:
    """E2E tests for Corrected Calcium Calculator"""

    ENDPOINT = "/api/v1/calculate/corrected_calcium"

    def test_normal_albumin_no_correction(self, test_client: Any) -> None:
        """Test with normal albumin (4.0 g/dL)"""
        payload = {
            "params": {
                "calcium_mg_dl": 9.0,
                "albumin_g_dl": 4.0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # No correction needed with normal albumin
        assert 8.8 <= data["result"]["value"] <= 9.2

    def test_low_albumin_correction(self, test_client: Any) -> None:
        """Test correction with low albumin"""
        payload = {
            "params": {
                "calcium_mg_dl": 8.0,
                "albumin_g_dl": 2.0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Corrected = 8.0 + 0.8*(4.0-2.0) = 9.6
        assert data["result"]["value"] > 9.0

    def test_very_low_albumin(self, test_client: Any) -> None:
        """Test with very low albumin (severe hypoalbuminemia)"""
        payload = {
            "params": {
                "calcium_mg_dl": 7.5,
                "albumin_g_dl": 1.5
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Significant correction
        assert data["result"]["value"] > 9.0

    def test_mild_hypoalbuminemia(self, test_client: Any) -> None:
        """Test with mild hypoalbuminemia"""
        payload = {
            "params": {
                "calcium_mg_dl": 8.5,
                "albumin_g_dl": 3.2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Corrected = 8.5 + 0.8*(4.0-3.2) = 9.14
        assert data["result"]["value"] > 8.5

    def test_hypercalcemia_with_low_albumin(self, test_client: Any) -> None:
        """Test hypercalcemia revealed after correction"""
        payload = {
            "params": {
                "calcium_mg_dl": 10.5,
                "albumin_g_dl": 2.5
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Corrected = 10.5 + 0.8*(4.0-2.5) = 11.7
        assert data["result"]["value"] > 11.0

    def test_true_hypocalcemia(self, test_client: Any) -> None:
        """Test true hypocalcemia (low calcium even after correction)"""
        payload = {
            "params": {
                "calcium_mg_dl": 6.5,
                "albumin_g_dl": 4.0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # No correction with normal albumin - true hypocalcemia
        assert data["result"]["value"] < 7.0

    def test_nephrotic_syndrome_patient(self, test_client: Any) -> None:
        """Test nephrotic syndrome patient with severe hypoalbuminemia"""
        payload = {
            "params": {
                "calcium_mg_dl": 7.8,
                "albumin_g_dl": 1.8
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Corrected = 7.8 + 0.8*(4.0-1.8) = 9.56
        assert data["result"]["value"] > 9.0

    def test_high_albumin(self, test_client: Any) -> None:
        """Test with high albumin (rare)"""
        payload = {
            "params": {
                "calcium_mg_dl": 10.0,
                "albumin_g_dl": 5.0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Negative correction with high albumin
        assert data["result"]["value"] < 10.0

    def test_critical_low_calcium(self, test_client: Any) -> None:
        """Test critical low calcium levels"""
        payload = {
            "params": {
                "calcium_mg_dl": 5.5,
                "albumin_g_dl": 2.5
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Corrected = 5.5 + 0.8*(4.0-2.5) = 6.7
        assert data["result"]["value"] < 7.5

    def test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "calcium_mg_dl": 9.0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
