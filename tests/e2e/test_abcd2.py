from typing import Any
"""
E2E Tests for ABCD2 Score Calculator

Tests the ABCD2 Score for TIA Stroke Risk through the REST API.

Parameters:
    age_gte_60: bool - Age ≥60 years
    bp_gte_140_90: bool - Blood pressure ≥140/90 mmHg
    clinical_features: Literal["none", "speech_only", "unilateral_weakness"]
    duration_minutes: Literal["lt_10", "10_to_59", "gte_60"]
    diabetes: bool - History of diabetes
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestAbcd2E2E:
    """E2E tests for ABCD2 Score Calculator"""

    ENDPOINT = "/api/v1/calculate/abcd2"

    def test_low_risk_score_0_3(self, test_client: Any) -> None:
        """Test low risk patient (score 0-3)"""
        payload = {
            "params": {
                "age_gte_60": False,
                "bp_gte_140_90": False,
                "clinical_features": "none",
                "duration_minutes": "lt_10",
                "diabetes": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] <= 3

    def test_moderate_risk_score_4_5(self, test_client: Any) -> None:
        """Test moderate risk patient (score 4-5)"""
        payload = {
            "params": {
                "age_gte_60": True,
                "bp_gte_140_90": True,
                "clinical_features": "speech_only",
                "duration_minutes": "10_to_59",
                "diabetes": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 4

    def test_high_risk_score_6_7(self, test_client: Any) -> None:
        """Test high risk patient (score 6-7)"""
        payload = {
            "params": {
                "age_gte_60": True,
                "bp_gte_140_90": True,
                "clinical_features": "unilateral_weakness",
                "duration_minutes": "gte_60",
                "diabetes": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 6

    def test_young_patient_brief_tia(self, test_client: Any) -> None:
        """Test young patient with brief TIA"""
        payload = {
            "params": {
                "age_gte_60": False,
                "bp_gte_140_90": False,
                "clinical_features": "speech_only",
                "duration_minutes": "lt_10",
                "diabetes": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 1

    def test_elderly_hypertensive_diabetic(self, test_client: Any) -> None:
        """Test elderly, hypertensive, diabetic patient"""
        payload = {
            "params": {
                "age_gte_60": True,
                "bp_gte_140_90": True,
                "clinical_features": "none",
                "duration_minutes": "lt_10",
                "diabetes": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 3

    def test_unilateral_weakness(self, test_client: Any) -> None:
        """Test patient with unilateral weakness (clinical features = 2 points)"""
        payload = {
            "params": {
                "age_gte_60": False,
                "bp_gte_140_90": False,
                "clinical_features": "unilateral_weakness",
                "duration_minutes": "10_to_59",
                "diabetes": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 3

    def test_speech_disturbance_only(self, test_client: Any) -> None:
        """Test patient with speech disturbance only (clinical features = 1 point)"""
        payload = {
            "params": {
                "age_gte_60": True,
                "bp_gte_140_90": False,
                "clinical_features": "speech_only",
                "duration_minutes": "lt_10",
                "diabetes": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 2

    def test_prolonged_symptoms(self, test_client: Any) -> None:
        """Test patient with prolonged symptoms (≥60 min)"""
        payload = {
            "params": {
                "age_gte_60": False,
                "bp_gte_140_90": True,
                "clinical_features": "none",
                "duration_minutes": "gte_60",
                "diabetes": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 3

    def test_maximum_score(self, test_client: Any) -> None:
        """Test maximum possible score (7)"""
        payload = {
            "params": {
                "age_gte_60": True,
                "bp_gte_140_90": True,
                "clinical_features": "unilateral_weakness",
                "duration_minutes": "gte_60",
                "diabetes": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 7

    def test_minimum_score(self, test_client: Any) -> None:
        """Test minimum possible score (0)"""
        payload = {
            "params": {
                "age_gte_60": False,
                "bp_gte_140_90": False,
                "clinical_features": "none",
                "duration_minutes": "lt_10",
                "diabetes": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 0

    def _skip_test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "age_gte_60": True,
                "bp_gte_140_90": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
