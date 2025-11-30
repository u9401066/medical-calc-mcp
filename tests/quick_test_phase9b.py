"""Quick test for Phase 9b calculators"""
import pytest
from src.domain.services.calculators import (
    WintersFormulaCalculator, 
    OsmolarGapCalculator, 
    FreeWaterDeficitCalculator
)


def test_winters_formula():
    """Test Winter's Formula calculation"""
    winters = WintersFormulaCalculator()
    result = winters.calculate(hco3=10, actual_paco2=25)
    # Expected = 1.5 * 10 + 8 = 23 mmHg
    assert result.value == 23.0
    assert "Expected_PaCO₂" in result.calculation_details


def test_osmolar_gap():
    """Test Osmolar Gap calculation"""
    osmolar = OsmolarGapCalculator()
    result = osmolar.calculate(measured_osm=320, sodium=140, glucose=180, bun=28)
    # Calculated = 2*140 + 180/18 + 28/2.8 = 280 + 10 + 10 = 300
    # Gap = 320 - 300 = 20
    assert abs(result.value - 20.0) < 0.5


def test_free_water_deficit():
    """Test Free Water Deficit calculation"""
    fwd = FreeWaterDeficitCalculator()
    result = fwd.calculate(current_sodium=160, weight_kg=70, target_sodium=140)
    # TBW = 70 * 0.6 = 42 L
    # FWD = 42 * ((160/140) - 1) = 42 * 0.143 = 6.0 L
    assert abs(result.value - 6.0) < 0.5


if __name__ == "__main__":
    test_winters_formula()
    test_osmolar_gap()
    test_free_water_deficit()
    print("All Phase 9b calculators working!")
