# Medical Calculator MCP Server 🏥

A DDD-architected medical calculator service providing 200+ clinical scoring tools for AI Agent integration via MCP (Model Context Protocol).

## 🎯 Features

- **Tool Discovery**: Intelligent tool selection via Low/High Level Keys
- **MCP Integration**: Native MCP protocol support for AI agents
- **REST API**: Optional FastAPI server for web/system integration
- **Python Library**: Direct import for Python projects
- **Original Content**: All formulas cite original research papers

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│           infrastructure/                    │
│    (MCP Server, API Server, Persistence)     │
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

## 🔍 Tool Discovery

Each calculator has two-level keys for intelligent selection:

### Low Level Key (Precise Selection)
- `tool_id`: Unique identifier (e.g., "ckd_epi_2021")
- `name`: Human-readable name
- `purpose`: What it calculates
- `input_params`: Required parameters
- `output_type`: Result format

### High Level Key (Exploration)
- `specialties`: Medical specialties (nephrology, cardiology, etc.)
- `conditions`: Related diseases/conditions
- `clinical_contexts`: Use cases (staging, risk_stratification, drug_dosing)
- `clinical_questions`: Natural language questions it answers
- `icd10_codes`: Related ICD-10 codes
- `keywords`: Search keywords

## 🚀 Usage

### As MCP Server (for AI Agents)
```bash
python -m src.infrastructure.mcp.server
```

### As REST API
```bash
python -m src.infrastructure.api.server
```

### As Python Library
```python
from src.domain.services.calculators import CkdEpi2021Calculator

calc = CkdEpi2021Calculator()
result = calc.calculate(age=65, sex="female", serum_creatinine=1.2)
print(result.interpretation)
```

## 📋 Available Tools

| Specialty | Tools |
|-----------|-------|
| Nephrology | CKD-EPI 2021, MDRD, Cockcroft-Gault, ... |
| Cardiology | CHA₂DS₂-VASc, HAS-BLED, HEART Score, ... |
| Pulmonology | CURB-65, PSI, A-a Gradient, ... |
| Emergency | APACHE II, SOFA, qSOFA, ... |
| ... | ... |

## 📜 Attribution & Copyright

- **All formulas cite original research papers** (Vancouver style)
- **All interpretation text is original content**
- **No commercial medical calculator service content used**

## 📄 License

Apache 2.0

## 👨‍💻 Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for development guide and roadmap.
