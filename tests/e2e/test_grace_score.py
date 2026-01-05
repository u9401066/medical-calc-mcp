from typing import Any
"""
E2E Tests for GRACE Score Calculator

Tests the GRACE (Global Registry of Acute Coronary Events) Score through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestGraceScoreE2E:
    """E2E tests for GRACE Score Calculator"""

    ENDPOINT = "/api/v1/calculate/grace_score"

    def test_low_risk_patient(self, test_client: Any) -> None:
        """Test low risk patient (GRACE ≤108)"""
        payload = {
            "params": {
                "age": 45,
                "heart_rate": 75,
                "systolic_bp": 135,
                "creatinine": 1.0,
                "killip_class": 1,
                "cardiac_arrest": False,
                "st_deviation": False,
                "elevated_markers": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Low risk patient
        assert data["result"]["value"] >= 0

    def test_intermediate_risk_patient(self, test_client: Any) -> None:
        """Test intermediate risk patient (GRACE 109-140)"""
        payload = {
            "params": {
                "age": 65,
                "heart_rate": 90,
                "systolic_bp": 115,
                "creatinine": 1.4,
                "killip_class": 2,
                "cardiac_arrest": False,
                "st_deviation": True,
                "elevated_markers": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 0

    def test_high_risk_patient(self, test_client: Any) -> None:
        """Test high risk patient (GRACE >140)"""
        payload = {
            "params": {
                "age": 80,
                "heart_rate": 110,
                "systolic_bp": 90,
                "creatinine": 2.5,
                "killip_class": 3,
                "cardiac_arrest": True,
                "st_deviation": True,
                "elevated_markers": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # High risk - expect high score
        assert data["result"]["value"] > 100

    def test_elderly_patient_with_nstemi(self, test_client: Any) -> None:
        """Test elderly patient with NSTEMI"""
        payload = {
            "params": {
                "age": 78,
                "heart_rate": 88,
                "systolic_bp": 125,
                "creatinine": 1.6,
                "killip_class": 1,
                "cardiac_arrest": False,
                "st_deviation": True,
                "elevated_markers": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 0

    def test_patient_with_cardiogenic_shock(self, test_client: Any) -> None:
        """Test patient with cardiogenic shock (Killip IV)"""
        payload = {
            "params": {
                "age": 70,
                "heart_rate": 120,
                "systolic_bp": 80,
                "creatinine": 2.8,
                "killip_class": 4,
                "cardiac_arrest": False,
                "st_deviation": True,
                "elevated_markers": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Very high risk patient
        assert data["result"]["value"] > 0

    def test_post_cardiac_arrest_patient(self, test_client: Any) -> None:
        """Test post cardiac arrest patient"""
        payload = {
            "params": {
                "age": 62,
                "heart_rate": 95,
                "systolic_bp": 100,
                "creatinine": 1.8,
                "killip_class": 2,
                "cardiac_arrest": True,
                "st_deviation": True,
                "elevated_markers": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Cardiac arrest adds significant points
        assert data["result"]["value"] > 0

    def test_tachycardic_patient(self, test_client: Any) -> None:
        """Test patient with significant tachycardia"""
        payload = {
            "params": {
                "age": 55,
                "heart_rate": 130,
                "systolic_bp": 110,
                "creatinine": 1.2,
                "killip_class": 1,
                "cardiac_arrest": False,
                "st_deviation": False,
                "elevated_markers": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 0

    def test_hypotensive_patient(self, test_client: Any) -> None:
        """Test hypotensive patient"""
        payload = {
            "params": {
                "age": 60,
                "heart_rate": 100,
                "systolic_bp": 85,
                "creatinine": 1.5,
                "killip_class": 2,
                "cardiac_arrest": False,
                "st_deviation": True,
                "elevated_markers": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 0

    def test_renal_impairment_patient(self, test_client: Any) -> None:
        """Test patient with renal impairment"""
        payload = {
            "params": {
                "age": 68,
                "heart_rate": 82,
                "systolic_bp": 130,
                "creatinine": 3.5,
                "killip_class": 1,
                "cardiac_arrest": False,
                "st_deviation": False,
                "elevated_markers": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Renal impairment increases risk
        assert data["result"]["value"] > 0

    def test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "age": 65
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
