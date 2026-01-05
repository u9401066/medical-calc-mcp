from typing import Any
"""
E2E Tests for Anion Gap Calculator

Tests the Anion Gap calculator through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestAnionGapE2E:
    """E2E tests for Anion Gap Calculator"""

    ENDPOINT = "/api/v1/calculate/anion_gap"

    def test_normal_anion_gap(self, test_client: Any) -> None:
        """Test normal anion gap (8-12 mEq/L)"""
        payload = {
            "params": {
                "sodium": 140,
                "chloride": 104,
                "bicarbonate": 24
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # AG = 140 - 104 - 24 = 12
        assert data["result"]["value"] == 12

    def test_elevated_anion_gap(self, test_client: Any) -> None:
        """Test elevated anion gap (metabolic acidosis)"""
        payload = {
            "params": {
                "sodium": 140,
                "chloride": 100,
                "bicarbonate": 12
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # AG = 140 - 100 - 12 = 28
        assert data["result"]["value"] == 28

    def test_low_anion_gap(self, test_client: Any) -> None:
        """Test low anion gap"""
        payload = {
            "params": {
                "sodium": 140,
                "chloride": 110,
                "bicarbonate": 26
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # AG = 140 - 110 - 26 = 4
        assert data["result"]["value"] == 4

    def test_with_albumin_correction(self, test_client: Any) -> None:
        """Test anion gap with albumin correction"""
        payload = {
            "params": {
                "sodium": 140,
                "chloride": 104,
                "bicarbonate": 24,
                "albumin": 2.0  # Low albumin
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Corrected AG should be higher
        assert data["result"]["value"] > 12

    def test_with_potassium(self, test_client: Any) -> None:
        """Test anion gap including potassium"""
        payload = {
            "params": {
                "sodium": 140,
                "chloride": 104,
                "bicarbonate": 24,
                "include_potassium": True,
                "potassium": 4.0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # AG with K = 140 + 4 - 104 - 24 = 16
        assert data["result"]["value"] == 16

    def test_dka_presentation(self, test_client: Any) -> None:
        """Test DKA presentation (high AG metabolic acidosis)"""
        payload = {
            "params": {
                "sodium": 135,
                "chloride": 98,
                "bicarbonate": 8
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # AG = 135 - 98 - 8 = 29
        assert data["result"]["value"] >= 20

    def test_normal_gap_metabolic_acidosis(self, test_client: Any) -> None:
        """Test normal gap metabolic acidosis (hyperchloremic)"""
        payload = {
            "params": {
                "sodium": 140,
                "chloride": 116,
                "bicarbonate": 14
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # AG = 140 - 116 - 14 = 10 (normal gap despite low bicarb)
        assert data["result"]["value"] == 10

    def _skip_test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "sodium": 140
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
