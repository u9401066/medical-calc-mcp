# 🗺️ Medical Calculator MCP - Development Roadmap

> **Last Updated**: 2025-12-02
> **Current Version**: v1.0.0 (Production Ready)
> **Status**: 64 Calculators | 641 Tests | 81% Coverage

本文件聚焦於**未來改進計畫**。已完成功能請參閱 [README.md](README.md)。

---

## ✅ Recently Completed | 最近完成 (2025-12-02)

| Item | Description | Status |
|------|-------------|--------|
| **Unused Imports Cleanup** | 移除 38 處未使用的導入 | ✅ Done |
| **Version Unification** | 統一版本號為 v1.0.0 | ✅ Done |
| **GitHub Actions CI** | 自動測試 + ruff 檢查 + 覆蓋率 | ✅ Done |
| **Pre-commit Hooks** | 提交前自動檢查程式碼品質 | ✅ Done |
| **Production Status** | Development Status 升級為 Stable | ✅ Done |

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

根據專案現況分析，以下是主要改進方向：

### 1. 🔐 Security & Production Readiness | 安全與生產就緒

| Item | Current | Target | Priority |
|------|---------|--------|----------|
| **Rate Limiting** | ❌ None | ✅ Request throttling | 🔴 HIGH |
| **API Authentication** | ❌ None | ✅ API Key / OAuth2 | 🔴 HIGH |
| **Request Logging** | ❌ Basic | ✅ Structured logging | 🟡 MEDIUM |
| **Health Metrics** | ❌ Basic | ✅ Prometheus metrics | 🟡 MEDIUM |
| **CORS Configuration** | ✅ Done | ✅ Complete | ✅ DONE |
| **Input Validation** | ✅ Done | ✅ Complete | ✅ DONE |

### 2. 🌐 Internationalization (i18n) | 國際化

| Item | Current | Target | Priority |
|------|---------|--------|----------|
| **繁體中文 (zh-TW)** | 部分 | ✅ 完整支援 | 🟡 MEDIUM |
| **簡體中文 (zh-CN)** | ❌ None | ✅ Full support | 🟢 LOW |
| **日本語 (ja)** | ❌ None | ✅ Full support | 🟢 LOW |
| **Tool Descriptions** | EN only | Multi-language | 🟡 MEDIUM |
| **Error Messages** | EN only | Multi-language | 🟡 MEDIUM |

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
| **Test Coverage** | 81% | 90%+ | 🟡 MEDIUM |
| **E2E Tests** | ❌ None | Docker-based E2E | 🟡 MEDIUM |
| **Load Testing** | ❌ None | Locust / k6 scripts | 🟢 LOW |
| **Mutation Testing** | ❌ None | mutmut | 🟢 LOW |
| **Type Checking** | Partial | mypy --strict | 🟡 MEDIUM |
| **CI/CD Pipeline** | ✅ Done | GitHub Actions | ✅ DONE |
| **Pre-commit Hooks** | ✅ Done | ruff + bandit | ✅ DONE |

---

## 🧮 New Calculators | 新計算器

### Phase 12: Neurology Extended (神經科擴充) ✅ COMPLETED

> **Status**: ✅ DONE | **Completed**: 2025-12-02

| Tool ID | Name | Purpose | Reference | Status |
|---------|------|---------|-----------|--------|
| `calculate_hunt_hess` | Hunt & Hess Scale | SAH 分級預後 | Hunt 1968 | ✅ Done |
| `calculate_fisher_grade` | Fisher Grade | SAH CT 分級 (Original + Modified) | Fisher 1980, Frontera 2006 | ✅ Done |
| `calculate_four_score` | FOUR Score | 優於 GCS 的昏迷評估 (E/M/B/R) | Wijdicks 2005 | ✅ Done |
| `calculate_ich_score` | ICH Score | 腦出血 30 天死亡率預測 | Hemphill 2001 | ✅ Done |

**全部完成**: NIHSS ✅, ABCD2 ✅, mRS ✅, Hunt & Hess ✅, Fisher ✅, FOUR ✅, ICH ✅ (7 tools)

### Phase 13: Infectious Disease (感染症)

> **Priority**: 🟡 MEDIUM | **Target**: 2026 Q1

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `calculate_mascc` | MASCC Score | 嗜中性白血球低下發燒風險 | Klastersky 2000 |
| `calculate_pitt_bacteremia` | Pitt Bacteremia | 菌血症預後 | Paterson 2004 |
| `calculate_centor` | Centor/McIsaac | 咽炎抗生素決策 | Centor 1981 |
| `calculate_quick_cpis` | Clinical Pulmonary Infection Score | VAP 診斷輔助 | Pugin 1991 |

