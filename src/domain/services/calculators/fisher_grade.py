"""
Fisher Grade (Modified Fisher Scale)

The Fisher Grade is a radiological grading system that quantifies the amount
and distribution of subarachnoid blood on CT scan. It is the most reliable
predictor of vasospasm following aneurysmal subarachnoid hemorrhage.

Reference (Original Fisher Scale):
    Fisher CM, Kistler JP, Davis JM. Relation of cerebral vasospasm to
    subarachnoid hemorrhage visualized by computerized tomographic scanning.
    Neurosurgery. 1980;6(1):1-9.
    DOI: 10.1227/00006123-198001000-00001
    PMID: 7354892

Reference (Modified Fisher Scale):
    Frontera JA, Claassen J, Schmidt JM, et al. Prediction of symptomatic
    vasospasm after subarachnoid hemorrhage: the modified Fisher scale.
    Neurosurgery. 2006;59(1):21-27.
    DOI: 10.1227/01.NEU.0000218821.34014.1B
    PMID: 16823296

Clinical Notes:
- Original Fisher Scale: Grades 1-4
- Modified Fisher Scale: Grades 0-4, better predicts symptomatic vasospasm
- Higher grades correlate with increased vasospasm risk
- Vasospasm typically peaks 4-14 days post-hemorrhage
- Grade 3-4: Consider aggressive vasospasm monitoring/prophylaxis
"""


