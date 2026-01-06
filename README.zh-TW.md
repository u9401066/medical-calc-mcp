# Medical Calculator MCP Server 🏥 (繁體中文)

為 AI Agent 提供醫學計算工具的 MCP 伺服器，採用 DDD 洋蔥架構設計。

[English Version](README.md)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP SDK](https://img.shields.io/badge/MCP-FastMCP-green.svg)](https://github.com/modelcontextprotocol/python-sdk)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![CI](https://github.com/u9401066/medical-calc-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/u9401066/medical-calc-mcp/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/tests-1639%20passed-brightgreen.svg)](#-開發指南)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-orange.svg)](https://github.com/astral-sh/ruff)
[![Architecture](https://img.shields.io/badge/architecture-DDD%20Onion-purple.svg)](#-架構)

---

## 📖 目錄

- [特色功能](#-特色功能)
- [為什麼需要這個專案？](#-為什麼需要這個專案)
- [架構](#-架構)
- [快速開始](#-快速開始)
- [部署模式](#-部署模式) 🚀 NEW
- [Agent 整合](#-agent-整合) 🤖 NEW
- [Docker 部署](#-docker-部署--new) 🐳
- [HTTPS 部署](#-https-部署--new) 🔒 NEW
- [REST API 接口](#-rest-api-接口--new) 🌐 NEW
- [安全性](#-安全性--new) 🔐 NEW
- [工具探索](#-工具探索)
- [可用工具](#-可用工具)
  - [快速導覽](#-快速導覽)
  - [麻醉科 / 術前評估](#-麻醉科--術前評估)
  - [重症加護 (ICU)](#-重症加護--icu)
  - [小兒科](#-小兒科)
  - [腎臟科](#-腎臟科)
  - [胸腔科](#-胸腔科)
  - [心臟科](#-心臟科)
  - [血液科](#-血液科)
  - [急診醫學](#-急診醫學)
  - [肝膽科](#-肝膽科)
  - [酸鹼代謝](#-酸鹼代謝)
  - [探索工具](#-探索工具)
  - [提示詞工作流程](#-提示詞工作流程)
- [使用範例](#-使用範例)
- [參考文獻](#-參考文獻)
- [開發指南](#-開發指南)
- [部署指南](docs/DEPLOYMENT.md) 📘
- [路線圖](ROADMAP.md)

---

## 🎯 特色功能

- **🔌 MCP 原生整合**：使用 FastMCP SDK，與 AI Agent 無縫整合
- **🔍 智慧工具探索**：雙層 Key 系統（Low/High Level），讓 AI 智慧選擇工具
- **🏗️ 乾淨 DDD 架構**：洋蔥式架構，關注點分離清晰
- **📚 循證醫學**：所有公式均引用原始同儕審查論文（Vancouver 格式）
- **🔒 型別安全**：完整 Python 型別提示，使用 dataclass 實體
- **🌐 雙語支援**：中英文文檔與工具說明

---

## 🤔 為什麼需要這個專案？

### 問題

當 AI Agent（如 Claude、GPT）需要進行醫學計算時，會遇到以下挑戰：

1. **幻覺風險 (Hallucination Risk)**：LLMs 可能會生成錯誤的公式或數值。
2. **版本混淆 (Version Confusion)**：同一個計算器有多個版本（例如 MELD vs MELD-Na vs MELD 3.0）。
3. **缺乏探索機制 (No Discovery Mechanism)**：AI 如何知道「心臟風險評估」該使用哪個工具？

### 解決方案

本專案提供：

| 特色 | 說明 |
|---------|-------------|
| **經驗證的計算器** | 經同儕審查、測試驗證的公式 |
| **工具探索** | AI 可依專科、病況或臨床問題搜尋 |
| **MCP 協定** | AI 與工具通訊的標準協定 |
| **論文引用** | 每個計算器都引用原始研究 |

---

## 🏗️ 架構

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
                           │ 使用
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     application/                             │
│               (Use Cases, DTOs, Validation)                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  DiscoveryUseCase, CalculateUseCase                  │    │
│  │  DiscoveryRequest/Response, CalculateRequest/Response│    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────────┘
                           │ 依賴於
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                       domain/                                │
│            (Entities, Services, Value Objects)               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  BaseCalculator, ToolMetadata, ScoreResult          │    │
│  │  LowLevelKey, HighLevelKey, ToolRegistry            │    │
│  └─────────────────────────────────────────────────────┘    │
│                    【核心，零依賴】                           │
└─────────────────────────────────────────────────────────────┘
```

### 關鍵設計決策

| 決策 | 決策理由 |
|----------|----------|
| **DDD 洋蔥架構** | 領域邏輯與基礎設施隔離 |
| **FastMCP** | 原生 Python MCP SDK，簡潔裝飾器 API |
| **Dataclasses** | 不可變、型別安全的實體 |
| **雙層 Key 系統** | 同時支援精確查找與探索式發現 |
| **分層驗證** | 三層驗證架構 (MCP/Application/Domain) |

### 驗證架構

```
┌─────────────────────────────────────────────────────────────┐
│  第 1 層：MCP (Infrastructure)                              │
│  └── Pydantic + JSON Schema: 型別驗證                        │
│      (自動從 Annotated[type, Field(description)] 生成)      │
├─────────────────────────────────────────────────────────────┤
│  第 2 層：應用程式 (Use Case)                                │
│  └── ParameterValidator: 計算前預先驗證                      │
│      (22 個參數規格與有效範圍)                               │
├─────────────────────────────────────────────────────────────┤
│  第 3 層：領域 (Calculator)                                  │
│  └── 醫學邏輯驗證                                            │
│      (臨床規則、公式限制)                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 快速開始

### 前置需求

- Python 3.11+ (MCP SDK 要求)
- [uv](https://github.com/astral-sh/uv) (建議使用)

### 安裝

```bash
# 複製儲存庫
git clone https://github.com/u9401066/medical-calc-mcp.git
cd medical-calc-mcp

# 使用 uv 安裝依賴並同步環境
uv sync
```

### 執行 MCP 伺服器

```bash
# 啟動 MCP 伺服器（stdio 傳輸）
uv run python -m src.main

# 或使用 MCP 開發檢查器
uvx mcp dev src/main.py
```

### 與 VS Code Copilot 整合 ⭐ NEW

專案已包含 `.vscode/mcp.json` 設定檔，可無縫整合 VS Code Copilot。

**自動設定:**

只需在 VS Code 開啟此專案，MCP 伺服器會自動被發現！

**在 VS Code 啟用 MCP:**

1. 開啟 VS Code 設定 (Ctrl+,)
2. 搜尋 `chat.mcp`
3. 啟用 `Chat: Mcp Discovery Enabled`
4. 重新啟動 VS Code

**使用方式:**

在 GitHub Copilot Chat 中，使用 `@medical-calc-mcp` 存取計算器：

```
@medical-calc-mcp 使用 PaO2/FiO2=200, platelets=80... 計算 SOFA 分數
```

---

## 🚀 部署模式 ⭐ NEW

本專案支援多種部署模式，可根據使用場景選擇：

| 模式 | 指令 | 連接埠 | 適用場景 |
|------|---------|------|----------|
| **api** | `uv run python -m src.main --mode api` | 8080 | 自定義 Agent、網頁應用程式、腳本 |
| **sse** | `uv run python -m src.main --mode sse` | 8000 | 遠端 MCP 客戶端、Docker |
| **stdio** | `uv run python -m src.main --mode stdio` | - | 本地 Claude Desktop、VS Code |

> 📘 詳細部署指南請參閱 [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

## 🤖 Agent 整合 ⭐ NEW

### Python Agent 範例

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

# 使用方式
client = MedicalCalculatorClient()

# 搜尋敗血症相關計算器
results = client.search("sepsis")

# 計算 SOFA 分數
result = client.calculate("sofa", {
    "pao2_fio2_ratio": 200,
    "platelets": 100,
    "bilirubin": 2.0,
    "gcs_score": 13,
    "creatinine": 2.5
})
print(f"SOFA Score: {result['result']['value']}")
```

---

## 🐳 Docker 部署 ⭐ NEW

MCP 伺服器可透過 Docker 作為**遠端 SSE (Server-Sent Events) 伺服器**執行。

### 使用 Docker 快速開始

```bash
# 建構並執行
docker-compose up -d

# 檢查服務是否運行
curl -sf http://localhost:8000/sse -o /dev/null && echo "OK"
```

---

## 🔒 HTTPS 部署 ⭐ NEW

為生產環境啟用 HTTPS 安全通訊。詳細說明請見 [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)。

---

## 🌐 REST API 接口 ⭐ NEW

除了 MCP 協議，伺服器還提供**獨立的 REST API**，可直接透過 HTTP 存取。預設通訊埠為 `8080`。

| 端點 | 方法 | 說明 |
|----------|--------|-------------|
| `/api/v1/calculators` | GET | 列出所有計算器 |
| `/api/v1/search?q={keyword}` | GET | 搜尋計算器 |
| `/api/v1/calculate/{tool_id}` | POST | 執行計算 |

---

## 🔐 安全性 ⭐ NEW

- **HTTPS**: 透過 Nginx 支援 TLS 1.2/1.3 加密。
- **輸入驗證**: 三層驗證機制（Pydantic → 參數規則 → 領域邏輯）。
- **速率限制**: 支援 Nginx 與應用層雙重保護。
- **API 認證**: 可選的 API Key 認證功能。

---

## 🔍 工具探索

**雙層 Key 系統**是本專案的核心創新：AI Agent 可依專科、臨床情境或快速關鍵字搜尋，每步回傳都包含 `next_step` 提示。

---

## 🔧 可用工具

> **總計**: 82 個工具 | 5 個提示詞 (Prompts) | 4 個資源 (Resources)

### 📑 快速導覽

| 專科 | 數量 | 連結 |
|-----------|-------|---------|
| 🏥 麻醉科 / 術前評估 | 9 | [→ 跳轉](#-麻醉科--術前評估) |
| 🩺 重症加護 (ICU) | 8 | [→ 跳轉](#-重症加護--icu) |
| 👶 小兒科 | 9 | [→ 跳轉](#-小兒科) |
| 🫘 腎臟科 | 2 | [→ 跳轉](#-腎臟科) |
| 🫁 胸腔科 | 6 | [→ 跳轉](#-胸腔科) |
| ❤️ 心臟科 | 9 | [→ 跳轉](#-心臟科) |
| 🚑 急診醫學 / 創傷 | 5 | [→ 跳轉](#-急診醫學) |
| 🟤 肝膽消化科 | 6 | [→ 跳轉](#-肝膽科) |
| 🧪 酸鹼代謝 | 4 | [→ 跳轉](#-酸鹼代謝) |
| 🩸 血液科 | 1 | [→ 跳轉](#-血液科) |
| 🧠 神經科 | 7 | [→ 跳轉](#-神經科) |
| 🔍 探索工具 | 7 | [→ 跳轉](#-探索工具) |
| 📝 提示詞流程 | 5 | [→ 跳轉](#-提示詞工作流程) |

*(其餘詳細工具清單請參考 [English Version](README.md#calculators-75-tools))*

---

## 👨‍💻 開發指南

```bash
# 1. 安裝 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 設定環境與安裝依賴
uv sync

# 3. 執行測試
uv run pytest
```

---

## 📄 授權

Apache 2.0 - 詳見 [LICENSE](LICENSE)

---

## 🙏 致謝

- [Model Context Protocol](https://modelcontextprotocol.io/)
- 原始醫學計算公式與評分系統的所有作者與研究者。
