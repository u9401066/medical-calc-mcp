# 🗺️ Medical Calculator MCP - Development Roadmap

> **Last Updated**: 2025-11-30
> **Current Version**: Phase 8 Complete ✅
> **Total Calculators**: 26 → Target: 50+

---

## 📊 Quick Navigation | 快速導覽

| Section | Description |
|---------|-------------|
| [Current Status](#-current-status--目前狀態) | 目前進度總覽 |
| [Phase 9: Acid-Base & Electrolytes](#-phase-9-acid-base--electrolytes-酸鹼電解質) | 酸鹼電解質計算器 |
| [Phase 10: Cardiovascular Extended](#-phase-10-cardiovascular-extended-心血管擴充) | 心血管擴充計算器 |
| [Phase 11: Respiratory & Oxygenation](#-phase-11-respiratory--oxygenation-呼吸氧合) | 呼吸氧合計算器 |
| [Phase 12: Neurology & Sedation](#-phase-12-neurology--sedation-神經鎮靜) | 神經鎮靜計算器 |
| [Phase 13: Infectious Disease](#-phase-13-infectious-disease-感染症) | 感染症計算器 |
| [Phase 14: Common Utilities](#-phase-14-common-utilities-通用工具) | 通用計算工具 |
| [Phase 15+: Infrastructure](#-phase-15-infrastructure-基礎設施) | 基礎設施升級 |

---

## 📈 Current Status | 目前狀態

### Completed Phases | 已完成階段

| Phase | Description | Calculators | Status |
|-------|-------------|-------------|--------|
| 1-3 | Foundation + MCP Integration | - | ✅ |
| 4 | ICU/ED Core (SOFA, qSOFA, NEWS, GCS, CAM-ICU) | 5 | ✅ |
| 5 | Pediatric/Anesthesia (MABL, Transfusion, Dosing) | 3 | ✅ |
| 5.5 | MCP Prompts + Enhanced Errors | - | ✅ |
| 6 | Multi-specialty (CURB-65, CHA₂DS₂-VASc, HEART, Wells, MELD) | 6 | ✅ |
| 7 | Validation Layer (22 Parameter Specs) | - | ✅ |
| 7.5 | Type Safety (CHA₂DS₂-VA, Caprini, PSI/PORT) | 3 | ✅ |
| 8 | Guideline Tools (HAS-BLED, Child-Pugh, KDIGO AKI) | 3 | ✅ |

### Current Stats | 目前統計

```
┌─────────────────────────────────────────────┐
│  📊 Project Statistics                       │
├─────────────────────────────────────────────┤
│  Calculators:          26                    │
│  MCP Tools:            33                    │
│  Tests:               128                    │
│  Coverage:             67%                   │
│  Prompts:               5                    │
│  Resources:             4                    │
└─────────────────────────────────────────────┘
```

---

## 🧪 Phase 9: Acid-Base & Electrolytes (酸鹼電解質)

> **Priority**: 🔴 HIGH - 每日 ICU/急診必用
> **Estimated**: 6 calculators
> **Source**: IBCC (EMCrit), Harrison's Principles

### Calculators

| Tool ID | Name | Purpose | Reference | Priority |
|---------|------|---------|-----------|----------|
| `anion_gap` | Anion Gap | 代謝性酸中毒鑑別 | Oh's ICU | 🔴 |
| `delta_ratio` | Delta Ratio (Delta Gap) | 混合型酸鹼障礙鑑別 | IBCC | 🔴 |
| `corrected_sodium` | Corrected Sodium | 高血糖校正真實血鈉 | Katz 1973 | 🔴 |
| `winters_formula` | Winter's Formula | 預測代謝性酸中毒 PCO₂ | Winter 1967 | 🟡 |
| `osmolar_gap` | Osmolar Gap | 毒物中毒篩檢 | IBCC | 🟡 |
| `free_water_deficit` | Free Water Deficit | 高鈉血症治療計劃 | Adrogue 2000 | 🟡 |

### Clinical Workflow

```
Acid-Base Analysis Workflow:
┌─────────────────────────────────────────────────────────┐
│ Step 1: ABG Analysis                                    │
│   └── pH, PCO₂, HCO₃⁻ interpretation                   │
│                                                         │
│ Step 2: Anion Gap Calculation                           │
│   └── AG = Na⁺ - (Cl⁻ + HCO₃⁻)                         │
│   └── Corrected AG (for albumin)                        │
│                                                         │
│ Step 3: Delta Ratio (if AG elevated)                    │
│   └── ΔAG / ΔHCO₃⁻ = (AG-12) / (24-HCO₃⁻)             │
│   └── <1: NAGMA coexists, 1-2: Pure HAGMA, >2: Met Alk │
│                                                         │
│ Step 4: Winter's Formula (if metabolic acidosis)        │
│   └── Expected PCO₂ = 1.5 × HCO₃⁻ + 8 ± 2             │
│   └── Compare with actual → respiratory compensation    │
│                                                         │
│ Step 5: Osmolar Gap (if toxic ingestion suspected)      │
│   └── Measured - Calculated Osm                         │
│   └── >10: Consider methanol, ethylene glycol           │
└─────────────────────────────────────────────────────────┘
```

---

## ❤️ Phase 10: Cardiovascular Extended (心血管擴充)

> **Priority**: 🔴 HIGH - ACS/心衰常用
> **Estimated**: 5 calculators
> **Source**: AHA/ESC Guidelines, IBCC

### Calculators

| Tool ID | Name | Purpose | Reference | Priority |
|---------|------|---------|-----------|----------|
| `corrected_qt` | Corrected QT (QTc) | 藥物致心律不整風險 | Bazett 1920, Fridericia 1920 | 🔴 |
| `shock_index` | Shock Index | 快速血流動力學評估 | Allgöwer 1967 | 🔴 |
| `map_calculation` | Mean Arterial Pressure | MAP 計算 | - | 🟡 |
| `fick_cardiac_output` | Fick Cardiac Output | 心輸出量估算 | Miller's Anesthesia | 🟡 |
| `grace_score` | GRACE Score | ACS 預後評估 | Fox 2006 | 🟡 |

### Notes

- **Corrected QT**: 支援 Bazett (most common)、Fridericia (for tachycardia)、Framingham
- **Shock Index**: HR/SBP > 1.0 suggests hemodynamic instability

---

## 🫁 Phase 11: Respiratory & Oxygenation (呼吸氧合)

> **Priority**: 🔴 HIGH - 機械通氣必用
> **Estimated**: 5 calculators
> **Source**: ARDSNet, Berlin Definition, IBCC

### Calculators

| Tool ID | Name | Purpose | Reference | Priority |
|---------|------|---------|-----------|----------|
| `aa_gradient` | A-a Gradient | 低血氧原因鑑別 | - | 🔴 |
| `pf_ratio` | P/F Ratio | ARDS 嚴重度分級 | Berlin 2012 | 🔴 |
| `ideal_body_weight` | Ideal Body Weight | 機械通氣 Vt 計算 | ARDSNet | 🔴 |
| `rox_index` | ROX Index | HFNC 失敗預測 | Roca 2016 | 🟡 |
| `pesi_score` | PESI/sPESI | PE 預後評估 | Aujesky 2005 | 🟡 |

### Clinical Context

```
Hypoxemia Differential (using A-a Gradient):
┌─────────────────────────────────────────────────────────┐
│ Normal A-a gradient (<10-15 mmHg adjusted for age):     │
│   └── Hypoventilation (neuromuscular, CNS, drugs)       │
│   └── Low FiO₂ (high altitude)                          │
│                                                         │
│ Elevated A-a gradient:                                  │
│   └── V/Q mismatch (PE, pneumonia, ARDS)               │
│   └── Shunt (ARDS, AVM, cardiac shunt)                 │
│   └── Diffusion impairment (ILD, CHF)                  │
└─────────────────────────────────────────────────────────┘
```

---

## 🧠 Phase 12: Neurology & Sedation (神經鎮靜)

> **Priority**: 🟡 MEDIUM
> **Estimated**: 4 calculators
> **Source**: AHA/ASA Guidelines, Wijdicks 2005

### Calculators

| Tool ID | Name | Purpose | Reference | Priority |
|---------|------|---------|-----------|----------|
| `nihss` | NIHSS | 急性中風嚴重度 | Brott 1989 | 🟡 |
| `hunt_hess` | Hunt & Hess Scale | SAH 分級 | Hunt & Hess 1968 | 🟡 |
| `four_score` | FOUR Score | 細緻昏迷評估 | Wijdicks 2005 | 🟡 |
| `abcd2_score` | ABCD² Score | TIA 後中風風險 | Johnston 2007 | 🟡 |

---

## 🔥 Phase 13: Infectious Disease (感染症)

> **Priority**: 🟡 MEDIUM
> **Estimated**: 3 calculators
> **Source**: IDSA Guidelines, SCCM

### Calculators

| Tool ID | Name | Purpose | Reference | Priority |
|---------|------|---------|-----------|----------|
| `mascc_score` | MASCC Score | 嗜中性白血球低下發燒風險 | Klastersky 2000 | 🟡 |
| `pitt_bacteremia` | Pitt Bacteremia Score | 菌血症預後 | Paterson 2004 | 🟡 |
| `centor_score` | Centor/McIsaac Score | 咽炎抗生素決策 | Centor 1981, McIsaac 1998 | 🟢 |

---

## 🏥 Phase 14: Common Utilities (通用工具)

> **Priority**: 🟡 MEDIUM - 各科通用
> **Estimated**: 5 calculators
> **Source**: Standard medical formulas

### Calculators

| Tool ID | Name | Purpose | Reference | Priority |
|---------|------|---------|-----------|----------|
| `bsa_calculation` | Body Surface Area | 化療/燒傷/腎功能 | Du Bois 1916, Mosteller 1987 | 🟡 |
| `creatinine_clearance` | Creatinine Clearance (CG) | 藥物劑量調整 | Cockcroft-Gault 1976 | 🟡 |
| `albumin_corrected_calcium` | Albumin-Corrected Calcium | 真實血鈣評估 | Payne 1973 | 🟡 |
| `parkland_formula` | Parkland Formula | 燒傷輸液計劃 | Baxter 1968 | 🟡 |
| `steroid_conversion` | Steroid Conversion | 類固醇等效劑量 | - | 🟢 |

---

## 🔧 Phase 15+: Infrastructure (基礎設施)

### Phase 15: HTTP Transport

```
┌─────────────────────────────────────────────────────────┐
│  FastAPI/Starlette Integration                          │
│  ├── REST API endpoints                                 │
│  ├── OpenAPI/Swagger documentation                      │
│  ├── Docker optimization                                │
│  └── Health check endpoints                             │
└─────────────────────────────────────────────────────────┘
```

### Phase 16: Internationalization (i18n)

```
┌─────────────────────────────────────────────────────────┐
│  Multi-language Support                                 │
│  ├── zh-TW (Traditional Chinese) - Primary              │
│  ├── zh-CN (Simplified Chinese)                         │
│  ├── ja (Japanese)                                      │
│  └── Translation framework                              │
└─────────────────────────────────────────────────────────┘
```

### Phase 17: Calculator Templates

```
┌─────────────────────────────────────────────────────────┐
│  Calculator Generator                                   │
│  ├── CLI tool for scaffolding                          │
│  ├── Auto-generate tests                               │
│  └── Reference template integration                     │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 Implementation Priority Matrix

### Priority Scoring

| Factor | Weight | Description |
|--------|--------|-------------|
| Clinical Frequency | 40% | 臨床使用頻率 |
| Guideline Inclusion | 30% | 指引推薦程度 |
| Implementation Complexity | 20% | 實作複雜度 (低=高優先) |
| User Requests | 10% | 使用者需求 |

### Priority Queue (Next 10 Calculators)

| Rank | Tool | Phase | Score | Reason |
|------|------|-------|-------|--------|
| 1 | Anion Gap | 9 | 95 | 每日 ICU 必用 |
| 2 | Corrected QT | 10 | 92 | 藥物安全性 |
| 3 | A-a Gradient | 11 | 90 | 低血氧鑑別 |
| 4 | Delta Ratio | 9 | 88 | 酸鹼分析配套 |
| 5 | Shock Index | 10 | 85 | 急診快速評估 |
| 6 | Corrected Sodium | 9 | 82 | DKA/HHS 必用 |
| 7 | Ideal Body Weight | 11 | 80 | 機械通氣基礎 |
| 8 | P/F Ratio | 11 | 78 | ARDS 分級 |
| 9 | ROX Index | 11 | 75 | HFNC 時代重要 |
| 10 | Winter's Formula | 9 | 72 | 酸鹼分析配套 |

---

## 📅 Timeline Estimate

```
2025 Q4 (Current)
├── Phase 8: ✅ Complete (HAS-BLED, Child-Pugh, KDIGO AKI)
└── Phase 9: 🔄 In Progress (Acid-Base)

2026 Q1
├── Phase 9: Complete (6 calculators)
├── Phase 10: Complete (5 calculators)
└── Phase 11: Start (5 calculators)

2026 Q2
├── Phase 11: Complete
├── Phase 12: Complete (4 calculators)
├── Phase 13: Complete (3 calculators)
└── Phase 14: Complete (5 calculators)

2026 Q3
├── Phase 15: HTTP Transport
└── Phase 16: i18n (zh-TW first)

Target: 50+ calculators by 2026 Q2
```

---

## 🔗 References | 參考來源

本 Roadmap 的計算器選擇基於以下來源（非 MDCalc）：

| Source | Type | Usage |
|--------|------|-------|
| **IBCC (EMCrit)** | Free Online Resource | Acid-base, Critical Care |
| **AHA/ESC Guidelines** | Professional Guidelines | Cardiology tools |
| **SCCM** | Professional Society | ICU scoring systems |
| **ARDSNet** | Clinical Trial Protocol | Ventilation parameters |
| **Harrison's Principles** | Medical Textbook | Formulas, algorithms |
| **Miller's Anesthesia** | Specialty Textbook | Anesthesia calculations |
| **KDIGO** | Clinical Practice Guidelines | Nephrology staging |
| **Original Papers** | Primary Literature | Validation references |

---

## 📝 Notes for Contributors

1. **新增計算器前**請先查閱 [CONTRIBUTING.md](CONTRIBUTING.md)
2. **每個計算器必須**引用原始論文 (PMID/DOI)
3. **優先實作**高優先級 (🔴) 工具
4. **測試覆蓋**：每個計算器至少 5 個測試案例
5. **驗證**：使用原始論文的範例數據驗證公式

---

*This roadmap is a living document and will be updated as development progresses.*

*本路線圖為動態文件，將隨開發進度更新。*
