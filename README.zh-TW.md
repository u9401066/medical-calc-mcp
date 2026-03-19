# Medical Calculator MCP Server 🏥 (繁體中文)

為 AI Agent 提供醫學計算工具的 MCP 伺服器，採用 DDD 洋蔥架構設計。

[English Version](README.md)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP SDK](https://img.shields.io/badge/MCP-FastMCP-green.svg)](https://github.com/modelcontextprotocol/python-sdk)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![CI](https://github.com/u9401066/medical-calc-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/u9401066/medical-calc-mcp/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/tests-2071%20collected-brightgreen.svg)](#-開發指南)
[![References](https://img.shields.io/badge/references-229%20PMIDs%20|%20190%20DOIs-blue.svg)](#-參考文獻)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-orange.svg)](https://github.com/astral-sh/ruff)
[![Architecture](https://img.shields.io/badge/architecture-DDD%20Onion-purple.svg)](#-架構)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

---

## 📖 目錄

- [特色功能](#-特色功能)
- [為什麼需要這個專案？](#-為什麼需要這個專案)
- [架構](#-架構)
- [快速開始](#-快速開始)
- [OpenClaw 相容性](#openclaw-相容性)
- [OpenClaw Registry 指南](docs/OPENCLAW.md)
- [部署模式](#-部署模式) 🚀 NEW
- [Agent 整合](#-agent-整合) 🤖 NEW
- [Docker 部署](#-docker-部署) 🐳
- [HTTPS 部署](#-https-部署) 🔒 NEW
- [REST API 接口](#-rest-api-接口) 🌐 NEW
- [安全性](#-安全性) 🔐 NEW
- [工具探索](#-工具探索)
- [可用工具](#-可用工具)
  - [快速導覽](#-快速導覽)
  - [麻醉科 / 術前評估](#-麻醉科--術前評估)
  - [重症加護](#-重症加護)
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

1. **幻覺風險 | Hallucination Risk**: LLMs 可能會產生錯誤的公式或數值
2. **版本混淆 | Version Confusion**: 同一計算器有多個版本（例如 MELD vs MELD-Na vs MELD 3.0）
3. **缺乏探索機制 | No Discovery Mechanism**: Agent 如何知道該使用哪個工具進行「心臟風險評估」？

### 解決方案

本專案提供：

| 特色 | 說明 |
|---------|------|
| **驗證過的計算器** | 經同儕審查、測試驗證的公式 |
| **工具探索** | AI 可依專科、病況或臨床問題搜尋 |
| **MCP 協定** | AI-工具通訊的標準協定 |
| **論文引用** | 每個計算器都引用原始研究 |

### 🧪 開發方法論

本專案採用「人機協作」的高標準流程，確保臨床準確性：

1. **領域定義**：由人工指定目標醫學專科或臨床領域。
2. **AI 檢索指引**：利用 AI 檢索相關最新的臨床指引（Clinical Guidelines）。
3. **指引特徵提取**：從指引中找出建議的分數計算系統與公式。
4. **原始文獻回溯**：回溯找出原始同儕審查論文（Original Papers），驗證公式係數。
5. **工具製作**：實作具備精確參數驗證與醫學解釋的計分工具。

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
│                    【核心層，零依賴】                         │
└─────────────────────────────────────────────────────────────┘
```

### 關鍵設計決策

| 決策 | 決策理由 |
|----------|-----------|
| **DDD 洋蔥架構** | 領域邏輯與基礎設施隔離 |
| **FastMCP** | 原生 Python MCP SDK，簡潔裝飾器 API |
| **Dataclasses** | 不可變、型別安全的實體 |
| **雙層 Key 系統** | 同時支援精確查找與探索式發現 |
| **分層驗證** | 三層驗證架構 (MCP/Application/Domain) |

### 驗證架構

```
┌─────────────────────────────────────────────────────────────┐
│  第一層: MCP (基礎設施層)                                      │
│  └── Pydantic + JSON Schema: 型別驗證                        │
│      (由 Annotated[type, Field(description)] 自動生成)       │
├─────────────────────────────────────────────────────────────┤
│  第二層: Application (應用層/Use Case)                        │
│  └── ParameterValidator: 計算前參數驗證                       │
│      (針對 22 種參數定義合法範圍)                              │
├─────────────────────────────────────────────────────────────┤
│  第三層: Domain (領域層/計算器)                                │
│  └── 醫學邏輯驗證                                            │
│      (臨床規則、公式限制條件)                                 │
└─────────────────────────────────────────────────────────────┘
```

**領域驗證模組** (`src/domain/validation/`):
- `rules.py`: 基礎類別 (RangeRule, EnumRule, TypeRule, CustomRule)
- `parameter_specs.py`: 22 種醫學參數規格
- `validators.py`: 包含 `validate_params()` 函式的 ParameterValidator

---

## 🚀 快速開始

### 前置需求

- Python 3.11+ (MCP SDK 要求)
- **uv** 套件管理工具（必要）- [安裝 uv](https://docs.astral.sh/uv/getting-started/installation/)

### 安裝

```bash
# 複製儲存庫
git clone https://github.com/u9401066/medical-calc-mcp.git
cd medical-calc-mcp

# 安裝 uv（如果尚未安裝）
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows:
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 同步依賴（自動建立 .venv）
uv sync
```

### 執行 MCP 伺服器

```bash
# 啟動 MCP 伺服器（stdio 傳輸）
uv run python -m src.main

# 或使用 MCP 開發檢查器 (Inspector)
uv run mcp dev src/main.py
```

## OpenClaw 相容性

這個儲存庫已特別整理成適合 OpenClaw 類型的 crawler、MCP registry 與 autonomous agent 快速理解、安裝與安全使用的形式。

### 方便被爬取的關鍵字

- MCP server
- medical calculator MCP
- FastMCP
- stdio MCP server
- SSE MCP server
- evidence-based medical scoring
- AI agent clinical tools
- schema-first calculation
- safe retry guidance

### 為什麼這個 Repo 對 OpenClaw 友善

- README 明確提供標準流程：`discover(...) -> get_tool_schema(tool_id) -> calculate(tool_id, params)`
- 起手 SOP 已暴露在多個 MCP surface：
  - Prompt: `tool_usage_playbook()`
  - Resource: `guide://tool-usage-playbook`
  - Index: `calculator://list`
- smart resolver 可處理模糊 tool id 與 specialty 輸入
- 失敗回應會提供 `guidance`、`suggestions`、`resolved_value`、`param_template`，方便安全重試
- 同時支援本地 `stdio` 與遠端 `sse` / `http` 傳輸

### 最短安裝方式

```bash
git clone https://github.com/u9401066/medical-calc-mcp.git
cd medical-calc-mcp
uv sync
uv run python -m src.main
```

### 建議 OpenClaw 的第一批操作

```text
1. Read resource: guide://tool-usage-playbook
2. Read resource: calculator://list
3. Call tool: discover(by="keyword", value="clinical problem")
4. Call tool: get_tool_schema("tool_id")
5. Call tool: calculate("tool_id", {...})
```

### MCP Client 設定範例

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

### 遠端 Hosted 模式

```bash
uv run python -m src.main --mode sse
# 或
uv run python -m src.main --mode http
```

如果 OpenClaw 會依據 README 內容來判斷是否值得安裝，這個專案現在已提供清楚的安裝方式、transport 模式與 schema-first 的安全 SOP。

### 與 VS Code Copilot 整合 ⭐ NEW

專案已包含 `.vscode/mcp.json` 設定檔，可無縫整合 VS Code Copilot。

**自動設定:**

只需在 VS Code 開啟此專案，MCP 伺服器會自動被發現！

```json
// .vscode/mcp.json (包含在儲存庫中)
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

**在 VS Code 啟用 MCP:**

1. 開啟 VS Code 設定 (Ctrl+,)
2. 搜尋 `chat.mcp`
3. 啟用 `Chat: Mcp Discovery Enabled`
4. 重新啟動 VS Code

**使用方式:**

在 GitHub Copilot Chat 中，使用 `@medical-calc-mcp` 存取計算器：

```
@medical-calc-mcp Calculate SOFA score with PaO2/FiO2=200, platelets=80...
```

### 與 Claude Desktop 整合

將以下內容加入 `claude_desktop_config.json`：

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

## 🚀 部署模式 ⭐ NEW

本專案支援多種部署模式，可根據使用場景選擇：

```
┌─────────────────────────────────────────────────────────────────────┐
│                            部署選項                                 │
├─────────────────┬─────────────────┬─────────────────────────────────┤
│   REST API      │   MCP SSE       │   MCP stdio                     │
│   (連接埠 8080)  │   (連接埠 8000)  │   (本地)                        │
├─────────────────┼─────────────────┼─────────────────────────────────┤
│ ✅ 任何 HTTP     │ ✅ MCP 客戶端    │ ✅ Claude Desktop               │
│    客戶端        │    (遠端)       │ ✅ VS Code Copilot              │
│ ✅ 自定義 Agent  │ ✅ Docker/雲端   │ ✅ MCP Inspector                │
│ ✅ Web 應用      │                 │                                 │
│ ✅ Python/JS    │                 │                                 │
└─────────────────┴─────────────────┴─────────────────────────────────┘
```

| 模式 | 指令 | 連接埠 | 適用場景 |
|------|---------|------|----------|
| **api** | `python src/main.py --mode api` | 8080 | 自定義 Agent、Web 應用、腳本 |
| **sse** | `python src/main.py --mode sse` | 8000 | 遠端 MCP 客戶端、Docker |
| **stdio** | `python src/main.py --mode stdio` | - | 本地 Claude Desktop、VS Code |

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

### LangChain / OpenAI Function Calling

關於 LangChain 與 OpenAI 整合範例，請參閱 [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md#-agent-integration-examples--agent-整合範例)。

### 快速 API 測試

```bash
# 啟動 API 伺服器
python src/main.py --mode api --port 8080

# 測試端點
curl http://localhost:8080/health
curl "http://localhost:8080/api/v1/search?q=sepsis"
curl -X POST "http://localhost:8080/api/v1/calculate/gcs" \
  -H "Content-Type: application/json" \
  -d '{"params": {"eye_response": 4, "verbal_response": 5, "motor_response": 6}}'
```

---

## 🐳 Docker 部署 ⭐ NEW

MCP 伺服器可透過 Docker 作為**遠端 SSE (Server-Sent Events) 伺服器**執行，支援：
- 🌐 從任何 MCP 相容客戶端遠端存取
- ☁️ 雲端部署（AWS、GCP、Azure 等）
- 🔄 使用 Docker Compose 或 Kubernetes 輕鬆擴展

### 使用 Docker 快速開始

```bash
# 建構並執行
docker-compose up -d

# 或手動建構
docker build -t medical-calc-mcp .
docker run -p 8000:8000 medical-calc-mcp

# 檢查服務是否運行
curl -sf http://localhost:8000/sse -o /dev/null && echo "OK"
```

### 傳輸模式

| 模式 | 適用場景 | 連接埠 | 指令 |
|------|----------|------|---------|
| `stdio` | 本地 Claude Desktop | - | `uv run python -m src.main` |
| `sse` | 遠端 MCP (Docker/雲端) | 8000 | `uv run python -m src.main --mode sse` |
| `http` | 可串流的 HTTP 傳輸 | 8000 | `uv run python -m src.main --mode http` |

> ⚠️ **重要**: SSE/HTTP 模式預設綁定到 `0.0.0.0` 以便遠端存取。

### 快速啟動指令

```bash
# 1. STDIO 模式 - 用於 Claude Desktop (本地)
uv run python -m src.main

# 2. SSE 模式 - 用於遠端 Agent (Docker/雲端)
uv run python -m src.main --mode sse
uv run python -m src.main --mode sse --host 0.0.0.0 --port 9000  # 自定義連接埠

# 3. HTTP 模式 - 可串流的 HTTP 傳輸
uv run python -m src.main --mode http
```

### 遠端 MCP 客戶端設定

**Claude Desktop (遠端 SSE):**

```json
{
  "mcpServers": {
    "medical-calc": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

**若是雲端部署，請將 `localhost` 替換為您的伺服器位址：**

```json
{
  "mcpServers": {
    "medical-calc": {
      "url": "https://your-server.example.com/sse"
    }
  }
}
```

### REST API 端點

> ⚠️ FastMCP SSE 模式僅提供以下端點：

| 端點 | 方法 | 說明 |
|----------|--------|-------------|
| `/sse` | GET | SSE 連線端點 |
| `/messages/` | POST | MCP 訊息端點 |

### 環境變數

| 變數 | 預設值 | 說明 |
|----------|---------|-------------|
| `MCP_MODE` | `stdio` | 傳輸模式 (stdio, sse, http) |
| `MCP_HOST` | `0.0.0.0` | 綁定主機位址 |
| `MCP_PORT` | `8000` | 綁定連接埠 |
| `LOG_LEVEL` | `INFO` | 日誌層級 |
| `DEBUG` | `false` | 啟動除錯模式 |

---

## 🔒 HTTPS 部署 ⭐ NEW

為生產環境啟用 HTTPS 安全通訊，支援彈性的憑證配置。

### 架構

```
┌─────────────────────────────────────────────────────────────────────┐
│                        HTTPS Deployment                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌─────────────┐                                                   │
│   │   客戶端    │                                                   │
│   │ (瀏覽器/    │                                                   │
│   │  AI Agent)  │                                                   │
│   └──────┬──────┘                                                   │
│          │ HTTPS (TLS 1.2/1.3)                                      │
│          ▼                                                          │
│   ┌──────────────────────────────────────────────────────────┐      │
│   │                    Nginx 反向代理                         │      │
│   │  ┌─────────────────────────────────────────────────────┐ │      │
│   │  │ • TLS 終端 (SSL 憑證)                                │ │      │
│   │  │ • 速率限制 (30/60 req/s)                            │ │      │
│   │  │ • 安全標頭 (XSS, CSRF 防護)                          │ │      │
│   │  │ • SSE 優化 (長連線)                                  │ │      │
│   │  └─────────────────────────────────────────────────────┘ │      │
│   └──────────────┬───────────────────────┬───────────────────┘      │
│                  │ HTTP (內部)            │ HTTP (內部)             │
│                  ▼                        ▼                         │
│   ┌──────────────────────┐    ┌──────────────────────┐              │
│   │   MCP SSE 伺服器     │    │   REST API 伺服器    │              │
│   │   (連接埠 8000)       │    │   (連接埠 8080)       │              │
│   │                      │    │                      │              │
│   │ • /sse               │    │ • /api/v1/*          │              │
│   │ • /messages          │    │ • /docs (Swagger)    │              │
│   │ • /health            │    │ • /health            │              │
│   └──────────────────────┘    └──────────────────────┘              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

外部端點 (HTTPS):
├── https://localhost/        → MCP SSE (透由 Nginx :443)
├── https://localhost/sse     → SSE 連線
├── https://localhost:8443/   → REST API (透由 Nginx :8443)
└── https://localhost:8443/docs → Swagger UI

內部 (HTTP, 僅 Docker 網絡):
├── http://medical-calc-mcp:8000  → MCP Server
└── http://medical-calc-api:8080  → API Server
```

### SSL 環境變數

| 變數 | 預設值 | 說明 |
|------|--------|------|
| `SSL_ENABLED` | `false` | 啟用 SSL/TLS (`true`/`false`) |
| `SSL_KEYFILE` | - | SSL 私鑰檔案路徑 |
| `SSL_CERTFILE` | - | SSL 憑證檔案路徑 |
| `SSL_CA_CERTS` | - | CA 憑證路徑（可選） |
| `SSL_DIR` | `./nginx/ssl` | SSL 憑證目錄（僅 Docker） |

### 選項一：Docker 部署（推薦）

適用於生產環境和團隊環境。

```bash
# 步驟一：生成 SSL 憑證
chmod +x scripts/generate-ssl-certs.sh
./scripts/generate-ssl-certs.sh

# 步驟二：啟動 HTTPS 服務
./scripts/start-https-docker.sh up

# 其他命令
./scripts/start-https-docker.sh down     # 停止服務
./scripts/start-https-docker.sh logs     # 查看日誌
./scripts/start-https-docker.sh restart  # 重新啟動
./scripts/start-https-docker.sh status   # 檢查狀態
```

**自訂憑證（Docker）：**

```bash
# 使用自訂憑證目錄
SSL_DIR=/path/to/your/certs docker-compose -f docker-compose.https.yml up -d

# 使用 Let's Encrypt 憑證
SSL_DIR=/etc/letsencrypt/live/example.com docker-compose -f docker-compose.https.yml up -d
```

**端點資訊：**

| 服務 | URL | 說明 |
|---------|-----|-------------|
| MCP SSE | `https://localhost/` | MCP Server-Sent Events |
| MCP SSE | `https://localhost/sse` | SSE 連線 |
| REST API | `https://localhost:8443/` | REST API 根目錄 |
| Swagger UI | `https://localhost:8443/docs` | API 文檔 |
| 健康檢查 | `https://localhost/health` | MCP 健康檢查 |
| 健康檢查 | `https://localhost:8443/health` | API 健康檢查 |

### 選項二：本地開發（無 Docker）

使用 Python/Uvicorn 原生 SSL 支援進行快速本地測試。

```bash
# 步驟一：生成 SSL 憑證（或使用您自己的憑證）
./scripts/generate-ssl-certs.sh

# 步驟二：啟動 HTTPS 服務
./scripts/start-https-local.sh          # 同時啟動 MCP 與 API
./scripts/start-https-local.sh sse      # 僅啟動 MCP SSE
./scripts/start-https-local.sh api      # 僅啟動 REST API
```

**自訂憑證（本地）：**

```bash
# 使用環境變數指定自訂憑證路徑
SSL_KEYFILE=/path/to/server.key \
SSL_CERTFILE=/path/to/server.crt \
./scripts/start-https-local.sh

# 自訂連接埠
SSL_KEYFILE=/certs/key.pem SSL_CERTFILE=/certs/cert.pem \
MCP_PORT=9000 API_PORT=9001 \
./scripts/start-https-local.sh

# 使用 CLI 參數直接指定
python -m src.main --mode sse --port 8443 \
    --ssl-keyfile /path/to/server.key \
    --ssl-certfile /path/to/server.crt
```

### 選項三：生產環境使用 Let's Encrypt

使用真實網域名稱和免費受信任憑證。

```bash
# 1. 編輯 nginx/nginx.conf，取消註解這些行：
ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

# 2. 使用 certbot 獲取憑證：
sudo certbot certonly --webroot -w /var/www/certbot \
  -d your-domain.com -d api.your-domain.com

# 3. 使用 Let's Encrypt 憑證啟動服務
SSL_DIR=/etc/letsencrypt/live/your-domain.com \
docker-compose -f docker-compose.https.yml up -d
```

### 檔案說明

| 檔案 | 說明 |
|------|-------------|
| `nginx/nginx.conf` | 包含 TLS、速率限制及 SSE 優化的 Nginx 配置 |
| `docker-compose.https.yml` | HTTPS 部署用的 Docker Compose 設定 |
| `scripts/generate-ssl-certs.sh` | 生成自簽名 SSL 憑證腳本 |
| `scripts/start-https-docker.sh` | 啟動/停止 Docker HTTPS 服務 |
| `scripts/start-https-local.sh` | 啟動本地 HTTPS（支援自訂憑證） |
| `src/infrastructure/mcp/config.py` | SslConfig 類別用於 SSL 配置 |

### SSL 配置參考

| 情境 | 憑證位置 | 配置方式 |
|------|----------|----------|
| Docker（預設） | `nginx/ssl/` | 無需配置 |
| Docker（自訂） | 自訂路徑 | `SSL_DIR` 環境變數或 volumes |
| Docker（Let's Encrypt） | `/etc/letsencrypt/...` | 修改 `nginx/nginx.conf` |
| 本地（預設） | `nginx/ssl/` | 無需配置 |
| 本地（自訂） | 自訂路徑 | `SSL_KEYFILE` + `SSL_CERTFILE` 環境變數 |
| CLI 直接指定 | 自訂路徑 | `--ssl-keyfile` + `--ssl-certfile` 參數 |

---

## 🌐 REST API 接口 ⭐ NEW

除了 MCP 協定，伺服器還提供**獨立的 REST API**，可直接透過 HTTP 存取。

### 快速開始

```bash
# 啟動 API 伺服器
python src/main.py --mode api --port 8080

# 使用 uvicorn（生產環境）
uvicorn src.infrastructure.api.server:app --host 0.0.0.0 --port 8080
```

### API 端點

| 端點 | 方法 | 說明 |
|----------|--------|-------------|
| `/health` | GET | 健康檢查 |
| `/api/v1/calculators` | GET | 列出所有計算器 |
| `/api/v1/calculators/{tool_id}` | GET | 取得計算器資訊 |
| `/api/v1/search?q={keyword}` | GET | 搜尋計算器 |
| `/api/v1/specialties` | GET | 列出所有專科 |
| `/api/v1/specialties/{specialty}` | GET | 依專科列出工具 |
| `/api/v1/calculate/{tool_id}` | POST | 執行計算 |

---

## 🔐 安全性 ⭐ NEW

### 安全特性

本專案實施多層安全機制：

| 層級 | 特性 | 說明 |
|-------|---------|-------------|
| **HTTPS** | TLS 1.2/1.3 加密 | 所有流量經由 Nginx 加密 |
| **輸入驗證** | 三層驗證機制 | Pydantic → ParameterValidator → 領域規則 |
| **CORS** | 可配置來源 | 透過環境變數控制範圍 |
| **速率限制** | Nginx + 應用層 | 雙層保護（供選用） |
| **API 認證** | 可選的 API Key | 預設關閉，可透過環境變數啟用 |
| **安全標頭** | XSS/CSRF 防護 | X-Frame-Options, X-Content-Type-Options |
| **依賴管理** | 漏洞掃描 | 已整合 pip-audit |
| **無資料庫** | 僅記憶體操作 | 無 SQL 注入風險 |
| **無機密儲存** | 無狀態設計 | 不存儲任何憑證 |

> 📖 **詳細 HTTPS 部署說明請參考 [HTTPS 部署](#-https-部署)。**

---

## 🔍 工具探索

**雙層 Key 系統**是本專案的核心創新：

### 探索理念

當 AI Agent 需要醫學計算工具時，使用**階層式導航**：

```
┌─────────────────────────────────────────────────────────────┐
│  路徑 A: 依專科篩選                                          │
│  ① list_specialties() → ["critical_care", "anesthesiology"]│
│  ② list_by_specialty("anesthesiology") → [tool_id, ...]    │
│  ③ get_calculator_info("rcri") → 參數、文獻                │
│  ④ calculate_rcri(...)                                      │
├─────────────────────────────────────────────────────────────┤
│  路徑 B: 依臨床情境篩選                                      │
│  ① list_contexts() → ["preoperative_assessment", ...]      │
│  ② list_by_context("preoperative_assessment") → [tools]    │
│  ③ get_calculator_info("asa_physical_status")              │
│  ④ calculate_asa_physical_status(...)                       │
├─────────────────────────────────────────────────────────────┤
│  路徑 C: 快速搜尋                                            │
│  ① search_calculators("sepsis") → [sofa_score, qsofa, ...] │
│  ② get_calculator_info("sofa_score")                        │
│  ③ calculate_sofa(...)                                      │
└─────────────────────────────────────────────────────────────┘
```

**每一步回傳都包含 `next_step` 提示，Agent 不會迷路！**

### 低階 Key (精準選擇)

用於**精確工具選擇**，當你確切知道需要什麼時：

```python
LowLevelKey(
    tool_id="ckd_epi_2021",           # 唯一識別碼
    name="CKD-EPI 2021",              # 人類可讀名稱
    purpose="Calculate eGFR",          # 功能描述
    input_params=["age", "sex", "creatinine"],  # 必要輸入參數
    output_type="eGFR with CKD staging"         # 輸出格式
)
```

### 探索 MCP 工具

| 工具 | 說明 |
|------|---------|
| `search_calculators(keyword)` | 🔍 快速關鍵字搜尋 |
| `list_by_specialty(specialty)` | 依醫學專科篩選工具 |
| `list_by_context(context)` | 依臨床情境篩選工具 |
| `list_calculators()` | 📋 列出所有計算器 |
| `get_calculator_info(tool_id)` | 📖 取得工具的完整 metadata |
| `list_specialties()` | 📋 列出可用專科 (返回 next_step) |
| `list_contexts()` | 📋 列出可用臨床情境 (返回 next_step) |

---

## 🔧 可用工具

> **Registry Snapshot**: 128 個計算器，涵蓋 26 個專科
>
> **品質快照**: 2071 個已收集測試 | 244 個 PMID | 205 個 DOI | 100% 計算器具文獻引用

### 📑 快速導覽
<!-- BEGIN GENERATED:CATALOG_OVERVIEW_ZH -->
此 README 不再內嵌手動維護的完整工具清單；repository docs 與網站版都改由同一生成來源輸出。

**Registry Snapshot**: 151 個計算器，涵蓋 31 個專科

- [完整工具目錄](docs/CALCULATOR_CATALOG.zh-TW.md)
- [English catalog](docs/CALCULATOR_CATALOG.md)
- [網站版計算器總覽](docs_site/zh-tw/calculators.md)
- [Website calculator catalog](docs_site/calculators/index.md)
- 本機重新產生：`uv run python scripts/generate_tool_catalog_docs.py`

| 專科 | 工具數 |
|------|------:|
| 重症醫學科 | 18 |
| 老年醫學科 | 13 |
| 心臟科 | 11 |
| 急診醫學科 | 9 |
| 精神科 | 9 |
| 麻醉科 | 8 |

如需直接檢視 live registry，也可執行 `python scripts/count_tools.py`、讀取 `calculator://list`，或在 MCP client 呼叫 `list_calculators()`。
<!-- END GENERATED:CATALOG_OVERVIEW_ZH -->

---

### 自動生成工具目錄

完整工具清單與專科摘要現在直接由 registry 產生，避免 README 與實作脫節。

- [完整工具目錄](docs/CALCULATOR_CATALOG.zh-TW.md)
- [English catalog](docs/CALCULATOR_CATALOG.md)
- 本機重新產生：`uv run python scripts/generate_tool_catalog_docs.py`

<!-- BEGIN GENERATED:GUIDELINE_OVERVIEW_ZH -->
### 📋 指引對齊概覽

這份摘要由與 docs / docs_site 相同的生成來源輸出，不再手動維護。

目前追蹤 **65/65** 個指引建議工具，涵蓋 **16** 個臨床領域。

- [指引覆蓋摘要](docs/GUIDELINE_COVERAGE_SUMMARY.zh-TW.md)
- [網站版指引摘要](docs_site/zh-tw/guideline-coverage.md)
- [2023-2025 詳細指引整理](docs/GUIDELINE_RECOMMENDED_TOOLS_2023_2025.md)
- [2020-2025 歷史整理](docs/GUIDELINE_RECOMMENDED_TOOLS_2020_2025.md)

| 領域 | 已實作 | 總數 | 覆蓋率 |
|------|-------:|-----:|-------:|
| 敗血症/重症 | 9 | 9 | 100% |
| 心血管 | 9 | 9 | 100% |
| 消化道出血 | 3 | 3 | 100% |
| 肝臟疾病 | 6 | 6 | 100% |
| 腎臟疾病 | 2 | 2 | 100% |
| 肺炎/呼吸 | 5 | 5 | 100% |
| 血栓栓塞 | 4 | 4 | 100% |
| 神經科 | 7 | 7 | 100% |
| 麻醉科 | 6 | 6 | 100% |
| 創傷 | 4 | 4 | 100% |
| 燒傷 | 2 | 2 | 100% |
| 小兒科 | 2 | 2 | 100% |
| 腫瘤科 | 2 | 2 | 100% |
| 營養科 | 2 | 2 | 100% |
| 風濕科 | 1 | 1 | 100% |
| 骨質疏鬆 | 1 | 1 | 100% |
<!-- END GENERATED:GUIDELINE_OVERVIEW_ZH -->

---

### 📝 提示詞工作流程

| 提示詞 | 說明 |
|--------|-------------|
| `sepsis_evaluation` | qSOFA → SOFA → RASS → CAM-ICU 流程 |
| `preoperative_risk_assessment` | ASA → RCRI → Mallampati 流程 |
| `icu_daily_assessment` | RASS → CAM-ICU → GCS → SOFA 每日巡房流程 |
| `pediatric_drug_dosing` | 體重依賴劑量 + MABL + 輸血量流程 |
| `acute_kidney_injury_assessment` | CKD-EPI + AKI 分期評估流程 |

---

## 📖 使用範例

### Python 範例 ⭐ NEW

專案在 `examples/` 資料夾中包含可直接執行的範例腳本：

```bash
# 基本使用範例
uv run python examples/basic_usage.py

# 臨床工作流程範例
uv run python examples/clinical_workflows.py
```

### 範例：CKD-EPI 2021 (eGFR)

**輸入:**

```json
{
  "serum_creatinine": 1.2,
  "age": 65,
  "sex": "female"
}
```

**輸出:**

```json
{
  "score_name": "CKD-EPI 2021",
  "result": 67.1,
  "unit": "mL/min/1.73m²",
  "interpretation": {
    "summary": "腎功能輕度降低 (G2)",
    "stage": "G2",
    "recommendation": "每年監測腎功能；調整經腎臟排泄之藥物劑量"
  }
}
```

---

## 👨‍💻 開發指南

### 快速開始 (開發者)

```bash
# 1. 安裝 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 設定環境並安裝依賴
uv sync

# 3. 執行測試
uv run pytest

# 4. 在開發模式下執行 MCP 伺服器
uv run mcp dev src/main.py
```

---

## 🧪 測試

### 測試策略

我們維持高品質的程式碼庫，擁有 **2019 個已收集測試**，並由 CI 自動產出覆蓋率報告。

```bash
# 執行所有測試
uv run pytest

# 執行並計算覆蓋率
uv run pytest --cov=src --cov-report=html

# 執行 linter
uv run ruff check src tests

# 自動修正 linting 問題
uv run ruff check --fix src tests
```

### CI/CD 流程

本專案使用 GitHub Actions 進行持續整合，具備以下功能：

| 功能 | 說明 |
|------|------|
| **develop 自動修正** | 自動修正 linting/格式問題並提交 |
| **多 Python 版本測試** | 在 Python 3.11, 3.12, 3.13 上測試 |
| **Docker 健康檢查** | 使用 `/health` endpoint 進行存活探針 |
| **自動發布** | 當 `pyproject.toml` 版本變更時自動建立 GitHub Release |
| **並行控制** | 取消同一分支上進行中的執行 |

---

## 🛠️ 需求

- **Python 3.11+**
- **uv** (建議用於套件管理)
- **MCP SDK** (FastMCP)

---

## 📄 授權協議

Apache 2.0 - 詳見 [LICENSE](LICENSE)

---

## 🙏 致謝

- [Model Context Protocol](https://modelcontextprotocol.io/) - Anthropic 提出的開源 AI-工具通訊協定
- [FastMCP](https://github.com/modelcontextprotocol/python-sdk) - MCP 的 Python SDK
- 所有被引用醫學計算公式與評分系統的原始作者
