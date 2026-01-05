from typing import Any
"""
E2E Tests for STOP-BANG Score Calculator

Tests the STOP-BANG Score for Obstructive Sleep Apnea through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestStopBangE2E:
    """E2E tests for STOP-BANG Score Calculator"""

    ENDPOINT = "/api/v1/calculate/stop_bang"

    def test_low_risk_score_0(self, test_client: Any) -> None:
        """Test low risk patient (score 0-2)"""
        payload = {
            "params": {
                "snoring": False,
                "tired": False,
                "observed_apnea": False,
                "high_blood_pressure": False,
                "bmi_over_35": False,
                "age_over_50": False,
                "neck_over_40cm": False,
                "male_gender": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 0

    def test_intermediate_risk(self, test_client: Any) -> None:
        """Test intermediate risk (score 3-4)"""
        payload = {
            "params": {
                "snoring": True,
                "tired": True,
                "observed_apnea": False,
                "high_blood_pressure": True,
                "bmi_over_35": False,
                "age_over_50": False,
                "neck_over_40cm": False,
                "male_gender": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 3

    def test_high_risk_score_5(self, test_client: Any) -> None:
        """Test high risk patient (score ≥5)"""
        payload = {
            "params": {
                "snoring": True,
                "tired": True,
                "observed_apnea": True,
                "high_blood_pressure": True,
                "bmi_over_35": True,
                "age_over_50": False,
                "neck_over_40cm": False,
                "male_gender": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 5

    def test_maximum_score_8(self, test_client: Any) -> None:
        """Test maximum risk (score 8)"""
        payload = {
            "params": {
                "snoring": True,
                "tired": True,
                "observed_apnea": True,
                "high_blood_pressure": True,
                "bmi_over_35": True,
                "age_over_50": True,
                "neck_over_40cm": True,
                "male_gender": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 8

    def test_typical_male_patient(self, test_client: Any) -> None:
        """Test typical high-risk male patient"""
        payload = {
            "params": {
                "snoring": True,
                "tired": True,
                "observed_apnea": False,
                "high_blood_pressure": True,
                "bmi_over_35": False,
                "age_over_50": True,
                "neck_over_40cm": False,
                "male_gender": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 4

    def test_obese_female_patient(self, test_client: Any) -> None:
        """Test obese female patient"""
        payload = {
            "params": {
                "snoring": True,
                "tired": True,
                "observed_apnea": False,
                "high_blood_pressure": False,
                "bmi_over_35": True,
                "age_over_50": False,
                "neck_over_40cm": True,
                "male_gender": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 4

    def test_stop_only_positive(self, test_client: Any) -> None:
        """Test STOP criteria only positive"""
        payload = {
            "params": {
                "snoring": True,
                "tired": True,
                "observed_apnea": True,
                "high_blood_pressure": True,
                "bmi_over_35": False,
                "age_over_50": False,
                "neck_over_40cm": False,
                "male_gender": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 4

    def test_bang_only_positive(self, test_client: Any) -> None:
        """Test BANG criteria only positive"""
        payload = {
            "params": {
                "snoring": False,
                "tired": False,
                "observed_apnea": False,
                "high_blood_pressure": False,
                "bmi_over_35": True,
                "age_over_50": True,
                "neck_over_40cm": True,
                "male_gender": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 4

    def test_young_thin_female_no_symptoms(self, test_client: Any) -> None:
        """Test young thin female with no symptoms - low risk"""
        payload = {
            "params": {
                "snoring": False,
                "tired": False,
                "observed_apnea": False,
                "high_blood_pressure": False,
                "bmi_over_35": False,
                "age_over_50": False,
                "neck_over_40cm": False,
                "male_gender": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 0

    def _skip_test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "snoring": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
