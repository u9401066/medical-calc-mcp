# 📋 2020-2025 臨床指引推薦評分工具總整理

> **最後更新**: 2025-12-03  
> **資料來源**: PubMed 系統性搜尋 + ESC/SCCM/AHA 官方指引  
> **搜尋方法**: PubMed Search MCP 多主題搜尋 (2020-2025)

本文件整理 2020-2025 年間主要臨床指引中提及的評分工具，並與本系統現有工具進行比對，
以識別缺口並規劃未來開發優先順序。

---

## 📊 整體對照摘要

| 領域 | 指引推薦工具 | 已實作 | 待實作 |
|------|-------------|--------|--------|
| 敗血症/重症 | SOFA, SOFA-2, qSOFA, NEWS2, APACHE II, RASS, CAM-ICU | ✅ 7/7 | ICDSC |
| 心血管 | CHA₂DS₂-VASc, CHA₂DS₂-VA, HAS-BLED, HEART, GRACE, TIMI | ✅ 6/6 | - |
| 消化道出血 | Rockall, Glasgow-Blatchford, AIMS65 | ⚠️ 1/3 | **Blatchford, AIMS65** |
| 肝臟疾病 | Child-Pugh, MELD, MELD-Na, FIB-4 | ✅ 4/4 | Maddrey, Lille |
| 腎臟疾病 | KDIGO AKI, CKD-EPI 2021 | ✅ 2/2 | - |
| 肺炎/呼吸 | CURB-65, PSI/PORT, ROX Index, P/F Ratio | ✅ 4/4 | Murray Score |
| 血栓栓塞 | Wells DVT, Wells PE, Caprini VTE | ✅ 3/3 | PESI/sPESI |
| 神經科 | GCS, NIHSS, mRS, ABCD2 | ✅ 4/4 | Hunt & Hess, Fisher |
| 麻醉科 | ASA, RCRI, Mallampati, STOP-BANG, Apfel, Aldrete | ✅ 6/6 | EuroSCORE II |
| 創傷 | GCS | ✅ 1/1 | **ISS, RTS, TRISS** |
| 燒傷 | - | ❌ 0/2 | **Parkland, TBSA** |
| 小兒科 | PEWS (多版本) | ❌ 0/1 | **Brighton PEWS** |

**總計**: 70 已實作 / 約 15 個高優先待實作

---

## 🫀 心血管領域 (Cardiology)

### 2024 ESC 心房顫動指引 (AF Guidelines) - 重大更新

> **PMID**: 39217497 | Eur Heart J. 2024;45(36):3314-3414  
> Van Gelder IC, et al.

| 評分工具 | 用途 | 狀態 | 指引建議 |
|---------|------|------|----------|
| **CHA₂DS₂-VA** (新版) | 中風風險評估 (性別中性) | ✅ 已實作 | **2024 ESC 推薦** |
| **CHA₂DS₂-VASc** | 中風風險評估 (傳統版) | ✅ 已實作 | 仍可使用 |
| **HAS-BLED** | 出血風險評估 | ✅ 已實作 | **ESC 強烈推薦** |
| DOAC Score | DOAC出血風險 | ❌ 待評估 | 🟢 低 |
| ABC-bleeding | 生物標記出血風險 | ❌ 待評估 | 🟢 低 |

**關鍵更新**:
- 2024 ESC 指引移除性別作為中風風險修飾因子
- 新評分系統 CHA₂DS₂-VA 最高分從 9 分降為 8 分
- 推薦同時使用 CHA₂DS₂-VA + HAS-BLED 平衡中風/出血風險

### 急性冠心症 (ACS)

| 工具 | 用途 | 狀態 | 指引推薦 |
|------|------|------|----------|
| **HEART Score** | 急診胸痛風險分層 | ✅ 已實作 | ACEP 推薦 |
| **TIMI STEMI** | STEMI 30天死亡率 | ✅ 已實作 | AHA/ACC |
| **GRACE Score** | ACS 死亡率預測 | ✅ 已實作 | ESC ACS指引 |

