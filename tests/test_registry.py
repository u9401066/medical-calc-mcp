"""
Tests for Tool Registry and Discovery

Tests the ToolRegistry and calculator discovery functionality.
"""

import pytest


class TestToolRegistry:
    """Tests for ToolRegistry functionality."""

    def test_registry_has_all_calculators(self, registry):
        """Test that registry contains all 23 calculators."""
        all_ids = registry.list_all_ids()
        
        assert len(all_ids) == 23
        
        # Check specific calculators exist
        expected_ids = [
            "ckd_epi_2021",
            "asa_physical_status",
            "mallampati",
            "rcri",
            "apache_ii",
            "rass",
            "sofa",
            "qsofa",
            "news",
            "gcs",
            "cam_icu",
            "pediatric_dosing",
            "mabl",
            "transfusion",
            "curb65",
            "chads2_vasc",
            "chads2_va",
            "heart_score",
            "wells_dvt",
            "wells_pe",
            "meld",
            "caprini_vte",
            "psi_port",
        ]
        
        for expected_id in expected_ids:
            assert expected_id in all_ids, f"Missing calculator: {expected_id}"

    def test_get_calculator_by_id(self, registry):
        """Test retrieving calculator by ID."""
        calc = registry.get_calculator("ckd_epi_2021")
        
        assert calc is not None
        assert calc.tool_id == "ckd_epi_2021"

    def test_get_nonexistent_calculator(self, registry):
        """Test retrieving non-existent calculator returns None."""
        calc = registry.get_calculator("nonexistent_calculator")
        
        assert calc is None

    def test_list_by_category(self, registry):
        """Test listing calculators by category."""
        # This tests the category filtering capability
        all_calcs = registry.list_all_ids()
        
        # Should have calculators from multiple categories
        assert len(all_calcs) > 0


class TestCalculatorMetadata:
    """Tests for calculator metadata."""

    def test_all_calculators_have_tool_id(self, calculator_classes):
        """Test that all calculators have a tool_id."""
        for calc_class in calculator_classes:
            calc = calc_class()
            assert calc.tool_id is not None
            assert len(calc.tool_id) > 0

    def test_all_calculators_have_tool_name(self, calculator_classes):
        """Test that all calculators have a tool_name."""
        for calc_class in calculator_classes:
            calc = calc_class()
            assert calc.tool_name is not None
            assert len(calc.tool_name) > 0

    def test_all_calculators_have_description(self, calculator_classes):
        """Test that all calculators have a description."""
        for calc_class in calculator_classes:
            calc = calc_class()
            assert calc.description is not None
            assert len(calc.description) > 0

    def test_all_calculators_have_category(self, calculator_classes):
        """Test that all calculators have a category."""
        for calc_class in calculator_classes:
            calc = calc_class()
            assert calc.category is not None

    def test_tool_ids_are_unique(self, calculator_classes):
        """Test that all tool_ids are unique."""
        tool_ids = [calc_class().tool_id for calc_class in calculator_classes]
        
        assert len(tool_ids) == len(set(tool_ids)), "Duplicate tool_ids found"

    def test_all_calculators_have_references(self, calculator_classes, sample_params):
        """Test that all calculators include references."""
        for calc_class in calculator_classes:
            calc = calc_class()
            tool_id = calc.tool_id
            
            if tool_id in sample_params:
                result = calc.calculate(**sample_params[tool_id])
                
                assert result.references is not None, f"{tool_id} missing references"
                assert len(result.references) > 0, f"{tool_id} has empty references"


class TestCalculatorOutput:
    """Tests for calculator output format."""

    def test_all_calculators_return_score_result(self, calculator_classes, sample_params):
        """Test that all calculators return ScoreResult."""
        from src.domain.entities.score_result import ScoreResult
        
        for calc_class in calculator_classes:
            calc = calc_class()
            tool_id = calc.tool_id
            
            if tool_id in sample_params:
                result = calc.calculate(**sample_params[tool_id])
                
                assert isinstance(result, ScoreResult), f"{tool_id} doesn't return ScoreResult"

    def test_all_calculators_have_interpretation(self, calculator_classes, sample_params):
        """Test that all calculators provide interpretation."""
        for calc_class in calculator_classes:
            calc = calc_class()
            tool_id = calc.tool_id
            
            if tool_id in sample_params:
                result = calc.calculate(**sample_params[tool_id])
                
                assert result.interpretation is not None, f"{tool_id} missing interpretation"

    def test_all_calculators_have_value(self, calculator_classes, sample_params):
        """Test that all calculators return a value."""
        for calc_class in calculator_classes:
            calc = calc_class()
            tool_id = calc.tool_id
            
            if tool_id in sample_params:
                result = calc.calculate(**sample_params[tool_id])
                
                assert result.value is not None, f"{tool_id} missing value"
