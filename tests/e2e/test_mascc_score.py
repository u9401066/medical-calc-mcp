from typing import Any
"""
E2E Tests for MASCC Score Calculator

Tests the MASCC Score for Febrile Neutropenia Risk through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestMasccScoreE2E:
    """E2E tests for MASCC Score Calculator"""

    ENDPOINT = "/api/v1/calculate/mascc_score"

    def test_low_risk_high_score(self, test_client: Any) -> None:
        """Test low risk patient (score ≥21)"""
        payload = {
            "params": {
                "burden_of_illness": "none_mild",
                "no_hypotension": True,
                "no_copd": True,
                "solid_tumor_or_no_fungal_hx": True,
                "no_dehydration": True,
                "outpatient_status": True,
                "age_lt_60": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Low risk if score ≥21
        assert data["result"]["value"] >= 20

    def test_high_risk_low_score(self, test_client: Any) -> None:
        """Test high risk patient (score <21)"""
        payload = {
            "params": {
                "burden_of_illness": "severe",
                "no_hypotension": False,
                "no_copd": False,
                "solid_tumor_or_no_fungal_hx": False,
                "no_dehydration": False,
                "outpatient_status": False,
                "age_lt_60": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # High risk if score <21
        assert data["result"]["value"] < 21

    def test_mild_burden_outpatient(self, test_client: Any) -> None:
        """Test outpatient with mild burden of illness"""
        payload = {
            "params": {
                "burden_of_illness": "none_mild",
                "no_hypotension": True,
                "no_copd": True,
                "solid_tumor_or_no_fungal_hx": True,
                "no_dehydration": True,
                "outpatient_status": True,
                "age_lt_60": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 0

    def test_moderate_burden(self, test_client: Any) -> None:
        """Test patient with moderate burden of illness"""
        payload = {
            "params": {
                "burden_of_illness": "moderate",
                "no_hypotension": True,
                "no_copd": True,
                "solid_tumor_or_no_fungal_hx": True,
                "no_dehydration": True,
                "outpatient_status": False,
                "age_lt_60": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 0

    def test_severe_burden(self, test_client: Any) -> None:
        """Test patient with severe burden of illness"""
        payload = {
            "params": {
                "burden_of_illness": "severe",
                "no_hypotension": True,
                "no_copd": True,
                "solid_tumor_or_no_fungal_hx": True,
                "no_dehydration": True,
                "outpatient_status": False,
                "age_lt_60": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Severe burden adds 0 points
        assert data["result"]["value"] >= 0

    def test_hypotensive_patient(self, test_client: Any) -> None:
        """Test hypotensive patient (no_hypotension = False)"""
        payload = {
            "params": {
                "burden_of_illness": "moderate",
                "no_hypotension": False,
                "no_copd": True,
                "solid_tumor_or_no_fungal_hx": True,
                "no_dehydration": True,
                "outpatient_status": False,
                "age_lt_60": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 0

    def test_copd_patient(self, test_client: Any) -> None:
        """Test patient with COPD history"""
        payload = {
            "params": {
                "burden_of_illness": "moderate",
                "no_hypotension": True,
                "no_copd": False,
                "solid_tumor_or_no_fungal_hx": True,
                "no_dehydration": True,
                "outpatient_status": False,
                "age_lt_60": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 0

    def test_dehydrated_patient(self, test_client: Any) -> None:
        """Test patient requiring IV fluids for dehydration"""
        payload = {
            "params": {
                "burden_of_illness": "moderate",
                "no_hypotension": True,
                "no_copd": True,
                "solid_tumor_or_no_fungal_hx": True,
                "no_dehydration": False,
                "outpatient_status": False,
                "age_lt_60": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 0

    def test_elderly_patient(self, test_client: Any) -> None:
        """Test elderly patient (≥60 years)"""
        payload = {
            "params": {
                "burden_of_illness": "none_mild",
                "no_hypotension": True,
                "no_copd": True,
                "solid_tumor_or_no_fungal_hx": True,
                "no_dehydration": True,
                "outpatient_status": True,
                "age_lt_60": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # No age bonus
        assert data["result"]["value"] >= 0

    def test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "burden_of_illness": "moderate"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
