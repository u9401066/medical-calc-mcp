"""
End-to-End Workflow Tests (Production Quality)

使用正確的 DiscoveryUseCase.execute() API 測試完整臨床工作流程。
測試情境模擬 AI Agent 實際使用模式。

Test Categories:
1. Discovery-First Workflow - 先探索再計算
2. Clinical Workflows - 臨床場景多工具組合
3. Error Recovery - 錯誤恢復機制
4. Agent Simulation - AI Agent 使用模式

Author: Medical-Calc MCP Team
"""

import pytest

from src.application.dto import (
    CalculateRequest,
    DiscoveryMode,
    DiscoveryRequest,
)
from src.application.use_cases.calculate_use_case import CalculateUseCase
from src.application.use_cases.discovery_use_case import DiscoveryUseCase


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def registry():
    """Get initialized tool registry with all calculators registered"""
    from src.domain.registry import ToolRegistry
    from src.domain.services.calculators import CALCULATORS

    reg = ToolRegistry()
    for calc_class in CALCULATORS:
        calc = calc_class()
        reg.register(calc)
    return reg


@pytest.fixture
def discovery(registry):
    """Discovery use case instance"""
    return DiscoveryUseCase(registry)


@pytest.fixture
def calculator(registry):
    """Calculate use case instance"""
    return CalculateUseCase(registry)


# =============================================================================
# Discovery-First Workflow Tests
# =============================================================================


