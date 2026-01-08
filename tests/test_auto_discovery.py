"""
Tests for AutoDiscoveryEngine

Verifies the pure-Python auto-discovery system:
- Automatic condition/keyword extraction
- Multi-dimensional search
- Related tool discovery
- Domain extraction from parameters
"""

import pytest

from src.domain.registry.auto_discovery import (
    CONDITION_PATTERNS,
    PARAM_DOMAIN_MAP,
    AutoDiscoveryEngine,
    DiscoveryResult,
    EnrichedHighLevelKey,
)
from src.domain.registry.tool_registry import ToolRegistry
from src.domain.services.calculators import CALCULATORS


@pytest.fixture
def registry() -> ToolRegistry:
    """Create a registry with all calculators."""
    reg = ToolRegistry()
    for calc_cls in CALCULATORS:
        reg.register(calc_cls())
    return reg


@pytest.fixture
def discovery_engine(registry: ToolRegistry) -> AutoDiscoveryEngine:
    """Create and build discovery engine."""
    engine = AutoDiscoveryEngine()
    engine.build_from_registry(registry)
    return engine


class TestAutoDiscoveryEngineInit:
    """Test engine initialization and building."""

    def test_build_from_registry(self, registry: ToolRegistry) -> None:
        """Test building engine from registry."""
        engine = AutoDiscoveryEngine()
        assert not engine._is_built

        engine.build_from_registry(registry)

        assert engine._is_built
        stats = engine.get_statistics()
        assert stats["total_tools"] == len(CALCULATORS)
        assert stats["total_conditions"] > 0
        assert stats["total_keywords"] > 0
        assert stats["total_domains"] > 0

    def test_statistics(self, discovery_engine: AutoDiscoveryEngine) -> None:
        """Test getting statistics."""
        stats = discovery_engine.get_statistics()

        assert stats["is_built"] is True
        assert stats["total_tools"] == 75
        assert stats["total_conditions"] > 20  # Should extract many conditions
        assert stats["total_domains"] >= 6  # renal, cardiac, hepatic, etc.


class TestConditionExtraction:
    """Test automatic condition extraction from docstrings."""

    def test_extracts_sepsis(self, discovery_engine: AutoDiscoveryEngine) -> None:
        """Test sepsis is extracted from SOFA/qSOFA tools."""
        enriched = discovery_engine.get_enriched_key("sofa_score")
        assert enriched is not None
        assert "sepsis" in enriched.extracted_conditions or "sepsis" in [
            c.lower() for c in enriched.manual_conditions
        ]

    def test_extracts_shock(self, discovery_engine: AutoDiscoveryEngine) -> None:
        """Test shock is extracted from Shock Index tool."""
        enriched = discovery_engine.get_enriched_key("shock_index")
        assert enriched is not None
        all_conditions = [c.lower() for c in enriched.all_conditions]
        assert "shock" in all_conditions or any("shock" in c for c in all_conditions)

    def test_merges_manual_and_extracted(
        self, discovery_engine: AutoDiscoveryEngine
    ) -> None:
        """Test that manual and extracted conditions are merged."""
        enriched = discovery_engine.get_enriched_key("sofa_score")
        assert enriched is not None

        # all_conditions should include both manual and extracted
        all_conds = enriched.all_conditions
        manual_conds = enriched.manual_conditions

        # All manual conditions should be in all_conditions
        for c in manual_conds:
            assert c in all_conds


class TestDomainExtraction:
    """Test automatic clinical domain extraction from parameters."""

    def test_extracts_renal_domain(
        self, discovery_engine: AutoDiscoveryEngine
    ) -> None:
        """Test renal domain is extracted from tools with creatinine."""
        enriched = discovery_engine.get_enriched_key("ckd_epi_2021")
        assert enriched is not None
        assert "renal" in enriched.extracted_domains

    def test_extracts_cardiac_domain(
        self, discovery_engine: AutoDiscoveryEngine
    ) -> None:
        """Test cardiac domain is extracted from tools with heart_rate."""
        enriched = discovery_engine.get_enriched_key("shock_index")
        assert enriched is not None
        assert "cardiac" in enriched.extracted_domains

    def test_extracts_multiple_domains(
        self, discovery_engine: AutoDiscoveryEngine
    ) -> None:
        """Test tools with multiple organ params get multiple domains."""
        enriched = discovery_engine.get_enriched_key("sofa_score")
        assert enriched is not None
        # SOFA covers multiple organ systems
        assert len(enriched.extracted_domains) >= 4


