"""
CPIS Calculator (Clinical Pulmonary Infection Score)

Assists in the diagnosis of ventilator-associated pneumonia (VAP).
Used to guide antibiotic therapy decisions and assess treatment response.

Original Reference:
    Pugin J, Auckenthaler R, Mili N, Janssens JP, Lew PD, Suter PM.
    Diagnosis of ventilator-associated pneumonia by bacteriologic analysis
    of bronchoscopic and nonbronchoscopic "blind" bronchoalveolar lavage fluid.
    Am Rev Respir Dis. 1991;143(5 Pt 1):1121-1129.
    doi:10.1164/ajrccm/143.5_Pt_1.1121. PMID: 2024824.
"""

from typing import Any

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, RiskLevel, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import (
    ClinicalContext,
    HighLevelKey,
    LowLevelKey,
    Specialty,
)
from ...value_objects.units import Unit
from ..base import BaseCalculator


class CpisCalculator(BaseCalculator):
    """
    Clinical Pulmonary Infection Score (CPIS)

    Scoring criteria (0-12 points):

    Temperature (°C):
    - 36.5-38.4: 0 points
    - 38.5-38.9: 1 point
    - ≥39.0 or ≤36.0: 2 points

    Blood leukocytes (×10³/µL):
    - 4.0-11.0: 0 points
    - <4.0 or >11.0: 1 point
    - + band forms ≥50%: add 1 point

    Tracheal secretions:
    - None/Scant: 0 points
    - Moderate non-purulent: 1 point
    - Abundant or purulent: 2 points

    Oxygenation (PaO₂/FiO₂):
    - >240 or ARDS: 0 points
    - ≤240 and no ARDS: 2 points

    Chest radiograph:
    - No infiltrate: 0 points
    - Diffuse/patchy infiltrate: 1 point
    - Localized infiltrate: 2 points

    Culture (semi-quantitative):
    - No or light growth: 0 points
    - Moderate or heavy growth: 1 point
    - + same organism on Gram stain: add 1 point

    Interpretation:
    - CPIS ≤6: Low probability of VAP, consider stopping antibiotics
    - CPIS >6: High probability of VAP, continue antibiotics
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="cpis",
                name="Clinical Pulmonary Infection Score (CPIS)",
                purpose="Assist in VAP diagnosis and guide antibiotic therapy decisions",
                input_params=[
                    "temperature_category",
                    "wbc_category",
                    "band_forms_gte_50",
                    "secretions",
                    "pao2_fio2_lte_240_no_ards",
                    "chest_xray",
                    "culture_growth",
                    "gram_stain_matches",
                ],
                output_type="Score 0-12 with VAP probability and antibiotic guidance"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.CRITICAL_CARE,
                    Specialty.PULMONOLOGY,
                    Specialty.INFECTIOUS_DISEASE,
                    Specialty.ANESTHESIOLOGY,
                ),
                conditions=(
                    "ventilator-associated pneumonia",
                    "VAP",
                    "hospital-acquired pneumonia",
                    "HAP",
                    "nosocomial pneumonia",
                    "pneumonia in ICU",
                ),
                clinical_contexts=(
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.TREATMENT_DECISION,
                    ClinicalContext.MONITORING,
                ),
            ),
            references=(
                Reference(
                    citation="Pugin J, et al. Am Rev Respir Dis. 1991;143(5 Pt 1):1121-1129.",
                    pmid="2024824",
                    doi="10.1164/ajrccm/143.5_Pt_1.1121",
                ),
                Reference(
                    citation="Singh N, et al. Am J Respir Crit Care Med. 2000;162(2 Pt 1):505-511.",
                    pmid="10934078",
                    doi="10.1164/ajrccm.162.2.9909095",
                ),
                Reference(
                    citation="Kalil AC, et al. Clin Infect Dis. 2016;63(5):e61-e111. (IDSA/ATS HAP/VAP Guidelines)",
                    pmid="27418577",
                    doi="10.1093/cid/ciw353",
                ),
            ),
        )

    def calculate(
        self,
        temperature_category: str,  # "normal", "elevated", "high"
        wbc_category: str,  # "normal", "abnormal"
        band_forms_gte_50: bool,
        secretions: str,  # "none", "moderate", "purulent"
        pao2_fio2_lte_240_no_ards: bool,
        chest_xray: str,  # "no_infiltrate", "diffuse", "localized"
        culture_growth: str,  # "none_light", "moderate_heavy"
        gram_stain_matches: bool,
    ) -> ScoreResult:
        """
        Calculate Clinical Pulmonary Infection Score.

        Args:
            temperature_category: Temperature category
                - "normal": 36.5-38.4°C (0 points)
                - "elevated": 38.5-38.9°C (1 point)
                - "high": ≥39.0°C or ≤36.0°C (2 points)
            wbc_category: White blood cell count
                - "normal": 4.0-11.0 ×10³/µL (0 points)
                - "abnormal": <4.0 or >11.0 ×10³/µL (1 point)
            band_forms_gte_50: Band forms ≥50% (adds 1 point if WBC abnormal)
            secretions: Tracheal secretion quality
                - "none": None or scant (0 points)
                - "moderate": Moderate non-purulent (1 point)
                - "purulent": Abundant or purulent (2 points)
            pao2_fio2_lte_240_no_ards: PaO₂/FiO₂ ≤240 without ARDS (2 points if true)
            chest_xray: Chest radiograph findings
                - "no_infiltrate": No infiltrate (0 points)
                - "diffuse": Diffuse or patchy infiltrate (1 point)
                - "localized": Localized infiltrate (2 points)
            culture_growth: Culture results
                - "none_light": No or light growth (0 points)
                - "moderate_heavy": Moderate or heavy growth (1 point)
            gram_stain_matches: Same organism on Gram stain (adds 1 point if culture positive)

        Returns:
            ScoreResult with CPIS and VAP management recommendation
        """
        score = 0
        components: dict[str, Any] = {}
        
        # Temperature
        if temperature_category == "high":
            score += 2
            components["temperature"] = "≥39.0°C or ≤36.0°C (+2)"
        elif temperature_category == "elevated":
            score += 1
            components["temperature"] = "38.5-38.9°C (+1)"
        else:  # normal
            components["temperature"] = "36.5-38.4°C (+0)"

        # WBC
        wbc_points = 0
        if wbc_category == "abnormal":
            wbc_points += 1
            wbc_desc = "<4 or >11 ×10³/µL (+1)"
            if band_forms_gte_50:
                wbc_points += 1
                wbc_desc += " + bands ≥50% (+1)"
        else:
            wbc_desc = "4-11 ×10³/µL (+0)"
        score += wbc_points
        components["wbc"] = wbc_desc

        # Tracheal secretions
        if secretions == "purulent":
            score += 2
            components["secretions"] = "Abundant/purulent (+2)"
        elif secretions == "moderate":
            score += 1
            components["secretions"] = "Moderate non-purulent (+1)"
        else:  # none
            components["secretions"] = "None/scant (+0)"

        # Oxygenation
        if pao2_fio2_lte_240_no_ards:
            score += 2
            components["oxygenation"] = "PaO₂/FiO₂ ≤240, no ARDS (+2)"
        else:
            components["oxygenation"] = "PaO₂/FiO₂ >240 or ARDS (+0)"

        # Chest X-ray
        if chest_xray == "localized":
            score += 2
            components["chest_xray"] = "Localized infiltrate (+2)"
        elif chest_xray == "diffuse":
            score += 1
            components["chest_xray"] = "Diffuse/patchy infiltrate (+1)"
        else:  # no_infiltrate
            components["chest_xray"] = "No infiltrate (+0)"

        # Culture
        culture_points = 0
        if culture_growth == "moderate_heavy":
            culture_points += 1
            culture_desc = "Moderate/heavy growth (+1)"
            if gram_stain_matches:
                culture_points += 1
                culture_desc += " + Gram stain match (+1)"
        else:
            culture_desc = "No/light growth (+0)"
        score += culture_points
        components["culture"] = culture_desc

        # Generate interpretation
        interpretation = self._interpret_score(score)

        return ScoreResult(
            tool_name=self.low_level_key.name,
            tool_id=self.low_level_key.tool_id,
            value=score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            calculation_details=components,
            references=list(self.references),
        )

    def _interpret_score(self, score: int) -> Interpretation:
        """Generate interpretation based on CPIS score"""

        if score <= 6:
            severity = Severity.MILD
            risk_level = RiskLevel.LOW
            summary = f"CPIS {score}/12: Low probability of VAP"
            detail = (
                "CPIS ≤6 suggests low probability of VAP. "
                "Consider discontinuing empiric antibiotics if started. "
                "If antibiotics continued, reassess in 3 days. "
                "Look for alternative sources of fever/infection."
            )
            recommendations = [
                "Consider discontinuing empiric antibiotics",
                "Look for alternative sources of infection",
                "Reassess in 3 days if antibiotics continued",
            ]
            next_steps = [
                "Review indication for continued antibiotic therapy",
                "Search for alternative diagnoses (line infection, sinusitis, UTI)",
                "Repeat CPIS at day 3 to guide therapy duration",
            ]
        else:
            severity = Severity.SEVERE
            risk_level = RiskLevel.HIGH
            summary = f"CPIS {score}/12: High probability of VAP"
            detail = (
                "CPIS >6 suggests high probability of VAP. "
                "Continue appropriate antibiotic therapy. "
                "Follow 2016 IDSA/ATS guidelines for HAP/VAP. "
                "Reassess at day 3 with repeat CPIS to evaluate response."
            )
            recommendations = [
                "Continue antibiotic therapy per guidelines",
                "Follow 2016 IDSA/ATS HAP/VAP recommendations",
                "Reassess at day 3 with repeat CPIS",
            ]
            next_steps = [
                "Ensure cultures obtained before antibiotics if not done",
                "Use local antibiogram for empiric therapy selection",
                "De-escalate based on culture results at 48-72h",
                "Consider 7-day course if good clinical response",
            ]

        return Interpretation(
            summary=summary,
            detail=detail,
            severity=severity,
            risk_level=risk_level,
            recommendations=tuple(recommendations),
            next_steps=tuple(next_steps),
        )
