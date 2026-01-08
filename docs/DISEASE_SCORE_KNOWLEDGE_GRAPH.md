# 🕸️ Disease-Score Knowledge Graph 設計文檔

> **創建日期**: 2026-01-08  
> **狀態**: 概念設計階段  
> **目標**: 解決「同一疾病不同學會/地區用不同評分算法」的臨床痛點

---

## 📋 問題背景

### 臨床痛點

1. **學會差異**: 同一疾病，美國 (AHA/ACC) 與歐洲 (ESC) 指引推薦不同工具
2. **地區偏好**: 台灣、日本、中國等亞洲地區可能有本土化驗證研究
3. **版本演進**: 同一工具有多個版本 (如 MELD → MELD-Na → MELD 3.0)
4. **目的差異**: 診斷 vs 預後 vs 治療決策，各有不同最佳工具

### 文獻支持

| PMID | 標題 | 關鍵發現 |
|------|------|---------|
| **35894866** | Comprehensive comparison of stroke risk scores (6.2M AF patients) | 比較 17 種 AF 中風風險評分 |
| **35365110** | ROX Index Meta-analysis | ROX 在不同地區表現差異 |
| **39400553** | GBS vs Rockall in UGIB | GI 出血評分工具比較 |

---

## 🏗️ 設計架構

### 1. 核心實體 (Entities)

```python
@dataclass
class Condition:
    """疾病/臨床情境實體"""
    condition_id: str          # e.g., "atrial_fibrillation_stroke_risk"
    name: str                  # "心房顫動中風風險"
    icd10_codes: tuple[str]    # ("I48",)
    clinical_questions: tuple[str]  # 臨床問題
    
@dataclass
class ScoreToolRelation:
    """疾病-評分工具關係"""
    condition_id: str
    tool_id: str
    
    # 指引來源
    guideline_sources: tuple[GuidelineSource]
    
    # 地區偏好
    regional_preferences: dict[str, str]  # {"US": "preferred", "EU": "alternative"}
    
    # 臨床用途
    clinical_purposes: tuple[ClinicalPurpose]  # diagnosis, prognosis, treatment
    
    # 驗證狀態
    validation_evidence: ValidationEvidence

@dataclass
class GuidelineSource:
    """指引來源"""
    organization: str      # "ESC", "AHA", "SCCM"
    guideline_name: str
    year: int
    pmid: str
    recommendation_class: str  # "I", "IIa", "IIb", "III"
    evidence_level: str        # "A", "B", "C"
```

### 2. 關係圖譜

```
                    ┌──────────────────┐
                    │  Condition       │
                    │  心房顫動中風風險  │
                    └────────┬─────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│ CHA₂DS₂-VASc   │  │ CHA₂DS₂-VA     │  │ GARFIELD-AF    │
│ (傳統版)        │  │ (2024 ESC)     │  │ (整合風險)      │
└────────────────┘  └────────────────┘  └────────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│ US: preferred  │  │ EU: preferred  │  │ Both: research │
│ EU: acceptable │  │ US: acceptable │  │                │
│ TW: preferred  │  │ TW: new        │  │                │
└────────────────┘  └────────────────┘  └────────────────┘
```

---

## 📊 具體案例分析

### 案例 1: 心房顫動中風風險評估

| 工具 | 指引來源 | 推薦等級 | 地區偏好 | 已實作 |
|------|---------|---------|---------|-------|
| **CHA₂DS₂-VASc** | ACC/AHA 2023 | Class I | 🇺🇸 US, 🇹🇼 TW | ✅ |
| **CHA₂DS₂-VA** | ESC 2024 | Class I | 🇪🇺 EU | ✅ |
| **GARFIELD-AF** | 研究工具 | - | 研究用 | ❌ |
| **ABC-stroke** | 研究工具 | - | 研究用 | ❌ |

**關鍵差異**: 2024 ESC 移除性別作為風險因子 (CHA₂DS₂-VA)

### 案例 2: ICU 嚴重度評估

