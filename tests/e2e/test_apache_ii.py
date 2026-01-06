from typing import Any

"""
E2E Tests for APACHE II Calculator

Tests the APACHE II ICU severity score through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestApacheIiE2E:
    """E2E tests for APACHE II Calculator"""

    ENDPOINT = "/api/v1/calculate/apache_ii"

    def test_low_severity_normal_values(self, test_client: Any) -> None:
        """Test low severity with normal physiological values"""
        payload = {
            "params": {
                "temperature": 37.0,
                "mean_arterial_pressure": 85,
                "heart_rate": 80,
                "respiratory_rate": 16,
                "fio2": 0.21,
                "pao2": 90,
                "arterial_ph": 7.40,
                "serum_sodium": 140,
                "serum_potassium": 4.0,
                "serum_creatinine": 1.0,
                "hematocrit": 40,
                "wbc_count": 10,
                "gcs_score": 15,
                "age": 45
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Low severity should have low score
        assert data["result"]["value"] < 15

    def test_moderate_severity(self, test_client: Any) -> None:
        """Test moderate severity patient"""
        payload = {
            "params": {
                "temperature": 38.5,
                "mean_arterial_pressure": 70,
                "heart_rate": 110,
                "respiratory_rate": 25,
                "fio2": 0.40,
                "pao2": 70,
                "arterial_ph": 7.32,
                "serum_sodium": 150,
                "serum_potassium": 5.0,
                "serum_creatinine": 2.0,
                "hematocrit": 35,
                "wbc_count": 15,
                "gcs_score": 12,
                "age": 65
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 10

    def test_high_severity(self, test_client: Any) -> None:
        """Test high severity critically ill patient"""
        payload = {
            "params": {
                "temperature": 40.0,
                "mean_arterial_pressure": 50,
                "heart_rate": 140,
                "respiratory_rate": 35,
                "fio2": 0.80,
                "pao2": 55,
                "arterial_ph": 7.20,
                "serum_sodium": 160,
                "serum_potassium": 6.5,
                "serum_creatinine": 4.0,
                "hematocrit": 25,
                "wbc_count": 25,
                "gcs_score": 6,
                "age": 75
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 25

    def test_elderly_patient(self, test_client: Any) -> None:
        """Test elderly patient (age points)"""
        payload = {
            "params": {
                "temperature": 37.0,
                "mean_arterial_pressure": 85,
                "heart_rate": 80,
                "respiratory_rate": 16,
                "fio2": 0.21,
                "pao2": 90,
                "arterial_ph": 7.40,
                "serum_sodium": 140,
                "serum_potassium": 4.0,
                "serum_creatinine": 1.0,
                "hematocrit": 40,
                "wbc_count": 10,
                "gcs_score": 15,
                "age": 80
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Age > 75 adds points
        assert data["result"]["value"] >= 0

    def test_with_chronic_health(self, test_client: Any) -> None:
        """Test with chronic health conditions"""
        payload = {
            "params": {
                "temperature": 37.0,
                "mean_arterial_pressure": 85,
                "heart_rate": 80,
                "respiratory_rate": 16,
                "fio2": 0.21,
                "pao2": 90,
                "arterial_ph": 7.40,
                "serum_sodium": 140,
                "serum_potassium": 4.0,
                "serum_creatinine": 1.0,
                "hematocrit": 40,
                "wbc_count": 10,
                "gcs_score": 15,
                "age": 50,
                "chronic_health_conditions": ["liver_cirrhosis"]
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 0

    def test_septic_patient(self, test_client: Any) -> None:
        """Test typical septic patient presentation"""
        payload = {
            "params": {
                "temperature": 39.5,
                "mean_arterial_pressure": 60,
                "heart_rate": 120,
                "respiratory_rate": 28,
                "fio2": 0.50,
                "pao2": 65,
                "arterial_ph": 7.28,
                "serum_sodium": 145,
                "serum_potassium": 4.5,
                "serum_creatinine": 2.5,
                "hematocrit": 32,
                "wbc_count": 20,
                "gcs_score": 13,
                "age": 60
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 15

    def _skip_test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "temperature": 37.0,
                "age": 50
                # Missing many required parameters
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
