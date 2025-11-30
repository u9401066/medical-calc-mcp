# Medical Calculator MCP Server 🏥

A DDD-architected medical calculator service providing clinical scoring tools for AI Agent integration via MCP (Model Context Protocol).

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP SDK](https://img.shields.io/badge/MCP-FastMCP-green.svg)](https://github.com/modelcontextprotocol/python-sdk)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

## 🎯 Features

- **MCP Integration**: Native FastMCP SDK for AI agent integration
- **Tool Discovery**: Intelligent tool search via keywords and specialties
- **DDD Architecture**: Clean Onion Architecture with domain-driven design
- **Original Content**: All formulas cite original research papers (Vancouver style)
- **Type Safe**: Full Python type hints with dataclass entities

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│           infrastructure/                    │
│         (MCP Server, FastMCP)                │
└──────────────────────┬──────────────────────┘
                       │ depends on
                       ▼
┌─────────────────────────────────────────────┐
│            application/                      │
│         (Use Cases, DTOs)                    │
└──────────────────────┬──────────────────────┘
                       │ depends on
                       ▼
┌─────────────────────────────────────────────┐
│              domain/                         │
│   (Entities, Services, Value Objects)        │
│          【Core, Zero Dependencies】          │
└─────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/u9401066/medical-calc-mcp.git
cd medical-calc-mcp

# Install dependencies (requires Python 3.11+)
pip install -r requirements.txt
```

### Run MCP Server

```bash
# Start MCP server (stdio transport)
python -m src.infrastructure.mcp.server
```

### Test with MCP Inspector

```bash
# Install MCP CLI tools
pip install "mcp[cli]"

# Run with inspector
mcp dev src/infrastructure/mcp/server.py
```

## 🔧 Available MCP Tools

### Calculators (6 tools)

| Tool | Purpose | Specialty |
|------|---------|-----------|
| `calculate_ckd_epi_2021` | eGFR calculation (2021 race-free equation) | Nephrology |
| `calculate_mallampati_score` | Airway assessment for intubation | Anesthesiology |
| `calculate_qsofa` | Quick sepsis screening | Critical Care |
| `calculate_meld_na` | Liver disease severity | Hepatology |
| `calculate_glasgow_coma_scale` | Consciousness level assessment | Neurology |
| `calculate_heart_score` | Chest pain risk stratification | Cardiology |

### Discovery Tools (2 tools)

| Tool | Purpose |
|------|---------|
| `discover_tools` | Search calculators by keyword |
| `list_calculators` | List all available calculators |

## 📖 Usage Examples

### CKD-EPI 2021 (eGFR)

```json
// Input
{
  "age": 65,
  "sex": "female",
  "serum_creatinine": 1.2
}

// Output
{
  "score_name": "CKD-EPI 2021",
  "result": 67.1,
  "unit": "mL/min/1.73m²",
  "interpretation": {
    "summary": "Mildly decreased kidney function (G2)",
    "stage": "G2",
    "recommendation": "Monitor kidney function annually"
  }
}
```

### Tool Discovery

```json
// discover_tools("airway")
{
  "count": 1,
  "tools": [
    {
      "tool_id": "mallampati_score",
      "name": "Mallampati Score",
      "purpose": "Airway assessment for predicting difficult intubation"
    }
  ]
}
```

## 🔍 Tool Discovery Keys

Each calculator has metadata for intelligent selection:

### Low Level Key (Precise Selection)
- `tool_id`: Unique identifier (e.g., "ckd_epi_2021")
- `name`: Human-readable name
- `purpose`: What it calculates
- `input_params`: Required parameters

### High Level Key (Exploration)
- `specialties`: Medical specialties
- `conditions`: Related diseases/conditions
- `clinical_contexts`: Use cases (staging, risk_stratification)
- `keywords`: Search keywords

## 📜 References

All calculators cite original research papers. See [references/README.md](references/README.md) for complete citations.

## 📄 License

Apache 2.0

## 👨‍💻 Development

### Project Status

- ✅ Phase 1: Foundation Layer (DDD architecture)
- ✅ Phase 2: 6 Example Calculators
- ✅ Phase 3: MCP Integration (FastMCP)
- ⏳ Phase 4: More Calculators
- ⏳ Phase 5: Validation Layer
- ⏳ Phase 6: Additional Transports (HTTP, WebSocket)

### Requirements

- Python 3.11+ (MCP SDK requirement)
- Dependencies: `mcp[cli]`, `pydantic`
