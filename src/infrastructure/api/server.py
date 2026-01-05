"""
Medical Calculator REST API Server

Provides HTTP REST API endpoints for all medical calculators.
Can run standalone or alongside the MCP server.

Usage:
    # Direct run
    python -m src.infrastructure.api.server

    # Via main entry point
    python src/main.py --mode api --port 8080

    # With uvicorn (production)
    uvicorn src.infrastructure.api.server:app --host 0.0.0.0 --port 8080
"""

import os
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import asdict
from pathlib import Path
from typing import Any, Optional

# Ensure project root is in path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

from src.application.dto import CalculateRequest, DiscoveryMode, DiscoveryRequest
from src.application.use_cases.calculate_use_case import CalculateUseCase
from src.application.use_cases.discovery_use_case import DiscoveryUseCase
from src.domain.registry.tool_registry import get_registry
from src.domain.services.calculators import CALCULATORS

# =============================================================================
# Pydantic Models for API
# =============================================================================

class CalculatorInput(BaseModel):
    """Generic calculator input model"""
    params: dict[str, Any] = Field(..., description="Calculator parameters")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "params": {
                    "serum_creatinine": 1.2,
                    "age": 65,
                    "sex": "female"
                }
            }
        }
    )


class CalculatorResponse(BaseModel):
    """Calculator response model"""
    success: bool
    calculator: str
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None


class DiscoveryResponse(BaseModel):
    """Discovery response model"""
    count: int
    tools: list[dict[str, Any]]


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    calculators: int
    mode: str = "api"


# =============================================================================
# Application Lifespan
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler"""
    # Startup: Register all calculators
    registry = get_registry()
    for calculator_cls in CALCULATORS:
        instance = calculator_cls()
        if registry.get_calculator(instance.tool_id) is None:
            registry.register(instance)

    yield

    # Shutdown: Cleanup if needed
    pass


# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="Medical Calculator API",
    description="""
## 醫學計算器 REST API

提供 41+ 個經過驗證的臨床評分工具，所有計算器均引用同儕審查研究論文。

### 功能特色
- 🔍 智慧工具探索 (依專科、臨床情境搜尋)
- 📚 循證醫學 (所有公式引用原始論文)
- 🔒 參數驗證 (範圍檢查、必填檢查)

### 使用流程
1. `GET /api/v1/calculators` - 列出所有計算器
2. `GET /api/v1/calculators/{tool_id}` - 取得計算器詳情
3. `POST /api/v1/calculate/{tool_id}` - 執行計算

### 專科分類
- Critical Care: SOFA, APACHE II, qSOFA, NEWS2, GCS, RASS, CAM-ICU
- Cardiology: CHA₂DS₂-VASc, HEART, GRACE, ACEF II
- Nephrology: CKD-EPI 2021, KDIGO AKI
- Pulmonology: CURB-65, PSI/PORT, P/F Ratio, ROX Index
- And more...
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware - Configure via environment variables for production
# Default: Allow all origins (development mode)
# Production: Set CORS_ORIGINS="https://example.com,https://api.example.com"
_cors_origins = os.environ.get("CORS_ORIGINS", "*")
_allowed_origins = ["*"] if _cors_origins == "*" else [o.strip() for o in _cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True if _cors_origins != "*" else False,  # Credentials only with specific origins
    allow_methods=["GET", "POST", "OPTIONS"],  # Only necessary methods
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
)


# =============================================================================
# Health & Info Endpoints
# =============================================================================

