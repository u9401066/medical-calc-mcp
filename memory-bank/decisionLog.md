# Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-12-01 | CORS 設定改為環境變數控制，生產環境需設定 CORS_ORIGINS | 預設 allow_origins=['*'] 過於寬鬆，生產環境需要限制來源以防止 CSRF 攻擊 |
| 2025-12-02 | Implement HTTPS support using Nginx reverse proxy with self-signed SSL certificates for development | Security requirement for production deployment. Nginx provides TLS termination, rate limiting, and SSE optimization. Self-signed certs for development, Let's Encrypt for production. Two deployment options: Docker (nginx + services) or Local (Uvicorn SSL direct). |
