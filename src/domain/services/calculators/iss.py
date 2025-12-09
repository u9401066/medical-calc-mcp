"""
Injury Severity Score (ISS) Calculator

創傷嚴重度評估工具，是創傷登錄和研究的國際標準。
基於 Abbreviated Injury Scale (AIS) 計算。

References:
- Baker SP, et al. J Trauma. 1974;14(3):187-196. PMID: 4814394
- AAAM. The Abbreviated Injury Scale 2015 Revision.
"""

from typing import Optional
from ..base import BaseCalculator
from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity, RiskLevel
from ...value_objects.reference import Reference
from ...value_objects.units import Unit
from ...value_objects.tool_keys import LowLevelKey, HighLevelKey, Specialty, ClinicalContext


class InjurySeverityScoreCalculator(BaseCalculator):
    """
    Injury Severity Score (ISS) Calculator
    
    ISS = sum of squares of highest AIS in 3 most injured body regions
    
    Body regions:
    1. Head/Neck
    2. Face
    3. Chest
    4. Abdomen
    5. Extremity (including pelvis)
    6. External (skin)
    
    AIS severity codes:
    1 = Minor
    2 = Moderate
    3 = Serious
    4 = Severe
    5 = Critical
    6 = Unsurvivable (ISS automatically = 75)
    
    ISS range: 1-75
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="iss",
                name="Injury Severity Score (ISS)",
                purpose="Calculate anatomic injury severity for trauma patients",
                input_params=(
                    "head_neck_ais", "face_ais", "chest_ais",
                    "abdomen_ais", "extremity_ais", "external_ais"
                ),
                output_type="ISS (1-75) with mortality prediction"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.SURGERY,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.CRITICAL_CARE,
                    Specialty.TRAUMA,
                ),
                conditions=(
                    "Trauma", "Polytrauma", "Multiple Injuries",
                    "Blunt Trauma", "Penetrating Trauma"
                ),
                clinical_contexts=(
                    ClinicalContext.EMERGENCY,
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.DISPOSITION,
                ),
                clinical_questions=(
                    "How severe is this trauma patient's injury?",
                    "What is the predicted mortality for this trauma?",
                    "Does this patient meet major trauma criteria?",
                    "Should this patient go to a trauma center?",
                ),
                icd10_codes=("T07",),
                keywords=(
                    "ISS", "Injury Severity Score", "trauma severity",
                    "AIS", "Abbreviated Injury Scale", "polytrauma",
                    "trauma registry", "injury severity", "major trauma"
                )
            ),
            references=(
                Reference(
                    citation="Baker SP, O'Neill B, Haddon W Jr, Long WB. The injury severity score: a method for describing patients with multiple injuries and evaluating emergency care. J Trauma. 1974;14(3):187-196.",
                    pmid="4814394",
                    year=1974
                ),
                Reference(
                    citation="Copes WS, Champion HR, Sacco WJ, et al. The Injury Severity Score revisited. J Trauma. 1988;28(1):69-77.",
                    pmid="3123707",
                    year=1988
                ),
            ),
            version="1.0.0",
            validation_status="validated"
        )
    
    def calculate(
        self,
        head_neck_ais: int = 0,
        face_ais: int = 0,
        chest_ais: int = 0,
        abdomen_ais: int = 0,
        extremity_ais: int = 0,
        external_ais: int = 0,
    ) -> ScoreResult:
        """
        Calculate Injury Severity Score
        
        Args:
            head_neck_ais: AIS for head/neck region (0-6)
            face_ais: AIS for face (0-6)
            chest_ais: AIS for chest/thorax (0-6)
            abdomen_ais: AIS for abdomen/pelvic contents (0-6)
            extremity_ais: AIS for extremity/pelvic girdle (0-6)
            external_ais: AIS for external/skin (0-6)
            
        AIS Codes:
            0 = No injury
            1 = Minor
            2 = Moderate
            3 = Serious
            4 = Severe
            5 = Critical
            6 = Unsurvivable (Maximum ISS = 75)
            
        Returns:
            ScoreResult with ISS and mortality prediction
        """
        # Validate inputs
        ais_values = {
            "Head/Neck": head_neck_ais,
            "Face": face_ais,
            "Chest": chest_ais,
            "Abdomen": abdomen_ais,
            "Extremity": extremity_ais,
            "External": external_ais,
        }
        
        for region, ais in ais_values.items():
            if not 0 <= ais <= 6:
                raise ValueError(f"{region} AIS must be between 0-6")
        
        # Check for AIS 6 (unsurvivable) - ISS automatically = 75
        if 6 in ais_values.values():
            iss = 75
            unsurvivable_regions = [r for r, a in ais_values.items() if a == 6]
            components = [
                f"{r}: AIS 6 (Unsurvivable)" for r in unsurvivable_regions
            ]
            components.append("ISS automatically = 75 (maximum)")
            
            return ScoreResult(
                value=75,
                unit=Unit.SCORE,
                interpretation=Interpretation(
                    summary="ISS 75: Unsurvivable Injury - Maximum Score",
                    detail=(
                        "ISS = 75 (Maximum). One or more unsurvivable injuries (AIS 6) detected. "
                        "ISS is automatically assigned maximum value of 75. "
                        "Prognosis: Very poor, high mortality expected."
                    ),
                    severity=Severity.CRITICAL,
                    risk_level=RiskLevel.VERY_HIGH,
                    stage="Unsurvivable",
                    stage_description="ISS = 75 (AIS 6 present)",
                    recommendations=(
                        "Focus on comfort care or heroic measures based on clinical context",
                        "Consider family notification",
                        "Document prognosis clearly",
                    ),
                    warnings=(
                        "Very high mortality expected",
                        "AIS 6 indicates unsurvivable injury",
                    ),
                ),
                references=list(self.metadata.references),
                tool_id=self.metadata.low_level.tool_id,
                tool_name=self.metadata.low_level.name,
                raw_inputs={
                    "head_neck_ais": head_neck_ais,
                    "face_ais": face_ais,
                    "chest_ais": chest_ais,
                    "abdomen_ais": abdomen_ais,
                    "extremity_ais": extremity_ais,
                    "external_ais": external_ais,
                },
                calculation_details={
                    "score_name": "Injury Severity Score (ISS)",
                    "iss": 75,
                    "max_ais": 6,
                    "unsurvivable_regions": unsurvivable_regions,
                    "mortality_estimate": ">90%",
                    "trauma_category": "Fatal/Unsurvivable",
                    "components": components,
                },
                formula_used="ISS = 75 (automatic for any AIS 6)",
                notes=[
                    "AIS 6 = unsurvivable injury",
                    "Focus on comfort care or heroic measures based on clinical context"
                ],
            )
        
        # Get three highest AIS scores
        ais_list = sorted(ais_values.values(), reverse=True)
        top_three = ais_list[:3]
        
        # Calculate ISS = sum of squares of top 3
        iss = sum(a ** 2 for a in top_three)
        
        # Build components
        components = []
        sorted_regions = sorted(ais_values.items(), key=lambda x: x[1], reverse=True)
        
        ais_labels = {
            0: "No injury",
            1: "Minor",
            2: "Moderate", 
            3: "Serious",
            4: "Severe",
            5: "Critical"
        }
        
        top_three_regions = []
        for i, (region, ais) in enumerate(sorted_regions):
            if ais > 0:
                label = ais_labels.get(ais, "Unknown")
                if i < 3 and ais > 0:
                    components.append(f"{region}: AIS {ais} ({label}) → {ais}² = {ais**2}")
                    top_three_regions.append(region)
                else:
                    components.append(f"{region}: AIS {ais} ({label}) - not in top 3")
        
        if not components:
            components = ["No injuries documented"]
        
        components.append(f"ISS = {' + '.join(str(a**2) for a in top_three if a > 0)} = {iss}")
        
        # Severity and mortality classification
        if iss == 0:
            severity = "No injury"
            mortality = "0%"
            trauma_category = "None"
            interpretation = Interpretation(
                summary=f"ISS {iss}: No Injury",
                detail="No documented injuries based on AIS scoring.",
                severity=Severity.NORMAL,
                risk_level=RiskLevel.VERY_LOW,
                stage="No Injury",
                stage_description="ISS = 0",
                recommendations=("Reassess if clinical findings suggest injury",),
            )
        elif iss <= 8:
            severity = "Minor"
            mortality = "<1%"
            trauma_category = "Minor trauma"
            interpretation = Interpretation(
                summary=f"ISS {iss}: Minor Trauma - Mortality {mortality}",
                detail=f"ISS = {iss}: Minor trauma with very low mortality.",
                severity=Severity.MILD,
                risk_level=RiskLevel.LOW,
                stage="Minor Trauma",
                stage_description=f"ISS = {iss}",
                recommendations=(
                    "Standard trauma evaluation",
                    "May not require trauma center",
                ),
            )
        elif iss <= 15:
            severity = "Moderate"
            mortality = "1-2%"
            trauma_category = "Moderate trauma"
            interpretation = Interpretation(
                summary=f"ISS {iss}: Moderate Trauma - Mortality {mortality}",
                detail=f"ISS = {iss}: Moderate trauma, low mortality risk.",
                severity=Severity.MODERATE,
                risk_level=RiskLevel.INTERMEDIATE,
                stage="Moderate Trauma",
                stage_description=f"ISS = {iss}",
                recommendations=(
                    "Thorough trauma evaluation",
                    "Monitor for occult injuries",
                    "Hospital admission likely",
                ),
            )
        elif iss <= 24:
            severity = "Serious"
            mortality = "5-10%"
            trauma_category = "Major trauma"
            interpretation = Interpretation(
                summary=f"ISS {iss}: Major Trauma - Mortality {mortality}",
                detail=f"ISS = {iss}: Major trauma (ISS >15). Significant injury burden.",
                severity=Severity.SEVERE,
                risk_level=RiskLevel.HIGH,
                stage="Major Trauma",
                stage_description=f"ISS = {iss}",
                recommendations=(
                    "Trauma center care recommended",
                    "Trauma team activation",
                    "ICU admission likely",
                    "Consider tertiary survey",
                ),
                warnings=(
                    "Major trauma - significant mortality risk",
                    "Watch for missed injuries",
                ),
            )
        elif iss <= 40:
            severity = "Severe"
            mortality = "15-25%"
            trauma_category = "Severe trauma"
            interpretation = Interpretation(
                summary=f"ISS {iss}: Severe Trauma - Mortality {mortality}",
                detail=f"ISS = {iss}: Severe trauma with significant mortality risk.",
                severity=Severity.SEVERE,
                risk_level=RiskLevel.HIGH,
                stage="Severe Trauma",
                stage_description=f"ISS = {iss}",
                recommendations=(
                    "Trauma center mandatory",
                    "ICU admission",
                    "Aggressive resuscitation",
                    "Damage control surgery if needed",
                ),
                warnings=(
                    "High mortality risk",
                    "Multi-system injury likely",
                ),
            )
        elif iss <= 54:
            severity = "Critical"
            mortality = "30-50%"
            trauma_category = "Critical trauma"
            interpretation = Interpretation(
                summary=f"ISS {iss}: Critical Trauma - Mortality {mortality}",
                detail=f"ISS = {iss}: Critical trauma with high mortality risk.",
                severity=Severity.CRITICAL,
                risk_level=RiskLevel.VERY_HIGH,
                stage="Critical Trauma",
                stage_description=f"ISS = {iss}",
                recommendations=(
                    "Trauma center ICU",
                    "Damage control resuscitation",
                    "Massive transfusion protocol likely",
                    "Early surgical intervention",
                ),
                warnings=(
                    "Very high mortality risk",
                    "Prepare for deterioration",
                ),
            )
        else:
            severity = "Unsurvivable"
            mortality = ">75%"
            trauma_category = "Unsurvivable trauma"
            interpretation = Interpretation(
                summary=f"ISS {iss}: Unsurvivable - Mortality {mortality}",
                detail=f"ISS = {iss}: Near-fatal injury severity.",
                severity=Severity.CRITICAL,
                risk_level=RiskLevel.VERY_HIGH,
                stage="Unsurvivable",
                stage_description=f"ISS = {iss}",
                recommendations=(
                    "Maximum resuscitation efforts",
                    "Consider goals of care",
                    "Family notification",
                ),
                warnings=(
                    "Extremely high mortality",
                    "Consider futility",
                ),
            )
        
        # Major trauma definition
        is_major_trauma = iss > 15
        
        return ScoreResult(
            value=iss,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.metadata.references),
            tool_id=self.metadata.low_level.tool_id,
            tool_name=self.metadata.low_level.name,
            raw_inputs={
                "head_neck_ais": head_neck_ais,
                "face_ais": face_ais,
                "chest_ais": chest_ais,
                "abdomen_ais": abdomen_ais,
                "extremity_ais": extremity_ais,
                "external_ais": external_ais,
            },
            calculation_details={
                "score_name": "Injury Severity Score (ISS)",
                "score_range": "0-75",
                "iss": iss,
                "severity": severity,
                "mortality_estimate": mortality,
                "trauma_category": trauma_category,
                "is_major_trauma": is_major_trauma,
                "max_ais": max(ais_values.values()),
                "top_three_regions": top_three_regions[:3],
                "top_three_ais": [ais_values[r] for r in top_three_regions[:3]] if top_three_regions else [],
                "components": components,
            },
            formula_used="ISS = sum of squares of 3 highest AIS",
            notes=[
                "ISS >15 = major trauma; ISS >25 = severe trauma",
                "Consider TRISS calculation for survival probability if combined with RTS"
            ],
        )