@app.get("/", tags=["Info"])
async def root() -> dict[str, Any]:
    """API root with service information"""
    registry = get_registry()
    return {
        "service": "Medical Calculator API",
        "version": "1.0.0",
        "calculators": len(registry.list_all()),
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Health check endpoint for Docker/K8s"""
    registry = get_registry()
    return HealthResponse(
        status="healthy",
        service="medical-calc-api",
        version="1.0.0",
        calculators=len(registry.list_all()),
        mode="api"
    )


# =============================================================================
# Discovery Endpoints
# =============================================================================

@app.get("/api/v1/calculators", response_model=DiscoveryResponse, tags=["Discovery"])
async def list_calculators(
    limit: int = Query(50, ge=1, le=100, description="Maximum results")
) -> DiscoveryResponse:
    """
    列出所有可用的計算器

    List all available calculators with their metadata.
    """
    registry = get_registry()
    use_case = DiscoveryUseCase(registry)

    request = DiscoveryRequest(mode=DiscoveryMode.LIST_ALL, limit=limit)
    result = use_case.execute(request)

    return DiscoveryResponse(
        count=len(result.tools),
        tools=[asdict(t) for t in result.tools]
    )


@app.get("/api/v1/calculators/{tool_id}", tags=["Discovery"])
async def get_calculator_info(tool_id: str) -> dict[str, Any]:
    """
    取得特定計算器的詳細資訊

    Get detailed information about a specific calculator including
    parameters, references, and usage examples.
    """
    registry = get_registry()
    use_case = DiscoveryUseCase(registry)

    request = DiscoveryRequest(mode=DiscoveryMode.GET_INFO, tool_id=tool_id)
    result = use_case.execute(request)

    if result.tool_detail is None:
        raise HTTPException(status_code=404, detail=f"Calculator '{tool_id}' not found")

    return asdict(result.tool_detail)


@app.get("/api/v1/search", response_model=DiscoveryResponse, tags=["Discovery"])
async def search_calculators(
    q: str = Query(..., min_length=1, description="Search keyword"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results")
) -> DiscoveryResponse:
    """
    依關鍵字搜尋計算器

    Search calculators by keyword (name, specialty, condition, etc.)
    """
    registry = get_registry()
    use_case = DiscoveryUseCase(registry)

    request = DiscoveryRequest(mode=DiscoveryMode.SEARCH, query=q, limit=limit)
    result = use_case.execute(request)

    return DiscoveryResponse(
        count=len(result.tools),
        tools=[asdict(t) for t in result.tools]
    )


@app.get("/api/v1/specialties", tags=["Discovery"])
async def list_specialties() -> dict[str, Any]:
    """
    列出所有可用的專科分類

    List all available medical specialties.
    """
    registry = get_registry()
    use_case = DiscoveryUseCase(registry)

    request = DiscoveryRequest(mode=DiscoveryMode.LIST_SPECIALTIES)
    result = use_case.execute(request)

    return {
        "specialties": result.available_specialties,
        "count": len(result.available_specialties) if result.available_specialties else 0
    }


@app.get("/api/v1/specialties/{specialty}", response_model=DiscoveryResponse, tags=["Discovery"])
async def list_by_specialty(
    specialty: str,
    limit: int = Query(20, ge=1, le=50, description="Maximum results")
) -> DiscoveryResponse:
    """
    列出特定專科的所有計算器

    List all calculators for a specific medical specialty.
    """
    registry = get_registry()
    use_case = DiscoveryUseCase(registry)

    request = DiscoveryRequest(mode=DiscoveryMode.BY_SPECIALTY, specialty=specialty, limit=limit)
    result = use_case.execute(request)

    return DiscoveryResponse(
        count=len(result.tools),
        tools=[asdict(t) for t in result.tools]
    )


@app.get("/api/v1/contexts", tags=["Discovery"])
async def list_contexts() -> dict[str, Any]:
    """
    列出所有臨床情境

    List all available clinical contexts.
    """
    registry = get_registry()
    use_case = DiscoveryUseCase(registry)

    request = DiscoveryRequest(mode=DiscoveryMode.LIST_CONTEXTS)
    result = use_case.execute(request)

    return {
        "contexts": result.available_contexts,
        "count": len(result.available_contexts) if result.available_contexts else 0
    }


# =============================================================================
# Calculator Endpoints
# =============================================================================

@app.post("/api/v1/calculate/{tool_id}", response_model=CalculatorResponse, tags=["Calculate"])
async def calculate(tool_id: str, input_data: CalculatorInput) -> CalculatorResponse:
    """
    執行計算

    Execute a medical calculation with the given parameters.

    Example for CKD-EPI 2021:
    ```json
    {
        "params": {
            "serum_creatinine": 1.2,
            "age": 65,
            "sex": "female"
        }
    }
    ```
    """
    registry = get_registry()
    use_case = CalculateUseCase(registry)

    request = CalculateRequest(
        tool_id=tool_id,
        params=input_data.params
    )
    result = use_case.execute(request)

    if not result.success:
        return CalculatorResponse(
            success=False,
            calculator=tool_id,
            error=result.error
        )

    # Convert dataclass to dict, excluding success and error fields
    result_dict = {
        "tool_id": result.tool_id,
        "score_name": result.score_name,
        "value": result.result,
        "unit": result.unit,
    }

    if result.interpretation:
        result_dict["interpretation"] = {
            "summary": result.interpretation.summary,
        }
        if result.interpretation.severity:
            result_dict["interpretation"]["severity"] = result.interpretation.severity
        if result.interpretation.recommendation:
            result_dict["interpretation"]["recommendation"] = result.interpretation.recommendation

    if result.component_scores:
        result_dict["component_scores"] = result.component_scores

    return CalculatorResponse(
        success=True,
        calculator=tool_id,
        result=result_dict
    )


# =============================================================================
# Convenience Endpoints (Direct Calculator Access)
# =============================================================================

@app.post("/api/v1/ckd-epi", tags=["Quick Calculate"])
async def calculate_ckd_epi(
    serum_creatinine: float = Query(..., gt=0, description="Serum creatinine (mg/dL)"),
    age: int = Query(..., ge=18, le=120, description="Age in years"),
    sex: str = Query(..., pattern="^(male|female)$", description="Sex (male/female)")
) -> dict[str, Any]:
    """
    快速計算 CKD-EPI 2021 eGFR

    Calculate eGFR using CKD-EPI 2021 equation (race-free).
    """
    registry = get_registry()
    use_case = CalculateUseCase(registry)

    request = CalculateRequest(
        tool_id="ckd_epi_2021",
        params={"serum_creatinine": serum_creatinine, "age": age, "sex": sex}
    )
    result = use_case.execute(request)

    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)

    # Convert dataclass result to dict
    result_dict = {
        "tool_id": result.tool_id,
        "score_name": result.score_name,
        "value": result.result,
        "unit": result.unit,
    }
    if result.interpretation:
        result_dict["interpretation"] = {
            "summary": result.interpretation.summary,
        }
    return result_dict


@app.post("/api/v1/sofa", tags=["Quick Calculate"])
async def calculate_sofa(
    pao2_fio2_ratio: float = Query(..., description="PaO2/FiO2 ratio"),
    platelets: float = Query(..., description="Platelets (×10³/µL)"),
    bilirubin: float = Query(..., description="Bilirubin (mg/dL)"),
    cardiovascular: str = Query(..., description="MAP or vasopressor status"),
    gcs_score: int = Query(..., ge=3, le=15, description="GCS score"),
    creatinine: float = Query(..., description="Creatinine (mg/dL)")
) -> dict[str, Any]:
    """
    快速計算 SOFA Score

    Calculate Sequential Organ Failure Assessment score.
    """
    registry = get_registry()
    use_case = CalculateUseCase(registry)

    request = CalculateRequest(
        tool_id="sofa_score",
        params={
            "pao2_fio2_ratio": pao2_fio2_ratio,
            "platelets": platelets,
            "bilirubin": bilirubin,
            "cardiovascular": cardiovascular,
            "gcs_score": gcs_score,
            "creatinine": creatinine
        }
    )
    result = use_case.execute(request)

    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)

    # Convert dataclass result to dict
    result_dict = {
        "tool_id": result.tool_id,
        "score_name": result.score_name,
        "value": result.result,
        "unit": result.unit,
    }
    if result.interpretation:
        result_dict["interpretation"] = {
            "summary": result.interpretation.summary,
        }
    return result_dict


# =============================================================================
# Entry Point
# =============================================================================

def main() -> None:
    """Run the API server"""
    import uvicorn

    host = os.environ.get("API_HOST", "0.0.0.0")
    port = int(os.environ.get("API_PORT", "8080"))

    print(f"🏥 Medical Calculator API starting on http://{host}:{port}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print(f"📖 ReDoc: http://{host}:{port}/redoc")

    uvicorn.run(
        "src.infrastructure.api.server:app",
        host=host,
        port=port,
        reload=os.environ.get("DEBUG", "false").lower() == "true"
    )


if __name__ == "__main__":
    main()
