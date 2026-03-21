from typing import Any, cast

from mcp.server.fastmcp import FastMCP

from src.domain.registry import ToolRegistry
from src.infrastructure.mcp.config import McpServerConfig
from src.infrastructure.mcp.guidance import get_tool_usage_playbook_markdown
from src.infrastructure.mcp.handlers.prompt_handler import PromptHandler

LEGACY_WORKFLOW_REFS = {
    "calculate_qsofa",
    "calculate_sofa",
    "calculate_apache_ii",
    "calculate_rass",
    "calculate_cam_icu",
    "calculate_gcs",
    "calculate_news2",
    "calculate_asa_physical_status",
    "calculate_rcri",
    "calculate_mallampati",
    "calculate_mabl",
    "calculate_ckd_epi_2021",
    "calculate_pediatric_dosing",
    "calculate_transfusion",
}


class _FakeMCP:
    def __init__(self) -> None:
        self.prompts: dict[str, Any] = {}

    def prompt(self) -> Any:
        def decorator(func: Any) -> Any:
            self.prompts[func.__name__] = func
            return func

        return decorator


def test_server_instructions_enforce_safe_sequence() -> None:
    instructions = McpServerConfig().instructions

    assert "discover(...)" in instructions
    assert "get_tool_schema(tool_id)" in instructions
    assert "calculate(tool_id, params)" in instructions
    assert "Never invent parameter names" in instructions
    assert "tool_usage_playbook" in instructions


def test_tool_usage_playbook_prompt_guides_small_models() -> None:
    fake_mcp = _FakeMCP()
    PromptHandler(cast(FastMCP, fake_mcp), ToolRegistry())

    assert "tool_usage_playbook" in fake_mcp.prompts

    prompt_text = fake_mcp.prompts["tool_usage_playbook"]()

    assert "Mandatory Sequence" in prompt_text
    assert "discover(...)" in prompt_text
    assert "get_tool_schema(tool_id)" in prompt_text
    assert "Never guess parameter names" in prompt_text
    assert "guidance.resolved_tool_id" in prompt_text


def test_shared_playbook_mentions_resource_and_prompt_entrypoints() -> None:
    playbook = get_tool_usage_playbook_markdown()

    assert "tool_usage_playbook()" in playbook
    assert "guide://tool-usage-playbook" in playbook
    assert "calculator://list" in playbook


def test_server_instructions_use_unified_tool_flow_examples() -> None:
    instructions = McpServerConfig().instructions

    for legacy_ref in LEGACY_WORKFLOW_REFS:
        assert legacy_ref not in instructions

    assert "qsofa_score" in instructions
    assert "transfusion_calc" in instructions
    assert "calculate('qsofa_score', params)" in instructions


def test_workflow_prompts_reference_canonical_tool_ids() -> None:
    fake_mcp = _FakeMCP()
    PromptHandler(cast(FastMCP, fake_mcp), ToolRegistry())

    workflow_prompt_names = {
        "sepsis_evaluation",
        "preoperative_risk_assessment",
        "icu_daily_assessment",
        "pediatric_drug_dosing",
        "acute_kidney_injury_assessment",
    }

    for prompt_name in workflow_prompt_names:
        prompt_text = fake_mcp.prompts[prompt_name]()
        assert "canonical tool ids" in prompt_text
        assert "Tool ID:" in prompt_text
        for legacy_ref in LEGACY_WORKFLOW_REFS:
            assert legacy_ref not in prompt_text

    assert "qsofa_score" in fake_mcp.prompts["sepsis_evaluation"]()
    assert "mallampati_score" in fake_mcp.prompts["preoperative_risk_assessment"]()
    assert "transfusion_calc" in fake_mcp.prompts["pediatric_drug_dosing"]()
