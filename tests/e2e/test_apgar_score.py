from typing import Any
"""
E2E Tests for APGAR Score Calculator

Tests the APGAR Score for Newborn Assessment through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestApgarScoreE2E:
    """E2E tests for APGAR Score Calculator"""

    ENDPOINT = "/api/v1/calculate/apgar_score"

    def test_perfect_score_10(self, test_client: Any) -> None:
        """Test perfect APGAR score (10)"""
        payload = {
            "params": {
                "appearance": 2,
                "pulse": 2,
                "grimace": 2,
                "activity": 2,
                "respiration": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 10

    def test_normal_score_8(self, test_client: Any) -> None:
        """Test normal APGAR score (8)"""
        payload = {
            "params": {
                "appearance": 1,  # Blue extremities
                "pulse": 2,
                "grimace": 2,
                "activity": 2,
                "respiration": 1  # Weak cry
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 8

    def test_moderately_depressed_score_5(self, test_client: Any) -> None:
        """Test moderately depressed score (5)"""
        payload = {
            "params": {
                "appearance": 1,
                "pulse": 1,
                "grimace": 1,
                "activity": 1,
                "respiration": 1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 5

    def test_severely_depressed_score_3(self, test_client: Any) -> None:
        """Test severely depressed score (3)"""
        payload = {
            "params": {
                "appearance": 0,
                "pulse": 1,
                "grimace": 1,
                "activity": 1,
                "respiration": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 3

    def test_critical_score_0(self, test_client: Any) -> None:
        """Test critical APGAR score (0)"""
        payload = {
            "params": {
                "appearance": 0,
                "pulse": 0,
                "grimace": 0,
                "activity": 0,
                "respiration": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 0

    def test_needs_resuscitation_threshold(self, test_client: Any) -> None:
        """Test score at resuscitation threshold (<7)"""
        payload = {
            "params": {
                "appearance": 1,
                "pulse": 2,
                "grimace": 1,
                "activity": 1,
                "respiration": 1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 6

    def test_vigorous_cry_pink(self, test_client: Any) -> None:
        """Test vigorous newborn"""
        payload = {
            "params": {
                "appearance": 2,
                "pulse": 2,
                "grimace": 2,
                "activity": 2,
                "respiration": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 10

    def test_bradycardic_newborn(self, test_client: Any) -> None:
        """Test newborn with bradycardia (<100)"""
        payload = {
            "params": {
                "appearance": 1,
                "pulse": 1,  # HR 60-99
                "grimace": 2,
                "activity": 2,
                "respiration": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 8

    def test_floppy_infant(self, test_client: Any) -> None:
        """Test floppy/hypotonic infant"""
        payload = {
            "params": {
                "appearance": 1,
                "pulse": 2,
                "grimace": 1,
                "activity": 0,  # Limp
                "respiration": 1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 5

    def test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "appearance": 2,
                "pulse": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