### 心臟手術風險

| 工具 | 用途 | 狀態 | 優先級 |
|------|------|------|--------|
| **ACEF II** | 心臟手術死亡率 | ✅ 已實作 | - |
| **EuroSCORE II** | 心臟手術死亡率 | ❌ 待實作 | 🟡 中 |
| **STS Score** | 心臟手術風險 | ❌ 待評估 | 🟢 低 |
| **TRI-SCORE** | 三尖瓣手術 (新2022) | ❌ 待評估 | 🟢 低 |

**近期文獻**:
- PMID: 34586392 - TRI-SCORE (Eur Heart J 2022)
- PMID: 35141860 - EuroSCORE II 八旬老人驗證

### VTE 風險評估

| 評分工具 | 用途 | 狀態 | 指引推薦 |
|---------|------|------|----------|
| **Wells DVT** | DVT 機率評估 | ✅ 已實作 | ASH 推薦 |
| **Wells PE** | PE 機率評估 | ✅ 已實作 | ESC PE 指引 |
| **Caprini VTE** | 手術VTE風險 | ✅ 已實作 | ACCP 推薦 |
| PESI/sPESI | PE 預後 | ❌ 待評估 | 🟡 中 |

---

## 🏥 重症醫學 (Critical Care)

### Surviving Sepsis Campaign 2021 Guidelines

> **PMID**: 34605781 | Crit Care Med. 2021;49(11):e1063-e1143  
> Evans L, et al.

| 評分工具 | 用途 | 狀態 | 指引建議強度 |
|---------|------|------|-------------|
| **SOFA** | 器官衰竭評估/Sepsis診斷 | ✅ 已實作 | **強推薦** |
| **qSOFA** | 床邊快速篩檢 | ✅ 已實作 | 有條件推薦 |
| **NEWS2** | 臨床惡化預警 | ✅ 已實作 | 指引提及 |
| **APACHE II** | ICU 死亡率 | ✅ 已實作 | 經典工具 |

**2024 專家共識 (Intensive Care Med 2024)** - PMID: 39531053:
- SOFA 仍為 Sepsis-3 核心診斷標準
- qSOFA 敏感度較低 (37%)，不應單獨作為篩檢工具
- NEWS/MEWS 表現與 SIRS/qSOFA 相當或更好

### SOFA-2 Score (2025 JAMA 新發表)

> **PMID**: 41159833 | JAMA 2025

| 工具 | 用途 | 狀態 | 備註 |
|------|------|------|------|
| **SOFA-2** | 器官衰竭評估 (2025新版) | ✅ 已實作 | **最新版本** |

**SOFA-2 更新要點**:
- 基於 **3.3M 患者數據** 重新校正
- 更新閾值以反映現代 ICU 實踐
- 包含 ECMO 和進階呼吸支持的考量

### ICU 鎮靜與譫妄 (PADIS Guidelines)

| 工具 | 用途 | 狀態 | 指引建議 |
|------|------|------|----------|
| **RASS** | 鎮靜深度評估 | ✅ 已實作 | **強推薦** |
| **CAM-ICU** | ICU 譫妄篩檢 | ✅ 已實作 | **強推薦** |
| **ICDSC** | ICU 譫妄評估 (替代) | ❌ 待實作 | 可接受替代 |

**相關文獻**:
- PMID: 36122204 - SAMDS-ICU 國際調查 (Ann Intensive Care 2022)
- PMID: 32035691 - 鎮靜對譫妄識別的影響 (Aust Crit Care 2020)

---

## 🫁 呼吸/肺臟領域 (Pulmonology)

### 社區型肺炎 (CAP)

| 工具 | 用途 | 狀態 | 指引推薦 |
|------|------|------|----------|
| **CURB-65** | CAP 嚴重度/住院決策 | ✅ 已實作 | BTS/IDSA 推薦 |
| **PSI/PORT** | CAP 死亡率預測 | ✅ 已實作 | IDSA/ATS 推薦 |

