# Configuration

Medical-Calc-MCP uses environment variables for configuration.

## Environment Variables

### Server Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8000` | Server port |
| `LOG_LEVEL` | `INFO` | Logging level |

### Security Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `SECURITY_ENABLED` | `false` | Enable security features |
| `SECURITY_API_KEY` | `""` | API key for authentication |
| `SECURITY_RATE_LIMIT_ENABLED` | `false` | Enable rate limiting |
| `SECURITY_RATE_LIMIT_REQUESTS` | `100` | Requests per window |
| `SECURITY_RATE_LIMIT_WINDOW` | `60` | Window in seconds |

### CORS Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `CORS_ORIGINS` | `*` | Allowed origins |
| `CORS_METHODS` | `*` | Allowed HTTP methods |

## Configuration Examples

### Development

```bash
export LOG_LEVEL=DEBUG
export SECURITY_ENABLED=false
uv run python -m src.rest_server
```

### Production

```bash
export LOG_LEVEL=WARNING
export SECURITY_ENABLED=true
export SECURITY_API_KEY="your-secure-api-key"
export SECURITY_RATE_LIMIT_ENABLED=true
export CORS_ORIGINS="https://your-app.com"
uv run python -m src.rest_server
```

### Docker Compose

```yaml
version: '3.8'
services:
  medical-calc:
    image: ghcr.io/u9401066/medical-calc-mcp:latest
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO
      - SECURITY_ENABLED=true
      - SECURITY_API_KEY=${API_KEY}
```
