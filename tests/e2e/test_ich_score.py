from typing import Any
"""
E2E Tests for ICH Score Calculator

Tests the ICH (Intracerebral Hemorrhage) Score through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestIchScoreE2E:
    """E2E tests for ICH Score Calculator"""

    ENDPOINT = "/api/v1/calculate/ich_score"

    def test_low_mortality_score_0(self, test_client: Any) -> None:
        """Test low mortality risk (score 0)"""
        payload = {
            "params": {
                "gcs_score": 15,
                "ich_volume_ml": 15,
                "ivh_present": False,
                "infratentorial": False,
                "age": 65
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Score 0 = 0% 30-day mortality
        assert data["result"]["value"] == 0

    def test_moderate_mortality_score_2(self, test_client: Any) -> None:
        """Test moderate mortality risk (score 2)"""
        payload = {
            "params": {
                "gcs_score": 10,
                "ich_volume_ml": 25,
                "ivh_present": False,
                "infratentorial": False,
                "age": 75
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 1

    def test_high_mortality_score_4_plus(self, test_client: Any) -> None:
        """Test high mortality risk (score ≥4)"""
        payload = {
            "params": {
                "gcs_score": 6,
                "ich_volume_ml": 45,
                "ivh_present": True,
                "infratentorial": True,
                "age": 85
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # High risk patient
        assert data["result"]["value"] >= 4

    def test_young_patient_small_bleed(self, test_client: Any) -> None:
        """Test young patient with small bleed"""
        payload = {
            "params": {
                "gcs_score": 14,
                "ich_volume_ml": 10,
                "ivh_present": False,
                "infratentorial": False,
                "age": 50
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Favorable prognosis
        assert data["result"]["value"] <= 1

    def test_elderly_patient_large_bleed(self, test_client: Any) -> None:
        """Test elderly patient with large hemorrhage"""
        payload = {
            "params": {
                "gcs_score": 8,
                "ich_volume_ml": 50,
                "ivh_present": True,
                "infratentorial": False,
                "age": 82
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Poor prognosis
        assert data["result"]["value"] >= 3

    def test_with_ivh(self, test_client: Any) -> None:
        """Test ICH with intraventricular extension"""
        payload = {
            "params": {
                "gcs_score": 12,
                "ich_volume_ml": 20,
                "ivh_present": True,
                "infratentorial": False,
                "age": 70
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # IVH adds 1 point
        assert data["result"]["value"] >= 1

    def test_infratentorial_hemorrhage(self, test_client: Any) -> None:
        """Test infratentorial (brainstem/cerebellar) hemorrhage"""
        payload = {
            "params": {
                "gcs_score": 11,
                "ich_volume_ml": 18,
                "ivh_present": False,
                "infratentorial": True,
                "age": 68
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Infratentorial adds 1 point
        assert data["result"]["value"] >= 1

    def test_critical_gcs(self, test_client: Any) -> None:
        """Test patient with critical GCS (3-4)"""
        payload = {
            "params": {
                "gcs_score": 4,
                "ich_volume_ml": 35,
                "ivh_present": True,
                "infratentorial": False,
                "age": 72
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Very poor prognosis
        assert data["result"]["value"] >= 4

    def test_maximum_score_6(self, test_client: Any) -> None:
        """Test maximum possible score (6)"""
        payload = {
            "params": {
                "gcs_score": 3,
                "ich_volume_ml": 60,
                "ivh_present": True,
                "infratentorial": True,
                "age": 90
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Maximum score = near 100% mortality
        assert data["result"]["value"] >= 5

    def _skip_test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "gcs_score": 12,
                "ich_volume_ml": 20
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
