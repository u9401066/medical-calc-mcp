# Development Guide 開發備忘

## 🎯 專案目標

建立一個 DDD 架構的醫學計算器 MCP Server，提供 200-300 個臨床評分工具，透過 Tool Discovery 機制幫助 AI Agent 智能選擇合適的工具。

## 🏗️ 架構設計

### DDD 分層

```
src/
├── domain/                    # 領域層（核心，零依賴）
│   ├── entities/              # 實體
│   │   ├── score_result.py    # 計算結果
│   │   └── tool_metadata.py   # 工具元資料
│   │
│   ├── services/              # 領域服務（計算邏輯）
│   │   ├── base.py            # 計算器基礎類別
│   │   └── calculators/       # 200-300 個計算器
│   │
│   ├── value_objects/         # 值物件
│   │   ├── units.py           # 單位
│   │   ├── interpretation.py  # 臨床解讀
│   │   ├── reference.py       # 文獻引用
│   │   └── tool_keys.py       # Low/High Level Keys
│   │
│   └── registry/              # 工具註冊與索引
│       ├── tool_registry.py   # 註冊表
│       └── taxonomy.py        # 分類法
│
├── application/               # 應用層
│   ├── use_cases/             # 使用案例
│   │   ├── calculate.py       # 執行計算
│   │   ├── discover_tools.py  # 工具發現
│   │   └── search_tools.py    # 工具搜尋
│   └── dto/                   # 資料傳輸物件
│
├── infrastructure/            # 基礎設施層
│   ├── mcp/                   # MCP Server
│   │   ├── server.py
│   │   └── tools.py
│   └── api/                   # REST API (optional)
│       ├── server.py
│       └── routes.py
│
└── shared/                    # 共用
    ├── exceptions.py
    └── constants.py
```

### Tool Discovery 設計

```python
@dataclass
class LowLevelKey:
    tool_id: str           # "ckd_epi_2021"
    name: str              # "CKD-EPI 2021"
    purpose: str           # "Calculate estimated GFR"
    input_params: List[str]
    output_type: str

@dataclass
class HighLevelKey:
    specialties: List[Specialty]
    conditions: List[str]
    clinical_contexts: List[ClinicalContext]
    clinical_questions: List[str]
    icd10_codes: List[str]
    keywords: List[str]
```

## 📅 開發階段

### Phase 1: Foundation 基礎建設
- [ ] 建立專案結構
- [ ] 實作 Domain 層基礎
  - [ ] value_objects (units, reference, tool_keys)
  - [ ] entities (score_result, tool_metadata)
  - [ ] base calculator class
- [ ] 實作 Tool Registry

### Phase 2: First Calculator 第一個計算器
- [ ] 實作 CKD-EPI 2021（含完整文獻引用）
- [ ] 撰寫單元測試
- [ ] 驗證 Tool Discovery 機制

### Phase 3: MCP Integration
- [ ] 實作 MCP Server
- [ ] 實作 Discovery Tools (list_categories, search_tools, get_tool_details)
- [ ] 實作 Calculator Tools (動態註冊)
- [ ] 測試與 Claude 整合

### Phase 4: More Calculators 擴充計算器
- [ ] Nephrology: MDRD, Cockcroft-Gault, FENa, ...
- [ ] Cardiology: CHA₂DS₂-VASc, HAS-BLED, HEART, ...
- [ ] Pulmonology: CURB-65, PSI, A-a Gradient, ...
- [ ] Emergency: APACHE II, SOFA, qSOFA, ...
- [ ] 目標: 50 → 100 → 200+

### Phase 5: API Server (Optional)
- [ ] FastAPI 實作
- [ ] OpenAPI 文檔
- [ ] Docker 部署

## 📝 Calculator 實作規範

每個計算器必須：

1. **繼承 BaseCalculator**
2. **提供完整 metadata**
   - LowLevelKey: 精確識別
   - HighLevelKey: 情境索引
   - References: 原始論文引用
3. **實作 calculate() 方法**
4. **返回 ScoreResult**
   - value: 計算結果
   - unit: 單位
   - interpretation: 臨床解讀（原創文字）
   - recommendations: 臨床建議
   - references: 文獻引用

### 範例

```python
class CkdEpi2021Calculator(BaseCalculator):
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="ckd_epi_2021",
                name="CKD-EPI 2021",
                purpose="Calculate eGFR without race",
                input_params=["age", "sex", "serum_creatinine"],
                output_type="eGFR (mL/min/1.73m²)"
            ),
            high_level=HighLevelKey(
                specialties=[Specialty.NEPHROLOGY],
                conditions=["CKD", "AKI", "Kidney Disease"],
                clinical_contexts=[
                    ClinicalContext.STAGING,
                    ClinicalContext.DRUG_DOSING
                ],
                clinical_questions=[
                    "What is the kidney function?",
                    "What stage of CKD?"
                ],
                icd10_codes=["N18.1", "N18.2", "N18.3"],
                keywords=["GFR", "eGFR", "creatinine", "kidney"]
            ),
            references=[
                Reference(
                    citation="Inker LA, et al. N Engl J Med. 2021;385(19):1737-1749",
                    doi="10.1056/NEJMoa2102953"
                )
            ]
        )
    
    def calculate(self, age: int, sex: str, serum_creatinine: float) -> ScoreResult:
        # 實作計算邏輯...
        pass
```

## 🔬 文獻引用規範

- **必須引用原始研究論文**
- **使用 Vancouver 格式**
- **包含 DOI/PMID**
- **禁止引用商業計算器網站**

## ⚠️ 注意事項

1. **Domain 層零外部依賴** - 不要 import 任何第三方庫
2. **所有文字原創** - 不複製任何商業來源
3. **公式驗證** - 對照原始論文驗證計算正確性
4. **邊界測試** - 每個計算器都要有邊界值測試
