# Medical Calculator MCP Server 🏥

A DDD-architected medical calculator service providing clinical scoring tools for AI Agent integration via MCP (Model Context Protocol).

為 AI Agent 提供醫學計算工具的 MCP 伺服器，採用 DDD 洋蔥架構設計。

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP SDK](https://img.shields.io/badge/MCP-FastMCP-green.svg)](https://github.com/modelcontextprotocol/python-sdk)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Architecture](https://img.shields.io/badge/architecture-DDD%20Onion-purple.svg)](#-architecture--架構)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

---

## 📖 Table of Contents | 目錄

- [Features | 特色功能](#-features--特色功能)
- [Why This Project? | 為什麼需要這個專案？](#-why-this-project--為什麼需要這個專案)
- [Architecture | 架構](#-architecture--架構)
- [Quick Start | 快速開始](#-quick-start--快速開始)
- [Tool Discovery | 工具探索](#-tool-discovery--工具探索)
- [Available Tools | 可用工具](#-available-tools--可用工具)
- [Usage Examples | 使用範例](#-usage-examples--使用範例)
- [References | 參考文獻](#-references--參考文獻)
- [Development | 開發指南](#-development--開發指南)

---

## 🎯 Features | 特色功能

### English

- **🔌 MCP Native Integration**: Built with FastMCP SDK for seamless AI agent integration
- **🔍 Intelligent Tool Discovery**: Two-level key system (Low/High Level) for smart tool selection
- **🏗️ Clean DDD Architecture**: Onion architecture with clear separation of concerns
- **📚 Evidence-Based**: All formulas cite original peer-reviewed research papers (Vancouver style)
- **🔒 Type Safe**: Full Python type hints with dataclass entities
- **🌐 Bilingual**: Chinese/English documentation and tool descriptions

### 中文

- **🔌 MCP 原生整合**：使用 FastMCP SDK，與 AI Agent 無縫整合
- **🔍 智慧工具探索**：雙層 Key 系統（Low/High Level），讓 AI 智慧選擇工具
- **🏗️ 乾淨 DDD 架構**：洋蔥式架構，關注點分離清晰
- **📚 循證醫學**：所有公式均引用原始同儕審查論文（Vancouver 格式）
- **🔒 型別安全**：完整 Python 型別提示，使用 dataclass 實體
- **🌐 雙語支援**：中英文文檔與工具說明

---

## 🤔 Why This Project? | 為什麼需要這個專案？

### The Problem | 問題

When AI agents (like Claude, GPT) need to perform medical calculations, they face challenges:

當 AI Agent（如 Claude、GPT）需要進行醫學計算時，會遇到以下挑戰：

1. **Hallucination Risk | 幻覺風險**: LLMs may generate incorrect formulas or values
2. **Version Confusion | 版本混淆**: Multiple versions of same calculator (e.g., MELD vs MELD-Na vs MELD 3.0)
3. **No Discovery Mechanism | 缺乏探索機制**: How does an agent know which tool to use for "cardiac risk assessment"?

### The Solution | 解決方案

This project provides:

本專案提供：

| Feature | Description | 說明 |
|---------|-------------|------|
| **Validated Calculators** | Peer-reviewed, tested formulas | 經同儕審查、測試驗證的公式 |
| **Tool Discovery** | AI can search by specialty, condition, or clinical question | AI 可依專科、病況或臨床問題搜尋 |
| **MCP Protocol** | Standard protocol for AI-tool communication | AI-工具通訊的標準協定 |
| **Paper References** | Every calculator cites original research | 每個計算器都引用原始研究 |

---

## 🏗️ Architecture | 架構

```
┌─────────────────────────────────────────────────────────────┐
│                    infrastructure/                           │
│              (MCP Server, FastMCP, Transport)                │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  MCP Tools: discover_tools, calculate_*, list_*     │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────────┘
                           │ depends on
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     application/                             │
│                  (Use Cases, DTOs)                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  CalculateUseCase, DiscoverToolsUseCase             │    │
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

### Key Design Decisions | 關鍵設計決策

| Decision | Rationale | 決策理由 |
|----------|-----------|----------|
| **DDD Onion** | Domain logic isolated from infrastructure | 領域邏輯與基礎設施隔離 |
| **FastMCP** | Native Python MCP SDK, simple decorator-based API | 原生 Python MCP SDK，簡潔裝飾器 API |
| **Dataclasses** | Immutable, type-safe entities | 不可變、型別安全的實體 |
| **Two-Level Keys** | Enable both precise lookup and exploratory discovery | 同時支援精確查找與探索式發現 |

---

## 🚀 Quick Start | 快速開始

### Prerequisites | 前置需求

- Python 3.11+ (required by MCP SDK)
- pip or uv package manager

### Installation | 安裝

```bash
# Clone repository | 複製儲存庫
git clone https://github.com/u9401066/medical-calc-mcp.git
cd medical-calc-mcp

# Create virtual environment (recommended) | 建立虛擬環境（建議）
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies | 安裝依賴
pip install -r requirements.txt
```

### Run MCP Server | 執行 MCP 伺服器

```bash
# Start MCP server (stdio transport) | 啟動 MCP 伺服器（stdio 傳輸）
python -m src.infrastructure.mcp.server

# Or with MCP development inspector | 或使用 MCP 開發檢查器
pip install "mcp[cli]"
mcp dev src/infrastructure/mcp/server.py
```

### Configure with Claude Desktop | 與 Claude Desktop 整合

Add to your `claude_desktop_config.json`:

將以下內容加入 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "medical-calc": {
      "command": "python",
      "args": ["-m", "src.infrastructure.mcp.server"],
      "cwd": "/path/to/medical-calc-mcp"
    }
  }
}
```

---

## 🔍 Tool Discovery | 工具探索

The **Two-Level Key System** is the core innovation of this project:

**雙層 Key 系統**是本專案的核心創新：

### Low Level Key | 低階 Key（精準選擇）

For **precise tool selection** when you know exactly what you need:

用於**精確工具選擇**，當你確切知道需要什麼時：

```python
LowLevelKey(
    tool_id="ckd_epi_2021",           # Unique identifier | 唯一識別碼
    name="CKD-EPI 2021",              # Human-readable name | 人類可讀名稱
    purpose="Calculate eGFR",          # What it does | 功能描述
    input_params=["age", "sex", "creatinine"],  # Required inputs | 必要輸入
    output_type="eGFR with CKD staging"         # Output format | 輸出格式
)
```

### High Level Key | 高階 Key（探索發現）

For **intelligent discovery** when exploring options:

用於**智慧探索**，當探索可用選項時：

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

### Discovery MCP Tools | 探索 MCP 工具

| Tool | Purpose | 用途 |
|------|---------|------|
| `discover_tools(query)` | Search by keyword, specialty, or clinical question | 依關鍵字、專科或臨床問題搜尋 |
| `list_calculators()` | List all available calculators | 列出所有可用計算器 |
| `get_calculator_info(tool_id)` | Get full metadata for a specific tool | 取得特定工具的完整 metadata |

### Example: AI Agent Workflow | 範例：AI Agent 工作流程

```
User: "I need to assess this patient's cardiac risk before surgery"
用戶：「我需要評估這位病患術前的心臟風險」

Agent: discover_tools("cardiac risk surgery")
       → Returns: RCRI (Lee Index), ASA Physical Status, ...

Agent: get_calculator_info("rcri")
       → Returns: Full metadata with input params, references

Agent: calculate_rcri(high_risk_surgery=True, ischemic_heart_disease=True, ...)
       → Returns: Score, risk percentage, recommendations
```

---

## 🔧 Available Tools | 可用工具

### Calculators | 計算器 (6 tools)

| Tool ID | Name | Specialty | Purpose |
|---------|------|-----------|---------|
| `calculate_ckd_epi_2021` | CKD-EPI 2021 | Nephrology | eGFR calculation (2021 race-free equation) |
| `calculate_asa_physical_status` | ASA-PS | Anesthesiology | Preoperative physical status classification |
| `calculate_mallampati` | Mallampati | Anesthesiology | Airway assessment for difficult intubation |
| `calculate_rcri` | RCRI (Lee Index) | Cardiology | Cardiac risk for non-cardiac surgery |
| `calculate_apache_ii` | APACHE II | Critical Care | ICU mortality prediction |
| `calculate_rass` | RASS | Critical Care | Sedation/agitation assessment |

### Discovery Tools | 探索工具 (3 tools)

| Tool | Description | 說明 |
|------|-------------|------|
| `discover_tools` | Free-text search across all metadata | 跨所有 metadata 的自由文字搜尋 |
| `list_calculators` | List all registered calculators | 列出所有已註冊的計算器 |
| `get_calculator_info` | Get detailed info for one calculator | 取得單一計算器的詳細資訊 |

### Resources | 資源

| Resource URI | Description |
|--------------|-------------|
| `calculator://list` | Markdown list of all calculators |
| `calculator://{tool_id}/references` | Paper references for a calculator |

---

## 📖 Usage Examples | 使用範例

### Example 1: CKD-EPI 2021 (eGFR)

**Input | 輸入:**
```json
{
  "serum_creatinine": 1.2,
  "age": 65,
  "sex": "female"
}
```

**Output | 輸出:**
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

### Example 2: Tool Discovery | 工具探索

**Query | 查詢:** `discover_tools("difficult airway")`

**Output | 輸出:**
```json
{
  "query": "difficult airway",
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

### Example 3: RCRI Cardiac Risk | RCRI 心臟風險

**Input | 輸入:**
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

**Output | 輸出:**
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

## 📜 References | 參考文獻

All calculators cite original peer-reviewed research. See [references/README.md](references/README.md) for complete citations.

所有計算器均引用原始同儕審查研究。完整引用請見 [references/README.md](references/README.md)。

### Citation Format | 引用格式

We use **Vancouver style** citations:

我們使用 **Vancouver 格式**引用：

```
Inker LA, Eneanya ND, Coresh J, et al. New Creatinine- and Cystatin C-Based 
Equations to Estimate GFR without Race. N Engl J Med. 2021;385(19):1737-1749. 
doi:10.1056/NEJMoa2102953
```

---

## 👨‍💻 Development | 開發指南

### Project Status | 專案狀態

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | ✅ Complete | Foundation Layer (DDD architecture) |
| Phase 2 | ✅ Complete | 6 Example Calculators |
| Phase 3 | ✅ Complete | MCP Integration (FastMCP) |
| Phase 4 | ⏳ Planned | More Calculators (from nobra_calculator) |
| Phase 5 | ⏳ Planned | Validation Layer & Error Handling |
| Phase 6 | ⏳ Planned | Additional Transports (HTTP, WebSocket) |

### Contributing | 貢獻

PRs are welcome! To add a new calculator:

歡迎 PR！要新增計算器：

1. Create calculator in `src/domain/services/calculators/`
2. Define `LowLevelKey` and `HighLevelKey` in the calculator
3. Add paper references with DOI/PMID
4. Register in `CALCULATORS` list
5. Add MCP tool wrapper in `server.py`

### Requirements | 需求

- Python 3.11+ (MCP SDK requirement)
- `mcp[cli]` - MCP Python SDK with FastMCP
- `pydantic` - Data validation

### Testing | 測試

```bash
# Run with MCP inspector | 使用 MCP 檢查器執行
mcp dev src/infrastructure/mcp/server.py

# Test specific calculator | 測試特定計算器
python -c "from src.domain.services.calculators import CkdEpi2021Calculator; \
           calc = CkdEpi2021Calculator(); \
           print(calc.calculate(age=65, sex='female', serum_creatinine=1.2))"
```

---

## 📄 License

Apache 2.0 - See [LICENSE](LICENSE)

---

## 🙏 Acknowledgments | 致謝

- [Model Context Protocol](https://modelcontextprotocol.io/) - Anthropic's open protocol for AI-tool communication
- [FastMCP](https://github.com/modelcontextprotocol/python-sdk) - Python SDK for MCP
- Original authors of all cited medical calculators and scoring systems
