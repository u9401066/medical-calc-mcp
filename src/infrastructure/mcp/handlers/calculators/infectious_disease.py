"""
Infectious Disease Calculator MCP Handlers

感染科計算器:
- MASCC Score: 發燒性嗜中性球低下風險
- Pitt Bacteremia Score: 菌血症預後
- Centor Score: 鏈球菌咽炎風險
- CPIS: 臨床肺部感染評分
"""

from typing import Literal
from mcp.server.fastmcp import FastMCP
from .....application.use_cases import CalculateUseCase


def register_infectious_disease_tools(mcp: FastMCP, use_case: CalculateUseCase) -> None:
    """Register infectious disease calculator tools"""
    
    @mcp.tool()
    def calculate_mascc_score(
        burden_of_illness: Literal["mild_or_none", "moderate", "severe"],
        hypotension: bool,
        copd: bool,
        solid_tumor: bool,
        fungal_infection: bool,
        dehydration: bool,
        outpatient_status: bool,
        age_under_60: bool
    ) -> str:
        """
        🦠 MASCC Score: 發燒性嗜中性球低下風險評估 (Febrile Neutropenia Risk)
        
        預測癌症化療後發燒性嗜中性球低下病人的嚴重併發症風險，
        用於決定住院或門診治療。
        
        **MASCC 計分項目 (加分制):**
        - **疾病負擔**: 無或輕微症狀 +5, 中等症狀 +3, 嚴重症狀 +0
        - **無低血壓**: +5
        - **無 COPD**: +4
        - **實體腫瘤或無真菌感染**: +4
        - **無脫水**: +3
        - **門診發作**: +3
        - **年齡 <60 歲**: +2
        
        **風險分層:**
        - ≥21 分: 低風險 (併發症率 <5%) → 可考慮門診治療
        - <21 分: 高風險 (併發症率 >5%) → 需住院治療
        
        **參考文獻:** Klastersky J, et al. J Clin Oncol. 2000;18(16):3038-3051.
        PMID: 10944139
        
        Returns:
            MASCC 分數、風險分層、處置建議
        """
        params = {
            "burden_of_illness": burden_of_illness,
            "hypotension": hypotension,
            "copd": copd,
            "solid_tumor": solid_tumor,
            "fungal_infection": fungal_infection,
            "dehydration": dehydration,
            "outpatient_status": outpatient_status,
            "age_under_60": age_under_60
        }
        return use_case.execute("mascc_score", params)
    
    @mcp.tool()
    def calculate_pitt_bacteremia_score(
        temperature: Literal["normal", "low_35_36_or_high_39_40", "very_low_lt_35_or_high_gt_40"],
        hypotension: Literal["none", "hypotension", "vasopressor_use"],
        mechanical_ventilation: bool,
        cardiac_arrest: bool,
        mental_status: Literal["alert", "disoriented", "stupor_or_coma"]
    ) -> str:
        """
        🦠 Pitt Bacteremia Score: 菌血症預後評估
        
        預測菌血症病人的死亡風險，用於評估疾病嚴重度和預後。
        
        **評分項目:**
        - **體溫**: 正常=0, 低溫(35-36°C)或高溫(39-40°C)=1, 極端(<35°C或>40°C)=2
        - **血壓**: 正常=0, 低血壓=2, 需要升壓劑=4
        - **機械通氣**: 有=2
        - **心跳停止**: 有=4
        - **意識狀態**: 清醒=0, 定向障礙=1, 昏迷=2
        
        **死亡風險:**
        - 0-1 分: 低風險 (~5%)
        - 2-3 分: 中風險 (~15%)
        - ≥4 分: 高風險 (~40%)
        
        **參考文獻:** Paterson DL, et al. Clin Infect Dis. 2004;39(2):206-214.
        PMID: 15307030
        
        Returns:
            Pitt 分數、死亡風險、預後分類
        """
        params = {
            "temperature": temperature,
            "hypotension": hypotension,
            "mechanical_ventilation": mechanical_ventilation,
            "cardiac_arrest": cardiac_arrest,
            "mental_status": mental_status
        }
        return use_case.execute("pitt_bacteremia", params)
    
    @mcp.tool()
    def calculate_centor_score(
        tonsillar_exudates: bool,
        tender_anterior_cervical_lymphadenopathy: bool,
        fever_history: bool,
        absence_of_cough: bool,
        age_years: int
    ) -> str:
        """
        🦠 Centor Score (Modified McIsaac): 鏈球菌咽炎風險評估
        
        評估急性咽炎病人為 A 群鏈球菌 (GAS) 感染的機率，
        指導是否需要快速抗原檢測或經驗性抗生素治療。
        
        **Modified Centor (McIsaac) 評分:**
        - **扁桃腺滲出物**: +1
        - **前頸部淋巴結腫大壓痛**: +1
        - **發燒病史 >38°C**: +1
        - **無咳嗽**: +1
        - **年齡調整**: 3-14歲 +1, 15-44歲 0, ≥45歲 -1
        
        **GAS 感染機率與處置:**
        - ≤0 分: 1-2.5% → 不需檢測或治療
        - 1 分: 5-10% → 可考慮快篩
        - 2-3 分: 15-35% → 建議快篩
        - ≥4 分: 50-75% → 快篩或經驗性治療
        
        **參考文獻:** 
        - Centor RM, et al. Med Decis Making. 1981;1(3):239-246. PMID: 6763125
        - McIsaac WJ, et al. CMAJ. 1998;158(1):75-83. PMID: 9475915
        
        Returns:
            Centor/McIsaac 分數、GAS 感染機率、處置建議
        """
        params = {
            "tonsillar_exudates": tonsillar_exudates,
            "tender_anterior_cervical_lymphadenopathy": tender_anterior_cervical_lymphadenopathy,
            "fever_history": fever_history,
            "absence_of_cough": absence_of_cough,
            "age_years": age_years
        }
        return use_case.execute("centor_score", params)
    
    @mcp.tool()
    def calculate_cpis(
        temperature: Literal["36.5_38.4", "38.5_38.9", "lt_36_or_gte_39"],
        wbc_count: Literal["4_11", "lt_4_or_gt_11", "lt_4_or_gt_11_with_bands"],
        tracheal_secretions: Literal["absent", "non_purulent", "purulent"],
        pao2_fio2_ratio: Literal["gt_240_or_ards", "lte_240_no_ards"],
        chest_xray: Literal["no_infiltrate", "diffuse", "localized"],
        culture: Literal["negative", "positive"]
    ) -> str:
        """
        🦠 CPIS: 臨床肺部感染評分 (Clinical Pulmonary Infection Score)
        
        輔助診斷呼吸器相關肺炎 (VAP) 並追蹤治療反應，
        可用於決定是否需要抗生素治療或何時停藥。
        
        **CPIS 評分項目 (0-2 分/項):**
        - **體溫**: 36.5-38.4°C=0, 38.5-38.9°C=1, <36°C或≥39°C=2
        - **白血球**: 4-11k=0, <4k或>11k=1, +band型>50%=加1
        - **氣管分泌物**: 無=0, 非膿性=1, 膿性=2
        - **氧合 (PaO2/FiO2)**: >240或ARDS=0, ≤240且無ARDS=2
        - **胸部X光**: 無浸潤=0, 瀰漫性=1, 局部=2
        - **痰液培養**: 陰性=0, 陽性=加1-2
        
        **診斷閾值:**
        - <6 分: VAP 可能性低 → 考慮停抗生素
        - ≥6 分: VAP 可能性高 → 繼續/開始抗生素
        
        **參考文獻:** Pugin J, et al. Am Rev Respir Dis. 1991;143(5):1121-1129.
        PMID: 2024824
        
        Returns:
            CPIS 分數、VAP 診斷建議、處置指引
        """
        params = {
            "temperature": temperature,
            "wbc_count": wbc_count,
            "tracheal_secretions": tracheal_secretions,
            "pao2_fio2_ratio": pao2_fio2_ratio,
            "chest_xray": chest_xray,
            "culture": culture
        }
        return use_case.execute("cpis", params)
