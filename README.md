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

### Key Design Decisions | 關鍵設計決策

| Decision | Rationale | 決策理由 |
|----------|-----------|----------|
| **DDD Onion** | Domain logic isolated from infrastructure | 領域邏輯與基礎設施隔離 |
| **FastMCP** | Native Python MCP SDK, simple decorator-based API | 原生 Python MCP SDK，簡潔裝飾器 API |
| **Dataclasses** | Immutable, type-safe entities | 不可變、型別安全的實體 |
| **Two-Level Keys** | Enable both precise lookup and exploratory discovery | 同時支援精確查找與探索式發現 |
| **Layered Validation** | 3-layer validation (MCP/Application/Domain) | 三層驗證架構 |

### Validation Architecture | 驗證架構

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: MCP (Infrastructure)                               │
│  └── Pydantic + JSON Schema: Type validation                │
│      (Automatic from Annotated[type, Field(description)])   │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: Application (Use Case)                             │
│  └── ParameterValidator: Pre-calculation validation         │
│      (22 parameter specs with valid ranges)                 │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: Domain (Calculator)                                │
│  └── Medical logic validation                                │
│      (Clinical rules, formula constraints)                  │
└─────────────────────────────────────────────────────────────┘
```

**Domain validation module** (`src/domain/validation/`):
- `rules.py`: Base classes (RangeRule, EnumRule, TypeRule, CustomRule)
- `parameter_specs.py`: 22 medical parameter specifications
- `validators.py`: ParameterValidator with `validate_params()` function

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

### Discovery Philosophy | 探索理念

When an AI agent needs a medical calculator, it uses **Hierarchical Navigation**:

當 AI Agent 需要醫學計算工具時，使用**階層式導航**：

```
┌─────────────────────────────────────────────────────────────┐
│  Path A: Specialty-based (依專科)                           │
│  ① list_specialties() → ["critical_care", "anesthesiology"]│
│  ② list_by_specialty("anesthesiology") → [tool_id, ...]    │
│  ③ get_calculator_info("rcri") → params, references        │
│  ④ calculate_rcri(...)                                      │
├─────────────────────────────────────────────────────────────┤
│  Path B: Context-based (依臨床情境)                          │
│  ① list_contexts() → ["preoperative_assessment", ...]      │
│  ② list_by_context("preoperative_assessment") → [tools]    │
│  ③ get_calculator_info("asa_physical_status")              │
│  ④ calculate_asa_physical_status(...)                       │
├─────────────────────────────────────────────────────────────┤
│  Path C: Quick Search (快速搜尋 - 已知關鍵字)                 │
│  ① search_calculators("sepsis") → [sofa_score, qsofa, ...] │
│  ② get_calculator_info("sofa_score")                        │
│  ③ calculate_sofa(...)                                      │
└─────────────────────────────────────────────────────────────┘
```

**每一步回傳都包含 `next_step` 提示，Agent 不會迷路！**

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

### 🔑 Key Feature: Multi-Specialty Tools | 關鍵特性：跨專科工具

**One tool can belong to multiple High Level categories!**

**一個工具可以屬於多個高階類別！**

Example: SOFA Score belongs to:

範例：SOFA 分數屬於：

| Category | Values | 值 |
|----------|--------|-----|
| Specialties | Critical Care, Emergency Medicine, Internal Medicine, Pulmonology | 重症、急診、內科、胸腔 |
| Conditions | Sepsis, Septic Shock, Organ Dysfunction, MODS | 敗血症、敗血性休克、器官衰竭 |
| Contexts | Severity Assessment, Prognosis, ICU Management, Diagnosis | 嚴重度評估、預後、ICU 管理、診斷 |

This means:
- Search "sepsis" → Returns SOFA, qSOFA, NEWS, ...
- Search "critical care" → Returns SOFA, APACHE II, RASS, GCS, CAM-ICU, ...
- Search "organ dysfunction" → Returns SOFA, ...

這表示：
- 搜尋 "sepsis" → 回傳 SOFA, qSOFA, NEWS, ...
- 搜尋 "critical care" → 回傳 SOFA, APACHE II, RASS, GCS, CAM-ICU, ...
- 搜尋 "organ dysfunction" → 回傳 SOFA, ...

### Discovery MCP Tools | 探索 MCP 工具

| Tool | Purpose | 用途 |
|------|---------|------|
| `discover_tools(query)` | Free text search | 自由文字搜尋 |
| `list_by_specialty(specialty)` | Filter by medical specialty | 依專科篩選 |
| `list_by_context(context)` | Filter by clinical context | 依臨床情境篩選 |
| `list_calculators()` | List all available calculators | 列出所有可用計算器 |
| `get_calculator_info(tool_id)` | Get full metadata for a tool | 取得工具的完整 metadata |
| `list_specialties()` | List available specialties | 列出可用專科 |
| `list_contexts()` | List available clinical contexts | 列出可用臨床情境 |

### Example: AI Agent Workflow | 範例：AI Agent 工作流程

```
User: "I need to assess this patient's cardiac risk before surgery"
用戶：「我需要評估這位病患術前的心臟風險」

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

### Example: ICU Sepsis Workup | 範例：ICU 敗血症評估

```
User: "Evaluate this ICU patient for sepsis"
用戶：「評估這位 ICU 病患是否有敗血症」

Agent: discover_tools("sepsis ICU")
       → Returns: SOFA, qSOFA, NEWS2, APACHE II

# Per Sepsis-3 guidelines:
# 依據 Sepsis-3 指引：

Agent: calculate_qsofa(respiratory_rate=24, systolic_bp=95, altered_mentation=True)
       → qSOFA = 3 (High risk, prompt evaluation needed)

Agent: calculate_sofa(pao2_fio2_ratio=200, platelets=80, bilirubin=2.5, ...)
       → SOFA = 8 (Sepsis confirmed if infection suspected, ≥2 point increase)
```

