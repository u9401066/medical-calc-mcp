# OpenClaw Registry Guide

This document is intended for OpenClaw-style crawlers, MCP registries, and autonomous agent platforms that index GitHub repositories and decide whether to install or connect to an MCP server.

## Recommended GitHub Repository Metadata

These values cannot be changed from inside the repository files alone, but they should be set in the GitHub repository settings.

### Suggested Repository Description

Evidence-based medical calculator MCP server built with FastMCP, featuring smart tool discovery, schema-first calculation, and safe retry guidance for AI agents.

### Suggested GitHub Topics

- mcp
- fastmcp
- medical-calculator
- ai-agent-tools
- openclaw
- model-context-protocol
- mcp-server
- clinical-decision-support
- healthcare-ai

## Repository Signals for OpenClaw

- Python 3.11+
- FastMCP-based MCP server
- Supports stdio, SSE, and HTTP transports
- Schema-first workflow for safer agent execution
- Smart identifier resolution for tool ids and specialties
- Guidance-oriented responses for retries
- Prompt and resource onboarding:
  - `tool_usage_playbook()`
  - `guide://tool-usage-playbook`
  - `calculator://list`

## Recommended Agent Workflow

Use this exact order unless a canonical tool id and all exact parameters are already known.

1. Read `guide://tool-usage-playbook`
2. Read `calculator://list`
3. Call `discover(by="keyword", value="clinical problem")`
4. Call `get_tool_schema("tool_id")`
5. Call `calculate("tool_id", {...})`

## Minimal Installation

```bash
git clone https://github.com/u9401066/medical-calc-mcp.git
cd medical-calc-mcp
uv sync
uv run python -m src.main
```

## MCP Client Configuration

### Local stdio

```json
{
  "mcpServers": {
    "medical-calc": {
      "command": "uv",
      "args": ["run", "python", "-m", "src.main"],
      "cwd": "/path/to/medical-calc-mcp"
    }
  }
}
```

### Remote SSE

```bash
uv run python -m src.main --mode sse
```

### Remote HTTP

```bash
uv run python -m src.main --mode http
```

## Machine-Readable Manifest

The repository root also includes `openclaw.json` with a registry-oriented manifest containing install, transport, discovery, and onboarding details.

## Why This Repo Is Registry-Friendly

- package metadata includes MCP and OpenClaw keywords
- README includes OpenClaw installation and usage guidance
- a dedicated onboarding document exists for crawlers and registries
- a machine-readable manifest exists for automated ingestion