class TestDiscoveryFirstWorkflow:
    """
    測試推薦的 Discovery-First 工作流程。

    Pattern:
    1. list_specialties() or list_contexts() → 獲取分類
    2. list_by_specialty() or search() → 找到工具
    3. get_info(tool_id) → 獲取參數
    4. calculate(tool_id, params) → 執行計算
    """

    def test_specialty_navigation_workflow(self, discovery, calculator):
        """
        Test: 通過專科導航找到並使用計算器

        Workflow:
        1. LIST_SPECIALTIES → 獲取所有專科
        2. BY_SPECIALTY → 列出該專科工具
        3. GET_INFO → 獲取工具詳情
        4. Calculate → 執行計算
        """
        print("\n" + "=" * 60)
        print("📋 TEST: Specialty Navigation Workflow")
        print("=" * 60)

        # Step 1: List all specialties
        response = discovery.execute(
            DiscoveryRequest(mode=DiscoveryMode.LIST_SPECIALTIES)
        )
        assert response.success, f"Failed to list specialties: {response.error}"
        assert len(response.available_specialties) > 0
        print(f"\n✅ Step 1: Found {len(response.available_specialties)} specialties")
        print(f"   Specialties: {response.available_specialties[:5]}...")

        # Step 2: Browse critical_care specialty
        response = discovery.execute(
            DiscoveryRequest(mode=DiscoveryMode.BY_SPECIALTY, specialty="critical_care")
        )
        assert response.success, f"Failed to list by specialty: {response.error}"
        assert len(response.tools) > 0
        print(f"\n✅ Step 2: Found {len(response.tools)} critical care tools")
        print(f"   Tools: {[t.tool_id for t in response.tools[:5]]}")

        # Step 3: Get info for NEWS2
        response = discovery.execute(
            DiscoveryRequest(mode=DiscoveryMode.GET_INFO, tool_id="news2_score")
        )
        assert response.success, f"Failed to get tool info: {response.error}"
        assert response.tool_detail is not None
        assert response.tool_detail.tool_id == "news2_score"
        print(f"\n✅ Step 3: Got NEWS2 info")
        print(f"   Parameters: {response.tool_detail.input_params}")

        # Step 4: Execute calculation with sample values
        calc_response = calculator.execute(
            CalculateRequest(
                tool_id="news2_score",
                params={
                    "respiratory_rate": 18,
                    "spo2": 96,
                    "on_supplemental_o2": False,
                    "temperature": 37.2,
                    "systolic_bp": 120,
                    "heart_rate": 80,
                    "consciousness": "A",
                },
            )
        )
        assert calc_response.success, f"Calculation failed: {calc_response.error}"
        print(f"\n✅ Step 4: NEWS2 = {calc_response.result}")
        print("=" * 60)

    def test_search_workflow(self, discovery, calculator):
        """
        Test: 通過關鍵字搜索找到工具

        Workflow:
        1. SEARCH "sepsis" → 找到相關工具
        2. GET_INFO → 獲取 qSOFA 詳情
        3. Calculate → 執行計算
        """
        print("\n" + "=" * 60)
        print("🔍 TEST: Search Workflow")
        print("=" * 60)

        # Step 1: Search for sepsis-related tools
        response = discovery.execute(
            DiscoveryRequest(mode=DiscoveryMode.SEARCH, query="sofa")
        )
        assert response.success
        tool_ids = [t.tool_id for t in response.tools]
        print(f"\n✅ Step 1: Sepsis search found {len(tool_ids)} tools")
        print(f"   Results: {tool_ids}")

        # Should find SOFA-related tools
        assert any(
            "sofa" in t.lower() for t in tool_ids
        ), f"Should find SOFA tools, got: {tool_ids}"

        # Step 2: Get qSOFA info (if available)
        if "qsofa_score" in tool_ids:
            response = discovery.execute(
                DiscoveryRequest(mode=DiscoveryMode.GET_INFO, tool_id="qsofa_score")
            )
            assert response.success
            print(f"\n✅ Step 2: Got qSOFA info")
            print(f"   Params: {response.tool_detail.input_params}")

            # Step 3: Calculate
            calc_response = calculator.execute(
                CalculateRequest(
                    tool_id="qsofa_score",
                    params={
                        "respiratory_rate": 24,
                        "systolic_bp": 95,
                        "altered_mentation": True,
                    },
                )
            )
            assert calc_response.success
            print(f"\n✅ Step 3: qSOFA = {calc_response.result}")
        print("=" * 60)

    def test_context_navigation_workflow(self, discovery):
        """
        Test: 通過臨床情境導航

        Workflow:
        1. LIST_CONTEXTS → 獲取所有臨床情境
        2. BY_CONTEXT → 列出該情境工具
        """
        print("\n" + "=" * 60)
        print("📊 TEST: Context Navigation Workflow")
        print("=" * 60)

        # Step 1: List all contexts
        response = discovery.execute(
            DiscoveryRequest(mode=DiscoveryMode.LIST_CONTEXTS)
        )
        assert response.success
        assert len(response.available_contexts) > 0
        print(f"\n✅ Step 1: Found {len(response.available_contexts)} contexts")
        print(f"   Contexts: {response.available_contexts}")

        # Step 2: Browse severity_assessment context
        if "severity_assessment" in response.available_contexts:
            response = discovery.execute(
                DiscoveryRequest(
                    mode=DiscoveryMode.BY_CONTEXT, context="severity_assessment"
                )
            )
            assert response.success
            print(f"\n✅ Step 2: Found {len(response.tools)} severity tools")
            print(f"   Tools: {[t.tool_id for t in response.tools]}")
        print("=" * 60)


# =============================================================================
# Clinical Workflow Tests
# =============================================================================


