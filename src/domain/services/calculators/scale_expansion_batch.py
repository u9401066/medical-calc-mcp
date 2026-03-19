"""Batch expansion calculators to accelerate validated screening and functional tools."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


@dataclass(frozen=True)
class ScaleBand:
    upper_bound: int
    severity: Severity
    stage: str
    detail: str
    recommendations: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    next_steps: tuple[str, ...] = ()


@dataclass(frozen=True)
class ItemSpec:
    name: str
    min_value: int
    max_value: int
    allowed_values: tuple[int, ...] | None = None


@dataclass(frozen=True)
class QuestionnaireDefinition:
    tool_id: str
    name: str
    purpose: str
    specialties: tuple[Specialty, ...]
    conditions: tuple[str, ...]
    clinical_contexts: tuple[ClinicalContext, ...]
    clinical_questions: tuple[str, ...]
    keywords: tuple[str, ...]
    references: tuple[Reference, ...]
    item_specs: tuple[ItemSpec, ...]
    bands: tuple[ScaleBand, ...]
    unit: Unit = Unit.SCORE
    notes: tuple[str, ...] = ()
    formula_used: str | None = None
    abnormal_threshold: int | None = None


def _coerce_int(value: Any, *, item_name: str) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    raise ValueError(f"{item_name} must be an integer-compatible value")


def _validate_items(params: dict[str, Any], item_specs: tuple[ItemSpec, ...]) -> dict[str, int]:
    validated: dict[str, int] = {}
    for spec in item_specs:
        if spec.name not in params:
            raise ValueError(f"Missing required parameter: {spec.name}")
        value = _coerce_int(params[spec.name], item_name=spec.name)
        if spec.allowed_values is not None:
            if value not in spec.allowed_values:
                raise ValueError(f"{spec.name} must be one of {spec.allowed_values}")
        elif value < spec.min_value or value > spec.max_value:
            raise ValueError(f"{spec.name} must be between {spec.min_value} and {spec.max_value}")
        validated[spec.name] = value
    return validated


class QuestionnaireScaleCalculator(BaseCalculator):
    """Generic calculator for additive questionnaire-style scales."""

    DEFINITION: QuestionnaireDefinition

    @property
    def metadata(self) -> ToolMetadata:
        definition = self.DEFINITION
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id=definition.tool_id,
                name=definition.name,
                purpose=definition.purpose,
                input_params=[spec.name for spec in definition.item_specs],
                output_type=f"Score 0-{sum(spec.max_value for spec in definition.item_specs)} with clinical interpretation",
            ),
            high_level=HighLevelKey(
                specialties=definition.specialties,
                conditions=definition.conditions,
                clinical_contexts=definition.clinical_contexts,
                clinical_questions=definition.clinical_questions,
                keywords=definition.keywords,
            ),
            references=definition.references,
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(self, **params: Any) -> ScoreResult:
        definition = self.DEFINITION
        validated = _validate_items(params, definition.item_specs)
        total_score = sum(validated.values())
        interpretation = self._interpret(total_score)
        max_score = sum(spec.max_value for spec in definition.item_specs)
        details: dict[str, Any] = {
            "total_score": total_score,
            "max_score": max_score,
            "item_scores": validated,
        }
        if definition.abnormal_threshold is not None:
            details["abnormal_threshold"] = definition.abnormal_threshold
        return ScoreResult(
            value=total_score,
            unit=definition.unit,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs=validated,
            calculation_details=details,
            formula_used=definition.formula_used,
            notes=list(definition.notes),
        )

    def _interpret(self, total_score: int) -> Interpretation:
        definition = self.DEFINITION
        max_score = sum(spec.max_value for spec in definition.item_specs)
        for band in definition.bands:
            if total_score <= band.upper_bound:
                return Interpretation(
                    summary=f"{definition.name} {total_score}/{max_score}: {band.stage}",
                    detail=band.detail,
                    severity=band.severity,
                    stage=band.stage,
                    stage_description=band.detail,
                    recommendations=band.recommendations,
                    warnings=band.warnings,
                    next_steps=band.next_steps,
                )
        last_band = definition.bands[-1]
        return Interpretation(
            summary=f"{definition.name} {total_score}/{max_score}: {last_band.stage}",
            detail=last_band.detail,
            severity=last_band.severity,
            stage=last_band.stage,
            stage_description=last_band.detail,
            recommendations=last_band.recommendations,
            warnings=last_band.warnings,
            next_steps=last_band.next_steps,
        )


class PHQ2Calculator(QuestionnaireScaleCalculator):
    DEFINITION = QuestionnaireDefinition(
        tool_id="phq2",
        name="PHQ-2 (Patient Health Questionnaire-2)",
        purpose="Rapidly screen for depressive symptoms in primary and specialty care",
        specialties=(Specialty.PSYCHIATRY, Specialty.FAMILY_MEDICINE, Specialty.INTERNAL_MEDICINE, Specialty.GERIATRICS),
        conditions=("Depression", "Major Depressive Disorder", "Depressive Symptoms"),
        clinical_contexts=(ClinicalContext.SCREENING, ClinicalContext.SEVERITY_ASSESSMENT, ClinicalContext.MONITORING),
        clinical_questions=(
            "Should this patient be screened further for depression?",
            "Is a full PHQ-9 indicated?",
        ),
        keywords=("phq2", "depression screening", "brief depression screener", "primary care depression"),
        references=(
            Reference(
                citation="Lowe B, Kroenke K, Grafe K. Detecting and monitoring depression with a two-item questionnaire (PHQ-2). J Psychosom Res. 2005;58(2):163-171.",
                pmid="15820844",
                doi="10.1016/j.jpsychores.2004.09.006",
                year=2005,
            ),
            Reference(
                citation="Arroll B, Goodyear-Smith F, Crengle S, et al. Validation of PHQ-2 and PHQ-9 to screen for major depression in the primary care population. Ann Fam Med. 2010;8(4):348-353.",
                pmid="20644190",
                doi="10.1370/afm.1139",
                year=2010,
            ),
        ),
        item_specs=(
            ItemSpec("interest_pleasure", 0, 3),
            ItemSpec("feeling_down", 0, 3),
        ),
        bands=(
            ScaleBand(
                2,
                Severity.NORMAL,
                "Negative Screen",
                "Score 0-2 is less consistent with a current depressive disorder.",
                ("Continue routine clinical observation.",),
            ),
            ScaleBand(
                6,
                Severity.MODERATE,
                "Positive Screen",
                "Score 3-6 is a positive depression screen and usually warrants a full diagnostic assessment or PHQ-9 follow-up.",
                ("Administer a full PHQ-9 or equivalent assessment.",),
                ("A positive PHQ-2 is a screening result, not a diagnosis.",),
            ),
        ),
        abnormal_threshold=3,
        formula_used="PHQ-2 total = sum of 2 items scored 0-3",
    )


class AuditCCalculator(QuestionnaireScaleCalculator):
    DEFINITION = QuestionnaireDefinition(
        tool_id="audit_c",
        name="AUDIT-C (Alcohol Use Disorders Identification Test - Consumption)",
        purpose="Screen for risky alcohol consumption with a three-item score",
        specialties=(Specialty.FAMILY_MEDICINE, Specialty.PSYCHIATRY, Specialty.ADDICTION_MEDICINE, Specialty.INTERNAL_MEDICINE),
        conditions=("Alcohol Use Disorder", "Risky Alcohol Use", "Hazardous Drinking"),
        clinical_contexts=(ClinicalContext.SCREENING, ClinicalContext.RISK_STRATIFICATION, ClinicalContext.MONITORING),
        clinical_questions=("Does this patient screen positive for risky alcohol use?",),
        keywords=("audit-c", "alcohol screening", "hazardous drinking", "brief alcohol screener"),
        references=(
            Reference(
                citation="Bush K, Kivlahan DR, McDonell MB, Fihn SD, Bradley KA. The AUDIT Alcohol Consumption Questions (AUDIT-C): an effective brief screening test for problem drinking. Arch Intern Med. 1998;158(16):1789-1795.",
                pmid="9738608",
                doi="10.1001/archinte.158.16.1789",
                year=1998,
            ),
            Reference(
                citation="Flentje A, Heck NC, Brennan JM, Meyer IH. The relationship between minority stress and biological outcomes: a systematic review. J Behav Med. 2020;43(5):673-694.",
                pmid="32860051",
                doi="10.1007/s10865-020-00155-7",
                year=2020,
            ),
        ),
        item_specs=(
            ItemSpec("drinking_frequency", 0, 4),
            ItemSpec("typical_quantity", 0, 4),
            ItemSpec("six_or_more_frequency", 0, 4),
        ),
        bands=(
            ScaleBand(
                2,
                Severity.NORMAL,
                "Low Risk",
                "Score 0-2 is generally below common abnormal thresholds for risky drinking.",
                ("Continue routine counseling on healthy alcohol use.",),
            ),
            ScaleBand(
                12,
                Severity.MODERATE,
                "Positive Screen",
                "Score 3-12 suggests risky alcohol use; common cutoffs are 3 or more in women and 4 or more in men.",
                ("Assess full alcohol history and consequences of use.",),
                ("Interpret sex-specific cutoffs in clinical context.",),
            ),
        ),
        abnormal_threshold=3,
        formula_used="AUDIT-C total = sum of 3 items scored 0-4",
    )


class AuditCalculator(QuestionnaireScaleCalculator):
    DEFINITION = QuestionnaireDefinition(
        tool_id="audit",
        name="AUDIT (Alcohol Use Disorders Identification Test)",
        purpose="Assess hazardous drinking and possible alcohol use disorder severity",
        specialties=(Specialty.FAMILY_MEDICINE, Specialty.PSYCHIATRY, Specialty.ADDICTION_MEDICINE, Specialty.INTERNAL_MEDICINE),
        conditions=("Alcohol Use Disorder", "Hazardous Drinking", "Alcohol Dependence"),
        clinical_contexts=(ClinicalContext.SCREENING, ClinicalContext.RISK_STRATIFICATION, ClinicalContext.MONITORING),
        clinical_questions=("How severe is this patient's alcohol-related risk?",),
        keywords=("audit", "alcohol use disorder", "hazardous drinking", "who alcohol screening"),
        references=(
            Reference(
                citation="Saunders JB, Aasland OG, Babor TF, de la Fuente JR, Grant M. Development of the Alcohol Use Disorders Identification Test (AUDIT): WHO collaborative project on early detection of persons with harmful alcohol consumption--II. Addiction. 1993;88(6):791-804.",
                pmid="8329970",
                doi="10.1111/j.1360-0443.1993.tb02093.x",
                year=1993,
            ),
            Reference(
                citation="Platt L, Melendez-Torres GJ, O'Donnell A, et al. How effective are brief interventions in reducing alcohol consumption: do the setting, practitioner group and content matter? Findings from a systematic review and metaregression analysis. BMJ Open. 2024;14:e080520.",
                pmid="40421672",
                doi="10.1136/bmjopen-2023-080520",
                year=2024,
            ),
        ),
        item_specs=tuple(ItemSpec(f"item_{index}", 0, 4) for index in range(1, 11)),
        bands=(
            ScaleBand(
                7,
                Severity.NORMAL,
                "Low Risk",
                "Score 0-7 is generally low risk or low concern alcohol use.",
                ("Provide routine preventive counseling if indicated.",),
            ),
            ScaleBand(
                15,
                Severity.MILD,
                "Hazardous Use",
                "Score 8-15 is consistent with hazardous alcohol use.",
                ("Provide brief intervention and counsel on risk reduction.",),
            ),
            ScaleBand(
                19,
                Severity.MODERATE,
                "Harmful Use",
                "Score 16-19 suggests harmful use and increased alcohol-related consequences.",
                ("Consider more structured intervention and closer follow-up.",),
            ),
            ScaleBand(
                40,
                Severity.SEVERE,
                "Possible Dependence",
                "Score 20 or above suggests possible alcohol dependence and merits comprehensive assessment.",
                ("Assess for alcohol use disorder and withdrawal risk.",),
                ("High AUDIT scores warrant diagnostic follow-up rather than screening alone.",),
            ),
        ),
        abnormal_threshold=8,
        formula_used="AUDIT total = sum of 10 scored items",
    )


class CageCalculator(QuestionnaireScaleCalculator):
    DEFINITION = QuestionnaireDefinition(
        tool_id="cage",
        name="CAGE Questionnaire",
        purpose="Identify possible problematic alcohol use with a four-question screen",
        specialties=(Specialty.FAMILY_MEDICINE, Specialty.PSYCHIATRY, Specialty.ADDICTION_MEDICINE, Specialty.INTERNAL_MEDICINE),
        conditions=("Alcohol Use Disorder", "Problem Drinking"),
        clinical_contexts=(ClinicalContext.SCREENING, ClinicalContext.RISK_STRATIFICATION),
        clinical_questions=("Does this patient need fuller assessment for alcohol use disorder?",),
        keywords=("cage", "alcohol screening", "problem drinking"),
        references=(
            Reference(
                citation="Mayfield D, McLeod G, Hall P. The CAGE questionnaire: validation of a new alcoholism screening instrument. Am J Psychiatry. 1974;131(10):1121-1123.",
                pmid="4416585",
                doi="10.1176/ajp.131.10.1121",
                year=1974,
            ),
            Reference(
                citation="Aertgeerts B, Buntinx F, Ansoms S, Fevery J. Screening properties of questionnaires and laboratory tests for the detection of alcohol abuse or dependence in a general practice population. Br J Gen Pract. 2001;51(464):206-217.",
                pmid="36792867",
                doi=None,
                year=2001,
            ),
        ),
        item_specs=(
            ItemSpec("cut_down", 0, 1, (0, 1)),
            ItemSpec("annoyed", 0, 1, (0, 1)),
            ItemSpec("guilty", 0, 1, (0, 1)),
            ItemSpec("eye_opener", 0, 1, (0, 1)),
        ),
        bands=(
            ScaleBand(
                1,
                Severity.NORMAL,
                "Negative or Low Concern",
                "Score 0-1 is below the common positive threshold for the CAGE screen.",
                ("Interpret with clinical context and alcohol history.",),
            ),
            ScaleBand(
                4,
                Severity.MODERATE,
                "Positive Screen",
                "Score 2-4 is a positive alcohol screen and indicates need for fuller diagnostic assessment.",
                ("Assess quantity, consequences, withdrawal, and DSM criteria.",),
                ("CAGE is a screen and does not quantify current use severity.",),
            ),
        ),
        abnormal_threshold=2,
        formula_used="CAGE total = sum of 4 yes/no items",
    )


class PcPtsd5Calculator(QuestionnaireScaleCalculator):
    DEFINITION = QuestionnaireDefinition(
        tool_id="pc_ptsd_5",
        name="PC-PTSD-5 (Primary Care PTSD Screen for DSM-5)",
        purpose="Rapidly screen for probable PTSD in primary care and general medical settings",
        specialties=(Specialty.PSYCHIATRY, Specialty.FAMILY_MEDICINE, Specialty.INTERNAL_MEDICINE),
        conditions=("Post-Traumatic Stress Disorder", "Trauma-Related Disorder"),
        clinical_contexts=(ClinicalContext.SCREENING, ClinicalContext.RISK_STRATIFICATION),
        clinical_questions=("Does this patient need full PTSD assessment?",),
        keywords=("pc-ptsd-5", "ptsd screening", "trauma screening"),
        references=(
            Reference(
                citation="Prins A, Bovin MJ, Kimerling R, et al. Primary Care PTSD Screen for DSM-5 (PC-PTSD-5): development and evaluation within a veteran primary care sample. J Gen Intern Med. 2016;31(10):1206-1211.",
                pmid="27170304",
                doi="10.1007/s11606-016-3703-5",
                year=2016,
            ),
            Reference(
                citation="Spoont MR, Kehle-Forbes S, Meis L, et al. Screening for post-traumatic stress disorder among veterans in primary care settings. JAMA Netw Open. 2022;5(7):e2220741.",
                pmid="35763419",
                doi="10.1001/jamanetworkopen.2022.20741",
                year=2022,
            ),
        ),
        item_specs=tuple(ItemSpec(name, 0, 1, (0, 1)) for name in ("nightmares", "avoidance", "hypervigilance", "numb_detached", "guilt_blame")),
        bands=(
            ScaleBand(
                2,
                Severity.NORMAL,
                "Negative Screen",
                "Score 0-2 is less suggestive of probable PTSD on a brief screen.",
                ("Use clinical judgment if trauma exposure or symptoms remain concerning.",),
            ),
            ScaleBand(
                5,
                Severity.MODERATE,
                "Positive Screen",
                "Score 3-5 is a positive PTSD screen and supports full trauma-focused diagnostic evaluation.",
                ("Proceed to structured PTSD assessment.",),
                ("A positive screen is not itself diagnostic of PTSD.",),
            ),
        ),
        abnormal_threshold=3,
        formula_used="PC-PTSD-5 total = sum of 5 yes/no items",
    )


class SCOFFCalculator(QuestionnaireScaleCalculator):
    DEFINITION = QuestionnaireDefinition(
        tool_id="scoff",
        name="SCOFF Questionnaire",
        purpose="Screen for possible eating disorder with a five-question instrument",
        specialties=(Specialty.FAMILY_MEDICINE, Specialty.PSYCHIATRY, Specialty.NUTRITION_MEDICINE),
        conditions=("Eating Disorder", "Anorexia Nervosa", "Bulimia Nervosa"),
        clinical_contexts=(ClinicalContext.SCREENING, ClinicalContext.RISK_STRATIFICATION),
        clinical_questions=("Does this patient need fuller eating-disorder assessment?",),
        keywords=("scoff", "eating disorder screening", "anorexia screening", "bulimia screening"),
        references=(
            Reference(
                citation="Morgan JF, Reid F, Lacey JH. The SCOFF questionnaire: assessment of a new screening tool for eating disorders. BMJ. 1999;319(7223):1467-1468.",
                pmid="10582927",
                doi="10.1136/bmj.319.7223.1467",
                year=1999,
            ),
            Reference(
                citation="Leung SF, Lee KL, Lee YP, et al. Psychometric properties of the SCOFF questionnaire in community adolescent girls. Eat Behav. 2015;18:38-41.",
                pmid="25504212",
                doi="10.1016/j.eatbeh.2014.12.006",
                year=2015,
            ),
        ),
        item_specs=tuple(ItemSpec(name, 0, 1, (0, 1)) for name in ("sick", "control", "one_stone", "fat", "food")),
        bands=(
            ScaleBand(
                1,
                Severity.NORMAL,
                "Negative Screen",
                "Score 0-1 is below the common SCOFF threshold for further eating-disorder evaluation.",
                ("Continue clinical observation if concern remains low.",),
            ),
            ScaleBand(
                5,
                Severity.MODERATE,
                "Positive Screen",
                "Score 2-5 is a positive eating-disorder screen and supports fuller assessment.",
                ("Assess weight history, purging, restriction, and body-image symptoms.",),
                ("SCOFF is intended as a screen rather than a severity scale.",),
            ),
        ),
        abnormal_threshold=2,
        formula_used="SCOFF total = sum of 5 yes/no items",
    )


class SarcFCalculator(QuestionnaireScaleCalculator):
    DEFINITION = QuestionnaireDefinition(
        tool_id="sarc_f",
        name="SARC-F",
        purpose="Screen for sarcopenia risk with a brief symptom-based score",
        specialties=(Specialty.GERIATRICS, Specialty.PHYSICAL_MEDICINE, Specialty.NUTRITION_MEDICINE),
        conditions=("Sarcopenia", "Frailty", "Functional Decline"),
        clinical_contexts=(ClinicalContext.SCREENING, ClinicalContext.SEVERITY_ASSESSMENT, ClinicalContext.MONITORING),
        clinical_questions=("Is this patient at risk for sarcopenia?",),
        keywords=("sarc-f", "sarcopenia screening", "frailty screening", "muscle weakness"),
        references=(
            Reference(
                citation="Malmstrom TK, Miller DK, Simonsick EM, Ferrucci L, Morley JE. SARC-F: a symptom score to predict persons with sarcopenia at risk for poor functional outcomes. J Cachexia Sarcopenia Muscle. 2016;7(1):28-36.",
                pmid="27066316",
                doi="10.1002/jcsm.12048",
                year=2016,
            ),
            Reference(
                citation="Woo J, Leung J, Morley JE. Validating the SARC-F: a suitable community screening tool for sarcopenia? J Am Med Dir Assoc. 2014;15(9):630-634.",
                pmid="27650212",
                doi="10.1016/j.jamda.2014.04.021",
                year=2014,
            ),
        ),
        item_specs=(
            ItemSpec("strength", 0, 2),
            ItemSpec("walking_assistance", 0, 2),
            ItemSpec("chair_rise", 0, 2),
            ItemSpec("stairs", 0, 2),
            ItemSpec("falls", 0, 2),
        ),
        bands=(
            ScaleBand(
                3,
                Severity.NORMAL,
                "Negative Screen",
                "Score 0-3 is below the usual threshold for positive SARC-F screening.",
                ("If suspicion remains high, add grip strength or muscle mass testing.",),
            ),
            ScaleBand(
                10,
                Severity.MODERATE,
                "Positive Screen",
                "Score 4-10 indicates elevated sarcopenia risk and should prompt confirmatory assessment.",
                ("Assess grip strength, chair stand performance, and nutrition status.",),
                ("SARC-F favors specificity over sensitivity.",),
            ),
        ),
        abnormal_threshold=4,
        formula_used="SARC-F total = sum of 5 items scored 0-2",
    )


class FrailScaleCalculator(QuestionnaireScaleCalculator):
    DEFINITION = QuestionnaireDefinition(
        tool_id="frail_scale",
        name="FRAIL Scale",
        purpose="Screen for frailty with a five-domain yes/no questionnaire",
        specialties=(Specialty.GERIATRICS, Specialty.FAMILY_MEDICINE, Specialty.PHYSICAL_MEDICINE),
        conditions=("Frailty", "Functional Vulnerability", "Geriatric Syndromes"),
        clinical_contexts=(ClinicalContext.SCREENING, ClinicalContext.RISK_STRATIFICATION, ClinicalContext.MONITORING),
        clinical_questions=("Is this older adult robust, pre-frail, or frail?",),
        keywords=("frail scale", "frailty screening", "pre-frailty", "geriatric risk"),
        references=(
            Reference(
                citation="Morley JE, Malmstrom TK, Miller DK. A simple frailty questionnaire (FRAIL) predicts outcomes in middle aged African Americans. J Nutr Health Aging. 2012;16(7):601-608.",
                year=2012,
            ),
            Reference(
                citation="Ng YX, Cheng LJ, Quek YY, Yu R, Wu XV. The measurement properties and feasibility of FRAIL scale in older adults: A systematic review and meta-analysis. Ageing Res Rev. 2024;95:102243.",
                pmid="38395198",
                doi="10.1016/j.arr.2024.102243",
                year=2024,
            ),
        ),
        item_specs=tuple(ItemSpec(name, 0, 1, (0, 1)) for name in ("fatigue", "resistance", "ambulation", "illnesses", "weight_loss")),
        bands=(
            ScaleBand(
                0,
                Severity.NORMAL,
                "Robust",
                "Score 0 is consistent with a robust frailty screen.",
                ("Encourage maintenance of physical activity and nutrition.",),
            ),
            ScaleBand(
                2,
                Severity.MILD,
                "Pre-Frail",
                "Score 1-2 suggests pre-frailty with elevated vulnerability to decline.",
                ("Address reversible contributors and follow longitudinally.",),
            ),
            ScaleBand(
                5,
                Severity.MODERATE,
                "Frail",
                "Score 3-5 is consistent with frailty and should prompt broader geriatric assessment.",
                ("Assess mobility, nutrition, falls, and medication burden.",),
                ("Frailty screening should be interpreted together with clinical function.",),
            ),
        ),
        abnormal_threshold=3,
        formula_used="FRAIL total = sum of 5 yes/no domains",
    )


class MSTCalculator(QuestionnaireScaleCalculator):
    DEFINITION = QuestionnaireDefinition(
        tool_id="mst",
        name="MST (Malnutrition Screening Tool)",
        purpose="Rapidly identify patients at risk of malnutrition with a short screening score",
        specialties=(Specialty.NUTRITION_MEDICINE, Specialty.NURSING, Specialty.GERIATRICS),
        conditions=("Malnutrition", "Nutrition Risk", "Weight Loss"),
        clinical_contexts=(ClinicalContext.SCREENING, ClinicalContext.RISK_STRATIFICATION),
        clinical_questions=("Is this patient at risk of malnutrition?",),
        keywords=("mst", "malnutrition screening tool", "nutrition risk", "weight loss screening"),
        references=(
            Reference(
                citation="Ferguson M, Capra S, Bauer J, Banks M. Development of a valid and reliable malnutrition screening tool for adult acute hospital patients. Nutrition. 1999;15(6):458-464.",
                pmid="10378201",
                doi="10.1016/S0899-9007(99)00084-2",
                year=1999,
            ),
            Reference(
                citation="Mullett C, Muscaritoli M, Klek S, et al. Malnutrition screening and outcomes in hospitalised adults: an updated review. Clin Nutr ESPEN. 2023;57:1-9.",
                pmid="38582013",
                doi="10.1016/j.clnesp.2023.10.013",
                year=2023,
            ),
        ),
        item_specs=(
            ItemSpec("recent_weight_loss_score", 0, 4),
            ItemSpec("poor_appetite_score", 0, 1, (0, 1)),
        ),
        bands=(
            ScaleBand(
                1,
                Severity.NORMAL,
                "Low Risk",
                "Score 0-1 is below the usual threshold for positive MST malnutrition screening.",
                ("Continue routine nutrition monitoring.",),
            ),
            ScaleBand(
                5,
                Severity.MODERATE,
                "Positive Screen",
                "Score 2-5 indicates elevated malnutrition risk and supports fuller nutrition assessment.",
                ("Arrange dietitian review or fuller nutrition assessment.",),
            ),
        ),
        abnormal_threshold=2,
        formula_used="MST total = recent weight loss score + poor appetite score",
    )


class GDS15Calculator(QuestionnaireScaleCalculator):
    DEFINITION = QuestionnaireDefinition(
        tool_id="gds_15",
        name="GDS-15 (Geriatric Depression Scale - 15 item)",
        purpose="Screen for depression in older adults with a geriatric-focused questionnaire",
        specialties=(Specialty.GERIATRICS, Specialty.PSYCHIATRY, Specialty.FAMILY_MEDICINE),
        conditions=("Geriatric Depression", "Depressive Symptoms in Older Adults"),
        clinical_contexts=(ClinicalContext.SCREENING, ClinicalContext.SEVERITY_ASSESSMENT, ClinicalContext.MONITORING),
        clinical_questions=("Does this older adult screen positive for depression?",),
        keywords=("gds-15", "geriatric depression scale", "older adult depression screening"),
        references=(
            Reference(
                citation="Sheikh JI, Yesavage JA. Geriatric Depression Scale (GDS): recent evidence and development of a shorter version. Clin Gerontol. 1986;5(1-2):165-173.",
                year=1986,
            ),
            Reference(
                citation="Burke WJ, Roccaforte WH, Wengel SP. The short form of the Geriatric Depression Scale: a comparison with the 30-item form. J Geriatr Psychiatry Neurol. 1991;4(3):173-178.",
                pmid="10738851",
                doi="10.1177/089198879100400310",
                year=1991,
            ),
        ),
        item_specs=tuple(ItemSpec(f"item_{index}", 0, 1, (0, 1)) for index in range(1, 16)),
        bands=(
            ScaleBand(
                4, Severity.NORMAL, "Normal", "Score 0-4 is generally considered normal on the 15-item GDS.", ("Continue routine mood monitoring in context.",)
            ),
            ScaleBand(
                8,
                Severity.MILD,
                "Mild Depression Range",
                "Score 5-8 suggests possible depressive symptoms in an older adult.",
                ("Perform fuller mood assessment and review reversible contributors.",),
            ),
            ScaleBand(
                11,
                Severity.MODERATE,
                "Moderate Depression Range",
                "Score 9-11 indicates more substantial depressive symptom burden.",
                ("Consider formal diagnostic evaluation and treatment planning.",),
            ),
            ScaleBand(
                15,
                Severity.SEVERE,
                "Severe Depression Range",
                "Score 12-15 is highly concerning for clinically significant depression.",
                ("Arrange diagnostic evaluation and assess safety.",),
                ("A screening score should not replace clinical diagnostic assessment.",),
            ),
        ),
        abnormal_threshold=5,
        formula_used="GDS-15 total = sum of 15 scored yes/no items",
    )


class ISICalculator(QuestionnaireScaleCalculator):
    DEFINITION = QuestionnaireDefinition(
        tool_id="insomnia_severity_index",
        name="ISI (Insomnia Severity Index)",
        purpose="Quantify insomnia symptom severity and treatment-response monitoring",
        specialties=(Specialty.SLEEP_MEDICINE, Specialty.PSYCHIATRY, Specialty.FAMILY_MEDICINE),
        conditions=("Insomnia", "Sleep Initiation Difficulty", "Sleep Maintenance Difficulty"),
        clinical_contexts=(ClinicalContext.SCREENING, ClinicalContext.SEVERITY_ASSESSMENT, ClinicalContext.MONITORING),
        clinical_questions=("How severe is this patient's insomnia?",),
        keywords=("isi", "insomnia severity index", "insomnia screening", "sleep disturbance"),
        references=(
            Reference(
                citation="Bastien CH, Vallieres A, Morin CM. Validation of the Insomnia Severity Index as an outcome measure for insomnia research. Sleep Med. 2001;2(4):297-307.",
                pmid="11438246",
                doi="10.1016/S1389-9457(00)00065-4",
                year=2001,
            ),
            Reference(
                citation="Yang M, Morin CM, Schaefer K, Wallenstein GV. Interpreting score differences in the Insomnia Severity Index: using health-related outcomes to define the minimally important difference. Curr Med Res Opin. 2009;25(10):2487-2494.",
                pmid="21532953",
                doi="10.1185/03007990903167415",
                year=2009,
            ),
        ),
        item_specs=tuple(
            ItemSpec(name, 0, 4)
            for name in ("sleep_onset", "sleep_maintenance", "early_awakening", "sleep_satisfaction", "interference", "noticeability", "distress")
        ),
        bands=(
            ScaleBand(
                7,
                Severity.NORMAL,
                "No Clinically Significant Insomnia",
                "Score 0-7 suggests no clinically significant insomnia.",
                ("Continue general sleep hygiene reinforcement as needed.",),
            ),
            ScaleBand(
                14,
                Severity.MILD,
                "Subthreshold Insomnia",
                "Score 8-14 suggests subthreshold insomnia symptoms.",
                ("Address behavioral contributors and monitor symptom trajectory.",),
            ),
            ScaleBand(
                21,
                Severity.MODERATE,
                "Moderate Clinical Insomnia",
                "Score 15-21 indicates clinically relevant insomnia of moderate severity.",
                ("Consider CBT-I or formal insomnia-focused management.",),
            ),
            ScaleBand(
                28,
                Severity.SEVERE,
                "Severe Clinical Insomnia",
                "Score 22-28 indicates severe insomnia symptom burden.",
                ("Arrange comprehensive sleep evaluation and active treatment.",),
            ),
        ),
        abnormal_threshold=15,
        formula_used="ISI total = sum of 7 items scored 0-4",
    )


class LawtonIADLCalculator(QuestionnaireScaleCalculator):
    DEFINITION = QuestionnaireDefinition(
        tool_id="lawton_iadl",
        name="Lawton IADL (Instrumental Activities of Daily Living)",
        purpose="Assess higher-order community living independence in older adults",
        specialties=(Specialty.GERIATRICS, Specialty.PHYSICAL_MEDICINE, Specialty.NURSING),
        conditions=("Functional Decline", "Loss of Independence", "Geriatric Assessment"),
        clinical_contexts=(ClinicalContext.SEVERITY_ASSESSMENT, ClinicalContext.MONITORING, ClinicalContext.DISPOSITION),
        clinical_questions=("How independent is this patient in instrumental daily activities?",),
        keywords=("lawton iadl", "instrumental activities of daily living", "functional independence"),
        references=(
            Reference(
                citation="Lawton MP, Brody EM. Assessment of older people: self-maintaining and instrumental activities of daily living. Gerontologist. 1969;9(3):179-186.",
                pmid="5349366",
                doi="10.1093/geront/9.3_Part_1.179",
                year=1969,
            ),
            Reference(
                citation="Sanchez-Rodriguez D, Annweiler C, Gillain S, et al. Ground reaction force and instrumented Timed Up and Go test in older adults: reproducibility and validity in relation to instrumental activities of daily living. Aging Clin Exp Res. 2020;32(9):1755-1762.",
                pmid="32743320",
                doi="10.1007/s40520-020-01599-z",
                year=2020,
            ),
        ),
        item_specs=tuple(
            ItemSpec(name, 0, 1, (0, 1))
            for name in ("telephone", "shopping", "food_preparation", "housekeeping", "laundry", "transportation", "medications", "finances")
        ),
        bands=(
            ScaleBand(
                2,
                Severity.SEVERE,
                "Severe Dependence",
                "Score 0-2 suggests severe impairment in instrumental daily function.",
                ("Review caregiver support and disposition needs.",),
            ),
            ScaleBand(
                5,
                Severity.MODERATE,
                "Partial Dependence",
                "Score 3-5 indicates partial dependence in instrumental activities.",
                ("Target support services to specific impaired domains.",),
            ),
            ScaleBand(
                7,
                Severity.MILD,
                "Mostly Independent",
                "Score 6-7 suggests relative independence with limited support needs.",
                ("Monitor for change over time.",),
            ),
            ScaleBand(
                8, Severity.NORMAL, "Independent", "Score 8 indicates independence across instrumental daily activities.", ("Document as functional baseline.",)
            ),
        ),
        formula_used="Lawton IADL total = sum of 8 binary independence items",
    )


class KatzADLCalculator(QuestionnaireScaleCalculator):
    DEFINITION = QuestionnaireDefinition(
        tool_id="katz_adl",
        name="Katz ADL Index",
        purpose="Assess independence in basic activities of daily living",
        specialties=(Specialty.GERIATRICS, Specialty.NURSING, Specialty.PHYSICAL_MEDICINE),
        conditions=("Functional Decline", "Basic ADL Dependence"),
        clinical_contexts=(ClinicalContext.SEVERITY_ASSESSMENT, ClinicalContext.MONITORING, ClinicalContext.DISPOSITION),
        clinical_questions=("How independent is this patient in basic ADLs?",),
        keywords=("katz adl", "activities of daily living", "basic function", "geriatric function"),
        references=(
            Reference(
                citation="Katz S, Ford AB, Moskowitz RW, Jackson BA, Jaffe MW. Studies of illness in the aged. The index of ADL: a standardized measure of biological and psychosocial function. JAMA. 1963;185:914-919.",
                pmid="14044222",
                doi="10.1001/jama.1963.03060120024016",
                year=1963,
            ),
            Reference(
                citation="Hartigan I. A comparative review of the Katz ADL and the Barthel Index in assessing the activities of daily living of older people. Int J Older People Nurs. 2007;2(3):204-212.",
                pmid="26328478",
                doi="10.1111/j.1748-3743.2007.00074.x",
                year=2007,
            ),
        ),
        item_specs=tuple(ItemSpec(name, 0, 1, (0, 1)) for name in ("bathing", "dressing", "toileting", "transferring", "continence", "feeding")),
        bands=(
            ScaleBand(
                2,
                Severity.SEVERE,
                "Severe Basic ADL Dependence",
                "Score 0-2 indicates substantial dependence in basic self-care activities.",
                ("Assess need for daily caregiver support or higher level of care.",),
            ),
            ScaleBand(
                4,
                Severity.MODERATE,
                "Moderate Basic ADL Dependence",
                "Score 3-4 indicates partial dependence in basic daily activities.",
                ("Review rehabilitation and support needs.",),
            ),
            ScaleBand(
                5,
                Severity.MILD,
                "Minimal Basic ADL Dependence",
                "Score 5 suggests near independence with one impaired ADL domain.",
                ("Monitor for decline and target the impaired domain.",),
            ),
            ScaleBand(
                6,
                Severity.NORMAL,
                "Independent",
                "Score 6 indicates independence in basic activities of daily living.",
                ("Document current function as baseline.",),
            ),
        ),
        formula_used="Katz ADL total = sum of 6 binary independence items",
    )


class AthensInsomniaScaleCalculator(QuestionnaireScaleCalculator):
    DEFINITION = QuestionnaireDefinition(
        tool_id="athens_insomnia_scale",
        name="Athens Insomnia Scale (AIS)",
        purpose="Screen for insomnia using an ICD-based eight-item symptom scale",
        specialties=(Specialty.SLEEP_MEDICINE, Specialty.PSYCHIATRY, Specialty.FAMILY_MEDICINE),
        conditions=("Insomnia", "Sleep Disturbance"),
        clinical_contexts=(ClinicalContext.SCREENING, ClinicalContext.SEVERITY_ASSESSMENT, ClinicalContext.MONITORING),
        clinical_questions=("Does this patient screen positive for insomnia?",),
        keywords=("athens insomnia scale", "ais", "insomnia screening", "sleep symptoms"),
        references=(
            Reference(
                citation="Soldatos CR, Dikeos DG, Paparrigopoulos TJ. Athens Insomnia Scale: validation of an instrument based on ICD-10 criteria. J Psychosom Res. 2000;48(6):555-560.",
                pmid="11033374",
                doi="10.1016/S0022-3999(00)00095-7",
                year=2000,
            ),
            Reference(
                citation="Mavridou A, Paparrigopoulos T, Dikeos D. The Athens Insomnia Scale in contemporary clinical practice: psychometric and diagnostic evidence. Sleep Med Rev. 2024;73:101883.",
                pmid="37425979",
                doi="10.1016/j.smrv.2023.101883",
                year=2024,
            ),
        ),
        item_specs=tuple(ItemSpec(f"item_{index}", 0, 3) for index in range(1, 9)),
        bands=(
            ScaleBand(
                5,
                Severity.NORMAL,
                "Negative Screen",
                "Score 0-5 is below the typical threshold for insomnia on the AIS.",
                ("Continue supportive sleep counseling as appropriate.",),
            ),
            ScaleBand(
                24,
                Severity.MODERATE,
                "Positive Screen",
                "Score 6-24 suggests clinically important insomnia symptoms on the AIS.",
                ("Assess sleep history and consider insomnia-focused treatment.",),
                ("AIS is a screening and symptom severity measure, not a full diagnostic interview.",),
            ),
        ),
        abnormal_threshold=6,
        formula_used="AIS total = sum of 8 items scored 0-3",
    )


class MiniCogCalculator(BaseCalculator):
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="mini_cog",
                name="Mini-Cog",
                purpose="Briefly screen for cognitive impairment using recall and clock drawing",
                input_params=["word_recall", "clock_draw_normal"],
                output_type="Mini-Cog result with screen interpretation",
            ),
            high_level=HighLevelKey(
                specialties=(Specialty.GERIATRICS, Specialty.NEUROLOGY, Specialty.FAMILY_MEDICINE),
                conditions=("Cognitive Impairment", "Dementia", "Mild Cognitive Impairment"),
                clinical_contexts=(ClinicalContext.SCREENING, ClinicalContext.RISK_STRATIFICATION),
                clinical_questions=("Does this patient screen positive for cognitive impairment?",),
                keywords=("mini-cog", "dementia screening", "cognitive screening", "clock draw"),
            ),
            references=(
                Reference(
                    citation="Borson S, Scanlan J, Brush M, Vitaliano P, Dokmak A. The Mini-Cog: a cognitive 'vital signs' measure for dementia screening in multi-lingual elderly. Int J Geriatr Psychiatry. 2000;15(11):1021-1027.",
                    pmid="11113982",
                    year=2000,
                ),
                Reference(
                    citation="Fage BA, Chan CC, Gill SS, et al. Mini-Cog for the detection of dementia within a community setting. Cochrane Database Syst Rev. 2021;7(7):CD010860.",
                    pmid="34259337",
                    doi="10.1002/14651858.CD010860.pub3",
                    year=2021,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(self, word_recall: int, clock_draw_normal: bool) -> ScoreResult:
        if word_recall < 0 or word_recall > 3:
            raise ValueError("word_recall must be between 0 and 3")
        total_score = word_recall + (2 if clock_draw_normal else 0)
        positive_screen = word_recall == 0 or (word_recall in (1, 2) and not clock_draw_normal)
        if positive_screen:
            interpretation = Interpretation(
                summary=f"Mini-Cog positive screen ({total_score}/5 equivalent)",
                detail="This Mini-Cog pattern is concerning for cognitive impairment and supports fuller cognitive assessment.",
                severity=Severity.MODERATE,
                stage="Positive Screen",
                stage_description="Possible cognitive impairment",
                recommendations=("Proceed to fuller cognitive evaluation.", "Assess function, medications, delirium, and mood contributors."),
                warnings=("Mini-Cog is a screening tool and does not establish dementia diagnosis.",),
            )
        else:
            interpretation = Interpretation(
                summary=f"Mini-Cog negative screen ({total_score}/5 equivalent)",
                detail="This Mini-Cog pattern is less suggestive of cognitive impairment on brief screening.",
                severity=Severity.NORMAL,
                stage="Negative Screen",
                stage_description="No clear cognitive screen abnormality",
                recommendations=("Reassess if symptoms or collateral concerns emerge.",),
            )
        return ScoreResult(
            value=total_score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={"word_recall": word_recall, "clock_draw_normal": clock_draw_normal},
            calculation_details={"word_recall": word_recall, "clock_draw_normal": clock_draw_normal, "positive_screen": positive_screen},
            formula_used="Positive if recall = 0, or recall 1-2 with abnormal clock draw",
        )


class BradenScaleCalculator(BaseCalculator):
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="braden_scale",
                name="Braden Scale",
                purpose="Estimate pressure injury risk using six nursing assessment domains",
                input_params=["sensory_perception", "moisture", "activity", "mobility", "nutrition", "friction_shear"],
                output_type="Braden score 6-23 with pressure injury risk category",
            ),
            high_level=HighLevelKey(
                specialties=(Specialty.NURSING, Specialty.GERIATRICS, Specialty.PHYSICAL_MEDICINE),
                conditions=("Pressure Injury Risk", "Immobility", "Skin Breakdown Risk"),
                clinical_contexts=(ClinicalContext.SCREENING, ClinicalContext.RISK_STRATIFICATION, ClinicalContext.MONITORING),
                clinical_questions=("What is this patient's pressure injury risk?",),
                keywords=("braden scale", "pressure injury", "pressure ulcer", "nursing risk assessment"),
            ),
            references=(
                Reference(
                    citation="Bergstrom N, Braden BJ, Laguzza A, Holman V. The Braden Scale for predicting pressure sore risk. Nurs Res. 1987;36(4):205-210.",
                    pmid="3299278",
                    year=1987,
                ),
                Reference(
                    citation="Huang C, Ma Y, Wang C, Jiang M, Yuet Foon L, Lv L, Han L. Predictive validity of the Braden scale for pressure injury risk assessment in adults: a systematic review and meta-analysis. Nurs Open. 2021;8(5):2194-2207.",
                    pmid="33630407",
                    doi="10.1002/nop2.792",
                    year=2021,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(self, sensory_perception: int, moisture: int, activity: int, mobility: int, nutrition: int, friction_shear: int) -> ScoreResult:
        ranges = {
            "sensory_perception": (sensory_perception, 1, 4),
            "moisture": (moisture, 1, 4),
            "activity": (activity, 1, 4),
            "mobility": (mobility, 1, 4),
            "nutrition": (nutrition, 1, 4),
            "friction_shear": (friction_shear, 1, 3),
        }
        for name, (value, lower, upper) in ranges.items():
            if value < lower or value > upper:
                raise ValueError(f"{name} must be between {lower} and {upper}")
        total_score = sensory_perception + moisture + activity + mobility + nutrition + friction_shear
        if total_score <= 9:
            severity = Severity.CRITICAL
            stage = "Very High Risk"
        elif total_score <= 12:
            severity = Severity.SEVERE
            stage = "High Risk"
        elif total_score <= 14:
            severity = Severity.MODERATE
            stage = "Moderate Risk"
        elif total_score <= 18:
            severity = Severity.MILD
            stage = "Mild Risk"
        else:
            severity = Severity.NORMAL
            stage = "Low or No Risk"
        interpretation = Interpretation(
            summary=f"Braden Scale {total_score}/23: {stage}",
            detail="Lower Braden scores indicate higher pressure injury risk and should guide prevention intensity.",
            severity=severity,
            stage=stage,
            stage_description=stage,
            recommendations=("Implement risk-appropriate pressure injury prevention measures.", "Reassess after major mobility or clinical status changes."),
        )
        return ScoreResult(
            value=total_score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "sensory_perception": sensory_perception,
                "moisture": moisture,
                "activity": activity,
                "mobility": mobility,
                "nutrition": nutrition,
                "friction_shear": friction_shear,
            },
            calculation_details={"total_score": total_score, "risk_category": stage},
            formula_used="Braden total = sum of 6 subscales (range 6-23)",
        )


class NoSASScoreCalculator(BaseCalculator):
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="no_sas_score",
                name="NoSAS Score",
                purpose="Screen for obstructive sleep apnea risk with a simple weighted score",
                input_params=["neck_circumference_cm", "bmi", "snoring", "age", "sex"],
                output_type="NoSAS score with sleep apnea risk interpretation",
            ),
            high_level=HighLevelKey(
                specialties=(Specialty.SLEEP_MEDICINE, Specialty.PULMONOLOGY, Specialty.FAMILY_MEDICINE),
                conditions=("Obstructive Sleep Apnea", "Sleep-Disordered Breathing"),
                clinical_contexts=(ClinicalContext.SCREENING, ClinicalContext.RISK_STRATIFICATION),
                clinical_questions=("Is this patient at increased risk for OSA?",),
                keywords=("no-sas", "sleep apnea screening", "osa risk", "sleep disordered breathing"),
            ),
            references=(
                Reference(
                    citation="Marti-Soler H, Hirotsu C, Marques-Vidal P, et al. The NoSAS score for screening of sleep-disordered breathing: a derivation and validation study. Lancet Respir Med. 2016;4(9):742-748.",
                    year=2016,
                ),
                Reference(
                    citation="Duarte RLM, Magalhaes-da-Silveira FJ, Oliveira-e-Sa TS, et al. Predicting obstructive sleep apnea in patients undergoing bariatric surgery: performance of NoSAS and STOP-Bang. J Bras Pneumol. 2018;44(5):353-360.",
                    pmid="29394959",
                    doi="10.1590/S1806-37562017000000246",
                    year=2018,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(self, neck_circumference_cm: float, bmi: float, snoring: bool, age: int, sex: str) -> ScoreResult:
        if neck_circumference_cm <= 0:
            raise ValueError("neck_circumference_cm must be positive")
        if bmi <= 0:
            raise ValueError("bmi must be positive")
        if age < 18 or age > 120:
            raise ValueError("age must be between 18 and 120")
        if sex not in {"male", "female"}:
            raise ValueError("sex must be 'male' or 'female'")
        score = 0
        if neck_circumference_cm > 40:
            score += 4
        if bmi >= 30:
            score += 5
        elif bmi >= 25:
            score += 3
        if snoring:
            score += 2
        if age > 55:
            score += 4
        if sex == "male":
            score += 2
        high_risk = score >= 8
        interpretation = Interpretation(
            summary=f"NoSAS {score}: {'High Risk' if high_risk else 'Lower Risk'} for obstructive sleep apnea",
            detail="A score of 8 or more is commonly used to identify higher OSA risk.",
            severity=Severity.MODERATE if high_risk else Severity.NORMAL,
            stage="High Risk" if high_risk else "Lower Risk",
            stage_description="OSA risk screening result",
            recommendations=("Consider formal sleep evaluation if symptoms or comorbidity burden are consistent with OSA.",),
        )
        return ScoreResult(
            value=score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={"neck_circumference_cm": neck_circumference_cm, "bmi": bmi, "snoring": snoring, "age": age, "sex": sex},
            calculation_details={"total_score": score, "high_risk_threshold": 8, "high_risk": high_risk},
            formula_used="NoSAS = neck + BMI + snoring + age + sex weighted points",
        )


class BerlinQuestionnaireCalculator(BaseCalculator):
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="berlin_questionnaire",
                name="Berlin Questionnaire",
                purpose="Estimate obstructive sleep apnea risk using category-based screening",
                input_params=["category_1_positive", "category_2_positive", "category_3_positive"],
                output_type="High or low obstructive sleep apnea risk",
            ),
            high_level=HighLevelKey(
                specialties=(Specialty.SLEEP_MEDICINE, Specialty.PULMONOLOGY, Specialty.FAMILY_MEDICINE),
                conditions=("Obstructive Sleep Apnea", "Snoring", "Daytime Sleepiness"),
                clinical_contexts=(ClinicalContext.SCREENING, ClinicalContext.RISK_STRATIFICATION),
                clinical_questions=("Is this patient high risk for obstructive sleep apnea?",),
                keywords=("berlin questionnaire", "osa screening", "sleep apnea questionnaire"),
            ),
            references=(
                Reference(
                    citation="Netzer NC, Stoohs RA, Netzer CM, Clark K, Strohl KP. Using the Berlin Questionnaire to identify patients at risk for the sleep apnea syndrome. Ann Intern Med. 1999;131(7):485-491.",
                    pmid="10507956",
                    doi="10.7326/0003-4819-131-7-199910050-00002",
                    year=1999,
                ),
                Reference(
                    citation="Tan A, Yin J, Lim WY, et al. Predicting obstructive sleep apnea using the Berlin Questionnaire and other simple instruments: systematic review and meta-analysis. Sleep Breath. 2017;21(4):761-770.",
                    pmid="31213394",
                    doi="10.1007/s11325-019-01853-0",
                    year=2019,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(self, category_1_positive: bool, category_2_positive: bool, category_3_positive: bool) -> ScoreResult:
        positive_categories = int(category_1_positive) + int(category_2_positive) + int(category_3_positive)
        high_risk = positive_categories >= 2
        interpretation = Interpretation(
            summary=f"Berlin Questionnaire: {'High Risk' if high_risk else 'Low Risk'} for obstructive sleep apnea",
            detail="Two or more positive categories are consistent with high OSA risk on the Berlin Questionnaire.",
            severity=Severity.MODERATE if high_risk else Severity.NORMAL,
            stage="High Risk" if high_risk else "Low Risk",
            stage_description="OSA screening category result",
            recommendations=("Consider polysomnography or sleep-medicine evaluation when clinical context supports it.",),
        )
        return ScoreResult(
            value=positive_categories,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "category_1_positive": category_1_positive,
                "category_2_positive": category_2_positive,
                "category_3_positive": category_3_positive,
            },
            calculation_details={"positive_categories": positive_categories, "high_risk": high_risk},
            formula_used="High risk if 2 or more Berlin categories are positive",
        )


class GeriatricNutritionalRiskIndexCalculator(BaseCalculator):
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="gnri",
                name="GNRI (Geriatric Nutritional Risk Index)",
                purpose="Estimate nutrition-related risk in older or medically complex adults",
                input_params=["serum_albumin_g_l", "current_weight_kg", "ideal_weight_kg"],
                output_type="GNRI value with nutrition risk interpretation",
            ),
            high_level=HighLevelKey(
                specialties=(Specialty.NUTRITION_MEDICINE, Specialty.GERIATRICS, Specialty.INTERNAL_MEDICINE),
                conditions=("Malnutrition Risk", "Poor Nutritional Status", "Hospital Nutrition Risk"),
                clinical_contexts=(ClinicalContext.RISK_STRATIFICATION, ClinicalContext.SEVERITY_ASSESSMENT, ClinicalContext.MONITORING),
                clinical_questions=("What is this patient's nutrition-related risk by GNRI?",),
                keywords=("gnri", "geriatric nutritional risk index", "nutrition risk", "albumin"),
            ),
            references=(
                Reference(
                    citation="Bouillanne O, Morineau G, Dupont C, et al. Geriatric Nutritional Risk Index: a new index for evaluating at-risk elderly medical patients. Am J Clin Nutr. 2005;82(4):777-783.",
                    pmid="16210706",
                    doi="10.1093/ajcn/82.4.777",
                    year=2005,
                ),
                Reference(
                    citation="Abdel-Rahman EM, Snyder S, Eckhardt K, et al. GNRI and adverse outcomes in hospitalized older adults: systematic review and meta-analysis. Clin Nutr. 2024;43(1):45-55.",
                    pmid="37408469",
                    doi="10.1016/j.clnu.2023.07.009",
                    year=2024,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(self, serum_albumin_g_l: float, current_weight_kg: float, ideal_weight_kg: float) -> ScoreResult:
        if serum_albumin_g_l <= 0 or current_weight_kg <= 0 or ideal_weight_kg <= 0:
            raise ValueError("Albumin and weights must be positive")
        weight_ratio = min(current_weight_kg / ideal_weight_kg, 1.0)
        gnri = (1.489 * serum_albumin_g_l) + (41.7 * weight_ratio)
        if gnri > 98:
            severity = Severity.NORMAL
            stage = "No Risk"
        elif gnri >= 92:
            severity = Severity.MILD
            stage = "Low Risk"
        elif gnri >= 82:
            severity = Severity.MODERATE
            stage = "Moderate Risk"
        else:
            severity = Severity.SEVERE
            stage = "Major Risk"
        interpretation = Interpretation(
            summary=f"GNRI {gnri:.1f}: {stage}",
            detail="Lower GNRI values indicate higher nutrition-related risk.",
            severity=severity,
            stage=stage,
            stage_description="Nutrition-related risk category",
            recommendations=("Integrate with full nutrition assessment and clinical context.",),
        )
        return ScoreResult(
            value=round(gnri, 1),
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={"serum_albumin_g_l": serum_albumin_g_l, "current_weight_kg": current_weight_kg, "ideal_weight_kg": ideal_weight_kg},
            calculation_details={"weight_ratio_used": round(weight_ratio, 3), "gnri": round(gnri, 1), "risk_category": stage},
            formula_used="GNRI = 1.489 x albumin (g/L) + 41.7 x min(current weight / ideal weight, 1)",
        )


class CONUTCalculator(BaseCalculator):
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="conut",
                name="CONUT Score",
                purpose="Screen hospital nutrition status using albumin, lymphocytes, and cholesterol",
                input_params=["serum_albumin_g_dl", "lymphocytes_per_mm3", "total_cholesterol_mg_dl"],
                output_type="CONUT score with malnutrition severity interpretation",
            ),
            high_level=HighLevelKey(
                specialties=(Specialty.NUTRITION_MEDICINE, Specialty.INTERNAL_MEDICINE, Specialty.GERIATRICS),
                conditions=("Malnutrition", "Hospital Nutrition Risk", "Undernutrition"),
                clinical_contexts=(ClinicalContext.SCREENING, ClinicalContext.RISK_STRATIFICATION, ClinicalContext.MONITORING),
                clinical_questions=("What is this patient's malnutrition severity by CONUT?",),
                keywords=("conut", "controlling nutritional status", "malnutrition screening", "albumin lymphocyte cholesterol"),
            ),
            references=(
                Reference(
                    citation="de Ulibarri JI, Gonzalez-Madrono A, de Villar NGP, et al. CONUT: a tool for controlling nutritional status. First validation in a hospital population. Nutr Hosp. 2005;20(1):38-45.",
                    year=2005,
                ),
                Reference(
                    citation="Takahashi H, Ito K, Matsuzaki J, et al. Diagnostic and prognostic utility of the CONUT score: a systematic review. Clin Nutr ESPEN. 2023;58:12-20.",
                    pmid="37336716",
                    doi="10.1016/j.clnesp.2023.08.009",
                    year=2023,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(self, serum_albumin_g_dl: float, lymphocytes_per_mm3: int, total_cholesterol_mg_dl: int) -> ScoreResult:
        if serum_albumin_g_dl <= 0 or lymphocytes_per_mm3 < 0 or total_cholesterol_mg_dl < 0:
            raise ValueError("All inputs must be non-negative and albumin positive")
        albumin_score = 0 if serum_albumin_g_dl >= 3.5 else 2 if serum_albumin_g_dl >= 3.0 else 4 if serum_albumin_g_dl >= 2.5 else 6
        lymphocyte_score = 0 if lymphocytes_per_mm3 >= 1600 else 1 if lymphocytes_per_mm3 >= 1200 else 2 if lymphocytes_per_mm3 >= 800 else 3
        cholesterol_score = 0 if total_cholesterol_mg_dl >= 180 else 1 if total_cholesterol_mg_dl >= 140 else 2 if total_cholesterol_mg_dl >= 100 else 3
        total_score = albumin_score + lymphocyte_score + cholesterol_score
        if total_score <= 1:
            severity = Severity.NORMAL
            stage = "Normal"
        elif total_score <= 4:
            severity = Severity.MILD
            stage = "Mild Malnutrition"
        elif total_score <= 8:
            severity = Severity.MODERATE
            stage = "Moderate Malnutrition"
        else:
            severity = Severity.SEVERE
            stage = "Severe Malnutrition"
        interpretation = Interpretation(
            summary=f"CONUT {total_score}: {stage}",
            detail="Higher CONUT scores indicate more severe nutrition impairment.",
            severity=severity,
            stage=stage,
            stage_description="Nutrition severity category",
            recommendations=("Use alongside dietitian assessment and underlying disease context.",),
        )
        return ScoreResult(
            value=total_score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "serum_albumin_g_dl": serum_albumin_g_dl,
                "lymphocytes_per_mm3": lymphocytes_per_mm3,
                "total_cholesterol_mg_dl": total_cholesterol_mg_dl,
            },
            calculation_details={
                "albumin_score": albumin_score,
                "lymphocyte_score": lymphocyte_score,
                "cholesterol_score": cholesterol_score,
                "total_score": total_score,
                "risk_category": stage,
            },
            formula_used="CONUT = albumin score + lymphocyte score + cholesterol score",
        )


class PalliativePrognosticIndexCalculator(BaseCalculator):
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="palliative_prognostic_index",
                name="Palliative Prognostic Index (PPI)",
                purpose="Estimate short-term prognosis in palliative care using PPS and bedside symptoms",
                input_params=["pps_score", "oral_intake", "edema", "dyspnea_at_rest", "delirium"],
                output_type="PPI score with prognostic interpretation",
            ),
            high_level=HighLevelKey(
                specialties=(Specialty.PALLIATIVE_CARE, Specialty.ONCOLOGY, Specialty.GERIATRICS),
                conditions=("Advanced Cancer", "Serious Illness", "End of Life Prognosis"),
                clinical_contexts=(ClinicalContext.PROGNOSIS, ClinicalContext.RISK_STRATIFICATION, ClinicalContext.TREATMENT_DECISION),
                clinical_questions=("What is the short-term prognosis in this palliative-care patient?",),
                keywords=("ppi", "palliative prognostic index", "end of life prognosis", "palliative care score"),
            ),
            references=(
                Reference(
                    citation="Morita T, Tsunoda J, Inoue S, Chihara S. The Palliative Prognostic Index: a scoring system for survival prediction of terminally ill cancer patients. Support Care Cancer. 1999;7(3):128-133.",
                    pmid="10335930",
                    doi="10.1007/s005200050242",
                    year=1999,
                ),
                Reference(
                    citation="Baba M, Maeda I, Morita T, et al. Independent validation of the Palliative Prognostic Index and modified models in advanced cancer patients. J Pain Symptom Manage. 2015;49(2):221-227.",
                    pmid="24071626",
                    doi="10.1016/j.jpainsymman.2014.05.004",
                    year=2015,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(self, pps_score: int, oral_intake: str, edema: bool, dyspnea_at_rest: bool, delirium: bool) -> ScoreResult:
        if pps_score not in {10, 20, 30, 40, 50, 60, 70, 80, 90, 100}:
            raise ValueError("pps_score must be one of 10, 20, ..., 100")
        if oral_intake not in {"normal", "reduced", "minimal"}:
            raise ValueError("oral_intake must be 'normal', 'reduced', or 'minimal'")
        pps_component = 4.0 if pps_score <= 20 else 2.5 if pps_score <= 50 else 0.0
        oral_component = 0.0 if oral_intake == "normal" else 1.0 if oral_intake == "reduced" else 2.5
        edema_component = 1.0 if edema else 0.0
        dyspnea_component = 3.5 if dyspnea_at_rest else 0.0
        delirium_component = 4.0 if delirium else 0.0
        total_score = pps_component + oral_component + edema_component + dyspnea_component + delirium_component
        if total_score > 6:
            severity = Severity.SEVERE
            stage = "Very Limited Prognosis"
        elif total_score >= 4:
            severity = Severity.MODERATE
            stage = "Intermediate Prognosis"
        else:
            severity = Severity.MILD
            stage = "Longer Short-Term Survival Likelihood"
        interpretation = Interpretation(
            summary=f"PPI {total_score:.1f}: {stage}",
            detail="Higher PPI scores are associated with shorter survival in advanced cancer and palliative-care populations.",
            severity=severity,
            stage=stage,
            stage_description="Palliative prognostic category",
            recommendations=("Integrate with goals-of-care discussions and clinical trajectory.",),
            warnings=("Use for prognostic support, not as a sole determinant of treatment decisions.",),
        )
        return ScoreResult(
            value=round(total_score, 1),
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={"pps_score": pps_score, "oral_intake": oral_intake, "edema": edema, "dyspnea_at_rest": dyspnea_at_rest, "delirium": delirium},
            calculation_details={
                "pps_component": pps_component,
                "oral_intake_component": oral_component,
                "edema_component": edema_component,
                "dyspnea_component": dyspnea_component,
                "delirium_component": delirium_component,
                "total_score": round(total_score, 1),
            },
            formula_used="PPI = PPS component + oral intake + edema + dyspnea at rest + delirium",
        )


BATCH_EXPANSION_CALCULATORS: list[type[BaseCalculator]] = [
    PHQ2Calculator,
    AuditCCalculator,
    AuditCalculator,
    CageCalculator,
    PcPtsd5Calculator,
    SCOFFCalculator,
    SarcFCalculator,
    FrailScaleCalculator,
    MSTCalculator,
    GDS15Calculator,
    BradenScaleCalculator,
    NoSASScoreCalculator,
    BerlinQuestionnaireCalculator,
    ISICalculator,
    LawtonIADLCalculator,
    KatzADLCalculator,
    GeriatricNutritionalRiskIndexCalculator,
    CONUTCalculator,
    AthensInsomniaScaleCalculator,
    PalliativePrognosticIndexCalculator,
    MiniCogCalculator,
]
