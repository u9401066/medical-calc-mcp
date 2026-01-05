from typing import Any
"""
E2E Tests for ISS (Injury Severity Score) Calculator

Tests the ISS for Trauma through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestIssE2E:
    """E2E tests for ISS Calculator"""

    ENDPOINT = "/api/v1/calculate/iss"

    def test_minor_injury_score_1_8(self, test_client: Any) -> None:
        """Test minor injury (ISS 1-8)"""
        payload = {
            "params": {
                "head_neck_ais": 1,
                "face_ais": 1,
                "chest_ais": 0,
                "abdomen_ais": 0,
                "extremity_ais": 2,
                "external_ais": 1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # ISS = 1² + 1² + 2² = 6
        assert data["result"]["value"] <= 8

    def test_moderate_injury_score_9_15(self, test_client: Any) -> None:
        """Test moderate injury (ISS 9-15)"""
        payload = {
            "params": {
                "head_neck_ais": 2,
                "face_ais": 1,
                "chest_ais": 2,
                "abdomen_ais": 0,
                "extremity_ais": 2,
                "external_ais": 1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # ISS calculated from 3 highest scores squared
        assert 9 <= data["result"]["value"] <= 16

    def test_severe_injury_score_16_24(self, test_client: Any) -> None:
        """Test severe injury (ISS 16-24)"""
        payload = {
            "params": {
                "head_neck_ais": 3,
                "face_ais": 1,
                "chest_ais": 3,
                "abdomen_ais": 2,
                "extremity_ais": 2,
                "external_ais": 1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # ISS = 3² + 3² + 2² = 22
        assert data["result"]["value"] >= 16

    def test_critical_injury_score_25_plus(self, test_client: Any) -> None:
        """Test critical injury (ISS ≥25)"""
        payload = {
            "params": {
                "head_neck_ais": 4,
                "face_ais": 2,
                "chest_ais": 4,
                "abdomen_ais": 3,
                "extremity_ais": 2,
                "external_ais": 1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # ISS = 4² + 4² + 3² = 41
        assert data["result"]["value"] >= 25

    def test_unsurvivable_ais_6(self, test_client: Any) -> None:
        """Test unsurvivable injury (AIS 6 in any region)"""
        payload = {
            "params": {
                "head_neck_ais": 6,
                "face_ais": 1,
                "chest_ais": 2,
                "abdomen_ais": 1,
                "extremity_ais": 1,
                "external_ais": 1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # AIS 6 = automatic ISS 75
        assert data["result"]["value"] == 75

    def test_polytrauma(self, test_client: Any) -> None:
        """Test polytrauma patient"""
        payload = {
            "params": {
                "head_neck_ais": 3,
                "face_ais": 2,
                "chest_ais": 4,
                "abdomen_ais": 3,
                "extremity_ais": 3,
                "external_ais": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Multiple severe injuries
        assert data["result"]["value"] >= 25

    def test_isolated_head_injury(self, test_client: Any) -> None:
        """Test isolated severe head injury"""
        payload = {
            "params": {
                "head_neck_ais": 5,
                "face_ais": 0,
                "chest_ais": 0,
                "abdomen_ais": 0,
                "extremity_ais": 0,
                "external_ais": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # ISS = 5² = 25
        assert data["result"]["value"] == 25

    def test_isolated_chest_injury(self, test_client: Any) -> None:
        """Test isolated severe chest injury"""
        payload = {
            "params": {
                "head_neck_ais": 0,
                "face_ais": 0,
                "chest_ais": 5,
                "abdomen_ais": 0,
                "extremity_ais": 0,
                "external_ais": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 25

    def test_maximum_non_fatal_score_75(self, test_client: Any) -> None:
        """Test maximum ISS (75)"""
        payload = {
            "params": {
                "head_neck_ais": 5,
                "face_ais": 3,
                "chest_ais": 5,
                "abdomen_ais": 5,
                "extremity_ais": 3,
                "external_ais": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # ISS = 5² + 5² + 5² = 75
        assert data["result"]["value"] == 75

    def test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "head_neck_ais": 2,
                "chest_ais": 3
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
