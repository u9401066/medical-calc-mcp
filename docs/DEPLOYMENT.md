# Deployment Guide | 部署指南

本指南說明如何將 Medical Calculator MCP Server 部署為獨立服務，供 AI Agent 或其他應用程式呼叫。

This guide explains how to deploy the Medical Calculator MCP Server as a standalone service for AI agents or other applications.

---

## 📋 Table of Contents | 目錄

- [Deployment Modes Overview | 部署模式總覽](#-deployment-modes-overview--部署模式總覽)
- [Mode 1: REST API (Recommended for Custom Agents)](#-mode-1-rest-api-recommended-for-custom-agents)
- [Mode 2: MCP SSE (Remote MCP Server)](#-mode-2-mcp-sse-remote-mcp-server)
- [Mode 3: MCP stdio (Local Integration)](#-mode-3-mcp-stdio-local-integration)
- [Docker Deployment | Docker 部署](#-docker-deployment--docker-部署)
- [HTTPS Deployment | HTTPS 部署](#-https-deployment--https-部署) 🔒 NEW
- [Cloud Deployment | 雲端部署](#-cloud-deployment--雲端部署)
- [Agent Integration Examples | Agent 整合範例](#-agent-integration-examples--agent-整合範例)
- [Security Considerations | 安全考量](#-security-considerations--安全考量)
- [Troubleshooting | 疑難排解](#-troubleshooting--疑難排解)

---

## 🎯 Deployment Modes Overview | 部署模式總覽

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           Deployment Options                                  │
├─────────────────┬─────────────────┬─────────────────┬────────────────────────┤
│   REST API      │   MCP SSE       │   MCP stdio     │   HTTPS (Production)   │
│   (Port 8080)   │   (Port 8000)   │   (Local)       │   (Nginx + TLS)        │
├─────────────────┼─────────────────┼─────────────────┼────────────────────────┤
│ ✅ Any HTTP     │ ✅ MCP Clients  │ ✅ Claude       │ ✅ Production deploy   │
│    client       │    (remote)     │    Desktop      │ ✅ Secure connections  │
│ ✅ Custom Agent │ ✅ Docker/Cloud │ ✅ VS Code      │ ✅ Rate limiting       │
│ ✅ Web Apps     │                 │    Copilot      │ ✅ TLS 1.2/1.3         │
│ ✅ Scripts      │                 │                 │                        │
└─────────────────┴─────────────────┴─────────────────┴────────────────────────┘
```

| Mode | Protocol | Port | Best For |
|------|----------|------|----------|
| **api** | HTTP REST | 8080 | Custom agents, web apps, any HTTP client |
| **sse** | MCP over SSE | 8000 | Remote MCP clients, Docker deployment |
| **stdio** | MCP stdio | - | Local Claude Desktop, VS Code Copilot |
| **https** | HTTPS (Nginx) | 443/8443 | Production with TLS encryption 🔒 |

---

## 🌐 Mode 1: REST API (Recommended for Custom Agents)

最通用的整合方式，任何能發送 HTTP 請求的應用程式都可使用。

### Quick Start | 快速開始

```bash
# 安裝依賴並同步環境
uv sync

# 啟動 REST API 伺服器
uv run python -m src.main --mode api --port 8080

# 或使用 uvicorn（生產環境）
uv run uvicorn src.infrastructure.api.server:app --host 0.0.0.0 --port 8080 --workers 4
```

### API Endpoints | API 端點

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | 健康檢查 |
| `/api/v1/calculators` | GET | 列出所有計算器 |
| `/api/v1/calculators/{tool_id}` | GET | 取得計算器詳細資訊 |
| `/api/v1/search?q={keyword}` | GET | 搜尋計算器 |
| `/api/v1/specialties` | GET | 列出所有專科 |
| `/api/v1/specialties/{specialty}` | GET | 依專科列出計算器 |
| `/api/v1/contexts` | GET | 列出所有臨床情境 |
| `/api/v1/contexts/{context}` | GET | 依情境列出計算器 |
| `/api/v1/calculate/{tool_id}` | POST | 執行計算 |

### API Documentation | API 文件

啟動後造訪：
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **OpenAPI JSON**: http://localhost:8080/openapi.json

### Example Requests | 請求範例

```bash
# 1. 健康檢查
curl http://localhost:8080/health

# 2. 列出所有計算器
curl http://localhost:8080/api/v1/calculators

# 3. 搜尋 sepsis 相關計算器
curl "http://localhost:8080/api/v1/search?q=sepsis"

# 4. 取得 SOFA 計算器資訊
curl http://localhost:8080/api/v1/calculators/sofa

# 5. 執行 SOFA 計算
curl -X POST "http://localhost:8080/api/v1/calculate/sofa" \
  -H "Content-Type: application/json" \
  -d '{
    "params": {
      "pao2_fio2_ratio": 200,
      "platelets": 100,
      "bilirubin": 2.0,
      "gcs_score": 13,
      "creatinine": 2.5
    }
  }'

# 6. 計算 CKD-EPI eGFR
curl -X POST "http://localhost:8080/api/v1/calculate/ckd_epi_2021" \
  -H "Content-Type: application/json" \
  -d '{
    "params": {
      "serum_creatinine": 1.2,
      "age": 65,
      "sex": "female"
    }
  }'
```

---

## 🔗 Mode 2: MCP SSE (Remote MCP Server)

適用於支援 MCP 協議的 AI 客戶端，可透過網路遠端連接。

### Quick Start | 快速開始

```bash
# 啟動 SSE 伺服器
python src/main.py --mode sse --host 0.0.0.0 --port 8000
```

### SSE Endpoints | SSE 端點

> ⚠️ FastMCP SSE 模式只提供以下端點：

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/sse` | GET | SSE 連接端點 |
| `/messages/` | POST | MCP 訊息端點 |

### Client Configuration | 客戶端設定

**Claude Desktop (Remote)**:
```json
{
  "mcpServers": {
    "medical-calc": {
      "url": "http://your-server-ip:8000/sse"
    }
  }
}
```

---

## 🖥️ Mode 3: MCP stdio (Local Integration)

適用於本地 AI 工具整合。

### VS Code Copilot

專案已包含 `.vscode/mcp.json`：

```json
{
  "servers": {
    "medical-calc-mcp": {
      "type": "stdio",
      "command": "${workspaceFolder}/.venv/bin/python",
      "args": ["-m", "src.infrastructure.mcp.server"]
    }
  }
}
```

### Claude Desktop (Local)

編輯 `claude_desktop_config.json`：

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

### MCP Inspector (Development)

```bash
uvx mcp dev src/main.py
```

---

## 🐳 Docker Deployment | Docker 部署

### Using Docker Compose (Recommended)

```bash
# 建構並啟動所有服務
docker-compose up -d

# 檢查狀態
docker-compose ps

# 查看日誌
docker-compose logs -f

# 停止服務
docker-compose down
```

`docker-compose.yml` 會啟動：
- **MCP SSE Server**: port 8000
- **REST API Server**: port 8080

### Using Docker Directly

```bash
# 建構映像
docker build -t medical-calc-mcp .

# 執行 MCP SSE 模式
docker run -d -p 8000:8000 --name mcp-sse \
  -e MCP_MODE=sse \
  medical-calc-mcp

# 執行 REST API 模式
docker run -d -p 8080:8080 --name mcp-api \
  medical-calc-mcp python src/main.py --mode api --port 8080
```

### Environment Variables | 環境變數

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_MODE` | `stdio` | 傳輸模式 (stdio, sse, http, api) |
| `MCP_HOST` | `0.0.0.0` | 綁定主機 |
| `MCP_PORT` | `8000` | 綁定埠號 |
| `API_PORT` | `8080` | REST API 埠號 |
| `LOG_LEVEL` | `INFO` | 日誌級別 |
| `DEBUG` | `false` | 除錯模式 |

---

## 🔒 HTTPS Deployment | HTTPS 部署

為生產環境提供安全的 HTTPS 連線，支援多種憑證配置方式。

Secure HTTPS connections for production with flexible certificate configuration.

### Architecture | 架構

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SSL/TLS 配置方式                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  方式 1: Docker + Nginx (推薦生產環境)                                       │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Client (HTTPS) → Nginx (TLS 終止) → App (HTTP 內部)                   │ │
│  │  憑證位置: 透過 volume 掛載至 /etc/nginx/ssl/                           │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  方式 2: 本地開發 (Python/Uvicorn 原生 SSL)                                  │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Client (HTTPS) → Python/Uvicorn (直接 SSL)                            │ │
│  │  憑證位置: 透過 --ssl-keyfile, --ssl-certfile 或環境變數指定             │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  方式 3: 直接 MCP Server SSL (無 Nginx)                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Client (HTTPS) → MCP Server (內建 SSL)                                │ │
│  │  憑證位置: 透過環境變數 SSL_KEYFILE, SSL_CERTFILE 指定                   │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Quick Start | 快速開始

```bash
# 1. 生成 SSL 憑證 (自簽，供開發使用)
./scripts/generate-ssl-certs.sh

# 2. 啟動 HTTPS 服務 (Docker + Nginx)
./scripts/start-https-docker.sh up

# 或本地啟動 (Python 原生 SSL)
./scripts/start-https-local.sh
```

### SSL 環境變數 | SSL Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SSL_ENABLED` | `false` | 啟用 SSL/TLS (`true`, `false`) |
| `SSL_KEYFILE` | - | SSL 私鑰檔案路徑 |
| `SSL_CERTFILE` | - | SSL 憑證檔案路徑 |
| `SSL_CA_CERTS` | - | CA 憑證檔案路徑 (選填，用於客戶端驗證) |
| `SSL_DIR` | `./nginx/ssl` | Docker SSL 憑證目錄 (docker-compose 專用) |

### 方式 1: Docker + Nginx (推薦)

最安全的生產環境配置，Nginx 處理 TLS 終止。

#### 使用預設憑證

```bash
# 生成自簽憑證
./scripts/generate-ssl-certs.sh

# 啟動服務
docker-compose -f docker-compose.https.yml up -d
```

#### 使用自訂憑證路徑

**方法 A: 環境變數**

```bash
# 指定憑證目錄
SSL_DIR=/path/to/your/certs docker-compose -f docker-compose.https.yml up -d

# 使用 Let's Encrypt
SSL_DIR=/etc/letsencrypt/live/example.com docker-compose -f docker-compose.https.yml up -d
```

**方法 B: 修改 docker-compose.https.yml**

```yaml
nginx:
  volumes:
    - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    # 修改為您的憑證路徑
    - /path/to/your/certs:/etc/nginx/ssl:ro
```

**方法 C: 修改 nginx/nginx.conf (Let's Encrypt)**

```nginx
# 取消註解並修改以下行
ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
```

### 方式 2: 本地開發 (Python 原生 SSL)

不使用 Docker，直接在 Python/Uvicorn 啟用 SSL。

#### 使用預設憑證

```bash
./scripts/start-https-local.sh
```

#### 使用自訂憑證

**方法 A: 環境變數**

```bash
# 指定憑證路徑
SSL_KEYFILE=/path/to/server.key \
SSL_CERTFILE=/path/to/server.crt \
./scripts/start-https-local.sh

# 也可以指定埠號
SSL_KEYFILE=/path/to/key.pem \
SSL_CERTFILE=/path/to/cert.pem \
MCP_PORT=9000 \
API_PORT=9001 \
./scripts/start-https-local.sh
```

**方法 B: 命令列參數**

```bash
# MCP SSE Server
python -m src.main --mode sse --port 8443 \
    --ssl-keyfile /path/to/server.key \
    --ssl-certfile /path/to/server.crt

# REST API Server (使用 uvicorn)
uv run uvicorn src.infrastructure.api.server:create_api_app \
    --factory \
    --host 0.0.0.0 \
    --port 9443 \
    --ssl-keyfile /path/to/server.key \
    --ssl-certfile /path/to/server.crt
```

### 方式 3: Docker 直接 SSL (無 Nginx)

容器內直接處理 SSL，適合簡單部署。

```yaml
# docker-compose-direct-ssl.yml (自行建立)
services:
  medical-calc-mcp:
    build: .
    ports:
      - "8443:8443"
    environment:
      - MCP_MODE=sse
      - MCP_PORT=8443
      - SSL_ENABLED=true
      - SSL_KEYFILE=/certs/server.key
      - SSL_CERTFILE=/certs/server.crt
    volumes:
      - /path/to/your/certs:/certs:ro
    command: >
      python -m src.main --mode sse --port 8443
      --ssl-keyfile /certs/server.key
      --ssl-certfile /certs/server.crt
```

### HTTPS Endpoints | HTTPS 端點

**Docker + Nginx:**

| Service | URL | Description |
|---------|-----|-------------|
| MCP SSE | `https://localhost/` | MCP Server-Sent Events |
| MCP SSE | `https://localhost/sse` | SSE connection |
| REST API | `https://localhost:8443/` | REST API root |
| Swagger UI | `https://localhost:8443/docs` | API documentation |

**本地開發 (預設埠號):**

| Service | URL | Description |
|---------|-----|-------------|
| MCP SSE | `https://localhost:8443/` | MCP Server |
| REST API | `https://localhost:9443/` | REST API |

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

### Production with Let's Encrypt

```bash
# 1. 取得 Let's Encrypt 憑證
sudo certbot certonly --webroot -w /var/www/certbot \
  -d your-domain.com -d api.your-domain.com

# 2. 修改 docker-compose.https.yml
# volumes:
#   - /etc/letsencrypt/live/your-domain.com:/etc/nginx/ssl:ro

# 3. 修改 nginx/nginx.conf
# ssl_certificate /etc/nginx/ssl/fullchain.pem;
# ssl_certificate_key /etc/nginx/ssl/privkey.pem;

# 4. 啟動服務
docker-compose -f docker-compose.https.yml up -d
```

### Trust Self-Signed Certificates | 信任自簽憑證

開發環境使用自簽憑證時，需將 CA 憑證加入系統信任。

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
1. 雙擊 nginx/ssl/ca.crt
2. 安裝憑證 → 本機電腦 → 受信任的根憑證授權
```

### Files | 相關檔案

| File | Description |
|------|-------------|
| `nginx/nginx.conf` | Nginx HTTPS 配置 (TLS 終止) |
| `docker-compose.https.yml` | Docker HTTPS 編排 |
| `scripts/generate-ssl-certs.sh` | 自簽 SSL 憑證生成 |
| `scripts/start-https-docker.sh` | Docker HTTPS 啟動腳本 |
| `scripts/start-https-local.sh` | 本地 HTTPS 啟動腳本 |
| `src/infrastructure/mcp/config.py` | SSL 配置類 (SslConfig) |

### SSL 配置參考表

| 情境 | 憑證位置 | 配置方式 |
|------|---------|---------|
| Docker 開發 | `nginx/ssl/` | 預設 (無需配置) |
| Docker + 自訂憑證 | 任意路徑 | `SSL_DIR` 環境變數或修改 volumes |
| Docker + Let's Encrypt | `/etc/letsencrypt/...` | 修改 `nginx/nginx.conf` |
| 本地開發 | `nginx/ssl/` | 預設 (無需配置) |
| 本地 + 自訂憑證 | 任意路徑 | `SSL_KEYFILE` + `SSL_CERTFILE` 環境變數 |
| 命令列 | 任意路徑 | `--ssl-keyfile` + `--ssl-certfile` 參數 |

> 📖 更多詳細說明請參考 [README.md HTTPS Deployment](../README.md#-https-deployment--https-部署--new)

---

## ☁️ Cloud Deployment | 雲端部署

### AWS ECS / Fargate

```yaml
# task-definition.json
{
  "family": "medical-calc-mcp",
  "containerDefinitions": [
    {
      "name": "mcp-api",
      "image": "your-ecr-repo/medical-calc-mcp:latest",
      "portMappings": [
        {"containerPort": 8080, "protocol": "tcp"}
      ],
      "command": ["python", "src/main.py", "--mode", "api", "--port", "8080"],
      "environment": [
        {"name": "LOG_LEVEL", "value": "INFO"}
      ]
    }
  ]
}
```

### Google Cloud Run

```bash
# 建構並推送到 GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/medical-calc-mcp

# 部署
gcloud run deploy medical-calc-mcp \
  --image gcr.io/PROJECT_ID/medical-calc-mcp \
  --platform managed \
  --port 8080 \
  --allow-unauthenticated
```

### Azure Container Instances

```bash
az container create \
  --resource-group myResourceGroup \
  --name medical-calc-mcp \
  --image your-registry/medical-calc-mcp:latest \
  --ports 8080 \
  --environment-variables MCP_MODE=api
```

---

## 🤖 Agent Integration Examples | Agent 整合範例

### Python Agent

```python
import requests
from typing import Any, Dict, Optional

class MedicalCalculatorClient:
    """Client for Medical Calculator MCP Server REST API"""

    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/api/v1"

    def health_check(self) -> bool:
        """Check if server is healthy"""
        try:
            r = requests.get(f"{self.base_url}/health", timeout=5)
            return r.status_code == 200
        except:
            return False

    def list_calculators(self) -> list:
        """List all available calculators"""
        r = requests.get(f"{self.api_url}/calculators")
        r.raise_for_status()
        return r.json()

    def search(self, query: str) -> list:
        """Search calculators by keyword"""
        r = requests.get(f"{self.api_url}/search", params={"q": query})
        r.raise_for_status()
        return r.json()

    def get_calculator_info(self, tool_id: str) -> dict:
        """Get detailed info about a calculator"""
        r = requests.get(f"{self.api_url}/calculators/{tool_id}")
        r.raise_for_status()
        return r.json()

    def calculate(self, tool_id: str, params: Dict[str, Any]) -> dict:
        """Execute a calculation"""
        r = requests.post(
            f"{self.api_url}/calculate/{tool_id}",
            json={"params": params}
        )
        r.raise_for_status()
        return r.json()


# Usage Example
if __name__ == "__main__":
    client = MedicalCalculatorClient()

    # Check health
    if not client.health_check():
        raise RuntimeError("Server not available")

    # Search for sepsis-related calculators
    results = client.search("sepsis")
    print(f"Found {len(results)} calculators")

    # Calculate SOFA score
    result = client.calculate("sofa", {
        "pao2_fio2_ratio": 200,
        "platelets": 100,
        "bilirubin": 2.0,
        "gcs_score": 13,
        "creatinine": 2.5
    })
    print(f"SOFA Score: {result}")
```

### LangChain Integration

```python
from langchain.tools import tool
import requests

BASE_URL = "http://localhost:8080/api/v1"

@tool
def calculate_sofa(
    pao2_fio2_ratio: float,
    platelets: float,
    bilirubin: float,
    gcs_score: int,
    creatinine: float
) -> str:
    """
    Calculate SOFA (Sequential Organ Failure Assessment) score.
    Used to assess organ dysfunction in critically ill patients.

    Args:
        pao2_fio2_ratio: PaO2/FiO2 ratio (mmHg)
        platelets: Platelet count (×10³/µL)
        bilirubin: Total bilirubin (mg/dL)
        gcs_score: Glasgow Coma Scale (3-15)
        creatinine: Serum creatinine (mg/dL)

    Returns:
        SOFA score with interpretation
    """
    r = requests.post(
        f"{BASE_URL}/calculate/sofa",
        json={
            "params": {
                "pao2_fio2_ratio": pao2_fio2_ratio,
                "platelets": platelets,
                "bilirubin": bilirubin,
                "gcs_score": gcs_score,
                "creatinine": creatinine
            }
        }
    )
    result = r.json()
    return f"SOFA Score: {result['result']['value']} - {result['result']['interpretation']['summary']}"


@tool
def search_medical_calculators(query: str) -> str:
    """
    Search for medical calculators by keyword.

    Args:
        query: Search keyword (e.g., "sepsis", "kidney", "cardiac")

    Returns:
        List of matching calculators
    """
    r = requests.get(f"{BASE_URL}/search", params={"q": query})
    results = r.json()
    return "\n".join([f"- {c['tool_id']}: {c['description']}" for c in results[:5]])
```

### OpenAI Function Calling

```python
import openai
import requests
import json

# Define functions for OpenAI
functions = [
    {
        "name": "calculate_medical_score",
        "description": "Calculate a medical score using the medical calculator server",
        "parameters": {
            "type": "object",
            "properties": {
                "calculator": {
                    "type": "string",
                    "description": "Calculator ID (e.g., 'sofa', 'gcs', 'ckd_epi_2021')"
                },
                "params": {
                    "type": "object",
                    "description": "Calculator parameters"
                }
            },
            "required": ["calculator", "params"]
        }
    }
]

def execute_function(name: str, args: dict) -> str:
    """Execute a function call from OpenAI"""
    if name == "calculate_medical_score":
        r = requests.post(
            f"http://localhost:8080/api/v1/calculate/{args['calculator']}",
            json={"params": args["params"]}
        )
        return json.dumps(r.json())
    return "Unknown function"

# Use with OpenAI
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Calculate SOFA score for a patient with PaO2/FiO2=200, platelets=100, bilirubin=2, GCS=13, creatinine=2.5"}],
    functions=functions,
    function_call="auto"
)
```

---

## 🔐 Security Considerations | 安全考量

### Security Features | 安全特性

本專案已實施多層安全機制：

| Layer | Feature | Status |
|-------|---------|--------|
| **HTTPS** | TLS 1.2/1.3 encryption | ✅ Implemented |
| **Rate Limiting** | Nginx: 30 req/s API, 60 req/s MCP | ✅ Implemented |
| **Security Headers** | X-Frame-Options, X-Content-Type-Options, X-XSS-Protection | ✅ Implemented |
| **Input Validation** | 3-layer: Pydantic → ParameterValidator → Domain | ✅ Implemented |
| **CORS** | Configurable origins via environment variable | ✅ Implemented |
| **No Database** | Stateless, in-memory only | ✅ No SQL injection |

### Production Recommendations

| Item | Recommendation | How |
|------|----------------|-----|
| **HTTPS** | ✅ Use provided Nginx + SSL | `./scripts/start-https-docker.sh up` |
| **Certificates** | Use Let's Encrypt for production | See HTTPS Deployment section |
| **CORS** | Restrict origins | `CORS_ORIGINS="https://your-app.com"` |
| **Authentication** | Add API Key or OAuth2 if needed | Nginx or application layer |
| **Network** | Run in private VPC | Cloud provider configuration |
| **Monitoring** | Enable access logging | Already configured in Nginx |

### Example: Adding API Key Authentication

```nginx
# In nginx/nginx.conf, add to location blocks:
location /api/ {
    # Check for API key header
    if ($http_x_api_key != "your-secret-key") {
        return 401;
    }

    proxy_pass http://api_backend/;
    # ... other settings
}
```

### Example: Adding Basic Auth with Nginx

```bash
# Create password file
sudo htpasswd -c /etc/nginx/.htpasswd admin
```

```nginx
# In nginx/nginx.conf:
location / {
    auth_basic "Medical Calculator API";
    auth_basic_user_file /etc/nginx/.htpasswd;

    proxy_pass http://localhost:8080;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

---

## 🔧 Troubleshooting | 疑難排解

### Common Issues | 常見問題

**1. Port already in use | 埠號已被佔用**
```bash
# 找出佔用埠號的程序
lsof -i :8080
# 或使用其他埠號
python src/main.py --mode api --port 8081
```

**2. Module not found | 找不到模組**
```bash
# 確保在專案根目錄
cd /path/to/medical-calc-mcp
# 重新安裝依賴並同步環境
uv sync
```

**3. Docker build fails | Docker 建構失敗**
```bash
# 清理並重建
docker-compose down
docker system prune -f
docker-compose build --no-cache
docker-compose up -d
```

**4. Connection refused | 連接被拒絕**
```bash
# 檢查服務是否運行
curl http://localhost:8080/health
# 檢查防火牆
sudo ufw allow 8080
```

### Getting Help | 取得協助

- GitHub Issues: https://github.com/u9401066/medical-calc-mcp/issues
- Documentation: 本專案 `/docs` 目錄

---

## 📚 Related Documents | 相關文件

- [README.md](../README.md) - 專案概述
- [ROADMAP.md](../ROADMAP.md) - 開發路線圖
- [CONTRIBUTING.md](../CONTRIBUTING.md) - 貢獻指南
- [examples/](../examples/) - 使用範例