| 工具 | 指引來源 | 推薦等級 | 地區偏好 | 已實作 |
|------|---------|---------|---------|-------|
| **APACHE II** | SCCM | 經典 | 🇺🇸 US, 🌏 Asia | ✅ |
| **APACHE IV** | Cerner | 更新版 | 🇺🇸 US | ❌ |
| **SAPS 3** | ESICM | - | 🇪🇺 EU | ❌ |
| **SOFA** | Sepsis-3 | Class I | 🌍 Global | ✅ |
| **SOFA-2** | JAMA 2025 | 最新 | 待觀察 | ✅ |

### 案例 3: 譫妄評估

| 工具 | 臨床情境 | 推薦等級 | 地區偏好 | 已實作 |
|------|---------|---------|---------|-------|
| **CAM-ICU** | ICU | PADIS 推薦 | 🌍 Global | ✅ |
| **ICDSC** | ICU | PADIS 替代 | 🇪🇺 EU | ✅ |
| **4AT** | 非 ICU | NICE 推薦 | 🇬🇧 UK | ✅ |
| **Nu-DESC** | 術後 | - | 🇪🇺 EU | ❌ |

### 案例 4: 心臟手術風險

| 工具 | 指引來源 | 推薦等級 | 地區偏好 | 已實作 |
|------|---------|---------|---------|-------|
| **EuroSCORE II** | EACTS/ESC | 推薦 | 🇪🇺 EU, 🌏 Asia | ✅ |
| **STS Score** | STS | 推薦 | 🇺🇸 US | ❌ |
| **ACEF II** | 研究 | - | 研究用 | ✅ |

---

## 🔧 實作計劃

### Phase 24A: 資料結構擴展

1. 在 `HighLevelKey` 新增欄位:
```python
@dataclass
class HighLevelKey:
    # 現有欄位...
    
    # 新增: 指引來源
    guideline_sources: tuple[GuidelineSource] = ()
    
    # 新增: 地區偏好
    regional_preferences: dict[str, str] = field(default_factory=dict)
    
    # 新增: 相關疾病
    related_conditions: tuple[str] = ()
```

### Phase 24B: Knowledge Graph 服務

```python
class ConditionScoreGraph:
    """疾病-評分工具知識圖譜服務"""
    
    def find_tools_for_condition(
        self, 
        condition: str,
        region: str = None,
        purpose: str = None
    ) -> list[ToolWithContext]:
        """根據疾病、地區、目的找適合的工具"""
        
    def compare_tools(
        self,
        tool_ids: list[str],
        condition: str
    ) -> ComparisonResult:
        """比較多個工具在同一疾病的適用性"""
        
    def get_regional_recommendation(
        self,
        condition: str,
        region: str
    ) -> RegionalRecommendation:
        """取得特定地區的推薦工具"""
```

### Phase 24C: MCP 工具整合

新增 MCP 工具:
- `find_tools_by_condition_region`: 根據疾病和地區找工具
- `compare_regional_guidelines`: 比較不同地區指引
- `get_guideline_history`: 取得工具的指引演變歷史

---

## 📚 參考文獻

### 評分工具比較研究

1. **PMID: 35894866** - van der Endt et al. Europace 2022
   - 6.2M AF 患者，比較 17 種中風風險評分
   
2. **PMID: 35365110** - ROX Index Meta-analysis, BMC Pulm Med 2022
   - ROX 在不同地區 HFNC 患者的表現

3. **PMID: 39400553** - GBS vs Rockall Meta-analysis, 2025
   - GI 出血評分工具比較

### 指引差異研究

4. **PMID: 39217497** - 2024 ESC AF Guidelines
   - CHA₂DS₂-VA 取代 CHA₂DS₂-VASc

5. **PMID: 38033089** - 2023 ACC/AHA AF Guidelines
   - 美國仍用 CHA₂DS₂-VASc

6. **PMID: 41105724** - LAAC 指引比較
   - AHA 2023 Class I vs ESC Class IIa

---

## 🎯 預期效益

### 對臨床醫師
- 快速找到適合其地區/學會的工具
- 了解不同工具的優缺點
- 減少選擇困擾

### 對研究者
- 系統性比較評分工具
- 追蹤指引演變
- 識別研究缺口

### 對教育
- 理解為何同一疾病有多種評分
- 學習指引制定的考量
- 批判性思考

---

*此文檔將隨實作進展持續更新*
*Last Update: 2026-01-08*
