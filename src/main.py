"""
Medical Calculator MCP Server - Main Entry Point

Supports multiple transport modes:
- stdio: Local mode for MCP Inspector and Claude Desktop
- sse: Server-Sent Events for remote/Docker deployment
- http: Streamable HTTP transport

Usage:
    # Local STDIO mode (default)
    python -m src.main
    
    # SSE mode for remote access
    python -m src.main --mode sse --host 0.0.0.0 --port 8000
    
    # HTTP mode
    python -m src.main --mode http
    
Docker:
    docker build -t medical-calc-mcp .
    docker run -p 8000:8000 medical-calc-mcp
"""

import argparse
import os
import sys
import logging
from pathlib import Path
from typing import Optional

# Ensure the project root is in the path for proper imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_app():
    """Create and configure the MCP server application"""
    from src.infrastructure.mcp.server import MedicalCalculatorServer
    return MedicalCalculatorServer()


def run_stdio():
    """Run in STDIO mode (local, for Claude Desktop)"""
    logger.info("Starting MCP Server in STDIO mode...")
    server = create_app()
    server.run(transport="stdio")


def run_sse(host: str = "0.0.0.0", port: int = 8000):
    """Run in SSE mode (remote, for Docker/cloud deployment)"""
    try:
        from starlette.applications import Starlette
        from starlette.routing import Route
        from starlette.responses import JSONResponse
        from mcp.server.sse import SseServerTransport
        import uvicorn
    except ImportError as e:
        logger.error(f"SSE mode requires additional packages: {e}")
        logger.error("Run: pip install starlette uvicorn sse-starlette")
        sys.exit(1)
    
    logger.info(f"Starting MCP Server in SSE mode on {host}:{port}...")
    
    # Create server instance
    server = create_app()
    
    # Create SSE transport
    sse_transport = SseServerTransport("/messages/")
    
    async def handle_sse(request):
        """Handle SSE connection"""
        async with sse_transport.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await server.mcp._mcp_server.run(
                streams[0], streams[1], server.mcp._mcp_server.create_initialization_options()
            )
    
    async def handle_messages(request):
        """Handle POST messages from client"""
        return await sse_transport.handle_post_message(request.scope, request.receive, request._send)
    
    async def health_check(request):
        """Health check endpoint for Docker/K8s"""
        return JSONResponse({
            "status": "healthy",
            "service": "medical-calc-mcp",
            "version": "1.0.0",
            "calculators": len(server.registry.list_all()),
        })
    
    async def info(request):
        """Server info endpoint"""
        return JSONResponse({
            "name": "Medical Calculator MCP Server",
            "version": "1.0.0",
            "mode": "sse",
            "calculators_count": len(server.registry.list_all()),
            "endpoints": {
                "health": "/health",
                "info": "/",
                "sse": "/sse",
                "messages": "/messages/"
            },
            "usage": {
                "claude_desktop": {
                    "mcpServers": {
                        "medical-calc": {
                            "url": f"http://{host}:{port}/sse"
                        }
                    }
                }
            }
        })
    
    # Create Starlette app with routes
    app = Starlette(
        debug=os.environ.get("DEBUG", "false").lower() == "true",
        routes=[
            Route("/health", health_check, methods=["GET"]),
            Route("/", info, methods=["GET"]),
            Route("/sse", handle_sse, methods=["GET"]),
            Route("/messages/", handle_messages, methods=["POST"]),
        ],
    )
    
    # Run with uvicorn
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=os.environ.get("LOG_LEVEL", "info").lower(),
    )


def run_http():
    """Run in streamable HTTP mode"""
    logger.info("Starting MCP Server in HTTP mode...")
    server = create_app()
    server.run(transport="http")


def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Medical Calculator MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Local mode (for Claude Desktop)
  python -m src.main
  
  # Remote SSE mode (for Docker)
  python -m src.main --mode sse --port 8000
  
  # HTTP mode
  python -m src.main --mode http

Environment Variables:
  MCP_MODE     Transport mode (stdio, sse, http)
  MCP_HOST     Host to bind (default: 0.0.0.0)
  MCP_PORT     Port to bind (default: 8000)
  LOG_LEVEL    Logging level (default: INFO)
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
        help="Host to bind for SSE mode (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=int(os.environ.get("MCP_PORT", "8000")),
        help="Port to bind for SSE mode (default: 8000)"
    )
    
    args = parser.parse_args()
    
    logger.info(f"Medical Calculator MCP Server starting...")
    logger.info(f"Mode: {args.mode}")
    
    if args.mode == "stdio":
        run_stdio()
    elif args.mode == "sse":
        run_sse(host=args.host, port=args.port)
    elif args.mode == "http":
        run_http()
    else:
        logger.error(f"Unknown mode: {args.mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
