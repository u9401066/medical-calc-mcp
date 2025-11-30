"""
Child-Pugh Score Calculator

Assesses severity of chronic liver disease (cirrhosis) for prognosis and treatment planning.

Original Reference:
    Pugh RNH, Murray-Lyon IM, Dawson JL, et al. Transection of the oesophagus
    for bleeding oesophageal varices. Br J Surg. 1973;60(8):646-649.
    doi:10.1002/bjs.1800600817. PMID: 4541913.

Modified scoring (current version) reference:
    Child CG, Turcotte JG. Surgery and portal hypertension. In: Child CG, ed.
    The Liver and Portal Hypertension. Philadelphia: Saunders; 1964:50-64.

Clinical utility references:
    Cholongitas E, Papatheodoridis GV, Vangeli M, et al. Systematic review:
    The model for end-stage liver disease - should it replace Child-Pugh's
    classification for assessing prognosis in cirrhosis? Aliment Pharmacol Ther.
    2005;22(11-12):1079-1089. doi:10.1111/j.1365-2036.2005.02691.x. PMID: 16305721.
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
    ClinicalContext,
)


class ChildPughCalculator(BaseCalculator):
    """
    Child-Pugh Score for Chronic Liver Disease Severity
    
    Scoring criteria (5 clinical measures, each 1-3 points):
    
    | Parameter          | 1 point      | 2 points       | 3 points        |
    |--------------------|--------------|----------------|-----------------|
    | Bilirubin (mg/dL)  | <2           | 2-3            | >3              |
    | Albumin (g/dL)     | >3.5         | 2.8-3.5        | <2.8            |
    | INR                | <1.7         | 1.7-2.2        | >2.2            |
    | Ascites            | None         | Mild/Controlled| Moderate-Severe |
    | Encephalopathy     | None         | Grade I-II     | Grade III-IV    |
    
    Classification:
    - Class A: 5-6 points (well-compensated disease)
    - Class B: 7-9 points (significant functional compromise)
    - Class C: 10-15 points (decompensated disease)
    
    Prognostic implications:
    - 1-year survival: Class A ~100%, Class B ~80%, Class C ~45%
    - 2-year survival: Class A ~85%, Class B ~60%, Class C ~35%
    
    Clinical applications:
    - Prognosis assessment in cirrhosis
    - Surgical risk stratification (perioperative mortality)
    - Liver transplant evaluation (often complemented by MELD)
    - Drug dosing adjustments in hepatic impairment
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="child_pugh",
                name="Child-Pugh Score",
                purpose="Assess severity of chronic liver disease (cirrhosis) for prognosis",
                input_params=[
                    "bilirubin",
                    "albumin",
                    "inr",
                    "ascites",
                    "encephalopathy_grade",
                ],
                output_type="Score 5-15 with Class A/B/C and survival estimates"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.HEPATOLOGY,
                    Specialty.GASTROENTEROLOGY,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.SURGERY,
                ),
                conditions=(
                    "cirrhosis",
                    "chronic liver disease",
                    "hepatic failure",
                    "portal hypertension",
                    "liver fibrosis",
                    "hepatitis",
                    "alcoholic liver disease",
                    "NASH cirrhosis",
                    "hepatocellular carcinoma",
                ),
                clinical_contexts=(
                    ClinicalContext.STAGING,
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.TREATMENT_DECISION,
                    ClinicalContext.DRUG_DOSING,
                    ClinicalContext.PREOPERATIVE_ASSESSMENT,
                ),
                clinical_questions=(
                    "What is the severity of this patient's cirrhosis?",
                    "What is the prognosis for this cirrhotic patient?",
                    "Is this patient a candidate for liver transplant?",
                    "What is the surgical risk for this cirrhotic patient?",
                    "How should I adjust drug dosing for liver impairment?",
                    "Is this patient compensated or decompensated cirrhosis?",
                ),
                icd10_codes=(
                    "K74.60",  # Unspecified cirrhosis of liver
                    "K74.69",  # Other cirrhosis of liver
                    "K70.30",  # Alcoholic cirrhosis of liver without ascites
                    "K70.31",  # Alcoholic cirrhosis of liver with ascites
                    "K76.6",   # Portal hypertension
                ),
                keywords=(
                    "Child-Pugh",
                    "Child Pugh",
                    "Child Turcotte Pugh",
                    "CTP score",
                    "cirrhosis severity",
                    "liver disease prognosis",
                    "hepatic reserve",
                    "compensated cirrhosis",
                    "decompensated cirrhosis",
                    "liver function score",
                )
            ),
            references=(
                Reference(
                    citation="Pugh RNH, Murray-Lyon IM, Dawson JL, et al. Transection of "
                             "the oesophagus for bleeding oesophageal varices. "
                             "Br J Surg. 1973;60(8):646-649.",
                    doi="10.1002/bjs.1800600817",
                    pmid="4541913",
                    year=1973,
                ),
                Reference(
                    citation="Child CG, Turcotte JG. Surgery and portal hypertension. "
                             "In: Child CG, ed. The Liver and Portal Hypertension. "
                             "Philadelphia: Saunders; 1964:50-64.",
                    year=1964,
                ),
                Reference(
                    citation="Cholongitas E, Papatheodoridis GV, Vangeli M, et al. "
                             "Systematic review: The model for end-stage liver disease - "
                             "should it replace Child-Pugh's classification for assessing "
                             "prognosis in cirrhosis? Aliment Pharmacol Ther. "
                             "2005;22(11-12):1079-1089.",
                    doi="10.1111/j.1365-2036.2005.02691.x",
                    pmid="16305721",
                    year=2005,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )
    
    def calculate(
        self,
        bilirubin: float,
        albumin: float,
        inr: float,
        ascites: str,
        encephalopathy_grade: int,
    ) -> ScoreResult:
        """
        Calculate Child-Pugh score.
        
        Args:
            bilirubin: Total bilirubin in mg/dL (typical range: 0.1-20+)
            albumin: Serum albumin in g/dL (typical range: 1.5-5.0)
            inr: International Normalized Ratio (typical range: 1.0-4.0)
            ascites: Ascites status - "none", "mild" (or "controlled"), "moderate_severe"
            encephalopathy_grade: Hepatic encephalopathy grade 0-4
                0 = None
                1 = Grade I (mild confusion, altered mood)
                2 = Grade II (drowsy, inappropriate behavior)
                3 = Grade III (somnolent but arousable, marked confusion)
                4 = Grade IV (coma, unresponsive)
            
        Returns:
            ScoreResult with score, Child-Pugh class, and clinical implications
        """
        # Validate inputs
        ascites_normalized = self._normalize_ascites(ascites)
        encephalopathy_normalized = self._normalize_encephalopathy(encephalopathy_grade)
        
        # Calculate component scores
        bilirubin_score = self._score_bilirubin(bilirubin)
        albumin_score = self._score_albumin(albumin)
        inr_score = self._score_inr(inr)
        ascites_score = self._score_ascites(ascites_normalized)
        encephalopathy_score = self._score_encephalopathy(encephalopathy_normalized)
        
        # Total score
        total_score = (
            bilirubin_score + albumin_score + inr_score + 
            ascites_score + encephalopathy_score
        )
        
        # Determine class
        child_class = self._determine_class(total_score)
        
        # Generate interpretation
        interpretation = self._interpret_score(
            total_score, child_class, ascites_normalized, encephalopathy_normalized
        )
        
        # Component details
        components = {
            "Bilirubin": {
                "value": f"{bilirubin} mg/dL",
                "points": bilirubin_score,
                "criteria": self._bilirubin_criteria(bilirubin_score),
            },
            "Albumin": {
                "value": f"{albumin} g/dL",
                "points": albumin_score,
                "criteria": self._albumin_criteria(albumin_score),
            },
            "INR": {
                "value": f"{inr}",
                "points": inr_score,
                "criteria": self._inr_criteria(inr_score),
            },
            "Ascites": {
                "value": ascites_normalized,
                "points": ascites_score,
            },
            "Encephalopathy": {
                "value": f"Grade {encephalopathy_normalized}",
                "points": encephalopathy_score,
            },
            "Total Score": total_score,
            "Child-Pugh Class": child_class,
        }
        
        return ScoreResult(
            tool_name=self.low_level_key.name,
            tool_id=self.low_level_key.tool_id,
            value=total_score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            calculation_details=components,
            references=list(self.references),
        )
    
    def _normalize_ascites(self, ascites: str) -> str:
        """Normalize ascites input to standard categories"""
        ascites_lower = ascites.lower().strip()
        
        if ascites_lower in ("none", "absent", "no", "0"):
            return "none"
        elif ascites_lower in ("mild", "slight", "controlled", "diuretic-controlled", "1"):
            return "mild"
        elif ascites_lower in ("moderate", "moderate_severe", "moderate-severe", 
                               "severe", "refractory", "tense", "2", "3"):
            return "moderate_severe"
        else:
            # Default to none if unrecognized
            return "none"
    
    def _normalize_encephalopathy(self, grade: int) -> int:
        """Normalize encephalopathy grade to 0-4"""
        if grade < 0:
            return 0
        elif grade > 4:
            return 4
        return grade
    
    def _score_bilirubin(self, bilirubin: float) -> int:
        """Score bilirubin component"""
        if bilirubin < 2:
            return 1
        elif bilirubin <= 3:
            return 2
        else:
            return 3
    
    def _score_albumin(self, albumin: float) -> int:
        """Score albumin component (inverse relationship)"""
        if albumin > 3.5:
            return 1
        elif albumin >= 2.8:
            return 2
        else:
            return 3
    
    def _score_inr(self, inr: float) -> int:
        """Score INR component"""
        if inr < 1.7:
            return 1
        elif inr <= 2.2:
            return 2
        else:
            return 3
    
    def _score_ascites(self, ascites: str) -> int:
        """Score ascites component"""
        if ascites == "none":
            return 1
        elif ascites == "mild":
            return 2
        else:  # moderate_severe
            return 3
    
    def _score_encephalopathy(self, grade: int) -> int:
        """Score encephalopathy component"""
        if grade == 0:
            return 1
        elif grade <= 2:
            return 2
        else:  # Grade III-IV
            return 3
    
    def _bilirubin_criteria(self, score: int) -> str:
        if score == 1:
            return "<2 mg/dL"
        elif score == 2:
            return "2-3 mg/dL"
        else:
            return ">3 mg/dL"
    
    def _albumin_criteria(self, score: int) -> str:
        if score == 1:
            return ">3.5 g/dL"
        elif score == 2:
            return "2.8-3.5 g/dL"
        else:
            return "<2.8 g/dL"
    
    def _inr_criteria(self, score: int) -> str:
        if score == 1:
            return "<1.7"
        elif score == 2:
            return "1.7-2.2"
        else:
            return ">2.2"
    
    def _determine_class(self, score: int) -> str:
        """Determine Child-Pugh class from total score"""
        if score <= 6:
            return "A"
        elif score <= 9:
            return "B"
        else:
            return "C"
    
    def _interpret_score(
        self,
        score: int,
        child_class: str,
        ascites: str,
        encephalopathy: int,
    ) -> Interpretation:
        """Generate interpretation based on Child-Pugh class"""
        
        # Survival data from multiple studies
        survival_data = {
            "A": {"1y": "100%", "2y": "85%", "operative_mortality": "10%"},
            "B": {"1y": "80%", "2y": "60%", "operative_mortality": "30%"},
            "C": {"1y": "45%", "2y": "35%", "operative_mortality": "82%"},
        }
        
        survival = survival_data[child_class]
        
        if child_class == "A":
            severity = Severity.MILD
            risk_level = RiskLevel.LOW
            summary = f"Child-Pugh Class A ({score} points): Well-compensated cirrhosis"
            detail = (
                f"Class A indicates well-compensated liver disease with good hepatic reserve. "
                f"Expected 1-year survival approximately {survival['1y']}, "
                f"2-year survival approximately {survival['2y']}. "
                f"Perioperative mortality risk approximately {survival['operative_mortality']}."
            )
            recommendations = [
                "Relatively preserved hepatic function",
                "Standard medication dosing may be appropriate for many drugs",
                "Surgical procedures generally tolerated with careful management",
                "Continue surveillance for hepatocellular carcinoma",
                "Monitor for progression to decompensation",
            ]
            next_steps = [
                "Consider MELD score for transplant evaluation if indicated",
                "Regular monitoring: LFTs, AFP, ultrasound per guidelines",
                "Variceal screening endoscopy if not recently done",
                "Address underlying etiology if treatable",
            ]
            
        elif child_class == "B":
            severity = Severity.MODERATE
            risk_level = RiskLevel.INTERMEDIATE
            summary = f"Child-Pugh Class B ({score} points): Significant functional compromise"
            detail = (
                f"Class B indicates significant hepatic dysfunction. "
                f"Expected 1-year survival approximately {survival['1y']}, "
                f"2-year survival approximately {survival['2y']}. "
                f"Perioperative mortality risk approximately {survival['operative_mortality']}."
            )
            recommendations = [
                "Moderate hepatic impairment - requires careful management",
                "Drug dosing adjustments needed for hepatically-metabolized medications",
                "Surgical risk significantly increased - optimize before elective procedures",
                "Consider liver transplant evaluation",
                "Aggressive management of decompensating events",
            ]
            next_steps = [
                "Calculate MELD score for transplant prioritization",
                "Referral to transplant hepatology if appropriate candidate",
                "Optimize nutrition (high protein, low sodium if ascites)",
                "Beta-blocker for variceal prophylaxis if indicated",
                "Diuretic management if ascites present",
            ]
            
        else:  # Class C
            severity = Severity.SEVERE
            risk_level = RiskLevel.HIGH
            summary = f"Child-Pugh Class C ({score} points): Decompensated cirrhosis"
            detail = (
                f"Class C indicates decompensated liver disease with poor prognosis. "
                f"Expected 1-year survival approximately {survival['1y']}, "
                f"2-year survival approximately {survival['2y']}. "
                f"Perioperative mortality risk approximately {survival['operative_mortality']}."
            )
            recommendations = [
                "Decompensated cirrhosis - high mortality without transplant",
                "Avoid elective surgery if possible (very high mortality)",
                "Maximum hepatic drug dose reductions required",
                "Liver transplant evaluation urgent if candidate",
                "Palliative care discussion if not transplant candidate",
            ]
            next_steps = [
                "Urgent MELD calculation for transplant listing priority",
                "Transplant center referral if not already established",
                "Aggressive supportive care for complications",
                "Goals of care discussion with patient and family",
                "Avoid nephrotoxic drugs - high hepatorenal syndrome risk",
            ]
        
        # Add warnings for specific complications
        warnings = []
        if ascites == "moderate_severe":
            warnings.append(
                "Moderate-severe ascites present: Consider paracentesis if tense. "
                "Monitor for spontaneous bacterial peritonitis (SBP). "
                "Sodium restriction and diuretic optimization needed."
            )
        if encephalopathy >= 2:
            warnings.append(
                f"Hepatic encephalopathy Grade {encephalopathy}: Assess for precipitants "
                "(infection, GI bleed, constipation, medications). "
                "Lactulose and rifaximin therapy per guidelines."
            )
        if child_class == "C":
            warnings.append(
                "Class C cirrhosis carries high short-term mortality. "
                "Consider transplant urgently if candidate. "
                "Ensure goals of care are documented."
            )
        
        return Interpretation(
            summary=summary,
            severity=severity,
            detail=detail,
            stage=f"Child-Pugh Class {child_class}",
            stage_description=f"Score {score}/15 (Class A: 5-6, B: 7-9, C: 10-15)",
            risk_level=risk_level,
            recommendations=tuple(recommendations),
            next_steps=tuple(next_steps),
            warnings=tuple(warnings),
        )