### ARDS 相關

| 工具 | 用途 | 狀態 | 參考 |
|------|------|------|------|
| **P/F Ratio** | ARDS 嚴重度 (Berlin) | ✅ 已實作 | Berlin 定義核心 |
| **IBW/TV** | 潮氣量計算 | ✅ 已實作 | ARDSNet 標準 |
| **Murray Score** | 肺損傷嚴重度 | ❌ 待實作 | 🟡 中 |

**重要文獻**:
- PMID: 32870298 - 低潮氣量通氣 RCT (JAMA 2020)

### 高流量氧療 (HFNC)

#### ROX Index - 2020-2025 大量驗證研究

| 工具 | 用途 | 狀態 | 驗證情況 |
|------|------|------|----------|
| **ROX Index** | HFNC 失敗預測 | ✅ 已實作 | **20+ 驗證研究** |

**Meta-Analysis 支持**:
- PMID: 35365110 - ROX Index 系統性回顧 (BMC Pulm Med 2022)
- PMID: 35177091 - ROX Index Meta-analysis (Respir Res 2022)
- PMID: 37605238 - COVID-19 中 ROX 表現 (Crit Care 2023)

---

## 🩸 消化道出血 (GI Bleeding) - ⚠️ 缺口領域

### 上消化道出血 (UGIB)

> **關鍵 Meta-Analysis**: PMID: 39400553 | Eur J Gastroenterol Hepatol. 2025

| 工具 | 用途 | 狀態 | 指引推薦 |
|------|------|------|----------|
| **Rockall Score** | UGIB 死亡率/再出血 | ✅ 已實作 | 廣泛使用 |
| **Glasgow-Blatchford (GBS)** | UGIB 需干預風險 | ❌ **待實作** | 🔴 **ESGE 推薦** |
| **AIMS65** | UGIB 死亡率 | ❌ **待實作** | 🔴 **多指引推薦** |

**Gap 分析**: 
- Glasgow-Blatchford 為目前最推薦的 UGIB 風險分層工具
- AIMS65 簡便易用，5 項指標即可計算
- **建議優先實作** 以完善消化道出血評估能力

**關鍵文獻**:
- PMID: 39400553 - Rockall vs GBS Meta-analysis (2025)
- PMID: 36542335 - 瑞士多中心驗證 (Eur J Emerg Med 2023)
- PMID: 37629235 - 預內視鏡風險分層回顧 (J Clin Med 2023)

---

## 🧠 神經科 (Neurology)

### 腦外傷 (TBI)

#### 2024 NINDS TBI Classification Recommendations
> **PMID**: 40393504 | J Neurotrauma 2025

| 工具 | 用途 | 狀態 | 指引狀態 |
|------|------|------|----------|
| **GCS** | 意識程度/TBI 嚴重度 | ✅ 已實作 | **核心標準** |
| **GCS-Pupils (GCS-P)** | GCS + 瞳孔反應 | ❌ 待評估 | 新提議 |

**關鍵更新** (2024 NINDS):
- GCS 仍為 TBI 分類核心標準
- 輕度 (13-15), 中度 (9-12), 重度 (≤8)
- 建議結合其他評估 (瞳孔反應、影像學)

### 中風 (Stroke)

| 工具 | 用途 | 狀態 | 指引推薦 |
|------|------|------|----------|
| **NIHSS** | 中風嚴重度量化 | ✅ 已實作 | **AHA/ASA 強推薦** |
| **mRS** | 中風後失能評估 | ✅ 已實作 | 主要預後指標 |
| **ABCD2** | TIA 後中風風險 | ✅ 已實作 | 指引推薦 |

### 蛛網膜下腔出血 (SAH) - Gap

