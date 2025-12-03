# 🗺️ Medical Calculator MCP - Development Roadmap

> **Last Updated**: 2025-12-03
> **Current Version**: v1.0.0 (Production Ready)
> **Status**: 68 Calculators | 768 Tests | 85% Coverage

本文件聚焦於**未來改進計畫**。已完成功能請參閱 [README.md](README.md)。

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
| **Rate Limiting** | ❌ None | ✅ Request throttling | 🔴 HIGH |
| **API Authentication** | ❌ None | ✅ API Key / OAuth2 | 🔴 HIGH |
| **Request Logging** | ❌ Basic | ✅ Structured logging | 🟡 MEDIUM |
| **Health Metrics** | ❌ Basic | ✅ Prometheus metrics | 🟡 MEDIUM |

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
| **Test Coverage** | 85% | 90%+ | 🟡 MEDIUM |
| **E2E Tests** | ❌ None | Docker-based E2E | 🟡 MEDIUM |
| **Load Testing** | ❌ None | Locust / k6 scripts | 🟢 LOW |
| **Type Checking** | Partial | mypy --strict | 🟡 MEDIUM |

---

## 🧮 New Calculators | 新計算器

### Phase 17: Trauma & Burns (創傷與燒傷)

> **Priority**: 🟡 MEDIUM | **Target**: 2026 Q1

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| \`calculate_iss\` | Injury Severity Score | 創傷嚴重度評估 | Baker 1974 |
| \`calculate_rts\` | Revised Trauma Score | 創傷生理評估 | Champion 1989 |
| \`calculate_triss\` | TRISS | 創傷存活機率 | Boyd 1987 |
| \`calculate_tbsa\` | TBSA (Rule of Nines) | 燒傷面積計算 | Wallace 1951 |

### Phase 18: Gastroenterology Extended (消化科擴充)

> **Priority**: 🟢 LOW | **Target**: 2026 Q2

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| \`calculate_blatchford\` | Blatchford Score | 上消化道出血風險 | Blatchford 2000 |
| \`calculate_aims65\` | AIMS65 Score | 上消化道出血死亡率 | Saltzman 2011 |
| \`calculate_lille\` | Lille Model | 酒精性肝炎類固醇反應 | Louvet 2007 |
| \`calculate_maddrey\` | Maddrey's DF | 酒精性肝炎嚴重度 | Maddrey 1978 |

### Phase 19: Obstetrics (產科)

> **Priority**: 🟢 LOW | **Target**: 2026 Q3

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| \`calculate_bishop_score\` | Bishop Score | 子宮頸成熟度/引產評估 | Bishop 1964 |
| \`calculate_ballard\` | Ballard Score | 新生兒胎齡評估 | Ballard 1991 |

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
├── 68 Calculators (Phase 16 done!)
├── Docker + REST API + SSE + HTTPS
├── GitHub Actions CI + Pre-commit hooks
├── 768 tests, 85% coverage
├── Ruff lint errors fixed
└── ✅ SSE remote deployment fix (FastMCP built-in transport)

2026 Q1 (Current Focus)
├── Rate Limiting + API Auth
├── Test coverage 90%+
├── Phase 17: Trauma & Burns (4 calculators)
├── 📦 PyPI package release (pip install medical-calc-mcp)
├── 🏷️ GitHub Release workflow (automated versioning)
└── Target: 72 calculators

2026 Q2 (Planned)
├── Phase 18: Gastroenterology Extended
├── i18n Framework (zh-TW, zh-CN)
├── Kubernetes templates
├── Documentation site (MkDocs)
└── Target: 76 calculators

2026 Q3 (Planned)
├── Phase 19: Obstetrics (2 calculators)
├── Calculator CLI generator
├── Cloud deployment templates
└── Target: 78+ calculators
\`\`\`

---

## 📋 Priority Queue | 優先佇列

### Immediate (Next Sprint)

| Rank | Item | Category | Effort |
|------|------|----------|--------|
| 1 | Rate Limiting | Security | S |
| 2 | API Key Authentication | Security | M |
| 3 | Structured Logging | Observability | S |
| 4 | Test Coverage 90% | Testing | M |

### Short-term (Next Month)

| Rank | Item | Category | Effort |
|------|------|----------|--------|
| 5 | ISS Calculator | Trauma | S |
| 6 | RTS Calculator | Trauma | S |
| 7 | TRISS Calculator | Trauma | M |
| 8 | i18n Framework | DX | L |

### Long-term (Next Quarter)

| Rank | Item | Category | Effort |
|------|------|----------|--------|
| 9 | Kubernetes templates | Infra | M |
| 10 | MkDocs Site | DX | M |
| 11 | Calculator CLI generator | DX | L |
| 12 | Prometheus metrics | Observability | M |

**Effort Legend**: S = Small (1-2 days), M = Medium (3-5 days), L = Large (1-2 weeks)

---

## 🏆 Success Metrics | 成功指標

| Metric | Current | Target (2026 Q2) |
|--------|---------|------------------|
| Calculators | **68** | 76+ |
| Test Coverage | 85% | 90%+ |
| API Response Time (p95) | ~50ms | <100ms |
| Documentation | README only | Full MkDocs site |
| i18n Languages | 1 (EN) | 3 (EN, zh-TW, zh-CN) |
| Security Features | CORS + HTTPS | Rate limit + Auth |

---

## 🤝 Contributing | 貢獻

歡迎貢獻！請參閱 [CONTRIBUTING.md](CONTRIBUTING.md)。

### Quick Contribution Ideas

1. **🔐 Security** - 實作 Rate Limiting 或 API Auth
2. **🧮 新計算器** - 從 Priority Queue 選擇一個
3. **📝 文件** - 改善 README 或新增範例
4. **🧪 測試** - 提高測試覆蓋率
5. **🌐 翻譯** - 協助翻譯工具描述為中文

---

*This roadmap focuses on future improvements. For completed features, see [README.md](README.md).*

*本路線圖聚焦於未來改進。已完成功能請參閱 [README.md](README.md)。*
