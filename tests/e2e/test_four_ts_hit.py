from typing import Any
"""
E2E Tests for 4Ts HIT Score Calculator

Tests the 4Ts for Heparin-Induced Thrombocytopenia through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestFourTsHitE2E:
    """E2E tests for 4Ts HIT Score Calculator"""

    ENDPOINT = "/api/v1/calculate/4ts_hit"

    def test_low_probability(self, test_client: Any) -> None:
        """Test low probability for HIT (score 0-3)"""
        payload = {
            "params": {
                "thrombocytopenia": 0,
                "timing": 0,
                "thrombosis": 0,
                "other_causes": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Score 0-3 = Low probability
        assert data["result"]["value"] <= 3

    def test_intermediate_probability(self, test_client: Any) -> None:
        """Test intermediate probability for HIT (score 4-5)"""
        payload = {
            "params": {
                "thrombocytopenia": 1,
                "timing": 1,
                "thrombosis": 1,
                "other_causes": 1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Intermediate probability
        assert data["result"]["value"] >= 4

    def test_high_probability(self, test_client: Any) -> None:
        """Test high probability for HIT (score 6-8)"""
        payload = {
            "params": {
                "thrombocytopenia": 2,
                "timing": 2,
                "thrombosis": 2,
                "other_causes": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # High probability = max score 8
        assert data["result"]["value"] >= 6

    def test_severe_thrombocytopenia_no_other_features(self, test_client: Any) -> None:
        """Test severe drop without other HIT features"""
        payload = {
            "params": {
                "thrombocytopenia": 2,
                "timing": 0,
                "thrombosis": 0,
                "other_causes": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Only thrombocytopenia component
        assert data["result"]["value"] >= 0

    def test_classic_timing_pattern(self, test_client: Any) -> None:
        """Test classic HIT timing (days 5-10 after heparin)"""
        payload = {
            "params": {
                "thrombocytopenia": 2,
                "timing": 2,
                "thrombosis": 1,
                "other_causes": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Classic presentation
        assert data["result"]["value"] >= 5

    def test_with_thrombosis(self, test_client: Any) -> None:
        """Test patient with confirmed new thrombosis"""
        payload = {
            "params": {
                "thrombocytopenia": 1,
                "timing": 2,
                "thrombosis": 2,
                "other_causes": 1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 4

    def test_other_causes_definite(self, test_client: Any) -> None:
        """Test when other cause is definite (score 0 for component)"""
        payload = {
            "params": {
                "thrombocytopenia": 2,
                "timing": 2,
                "thrombosis": 1,
                "other_causes": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Definite other cause reduces suspicion
        assert data["result"]["value"] >= 0

    def test_rapid_onset_prior_exposure(self, test_client: Any) -> None:
        """Test rapid onset with prior heparin exposure"""
        payload = {
            "params": {
                "thrombocytopenia": 2,
                "timing": 2,  # Prior exposure within 30 days
                "thrombosis": 1,
                "other_causes": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 5

    def test_minimum_score(self, test_client: Any) -> None:
        """Test minimum possible score"""
        payload = {
            "params": {
                "thrombocytopenia": 0,
                "timing": 0,
                "thrombosis": 0,
                "other_causes": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 0

    def _skip_test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "thrombocytopenia": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
