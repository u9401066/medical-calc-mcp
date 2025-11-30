"""
Calculator Handler

MCP tool handlers for calculator operations.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP

from ....application.dto import CalculateRequest
from ....application.use_cases import CalculateUseCase
from ....domain.registry.tool_registry import ToolRegistry


class CalculatorHandler:
    """
    Handler for calculator-related MCP tools.
    
    Registers all calculator tools with the MCP server.
    Each calculator gets its own dedicated MCP tool with typed parameters.
    """
    
    def __init__(self, mcp: FastMCP, registry: ToolRegistry):
        self._mcp = mcp
        self._registry = registry
        self._use_case = CalculateUseCase(registry)
        
        # Register tools
        self._register_tools()
    
    def _register_tools(self) -> None:
        """Register all calculator tools with MCP"""
        
        # =================================================================
        # Nephrology
        # =================================================================
        
        @self._mcp.tool()
        def calculate_ckd_epi_2021(
            serum_creatinine: float,
            age: int,
            sex: str
        ) -> dict[str, Any]:
            """
            計算 CKD-EPI 2021 eGFR (腎絲球過濾率)
            
            Calculate estimated GFR using the 2021 CKD-EPI equation (race-free).
            
            Args:
                serum_creatinine: 血清肌酐值 (mg/dL)
                age: 年齡 (歲, 18-120)
                sex: 性別 ("male" 或 "female")
                
            Returns:
                eGFR 值、CKD 分期、臨床解讀和建議
                
            Reference:
                Inker LA, et al. N Engl J Med. 2021;385(19):1737-1749.
            """
            request = CalculateRequest(
                tool_id="ckd_epi_2021",
                params={"serum_creatinine": serum_creatinine, "age": age, "sex": sex}
            )
            response = self._use_case.execute(request)
            return response.to_dict()
        
        # =================================================================
        # Anesthesiology / Preoperative
        # =================================================================
        
        @self._mcp.tool()
        def calculate_asa_physical_status(
            asa_class: int,
            is_emergency: bool = False
        ) -> dict[str, Any]:
            """
            ASA 身體狀態分級
            
            Classify patient using ASA Physical Status Classification (I-VI).
            
            Args:
                asa_class: ASA 分級 (1-6)
                    1: 健康病人
                    2: 輕度全身性疾病
                    3: 嚴重全身性疾病
                    4: 持續威脅生命的嚴重全身性疾病
                    5: 瀕死病人，不手術無法存活
                    6: 腦死器官捐贈者
                is_emergency: 是否為緊急手術 (加 E 字尾)
                
            Returns:
                ASA 分級、描述、周術期死亡率風險估計
            """
            request = CalculateRequest(
                tool_id="asa_physical_status",
                params={"asa_class": asa_class, "is_emergency": is_emergency}
            )
            response = self._use_case.execute(request)
            return response.to_dict()
        
        @self._mcp.tool()
        def calculate_mallampati(mallampati_class: int) -> dict[str, Any]:
            """
            Mallampati 氣道評估分級
            
            Predict difficult intubation using Modified Mallampati Classification.
            
            Args:
                mallampati_class: Mallampati 分級 (1-4)
                    1: 可見軟顎、懸雍垂、咽門弓
                    2: 可見軟顎、懸雍垂
                    3: 可見軟顎、懸雍垂基部
                    4: 只可見硬顎
                    
            Returns:
                分級、困難插管風險評估、建議
            """
            request = CalculateRequest(
                tool_id="mallampati_score",
                params={"mallampati_class": mallampati_class}
            )
            response = self._use_case.execute(request)
            return response.to_dict()
        
        @self._mcp.tool()
        def calculate_rcri(
            high_risk_surgery: bool = False,
            ischemic_heart_disease: bool = False,
            heart_failure: bool = False,
            cerebrovascular_disease: bool = False,
            insulin_diabetes: bool = False,
            creatinine_above_2: bool = False
        ) -> dict[str, Any]:
            """
            計算 RCRI 心臟風險指數 (Lee Index)
            
            Estimate risk of major cardiac complications after non-cardiac surgery.
            
            Args:
                high_risk_surgery: 高風險手術（腹腔內、胸腔內、主動脈上血管手術）
                ischemic_heart_disease: 缺血性心臟病史
                heart_failure: 心衰竭病史
                cerebrovascular_disease: 腦血管疾病史
                insulin_diabetes: 需胰島素治療的糖尿病
                creatinine_above_2: 肌酐 >2 mg/dL
                
            Returns:
                RCRI 分數 (0-6)、心臟併發症風險百分比、建議
            """
            request = CalculateRequest(
                tool_id="rcri",
                params={
                    "high_risk_surgery": high_risk_surgery,
                    "ischemic_heart_disease": ischemic_heart_disease,
                    "heart_failure": heart_failure,
                    "cerebrovascular_disease": cerebrovascular_disease,
                    "insulin_diabetes": insulin_diabetes,
                    "creatinine_above_2": creatinine_above_2
                }
            )
            response = self._use_case.execute(request)
            return response.to_dict()
        
        # =================================================================
        # Critical Care / ICU
        # =================================================================
        
        @self._mcp.tool()
        def calculate_apache_ii(
            temperature: float,
            mean_arterial_pressure: float,
            heart_rate: float,
            respiratory_rate: float,
            fio2: float,
            arterial_ph: float = 7.40,
            serum_sodium: float = 140.0,
            serum_potassium: float = 4.0,
            serum_creatinine: float = 1.0,
            hematocrit: float = 40.0,
            wbc_count: float = 10.0,
            gcs_score: int = 15,
            age: int = 50,
            pao2: float | None = None,
            aado2: float | None = None,
            chronic_conditions: list[str] | None = None,
            admission_type: str = "nonoperative",
            acute_renal_failure: bool = False
        ) -> dict[str, Any]:
            """
            計算 APACHE II 分數 (ICU 嚴重度評估)
            
            Estimate ICU mortality based on acute physiology and chronic health.
            
            Args:
                temperature: 體溫 (°C)
                mean_arterial_pressure: 平均動脈壓 (mmHg)
                heart_rate: 心率 (bpm)
                respiratory_rate: 呼吸速率 (次/分)
                fio2: 吸入氧濃度 (0.21-1.0)
                arterial_ph: 動脈血 pH (預設 7.40)
                serum_sodium: 血鈉 (mEq/L, 預設 140)
                serum_potassium: 血鉀 (mEq/L, 預設 4.0)
                serum_creatinine: 血肌酐 (mg/dL, 預設 1.0)
                hematocrit: 血球容積比 (%, 預設 40)
                wbc_count: 白血球計數 (×10³/µL, 預設 10)
                gcs_score: 格拉斯哥昏迷指數 (3-15, 預設 15)
                age: 年齡 (歲)
                pao2: 動脈血氧分壓 (mmHg, FiO2<0.5 時使用)
                aado2: 肺泡-動脈氧分壓差 (mmHg, FiO2≥0.5 時使用)
                chronic_conditions: 慢性健康問題清單
                admission_type: 入院類型
                acute_renal_failure: 是否有急性腎衰竭
                
            Returns:
                APACHE II 分數、預估死亡率、建議
            """
            request = CalculateRequest(
                tool_id="apache_ii",
                params={
                    "temperature": temperature,
                    "mean_arterial_pressure": mean_arterial_pressure,
                    "heart_rate": heart_rate,
                    "respiratory_rate": respiratory_rate,
                    "fio2": fio2,
                    "arterial_ph": arterial_ph,
                    "serum_sodium": serum_sodium,
                    "serum_potassium": serum_potassium,
                    "serum_creatinine": serum_creatinine,
                    "hematocrit": hematocrit,
                    "wbc_count": wbc_count,
                    "gcs_score": gcs_score,
                    "age": age,
                    "pao2": pao2,
                    "aado2": aado2,
                    "chronic_health_conditions": tuple(chronic_conditions or []),
                    "admission_type": admission_type,
                    "acute_renal_failure": acute_renal_failure
                }
            )
            response = self._use_case.execute(request)
            return response.to_dict()
        
        @self._mcp.tool()
        def calculate_rass(rass_score: int) -> dict[str, Any]:
            """
            RASS 鎮靜躁動評估量表
            
            Assess level of agitation or sedation in ICU patients.
            
            Args:
                rass_score: RASS 分數 (-5 到 +4)
                    +4: 好鬥 (Combative)
                    +3: 非常躁動 (Very agitated)
                    +2: 躁動 (Agitated)
                    +1: 不安 (Restless)
                     0: 警醒平靜 (Alert and calm)
                    -1: 嗜睡 (Drowsy)
                    -2: 輕度鎮靜 (Light sedation)
                    -3: 中度鎮靜 (Moderate sedation)
                    -4: 深度鎮靜 (Deep sedation)
                    -5: 無法喚醒 (Unarousable)
                    
            Returns:
                RASS 解讀、鎮靜程度評估、建議
            """
            request = CalculateRequest(
                tool_id="rass",
                params={"rass_score": rass_score}
            )
            response = self._use_case.execute(request)
            return response.to_dict()
        
        @self._mcp.tool()
        def calculate_sofa(
            pao2_fio2_ratio: float,
            platelets: float,
            bilirubin: float,
            gcs_score: int,
            creatinine: float,
            map_value: float | None = None,
            dopamine_dose: float | None = None,
            dobutamine_any: bool = False,
            epinephrine_dose: float | None = None,
            norepinephrine_dose: float | None = None,
            is_mechanically_ventilated: bool = False,
            urine_output_24h: float | None = None,
        ) -> dict[str, Any]:
            """
            計算 SOFA 分數 (Sequential Organ Failure Assessment)
            
            SOFA 評估六個器官系統功能，是 Sepsis-3 診斷標準的核心。
            SOFA ≥2 分在懷疑感染時符合敗血症定義。
            
            Args:
                pao2_fio2_ratio: PaO2/FiO2 比值 (mmHg)
                platelets: 血小板計數 (×10³/µL)
                bilirubin: 總膽紅素 (mg/dL)
                gcs_score: 格拉斯哥昏迷指數 (3-15)
                creatinine: 血清肌酐 (mg/dL)
                map_value: 平均動脈壓 (mmHg)
                dopamine_dose: Dopamine 劑量 (µg/kg/min)
                dobutamine_any: 是否使用 Dobutamine
                epinephrine_dose: Epinephrine 劑量 (µg/kg/min)
                norepinephrine_dose: Norepinephrine 劑量 (µg/kg/min)
                is_mechanically_ventilated: 是否使用機械通氣
                urine_output_24h: 24 小時尿量 (mL)
                
            Returns:
                SOFA 分數 (0-24)、各器官分數、死亡率預測
                
            References:
                Vincent JL, et al. Intensive Care Med. 1996.
                Singer M, et al. JAMA. 2016. (Sepsis-3)
            """
            request = CalculateRequest(
                tool_id="sofa_score",
                params={
                    "pao2_fio2_ratio": pao2_fio2_ratio,
                    "platelets": platelets,
                    "bilirubin": bilirubin,
                    "gcs_score": gcs_score,
                    "creatinine": creatinine,
                    "map_value": map_value,
                    "dopamine_dose": dopamine_dose,
                    "dobutamine_any": dobutamine_any,
                    "epinephrine_dose": epinephrine_dose,
                    "norepinephrine_dose": norepinephrine_dose,
                    "is_mechanically_ventilated": is_mechanically_ventilated,
                    "urine_output_24h": urine_output_24h,
                }
            )
            response = self._use_case.execute(request)
            return response.to_dict()
        
        @self._mcp.tool()
        def calculate_qsofa(
            respiratory_rate: int,
            systolic_bp: int,
            altered_mentation: bool = False,
            gcs_score: int = 15,
        ) -> dict[str, Any]:
            """
            計算 qSOFA 分數 (Quick SOFA)
            
            qSOFA 是一個快速床邊評估工具，用於識別感染風險較高的病患。
            注意：依據 SSC 2021 指引，不建議單獨使用 qSOFA 作為敗血症篩檢工具。
            
            Args:
                respiratory_rate: 呼吸速率 (次/分)
                systolic_bp: 收縮壓 (mmHg)
                altered_mentation: 意識改變 (GCS <15 或急性意識變化)
                gcs_score: GCS 分數 (3-15)
                
            Returns:
                qSOFA 分數 (0-3) 和風險評估
            """
            request = CalculateRequest(
                tool_id="qsofa_score",
                params={
                    "respiratory_rate": respiratory_rate,
                    "systolic_bp": systolic_bp,
                    "altered_mentation": altered_mentation,
                    "gcs_score": gcs_score,
                }
            )
            response = self._use_case.execute(request)
            return response.to_dict()
        
        @self._mcp.tool()
        def calculate_news2(
            respiratory_rate: int,
            spo2: int,
            on_supplemental_o2: bool,
            temperature: float,
            systolic_bp: int,
            heart_rate: int,
            consciousness: str = "A",
            use_scale_2: bool = False,
        ) -> dict[str, Any]:
            """
            計算 NEWS2 分數 (National Early Warning Score 2)
            
            NEWS2 用於偵測住院病患的臨床惡化，觸發適當的臨床反應。
            
            Args:
                respiratory_rate: 呼吸速率 (次/分)
                spo2: 血氧飽和度 (%)
                on_supplemental_o2: 是否使用氧氣
                temperature: 體溫 (°C)
                systolic_bp: 收縮壓 (mmHg)
                heart_rate: 心率 (次/分)
                consciousness: AVPU 意識狀態 (A/V/P/U/C)
                use_scale_2: 是否使用 Scale 2（高碳酸血症呼吸衰竭）
                
            Returns:
                NEWS2 分數 (0-20) 和臨床反應建議
            """
            request = CalculateRequest(
                tool_id="news2_score",
                params={
                    "respiratory_rate": respiratory_rate,
                    "spo2": spo2,
                    "on_supplemental_o2": on_supplemental_o2,
                    "temperature": temperature,
                    "systolic_bp": systolic_bp,
                    "heart_rate": heart_rate,
                    "consciousness": consciousness,
                    "use_scale_2": use_scale_2,
                }
            )
            response = self._use_case.execute(request)
            return response.to_dict()
        
        @self._mcp.tool()
        def calculate_gcs(
            eye_response: int,
            verbal_response: int,
            motor_response: int,
            is_intubated: bool = False,
        ) -> dict[str, Any]:
            """
            計算 GCS 分數 (Glasgow Coma Scale)
            
            GCS 評估意識程度，是最廣泛使用的昏迷量表。
            
            Args:
                eye_response: 眼睛反應 (1-4)
                verbal_response: 語言反應 (1-5)
                motor_response: 運動反應 (1-6)
                is_intubated: 是否已插管
                
            Returns:
                GCS 分數 (3-15) 和腦傷嚴重度分級
            """
            request = CalculateRequest(
                tool_id="glasgow_coma_scale",
                params={
                    "eye_response": eye_response,
                    "verbal_response": verbal_response,
                    "motor_response": motor_response,
                    "is_intubated": is_intubated,
                }
            )
            response = self._use_case.execute(request)
            return response.to_dict()
        
        @self._mcp.tool()
        def calculate_cam_icu(
            rass_score: int,
            acute_onset_fluctuation: bool,
            inattention_score: int,
            altered_loc: bool = False,
            disorganized_thinking_errors: int = 0,
        ) -> dict[str, Any]:
            """
            計算 CAM-ICU (Confusion Assessment Method for ICU)
            
            CAM-ICU 是 ICU 病患譫妄篩檢的標準工具。
            
            Args:
                rass_score: RASS 分數 (-5 到 +4)
                acute_onset_fluctuation: Feature 1 - 急性發作或波動病程
                inattention_score: Feature 2 - ASE 注意力測試錯誤數
                altered_loc: Feature 3 - 意識程度改變
                disorganized_thinking_errors: Feature 4 - 思維障礙測試錯誤數
                
            Returns:
                CAM-ICU 結果和建議
            """
            request = CalculateRequest(
                tool_id="cam_icu",
                params={
                    "rass_score": rass_score,
                    "acute_onset_fluctuation": acute_onset_fluctuation,
                    "inattention_score": inattention_score,
                    "altered_loc": altered_loc,
                    "disorganized_thinking_errors": disorganized_thinking_errors,
                }
            )
            response = self._use_case.execute(request)
            return response.to_dict()
        
        # =================================================================
        # Pediatric & Anesthesia
        # =================================================================
        
        @self._mcp.tool()
        def calculate_pediatric_drug_dose(
            drug_name: str,
            weight_kg: float,
            route: str = "iv",
            indication: str | None = None,
        ) -> dict[str, Any]:
            """
            小兒藥物劑量計算器
            
            根據體重計算常見小兒藥物的建議劑量，包含安全上限檢查。
            
            Args:
                drug_name: 藥物名稱 (例如: acetaminophen, ibuprofen, amoxicillin, 
                           ceftriaxone, ondansetron, morphine, fentanyl, ketamine)
                weight_kg: 體重 (公斤)
                route: 給藥途徑 (iv, po, im, pr)
                indication: 適應症 (可選，用於選擇適當劑量)
                
            Returns:
                建議劑量範圍、最大劑量、給藥頻率和注意事項
                
            References:
                Lexicomp Pediatric & Neonatal Dosage Handbook
                Nelson Textbook of Pediatrics, 21st ed
            """
            request = CalculateRequest(
                tool_id="pediatric_dosing",
                params={
                    "drug_name": drug_name,
                    "weight_kg": weight_kg,
                    "route": route,
                    "indication": indication,
                }
            )
            response = self._use_case.execute(request)
            return response.to_dict()
        
        @self._mcp.tool()
        def calculate_mabl(
            weight_kg: float,
            initial_hematocrit: float,
            target_hematocrit: float,
            patient_type: str = "adult_male",
        ) -> dict[str, Any]:
            """
            計算最大允許失血量 (Maximum Allowable Blood Loss)
            
            MABL 用於術前評估，決定何時需要輸血。
            
            公式: MABL = EBV × (Hi - Hf) / Havg
            
            Args:
                weight_kg: 體重 (公斤)
                initial_hematocrit: 術前血球容積比 (%)
                target_hematocrit: 目標/最低可接受血球容積比 (%)
                patient_type: 病患類型
                    - preterm_neonate: 早產兒 (EBV 90 mL/kg)
                    - term_neonate: 足月新生兒 (EBV 85 mL/kg)
                    - infant: 嬰兒 (EBV 80 mL/kg)
                    - child: 兒童 (EBV 75 mL/kg)
                    - adult_male: 成年男性 (EBV 70 mL/kg)
                    - adult_female: 成年女性 (EBV 65 mL/kg)
                    
            Returns:
                MABL (mL)、EBV、允許失血百分比和輸血建議
                
            Reference:
                Miller's Anesthesia, 9th ed, Chapter 49
                Gross JB. Anesthesiology 1983;58(3):277-280
            """
            request = CalculateRequest(
                tool_id="mabl",
                params={
                    "weight_kg": weight_kg,
                    "initial_hematocrit": initial_hematocrit,
                    "target_hematocrit": target_hematocrit,
                    "patient_type": patient_type,
                }
            )
            response = self._use_case.execute(request)
            return response.to_dict()
        
        @self._mcp.tool()
        def calculate_transfusion_volume(
            weight_kg: float,
            product_type: str = "prbc",
            patient_type: str = "adult_male",
            current_hematocrit: float | None = None,
            target_hematocrit: float | None = None,
            current_hemoglobin: float | None = None,
            target_hemoglobin: float | None = None,
            current_platelet: float | None = None,
            target_platelet: float | None = None,
        ) -> dict[str, Any]:
            """
            輸血量計算器
            
            計算達到目標 Hct/Hgb/Plt 所需的血品量。
            
            Args:
                weight_kg: 體重 (公斤)
                product_type: 血品類型
                    - prbc: 濃縮紅血球
                    - whole_blood: 全血
                    - platelets: 分離術血小板
                    - platelet_concentrate: 濃縮血小板
                    - ffp: 新鮮冷凍血漿
                    - cryoprecipitate: 冷凍沉澱品
                patient_type: 病患類型 (用於計算 EBV)
                current_hematocrit: 目前 Hct (%)
                target_hematocrit: 目標 Hct (%)
                current_hemoglobin: 目前 Hgb (g/dL) - 替代 Hct
                target_hemoglobin: 目標 Hgb (g/dL)
                current_platelet: 目前血小板 (×10⁹/L)
                target_platelet: 目標血小板 (×10⁹/L)
                
            Returns:
                所需輸血量 (mL)、血品單位數、預期上升值
                
            References:
                Roseff SD, et al. Transfusion. 2002.
                New HV, et al. Br J Haematol. 2016.
            """
            request = CalculateRequest(
                tool_id="transfusion_calc",
                params={
                    "weight_kg": weight_kg,
                    "product_type": product_type,
                    "patient_type": patient_type,
                    "current_hematocrit": current_hematocrit,
                    "target_hematocrit": target_hematocrit,
                    "current_hemoglobin": current_hemoglobin,
                    "target_hemoglobin": target_hemoglobin,
                    "current_platelet": current_platelet,
                    "target_platelet": target_platelet,
                }
            )
            response = self._use_case.execute(request)
            return response.to_dict()
