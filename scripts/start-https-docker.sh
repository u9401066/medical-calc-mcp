#!/bin/bash
# =============================================================================
# start-https-docker.sh - Docker HTTPS 快速啟動腳本
# =============================================================================
#
# 使用方式：
#   chmod +x scripts/start-https-docker.sh
#   ./scripts/start-https-docker.sh
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
NC='\033[0m'

cd "$PROJECT_ROOT"

echo -e "${GREEN}🐳 Medical Calculator MCP - Docker HTTPS 啟動${NC}"
echo "============================================"

# 檢查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ 錯誤: 需要安裝 Docker${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ 錯誤: 需要安裝 Docker Compose${NC}"
    exit 1
fi

# 檢查 SSL 憑證
if [ ! -f "$SSL_DIR/server.crt" ] || [ ! -f "$SSL_DIR/server.key" ]; then
    echo -e "${YELLOW}⚠️  SSL 憑證不存在，正在生成...${NC}"
    bash "$SCRIPT_DIR/generate-ssl-certs.sh"
fi

# 解析參數
ACTION="${1:-up}"

case "$ACTION" in
    up)
        echo -e "${GREEN}🚀 啟動 HTTPS 服務...${NC}"
        if docker compose version &> /dev/null; then
            docker compose -f docker-compose.https.yml up -d --build
        else
            docker-compose -f docker-compose.https.yml up -d --build
        fi
        echo ""
        echo -e "${GREEN}✅ 服務已啟動！${NC}"
        echo ""
        echo "端點："
        echo "  MCP SSE:  https://localhost/"
        echo "  REST API: https://localhost:8443/"
        echo "  API Docs: https://localhost:8443/docs"
        echo ""
        echo "查看日誌: docker-compose -f docker-compose.https.yml logs -f"
        ;;
    down)
        echo -e "${YELLOW}🛑 停止服務...${NC}"
        if docker compose version &> /dev/null; then
            docker compose -f docker-compose.https.yml down
        else
            docker-compose -f docker-compose.https.yml down
        fi
        echo -e "${GREEN}✅ 服務已停止${NC}"
        ;;
    logs)
        if docker compose version &> /dev/null; then
            docker compose -f docker-compose.https.yml logs -f
        else
            docker-compose -f docker-compose.https.yml logs -f
        fi
        ;;
    restart)
        echo -e "${YELLOW}🔄 重啟服務...${NC}"
        if docker compose version &> /dev/null; then
            docker compose -f docker-compose.https.yml restart
        else
            docker-compose -f docker-compose.https.yml restart
        fi
        echo -e "${GREEN}✅ 服務已重啟${NC}"
        ;;
    status)
        if docker compose version &> /dev/null; then
            docker compose -f docker-compose.https.yml ps
        else
            docker-compose -f docker-compose.https.yml ps
        fi
        ;;
    *)
        echo "Usage: $0 [up|down|logs|restart|status]"
        echo ""
        echo "Commands:"
        echo "  up      - 啟動 HTTPS 服務 (預設)"
        echo "  down    - 停止服務"
        echo "  logs    - 查看日誌"
        echo "  restart - 重啟服務"
        echo "  status  - 查看服務狀態"
        exit 1
        ;;
esac
