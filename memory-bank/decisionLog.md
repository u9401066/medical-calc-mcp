# Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-12-01 | CORS 設定改為環境變數控制，生產環境需設定 CORS_ORIGINS | 預設 allow_origins=['*'] 過於寬鬆，生產環境需要限制來源以防止 CSRF 攻擊 |
| 2025-12-02 | Implement HTTPS support using Nginx reverse proxy with self-signed SSL certificates for development | Security requirement for production deployment. Nginx provides TLS termination, rate limiting, and SSE optimization. Self-signed certs for development, Let's Encrypt for production. Two deployment options: Docker (nginx + services) or Local (Uvicorn SSL direct). |
| 2025-12-03 | Simplified main.py to use FastMCP built-in SSE/HTTP transport instead of custom Starlette implementation | FastMCP SDK already provides complete SSE and HTTP transport support via host/port parameters in FastMCP constructor. The previous custom implementation was redundant and buggy. New approach: pass host/port to McpServerConfig, which passes to FastMCP init, then call server.run(transport='sse') to use built-in uvicorn server. |
| 2025-12-03 | Health checks use /sse endpoint instead of /health for MCP SSE mode | FastMCP SSE mode only provides /sse and /messages/ endpoints. There is no /health endpoint. Docker, CI, and docker-compose health checks updated to curl /sse with -sf flags. REST API mode (port 8080) still has /health via FastAPI. |
