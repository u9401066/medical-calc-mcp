"""
Medical Calculator MCP Server - Main Entry Point

Supports multiple transport modes via FastMCP:
- stdio: Local mode for MCP Inspector and Claude Desktop (default)
- sse: Server-Sent Events for remote/Docker deployment
- http: Streamable HTTP transport

SSL/TLS Support:
- Use --ssl-keyfile and --ssl-certfile for direct SSL configuration
- Or use environment variables: SSL_ENABLED, SSL_KEYFILE, SSL_CERTFILE

Usage:
    # Local STDIO mode (default, for Claude Desktop)
    python -m src.main

    # SSE mode for remote access (Docker, cloud)
    python -m src.main --mode sse
    python -m src.main --mode sse --host 0.0.0.0 --port 8000

    # SSE mode with SSL/TLS (HTTPS)
    python -m src.main --mode sse --ssl-keyfile /path/to/key.pem --ssl-certfile /path/to/cert.pem

    # Using environment variables for SSL
    SSL_ENABLED=true SSL_KEYFILE=/path/to/key.pem SSL_CERTFILE=/path/to/cert.pem python -m src.main --mode sse

    # Streamable HTTP mode
    python -m src.main --mode http

Docker:
    docker build -t medical-calc-mcp .
    docker run -p 8000:8000 medical-calc-mcp

Environment Variables:
    MCP_MODE       Transport mode: stdio, sse, http (default: stdio)
    MCP_HOST       Host to bind (default: 0.0.0.0)
    MCP_PORT       Port to bind (default: 8000)
    LOG_LEVEL      Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)
    SSL_ENABLED    Enable SSL/TLS: true, false (default: false)
    SSL_KEYFILE    Path to SSL private key file
    SSL_CERTFILE   Path to SSL certificate file
    SSL_CA_CERTS   Path to CA certificates for client verification (optional)
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Configure logging to stderr IMMEDIATELY to avoid interfering with MCP stdio transport
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"), format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", stream=sys.stderr)
logger = logging.getLogger(__name__)

# Ensure the project root is in the path for proper imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.infrastructure.mcp.config import McpServerConfig, SslConfig
from src.infrastructure.mcp.server import MedicalCalculatorServer


def create_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    ssl_keyfile: str | None = None,
    ssl_certfile: str | None = None,
    ssl_ca_certs: str | None = None,
) -> MedicalCalculatorServer:
    """
    Create and configure the MCP server with custom host/port and SSL settings.

    Args:
        host: Host to bind (for SSE/HTTP modes)
        port: Port to bind (for SSE/HTTP modes)
        ssl_keyfile: Path to SSL private key file (optional)
        ssl_certfile: Path to SSL certificate file (optional)
        ssl_ca_certs: Path to CA certificates for client verification (optional)

    Returns:
        MedicalCalculatorServer instance
    """
    # Build SSL configuration
    # Priority: CLI args > Environment variables
    if ssl_keyfile and ssl_certfile:
        ssl_config = SslConfig(
            enabled=True,
            keyfile=ssl_keyfile,
            certfile=ssl_certfile,
            ca_certs=ssl_ca_certs,
        )
    else:
        ssl_config = SslConfig.from_env()

    config = McpServerConfig(host=host, port=port, ssl=ssl_config)
    return MedicalCalculatorServer(config=config)


def main() -> None:
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Medical Calculator MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Local MCP mode (for Claude Desktop)
  python -m src.main

  # Remote SSE mode (for Docker/remote agents)
  python -m src.main --mode sse
  python -m src.main --mode sse --host 0.0.0.0 --port 9000

  # SSE mode with SSL/TLS (HTTPS)
  python -m src.main --mode sse --ssl-keyfile /path/to/server.key --ssl-certfile /path/to/server.crt

  # Using environment variables for SSL
  SSL_ENABLED=true SSL_KEYFILE=/certs/key.pem SSL_CERTFILE=/certs/cert.pem python -m src.main --mode sse

  # Streamable HTTP mode
  python -m src.main --mode http

Environment Variables:
  MCP_MODE       Transport mode (default: stdio)
  MCP_HOST       Host to bind (default: 0.0.0.0)
  MCP_PORT       Port to bind (default: 8000)
  SSL_ENABLED    Enable SSL/TLS (default: false)
  SSL_KEYFILE    Path to SSL private key
  SSL_CERTFILE   Path to SSL certificate

Claude Desktop Configuration (for SSE mode):
  {
    "mcpServers": {
      "medical-calc": {
        "url": "http://YOUR_HOST:8000/sse"
      }
    }
  }

Claude Desktop Configuration (for HTTPS SSE mode):
  {
    "mcpServers": {
      "medical-calc": {
        "url": "https://YOUR_HOST:8000/sse"
      }
    }
  }
        """,
    )

    parser.add_argument("--mode", "-m", choices=["stdio", "sse", "http"], default=os.environ.get("MCP_MODE", "stdio"), help="Transport mode (default: stdio)")
    parser.add_argument("--host", "-H", default=os.environ.get("MCP_HOST", "0.0.0.0"), help="Host to bind for SSE/HTTP mode (default: 0.0.0.0)")
    parser.add_argument("--port", "-p", type=int, default=int(os.environ.get("MCP_PORT", "8000")), help="Port to bind for SSE/HTTP mode (default: 8000)")

    # SSL/TLS arguments
    ssl_group = parser.add_argument_group("SSL/TLS Options", "Configure HTTPS with custom certificates")
    ssl_group.add_argument(
        "--ssl-keyfile",
        default=os.environ.get("SSL_KEYFILE"),
        help="Path to SSL private key file (enables HTTPS)",
    )
    ssl_group.add_argument(
        "--ssl-certfile",
        default=os.environ.get("SSL_CERTFILE"),
        help="Path to SSL certificate file (enables HTTPS)",
    )
    ssl_group.add_argument(
        "--ssl-ca-certs",
        default=os.environ.get("SSL_CA_CERTS"),
        help="Path to CA certificates for client verification (optional)",
    )

    args = parser.parse_args()

    # Validate SSL args (both must be provided if either is)
    if bool(args.ssl_keyfile) != bool(args.ssl_certfile):
        parser.error("--ssl-keyfile and --ssl-certfile must be specified together")

    logger.info("=" * 60)
    logger.info("Medical Calculator MCP Server")
    logger.info("=" * 60)
    logger.info(f"Mode: {args.mode.upper()}")

    # Create server with host/port settings and SSL configuration
    server = create_server(
        host=args.host,
        port=args.port,
        ssl_keyfile=args.ssl_keyfile,
        ssl_certfile=args.ssl_certfile,
        ssl_ca_certs=args.ssl_ca_certs,
    )

    # Check if SSL is enabled
    ssl_enabled = args.ssl_keyfile and args.ssl_certfile
    protocol = "https" if ssl_enabled else "http"

    if args.mode == "stdio":
        logger.info("Starting in STDIO mode (for Claude Desktop local)...")
        if ssl_enabled:
            logger.warning("SSL options are ignored in STDIO mode")
        server.run(transport="stdio")

    elif args.mode == "sse":
        logger.info(f"Starting in SSE mode on {protocol}://{args.host}:{args.port}")
        logger.info(f"SSE Endpoint: {protocol}://{args.host}:{args.port}/sse")
        if ssl_enabled:
            logger.info(f"SSL Enabled: keyfile={args.ssl_keyfile}, certfile={args.ssl_certfile}")
        logger.info("-" * 60)

        # Run with SSL if configured
        if ssl_enabled:
            server.run(
                transport="sse",
                ssl_keyfile=args.ssl_keyfile,
                ssl_certfile=args.ssl_certfile,
            )
        else:
            server.run(transport="sse")

    elif args.mode == "http":
        logger.info(f"Starting in HTTP mode on {protocol}://{args.host}:{args.port}")
        logger.info(f"MCP Endpoint: {protocol}://{args.host}:{args.port}/mcp")
        if ssl_enabled:
            logger.info(f"SSL Enabled: keyfile={args.ssl_keyfile}, certfile={args.ssl_certfile}")
        logger.info("-" * 60)

        # Run with SSL if configured
        if ssl_enabled:
            server.run(
                transport="http",
                ssl_keyfile=args.ssl_keyfile,
                ssl_certfile=args.ssl_certfile,
            )
        else:
            server.run(transport="http")


if __name__ == "__main__":
    main()
