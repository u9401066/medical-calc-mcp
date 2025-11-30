"""
Tests for Pediatric and Transfusion Calculators

Tests Pediatric Dosing, MABL, and Transfusion calculators.
"""

import pytest


class TestPediatricDosingCalculator:
    """Tests for Pediatric Weight-Based Dosing Calculator."""

    def test_amoxicillin_dosing(self):
        """Test amoxicillin dosing calculation."""
        from src.domain.services.calculators import PediatricDosingCalculator
        
        calc = PediatricDosingCalculator()
        result = calc.calculate(weight_kg=20, drug_name="amoxicillin")
        
        assert result.value is not None
        assert result.interpretation is not None

    def test_acetaminophen_dosing(self):
        """Test acetaminophen dosing calculation."""
        from src.domain.services.calculators import PediatricDosingCalculator
        
        calc = PediatricDosingCalculator()
        result = calc.calculate(weight_kg=15, drug_name="acetaminophen")
        
        assert result.value is not None

    def test_ibuprofen_dosing(self):
        """Test ibuprofen dosing calculation."""
        from src.domain.services.calculators import PediatricDosingCalculator
        
        calc = PediatricDosingCalculator()
        result = calc.calculate(weight_kg=25, drug_name="ibuprofen")
        
        assert result.value is not None

    def test_tool_id(self):
        """Test tool ID is correct."""
        from src.domain.services.calculators import PediatricDosingCalculator
        
        calc = PediatricDosingCalculator()
        assert calc.tool_id == "pediatric_dosing"


class TestMablCalculator:
    """Tests for Maximum Allowable Blood Loss (MABL) Calculator."""

    def test_normal_patient(self):
        """Test MABL for normal patient."""
        from src.domain.services.calculators import MablCalculator
        
        calc = MablCalculator()
        result = calc.calculate(
            weight_kg=70,
            starting_hematocrit=40,
            minimum_hematocrit=25,
        )
        
        assert result.value is not None
        assert result.value > 0
        assert "mL" in str(result.unit).lower()

    def test_anemic_patient(self):
        """Test MABL for anemic patient."""
        from src.domain.services.calculators import MablCalculator
        
        calc = MablCalculator()
        result = calc.calculate(
            weight_kg=70,
            starting_hematocrit=30,
            minimum_hematocrit=25,
        )
        
        # Lower starting Hct = less allowable blood loss
        assert result.value is not None
        assert result.value > 0

    def test_pediatric_patient(self):
        """Test MABL for pediatric patient."""
        from src.domain.services.calculators import MablCalculator
        
        calc = MablCalculator()
        result = calc.calculate(
            weight_kg=20,
            starting_hematocrit=38,
            minimum_hematocrit=25,
        )
        
        assert result.value is not None
        assert result.value > 0

    def test_weight_affects_mabl(self):
        """Test that weight directly affects MABL."""
        from src.domain.services.calculators import MablCalculator
        
        calc = MablCalculator()
        
        result1 = calc.calculate(
            weight_kg=50,
            starting_hematocrit=40,
            minimum_hematocrit=25,
        )
        
        result2 = calc.calculate(
            weight_kg=100,
            starting_hematocrit=40,
            minimum_hematocrit=25,
        )
        
        # Heavier patient = more allowable blood loss
        assert result2.value > result1.value

    def test_tool_id(self):
        """Test tool ID is correct."""
        from src.domain.services.calculators import MablCalculator
        
        calc = MablCalculator()
        assert calc.tool_id == "mabl"


class TestTransfusionCalculator:
    """Tests for Transfusion Volume Calculator."""

    def test_prbc_transfusion(self):
        """Test PRBC transfusion calculation."""
        from src.domain.services.calculators import TransfusionCalculator
        
        calc = TransfusionCalculator()
        result = calc.calculate(
            weight_kg=70,
            current_hematocrit=25,
            target_hematocrit=35,
        )
        
        assert result.value is not None
        assert result.value > 0

    def test_minimal_transfusion_need(self):
        """Test minimal transfusion need."""
        from src.domain.services.calculators import TransfusionCalculator
        
        calc = TransfusionCalculator()
        result = calc.calculate(
            weight_kg=70,
            current_hematocrit=33,
            target_hematocrit=35,
        )
        
        assert result.value is not None

    def test_pediatric_transfusion(self):
        """Test pediatric transfusion calculation."""
        from src.domain.services.calculators import TransfusionCalculator
        
        calc = TransfusionCalculator()
        result = calc.calculate(
            weight_kg=20,
            current_hematocrit=22,
            target_hematocrit=30,
        )
        
        assert result.value is not None
        assert result.value > 0

    def test_larger_deficit_more_blood(self):
        """Test that larger Hct deficit requires more blood."""
        from src.domain.services.calculators import TransfusionCalculator
        
        calc = TransfusionCalculator()
        
        # Small deficit
        result1 = calc.calculate(
            weight_kg=70,
            current_hematocrit=30,
            target_hematocrit=35,
        )
        
        # Large deficit
        result2 = calc.calculate(
            weight_kg=70,
            current_hematocrit=20,
            target_hematocrit=35,
        )
        
        assert result2.value > result1.value

    def test_tool_id(self):
        """Test tool ID is correct."""
        from src.domain.services.calculators import TransfusionCalculator
        
        calc = TransfusionCalculator()
        assert calc.tool_id == "transfusion"
