# Product Context

Describe the product.

## Overview

Provide a high-level overview of the project.

## Core Features

- Feature 1
- Feature 2

## Technical Stack

- Tech 1
- Tech 2

## Project Description

A high-quality medical calculator MCP server providing 78+ clinical tools with intelligent discovery and strict type safety.



A DDD-architected medical calculator MCP server providing 51 validated clinical scoring tools for AI Agent integration. Supports MCP SSE, REST API, and HTTPS deployment.



Medical Calculator MCP Server - 為 AI Agent 提供經驗證的醫學計算工具。採用 DDD 洋蔥架構設計，支援 50+ 臨床評分工具，涵蓋重症醫學、麻醉科、急診醫學、腎臟科等專科。所有計算公式均引用同儕審查論文，確保臨床準確性。



## Architecture

DDD Onion Architecture with clear separation of Domain, Application, and Infrastructure layers. Now modernized with uv and strict typing.



DDD Onion Architecture with 4 layers: Domain (core business logic), Application (use cases), Infrastructure (MCP/API servers, Nginx), Shared (utilities). Deployment options: stdio (local), SSE (remote MCP), API (REST), HTTPS (production with Nginx reverse proxy).



DDD Onion Architecture with 4 layers:\n\n1. **Domain Layer** (Core): Calculators, Entities (ScoreResult, ToolMetadata), Value Objects (Units, Interpretation), Registry\n2. **Application Layer**: Use Cases (CalculateUseCase, DiscoveryUseCase), DTOs, Parameter Validation\n3. **Infrastructure Layer**: MCP Server (FastMCP), REST API (FastAPI), Handlers, Resources\n4. **Shared Layer**: Common utilities\n\nDeployment Modes:\n- stdio: Local MCP (Claude Desktop, VS Code Copilot)\n- sse: Remote MCP over Server-Sent Events (Docker/Cloud)\n- api: REST API via FastAPI (port 8080)\n- http: Streamable HTTP transport



## Technologies

- Python 3.11+
- uv
- Docker
- MCP (Model Context Protocol)



- Python 3.11+
- FastMCP SDK 1.22.0
- FastAPI 0.123.0
- Uvicorn 0.38.0
- Pydantic 2.11.0
- Starlette 0.50.0
- Nginx (HTTPS reverse proxy)
- Docker
- Docker Compose



- Python 3.11+
- FastMCP (MCP SDK)
- FastAPI
- Pydantic
- Starlette
- Uvicorn
- Docker
- Docker Compose



## Libraries and Dependencies

- FastMCP SDK
- Pydantic v2
- Pytest
- Mypy (Strict)
- Ruff



- fastmcp
- fastapi
- uvicorn
- pydantic
- starlette
- httpx
- openssl (SSL certificate generation)



- mcp[cli]
- fastapi
- uvicorn
- starlette
- sse-starlette
- pydantic
- pytest
- pytest-asyncio
- httpx

