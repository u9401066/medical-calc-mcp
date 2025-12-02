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
- [Deployment Modes | 部署模式](#-deployment-modes--部署模式) 🚀 NEW
- [Agent Integration | Agent 整合](#-agent-integration--agent-整合) 🤖 NEW
- [Docker Deployment | Docker 部署](#-docker-deployment--docker-部署--new) 🐳
- [HTTPS Deployment | HTTPS 部署](#-https-deployment--https-部署--new) 🔒 NEW
- [REST API | REST API 接口](#-rest-api--rest-api-接口--new) 🌐 NEW
- [Security | 安全性](#-security--安全性--new) 🔐 NEW
- [Tool Discovery | 工具探索](#-tool-discovery--工具探索)
- [Available Tools | 可用工具](#-available-tools--可用工具)
  - [Quick Navigation | 快速導覽](#-quick-navigation--快速導覽)
  - [Anesthesiology](#-anesthesiology--preoperative--麻醉科--術前評估)
  - [Critical Care](#-critical-care--icu--重症加護)
  - [Pediatrics](#-pediatrics--小兒科)
  - [Nephrology](#-nephrology--腎臟科)
  - [Pulmonology](#-pulmonology--胸腔科)
  - [Cardiology](#-cardiology--心臟科)
  - [Hematology](#-hematology--血液科)
  - [Emergency Medicine](#-emergency-medicine--急診醫學)
  - [Hepatology](#-hepatology--肝膽科)
  - [Acid-Base / Metabolic](#-acid-base--metabolic--酸鹼代謝)
  - [Discovery Tools](#-discovery-tools--探索工具)
  - [Prompts](#-prompts--提示詞工作流程)
- [Usage Examples | 使用範例](#-usage-examples--使用範例)
- [References | 參考文獻](#-references--參考文獻)
- [Development | 開發指南](#-development--開發指南)
- [Deployment Guide | 部署指南](docs/DEPLOYMENT.md) 📘
- [Roadmap | 路線圖](ROADMAP.md)

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

### Configure with VS Code Copilot | 與 VS Code Copilot 整合 ⭐ NEW

The project includes a `.vscode/mcp.json` configuration file for seamless VS Code Copilot integration.

專案已包含 `.vscode/mcp.json` 設定檔，可無縫整合 VS Code Copilot。

**Automatic Setup | 自動設定:**

Simply open this project in VS Code - the MCP server will be auto-discovered!

只需在 VS Code 開啟此專案，MCP 伺服器會自動被發現！

```json
// .vscode/mcp.json (included in repo)
{
  "servers": {
    "medical-calc-mcp": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "python", "-m", "medical_calc_mcp"]
    }
  }
}
```

**Enable MCP in VS Code | 在 VS Code 啟用 MCP:**

1. Open VS Code Settings (Ctrl+,)
2. Search for `chat.mcp`
3. Enable `Chat: Mcp Discovery Enabled`
4. Restart VS Code

**Usage | 使用方式:**

In GitHub Copilot Chat, use `@medical-calc-mcp` to access calculators:

在 GitHub Copilot Chat 中，使用 `@medical-calc-mcp` 存取計算器：

```
@medical-calc-mcp Calculate SOFA score with PaO2/FiO2=200, platelets=80...
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

## 🚀 Deployment Modes | 部署模式 ⭐ NEW

本專案支援多種部署模式，可根據使用場景選擇：

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
| **api** | `python src/main.py --mode api` | 8080 | Custom agents, web apps, scripts |
| **sse** | `python src/main.py --mode sse` | 8000 | Remote MCP clients, Docker |
| **stdio** | `python src/main.py --mode stdio` | - | Local Claude Desktop, VS Code |

> 📘 詳細部署指南請參閱 [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

## 🤖 Agent Integration | Agent 整合 ⭐ NEW

### Python Agent Example | Python Agent 範例

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

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md#-agent-integration-examples--agent-整合範例) for LangChain and OpenAI integration examples.

### Quick API Test | 快速 API 測試

```bash
# Start API server
python src/main.py --mode api --port 8080

# Test endpoints
curl http://localhost:8080/health
curl "http://localhost:8080/api/v1/search?q=sepsis"
curl -X POST "http://localhost:8080/api/v1/calculate/gcs" \
  -H "Content-Type: application/json" \
  -d '{"params": {"eye_response": 4, "verbal_response": 5, "motor_response": 6}}'
```

---

## 🐳 Docker Deployment | Docker 部署 ⭐ NEW

The MCP server can run as a **remote SSE (Server-Sent Events) server** via Docker, enabling:
- 🌐 Remote access from any MCP-compatible client
- ☁️ Cloud deployment (AWS, GCP, Azure, etc.)
- 🔄 Easy scaling with Docker Compose or Kubernetes

MCP 伺服器可透過 Docker 作為**遠端 SSE (Server-Sent Events) 伺服器**執行，支援：
- 🌐 從任何 MCP 相容客戶端遠端存取
- ☁️ 雲端部署（AWS、GCP、Azure 等）
- 🔄 使用 Docker Compose 或 Kubernetes 輕鬆擴展

### Quick Start with Docker | 使用 Docker 快速開始

```bash
# Build and run | 建構並執行
docker-compose up -d

# Or build manually | 或手動建構
docker build -t medical-calc-mcp .
docker run -p 8000:8000 medical-calc-mcp

# Check health | 檢查健康狀態
curl http://localhost:8000/health
```

### Transport Modes | 傳輸模式

| Mode | Use Case | Port | Command |
|------|----------|------|---------|
| `stdio` | Local Claude Desktop | - | `python src/main.py --mode stdio` |
| `sse` | Remote MCP (Docker/Cloud) | 8000 | `python src/main.py --mode sse --port 8000` |
| `api` | REST API (FastAPI) | 8080 | `python src/main.py --mode api --port 8080` |
| `http` | Streamable HTTP transport | - | `python src/main.py --mode http` |

### Remote MCP Client Configuration | 遠端 MCP 客戶端設定

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

### API Endpoints | API 端點

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Server info and configuration |
| `/health` | GET | Health check for Docker/K8s |
| `/sse` | GET | SSE connection endpoint |
| `/messages/` | POST | MCP message endpoint |

### Environment Variables | 環境變數

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_MODE` | `stdio` | Transport mode (stdio, sse, http) |
| `MCP_HOST` | `0.0.0.0` | Host to bind |
| `MCP_PORT` | `8000` | Port to bind |
| `LOG_LEVEL` | `INFO` | Logging level |
| `DEBUG` | `false` | Enable debug mode |

### Docker Compose Example | Docker Compose 範例

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

## 🔒 HTTPS Deployment | HTTPS 部署 ⭐ NEW

Enable HTTPS for secure communication in production environments.

為生產環境啟用 HTTPS 安全通訊。

### Architecture | 架構

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

### Option 1: Docker Deployment (Recommended) | Docker 部署（推薦）

Best for production and team environments.

適用於生產環境和團隊環境。

```bash
# Step 1: Generate SSL certificates | 步驟一：生成 SSL 憑證
chmod +x scripts/generate-ssl-certs.sh
./scripts/generate-ssl-certs.sh

# Step 2: Start HTTPS services | 步驟二：啟動 HTTPS 服務
./scripts/start-https-docker.sh up

# Other commands | 其他命令
./scripts/start-https-docker.sh down     # Stop services
./scripts/start-https-docker.sh logs     # View logs
./scripts/start-https-docker.sh restart  # Restart
./scripts/start-https-docker.sh status   # Check status
```

**Endpoints | 端點：**

| Service | URL | Description |
|---------|-----|-------------|
| MCP SSE | `https://localhost/` | MCP Server-Sent Events |
| MCP SSE | `https://localhost/sse` | SSE connection |
| REST API | `https://localhost:8443/` | REST API root |
| Swagger UI | `https://localhost:8443/docs` | API documentation |
| Health | `https://localhost/health` | MCP health check |
| Health | `https://localhost:8443/health` | API health check |

### Option 2: Local Development (No Docker) | 本地開發（無 Docker）

Uses Uvicorn's native SSL support for quick local testing.

使用 Uvicorn 原生 SSL 支援進行快速本地測試。

```bash
# Step 1: Generate SSL certificates | 步驟一：生成 SSL 憑證
./scripts/generate-ssl-certs.sh

# Step 2: Start HTTPS services | 步驟二：啟動 HTTPS 服務
./scripts/start-https-local.sh          # Start both MCP and API
./scripts/start-https-local.sh sse      # Start MCP SSE only
./scripts/start-https-local.sh api      # Start REST API only
```

**Endpoints | 端點：**

| Service | URL | Description |
|---------|-----|-------------|
| MCP SSE | `https://localhost:8443/` | MCP Server-Sent Events |
| REST API | `https://localhost:9443/` | REST API |
| Swagger UI | `https://localhost:9443/docs` | API documentation |

### Option 3: Production with Let's Encrypt | 生產環境使用 Let's Encrypt

For real domain names with free trusted certificates.

使用真實網域名稱和免費受信任憑證。

```bash
# 1. Edit nginx/nginx.conf, uncomment these lines:
# 編輯 nginx/nginx.conf，取消註解這些行：

ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

# 2. Use certbot to obtain certificates:
# 使用 certbot 獲取憑證：

sudo certbot certonly --webroot -w /var/www/certbot \
  -d your-domain.com -d api.your-domain.com

# 3. Start services
# 啟動服務
docker-compose -f docker-compose.https.yml up -d
```

### Trust Self-Signed Certificates | 信任自簽憑證

To avoid browser warnings during development:

消除開發時的瀏覽器警告：

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

### Claude Desktop Configuration (HTTPS) | Claude Desktop 設定

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

### Files Overview | 檔案說明

| File | Description |
|------|-------------|
| `nginx/nginx.conf` | Nginx configuration with TLS, rate limiting, SSE optimization |
| `docker-compose.https.yml` | Docker Compose for HTTPS deployment |
| `scripts/generate-ssl-certs.sh` | Generate self-signed SSL certificates |
| `scripts/start-https-docker.sh` | Start/stop Docker HTTPS services |
| `scripts/start-https-local.sh` | Start local HTTPS (Uvicorn SSL) |

### Troubleshooting | 故障排除

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

## 🌐 REST API | REST API 接口 ⭐ NEW

Besides MCP protocol, the server also provides a **standalone REST API** for direct HTTP access.

除了 MCP 協議，伺服器還提供**獨立的 REST API**，可直接透過 HTTP 存取。

### Quick Start | 快速開始

```bash
# Start API server | 啟動 API 伺服器
python src/main.py --mode api --port 8080

# With uvicorn (production) | 使用 uvicorn（生產環境）
uvicorn src.infrastructure.api.server:app --host 0.0.0.0 --port 8080
```

### API Documentation | API 文件

Once running, visit:
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **OpenAPI JSON**: http://localhost:8080/openapi.json

### API Endpoints | API 端點

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/v1/calculators` | GET | List all calculators |
| `/api/v1/calculators/{tool_id}` | GET | Get calculator info |
| `/api/v1/search?q={keyword}` | GET | Search calculators |
| `/api/v1/specialties` | GET | List specialties |
| `/api/v1/specialties/{specialty}` | GET | List by specialty |
| `/api/v1/calculate/{tool_id}` | POST | Execute calculation |

### Example: Calculate CKD-EPI | 範例：計算 CKD-EPI

```bash
# Using curl
curl -X POST "http://localhost:8080/api/v1/calculate/ckd_epi_2021" \
  -H "Content-Type: application/json" \
  -d '{"params": {"serum_creatinine": 1.2, "age": 65, "sex": "female"}}'
```

**Response | 回應:**
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

### Quick Calculate Endpoints | 快速計算端點

Some calculators have dedicated endpoints with query parameters:

部分計算器有專用端點，使用查詢參數：

```bash
# CKD-EPI (Query parameters)
curl "http://localhost:8080/api/v1/ckd-epi?serum_creatinine=1.2&age=65&sex=female"

# SOFA Score
curl -X POST "http://localhost:8080/api/v1/sofa?pao2_fio2_ratio=200&platelets=100&bilirubin=2.0&cardiovascular=dopamine_lte_5&gcs_score=13&creatinine=2.5"
```

---

## 🔐 Security | 安全性 ⭐ NEW

### Security Features | 安全特性

This project implements multiple security layers:

本專案實施多層安全機制：

| Layer | Feature | Description |
|-------|---------|-------------|
| **HTTPS** | TLS 1.2/1.3 encryption | All traffic encrypted via Nginx |
| **Input Validation** | 3-layer validation | Pydantic → ParameterValidator → Domain rules |
| **CORS** | Configurable origins | Environment variable controlled |
| **Rate Limiting** | Nginx rate limits | 30 req/s API, 60 req/s MCP |
| **Security Headers** | XSS/CSRF protection | X-Frame-Options, X-Content-Type-Options |
| **Dependencies** | Vulnerability scanning | pip-audit integrated |
| **No Database** | In-memory only | No SQL injection risk |
| **No Secrets** | Stateless | No credentials stored |

> 📖 **For detailed HTTPS deployment instructions, see [HTTPS Deployment](#-https-deployment--https-部署--new).**
>
> **詳細 HTTPS 部署說明請參考 [HTTPS 部署](#-https-deployment--https-部署--new)。**

### Configuration | 設定

**CORS Configuration | CORS 設定:**

```bash
# Development (default) - Allow all origins
# 開發環境（預設）- 允許所有來源
CORS_ORIGINS="*"

# Production - Restrict to specific domains
# 生產環境 - 限制特定網域
CORS_ORIGINS="https://your-app.com,https://api.your-app.com"
```

**Other Security Settings | 其他安全設定:**

```bash
# API Server
API_HOST=0.0.0.0   # Use 127.0.0.1 for local only
API_PORT=8080

# MCP Server  
MCP_HOST=0.0.0.0   # Use 127.0.0.1 for local only
MCP_PORT=8000
```

### Production Recommendations | 生產環境建議

| Item | Recommendation | 建議 |
|------|----------------|------|
| **HTTPS** | ✅ Use provided Nginx + SSL config | 使用提供的 Nginx + SSL 配置 |
| **CORS** | Set specific `CORS_ORIGINS` | 設定特定 `CORS_ORIGINS` |
| **Rate Limiting** | ✅ Nginx configured (30/60 req/s) | Nginx 已配置 |
| **Authentication** | Add API key or OAuth2 if needed | 如需要可加入 API key 或 OAuth2 |
| **Network** | Run in private network/VPC | 在私有網路/VPC 中執行 |
| **Certificates** | Use Let's Encrypt for production | 生產環境使用 Let's Encrypt |
| **Monitoring** | Enable access logging | 啟用存取日誌 |

### Dependency Security | 依賴安全

```bash
# Check for known vulnerabilities | 檢查已知漏洞
pip install pip-audit
pip-audit --strict

# Upgrade all packages | 升級所有套件
pip install --upgrade pip setuptools
pip install -r requirements.txt --upgrade
```

### Security Audit Results | 安全審查結果 (2025-06)

✅ **Passed Checks | 通過檢查:**
- No SQL/Command injection vulnerabilities
- No hardcoded secrets or credentials
- No sensitive data exposure in error messages
- Input validation at all layers
- Dependencies updated (no known CVEs)

⚠️ **Notes | 注意事項:**
- Default CORS is permissive (`*`) - configure for production
- No built-in authentication - add at infrastructure layer if needed
- Medical calculations are for reference only - not for clinical decisions

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
| `search_calculators(keyword)` | Keyword search | 關鍵字搜尋 |
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

Agent: search_calculators("sepsis")
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

> **MCP Primitives**: 58 Tools + 5 Prompts + 4 Resources
>
> **Current Stats**: 51 Calculators | 518 Tests | 80% Coverage | Phase 13 Complete ✅
>
> 📋 **[See Full Roadmap →](ROADMAP.md)** | **[Contributing Guide →](CONTRIBUTING.md)**

### 📑 Quick Navigation | 快速導覽

| Specialty | Count | Jump To |
|-----------|-------|---------|
| 🏥 Anesthesiology / Preoperative | 9 | [→ Jump](#-anesthesiology--preoperative--麻醉科--術前評估) |
| 🩺 Critical Care / ICU | 8 | [→ Jump](#-critical-care--icu--重症加護) |
| 👶 Pediatrics | 1 | [→ Jump](#-pediatrics--小兒科) |
| 🫘 Nephrology | 2 | [→ Jump](#-nephrology--腎臟科) |
| 🫁 Pulmonology | 5 | [→ Jump](#-pulmonology--胸腔科) |
| ❤️ Cardiology | 9 | [→ Jump](#-cardiology--心臟科) |
| 🚑 Emergency Medicine | 3 | [→ Jump](#-emergency-medicine--急診醫學) |
| 🟤 Hepatology | 4 | [→ Jump](#-hepatology--肝膽科) |
| 🧪 Acid-Base / Metabolic | 4 | [→ Jump](#-acid-base--metabolic--酸鹼代謝) |
| 🩸 Hematology | 1 | [→ Jump](#-hematology--血液科) |
| 🧠 Neurology | 4 | [→ Jump](#-neurology--神經科) |
| 🔍 Discovery Tools | 7 | [→ Jump](#-discovery-tools--探索工具) |
| 📝 Prompts | 5 | [→ Jump](#-prompts--提示詞工作流程) |

---

### Calculators | 計算器 (51 tools)

#### 🏥 Anesthesiology / Preoperative | 麻醉科 / 術前評估

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

[↑ Back to Navigation](#-quick-navigation--快速導覽)

#### 🩺 Critical Care / ICU | 重症加護

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

[↑ Back to Navigation](#-quick-navigation--快速導覽)

#### 👶 Pediatrics | 小兒科

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `calculate_pediatric_drug_dose` | Pediatric Dosing | Weight-based drug dosing | Lexicomp, Anderson 2017 |

[↑ Back to Navigation](#-quick-navigation--快速導覽)

#### 🫘 Nephrology | 腎臟科

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `calculate_ckd_epi_2021` | CKD-EPI 2021 | eGFR (race-free) | Inker 2021 |
| `calculate_kdigo_aki` | KDIGO AKI | Acute kidney injury staging | KDIGO 2012 |

[↑ Back to Navigation](#-quick-navigation--快速導覽)

#### 🫁 Pulmonology | 胸腔科

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `calculate_curb65` | CURB-65 | Pneumonia severity & disposition | Lim 2003 |
| `calculate_psi_port` | PSI/PORT | CAP mortality prediction | Fine 1997 |
| `calculate_ideal_body_weight` | IBW (Devine) | Ventilator tidal volume (ARDSNet) | Devine 1974, ARDSNet 2000 |
| `calculate_pf_ratio` | P/F Ratio | ARDS Berlin classification | ARDS Task Force 2012 |
| `calculate_rox_index` | ROX Index | HFNC failure prediction | Roca 2016 |

[↑ Back to Navigation](#-quick-navigation--快速導覽)

#### ❤️ Cardiology | 心臟科

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

[↑ Back to Navigation](#-quick-navigation--快速導覽)

#### 🩸 Hematology | 血液科

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `calculate_4ts_hit` | 4Ts HIT Score | Heparin-induced thrombocytopenia | Lo 2006, Cuker 2012 |

[↑ Back to Navigation](#-quick-navigation--快速導覽)

#### 🧠 Neurology | 神經科

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `calculate_nihss` | NIHSS | NIH Stroke Scale - stroke severity | Brott 1989 |
| `calculate_abcd2` | ABCD2 Score 🆕 | TIA 7-day stroke risk prediction | Johnston 2007 |
| `calculate_modified_rankin_scale` | Modified Rankin Scale 🆕 | Post-stroke disability assessment | van Swieten 1988 |

[↑ Back to Navigation](#-quick-navigation--快速導覽)

#### 🚑 Emergency Medicine | 急診醫學

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `calculate_wells_dvt` | Wells DVT | DVT probability assessment | Wells 2003 |
| `calculate_wells_pe` | Wells PE | PE probability assessment | Wells 2000 |
| `calculate_shock_index` | Shock Index (SI) | Rapid hemodynamic assessment | Allgöwer 1967 |

[↑ Back to Navigation](#-quick-navigation--快速導覽)

#### 🟤 Hepatology | 肝膽科

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `calculate_meld_score` | MELD Score | End-stage liver disease mortality | Kamath 2001 |
| `calculate_child_pugh` | Child-Pugh | Cirrhosis severity staging | Pugh 1973 |
| `calculate_rockall_score` | Rockall Score 🆕 | Upper GI bleeding risk (mortality/rebleeding) | Rockall 1996 |
| `calculate_fib4_index` | FIB-4 Index 🆕 | Liver fibrosis non-invasive assessment | Sterling 2006 |

[↑ Back to Navigation](#-quick-navigation--快速導覽)

#### 🧪 Acid-Base / Metabolic | 酸鹼代謝

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `calculate_anion_gap` | Anion Gap | Metabolic acidosis differential | Kraut 2007, Figge 1998 |
| `calculate_delta_ratio` | Delta Ratio (Delta Gap) | Mixed acid-base disorder detection | Wrenn 1990, Rastegar 2007 |
| `calculate_corrected_sodium` | Corrected Sodium | True sodium in hyperglycemia | Katz 1973, Hillier 1999 |
| `calculate_winters_formula` | Winter's Formula | Expected PaCO₂ in metabolic acidosis | Albert 1967, Narins 1980 |
| `calculate_osmolar_gap` | Osmolar Gap | Toxic alcohol screening | Hoffman 1993, Lynd 2008 |
| `calculate_free_water_deficit` | Free Water Deficit | Hypernatremia treatment planning | Adrogue 2000, Sterns 2015 |
| `calculate_aa_gradient` | A-a Gradient | Alveolar-arterial O₂ gradient | Kanber 1968, West 2016 |

[↑ Back to Navigation](#-quick-navigation--快速導覽)

---

### 🔍 Discovery Tools | 探索工具

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

[↑ Back to Navigation](#-quick-navigation--快速導覽)

---

### 📦 Resources | 資源

| Resource URI | Description |
|--------------|-------------|
| `calculator://list` | Markdown list of all calculators |
| `calculator://{tool_id}/references` | Paper references for a calculator |
| `calculator://{tool_id}/parameters` | Input parameter definitions |
| `calculator://{tool_id}/info` | Full calculator metadata |

---

### 📝 Prompts | 提示詞工作流程

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

[↑ Back to Navigation](#-quick-navigation--快速導覽)

---

## 📖 Usage Examples | 使用範例

### Python Examples | Python 範例 ⭐ NEW

The project includes ready-to-run example scripts in the `examples/` folder:

專案在 `examples/` 資料夾中包含可直接執行的範例腳本：

```bash
# Basic usage examples | 基本使用範例
python examples/basic_usage.py

# Clinical workflow examples | 臨床工作流程範例
python examples/clinical_workflows.py
```

**Available Examples | 可用範例:**

| File | Description | 說明 |
|------|-------------|------|
| `basic_usage.py` | Individual calculator usage (CKD-EPI, SOFA, RCRI, CHA₂DS₂-VASc, Wells PE) | 單一計算器使用 |
| `clinical_workflows.py` | Multi-calculator clinical scenarios (Sepsis, Preop, Chest Pain, AF) | 多計算器臨床情境 |

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

**Query | 查詢:** `search_calculators("airway")`

**Output | 輸出:**
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
| Phase 6 | ✅ Complete | More Calculators (CURB-65, CHA₂DS₂-VASc, HEART, Wells DVT/PE, MELD) |
| Phase 7 | ✅ Complete | Validation Layer (Domain validation module, 22 parameter specs) |
| Phase 7.5 | ✅ Complete | CHA₂DS₂-VA (2024 ESC), Caprini VTE, PSI/PORT + Type Safety Fixes |
| Phase 8 | ✅ Complete | **Guideline-Recommended Tools** (HAS-BLED, Child-Pugh, KDIGO AKI) |
| Phase 9 | 📋 Planned | HTTP Transport (FastAPI/Starlette for web deployment) |
| Phase 10 | 📋 Planned | Internationalization (i18n for multi-language support) |
| Phase 13 | ✅ Complete | **Additional Clinical Tools** (ABCD2, mRS, TIMI STEMI, Rockall, FIB-4) |

### Roadmap | 路線圖

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
├── ✅ Anion Gap                                                 Target: 50+ calculators
├── ✅ Delta Ratio
├── ✅ Corrected Sodium
├── ✅ Winter's Formula
├── ✅ Osmolar Gap
└── ✅ Free Water Deficit
```

### Recently Added Calculators | 最近新增的計算器 (Phase 13 Complete ✅)

| Priority | Tool ID | Name | Status | Reference |
|----------|---------|------|--------|-----------|
| ✅ Done | `abcd2` | ABCD2 Score | Complete | Johnston 2007 |
| ✅ Done | `modified_rankin_scale` | Modified Rankin Scale (mRS) | Complete | van Swieten 1988 |
| ✅ Done | `timi_stemi` | TIMI STEMI Risk Score | Complete | Morrow 2000 |
| ✅ Done | `rockall_score` | Rockall Score | Complete | Rockall 1996 |
| ✅ Done | `fib4_index` | FIB-4 Index | Complete | Sterling 2006 |

---

### Testing | 測試

#### Testing Strategy | 測試策略

```
┌─────────────────────────────────────────────────────────────────┐
│                        Testing Pyramid                          │
├─────────────────────────────────────────────────────────────────┤
│                     E2E Tests (MCP Protocol)                     │
│                    ╱                          ╲                  │
│           Integration Tests              MCP Inspector           │
│          (Use Cases + Registry)          (Manual Testing)        │
│                  ╱              ╲                                │
│      Unit Tests (Domain)    Validation Tests                     │
│      ╱                  ╲                                        │
│  Calculator Tests    Entity Tests                                │
└─────────────────────────────────────────────────────────────────┘
```

#### Quick Testing | 快速測試

```bash
# 1. Domain Unit Test - Calculator logic
# 1. Domain 單元測試 - 計算器邏輯
python -c "
from src.domain.services.calculators.sofa_score import SofaScoreCalculator
calc = SofaScoreCalculator()
result = calc.calculate(
    pao2_fio2_ratio=200, platelets=100, bilirubin=2.0,
    cardiovascular='dopamine_lte_5', gcs_score=13, creatinine=2.5
)
print(f'SOFA: {result.value}, Severity: {result.interpretation.severity}')
"

# 2. Validation Test - Parameter specs
# 2. 驗證測試 - 參數規格
python -c "
from src.domain.validation import validate_params
result = validate_params({'age': 150, 'sex': 'unknown'}, required=['age', 'sex'])
print(f'Valid: {result.is_valid}')
print(f'Errors: {result.get_error_message()}')
"

# 3. Integration Test - Use Case
# 3. 整合測試 - Use Case
python -c "
from src.infrastructure.mcp.server import MedicalCalculatorServer
server = MedicalCalculatorServer()
# Test discovery
from src.application.use_cases.discovery_use_case import DiscoveryUseCase
from src.application.dto import DiscoveryRequest, DiscoveryMode
use_case = DiscoveryUseCase(server.registry)
result = use_case.execute(DiscoveryRequest(mode=DiscoveryMode.BY_SPECIALTY, specialty='critical_care'))
print(f'Found {len(result.tools)} tools for critical_care')
"

# 4. MCP Protocol Test - Full E2E
# 4. MCP 協議測試 - 完整端對端
mcp dev src/infrastructure/mcp/server.py
# Then use Inspector UI to test tools interactively
```

#### Automated Test Suite (Planned) | 自動化測試套件（計劃中）

```bash
# Install test dependencies | 安裝測試依賴
pip install pytest pytest-cov pytest-asyncio

# Run all tests | 執行所有測試
pytest tests/ -v

# Run with coverage | 執行並計算覆蓋率
pytest tests/ --cov=src --cov-report=html

# Run specific layer tests | 執行特定層測試
pytest tests/domain/ -v          # Domain layer
pytest tests/application/ -v      # Application layer
pytest tests/integration/ -v      # Integration tests
```

#### Test File Structure (Planned) | 測試檔案結構（計劃中）

```
tests/
├── domain/
│   ├── services/
│   │   └── calculators/
│   │       ├── test_sofa_score.py
│   │       ├── test_ckd_epi.py
│   │       └── test_gcs.py
│   ├── validation/
│   │   ├── test_rules.py
│   │   └── test_parameter_specs.py
│   └── registry/
│       └── test_tool_registry.py
├── application/
│   ├── use_cases/
│   │   ├── test_calculate_use_case.py
│   │   └── test_discovery_use_case.py
│   └── dto/
│       └── test_dto_serialization.py
├── integration/
│   ├── test_mcp_tools.py
│   └── test_mcp_resources.py
└── conftest.py                   # Shared fixtures
```

#### Medical Formula Verification | 醫學公式驗證

Each calculator should be verified against:
每個計算器應驗證：

1. **Original Paper Examples** - Use cases from the original publication
2. **Edge Cases** - Boundary values (min/max inputs)
3. **Known Values** - Validated against trusted sources (UpToDate, PubMed)
4. **Clinical Reasonability** - Results within clinically expected ranges

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

# Test validation module | 測試驗證模組
python -c "from src.domain.validation import validate_params; \
           r = validate_params({'age': 150}, required=['age']); \
           print(f'Valid: {r.is_valid}, Error: {r.get_error_message()}')"
```

For comprehensive testing guide, see [Testing section](#testing--測試) above.

詳細測試指南請參考上方的[測試章節](#testing--測試)。

---

## 📄 License

Apache 2.0 - See [LICENSE](LICENSE)

---

## 🙏 Acknowledgments | 致謝

- [Model Context Protocol](https://modelcontextprotocol.io/) - Anthropic's open protocol for AI-tool communication
- [FastMCP](https://github.com/modelcontextprotocol/python-sdk) - Python SDK for MCP
- Original authors of all cited medical calculators and scoring systems
