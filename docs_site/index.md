# Medical Calculator MCP Server

<div align="center">

🏥 **152 Validated Medical Calculators for AI Agents**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP SDK](https://img.shields.io/badge/MCP-FastMCP-green.svg)](https://github.com/modelcontextprotocol/python-sdk)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/u9401066/medical-calc-mcp/blob/main/LICENSE)
[![Tests](https://img.shields.io/badge/tests-2095%20collected-brightgreen.svg)](https://github.com/u9401066/medical-calc-mcp)

</div>

---

## 🎯 What is this?

**Medical-Calc-MCP** is a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that provides **152 validated medical calculators** for AI agents like Claude, GPT, and other LLMs.

!!! warning "Clinical Disclaimer"
    This tool is for educational and research purposes. Always verify calculations with clinical judgment and institutional protocols.

## ✨ Key Features

<div class="grid cards" markdown>

- :material-calculator:{ .lg .middle } **152 Clinical Calculators**

    ---

    Evidence-based formulas across 31 medical specialties with peer-reviewed citations

- :material-robot:{ .lg .middle } **MCP Native**

    ---

    Built with FastMCP SDK for seamless AI agent integration

- :material-magnify:{ .lg .middle } **Intelligent Discovery**

    ---

    Two-level key system for smart tool selection by context

- :material-shield-check:{ .lg .middle } **Validated & Safe**

    ---

    Boundary validation with literature-backed clinical ranges

</div>

## 🚀 Quick Start

=== "Claude Desktop"

    Add to your `claude_desktop_config.json`:

    ```json
    {
      "mcpServers": {
        "medical-calc": {
          "command": "uv",
          "args": ["run", "--directory", "/path/to/medical-calc-mcp", "python", "-m", "src.main"]
        }
      }
    }
    ```

=== "VS Code Copilot"

    Add to `.vscode/mcp.json`:

    ```json
    {
      "servers": {
        "medical-calc": {
          "type": "stdio",
          "command": "uv",
          "args": ["run", "--directory", "${workspaceFolder}", "python", "-m", "src.main"]
        }
      }
    }
    ```

=== "Docker"

    ```bash
    docker run -p 8000:8000 ghcr.io/u9401066/medical-calc-mcp:latest
    ```

## 📊 Specialty Coverage

| Specialty | Calculators | Examples |
|-----------|-------------|----------|
| Critical Care | 15+ | SOFA, APACHE II, qSOFA, NEWS2 |
| Cardiology | 12+ | CHA₂DS₂-VASc, HEART, TIMI |
| Nephrology | 8+ | CKD-EPI, KDIGO AKI |
| Anesthesiology | 10+ | ASA-PS, Mallampati, STOP-BANG |
| Psychiatry | 7 | PHQ-9, GAD-7, HAM-D |
| Geriatrics | 6 | MMSE, MoCA, Barthel Index |
| ... | ... | [See all →](calculators/index.md) |

## 📖 Documentation

- [Getting Started](getting-started/quickstart.md) - Installation and setup
- [Calculator Reference](calculators/index.md) - Generated registry-backed calculator catalog
- [Guideline Coverage](development/guideline-coverage.md) - Generated implementation-to-guideline overview
- [API Reference](api/mcp-tools.md) - MCP tools and REST API
- [Architecture](development/architecture.md) - DDD design principles
- [Agent CDS Gap Plan](https://github.com/u9401066/medical-calc-mcp/blob/main/docs/AGENT_CLINICAL_DECISION_SUPPORT_GAP_AND_BREAKTHROUGH_PLAN.md) - Strategic roadmap beyond calculator count
- [Agent E2E Benchmark](https://github.com/u9401066/medical-calc-mcp/blob/main/docs/AGENT_DECISION_SUPPORT_E2E_BENCHMARK.md) - Task-level benchmark for agent clinical support

## 🤝 Contributing

Contributions are welcome! See our [Contributing Guide](development/contributing.md).

## 📜 License

Apache 2.0 - See [LICENSE](https://github.com/u9401066/medical-calc-mcp/blob/main/LICENSE)
