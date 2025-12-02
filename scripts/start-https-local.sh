#!/bin/bash
# =============================================================================
# start-https-local.sh - 本地 HTTPS 啟動腳本 (不使用 Docker)
# =============================================================================
#
# 使用 Uvicorn 原生 SSL 支援直接啟動 HTTPS 服務
#
# 使用方式：
#   chmod +x scripts/start-https-local.sh
#   ./scripts/start-https-local.sh
#
# 前置需求：
#   1. 已安裝依賴：pip install -r requirements.txt
#   2. 已生成憑證：./scripts/generate-ssl-certs.sh
#
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SSL_DIR="$PROJECT_ROOT/nginx/ssl"

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

cd "$PROJECT_ROOT"

echo -e "${GREEN}🔐 Medical Calculator MCP - HTTPS 本地啟動${NC}"
echo "============================================"

# 檢查 SSL 憑證
if [ ! -f "$SSL_DIR/server.crt" ] || [ ! -f "$SSL_DIR/server.key" ]; then
    echo -e "${YELLOW}⚠️  SSL 憑證不存在，正在生成...${NC}"
    bash "$SCRIPT_DIR/generate-ssl-certs.sh"
fi

# 檢查 Python 依賴
if ! python -c "import uvicorn" 2>/dev/null; then
    echo -e "${RED}❌ 缺少依賴，請先執行: pip install -r requirements.txt${NC}"
    exit 1
fi

# 解析參數
MODE="${1:-both}"  # sse, api, both

start_mcp_sse() {
    echo -e "${BLUE}🚀 啟動 MCP SSE Server (HTTPS, port 8443)...${NC}"
    uvicorn src.infrastructure.mcp.server:create_app \
        --factory \
        --host 0.0.0.0 \
        --port 8443 \
        --ssl-keyfile "$SSL_DIR/server.key" \
        --ssl-certfile "$SSL_DIR/server.crt" \
        --log-level info &
    MCP_PID=$!
    echo -e "${GREEN}✅ MCP SSE: https://localhost:8443/${NC}"
}

start_rest_api() {
    echo -e "${BLUE}🚀 啟動 REST API Server (HTTPS, port 9443)...${NC}"
    uvicorn src.infrastructure.api.server:create_api_app \
        --factory \
        --host 0.0.0.0 \
        --port 9443 \
        --ssl-keyfile "$SSL_DIR/server.key" \
        --ssl-certfile "$SSL_DIR/server.crt" \
        --log-level info &
    API_PID=$!
    echo -e "${GREEN}✅ REST API: https://localhost:9443/${NC}"
}

cleanup() {
    echo -e "\n${YELLOW}🛑 正在關閉服務...${NC}"
    [ -n "$MCP_PID" ] && kill $MCP_PID 2>/dev/null
    [ -n "$API_PID" ] && kill $API_PID 2>/dev/null
    echo -e "${GREEN}✅ 服務已關閉${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

case "$MODE" in
    sse)
        start_mcp_sse
        ;;
    api)
        start_rest_api
        ;;
    both)
        start_mcp_sse
        sleep 1
        start_rest_api
        ;;
    *)
        echo "Usage: $0 [sse|api|both]"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}🔐 HTTPS 服務已啟動${NC}"
echo ""
echo "端點："
case "$MODE" in
    sse)
        echo "  MCP SSE:  https://localhost:8443/"
        ;;
    api)
        echo "  REST API: https://localhost:9443/"
        echo "  API Docs: https://localhost:9443/docs"
        ;;
    both)
        echo "  MCP SSE:  https://localhost:8443/"
        echo "  REST API: https://localhost:9443/"
        echo "  API Docs: https://localhost:9443/docs"
        ;;
esac
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止服務${NC}"
echo -e "${GREEN}============================================${NC}"

# 等待所有後台進程
wait
