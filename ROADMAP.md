# 🗺️ Medical Calculator MCP - Development Roadmap

> **Last Updated**: 2025-12-03
> **Current Version**: v1.0.0 (Production Ready)
> **Status**: 71 Calculator Files | 51 MCP Tools | 919 Tests | 88% Coverage

本文件聚焦於**未來改進計畫**。已完成功能請參閱 [README.md](README.md)。

> 📋 **2020-2025 指引缺口分析**: 參閱 [docs/GUIDELINE_RECOMMENDED_TOOLS_2020_2025.md](docs/GUIDELINE_RECOMMENDED_TOOLS_2020_2025.md)

---

## 📊 Quick Navigation | 快速導覽

| Section | Description |
|---------|-------------|
| [Improvement Areas](#-improvement-areas--改進方向) | 可改進的領域 |
| [New Calculators](#-new-calculators--新計算器) | 計畫新增的計算器 |
| [Infrastructure](#-infrastructure--基礎設施) | 技術改進計畫 |
| [Developer Experience](#-developer-experience--開發體驗) | 開發者工具改進 |
| [Timeline](#-timeline--時程規劃) | 開發時程 |

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
| **Test Coverage** | ✅ 88% | 90%+ | 🟡 MEDIUM |
| **E2E Tests** | ✅ 27 tests | Docker-based E2E | ✅ DONE |
| **Load Testing** | ❌ None | Locust / k6 scripts | 🟢 LOW |
| **Type Checking** | Partial | mypy --strict | 🟡 MEDIUM |

> **Testing Progress** (2025-12-03):
> - Total tests: 884 (was 799)
> - E2E tests: 27 tests (REST API, Clinical Workflows, Performance, Integration)
> - Coverage enhancement tests: 60 tests (Validation, Handlers, Edge cases)

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
| `calculate_iss` | Injury Severity Score | 創傷嚴重度評估 | Baker 1974 | ACS-COT | ❌ TODO |
| `calculate_rts` | Revised Trauma Score | 創傷生理評估 | Champion 1989 | ATLS | ❌ TODO |
| `calculate_triss` | TRISS | 創傷存活機率 | Boyd 1987 | TARN | ❌ TODO |
| `calculate_tbsa` | TBSA (Rule of Nines) | 燒傷面積計算 | Wallace 1951 | ABA | ❌ TODO |
| ~~`calculate_parkland`~~ | ~~Parkland Formula~~ | 燒傷輸液計算 | Baxter 1968 | ABA Guidelines | ✅ DONE |

### Phase 19: GI Bleeding Extended (消化道出血擴充)

> **Priority**: 🔴 HIGH | **Target**: 2026 Q1
> **Rationale**: Glasgow-Blatchford 和 AIMS65 為國際指引推薦 (PMID: 39400553)

| Tool ID | Name | Purpose | Reference | Guideline |
|---------|------|---------|-----------|-----------|
| `calculate_blatchford` | Glasgow-Blatchford Score | 上消化道出血需干預風險 | Blatchford 2000 | **ESGE 推薦** |
| `calculate_aims65` | AIMS65 Score | 上消化道出血死亡率 | Saltzman 2011 | **多指引推薦** |

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
| **PyPI Package** | 📋 Planned | `pip install medical-calc-mcp` |
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

\`\`\`
2025 Q4 ✅ COMPLETED
├── 71 Calculator Files (51 registered as MCP tools)
├── Docker + REST API + SSE + HTTPS
├── GitHub Actions CI + Pre-commit hooks
├── 919 tests, 88% coverage
├── Ruff lint errors fixed
├── ✅ SSE remote deployment fix (FastMCP built-in transport)
├── ✅ Reference class: level_of_evidence field added
├── ✅ Bishop Score + Ballard Score (Phase 17 Obstetrics)
├── ✅ Parkland Formula (Phase 18 Burns)
├── ✅ PEWS (Phase 20 Pediatrics)
├── ✅ Hunt & Hess + Fisher Grade (Phase 22 Neurology)
└── ✅ Security Module (Optional Rate Limiting + API Auth)

2026 Q1 (Current Focus)
├── ✅ Rate Limiting + API Auth (DONE)
├── Test coverage 90%+
├── Phase 18: Trauma (4 calculators remaining) - ISS, RTS, TRISS, TBSA
├── Phase 19: GI Bleeding (2 calculators) - Blatchford, AIMS65
├── 📦 PyPI package release (pip install medical-calc-mcp)
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
| Calculator Files | **71** | 80+ |
| MCP Tools | **51** | 60+ |
| Test Coverage | 88% | 90%+ |
| API Response Time (p95) | ~50ms | <100ms |
| Documentation | README only | Full MkDocs site |
| i18n Languages | 1 (EN) | 3 (EN, zh-TW, zh-CN) |
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