| 工具 | 用途 | 狀態 | 優先級 |
|------|------|------|--------|
| **Hunt & Hess Grade** | SAH 臨床嚴重度 | ❌ 待實作 | 🟡 中 |
| **Fisher Grade** | SAH CT 分級 | ❌ 待實作 | 🟡 中 |
| **WFNS Grade** | SAH 分級 | ❌ 待評估 | 🟢 低 |

---

## 💉 麻醉科 (Anesthesiology)

### 術前評估

| 工具 | 用途 | 狀態 | 指引推薦 |
|------|------|------|----------|
| **ASA Physical Status** | 術前風險分級 | ✅ 已實作 | **核心標準** |
| **RCRI** | 非心臟手術心臟風險 | ✅ 已實作 | AHA/ACC 推薦 |
| **Mallampati** | 困難氣道預測 | ✅ 已實作 | 廣泛使用 |
| **STOP-BANG** | OSA 篩檢 | ✅ 已實作 | AASM 推薦 |

**相關文獻**:
- PMID: 38278596 - 術前心臟檢查更新 (Anesth Clin 2024)
- PMID: 39956581 - RCRI 性別差異研究 (Circ J 2025)

### 困難氣道

| 工具 | 用途 | 狀態 | 參考 |
|------|------|------|------|
| **Mallampati** | 視覺化評估 | ✅ 已實作 | - |
| El-Ganzouri Risk Index | 多因子困難氣道 | ❌ 待評估 | 🟢 低 |
| LEMON | 急診困難氣道 | ❌ 待評估 | 🟢 低 |

### 術後恢復

| 工具 | 用途 | 狀態 | 參考 |
|------|------|------|------|
| **Aldrete Score** | PACU 出院標準 | ✅ 已實作 | 標準工具 |
| **Apfel Score** | PONV 風險 | ✅ 已實作 | PONV 預防指引 |

---

## 🩺 肝臟疾病 (Hepatology)

### 肝硬化相關

| 工具 | 用途 | 狀態 | 指引推薦 |
|------|------|------|----------|
| **Child-Pugh** | 肝硬化嚴重度 | ✅ 已實作 | AASLD 推薦 |
| **MELD** | 肝移植優先順序 | ✅ 已實作 | UNOS 標準 |
| **MELD-Na** | MELD + 鈉 | ✅ 已實作 | 2016 UNOS 採用 |
| **FIB-4** | 非侵入性纖維化 | ✅ 已實作 | AASLD/EASL 推薦 |

### 酒精性肝炎 - Gap

| 工具 | 用途 | 狀態 | 優先級 |
|------|------|------|--------|
| **Maddrey DF** | 酒精性肝炎嚴重度 | ❌ 待實作 | 🟡 中 |
| **Lille Model** | 類固醇反應預測 | ❌ 待實作 | 🟡 中 |

---

## 🫘 腎臟疾病 (Nephrology)

| 工具 | 用途 | 狀態 | 指引推薦 |
|------|------|------|----------|
| **CKD-EPI 2021** | eGFR 計算 (無種族) | ✅ 已實作 | **KDIGO 2021** |
| **KDIGO AKI** | 急性腎損傷分期 | ✅ 已實作 | **KDIGO AKI** |

---

## 👶 小兒科 (Pediatrics) - ⚠️ 缺口領域

### 小兒早期預警系統 (PEWS)

| 工具 | 用途 | 狀態 | 驗證情況 |
|------|------|------|----------|
| **Brighton PEWS** | 小兒惡化預警 | ❌ **待實作** | 🔴 **高優先** |
| Bedside PEWS | 小兒惡化預警 | ❌ 待評估 | 多國驗證 |
| Cardiff PEWS | 小兒惡化預警 | ❌ 待評估 | 英國使用 |

**Gap 分析**: 
- PEWS 為兒科住院安全核心工具
- Brighton PEWS 為最廣泛採用版本
- **建議優先實作** Brighton PEWS

---

## 🔥 創傷與燒傷 (Trauma & Burns) - ⚠️ 缺口領域

### 創傷評分

