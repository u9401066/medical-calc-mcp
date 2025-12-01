"""
Hepatology Calculator Handlers

MCP tool handlers for hepatology/gastroenterology calculators.
"""

from typing import Annotated, Any, Literal

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .....application.dto import CalculateRequest
from .....application.use_cases import CalculateUseCase


def register_hepatology_tools(mcp: FastMCP, use_case: CalculateUseCase) -> None:
    """Register all hepatology calculator tools with MCP"""
    
    @mcp.tool()
    def calculate_meld_score(
        creatinine: Annotated[float, Field(
            gt=0, le=15.0,
            description="血清肌酸酐 Serum creatinine | Unit: mg/dL | Range: 0.5-15.0"
        )],
        bilirubin: Annotated[float, Field(
            gt=0, le=50.0,
            description="總膽紅素 Total bilirubin | Unit: mg/dL | Range: 0.1-50.0"
        )],
        inr: Annotated[float, Field(
            gt=0, le=10.0,
            description="國際標準化比值 INR | Range: 1.0-10.0"
        )],
        sodium: Annotated[float, Field(
            ge=100, le=160,
            description="血清鈉 Serum sodium | Unit: mEq/L | Range: 100-160 (用於 MELD-Na)"
        )] = 137.0,
        on_dialysis: Annotated[bool, Field(
            description="透析狀態 Dialyzed ≥2x/week or CVVHD? | If true, Cr is set to 4.0"
        )] = False,
    ) -> dict[str, Any]:
        """
        🫀 MELD Score: 末期肝病預後評估
        
        預測末期肝病患者的 90 天死亡率，用於肝臟移植優先排序。
        
        **輸入參數:**
        - Creatinine (mg/dL): 最小 1.0, 最大 4.0
        - Bilirubin (mg/dL): 最小 1.0
        - INR: 最小 1.0
        - Sodium (mEq/L): 範圍 125-137 (用於 MELD-Na)
        - 透析: 若每週 ≥2 次透析，Cr 設為 4.0
        
        **MELD 公式:**
        MELD = 10 × [0.957×ln(Cr) + 0.378×ln(Bili) + 1.120×ln(INR)] + 6.43
        
        **MELD-Na 公式 (UNOS 2016):**
        MELD-Na = MELD + 1.32×(137-Na) - 0.033×MELD×(137-Na)
        
        **90 天死亡率:**
        - <10: 1.9%
        - 10-19: 6.0%
        - 20-29: 19.6%
        - 30-39: 52.6%
        - ≥40: 71.3%
        
        **參考文獻:** 
        - Kamath PS, et al. Hepatology. 2001;33(2):464-470. PMID: 11172350
        - Kim WR, et al. N Engl J Med. 2008;359(10):1018-1026. PMID: 18768945
        
        Returns:
            MELD 分數、MELD-Na 分數、90 天死亡率、移植建議
        """
        request = CalculateRequest(
            tool_id="meld_score",
            params={
                "creatinine": creatinine,
                "bilirubin": bilirubin,
                "inr": inr,
                "sodium": sodium,
                "on_dialysis": on_dialysis,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()

    @mcp.tool()
    def calculate_child_pugh(
        bilirubin: Annotated[float, Field(
            gt=0, le=30.0,
            description="總膽紅素 Total bilirubin | Unit: mg/dL | Range: 0.1-30.0"
        )],
        albumin: Annotated[float, Field(
            gt=0, le=6.0,
            description="血清白蛋白 Serum albumin | Unit: g/dL | Range: 1.0-6.0"
        )],
        inr: Annotated[float, Field(
            gt=0, le=6.0,
            description="國際標準化比值 INR | Range: 1.0-6.0"
        )],
        ascites: Annotated[
            Literal["none", "mild", "moderate_severe"],
            Field(description="腹水狀態 Ascites status | Options: 'none'=無, 'mild'=輕度/可控, 'moderate_severe'=中重度")
        ],
        encephalopathy_grade: Annotated[
            Literal[0, 1, 2, 3, 4],
            Field(description="肝腦病變分級 Hepatic encephalopathy | 0=無, 1=輕度混亂, 2=嗜睡, 3=半昏迷, 4=昏迷")
        ],
    ) -> dict[str, Any]:
        """
        🫀 Child-Pugh Score: 肝硬化嚴重度評估
        
        評估慢性肝病（肝硬化）的嚴重程度，用於預後及治療決策。
        
        **計分標準 (5項指標，每項1-3分):**
        
        | 參數 | 1分 | 2分 | 3分 |
        |------|-----|-----|-----|
        | Bilirubin (mg/dL) | <2 | 2-3 | >3 |
        | Albumin (g/dL) | >3.5 | 2.8-3.5 | <2.8 |
        | INR | <1.7 | 1.7-2.2 | >2.2 |
        | 腹水 | 無 | 輕度 | 中重度 |
        | 肝腦病變 | 無 | I-II級 | III-IV級 |
        
        **分級與預後:**
        - Class A (5-6分): 代償良好，1年存活率 ~100%
        - Class B (7-9分): 功能受損，1年存活率 ~80%
        - Class C (10-15分): 失代償，1年存活率 ~45%
        
        **臨床應用:**
        - 肝硬化預後評估
        - 手術風險分層（圍手術期死亡率）
        - 肝移植評估（常與 MELD 互補）
        - 肝功能不全時藥物劑量調整
        
        **參考文獻:** 
        - Pugh RNH, et al. Br J Surg. 1973;60(8):646-649. PMID: 4541913
        - Child CG, Turcotte JG. The Liver and Portal Hypertension. 1964.
        
        Returns:
            Child-Pugh 分數 (5-15)、分級 (A/B/C)、存活率估計
        """
        request = CalculateRequest(
            tool_id="child_pugh",
            params={
                "bilirubin": bilirubin,
                "albumin": albumin,
                "inr": inr,
                "ascites": ascites,
                "encephalopathy_grade": encephalopathy_grade,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()

    @mcp.tool()
    def calculate_rockall_score(
        age_years: Annotated[int, Field(
            ge=18, le=120,
            description="年齡 Patient age in years"
        )],
        shock_status: Annotated[
            Literal["none", "tachycardia", "hypotension"],
            Field(description="休克狀態 Shock | 'none'=無(HR<100,SBP≥100), 'tachycardia'=心搏過速(HR≥100,SBP≥100), 'hypotension'=低血壓(SBP<100)")
        ],
        comorbidity: Annotated[
            Literal["none", "cardiac_major", "renal_liver_malignancy"],
            Field(description="共病狀態 Comorbidity | 'none'=無, 'cardiac_major'=心衰/缺血心臟病/其他重大, 'renal_liver_malignancy'=腎衰/肝衰/惡性腫瘤轉移")
        ],
        diagnosis: Annotated[
            Literal["mallory_weiss_no_lesion", "other_diagnosis", "gi_malignancy"],
            Field(description="內視鏡診斷 Diagnosis | 'mallory_weiss_no_lesion'=撕裂傷/無病灶, 'other_diagnosis'=消化性潰瘍/其他, 'gi_malignancy'=上消化道惡性腫瘤")
        ],
        stigmata_of_recent_hemorrhage: Annotated[
            Literal["none_or_dark_spot", "blood_clot_visible_vessel"],
            Field(description="近期出血跡象 Stigmata of recent hemorrhage | 'none_or_dark_spot'=無/黑點, 'blood_clot_visible_vessel'=血塊/可見血管/活動性出血")
        ],
    ) -> dict[str, Any]:
        """
        🩸 Rockall Score: 上消化道出血風險評估
        
        預測上消化道出血(UGIB)患者的再出血及死亡風險。
        
        **Pre-Endoscopy Rockall (0-7分):**
        - 年齡: <60=0, 60-79=1, ≥80=2
        - 休克: 無=0, 心搏過速=1, 低血壓=2
        - 共病: 無=0, 心衰等=2, 腎肝惡性=3
        
        **完整 Rockall (加上內視鏡發現, 0-11分):**
        - 診斷: Mallory-Weiss/無=0, 其他=1, 惡性腫瘤=2
        - 出血跡象: 無/黑點=0, 血管/血塊=2, 活動出血=2
        
        **再出血風險:**
        - 0分: 4.9%
        - 1分: 3.4%
        - 2分: 5.3%
        - 3分: 11.2%
        - 4分: 14.1%
        - 5分: 24.1%
        - 6分: 32.9%
        - 7分: 43.8%
        - ≥8分: >50%
        
        **死亡風險:**
        - 0-2分: <1%
        - 3-4分: ~5%
        - 5-6分: ~10%
        - 7-8分: ~20%
        - ≥9分: >30%
        
        **臨床應用:**
        - Clinical Rockall (pre-endoscopy) ≤2: 可考慮門診內視鏡
        - Full Rockall ≤2: 早期出院風險低
        - Full Rockall ≥5: 高風險，需加護病房觀察
        
        **參考文獻:** 
        Rockall TA, et al. Gut. 1996;38(3):316-321. PMID: 8675081
        
        Returns:
            Rockall score (Full 0-11, Clinical 0-7)、再出血率、死亡率、處置建議
        """
        request = CalculateRequest(
            tool_id="rockall_score",
            params={
                "age_years": age_years,
                "shock_status": shock_status,
                "comorbidity": comorbidity,
                "diagnosis": diagnosis,
                "stigmata_of_recent_hemorrhage": stigmata_of_recent_hemorrhage,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()

    @mcp.tool()
    def calculate_fib4_index(
        age_years: Annotated[int, Field(
            ge=18, le=100,
            description="年齡 Patient age in years (18-100)"
        )],
        ast: Annotated[float, Field(
            gt=0, le=5000,
            description="AST (SGOT) | Unit: U/L | Range: 1-5000"
        )],
        alt: Annotated[float, Field(
            gt=0, le=5000,
            description="ALT (SGPT) | Unit: U/L | Range: 1-5000"
        )],
        platelet_count: Annotated[float, Field(
            gt=0, le=1000,
            description="血小板計數 Platelet count | Unit: 10^9/L (K/µL) | Range: 1-1000"
        )],
    ) -> dict[str, Any]:
        """
        🫀 FIB-4 Index: 肝纖維化非侵入性評估
        
        使用年齡及常規血液檢查評估肝臟纖維化程度。
        
        **公式:** FIB-4 = (Age × AST) / (Platelets × √ALT)
        
        **標準切點 (年齡 ≤65):**
        - <1.30: 低風險 (F0-F1) - NPV ~90%
        - 1.30-2.67: 不確定，需進一步檢查
        - >2.67: 高風險 (F3-F4) - PPV ~65%
        
        **年齡調整切點 (年齡 >65):**
        - <2.0: 低風險
        - 2.0-3.25: 不確定
        - >3.25: 高風險
        
        **臨床應用:**
        - 最初驗證於 HCV，也適用於 NAFLD/NASH
        - 可搭配 FibroScan 提高準確度
        - 低風險可排除進展性纖維化
        - 高風險需進一步確認 (彈性成像或切片)
        
        **適應症:**
        - 慢性 C 型肝炎
        - 慢性 B 型肝炎
        - 非酒精性脂肪肝/脂肪性肝炎
        - 肝硬化篩檢
        
        **參考文獻:** 
        Sterling RK, et al. Hepatology. 2006;43(6):1317-1325. PMID: 16729309
        
        Returns:
            FIB-4 指數、纖維化階段預測、NPV/PPV、處置建議
        """
        request = CalculateRequest(
            tool_id="fib4_index",
            params={
                "age_years": age_years,
                "ast": ast,
                "alt": alt,
                "platelet_count": platelet_count,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()
