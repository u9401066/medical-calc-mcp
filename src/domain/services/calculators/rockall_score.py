"""
Rockall Score for Upper GI Bleeding

Predicts mortality and rebleeding risk in upper gastrointestinal bleeding.

Reference:
    Rockall TA, Logan RF, Devlin HB, Northfield TC.
    Risk assessment after acute upper gastrointestinal haemorrhage.
    Gut. 1996;38(3):316-321.
    DOI: 10.1136/gut.38.3.316
    PMID: 8675081
"""

from typing import Literal

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, RiskLevel, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class RockallScoreCalculator(BaseCalculator):
    """
    Rockall Score for Upper GI Bleeding

    Full Rockall Score (with endoscopy) predicts mortality and rebleeding.

    Components:
    - Age: <60 (0), 60-79 (1), ≥80 (2)
    - Shock: None (0), Pulse>100 (1), SBP<100 (2)
    - Comorbidity: None (0), CHF/IHD/major (2), Renal/liver/mets (3)
    - Diagnosis: Mallory-Weiss (0), Other (1), GI malignancy (2)
    - Stigmata: None/dark spot (0), Blood/clot/visible vessel (2)

    Total: 0-11 points

    Mortality by score:
    - 0: 0.0%
    - 1: 0.0%
    - 2: 0.2%
    - 3: 2.9%
    - 4: 5.3%
    - 5: 10.8%
    - 6: 17.3%
    - 7: 27.0%
    - ≥8: 41.1%
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="rockall_score",
                name="Rockall Score",
                purpose="Predict mortality and rebleeding in upper GI bleeding",
                input_params=[
                    "age_years",
                    "shock_status",
                    "comorbidity",
                    "diagnosis",
                    "stigmata_of_recent_hemorrhage"
                ],
                output_type="Rockall score (0-11) with mortality risk"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.GASTROENTEROLOGY,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.CRITICAL_CARE,
                    Specialty.INTERNAL_MEDICINE,
                ),
                conditions=(
                    "Upper GI Bleeding",
                    "UGIB",
                    "Gastrointestinal Hemorrhage",
                    "Hematemesis",
                    "Melena",
                    "Peptic Ulcer Bleeding",
                    "Variceal Bleeding",
                ),
                clinical_contexts=(
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.DISPOSITION,
                    ClinicalContext.TREATMENT_DECISION,
                ),
                clinical_questions=(
                    "What is the mortality risk for this GI bleed?",
                    "Should this GI bleed patient be admitted to ICU?",
                    "What is the rebleeding risk?",
                    "Is this a high-risk upper GI bleed?",
                ),
                icd10_codes=(
                    "K92.0",   # Hematemesis
                    "K92.1",   # Melena
                    "K92.2",   # GI hemorrhage, unspecified
                    "K25.0",   # Gastric ulcer with hemorrhage
                    "K26.0",   # Duodenal ulcer with hemorrhage
                    "I85.01",  # Esophageal varices with bleeding
                ),
                keywords=(
                    "Rockall", "GI bleed", "upper GI bleeding", "UGIB",
                    "hematemesis", "melena", "mortality", "rebleeding",
                    "peptic ulcer", "endoscopy",
                )
            ),
            references=(
                Reference(
                    citation="Rockall TA, Logan RF, Devlin HB, Northfield TC. "
                             "Risk assessment after acute upper gastrointestinal haemorrhage. "
                             "Gut. 1996;38(3):316-321.",
                    doi="10.1136/gut.38.3.316",
                    pmid="8675081",
                    year=1996
                ),
            ),
            version="1.0.0",
            validation_status="validated"
        )

    def calculate(
        self,
        age_years: int,
        shock_status: Literal["none", "tachycardia", "hypotension"],
        comorbidity: Literal["none", "cardiac_major", "renal_liver_malignancy"],
        diagnosis: Literal["mallory_weiss_no_lesion", "other_diagnosis", "gi_malignancy"],
        stigmata_of_recent_hemorrhage: Literal["none_or_dark_spot", "blood_clot_visible_vessel"]
    ) -> ScoreResult:
        """
        Calculate Full Rockall Score.

        Args:
            age_years: Patient age in years
            shock_status: Hemodynamic status
                - "none": Pulse <100, SBP ≥100
                - "tachycardia": Pulse ≥100, SBP ≥100
                - "hypotension": SBP <100
            comorbidity: Comorbid conditions
                - "none": No major comorbidity
                - "cardiac_major": CHF, IHD, or any major comorbidity
                - "renal_liver_malignancy": Renal failure, liver failure, or disseminated malignancy
            diagnosis: Endoscopic diagnosis
                - "mallory_weiss_no_lesion": Mallory-Weiss tear, no lesion, or no SRH
                - "other_diagnosis": All other diagnoses (peptic ulcer, erosive disease, etc.)
                - "gi_malignancy": Upper GI malignancy
            stigmata_of_recent_hemorrhage: Endoscopic findings
                - "none_or_dark_spot": None, or dark spot only
                - "blood_clot_visible_vessel": Blood in upper GI, adherent clot, visible vessel

        Returns:
            ScoreResult with Rockall score and mortality/rebleeding risk
        """
        # Calculate age points
        if age_years >= 80:
            age_points = 2
        elif age_years >= 60:
            age_points = 1
        else:
            age_points = 0

        # Shock points
        shock_points_map = {
            "none": 0,
            "tachycardia": 1,
            "hypotension": 2
        }
        shock_points = shock_points_map[shock_status]

        # Comorbidity points
        comorbidity_points_map = {
            "none": 0,
            "cardiac_major": 2,
            "renal_liver_malignancy": 3
        }
        comorbidity_points = comorbidity_points_map[comorbidity]

        # Diagnosis points
        diagnosis_points_map = {
            "mallory_weiss_no_lesion": 0,
            "other_diagnosis": 1,
            "gi_malignancy": 2
        }
        diagnosis_points = diagnosis_points_map[diagnosis]

        # Stigmata points
        stigmata_points_map = {
            "none_or_dark_spot": 0,
            "blood_clot_visible_vessel": 2
        }
        stigmata_points = stigmata_points_map[stigmata_of_recent_hemorrhage]

        # Total score (Full Rockall)
        score = age_points + shock_points + comorbidity_points + diagnosis_points + stigmata_points

        # Pre-endoscopy score (Clinical Rockall)
        clinical_score = age_points + shock_points + comorbidity_points

        # Get risks
        mortality_risk, rebleed_risk = self._get_risks(score)

        # Get interpretation
        interpretation = self._get_interpretation(score, mortality_risk, rebleed_risk)

        return ScoreResult(
            value=float(score),
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "age_years": age_years,
                "shock_status": shock_status,
                "comorbidity": comorbidity,
                "diagnosis": diagnosis,
                "stigmata_of_recent_hemorrhage": stigmata_of_recent_hemorrhage
            },
            calculation_details={
                "total_score": score,
                "clinical_score_pre_endoscopy": clinical_score,
                "max_possible": 11,
                "component_scores": {
                    "age": age_points,
                    "shock": shock_points,
                    "comorbidity": comorbidity_points,
                    "diagnosis": diagnosis_points,
                    "stigmata": stigmata_points
                },
                "mortality_risk": f"{mortality_risk}%",
                "rebleed_risk": f"{rebleed_risk}%"
            },
            notes=self._get_notes(score, clinical_score)
        )

    def _get_risks(self, score: int) -> tuple[float, float]:
        """
        Get mortality and rebleeding risk.

        Returns:
            Tuple of (mortality %, rebleed %)
        """
        # Mortality data from Rockall 1996
        mortality_table = {
            0: 0.0,
            1: 0.0,
            2: 0.2,
            3: 2.9,
            4: 5.3,
            5: 10.8,
            6: 17.3,
            7: 27.0
        }

        # Rebleeding data
        rebleed_table = {
            0: 4.9,
            1: 3.4,
            2: 5.3,
            3: 11.2,
            4: 14.1,
            5: 24.1,
            6: 32.9,
            7: 43.8
        }

        if score >= 8:
            return (41.1, 41.8)

        return (
            mortality_table.get(score, 41.1),
            rebleed_table.get(score, 41.8)
        )

    def _get_interpretation(
        self,
        score: int,
        mortality: float,
        rebleed: float
    ) -> Interpretation:
        """Get clinical interpretation based on score"""

        if score <= 2:
            return Interpretation(
                summary=f"Low Risk GI Bleed (Rockall {score})",
                detail=f"Mortality: {mortality}%. Rebleeding: {rebleed}%.",
                severity=Severity.MILD,
                risk_level=RiskLevel.LOW,
                stage="Low Risk",
                stage_description=f"Rockall {score}",
                recommendations=(
                    "May be suitable for early discharge",
                    "Consider outpatient follow-up",
                    "PPI therapy",
                    "Eradicate H. pylori if present",
                ),
                next_steps=(
                    "Complete endoscopy if not done",
                    "Outpatient follow-up in 2-4 weeks",
                    "Dietary counseling",
                )
            )
        elif score <= 4:
            return Interpretation(
                summary=f"Intermediate Risk GI Bleed (Rockall {score})",
                detail=f"Mortality: {mortality}%. Rebleeding: {rebleed}%.",
                severity=Severity.MODERATE,
                risk_level=RiskLevel.INTERMEDIATE,
                stage="Intermediate Risk",
                stage_description=f"Rockall {score}",
                recommendations=(
                    "Hospital admission recommended",
                    "IV PPI therapy (infusion if high-risk stigmata)",
                    "NPO until stable",
                    "Blood transfusion as needed (threshold Hgb 7-8)",
                    "Repeat endoscopy if rebleeding",
                ),
                warnings=(
                    "Monitor for signs of rebleeding",
                    "Type and screen/crossmatch available",
                ),
                next_steps=(
                    "Admission to monitored bed",
                    "GI consultation",
                    "Repeat labs in 6-12 hours",
                )
            )
        elif score <= 6:
            return Interpretation(
                summary=f"High Risk GI Bleed (Rockall {score})",
                detail=f"Mortality: {mortality}%. Rebleeding: {rebleed}%.",
                severity=Severity.MODERATE,
                risk_level=RiskLevel.HIGH,
                stage="High Risk",
                stage_description=f"Rockall {score}",
                recommendations=(
                    "ICU or step-down admission",
                    "Aggressive resuscitation",
                    "Urgent endoscopy with intervention",
                    "High-dose IV PPI (bolus + infusion)",
                    "Blood product support (pRBC, FFP, platelets)",
                    "Consider interventional radiology or surgery if failed endoscopy",
                ),
                warnings=(
                    "High mortality risk - escalate care early",
                    "Have blood products available",
                    "Consider IR or surgery backup",
                ),
                next_steps=(
                    "ICU admission",
                    "Urgent GI consult for repeat endoscopy",
                    "Multidisciplinary approach",
                )
            )
        else:  # score > 6
            return Interpretation(
                summary=f"Very High Risk GI Bleed (Rockall {score})",
                detail=f"Mortality: {mortality}%. Rebleeding: {rebleed}%.",
                severity=Severity.SEVERE,
                risk_level=RiskLevel.VERY_HIGH,
                stage="Very High Risk",
                stage_description=f"Rockall {score}",
                recommendations=(
                    "ICU admission mandatory",
                    "Aggressive resuscitation",
                    "Emergent endoscopy",
                    "Massive transfusion protocol if needed",
                    "Early surgical and IR consultation",
                    "Goals of care discussion with family",
                ),
                warnings=(
                    "Very high mortality risk (>25%)",
                    "Consider comfort measures if appropriate",
                    "Document advance directives",
                ),
                next_steps=(
                    "Emergent intervention",
                    "Family meeting for prognosis discussion",
                    "Consider palliative care if futile",
                )
            )

    def _get_notes(self, score: int, clinical_score: int) -> list[str]:
        """Get clinical notes"""
        notes = [
            f"Clinical Rockall (pre-endoscopy): {clinical_score}",
            "Full Rockall score requires endoscopic findings",
        ]

        if score <= 2:
            notes.append(
                "Rockall ≤2: May be suitable for early discharge (within 24h)"
            )

        if clinical_score >= 3:
            notes.append(
                "High pre-endoscopy score: Consider urgent endoscopy"
            )

        notes.append(
            "Consider Glasgow-Blatchford Score (GBS) for need for intervention"
        )

        return notes

