"""
P/F Ratio Calculator

Calculates the PaO2/FiO2 ratio for ARDS severity classification per Berlin Definition.

Reference:
    ARDS Definition Task Force. Acute respiratory distress syndrome: 
    the Berlin Definition. JAMA. 2012;307(23):2526-2533.
    DOI: 10.1001/jama.2012.5669
    PMID: 22797452
    
    Ranieri VM, Rubenfeld GD, Thompson BT, et al. Acute respiratory distress 
    syndrome: the Berlin Definition. JAMA. 2012;307(23):2526-2533.
    DOI: 10.1001/jama.2012.5669
    PMID: 22797452
"""

from typing import Optional

from ..base import BaseCalculator
from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.units import Unit
from ...value_objects.reference import Reference
from ...value_objects.interpretation import Interpretation, Severity, RiskLevel
from ...value_objects.tool_keys import (
    LowLevelKey,
    HighLevelKey,
    Specialty,
    ClinicalContext,
)


class PfRatioCalculator(BaseCalculator):
    """
    P/F Ratio (PaO2/FiO2) Calculator
    
    The P/F ratio is the primary measure for classifying ARDS severity
    according to the Berlin Definition (2012).
    
    Formula:
        P/F Ratio = PaO2 (mmHg) / FiO2 (decimal)
        
    Berlin Definition ARDS Classification (with PEEP ≥5 cmH2O):
        - Mild ARDS: 200 < P/F ≤ 300 mmHg
        - Moderate ARDS: 100 < P/F ≤ 200 mmHg
        - Severe ARDS: P/F ≤ 100 mmHg
        
    Mortality by ARDS Severity:
        - Mild: 27%
        - Moderate: 32%
        - Severe: 45%
        
    Notes:
        - Requires PEEP or CPAP ≥5 cmH2O for ARDS diagnosis
        - Must have bilateral opacities on imaging
        - Not fully explained by cardiac failure or fluid overload
        - Acute onset (within 1 week of known insult)
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="pf_ratio",
                name="P/F Ratio (PaO2/FiO2)",
                purpose="Calculate P/F ratio for ARDS severity classification",
                input_params=["pao2", "fio2", "peep"],
                output_type="P/F ratio with Berlin Definition ARDS staging"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.CRITICAL_CARE,
                    Specialty.PULMONOLOGY,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.ANESTHESIOLOGY,
                ),
                conditions=(
                    "ARDS",
                    "Acute respiratory distress syndrome",
                    "Respiratory failure",
                    "Hypoxemia",
                    "Pneumonia",
                    "COVID-19",
                    "Sepsis",
                ),
                clinical_contexts=(
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "Does this patient have ARDS?",
                    "What is the severity of ARDS?",
                    "What is the P/F ratio?",
                    "How severe is the hypoxemia?",
                ),
                icd10_codes=("J80", "J96.0", "J96.9"),
                keywords=(
                    "P/F ratio", "PaO2/FiO2", "ARDS", "Berlin definition",
                    "oxygenation", "hypoxemia", "respiratory failure",
                    "acute lung injury", "ALI",
                ),
            ),
            references=self._get_references(),
        )
    
    def _get_references(self) -> tuple[Reference, ...]:
        return (
            Reference(
                citation="ARDS Definition Task Force. Acute respiratory distress syndrome: the Berlin Definition. JAMA. 2012;307(23):2526-2533.",
                doi="10.1001/jama.2012.5669",
                pmid="22797452",
                year=2012,
            ),
        )
    
    def calculate(
        self,
        pao2: float,
        fio2: float,
        peep: float = None,
        on_mechanical_ventilation: bool = True,
    ) -> ScoreResult:
        """
        Calculate P/F ratio.
        
        Args:
            pao2: Arterial oxygen partial pressure (mmHg)
            fio2: Fraction of inspired oxygen (0.21-1.0 or 21-100%)
            peep: Positive end-expiratory pressure (cmH2O), for ARDS classification
            on_mechanical_ventilation: Whether patient is mechanically ventilated
            
        Returns:
            ScoreResult with P/F ratio and ARDS classification
        """
        # Validate inputs
        if pao2 < 20 or pao2 > 700:
            raise ValueError(f"PaO2 {pao2} mmHg is outside expected range (20-700 mmHg)")
        
        # Handle FiO2 as percentage if > 1
        if fio2 > 1:
            fio2 = fio2 / 100
        
        if fio2 < 0.21 or fio2 > 1.0:
            raise ValueError(f"FiO2 {fio2} is outside expected range (0.21-1.0)")
        
        if peep is not None and (peep < 0 or peep > 40):
            raise ValueError(f"PEEP {peep} cmH2O is outside expected range (0-40 cmH2O)")
        
        # Calculate P/F ratio
        pf_ratio = pao2 / fio2
        pf_ratio = round(pf_ratio, 1)
        
        # Check PEEP requirement for ARDS classification
        peep_adequate = peep is not None and peep >= 5
        
        # Generate interpretation
        interpretation = self._interpret_pf_ratio(
            pf_ratio, peep, peep_adequate, on_mechanical_ventilation
        )
        
        # Build calculation details
        details = {
            "PaO2": f"{pao2} mmHg",
            "FiO2": f"{fio2:.0%}" if fio2 <= 1 else f"{fio2}%",
            "P/F_ratio": f"{pf_ratio} mmHg",
        }
        
        if peep is not None:
            details["PEEP"] = f"{peep} cmH2O"
            details["PEEP_adequate_for_ARDS"] = "Yes" if peep_adequate else "No (requires ≥5 cmH2O)"
        
        if on_mechanical_ventilation:
            details["Ventilation"] = "Mechanical ventilation"
        
        return ScoreResult(
            value=pf_ratio,
            unit=Unit.MMHG,
            interpretation=interpretation,
            references=self._get_references(),
            tool_id=self.tool_id,
            tool_name=self.metadata.name,
            raw_inputs={
                "pao2": pao2,
                "fio2": fio2,
                "peep": peep,
                "on_mechanical_ventilation": on_mechanical_ventilation,
            },
            calculation_details=details,
            formula_used="P/F Ratio = PaO2 / FiO2",
        )
    
    def _interpret_pf_ratio(
        self,
        pf_ratio: float,
        peep: float,
        peep_adequate: bool,
        on_mv: bool,
    ) -> Interpretation:
        """Generate interpretation based on Berlin Definition."""
        
        # Classify ARDS severity
        if pf_ratio <= 100:
            ards_class = "Severe ARDS"
            mortality = "45%"
            severity = Severity.CRITICAL
            risk_level = RiskLevel.VERY_HIGH
        elif pf_ratio <= 200:
            ards_class = "Moderate ARDS"
            mortality = "32%"
            severity = Severity.SEVERE
            risk_level = RiskLevel.HIGH
        elif pf_ratio <= 300:
            ards_class = "Mild ARDS"
            mortality = "27%"
            severity = Severity.MODERATE
            risk_level = RiskLevel.INTERMEDIATE
        elif pf_ratio <= 400:
            ards_class = "Hypoxemia (not ARDS)"
            mortality = "N/A"
            severity = Severity.MILD
            risk_level = RiskLevel.LOW
        else:
            ards_class = "Normal oxygenation"
            mortality = "N/A"
            severity = Severity.NORMAL
            risk_level = RiskLevel.LOW
        
        # Check if ARDS criteria met
        can_diagnose_ards = peep_adequate and pf_ratio <= 300
        
        if pf_ratio <= 300:
            if peep_adequate:
                summary = f"P/F Ratio {pf_ratio}: {ards_class} (Berlin Definition)"
                detail = f"With PEEP ≥5 cmH2O, this P/F ratio meets Berlin Definition criteria for {ards_class}. Expected mortality: {mortality}."
            else:
                summary = f"P/F Ratio {pf_ratio}: Consistent with {ards_class} (PEEP data needed)"
                detail = f"P/F ratio suggests {ards_class}, but ARDS diagnosis requires PEEP ≥5 cmH2O. Provide PEEP to confirm classification."
        else:
            summary = f"P/F Ratio {pf_ratio}: {ards_class}"
            detail = f"P/F ratio >{300 if pf_ratio > 300 else 400} does not meet ARDS criteria by Berlin Definition."
        
        recommendations = []
        if pf_ratio <= 100:
            recommendations = [
                "Consider prone positioning (≥16 hours/day)",
                "Lung protective ventilation: 6 mL/kg IBW tidal volume",
                "Target plateau pressure <30 cmH2O",
                "Consider neuromuscular blockade for first 48 hours",
                "ECMO may be considered if refractory",
            ]
        elif pf_ratio <= 200:
            recommendations = [
                "Lung protective ventilation: 6-8 mL/kg IBW",
                "Target plateau pressure <30 cmH2O",
                "Consider prone positioning",
                "Conservative fluid management",
            ]
        elif pf_ratio <= 300:
            recommendations = [
                "Lung protective ventilation: 6-8 mL/kg IBW",
                "Monitor for progression",
                "Treat underlying cause",
            ]
        else:
            recommendations = [
                "Continue monitoring oxygenation",
                "Investigate cause of any hypoxemia",
            ]
        
        warnings = []
        if not peep_adequate and pf_ratio <= 300:
            warnings.append("⚠️ ARDS requires PEEP ≥5 cmH2O for formal diagnosis")
        if pf_ratio <= 100:
            warnings.append("⚠️ Severe ARDS - high mortality risk, consider advanced therapies")
        
        return Interpretation(
            summary=summary,
            detail=detail,
            severity=severity,
            risk_level=risk_level,
            stage=ards_class if pf_ratio <= 300 else None,
            recommendations=tuple(recommendations),
            warnings=tuple(warnings),
            next_steps=(
                "Confirm bilateral opacities on chest imaging",
                "Rule out cardiogenic pulmonary edema",
                "Document acute onset (within 1 week)",
                "Apply lung protective ventilation strategy",
            ),
        )
