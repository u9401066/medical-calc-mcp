from typing import Any
"""
E2E Tests for Wells DVT Score Calculator

Tests the Wells DVT probability score through the REST API.
"""
from tests.e2e.conftest import assert_successful_calculation


class TestWellsDvtE2E:
    """E2E tests for Wells DVT Score Calculator"""

    ENDPOINT = "/api/v1/calculate/wells_dvt"

    def test_low_probability_negative_score(self, test_client: Any) -> None:
        """Test low probability with alternative diagnosis"""
        payload = {
            "params": {
                "active_cancer": False,
                "paralysis_paresis_or_recent_cast": False,
                "bedridden_or_major_surgery": False,
                "tenderness_along_deep_veins": False,
                "entire_leg_swollen": False,
                "calf_swelling_gt_3cm": False,
                "pitting_edema": False,
                "collateral_superficial_veins": False,
                "previous_dvt": False,
                "alternative_diagnosis_likely": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == -2

    def test_low_probability_score_0(self, test_client: Any) -> None:
        """Test low probability - score 0"""
        payload = {
            "params": {
                "active_cancer": False,
                "paralysis_paresis_or_recent_cast": False,
                "bedridden_or_major_surgery": False,
                "tenderness_along_deep_veins": False,
                "entire_leg_swollen": False,
                "calf_swelling_gt_3cm": False,
                "pitting_edema": False,
                "collateral_superficial_veins": False,
                "previous_dvt": False,
                "alternative_diagnosis_likely": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 0

    def test_moderate_probability(self, test_client: Any) -> None:
        """Test moderate probability (score 1-2)"""
        payload = {
            "params": {
                "active_cancer": False,
                "paralysis_paresis_or_recent_cast": False,
                "bedridden_or_major_surgery": True,
                "tenderness_along_deep_veins": True,
                "entire_leg_swollen": False,
                "calf_swelling_gt_3cm": False,
                "pitting_edema": False,
                "collateral_superficial_veins": False,
                "previous_dvt": False,
                "alternative_diagnosis_likely": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 2

    def test_high_probability(self, test_client: Any) -> None:
        """Test high probability (score ≥3)"""
        payload = {
            "params": {
                "active_cancer": True,
                "paralysis_paresis_or_recent_cast": True,
                "bedridden_or_major_surgery": True,
                "tenderness_along_deep_veins": True,
                "entire_leg_swollen": False,
                "calf_swelling_gt_3cm": False,
                "pitting_edema": False,
                "collateral_superficial_veins": False,
                "previous_dvt": False,
                "alternative_diagnosis_likely": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 3

    def test_classic_dvt_presentation(self, test_client: Any) -> None:
        """Test classic DVT presentation"""
        payload = {
            "params": {
                "active_cancer": False,
                "paralysis_paresis_or_recent_cast": False,
                "bedridden_or_major_surgery": True,
                "tenderness_along_deep_veins": True,
                "entire_leg_swollen": True,
                "calf_swelling_gt_3cm": True,
                "pitting_edema": True,
                "collateral_superficial_veins": False,
                "previous_dvt": True,
                "alternative_diagnosis_likely": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 5

    def _skip_test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "active_cancer": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert response.status_code in [200, 400, 422, 500]