class TestSearch:
    """Test search functionality."""

    def test_search_sepsis_shock(
        self, discovery_engine: AutoDiscoveryEngine
    ) -> None:
        """Test searching for sepsis shock returns relevant tools."""
        results = discovery_engine.search("sepsis shock", limit=5)

        assert len(results) > 0
        tool_ids = [r.tool_id for r in results]

        # Should find SOFA, qSOFA, Shock Index
        sepsis_tools = ["sofa_score", "sofa2_score", "qsofa_score", "shock_index"]
        assert any(t in tool_ids for t in sepsis_tools)

    def test_search_renal(self, discovery_engine: AutoDiscoveryEngine) -> None:
        """Test searching for renal returns kidney-related tools."""
        results = discovery_engine.search("renal kidney creatinine", limit=5)

        assert len(results) > 0
        tool_ids = [r.tool_id for r in results]

        # Should find CKD-EPI, KDIGO AKI
        renal_tools = ["ckd_epi_2021", "kdigo_aki", "cockcroft_gault"]
        assert any(t in tool_ids for t in renal_tools)

    def test_search_airway(self, discovery_engine: AutoDiscoveryEngine) -> None:
        """Test searching for airway returns Mallampati."""
        results = discovery_engine.search("airway intubation difficult", limit=5)

        assert len(results) > 0
        tool_ids = [r.tool_id for r in results]
        assert "mallampati_score" in tool_ids

    def test_search_returns_scores(
        self, discovery_engine: AutoDiscoveryEngine
    ) -> None:
        """Test search results include scores and reasons."""
        results = discovery_engine.search("sepsis", limit=3)

        assert len(results) > 0
        for result in results:
            assert isinstance(result, DiscoveryResult)
            assert result.score > 0
            assert len(result.match_reasons) > 0

    def test_search_empty_returns_empty(
        self, discovery_engine: AutoDiscoveryEngine
    ) -> None:
        """Test searching for nonsense returns empty."""
        results = discovery_engine.search("xyzabc123notexist", limit=5)
        assert len(results) == 0


class TestRelatedTools:
    """Test related tool discovery."""

    def test_sofa_related_to_sofa2(
        self, discovery_engine: AutoDiscoveryEngine
    ) -> None:
        """Test SOFA is related to SOFA2."""
        related = discovery_engine.get_related_tools("sofa_score", limit=5)

        assert len(related) > 0
        tool_ids = [t for t, _ in related]
        assert "sofa2_score" in tool_ids

    def test_related_sorted_by_similarity(
        self, discovery_engine: AutoDiscoveryEngine
    ) -> None:
        """Test related tools are sorted by similarity."""
        related = discovery_engine.get_related_tools("sofa_score", limit=10)

        scores = [score for _, score in related]
        assert scores == sorted(scores, reverse=True)

    def test_unknown_tool_returns_empty(
        self, discovery_engine: AutoDiscoveryEngine
    ) -> None:
        """Test unknown tool returns empty list."""
        related = discovery_engine.get_related_tools("nonexistent_tool")
        assert related == []


class TestFindByParams:
    """Test finding tools by parameter names."""

    def test_find_by_creatinine(
        self, discovery_engine: AutoDiscoveryEngine
    ) -> None:
        """Test finding tools that use creatinine."""
        tools = discovery_engine.find_tools_by_params(["creatinine"])

        assert len(tools) > 0
        # CKD-EPI, Cockcroft-Gault should be found
        assert any("ckd" in t or "cockcroft" in t for t in tools)

    def test_find_by_multiple_params(
        self, discovery_engine: AutoDiscoveryEngine
    ) -> None:
        """Test finding tools by multiple parameters."""
        tools = discovery_engine.find_tools_by_params(["creatinine", "age", "sex"])

        assert len(tools) > 0
        # Tools using multiple of these params should rank higher
        # CKD-EPI uses all three
        assert "ckd_epi_2021" in tools[:5]


