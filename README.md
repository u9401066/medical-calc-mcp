# Medical Calculator MCP Server 🏥

A DDD-architected medical calculator service providing clinical scoring tools for AI Agent integration via MCP (Model Context Protocol).

[繁體中文版 (Traditional Chinese)](README.zh-TW.md)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP SDK](https://img.shields.io/badge/MCP-FastMCP-green.svg)](https://github.com/modelcontextprotocol/python-sdk)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![CI](https://github.com/u9401066/medical-calc-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/u9401066/medical-calc-mcp/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/tests-1639%20passed-brightgreen.svg)](#-development)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-orange.svg)](https://github.com/astral-sh/ruff)
[![Architecture](https://img.shields.io/badge/architecture-DDD%20Onion-purple.svg)](#-architecture)

---

## 📖 Table of Contents

- [Features](#-features)
- [Why This Project?](#-why-this-project)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Deployment Modes](#-deployment-modes) 🚀 NEW
- [Agent Integration](#-agent-integration) 🤖 NEW
- [Docker Deployment](#-docker-deployment) 🐳
- [HTTPS Deployment](#-https-deployment) 🔒 NEW
- [REST API](#-rest-api) 🌐 NEW
- [Security](#-security) 🔐 NEW
- [Tool Discovery](#-tool-discovery)
- [Available Tools](#-available-tools)
- [Usage Examples](#-usage-examples)
- [References](#-references)
- [Development](#-development)
- [Deployment Guide](docs/DEPLOYMENT.md) 📘
- [Roadmap | 路線圖](ROADMAP.md)

---

## 🎯 Features

- **🔌 MCP Native Integration**: Built with FastMCP SDK for seamless AI agent integration
- **🔍 Intelligent Tool Discovery**: Two-level key system (Low/High Level) for smart tool selection
- **🏗️ Clean DDD Architecture**: Onion architecture with clear separation of concerns
- **📚 Evidence-Based**: All formulas cite original peer-reviewed research papers (Vancouver style)
- **🔒 Type Safe**: Full Python type hints with dataclass entities
- **🌐 Multilingual Support**: Ready for i18n with English and Chinese documentation

---

## 🤔 Why This Project?

### The Problem

When AI agents (like Claude, GPT) need to perform medical calculations, they face challenges:

1. **Hallucination Risk**: LLMs may generate incorrect formulas or values
2. **Version Confusion**: Multiple versions of same calculator (e.g., MELD vs MELD-Na vs MELD 3.0)
3. **No Discovery Mechanism**: How does an agent know which tool to use for "cardiac risk assessment"?

### The Solution

This project provides:

| Feature | Description |
|---------|-------------|
| **Validated Calculators** | Peer-reviewed, tested formulas |
| **Tool Discovery** | AI can search by specialty, condition, or clinical question |
| **MCP Protocol** | Standard protocol for AI-tool communication |
| **Paper References** | Every calculator cites original research |

---

## 🏗️ Architecture

The project follows the **Onion Architecture (DDD)**:

- **Infrastructure Layer**: MCP Server, Handlers (Standardize protocol communication)
- **Application Layer**: Use Cases (Orchestrate domain logic, input validation)
- **Domain Layer**: Core Calculators, Entities (Pure medical logic, zero dependencies)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended)

### Installation

```bash
# Clone repository
git clone https://github.com/u9401066/medical-calc-mcp.git
cd medical-calc-mcp

# Setup environment and install dependencies
uv sync
```

### Run MCP Server

```bash
# Start MCP server (stdio transport)
uv run python -m src.main

# Or with MCP development inspector
uvx mcp dev src/main.py
```

---

## 🚀 Deployment Modes ⭐ NEW

| Mode | Command | Port | Best For |
|------|---------|------|----------|
| **api** | `uv run python -m src.main --mode api` | 8080 | Custom agents, web apps |
| **sse** | `uv run python -m src.main --mode sse` | 8000 | Remote MCP clients, Docker |
| **stdio** | `uv run python -m src.main --mode stdio` | - | Local Claude Desktop, VS Code |

---

## 🤖 Agent Integration ⭐ NEW

### Python Example

```python
import requests

# Example: Calculate SOFA score via REST API
r = requests.post("http://localhost:8080/api/v1/calculate/sofa", json={
    "params": {
        "pao2_fio2_ratio": 200,
        "platelets": 100,
        "bilirubin": 2.0,
        "gcs_score": 13,
        "creatinine": 2.5
    }
})
print(r.json())
```

---

## 👨‍💻 Development

```bash
# Setup environment
uv sync

# Run tests
uv run pytest

# Type check
uv run mypy --strict src
```

---

## 📜 References

All formulas cite peer-reviewed research. See [references/README.md](references/README.md) for full citations.

---

## 📄 License

Apache 2.0 - See [LICENSE](LICENSE)
