#!/bin/bash
# =============================================================================
# start-https-local.sh - 本地 HTTPS 啟動腳本 (不使用 Docker)
# =============================================================================
#
# 使用 Uvicorn 原生 SSL 支援直接啟動 HTTPS 服務，或使用 Python main.py
# 並提供環境變數支援自訂憑證路徑。
#
# 使用方式：
#   chmod +x scripts/start-https-local.sh
#   ./scripts/start-https-local.sh              # 使用預設路徑
#   ./scripts/start-https-local.sh sse          # 只啟動 MCP SSE
#   ./scripts/start-https-local.sh api          # 只啟動 REST API
#
# 環境變數 (可選，用於自訂憑證路徑)：
#   SSL_KEYFILE   - SSL 私鑰檔案路徑 (預設: nginx/ssl/server.key)
#   SSL_CERTFILE  - SSL 憑證檔案路徑 (預設: nginx/ssl/server.crt)
#   MCP_PORT      - MCP SSE 伺服器埠號 (預設: 8443)
#   API_PORT      - REST API 伺服器埠號 (預設: 9443)
#
# 範例：
#   # 使用自訂憑證路徑
#   SSL_KEYFILE=/etc/ssl/private/my.key SSL_CERTFILE=/etc/ssl/certs/my.crt ./scripts/start-https-local.sh
#
#   # 使用自訂埠號
#   MCP_PORT=9000 API_PORT=9001 ./scripts/start-https-local.sh
#
# 前置需求：
#   1. 已安裝依賴：uv sync
#   2. 已生成憑證：./scripts/generate-ssl-certs.sh (或使用自訂憑證)
#
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 預設 SSL 憑證路徑 (可透過環境變數覆蓋)
DEFAULT_SSL_DIR="$PROJECT_ROOT/nginx/ssl"
SSL_KEYFILE="${SSL_KEYFILE:-$DEFAULT_SSL_DIR/server.key}"
SSL_CERTFILE="${SSL_CERTFILE:-$DEFAULT_SSL_DIR/server.crt}"

# 預設埠號 (可透過環境變數覆蓋)
MCP_PORT="${MCP_PORT:-8443}"
API_PORT="${API_PORT:-9443}"

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

cd "$PROJECT_ROOT"

echo -e "${GREEN}🔐 Medical Calculator MCP - HTTPS 本地啟動${NC}"
echo "============================================"
echo -e "SSL 私鑰:  ${YELLOW}$SSL_KEYFILE${NC}"
echo -e "SSL 憑證:  ${YELLOW}$SSL_CERTFILE${NC}"
echo "============================================"

# 檢查 SSL 憑證
if [ ! -f "$SSL_KEYFILE" ] || [ ! -f "$SSL_CERTFILE" ]; then
    echo -e "${YELLOW}⚠️  SSL 憑證不存在${NC}"
    
    # 如果使用預設路徑，嘗試自動生成
    if [ "$SSL_KEYFILE" = "$DEFAULT_SSL_DIR/server.key" ]; then
        echo -e "${YELLOW}   正在使用預設路徑，嘗試自動生成...${NC}"
        bash "$SCRIPT_DIR/generate-ssl-certs.sh"
    else
        echo -e "${RED}❌ 請確認憑證檔案存在：${NC}"
        echo -e "   私鑰: $SSL_KEYFILE"
        echo -e "   憑證: $SSL_CERTFILE"
        echo ""
        echo -e "您可以："
        echo -e "  1. 使用預設憑證: unset SSL_KEYFILE SSL_CERTFILE && ./scripts/start-https-local.sh"
        echo -e "  2. 生成自簽憑證: ./scripts/generate-ssl-certs.sh"
        echo -e "  3. 確認自訂憑證路徑正確"
        exit 1
    fi
fi

# 檢查 Python 依賴 (使用 uv)
if ! command -v uv &> /dev/null; then
    echo -e "${RED}❌ 需要安裝 uv 套件管理器${NC}"
    echo "請執行: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

if ! uv run python -c "import uvicorn" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  缺少依賴，正在安裝...${NC}"
    uv sync
fi

# 解析參數
MODE="${1:-both}"  # sse, api, both

# 儲存 PID 以便清理
MCP_PID=""
API_PID=""

start_mcp_sse() {
    echo -e "${BLUE}🚀 啟動 MCP SSE Server (HTTPS, port $MCP_PORT)...${NC}"
    
    # 使用 main.py 並透過命令列參數傳遞 SSL 設定
    uv run python -m src.main \
        --mode sse \
        --host 0.0.0.0 \
        --port "$MCP_PORT" \
        --ssl-keyfile "$SSL_KEYFILE" \
        --ssl-certfile "$SSL_CERTFILE" &
    MCP_PID=$!
    
    echo -e "${GREEN}✅ MCP SSE: https://localhost:$MCP_PORT/${NC}"
}

start_rest_api() {
    echo -e "${BLUE}🚀 啟動 REST API Server (HTTPS, port $API_PORT)...${NC}"
    
    # REST API 使用 uvicorn 直接啟動
    uv run uvicorn src.infrastructure.api.server:create_api_app \
        --factory \
        --host 0.0.0.0 \
        --port "$API_PORT" \
        --ssl-keyfile "$SSL_KEYFILE" \
        --ssl-certfile "$SSL_CERTFILE" \
        --log-level info &
    API_PID=$!
    
    echo -e "${GREEN}✅ REST API: https://localhost:$API_PORT/${NC}"
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
        echo ""
        echo "環境變數："
        echo "  SSL_KEYFILE   - SSL 私鑰檔案路徑"
        echo "  SSL_CERTFILE  - SSL 憑證檔案路徑"
        echo "  MCP_PORT      - MCP SSE 伺服器埠號 (預設: 8443)"
        echo "  API_PORT      - REST API 伺服器埠號 (預設: 9443)"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}🔐 HTTPS 服務已啟動${NC}"
echo ""
echo "設定："
echo -e "  SSL 私鑰:  ${YELLOW}$SSL_KEYFILE${NC}"
echo -e "  SSL 憑證:  ${YELLOW}$SSL_CERTFILE${NC}"
echo ""
echo "端點："
case "$MODE" in
    sse)
        echo "  MCP SSE:  https://localhost:$MCP_PORT/"
        ;;
    api)
        echo "  REST API: https://localhost:$API_PORT/"
        echo "  API Docs: https://localhost:$API_PORT/docs"
        ;;
    both)
        echo "  MCP SSE:  https://localhost:$MCP_PORT/"
        echo "  REST API: https://localhost:$API_PORT/"
        echo "  API Docs: https://localhost:$API_PORT/docs"
        ;;
esac
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止服務${NC}"
echo -e "${GREEN}============================================${NC}"

# 等待所有後台進程
wait
