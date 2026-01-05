from typing import Any
"""
E2E Tests for Bishop Score Calculator

Tests the Bishop Score for Cervical Favorability through the REST API.

Parameters:
    dilation: int (0-3) - Cervical dilation score
        0 = Closed, 1 = 1-2 cm, 2 = 3-4 cm, 3 = ≥5 cm
    effacement: int (0-3) - Cervical effacement score
        0 = 0-30%, 1 = 40-50%, 2 = 60-70%, 3 = ≥80%
    station: int (0-3) - Fetal station score
        0 = -3, 1 = -2, 2 = -1/0, 3 = +1/+2
    consistency: str - Cervical consistency
        "firm", "medium", "soft"
    position: str - Cervical position
        "posterior", "mid", "anterior"
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestBishopScoreE2E:
    """E2E tests for Bishop Score Calculator"""

    ENDPOINT = "/api/v1/calculate/bishop_score"

    def test_unfavorable_cervix_score_0_3(self, test_client: Any) -> None:
        """Test unfavorable cervix (score 0-3)"""
        payload = {
            "params": {
                "dilation": 0,
                "effacement": 0,
                "station": 0,
                "consistency": "firm",
                "position": "posterior"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Unfavorable for induction
        assert data["result"]["value"] <= 3

    def test_intermediate_cervix_score_5_6(self, test_client: Any) -> None:
        """Test intermediate cervix (score 5-6)"""
        payload = {
            "params": {
                "dilation": 1,
                "effacement": 1,
                "station": 1,
                "consistency": "medium",
                "position": "mid"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 5

    def test_favorable_cervix_score_8_plus(self, test_client: Any) -> None:
        """Test favorable cervix (score ≥8)"""
        payload = {
            "params": {
                "dilation": 2,
                "effacement": 2,
                "station": 2,
                "consistency": "soft",
                "position": "anterior"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Favorable for induction
        assert data["result"]["value"] >= 8

    def test_maximum_score_13(self, test_client: Any) -> None:
        """Test maximum possible score (13)"""
        payload = {
            "params": {
                "dilation": 3,
                "effacement": 3,
                "station": 3,
                "consistency": "soft",
                "position": "anterior"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Maximum score
        assert data["result"]["value"] == 13

    def test_nulliparous_unfavorable(self, test_client: Any) -> None:
        """Test nulliparous patient with unfavorable cervix"""
        payload = {
            "params": {
                "dilation": 0,
                "effacement": 1,
                "station": 0,
                "consistency": "firm",
                "position": "posterior"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] <= 3

    def test_multiparous_favorable(self, test_client: Any) -> None:
        """Test multiparous patient with favorable cervix"""
        payload = {
            "params": {
                "dilation": 2,
                "effacement": 3,
                "station": 2,
                "consistency": "soft",
                "position": "anterior"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 9

    def test_partially_dilated_effaced(self, test_client: Any) -> None:
        """Test partially dilated and effaced cervix"""
        payload = {
            "params": {
                "dilation": 2,
                "effacement": 2,
                "station": 1,
                "consistency": "medium",
                "position": "mid"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 5

    def test_term_ripening(self, test_client: Any) -> None:
        """Test cervix ripening at term"""
        payload = {
            "params": {
                "dilation": 1,
                "effacement": 2,
                "station": 1,
                "consistency": "soft",
                "position": "mid"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 5

    def test_need_cervical_ripening(self, test_client: Any) -> None:
        """Test when cervical ripening is needed"""
        payload = {
            "params": {
                "dilation": 0,
                "effacement": 0,
                "station": 0,
                "consistency": "firm",
                "position": "posterior"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Score 0 = needs ripening agent
        assert data["result"]["value"] == 0

    def test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "dilation": 2,
                "effacement": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
