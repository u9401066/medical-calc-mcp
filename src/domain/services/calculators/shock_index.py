"""
Shock Index Calculator

Calculates the ratio of heart rate to systolic blood pressure.
A simple bedside tool for rapid hemodynamic assessment in emergency settings.

References:
    Allgöwer M, Burri C. Schockindex. Dtsch Med Wochenschr. 1967;92(43):1947-1950.
    DOI: 10.1055/s-0028-1106070
    PMID: 5592563
    
    Birkhahn RH, Gaeta TJ, Terry D, Bove JJ, Tloczkowski J. Shock index in 
    diagnosing early acute hypovolemia. Am J Emerg Med. 2005;23(3):323-326.
    DOI: 10.1016/j.ajem.2005.02.029
    PMID: 15915406
    
    Rady MY, Nightingale P, Little RA, Edwards JD. Shock index: a re-evaluation 
    in acute circulatory failure. Resuscitation. 1992;23(3):227-234.
    DOI: 10.1016/0300-9572(92)90006-x
    PMID: 1321482
    
    Cannon CM, Braxton CC, Kling-Smith M, et al. Utility of the shock index in 
    predicting mortality in traumatically injured patients. J Trauma. 
    2009;67(6):1426-1430.
    DOI: 10.1097/TA.0b013e3181bbf728
    PMID: 20009697
"""

from typing import Optional, Literal

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


