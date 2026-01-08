"""
Bosniak Classification (Renal Cyst Classification)

The Bosniak classification system categorizes renal cysts based on
imaging characteristics to predict malignancy risk and guide management.

Reference (Original Classification):
    Bosniak MA. The current radiological approach to renal cysts.
    Radiology. 1986;158(1):1-10.
    PMID: 3510019

Reference (2019 Update - Bosniak v2019):
    Silverman SG, Pedrosa I, Ellis JH, et al. Bosniak Classification of
    Cystic Renal Masses, Version 2019: An Update Proposal and Needs
    Assessment. Radiology. 2019;292(2):475-488.
    PMID: 31210616
"""

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import (
    ClinicalContext,
    HighLevelKey,
    LowLevelKey,
    Specialty,
)
from ...value_objects.units import Unit
from ..base import BaseCalculator


class BosniakClassificationCalculator(BaseCalculator):
    """
    Bosniak Classification Calculator (v2019)

    Classifies renal cystic masses based on CT/MRI characteristics.
    Categories: I, II, IIF, III, IV
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="bosniak",
                name="Bosniak Classification (Renal Cyst Classification v2019)",
                purpose="Classify renal cysts and predict malignancy risk",
                input_params=[
                    "septations",
                    "wall_characteristics",
                    "calcification",
                    "enhancement",
                    "solid_component",
                ],
                output_type="Bosniak category (I-IV) with malignancy risk",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.UROLOGY,
                    Specialty.RADIOLOGY,
                    Specialty.NEPHROLOGY,
                ),
                conditions=(
                    "Renal Cyst",
                    "Cystic Renal Mass",
                    "Renal Cell Carcinoma",
                    "Complex Renal Cyst",
                    "Kidney Mass",
                ),
                clinical_contexts=(
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.TREATMENT_DECISION,
                ),
                clinical_questions=(
                    "Is this renal cyst malignant?",
                    "Does this renal cyst need surgery?",
                    "Classify this renal cyst",
                    "What is the Bosniak category?",
                ),
                keywords=(
                    "Bosniak",
                    "renal cyst",
                    "kidney cyst",
                    "cystic renal mass",
                    "renal cell carcinoma",
                    "RCC",
                ),
            ),
            references=(
                Reference(
                    citation="Bosniak MA. The current radiological approach to renal cysts. Radiology. 1986;158(1):1-10.",
                    pmid="3510019",
                    doi="10.1148/radiology.158.1.3510019",
                    year=1986,
                ),
                Reference(
                    citation="Silverman SG, Pedrosa I, Ellis JH, et al. Bosniak Classification of Cystic Renal Masses, Version 2019. Radiology. 2019;292(2):475-488.",
                    pmid="31210616",
                    doi="10.1148/radiol.2019182646",
                    year=2019,
                ),
            ),
        )

    def calculate(self, **params) -> ScoreResult:
        """
        Calculate Bosniak classification.

        Args:
            septations: Septal characteristics
                "none" = No septa
                "few_thin" = 1-3 thin (<2mm) septa
                "many_thin" = ≥4 thin septa
                "thick" = Thick (≥3mm) or measurably enhancing septa

            wall_characteristics: Cyst wall
                "thin_smooth" = Thin, smooth wall
                "minimally_thick" = Minimally thickened (≤2mm)
                "thick_irregular" = Thick (≥3mm) or irregular wall

            calcification: Calcification pattern
                "none" = No calcification
                "thin" = Thin calcification
                "thick_nodular" = Thick, nodular, or irregular calcification

            enhancement: Enhancement pattern
                "none" = No enhancement
                "wall_septal" = Wall or septal enhancement
                "nodular" = Nodular enhancement

            solid_component: Enhancing soft tissue component
                "none" = No solid component
                "present" = Enhancing soft tissue present

        Returns:
            ScoreResult with Bosniak category and management
        """
        # Extract parameters
        septations = str(params.get("septations", "none")).lower()
        wall = str(params.get("wall_characteristics", "thin_smooth")).lower()
        calcification = str(params.get("calcification", "none")).lower()
        enhancement = str(params.get("enhancement", "none")).lower()
        solid = str(params.get("solid_component", "none")).lower()

        # Validate inputs
        valid_septations = ["none", "few_thin", "many_thin", "thick"]
        valid_wall = ["thin_smooth", "minimally_thick", "thick_irregular"]
        valid_calcification = ["none", "thin", "thick_nodular"]
        valid_enhancement = ["none", "wall_septal", "nodular"]
        valid_solid = ["none", "present"]

        if septations not in valid_septations:
            raise ValueError(f"septations must be one of {valid_septations}")
        if wall not in valid_wall:
            raise ValueError(f"wall_characteristics must be one of {valid_wall}")
        if calcification not in valid_calcification:
            raise ValueError(f"calcification must be one of {valid_calcification}")
        if enhancement not in valid_enhancement:
            raise ValueError(f"enhancement must be one of {valid_enhancement}")
        if solid not in valid_solid:
            raise ValueError(f"solid_component must be one of {valid_solid}")

        # Determine Bosniak category (v2019 criteria)
        # Category IV: Enhancing soft tissue component
        if solid == "present" or enhancement == "nodular":
            category = "IV"
            malignancy_risk = "~90%"
            severity = Severity.CRITICAL
            description = "Cystic renal mass with enhancing soft tissue"

        # Category III: Thick enhancing wall/septa OR thick calcification
        elif septations == "thick" or wall == "thick_irregular" or calcification == "thick_nodular":
            category = "III"
            malignancy_risk = "~50%"
            severity = Severity.SEVERE
            description = "Indeterminate cystic mass"

        # Category IIF: Many thin septa OR minimally thick wall OR minimal enhancement
        elif septations == "many_thin" or wall == "minimally_thick" or enhancement == "wall_septal":
            category = "IIF"
            malignancy_risk = "~5-10%"
            severity = Severity.MODERATE
            description = "Minimally complex cyst requiring follow-up"

        # Category II: Few thin septa OR thin calcification OR hyperdense cyst
        elif septations == "few_thin" or calcification == "thin":
            category = "II"
            malignancy_risk = "~0%"
            severity = Severity.MILD
            description = "Minimally complex benign cyst"

        # Category I: Simple cyst
        else:
            category = "I"
            malignancy_risk = "0%"
            severity = Severity.NORMAL
            description = "Simple benign cyst"

        # Management recommendations (per AUA/ACR guidelines)
        recommendations = []
        if category == "I":
            recommendations.append("Benign simple cyst - no follow-up needed")
            recommendations.append("No further imaging required")
        elif category == "II":
            recommendations.append("Benign complex cyst - no follow-up needed")
            recommendations.append("No intervention required")
        elif category == "IIF":
            recommendations.append("Follow-up imaging recommended")
            recommendations.append("CT or MRI at 6 months, then annually for 5 years")
            recommendations.append("If stable at 5 years, likely benign")
            recommendations.append("If progression, upgrade category")
        elif category == "III":
            recommendations.append("Surgical excision or active surveillance")
            recommendations.append("Partial nephrectomy preferred if surgically feasible")
            recommendations.append("Active surveillance option for elderly/comorbid patients")
            recommendations.append("Discuss risks/benefits with patient")
        else:  # IV
            recommendations.append("Surgical excision recommended")
            recommendations.append("Partial nephrectomy if technically feasible")
            recommendations.append("Radical nephrectomy if partial not possible")
            recommendations.append("High malignancy risk - urgent urology referral")

        warnings = []
        if category in ["III", "IV"]:
            warnings.append(f"High malignancy risk ({malignancy_risk}) - surgical evaluation needed")
        if category == "IIF":
            warnings.append("Requires surveillance - do not discharge without follow-up plan")

        next_steps = {
            "I": ["No further imaging"],
            "II": ["No further imaging"],
            "IIF": ["CT/MRI at 6 months", "Annual imaging for 5 years if stable"],
            "III": ["Urology referral", "Discuss surgery vs surveillance"],
            "IV": ["Urgent urology referral", "Staging workup", "Surgical planning"],
        }

        findings = []
        if septations != "none":
            findings.append(f"Septa: {septations.replace('_', ' ')}")
        if wall != "thin_smooth":
            findings.append(f"Wall: {wall.replace('_', ' ')}")
        if calcification != "none":
            findings.append(f"Calcification: {calcification.replace('_', ' ')}")
        if enhancement != "none":
            findings.append(f"Enhancement: {enhancement.replace('_', ' ')}")
        if solid != "none":
            findings.append("Enhancing soft tissue present")

        return ScoreResult(
            value=["I", "II", "IIF", "III", "IV"].index(category) + 1,  # Numeric for sorting
            unit=Unit.CATEGORY,
            interpretation=Interpretation(
                summary=f"Bosniak {category}: {description} (Malignancy risk: {malignancy_risk})",
                detail=(
                    f"Bosniak category {category} based on imaging features. "
                    f"Findings: {', '.join(findings) if findings else 'Simple cyst'}. "
                    f"Estimated malignancy risk: {malignancy_risk}. "
                    f"{'Benign - no intervention needed.' if category in ['I', 'II'] else 'Follow-up or intervention required.'}"
                ),
                severity=severity,
                stage=f"Bosniak {category}",
                stage_description=description,
                recommendations=recommendations,
                warnings=warnings,
                next_steps=next_steps.get(category, []),
            ),
            references=self.metadata.references,
            tool_id=self.metadata.low_level.tool_id,
            tool_name=self.metadata.low_level.name,
            raw_inputs=params,
            calculation_details={
                "bosniak_category": category,
                "malignancy_risk": malignancy_risk,
                "description": description,
                "septations": septations,
                "wall_characteristics": wall,
                "calcification": calcification,
                "enhancement": enhancement,
                "solid_component": solid,
                "findings": findings,
            },
        )
