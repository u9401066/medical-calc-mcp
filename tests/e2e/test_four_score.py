from typing import Any
"""
E2E Tests for FOUR Score Calculator

Tests the Full Outline of UnResponsiveness (FOUR) Score through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestFourScoreE2E:
    """E2E tests for FOUR Score Calculator"""

    ENDPOINT = "/api/v1/calculate/four_score"

    def test_maximum_score_normal(self, test_client: Any) -> None:
        """Test maximum score (16) - fully conscious"""
        payload = {
            "params": {
                "eye_response": 4,
                "motor_response": 4,
                "brainstem_reflexes": 4,
                "respiration": 4
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 16

    def test_minimum_score_coma(self, test_client: Any) -> None:
        """Test minimum score (0) - deep coma"""
        payload = {
            "params": {
                "eye_response": 0,
                "motor_response": 0,
                "brainstem_reflexes": 0,
                "respiration": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 0

    def test_locked_in_syndrome(self, test_client: Any) -> None:
        """Test locked-in syndrome pattern"""
        payload = {
            "params": {
                "eye_response": 4,  # Can blink/track
                "motor_response": 0,  # No motor response
                "brainstem_reflexes": 4,  # Preserved
                "respiration": 4  # Normal breathing
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Locked-in has preserved eyes and brainstem
        assert data["result"]["value"] == 12

    def test_sedated_icu_patient(self, test_client: Any) -> None:
        """Test sedated ICU patient"""
        payload = {
            "params": {
                "eye_response": 1,
                "motor_response": 2,
                "brainstem_reflexes": 4,
                "respiration": 1  # Intubated
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 8

    def test_brainstem_death_pattern(self, test_client: Any) -> None:
        """Test pattern consistent with brainstem death"""
        payload = {
            "params": {
                "eye_response": 0,
                "motor_response": 0,
                "brainstem_reflexes": 0,
                "respiration": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # All zeros suggest brain death
        assert data["result"]["value"] == 0

    def test_improving_patient(self, test_client: Any) -> None:
        """Test patient showing improvement"""
        payload = {
            "params": {
                "eye_response": 3,
                "motor_response": 3,
                "brainstem_reflexes": 4,
                "respiration": 3
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 13

    def test_poor_prognosis_indicators(self, test_client: Any) -> None:
        """Test patient with poor prognostic indicators"""
        payload = {
            "params": {
                "eye_response": 0,
                "motor_response": 1,
                "brainstem_reflexes": 2,
                "respiration": 1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Low score indicates poor prognosis
        assert data["result"]["value"] <= 4

    def test_eye_tracking_present(self, test_client: Any) -> None:
        """Test patient with eye tracking"""
        payload = {
            "params": {
                "eye_response": 4,
                "motor_response": 2,
                "brainstem_reflexes": 3,
                "respiration": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 11

    def test_posturing_response(self, test_client: Any) -> None:
        """Test patient with posturing response"""
        payload = {
            "params": {
                "eye_response": 1,
                "motor_response": 1,  # Posturing
                "brainstem_reflexes": 3,
                "respiration": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 7

    def test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "eye_response": 4,
                "motor_response": 4
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