class ShockIndexCalculator(BaseCalculator):
    """
    Shock Index (SI) Calculator
    
    The Shock Index is a simple ratio of heart rate to systolic blood pressure
    that provides a rapid assessment of hemodynamic status.
    
    Formula:
        SI = Heart Rate (bpm) / Systolic BP (mmHg)
        
    Normal Range:
        0.5 - 0.7
        
    Interpretation:
        < 0.6: Normal, hemodynamically stable
        0.6 - 0.9: Normal to borderline
        1.0: Upper limit of normal (HR = SBP)
        > 1.0: Elevated - suggests hemodynamic instability
        > 1.4: Severely elevated - high mortality risk
        
    Modified Shock Index (MSI):
        MSI = Heart Rate / Mean Arterial Pressure (MAP)
        Normal: 0.7 - 1.3
        
    Age-adjusted Shock Index (in pediatrics):
        Varies by age group
        
    Clinical Applications:
        - Trauma triage
        - Early detection of occult hemorrhage
        - Prediction of massive transfusion need
        - Assessment of hypovolemic shock
        - Emergency department risk stratification
        - Obstetric hemorrhage assessment
        
    Advantages:
        - Quick bedside calculation
        - No equipment needed beyond vital signs
        - Detects compensated shock before BP drops
        - Predicts mortality better than HR or BP alone
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="shock_index",
                name="Shock Index (SI)",
                purpose="Calculate HR/SBP ratio for rapid hemodynamic assessment",
                input_params=["heart_rate", "systolic_bp", "diastolic_bp", "patient_type"],
                output_type="Shock Index with hemodynamic interpretation"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.SURGERY,
                    Specialty.CRITICAL_CARE,
                    Specialty.OBSTETRICS,
                ),
                conditions=(
                    "Shock",
                    "Hypovolemia",
                    "Hemorrhage",
                    "Trauma",
                    "Sepsis",
                    "Hemodynamic instability",
                    "Postpartum hemorrhage",
                    "Gastrointestinal bleeding",
                    "Ruptured AAA",
                    "Ectopic pregnancy",
                ),
                clinical_contexts=(
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "Is this patient in early shock?",
                    "Does this trauma patient need massive transfusion?",
                    "Is there occult hemorrhage?",
                    "How unstable is this patient hemodynamically?",
                    "Should I activate the trauma team?",
                    "Is this postpartum hemorrhage significant?",
                ),
                icd10_codes=("R57.9", "R57.1", "T79.4", "R58"),
                keywords=(
                    "shock index", "SI", "hemodynamic", "triage", "trauma",
                    "hemorrhage", "hypovolemia", "massive transfusion", "shock",
                    "vital signs", "heart rate", "blood pressure", "instability",
                ),
            ),
            references=self._get_references(),
        )
    
    def _get_references(self) -> tuple[Reference, ...]:
        return (
            Reference(
                citation="Allgöwer M, Burri C. Schockindex. Dtsch Med Wochenschr. 1967;92(43):1947-1950.",
                doi="10.1055/s-0028-1106070",
                pmid="5592563",
                year=1967,
            ),
            Reference(
                citation="Birkhahn RH, Gaeta TJ, Terry D, Bove JJ, Tloczkowski J. Shock index in diagnosing early acute hypovolemia. Am J Emerg Med. 2005;23(3):323-326.",
                doi="10.1016/j.ajem.2005.02.029",
                pmid="15915406",
                year=2005,
            ),
            Reference(
                citation="Cannon CM, Braxton CC, Kling-Smith M, et al. Utility of the shock index in predicting mortality in traumatically injured patients. J Trauma. 2009;67(6):1426-1430.",
                doi="10.1097/TA.0b013e3181bbf728",
                pmid="20009697",
                year=2009,
            ),
        )
    
    def calculate(
        self,
        heart_rate: float,
        systolic_bp: float,
        diastolic_bp: Optional[float] = None,
        patient_type: Literal["adult", "pediatric", "obstetric"] = "adult",
    ) -> ScoreResult:
        """
        Calculate Shock Index.
        
        Args:
            heart_rate: Heart rate in beats per minute (bpm)
            systolic_bp: Systolic blood pressure in mmHg
            diastolic_bp: Diastolic blood pressure in mmHg (optional, for MSI)
            patient_type: Patient category ('adult', 'pediatric', 'obstetric')
            
        Returns:
            ScoreResult with Shock Index and interpretation
        """
        # Validate inputs
        if heart_rate < 20 or heart_rate > 300:
            raise ValueError(f"Heart rate {heart_rate} bpm is outside expected range (20-300 bpm)")
        if systolic_bp < 30 or systolic_bp > 300:
            raise ValueError(f"Systolic BP {systolic_bp} mmHg is outside expected range (30-300 mmHg)")
        if diastolic_bp is not None and (diastolic_bp < 20 or diastolic_bp > 200):
            raise ValueError(f"Diastolic BP {diastolic_bp} mmHg is outside expected range (20-200 mmHg)")
        
        # Calculate Shock Index
        shock_index = heart_rate / systolic_bp
        shock_index = round(shock_index, 2)
        
        # Calculate Modified Shock Index (MSI) if diastolic provided
        msi = None
        map_value = None
        if diastolic_bp is not None:
            map_value = (systolic_bp + 2 * diastolic_bp) / 3
            msi = heart_rate / map_value
            msi = round(msi, 2)
        
        # Generate interpretation
        interpretation = self._interpret_shock_index(
            shock_index, msi, patient_type
        )
        
        # Build calculation details
        details = {
            "Heart_rate": f"{heart_rate} bpm",
            "Systolic_BP": f"{systolic_bp} mmHg",
            "Shock_Index": f"{shock_index:.2f}",
        }
        
        if diastolic_bp is not None:
            details["Diastolic_BP"] = f"{diastolic_bp} mmHg"
            details["MAP"] = f"{map_value:.1f} mmHg"
            details["Modified_Shock_Index"] = f"{msi:.2f}"
        
        details["Patient_type"] = patient_type.capitalize()
        
        return ScoreResult(
            value=shock_index,
            unit=Unit.RATIO,
            interpretation=interpretation,
            references=self._get_references(),
            tool_id=self.tool_id,
            tool_name=self.metadata.name,
            raw_inputs={
                "heart_rate": heart_rate,
                "systolic_bp": systolic_bp,
                "diastolic_bp": diastolic_bp,
                "patient_type": patient_type,
            },
            calculation_details=details,
            formula_used="SI = Heart Rate / Systolic BP",
        )
    
    def _interpret_shock_index(
        self, 
        si: float, 
        msi: Optional[float],
        patient_type: str
    ) -> Interpretation:
        """Generate interpretation based on Shock Index."""
        
        # Adjust thresholds for obstetric patients
        # In pregnancy, normal HR increases and BP may be lower
        if patient_type == "obstetric":
            normal_upper = 0.9
            elevated_threshold = 1.0
            severe_threshold = 1.3
            context_note = "In pregnancy, SI >0.9 may indicate significant hemorrhage."
        elif patient_type == "pediatric":
            normal_upper = 1.0  # Children have higher baseline HR
            elevated_threshold = 1.2
            severe_threshold = 1.5
            context_note = "Pediatric thresholds vary by age; use age-specific references."
        else:  # adult
            normal_upper = 0.7
            elevated_threshold = 1.0
            severe_threshold = 1.4
            context_note = ""
        
        # Determine severity
        if si <= 0.5:
            severity = Severity.NORMAL
            risk_level = RiskLevel.VERY_LOW
            summary = f"Low Shock Index ({si:.2f}) - Hemodynamically stable"
            detail = "Vital signs suggest adequate perfusion and compensated hemodynamics."
            recommendations = (
                "Continue routine monitoring",
                "No immediate hemodynamic concern based on SI alone",
            )
            warnings = ()
        elif si <= normal_upper:
            severity = Severity.NORMAL
            risk_level = RiskLevel.LOW
            summary = f"Normal Shock Index ({si:.2f})"
            detail = f"SI is within normal range for {patient_type} patients."
            recommendations = (
                "Continue standard monitoring",
                "Reassess if clinical condition changes",
            )
            warnings = ()
        elif si < elevated_threshold:
            severity = Severity.MILD
            risk_level = RiskLevel.LOW
            summary = f"Borderline Shock Index ({si:.2f})"
            detail = f"SI is at the upper limit of normal. May indicate early compensated shock."
            recommendations = (
                "Increase monitoring frequency",
                "Assess for signs of hypoperfusion",
                "Consider IV access if not established",
                "Evaluate for sources of volume loss",
            )
            warnings = (
                "Borderline SI - consider occult hemorrhage or early shock",
            )
        elif si < severe_threshold:
            severity = Severity.MODERATE
            risk_level = RiskLevel.INTERMEDIATE
            summary = f"Elevated Shock Index ({si:.2f}) - Hemodynamic instability"
            detail = "SI >1.0 indicates significant hemodynamic compromise. Associated with increased mortality and need for intervention."
            recommendations = (
                "Large-bore IV access x 2",
                "Initiate fluid resuscitation",
                "Type and screen / crossmatch blood",
                "Continuous cardiac monitoring",
                "Identify and treat source of shock",
                "Consider massive transfusion protocol if hemorrhage suspected",
                "Prepare for possible ICU admission",
            )
            warnings = (
                "⚠️ Elevated SI indicates hemodynamic instability",
                "Consider early activation of trauma/critical care team",
            )
        else:  # >= severe_threshold
            severity = Severity.SEVERE
            risk_level = RiskLevel.HIGH
            summary = f"Severely Elevated Shock Index ({si:.2f}) - CRITICAL"
            detail = f"SI ≥{severe_threshold:.1f} is associated with high mortality and need for massive transfusion. Immediate intervention required."
            recommendations = (
                "ACTIVATE massive transfusion protocol",
                "Immediate large-bore IV access",
                "Rapid fluid and blood product resuscitation",
                "Identify source of hemorrhage/shock immediately",
                "Consider emergent surgery or intervention",
                "ICU admission",
                "Arterial line for continuous BP monitoring",
                "Consider vasopressors if fluid-unresponsive",
            )
            warnings = (
                "🚨 CRITICAL: Severely elevated SI - high mortality risk",
                "Immediate resuscitation and intervention required",
                "High likelihood of needing massive transfusion",
            )
        
        # Add MSI information if available
        next_steps = [
            "Serial vital signs to assess trend",
            "Point-of-care lactate if available",
            "Bedside ultrasound (FAST exam if trauma)",
        ]
        
        if msi is not None:
            if msi > 1.3:
                next_steps.append(f"Modified SI {msi:.2f} also elevated - confirms instability")
            else:
                next_steps.append(f"Modified SI {msi:.2f} within normal range (0.7-1.3)")
        
        if context_note:
            next_steps.append(context_note)
        
        return Interpretation(
            summary=summary,
            detail=detail,
            severity=severity,
            risk_level=risk_level,
            recommendations=recommendations,
            warnings=warnings,
            next_steps=tuple(next_steps),
        )
