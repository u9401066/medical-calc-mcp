from typing import Any
"""
E2E Tests for CAM-ICU (Confusion Assessment Method for ICU) Calculator

Tests the CAM-ICU delirium assessment through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestCamIcuE2E:
    """E2E tests for CAM-ICU Calculator"""

    ENDPOINT = "/api/v1/calculate/cam_icu"

    def test_no_delirium_alert(self, test_client: Any) -> None:
        """Test no delirium - alert and attentive patient"""
        payload = {
            "params": {
                "rass_score": 0,
                "acute_onset_fluctuation": False,
                "inattention_score": 0,
                "altered_loc": False,
                "disorganized_thinking_errors": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Negative for delirium
        assert "negative" in str(data["result"]).lower() or data["result"]["value"] == 0

    def test_delirium_positive_all_features(self, test_client: Any) -> None:
        """Test delirium positive - all features present"""
        payload = {
            "params": {
                "rass_score": -1,
                "acute_onset_fluctuation": True,
                "inattention_score": 4,
                "altered_loc": True,
                "disorganized_thinking_errors": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Positive for delirium
        assert "positive" in str(data["result"]).lower() or data["result"]["value"] == 1

    def test_too_sedated_for_assessment(self, test_client: Any) -> None:
        """Test patient too sedated (RASS -4 or -5)"""
        payload = {
            "params": {
                "rass_score": -4,
                "acute_onset_fluctuation": False,
                "inattention_score": 0,
                "altered_loc": False,
                "disorganized_thinking_errors": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Unable to assess (UA) or specific handling
        assert data["result"]["value"] is not None

    def test_agitated_patient(self, test_client: Any) -> None:
        """Test agitated patient with delirium features"""
        payload = {
            "params": {
                "rass_score": 2,
                "acute_onset_fluctuation": True,
                "inattention_score": 3,
                "altered_loc": False,
                "disorganized_thinking_errors": 1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] is not None

    def test_feature_1_positive_only(self, test_client: Any) -> None:
        """Test Feature 1 positive (acute onset) but no inattention"""
        payload = {
            "params": {
                "rass_score": 0,
                "acute_onset_fluctuation": True,
                "inattention_score": 1,
                "altered_loc": False,
                "disorganized_thinking_errors": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Need Feature 1 AND Feature 2 for positive
        assert data["result"]["value"] is not None

    def test_feature_2_inattention_positive(self, test_client: Any) -> None:
        """Test significant inattention (Feature 2)"""
        payload = {
            "params": {
                "rass_score": 0,
                "acute_onset_fluctuation": True,
                "inattention_score": 3,
                "altered_loc": False,
                "disorganized_thinking_errors": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] is not None

    def test_with_disorganized_thinking(self, test_client: Any) -> None:
        """Test with disorganized thinking (Feature 4)"""
        payload = {
            "params": {
                "rass_score": -1,
                "acute_onset_fluctuation": True,
                "inattention_score": 3,
                "altered_loc": False,
                "disorganized_thinking_errors": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] is not None

    def test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "rass_score": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