### ~~Phase 14: Common Utilities (通用工具)~~ ✅ COMPLETED

> **Completed**: 2025-12-02 | **4/4 tools**

| Tool ID | Name | Purpose | Reference | Status |
|---------|------|---------|-----------|--------|
| `calculate_bsa` | Body Surface Area | 化療/燒傷計算 | Du Bois 1916, Mosteller | ✅ Done |
| `calculate_cockcroft_gault` | Creatinine Clearance | 藥物劑量調整 | Cockcroft-Gault 1976 | ✅ Done |
| `calculate_corrected_calcium` | Albumin-Corrected Ca | 真實血鈣評估 | Payne 1973 | ✅ Done |
| `calculate_parkland_formula` | Parkland Formula | 燒傷輸液計劃 | Baxter 1968 | ✅ Done |

**全部完成**: BSA ✅, Cockcroft-Gault ✅, Corrected Calcium ✅, Parkland ✅ (4 tools)

### Phase 15: Obstetrics & Pediatrics (婦產兒科)

> **Priority**: 🟢 LOW | **Target**: 2026 Q3

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `calculate_bishop_score` | Bishop Score | 子宮頸成熟度/引產評估 | Bishop 1964 |
| `calculate_apgar` | APGAR Score | 新生兒評估 | Apgar 1953 |
| `calculate_pews` | Pediatric Early Warning | 兒童病情惡化 | Parshuram 2009 |
| `calculate_ballard` | Ballard Score | 新生兒胎齡評估 | Ballard 1991 |

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
| **IP Allowlist** | 白名單機制 | Middleware |

**Implementation Example:**
```python
# Rate limiting with slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/v1/calculate/{tool_id}")
@limiter.limit("100/minute")
async def calculate(...):
    ...
```

### Cloud Deployment Templates (雲端部署模板)

> **Priority**: 🟡 MEDIUM

| Platform | Status | Template |
|----------|--------|----------|
| **Docker Compose** | ✅ Done | `docker-compose.yml` |
| **Kubernetes** | 📋 Planned | `k8s/` manifests |
| **AWS ECS/Fargate** | 📋 Planned | CloudFormation / Terraform |
| **GCP Cloud Run** | 📋 Planned | `cloudbuild.yaml` |
| **Azure Container Apps** | 📋 Planned | ARM template |

### Streamable HTTP Transport (MCP 串流傳輸)

> **Priority**: 🟢 LOW

MCP SDK 支援的新傳輸方式，適合長時間連線場景：

```python
# Future: Streamable HTTP
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("medical-calc")
mcp.run(transport="streamable-http")
```

---

## 🧑‍💻 Developer Experience | 開發體驗

### Calculator CLI Generator (計算器產生器)

> **Priority**: 🟡 MEDIUM

自動產生新計算器的腳手架工具：

```bash
# Future CLI usage
python -m medical_calc.cli new calculator \
    --name "Bishop Score" \
    --specialty obstetrics \
    --reference "Bishop 1964"

# Generates:
# - src/domain/services/calculators/bishop_score.py
# - tests/test_bishop_score.py
# - Updates __init__.py
```

### VS Code Extension (VS Code 擴充)

> **Priority**: 🟢 LOW

提供開發者更好的編輯體驗：

| Feature | Description |
|---------|-------------|
| **Calculator Snippets** | 快速插入計算器模板 |
| **Reference Lookup** | 快速查詢論文 PMID |
| **Test Runner** | 一鍵執行單一計算器測試 |
| **Validation Preview** | 即時預覽參數驗證 |

### Documentation Site (文件網站)

> **Priority**: 🟡 MEDIUM

使用 MkDocs Material 建立文件網站：

| Section | Content |
|---------|---------|
| **Getting Started** | 快速開始指南 |
| **Calculator Reference** | 所有計算器 API 文件 |
| **Clinical Workflows** | 臨床工作流程範例 |
| **API Reference** | REST API 完整文件 |
| **Contributing** | 貢獻者指南 |

```bash
# Future docs build
pip install mkdocs-material
mkdocs build
mkdocs serve  # http://localhost:8000
```

---

## 🔧 Technical Debt | 技術債

### Code Quality Issues (程式碼品質)

| Issue | Location | Status |
|-------|----------|--------|
| **Pydantic deprecation** | `api/server.py` | ✅ Fixed |
| **Type hints incomplete** | Various | 📋 Add mypy --strict |
| **Docstring inconsistency** | Some calculators | 📋 Standardize format |
| **Test duplication** | test_*.py | 📋 Extract fixtures |