from typing import Any

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class FisherGradeCalculator(BaseCalculator):
    """
    Fisher Grade Calculator (Original and Modified)

    The Fisher Grade assesses subarachnoid hemorrhage severity on CT
    and predicts risk of cerebral vasospasm.

    Original Fisher Scale (1980):
    - Grade 1: No blood detected
    - Grade 2: Diffuse or thin layer <1mm thick
    - Grade 3: Localized clot and/or thick layer ≥1mm
    - Grade 4: Intracerebral or intraventricular clot with diffuse
               or no subarachnoid blood

    Modified Fisher Scale (2006):
    - Grade 0: No blood on CT
    - Grade 1: Thin SAH, no IVH
    - Grade 2: Thin SAH with IVH
    - Grade 3: Thick SAH, no IVH
    - Grade 4: Thick SAH with IVH

    Vasospasm Risk (Modified Fisher):
    - Grade 0-1: ~20% risk
    - Grade 2: ~30% risk
    - Grade 3: ~30-40% risk
    - Grade 4: ~40-50% risk
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="fisher_grade",
                name="Fisher Grade (Modified Fisher Scale)",
                purpose="Predict vasospasm risk in subarachnoid hemorrhage based on CT findings",
                input_params=["thick_sah", "ivh_present", "use_modified"],
                output_type="Fisher Grade (0-4) with vasospasm risk prediction"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.NEUROLOGY,
                    Specialty.NEUROSURGERY,
                    Specialty.CRITICAL_CARE,
                    Specialty.RADIOLOGY,
                ),
                conditions=(
                    "Subarachnoid Hemorrhage",
                    "SAH",
                    "Cerebral Vasospasm",
                    "Delayed Cerebral Ischemia",
                    "Aneurysmal SAH",
                    "Intracranial Hemorrhage",
                ),
                clinical_contexts=(
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "What is the vasospasm risk for this SAH patient?",
                    "How much blood is visible on the CT scan?",
                    "Should we initiate aggressive vasospasm monitoring?",
                    "What is the Modified Fisher Grade?",
                ),
                icd10_codes=("I60", "I60.9", "G45.8"),
                keywords=(
                    "Fisher", "Fisher Grade", "Modified Fisher", "SAH",
                    "subarachnoid", "vasospasm", "CT grading", "IVH",
                    "intraventricular hemorrhage", "delayed ischemia",
                )
            ),
            references=(
                Reference(
                    citation="Fisher CM, Kistler JP, Davis JM. Relation of cerebral "
                             "vasospasm to subarachnoid hemorrhage visualized by "
                             "computerized tomographic scanning. "
                             "Neurosurgery. 1980;6(1):1-9.",
                    doi="10.1227/00006123-198001000-00001",
                    pmid="7354892",
                    year=1980
                ),
                Reference(
                    citation="Frontera JA, Claassen J, Schmidt JM, et al. Prediction "
                             "of symptomatic vasospasm after subarachnoid hemorrhage: "
                             "the modified Fisher scale. Neurosurgery. 2006;59(1):21-27.",
                    doi="10.1227/01.NEU.0000218821.34014.1B",
                    pmid="16823296",
                    year=2006
                ),
            ),
            version="1.0.0",
            validation_status="validated"
        )

    def calculate(
        self,
        thick_sah: bool,
        ivh_present: bool = False,
        no_blood: bool = False,
        use_modified: bool = True,
    ) -> ScoreResult:
        """
        Calculate Fisher Grade (Original or Modified).

        Args:
            thick_sah: Thick subarachnoid hemorrhage (≥1mm layer) present
            ivh_present: Intraventricular hemorrhage (IVH) present
            no_blood: No blood visible on CT (Grade 0 or 1 depending on scale)
            use_modified: Use Modified Fisher Scale (default True, recommended)

        Returns:
            ScoreResult with Fisher Grade and vasospasm risk
        """
        if use_modified:
            grade = self._calculate_modified_fisher(thick_sah, ivh_present, no_blood)
            scale_name = "Modified Fisher Scale"
        else:
            grade = self._calculate_original_fisher(thick_sah, ivh_present, no_blood)
            scale_name = "Original Fisher Scale"

        interpretation = self._get_interpretation(grade, use_modified)

        return ScoreResult(
            value=grade,
            unit=Unit.GRADE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "thick_sah": thick_sah,
                "ivh_present": ivh_present,
                "no_blood": no_blood,
                "use_modified": use_modified,
            },
            calculation_details={
                "grade": grade,
                "scale": scale_name,
                "ct_findings": self._describe_ct_findings(thick_sah, ivh_present, no_blood),
                "vasospasm_risk": self._get_vasospasm_risk(grade, use_modified),
            },
        )

    def _calculate_modified_fisher(
        self, thick_sah: bool, ivh_present: bool, no_blood: bool
    ) -> int:
        """Calculate Modified Fisher Grade (0-4)"""
        if no_blood:
            return 0

        if thick_sah:
            return 4 if ivh_present else 3
        else:  # thin SAH
            return 2 if ivh_present else 1

    def _calculate_original_fisher(
        self, thick_sah: bool, ivh_present: bool, no_blood: bool
    ) -> int:
        """Calculate Original Fisher Grade (1-4)"""
        if no_blood:
            return 1

        # Original Fisher Grade 4: ICH or IVH with diffuse/no SAH
        if ivh_present and not thick_sah:
            return 4

        # Grade 3: Thick SAH
        if thick_sah:
            return 3

        # Grade 2: Thin SAH
        return 2

    def _describe_ct_findings(
        self, thick_sah: bool, ivh_present: bool, no_blood: bool
    ) -> str:
        """Describe CT findings in plain text"""
        if no_blood:
            return "No subarachnoid blood detected on CT"

        findings = []
        if thick_sah:
            findings.append("Thick subarachnoid hemorrhage (≥1mm layer)")
        else:
            findings.append("Thin subarachnoid hemorrhage (<1mm layer)")

        if ivh_present:
            findings.append("Intraventricular hemorrhage present")

        return "; ".join(findings)

    def _get_vasospasm_risk(self, grade: int, use_modified: bool) -> dict[str, str]:
        """Get vasospasm risk percentages"""
        risks: dict[int, dict[str, str]]
        if use_modified:
            risks = {
                0: {"symptomatic_vasospasm": "0%", "angiographic_vasospasm": "<10%"},
                1: {"symptomatic_vasospasm": "12-20%", "angiographic_vasospasm": "25-35%"},
                2: {"symptomatic_vasospasm": "21-27%", "angiographic_vasospasm": "35-45%"},
                3: {"symptomatic_vasospasm": "19-33%", "angiographic_vasospasm": "40-55%"},
                4: {"symptomatic_vasospasm": "40-50%", "angiographic_vasospasm": "55-70%"},
            }
        else:
            risks = {
                1: {"symptomatic_vasospasm": "3-7%", "angiographic_vasospasm": "15-25%"},
                2: {"symptomatic_vasospasm": "14-20%", "angiographic_vasospasm": "25-40%"},
                3: {"symptomatic_vasospasm": "33-40%", "angiographic_vasospasm": "50-70%"},
                4: {"symptomatic_vasospasm": "28-35%", "angiographic_vasospasm": "40-55%"},
            }
        return risks.get(grade, {})

    def _get_interpretation(self, grade: int, use_modified: bool) -> Interpretation:
        """Generate interpretation based on grade"""
        if use_modified:
            return self._interpret_modified_fisher(grade)
        else:
            return self._interpret_original_fisher(grade)

    def _interpret_modified_fisher(self, grade: int) -> Interpretation:
        """Interpret Modified Fisher Grade"""
        if grade == 0:
            return Interpretation(
                summary="Modified Fisher Grade 0 - No SAH on CT",
                detail="No subarachnoid blood detected on CT. If clinical suspicion "
                       "remains high, lumbar puncture is indicated.",
                severity=Severity.NORMAL,
                stage="Grade 0",
                stage_description="No SAH detected",
                recommendations=(
                    "Consider lumbar puncture if clinical suspicion for SAH remains high",
                    "Review clinical presentation and imaging",
                ),
                next_steps=(
                    "LP if SAH suspected (xanthochromia testing)",
                    "Consider alternative diagnoses",
                ),
            )
        elif grade == 1:
            return Interpretation(
                summary="Modified Fisher Grade 1 - Thin SAH without IVH",
                detail="Thin layer of subarachnoid blood (<1mm) without intraventricular "
                       "hemorrhage. Lower vasospasm risk (12-20%).",
                severity=Severity.MILD,
                stage="Grade 1",
                stage_description="Thin SAH, no IVH - lower vasospasm risk",
                recommendations=(
                    "Start nimodipine 60mg PO/NG q4h x 21 days",
                    "Daily TCD monitoring days 3-14",
                    "Standard ICU monitoring",
                    "Secure aneurysm within 72 hours",
                ),
                next_steps=(
                    "Aneurysm treatment (coiling/clipping)",
                    "Vasospasm surveillance",
                    "Serial neurological exams",
                ),
            )
        elif grade == 2:
            return Interpretation(
                summary="Modified Fisher Grade 2 - Thin SAH with IVH",
                detail="Thin subarachnoid hemorrhage with intraventricular extension. "
                       "Moderate vasospasm risk (21-27%). May require EVD.",
                severity=Severity.MODERATE,
                stage="Grade 2",
                stage_description="Thin SAH with IVH - moderate risk",
                recommendations=(
                    "Nimodipine 60mg q4h x 21 days",
                    "Consider EVD for hydrocephalus or ICP elevation",
                    "Daily TCD monitoring",
                    "Optimize cerebral perfusion pressure",
                ),
                warnings=(
                    "Higher vasospasm risk due to IVH",
                    "Watch for hydrocephalus",
                ),
                next_steps=(
                    "EVD placement if indicated",
                    "Aneurysm securing",
                    "Vasospasm monitoring",
                ),
            )
        elif grade == 3:
            return Interpretation(
                summary="Modified Fisher Grade 3 - Thick SAH without IVH",
                detail="Thick layer of subarachnoid hemorrhage (≥1mm) without IVH. "
                       "High vasospasm risk (30-40%). Aggressive monitoring required.",
                severity=Severity.SEVERE,
                stage="Grade 3",
                stage_description="Thick SAH, no IVH - high vasospasm risk",
                recommendations=(
                    "Nimodipine 60mg q4h x 21 days (mandatory)",
                    "TCD twice daily during vasospasm period (days 3-14)",
                    "Early aneurysm securing",
                    "Maintain euvolemia, avoid hypotension",
                    "Consider induced hypertension if symptomatic vasospasm",
                ),
                warnings=(
                    "High vasospasm risk (30-40%)",
                    "Peak risk days 4-14 post-hemorrhage",
                    "Delayed cerebral ischemia possible",
                ),
                next_steps=(
                    "Urgent aneurysm treatment",
                    "Aggressive TCD surveillance",
                    "Prepare for possible HHH therapy",
                ),
            )
        else:  # grade 4
            return Interpretation(
                summary="Modified Fisher Grade 4 - Thick SAH with IVH",
                detail="Thick subarachnoid hemorrhage with intraventricular extension. "
                       "Highest vasospasm risk (40-50%). Intensive monitoring essential.",
                severity=Severity.CRITICAL,
                stage="Grade 4",
                stage_description="Thick SAH with IVH - highest vasospasm risk",
                recommendations=(
                    "Nimodipine 60mg q4h x 21 days (mandatory)",
                    "TCD twice daily, CTA if velocities elevated",
                    "EVD strongly recommended for IVH/hydrocephalus",
                    "Early aneurysm treatment",
                    "Continuous EEG for ischemia detection",
                ),
                warnings=(
                    "Highest vasospasm risk (40-50%)",
                    "High risk for delayed cerebral ischemia",
                    "Hydrocephalus likely with IVH",
                ),
                next_steps=(
                    "EVD placement",
                    "Aneurysm securing",
                    "Intensive vasospasm surveillance",
                    "Consider continuous EEG",
                ),
            )

    def _interpret_original_fisher(self, grade: int) -> Interpretation:
        """Interpret Original Fisher Grade"""
        if grade == 1:
            return Interpretation(
                summary="Original Fisher Grade 1 - No blood detected",
                detail="No subarachnoid blood on CT. If SAH suspected, "
                       "lumbar puncture is indicated.",
                severity=Severity.NORMAL,
                stage="Grade 1",
                stage_description="No SAH on CT",
                recommendations=(
                    "Consider lumbar puncture if clinical suspicion remains",
                    "Routine monitoring if no SAH confirmed",
                ),
            )
        elif grade == 2:
            return Interpretation(
                summary="Original Fisher Grade 2 - Diffuse/thin SAH",
                detail="Thin layer of SAH (<1mm) present. Moderate vasospasm risk.",
                severity=Severity.MODERATE,
                stage="Grade 2",
                stage_description="Thin SAH - moderate vasospasm risk",
                recommendations=(
                    "Nimodipine 60mg q4h x 21 days",
                    "Daily TCD monitoring for vasospasm",
                    "Secure aneurysm",
                ),
            )
        elif grade == 3:
            return Interpretation(
                summary="Original Fisher Grade 3 - Localized clot or thick SAH",
                detail="Thick SAH (≥1mm) or localized clot. High vasospasm risk (33-40%).",
                severity=Severity.SEVERE,
                stage="Grade 3",
                stage_description="Thick SAH - high vasospasm risk",
                recommendations=(
                    "Nimodipine 60mg q4h x 21 days",
                    "TCD twice daily during vasospasm period",
                    "Early aneurysm securing",
                    "Aggressive vasospasm surveillance",
                ),
                warnings=(
                    "High vasospasm risk (33-40%)",
                ),
            )
        else:  # grade 4
            return Interpretation(
                summary="Original Fisher Grade 4 - ICH/IVH with diffuse or no SAH",
                detail="Intracerebral or intraventricular extension with diffuse "
                       "or minimal subarachnoid blood.",
                severity=Severity.SEVERE,
                stage="Grade 4",
                stage_description="ICH/IVH present",
                recommendations=(
                    "Consider EVD for hydrocephalus",
                    "Daily TCD monitoring",
                    "Manage ICP if elevated",
                    "Nimodipine for vasospasm prophylaxis",
                ),
                warnings=(
                    "Hydrocephalus may develop",
                    "Monitor for vasospasm despite less SAH",
                ),
            )