| 工具 | 用途 | 狀態 | 優先級 |
|------|------|------|--------|
| **GCS** | TBI 評估 | ✅ 已實作 | - |
| **ISS** | 創傷嚴重度 | ❌ **待實作** | 🔴 **高** |
| **RTS** | 生理創傷評分 | ❌ **待實作** | 🔴 **高** |
| **TRISS** | 創傷存活預測 | ❌ **待實作** | 🔴 **高** |

### 燒傷評估

| 工具 | 用途 | 狀態 | 優先級 |
|------|------|------|--------|
| **Parkland Formula** | 燒傷輸液計算 | ❌ **待實作** | 🔴 **高** |
| **TBSA (Rule of 9s)** | 燒傷面積 | ❌ **待實作** | 🔴 **高** |

---

## 📈 缺口分析與開發優先順序

### 🔴 高優先級 (Phase 18-20)

| 工具 | 領域 | 理由 | 目標版本 |
|------|------|------|----------|
| **Glasgow-Blatchford** | GI | UGIB 標準工具，ESGE 推薦 | Phase 19 |
| **AIMS65** | GI | UGIB 死亡率預測 | Phase 19 |
| **Brighton PEWS** | Pediatrics | 兒科安全核心工具 | Phase 20 |
| **ISS** | Trauma | 創傷嚴重度國際標準 | Phase 18 |
| **RTS** | Trauma | 創傷生理評分 | Phase 18 |
| **TRISS** | Trauma | 創傷存活預測 | Phase 18 |
| **Parkland Formula** | Burns | 燒傷復甦基礎 | Phase 18 |
| **TBSA** | Burns | 燒傷面積計算 | Phase 18 |

### 🟡 中優先級 (Phase 21-23)

| 工具 | 領域 | 理由 |
|------|------|------|
| **EuroSCORE II** | Cardiac Surgery | 心臟手術廣泛使用 |
| **Hunt & Hess** | Neurology | SAH 分級標準 |
| **Fisher Grade** | Neurology | SAH CT 分級 |
| **Maddrey DF** | Hepatology | 酒精性肝炎 |
| **Lille Model** | Hepatology | 類固醇反應 |
| **Murray Score** | Pulmonology | 肺損傷評分 |
| **ICDSC** | Critical Care | ICU 譫妄替代 |
| **PESI/sPESI** | Pulmonology | PE 預後 |

### 🟢 低優先級/待評估

| 工具 | 領域 | 備註 |
|------|------|------|
| APACHE IV | Critical Care | APACHE II 更新版 |
| SAPS 3 | Critical Care | 歐洲常用 |
| STS Score | Cardiac Surgery | 美國常用 |
| GCS-Pupils | Neurology | 新提議 |
| DOAC Score | Cardiology | 新興工具 |

---

## 📚 重要參考文獻

### 主要指引

| 指引 | 年份 | PMID | 推薦工具 |
|------|------|------|----------|
| Surviving Sepsis Campaign | 2021 | 34605781 | SOFA, qSOFA |
| ESC AF Guidelines | 2024 | 39217497 | CHA₂DS₂-VA, HAS-BLED |
| SOFA-2 Development | 2025 | 41159833 | SOFA-2 |
| NINDS TBI Classification | 2025 | 40393504 | GCS |
| ROX Index Meta-Analysis | 2022 | 35365110 | ROX Index |
| UGIB Scoring Meta-Analysis | 2025 | 39400553 | GBS, Rockall, AIMS65 |

### 其他重要文獻

1. Martin-Loeches I, et al. Intensive Care Med. 2024;50(12):2043-2049. PMID: 39531053
2. Chua WL, et al. J Clin Nurs. 2024;33(6):2005-2018. PMID: 38379353
3. Karalapillai D, et al. JAMA. 2020;324:848-858. PMID: 32870298

---

*此文件將隨新指引發布持續維護*  
*Generated by PubMed Search MCP + Manual Curation*  
*Last Update: 2025-12-03*
