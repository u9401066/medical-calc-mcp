"""
Medical Calculator MCP Server - Main Entry Point

Supports multiple transport modes via FastMCP:
- stdio: Local mode for MCP Inspector and Claude Desktop (default)
- sse: Server-Sent Events for remote/Docker deployment
- http: Streamable HTTP transport

Usage:
    # Local STDIO mode (default, for Claude Desktop)
    python -m src.main

    # SSE mode for remote access (Docker, cloud)
    python -m src.main --mode sse
    python -m src.main --mode sse --host 0.0.0.0 --port 8000

    # Streamable HTTP mode
    python -m src.main --mode http

Docker:
    docker build -t medical-calc-mcp .
    docker run -p 8000:8000 medical-calc-mcp

Environment Variables:
    MCP_MODE     Transport mode: stdio, sse, http (default: stdio)
    MCP_HOST     Host to bind (default: 0.0.0.0)
    MCP_PORT     Port to bind (default: 8000)
    LOG_LEVEL    Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Configure logging to stderr IMMEDIATELY to avoid interfering with MCP stdio transport
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Ensure the project root is in the path for proper imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.infrastructure.mcp.config import McpServerConfig
from src.infrastructure.mcp.server import MedicalCalculatorServer


def create_server(host: str = "0.0.0.0", port: int = 8000) -> MedicalCalculatorServer:
    """
    Create and configure the MCP server with custom host/port.

    Args:
        host: Host to bind (for SSE/HTTP modes)
        port: Port to bind (for SSE/HTTP modes)

    Returns:
        MedicalCalculatorServer instance
    """
    config = McpServerConfig(host=host, port=port)
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

  # Streamable HTTP mode
  python -m src.main --mode http

Claude Desktop Configuration (for SSE mode):
  {
    "mcpServers": {
      "medical-calc": {
        "url": "http://YOUR_HOST:8000/sse"
      }
    }
  }
        """
    )

    parser.add_argument(
        "--mode", "-m",
        choices=["stdio", "sse", "http"],
        default=os.environ.get("MCP_MODE", "stdio"),
        help="Transport mode (default: stdio)"
    )
    parser.add_argument(
        "--host", "-H",
        default=os.environ.get("MCP_HOST", "0.0.0.0"),
        help="Host to bind for SSE/HTTP mode (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=int(os.environ.get("MCP_PORT", "8000")),
        help="Port to bind for SSE/HTTP mode (default: 8000)"
    )

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Medical Calculator MCP Server")
    logger.info("=" * 60)
    logger.info(f"Mode: {args.mode.upper()}")

    # Create server with host/port settings
    server = create_server(host=args.host, port=args.port)

    if args.mode == "stdio":
        logger.info("Starting in STDIO mode (for Claude Desktop local)...")
        server.run(transport="stdio")

    elif args.mode == "sse":
        logger.info(f"Starting in SSE mode on http://{args.host}:{args.port}")
        logger.info(f"SSE Endpoint: http://{args.host}:{args.port}/sse")
        logger.info("-" * 60)
        server.run(transport="sse")

    elif args.mode == "http":
        logger.info(f"Starting in HTTP mode on http://{args.host}:{args.port}")
        logger.info(f"MCP Endpoint: http://{args.host}:{args.port}/mcp")
        logger.info("-" * 60)
        server.run(transport="http")


if __name__ == "__main__":
    main()
