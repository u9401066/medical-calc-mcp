# Copilot Instructions for Medical Calculator MCP

> Medical Calculator MCP Server - 醫學計算工具 MCP 伺服器
> 為 AI Agent 提供經過驗證的醫學計算工具

## 📊 專案概況

| 指標 | 數值 |
|------|------|
| **計算器數量** | 151 (涵蓋 31 個專科) |
| **Unified MCP Tools** | 6 (3 發現工具 + 3 計算工具) |
| **測試數量** | 2073+ |
| **測試覆蓋率** | 92% |
| **文獻引用** | 244 PMIDs, 205 DOIs (100% 覆蓋) |
| **架構** | DDD Onion + FastMCP |
| **Python 版本** | 3.11+ |
| **套件管理** | uv |

## 🛠️ 開發環境

```bash
# 安裝依賴
uv sync

# 執行測試
uv run pytest

# 執行型別檢查 (必須通過 --strict)
uv run mypy --no-incremental --strict src tests

# 執行 Lint 檢查
uv run ruff check .

# 計算工具數量
uv run python scripts/count_tools.py

# 計算引用文獻數量
uv run python scripts/count_references.py

# 啟動 MCP 伺服器 (stdio)
uv run python -m src.main

# 啟動 MCP 開發模式
uv run mcp dev src/main.py

# 啟動 REST API
uv run python src/main.py --mode api --port 8080
```

## 📁 專案結構

```
src/
├── domain/           # 核心業務邏輯 (無依賴)
│   ├── entities/     # ScoreResult, ToolMetadata
│   ├── services/     # BaseCalculator, ToolRegistry
│   │   └── calculators/  # 151 個計算器實作
│   ├── validation/   # ParameterValidator, BoundarySpec
│   └── value_objects/    # Unit, Reference, Interpretation
├── application/      # 用例層
│   └── use_cases/    # DiscoveryUseCase, CalculateUseCase
├── infrastructure/   # 基礎設施層
│   ├── mcp/          # MCP Server, Handlers
│   │   └── handlers/ # 按專科分類的 handlers
│   └── api/          # REST API (FastAPI)
└── shared/           # 共用工具
```

## 🔧 新增計算器標準流程

### 1. 建立 Calculator (Domain Layer)

位置: `src/domain/services/calculators/[specialty]/`

```python
from ..base import BaseCalculator
from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import LowLevelKey, HighLevelKey, Specialty

class MyCalculator(BaseCalculator):
    @property
    def tool_id(self) -> str:
        return "my_calculator"

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(...)

    @property
    def references(self) -> list[Reference]:
        return [Reference(citation="...", doi="...", pmid="...", year=2020)]

    def calculate(self, param1: float, param2: str) -> ScoreResult:
        # 實作計算邏輯
        pass
```

### 2. 註冊 Calculator

位置: `src/domain/services/calculators/__init__.py`

### 3. 建立 MCP Handler

位置: `src/infrastructure/mcp/handlers/calculators/[specialty].py`

關鍵: 使用 `Literal` + `Field` 約束參數

```python
from typing import Annotated, Literal
from pydantic import Field

@mcp.tool()
def calculate_my_tool(
    sex: Annotated[Literal["male", "female"], Field(description="性別 Sex")],
    age: Annotated[int, Field(ge=18, le=120, description="年齡 Age | years")],
) -> dict[str, Any]:
    """🏥 工具名稱: 說明"""
    pass
```

### 4. 撰寫測試

位置: `tests/test_[specialty].py`

## 🔍 工具發現 API (6 個核心工具)

| 工具 | 功能 |
|------|------|
| `discover(by, value)` | 統一發現入口 (specialty/context/keyword) |
| `get_related_tools(tool_id)` | 圖譜關聯工具 |
| `find_tools_by_params(params)` | 反向查詢可用工具 |
| `get_tool_schema(tool_id)` | 取得參數規格 |
| `calculate(tool_id, params)` | 執行計算 |
| `calculate_batch(calculations)` | 批次計算 |

## 🏥 專科分類 (26 專科, 128 計算器)

| 專科 | 數量 | 例子 |
|------|------|------|
| Critical Care | 18 | SOFA, APACHE II, qSOFA, NEWS2, RASS, SIRS |
| Cardiology | 11 | GRACE, CHA₂DS₂-VASc, HAS-BLED, Framingham |
| Emergency | 9 | GCS, Wells DVT/PE, PERC Rule, Shock Index |
| Anesthesiology | 8 | ASA, RCRI, Mallampati, MABL, STOP-BANG |
| Neurology | 7 | NIHSS, ABCD2, Hunt-Hess, ICH Score |
| Psychiatry | 7 | PHQ-9, GAD-7, MADRS, HAM-D |
| Geriatrics | 7 | Barthel, MoCA, MMSE, CFS |
| Nephrology | 6 | CKD-EPI, FENa, Serum Osmolality |
| Pediatrics | 6 | APGAR, PEWS, pSOFA, PIM3 |
| Surgery/Trauma | 6 | ISS, TRISS, Caprini VTE, Parkland |
| Endocrinology | 6 | FINDRISC, FRAX |
| Pain Medicine | 1 | MME Calculator |
| 其他 | 36 | 肝臟、肺臟、血液、皮膚等 |

## 📋 臨床工作流程範例

### 敗血症評估
```
qSOFA → SOFA → RASS → CAM-ICU
```

### 術前評估
```
ASA-PS → RCRI → Mallampati → STOP-BANG
```

### 上消化道出血
```
Glasgow-Blatchford → AIMS65 → Rockall
```

## ⚠️ 品質要求

- [ ] **型別**: `mypy --strict` 通過
- [ ] **Lint**: `ruff check` 通過
- [ ] **測試**: 每個計算器需有單元測試
- [ ] **文獻**: 每個計算器需有 PMID/DOI 引用
- [ ] **雙語**: Description 需中英雙語

## 📚 關鍵文件

| 文件 | 說明 |
|------|------|
| [README.md](../README.md) | 專案完整說明 |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | 開發標準 |
| [ROADMAP.md](../ROADMAP.md) | 發展路線圖 |
| [docs/DEPLOYMENT.md](../docs/DEPLOYMENT.md) | 部署指南 |

## 回應風格
- 使用繁體中文
- 遵循 DDD 架構原則
- 確保所有計算器有文獻引用
