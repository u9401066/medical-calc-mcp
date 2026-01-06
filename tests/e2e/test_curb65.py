from typing import Any

"""
E2E Tests for CURB-65 Calculator

Tests the CURB-65 pneumonia severity score through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestCurb65E2E:
    """E2E tests for CURB-65 Calculator"""

    ENDPOINT = "/api/v1/calculate/curb65"

    def test_low_risk_score_0(self, test_client: Any) -> None:
        """Test low risk - CURB-65 score 0"""
        payload = {
            "params": {
                "confusion": False,
                "bun_gt_19_or_urea_gt_7": False,
                "respiratory_rate_gte_30": False,
                "sbp_lt_90_or_dbp_lte_60": False,
                "age_gte_65": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 0

    def test_low_risk_score_1(self, test_client: Any) -> None:
        """Test low risk - CURB-65 score 1"""
        payload = {
            "params": {
                "confusion": False,
                "bun_gt_19_or_urea_gt_7": False,
                "respiratory_rate_gte_30": False,
                "sbp_lt_90_or_dbp_lte_60": False,
                "age_gte_65": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 1

    def test_moderate_risk_score_2(self, test_client: Any) -> None:
        """Test moderate risk - CURB-65 score 2"""
        payload = {
            "params": {
                "confusion": True,
                "bun_gt_19_or_urea_gt_7": False,
                "respiratory_rate_gte_30": False,
                "sbp_lt_90_or_dbp_lte_60": False,
                "age_gte_65": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 2

    def test_high_risk_score_3(self, test_client: Any) -> None:
        """Test high risk - CURB-65 score 3"""
        payload = {
            "params": {
                "confusion": True,
                "bun_gt_19_or_urea_gt_7": True,
                "respiratory_rate_gte_30": False,
                "sbp_lt_90_or_dbp_lte_60": False,
                "age_gte_65": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 3

    def test_very_high_risk_score_4(self, test_client: Any) -> None:
        """Test very high risk - CURB-65 score 4"""
        payload = {
            "params": {
                "confusion": True,
                "bun_gt_19_or_urea_gt_7": True,
                "respiratory_rate_gte_30": True,
                "sbp_lt_90_or_dbp_lte_60": False,
                "age_gte_65": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 4

    def test_maximum_risk_score_5(self, test_client: Any) -> None:
        """Test maximum risk - CURB-65 score 5"""
        payload = {
            "params": {
                "confusion": True,
                "bun_gt_19_or_urea_gt_7": True,
                "respiratory_rate_gte_30": True,
                "sbp_lt_90_or_dbp_lte_60": True,
                "age_gte_65": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 5

    def test_young_severe_pneumonia(self, test_client: Any) -> None:
        """Test young patient with severe pneumonia"""
        payload = {
            "params": {
                "confusion": True,
                "bun_gt_19_or_urea_gt_7": True,
                "respiratory_rate_gte_30": True,
                "sbp_lt_90_or_dbp_lte_60": True,
                "age_gte_65": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 4

    def test_elderly_mild_pneumonia(self, test_client: Any) -> None:
        """Test elderly with mild pneumonia"""
        payload = {
            "params": {
                "confusion": False,
                "bun_gt_19_or_urea_gt_7": False,
                "respiratory_rate_gte_30": False,
                "sbp_lt_90_or_dbp_lte_60": False,
                "age_gte_65": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 1

    def _skip_test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "confusion": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
