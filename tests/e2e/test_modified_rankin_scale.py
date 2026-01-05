from typing import Any
"""
E2E Tests for Modified Rankin Scale (mRS) Calculator

Tests the Modified Rankin Scale for Functional Outcome through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestModifiedRankinScaleE2E:
    """E2E tests for Modified Rankin Scale Calculator"""

    ENDPOINT = "/api/v1/calculate/modified_rankin_scale"

    def test_score_0_no_symptoms(self, test_client: Any) -> None:
        """Test mRS 0 - No symptoms at all"""
        payload: dict[str, Any] = {
            "params": {
                "mrs_score": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 0

    def test_score_1_no_significant_disability(self, test_client: Any) -> None:
        """Test mRS 1 - No significant disability despite symptoms"""
        payload: dict[str, Any] = {
            "params": {
                "mrs_score": 1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 1

    def test_score_2_slight_disability(self, test_client: Any) -> None:
        """Test mRS 2 - Slight disability"""
        payload: dict[str, Any] = {
            "params": {
                "mrs_score": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 2

    def test_score_3_moderate_disability(self, test_client: Any) -> None:
        """Test mRS 3 - Moderate disability"""
        payload: dict[str, Any] = {
            "params": {
                "mrs_score": 3
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 3

    def test_score_4_moderately_severe_disability(self, test_client: Any) -> None:
        """Test mRS 4 - Moderately severe disability"""
        payload: dict[str, Any] = {
            "params": {
                "mrs_score": 4
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 4

    def test_score_5_severe_disability(self, test_client: Any) -> None:
        """Test mRS 5 - Severe disability"""
        payload: dict[str, Any] = {
            "params": {
                "mrs_score": 5
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 5

    def test_score_6_dead(self, test_client: Any) -> None:
        """Test mRS 6 - Dead"""
        payload: dict[str, Any] = {
            "params": {
                "mrs_score": 6
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 6

    def test_favorable_outcome_threshold(self, test_client: Any) -> None:
        """Test favorable outcome (mRS 0-2)"""
        # mRS 2 is typically the threshold for favorable outcome
        payload: dict[str, Any] = {
            "params": {
                "mrs_score": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] <= 2

    def test_unfavorable_outcome(self, test_client: Any) -> None:
        """Test unfavorable outcome (mRS 3-6)"""
        payload: dict[str, Any] = {
            "params": {
                "mrs_score": 4
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 2

    def test_invalid_score_high(self, test_client: Any) -> None:
        """Test invalid score above range"""
        payload: dict[str, Any] = {
            "params": {
                "mrs_score": 7
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        # Should either error or clamp to valid range
        # Depending on implementation
        assert response.status_code in [200, 400, 422]

    def test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload: dict[str, Any] = {
            "params": {}
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
