# Quick Start

Get up and running with Medical-Calc-MCP in minutes.

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Installation

### Option 1: Clone Repository

```bash
git clone https://github.com/u9401066/medical-calc-mcp.git
cd medical-calc-mcp
uv sync
```

### Option 2: Docker

```bash
docker pull ghcr.io/u9401066/medical-calc-mcp:latest
```

## Running the Server

### MCP Mode (for AI Agents)

```bash
uv run python -m src.main
```

### REST API Mode

```bash
uv run python -m src.rest_server
```

Server runs at `http://localhost:8000`

## Your First Calculation

### Using MCP Tools

Once connected to an AI agent, you can use natural language:

> "Calculate the CKD-EPI eGFR for a 65-year-old male with creatinine 1.2 mg/dL"

### Using REST API

```bash
curl -X POST http://localhost:8000/api/v1/calculate/ckd_epi_2021 \
  -H "Content-Type: application/json" \
  -d '{"serum_creatinine": 1.2, "age": 65, "sex": "male"}'
```

## Next Steps

- [Installation Details](installation.md) - Advanced setup options
- [Configuration](configuration.md) - Environment variables
- [Calculator Reference](../calculators/index.md) - Browse all 121 calculators