---

## 🔧 Available Tools | 可用工具

> **MCP Primitives**: 21 Tools + 5 Prompts + 4 Resources

### Calculators | 計算器 (14 tools)

#### Anesthesiology / Preoperative | 麻醉科 / 術前評估

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `calculate_asa_physical_status` | ASA-PS | Physical status classification | Mayhew 2019 |
| `calculate_mallampati` | Mallampati | Airway assessment | Mallampati 1985 |
| `calculate_rcri` | RCRI (Lee Index) | Cardiac risk non-cardiac surgery | Lee 1999 |
| `calculate_mabl` | MABL | Maximum allowable blood loss | Gross 1983 |
| `calculate_transfusion_volume` | Transfusion Calc | Blood product volume calculation | Roseff 2002 |

#### Critical Care / ICU | 重症加護

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `calculate_apache_ii` | APACHE II | ICU mortality prediction | Knaus 1985 |
| `calculate_sofa` | SOFA Score | Organ dysfunction (Sepsis-3) | Vincent 1996, Singer 2016 |
| `calculate_qsofa` | qSOFA | Bedside sepsis screening | Singer 2016 (Sepsis-3) |
| `calculate_news2` | NEWS2 | Clinical deterioration | RCP 2017 |
| `calculate_gcs` | Glasgow Coma Scale | Consciousness assessment | Teasdale 1974 |
| `calculate_rass` | RASS | Sedation/agitation | Sessler 2002 |
| `calculate_cam_icu` | CAM-ICU | ICU delirium screening | Ely 2001 |

#### Pediatrics | 小兒科

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `calculate_pediatric_drug_dose` | Pediatric Dosing | Weight-based drug dosing | Lexicomp, Anderson 2017 |

#### Nephrology | 腎臟科

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `calculate_ckd_epi_2021` | CKD-EPI 2021 | eGFR (race-free) | Inker 2021 |

### Discovery Tools | 探索工具 (7 tools)

#### Step 1: Entry Points (起點)

| Tool | Description | 說明 |
|------|-------------|------|
| `list_specialties()` | 📋 List available specialties | 列出可用專科 (返回 next_step) |
| `list_contexts()` | 📋 List available clinical contexts | 列出可用臨床情境 (返回 next_step) |
| `list_calculators()` | 📋 List all registered calculators | 列出所有計算器 |

#### Step 2: Filter by Category (篩選)

| Tool | Description | 說明 |
|------|-------------|------|
| `list_by_specialty(specialty)` | Filter tools by medical specialty | 依專科篩選工具 |
| `list_by_context(context)` | Filter tools by clinical context | 依臨床情境篩選工具 |
| `search_calculators(keyword)` | 🔍 Quick keyword search | 快速關鍵字搜尋 |

#### Step 3: Get Details (取得詳情)

| Tool | Description | 說明 |
|------|-------------|------|
| `get_calculator_info(tool_id)` | 📖 Get params, references, examples | 取得參數、引用文獻、範例 |

### Resources | 資源

| Resource URI | Description |
|--------------|-------------|
| `calculator://list` | Markdown list of all calculators |
| `calculator://{tool_id}/references` | Paper references for a calculator |
| `calculator://{tool_id}/parameters` | Input parameter definitions |
| `calculator://{tool_id}/info` | Full calculator metadata |

### Prompts | 提示詞工作流程 (5 prompts)

Prompts provide guided multi-tool workflows for common clinical scenarios:

提示詞提供常見臨床情境的多工具引導工作流程：

| Prompt | Description | 說明 |
|--------|-------------|------|
| `sepsis_evaluation` | qSOFA → SOFA → RASS → CAM-ICU workflow | 敗血症評估流程 |
| `preoperative_risk_assessment` | ASA → RCRI → Mallampati workflow | 術前風險評估流程 |
| `icu_daily_assessment` | RASS → CAM-ICU → GCS → SOFA daily rounds | ICU 每日評估流程 |
| `pediatric_drug_dosing` | Weight-based dosing + MABL + transfusion | 兒科藥物劑量流程 |
| `acute_kidney_injury_assessment` | CKD-EPI + AKI staging workflow | 急性腎損傷評估流程 |

**Usage | 使用方式:**
```
# In MCP client, request a prompt:
prompt: sepsis_evaluation
→ Returns structured workflow with step-by-step guidance
```

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
| Phase 2 | ✅ Complete | 6 Example Calculators (CKD-EPI, ASA, Mallampati, RCRI, APACHE II, RASS) |
| Phase 3 | ✅ Complete | MCP Integration (FastMCP) with Tool Discovery |
| Phase 4 | ✅ Complete | ICU/ED Calculators (SOFA, qSOFA, NEWS, GCS, CAM-ICU) per Sepsis-3 |
| Phase 5 | ✅ Complete | Pediatric/Anesthesia (MABL, Transfusion, Pediatric Dosing) + Handler Modularization |
| Phase 5.5 | ✅ Complete | MCP Prompts (5 workflows) + Parameter Descriptions + Enhanced Errors |
| Phase 6 | ⏳ Planned | More Calculators (CURB-65, Wells Score, etc.) |
| Phase 7 | ✅ Complete | Validation Layer (Domain validation module, 22 parameter specs) |
| Phase 8 | ⏳ Planned | Additional Transports (HTTP, WebSocket) |

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
