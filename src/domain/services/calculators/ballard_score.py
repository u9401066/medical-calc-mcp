"""
Ballard Score (New Ballard Score) - Newborn Gestational Age Assessment

A validated scoring system combining neuromuscular and physical maturity
signs to estimate gestational age of newborns, accurate from 20-44 weeks.

Reference:
    Ballard JL, Khoury JC, Wedig K, Wang L, Eilers-Walsman BL, Lipp R.
    New Ballard Score, expanded to include extremely premature infants.
    J Pediatr. 1991 Sep;119(3):417-23.
    DOI: 10.1016/s0022-3476(05)82056-6
    PMID: 1880657

Clinical Use:
    - Best performed within first 12-24 hours of life
    - Combines 6 neuromuscular and 6 physical maturity signs
    - Total score range: -10 to 50, corresponding to 20-44 weeks
    - More accurate than dates alone for premature infants
"""

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, RiskLevel, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class BallardScoreCalculator(BaseCalculator):
    """
    New Ballard Score for Gestational Age Assessment

    Neuromuscular Maturity (6 items, each -1 to 4 or 5):
    1. Posture
    2. Square Window (wrist)
    3. Arm Recoil
    4. Popliteal Angle
    5. Scarf Sign
    6. Heel to Ear

    Physical Maturity (6 items, each -1 to 4 or 5):
    1. Skin
    2. Lanugo
    3. Plantar Surface
    4. Breast
    5. Eye/Ear
    6. Genitals (male or female)

    Total Score Range: -10 to 50
    Gestational Age: 20-44 weeks

    Scoring accuracy: ±2 weeks
    Best timing: First 12-24 hours of life
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="ballard_score",
                name="New Ballard Score",
                purpose="Estimate gestational age of newborns from physical and neuromuscular maturity",
                input_params=[
                    "posture",
                    "square_window",
                    "arm_recoil",
                    "popliteal_angle",
                    "scarf_sign",
                    "heel_to_ear",
                    "skin",
                    "lanugo",
                    "plantar_surface",
                    "breast",
                    "eye_ear",
                    "genitals",
                ],
                output_type="Ballard score (-10 to 50) with estimated gestational age",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.NEONATOLOGY,
                    Specialty.PEDIATRICS,
                    Specialty.OBSTETRICS,
                ),
                conditions=(
                    "Prematurity",
                    "Preterm Birth",
                    "Gestational Age Assessment",
                    "Small for Gestational Age",
                    "Large for Gestational Age",
                    "Low Birth Weight",
                    "Extremely Low Birth Weight",
                    "Very Preterm Infant",
                ),
                clinical_contexts=(
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.STAGING,
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.TREATMENT_DECISION,
                ),
            ),
            references=(
                Reference(
                    citation="Ballard JL, et al. New Ballard Score, expanded to include extremely premature infants. J Pediatr. 1991 Sep;119(3):417-23.",
                    pmid="1880657",
                    doi="10.1016/s0022-3476(05)82056-6",
                    year=1991,
                    level_of_evidence="Validation study",
                ),
                Reference(
                    citation="Dubowitz LM, Dubowitz V, Goldberg C. Clinical assessment of gestational age in the newborn infant. J Pediatr. 1970;77(1):1-10.",
                    pmid="5430794",
                    doi="10.1016/s0022-3476(70)80038-5",
                    year=1970,
                    level_of_evidence="Original study (Dubowitz Score)",
                ),
            ),
        )

    def calculate(
        self,
        # Neuromuscular Maturity (each -1 to 4 or 5)
        posture: int,
        square_window: int,
        arm_recoil: int,
        popliteal_angle: int,
        scarf_sign: int,
        heel_to_ear: int,
        # Physical Maturity (each -1 to 4 or 5)
        skin: int,
        lanugo: int,
        plantar_surface: int,
        breast: int,
        eye_ear: int,
        genitals: int,
    ) -> ScoreResult:
        """
        Calculate New Ballard Score for gestational age estimation.

        Neuromuscular Maturity Scoring (-1 to 4 or 5):

        posture: (-1 to 4)
            -1 = Completely flaccid
            0 = Slight flexion of hips and knees
            1 = Moderate flexion of hips and knees
            2 = Legs flexed, arms extended
            3 = Full flexion of arms and legs
            4 = Full flexion, active movement

        square_window: (-1 to 4) - wrist flexion angle
            -1 = >90°, 0 = 90°, 1 = 60°, 2 = 45°, 3 = 30°, 4 = 0°

        arm_recoil: (-1 to 4)
            -1 = Arms remain extended
            0 = Slow, random movement (140-180°)
            1 = Sluggish flexion (110-140°)
            2 = Brisk flexion (90-110°)
            3 = Very brisk (<90°)
            4 = Instantaneous (<90°)

        popliteal_angle: (-1 to 5)
            -1 = 180°, 0 = 160°, 1 = 140°, 2 = 120°, 3 = 100°, 4 = 90°, 5 = <90°

        scarf_sign: (-1 to 4)
            -1 = Elbow passes axillary line
            0 = Elbow reaches axillary line
            1 = Elbow between axillary and midline
            2 = Elbow at midline
            3 = Elbow does not reach midline
            4 = Elbow at anterior axillary line

        heel_to_ear: (-1 to 4)
            -1 = Heel reaches ear easily
            0 = Heel almost reaches ear
            1-4 = Progressive resistance

        Physical Maturity Scoring (-1 to 5):

        skin: (-1 to 5)
            -1 = Sticky, friable, transparent
            0 = Gelatinous, red, translucent
            1 = Smooth pink, visible veins
            2 = Superficial peeling, few veins
            3 = Cracking, pale areas, rare veins
            4 = Parchment, deep cracking
            5 = Leathery, cracked, wrinkled

        lanugo: (-1 to 4)
            -1 = None, 0 = Sparse, 1 = Abundant, 2 = Thinning, 3 = Bald areas, 4 = Mostly bald

        plantar_surface: (-1 to 4)
            -1 = Heel-toe <40 mm, no crease
            0 = Heel-toe 40-50 mm, faint marks
            1-4 = Progressive creasing

        breast: (-1 to 4)
            -1 = Imperceptible
            0 = Barely perceptible
            1-4 = Progressive development

        eye_ear: (-1 to 4)
            -1 = Lids fused
            0 = Lids open, pinna flat
            1-4 = Progressive cartilage development

        genitals: (-1 to 4)
            Male: -1 (flat) to 4 (pendulous, deep rugae)
            Female: -1 (prominent clitoris) to 4 (majora cover minora)

        Returns:
            ScoreResult with Ballard score and estimated gestational age
        """
        # Validate all inputs
        neuromuscular_items = {
            "posture": (posture, -1, 4),
            "square_window": (square_window, -1, 4),
            "arm_recoil": (arm_recoil, -1, 4),
            "popliteal_angle": (popliteal_angle, -1, 5),
            "scarf_sign": (scarf_sign, -1, 4),
            "heel_to_ear": (heel_to_ear, -1, 4),
        }

        physical_items = {
            "skin": (skin, -1, 5),
            "lanugo": (lanugo, -1, 4),
            "plantar_surface": (plantar_surface, -1, 4),
            "breast": (breast, -1, 4),
            "eye_ear": (eye_ear, -1, 4),
            "genitals": (genitals, -1, 4),
        }

        for name, (value, min_val, max_val) in {**neuromuscular_items, **physical_items}.items():
            if not isinstance(value, int) or value < min_val or value > max_val:
                raise ValueError(f"{name} must be an integer from {min_val} to {max_val}")

        # Calculate subscores
        neuromuscular_score = posture + square_window + arm_recoil + popliteal_angle + scarf_sign + heel_to_ear
        physical_score = skin + lanugo + plantar_surface + breast + eye_ear + genitals
        total_score = neuromuscular_score + physical_score

        # Convert to gestational age (linear interpolation)
        # Score -10 = 20 weeks, Score 50 = 44 weeks
        # Each 5 points = 2 weeks
        gestational_age_weeks = 20 + ((total_score + 10) / 5) * 2
        gestational_age_weeks = round(gestational_age_weeks, 1)

        # Categorize maturity
        if gestational_age_weeks < 28:
            category = "Extremely Preterm"
            severity = Severity.CRITICAL
            risk_level = RiskLevel.VERY_HIGH
            clinical_action = "Extremely preterm infant requiring Level III/IV NICU care. High risk of RDS, IVH, NEC, ROP. Surfactant likely needed."
        elif gestational_age_weeks < 32:
            category = "Very Preterm"
            severity = Severity.SEVERE
            risk_level = RiskLevel.HIGH
            clinical_action = "Very preterm infant requiring NICU care. Monitor for respiratory distress, feeding intolerance, and neurological complications."
        elif gestational_age_weeks < 34:
            category = "Moderate Preterm"
            severity = Severity.MODERATE
            risk_level = RiskLevel.INTERMEDIATE
            clinical_action = "Moderate preterm infant. Monitor respiratory status, thermoregulation, and feeding."
        elif gestational_age_weeks < 37:
            category = "Late Preterm"
            severity = Severity.MILD
            risk_level = RiskLevel.LOW
            clinical_action = "Late preterm infant. Higher risk of hypoglycemia, hypothermia, hyperbilirubinemia, and feeding difficulties."
        elif gestational_age_weeks <= 42:
            category = "Term"
            severity = Severity.NORMAL
            risk_level = RiskLevel.VERY_LOW
            clinical_action = "Term infant. Routine newborn care."
        else:
            category = "Post-term"
            severity = Severity.MILD
            risk_level = RiskLevel.LOW
            clinical_action = "Post-term infant. Monitor for meconium aspiration, hypoglycemia, and polycythemia."

        # Build interpretation
        interpretation = Interpretation(
            severity=severity,
            risk_level=risk_level,
            summary=f"Ballard Score {total_score}: Estimated GA {gestational_age_weeks} weeks ({category})",
            detail=(
                f"Neuromuscular maturity: {neuromuscular_score}\n"
                f"Physical maturity: {physical_score}\n"
                f"Total score: {total_score}\n\n"
                f"Estimated gestational age: {gestational_age_weeks} weeks\n"
                f"Category: {category}\n"
                f"Accuracy: ±2 weeks (best if performed within first 12-24 hours)"
            ),
            recommendations=(clinical_action,),
        )

        # Calculation details
        details = {
            "estimated_gestational_age_weeks": gestational_age_weeks,
            "neuromuscular_maturity_score": neuromuscular_score,
            "physical_maturity_score": physical_score,
            "maturity_category": category,
            "accuracy": "±2 weeks (best if performed within first 12-24 hours)",
            "component_scores": {
                "neuromuscular": {
                    "posture": posture,
                    "square_window": square_window,
                    "arm_recoil": arm_recoil,
                    "popliteal_angle": popliteal_angle,
                    "scarf_sign": scarf_sign,
                    "heel_to_ear": heel_to_ear,
                },
                "physical": {
                    "skin": skin,
                    "lanugo": lanugo,
                    "plantar_surface": plantar_surface,
                    "breast": breast,
                    "eye_ear": eye_ear,
                    "genitals": genitals,
                },
            },
            "next_step": "Plot on Fenton/WHO growth chart to assess AGA/SGA/LGA status",
        }

        return ScoreResult(
            value=float(total_score),
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "posture": posture,
                "square_window": square_window,
                "arm_recoil": arm_recoil,
                "popliteal_angle": popliteal_angle,
                "scarf_sign": scarf_sign,
                "heel_to_ear": heel_to_ear,
                "skin": skin,
                "lanugo": lanugo,
                "plantar_surface": plantar_surface,
                "breast": breast,
                "eye_ear": eye_ear,
                "genitals": genitals,
            },
            calculation_details=details,
        )
