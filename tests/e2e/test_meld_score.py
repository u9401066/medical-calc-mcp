from typing import Any
"""
E2E Tests for MELD Score Calculator

Tests the MELD (Model for End-Stage Liver Disease) score through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestMeldScoreE2E:
    """E2E tests for MELD Score Calculator"""

    ENDPOINT = "/api/v1/calculate/meld_score"

    def test_low_meld_score(self, test_client: Any) -> None:
        """Test low MELD score (good liver function)"""
        payload = {
            "params": {
                "creatinine": 0.8,
                "bilirubin": 1.0,
                "inr": 1.0,
                "sodium": 140,
                "on_dialysis": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Low MELD should be < 10
        assert data["result"]["value"] < 15

    def test_moderate_meld_score(self, test_client: Any) -> None:
        """Test moderate MELD score"""
        payload = {
            "params": {
                "creatinine": 1.5,
                "bilirubin": 3.0,
                "inr": 1.5,
                "sodium": 135,
                "on_dialysis": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert 10 <= data["result"]["value"] <= 25

    def test_high_meld_score(self, test_client: Any) -> None:
        """Test high MELD score (severe liver disease)"""
        payload = {
            "params": {
                "creatinine": 3.0,
                "bilirubin": 10.0,
                "inr": 2.5,
                "sodium": 128,
                "on_dialysis": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 25

    def test_on_dialysis(self, test_client: Any) -> None:
        """Test patient on dialysis (creatinine set to 4.0)"""
        payload = {
            "params": {
                "creatinine": 1.0,  # Will be set to 4.0
                "bilirubin": 5.0,
                "inr": 2.0,
                "sodium": 130,
                "on_dialysis": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 20

    def test_meld_na(self, test_client: Any) -> None:
        """Test MELD-Na with hyponatremia"""
        payload = {
            "params": {
                "creatinine": 2.0,
                "bilirubin": 5.0,
                "inr": 1.8,
                "sodium": 125,  # Low sodium adds to score
                "on_dialysis": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 15

    def test_minimum_values(self, test_client: Any) -> None:
        """Test with minimum lab values"""
        payload = {
            "params": {
                "creatinine": 0.5,
                "bilirubin": 0.5,
                "inr": 0.8,
                "sodium": 140,
                "on_dialysis": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # MELD has minimum score of 6
        assert data["result"]["value"] >= 6

    def test_maximum_score(self, test_client: Any) -> None:
        """Test maximum MELD score (capped at 40)"""
        payload = {
            "params": {
                "creatinine": 4.0,
                "bilirubin": 30.0,
                "inr": 4.0,
                "sodium": 120,
                "on_dialysis": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] <= 40

    def test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "creatinine": 1.0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
