"""
Surgery / Perioperative Calculator Handlers

MCP tool handlers for surgical and perioperative risk calculators.
"""

from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .....application.dto import CalculateRequest
from .....application.use_cases import CalculateUseCase


def register_surgery_tools(mcp: FastMCP, use_case: CalculateUseCase) -> None:
    """Register all surgery/perioperative calculator tools with MCP"""
    
    @mcp.tool()
    def calculate_caprini_vte(
        age_years: Annotated[int, Field(ge=18, le=120, description="年齡 Age | Unit: years | Range: 18-120")],
        # Surgery type (1-2 points)
        minor_surgery: Annotated[bool, Field(description="小手術 Minor surgery planned (+1)", default=False)],
        major_surgery: Annotated[bool, Field(description="大手術 >45分鐘 Major surgery >45 min (+2)", default=False)],
        laparoscopic_surgery_gt_45min: Annotated[bool, Field(description="腹腔鏡手術 >45分鐘 (+2)", default=False)],
        arthroscopic_surgery: Annotated[bool, Field(description="關節鏡手術 Arthroscopic surgery (+2)", default=False)],
        prior_major_surgery_lt_1mo: Annotated[bool, Field(description="近一個月內大手術史 (+1)", default=False)],
        # Medical conditions (1 point each)
        varicose_veins: Annotated[bool, Field(description="靜脈曲張 Varicose veins (+1)", default=False)],
        inflammatory_bowel_disease: Annotated[bool, Field(description="發炎性腸病 IBD (+1)", default=False)],
        swollen_legs: Annotated[bool, Field(description="下肢水腫 Current leg swelling (+1)", default=False)],
        obesity_bmi_gt_25: Annotated[bool, Field(description="肥胖 BMI >25 (+1)", default=False)],
        acute_mi: Annotated[bool, Field(description="急性心肌梗塞 Acute MI (+1)", default=False)],
        chf_lt_1mo: Annotated[bool, Field(description="心衰竭 <1個月 CHF <1 month (+1)", default=False)],
        sepsis_lt_1mo: Annotated[bool, Field(description="敗血症 <1個月 Sepsis <1 month (+1)", default=False)],
        lung_disease: Annotated[bool, Field(description="嚴重肺病/肺炎 <1個月 (+1)", default=False)],
        copd: Annotated[bool, Field(description="COPD/肺功能異常 (+1)", default=False)],
        bed_rest_medical: Annotated[bool, Field(description="內科病人臥床 Medical patient at bed rest (+1)", default=False)],
        bed_confined_gt_72hr: Annotated[bool, Field(description="臥床 >72小時 Confined to bed >72h (+2)", default=False)],
        leg_cast_or_brace: Annotated[bool, Field(description="下肢石膏或支架 Leg cast/brace (+1)", default=False)],
        immobilizing_cast_lt_1mo: Annotated[bool, Field(description="固定石膏 <1個月 (+2)", default=False)],
        central_venous_access: Annotated[bool, Field(description="中央靜脈導管 Central venous access (+1)", default=False)],
        # 2-point factors
        malignancy: Annotated[bool, Field(description="惡性腫瘤(現在或過去) Malignancy (+2)", default=False)],
        # 3-point factors (thrombophilia)
        history_dvt_pe: Annotated[bool, Field(description="DVT/PE病史 History of DVT/PE (+3)", default=False)],
        family_history_thrombosis: Annotated[bool, Field(description="血栓家族史 Family history (+3)", default=False)],
        factor_v_leiden: Annotated[bool, Field(description="Factor V Leiden (+3)", default=False)],
        prothrombin_20210a: Annotated[bool, Field(description="Prothrombin 20210A (+3)", default=False)],
        elevated_homocysteine: Annotated[bool, Field(description="高同半胱胺酸血症 (+3)", default=False)],
        lupus_anticoagulant: Annotated[bool, Field(description="狼瘡抗凝血因子 (+3)", default=False)],
        anticardiolipin_antibodies: Annotated[bool, Field(description="抗心磷脂抗體 (+3)", default=False)],
        hit_history: Annotated[bool, Field(description="HIT病史 Heparin-induced thrombocytopenia (+3)", default=False)],
        other_thrombophilia: Annotated[bool, Field(description="其他血栓傾向 Other thrombophilia (+3)", default=False)],
        # 5-point factors
        stroke_lt_1mo: Annotated[bool, Field(description="中風 <1個月 Stroke <1 month (+5)", default=False)],
        elective_arthroplasty: Annotated[bool, Field(description="選擇性關節置換術 Elective arthroplasty (+5)", default=False)],
        hip_pelvis_leg_fracture_lt_1mo: Annotated[bool, Field(description="髖/骨盆/下肢骨折 <1個月 (+5)", default=False)],
        spinal_cord_injury_lt_1mo: Annotated[bool, Field(description="急性脊髓損傷 <1個月 (+5)", default=False)],
        # Female-specific
        female: Annotated[bool, Field(description="女性 Female patient", default=False)],
        oral_contraceptives_or_hrt: Annotated[bool, Field(description="口服避孕藥或HRT (女性+1)", default=False)],
        pregnancy_or_postpartum: Annotated[bool, Field(description="懷孕或產後 <1個月 (女性+1)", default=False)],
        pregnancy_loss_history: Annotated[bool, Field(description="不明死胎/反覆流產/早產合併毒血症 (女性+1)", default=False)],
    ) -> dict[str, Any]:
        """
        🔪 Caprini VTE 風險評估: 手術病人靜脈血栓栓塞風險
        
        評估手術病人發生深部靜脈血栓 (DVT) 和肺栓塞 (PE) 的風險，
        以指導預防性抗凝治療的選擇與時程。
        
        **計分方式:**
        - 1分: 年齡41-60、小手術、靜脈曲張、IBD、下肢水腫、BMI>25、
               急性MI、心衰<1月、敗血症<1月、肺病、COPD、臥床(內科)、
               下肢石膏/支架、中央靜脈導管
        - 2分: 年齡61-74、關節鏡手術、大手術>45分、腹腔鏡>45分、
               惡性腫瘤、臥床>72h、固定石膏<1月
        - 3分: 年齡≥75、DVT/PE病史、血栓家族史、Factor V Leiden、
               Prothrombin 20210A、高同半胱胺酸、狼瘡抗凝、
               抗心磷脂抗體、HIT病史、其他血栓傾向
        - 5分: 中風<1月、選擇性關節置換、髖/骨盆/腿骨折<1月、
               急性脊髓損傷<1月
        - 女性專用(+1): 口服避孕藥/HRT、懷孕或產後、不良妊娠史
        
        **風險分級與VTE發生率:**
        - 0分: 極低風險 (~0.5%) → 早期下床活動
        - 1-2分: 低風險 (~1.5%) → 機械性預防 (SCD)
        - 3-4分: 中度風險 (~3%) → 藥物預防或機械預防
        - ≥5分: 高風險 (~6%) → 藥物預防 + 機械預防
        
        **參考文獻:** 
        - Caprini JA. Dis Mon. 2005;51(2-3):70-78. PMID: 15900257
        - Bahl V, et al. Ann Surg. 2010;251(2):344-350. PMID: 19779324
        
        Returns:
            Caprini 分數、VTE 風險等級、預防措施建議
        """
        request = CalculateRequest(
            tool_id="caprini_vte",
            params={
                "age_years": age_years,
                "minor_surgery": minor_surgery,
                "major_surgery": major_surgery,
                "laparoscopic_surgery_gt_45min": laparoscopic_surgery_gt_45min,
                "arthroscopic_surgery": arthroscopic_surgery,
                "prior_major_surgery_lt_1mo": prior_major_surgery_lt_1mo,
                "varicose_veins": varicose_veins,
                "inflammatory_bowel_disease": inflammatory_bowel_disease,
                "swollen_legs": swollen_legs,
                "obesity_bmi_gt_25": obesity_bmi_gt_25,
                "acute_mi": acute_mi,
                "chf_lt_1mo": chf_lt_1mo,
                "sepsis_lt_1mo": sepsis_lt_1mo,
                "lung_disease": lung_disease,
                "copd": copd,
                "bed_rest_medical": bed_rest_medical,
                "bed_confined_gt_72hr": bed_confined_gt_72hr,
                "leg_cast_or_brace": leg_cast_or_brace,
                "immobilizing_cast_lt_1mo": immobilizing_cast_lt_1mo,
                "central_venous_access": central_venous_access,
                "malignancy": malignancy,
                "history_dvt_pe": history_dvt_pe,
                "family_history_thrombosis": family_history_thrombosis,
                "factor_v_leiden": factor_v_leiden,
                "prothrombin_20210a": prothrombin_20210a,
                "elevated_homocysteine": elevated_homocysteine,
                "lupus_anticoagulant": lupus_anticoagulant,
                "anticardiolipin_antibodies": anticardiolipin_antibodies,
                "hit_history": hit_history,
                "other_thrombophilia": other_thrombophilia,
                "stroke_lt_1mo": stroke_lt_1mo,
                "elective_arthroplasty": elective_arthroplasty,
                "hip_pelvis_leg_fracture_lt_1mo": hip_pelvis_leg_fracture_lt_1mo,
                "spinal_cord_injury_lt_1mo": spinal_cord_injury_lt_1mo,
                "female": female,
                "oral_contraceptives_or_hrt": oral_contraceptives_or_hrt,
                "pregnancy_or_postpartum": pregnancy_or_postpartum,
                "pregnancy_loss_history": pregnancy_loss_history,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()