class TestClinicalWorkflows:
    """
    測試完整臨床工作流程 - 多工具組合使用。

    這些測試模擬真實臨床場景中的多步驟評估流程。
    """

    def test_sepsis_evaluation_workflow(self, calculator):
        """
        Sepsis Evaluation Workflow (敗血症評估)

        Clinical Flow:
        1. qSOFA → 床邊快篩
        2. SOFA → 完整器官衰竭評估 (如果 qSOFA ≥ 2)
        3. RASS → 鎮靜程度
        4. CAM-ICU → 譫妄篩檢
        """
        print("\n" + "=" * 60)
        print("🦠 CLINICAL WORKFLOW: Sepsis Evaluation")
        print("=" * 60)

        # Step 1: qSOFA screening
        qsofa_result = calculator.execute(
            CalculateRequest(
                tool_id="qsofa_score",
                params={
                    "respiratory_rate": 26,  # ≥22 → 1 point
                    "systolic_bp": 90,  # ≤100 → 1 point
                    "altered_mentation": True,  # → 1 point
                },
            )
        )
        assert qsofa_result.success, f"qSOFA failed: {qsofa_result.error}"
        print(f"\n1️⃣ qSOFA Score: {qsofa_result.result}")

        qsofa_score = qsofa_result.result
        assert qsofa_score >= 2, "Test case should have qSOFA ≥ 2"

        # Step 2: Full SOFA (since qSOFA ≥ 2)
        print("   ⚠️ qSOFA ≥ 2 → Proceeding to full SOFA assessment")

        sofa_result = calculator.execute(
            CalculateRequest(
                tool_id="sofa_score",
                params={
                    "pao2_fio2_ratio": 250,  # 200-300 → 2 points
                    "platelets": 120,  # 100-150 → 1 point
                    "bilirubin": 1.5,  # 1.2-2 → 1 point
                    "gcs_score": 13,  # 13-14 → 1 point
                    "creatinine": 1.8,  # 1.2-2 → 1 point
                    "map_value": 65,  # <70 → 1 point
                },
            )
        )
        assert sofa_result.success, f"SOFA failed: {sofa_result.error}"
        print(f"2️⃣ SOFA Score: {sofa_result.result}")

        # Step 3: RASS assessment
        rass_result = calculator.execute(
            CalculateRequest(tool_id="rass", params={"rass_score": -1})
        )
        assert rass_result.success, f"RASS failed: {rass_result.error}"
        print(f"3️⃣ RASS Level: {rass_result.result}")

        # Step 4: CAM-ICU (requires RASS ≥ -3)
        cam_result = calculator.execute(
            CalculateRequest(
                tool_id="cam_icu",
                params={
                    "rass_score": -1,
                    "acute_onset_fluctuation": True,  # Feature 1
                    "inattention_score": 5,  # Feature 2 (≥3 = positive)
                    "altered_loc": True,  # Feature 3
                    "disorganized_thinking_errors": 2,  # Feature 4
                },
            )
        )
        assert cam_result.success, f"CAM-ICU failed: {cam_result.error}"
        print(f"4️⃣ CAM-ICU: {cam_result.result}")
        print("=" * 60)

    def test_preoperative_assessment_workflow(self, calculator):
        """
        Preoperative Assessment Workflow (術前評估)

        Clinical Flow:
        1. ASA Physical Status → 整體健康狀態
        2. RCRI → 心臟風險
        3. Mallampati → 氣道評估
        4. STOP-BANG → OSA 篩檢
        """
        print("\n" + "=" * 60)
        print("🏥 CLINICAL WORKFLOW: Preoperative Assessment")
        print("=" * 60)

        # Step 1: ASA Classification
        asa_result = calculator.execute(
            CalculateRequest(
                tool_id="asa_physical_status",
                params={"asa_class": 3, "is_emergency": False},
            )
        )
        assert asa_result.success, f"ASA failed: {asa_result.error}"
        print(f"\n1️⃣ ASA Physical Status: {asa_result.result}")

        # Step 2: RCRI for cardiac risk
        rcri_result = calculator.execute(
            CalculateRequest(
                tool_id="rcri",
                params={
                    "high_risk_surgery": True,
                    "ischemic_heart_disease": False,
                    "congestive_heart_failure": False,
                    "cerebrovascular_disease": False,
                    "insulin_therapy_diabetes": True,
                    "preop_creatinine_gt_2": False,
                },
            )
        )
        assert rcri_result.success, f"RCRI failed: {rcri_result.error}"
        print(f"2️⃣ RCRI Score: {rcri_result.result}")

        # Step 3: Mallampati airway assessment
        mallampati_result = calculator.execute(
            CalculateRequest(tool_id="mallampati_score", params={"mallampati_class": 2})
        )
        assert mallampati_result.success, f"Mallampati failed: {mallampati_result.error}"
        print(f"3️⃣ Mallampati Class: {mallampati_result.result}")

        # Step 4: STOP-BANG for OSA
        stopbang_result = calculator.execute(
            CalculateRequest(
                tool_id="stop_bang",
                params={
                    "snoring": True,
                    "tired": True,
                    "observed_apnea": False,
                    "high_blood_pressure": True,
                    "bmi_over_35": False,
                    "age_over_50": True,
                    "neck_over_40cm": False,
                    "male_gender": True,
                },
            )
        )
        assert stopbang_result.success, f"STOP-BANG failed: {stopbang_result.error}"
        print(f"4️⃣ STOP-BANG Score: {stopbang_result.result}")
        print("=" * 60)

    def test_aki_evaluation_workflow(self, calculator):
        """
        AKI Evaluation Workflow (急性腎損傷評估)

        Clinical Flow:
        1. CKD-EPI → 基線 eGFR
        2. KDIGO AKI → AKI 分期
        """
        print("\n" + "=" * 60)
        print("🫘 CLINICAL WORKFLOW: AKI Evaluation")
        print("=" * 60)

        # Step 1: Baseline eGFR
        egfr_result = calculator.execute(
            CalculateRequest(
                tool_id="ckd_epi_2021",
                params={
                    "serum_creatinine": 0.9,  # baseline
                    "age": 65,
                    "sex": "male",
                },
            )
        )
        assert egfr_result.success, f"CKD-EPI failed: {egfr_result.error}"
        print(f"\n1️⃣ Baseline eGFR: {egfr_result.result} {egfr_result.unit}")

        # Step 2: KDIGO AKI staging (elevated creatinine)
        kdigo_result = calculator.execute(
            CalculateRequest(
                tool_id="kdigo_aki",
                params={
                    "current_creatinine": 2.1,  # elevated
                    "baseline_creatinine": 0.9,
                    "creatinine_increase_48h": 1.2,
                    "urine_output_ml_kg_h": 0.4,
                    "urine_output_duration_hours": 8,
                },
            )
        )
        assert kdigo_result.success, f"KDIGO AKI failed: {kdigo_result.error}"
        print(f"2️⃣ KDIGO AKI Stage: {kdigo_result.result}")
        if kdigo_result.interpretation:
            print(f"   📋 {kdigo_result.interpretation.summary}")
        print("=" * 60)

    def test_gi_bleeding_evaluation_workflow(self, calculator):
        """
        GI Bleeding Evaluation Workflow (上消化道出血評估)

        Clinical Flow:
        1. Glasgow-Blatchford → 需要干預風險
        2. Rockall Score → 再出血/死亡風險
        """
        print("\n" + "=" * 60)
        print("🩸 CLINICAL WORKFLOW: GI Bleeding Evaluation")
        print("=" * 60)

        # Step 1: Glasgow-Blatchford Score
        gbs_result = calculator.execute(
            CalculateRequest(
                tool_id="glasgow_blatchford",
                params={
                    "bun": 25,  # mg/dL
                    "hemoglobin": 10.0,  # g/dL
                    "systolic_bp": 100,  # mmHg
                    "heart_rate": 100,  # bpm
                    "melena": True,
                    "syncope": False,
                    "hepatic_disease": False,
                    "cardiac_failure": False,
                    "sex": "male",
                },
            )
        )
        assert gbs_result.success, f"Glasgow-Blatchford failed: {gbs_result.error}"
        print(f"\n1️⃣ Glasgow-Blatchford Score: {gbs_result.result}")

        # Step 2: Rockall Score
        rockall_result = calculator.execute(
            CalculateRequest(
                tool_id="rockall_score",
                params={
                    "age_years": 65,
                    "shock_status": "tachycardia",
                    "comorbidity": "cardiac_major",
                    "diagnosis": "other_diagnosis",
                    "stigmata_of_recent_hemorrhage": "none_or_dark_spot",
                },
            )
        )
        assert rockall_result.success, f"Rockall failed: {rockall_result.error}"
        print(f"2️⃣ Rockall Score: {rockall_result.result}")
        print("=" * 60)


