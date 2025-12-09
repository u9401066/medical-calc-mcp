"""
Trauma Calculator MCP Handlers

MCP tool handlers for trauma assessment and burns:
- TBSA (Total Body Surface Area): Burns assessment with Rule of Nines
- ISS (Injury Severity Score): Anatomic injury severity
- sPESI: Pulmonary embolism severity (often trauma-related)

References:
- ATLS 10th Edition
- ABA Guidelines for Burns
- Baker SP, et al. J Trauma. 1974
"""

from typing import Optional
from mcp.server.fastmcp import FastMCP

from .....domain.services.calculators import (
    TbsaCalculator,
    InjurySeverityScoreCalculator,
    SimplifiedPESICalculator,
)


def register_trauma_tools(mcp: FastMCP) -> None:
    """Register all trauma calculator tools"""
    
    tbsa_calc = TbsaCalculator()
    iss_calc = InjurySeverityScoreCalculator()
    spesi_calc = SimplifiedPESICalculator()
    
    @mcp.tool()
    def calculate_tbsa(
        head_neck: float = 0,
        anterior_trunk: float = 0,
        posterior_trunk: float = 0,
        right_arm: float = 0,
        left_arm: float = 0,
        right_leg: float = 0,
        left_leg: float = 0,
        genitalia: float = 0,
        age: Optional[int] = None,
        method: str = "rule_of_nines",
    ) -> dict:
        """
        🔥 TBSA: 燒傷總體表面積計算 (Rule of Nines)
        
        計算燒傷面積百分比，用於 Parkland 公式液體復甦和燒傷嚴重度分級。
        支援成人 Rule of Nines 和兒童 Lund-Browder 修正。
        
        **成人 Rule of Nines:**
        - Head/Neck: 9%
        - Anterior trunk: 18%
        - Posterior trunk: 18%
        - Each arm: 9%
        - Each leg: 18%
        - Genitalia: 1%
        
        **兒童修正 (Lund-Browder):**
        - 嬰兒頭部較大 (18% → 9%)
        - 下肢較小 (14% → 18%)
        
        **燒傷嚴重度:**
        - Minor: <10% TBSA (or <5% full thickness)
        - Moderate: 10-20% TBSA
        - Severe: >20% TBSA → 需燒傷中心轉介
        
        **Parkland 公式:**
        液體需求 = 4 mL × kg × %TBSA (前 24h)
        
        **參考文獻:** Wallace AB. Lancet. 1951;1(6653):501-504.
        
        Returns:
            TBSA%、燒傷嚴重度、液體需求估計、轉介建議
        """
        result = tbsa_calc.calculate(
            head_neck=head_neck,
            anterior_trunk=anterior_trunk,
            posterior_trunk=posterior_trunk,
            right_arm=right_arm,
            left_arm=left_arm,
            right_leg=right_leg,
            left_leg=left_leg,
            genitalia=genitalia,
            age=age,
            method=method,
        )
        return result.to_dict()
    
    @mcp.tool()
    def calculate_iss(
        head_neck_ais: int = 0,
        face_ais: int = 0,
        chest_ais: int = 0,
        abdomen_ais: int = 0,
        extremity_ais: int = 0,
        external_ais: int = 0,
    ) -> dict:
        """
        🏥 Injury Severity Score (ISS): 創傷嚴重度評分
        
        國際標準創傷嚴重度評估工具，基於 Abbreviated Injury Scale (AIS)。
        取最嚴重的 3 個身體區域 AIS 分數平方和。
        
        **六個身體區域:**
        1. Head/Neck (頭頸部)
        2. Face (顏面)
        3. Chest (胸部)
        4. Abdomen (腹部/骨盆內臟)
        5. Extremity (四肢/骨盆環)
        6. External (皮膚)
        
        **AIS 分級 (0-6):**
        - 0 = No injury
        - 1 = Minor
        - 2 = Moderate
        - 3 = Serious
        - 4 = Severe
        - 5 = Critical
        - 6 = Unsurvivable (ISS 自動 = 75)
        
        **ISS 計算:**
        ISS = (最高AIS)² + (次高AIS)² + (第三高AIS)²
        
        **ISS 分類:**
        - 1-8: Minor trauma
        - 9-15: Moderate trauma
        - 16-24: Serious trauma (Major trauma)
        - 25-40: Severe trauma
        - 41-54: Critical trauma
        - 55-75: Usually fatal
        
        **ISS >15 = Major Trauma → 需創傷中心照護**
        
        **參考文獻:** Baker SP, et al. J Trauma. 1974;14(3):187-196.
        PMID: 4814394
        
        Returns:
            ISS (0-75)、死亡率預估、創傷分級、處置建議
        """
        result = iss_calc.calculate(
            head_neck_ais=head_neck_ais,
            face_ais=face_ais,
            chest_ais=chest_ais,
            abdomen_ais=abdomen_ais,
            extremity_ais=extremity_ais,
            external_ais=external_ais,
        )
        return result.to_dict()
    
    @mcp.tool()
    def calculate_spesi(
        age: int,
        cancer: bool = False,
        chronic_cardiopulmonary_disease: bool = False,
        heart_rate: Optional[int] = None,
        systolic_bp: Optional[int] = None,
        spo2: Optional[float] = None,
        heart_rate_gte_110: Optional[bool] = None,
        sbp_lt_100: Optional[bool] = None,
        spo2_lt_90: Optional[bool] = None,
    ) -> dict:
        """
        🫁 sPESI: 簡化版肺栓塞嚴重度指數 (Simplified PESI)
        
        **ESC 2019 推薦**的急性肺栓塞 30 天死亡風險分層工具。
        比原始 PESI 簡單，僅需 6 個變數。
        
        **六項評估指標 (各+1分):**
        - Age >80 years (年齡 >80 歲)
        - Cancer (活動性或近一年內癌症)
        - Chronic cardiopulmonary disease (慢性心肺疾病)
        - Heart rate ≥110 bpm (心跳 ≥110)
        - Systolic BP <100 mmHg (收縮壓 <100)
        - SpO₂ <90% (血氧 <90%)
        
        **風險分層:**
        - sPESI 0: **Low risk** (30天死亡率 ~1%)
          → 考慮門診治療 (如符合其他條件)
        - sPESI ≥1: **Not low risk** (30天死亡率 ~10.9%)
          → 住院治療，需進一步風險分層
        
        **ESC 2019 進階分層:**
        - sPESI 0 + 無 RV 功能障礙 + Troponin(-) = Low risk
        - sPESI ≥1 或 RV 功能障礙 或 Troponin(+) = Intermediate risk
        - 休克或低血壓 = High risk → 考慮再灌流
        
        **參考文獻:**
        - Jiménez D, et al. Arch Intern Med. 2010;170(15):1383-1389. PMID: 20696966
        - ESC 2019 PE Guidelines. Eur Heart J. 2020. PMID: 31504429
        
        Returns:
            sPESI (0-6)、30 天死亡率、風險分類、門診/住院建議
        """
        result = spesi_calc.calculate(
            age=age,
            cancer=cancer,
            chronic_cardiopulmonary_disease=chronic_cardiopulmonary_disease,
            heart_rate=heart_rate,
            systolic_bp=systolic_bp,
            spo2=spo2,
            heart_rate_gte_110=heart_rate_gte_110,
            sbp_lt_100=sbp_lt_100,
            spo2_lt_90=spo2_lt_90,
        )
        return result.to_dict()
