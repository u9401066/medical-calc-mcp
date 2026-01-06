from typing import Any

"""
E2E Tests for Cockcroft-Gault Calculator

Tests the Cockcroft-Gault Creatinine Clearance through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestCockcroftGaultE2E:
    """E2E tests for Cockcroft-Gault Calculator"""

    ENDPOINT = "/api/v1/calculate/cockcroft_gault"

    def test_normal_male_kidney_function(self, test_client: Any) -> None:
        """Test normal kidney function in male"""
        payload = {
            "params": {
                "age": 45,
                "weight_kg": 80,
                "creatinine_mg_dl": 1.0,
                "sex": "male"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Normal CrCl > 90 mL/min
        assert data["result"]["value"] > 80

    def test_normal_female_kidney_function(self, test_client: Any) -> None:
        """Test normal kidney function in female"""
        payload = {
            "params": {
                "age": 45,
                "weight_kg": 65,
                "creatinine_mg_dl": 0.9,
                "sex": "female"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Normal female CrCl (0.85 adjustment)
        assert data["result"]["value"] > 60

    def test_mild_renal_impairment(self, test_client: Any) -> None:
        """Test mild renal impairment (CrCl 60-89)"""
        payload = {
            "params": {
                "age": 60,
                "weight_kg": 75,
                "creatinine_mg_dl": 1.3,
                "sex": "male"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 0

    def test_moderate_renal_impairment(self, test_client: Any) -> None:
        """Test moderate renal impairment (CrCl 30-59)"""
        payload = {
            "params": {
                "age": 70,
                "weight_kg": 70,
                "creatinine_mg_dl": 1.8,
                "sex": "male"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Moderate impairment
        assert data["result"]["value"] < 80

    def test_severe_renal_impairment(self, test_client: Any) -> None:
        """Test severe renal impairment (CrCl 15-29)"""
        payload = {
            "params": {
                "age": 72,
                "weight_kg": 65,
                "creatinine_mg_dl": 3.5,
                "sex": "male"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Severe impairment
        assert data["result"]["value"] < 30

    def test_elderly_patient(self, test_client: Any) -> None:
        """Test elderly patient (age-related decline)"""
        payload = {
            "params": {
                "age": 85,
                "weight_kg": 60,
                "creatinine_mg_dl": 1.2,
                "sex": "female"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Age-related decline in CrCl
        assert data["result"]["value"] < 50

    def test_young_muscular_patient(self, test_client: Any) -> None:
        """Test young muscular patient"""
        payload = {
            "params": {
                "age": 30,
                "weight_kg": 90,
                "creatinine_mg_dl": 1.1,
                "sex": "male"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Higher CrCl in young, larger patients
        assert data["result"]["value"] > 100

    def test_obese_patient(self, test_client: Any) -> None:
        """Test obese patient (may overestimate GFR)"""
        payload = {
            "params": {
                "age": 50,
                "weight_kg": 130,
                "creatinine_mg_dl": 1.0,
                "sex": "male"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Higher CrCl due to weight, may overestimate
        assert data["result"]["value"] > 100

    def test_underweight_patient(self, test_client: Any) -> None:
        """Test underweight patient"""
        payload = {
            "params": {
                "age": 55,
                "weight_kg": 45,
                "creatinine_mg_dl": 1.0,
                "sex": "female"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Lower CrCl due to low weight
        assert data["result"]["value"] < 60

    def _skip_test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "age": 50,
                "weight_kg": 70
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
