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
- [Cloud Deployment | 雲端部署](#-cloud-deployment--雲端部署)
- [Agent Integration Examples | Agent 整合範例](#-agent-integration-examples--agent-整合範例)
- [Security Considerations | 安全考量](#-security-considerations--安全考量)
- [Troubleshooting | 疑難排解](#-troubleshooting--疑難排解)

---

## 🎯 Deployment Modes Overview | 部署模式總覽

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
│ ✅ Scripts      │                 │                                 │
└─────────────────┴─────────────────┴─────────────────────────────────┘
```

| Mode | Protocol | Port | Best For |
|------|----------|------|----------|
| **api** | HTTP REST | 8080 | Custom agents, web apps, any HTTP client |
| **sse** | MCP over SSE | 8000 | Remote MCP clients, Docker deployment |
| **stdio** | MCP stdio | - | Local Claude Desktop, VS Code Copilot |

---

## 🌐 Mode 1: REST API (Recommended for Custom Agents)

最通用的整合方式，任何能發送 HTTP 請求的應用程式都可使用。

### Quick Start | 快速開始

```bash
# 安裝依賴
pip install -r requirements.txt

# 啟動 REST API 伺服器
python src/main.py --mode api --port 8080

# 或使用 uvicorn（生產環境）
uvicorn src.infrastructure.api.server:app --host 0.0.0.0 --port 8080 --workers 4
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

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | 伺服器資訊 |
| `/health` | GET | 健康檢查 |
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
pip install "mcp[cli]"
mcp dev src/infrastructure/mcp/server.py
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

### Production Recommendations

1. **使用 HTTPS**: 在生產環境中使用 TLS/SSL
2. **API 認證**: 考慮加入 API Key 或 OAuth2
3. **速率限制**: 防止濫用
4. **輸入驗證**: 伺服器已包含三層驗證
5. **日誌審計**: 記錄所有計算請求

### Example: Adding Basic Auth with Nginx

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        auth_basic "Medical Calculator API";
        auth_basic_user_file /etc/nginx/.htpasswd;
        
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
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
# 啟動虛擬環境
source .venv/bin/activate
# 重新安裝依賴
pip install -r requirements.txt
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
