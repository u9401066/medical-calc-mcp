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

Medical Calculator MCP Server - 為 AI Agent 提供經驗證的醫學計算工具。採用 DDD 洋蔥架構設計，支援 50+ 臨床評分工具，涵蓋重症醫學、麻醉科、急診醫學、腎臟科等專科。所有計算公式均引用同儕審查論文，確保臨床準確性。



## Architecture

DDD Onion Architecture with 4 layers:\n\n1. **Domain Layer** (Core): Calculators, Entities (ScoreResult, ToolMetadata), Value Objects (Units, Interpretation), Registry\n2. **Application Layer**: Use Cases (CalculateUseCase, DiscoveryUseCase), DTOs, Parameter Validation\n3. **Infrastructure Layer**: MCP Server (FastMCP), REST API (FastAPI), Handlers, Resources\n4. **Shared Layer**: Common utilities\n\nDeployment Modes:\n- stdio: Local MCP (Claude Desktop, VS Code Copilot)\n- sse: Remote MCP over Server-Sent Events (Docker/Cloud)\n- api: REST API via FastAPI (port 8080)\n- http: Streamable HTTP transport



## Technologies

- Python 3.11+
- FastMCP (MCP SDK)
- FastAPI
- Pydantic
- Starlette
- Uvicorn
- Docker
- Docker Compose



## Libraries and Dependencies

- mcp[cli]
- fastapi
- uvicorn
- starlette
- sse-starlette
- pydantic
- pytest
- pytest-asyncio
- httpx

