"""
Auto Discovery Engine

Lightweight, pure-Python tool discovery system.
Zero external dependencies - uses only stdlib.

Features:
- Auto-enriches HighLevelKey with extracted conditions, keywords
- Inverted indexes for multi-dimensional search
- Pre-computed similarity for related tools
- Efficient search across all dimensions

Design Rationale (based on actual data analysis):
- 75 tools, parameter sharing is sparse (6.6% density)
- Specialty/context sharing is dense (Critical Care: 56 tools)
- Graph libraries (networkx) add no value for this scale
- Simple similarity scoring works better than graph traversal

NO external dependencies required:
- No networkx (graph too sparse, not needed)
- No torch/transformers (tools are fixed, no semantic search needed)
- No numpy (pure Python math is fast enough for 75 tools)
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..services.base import BaseCalculator
    from ..value_objects.tool_keys import ClinicalContext, Specialty
    from .tool_registry import ToolRegistry


# =============================================================================
# Medical Term Dictionaries (for auto-extraction)
# =============================================================================

# Condition patterns - medical conditions that can be extracted from docstrings
CONDITION_PATTERNS: dict[str, list[str]] = {
    # Critical conditions
    "sepsis": ["sepsis", "septic", "敗血症"],
    "shock": ["shock", "休克"],
    "ards": ["ards", "acute respiratory distress"],
    "aki": ["aki", "acute kidney injury", "急性腎損傷"],
    "ckd": ["ckd", "chronic kidney disease", "慢性腎病"],
    "stroke": ["stroke", "cva", "中風"],
    "mi": ["myocardial infarction", "mi", "stemi", "nstemi", "心肌梗塞"],
    "heart_failure": ["heart failure", "hf", "chf", "心衰竭"],
    "trauma": ["trauma", "injury", "創傷"],
    "tbi": ["tbi", "traumatic brain", "頭部外傷"],
    "hemorrhage": ["hemorrhage", "bleeding", "出血"],
    "pe": ["pulmonary embolism", "pe", "肺栓塞"],
    "dvt": ["dvt", "deep vein thrombosis", "深層靜脈栓塞"],
    "pneumonia": ["pneumonia", "肺炎"],
    "delirium": ["delirium", "譫妄"],
    "coma": ["coma", "昏迷"],
    "liver_failure": ["liver failure", "hepatic failure", "肝衰竭"],
    "respiratory_failure": ["respiratory failure", "呼吸衰竭"],
    "anemia": ["anemia", "貧血"],
    "coagulopathy": ["coagulopathy", "dic", "凝血異常"],
    "acidosis": ["acidosis", "酸中毒"],
    "alkalosis": ["alkalosis", "鹼中毒"],
    "hyperkalemia": ["hyperkalemia", "高血鉀"],
    "hyponatremia": ["hyponatremia", "低血鈉"],
    "hypoglycemia": ["hypoglycemia", "低血糖"],
    "atrial_fibrillation": ["atrial fibrillation", "afib", "af", "心房顫動"],
    "cirrhosis": ["cirrhosis", "肝硬化"],
    "gi_bleeding": ["gi bleeding", "gastrointestinal bleeding", "消化道出血"],
    "pancreatitis": ["pancreatitis", "胰臟炎"],
    "meningitis": ["meningitis", "腦膜炎"],
    "encephalopathy": ["encephalopathy", "腦病變"],
    "osa": ["osa", "obstructive sleep apnea", "睡眠呼吸中止"],
    "ponv": ["ponv", "postoperative nausea", "術後噁心嘔吐"],
}

# Parameter to clinical domain mapping
PARAM_DOMAIN_MAP: dict[str, tuple[str, str]] = {
    # Renal
    "creatinine": ("renal", "腎功能"),
    "gfr": ("renal", "腎功能"),
    "bun": ("renal", "腎功能"),
    "urine": ("renal", "腎功能"),
    # Hepatic
    "bilirubin": ("hepatic", "肝功能"),
    "albumin": ("hepatic", "肝功能"),
    "inr": ("hepatic", "凝血功能"),
    "ast": ("hepatic", "肝功能"),
    "alt": ("hepatic", "肝功能"),
    # Cardiac
    "heart_rate": ("cardiac", "心臟功能"),
    "bp": ("cardiac", "血流動力學"),
    "systolic": ("cardiac", "血流動力學"),
    "diastolic": ("cardiac", "血流動力學"),
    "map": ("cardiac", "血流動力學"),
    "ejection": ("cardiac", "心臟功能"),
    "lvef": ("cardiac", "心臟功能"),
    "troponin": ("cardiac", "心肌損傷"),
    # Respiratory
    "fio2": ("respiratory", "呼吸功能"),
    "pao2": ("respiratory", "氧合狀態"),
    "spo2": ("respiratory", "氧合狀態"),
    "pco2": ("respiratory", "通氣狀態"),
    "respiratory_rate": ("respiratory", "呼吸功能"),
    "ventilator": ("respiratory", "呼吸支持"),
    # Neurological
    "gcs": ("neurological", "意識狀態"),
    "pupil": ("neurological", "神經功能"),
    "motor": ("neurological", "神經功能"),
    # Hematology
    "platelet": ("hematology", "凝血功能"),
    "hemoglobin": ("hematology", "血液功能"),
    "hematocrit": ("hematology", "血液功能"),
    "wbc": ("hematology", "感染指標"),
    # Metabolic
    "glucose": ("metabolic", "代謝功能"),
    "sodium": ("metabolic", "電解質"),
    "potassium": ("metabolic", "電解質"),
    "lactate": ("metabolic", "組織灌流"),
    "ph": ("metabolic", "酸鹼平衡"),
    "bicarbonate": ("metabolic", "酸鹼平衡"),
    # Demographics
    "age": ("demographics", "人口學"),
    "weight": ("demographics", "體型"),
    "height": ("demographics", "體型"),
    "sex": ("demographics", "人口學"),
    "bmi": ("demographics", "體型"),
}

# Clinical question templates based on context
QUESTION_TEMPLATES: dict[str, list[str]] = {
    "severity_assessment": [
        "How severe is {condition}?",
        "What is the severity of this patient's {condition}?",
        "{condition} 嚴重程度如何?",
    ],
    "prognosis": [
        "What is the prognosis for {condition}?",
        "What is the mortality risk?",
        "{condition} 的預後如何?",
    ],
    "risk_stratification": [
        "What is the risk of {outcome}?",
        "Should this patient be admitted?",
        "風險分層?",
    ],
    "diagnosis": [
        "Does this patient have {condition}?",
        "How to diagnose {condition}?",
        "是否為 {condition}?",
    ],
    "drug_dosing": [
        "What dose should I use?",
        "How to adjust dose for {organ} function?",
        "劑量如何調整?",
    ],
    "treatment_decision": [
        "Should I treat {condition}?",
        "What treatment is indicated?",
        "是否需要治療?",
    ],
    "preoperative_assessment": [
        "Is this patient fit for surgery?",
        "What is the surgical risk?",
        "術前風險評估?",
    ],
    "airway_management": [
        "Will intubation be difficult?",
        "How to assess the airway?",
        "氣道評估?",
    ],
    "sedation_assessment": [
        "What is the sedation level?",
        "Is the patient adequately sedated?",
        "鎮靜程度?",
    ],
    "transfusion_decision": [
        "Does this patient need transfusion?",
        "How much blood to give?",
        "是否需要輸血?",
    ],
}


@dataclass
class DiscoveryResult:
    """Result from discovery search."""

    tool_id: str
    score: float
    match_reasons: list[str]


@dataclass
class EnrichedHighLevelKey:
    """
    Auto-enriched HighLevelKey with extracted metadata.

    Contains both original (manual) and extracted (auto) fields.
    """

    # Original fields (from manual definition)
    specialties: tuple[Specialty, ...]
    clinical_contexts: tuple[ClinicalContext, ...]
    manual_conditions: tuple[str, ...]
    manual_keywords: tuple[str, ...]
    manual_questions: tuple[str, ...]
    icd10_codes: tuple[str, ...]

    # Auto-extracted fields
    extracted_conditions: tuple[str, ...]
    extracted_keywords: tuple[str, ...]
    extracted_questions: tuple[str, ...]
    extracted_domains: tuple[str, ...]  # e.g., "renal", "cardiac"

    @property
    def all_conditions(self) -> tuple[str, ...]:
        """Combine manual and extracted conditions."""
        return tuple(set(self.manual_conditions + self.extracted_conditions))

    @property
    def all_keywords(self) -> tuple[str, ...]:
        """Combine manual and extracted keywords."""
        return tuple(set(self.manual_keywords + self.extracted_keywords))

    @property
    def all_questions(self) -> tuple[str, ...]:
        """Combine manual and extracted questions."""
        return tuple(set(self.manual_questions + self.extracted_questions))


class AutoDiscoveryEngine:
    """
    Lightweight auto-discovery engine for medical calculators.

    Automatically enriches tool metadata by extracting:
    1. Conditions from docstrings (regex patterns)
    2. Keywords from parameter names and docstrings
    3. Clinical questions from context templates
    4. Clinical domains from parameter types

    Then builds multi-dimensional inverted indexes for fast search.

    Zero external dependencies - pure Python stdlib only.
    """

    def __init__(self) -> None:
        # Enriched metadata per tool
        self._enriched_keys: dict[str, EnrichedHighLevelKey] = {}

        # Inverted indexes (all lowercase for case-insensitive search)
        self._by_condition: dict[str, set[str]] = defaultdict(set)
        self._by_keyword: dict[str, set[str]] = defaultdict(set)
        self._by_domain: dict[str, set[str]] = defaultdict(set)
        self._by_param: dict[str, set[str]] = defaultdict(set)
        self._by_question_word: dict[str, set[str]] = defaultdict(set)

        # Pre-computed similarity (tool_id -> [(related_tool_id, score)])
        self._related_tools: dict[str, list[tuple[str, float]]] = {}

        # Build status
        self._is_built = False

    def build_from_registry(self, registry: ToolRegistry) -> None:
        """
        Build discovery indexes from registry.

        Called once at server startup. Extracts and indexes all metadata.
        """
        self._clear()

        # Step 1: Enrich each tool's metadata
        for tool_id in registry.list_all_ids():
            calc = registry.get_calculator(tool_id)
            if calc is None:
                continue

            enriched = self._enrich_tool(calc)
            self._enriched_keys[tool_id] = enriched

            # Build inverted indexes
            self._index_tool(tool_id, enriched, calc)

        # Step 2: Pre-compute related tools
        self._compute_all_similarities(registry)

        self._is_built = True

    def _clear(self) -> None:
        """Clear all indexes."""
        self._enriched_keys.clear()
        self._by_condition.clear()
        self._by_keyword.clear()
        self._by_domain.clear()
        self._by_param.clear()
        self._by_question_word.clear()
        self._related_tools.clear()
        self._is_built = False

    def _enrich_tool(self, calc: BaseCalculator) -> EnrichedHighLevelKey:
        """
        Extract additional metadata from a calculator.

        Returns EnrichedHighLevelKey with both manual and auto-extracted fields.
        """
        high_key = calc.high_level_key
        low_key = calc.metadata.low_level

        # Get docstring text for extraction
        doc = calc.calculate.__doc__ or ""
        class_doc = calc.__class__.__doc__ or ""
        full_doc = f"{class_doc} {doc} {low_key.purpose}".lower()

        # 1. Extract conditions from docstring
        extracted_conditions = self._extract_conditions(full_doc)

        # 2. Extract keywords from docstring + params
        extracted_keywords = self._extract_keywords(full_doc, low_key.input_params)

        # 3. Generate clinical questions from context
        extracted_questions = self._generate_questions(high_key.clinical_contexts, extracted_conditions)

        # 4. Extract clinical domains from parameters
        extracted_domains = self._extract_domains(low_key.input_params)

        return EnrichedHighLevelKey(
            specialties=high_key.specialties,
            clinical_contexts=high_key.clinical_contexts,
            manual_conditions=high_key.conditions,
            manual_keywords=high_key.keywords,
            manual_questions=high_key.clinical_questions,
            icd10_codes=high_key.icd10_codes,
            extracted_conditions=tuple(extracted_conditions),
            extracted_keywords=tuple(extracted_keywords),
            extracted_questions=tuple(extracted_questions),
            extracted_domains=tuple(extracted_domains),
        )

    def _extract_conditions(self, text: str) -> set[str]:
        """Extract medical conditions from text using patterns."""
        conditions: set[str] = set()

        for condition, patterns in CONDITION_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in text:
                    conditions.add(condition)
                    break

        return conditions

    def _extract_keywords(self, text: str, params: list[str]) -> set[str]:
        """Extract keywords from text and parameter names."""
        keywords: set[str] = set()

        # From parameter names
        for param in params:
            # Normalize: remove units, numbers
            clean = re.sub(r"_(mg_dl|mmhg|bpm|kg|cm|ml|min|h|score|value|level)$", "", param.lower())
            clean = re.sub(r"\d+", "", clean).strip("_")
            if len(clean) >= 3:
                keywords.add(clean)

        # From text - medical terms
        medical_patterns = [
            r"\b(score|scale|index|ratio|grade|stage|level|class)\b",
            r"\b(assessment|evaluation|prediction|estimation|calculation)\b",
            r"\b(mortality|survival|prognosis|outcome|risk)\b",
            r"\b(icu|emergency|surgical|operative|postoperative|preoperative)\b",
            r"\b(pediatric|neonatal|adult|geriatric)\b",
        ]

        for pattern in medical_patterns:
            matches = re.findall(pattern, text)
            keywords.update(matches)

        # Filter stopwords
        stopwords = {
            "the",
            "and",
            "for",
            "with",
            "from",
            "this",
            "that",
            "have",
            "been",
            "were",
            "will",
            "would",
            "could",
            "should",
            "using",
            "based",
            "calculate",
            "assessment",
            "score",
        }
        keywords -= stopwords

        return keywords

    def _generate_questions(
        self,
        contexts: tuple[ClinicalContext, ...],
        conditions: set[str],
    ) -> set[str]:
        """Generate clinical questions from context and conditions."""
        questions: set[str] = set()

        for context in contexts:
            templates = QUESTION_TEMPLATES.get(context.value, [])
            for template in templates:
                if "{condition}" in template:
                    for condition in conditions:
                        questions.add(template.replace("{condition}", condition))
                elif "{" not in template:
                    questions.add(template)

        return questions

    def _extract_domains(self, params: list[str]) -> set[str]:
        """Extract clinical domains from parameter names."""
        domains: set[str] = set()

        for param in params:
            param_lower = param.lower()
            for key, (domain, _) in PARAM_DOMAIN_MAP.items():
                if key in param_lower:
                    domains.add(domain)
                    break

        return domains

    def _index_tool(
        self,
        tool_id: str,
        enriched: EnrichedHighLevelKey,
        calc: BaseCalculator,
    ) -> None:
        """Add tool to all inverted indexes."""
        # Index conditions
        for condition in enriched.all_conditions:
            self._by_condition[condition.lower()].add(tool_id)

        # Index keywords
        for keyword in enriched.all_keywords:
            self._by_keyword[keyword.lower()].add(tool_id)

        # Index domains
        for domain in enriched.extracted_domains:
            self._by_domain[domain.lower()].add(tool_id)

        # Index parameters
        for param in calc.metadata.low_level.input_params:
            norm = self._normalize_param(param)
            self._by_param[norm].add(tool_id)

        # Index question words (for natural language search)
        for question in enriched.all_questions:
            words = re.findall(r"\b[a-z]{3,}\b", question.lower())
            for word in words:
                self._by_question_word[word].add(tool_id)

    def _normalize_param(self, param: str) -> str:
        """Normalize parameter name for matching."""
        param = re.sub(r"_(mg_dl|mmhg|bpm|kg|cm|ml|min|h|score|value|level)$", "", param.lower())
        param = re.sub(r"\d+", "", param)
        return param.strip("_")

    def _compute_all_similarities(self, registry: ToolRegistry) -> None:
        """Pre-compute related tools for each tool."""
        tool_ids = registry.list_all_ids()
        similarities: dict[str, list[tuple[str, float]]] = defaultdict(list)

        for i, tool1 in enumerate(tool_ids):
            enriched1 = self._enriched_keys.get(tool1)
            if enriched1 is None:
                continue

            for tool2 in tool_ids[i + 1 :]:
                enriched2 = self._enriched_keys.get(tool2)
                if enriched2 is None:
                    continue

                score = self._compute_similarity(enriched1, enriched2)

                if score > 0.15:  # Meaningful relationship threshold
                    similarities[tool1].append((tool2, score))
                    similarities[tool2].append((tool1, score))

        # Sort and cache top related tools
        for tool_id, related in similarities.items():
            related.sort(key=lambda x: x[1], reverse=True)
            self._related_tools[tool_id] = related[:10]

    def _compute_similarity(self, e1: EnrichedHighLevelKey, e2: EnrichedHighLevelKey) -> float:
        """Compute similarity between two enriched keys."""
        score = 0.0

        # Specialty overlap (weight: 0.35)
        specs1 = set(e1.specialties)
        specs2 = set(e2.specialties)
        if specs1 and specs2:
            score += 0.35 * len(specs1 & specs2) / len(specs1 | specs2)

        # Context overlap (weight: 0.25)
        ctx1 = set(e1.clinical_contexts)
        ctx2 = set(e2.clinical_contexts)
        if ctx1 and ctx2:
            score += 0.25 * len(ctx1 & ctx2) / len(ctx1 | ctx2)

        # Condition overlap (weight: 0.20)
        cond1 = set(e1.all_conditions)
        cond2 = set(e2.all_conditions)
        if cond1 and cond2:
            score += 0.20 * len(cond1 & cond2) / len(cond1 | cond2)

        # Domain overlap (weight: 0.15)
        dom1 = set(e1.extracted_domains)
        dom2 = set(e2.extracted_domains)
        if dom1 and dom2:
            score += 0.15 * len(dom1 & dom2) / len(dom1 | dom2)

        # Keyword overlap (weight: 0.05)
        kw1 = set(e1.all_keywords)
        kw2 = set(e2.all_keywords)
        if kw1 and kw2:
            score += 0.05 * len(kw1 & kw2) / len(kw1 | kw2)

        return score

    # =========================================================================
    # Public API
    # =========================================================================

    def search(self, query: str, limit: int = 10) -> list[DiscoveryResult]:
        """
        Search for tools matching a natural language query.

        Searches across all dimensions:
        - Conditions
        - Keywords
        - Domains
        - Parameters
        - Question words

        Returns ranked results with match reasons.
        """
        if not self._is_built:
            return []

        query_lower = query.lower()
        query_words = set(re.findall(r"\b[a-z]{3,}\b", query_lower))

        scores: dict[str, tuple[float, list[str]]] = {}

        def add_score(tool_id: str, points: float, reason: str) -> None:
            if tool_id not in scores:
                scores[tool_id] = (0.0, [])
            current, reasons = scores[tool_id]
            scores[tool_id] = (current + points, reasons + [reason])

        # Search conditions (highest weight)
        for word in query_words:
            for condition, tools in self._by_condition.items():
                if word in condition or condition in word:
                    for tool_id in tools:
                        add_score(tool_id, 3.0, f"condition:{condition}")

        # Search domains
        for word in query_words:
            for domain, tools in self._by_domain.items():
                if word in domain or domain in word:
                    for tool_id in tools:
                        add_score(tool_id, 2.0, f"domain:{domain}")

        # Search keywords
        for word in query_words:
            for keyword, tools in self._by_keyword.items():
                if word in keyword or keyword in word:
                    for tool_id in tools:
                        add_score(tool_id, 1.5, f"keyword:{keyword}")

        # Search parameters
        for word in query_words:
            for param, tools in self._by_param.items():
                if word in param or param in word:
                    for tool_id in tools:
                        add_score(tool_id, 1.0, f"param:{param}")

        # Search question words
        for word in query_words:
            if word in self._by_question_word:
                for tool_id in self._by_question_word[word]:
                    add_score(tool_id, 0.5, f"question:{word}")

        # Build and sort results
        results = [DiscoveryResult(tool_id=tid, score=score, match_reasons=reasons) for tid, (score, reasons) in scores.items() if score > 0]
        results.sort(key=lambda x: x.score, reverse=True)

        return results[:limit]

    def get_related_tools(self, tool_id: str, limit: int = 5) -> list[tuple[str, float]]:
        """
        Get tools related to the given tool.

        Returns list of (tool_id, similarity_score) tuples,
        sorted by similarity (highest first).
        """
        if not self._is_built:
            return []

        return self._related_tools.get(tool_id, [])[:limit]

    def find_tools_by_params(self, params: list[str]) -> list[str]:
        """
        Find tools that use the given parameters.

        Useful for: "I have creatinine and age, what can I calculate?"

        Returns tool IDs sorted by number of matching parameters.
        """
        if not self._is_built:
            return []

        matching: dict[str, int] = defaultdict(int)

        for param in params:
            norm = self._normalize_param(param)
            for tool_id in self._by_param.get(norm, set()):
                matching[tool_id] += 1

        # Sort by match count
        sorted_tools = sorted(matching.items(), key=lambda x: x[1], reverse=True)
        return [tool_id for tool_id, _ in sorted_tools]

    def find_tools_by_condition(self, condition: str) -> list[str]:
        """Find tools related to a specific condition."""
        if not self._is_built:
            return []

        condition_lower = condition.lower()
        matching: set[str] = set()

        for cond, tools in self._by_condition.items():
            if condition_lower in cond or cond in condition_lower:
                matching.update(tools)

        return list(matching)

    def find_tools_by_domain(self, domain: str) -> list[str]:
        """Find tools related to a clinical domain (renal, cardiac, etc.)."""
        if not self._is_built:
            return []

        return list(self._by_domain.get(domain.lower(), set()))

    def get_enriched_key(self, tool_id: str) -> EnrichedHighLevelKey | None:
        """Get the enriched HighLevelKey for a tool."""
        return self._enriched_keys.get(tool_id)

    def get_statistics(self) -> dict[str, int | bool]:
        """Get discovery engine statistics."""
        return {
            "total_tools": len(self._enriched_keys),
            "total_conditions": len(self._by_condition),
            "total_keywords": len(self._by_keyword),
            "total_domains": len(self._by_domain),
            "total_params": len(self._by_param),
            "total_relationships": sum(len(v) for v in self._related_tools.values()) // 2,
            "is_built": self._is_built,
        }


# =============================================================================
# Singleton Instance
# =============================================================================

_discovery_engine: AutoDiscoveryEngine | None = None


def get_discovery_engine() -> AutoDiscoveryEngine:
    """Get the global discovery engine instance."""
    global _discovery_engine
    if _discovery_engine is None:
        _discovery_engine = AutoDiscoveryEngine()
    return _discovery_engine
