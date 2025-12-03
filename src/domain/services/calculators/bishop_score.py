"""
Bishop Score - Cervical Ripening Assessment for Labor Induction

A classic scoring system to assess cervical favorability and predict
successful labor induction.

Reference:
    Bishop EH. Pelvic scoring for elective induction.
    Obstet Gynecol. 1964 Aug;24:266-8.
    PMID: 14199536

Clinical Use:
    - Score ≥8: Favorable cervix, high likelihood of successful vaginal delivery
    - Score 6-7: Intermediate, induction may proceed with ripening agents
    - Score ≤5: Unfavorable cervix, consider cervical ripening before induction
"""

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
    ClinicalContext
)


class BishopScoreCalculator(BaseCalculator):
    """
    Bishop Score for Cervical Assessment
    
    Evaluates five cervical parameters:
    1. Dilation (cm): 0-3 points
    2. Effacement (%): 0-3 points
    3. Station (-3 to +2): 0-3 points
    4. Consistency (firm to soft): 0-2 points
    5. Position (posterior to anterior): 0-2 points
    
    Total Score: 0-13 points
    
    Interpretation:
    - ≥8: Favorable cervix - proceed with induction
    - 6-7: Moderately favorable - consider ripening
    - ≤5: Unfavorable - cervical ripening recommended
    """

    # Scoring tables for string inputs
    CONSISTENCY_SCORES = {
        "firm": 0,
        "medium": 1,
        "soft": 2,
    }
    
    POSITION_SCORES = {
        "posterior": 0,
        "mid": 1,
        "anterior": 2,
    }

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="bishop_score",
                name="Bishop Score",
                purpose="Assess cervical favorability for labor induction",
                input_params=[
                    "dilation",
                    "effacement",
                    "station",
                    "consistency",
                    "position"
                ],
                output_type="Bishop score (0-13) with induction success prediction"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.OBSTETRICS,
                    Specialty.OBSTETRIC_ANESTHESIA,
                ),
                conditions=(
                    "Labor Induction",
                    "Cervical Ripening",
                    "Post-term Pregnancy",
                    "Pre-eclampsia",
                    "PROM",
                    "Premature Rupture of Membranes",
                    "Oligohydramnios",
                    "Gestational Diabetes",
                    "IUGR",
                ),
                clinical_contexts=(
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.TREATMENT_DECISION,
                    ClinicalContext.RISK_STRATIFICATION,
                ),
            ),
            references=(
                Reference(
                    citation="Bishop EH. Pelvic scoring for elective induction. "
                             "Obstet Gynecol. 1964 Aug;24:266-8.",
                    pmid="14199536",
                    year=1964,
                    level_of_evidence="Original study"
                ),
                Reference(
                    citation="ACOG Practice Bulletin No. 107: Induction of labor. "
                             "Obstet Gynecol. 2009;114:386-397.",
                    pmid="19623003",
                    doi="10.1097/AOG.0b013e3181b48ef5",
                    year=2009,
                    level_of_evidence="Clinical guideline"
                ),
            )
        )

    def calculate(
        self,
        dilation: int,
        effacement: int,
        station: int,
        consistency: str,
        position: str,
    ) -> ScoreResult:
        """
        Calculate Bishop Score for cervical assessment.
        
        Args:
            dilation: Cervical dilation score (0-3)
                0 = Closed, 1 = 1-2 cm, 2 = 3-4 cm, 3 = ≥5 cm
            effacement: Cervical effacement score (0-3)
                0 = 0-30%, 1 = 40-50%, 2 = 60-70%, 3 = ≥80%
            station: Fetal station score (0-3)
                0 = -3, 1 = -2, 2 = -1/0, 3 = +1/+2
            consistency: Cervical consistency
                Options: "firm", "medium", "soft"
            position: Cervical position
                Options: "posterior", "mid", "anterior"
        
        Returns:
            ScoreResult with Bishop score and induction recommendations
        """
        # Validate inputs
        if dilation not in [0, 1, 2, 3]:
            raise ValueError("dilation must be 0, 1, 2, or 3")
        if effacement not in [0, 1, 2, 3]:
            raise ValueError("effacement must be 0, 1, 2, or 3")
        if station not in [0, 1, 2, 3]:
            raise ValueError("station must be 0, 1, 2, or 3")
        
        consistency_lower = consistency.lower()
        if consistency_lower not in self.CONSISTENCY_SCORES:
            raise ValueError("consistency must be 'firm', 'medium', or 'soft'")
        
        position_lower = position.lower()
        if position_lower not in self.POSITION_SCORES:
            raise ValueError("position must be 'posterior', 'mid', or 'anterior'")
        
        # Calculate score components
        consistency_score = self.CONSISTENCY_SCORES[consistency_lower]
        position_score = self.POSITION_SCORES[position_lower]
        
        # Total Bishop Score
        total_score = dilation + effacement + station + consistency_score + position_score
        
        # Interpretation descriptions
        dilation_desc = ["Closed", "1-2 cm", "3-4 cm", "≥5 cm"][dilation]
        effacement_desc = ["0-30%", "40-50%", "60-70%", "≥80%"][effacement]
        station_desc = ["-3", "-2", "-1/0", "+1/+2"][station]
        
        # Interpretation based on score
        if total_score >= 8:
            severity = Severity.NORMAL
            risk_level = RiskLevel.LOW
            category = "Favorable Cervix"
            success_rate = "~90-95%"
            recommendation = (
                "Cervix is favorable for induction. "
                "Proceed with oxytocin induction. "
                "High likelihood of successful vaginal delivery."
            )
            ripening_needed = False
        elif total_score >= 6:
            severity = Severity.MILD
            risk_level = RiskLevel.INTERMEDIATE
            category = "Moderately Favorable"
            success_rate = "~70-80%"
            recommendation = (
                "Cervix is moderately favorable. "
                "May proceed with induction, but consider cervical ripening "
                "(prostaglandins or mechanical methods) to improve success rate."
            )
            ripening_needed = True
        else:  # score <= 5
            severity = Severity.MODERATE
            risk_level = RiskLevel.HIGH
            category = "Unfavorable Cervix"
            success_rate = "~50-60% without ripening"
            recommendation = (
                "Cervix is unfavorable for induction. "
                "Cervical ripening strongly recommended before oxytocin. "
                "Options: Misoprostol, Dinoprostone (PGE2), Foley catheter, "
                "or Cook balloon."
            )
            ripening_needed = True
        
        # Build interpretation
        interpretation = Interpretation(
            severity=severity,
            risk_level=risk_level,
            summary=f"Bishop Score {total_score}/13: {category}",
            detail=(
                f"Component scores:\n"
                f"  • Dilation: {dilation} ({dilation_desc})\n"
                f"  • Effacement: {effacement} ({effacement_desc})\n"
                f"  • Station: {station} ({station_desc})\n"
                f"  • Consistency: {consistency_score} ({consistency})\n"
                f"  • Position: {position_score} ({position})\n\n"
                f"Predicted success rate: {success_rate}"
            ),
            recommendations=(recommendation,),
        )
        
        # Calculation details
        details = {
            "score_breakdown": {
                "dilation": f"{dilation} ({dilation_desc})",
                "effacement": f"{effacement} ({effacement_desc})",
                "station": f"{station} ({station_desc})",
                "consistency": f"{consistency_score} ({consistency})",
                "position": f"{position_score} ({position})",
            },
            "category": category,
            "predicted_success_rate": success_rate,
            "ripening_needed": ripening_needed,
            "next_step": (
                "Consider cervical ripening method selection"
                if ripening_needed
                else "Proceed with induction protocol"
            ),
        }
        
        # Add ripening options if needed
        if ripening_needed:
            details["ripening_options"] = [
                "Misoprostol (Cytotec) 25 mcg PV q4h",
                "Dinoprostone (Cervidil) 10 mg insert",
                "Dinoprostone (Prepidil) 0.5 mg gel",
                "Foley catheter (16-18 Fr, 30-60 mL)",
                "Cook double balloon catheter",
            ]

        return ScoreResult(
            value=float(total_score),
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "dilation": dilation,
                "effacement": effacement,
                "station": station,
                "consistency": consistency,
                "position": position,
            },
            calculation_details=details
        )
