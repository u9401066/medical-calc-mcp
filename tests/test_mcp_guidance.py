from typing import Any, cast

from mcp.server.fastmcp import FastMCP

from src.domain.registry import ToolRegistry
from src.infrastructure.mcp.config import McpServerConfig
from src.infrastructure.mcp.guidance import get_tool_usage_playbook_markdown
from src.infrastructure.mcp.handlers.prompt_handler import PromptHandler


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
