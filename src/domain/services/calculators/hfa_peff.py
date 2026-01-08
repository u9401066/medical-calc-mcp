"""
HFA-PEFF Score - Heart Failure with Preserved Ejection Fraction Diagnostic Algorithm

The HFA-PEFF is a consensus-based diagnostic algorithm from the Heart Failure
Association (HFA) of the European Society of Cardiology (ESC) for diagnosing
heart failure with preserved ejection fraction (HFpEF).

Reference (Original):
    Pieske B, Tschöpe C, de Boer RA, et al. How to diagnose heart failure
    with preserved ejection fraction: the HFA-PEFF diagnostic algorithm:
    a consensus recommendation from the Heart Failure Association (HFA)
    of the European Society of Cardiology (ESC).
    Eur Heart J. 2019;40(40):3297-3317.
    DOI: 10.1093/eurheartj/ehz641
    PMID: 31504452

Reference (Full Publication):
    Pieske B, Tschöpe C, de Boer RA, et al. How to diagnose heart failure
    with preserved ejection fraction: the HFA-PEFF diagnostic algorithm.
    Eur J Heart Fail. 2020;22(3):391-412.
    DOI: 10.1002/ejhf.1741
    PMID: 32133741
"""

from typing import Optional

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class HFAPEFFCalculator(BaseCalculator):
    """
    HFA-PEFF Score Calculator

    Step 2 of HFA-PEFF algorithm (Echocardiographic and Natriuretic Peptide Score)

    Three domains scored:
    1. Functional domain (E/e' ratio, e' velocity)
    2. Morphological domain (LAVI, LVMI, LV wall thickness)
    3. Biomarker domain (NT-proBNP or BNP in sinus rhythm/AF)

    Each domain: Major criteria = 2 points, Minor criteria = 1 point

    Total score interpretation:
    - 0-1: HFpEF unlikely
    - 2-4: Intermediate - needs further workup
    - 5-6: HFpEF very likely
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="hfa_peff",
                name="HFA-PEFF Score (Heart Failure with Preserved Ejection Fraction)",
                purpose="Diagnose HFpEF using echocardiographic and biomarker criteria",
                input_params=[
                    "e_e_prime",
                    "septal_e_prime",
                    "lateral_e_prime",
                    "tr_velocity",
                    "lavi",
                    "lvmi",
                    "relative_wall_thickness",
                    "nt_probnp",
                    "bnp",
                    "atrial_fibrillation",
                ],
                output_type="Score (0-6) with HFpEF probability classification",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.CARDIOLOGY,
                    Specialty.INTERNAL_MEDICINE,
                ),
                conditions=(
                    "Heart Failure",
                    "HFpEF",
                    "Heart Failure with Preserved Ejection Fraction",
                    "Diastolic Heart Failure",
                    "Dyspnea",
                    "Unexplained Dyspnea",
                ),
                clinical_contexts=(
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.SCREENING,
                    ClinicalContext.RISK_STRATIFICATION,
                ),
                clinical_questions=(
                    "Does this patient have HFpEF?",
                    "Is unexplained dyspnea due to HFpEF?",
                    "How do I diagnose heart failure with preserved EF?",
                    "Should I do further testing for HFpEF?",
                ),
                icd10_codes=("I50.3", "I50.30", "I50.31", "I50.32", "I50.33"),
                keywords=(
                    "HFA-PEFF",
                    "HFpEF",
                    "diastolic heart failure",
                    "preserved ejection fraction",
                    "E/e'",
                    "LAVI",
                    "NT-proBNP",
                    "BNP",
                    "diastolic dysfunction",
                ),
            ),
            references=(
                Reference(
                    citation="Pieske B, Tschöpe C, de Boer RA, et al. How to diagnose heart "
                    "failure with preserved ejection fraction: the HFA-PEFF diagnostic "
                    "algorithm. Eur Heart J. 2019;40(40):3297-3317.",
                    doi="10.1093/eurheartj/ehz641",
                    pmid="31504452",
                    year=2019,
                ),
                Reference(
                    citation="Pieske B, Tschöpe C, de Boer RA, et al. How to diagnose heart "
                    "failure with preserved ejection fraction: the HFA-PEFF diagnostic "
                    "algorithm. Eur J Heart Fail. 2020;22(3):391-412.",
                    doi="10.1002/ejhf.1741",
                    pmid="32133741",
                    year=2020,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        e_e_prime: Optional[float] = None,
        septal_e_prime: Optional[float] = None,
        lateral_e_prime: Optional[float] = None,
        tr_velocity: Optional[float] = None,
        lavi: Optional[float] = None,
        lvmi: Optional[float] = None,
        relative_wall_thickness: Optional[float] = None,
        nt_probnp: Optional[float] = None,
        bnp: Optional[float] = None,
        atrial_fibrillation: bool = False,
        sex: str = "male",
    ) -> ScoreResult:
        """
        Calculate HFA-PEFF score.

        Args:
            e_e_prime: E/e' ratio (average of septal and lateral)
            septal_e_prime: Septal e' velocity (cm/s)
            lateral_e_prime: Lateral e' velocity (cm/s)
            tr_velocity: Tricuspid regurgitation velocity (m/s)
            lavi: Left atrial volume index (mL/m²)
            lvmi: Left ventricular mass index (g/m²)
            relative_wall_thickness: Relative wall thickness
            nt_probnp: NT-proBNP level (pg/mL)
            bnp: BNP level (pg/mL)
            atrial_fibrillation: Whether patient is in AF
            sex: "male" or "female" (for LVMI thresholds)

        Returns:
            ScoreResult with HFA-PEFF score and interpretation
        """
        # Validate sex
        sex = sex.lower()
        if sex not in ("male", "female"):
            raise ValueError("Sex must be 'male' or 'female'")

        # Initialize domain scores
        functional_score = 0
        morphological_score = 0
        biomarker_score = 0

        functional_details: dict = {}
        morphological_details: dict = {}
        biomarker_details: dict = {}

        # FUNCTIONAL DOMAIN
        # Major criteria (2 points): E/e' ≥15 OR septal e' <7 OR lateral e' <10
        # Minor criteria (1 point): E/e' 9-14 OR septal e' 7-9 OR lateral e' 10-12

        functional_major = False
        functional_minor = False

        if e_e_prime is not None:
            if e_e_prime >= 15:
                functional_major = True
                functional_details["e_e_prime"] = {"value": e_e_prime, "criteria": "Major (≥15)"}
            elif 9 <= e_e_prime < 15:
                functional_minor = True
                functional_details["e_e_prime"] = {"value": e_e_prime, "criteria": "Minor (9-14)"}
            else:
                functional_details["e_e_prime"] = {"value": e_e_prime, "criteria": "Normal (<9)"}

        if septal_e_prime is not None:
            if septal_e_prime < 7:
                functional_major = True
                functional_details["septal_e_prime"] = {"value": septal_e_prime, "criteria": "Major (<7)"}
            elif septal_e_prime <= 9:
                functional_minor = True
                functional_details["septal_e_prime"] = {"value": septal_e_prime, "criteria": "Minor (7-9)"}
            else:
                functional_details["septal_e_prime"] = {"value": septal_e_prime, "criteria": "Normal (>9)"}

        if lateral_e_prime is not None:
            if lateral_e_prime < 10:
                functional_major = True
                functional_details["lateral_e_prime"] = {"value": lateral_e_prime, "criteria": "Major (<10)"}
            elif lateral_e_prime <= 12:
                functional_minor = True
                functional_details["lateral_e_prime"] = {"value": lateral_e_prime, "criteria": "Minor (10-12)"}
            else:
                functional_details["lateral_e_prime"] = {"value": lateral_e_prime, "criteria": "Normal (>12)"}

        if tr_velocity is not None:
            if tr_velocity > 2.8:
                functional_major = True
                functional_details["tr_velocity"] = {"value": tr_velocity, "criteria": "Major (>2.8)"}
            else:
                functional_details["tr_velocity"] = {"value": tr_velocity, "criteria": "Normal (≤2.8)"}

        if functional_major:
            functional_score = 2
        elif functional_minor:
            functional_score = 1

        # MORPHOLOGICAL DOMAIN
        # Major criteria (2 points): LAVI >34 AND (LVMI elevated OR RWT >0.42)
        # Minor criteria (1 point): LAVI 29-34 OR LVMI elevated OR RWT >0.42

        # LVMI thresholds: Male >115 g/m², Female >95 g/m²
        lvmi_threshold = 115 if sex == "male" else 95
        lvmi_elevated = lvmi is not None and lvmi > lvmi_threshold
        lavi_major = lavi is not None and lavi > 34
        lavi_minor = lavi is not None and 29 <= lavi <= 34
        rwt_elevated = relative_wall_thickness is not None and relative_wall_thickness > 0.42

        morphological_major = lavi_major and (lvmi_elevated or rwt_elevated)
        morphological_minor = lavi_minor or lvmi_elevated or rwt_elevated

        if lavi is not None:
            if lavi > 34:
                morphological_details["lavi"] = {"value": lavi, "criteria": "Major (>34)"}
            elif lavi >= 29:
                morphological_details["lavi"] = {"value": lavi, "criteria": "Minor (29-34)"}
            else:
                morphological_details["lavi"] = {"value": lavi, "criteria": "Normal (<29)"}

        if lvmi is not None:
            if lvmi > lvmi_threshold:
                morphological_details["lvmi"] = {"value": lvmi, "criteria": f"Elevated (>{lvmi_threshold} for {sex})"}
            else:
                morphological_details["lvmi"] = {"value": lvmi, "criteria": "Normal"}

        if relative_wall_thickness is not None:
            if relative_wall_thickness > 0.42:
                morphological_details["rwt"] = {"value": relative_wall_thickness, "criteria": "Elevated (>0.42)"}
            else:
                morphological_details["rwt"] = {"value": relative_wall_thickness, "criteria": "Normal (≤0.42)"}

        if morphological_major:
            morphological_score = 2
        elif morphological_minor:
            morphological_score = 1

        # BIOMARKER DOMAIN
        # Different thresholds for sinus rhythm vs AF

        if atrial_fibrillation:
            # AF thresholds
            nt_probnp_major = nt_probnp is not None and nt_probnp > 660
            nt_probnp_minor = nt_probnp is not None and 365 <= nt_probnp <= 660
            bnp_major = bnp is not None and bnp > 150
            bnp_minor = bnp is not None and 105 <= bnp <= 150
        else:
            # Sinus rhythm thresholds
            nt_probnp_major = nt_probnp is not None and nt_probnp > 220
            nt_probnp_minor = nt_probnp is not None and 125 <= nt_probnp <= 220
            bnp_major = bnp is not None and bnp > 80
            bnp_minor = bnp is not None and 35 <= bnp <= 80

        biomarker_major = nt_probnp_major or bnp_major
        biomarker_minor = nt_probnp_minor or bnp_minor

        rhythm_text = "AF" if atrial_fibrillation else "SR"
        if nt_probnp is not None:
            if atrial_fibrillation:
                if nt_probnp > 660:
                    biomarker_details["nt_probnp"] = {"value": nt_probnp, "criteria": f"Major (>660 in {rhythm_text})"}
                elif nt_probnp >= 365:
                    biomarker_details["nt_probnp"] = {"value": nt_probnp, "criteria": f"Minor (365-660 in {rhythm_text})"}
                else:
                    biomarker_details["nt_probnp"] = {"value": nt_probnp, "criteria": f"Normal (<365 in {rhythm_text})"}
            else:
                if nt_probnp > 220:
                    biomarker_details["nt_probnp"] = {"value": nt_probnp, "criteria": f"Major (>220 in {rhythm_text})"}
                elif nt_probnp >= 125:
                    biomarker_details["nt_probnp"] = {"value": nt_probnp, "criteria": f"Minor (125-220 in {rhythm_text})"}
                else:
                    biomarker_details["nt_probnp"] = {"value": nt_probnp, "criteria": f"Normal (<125 in {rhythm_text})"}

        if bnp is not None:
            if atrial_fibrillation:
                if bnp > 150:
                    biomarker_details["bnp"] = {"value": bnp, "criteria": f"Major (>150 in {rhythm_text})"}
                elif bnp >= 105:
                    biomarker_details["bnp"] = {"value": bnp, "criteria": f"Minor (105-150 in {rhythm_text})"}
                else:
                    biomarker_details["bnp"] = {"value": bnp, "criteria": f"Normal (<105 in {rhythm_text})"}
            else:
                if bnp > 80:
                    biomarker_details["bnp"] = {"value": bnp, "criteria": f"Major (>80 in {rhythm_text})"}
                elif bnp >= 35:
                    biomarker_details["bnp"] = {"value": bnp, "criteria": f"Minor (35-80 in {rhythm_text})"}
                else:
                    biomarker_details["bnp"] = {"value": bnp, "criteria": f"Normal (<35 in {rhythm_text})"}

        if biomarker_major:
            biomarker_score = 2
        elif biomarker_minor:
            biomarker_score = 1

        # TOTAL SCORE
        total_score = functional_score + morphological_score + biomarker_score

        # Determine probability category
        if total_score >= 5:
            category = "HFpEF Very Likely"
        elif total_score >= 2:
            category = "Intermediate - Further Workup Needed"
        else:
            category = "HFpEF Unlikely"

        # Get interpretation
        interpretation = self._get_interpretation(total_score, category, functional_score, morphological_score, biomarker_score)

        return ScoreResult(
            value=total_score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "e_e_prime": e_e_prime,
                "septal_e_prime": septal_e_prime,
                "lateral_e_prime": lateral_e_prime,
                "tr_velocity": tr_velocity,
                "lavi": lavi,
                "lvmi": lvmi,
                "relative_wall_thickness": relative_wall_thickness,
                "nt_probnp": nt_probnp,
                "bnp": bnp,
                "atrial_fibrillation": atrial_fibrillation,
                "sex": sex,
            },
            calculation_details={
                "domains": {
                    "functional": {
                        "score": functional_score,
                        "max": 2,
                        "details": functional_details,
                    },
                    "morphological": {
                        "score": morphological_score,
                        "max": 2,
                        "details": morphological_details,
                    },
                    "biomarker": {
                        "score": biomarker_score,
                        "max": 2,
                        "details": biomarker_details,
                    },
                },
                "total_score": total_score,
                "max_score": 6,
                "category": category,
            },
            formula_used="HFA-PEFF = Functional (0-2) + Morphological (0-2) + Biomarker (0-2)",
        )

    def _get_interpretation(self, score: int, category: str, functional: int, morphological: int, biomarker: int) -> Interpretation:
        """Get interpretation based on HFA-PEFF score"""

        domain_text = f"Functional={functional}, Morphological={morphological}, Biomarker={biomarker}"

        if score >= 5:
            return Interpretation(
                summary=f"HFA-PEFF {score}/6: HFpEF Very Likely",
                detail=f"Score ≥5 indicates HFpEF diagnosis can be established without "
                f"additional testing. Domain scores: {domain_text}. "
                f"Sensitivity ~90%, Specificity ~90% at cutoff ≥5.",
                severity=Severity.MODERATE,
                stage="Definite HFpEF",
                stage_description="Score 5-6: HFpEF can be diagnosed",
                recommendations=(
                    "HFpEF diagnosis confirmed",
                    "Consider Step 4: Search for specific HFpEF etiology",
                    "Etiologic workup may include:",
                    "- Cardiac MRI for infiltrative disease",
                    "- Genetic testing if appropriate",
                    "- Rule out specific causes (amyloidosis, HCM, etc.)",
                    "Initiate evidence-based HFpEF therapy",
                    "SGLT2 inhibitors are guideline-recommended",
                ),
                warnings=(
                    "Consider specific etiologies requiring targeted treatment",
                    "Screen for cardiac amyloidosis in appropriate patients",
                ),
                next_steps=(
                    "Establish HFpEF diagnosis",
                    "Search for specific etiology (Step 4)",
                    "Initiate guideline-directed therapy",
                ),
            )
        elif score >= 2:
            return Interpretation(
                summary=f"HFA-PEFF {score}/6: Intermediate - Further Testing Needed",
                detail=f"Score 2-4 requires additional functional testing (Step 3). "
                f"Domain scores: {domain_text}. "
                f"Consider diastolic stress test or invasive hemodynamics.",
                severity=Severity.MILD,
                stage="Intermediate",
                stage_description="Score 2-4: Needs functional testing",
                recommendations=(
                    "Proceed to Step 3: Functional Testing",
                    "Options include:",
                    "- Exercise stress echocardiography (preferred non-invasive)",
                    "- Diastolic stress test",
                    "- Invasive hemodynamic assessment (gold standard)",
                    "Step 3 criteria:",
                    "- E/e' ≥15 with exercise",
                    "- PCWP ≥15 at rest or ≥25 with exercise",
                ),
                warnings=(
                    "Do not exclude HFpEF based on intermediate score alone",
                    "Clinical judgment remains important",
                ),
                next_steps=(
                    "Exercise stress echo or hemodynamic testing",
                    "If positive: diagnose HFpEF",
                    "If negative: consider alternative diagnoses",
                ),
            )
        else:
            return Interpretation(
                summary=f"HFA-PEFF {score}/6: HFpEF Unlikely",
                detail=f"Score 0-1 suggests HFpEF is unlikely. Domain scores: {domain_text}. Consider alternative causes of symptoms.",
                severity=Severity.NORMAL,
                stage="HFpEF Unlikely",
                stage_description="Score 0-1: HFpEF unlikely",
                recommendations=(
                    "HFpEF unlikely based on current data",
                    "Consider alternative diagnoses for dyspnea:",
                    "- Pulmonary disease (COPD, ILD)",
                    "- Coronary artery disease",
                    "- Deconditioning",
                    "- Anemia",
                    "- Obesity",
                    "If clinical suspicion remains high, consider functional testing",
                ),
                next_steps=(
                    "Evaluate for alternative diagnoses",
                    "May consider functional testing if high clinical suspicion",
                ),
            )