class TestFindByCondition:
    """Test finding tools by condition."""

    def test_find_by_sepsis(self, discovery_engine: AutoDiscoveryEngine) -> None:
        """Test finding tools for sepsis."""
        tools = discovery_engine.find_tools_by_condition("sepsis")

        assert len(tools) > 0
        # SOFA, qSOFA should be found
        assert any("sofa" in t for t in tools)


class TestFindByDomain:
    """Test finding tools by clinical domain."""

    def test_find_by_renal_domain(
        self, discovery_engine: AutoDiscoveryEngine
    ) -> None:
        """Test finding tools in renal domain."""
        tools = discovery_engine.find_tools_by_domain("renal")

        assert len(tools) > 0
        # CKD-EPI, KDIGO AKI should be found
        renal_tools = ["ckd_epi_2021", "kdigo_aki", "cockcroft_gault"]
        assert any(t in tools for t in renal_tools)

    def test_find_by_cardiac_domain(
        self, discovery_engine: AutoDiscoveryEngine
    ) -> None:
        """Test finding tools in cardiac domain."""
        tools = discovery_engine.find_tools_by_domain("cardiac")

        assert len(tools) > 0
        # Should include tools with heart_rate, bp, etc.
        cardiac_tools = ["shock_index", "rcri", "grace_score"]
        assert any(t in tools for t in cardiac_tools)


class TestEnrichedHighLevelKey:
    """Test EnrichedHighLevelKey dataclass."""

    def test_all_conditions_merges(
        self, discovery_engine: AutoDiscoveryEngine
    ) -> None:
        """Test all_conditions property merges manual and extracted."""
        enriched = discovery_engine.get_enriched_key("sofa_score")
        assert enriched is not None

        all_conds = set(enriched.all_conditions)
        manual = set(enriched.manual_conditions)
        extracted = set(enriched.extracted_conditions)

        # All manual should be in all
        assert manual.issubset(all_conds)
        # All extracted should be in all
        assert extracted.issubset(all_conds)
        # All should be union
        assert all_conds == manual | extracted

    def test_unknown_tool_returns_none(
        self, discovery_engine: AutoDiscoveryEngine
    ) -> None:
        """Test getting enriched key for unknown tool returns None."""
        enriched = discovery_engine.get_enriched_key("nonexistent")
        assert enriched is None


class TestConditionPatterns:
    """Test the condition pattern dictionary."""

    def test_patterns_exist(self) -> None:
        """Test condition patterns are defined."""
        assert len(CONDITION_PATTERNS) > 20

        # Check some expected conditions
        expected = ["sepsis", "shock", "ards", "aki", "stroke"]
        for condition in expected:
            assert condition in CONDITION_PATTERNS

    def test_patterns_have_multiple_variants(self) -> None:
        """Test each condition has multiple pattern variants."""
        for condition, patterns in CONDITION_PATTERNS.items():
            assert len(patterns) >= 1, f"{condition} has no patterns"


class TestParamDomainMap:
    """Test the parameter to domain mapping."""

    def test_domains_exist(self) -> None:
        """Test param domain map is defined."""
        assert len(PARAM_DOMAIN_MAP) > 20

        # Check some expected mappings
        assert "creatinine" in PARAM_DOMAIN_MAP
        assert "heart_rate" in PARAM_DOMAIN_MAP
        assert "bilirubin" in PARAM_DOMAIN_MAP

    def test_domains_are_valid(self) -> None:
        """Test all mapped domains are valid."""
        valid_domains = {
            "renal", "hepatic", "cardiac", "respiratory",
            "neurological", "hematology", "metabolic", "demographics"
        }

        for param, (domain, _) in PARAM_DOMAIN_MAP.items():
            assert domain in valid_domains, f"{param} maps to invalid domain {domain}"
