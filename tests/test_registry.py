"""Tests for Tool Registry"""


class TestToolRegistry:
    def test_registry_not_empty(self) -> None:
        from src.infrastructure.mcp.server import MedicalCalculatorServer
        server = MedicalCalculatorServer()
        all_ids = server.registry.list_all_ids()
        assert len(all_ids) >= 20

    def test_registry_has_calculators(self) -> None:
        from src.infrastructure.mcp.server import MedicalCalculatorServer
        server = MedicalCalculatorServer()
        calc = server.registry.get_calculator("ckd_epi_2021")
        assert calc is not None


class TestCalculatorMetadata:
    def test_all_have_tool_id(self) -> None:
        from src.domain.services.calculators import CALCULATORS
        for cls in CALCULATORS:
            calc = cls()
            assert hasattr(calc, "tool_id")
            assert calc.tool_id is not None