### Architecture Improvements (架構改進)

| Item | Current | Improved |
|------|---------|----------|
| **Result serialization** | Manual `asdict()` | Dedicated serializer |
| **Error handling** | String messages | Error codes + i18n |
| **Configuration** | Environment vars | Pydantic Settings |
| **Dependency injection** | Manual | FastAPI Depends |

---

## 📅 Timeline | 時程規劃

```
2025 Q4 (Current - DONE ✅)
├── 64 Calculators complete (Phase 15 done!)
├── Security audit complete  
├── Docker + REST API + SSE + HTTPS complete
├── GitHub Actions CI + Pre-commit hooks ✅
├── Phase 15: Pediatric Scores ✅ (APGAR, PEWS, pSOFA, PIM3, pGCS)
└── 641 tests, 81% coverage

2026 Q1 (Planned)
├── Phase 16: Infectious Disease (4 calculators)
├── Rate Limiting + API Auth
├── Test coverage 85%+
└── Target: 68 calculators

2026 Q2 (Planned)
├── Phase 14: Common Utilities (4 calculators)
├── i18n Framework (zh-TW, zh-CN)
├── Kubernetes templates
├── Documentation site (MkDocs)
└── Target: 63 calculators

2026 Q3 (Planned)
├── Phase 15: Obstetrics & Pediatrics (4 calculators)
├── Calculator CLI generator
├── Cloud deployment templates
├── Test coverage 90%+
└── Target: 67+ calculators
```

---

## 📋 Priority Queue | 優先佇列

### Immediate (Next Sprint) - Security First

| Rank | Item | Category | Effort | Status |
|------|------|----------|--------|--------|
| 1 | Rate Limiting | Security | S | 📋 TODO |
| 2 | API Key Authentication | Security | M | 📋 TODO |
| 3 | Structured Logging | Observability | S | 📋 TODO |
| 4 | Hunt & Hess Calculator | Neurology | S | ✅ Done |
| 5 | Fisher Grade Calculator | Neurology | S | ✅ Done |

### Short-term (Next Month)

| Rank | Item | Category | Effort | Status |
|------|------|----------|--------|--------|
| 6 | FOUR Score Calculator | Neurology | M | ✅ Done |
| 7 | ICH Score Calculator | Neurology | S | ✅ Done |
| 8 | MASCC Score Calculator | Infectious | M | 📋 TODO |
| 9 | i18n Framework | DX | L | 📋 TODO |
| 10 | MkDocs Site | DX | M | 📋 TODO |

### Long-term (Next Quarter)

| Rank | Item | Category | Effort |
|------|------|----------|--------|
| 11 | Kubernetes templates | Infra | M |
| 12 | Calculator CLI generator | DX | L |
| 13 | Prometheus metrics | Observability | M |
| 14 | Load testing suite | Testing | M |
| 15 | OpenTelemetry tracing | Observability | M |

**Effort Legend**: S = Small (1-2 days), M = Medium (3-5 days), L = Large (1-2 weeks)

---

## 🏆 Success Metrics | 成功指標

| Metric | Current | Target (2026 Q2) |
|--------|---------|------------------|
| Calculators | **64** | 70+ |
| Test Coverage | 81% | 90%+ |
| API Response Time (p95) | ~50ms | <100ms |
| Documentation | README only | Full MkDocs site |
| i18n Languages | 1 (EN) | 3 (EN, zh-TW, zh-CN) |
| Production Deployments | 0 | 3+ (examples) |
| Security Features | CORS + HTTPS | Rate limit + Auth |
| CI/CD | ✅ GitHub Actions | Full pipeline |

---

## 🤝 Contributing | 貢獻

歡迎貢獻！請參閱 [CONTRIBUTING.md](CONTRIBUTING.md)。

### Quick Contribution Ideas

1. **🔐 Security** - 實作 Rate Limiting 或 API Auth
2. **🧮 新計算器** - 從 Priority Queue 選擇一個
3. **📝 文件** - 改善 README 或新增範例
4. **🧪 測試** - 提高測試覆蓋率
5. **🌐 翻譯** - 協助翻譯工具描述為中文
6. **🐛 Bug 修復** - 查看 Issues 清單

---

*This roadmap focuses on future improvements. For completed features, see [README.md](README.md).*

*本路線圖聚焦於未來改進。已完成功能請參閱 [README.md](README.md)。*