# =============================================================================
# Error Recovery Tests
# =============================================================================


class TestErrorRecoveryWorkflow:
    """
    測試錯誤處理與恢復機制。

    模擬 Agent 遇到錯誤時的恢復流程。
    """

    def test_wrong_tool_id_recovery(self, calculator, discovery):
        """
        Test: 工具 ID 錯誤時的恢復

        Scenario:
        1. 使用錯誤 ID "news" (應該是 "news2_score")
        2. 收到錯誤訊息帶有建議
        3. 使用 SEARCH 找到正確工具
        4. 重新執行
        """
        print("\n" + "=" * 60)
        print("🔧 ERROR RECOVERY: Wrong Tool ID")
        print("=" * 60)

        # Step 1: Try wrong tool ID
        response = calculator.execute(
            CalculateRequest(tool_id="news", params={})  # Wrong!
        )
        assert not response.success
        print(f"\n❌ Step 1: Error (expected): {response.error[:100]}...")

        # Step 2: Error should help recovery
        # Either suggest correct tool or provide search hint
        error_lower = response.error.lower()
        assert any(x in error_lower for x in ["news2_score", "did you mean", "not found"])

        # Step 3: Use search to find correct tool
        search_response = discovery.execute(
            DiscoveryRequest(mode=DiscoveryMode.SEARCH, query="news2")
        )
        assert search_response.success
        tool_ids = [t.tool_id for t in search_response.tools]
        print(f"\n✅ Step 3: Search found: {tool_ids}")
        assert "news2_score" in tool_ids

        # Step 4: Now use correct tool
        correct_response = calculator.execute(
            CalculateRequest(
                tool_id="news2_score",
                params={
                    "respiratory_rate": 18,
                    "spo2": 96,
                    "on_supplemental_o2": False,
                    "temperature": 37.0,
                    "systolic_bp": 120,
                    "heart_rate": 80,
                    "consciousness": "A",
                },
            )
        )
        assert correct_response.success
        print(f"✅ Step 4: NEWS2 = {correct_response.result}")
        print("=" * 60)

    def test_missing_params_recovery(self, calculator, discovery):
        """
        Test: 缺少參數時的恢復

        Scenario:
        1. 只提供部分參數
        2. 收到錯誤訊息帶有 param_template
        3. 使用 GET_INFO 獲取完整參數列表
        4. 重新執行
        """
        print("\n" + "=" * 60)
        print("🔧 ERROR RECOVERY: Missing Parameters")
        print("=" * 60)

        # Step 1: Try with missing params
        response = calculator.execute(
            CalculateRequest(
                tool_id="ckd_epi_2021",
                params={"serum_creatinine": 1.2},  # Missing age, sex
            )
        )
        assert not response.success
        print(f"\n❌ Step 1: Error (expected): {response.error[:150]}...")

        # Step 2: Check if param_template is provided
        if response.component_scores and "param_template" in response.component_scores:
            print(f"   📋 Template provided: {response.component_scores['param_template']}")

        # Step 3: Get full parameter info
        info_response = discovery.execute(
            DiscoveryRequest(mode=DiscoveryMode.GET_INFO, tool_id="ckd_epi_2021")
        )
        assert info_response.success
        print(f"\n✅ Step 3: Required params: {info_response.tool_detail.input_params}")

        # Step 4: Retry with all params
        retry_response = calculator.execute(
            CalculateRequest(
                tool_id="ckd_epi_2021",
                params={"serum_creatinine": 1.2, "age": 55, "sex": "female"},
            )
        )
        assert retry_response.success
        print(f"✅ Step 4: eGFR = {retry_response.result} {retry_response.unit}")
        print("=" * 60)

    def test_invalid_param_value_recovery(self, calculator):
        """
        Test: 參數值無效時的恢復

        Scenario:
        1. 提供超出範圍的值
        2. 收到驗證錯誤
        3. 修正後重新執行
        """
        print("\n" + "=" * 60)
        print("🔧 ERROR RECOVERY: Invalid Parameter Value")
        print("=" * 60)

        # Step 1: Try with out-of-range value
        response = calculator.execute(
            CalculateRequest(
                tool_id="ckd_epi_2021",
                params={
                    "serum_creatinine": 1.2,
                    "age": 200,  # Invalid! (should be 18-120)
                    "sex": "male",
                },
            )
        )
        # Should fail validation
        assert not response.success
        print(f"\n❌ Step 1: Error (expected): {response.error[:150]}...")

        # Step 2: Fix and retry
        retry_response = calculator.execute(
            CalculateRequest(
                tool_id="ckd_epi_2021",
                params={"serum_creatinine": 1.2, "age": 65, "sex": "male"},
            )
        )
        assert retry_response.success
        print(f"\n✅ Step 2: Fixed! eGFR = {retry_response.result}")
        print("=" * 60)


