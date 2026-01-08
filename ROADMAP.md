# 🗺️ Medical Calculator MCP - Development Roadmap

> **Last Updated**: 2026-01-08
> **Current Version**: v1.3.0 (Production Ready)
> **Status**: 82 Tools (75 Calculators + 7 Discovery) | 124 Core Tests | 92% Coverage

本文件聚焦於**未來改進計畫**。已完成功能請參閱 [README.md](README.md)。

> 📋 **2020-2025 指引缺口分析**: 參閱 [docs/GUIDELINE_RECOMMENDED_TOOLS_2020_2025.md](docs/GUIDELINE_RECOMMENDED_TOOLS_2020_2025.md)

---

## 📊 Quick Navigation | 快速導覽

| Section | Description |
|---------|-------------|
| [🎓 Academic Research Framework](#-academic-research-framework--學術研究框架) | **論文核心架構 (Neuro-Symbolic Framework)** |
| [📈 Benchmark Strategy](#-benchmark-strategy--評測策略) | **MedCalc-Bench 整合與自建評測集** |
| [🕸️ Clinical Knowledge Graph](#️-clinical-knowledge-graph--臨床知識圖譜) | **超圖/共病關聯 (Hypergraph)** |
| [Improvement Areas](#-improvement-areas--改進方向) | 可改進的領域 |
| [New Calculators](#-new-calculators--新計算器) | 計畫新增的計算器 |
| [Infrastructure](#-infrastructure--基礎設施) | 技術改進計畫 |
| [Developer Experience](#-developer-experience--開發體驗) | 開發者工具改進 |
| [Timeline](#-timeline--時程規劃) | 開發時程 |

---

## 🎓 Academic Research Framework | 學術研究框架

> **論文標題提案**: *"Medical-Calc-MCP: A Neuro-Symbolic Framework for Reliable Clinical Reasoning with Dynamic Knowledge Graphs and Automated Constraint Verification"*

### Core Innovation | 核心創新

本專案提出 **Neuro-Symbolic Framework**，結合 LLM 的自然語言理解與符號計算的精確性：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     NEURO-SYMBOLIC FRAMEWORK                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  MODULE 1: Discovery Engine (工具發現引擎)                           │   │
│  │  ────────────────────────────────────────────────────────────────── │   │
│  │  Input: User Query / Clinical Question                              │   │
│  │                                                                     │   │
│  │  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   │   │
│  │  │ High/Low Level  │   │   Hypergraph    │   │  Auto Metadata  │   │   │
│  │  │   Key Search    │ + │   Traversal     │ + │   Generation    │   │   │
│  │  │ (Two-Level Key) │   │ (Related Tools) │   │ (Self-Describe) │   │   │
│  │  └─────────────────┘   └─────────────────┘   └─────────────────┘   │   │
│  │                                                                     │   │
│  │  Output: Ranked Tool Set + Related Recommendations                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  MODULE 2: Reasoning Interface (推理介面)                            │   │
│  │  ────────────────────────────────────────────────────────────────── │   │
│  │  Input: Unstructured Clinical Context / EHR Data                    │   │
│  │                                                                     │   │
│  │  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   │   │
│  │  │  ParamMatcher   │   │ Semantic Slot   │   │  Multi-lingual  │   │   │
│  │  │ (Alias/Fuzzy)   │ → │    Filling      │ → │    Support      │   │   │
│  │  │   ✅ DONE       │   │ (Entity Align)  │   │ (Cr/肌酸酐/SCr) │   │   │
│  │  └─────────────────┘   └─────────────────┘   └─────────────────┘   │   │
│  │                                                                     │   │
│  │  Output: Structured DTO (Data Transfer Object)                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  MODULE 3: Safety Layer (安全層)                                     │   │
│  │  ────────────────────────────────────────────────────────────────── │   │
│  │  Input: Structured DTO                                              │   │
│  │                                                                     │   │
│  │  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   │   │
│  │  │ BoundaryValidator│   │Literature-Based │   │ Evidence-Based  │   │   │
│  │  │  (Clinical Range)│ → │Constraint Extract│ → │   Guardrails    │   │   │
│  │  │   ✅ DONE       │   │ (NLP from PDF)  │   │ (PMID-backed)   │   │   │
│  │  └─────────────────┘   └─────────────────┘   └─────────────────┘   │   │
│  │                                                                     │   │
│  │  Output: Validated Result / Error with Literature Citation          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Four Core Contributions | 四大核心貢獻

| # | Contribution | Academic Concept | Status | Implementation |
|---|--------------|------------------|--------|----------------|
| 1 | **Clinical Knowledge Graph** | Context-Aware Hypergraph | 📋 Planned | Tool relationship edges |
| 2 | **Parameter Slot Filling** | Semantic Entity Alignment | ✅ Done | ParamMatcher (60+ aliases) |
| 3 | **Auto Metadata Generation** | Self-Describing Agents | 📋 Planned | PDF → Schema Pipeline |
| 4 | **Literature-Based Constraints** | Evidence-Based Guardrails | ✅ Done | BoundaryValidator (17+ params) |

### Research Questions | 研究問題

1. **RQ1**: How can Hypergraph-based tool discovery improve clinical decision completeness compared to keyword/vector search?
2. **RQ2**: Does semantic parameter mapping reduce input errors compared to raw LLM extraction?
3. **RQ3**: Can literature-derived constraints prevent clinically impossible values while maintaining usability?

---

## 📈 Benchmark Strategy | 評測策略

### Current Academic Landscape | 學術現狀

| Benchmark | Focus | Medical Calculation? | Our Relevance |
|-----------|-------|---------------------|---------------|
| MedQA | Medical knowledge | ❌ No calculation | Low |
| PubMedQA | Literature QA | ❌ No calculation | Low |
| GSM8K | Math reasoning | ❌ Not medical | Low |
| **MedCalc-Bench** (NeurIPS 2024 Oral) | **Medical Calculation** | ✅ **55 formulas, 1000+ cases** | **🔴 Primary Baseline** |
| **BFCL** (Berkeley, 2025) | Tool/Function Calling | 🟡 General intent | Tool Discovery Eval |
| **API-BLEND** (ACL 2024) | Slot Filling | 🟢 Parameter extraction | ParamMatcher Eval |

> **Key Finding from MedCalc-Bench (arXiv:2406.12036)**:
> GPT-4 achieves only **~50% accuracy** on medical calculations. Main errors identified:
> 1. **Parameter Extraction Error**: Vocabulary mismatch (LLM uses wrong names).
> 2. **Calculation Logic Error**: Hallucinating formulas or wrong versions.
> 3. **Arithmetic Error**: Miscalculating numbers.

### Our Academic Value Levels | 學術價值層次

| Level | Feature | Academic Concept | Scholarly Value |
| :--- | :--- | :--- | :--- |
| **L1** | **Calculator Engine** | Validated Symbolic Execution | Extends LLM with precision |
| **L2** | **Tool Selection** | Hierarchical Tool Retrieval | Solves RAG precision issues |
| **L3** | **ParamMatcher** | Semantic Slot Filling | Solves vocabulary mismatch |
| **L4** | **BoundaryValidator** | **Literature-Derived Constraints** | **Unique Contribution** (Safety) |
| **L5** | **Clinical KG** | **Context-Aware Hypergraph** | **Unique Contribution** (Workflow) |

### Proposed Evaluation Framework | 評測框架

1. **MedCalc-Bench Integration (Baseline Comparison)**

   - Dataset: 55 formulas × 1000+ clinical vignettes.
   - Comparison: GPT-4o Direct Answer (Baseline) vs. GPT-4o + Medical-Calc-MCP.
   - Hypothesis: 50% → 95%+ accuracy improvement.

2. **Parameter Extraction Ablation (ParamMatcher Eval)**

   - Measure F1-score of matching clinical notes to tool parameters.
   - Variants: Raw LLM Extraction vs. LLM + Alias Table vs. Full ParamMatcher (Fuzzy/Suffix).

3. **Adversarial Safety Evaluation (BoundaryValidator Eval)**

   - **Unique Metric**: "Boundary Violation Recapture Rate".
   - Input: Adversarial clinical data (e.g. Weight=500kg, Temp=20°C).
   - Goal: Compare LLM's "hallucinated compliance" vs. our PMID-backed rejection/warning.

4. **Agentic Tool Selection (Hypergraph/Two-Level Key Eval)**

   - Input: Ambiguous clinical scenarios requiring multi-step assessment.
   - Metric: Precision@1 and Completion Rate of clinical workflows (e.g. Sepsis screening).

### Evaluation Metrics | 評測指標

| Metric | Description | Target |
| :--- | :--- | :--- |
| **Calculation Accuracy** | Exact match with ground truth | >95% |
| **Parameter Extraction F1** | Correct value extraction from vignette | >90% |
| **Tool Selection Precision@1** | Correct tool selected first | >85% |
| **Boundary Capture Rate** | % of clinically impossible values detected | 100% |
| **Safety Confidence** | % of warnings citing literature (PMID) | 100% |

### Implementation Roadmap | 實作路線

| Phase | Task | Timeline | Status |
|-------|------|----------|--------|
| B1 | Integrate MedCalc-Bench dataset | 2026 Q1 | 📋 Planned |
| B2 | Generate Med-MCP-Eval (820 cases) | 2026 Q1 | 📋 Planned |
| B3 | Implement Tool Selection eval | 2026 Q2 | 📋 Planned |
| B4 | Run baseline experiments (GPT-4o) | 2026 Q2 | 📋 Planned |
| B5 | Publish benchmark results | 2026 Q3 | 📋 Planned |

---

## 🕸️ Clinical Knowledge Graph | 臨床知識圖譜

> **Academic Concept**: Context-Aware Hypergraph / Clinical Decision Support Graph

### Motivation | 動機

傳統工具檢索是**線性的**（Keyword Search）或**向量相似度**（Vector Similarity）。
但醫療決策**不是孤立的**——工具之間存在**臨床關聯性**。

**Example**: 當查詢 `CHA₂DS₂-VASc` (中風風險) 時，系統應自動提示 `HAS-BLED` (出血風險)，
因為這兩個分數在臨床上**總是成對出現**以評估抗凝血劑用藥。

### Graph Edge Types | 邊類型

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CLINICAL KNOWLEDGE GRAPH                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Edge Type 1: PRE-REQUISITE (前置條件)                                      │
│  ─────────────────────────────────────                                      │
│  • qSOFA ──[screen_positive]──→ SOFA (qSOFA≥2 時需完整 SOFA)                │
│  • RASS ──[required_for]──→ CAM-ICU (CAM-ICU 需要先評估 RASS)               │
│  • NEWS2 ──[triggers]──→ Sepsis Workup (NEWS2≥5 時觸發敗血症篩檢)           │
│                                                                             │
│  Edge Type 2: RISK-BENEFIT PAIR (風險效益對)                                 │
│  ─────────────────────────────────────────                                  │
│  • CHA₂DS₂-VASc ←──[balance]──→ HAS-BLED (中風風險 vs 出血風險)              │
│  • Caprini VTE ←──[balance]──→ Bleeding Risk (血栓風險 vs 出血風險)          │
│  • RCRI ←──[inform]──→ ASA-PS (心臟風險 ↔ 整體手術風險)                      │
│                                                                             │
│  Edge Type 3: COMORBIDITY (共病關聯)                                         │
│  ─────────────────────────────────────                                      │
│  • CKD-EPI ──[affects_dosing]──→ Drug Dosing Calculators                    │
│  • Child-Pugh ──[affects]──→ MELD (兩者都評估肝功能)                         │
│  • SOFA ──[organ_specific]──→ KDIGO AKI (SOFA腎臟分項 ↔ AKI分期)            │
│                                                                             │
│  Edge Type 4: WORKFLOW (臨床流程)                                           │
│  ─────────────────────────────────                                          │
│  • Sepsis Pathway: qSOFA → SOFA → RASS → CAM-ICU                           │
│  • Preop Pathway: ASA → RCRI → Mallampati → STOP-BANG                      │
│  • GI Bleed Pathway: Glasgow-Blatchford → Rockall → Endoscopy Decision     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Visual Graph Example | 圖譜視覺化

```
                        ┌─────────────┐
                        │   qSOFA     │
                        │ (Screening) │
                        └──────┬──────┘
                               │ screen_positive
                               ▼
    ┌──────────┐         ┌─────────────┐         ┌──────────┐
    │   RASS   │◄────────│    SOFA     │────────►│  APACHE  │
    │(Sedation)│required │  (Sepsis-3) │ compare │   II     │
    └────┬─────┘         └─────────────┘         └──────────┘
         │ required_for
         ▼
    ┌──────────┐
    │ CAM-ICU  │
    │(Delirium)│
    └──────────┘


    ┌──────────────┐                    ┌──────────────┐
    │ CHA₂DS₂-VASc │◄───── balance ────►│   HAS-BLED   │
    │ (Stroke Risk)│                    │(Bleed Risk)  │
    └──────────────┘                    └──────────────┘
           │                                    │
           └──────────► Anticoagulation ◄───────┘
                         Decision
```

### Implementation Plan | 實作計畫

| Phase | Task | Description | Timeline |
|-------|------|-------------|----------|
| G1 | Define Edge Schema | Create `GraphEdge` dataclass with edge types | 2026 Q1 |
| G2 | Manual Graph Population | Define 50+ edges for existing 75 calculators | 2026 Q1 |
| G3 | Graph Query API | `get_related_tools(tool_id)` MCP tool | 2026 Q2 |
| G4 | Workflow Prompts | Auto-generate multi-tool prompts | 2026 Q2 |
| G5 | LLM-Assisted Expansion | Use GPT-4 to suggest new edges from literature | 2026 Q3 |

### Data Structure | 資料結構

```python
@dataclass
class GraphEdge:
    source_tool: str           # e.g., "qsofa_score"
    target_tool: str           # e.g., "sofa_score"
    edge_type: EdgeType        # PRE_REQUISITE, RISK_BENEFIT_PAIR, COMORBIDITY, WORKFLOW
    condition: str | None      # e.g., "qSOFA >= 2"
    clinical_rationale: str    # e.g., "Sepsis-3 recommends full SOFA if qSOFA positive"
    reference: str | None      # e.g., "Singer 2016 JAMA"
    bidirectional: bool        # True for RISK_BENEFIT_PAIR

class ClinicalKnowledgeGraph:
    def get_related_tools(self, tool_id: str) -> list[RelatedTool]
    def get_workflow(self, context: str) -> list[str]  # Ordered tool sequence
    def suggest_next(self, completed_tools: list[str]) -> list[str]
```

---

## 🎯 Improvement Areas | 改進方向

### 1. 🔐 Security & Production Readiness | 安全與生產就緒

| Item | Current | Target | Priority |
|------|---------|--------|----------|
| **Rate Limiting** | ✅ Optional | ✅ Request throttling | ✅ DONE |
| **API Authentication** | ✅ Optional | ✅ API Key | ✅ DONE |
| **Request Logging** | ❌ Basic | ✅ Structured logging | 🟡 MEDIUM |
| **Health Metrics** | ❌ Basic | ✅ Prometheus metrics | 🟡 MEDIUM |

> **Security Update** (2025-12-03):
> - Rate Limiting: Token bucket algorithm, per-IP, configurable via env vars
> - API Authentication: API Key based, constant-time comparison, disabled by default
> - All security features optional - enable via `SECURITY_*` environment variables

### 2. 🌐 Internationalization (i18n) | 國際化

| Item | Current | Target | Priority |
|------|---------|--------|----------|
| **繁體中文 (zh-TW)** | 部分 | ✅ 完整支援 | 🟡 MEDIUM |
| **簡體中文 (zh-CN)** | ❌ None | ✅ Full support | 🟢 LOW |
| **日本語 (ja)** | ❌ None | ✅ Full support | 🟢 LOW |
| **Tool Descriptions** | EN only | Multi-language | 🟡 MEDIUM |

### 3. 📊 Observability | 可觀測性

| Item | Current | Target | Priority |
|------|---------|--------|----------|
| **Structured Logging** | print() | JSON logging (structlog) | 🟡 MEDIUM |
| **Request Tracing** | ❌ None | OpenTelemetry | 🟢 LOW |
| **Metrics Export** | ❌ None | Prometheus /metrics | 🟡 MEDIUM |
| **Error Tracking** | ❌ None | Sentry integration | 🟢 LOW |

### 4. 🧪 Testing & Quality | 測試與品質

| Item | Current | Target | Priority |
|------|---------|--------|----------|
| **Test Coverage** | ✅ 92% | 90%+ | 🟢 HIGH |
| **E2E Tests** | ✅ 697 tests (77 files) | Full Calculator Coverage | ✅ DONE |
| **Load Testing** | ❌ None | Locust / k6 scripts | 🟢 LOW |
| **Type Checking** | ✅ 100% | mypy --strict | ✅ DONE |

> **Testing Progress** (2025-12-09):
> - Total tests: 1639 (was 940)
> - E2E tests: 697 tests across 77 test files (one per calculator)
> - Full REST API endpoint coverage for all 75 calculators
> - Tests include clinical scenarios, edge cases, and error handling

### 5. 🛡️ Parameter Boundary Validation | 參數邊界驗證 (NEW!)

> **Priority**: 🔴 HIGH | **Target**: 2026 Q1
> **Rationale**: MCP 自動防呆，確保輸入值在臨床有效範圍內

| Item | Current | Target | Priority |
|------|---------|--------|----------|
| **BoundarySpec** | ✅ Core module | Production ready | ✅ DONE |
| **Reference Backed** | ✅ 15+ params | 50+ params with PMID | 🔴 HIGH |
| **Auto-validation** | 📋 Planned | Integrated in calculate() | 🔴 HIGH |
| **Markdown Docs** | ✅ Auto-generated | Full parameter docs | 🟡 MEDIUM |

**設計架構:**
```
BoundaryRegistry
├── BoundarySpec (參數邊界規範)
│   ├── physiological_min/max (生理極限 - 超出=錯誤)
│   ├── warning_min/max (警告閾值 - 超出=需複檢)
│   ├── clinical_min/max (臨床常見範圍)
│   └── BoundaryReference (文獻來源 - PMID/DOI)
└── validate_all(params) → ValidationResult[]
```

**已定義參數邊界:**
- Vital Signs: temperature, heart_rate, respiratory_rate, systolic_bp, MAP, SpO2
- Renal: serum_creatinine, BUN
- Hematology: hemoglobin, hematocrit, platelets
- Liver: bilirubin
- Demographics: age, weight_kg
- Oxygenation: FiO2, P/F ratio
- Scores: GCS, RASS

---

## 🧮 New Calculators | 新計算器

### Phase 17: Obstetrics (產科) ✅ COMPLETED

> **Status**: ✅ DONE | **Completed**: 2025-12-03

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| \`calculate_bishop_score\` | Bishop Score | 子宮頸成熟度/引產評估 | Bishop 1964 |
| \`calculate_ballard_score\` | Ballard Score (New Ballard) | 新生兒胎齡評估 | Ballard 1991 |

### Phase 18: Trauma & Burns (創傷與燒傷)

> **Priority**: 🔴 HIGH | **Target**: 2026 Q1
> **Rationale**: 創傷評分為國際標準

| Tool ID | Name | Purpose | Reference | Guideline | Status |
|---------|------|---------|-----------|-----------|--------|
| `calculate_iss` | Injury Severity Score | 創傷嚴重度評估 | Baker 1974 | ACS-COT | ✅ DONE |
| `calculate_rts` | Revised Trauma Score | 創傷生理評估 | Champion 1989 | ATLS | ❌ TODO |
| `calculate_triss` | TRISS | 創傷存活機率 | Boyd 1987 | TARN | ❌ TODO |
| `calculate_tbsa` | TBSA (Rule of Nines) | 燒傷面積計算 | Wallace 1951 | ABA | ✅ DONE |
| ~~`calculate_parkland`~~ | ~~Parkland Formula~~ | 燒傷輸液計算 | Baxter 1968 | ABA Guidelines | ✅ DONE |

### Phase 19: GI Bleeding Extended (消化道出血擴充) ✅ COMPLETED

> **Status**: ✅ DONE | **Completed**: 2025-12-03
> **Rationale**: Glasgow-Blatchford 和 AIMS65 為國際指引推薦 (PMID: 39400553)

| Tool ID | Name | Purpose | Reference | Guideline | Status |
|---------|------|---------|-----------|-----------|--------|
| `calculate_glasgow_blatchford` | Glasgow-Blatchford Score | 上消化道出血需干預風險 | Blatchford 2000 | **ESGE 推薦** | ✅ DONE |
| `calculate_aims65` | AIMS65 Score | 上消化道出血死亡率 | Saltzman 2011 | **多指引推薦** | ✅ DONE |
| `calculate_spesi` | Simplified PESI | PE 30天死亡率 | Jiménez 2010 | **ESC 2019 Class I** | ✅ DONE (Bonus) |

### Phase 20: Pediatric Safety (小兒安全) ✅ COMPLETED

> **Status**: ✅ DONE | **Completed**: 2025-12-02

| Tool ID | Name | Purpose | Reference | Guideline |
|---------|------|---------|-----------|-----------|
| `calculate_pews` | Brighton PEWS | 小兒早期預警 | Monaghan 2005 | RCPCH |

### Phase 21: Gastroenterology Extended (消化科擴充)

> **Priority**: 🟡 MEDIUM | **Target**: 2026 Q2

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `calculate_lille` | Lille Model | 酒精性肝炎類固醇反應 | Louvet 2007 |
| `calculate_maddrey` | Maddrey's DF | 酒精性肝炎嚴重度 | Maddrey 1978 |

### Phase 22: Neurology Extended (神經科擴充) ✅ COMPLETED

> **Status**: ✅ DONE | **Completed**: 2025-12-02

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `calculate_hunt_hess` | Hunt & Hess Grade | SAH 臨床嚴重度 | Hunt 1968 |
| `calculate_fisher_grade` | Fisher Grade | SAH CT 分級 | Fisher 1980 |

### Phase 23: Cardiac Surgery (心臟手術擴充)

> **Priority**: 🟡 MEDIUM | **Target**: 2026 Q3

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `calculate_euroscore2` | EuroSCORE II | 心臟手術死亡率 | Nashef 2012 |

---

## 🛠️ Infrastructure | 基礎設施

### API Gateway & Security (安全閘道)

> **Priority**: 🔴 HIGH

| Feature | Description | Approach |
|---------|-------------|----------|
| **Rate Limiting** | 限制請求頻率 | slowapi / redis-based |
| **API Key Auth** | API 金鑰認證 | Header-based X-API-Key |
| **OAuth2 (Optional)** | 企業級認證 | FastAPI OAuth2 |
| **Request Validation** | 請求大小限制 | Middleware |

### Cloud Deployment Templates (雲端部署模板)

> **Priority**: 🟡 MEDIUM

| Platform | Status | Template |
|----------|--------|----------|
| **Docker Compose** | ✅ Done | `docker-compose.yml` |
| **Kubernetes** | 📋 Planned | `k8s/` manifests |
| **AWS ECS/Fargate** | 📋 Planned | CloudFormation / Terraform |
| **GCP Cloud Run** | 📋 Planned | `cloudbuild.yaml` |

### Package Distribution (套件發布)

> **Priority**: 🟡 MEDIUM

| Item | Status | Description |
|------|--------|-------------|
| **PyPI Package** | 📋 Planned | `uv add medical-calc-mcp` |
| **GitHub Releases** | 📋 Planned | Automated versioning with tags |
| **Docker Hub** | 📋 Planned | `docker pull medical-calc-mcp` |

---

## 🧑‍💻 Developer Experience | 開發體驗

### Calculator CLI Generator (計算器產生器)

> **Priority**: 🟡 MEDIUM

\`\`\`bash
# Future CLI usage
python -m medical_calc.cli new calculator \\
    --name "Bishop Score" \\
    --specialty obstetrics \\
    --reference "Bishop 1964"
\`\`\`

### Documentation Site (文件網站)

> **Priority**: 🟡 MEDIUM

使用 MkDocs Material 建立文件網站：

| Section | Content |
|---------|---------|
| **Getting Started** | 快速開始指南 |
| **Calculator Reference** | 所有計算器 API 文件 |
| **Clinical Workflows** | 臨床工作流程範例 |
| **API Reference** | REST API 完整文件 |

---

## 📅 Timeline | 時程規劃

```
2025 Q4 ✅ COMPLETED
├── 70 Calculators = 70 MCP Tools (all registered!)
├── Docker + REST API + SSE + HTTPS
├── GitHub Actions CI + Pre-commit hooks
├── 1566 tests, 92% coverage
├── Ruff lint errors fixed
├── ✅ SSE remote deployment fix (FastMCP built-in transport)
├── ✅ Reference class: level_of_evidence field added
├── ✅ Bishop Score + Ballard Score (Phase 17 Obstetrics)
├── ✅ Parkland Formula (Phase 18 Burns)
├── ✅ PEWS (Phase 20 Pediatrics)
├── ✅ Hunt & Hess + Fisher Grade (Phase 22 Neurology)
├── ✅ Security Module (Optional Rate Limiting + API Auth)
└── ✅ Infectious Disease + Obstetrics MCP handlers added

2026 Q1 (Current Focus)
├── ✅ Rate Limiting + API Auth (DONE)
├── ✅ BoundarySpec Module (DONE) - 參數邊界驗證框架
├── ✅ E2E Workflow Tests (DONE) - 17 production-quality tests
├── ✅ ParamMatcher Service (DONE) - 智慧參數匹配
├── 📋 Boundary Integration - 整合至 calculate() 流程
├── Test coverage 90%+
├── Phase 18: Trauma (4 calculators remaining) - ISS, RTS, TRISS, TBSA
├── Phase 19: GI Bleeding (2 calculators) - Blatchford, AIMS65
├── 📦 PyPI package release (uv add medical-calc-mcp)
├── 🏷️ GitHub Release workflow (automated versioning)
└── Target: 77 calculators

2026 Q2 (Planned)
├── Phase 21: Gastroenterology Extended (Lille, Maddrey)
├── Phase 23: Cardiac Surgery (EuroSCORE II)
├── i18n Framework (zh-TW, zh-CN)
├── Kubernetes templates
├── Documentation site (MkDocs)
└── Target: 80+ calculators

2026 Q3 (Planned)
├── Calculator CLI generator
├── Cloud deployment templates
└── Target: 85+ calculators
\`\`\`

---

## 📋 Priority Queue | 優先佇列

### Immediate (Next Sprint)

| Rank | Item | Category | Effort |
|------|------|----------|--------|
| 1 | ~~Rate Limiting~~ | ~~Security~~ | ✅ DONE |
| 2 | ~~API Key Authentication~~ | ~~Security~~ | ✅ DONE |
| 3 | Structured Logging | Observability | S |
| 4 | Test Coverage 90% | Testing | M |

### Short-term (Next Month)

| Rank | Item | Category | Effort |
|------|------|----------|--------|
| 5 | ISS Calculator | Trauma | S |
| 6 | RTS Calculator | Trauma | S |
| 7 | TRISS Calculator | Trauma | M |
| 8 | TBSA Calculator | Burns | S |
| 9 | Blatchford Score | GI Bleeding | S |
| 10 | AIMS65 Score | GI Bleeding | S |

### Long-term (Next Quarter)

| Rank | Item | Category | Effort |
|------|------|----------|--------|
| 11 | Kubernetes templates | Infra | M |
| 12 | MkDocs Site | DX | M |
| 13 | Calculator CLI generator | DX | L |
| 14 | Prometheus metrics | Observability | M |

**Effort Legend**: S = Small (1-2 days), M = Medium (3-5 days), L = Large (1-2 weeks)

---

## 🏆 Success Metrics | 成功指標

| Metric | Current | Target (2026 Q2) |
|--------|---------|------------------|
| Calculator Files | **75** | 80+ |
| MCP Tools | **82** | 85+ |
| Total Tests | **1566** | 1800+ |
| E2E Tests | **697** | 750+ |
| Test Coverage | **92%** | 95%+ |
| API Response Time (p95) | ~50ms | <100ms |
| Documentation | **i18n (EN/ZH)** | Full MkDocs site |
| i18n Languages | 2 (EN, zh-TW) | 3 (EN, zh-TW, zh-CN) |
| Security Features | ✅ CORS + HTTPS + Rate Limit + Auth | ✅ Complete |

---

## 🤝 Contributing | 貢獻

歡迎貢獻！請參閱 [CONTRIBUTING.md](CONTRIBUTING.md)。

### Quick Contribution Ideas

1. **🧮 新計算器** - 從 Priority Queue 選擇一個 (ISS, RTS, TRISS, TBSA, Blatchford, AIMS65)
2. **📝 文件** - 改善 README 或新增範例
3. **🧪 測試** - 提高測試覆蓋率至 90%
4. **🌐 翻譯** - 協助翻譯工具描述為中文
5. **📊 Observability** - 實作 Structured Logging 或 Prometheus metrics

---

*This roadmap focuses on future improvements. For completed features, see [README.md](README.md).*

*本路線圖聚焦於未來改進。已完成功能請參閱 [README.md](README.md)。*
