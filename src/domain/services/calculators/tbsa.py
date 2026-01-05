"""
TBSA (Total Body Surface Area) Calculator

燒傷面積計算器，使用 Rule of Nines 和 Lund-Browder 圖表。
是燒傷輸液計算(Parkland Formula)的前提工具。

References:
- Wallace AB. Lancet. 1951;1(6653):501-504. PMID: 14805109
- Lund CC, Browder NC. Surg Gynecol Obstet. 1944;79:352-358.
- American Burn Association Guidelines
"""

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, RiskLevel, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class TbsaCalculator(BaseCalculator):
    """
    TBSA (Total Body Surface Area) Calculator for Burns

    使用 Rule of Nines 計算燒傷面積百分比。
    成人與兒童有不同的體表面積分布。

    輸出: TBSA %
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="tbsa",
                name="TBSA Calculator (Rule of Nines)",
                purpose="Calculate total body surface area burned using Rule of Nines",
                input_params=[
                    "head_neck", "anterior_trunk", "posterior_trunk",
                    "right_arm", "left_arm", "right_leg", "left_leg",
                    "genitalia", "age", "method"
                ],
                output_type="TBSA percentage with burn severity classification"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.SURGERY,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.CRITICAL_CARE,
                    Specialty.TRAUMA,
                ),
                conditions=(
                    "Burns", "Burn Injury", "Thermal Injury",
                    "Scald", "Chemical Burn"
                ),
                clinical_contexts=(
                    ClinicalContext.EMERGENCY,
                    ClinicalContext.FLUID_MANAGEMENT,
                    ClinicalContext.DISPOSITION,
                ),
                clinical_questions=(
                    "What percentage of body surface is burned?",
                    "Does this burn require fluid resuscitation?",
                    "How severe is this burn injury?",
                    "Should this patient go to a burn center?",
                ),
                icd10_codes=("T30", "T31"),
                keywords=(
                    "TBSA", "burns", "burn area", "Rule of Nines",
                    "body surface area", "burn severity", "Parkland",
                    "thermal injury", "scald", "Lund-Browder"
                )
            ),
            references=(
                Reference(
                    citation="Wallace AB. The exposure treatment of burns. Lancet. 1951;1(6653):501-504.",
                    doi="10.1016/S0140-6736(51)91975-7",
                    pmid="14805109",
                    year=1951
                ),
                Reference(
                    citation="Lund CC, Browder NC. The estimation of areas of burns. Surg Gynecol Obstet. 1944;79:352-358.",
                    year=1944
                ),
            ),
            version="1.0.0",
            validation_status="validated"
        )

    def calculate(
        self,
        head_neck: float = 0,
        chest: float = 0,
        abdomen: float = 0,
        upper_back: float = 0,
        lower_back: float = 0,
        right_arm: float = 0,
        left_arm: float = 0,
        right_hand: float = 0,
        left_hand: float = 0,
        perineum: float = 0,
        right_thigh: float = 0,
        left_thigh: float = 0,
        right_leg: float = 0,
        left_leg: float = 0,
        right_foot: float = 0,
        left_foot: float = 0,
        patient_type: str = "adult",  # adult, child, infant
    ) -> ScoreResult:
        """
        Calculate TBSA using Rule of Nines

        Each parameter is the PERCENTAGE of that body part burned (0-100%).
        For example, if half of the right arm is burned, enter 50.

        Args:
            head_neck: % of head/neck burned (adult 9%, infant 18%)
            chest: % of anterior chest burned (9%)
            abdomen: % of abdomen burned (9%)
            upper_back: % of upper back burned (9%)
            lower_back: % of lower back/buttocks burned (9%)
            right_arm: % of right arm burned (9%)
            left_arm: % of left arm burned (9%)
            right_hand: % of right hand burned (included in arm or 1%)
            left_hand: % of left hand burned (included in arm or 1%)
            perineum: % of perineum burned (1%)
            right_thigh: % of right anterior thigh burned (adult 9%, child varies)
            left_thigh: % of left anterior thigh burned
            right_leg: % of right lower leg burned (adult 9%)
            left_leg: % of left lower leg burned
            right_foot: % of right foot burned (included in leg)
            left_foot: % of left foot burned
            patient_type: "adult" (>14y), "child" (1-14y), or "infant" (<1y)

        Returns:
            ScoreResult with TBSA percentage and burn severity
        """
        # Validate inputs
        all_inputs = [
            head_neck, chest, abdomen, upper_back, lower_back,
            right_arm, left_arm, right_hand, left_hand, perineum,
            right_thigh, left_thigh, right_leg, left_leg, right_foot, left_foot
        ]
        for val in all_inputs:
            if not 0 <= val <= 100:
                raise ValueError("All percentages must be between 0-100")

        if patient_type.lower() not in ["adult", "child", "infant"]:
            raise ValueError("patient_type must be 'adult', 'child', or 'infant'")

        patient_type = patient_type.lower()

        # Rule of Nines percentages by patient type
        # Values are the % BSA for ENTIRE region
        regions: dict[str, tuple[float, float]]
        if patient_type == "adult":
            regions = {
                "head_neck": (9.0, head_neck),
                "chest": (9.0, chest),
                "abdomen": (9.0, abdomen),
                "upper_back": (9.0, upper_back),
                "lower_back": (9.0, lower_back),
                "right_arm": (9.0, right_arm),
                "left_arm": (9.0, left_arm),
                "right_hand": (1.0, right_hand),  # Palm rule
                "left_hand": (1.0, left_hand),
                "perineum": (1.0, perineum),
                "right_thigh": (9.0, right_thigh),
                "left_thigh": (9.0, left_thigh),
                "right_leg": (9.0, right_leg),
                "left_leg": (9.0, left_leg),
                "right_foot": (1.0, right_foot),
                "left_foot": (1.0, left_foot),
            }
        elif patient_type == "child":
            # Child: Head larger, legs smaller
            regions = {
                "head_neck": (15.0, head_neck),
                "chest": (9.0, chest),
                "abdomen": (9.0, abdomen),
                "upper_back": (9.0, upper_back),
                "lower_back": (9.0, lower_back),
                "right_arm": (9.0, right_arm),
                "left_arm": (9.0, left_arm),
                "right_hand": (1.0, right_hand),
                "left_hand": (1.0, left_hand),
                "perineum": (1.0, perineum),
                "right_thigh": (7.0, right_thigh),
                "left_thigh": (7.0, left_thigh),
                "right_leg": (7.0, right_leg),
                "left_leg": (7.0, left_leg),
                "right_foot": (1.0, right_foot),
                "left_foot": (1.0, left_foot),
            }
        else:  # infant
            # Infant: Head much larger, legs smaller
            regions = {
                "head_neck": (18.0, head_neck),
                "chest": (9.0, chest),
                "abdomen": (9.0, abdomen),
                "upper_back": (9.0, upper_back),
                "lower_back": (9.0, lower_back),
                "right_arm": (9.0, right_arm),
                "left_arm": (9.0, left_arm),
                "right_hand": (1.0, right_hand),
                "left_hand": (1.0, left_hand),
                "perineum": (1.0, perineum),
                "right_thigh": (5.5, right_thigh),
                "left_thigh": (5.5, left_thigh),
                "right_leg": (5.0, right_leg),
                "left_leg": (5.0, left_leg),
                "right_foot": (1.0, right_foot),
                "left_foot": (1.0, left_foot),
            }

        # Calculate TBSA
        tbsa: float = 0.0
        components = []

        for region_name, (max_pct, burned_pct) in regions.items():
            if burned_pct > 0:
                contribution = (max_pct * burned_pct) / 100
                tbsa += contribution
                components.append(f"{region_name.replace('_', ' ').title()}: {burned_pct:.0f}% of {max_pct}% = {contribution:.1f}%")

        tbsa = round(tbsa, 1)

        # Severity classification
        if tbsa < 10:
            severity = "Minor"
            fluid_needed = "Usually no IV fluids needed"
            disposition = "May be treated outpatient if <10% and no high-risk features"
            interpretation = Interpretation(
                summary=f"TBSA {tbsa}%: Minor Burn",
                detail=(
                    f"Total Body Surface Area burned: {tbsa}%. "
                    "Minor burn, may be appropriate for outpatient management "
                    "if no high-risk features present."
                ),
                severity=Severity.MILD,
                risk_level=RiskLevel.LOW,
                stage="Minor Burn",
                stage_description=f"TBSA {tbsa}%",
                recommendations=(
                    "Consider outpatient management if appropriate",
                    "Assess for burn center referral criteria",
                    "Wound care and follow-up",
                ),
                next_steps=(
                    "Assess burn depth",
                    "Check for high-risk features",
                    "Arrange follow-up",
                ),
            )
        elif tbsa < 20:
            severity = "Moderate"
            fluid_needed = "IV fluid resuscitation recommended"
            disposition = "Hospital admission, consider burn center"
            interpretation = Interpretation(
                summary=f"TBSA {tbsa}%: Moderate Burn - Hospital Admission",
                detail=(
                    f"Total Body Surface Area burned: {tbsa}%. "
                    "Moderate burn requiring hospital admission. "
                    "Consider burn center referral."
                ),
                severity=Severity.MODERATE,
                risk_level=RiskLevel.INTERMEDIATE,
                stage="Moderate Burn",
                stage_description=f"TBSA {tbsa}%",
                recommendations=(
                    "Hospital admission required",
                    "IV fluid resuscitation",
                    "Consider burn center referral",
                    "Pain management",
                ),
                warnings=(
                    "Monitor for fluid shifts",
                    "Watch for compartment syndrome if circumferential",
                ),
                next_steps=(
                    "Start IV fluids",
                    "Calculate Parkland if >15%",
                    "Burn center consultation",
                ),
            )
        elif tbsa < 40:
            severity = "Major"
            fluid_needed = "Aggressive IV resuscitation required (Parkland formula)"
            disposition = "Burn center admission required"
            interpretation = Interpretation(
                summary=f"TBSA {tbsa}%: Major Burn - Burn Center Required",
                detail=(
                    f"Total Body Surface Area burned: {tbsa}%. "
                    "Major burn requiring burn center admission. "
                    "Aggressive fluid resuscitation using Parkland formula."
                ),
                severity=Severity.SEVERE,
                risk_level=RiskLevel.HIGH,
                stage="Major Burn",
                stage_description=f"TBSA {tbsa}%",
                recommendations=(
                    "Burn center admission required",
                    "Aggressive IV resuscitation (Parkland formula)",
                    "Central line and Foley catheter",
                    "Monitor urine output 0.5-1 mL/kg/hr",
                    "Escharotomy if circumferential",
                ),
                warnings=(
                    "High mortality risk",
                    "Risk of respiratory failure with inhalation injury",
                    "Monitor for compartment syndrome",
                ),
                next_steps=(
                    "Calculate Parkland formula",
                    "Arrange burn center transfer",
                    "Consider intubation if airway compromise",
                ),
            )
        else:
            severity = "Critical"
            fluid_needed = "Emergent aggressive resuscitation"
            disposition = "Burn center ICU, high mortality risk"
            interpretation = Interpretation(
                summary=f"TBSA {tbsa}%: Critical Burn - High Mortality Risk",
                detail=(
                    f"Total Body Surface Area burned: {tbsa}%. "
                    "Critical burn with high mortality risk. "
                    "Requires burn center ICU and aggressive resuscitation."
                ),
                severity=Severity.CRITICAL,
                risk_level=RiskLevel.VERY_HIGH,
                stage="Critical Burn",
                stage_description=f"TBSA {tbsa}%",
                recommendations=(
                    "Burn center ICU admission",
                    "Emergent aggressive resuscitation",
                    "Intubation and mechanical ventilation likely",
                    "Massive fluid resuscitation",
                    "Early surgical consultation",
                ),
                warnings=(
                    "Very high mortality risk",
                    "Multi-organ failure likely",
                    "Consider goals of care discussion",
                ),
                next_steps=(
                    "Emergent burn center transfer",
                    "Airway management",
                    "Aggressive resuscitation",
                ),
            )

        # Burn center referral criteria (ABA)
        burn_center_criteria = []
        if tbsa >= 10:
            burn_center_criteria.append("TBSA ≥10%")
        if head_neck > 0:
            burn_center_criteria.append("Face/neck involvement")
        if right_hand > 0 or left_hand > 0:
            burn_center_criteria.append("Hands involved")
        if right_foot > 0 or left_foot > 0:
            burn_center_criteria.append("Feet involved")
        if perineum > 0:
            burn_center_criteria.append("Perineum involved")

        return ScoreResult(
            value=tbsa,
            unit=Unit.PERCENT,
            interpretation=interpretation,
            references=list(self.metadata.references),
            tool_id=self.metadata.low_level.tool_id,
            tool_name=self.metadata.low_level.name,
            raw_inputs={
                "head_neck": head_neck,
                "chest": chest,
                "abdomen": abdomen,
                "upper_back": upper_back,
                "lower_back": lower_back,
                "right_arm": right_arm,
                "left_arm": left_arm,
                "right_hand": right_hand,
                "left_hand": left_hand,
                "perineum": perineum,
                "right_thigh": right_thigh,
                "left_thigh": left_thigh,
                "right_leg": right_leg,
                "left_leg": left_leg,
                "right_foot": right_foot,
                "left_foot": left_foot,
                "patient_type": patient_type,
            },
            calculation_details={
                "score_name": "TBSA (Rule of Nines)",
                "tbsa_percent": tbsa,
                "severity": severity,
                "patient_type": patient_type,
                "fluid_recommendation": fluid_needed,
                "disposition": disposition,
                "components": components if components else ["No burns documented"],
                "burn_center_criteria": burn_center_criteria,
            },
            formula_used="TBSA = sum of (region % × burn %) for all regions",
            notes=[
                "For 2nd/3rd degree burns ≥20% TBSA, use Parkland formula",
                f"{'Calculate Parkland formula for fluid resuscitation' if tbsa >= 15 else 'Assess burn depth and consider outpatient vs admission'}"
            ],
        )
