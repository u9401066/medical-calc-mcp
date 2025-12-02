"""
Corrected QT Interval (QTc) Calculator

Calculates the heart-rate corrected QT interval using multiple formulas.
Essential for drug safety monitoring and arrhythmia risk assessment.

References:
    Bazett HC. An analysis of the time-relations of electrocardiograms.
    Heart. 1920;7:353-370.
    
    Fridericia LS. Die Systolendauer im Elektrokardiogramm bei normalen 
    Menschen und bei Herzkranken. Acta Med Scand. 1920;53:469-486.
    
    Framingham Study formula:
    Sagie A, et al. An improved method for adjusting the QT interval for 
    heart rate. Am J Cardiol. 1992;70(7):797-801.
    DOI: 10.1016/0002-9149(92)90562-d
    PMID: 1519533
    
    ESC Guidelines 2015:
    Priori SG, et al. 2015 ESC Guidelines for the management of patients 
    with ventricular arrhythmias and the prevention of sudden cardiac death.
    Eur Heart J. 2015;36(41):2793-2867.
    DOI: 10.1093/eurheartj/ehv316
    PMID: 26320108
"""

import math
from typing import Literal

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


class CorrectedQtCalculator(BaseCalculator):
    """
    Corrected QT Interval (QTc) Calculator
    
    The QT interval represents ventricular depolarization and repolarization.
    QT prolongation increases the risk of Torsades de Pointes (TdP) and
    sudden cardiac death.
    
    Formulas:
        Bazett (most common):
            QTc = QT / √RR
            
        Fridericia (preferred for tachycardia/bradycardia):
            QTc = QT / ∛RR
            
        Framingham (linear correction):
            QTc = QT + 0.154 × (1 - RR)
            
        Where RR = 60 / HR (in seconds)
        
    Normal Values:
        Males: ≤450 ms
        Females: ≤460 ms
        
    Prolonged QTc:
        Borderline: 450-470 ms (males), 460-480 ms (females)
        Prolonged: >470 ms (males), >480 ms (females)
        Markedly prolonged: >500 ms (high risk for TdP)
        
    Common QT-Prolonging Drugs:
        - Antiarrhythmics: amiodarone, sotalol, dofetilide, quinidine
        - Antibiotics: fluoroquinolones, macrolides, azole antifungals
        - Antipsychotics: haloperidol, droperidol, ziprasidone
        - Antiemetics: ondansetron (high dose), droperidol
        - Others: methadone, TCAs, citalopram/escitalopram
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="corrected_qt",
                name="Corrected QT Interval (QTc)",
                purpose="Calculate heart-rate corrected QT interval for arrhythmia risk",
                input_params=["qt_interval", "heart_rate", "sex", "formula"],
                output_type="QTc (ms) with risk assessment"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.CARDIOLOGY,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.CRITICAL_CARE,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.ANESTHESIOLOGY,
                ),
                conditions=(
                    "QT prolongation",
                    "Long QT syndrome",
                    "Torsades de Pointes",
                    "TdP",
                    "Drug-induced arrhythmia",
                    "Ventricular arrhythmia",
                    "Sudden cardiac death risk",
                    "Electrolyte abnormalities",
                ),
                clinical_contexts=(
                    ClinicalContext.MONITORING,
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.DRUG_DOSING,
                ),
                clinical_questions=(
                    "Is this patient's QT interval prolonged?",
                    "Is it safe to start this QT-prolonging drug?",
                    "What is the risk of Torsades de Pointes?",
                    "Does the patient have drug-induced QT prolongation?",
                    "Should I discontinue this medication due to QT prolongation?",
                ),
                icd10_codes=("I45.81", "R94.31", "I49.9"),
                keywords=(
                    "QTc", "QT interval", "corrected QT", "Bazett", "Fridericia",
                    "QT prolongation", "Torsades", "TdP", "arrhythmia", "ECG",
                ),
            ),
            references=self._get_references(),
        )
    
    def _get_references(self) -> tuple[Reference, ...]:
        return (
            Reference(
                citation="Bazett HC. An analysis of the time-relations of electrocardiograms. Heart. 1920;7:353-370.",
                doi=None,
                pmid=None,
                year=1920,
            ),
            Reference(
                citation="Fridericia LS. Die Systolendauer im Elektrokardiogramm bei normalen Menschen und bei Herzkranken. Acta Med Scand. 1920;53:469-486.",
                doi=None,
                pmid=None,
                year=1920,
            ),
            Reference(
                citation="Priori SG, Blomström-Lundqvist C, Mazzanti A, et al. 2015 ESC Guidelines for the management of patients with ventricular arrhythmias and the prevention of sudden cardiac death. Eur Heart J. 2015;36(41):2793-2867.",
                doi="10.1093/eurheartj/ehv316",
                pmid="26320108",
                year=2015,
            ),
        )
    
    def calculate(
        self,
        qt_interval: float,
        heart_rate: float,
        sex: Literal["male", "female"] = "male",
        formula: Literal["bazett", "fridericia", "framingham"] = "bazett",
    ) -> ScoreResult:
        """
        Calculate corrected QT interval.
        
        Args:
            qt_interval: Measured QT interval in milliseconds (ms)
            heart_rate: Heart rate in beats per minute (bpm)
            sex: Patient sex ('male' or 'female')
            formula: Correction formula ('bazett', 'fridericia', 'framingham')
            
        Returns:
            ScoreResult with QTc value and risk interpretation
        """
        # Validate inputs
        if qt_interval < 200 or qt_interval > 800:
            raise ValueError(f"QT interval {qt_interval} ms is outside physiological range (200-800 ms)")
        if heart_rate < 30 or heart_rate > 250:
            raise ValueError(f"Heart rate {heart_rate} bpm is outside physiological range (30-250 bpm)")
        
        # Calculate RR interval in seconds
        rr_interval = 60 / heart_rate
        
        # Calculate QTc based on formula
        if formula == "bazett":
            qtc = qt_interval / math.sqrt(rr_interval)
            formula_used = "QTc = QT / √RR (Bazett)"
        elif formula == "fridericia":
            qtc = qt_interval / (rr_interval ** (1/3))
            formula_used = "QTc = QT / ∛RR (Fridericia)"
        elif formula == "framingham":
            qtc = qt_interval + 154 * (1 - rr_interval)
            formula_used = "QTc = QT + 154 × (1 - RR) (Framingham)"
        else:
            raise ValueError(f"Unknown formula: {formula}")
        
        qtc = round(qtc, 0)
        
        # Determine risk category based on sex
        interpretation = self._interpret_qtc(qtc, sex)
        
        # Build calculation details
        details = {
            "QT_measured": f"{qt_interval} ms",
            "Heart_rate": f"{heart_rate} bpm",
            "RR_interval": f"{rr_interval:.3f} s",
            "Formula": formula.capitalize(),
            "QTc": f"{qtc:.0f} ms",
            "Sex": sex.capitalize(),
        }
        
        return ScoreResult(
            value=qtc,
            unit=Unit.MS,
            interpretation=interpretation,
            references=self._get_references(),
            tool_id=self.tool_id,
            tool_name=self.metadata.name,
            raw_inputs={
                "qt_interval": qt_interval,
                "heart_rate": heart_rate,
                "sex": sex,
                "formula": formula,
            },
            calculation_details=details,
            formula_used=formula_used,
        )
    
    def _interpret_qtc(self, qtc: float, sex: str) -> Interpretation:
        """Generate interpretation based on QTc value and sex."""
        
        # Define thresholds based on sex
        if sex == "male":
            normal_upper = 450
            borderline_upper = 470
        else:  # female
            normal_upper = 460
            borderline_upper = 480
        
        # Determine severity and risk
        if qtc <= normal_upper:
            severity = Severity.NORMAL
            risk_level = RiskLevel.VERY_LOW
            summary = f"Normal QTc ({qtc:.0f} ms)"
            detail = f"QTc is within normal limits for {sex}s (≤{normal_upper} ms)."
            recommendations = (
                "No QT-related drug restrictions",
                "Continue current medications if clinically indicated",
                "Standard ECG monitoring as needed",
            )
            warnings = ()
        elif qtc <= borderline_upper:
            severity = Severity.MILD
            risk_level = RiskLevel.LOW
            summary = f"Borderline prolonged QTc ({qtc:.0f} ms)"
            detail = f"QTc is borderline prolonged for {sex}s ({normal_upper}-{borderline_upper} ms). Low risk of TdP but warrants attention."
            recommendations = (
                "Review medications for QT-prolonging drugs",
                "Check and correct electrolytes (K⁺, Mg²⁺, Ca²⁺)",
                "Avoid adding additional QT-prolonging agents",
                "Consider ECG monitoring if starting new medications",
            )
            warnings = (
                "Borderline QT prolongation - use caution with QT-prolonging drugs",
            )
        elif qtc <= 500:
            severity = Severity.MODERATE
            risk_level = RiskLevel.INTERMEDIATE
            summary = f"Prolonged QTc ({qtc:.0f} ms)"
            detail = f"QTc is prolonged (>{borderline_upper} ms). Increased risk of Torsades de Pointes."
            recommendations = (
                "Review and discontinue non-essential QT-prolonging drugs",
                "Urgently correct electrolyte abnormalities",
                "Continuous ECG monitoring recommended",
                "Consider cardiology consultation",
                "Avoid additional QT-prolonging agents",
            )
            warnings = (
                "Prolonged QT - increased risk of Torsades de Pointes",
                "Review all medications for QT effects",
            )
        else:  # > 500 ms
            severity = Severity.SEVERE
            risk_level = RiskLevel.HIGH
            summary = f"Markedly prolonged QTc ({qtc:.0f} ms) - HIGH RISK"
            detail = "QTc >500 ms is associated with significantly increased risk of Torsades de Pointes and sudden cardiac death."
            recommendations = (
                "STOP all QT-prolonging medications immediately",
                "Continuous telemetry monitoring",
                "Aggressive electrolyte repletion (K⁺ >4.0, Mg²⁺ >2.0)",
                "Urgent cardiology consultation",
                "Have defibrillator available",
                "Consider IV magnesium prophylaxis",
            )
            warnings = (
                "⚠️ CRITICAL: QTc >500 ms - high risk of fatal arrhythmia",
                "Immediate intervention required",
            )
        
        return Interpretation(
            summary=summary,
            detail=detail,
            severity=severity,
            risk_level=risk_level,
            recommendations=recommendations,
            warnings=warnings,
            next_steps=(
                "Monitor ECG after any medication changes",
                "Repeat ECG if electrolytes corrected",
                "Check family history of sudden death or Long QT syndrome",
            ),
        )
