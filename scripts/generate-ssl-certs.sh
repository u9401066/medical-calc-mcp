#!/bin/bash
# =============================================================================
# generate-ssl-certs.sh - 生成本地開發用 SSL 憑證
# =============================================================================
#
# 用途：為本地開發環境生成自簽 SSL 憑證
#
# 使用方式：
#   chmod +x scripts/generate-ssl-certs.sh
#   ./scripts/generate-ssl-certs.sh
#
# 產出：
#   - nginx/ssl/server.key  (私鑰)
#   - nginx/ssl/server.crt  (憑證)
#   - nginx/ssl/ca.crt      (CA 憑證，可匯入瀏覽器信任)
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
NC='\033[0m' # No Color

echo -e "${GREEN}🔐 生成本地開發用 SSL 憑證${NC}"
echo "============================================"

# 建立 SSL 目錄
mkdir -p "$SSL_DIR"

# 檢查 OpenSSL
if ! command -v openssl &> /dev/null; then
    echo -e "${RED}❌ 錯誤: 需要安裝 OpenSSL${NC}"
    echo "請執行: sudo apt-get install openssl (Ubuntu/Debian)"
    echo "或: brew install openssl (macOS)"
    exit 1
fi

# 配置
DAYS_VALID=365
COUNTRY="TW"
STATE="Taiwan"
CITY="Taipei"
ORG="Medical Calculator MCP"
OU="Development"
CN="localhost"

# 額外的 SAN (Subject Alternative Names)
# 支援多種本地存取方式
cat > "$SSL_DIR/openssl.cnf" << EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
x509_extensions = v3_req
distinguished_name = dn

[dn]
C = $COUNTRY
ST = $STATE
L = $CITY
O = $ORG
OU = $OU
CN = $CN

[v3_req]
subjectAltName = @alt_names
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth

[alt_names]
DNS.1 = localhost
DNS.2 = *.localhost
DNS.3 = medical-calc-mcp
DNS.4 = medical-calc-api
DNS.5 = host.docker.internal
IP.1 = 127.0.0.1
IP.2 = ::1
IP.3 = 0.0.0.0
EOF

echo -e "${YELLOW}📝 生成 CA 私鑰...${NC}"
openssl genrsa -out "$SSL_DIR/ca.key" 4096

echo -e "${YELLOW}📝 生成 CA 憑證...${NC}"
openssl req -new -x509 -days $DAYS_VALID -key "$SSL_DIR/ca.key" -out "$SSL_DIR/ca.crt" \
    -subj "/C=$COUNTRY/ST=$STATE/L=$CITY/O=$ORG/OU=Certificate Authority/CN=Medical Calc Dev CA"

echo -e "${YELLOW}📝 生成伺服器私鑰...${NC}"
openssl genrsa -out "$SSL_DIR/server.key" 2048

echo -e "${YELLOW}📝 生成憑證簽署請求 (CSR)...${NC}"
openssl req -new -key "$SSL_DIR/server.key" -out "$SSL_DIR/server.csr" \
    -config "$SSL_DIR/openssl.cnf"

echo -e "${YELLOW}📝 使用 CA 簽署伺服器憑證...${NC}"
openssl x509 -req -days $DAYS_VALID \
    -in "$SSL_DIR/server.csr" \
    -CA "$SSL_DIR/ca.crt" \
    -CAkey "$SSL_DIR/ca.key" \
    -CAcreateserial \
    -out "$SSL_DIR/server.crt" \
    -extensions v3_req \
    -extfile "$SSL_DIR/openssl.cnf"

# 清理臨時文件
rm -f "$SSL_DIR/server.csr" "$SSL_DIR/openssl.cnf" "$SSL_DIR/ca.srl"

# 設定權限
chmod 600 "$SSL_DIR/server.key" "$SSL_DIR/ca.key"
chmod 644 "$SSL_DIR/server.crt" "$SSL_DIR/ca.crt"

echo ""
echo -e "${GREEN}✅ SSL 憑證生成完成！${NC}"
echo "============================================"
echo -e "憑證位置: ${YELLOW}$SSL_DIR${NC}"
echo ""
echo "生成的文件："
ls -la "$SSL_DIR"
echo ""
echo -e "${YELLOW}📌 如何信任此憑證 (消除瀏覽器警告)：${NC}"
echo ""
echo "Linux (Ubuntu/Debian):"
echo "  sudo cp $SSL_DIR/ca.crt /usr/local/share/ca-certificates/medical-calc-dev.crt"
echo "  sudo update-ca-certificates"
echo ""
echo "macOS:"
echo "  sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain $SSL_DIR/ca.crt"
echo ""
echo "Windows:"
echo "  雙擊 ca.crt → 安裝憑證 → 本機電腦 → 受信任的根憑證授權"
echo ""
echo -e "${GREEN}🚀 現在可以啟動 HTTPS 服務：${NC}"
echo "  Docker:  docker-compose -f docker-compose.https.yml up -d"
echo "  本地:    ./scripts/start-https-local.sh"
echo ""
echo "存取位址："
echo "  MCP SSE:  https://localhost/"
echo "  REST API: https://localhost:8443/"
