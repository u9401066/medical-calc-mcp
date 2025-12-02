# System Patterns

## Architectural Patterns

- Pattern 1: Description

## Design Patterns

- Pattern 1: Description

## Common Idioms

- Idiom 1: Description

## HTTPS Reverse Proxy Pattern

HTTPS deployment uses Nginx as reverse proxy for TLS termination, rate limiting, and SSE optimization. Internal services communicate via HTTP within Docker network. SSL certificates can be self-signed (development) or Let's Encrypt (production). Nginx handles security headers (XSS, CSRF, X-Frame-Options) and SSE-specific settings (24h timeout, no buffering, chunked transfer disabled).

### Examples

- nginx/nginx.conf - TLS termination and rate limiting config
- docker-compose.https.yml - Multi-service HTTPS orchestration
- scripts/generate-ssl-certs.sh - Self-signed CA and server certificates
- scripts/start-https-local.sh - Uvicorn native SSL for development
