# Medical Calculator MCP - 新工具開發標準

## 概述

本文件定義了新增醫學計算工具的開發標準，確保所有工具符合一致的品質標準。

## 開發環境設定

本專案使用 `uv` 進行套件管理。

```bash
# 安裝依賴
uv sync

# 執行測試
uv run pytest

# 執行型別檢查 (必須通過 --strict)
uv run mypy --strict src tests

# 執行 Lint 檢查
uv run ruff check .
```

## 開發流程

### 1. 建立 Calculator (Domain Layer)

位置: `src/domain/services/calculators/`

```python
"""
Calculator 名稱

[臨床描述]

References:
    [文獻引用]
"""

from ..base import BaseCalculator
from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.units import Unit
from ...value_objects.reference import Reference
from ...value_objects.interpretation import Interpretation, Severity, RiskLevel
from ...value_objects.tool_keys import (
    LowLevelKey,
    HighLevelKey,
    Specialty,
    ClinicalContext,
)


class MyCalculator(BaseCalculator):
    """Calculator docstring with scoring criteria"""
    
    @property
    def tool_id(self) -> str:
        return "my_calculator"
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level_key=LowLevelKey.MY_KEY,
            high_level_keys={HighLevelKey.CATEGORY},
            specialties={Specialty.SPECIALTY_NAME},
            clinical_contexts={ClinicalContext.CONTEXT},
        )
    
    @property
    def references(self) -> list[Reference]:
        return [
            Reference(
                citation="Author A, et al. Title. Journal. Year;Vol:Pages.",
                doi="10.xxxx/xxxxx",
                pmid="12345678",
                year=2020,
            )
        ]
    
    def calculate(
        self,
        param1: float,
        param2: str,
    ) -> ScoreResult:
        """Calculate with full parameter documentation"""
        # Implementation
        pass
```

### 2. 註冊 Calculator

位置: `src/domain/services/calculators/__init__.py`

```python
from .my_calculator import MyCalculator

CALCULATORS = [
    # ... existing calculators
    MyCalculator,
]
```

### 3. 建立 MCP Handler (Infrastructure Layer)

位置: `src/infrastructure/mcp/handlers/calculators/[specialty].py`

**關鍵原則: 使用 Literal + Field 約束**

```python
from typing import Annotated, Literal
from pydantic import Field

@mcp.tool()
def calculate_my_tool(
    # 枚舉值：必須使用 Literal
    sex: Annotated[
        Literal["male", "female"],
        Field(description="性別 Sex | Options: 'male' or 'female'")
    ],
    
    # 整數範圍：使用 Field 約束
    age: Annotated[
        int,
        Field(ge=18, le=120, description="年齡 Age | Unit: years | Range: 18-120")
    ],
    
    # 浮點數範圍：使用 Field 約束
    creatinine: Annotated[
        float,
        Field(gt=0, le=20.0, description="血清肌酐 Serum Cr | Unit: mg/dL | Range: >0-20.0")
    ],
    
    # 選項型字串：使用 Literal
    admission_type: Annotated[
        Literal["nonoperative", "elective_postop", "emergency_postop"],
        Field(description="入院類型 | Options: 'nonoperative', 'elective_postop', 'emergency_postop'")
    ] = "nonoperative",
    
    # 布林值：有預設值
    is_emergency: Annotated[bool, Field(description="是否緊急 Emergency")] = False,
    
) -> dict[str, Any]:
    """
    🏥 工具名稱: 中文描述
    
    [臨床說明]
    
    **評分項目:**
    - 項目1: 說明
    - 項目2: 說明
    
    **風險分層:**
    - 低風險: 建議
    - 高風險: 建議
    
    **參考文獻:** Author, et al. Journal. Year. PMID: xxxxx
    
    Returns:
        分數、解釋、建議
    """
    request = CalculateRequest(
        tool_id="my_calculator",
        params={...}
    )
    response = use_case.execute(request)
    return response.to_dict()
```

## 參數驗證標準

### 類型選擇指南

| 情境 | 使用類型 | 範例 |
|------|---------|------|
| 固定選項 | `Literal[...]` | `Literal["male", "female"]` |
| 有限整數 | `Literal[...]` | `Literal[1, 2, 3, 4, 5, 6]` |
| 連續整數 | `int + Field(ge=, le=)` | `Field(ge=3, le=15)` |
| 連續浮點 | `float + Field(ge=, le=)` | `Field(gt=0, le=20.0)` |
| 是/否 | `bool` | `Annotated[bool, Field(...)]` |
| 選填值 | `Optional[T]` | `Optional[float]` |

### Description 格式標準

```
中文名稱 English name | Unit: 單位 | Range: 範圍
```

範例:
- `血清肌酐 Serum creatinine | Unit: mg/dL | Range: 0.1-20.0`
- `年齡 Age | Unit: years | Range: 18-120`
- `性別 Sex | Options: 'male' or 'female'`

### 預設值語法

✅ 正確:
```python
param: Annotated[bool, Field(description="...")] = False
```

❌ 錯誤 (會導致語法錯誤):
```python
param: Annotated[bool, Field(description="...", default=False)]  # 混用會錯誤
```

## 測試標準

### 必要測試類型

1. **基本功能測試** - 正常輸入產生正確結果
2. **邊界值測試** - 最小/最大值正確處理
3. **枚舉值測試** - 所有有效選項都能接受
4. **Interpretation 測試** - 臨床解釋內容正確
5. **References 測試** - 文獻引用完整

### 測試檔案位置

`tests/test_[specialty].py`

```python
class TestMyCalculator:
    def test_basic_calculation(self):
        from src.domain.services.calculators import MyCalculator
        calc = MyCalculator()
        result = calc.calculate(param1=value1, param2=value2)
        assert result.value == expected
    
    def test_boundary_values(self):
        # 測試邊界條件
        pass
    
    def test_all_valid_options(self):
        # 測試所有有效選項
        for option in ["opt1", "opt2", "opt3"]:
            result = calc.calculate(..., param=option)
            assert result.value is not None
    
    def test_tool_id(self):
        assert MyCalculator().tool_id == "my_calculator"
```

## 品質檢查清單

### Calculator 層
- [ ] 繼承 `BaseCalculator`
- [ ] 實作 `tool_id`, `metadata`, `references`
- [ ] 有完整 docstring
- [ ] 有 PMID/DOI 引用

### MCP Handler 層
- [ ] 枚舉參數使用 `Literal`
- [ ] 數值參數有 `Field(ge=, le=)` 約束
- [ ] Description 包含單位和範圍
- [ ] Docstring 有中英文說明
- [ ] Docstring 有參考文獻 PMID

### 測試層
- [ ] 基本計算測試
- [ ] 邊界值測試
- [ ] 有效選項測試
- [ ] tool_id 測試
- [ ] 測試覆蓋率 > 80%

## 目前統計

| 指標 | 數值 |
|------|------|
| Calculators | 121 |
| MCP Tools | 128 |
| Tests | 1721+ |
| Coverage | 92% |
