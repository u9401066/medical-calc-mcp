from typing import Any
"""
E2E Tests for Glasgow-Blatchford Score Calculator

Tests the Glasgow-Blatchford Score for Upper GI Bleeding through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestGlasgowBlatchfordE2E:
    """E2E tests for Glasgow-Blatchford Score Calculator"""

    ENDPOINT = "/api/v1/calculate/glasgow_blatchford"

    def test_low_risk_score_0(self, test_client: Any) -> None:
        """Test low risk patient (score 0) - can be discharged"""
        payload = {
            "params": {
                "bun_mg_dl": 18,
                "hemoglobin_g_dl": 13.5,
                "systolic_bp_mmhg": 120,
                "heart_rate_bpm": 80,
                "melena": False,
                "syncope": False,
                "hepatic_disease": False,
                "cardiac_failure": False,
                "sex": "male"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Score 0 = safe for outpatient management
        assert data["result"]["value"] <= 1

    def test_intermediate_risk(self, test_client: Any) -> None:
        """Test intermediate risk patient (score 3-5)"""
        payload = {
            "params": {
                "bun_mg_dl": 32,
                "hemoglobin_g_dl": 11.0,
                "systolic_bp_mmhg": 105,
                "heart_rate_bpm": 95,
                "melena": True,
                "syncope": False,
                "hepatic_disease": False,
                "cardiac_failure": False,
                "sex": "male"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 3

    def test_high_risk(self, test_client: Any) -> None:
        """Test high risk patient (score >6)"""
        payload = {
            "params": {
                "bun_mg_dl": 50,
                "hemoglobin_g_dl": 8.5,
                "systolic_bp_mmhg": 85,
                "heart_rate_bpm": 110,
                "melena": True,
                "syncope": True,
                "hepatic_disease": True,
                "cardiac_failure": False,
                "sex": "male"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # High risk - needs intervention
        assert data["result"]["value"] >= 8

    def test_female_with_anemia(self, test_client: Any) -> None:
        """Test female patient with significant anemia"""
        payload = {
            "params": {
                "bun_mg_dl": 25,
                "hemoglobin_g_dl": 9.0,
                "systolic_bp_mmhg": 110,
                "heart_rate_bpm": 90,
                "melena": True,
                "syncope": False,
                "hepatic_disease": False,
                "cardiac_failure": False,
                "sex": "female"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Female hemoglobin cutoffs differ
        assert data["result"]["value"] >= 3

    def test_elevated_bun(self, test_client: Any) -> None:
        """Test patient with elevated BUN"""
        payload = {
            "params": {
                "bun_mg_dl": 70,
                "hemoglobin_g_dl": 12.5,
                "systolic_bp_mmhg": 115,
                "heart_rate_bpm": 85,
                "melena": False,
                "syncope": False,
                "hepatic_disease": False,
                "cardiac_failure": False,
                "sex": "male"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # High BUN adds points
        assert data["result"]["value"] >= 4

    def test_hypotensive_tachycardic(self, test_client: Any) -> None:
        """Test hypotensive and tachycardic patient"""
        payload = {
            "params": {
                "bun_mg_dl": 28,
                "hemoglobin_g_dl": 10.5,
                "systolic_bp_mmhg": 80,
                "heart_rate_bpm": 115,
                "melena": True,
                "syncope": False,
                "hepatic_disease": False,
                "cardiac_failure": False,
                "sex": "male"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Hemodynamic instability adds significant points
        assert data["result"]["value"] >= 6

    def test_with_syncope(self, test_client: Any) -> None:
        """Test patient with syncope"""
        payload = {
            "params": {
                "bun_mg_dl": 22,
                "hemoglobin_g_dl": 11.5,
                "systolic_bp_mmhg": 95,
                "heart_rate_bpm": 100,
                "melena": True,
                "syncope": True,
                "hepatic_disease": False,
                "cardiac_failure": False,
                "sex": "male"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Syncope adds 2 points
        assert data["result"]["value"] >= 4

    def test_with_comorbidities(self, test_client: Any) -> None:
        """Test patient with hepatic disease and heart failure"""
        payload = {
            "params": {
                "bun_mg_dl": 35,
                "hemoglobin_g_dl": 10.0,
                "systolic_bp_mmhg": 100,
                "heart_rate_bpm": 95,
                "melena": True,
                "syncope": False,
                "hepatic_disease": True,
                "cardiac_failure": True,
                "sex": "male"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Comorbidities add points
        assert data["result"]["value"] >= 6

    def test_maximum_score(self, test_client: Any) -> None:
        """Test maximum possible score (23)"""
        payload = {
            "params": {
                "bun_mg_dl": 100,
                "hemoglobin_g_dl": 6.0,
                "systolic_bp_mmhg": 70,
                "heart_rate_bpm": 130,
                "melena": True,
                "syncope": True,
                "hepatic_disease": True,
                "cardiac_failure": True,
                "sex": "male"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Maximum or near maximum score
        assert data["result"]["value"] >= 15

    def test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "bun_mg_dl": 25,
                "hemoglobin_g_dl": 12.0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