# =============================================================================
# Agent Simulation Tests
# =============================================================================


class TestAgentSimulation:
    """
    模擬 AI Agent 使用系統的完整交互流程。
    """

    def test_agent_first_interaction(self, discovery, calculator):
        """
        Simulate: Agent 首次與系統交互

        User: "幫我評估這位病人的腎功能"

        Agent Behavior:
        1. 搜索腎臟相關工具
        2. 選擇最相關的工具
        3. 獲取參數資訊
        4. 執行計算
        5. 解讀結果
        """
        print("\n" + "=" * 60)
        print("🤖 AGENT SIMULATION: First Interaction")
        print("=" * 60)
        print("   User: '幫我評估這位病人的腎功能'")

        # Step 1: Agent searches for kidney-related tools
        print("\n🔍 Agent: Searching for kidney function tools...")
        search_response = discovery.execute(
            DiscoveryRequest(mode=DiscoveryMode.SEARCH, query="kidney eGFR creatinine")
        )
        assert search_response.success
        print(f"   Found: {[t.tool_id for t in search_response.tools]}")

        # Step 2: Agent selects CKD-EPI
        print("\n📋 Agent: Getting CKD-EPI 2021 info...")
        info_response = discovery.execute(
            DiscoveryRequest(mode=DiscoveryMode.GET_INFO, tool_id="ckd_epi_2021")
        )
        assert info_response.success
        print(f"   Description: {info_response.tool_detail.purpose[:80]}...")
        print(f"   Required: {info_response.tool_detail.input_params}")

        # Step 3: Agent executes calculation
        print("\n⚙️ Agent: Executing calculation...")
        calc_response = calculator.execute(
            CalculateRequest(
                tool_id="ckd_epi_2021",
                params={"serum_creatinine": 1.5, "age": 72, "sex": "female"},
            )
        )
        assert calc_response.success
        print(f"   Result: eGFR = {calc_response.result} {calc_response.unit}")

        # Step 4: Agent interprets result
        if calc_response.interpretation:
            print(f"\n💡 Agent: {calc_response.interpretation.summary}")
        print("=" * 60)

    def test_agent_multi_tool_assessment(self, discovery, calculator):
        """
        Simulate: Agent 執行多工具綜合評估

        User: "這位 68 歲男性剛做完大手術，評估他的整體風險"

        Agent Behavior:
        1. 列出所有可用工具分類
        2. 執行多個相關評估
        3. 彙整結果
        """
        print("\n" + "=" * 60)
        print("🤖 AGENT SIMULATION: Multi-Tool Assessment")
        print("=" * 60)
        print("   User: '68 歲男性，剛做完大手術，評估整體風險'")

        # Step 1: List specialties to understand scope
        print("\n📊 Agent: Reviewing available specialties...")
        spec_response = discovery.execute(
            DiscoveryRequest(mode=DiscoveryMode.LIST_SPECIALTIES)
        )
        assert spec_response.success
        print(f"   Available: {spec_response.available_specialties}")

        # Step 2: Execute multiple assessments
        print("\n⚙️ Agent: Running comprehensive assessment...")

        results = {}

        # NEWS2 for early warning
        news_result = calculator.execute(
            CalculateRequest(
                tool_id="news2_score",
                params={
                    "respiratory_rate": 22,
                    "spo2": 94,
                    "on_supplemental_o2": True,
                    "temperature": 37.5,
                    "systolic_bp": 105,
                    "heart_rate": 95,
                    "consciousness": "A",
                },
            )
        )
        if news_result.success:
            results["NEWS2"] = news_result.result

        # qSOFA for sepsis screening
        qsofa_result = calculator.execute(
            CalculateRequest(
                tool_id="qsofa_score",
                params={
                    "respiratory_rate": 22,
                    "systolic_bp": 105,
                    "altered_mentation": False,
                },
            )
        )
        if qsofa_result.success:
            results["qSOFA"] = qsofa_result.result

        # CKD-EPI for kidney function
        egfr_result = calculator.execute(
            CalculateRequest(
                tool_id="ckd_epi_2021",
                params={"serum_creatinine": 1.3, "age": 68, "sex": "male"},
            )
        )
        if egfr_result.success:
            results["eGFR"] = f"{egfr_result.result} {egfr_result.unit}"

        # Step 3: Summarize
        print(f"\n📋 Assessment Summary:")
        for tool, result in results.items():
            print(f"   • {tool}: {result}")

        print("\n💡 Agent: 這位 68 歲男性術後:")
        print(f"   - NEWS2 {results.get('NEWS2', 'N/A')} → 注意程度依分數判斷")
        print(f"   - qSOFA {results.get('qSOFA', 'N/A')} → 敗血症風險")
        print(f"   - eGFR {results.get('eGFR', 'N/A')} → 腎功能狀態")
        print("=" * 60)


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """
    測試邊界情況和特殊場景。
    """

    def test_list_all_tools(self, discovery):
        """Test: 列出所有可用工具"""
        response = discovery.execute(
            DiscoveryRequest(mode=DiscoveryMode.LIST_ALL, limit=100)
        )
        assert response.success
        assert len(response.tools) > 50  # Should have many tools
        print(f"\n✅ Total tools available: {len(response.tools)}")

    def test_invalid_specialty(self, discovery):
        """Test: 無效專科名稱處理"""
        response = discovery.execute(
            DiscoveryRequest(mode=DiscoveryMode.BY_SPECIALTY, specialty="invalid_specialty_xyz")
        )
        assert not response.success
        error_lower = response.error.lower()
        assert "unknown" in error_lower or "invalid" in error_lower
        # Should provide available specialties
        assert len(response.available_specialties) > 0
        print(f"\n✅ Error handled: {response.error[:50]}...")
        print(f"   Available: {response.available_specialties}")

    def test_invalid_context(self, discovery):
        """Test: 無效臨床情境處理"""
        response = discovery.execute(
            DiscoveryRequest(mode=DiscoveryMode.BY_CONTEXT, context="invalid_context_xyz")
        )
        assert not response.success
        assert len(response.available_contexts) > 0
        print(f"\n✅ Error handled, available contexts: {response.available_contexts}")

    def test_tool_not_found(self, discovery):
        """Test: 工具不存在處理"""
        response = discovery.execute(
            DiscoveryRequest(mode=DiscoveryMode.GET_INFO, tool_id="nonexistent_tool_xyz")
        )
        assert not response.success
        assert "not found" in response.error.lower()
        print(f"\n✅ Error handled: {response.error[:80]}...")

    def test_param_alias_matching(self, calculator):
        """Test: 參數別名匹配 (ParamMatcher 功能)"""
        # Use alias "cr" instead of "serum_creatinine"
        response = calculator.execute(
            CalculateRequest(
                tool_id="ckd_epi_2021",
                params={
                    "cr": 1.2,  # Alias for serum_creatinine
                    "age": 55,
                    "sex": "male",
                },
            )
        )
        # Should either succeed (alias matched) or give helpful error
        if response.success:
            print(f"\n✅ Alias 'cr' matched! eGFR = {response.result}")
        else:
            print(f"\n📋 Alias not matched, error: {response.error[:100]}...")
            # Error should still be helpful
            error_lower = response.error.lower()
            assert "serum_creatinine" in error_lower or "param" in error_lower
