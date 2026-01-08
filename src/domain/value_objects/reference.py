"""
Reference Value Object

Represents a citation to an original research paper.
All medical calculators must cite their original sources.
"""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class Reference:
    """
    A citation to an original research paper.

    Uses Vancouver citation style.

    Example:
        Reference(
            citation="Inker LA, Eneanya ND, Coresh J, et al. New Creatinine- and "
                     "Cystatin C-Based Equations to Estimate GFR without Race. "
                     "N Engl J Med. 2021;385(19):1737-1749.",
            doi="10.1056/NEJMoa2102953",
            pmid="34554658",
            year=2021,
            level_of_evidence="Class I"
        )

    Level of Evidence (Oxford CEBM):
        - Class I / Level A: High-quality RCT, systematic review
        - Class II / Level B: Lower-quality RCT, prospective cohort
        - Class III / Level C: Case-control, retrospective cohort
        - Class IV / Level D: Case series, case reports
        - Class V / Level E: Expert opinion, consensus
        - "Validation study": Original validation cohort
        - "Clinical guideline": Society guidelines (e.g., AHA, ESC, ACOG)
    """

    citation: str  # Full Vancouver-style citation
    doi: Optional[str] = None  # Digital Object Identifier
    pmid: Optional[str] = None  # PubMed ID
    pmcid: Optional[str] = None  # PubMed Central ID
    year: Optional[int] = None  # Publication year
    url: Optional[str] = None  # Direct URL (if no DOI)
    level_of_evidence: Optional[str] = None  # Evidence level (Oxford CEBM or custom)

    def __post_init__(self) -> None:
        if not self.citation:
            raise ValueError("Citation text is required")

    @property
    def doi_url(self) -> Optional[str]:
        """Get the DOI URL if DOI is available"""
        if self.doi:
            return f"https://doi.org/{self.doi}"
        return None

    @property
    def pubmed_url(self) -> Optional[str]:
        """Get the PubMed URL if PMID is available"""
        if self.pmid:
            return f"https://pubmed.ncbi.nlm.nih.gov/{self.pmid}/"
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "citation": self.citation,
            "doi": self.doi,
            "pmid": self.pmid,
            "pmcid": self.pmcid,
            "year": self.year,
            "url": self.url or self.doi_url or self.pubmed_url,
            "level_of_evidence": self.level_of_evidence,
        }
