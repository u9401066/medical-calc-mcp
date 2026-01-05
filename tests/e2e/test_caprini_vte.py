from typing import Any
"""
E2E Tests for Caprini VTE Score Calculator

Tests the Caprini VTE risk assessment through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestCapriniVteE2E:
    """E2E tests for Caprini VTE Score Calculator"""

    ENDPOINT = "/api/v1/calculate/caprini_vte"

    def test_very_low_risk(self, test_client: Any) -> None:
        """Test very low risk (score 0)"""
        payload: dict[str, Any] = {
            "params": {
                "age_years": 35,
                "minor_surgery": True,
                "major_surgery": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] <= 1

    def test_low_risk(self, test_client: Any) -> None:
        """Test low risk (score 1-2)"""
        payload: dict[str, Any] = {
            "params": {
                "age_years": 45,  # 41-60 = 1 point
                "minor_surgery": True  # +1 point = total 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert 1 <= data["result"]["value"] <= 2

    def test_moderate_risk(self, test_client: Any) -> None:
        """Test moderate risk (score 3-4)"""
        payload: dict[str, Any] = {
            "params": {
                "age_years": 65,  # 61-74 = 2 points
                "minor_surgery": True,  # +1 point
                "obesity_bmi_gt_25": True  # +1 point = total 4
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert 3 <= data["result"]["value"] <= 5

    def test_high_risk(self, test_client: Any) -> None:
        """Test high risk (score 5+)"""
        payload: dict[str, Any] = {
            "params": {
                "age_years": 70,
                "major_surgery": True,
                "history_dvt_pe": True,
                "malignancy": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 5

    def test_highest_risk_multiple_factors(self, test_client: Any) -> None:
        """Test highest risk with multiple factors"""
        payload: dict[str, Any] = {
            "params": {
                "age_years": 75,
                "major_surgery": True,
                "history_dvt_pe": True,
                "malignancy": True,
                "stroke_lt_1mo": True,
                "hip_pelvis_leg_fracture_lt_1mo": True,
                "spinal_cord_injury_lt_1mo": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 10

    def test_orthopedic_surgery(self, test_client: Any) -> None:
        """Test orthopedic surgery patient"""
        payload: dict[str, Any] = {
            "params": {
                "age_years": 68,
                "elective_arthroplasty": True,
                "bed_confined_gt_72hr": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 5

    def test_cancer_patient(self, test_client: Any) -> None:
        """Test cancer patient undergoing surgery"""
        payload: dict[str, Any] = {
            "params": {
                "age_years": 60,
                "major_surgery": True,
                "malignancy": True,
                "central_venous_access": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 4

    def test_pregnancy_related(self, test_client: Any) -> None:
        """Test pregnancy-related risk factors"""
        payload: dict[str, Any] = {
            "params": {
                "age_years": 30,
                "female": True,
                "pregnancy_or_postpartum": True,
                "bed_rest_medical": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 2

    def test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload: dict[str, Any] = {
            "params": {}
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
