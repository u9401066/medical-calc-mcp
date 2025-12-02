# Active Context

## Current Goals

- HTTPS deployment completed. Added comprehensive HTTPS support including:
- 1. Nginx reverse proxy with TLS termination (nginx/nginx.conf)
- 2. Docker HTTPS deployment (docker-compose.https.yml)
- 3. SSL certificate generation script (scripts/generate-ssl-certs.sh)
- 4. Local HTTPS startup scripts (scripts/start-https-local.sh, scripts/start-https-docker.sh)
- 5. Rate limiting configured (30 req/s API, 60 req/s MCP)
- 6. Security headers (XSS, CSRF protection)
- 7. SSE-optimized proxy settings (24h timeout, no buffering)
- Endpoints:
- - Docker: https://localhost/ (MCP), https://localhost:8443/ (API)
- - Local: https://localhost:8443/ (MCP), https://localhost:9443/ (API)
- Next focus areas: Phase 12 (Neurology), Rate Limiting with Redis, API Authentication

## Current Blockers

- None yet