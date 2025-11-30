# 🗺️ Medical Calculator MCP - Development Roadmap

> **Last Updated**: 2025-12-01
> **Current Version**: Phase 11 Complete ✅ + Infrastructure Complete ✅
> **Total Calculators**: 42 → Target: 50+

---

## 📊 Quick Navigation | 快速導覽

| Section | Description |
|---------|-------------|
| [Current Status](#-current-status--目前狀態) | 目前進度總覽 |
| [Completed Phases](#-completed-phases--已完成階段) | 所有已完成階段詳情 |
| [Next Phase: Neurology](#-next-phase-neurology--sedation-神經鎮靜) | 下一階段計畫 |
| [Future Phases](#-future-phases--未來階段) | 未來開發計畫 |
| [Infrastructure Status](#-infrastructure-status--基礎設施狀態) | Docker, REST API 狀態 |

---

## 📈 Current Status | 目前狀態

### 🎉 Milestones Achieved | 已達成里程碑

```
┌─────────────────────────────────────────────────────────┐
│  🏆 PROJECT MILESTONES                                  │
├─────────────────────────────────────────────────────────┤
│  ✅ 42 Clinical Calculators                             │
│  ✅ 48 MCP Tools                                        │
│  ✅ 437 Test Cases                                      │
│  ✅ Docker + SSE Remote Server                          │
│  ✅ REST API (FastAPI + Swagger)                        │
│  ✅ SOFA-2 (JAMA 2025) - Latest Evidence               │
│  ✅ 2024 ESC Guidelines (CHA₂DS₂-VA, HAS-BLED)         │
└─────────────────────────────────────────────────────────┘
```

### Current Stats | 目前統計

```
┌─────────────────────────────────────────────────────────┐
│  📊 Project Statistics (2025-12-01)                     │
├─────────────────────────────────────────────────────────┤
│  Calculators:          42                               │
│  MCP Tools:            48                               │
│  Tests:               437                               │
│  Test Coverage:        79%                              │
│  Prompts:               5                               │
│  Resources:             4                               │
├─────────────────────────────────────────────────────────┤
│  🐳 Docker:            ✅ Complete                      │
│  🌐 REST API:          ✅ Complete (FastAPI)            │
│  📡 SSE Transport:     ✅ Complete                      │
│  📖 Swagger/OpenAPI:   ✅ Complete                      │
└─────────────────────────────────────────────────────────┘
```

---

## ✅ Completed Phases | 已完成階段

### Phase Summary Table

| Phase | Description | Calculators | Status |
|-------|-------------|-------------|--------|
| 1-3 | Foundation + MCP Integration | - | ✅ |
| 4 | ICU/ED Core (SOFA, qSOFA, NEWS, GCS, CAM-ICU, RASS, APACHE II) | 7 | ✅ |
| 5 | Pediatric/Anesthesia (MABL, Transfusion, Dosing, ASA, Mallampati, RCRI) | 6 | ✅ |
| 5.5 | MCP Prompts + Enhanced Errors | - | ✅ |
| 6 | Multi-specialty (CURB-65, CHA₂DS₂-VASc, HEART, Wells DVT/PE, MELD) | 6 | ✅ |
| 7 | Validation Layer (22 Parameter Specs) | - | ✅ |
| 7.5 | Type Safety (CHA₂DS₂-VA 2024, Caprini, PSI/PORT) | 3 | ✅ |
| 8 | Guideline Tools (HAS-BLED 2024, Child-Pugh, KDIGO AKI) | 3 | ✅ |
| 9 | Acid-Base Complete (AG, Delta Ratio, Corrected Na, Winter's, Osmolar Gap, FWD) | 6 | ✅ |
| 10 | High-Priority (QTc, A-a Gradient, Shock Index) | 3 | ✅ |
| 11 | Extended (IBW, P/F Ratio, ROX Index, GRACE, 4Ts HIT, ACEF II, SOFA-2) | 7 | ✅ |
| Infra | Docker + SSE + REST API | - | ✅ |

### Detailed Calculator List by Specialty

#### 🩺 Critical Care / ICU (8 tools)

| Tool ID | Name | Reference | Status |
|---------|------|-----------|--------|
| `calculate_apache_ii` | APACHE II | Knaus 1985 | ✅ |
| `calculate_sofa` | SOFA Score | Vincent 1996, Sepsis-3 2016 | ✅ |
| `calculate_sofa2` | **SOFA-2 (2025)** 🆕 | Ranzani JAMA 2025 | ✅ |
| `calculate_qsofa` | qSOFA | Singer 2016 | ✅ |
| `calculate_news2` | NEWS2 | RCP 2017 | ✅ |
| `calculate_gcs` | Glasgow Coma Scale | Teasdale 1974 | ✅ |
| `calculate_rass` | RASS | Sessler 2002 | ✅ |
| `calculate_cam_icu` | CAM-ICU | Ely 2001 | ✅ |

#### 💉 Anesthesiology / Preoperative (6 tools)

| Tool ID | Name | Reference | Status |
|---------|------|-----------|--------|
| `calculate_asa_physical_status` | ASA Physical Status | ASA Guidelines | ✅ |
| `calculate_mallampati` | Mallampati Score | Mallampati 1985 | ✅ |
| `calculate_rcri` | RCRI (Revised Cardiac Risk) | Lee 1999 | ✅ |
| `calculate_mabl` | Maximum Allowable Blood Loss | Miller's Anesthesia | ✅ |
| `calculate_transfusion_volume` | Transfusion Calculator | Roseff 2002 | ✅ |
| `calculate_pediatric_drug_dose` | Pediatric Dosing | Lexicomp | ✅ |

#### ❤️ Cardiology (7 tools)

| Tool ID | Name | Reference | Status |
|---------|------|-----------|--------|
| `calculate_chads2_vasc` | CHA₂DS₂-VASc | Lip 2010 | ✅ |
| `calculate_chads2_va` | CHA₂DS₂-VA (2024 ESC) | Van Gelder 2024 | ✅ |
| `calculate_has_bled` | HAS-BLED (2024 ESC) | Pisters 2010, ESC 2024 | ✅ |
| `calculate_heart_score` | HEART Score | Six 2008 | ✅ |
| `calculate_corrected_qt` | Corrected QT (QTc) | Bazett, Fridericia | ✅ |
| `calculate_grace_score` | GRACE Score | Fox 2006 | ✅ |
| `calculate_acef_ii` | ACEF II Score | Ranucci 2018 | ✅ |

#### 🫁 Pulmonology (5 tools)

| Tool ID | Name | Reference | Status |
|---------|------|-----------|--------|
| `calculate_curb65` | CURB-65 | Lim 2003 | ✅ |
| `calculate_psi_port` | PSI/PORT | Fine 1997 | ✅ |
| `calculate_aa_gradient` | A-a Gradient | West Physiology | ✅ |
| `calculate_pf_ratio` | P/F Ratio | Berlin ARDS 2012 | ✅ |
| `calculate_rox_index` | ROX Index | Roca 2016 | ✅ |

#### 🫘 Nephrology (2 tools)

| Tool ID | Name | Reference | Status |
|---------|------|-----------|--------|
| `calculate_ckd_epi_2021` | CKD-EPI 2021 | Inker 2021 | ✅ |
| `calculate_kdigo_aki` | KDIGO AKI Staging | KDIGO 2012 | ✅ |

#### 🟤 Hepatology (2 tools)

| Tool ID | Name | Reference | Status |
|---------|------|-----------|--------|
| `calculate_meld_score` | MELD / MELD-Na | Kamath 2001, Kim 2008 | ✅ |
| `calculate_child_pugh` | Child-Pugh Score | Pugh 1973 | ✅ |

#### 🚑 Emergency Medicine (3 tools)

| Tool ID | Name | Reference | Status |
|---------|------|-----------|--------|
| `calculate_wells_dvt` | Wells DVT | Wells 2003 | ✅ |
| `calculate_wells_pe` | Wells PE | Wells 2000 | ✅ |
| `calculate_shock_index` | Shock Index | Allgöwer 1967 | ✅ |

#### 🩸 Hematology (2 tools)

| Tool ID | Name | Reference | Status |
|---------|------|-----------|--------|
| `calculate_4ts_hit` | 4Ts HIT Score | Lo 2006, Cuker 2012 | ✅ |
| `calculate_caprini_vte` | Caprini VTE Risk | Caprini 2005 | ✅ |

#### ⚗️ Acid-Base & Electrolytes (6 tools)

| Tool ID | Name | Reference | Status |
|---------|------|-----------|--------|
| `calculate_anion_gap` | Anion Gap | Kraut 2007 | ✅ |
| `calculate_delta_ratio` | Delta Ratio | Wrenn 1990 | ✅ |
| `calculate_corrected_sodium` | Corrected Sodium | Katz 1973 | ✅ |
| `calculate_winters_formula` | Winter's Formula | Winter 1967 | ✅ |
| `calculate_osmolar_gap` | Osmolar Gap | IBCC | ✅ |
| `calculate_free_water_deficit` | Free Water Deficit | Adrogue 2000 | ✅ |

#### 📐 Common Utilities (1 tool)

| Tool ID | Name | Reference | Status |
|---------|------|-----------|--------|
| `calculate_ideal_body_weight` | Ideal Body Weight | Devine 1974, ARDSNet | ✅ |

---

## 🔜 Next Phase: Neurology & Sedation (神經鎮靜)

> **Priority**: 🟡 MEDIUM
> **Estimated**: 4 calculators
> **Target**: 2026 Q1

### Planned Calculators

| Tool ID | Name | Purpose | Reference | Priority |
|---------|------|---------|-----------|----------|
| `nihss` | NIHSS | 急性中風嚴重度 | Brott 1989 | 🟡 |
| `hunt_hess` | Hunt & Hess Scale | SAH 分級 | Hunt & Hess 1968 | 🟡 |
| `four_score` | FOUR Score | 細緻昏迷評估 (優於 GCS) | Wijdicks 2005 | 🟡 |
| `abcd2_score` | ABCD² Score | TIA 後中風風險 | Johnston 2007 | 🟡 |

---

## 📋 Future Phases | 未來階段

### Phase: Infectious Disease (感染症)

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `mascc_score` | MASCC Score | 嗜中性白血球低下發燒風險 | Klastersky 2000 |
| `pitt_bacteremia` | Pitt Bacteremia Score | 菌血症預後 | Paterson 2004 |
| `centor_score` | Centor/McIsaac Score | 咽炎抗生素決策 | Centor 1981 |

### Phase: Common Utilities (通用工具)

| Tool ID | Name | Purpose | Reference |
|---------|------|---------|-----------|
| `bsa_calculation` | Body Surface Area | 化療/燒傷 | Du Bois 1916 |
| `creatinine_clearance` | Creatinine Clearance (CG) | 藥物劑量調整 | Cockcroft-Gault 1976 |
| `albumin_corrected_calcium` | Albumin-Corrected Ca | 真實血鈣評估 | Payne 1973 |
| `parkland_formula` | Parkland Formula | 燒傷輸液計劃 | Baxter 1968 |

### Phase: Advanced Infrastructure

| Feature | Description | Status |
|---------|-------------|--------|
| Streamable HTTP | MCP Streamable HTTP transport | 📋 Planned |
| i18n (zh-TW) | 繁體中文完整支援 | 📋 Planned |
| Calculator CLI | CLI scaffolding tool | 📋 Planned |
| Cloud Deploy | GCP Cloud Run / AWS Lambda | 📋 Planned |

---

## 🔧 Infrastructure Status | 基礎設施狀態

### ✅ Completed Infrastructure

| Feature | Description | Status |
|---------|-------------|--------|
| **Docker** | Python 3.11-slim container | ✅ Complete |
| **SSE Transport** | Remote MCP via Server-Sent Events | ✅ Complete |
| **REST API** | FastAPI with Swagger UI | ✅ Complete |
| **docker-compose** | Multi-service orchestration | ✅ Complete |

### Deployment Options

```
┌─────────────────────────────────────────────────────────┐
│  🚀 DEPLOYMENT OPTIONS                                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Option 1: Local (stdio)                                │
│  └── python -m src.main --mode stdio                    │
│                                                         │
│  Option 2: Docker SSE                                   │
│  └── docker-compose up medical-calc-mcp                 │
│  └── Exposes: http://localhost:8000/                    │
│                                                         │
│  Option 3: Docker REST API                              │
│  └── docker-compose up medical-calc-api                 │
│  └── Swagger: http://localhost:8080/docs                │
│                                                         │
│  Option 4: Both Services                                │
│  └── docker-compose up -d                               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📅 Timeline | 時程規劃

```
2025 Q4 (Completed ✅)
├── Phase 9: ✅ Acid-Base Complete (6 calculators)
├── Phase 10: ✅ High-Priority (3 calculators)
├── Phase 11: ✅ Extended (7 calculators including SOFA-2)
└── Infrastructure: ✅ Docker + SSE + REST API

2026 Q1 (Planned)
├── Neurology Phase (4 calculators: NIHSS, Hunt-Hess, FOUR, ABCD²)
├── Infectious Disease (3 calculators)
└── Target: 49 calculators

2026 Q2 (Planned)
├── Common Utilities (4 calculators)
├── i18n Framework (zh-TW)
└── Target: 53+ calculators

2026 Q3+ (Planned)
├── Streamable HTTP Transport
├── Cloud Deployment Templates
└── Calculator CLI Generator
```

---

## 📋 Priority Queue | 優先佇列

### Next 8 Calculators to Implement

| Rank | Tool | Category | Clinical Reason |
|------|------|----------|-----------------|
| 1 | NIHSS | Neurology | 急性中風必用 |
| 2 | Hunt-Hess | Neurology | SAH 標準分級 |
| 3 | ABCD² | Neurology | TIA 風險評估 |
| 4 | FOUR Score | Neurology | 優於 GCS 的昏迷評估 |
| 5 | MASCC | Infectious | 發燒嗜中性低下風險 |
| 6 | BSA | Utility | 化療劑量基礎 |
| 7 | CrCl (CG) | Utility | 藥物劑量調整 |
| 8 | Centor/McIsaac | Infectious | 咽炎抗生素決策 |

---

## 🔗 References | 參考來源

| Source | Type | Usage |
|--------|------|-------|
| **JAMA** | Original Research | SOFA-2 (2025) |
| **ESC Guidelines 2024** | Professional Guidelines | CHA₂DS₂-VA, HAS-BLED |
| **IBCC (EMCrit)** | Free Online Resource | Acid-base, Critical Care |
| **AHA/ACC Guidelines** | Professional Guidelines | Cardiology tools |
| **SCCM** | Professional Society | ICU scoring systems |
| **ARDSNet** | Clinical Trial Protocol | Ventilation parameters |
| **KDIGO** | Clinical Practice Guidelines | Nephrology staging |
| **Original Papers** | Primary Literature | All calculator validation |

---

## 📝 Notes for Contributors

1. **新增計算器前**請先查閱 [CONTRIBUTING.md](CONTRIBUTING.md)
2. **每個計算器必須**引用原始論文 (PMID/DOI)
3. **優先實作**高優先級工具
4. **測試覆蓋**：每個計算器至少 5 個測試案例
5. **驗證**：使用原始論文的範例數據驗證公式
6. **Infrastructure**: Docker 和 REST API 已完成，可專注於新計算器

---

## 🏆 Achievement Summary | 成就總結

| Milestone | Target | Achieved | Status |
|-----------|--------|----------|--------|
| Core Calculators | 30 | 42 | ✅ 140% |
| MCP Tools | 30 | 48 | ✅ 160% |
| Test Coverage | 70% | 79% | ✅ |
| Docker Support | Yes | Yes | ✅ |
| REST API | Yes | Yes | ✅ |
| 2024/2025 Guidelines | 2 | 3 | ✅ |

---

*This roadmap is a living document and will be updated as development progresses.*

*本路線圖為動態文件，將隨開發進度更新。*
