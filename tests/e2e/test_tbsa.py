from typing import Any
"""
E2E Tests for TBSA (Total Body Surface Area) Burn Calculator

Tests the TBSA Burn Calculator through the REST API.

Actual parameters:
- head_neck: % of head/neck burned (0-100)
- chest: % of anterior chest burned (0-100)
- abdomen: % of abdomen burned (0-100)
- upper_back: % of upper back burned (0-100)
- lower_back: % of lower back/buttocks burned (0-100)
- right_arm: % of right arm burned (0-100)
- left_arm: % of left arm burned (0-100)
- right_hand: % of right hand burned (0-100)
- left_hand: % of left hand burned (0-100)
- perineum: % of perineum burned (0-100)
- right_thigh: % of right thigh burned (0-100)
- left_thigh: % of left thigh burned (0-100)
- right_leg: % of right lower leg burned (0-100)
- left_leg: % of left lower leg burned (0-100)
- right_foot: % of right foot burned (0-100)
- left_foot: % of left foot burned (0-100)
- patient_type: "adult", "child", or "infant"

Rule of Nines (adult):
- Head/neck: 9%, Chest: 9%, Abdomen: 9%
- Upper back: 9%, Lower back: 9%
- Each arm: 9%, Each hand: 1%
- Perineum: 1%
- Each thigh: 9%, Each lower leg: 9%, Each foot: 1%
"""
from tests.e2e.conftest import assert_successful_calculation


class TestTbsaE2E:
    """E2E tests for TBSA Burn Calculator"""

    ENDPOINT = "/api/v1/calculate/tbsa"

    def test_minor_burn(self, test_client: Any) -> None:
        """Test minor burn (<10% TBSA) - partial head burn"""
        payload = {
            "params": {
                "head_neck": 50,  # 50% of head burned = 4.5% TBSA
                "patient_type": "adult"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Minor burn - 50% of 9% head = 4.5% TBSA
        assert data["result"]["value"] < 10

    def test_moderate_burn(self, test_client: Any) -> None:
        """Test moderate burn (10-20% TBSA)"""
        payload = {
            "params": {
                "head_neck": 100,   # 9%
                "chest": 50,        # 4.5%
                "patient_type": "adult"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # ~13.5% TBSA
        assert 10 <= data["result"]["value"] <= 20

    def test_severe_burn(self, test_client: Any) -> None:
        """Test severe burn (>20% TBSA)"""
        payload = {
            "params": {
                "head_neck": 100,    # 9%
                "chest": 100,        # 9%
                "abdomen": 100,      # 9%
                "right_arm": 100,    # 9%
                "patient_type": "adult"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # ~36% TBSA
        assert data["result"]["value"] >= 30

    def test_massive_burn(self, test_client: Any) -> None:
        """Test massive burn (>50% TBSA)"""
        payload = {
            "params": {
                "head_neck": 100,    # 9%
                "chest": 100,        # 9%
                "abdomen": 100,      # 9%
                "upper_back": 100,   # 9%
                "lower_back": 100,   # 9%
                "right_arm": 100,    # 9%
                "left_arm": 100,     # 9%
                "patient_type": "adult"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # ~63% TBSA
        assert data["result"]["value"] >= 50

    def test_face_and_hands(self, test_client: Any) -> None:
        """Test burn to face and hands (critical areas)"""
        payload = {
            "params": {
                "head_neck": 100,    # 9%
                "right_hand": 100,   # 1%
                "left_hand": 100,    # 1%
                "patient_type": "adult"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # 11% TBSA
        assert data["result"]["value"] == 11

    def test_trunk_only(self, test_client: Any) -> None:
        """Test trunk burns only"""
        payload = {
            "params": {
                "chest": 100,        # 9%
                "abdomen": 100,      # 9%
                "upper_back": 100,   # 9%
                "lower_back": 100,   # 9%
                "patient_type": "adult"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # 36% TBSA
        assert data["result"]["value"] == 36

    def test_lower_extremities(self, test_client: Any) -> None:
        """Test lower extremity burns"""
        payload = {
            "params": {
                "right_thigh": 100,  # 9%
                "left_thigh": 100,   # 9%
                "right_leg": 100,    # 9%
                "left_leg": 100,     # 9%
                "patient_type": "adult"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # 36% TBSA
        assert data["result"]["value"] == 36

    def test_scattered_burns(self, test_client: Any) -> None:
        """Test scattered burns across body"""
        payload = {
            "params": {
                "head_neck": 50,     # 4.5%
                "chest": 50,         # 4.5%
                "right_arm": 50,     # 4.5%
                "patient_type": "adult"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # ~13.5% TBSA
        assert 12 <= data["result"]["value"] <= 15

    def test_child_burn(self, test_client: Any) -> None:
        """Test burn calculation for a child (different percentages)"""
        payload = {
            "params": {
                "head_neck": 100,    # 15% in child (vs 9% in adult)
                "patient_type": "child"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Child head is 15% of BSA
        assert data["result"]["value"] == 15

    def test_infant_burn(self, test_client: Any) -> None:
        """Test burn calculation for an infant (different percentages)"""
        payload = {
            "params": {
                "head_neck": 100,    # 18% in infant
                "patient_type": "infant"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Infant head is 18% of BSA
        assert data["result"]["value"] == 18

    def test_all_default_params(self, test_client: Any) -> None:
        """Test with minimal parameters (all have defaults)"""
        payload = {
            "params": {
                "head_neck": 100
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # 9% TBSA with default adult
        assert data["result"]["value"] == 9
