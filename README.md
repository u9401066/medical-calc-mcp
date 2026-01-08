# Medical Calculator MCP Server 🏥

A DDD-architected medical calculator service providing clinical scoring tools for AI Agent integration via MCP (Model Context Protocol).

[繁體中文版 (Traditional Chinese)](README.zh-TW.md)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP SDK](https://img.shields.io/badge/MCP-FastMCP-green.svg)](https://github.com/modelcontextprotocol/python-sdk)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![CI](https://github.com/u9401066/medical-calc-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/u9401066/medical-calc-mcp/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/tests-124%20passed-brightgreen.svg)](#-development)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-orange.svg)](https://github.com/astral-sh/ruff)
[![Architecture](https://img.shields.io/badge/architecture-DDD%20Onion-purple.svg)](#-architecture)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

---

## 📖 Table of Contents

- [Features](#-features)
- [Why This Project?](#-why-this-project)
- [Research Framework](#-research-framework) 🔬 NEW
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
  - [Quick Navigation](#-quick-navigation)
  - [Anesthesiology](#-anesthesiology--preoperative)
  - [Critical Care](#-critical-care--icu)
  - [Pediatrics](#-pediatrics)
  - [Nephrology](#-nephrology)
  - [Pulmonology](#-pulmonology)
  - [Cardiology](#-cardiology)
  - [Hematology](#-hematology)
  - [Emergency Medicine](#-emergency-medicine)
  - [Hepatology](#-hepatology)
  - [Acid-Base / Metabolic](#-acid-base--metabolic)
  - [Discovery Tools](#-discovery-tools)
  - [Prompts](#-prompts)
- [Usage Examples](#-usage-examples)
- [References](#-references)
- [Development](#-development)
- [Deployment Guide](docs/DEPLOYMENT.md) 📘
- [Roadmap](ROADMAP.md)

---

## 🎯 Features

- **🔌 MCP Native Integration**: Built with FastMCP SDK for seamless AI agent integration
- **🔍 Intelligent Tool Discovery**: Two-level key system (Low/High Level) for smart tool selection
- **🛡️ Smart Parameter Matching**: Alias support, fuzzy matching, and typo tolerance
- **⚠️ Boundary Validation**: Literature-backed clinical range checking with automatic warnings
- **🏗️ Clean DDD Architecture**: Onion architecture with clear separation of concerns
- **📚 Evidence-Based**: All formulas cite original peer-reviewed research papers (Vancouver style)
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

1.  **Domain Specification**: Human experts define the target medical specialty or clinical domain.
2.  **AI-Driven Search**: AI agents perform comprehensive searches for the latest clinical guidelines and consensus.
3.  **Guideline Extraction**: Systematically identify recommended scoring systems and calculations mentioned in those guidelines.
4.  **Source Validation**: Trace back to original peer-reviewed primary papers to verify exact formulas and coefficients.
5.  **Implementation**: Develop validated calculation tools with precise parameters and evidence-based interpretations.

---

## 🔬 Research Framework

> This project implements a **Neuro-Symbolic Framework** for reliable medical calculation, combining LLM understanding with validated symbolic computation.

### Academic Positioning

| Challenge | Traditional LLM | Our Solution |
|-----------|-----------------|--------------|
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

Enable HTTPS for secure communication in production environments.

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

Uses Uvicorn's native SSL support for quick local testing.

```bash
# Step 1: Generate SSL certificates
./scripts/generate-ssl-certs.sh

# Step 2: Start HTTPS services
./scripts/start-https-local.sh          # Start both MCP and API
./scripts/start-https-local.sh sse      # Start MCP SSE only
./scripts/start-https-local.sh api      # Start REST API only
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

# 3. Start services
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
| `scripts/start-https-local.sh` | Start local HTTPS (Uvicorn SSL) |

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
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **OpenAPI JSON**: http://localhost:8080/openapi.json

### API Endpoints

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

The **Two-Level Key System** is the core innovation of this project:

### Discovery Philosophy

When an AI agent needs a medical calculator, it uses **Hierarchical Navigation**:

```
┌─────────────────────────────────────────────────────────────┐
│  Path A: Specialty-based                                     │
│  ① list_specialties() → ["critical_care", "anesthesiology"]│
│  ② list_by_specialty("anesthesiology") → [tool_id, ...]    │
│  ③ get_calculator_info("rcri") → params, references        │
│  ④ calculate("rcri", {...params})                           │
├─────────────────────────────────────────────────────────────┤
│  Path B: Context-based                                       │
│  ① list_contexts() → ["preoperative_assessment", ...]      │
│  ② list_by_context("preoperative_assessment") → [tools]    │
│  ③ get_calculator_info("asa_physical_status")              │
│  ④ calculate("asa_physical_status", {...params})            │
├─────────────────────────────────────────────────────────────┤
│  Path C: Quick Search (Quick keyword search)                 │
│  ① search_calculators("sepsis") → [sofa_score, qsofa, ...] │
│  ② get_calculator_info("sofa_score")                        │
│  ③ calculate("sofa_score", {...params})                     │
└─────────────────────────────────────────────────────────────┘
```

**Every step returns `next_step` hints, so the Agent never gets lost!**

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
- 🎯 **Token Efficient**: Only 10 tools instead of 75+ in context
- 🔍 **Discovery First**: Use discovery tools to find the right calculator
- 📖 **Self-Documenting**: `get_calculator_info()` shows exact params needed

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

### Discovery MCP Tools

| Tool | Purpose |
|------|---------|
| `search_calculators(keyword)` | Keyword search |
| `list_by_specialty(specialty)` | Filter by medical specialty |
| `list_by_context(context)` | Filter by clinical context |
| `list_calculators()` | List all available calculators |
| `get_calculator_info(tool_id)` | Get full metadata for a tool |
| `list_specialties()` | List available specialties |
| `list_contexts()` | List available clinical contexts |

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

> **MCP Primitives**: 82 Tools + 5 Prompts + 4 Resources
>
> **Current Stats**: 82 Tools | 1540+ Tests | 92% Coverage | Phase 19 Complete ✅
>
> 📋 **[See Full Roadmap →](ROADMAP.md)** | **[Contributing Guide →](CONTRIBUTING.md)**

### 📑 Quick Navigation

| Specialty | Count | Jump To |
|-----------|-------|---------|
| Anesthesiology / Preoperative | 9 | [→ Jump](#-anesthesiology--preoperative) |
| Critical Care / ICU | 8 | [→ Jump](#-critical-care--icu) |
| Pediatrics | 9 | [→ Jump](#-pediatrics) |
| Obstetrics | 2 | [→ Jump](#-obstetrics) |
| Nephrology | 2 | [→ Jump](#-nephrology) |
| Pulmonology | 6 | [→ Jump](#-pulmonology) |
| Cardiology | 8 | [→ Jump](#-cardiology) |
| Infectious Disease | 4 | [→ Jump](#-infectious-disease) |
| Emergency Medicine / Trauma | 5 | [→ Jump](#-emergency-medicine) |
| Hepatology / GI | 6 | [→ Jump](#-hepatology--gi) |
| Acid-Base / Metabolic | 7 | [→ Jump](#-acid-base--metabolic) |
| Hematology | 1 | [→ Jump](#-hematology) |
| Neurology | 7 | [→ Jump](#-neurology) |
| General Tools | 4 | [→ Jump](#-general-tools) |
| Discovery Tools | 7 | [→ Jump](#-discovery-tools) |
| Prompts | 5 | [→ Jump](#-prompts) |

---

### Calculators (75 tools)

#### 🏥 Anesthesiology / Preoperative

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `calculate_asa_physical_status` | ASA-PS | Physical status classification | Mayhew 2019 |
| `calculate_mallampati` | Mallampati | Airway assessment | Mallampati 1985 |
| `calculate_rcri` | RCRI (Lee Index) | Cardiac risk non-cardiac surgery | Lee 1999 |
| `calculate_mabl` | MABL | Maximum allowable blood loss | Gross 1983 |
| `calculate_transfusion_volume` | Transfusion Calc | Blood product volume calculation | Roseff 2002 |
| `calculate_caprini_vte` | Caprini VTE | Surgical VTE risk assessment | Caprini 2005 |
| `calculate_apfel_ponv` | Apfel Score 🆕 | PONV risk prediction | Apfel 1999 |
| `calculate_stop_bang` | STOP-BANG 🆕 | OSA screening questionnaire | Chung 2008 |
| `calculate_aldrete_score` | Aldrete Score 🆕 | PACU recovery assessment | Aldrete 1970 |

[↑ Back to Navigation](#-quick-navigation)

#### 🩺 Critical Care / ICU

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `calculate_apache_ii` | APACHE II | ICU mortality prediction | Knaus 1985 |
| `calculate_sofa` | SOFA Score | Organ dysfunction (Sepsis-3) | Vincent 1996, Singer 2016 |
| `calculate_sofa2` | **SOFA-2 (2025)** 🆕 | Updated organ dysfunction (3.3M pts) | Ranzani JAMA 2025 |
| `calculate_qsofa` | qSOFA | Bedside sepsis screening | Singer 2016 (Sepsis-3) |
| `calculate_news2` | NEWS2 | Clinical deterioration | RCP 2017 |
| `calculate_gcs` | Glasgow Coma Scale | Consciousness assessment | Teasdale 1974 |
| `calculate_rass` | RASS | Sedation/agitation | Sessler 2002 |
| `calculate_cam_icu` | CAM-ICU | ICU delirium screening | Ely 2001 |

**SOFA-2 (2025 Update)**: New P/F thresholds (300/225/150/75), updated platelet thresholds (150/100/80/50), combined NE+Epi dosing, ECMO and RRT criteria. AUROC 0.79.

[↑ Back to Navigation](#-quick-navigation)

#### 👶 Pediatrics

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `calculate_apgar_score` | APGAR Score 🆕 | Newborn assessment (1, 5, 10 min) | Apgar 1953, AAP 2015 |
| `calculate_pews` | PEWS 🆕 | Pediatric Early Warning Score | Parshuram 2009 |
| `calculate_pediatric_sofa` | pSOFA 🆕 | Pediatric organ dysfunction (sepsis) | Matics 2017 |
| `calculate_pim3` | PIM3 🆕 | PICU mortality prediction | Straney 2013 |
| `calculate_pediatric_gcs` | Pediatric GCS 🆕 | Age-adapted consciousness scale | Reilly 1988 |
| `calculate_pediatric_drug_dose` | Pediatric Dosing | Weight-based drug dosing | Lexicomp, Anderson 2017 |
| `calculate_mabl` | MABL | Maximum allowable blood loss | Miller's Anesthesia |
| `calculate_transfusion_volume` | Transfusion Volume | Blood product volume calculation | AABB |
| `calculate_body_surface_area` | BSA | Body Surface Area (Mosteller) | Mosteller 1987 |

[↑ Back to Navigation](#-quick-navigation)

#### � Obstetrics

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|------------|
| `calculate_bishop_score` | Bishop Score 🆕 | Cervical ripening for labor induction | Bishop 1964 |
| `calculate_ballard_score` | Ballard Score 🆕 | Newborn gestational age assessment | Ballard 1991 |

[↑ Back to Navigation](#-quick-navigation)

#### �🫘 Nephrology

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `calculate_ckd_epi_2021` | CKD-EPI 2021 | eGFR (race-free) | Inker 2021 |
| `calculate_kdigo_aki` | KDIGO AKI | Acute kidney injury staging | KDIGO 2012 |

[↑ Back to Navigation](#-quick-navigation)

#### 🫁 Pulmonology

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `calculate_curb65` | CURB-65 | Pneumonia severity & disposition | Lim 2003 |
| `calculate_psi_port` | PSI/PORT | CAP mortality prediction | Fine 1997 |
| `calculate_ideal_body_weight` | IBW (Devine) | Ventilator tidal volume (ARDSNet) | Devine 1974, ARDSNet 2000 |
| `calculate_pf_ratio` | P/F Ratio | ARDS Berlin classification | ARDS Task Force 2012 |
| `calculate_rox_index` | ROX Index | HFNC failure prediction | Roca 2016 |
| `calculate_spesi` | sPESI 🆕 | Simplified PESI for PE 30-day mortality (ESC Class I) | Jiménez 2010 |

[↑ Back to Navigation](#-quick-navigation)

#### ❤️ Cardiology

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `calculate_chads2_vasc` | CHA₂DS₂-VASc | AF stroke risk for anticoagulation | Lip 2010 |
| `calculate_chads2_va` | CHA₂DS₂-VA (2024 ESC) | AF stroke risk (sex-neutral) | Van Gelder 2024 |
| `calculate_has_bled` | HAS-BLED | AF bleeding risk (modifiable factors) | Pisters 2010, ESC 2024 |
| `calculate_heart_score` | HEART Score | Chest pain risk stratification | Six 2008 |
| `calculate_corrected_qt` | Corrected QT (QTc) | QT interval correction for drug safety | Bazett 1920, ESC 2015 |
| `calculate_grace_score` | GRACE Score | ACS mortality risk stratification | Fox 2006 |
| `calculate_acef_ii` | ACEF II Score | Cardiac surgery mortality risk | Ranucci 2018 |
| `calculate_timi_stemi` | TIMI STEMI 🆕 | STEMI 30-day mortality prediction | Morrow 2000 |

[↑ Back to Navigation](#-quick-navigation)

#### � Infectious Disease

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|------------|
| `calculate_mascc_score` | MASCC Score 🆕 | Febrile neutropenia risk assessment | Klastersky 2000 |
| `calculate_pitt_bacteremia_score` | Pitt Bacteremia 🆕 | Bacteremia prognosis & mortality | Paterson 2004 |
| `calculate_centor_score` | Centor/McIsaac Score 🆕 | Streptococcal pharyngitis risk | Centor 1981, McIsaac 1998 |
| `calculate_cpis` | CPIS 🆕 | Clinical Pulmonary Infection Score (VAP) | Pugin 1991 |

[↑ Back to Navigation](#-quick-navigation)

#### �🩸 Hematology

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `calculate_4ts_hit` | 4Ts HIT Score | Heparin-induced thrombocytopenia | Lo 2006, Cuker 2012 |

[↑ Back to Navigation](#-quick-navigation)

#### 🧠 Neurology

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `calculate_nihss` | NIHSS | NIH Stroke Scale - stroke severity | Brott 1989 |
| `calculate_abcd2` | ABCD2 Score | TIA 7-day stroke risk prediction | Johnston 2007 |
| `calculate_modified_rankin_scale` | Modified Rankin Scale | Post-stroke disability assessment | van Swieten 1988 |
| `calculate_hunt_hess` | Hunt & Hess Scale 🆕 | SAH clinical grading for prognosis & surgical timing | Hunt & Hess 1968 |
| `calculate_fisher_grade` | Fisher Grade 🆕 | SAH CT grading for vasospasm prediction | Fisher 1980, Frontera 2006 |
| `calculate_four_score` | FOUR Score 🆕 | Coma evaluation (E/M/B/R, 0-16) | Wijdicks 2005 |
| `calculate_ich_score` | ICH Score 🆕 | Intracerebral hemorrhage 30-day mortality | Hemphill 2001 |

[↑ Back to Navigation](#-quick-navigation)

#### 🔬 General Tools

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `calculate_body_surface_area` | Body Surface Area 🆕 | BSA for chemo/burn/cardiac dosing | Du Bois 1916, Mosteller 1987 |
| `calculate_cockcroft_gault` | Cockcroft-Gault CrCl 🆕 | Creatinine clearance for drug dosing | Cockcroft-Gault 1976 |
| `calculate_corrected_calcium` | Corrected Calcium 🆕 | Albumin-corrected calcium | Payne 1973 |
| `calculate_parkland_formula` | Parkland Formula 🆕 | Burn fluid resuscitation | Baxter 1968 |

[↑ Back to Navigation](#-quick-navigation)

#### 🚑 Emergency Medicine / Trauma

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `calculate_wells_dvt` | Wells DVT | DVT probability assessment | Wells 2003 |
| `calculate_wells_pe` | Wells PE | PE probability assessment | Wells 2000 |
| `calculate_shock_index` | Shock Index (SI) | Rapid hemodynamic assessment | Allgöwer 1967 |
| `calculate_iss` | ISS 🆕 | Injury Severity Score - trauma mortality prediction | Baker 1974 |
| `calculate_tbsa` | TBSA 🆕 | Burns surface area (Rule of Nines / Lund-Browder) | Wallace 1951, Lund 1944 |

[↑ Back to Navigation](#-quick-navigation)

#### 🟤 Hepatology / GI

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `calculate_meld_score` | MELD Score | End-stage liver disease mortality | Kamath 2001 |
| `calculate_child_pugh` | Child-Pugh | Cirrhosis severity staging | Pugh 1973 |
| `calculate_rockall_score` | Rockall Score 🆕 | Upper GI bleeding risk (mortality/rebleeding) | Rockall 1996 |
| `calculate_fib4_index` | FIB-4 Index 🆕 | Liver fibrosis non-invasive assessment | Sterling 2006 |
| `calculate_glasgow_blatchford` | Glasgow-Blatchford 🆕 | UGIB pre-endoscopy risk (ESGE Class I) | Blatchford 2000 |
| `calculate_aims65` | AIMS65 🆕 | UGIB in-hospital mortality prediction | Saltzman 2011 |

[↑ Back to Navigation](#-quick-navigation)

#### 🧪 Acid-Base / Metabolic

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `calculate_anion_gap` | Anion Gap | Metabolic acidosis differential | Kraut 2007, Figge 1998 |
| `calculate_delta_ratio` | Delta Ratio (Delta Gap) | Mixed acid-base disorder detection | Wrenn 1990, Rastegar 2007 |
| `calculate_corrected_sodium` | Corrected Sodium | True sodium in hyperglycemia | Katz 1973, Hillier 1999 |
| `calculate_winters_formula` | Winter's Formula | Expected PaCO₂ in metabolic acidosis | Albert 1967, Narins 1980 |
| `calculate_osmolar_gap` | Osmolar Gap | Toxic alcohol screening | Hoffman 1993, Lynd 2008 |
| `calculate_free_water_deficit` | Free Water Deficit | Hypernatremia treatment planning | Adrogue 2000, Sterns 2015 |
| `calculate_aa_gradient` | A-a Gradient | Alveolar-arterial O₂ gradient | Kanber 1968, West 2016 |

[↑ Back to Navigation](#-quick-navigation)

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

# 3. Run tests
uv run pytest

# 4. Run MCP server in dev mode
uv run mcp dev src/main.py
```

---

## 🧪 Testing

### Testing Strategy

We maintain a high-quality codebase with over **1540+ tests** and **90% code coverage**.

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
uv run mypy --strict src tests

# Run linter
uv run ruff check src tests

# Auto-fix linting issues
uv run ruff check --fix src tests
```

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
