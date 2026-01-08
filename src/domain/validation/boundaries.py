"""
Clinical Parameter Boundaries - 臨床參數邊界規範

此模組定義醫學參數的「臨床有效邊界」，所有邊界值均有文獻佐證。
用於 MCP 輸入驗證自動防呆，並可自動生成對應文檔。

設計原則：
1. 每個邊界定義必須有文獻來源 (Reference)
2. 支援生理極限 vs 臨床常見範圍的區分
3. 可自動生成 Markdown 文檔
4. 與現有 Pydantic Field 驗證整合

Architecture:
┌─────────────────────────────────────────────────────────────┐
│                    BoundaryRegistry                         │
│  - get_boundary(param_name) -> BoundarySpec                │
│  - validate(param_name, value) -> ValidationResult         │
│  - generate_docs() -> str                                   │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                    BoundarySpec                             │
│  - param_name: str                                         │
│  - display_name: str (中英文)                               │
│  - unit: str                                                │
│  - physiological_min/max: float (生理極限)                  │
│  - clinical_min/max: float (臨床常見)                       │
│  - warning_min/max: float (警告閾值)                        │
│  - reference: BoundaryReference                            │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                  BoundaryReference                          │
│  - source: str (教科書/指引名稱)                            │
│  - citation: str (完整引用)                                 │
│  - pmid: Optional[str]                                     │
│  - year: int                                               │
│  - level_of_evidence: str (A/B/C/D)                        │
│  - notes: str (額外說明)                                    │
└─────────────────────────────────────────────────────────────┘

Author: Medical-Calc MCP Team
Date: 2026-01-08
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class EvidenceLevel(Enum):
    """證據等級 (GRADE system)"""
    A = "A"  # 高品質 - RCT, Meta-analysis
    B = "B"  # 中品質 - Observational studies
    C = "C"  # 低品質 - Case series, Expert opinion
    D = "D"  # 非常低 - Textbook, Clinical experience


class ValidationSeverity(Enum):
    """驗證結果嚴重程度"""
    PASS = "pass"           # 通過驗證
    WARNING = "warning"     # 警告 (超出臨床常見範圍但在生理可能範圍內)
    ERROR = "error"         # 錯誤 (超出生理可能範圍)
    CRITICAL = "critical"   # 嚴重錯誤 (完全不可能的值)


@dataclass(frozen=True)
class BoundaryReference:
    """
    參數邊界的文獻來源

    每個邊界定義都必須有可追溯的文獻支持。
    """
    source: str              # 來源名稱 (教科書/指引)
    citation: str            # 完整引用格式
    year: int                # 出版年份
    level_of_evidence: EvidenceLevel = EvidenceLevel.C
    pmid: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "citation": self.citation,
            "year": self.year,
            "level_of_evidence": self.level_of_evidence.value,
            "pmid": self.pmid,
            "doi": self.doi,
            "notes": self.notes,
        }


@dataclass
class BoundarySpec:
    """
    臨床參數邊界規範

    定義參數的三層邊界：
    1. physiological_min/max - 生理極限 (超出=不可能)
    2. warning_min/max - 警告閾值 (超出=需複檢)
    3. clinical_min/max - 臨床常見範圍 (供參考)

    Example:
        serum_creatinine:
        - physiological: 0.1 - 30.0 mg/dL (人體極限)
        - warning: 0.2 - 15.0 mg/dL (超出需確認)
        - clinical: 0.5 - 5.0 mg/dL (常見值)
    """
    # 識別資訊
    param_name: str               # 參數名稱 (snake_case)
    display_name: str             # 顯示名稱 (中英文)
    unit: str                     # 單位
    data_type: type = float       # 資料型態 (int, float, bool, str)

    # 生理極限 (超出=錯誤)
    physiological_min: Optional[float] = None
    physiological_max: Optional[float] = None

    # 警告閾值 (超出=警告，可能需複檢)
    warning_min: Optional[float] = None
    warning_max: Optional[float] = None

    # 臨床常見範圍 (參考用，不觸發警告)
    clinical_min: Optional[float] = None
    clinical_max: Optional[float] = None

    # 文獻來源 (必須)
    reference: Optional[BoundaryReference] = None

    # 額外資訊
    description: str = ""
    aliases: list[str] = field(default_factory=list)

    def validate(self, value: Any) -> "ValidationResult":
        """
        驗證數值是否在邊界內

        Returns:
            ValidationResult with severity and message
        """
        # None 值由其他驗證處理
        if value is None:
            return ValidationResult(
                param_name=self.param_name,
                value=value,
                severity=ValidationSeverity.PASS,
                message="Value is None (optional parameter)"
            )

        # 型態檢查
        if not isinstance(value, (int, float)):
            return ValidationResult(
                param_name=self.param_name,
                value=value,
                severity=ValidationSeverity.ERROR,
                message=f"Expected numeric type, got {type(value).__name__}"
            )

        numeric_value = float(value)

        # 檢查生理極限
        if self.physiological_min is not None and numeric_value < self.physiological_min:
            return ValidationResult(
                param_name=self.param_name,
                value=value,
                severity=ValidationSeverity.CRITICAL,
                message=f"{self.display_name} = {value} {self.unit} is below physiological minimum ({self.physiological_min} {self.unit})",
                boundary_spec=self
            )

        if self.physiological_max is not None and numeric_value > self.physiological_max:
            return ValidationResult(
                param_name=self.param_name,
                value=value,
                severity=ValidationSeverity.CRITICAL,
                message=f"{self.display_name} = {value} {self.unit} exceeds physiological maximum ({self.physiological_max} {self.unit})",
                boundary_spec=self
            )

        # 檢查警告閾值
        if self.warning_min is not None and numeric_value < self.warning_min:
            return ValidationResult(
                param_name=self.param_name,
                value=value,
                severity=ValidationSeverity.WARNING,
                message=f"{self.display_name} = {value} {self.unit} is unusually low (typical range: ≥{self.warning_min} {self.unit}). Please verify.",
                boundary_spec=self
            )

        if self.warning_max is not None and numeric_value > self.warning_max:
            return ValidationResult(
                param_name=self.param_name,
                value=value,
                severity=ValidationSeverity.WARNING,
                message=f"{self.display_name} = {value} {self.unit} is unusually high (typical range: ≤{self.warning_max} {self.unit}). Please verify.",
                boundary_spec=self
            )

        return ValidationResult(
            param_name=self.param_name,
            value=value,
            severity=ValidationSeverity.PASS,
            message="OK",
            boundary_spec=self
        )

    def to_pydantic_field_kwargs(self) -> dict[str, Any]:
        """
        生成 Pydantic Field 的 kwargs

        用於自動生成 MCP tool 的參數驗證。

        Returns:
            dict compatible with pydantic.Field()
        """
        kwargs: dict[str, Any] = {}

        if self.physiological_min is not None:
            kwargs["ge"] = self.physiological_min
        if self.physiological_max is not None:
            kwargs["le"] = self.physiological_max

        # 生成描述文字
        desc_parts = [self.display_name]
        if self.unit:
            desc_parts.append(f"| Unit: {self.unit}")
        if self.physiological_min is not None and self.physiological_max is not None:
            desc_parts.append(f"| Range: {self.physiological_min}-{self.physiological_max}")
        if self.clinical_min is not None and self.clinical_max is not None:
            desc_parts.append(f"(typical: {self.clinical_min}-{self.clinical_max})")

        kwargs["description"] = " ".join(desc_parts)

        return kwargs

    def to_markdown(self) -> str:
        """
        生成 Markdown 文檔片段

        Returns:
            Markdown formatted documentation
        """
        lines = [
            f"### {self.display_name}",
            "",
            f"**Parameter:** `{self.param_name}`",
            f"**Unit:** {self.unit}" if self.unit else "",
            "",
            "| Range Type | Min | Max |",
            "|------------|-----|-----|",
        ]

        if self.physiological_min is not None or self.physiological_max is not None:
            lines.append(
                f"| Physiological | {self.physiological_min or '-'} | {self.physiological_max or '-'} |"
            )

        if self.warning_min is not None or self.warning_max is not None:
            lines.append(
                f"| Warning | {self.warning_min or '-'} | {self.warning_max or '-'} |"
            )

        if self.clinical_min is not None or self.clinical_max is not None:
            lines.append(
                f"| Clinical (typical) | {self.clinical_min or '-'} | {self.clinical_max or '-'} |"
            )

        if self.reference:
            lines.extend([
                "",
                f"**Reference:** {self.reference.citation}",
                f"**Evidence Level:** {self.reference.level_of_evidence.value}",
            ])
            if self.reference.pmid:
                lines.append(f"**PMID:** {self.reference.pmid}")

        return "\n".join(filter(None, lines))


@dataclass
class ValidationResult:
    """驗證結果"""
    param_name: str
    value: Any
    severity: ValidationSeverity
    message: str
    boundary_spec: Optional[BoundarySpec] = None

    @property
    def is_valid(self) -> bool:
        """是否通過驗證 (PASS 或 WARNING)"""
        return self.severity in (ValidationSeverity.PASS, ValidationSeverity.WARNING)

    @property
    def is_error(self) -> bool:
        """是否為錯誤"""
        return self.severity in (ValidationSeverity.ERROR, ValidationSeverity.CRITICAL)

    def to_dict(self) -> dict[str, Any]:
        return {
            "param_name": self.param_name,
            "value": self.value,
            "severity": self.severity.value,
            "message": self.message,
            "is_valid": self.is_valid,
        }


# =============================================================================
# Reference Sources (常用文獻來源)
# =============================================================================


# Harrison's Principles of Internal Medicine
HARRISON_REFERENCE = BoundaryReference(
    source="Harrison's Principles of Internal Medicine",
    citation="Loscalzo J, et al. Harrison's Principles of Internal Medicine. 21st ed. McGraw-Hill; 2022.",
    year=2022,
    level_of_evidence=EvidenceLevel.C,
    notes="Standard internal medicine textbook"
)

# UpToDate
UPTODATE_REFERENCE = BoundaryReference(
    source="UpToDate",
    citation="UpToDate. Wolters Kluwer; 2025.",
    year=2025,
    level_of_evidence=EvidenceLevel.C,
    url="https://www.uptodate.com",
    notes="Continuously updated clinical decision support"
)

# KDIGO Guidelines
KDIGO_REFERENCE = BoundaryReference(
    source="KDIGO CKD Guideline",
    citation="Kidney Disease: Improving Global Outcomes (KDIGO) CKD Work Group. KDIGO 2024 Clinical Practice Guideline for the Evaluation and Management of CKD. Kidney Int. 2024;105(4S):S117-S314.",
    year=2024,
    level_of_evidence=EvidenceLevel.A,
    pmid="38490803",
    doi="10.1016/j.kint.2023.10.018"
)

# Sepsis-3 Definitions
SEPSIS3_REFERENCE = BoundaryReference(
    source="Sepsis-3 Definitions",
    citation="Singer M, et al. The Third International Consensus Definitions for Sepsis and Septic Shock (Sepsis-3). JAMA. 2016;315(8):801-810.",
    year=2016,
    level_of_evidence=EvidenceLevel.A,
    pmid="26903338",
    doi="10.1001/jama.2016.0287"
)

# PADIS Guidelines
PADIS_REFERENCE = BoundaryReference(
    source="PADIS Guidelines",
    citation="Devlin JW, et al. Clinical Practice Guidelines for the Prevention and Management of Pain, Agitation/Sedation, Delirium, Immobility, and Sleep Disruption in Adult Patients in the ICU. Crit Care Med. 2018;46(9):e825-e873.",
    year=2018,
    level_of_evidence=EvidenceLevel.A,
    pmid="30113379",
    doi="10.1097/CCM.0000000000003299"
)


# =============================================================================
# Clinical Parameter Boundaries (臨床參數邊界定義)
# =============================================================================


CLINICAL_BOUNDARIES: dict[str, BoundarySpec] = {
    # =========================================================================
    # Vital Signs (生命徵象)
    # =========================================================================
    "temperature": BoundarySpec(
        param_name="temperature",
        display_name="體溫 Temperature",
        unit="°C",
        data_type=float,
        physiological_min=25.0,   # 極低體溫仍可存活 (復溫後)
        physiological_max=45.0,   # >45°C 通常致命
        warning_min=32.0,         # <32°C 嚴重低體溫
        warning_max=42.0,         # >42°C 嚴重高熱
        clinical_min=36.0,        # 正常範圍
        clinical_max=38.5,
        reference=HARRISON_REFERENCE,
        description="Core body temperature"
    ),

    "heart_rate": BoundarySpec(
        param_name="heart_rate",
        display_name="心率 Heart Rate",
        unit="bpm",
        data_type=int,
        physiological_min=20,     # 嚴重心搏過緩 (需pace)
        physiological_max=300,    # VT/VF 仍可量到
        warning_min=40,           # 需要評估
        warning_max=180,          # 可能血流動力學不穩
        clinical_min=60,          # 正常範圍
        clinical_max=100,
        reference=HARRISON_REFERENCE,
        description="Heart rate in beats per minute",
        aliases=["hr", "pulse"]
    ),

    "respiratory_rate": BoundarySpec(
        param_name="respiratory_rate",
        display_name="呼吸速率 Respiratory Rate",
        unit="breaths/min",
        data_type=int,
        physiological_min=0,      # 呼吸停止
        physiological_max=70,     # 嚴重呼吸窘迫
        warning_min=8,            # 呼吸抑制
        warning_max=40,           # 呼吸窘迫
        clinical_min=12,          # 正常範圍
        clinical_max=20,
        reference=HARRISON_REFERENCE,
        description="Respiratory rate",
        aliases=["rr"]
    ),

    "systolic_bp": BoundarySpec(
        param_name="systolic_bp",
        display_name="收縮壓 Systolic BP",
        unit="mmHg",
        data_type=int,
        physiological_min=30,     # 嚴重休克 (CPR中可能測到)
        physiological_max=300,    # 高血壓急症
        warning_min=70,           # 低血壓
        warning_max=200,          # 高血壓
        clinical_min=90,          # 正常範圍
        clinical_max=140,
        reference=HARRISON_REFERENCE,
        description="Systolic blood pressure",
        aliases=["sbp"]
    ),

    "mean_arterial_pressure": BoundarySpec(
        param_name="mean_arterial_pressure",
        display_name="平均動脈壓 MAP",
        unit="mmHg",
        data_type=float,
        physiological_min=20,     # 嚴重休克
        physiological_max=200,    # 高血壓急症
        warning_min=55,           # 器官灌流不足
        warning_max=150,          # 高血壓
        clinical_min=65,          # Sepsis target
        clinical_max=100,
        reference=SEPSIS3_REFERENCE,
        description="Mean arterial pressure",
        aliases=["map"]
    ),

    "spo2": BoundarySpec(
        param_name="spo2",
        display_name="血氧飽和度 SpO2",
        unit="%",
        data_type=int,
        physiological_min=40,     # 最低可量測
        physiological_max=100,    # 最高 100%
        warning_min=88,           # 低血氧
        warning_max=100,          # 正常
        clinical_min=94,          # 一般目標
        clinical_max=100,
        reference=HARRISON_REFERENCE,
        description="Peripheral oxygen saturation"
    ),

    # =========================================================================
    # Laboratory Values - Renal (腎功能)
    # =========================================================================
    "serum_creatinine": BoundarySpec(
        param_name="serum_creatinine",
        display_name="血清肌酐 Creatinine",
        unit="mg/dL",
        data_type=float,
        physiological_min=0.1,    # 極低 (可能是稀釋)
        physiological_max=30.0,   # ESRD 可達此值
        warning_min=0.3,          # 極低需確認
        warning_max=15.0,         # 非常高
        clinical_min=0.6,         # 正常範圍
        clinical_max=1.3,
        reference=KDIGO_REFERENCE,
        description="Serum creatinine",
        aliases=["creatinine", "cr", "scr"]
    ),

    "bun": BoundarySpec(
        param_name="bun",
        display_name="血尿素氮 BUN",
        unit="mg/dL",
        data_type=float,
        physiological_min=1,      # 極低
        physiological_max=200,    # ESRD
        warning_min=5,            # 低
        warning_max=100,          # 高
        clinical_min=7,           # 正常範圍
        clinical_max=20,
        reference=HARRISON_REFERENCE,
        description="Blood urea nitrogen"
    ),

    # =========================================================================
    # Laboratory Values - Hematology (血液學)
    # =========================================================================
    "hemoglobin": BoundarySpec(
        param_name="hemoglobin",
        display_name="血紅素 Hemoglobin",
        unit="g/dL",
        data_type=float,
        physiological_min=2.0,    # 嚴重貧血 (仍可存活)
        physiological_max=25.0,   # 紅血球增多症
        warning_min=6.0,          # 嚴重貧血
        warning_max=20.0,         # 高
        clinical_min=12.0,        # 正常範圍 (女)
        clinical_max=17.5,        # 正常範圍 (男)
        reference=HARRISON_REFERENCE,
        description="Hemoglobin concentration",
        aliases=["hgb", "hb"]
    ),

    "hematocrit": BoundarySpec(
        param_name="hematocrit",
        display_name="血球容積比 Hematocrit",
        unit="%",
        data_type=float,
        physiological_min=10,     # 嚴重貧血
        physiological_max=70,     # 紅血球增多症
        warning_min=20,           # 嚴重貧血
        warning_max=60,           # 高
        clinical_min=36,          # 正常範圍 (女)
        clinical_max=52,          # 正常範圍 (男)
        reference=HARRISON_REFERENCE,
        description="Hematocrit",
        aliases=["hct"]
    ),

    "platelets": BoundarySpec(
        param_name="platelets",
        display_name="血小板 Platelets",
        unit="×10³/µL",
        data_type=float,
        physiological_min=0,      # 可能是 ITP
        physiological_max=2000,   # 血小板增多症
        warning_min=20,           # 嚴重血小板低下
        warning_max=1000,         # 血小板增多
        clinical_min=150,         # 正常範圍
        clinical_max=400,
        reference=HARRISON_REFERENCE,
        description="Platelet count",
        aliases=["plt"]
    ),

    # =========================================================================
    # Laboratory Values - Liver (肝功能)
    # =========================================================================
    "bilirubin": BoundarySpec(
        param_name="bilirubin",
        display_name="總膽紅素 Bilirubin",
        unit="mg/dL",
        data_type=float,
        physiological_min=0,
        physiological_max=60,     # 嚴重肝衰竭
        warning_min=0,
        warning_max=20,           # 非常高
        clinical_min=0.1,         # 正常範圍
        clinical_max=1.2,
        reference=HARRISON_REFERENCE,
        description="Total bilirubin"
    ),

    # =========================================================================
    # Demographics (人口學)
    # =========================================================================
    "age": BoundarySpec(
        param_name="age",
        display_name="年齡 Age",
        unit="years",
        data_type=int,
        physiological_min=0,      # 新生兒
        physiological_max=120,    # 最高齡
        warning_min=0,
        warning_max=120,
        clinical_min=18,          # 成人
        clinical_max=100,
        reference=HARRISON_REFERENCE,
        description="Patient age in years"
    ),

    "weight_kg": BoundarySpec(
        param_name="weight_kg",
        display_name="體重 Weight",
        unit="kg",
        data_type=float,
        physiological_min=0.5,    # 極早產兒
        physiological_max=500,    # 病態肥胖
        warning_min=2.0,          # 新生兒
        warning_max=300,          # 肥胖
        clinical_min=40,          # 成人正常
        clinical_max=120,
        reference=HARRISON_REFERENCE,
        description="Body weight in kilograms",
        aliases=["weight", "wt"]
    ),

    # =========================================================================
    # Oxygenation (氧合)
    # =========================================================================
    "fio2": BoundarySpec(
        param_name="fio2",
        display_name="吸入氧濃度 FiO2",
        unit="",
        data_type=float,
        physiological_min=0.21,   # Room air
        physiological_max=1.0,    # 100% O2
        warning_min=0.21,
        warning_max=1.0,
        clinical_min=0.21,
        clinical_max=0.6,         # 避免氧毒性
        reference=HARRISON_REFERENCE,
        description="Fraction of inspired oxygen (0.21-1.0)"
    ),

    "pao2_fio2_ratio": BoundarySpec(
        param_name="pao2_fio2_ratio",
        display_name="PaO2/FiO2 比值",
        unit="mmHg",
        data_type=float,
        physiological_min=20,     # 嚴重 ARDS
        physiological_max=700,    # 最高 (100% O2 時)
        warning_min=60,           # 嚴重低血氧
        warning_max=500,
        clinical_min=300,         # 輕度 ARDS 閾值
        clinical_max=500,         # 正常
        reference=SEPSIS3_REFERENCE,
        description="PaO2/FiO2 ratio (P/F ratio)"
    ),

    # =========================================================================
    # Scores (評分)
    # =========================================================================
    "gcs_score": BoundarySpec(
        param_name="gcs_score",
        display_name="GCS 昏迷指數",
        unit="",
        data_type=int,
        physiological_min=3,      # 最低 (E1V1M1)
        physiological_max=15,     # 最高 (E4V5M6)
        warning_min=3,
        warning_max=15,
        clinical_min=3,
        clinical_max=15,
        reference=HARRISON_REFERENCE,
        description="Glasgow Coma Scale (3-15)"
    ),

    "rass_score": BoundarySpec(
        param_name="rass_score",
        display_name="RASS 鎮靜評估",
        unit="",
        data_type=int,
        physiological_min=-5,     # 無法喚醒
        physiological_max=4,      # 具攻擊性
        warning_min=-5,
        warning_max=4,
        clinical_min=-2,          # 目標範圍
        clinical_max=0,
        reference=PADIS_REFERENCE,
        description="Richmond Agitation-Sedation Scale (-5 to +4)"
    ),
}


# =============================================================================
# BoundaryRegistry (邊界註冊表)
# =============================================================================


class BoundaryRegistry:
    """
    臨床參數邊界註冊表

    用於統一管理所有參數的邊界定義，並提供驗證功能。
    """

    _instance: Optional["BoundaryRegistry"] = None

    def __init__(self) -> None:
        self._boundaries: dict[str, BoundarySpec] = {}
        self._alias_map: dict[str, str] = {}  # alias -> canonical name

    @classmethod
    def instance(cls) -> "BoundaryRegistry":
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = BoundaryRegistry()
            cls._instance._load_default_boundaries()
        return cls._instance

    def _load_default_boundaries(self) -> None:
        """Load default clinical boundaries"""
        for name, spec in CLINICAL_BOUNDARIES.items():
            self.register(spec)

    def register(self, spec: BoundarySpec) -> None:
        """Register a boundary specification"""
        self._boundaries[spec.param_name] = spec

        # Register aliases
        for alias in spec.aliases:
            self._alias_map[alias.lower()] = spec.param_name

    def get_boundary(self, param_name: str) -> Optional[BoundarySpec]:
        """Get boundary spec by parameter name or alias"""
        # Try direct lookup
        if param_name in self._boundaries:
            return self._boundaries[param_name]

        # Try alias lookup
        canonical = self._alias_map.get(param_name.lower())
        if canonical:
            return self._boundaries.get(canonical)

        return None

    def validate(self, param_name: str, value: Any) -> ValidationResult:
        """
        Validate a parameter value against its boundary

        Returns:
            ValidationResult (PASS if no boundary defined)
        """
        spec = self.get_boundary(param_name)

        if spec is None:
            return ValidationResult(
                param_name=param_name,
                value=value,
                severity=ValidationSeverity.PASS,
                message=f"No boundary defined for '{param_name}'"
            )

        return spec.validate(value)

    def validate_all(
        self,
        params: dict[str, Any],
        fail_fast: bool = False
    ) -> list[ValidationResult]:
        """
        Validate multiple parameters

        Args:
            params: Dictionary of param_name -> value
            fail_fast: Stop on first error

        Returns:
            List of ValidationResult
        """
        results = []

        for name, value in params.items():
            result = self.validate(name, value)
            results.append(result)

            if fail_fast and result.is_error:
                break

        return results

    def get_all_boundaries(self) -> list[BoundarySpec]:
        """Get all registered boundary specifications"""
        return list(self._boundaries.values())

    def generate_markdown_docs(self) -> str:
        """
        Generate complete Markdown documentation for all boundaries

        Returns:
            Markdown formatted documentation
        """
        lines = [
            "# Clinical Parameter Boundaries",
            "",
            "This document defines the validated boundaries for all clinical parameters.",
            "Each boundary is backed by peer-reviewed references.",
            "",
            "---",
            "",
        ]

        # Group by category (inferred from param_name)
        categories: dict[str, list[BoundarySpec]] = {
            "Vital Signs": [],
            "Renal Function": [],
            "Hematology": [],
            "Liver Function": [],
            "Demographics": [],
            "Oxygenation": [],
            "Scores": [],
            "Other": [],
        }

        for spec in self._boundaries.values():
            if spec.param_name in ["temperature", "heart_rate", "respiratory_rate", "systolic_bp", "mean_arterial_pressure", "spo2"]:
                categories["Vital Signs"].append(spec)
            elif spec.param_name in ["serum_creatinine", "bun"]:
                categories["Renal Function"].append(spec)
            elif spec.param_name in ["hemoglobin", "hematocrit", "platelets"]:
                categories["Hematology"].append(spec)
            elif spec.param_name in ["bilirubin"]:
                categories["Liver Function"].append(spec)
            elif spec.param_name in ["age", "weight_kg"]:
                categories["Demographics"].append(spec)
            elif spec.param_name in ["fio2", "pao2_fio2_ratio"]:
                categories["Oxygenation"].append(spec)
            elif spec.param_name in ["gcs_score", "rass_score"]:
                categories["Scores"].append(spec)
            else:
                categories["Other"].append(spec)

        for category, specs in categories.items():
            if specs:
                lines.append(f"## {category}")
                lines.append("")
                for spec in specs:
                    lines.append(spec.to_markdown())
                    lines.append("")
                    lines.append("---")
                    lines.append("")

        return "\n".join(lines)


# =============================================================================
# Convenience Functions
# =============================================================================


def get_boundary_registry() -> BoundaryRegistry:
    """Get the global boundary registry instance"""
    return BoundaryRegistry.instance()


def validate_param(param_name: str, value: Any) -> ValidationResult:
    """Convenience function to validate a single parameter"""
    return get_boundary_registry().validate(param_name, value)


def get_boundary(param_name: str) -> Optional[BoundarySpec]:
    """Convenience function to get a boundary specification"""
    return get_boundary_registry().get_boundary(param_name)
