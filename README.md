# Medical Calculator MCP Server 🏥

A DDD-architected medical calculator service providing clinical scoring tools for AI Agent integration via MCP (Model Context Protocol).

[繁體中文版 (Traditional Chinese)](README.zh-TW.md)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP SDK](https://img.shields.io/badge/MCP-FastMCP-green.svg)](https://github.com/modelcontextprotocol/python-sdk)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![CI](https://github.com/u9401066/medical-calc-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/u9401066/medical-calc-mcp/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/tests-1752%20passed-brightgreen.svg)](#-development)
[![References](https://img.shields.io/badge/references-229%20PMIDs%20|%20190%20DOIs-blue.svg)](#references)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-orange.svg)](https://github.com/astral-sh/ruff)
[![Architecture](https://img.shields.io/badge/architecture-DDD%20Onion-purple.svg)](#architecture)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

---

## 📖 Table of Contents

- [Features](#features)
- [Why This Project?](#why-this-project)
- [Research Framework](#research-framework)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [OpenClaw Compatibility](#openclaw-compatibility)
- [OpenClaw Registry Guide](docs/OPENCLAW.md)
- [Deployment Modes](#deployment-modes)
- [Agent Integration](#agent-integration)
- [Docker Deployment](#docker-deployment)
- [HTTPS Deployment](#https-deployment)
- [REST API](#rest-api)
- [Security](#security)
- [Tool Discovery](#tool-discovery)
- [Available Tools](#available-tools)
  - [Quick Navigation](#quick-navigation)
  - [Anesthesiology](#anesthesiology--preoperative)
  - [Critical Care](#critical-care--icu)
  - [Pediatrics](#pediatrics)
  - [Nephrology](#nephrology)
  - [Pulmonology](#pulmonology)
  - [Cardiology](#cardiology)
  - [Hematology](#hematology)
  - [Emergency Medicine](#emergency-medicine)
  - [Hepatology](#hepatology)
  - [Acid-Base / Metabolic](#acid-base--metabolic)
  - [Discovery Tools](#discovery-tools)
  - [Prompts](#prompts)
- [Usage Examples](#usage-examples)
- [References](#references)
- [Development](#development)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Clinical Guidelines Review](docs/GUIDELINE_RECOMMENDED_TOOLS_2023_2025.md)
- [Roadmap](ROADMAP.md)

---

## 🎯 Features

- **🔌 MCP Native Integration**: Built with FastMCP SDK for seamless AI agent integration
- **🔍 Intelligent Tool Discovery**: Two-level key system + Tool Relation Graph (Hypergraph) for smart tool selection
- **🛡️ Smart Parameter Matching**: Alias support, fuzzy matching, and typo tolerance
- **⚠️ Boundary Validation**: Literature-backed clinical range checking with automatic warnings
- **🏗️ Clean DDD Architecture**: Onion architecture with clear separation of concerns
- **📚 Evidence-Based**: All 121 calculators cite peer-reviewed research (100% coverage, Vancouver style)
- **🔒 Type Safe**: Full Python type hints with dataclass entities
- **🌐 Bilingual**: Chinese/English documentation and tool descriptions

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

### 🧪 Development Methodology

We employ a human-in-the-loop, AI-augmented workflow to ensure clinical accuracy:

1. **Domain Specification**: Human experts define the target medical specialty or clinical domain.
2. **AI-Driven Search**: AI agents perform comprehensive searches for the latest clinical guidelines and consensus.
3. **Guideline Extraction**: Systematically identify recommended scoring systems and calculations mentioned in those guidelines.
4. **Source Validation**: Trace back to original peer-reviewed primary papers to verify exact formulas and coefficients.
5. **Implementation**: Develop validated calculation tools with precise parameters and evidence-based interpretations.

---

## 🔬 Research Framework

> This project implements a **Neuro-Symbolic Framework** for reliable medical calculation, combining LLM understanding with validated symbolic computation.

### Academic Positioning

| Challenge | Traditional LLM | Our Solution |
| --------- | --------------- | ------------ |
| **Calculation Accuracy** | ~50% (MedCalc-Bench) | >95% via validated formulas |
| **Parameter Extraction** | Vocabulary mismatch | ParamMatcher (60+ aliases) |
| **Safety Guardrails** | No clinical constraints | BoundaryValidator (PMID-backed) |
| **Tool Discovery** | Keyword/RAG only | Two-Level Key + Hypergraph |

### Three-Module Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     NEURO-SYMBOLIC MEDICAL REASONING                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐     │
│  │  Discovery Engine │ → │ Reasoning Interface│ → │    Safety Layer   │     │
│  │  (Tool Selection) │   │  (Param Matching)  │   │  (Validation)     │     │
│  │                   │   │                    │   │                   │     │
│  │  • High/Low Keys  │   │  • Alias Matching  │   │  • Range Check    │     │
│  │  • Hypergraph     │   │  • Fuzzy Match     │   │  • PMID Citation  │     │
│  │  • Context-Aware  │   │  • Multi-lingual   │   │  • Error Messages │     │
│  └───────────────────┘   └───────────────────┘   └───────────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Core Contributions

1. **Semantic Parameter Mapping** (ParamMatcher): Resolves vocabulary mismatch between clinical text and calculator parameters through alias tables, fuzzy matching, and suffix normalization.

2. **Literature-Based Guardrails** (BoundaryValidator): Validates input values against clinically impossible ranges derived from peer-reviewed literature (17+ parameters with PMID citations).

3. **Context-Aware Tool Discovery**: Two-level key system + Clinical Knowledge Graph for intelligent tool recommendation based on clinical context.

### 🏆 Levels of Academic Value

| Level | Contribution | Scholarly Focus |
| ----- | ------------ | --------------- |
| **L1** | **Validated Symbolic Engine** | Extends LLM with deterministic precision |
| **L2** | **Hierarchical Tool Discovery** | Solves RAG precision in high-stakes domains |
| **L3** | **Robust Semantic Extraction** | Resolves the "Vocabulary Mismatch" problem |
| **L4** | **Knowledge-Gated Safety Layer** | **Unique**: Literature-derived constraint verification |
| **L5** | **Clinical Hypergraph Agent** | Cross-specialty workflow reasoning |

> 📄 For detailed research roadmap and benchmark strategy, see [ROADMAP.md](ROADMAP.md)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    infrastructure/mcp/                       │
│                (MCP Server, Handlers, Resources)             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  MedicalCalculatorServer                             │    │
│  │  ├── handlers/DiscoveryHandler (discover, list...)   │    │
│  │  ├── handlers/CalculatorHandler (calculate_*)        │    │
│  │  └── resources/CalculatorResourceHandler             │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────────┘
                           │ uses
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     application/                             │
│               (Use Cases, DTOs, Validation)                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  DiscoveryUseCase, CalculateUseCase                  │    │
│  │  DiscoveryRequest/Response, CalculateRequest/Response│    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────────┘
                           │ depends on
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                       domain/                                │
│            (Entities, Services, Value Objects)               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  BaseCalculator, ToolMetadata, ScoreResult          │    │
│  │  LowLevelKey, HighLevelKey, ToolRegistry            │    │
│  └─────────────────────────────────────────────────────┘    │
│                    【Core, Zero Dependencies】                │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **DDD Onion** | Domain logic isolated from infrastructure |
| **FastMCP** | Native Python MCP SDK, simple decorator-based API |
| **Dataclasses** | Immutable, type-safe entities |
| **Two-Level Keys** | Enable both precise lookup and exploratory discovery |
| **Layered Validation** | 3-layer validation (MCP/Application/Domain) |

### Validation Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: MCP (Infrastructure)                               │
│  └── Pydantic + JSON Schema: Type validation                │
│      (Automatic from Annotated[type, Field(description)])   │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: Application (Use Case)                             │
│  ├── ParamMatcher: Intelligent parameter matching           │
│  │   (Alias, fuzzy, suffix matching with typo tolerance)    │
│  └── BoundaryValidator: Clinical range validation           │
│      (Literature-backed warnings for extreme values)        │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: Domain (Calculator)                                │
│  └── ParameterValidator: Medical logic validation           │
│      (22 parameter specs with valid ranges)                 │
└─────────────────────────────────────────────────────────────┘
```

**Domain validation module** (`src/domain/validation/`):
- `rules.py`: Base classes (RangeRule, EnumRule, TypeRule, CustomRule)
- `parameter_specs.py`: 22 medical parameter specifications
- `validators.py`: ParameterValidator with `validate_params()` function
- `boundaries.py`: BoundarySpec with literature-backed clinical ranges

**Parameter Matching** (`src/domain/services/param_matcher.py`):
- Alias matching: `cr` → `serum_creatinine`, `hr` → `heart_rate`
- Fuzzy matching: `creatnine` → `creatinine` (typo tolerance)
- Suffix stripping: `creatinine_mg_dl` → `creatinine`

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+ (required by MCP SDK)
- **uv** package manager (recommended) - [Install uv](https://docs.astral.sh/uv/getting-started/installation/)

### Installation

```bash
# Clone repository
git clone https://github.com/u9401066/medical-calc-mcp.git
cd medical-calc-mcp

# Install uv (if not already installed)
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows:
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Sync dependencies (creates .venv automatically)
uv sync
```

### Run MCP Server

```bash
# Start MCP server (stdio transport)
uv run python -m src.main

# Or with MCP development inspector
uv run mcp dev src/main.py
```

## OpenClaw Compatibility

This repository is intentionally structured so OpenClaw-style crawlers, MCP registries, and autonomous coding agents can discover it, install it, and operate it safely with minimal guessing.

### Discovery Keywords

- MCP server
- medical calculator MCP
- FastMCP
- stdio MCP server
- SSE MCP server
- evidence-based medical scoring
- AI agent clinical tools
- schema-first calculation
- safe retry guidance

### Why This Repo Is OpenClaw-Friendly

- Clear canonical workflow: `discover(...) -> get_tool_schema(tool_id) -> calculate(tool_id, params)`
- Start-here guidance is exposed in multiple MCP surfaces:
  - Prompt: `tool_usage_playbook()`
  - Resource: `guide://tool-usage-playbook`
  - Index: `calculator://list`
- Smart resolver handles fuzzy tool ids and specialty names across tools and resources
- Failed calls return retry-friendly fields such as `guidance`, `suggestions`, `resolved_value`, and `param_template`
- Supports local `stdio` and hosted `sse` / `http` transports

### Minimal Install

```bash
git clone https://github.com/u9401066/medical-calc-mcp.git
cd medical-calc-mcp
uv sync
uv run python -m src.main
```

### Recommended First Actions for OpenClaw

```text
1. Read resource: guide://tool-usage-playbook
2. Read resource: calculator://list
3. Call tool: discover(by="keyword", value="clinical problem")
4. Call tool: get_tool_schema("tool_id")
5. Call tool: calculate("tool_id", {...})
```

### Example MCP Client Config

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

### Hosted Mode for Remote Crawlers / Agents

```bash
uv run python -m src.main --mode sse
# or
uv run python -m src.main --mode http
```

If your OpenClaw deployment ranks repositories by install clarity and MCP readiness, this repo now exposes a direct install path, explicit transport modes, and a schema-first SOP designed to reduce agent misuse.

### Configure with VS Code Copilot ⭐ NEW

The project includes a `.vscode/mcp.json` configuration file for seamless VS Code Copilot integration.

**Automatic Setup:**

Simply open this project in VS Code - the MCP server will be auto-discovered!

```json
// .vscode/mcp.json (included in repo)
{
  "servers": {
    "medical-calc-mcp": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "python", "-m", "src.main"]
    }
  }
}
```

**Enable MCP in VS Code:**

1. Open VS Code Settings (Ctrl+,)
2. Search for `chat.mcp`
3. Enable `Chat: Mcp Discovery Enabled`
4. Restart VS Code

**Usage:**

In GitHub Copilot Chat, use `@medical-calc-mcp` to access calculators:

```
@medical-calc-mcp Calculate SOFA score with PaO2/FiO2=200, platelets=80...
```

### Configure with Claude Desktop

Add to your `claude_desktop_config.json`:

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

---

## 🚀 Deployment Modes ⭐ NEW

This project supports multiple deployment modes for different use cases:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Deployment Options                            │
├─────────────────┬─────────────────┬─────────────────────────────────┤
│   REST API      │   MCP SSE       │   MCP stdio                     │
│   (Port 8080)   │   (Port 8000)   │   (Local)                       │
├─────────────────┼─────────────────┼─────────────────────────────────┤
│ ✅ Any HTTP     │ ✅ MCP Clients  │ ✅ Claude Desktop               │
│    client       │    (remote)     │ ✅ VS Code Copilot              │
│ ✅ Custom Agent │ ✅ Docker/Cloud │ ✅ MCP Inspector                │
│ ✅ Web Apps     │                 │                                 │
│ ✅ Python/JS    │                 │                                 │
└─────────────────┴─────────────────┴─────────────────────────────────┘
```

| Mode | Command | Port | Best For |
|------|---------|------|----------|
| **api** | `uv run python src/main.py --mode api` | 8080 | Custom agents, web apps, scripts |
| **sse** | `uv run python src/main.py --mode sse` | 8000 | Remote MCP clients, Docker |
| **stdio** | `uv run python src/main.py --mode stdio` | - | Local Claude Desktop, VS Code |

> 📘 For detailed deployment instructions, see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

## 🤖 Agent Integration ⭐ NEW

### Python Agent Example

```python
import requests

class MedicalCalculatorClient:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.api_url = f"{base_url}/api/v1"
    
    def search(self, query: str) -> list:
        r = requests.get(f"{self.api_url}/search", params={"q": query})
        return r.json()
    
    def calculate(self, tool_id: str, params: dict) -> dict:
        r = requests.post(f"{self.api_url}/calculate/{tool_id}", json={"params": params})
        return r.json()

# Usage
client = MedicalCalculatorClient()

# Search for sepsis calculators
results = client.search("sepsis")

# Calculate SOFA score
result = client.calculate("sofa", {
    "pao2_fio2_ratio": 200,
    "platelets": 100,
    "bilirubin": 2.0,
    "gcs_score": 13,
    "creatinine": 2.5
})
print(f"SOFA Score: {result['result']['value']}")
```

### LangChain / OpenAI Function Calling

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md#-agent-integration-examples) for LangChain and OpenAI integration examples.

### Quick API Test

```bash
# Start API server
uv run python src/main.py --mode api --port 8080

# Test endpoints
curl http://localhost:8080/health
curl "http://localhost:8080/api/v1/search?q=sepsis"
curl -X POST "http://localhost:8080/api/v1/calculate/gcs" \
  -H "Content-Type: application/json" \
  -d '{"params": {"eye_response": 4, "verbal_response": 5, "motor_response": 6}}'
```

---

## 🐳 Docker Deployment ⭐ NEW

The MCP server can run as a **remote SSE (Server-Sent Events) server** via Docker, enabling:
- 🌐 Remote access from any MCP-compatible client
- ☁️ Cloud deployment (AWS, GCP, Azure, etc.)
- 🔄 Easy scaling with Docker Compose or Kubernetes

### Quick Start with Docker

```bash
# Build and run
docker-compose up -d

# Or build manually
docker build -t medical-calc-mcp .
docker run -p 8000:8000 medical-calc-mcp

# Check service is running
curl -sf http://localhost:8000/sse -o /dev/null && echo "OK"
```

### Transport Modes

| Mode | Use Case | Port | Command |
|------|----------|------|---------|
| `stdio` | Local Claude Desktop | - | `uv run python -m src.main` |
| `sse` | Remote MCP (Docker/Cloud) | 8000 | `uv run python -m src.main --mode sse` |
| `http` | Streamable HTTP transport | 8000 | `uv run python -m src.main --mode http` |

> ⚠️ **Important**: SSE/HTTP modes bind to `0.0.0.0` by default for remote access.

### Quick Start Commands

```bash
# 1. STDIO Mode - For Claude Desktop (local)
uv run python -m src.main

# 2. SSE Mode - For remote agents (Docker/Cloud)
uv run python -m src.main --mode sse
uv run python -m src.main --mode sse --host 0.0.0.0 --port 9000  # Custom port

# 3. HTTP Mode - Streamable HTTP transport
uv run python -m src.main --mode http
```

### Remote MCP Client Configuration

**Claude Desktop (Remote SSE):**

```json
{
  "mcpServers": {
    "medical-calc": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

**For cloud deployment, replace `localhost` with your server address:**

```json
{
  "mcpServers": {
    "medical-calc": {
      "url": "https://your-server.example.com/sse"
    }
  }
}
```

### API Endpoints

> ⚠️ FastMCP SSE mode only provides these endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/sse` | GET | SSE connection endpoint |
| `/messages/` | POST | MCP message endpoint |

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_MODE` | `stdio` | Transport mode (stdio, sse, http) |
| `MCP_HOST` | `0.0.0.0` | Host to bind |
| `MCP_PORT` | `8000` | Port to bind |
| `LOG_LEVEL` | `INFO` | Logging level |
| `DEBUG` | `false` | Enable debug mode |

### Docker Compose Example

```yaml
version: '3.8'
services:
  # MCP Server (SSE mode)
  medical-calc-mcp:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MCP_MODE=sse
    
  # REST API Server (FastAPI)
  medical-calc-api:
    build: .
    ports:
      - "8080:8080"
    command: ["python", "src/main.py", "--mode", "api", "--port", "8080"]
```

---

## 🔒 HTTPS Deployment ⭐ NEW

Enable HTTPS for secure communication in production environments with flexible certificate configuration.

### Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        HTTPS Deployment                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌─────────────┐                                                   │
│   │   Client    │                                                   │
│   │ (Browser/   │                                                   │
│   │  AI Agent)  │                                                   │
│   └──────┬──────┘                                                   │
│          │ HTTPS (TLS 1.2/1.3)                                      │
│          ▼                                                          │
│   ┌──────────────────────────────────────────────────────────┐      │
│   │                    Nginx Reverse Proxy                    │      │
│   │  ┌─────────────────────────────────────────────────────┐ │      │
│   │  │ • TLS Termination (SSL Certificates)                │ │      │
│   │  │ • Rate Limiting (30/60 req/s)                       │ │      │
│   │  │ • Security Headers (XSS, CSRF protection)           │ │      │
│   │  │ • SSE Optimization (long-lived connections)         │ │      │
│   │  └─────────────────────────────────────────────────────┘ │      │
│   └──────────────┬───────────────────────┬───────────────────┘      │
│                  │ HTTP (internal)        │ HTTP (internal)         │
│                  ▼                        ▼                         │
│   ┌──────────────────────┐    ┌──────────────────────┐              │
│   │   MCP SSE Server     │    │   REST API Server    │              │
│   │   (Port 8000)        │    │   (Port 8080)        │              │
│   │                      │    │                      │              │
│   │ • /sse               │    │ • /api/v1/*          │              │
│   │ • /messages          │    │ • /docs (Swagger)    │              │
│   │ • /health            │    │ • /health            │              │
│   └──────────────────────┘    └──────────────────────┘              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

External Endpoints (HTTPS):
├── https://localhost/        → MCP SSE (via Nginx :443)
├── https://localhost/sse     → SSE Connection
├── https://localhost:8443/   → REST API (via Nginx :8443)
└── https://localhost:8443/docs → Swagger UI

Internal (HTTP, Docker network only):
├── http://medical-calc-mcp:8000  → MCP Server
└── http://medical-calc-api:8080  → API Server
```

### SSL Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SSL_ENABLED` | `false` | Enable SSL/TLS (`true`/`false`) |
| `SSL_KEYFILE` | - | Path to SSL private key file |
| `SSL_CERTFILE` | - | Path to SSL certificate file |
| `SSL_CA_CERTS` | - | Path to CA certificates (optional) |
| `SSL_DIR` | `./nginx/ssl` | SSL cert directory (Docker only) |

### Option 1: Docker Deployment (Recommended)

Best for production and team environments.

```bash
# Step 1: Generate SSL certificates
chmod +x scripts/generate-ssl-certs.sh
./scripts/generate-ssl-certs.sh

# Step 2: Start HTTPS services
./scripts/start-https-docker.sh up

# Other commands
./scripts/start-https-docker.sh down     # Stop services
./scripts/start-https-docker.sh logs     # View logs
./scripts/start-https-docker.sh restart  # Restart
./scripts/start-https-docker.sh status   # Check status
```

**Custom Certificates (Docker):**

```bash
# Use custom certificate directory
SSL_DIR=/path/to/your/certs docker-compose -f docker-compose.https.yml up -d

# Use Let's Encrypt certificates
SSL_DIR=/etc/letsencrypt/live/example.com docker-compose -f docker-compose.https.yml up -d
```

**Endpoints:**

| Service | URL | Description |
|---------|-----|-------------|
| MCP SSE | `https://localhost/` | MCP Server-Sent Events |
| MCP SSE | `https://localhost/sse` | SSE connection |
| REST API | `https://localhost:8443/` | REST API root |
| Swagger UI | `https://localhost:8443/docs` | API documentation |
| Health | `https://localhost/health` | MCP health check |
| Health | `https://localhost:8443/health` | API health check |

### Option 2: Local Development (No Docker)

Uses Python/Uvicorn native SSL support for quick local testing.

```bash
# Step 1: Generate SSL certificates (or use your own)
./scripts/generate-ssl-certs.sh

# Step 2: Start HTTPS services
./scripts/start-https-local.sh          # Start both MCP and API
./scripts/start-https-local.sh sse      # Start MCP SSE only
./scripts/start-https-local.sh api      # Start REST API only
```

**Custom Certificates (Local):**

```bash
# Use custom certificate paths via environment variables
SSL_KEYFILE=/path/to/server.key \
SSL_CERTFILE=/path/to/server.crt \
./scripts/start-https-local.sh

# Custom ports
SSL_KEYFILE=/certs/key.pem SSL_CERTFILE=/certs/cert.pem \
MCP_PORT=9000 API_PORT=9001 \
./scripts/start-https-local.sh

# Direct command with CLI arguments
python -m src.main --mode sse --port 8443 \
    --ssl-keyfile /path/to/server.key \
    --ssl-certfile /path/to/server.crt
```

**Endpoints:**

| Service | URL | Description |
|---------|-----|-------------|
| MCP SSE | `https://localhost:8443/` | MCP Server-Sent Events |
| REST API | `https://localhost:9443/` | REST API |
| Swagger UI | `https://localhost:9443/docs` | API documentation |

### Option 3: Production with Let's Encrypt

For real domain names with free trusted certificates.

```bash
# 1. Edit nginx/nginx.conf, uncomment these lines:
ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

# 2. Use certbot to obtain certificates:
sudo certbot certonly --webroot -w /var/www/certbot \
  -d your-domain.com -d api.your-domain.com

# 3. Start services with Let's Encrypt certs
SSL_DIR=/etc/letsencrypt/live/your-domain.com \
docker-compose -f docker-compose.https.yml up -d
```

### Trust Self-Signed Certificates

To avoid browser warnings during development:

**Linux (Ubuntu/Debian):**

```bash
sudo cp nginx/ssl/ca.crt /usr/local/share/ca-certificates/medical-calc-dev.crt
sudo update-ca-certificates
```

**macOS:**

```bash
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain nginx/ssl/ca.crt
```

**Windows:**

```
1. Double-click nginx/ssl/ca.crt
2. Install Certificate → Local Machine
3. Place in "Trusted Root Certification Authorities"
```

### Claude Desktop Configuration (HTTPS)

```json
{
  "mcpServers": {
    "medical-calc": {
      "url": "https://localhost/sse"
    }
  }
}
```

For production with a real domain:

```json
{
  "mcpServers": {
    "medical-calc": {
      "url": "https://mcp.your-domain.com/sse"
    }
  }
}
```

### Files Overview

| File | Description |
|------|-------------|
| `nginx/nginx.conf` | Nginx configuration with TLS, rate limiting, SSE optimization |
| `docker-compose.https.yml` | Docker Compose for HTTPS deployment |
| `scripts/generate-ssl-certs.sh` | Generate self-signed SSL certificates |
| `scripts/start-https-docker.sh` | Start/stop Docker HTTPS services |
| `scripts/start-https-local.sh` | Start local HTTPS (supports custom certs) |
| `src/infrastructure/mcp/config.py` | SslConfig class for SSL configuration |

### SSL Configuration Reference

| Scenario | Cert Location | Configuration Method |
|----------|---------------|---------------------|
| Docker (default) | `nginx/ssl/` | No config needed |
| Docker (custom) | Custom path | `SSL_DIR` env var or volumes |
| Docker (Let's Encrypt) | `/etc/letsencrypt/...` | Modify `nginx/nginx.conf` |
| Local (default) | `nginx/ssl/` | No config needed |
| Local (custom) | Custom path | `SSL_KEYFILE` + `SSL_CERTFILE` env vars |
| CLI direct | Custom path | `--ssl-keyfile` + `--ssl-certfile` args |

### Troubleshooting

**Certificate not trusted:**

```bash
# Regenerate certificates
rm -rf nginx/ssl/*
./scripts/generate-ssl-certs.sh

# Then re-add to system trust store (see above)
```

**Port already in use:**

```bash
# Check what's using the port
sudo lsof -i :443
sudo lsof -i :8443

# Kill the process or use different ports
```

**Docker container not starting:**

```bash
# Check logs
docker-compose -f docker-compose.https.yml logs nginx
docker-compose -f docker-compose.https.yml logs medical-calc-mcp

# Rebuild
docker-compose -f docker-compose.https.yml up -d --build
```

**SSE connection timeout:**

```bash
# Nginx is configured for 24h timeout, but if issues persist:
# Check nginx/nginx.conf has these settings:
proxy_read_timeout 24h;
proxy_send_timeout 24h;
proxy_buffering off;
```

---

## 🌐 REST API ⭐ NEW

Besides MCP protocol, the server also provides a **standalone REST API** for direct HTTP access.

### Quick Start

```bash
# Start API server
uv run python src/main.py --mode api --port 8080

# With uvicorn (production)
uv run uvicorn src.infrastructure.api.server:app --host 0.0.0.0 --port 8080
```

### API Documentation

Once running, visit:
- **Swagger UI**: <http://localhost:8080/docs>
- **ReDoc**: <http://localhost:8080/redoc>
- **OpenAPI JSON**: <http://localhost:8080/openapi.json>

### REST API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/v1/calculators` | GET | List all calculators |
| `/api/v1/calculators/{tool_id}` | GET | Get calculator info |
| `/api/v1/search?q={keyword}` | GET | Search calculators |
| `/api/v1/specialties` | GET | List specialties |
| `/api/v1/specialties/{specialty}` | GET | List by specialty |
| `/api/v1/calculate/{tool_id}` | POST | Execute calculation |

### Example: Calculate CKD-EPI

```bash
# Using curl
curl -X POST "http://localhost:8080/api/v1/calculate/ckd_epi_2021" \
  -H "Content-Type: application/json" \
  -d '{"params": {"serum_creatinine": 1.2, "age": 65, "sex": "female"}}'
```

**Response:**

```json
{
  "success": true,
  "calculator": "ckd_epi_2021",
  "result": {
    "score_name": "CKD-EPI 2021",
    "value": 49.2,
    "unit": "mL/min/1.73m²",
    "interpretation": {
      "summary": "G3a: Mildly to moderately decreased",
      "severity": "moderate"
    }
  }
}
```

### Quick Calculate Endpoints

Some calculators have dedicated endpoints with query parameters:

```bash
# CKD-EPI (Query parameters)
curl "http://localhost:8080/api/v1/ckd-epi?serum_creatinine=1.2&age=65&sex=female"

# SOFA Score
curl -X POST "http://localhost:8080/api/v1/sofa?pao2_fio2_ratio=200&platelets=100&bilirubin=2.0&cardiovascular=dopamine_lte_5&gcs_score=13&creatinine=2.5"
```

---

## 🔐 Security ⭐ NEW

### Security Features

This project implements multiple security layers:

| Layer | Feature | Description |
|-------|---------|-------------|
| **HTTPS** | TLS 1.2/1.3 encryption | All traffic encrypted via Nginx |
| **Input Validation** | 3-layer validation | Pydantic → ParameterValidator → Domain rules |
| **CORS** | Configurable origins | Environment variable controlled |
| **Rate Limiting** | Nginx + Application level | Dual-layer protection (optional) |
| **API Authentication** | Optional API Key | Disabled by default, enable via env |
| **Security Headers** | XSS/CSRF protection | X-Frame-Options, X-Content-Type-Options |
| **Dependencies** | Vulnerability scanning | pip-audit integrated |
| **No Database** | In-memory only | No SQL injection risk |
| **No Secrets** | Stateless | No credentials stored |

> 📖 **For detailed HTTPS deployment instructions, see [HTTPS Deployment](#-https-deployment).**

### 🔑 Optional Security Features

All optional security features are **DISABLED by default**. Enable via environment variables:

#### Rate Limiting (Application Level)

```bash
# Enable rate limiting
SECURITY_RATE_LIMIT_ENABLED=true   # Default: false
SECURITY_RATE_LIMIT_RPM=60         # Requests per minute (default: 60)
SECURITY_RATE_LIMIT_BURST=10       # Burst size (default: 10)
SECURITY_RATE_LIMIT_BY_IP=true     # Per-IP rate limiting (default: true)
```

#### API Key Authentication

```bash
# Enable API authentication
SECURITY_AUTH_ENABLED=true         # Default: false
SECURITY_API_KEYS=key1,key2,key3   # Comma-separated API keys (min 8 chars each)
SECURITY_AUTH_HEADER=X-API-Key     # Header name (default: X-API-Key)
SECURITY_AUTH_PARAM=api_key        # Query param name (default: api_key)
```

**Usage Example:**

```bash
# With header
curl -H "X-API-Key: your-api-key" http://localhost:8000/sse

# With query parameter
curl "http://localhost:8000/sse?api_key=your-api-key"

# With Bearer token
curl -H "Authorization: Bearer your-api-key" http://localhost:8000/sse
```

#### Security Scenarios

| Scenario | Rate Limit | Auth | Configuration |
|----------|------------|------|---------------|
| **Local Development** | ❌ Off | ❌ Off | Default (no env vars) |
| **Internal Network** | ✅ On | ❌ Off | `SECURITY_RATE_LIMIT_ENABLED=true` |
| **Public API** | ✅ On | ✅ On | Both enabled + API keys |

### Configuration

**CORS Configuration:**

```bash
# Development (default) - Allow all origins
CORS_ORIGINS="*"

# Production - Restrict to specific domains
CORS_ORIGINS="https://your-app.com,https://api.your-app.com"
```

**Other Security Settings:**

```bash
# API Server
API_HOST=0.0.0.0   # Use 127.0.0.1 for local only
API_PORT=8080

# MCP Server  
MCP_HOST=0.0.0.0   # Use 127.0.0.1 for local only
MCP_PORT=8000
```

### Production Recommendations

| Item | Recommendation |
|------|----------------|
| **HTTPS** | ✅ Use provided Nginx + SSL config |
| **CORS** | Set specific `CORS_ORIGINS` |
| **Rate Limiting** | ✅ Enable application-level rate limiting |
| **Authentication** | ✅ Enable API key authentication |
| **Network** | Run in private network/VPC |
| **Certificates** | Use Let's Encrypt for production |
| **Monitoring** | Enable access logging |

### Dependency Security

```bash
# Check for known vulnerabilities
uv run pip-audit --strict

# Upgrade all packages
uv sync --upgrade

# Lock dependencies
uv lock
```

### Security Audit Results (2025-06)

✅ **Passed Checks:**
- No SQL/Command injection vulnerabilities
- No hardcoded secrets or credentials
- No sensitive data exposure in error messages
- Input validation at all layers
- Dependencies updated (no known CVEs)

⚠️ **Notes:**
- Default CORS is permissive (`*`) - configure for production
- No built-in authentication - add at infrastructure layer if needed
- Medical calculations are for reference only - not for clinical decisions

---

## 🔍 Tool Discovery

The **Two-Level Key System** combined with **Tool Relation Graph** is the core innovation of this project:

### Discovery Philosophy

When an AI agent needs a medical calculator, it uses **Unified Discovery**:

```
┌─────────────────────────────────────────────────────────────┐
│  discover() - Unified Entry Point (v3.0)                     │
├─────────────────────────────────────────────────────────────┤
│  Path A: Explore All Categories                              │
│  ① discover() → {specialties: [...], contexts: [...]}       │
│  ② discover(by="specialty", value="critical_care")          │
│  ③ get_tool_schema("sofa_score") → params, references       │
│  ④ calculate("sofa_score", {...params})                      │
├─────────────────────────────────────────────────────────────┤
│  Path B: Context-based                                       │
│  ① discover(by="context", value="preoperative_assessment")  │
│  ② get_tool_schema("rcri") → params, param_sources          │
│  ③ calculate("rcri", {...params})                            │
├─────────────────────────────────────────────────────────────┤
│  Path C: Keyword Search                                      │
│  ① discover(by="keyword", value="sepsis")                    │
│  ② get_tool_schema("qsofa_score")                            │
│  ③ calculate("qsofa_score", {...params})                     │
├─────────────────────────────────────────────────────────────┤
│  Path D: Graph-based Discovery                               │
│  ① get_related_tools("sofa_score") → [qsofa, apache_ii...]  │
│  ② find_tools_by_params(["creatinine", "age"]) → [tools...] │
└─────────────────────────────────────────────────────────────┘
```

**Every step returns `next_step` hints, so the Agent never gets lost!**

### Tool Relation Graph (Hypergraph)

The **ToolRelationGraph** connects tools based on:

| Relation Type | Weight | Example |
|---------------|--------|---------|
| `SHARED_PARAM` | 0.2 | SOFA ↔ APACHE II (both use creatinine) |
| `SAME_SPECIALTY` | 0.3 | SOFA ↔ qSOFA (both Critical Care) |
| `SAME_CONTEXT` | 0.2 | RCRI ↔ ASA (both Preoperative Assessment) |

```python
# Find related tools via graph traversal
get_related_tools("sofa_score")
# → [{"tool_id": "qsofa_score", "similarity": 0.85},
#    {"tool_id": "apache_ii", "similarity": 0.72}, ...]

# Reverse lookup: "I have these values, what can I calculate?"
find_tools_by_params(["creatinine", "bilirubin", "inr"])
# → [meld_score, child_pugh, ...]
```

### Unified Calculate Interface (v2.0)

Instead of 75+ individual calculator tools, we provide a **single unified `calculate()` tool**:

```python
# Old approach (deprecated):
# calculate_sofa(pao2_fio2=300, platelets=150, ...)

# New approach (v2.0):
calculate(
    tool_id="sofa_score",
    params={
        "pao2_fio2_ratio": 300,
        "platelets": 150,
        "bilirubin": 1.2,
        # ... other params
    }
)
```

**Benefits:**
- 🎯 **Token Efficient**: Only 6 tools instead of 75+ in context
- 🔍 **Discovery First**: Use discover() to find the right calculator
- 📖 **Self-Documenting**: `get_tool_schema()` shows exact params needed

### Low Level Key (Precise Selection)

For **precise tool selection** when you know exactly what you need:

```python
LowLevelKey(
    tool_id="ckd_epi_2021",           # Unique identifier
    name="CKD-EPI 2021",              # Human-readable name
    purpose="Calculate eGFR",          # What it does
    input_params=["age", "sex", "creatinine"],  # Required inputs
    output_type="eGFR with CKD staging"         # Output format
)
```

### High Level Key (Intelligent Discovery)

For **intelligent discovery** when exploring options:

```python
HighLevelKey(
    specialties=(Specialty.NEPHROLOGY, Specialty.INTERNAL_MEDICINE),
    conditions=("chronic kidney disease", "CKD", "renal impairment"),
    clinical_contexts=(ClinicalContext.STAGING, ClinicalContext.DRUG_DOSING),
    clinical_questions=(
        "What is the patient's kidney function?",
        "Should I adjust drug dosage for renal function?",
    ),
    icd10_codes=("N18", "N19"),
    keywords=("eGFR", "GFR", "creatinine", "kidney function")
)
```

### 🔑 Key Feature: Multi-Specialty Tools

**One tool can belong to multiple High Level categories!**

Example: SOFA Score belongs to:

| Category | Values |
|----------|--------|
| Specialties | Critical Care, Emergency Medicine, Internal Medicine, Pulmonology |
| Conditions | Sepsis, Septic Shock, Organ Dysfunction, MODS |
| Contexts | Severity Assessment, Prognosis, ICU Management, Diagnosis |

This means:
- Search "sepsis" → Returns SOFA, qSOFA, NEWS, ...
- Search "critical care" → Returns SOFA, APACHE II, RASS, GCS, CAM-ICU, ...
- Search "organ dysfunction" → Returns SOFA, ...

### Consolidated MCP Tools (v3.0)

| Layer | Tool | Purpose |
|-------|------|---------|
| **High-Level** | `discover(by, value, limit)` | Unified discovery (specialty/context/keyword/all) |
| **High-Level** | `get_related_tools(tool_id)` | Graph-based related tool discovery |
| **High-Level** | `find_tools_by_params(params)` | Reverse lookup by available parameters |
| **Low-Level** | `get_tool_schema(tool_id)` | Full metadata + param schemas + references |
| **Low-Level** | `calculate(tool_id, params)` | Execute single calculation |
| **Low-Level** | `calculate_batch(calculations)` | Batch calculations with cross-analysis |

**Total: 6 tools** (consolidated from 12 in v2.0)

### Example: AI Agent Workflow

```
User: "I need to assess this patient's cardiac risk before surgery"

# Step 1: Agent uses hierarchical navigation
Agent: list_contexts()
       → Returns: [..., "preoperative_assessment", ...]
       → next_step: "list_by_context('preoperative_assessment')"

# Step 2: Filter by context
Agent: list_by_context("preoperative_assessment")
       → Returns: [rcri, asa_physical_status, mallampati_score, ...]
       → next_step: "get_calculator_info('rcri')"

# Step 3: Get tool details
Agent: get_calculator_info("rcri")
       → Returns: Full metadata with input params, references
       → next_step: "calculate_rcri(...)"

# Step 4: Calculate
Agent: calculate_rcri(high_risk_surgery=True, ischemic_heart_disease=True, ...)
       → Returns: Score, risk percentage, recommendations
```

### Example: ICU Sepsis Workup

```
User: "Evaluate this ICU patient for sepsis"

Agent: search_calculators("sepsis")
       → Returns: SOFA, qSOFA, NEWS2, APACHE II

# Per Sepsis-3 guidelines:

Agent: calculate_qsofa(respiratory_rate=24, systolic_bp=95, altered_mentation=True)
       → qSOFA = 3 (High risk, prompt evaluation needed)

Agent: calculate_sofa(pao2_fio2_ratio=200, platelets=80, bilirubin=2.5, ...)
       → SOFA = 8 (Sepsis confirmed if infection suspected, ≥2 point increase)
```

---

## 🔧 Available Tools

> **Registry Snapshot**: 128 calculators across 26 specialties
>
> **Quality Snapshot**: 2067 collected tests | 244 PMIDs | 205 DOIs | 100% citation coverage
>
> 📋 **[See Full Roadmap →](ROADMAP.md)** | **[Contributing Guide →](CONTRIBUTING.md)**

### 📑 Quick Navigation
<!-- BEGIN GENERATED:CATALOG_OVERVIEW -->
This README no longer carries a hand-maintained calculator inventory. The same generated source now feeds repository docs and MkDocs pages.

**Registry Snapshot**: 151 calculators across 31 specialties

- [Full calculator catalog](docs/CALCULATOR_CATALOG.md)
- [Traditional Chinese catalog](docs/CALCULATOR_CATALOG.zh-TW.md)
- [Website calculator catalog](docs_site/calculators/index.md)
- [網站版繁中總覽](docs_site/zh-tw/calculators.md)
- Regenerate locally with `uv run python scripts/generate_tool_catalog_docs.py`

| Specialty | Tools |
|-----------|------:|
| Critical Care | 18 |
| Geriatrics | 13 |
| Cardiology | 11 |
| Emergency Medicine | 9 |
| Psychiatry | 9 |
| Anesthesiology | 8 |

You can still inspect the live registry via `python scripts/count_tools.py`, `calculator://list`, or `list_calculators()` from your MCP client.
<!-- END GENERATED:CATALOG_OVERVIEW -->

---

### Generated calculator catalog

The full tool inventory and specialty summary are generated directly from the registry to remove README drift risk.

- [Full calculator catalog](docs/CALCULATOR_CATALOG.md)
- [Traditional Chinese catalog](docs/CALCULATOR_CATALOG.zh-TW.md)
- Regenerate locally with `uv run python scripts/generate_tool_catalog_docs.py`

---

### 🔍 Discovery Tools

#### Step 1: Entry Points

| Tool | Description |
|------|-------------|
| `list_specialties()` | 📋 List available specialties (returns next_step) |
| `list_contexts()` | 📋 List available clinical contexts (returns next_step) |
| `list_calculators()` | 📋 List all registered calculators |

#### Step 2: Filter by Category

| Tool | Description |
|------|-------------|
| `list_by_specialty(specialty)` | Filter tools by medical specialty |
| `list_by_context(context)` | Filter tools by clinical context |
| `search_calculators(keyword)` | 🔍 Quick keyword search |

#### Step 3: Get Details

| Tool | Description |
|------|-------------|
| `get_calculator_info(tool_id)` | 📖 Get params, references, examples |

#### Step 4: Execute Calculation

| Tool | Description |
|------|-------------|
| `calculate(tool_id, params)` | 🧮 Unified calculator (supports all 75+ calculators) |

[↑ Back to Navigation](#-quick-navigation)

---

### 📦 Resources

| Resource URI | Description |
|--------------|-------------|
| `calculator://list` | Markdown list of all calculators |
| `calculator://{tool_id}/references` | Paper references for a calculator |
| `calculator://{tool_id}/parameters` | Input parameter definitions |
| `calculator://{tool_id}/info` | Full calculator metadata |

---

### 📝 Prompts

Prompts provide guided multi-tool workflows for common clinical scenarios:

| Prompt | Description |
|--------|-------------|
| `sepsis_evaluation` | qSOFA → SOFA → RASS → CAM-ICU workflow |
| `preoperative_risk_assessment` | ASA → RCRI → Mallampati workflow |
| `icu_daily_assessment` | RASS → CAM-ICU → GCS → SOFA daily rounds |
| `pediatric_drug_dosing` | Weight-based dosing + MABL + transfusion |
| `acute_kidney_injury_assessment` | CKD-EPI + AKI staging workflow |

**Usage:**

```
# In MCP client, request a prompt:
prompt: sepsis_evaluation
→ Returns structured workflow with step-by-step guidance
```

[↑ Back to Navigation](#-quick-navigation)

---

## 📖 Usage Examples

### Python Examples ⭐ NEW

The project includes ready-to-run example scripts in the `examples/` folder:

```bash
# Basic usage examples
uv run python examples/basic_usage.py

# Clinical workflow examples
uv run python examples/clinical_workflows.py
```

**Available Examples:**

| File | Description |
|------|-------------|
| `basic_usage.py` | Individual calculator usage (CKD-EPI, SOFA, RCRI, CHA₂DS₂-VASc, Wells PE) |
| `clinical_workflows.py` | Multi-calculator clinical scenarios (Sepsis, Preop, Chest Pain, AF) |

### Example 1: CKD-EPI 2021 (eGFR)

**Input:**

```json
{
  "serum_creatinine": 1.2,
  "age": 65,
  "sex": "female"
}
```

**Output:**

```json
{
  "score_name": "CKD-EPI 2021",
  "result": 67.1,
  "unit": "mL/min/1.73m²",
  "interpretation": {
    "summary": "Mildly decreased kidney function (G2)",
    "stage": "G2",
    "recommendation": "Monitor kidney function annually; adjust renally-excreted drugs"
  },
  "references": [{
    "citation": "Inker LA, et al. N Engl J Med. 2021;385(19):1737-1749.",
    "doi": "10.1056/NEJMoa2102953"
  }]
}
```

### Example 2: Tool Discovery

**Query:** `search_calculators("airway")`

**Output:**

```json
{
  "keyword": "airway",
  "count": 1,
  "tools": [{
    "tool_id": "mallampati_score",
    "name": "Modified Mallampati Classification",
    "purpose": "Predict difficult intubation based on oropharyngeal visualization",
    "specialties": ["anesthesiology", "emergency_medicine"],
    "input_params": ["mallampati_class"]
  }]
}
```

### Example 3: RCRI Cardiac Risk

**Input:**

```json
{
  "high_risk_surgery": true,
  "ischemic_heart_disease": true,
  "heart_failure": false,
  "cerebrovascular_disease": false,
  "insulin_diabetes": true,
  "creatinine_above_2": false
}
```

**Output:**

```json
{
  "score_name": "Revised Cardiac Risk Index",
  "result": 3,
  "interpretation": {
    "summary": "RCRI Class III - Elevated cardiac risk",
    "risk_percentage": "6.6%",
    "recommendation": "Consider cardiology consultation; optimize medical therapy"
  }
}
```

---

## 📜 References

All calculators cite original peer-reviewed research. See [references/README.md](references/README.md) for complete citations.

### 📋 Guideline Mapping

We systematically map our calculators to clinical guidelines:

<!-- BEGIN GENERATED:GUIDELINE_OVERVIEW -->
We systematically map our calculators to major clinical guideline reviews, and this overview is generated from the same source used by the docs and website.

Tracked coverage: **65/65** recommended tools across **16** domains.

- [Generated guideline coverage summary](docs/GUIDELINE_COVERAGE_SUMMARY.md)
- [Website guideline coverage page](docs_site/development/guideline-coverage.md)
- [2023-2025 detailed guideline review](docs/GUIDELINE_RECOMMENDED_TOOLS_2023_2025.md)
- [2020-2025 historical guideline review](docs/GUIDELINE_RECOMMENDED_TOOLS_2020_2025.md)

| Domain | Implemented | Total | Coverage |
|--------|------------:|------:|---------:|
| Sepsis / Critical Care | 9 | 9 | 100% |
| Cardiovascular | 9 | 9 | 100% |
| GI Bleeding | 3 | 3 | 100% |
| Liver Disease | 6 | 6 | 100% |
| Kidney Disease | 2 | 2 | 100% |
| Respiratory / Pneumonia | 5 | 5 | 100% |
| Thromboembolism | 4 | 4 | 100% |
| Neurology | 7 | 7 | 100% |
| Anesthesiology | 6 | 6 | 100% |
| Trauma | 4 | 4 | 100% |
| Burns | 2 | 2 | 100% |
| Pediatrics | 2 | 2 | 100% |
| Oncology | 2 | 2 | 100% |
| Nutrition | 2 | 2 | 100% |
| Rheumatology | 1 | 1 | 100% |
| Osteoporosis | 1 | 1 | 100% |
<!-- END GENERATED:GUIDELINE_OVERVIEW -->

### Citation Format

We use **Vancouver style** citations:

```
Inker LA, Eneanya ND, Coresh J, et al. New Creatinine- and Cystatin C-Based 
Equations to Estimate GFR without Race. N Engl J Med. 2021;385(19):1737-1749. 
doi:10.1056/NEJMoa2102953
```

---

## 👨‍💻 Development

### Project Status

| Phase | Status | Description |
|-------|--------|-------------|
| **Modernization** | ✅ Complete | **Migrated to `uv`, 100% `mypy --strict` coverage, `ruff` integration** |
| Phase 1-8 | ✅ Complete | Foundation, 78 Calculators, MCP Integration, Validation Layer |
| Phase 13 | ✅ Complete | Additional Clinical Tools (ABCD2, mRS, TIMI STEMI, Rockall, FIB-4) |
| Phase 17-18 | ✅ Complete | Obstetrics (Bishop, Ballard), Trauma (ISS, TBSA, Parkland) |

### Quick Start (Developer)

```bash
# 1. Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Setup environment and install dependencies
uv sync

# CI-parity install using the lock file
uv sync --frozen --extra dev --group dev

# 3. Run tests
uv run pytest

# 4. Run MCP server in dev mode
uv run mcp dev src/main.py
```

---

## 🧪 Testing

### Testing Strategy

We maintain a high-quality codebase with **2,019 collected tests** and automated coverage reporting in CI.

```
┌─────────────────────────────────────────────────────────────────┐
│                        Testing Pyramid                          │
├─────────────────────────────────────────────────────────────────┤
│                     E2E Tests (MCP Protocol)                     │
│                    (700+ tests covering all tools)               │
│                               ╱  ╲                               │
│           Integration Tests              MCP Inspector           │
│          (Use Cases + Registry)          (Manual Testing)        │
│                  ╱              ╲                                │
│      Unit Tests (Domain)    Validation Tests                     │
│      (940+ tests for logic) (Parameter constraints)              │
└─────────────────────────────────────────────────────────────────┘
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific layer tests
uv run pytest tests/test_acid_base.py -v

# Run with verbose output
uv run pytest -v --tb=short
```

### Type Safety

The project enforces **strict type checking** across the entire codebase.

```bash
# Run strict type check
uv run mypy --no-incremental --strict src tests

# Run linter
uv run ruff check src tests

# Auto-fix linting issues
uv run ruff check --fix src tests
```

### API Contract

The REST API OpenAPI contract is tracked as a generated artifact so schema drift is caught in CI before downstream clients break.

```bash
# Refresh the generated OpenAPI snapshot
uv run python scripts/generate_openapi_spec.py

# Refresh the generated REST API reference
uv run python scripts/generate_rest_api_docs.py

# Verify generated docs and API contract are current
uv run python scripts/check_project_consistency.py --check-tests
```

Dependency upgrade policy is documented in [docs/DEPENDENCY_UPGRADE_PLAYBOOK.md](docs/DEPENDENCY_UPGRADE_PLAYBOOK.md).

### CI/CD Pipeline

The project uses GitHub Actions for continuous integration with the following features:

```
┌─────────────────────────────────────────────────────────────┐
│                    Push to develop                          │
├─────────────────────────────────────────────────────────────┤
│  auto-fix:                                                  │
│    • ruff check --fix (auto-fix linting)                    │
│    • ruff format (auto-format code)                         │
│    • uv lock (update dependency lock)                       │
│    • Auto-commit back to develop [skip ci]                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    test (3.11, 3.12, 3.13)                  │
├─────────────────────────────────────────────────────────────┤
│    • ruff check (lint)                                      │
│    • ruff format --check (format check)                     │
│    • mypy (type check)                                      │
│    • pytest (tests + coverage ≥90%)                         │
└─────────────────────────────────────────────────────────────┘
                            ↓ (main only)
┌─────────────────────────────────────────────────────────────┐
│                    docker + release                         │
├─────────────────────────────────────────────────────────────┤
│    • Build & test Docker image (/health endpoint)           │
│    • Auto-create GitHub Release when version changes        │
└─────────────────────────────────────────────────────────────┘
```

| Feature | Description |
|---------|-------------|
| **Auto-fix on develop** | Automatically fix linting/formatting issues |
| **Multi-Python testing** | Tests on Python 3.11, 3.12, 3.13 |
| **Docker health check** | Uses `/health` endpoint for liveness probes |
| **Auto-release** | Creates GitHub Release when `pyproject.toml` version changes |
| **Concurrency control** | Cancels in-progress runs for same branch |

---

## 🛠️ Requirements

- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/)** - Fast Python package manager (required)
- **MCP SDK** (FastMCP) - Installed automatically via `uv sync`

---

### Roadmap

> 📋 **[See Full Roadmap →](ROADMAP.md)** for detailed implementation plans

```
2025 Q4 (Current)                2026 Q1                          2026 Q2
───────────────────────────────────────────────────────────────────────────────
Phase 8: ✅ Complete             Phase 9-10: Acid-Base/Cardio    Phase 11-14: Complete
├── ✅ HAS-BLED (2024 ESC)       ├── Anion Gap, Delta Ratio      ├── Resp/Oxygenation
├── ✅ Child-Pugh               ├── Corrected QT, Shock Index    ├── Neuro/Sedation
└── ✅ KDIGO AKI                └── A-a Gradient, IBW           ├── Infectious Disease
                                                                 └── Common Utilities
Phase 9: ✅ Complete
├── ✅ Anion Gap
├── ✅ Delta Ratio
├── ✅ Corrected Sodium
├── ✅ Winter's Formula
├── ✅ Osmolar Gap
└── ✅ Free Water Deficit
```

### Recently Added Calculators (Phase 13 Complete ✅)

| Priority | Tool ID | Name | Status | Reference |
|----------|---------|------|--------|-----------|
| ✅ Done | `abcd2` | ABCD2 Score | Complete | Johnston 2007 |
| ✅ Done | `modified_rankin_scale` | Modified Rankin Scale (mRS) | Complete | van Swieten 1988 |
| ✅ Done | `timi_stemi` | TIMI STEMI Risk Score | Complete | Morrow 2000 |
| ✅ Done | `rockall_score` | Rockall Score | Complete | Rockall 1996 |
| ✅ Done | `fib4_index` | FIB-4 Index | Complete | Sterling 2006 |

---

## 📄 License

Apache 2.0 - See [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) - Anthropic's open protocol for AI-tool communication
- [FastMCP](https://github.com/modelcontextprotocol/python-sdk) - Python SDK for MCP
- Original authors of all cited medical calculators and scoring systems
