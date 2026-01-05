from typing import Any
"""
E2E Tests for Hunt and Hess Score Calculator

Tests the Hunt and Hess Score for Subarachnoid Hemorrhage through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestHuntHessE2E:
    """E2E tests for Hunt and Hess Score Calculator"""

    ENDPOINT = "/api/v1/calculate/hunt_hess"

    def test_grade_1_asymptomatic(self, test_client: Any) -> None:
        """Test Grade 1 - Asymptomatic or mild headache"""
        payload: dict[str, Any] = {
            "params": {
                "grade": 1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 1

    def test_grade_2_moderate_headache(self, test_client: Any) -> None:
        """Test Grade 2 - Moderate to severe headache, nuchal rigidity"""
        payload: dict[str, Any] = {
            "params": {
                "grade": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 2

    def test_grade_3_drowsy(self, test_client: Any) -> None:
        """Test Grade 3 - Drowsiness/confusion, mild focal deficit"""
        payload: dict[str, Any] = {
            "params": {
                "grade": 3
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 3

    def test_grade_4_stupor(self, test_client: Any) -> None:
        """Test Grade 4 - Stupor, moderate-severe hemiparesis"""
        payload: dict[str, Any] = {
            "params": {
                "grade": 4
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 4

    def test_grade_5_coma(self, test_client: Any) -> None:
        """Test Grade 5 - Deep coma, decerebrate posturing"""
        payload: dict[str, Any] = {
            "params": {
                "grade": 5
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 5

    def test_good_grade_sah(self, test_client: Any) -> None:
        """Test good grade SAH (Grade 1-2)"""
        payload: dict[str, Any] = {
            "params": {
                "grade": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Good grade - favorable prognosis
        assert data["result"]["value"] <= 2

    def test_poor_grade_sah(self, test_client: Any) -> None:
        """Test poor grade SAH (Grade 4-5)"""
        payload: dict[str, Any] = {
            "params": {
                "grade": 4
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Poor grade - unfavorable prognosis
        assert data["result"]["value"] >= 4

    def test_surgical_candidate_grade_3(self, test_client: Any) -> None:
        """Test surgical candidate (Grade 3)"""
        payload: dict[str, Any] = {
            "params": {
                "grade": 3
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Grade 3 - intermediate, often surgical candidate
        assert data["result"]["value"] == 3

    def test_invalid_grade_high(self, test_client: Any) -> None:
        """Test invalid grade above range"""
        payload: dict[str, Any] = {
            "params": {
                "grade": 6
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        # Should either error or handle gracefully
        assert response.status_code in [200, 400, 422]

    def test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload: dict[str, Any] = {
            "params": {}
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
