#!/usr/bin/env python
"""Build a HF-style benchmark dataset from validated calculator test cases."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.domain.registry import ToolRegistry  # noqa: E402
from src.domain.services.base import BaseCalculator  # noqa: E402
from src.domain.services.calculators import CALCULATORS  # noqa: E402
from src.shared.hf_benchmark_dataset import HfBenchmarkCase, write_hf_benchmark_cases_jsonl  # noqa: E402

KEYWORD_SKIP_TOKENS = (
    "invalid",
    "raises",
    "error",
    "missing",
    "exception",
)
GUIDELINE_DOMAIN_LABELS = {
    "敗血症/重症": "Sepsis / Critical Care",
    "心血管": "Cardiovascular",
    "消化道出血": "GI Bleeding",
    "肝臟疾病": "Liver Disease",
    "腎臟疾病": "Kidney Disease",
    "肺炎/呼吸": "Respiratory / Pneumonia",
    "血栓栓塞": "Thromboembolism",
    "神經科": "Neurology",
    "麻醉科": "Anesthesiology",
    "創傷": "Trauma",
    "燒傷": "Burns",
    "小兒科": "Pediatrics",
    "腫瘤科": "Oncology",
    "營養科": "Nutrition",
    "風濕科": "Rheumatology",
    "骨質疏鬆": "Osteoporosis",
}
CURATED_SEED_CASES: dict[str, list[dict[str, Any]]] = {
    "ecog_performance_status": [
        {"ecog_grade": 0},
        {"ecog_grade": 2},
        {"ecog_grade": 4},
    ],
    "karnofsky_performance_scale": [
        {"kps_score": 90},
        {"kps_score": 60},
        {"kps_score": 30},
    ],
    "nrs_2002": [
        {"bmi": 22.0, "weight_loss_percent_3m": 2.0, "reduced_intake_percent": 90.0, "disease_severity": 1, "age": 65},
        {"bmi": 18.0, "weight_loss_percent_3m": 8.0, "reduced_intake_percent": 45.0, "disease_severity": 2, "age": 74},
        {"bmi": 16.5, "weight_loss_percent_3m": 12.0, "reduced_intake_percent": 20.0, "disease_severity": 3, "age": 81},
    ],
    "nutric_score": [
        {"age": 45, "apache_ii": 12, "sofa": 4, "comorbidities": 1, "days_hospital_to_icu": 0},
        {"age": 68, "apache_ii": 18, "sofa": 7, "comorbidities": 2, "days_hospital_to_icu": 1},
        {"age": 79, "apache_ii": 30, "sofa": 12, "comorbidities": 3, "days_hospital_to_icu": 3},
    ],
    "das28": [
        {"tender_joint_count": 1, "swollen_joint_count": 1, "patient_global_assessment": 15.0, "esr": 12.0},
        {"tender_joint_count": 8, "swollen_joint_count": 6, "patient_global_assessment": 60.0, "esr": 45.0},
        {"tender_joint_count": 12, "swollen_joint_count": 10, "patient_global_assessment": 80.0, "crp": 25.0},
    ],
    "frax": [
        {
            "age": 65,
            "sex": "female",
            "weight": 60.0,
            "height": 160.0,
            "previous_fracture": False,
            "parent_hip_fracture": False,
            "smoking": False,
            "glucocorticoids": False,
            "rheumatoid_arthritis": False,
            "secondary_osteoporosis": False,
            "alcohol_3_or_more": False,
            "bmd_tscore": -1.5,
        },
        {
            "age": 78,
            "sex": "female",
            "weight": 52.0,
            "height": 156.0,
            "previous_fracture": True,
            "parent_hip_fracture": True,
            "smoking": False,
            "glucocorticoids": True,
            "rheumatoid_arthritis": True,
            "secondary_osteoporosis": False,
            "alcohol_3_or_more": False,
            "bmd_tscore": -2.8,
        },
        {
            "age": 72,
            "sex": "male",
            "weight": 70.0,
            "height": 172.0,
            "previous_fracture": True,
            "parent_hip_fracture": False,
            "smoking": True,
            "glucocorticoids": False,
            "rheumatoid_arthritis": False,
            "secondary_osteoporosis": True,
            "alcohol_3_or_more": True,
            "bmd_tscore": -2.2,
        },
    ],
}


@dataclass(frozen=True)
class ExtractedCall:
    test_file: str
    test_name: str
    line_number: int
    calculator_class_name: str
    kwargs: dict[str, Any]


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()
    for calculator_class in CALCULATORS:
        registry.register(calculator_class())
    return registry


def build_calculator_instances() -> dict[str, BaseCalculator]:
    return {calculator_class.__name__: calculator_class() for calculator_class in CALCULATORS}


def parse_guideline_tool_domains() -> dict[str, tuple[str, ...]]:
    doc_path = PROJECT_ROOT / "docs" / "GUIDELINE_RECOMMENDED_TOOLS_2023_2025.md"
    lines = doc_path.read_text(encoding="utf-8").splitlines()
    in_summary = False
    domain_map: dict[str, set[str]] = defaultdict(set)

    for line in lines:
        if line.startswith("## 📊 整體對照摘要"):
            in_summary = True
            continue
        if not in_summary:
            continue
        if in_summary and domain_map and not line.lstrip().startswith("|"):
            break
        if not line.lstrip().startswith("|"):
            continue
        parts = [part.strip() for part in line.split("|")]
        if len(parts) < 5:
            continue
        domain_zh = parts[1]
        if domain_zh in {"", "領域"} or set(domain_zh) == {"-"}:
            continue
        domain_en = GUIDELINE_DOMAIN_LABELS.get(domain_zh, domain_zh)
        raw_tools = [item.strip().strip("`*") for item in parts[2].split(",")]
        for raw_tool in raw_tools:
            tool_id = raw_tool.strip()
            if not tool_id:
                continue
            normalized = (
                tool_id.replace(" ", "_")
                .replace("&", "and")
                .replace("/", "_")
                .replace("-", "_")
                .replace(".", "")
            )
            normalized = normalized.lower()
            alias_map = {
                "news2": "news_score",
                "gcs": "glasgow_coma_scale",
                "mrs": "modified_rankin_scale",
                "timi": "timi_stemi",
                "pesi_spesi": "spesi",
                "spesi": "spesi",
                "meld_na": "meld_score",
                "meld": "meld_score",
                "asa": "asa_physical_status",
                "stop_bang": "stop_bang",
                "apfel": "apfel_ponv",
                "aldrete": "aldrete_score",
                "pf_ratio": "pf_ratio",
                "murray_score": "murray_lung_injury_score",
                "hunt_and_hess": "hunt_hess",
                "4at": "four_at",
                "psi_port": "psi_port",
                "ecog_ps": "ecog_performance_status",
                "karnofsky": "karnofsky_performance_scale",
                "nrs_2002": "nrs_2002",
                "nutric": "nutric_score",
                "das28": "das28",
                "frax": "frax",
                "qsofa": "qsofa_score",
                "apache_ii": "apache_ii",
                "cam_icu": "cam_icu",
                "icdsc": "icdsc",
                "rockall": "rockall_score",
                "glasgow_blatchford": "glasgow_blatchford",
                "aims65": "aims65",
                "child_pugh": "child_pugh",
                "maddrey_df": "maddrey_df",
                "lille_model": "lille_model",
                "ckd_epi_2021": "ckd_epi_2021",
                "kdigo_aki": "kdigo_aki",
                "wells_dvt": "wells_dvt",
                "wells_pe": "wells_pe",
                "caprini_vte": "caprini_vte",
                "sofa": "sofa_score",
                "sofa_2": "sofa2_score",
                "rass": "rass",
                "heart": "heart_score",
                "grace": "grace_score",
                "cha2ds2_vasc": "chads2_vasc",
                "cha2ds2_va": "chads2_va",
                "has_bled": "has_bled",
                "euroscore_ii": "euroscore_ii",
                "hfa_peff": "hfa_peff",
                "score2": "score2",
                "iss": "iss",
                "rts": "rts",
                "triss": "triss",
                "parkland": "parkland_formula",
                "tbsa": "tbsa",
                "pews": "pews",
                "psofa_phoenix_2024": "pediatric_sofa",
                "fib_4": "fib4_index",
            }
            resolved = alias_map.get(normalized, normalized)
            domain_map[resolved].add(domain_en)
    return {tool_id: tuple(sorted(domains)) for tool_id, domains in domain_map.items()}


def _called_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _target_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "self":
        return f"self.{node.attr}"
    return None


def _literal_value(node: ast.AST) -> tuple[bool, Any]:
    if isinstance(node, ast.Constant):
        return True, node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        success, value = _literal_value(node.operand)
        if not success or not isinstance(value, (int, float)):
            return False, None
        return True, -value if isinstance(node.op, ast.USub) else value
    if isinstance(node, ast.Tuple):
        tuple_values: list[Any] = []
        for item in node.elts:
            success, value = _literal_value(item)
            if not success:
                return False, None
            tuple_values.append(value)
        return True, tuple(tuple_values)
    if isinstance(node, ast.List):
        list_values: list[Any] = []
        for item in node.elts:
            success, value = _literal_value(item)
            if not success:
                return False, None
            list_values.append(value)
        return True, list_values
    if isinstance(node, ast.Dict):
        dict_values: dict[str, Any] = {}
        for key_node, value_node in zip(node.keys, node.values, strict=False):
            if key_node is None:
                return False, None
            success_key, key_value = _literal_value(key_node)
            success_value, value = _literal_value(value_node)
            if not success_key or not success_value or not isinstance(key_value, str):
                return False, None
            dict_values[key_value] = value
        return True, dict_values
    return False, None


def _is_calculator_constructor(node: ast.AST, known_class_names: set[str]) -> str | None:
    if not isinstance(node, ast.Call):
        return None
    name = _called_name(node.func)
    if name in known_class_names:
        return name
    return None


def _extract_call_from_node(
    call_node: ast.Call,
    *,
    env: dict[str, str],
    known_class_names: set[str],
    test_file: Path,
    test_name: str,
) -> ExtractedCall | None:
    calculator_class_name: str | None = None
    func = call_node.func
    if isinstance(func, ast.Attribute) and func.attr == "calculate":
        direct_constructor = _is_calculator_constructor(func.value, known_class_names)
        if direct_constructor is not None:
            calculator_class_name = direct_constructor
        else:
            base_name = _target_name(func.value) or (func.value.id if isinstance(func.value, ast.Name) else None)
            if base_name is not None:
                calculator_class_name = env.get(base_name)
    if calculator_class_name is None:
        return None
    if call_node.args:
        return None
    kwargs: dict[str, Any] = {}
    for keyword in call_node.keywords:
        if keyword.arg is None:
            return None
        success, value = _literal_value(keyword.value)
        if not success:
            return None
        kwargs[keyword.arg] = value
    if not kwargs:
        return None
    lowered_name = test_name.lower()
    if any(token in lowered_name for token in KEYWORD_SKIP_TOKENS):
        return None
    return ExtractedCall(
        test_file=str(test_file.relative_to(PROJECT_ROOT)),
        test_name=test_name,
        line_number=call_node.lineno,
        calculator_class_name=calculator_class_name,
        kwargs=kwargs,
    )


def _collect_self_assignments(class_node: ast.ClassDef, known_class_names: set[str]) -> dict[str, str]:
    assignments: dict[str, str] = {}
    for node in ast.walk(class_node):
        if not isinstance(node, ast.Assign):
            continue
        class_name = _is_calculator_constructor(node.value, known_class_names)
        if class_name is None:
            continue
        for target in node.targets:
            target_name = _target_name(target)
            if target_name is not None:
                assignments[target_name] = class_name
    return assignments


def _is_pytest_fixture(function_node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for decorator in function_node.decorator_list:
        if isinstance(decorator, ast.Attribute) and decorator.attr == "fixture":
            return True
        if isinstance(decorator, ast.Name) and decorator.id == "fixture":
            return True
        if isinstance(decorator, ast.Call):
            name = _called_name(decorator.func)
            if name == "fixture":
                return True
    return False


def _fixture_returned_calculator(
    function_node: ast.FunctionDef | ast.AsyncFunctionDef,
    known_class_names: set[str],
) -> str | None:
    for node in ast.walk(function_node):
        if not isinstance(node, ast.Return) or node.value is None:
            continue
        class_name = _is_calculator_constructor(node.value, known_class_names)
        if class_name is not None:
            return class_name
    return None


def _collect_module_fixture_map(module_node: ast.Module, known_class_names: set[str]) -> dict[str, str]:
    fixture_map: dict[str, str] = {}
    for node in module_node.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or not _is_pytest_fixture(node):
            continue
        returned_class = _fixture_returned_calculator(node, known_class_names)
        if returned_class is not None:
            fixture_map[node.name] = returned_class
    return fixture_map


def _collect_class_fixture_map(class_node: ast.ClassDef, known_class_names: set[str]) -> dict[str, str]:
    fixture_map: dict[str, str] = {}
    for node in class_node.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or not _is_pytest_fixture(node):
            continue
        returned_class = _fixture_returned_calculator(node, known_class_names)
        if returned_class is not None:
            fixture_map[node.name] = returned_class
    return fixture_map


def _collect_calls_from_function(
    function_node: ast.FunctionDef | ast.AsyncFunctionDef,
    *,
    base_env: dict[str, str],
    fixture_map: dict[str, str],
    known_class_names: set[str],
    test_file: Path,
    test_name: str,
) -> list[ExtractedCall]:
    env = dict(base_env)
    for argument in function_node.args.args:
        if argument.arg in {"self", "cls"}:
            continue
        fixture_class = fixture_map.get(argument.arg)
        if fixture_class is not None:
            env[argument.arg] = fixture_class
    extracted: list[ExtractedCall] = []
    for statement in function_node.body:
        if isinstance(statement, ast.Assign):
            class_name = _is_calculator_constructor(statement.value, known_class_names)
            if class_name is not None:
                for target in statement.targets:
                    target_name = _target_name(target)
                    if target_name is None and isinstance(target, ast.Name):
                        target_name = target.id
                    if target_name is not None:
                        env[target_name] = class_name
        for node in ast.walk(statement):
            if not isinstance(node, ast.Call):
                continue
            extracted_call = _extract_call_from_node(
                node,
                env=env,
                known_class_names=known_class_names,
                test_file=test_file,
                test_name=test_name,
            )
            if extracted_call is not None:
                extracted.append(extracted_call)
    return extracted


def extract_calls_from_test_file(test_file: Path, known_class_names: set[str]) -> list[ExtractedCall]:
    tree = ast.parse(test_file.read_text(encoding="utf-8"), filename=str(test_file))
    extracted: list[ExtractedCall] = []
    module_fixture_map = _collect_module_fixture_map(tree, known_class_names)
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            extracted.extend(
                _collect_calls_from_function(
                    node,
                    base_env={},
                    fixture_map=module_fixture_map,
                    known_class_names=known_class_names,
                    test_file=test_file,
                    test_name=node.name,
                )
            )
        elif isinstance(node, ast.ClassDef):
            base_env = _collect_self_assignments(node, known_class_names)
            class_fixture_map = {**module_fixture_map, **_collect_class_fixture_map(node, known_class_names)}
            for body_node in node.body:
                if isinstance(body_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    extracted.extend(
                        _collect_calls_from_function(
                            body_node,
                            base_env=base_env,
                            fixture_map=class_fixture_map,
                            known_class_names=known_class_names,
                            test_file=test_file,
                            test_name=f"{node.name}.{body_node.name}",
                        )
                    )
    return extracted


def extract_calls_from_tests(tests_dir: Path, known_class_names: set[str]) -> list[ExtractedCall]:
    extracted: list[ExtractedCall] = []
    for test_file in sorted(tests_dir.glob("test_*.py")):
        extracted.extend(extract_calls_from_test_file(test_file, known_class_names))
    return extracted


def build_curated_seed_calls(calculators_by_class_name: dict[str, BaseCalculator]) -> list[ExtractedCall]:
    """Add curated seeds for guideline tools that do not yet have direct test coverage."""

    tool_id_to_class_name = {calculator.tool_id: class_name for class_name, calculator in calculators_by_class_name.items()}
    extracted: list[ExtractedCall] = []
    for tool_id, payloads in CURATED_SEED_CASES.items():
        class_name = tool_id_to_class_name.get(tool_id)
        if class_name is None:
            continue
        for index, payload in enumerate(payloads, start=1):
            extracted.append(
                ExtractedCall(
                    test_file="curated_guideline_seeds",
                    test_name=f"curated.{tool_id}.{index}",
                    line_number=index,
                    calculator_class_name=class_name,
                    kwargs=payload,
                )
            )
    return extracted


def _canonical_params(params: dict[str, Any]) -> str:
    return json.dumps(params, ensure_ascii=False, sort_keys=True)


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return f"{value:g}"
    return str(value)


def _build_question(tool_id: str, metadata: Any, params: dict[str, Any]) -> str:
    param_text = ", ".join(f"{key}={_format_value(value)}" for key, value in sorted(params.items()))
    return (
        f"Use the canonical tool {tool_id} ({metadata.low_level.name}) to calculate the clinically bounded result "
        f"from the following structured inputs: {param_text}. Return a grounded numeric answer."
    )


def _determine_split(index: int, total: int) -> str:
    train_cutoff = int(total * 0.7)
    validation_cutoff = int(total * 0.85)
    if index < train_cutoff:
        return "train"
    if index < validation_cutoff:
        return "validation"
    return "test"


def _build_case(
    *,
    calculator: BaseCalculator,
    params: dict[str, Any],
    expected_value: float,
    extracted_call: ExtractedCall,
    ordinal: int,
) -> HfBenchmarkCase:
    metadata = calculator.metadata
    tool_id = calculator.tool_id
    primary_specialty = metadata.high_level.specialties[0].value if metadata.high_level.specialties else "other"
    tolerance = 0.0 if float(expected_value).is_integer() else 1e-6
    references = tuple(reference.to_dict() for reference in metadata.references)
    return HfBenchmarkCase(
        case_id=f"{tool_id}_{ordinal:04d}",
        source="medical_calc_mcp_unit_tests",
        split="unspecified",
        question=_build_question(tool_id, metadata, params),
        tool_id=tool_id,
        calculator_name=metadata.low_level.name,
        params=params,
        expected_value=expected_value,
        abs_tolerance=tolerance,
        lower_limit=expected_value - tolerance,
        upper_limit=expected_value + tolerance,
        primary_specialty=primary_specialty,
        specialties=tuple(s.value for s in metadata.high_level.specialties),
        guideline_domains=(),
        formula_source_type=metadata.formula_source_type,
        references=references,
        provenance={
            "source_test_file": extracted_call.test_file,
            "source_test_name": extracted_call.test_name,
            "source_line_number": extracted_call.line_number,
            "calculator_class_name": extracted_call.calculator_class_name,
        },
    )


def build_seed_cases(
    extracted_calls: Iterable[ExtractedCall],
    calculators_by_class_name: dict[str, BaseCalculator],
) -> list[HfBenchmarkCase]:
    deduped: dict[tuple[str, str], ExtractedCall] = {}
    for extracted_call in extracted_calls:
        calculator = calculators_by_class_name.get(extracted_call.calculator_class_name)
        if calculator is None:
            continue
        dedupe_key = (calculator.tool_id, _canonical_params(extracted_call.kwargs))
        deduped.setdefault(dedupe_key, extracted_call)

    valid_payloads: list[tuple[ExtractedCall, BaseCalculator, float]] = []
    for extracted_call in deduped.values():
        calculator = calculators_by_class_name[extracted_call.calculator_class_name]
        try:
            result = calculator.calculate(**extracted_call.kwargs)
        except Exception:
            continue
        if not isinstance(result.value, (int, float)):
            continue
        valid_payloads.append((extracted_call, calculator, float(result.value)))

    ordered_payloads = sorted(
        valid_payloads,
        key=lambda item: (item[1].tool_id, item[0].test_file, item[0].line_number),
    )
    cases: list[HfBenchmarkCase] = []
    per_tool_counter: Counter[str] = Counter()

    for extracted_call, calculator, expected_value in ordered_payloads:
        tool_id = calculator.tool_id
        per_tool_counter[tool_id] += 1
        cases.append(_build_case(calculator=calculator, params=extracted_call.kwargs, expected_value=expected_value, extracted_call=extracted_call, ordinal=per_tool_counter[tool_id]))
    return cases


def augment_cases(
    seed_cases: list[HfBenchmarkCase],
    calculators_by_tool_id: dict[str, BaseCalculator],
    *,
    target_cases: int,
) -> list[HfBenchmarkCase]:
    """Expand seed cases using observed per-tool parameter values and retain only executable variants."""

    by_tool_param_values: dict[str, dict[str, list[Any]]] = defaultdict(lambda: defaultdict(list))
    for case in seed_cases:
        for param_name, value in case.params.items():
            bucket = by_tool_param_values[case.tool_id][param_name]
            if value not in bucket:
                bucket.append(value)

    augmented = list(seed_cases)
    seen = {(case.tool_id, _canonical_params(case.params)) for case in seed_cases}
    per_tool_counter = Counter(case.tool_id for case in seed_cases)

    for seed_case in seed_cases:
        if len(augmented) >= target_cases:
            break
        calculator = calculators_by_tool_id[seed_case.tool_id]
        observed_values = by_tool_param_values[seed_case.tool_id]
        for param_name in sorted(seed_case.params):
            current_value = seed_case.params[param_name]
            alternatives = [value for value in observed_values.get(param_name, []) if value != current_value]
            for alternative in alternatives[:4]:
                if len(augmented) >= target_cases:
                    break
                candidate_params = {**seed_case.params, param_name: alternative}
                dedupe_key = (seed_case.tool_id, _canonical_params(candidate_params))
                if dedupe_key in seen:
                    continue
                try:
                    result = calculator.calculate(**candidate_params)
                except Exception:
                    continue
                if not isinstance(result.value, (int, float)):
                    continue
                per_tool_counter[seed_case.tool_id] += 1
                augmented.append(
                    _build_case(
                        calculator=calculator,
                        params=candidate_params,
                        expected_value=float(result.value),
                        extracted_call=ExtractedCall(
                            test_file=str(seed_case.provenance.get("source_test_file", "generated")),
                            test_name=str(seed_case.provenance.get("source_test_name", "generated_variant")),
                            line_number=int(seed_case.provenance.get("source_line_number", 0)),
                            calculator_class_name=str(seed_case.provenance.get("calculator_class_name", calculator.__class__.__name__)),
                            kwargs=candidate_params,
                        ),
                        ordinal=per_tool_counter[seed_case.tool_id],
                    )
                )
                seen.add(dedupe_key)
            if len(augmented) >= target_cases:
                break
    return augmented


def assign_case_metadata(
    cases: list[HfBenchmarkCase],
    guideline_domain_map: dict[str, tuple[str, ...]],
) -> list[HfBenchmarkCase]:
    total = len(cases)
    ordered = sorted(cases, key=lambda case: (case.tool_id, case.case_id))
    assigned: list[HfBenchmarkCase] = []
    for index, case in enumerate(ordered):
        payload = case.to_dict()
        payload["split"] = _determine_split(index, total)
        payload["guideline_domains"] = list(guideline_domain_map.get(case.tool_id, ()))
        assigned.append(HfBenchmarkCase.from_dict(payload))
    return assigned


def rebalance_splits(cases: list[HfBenchmarkCase], required_domains: set[str]) -> list[HfBenchmarkCase]:
    """Ensure the test split covers all required guideline domains."""

    if not cases:
        return cases
    test_domains = {domain for case in cases if case.split == "test" for domain in case.guideline_domains}
    missing_domains = sorted(required_domains - test_domains)
    if not missing_domains:
        return cases

    by_domain_non_test: dict[str, list[int]] = defaultdict(list)
    for index, case in enumerate(cases):
        if case.split == "test":
            continue
        for domain in case.guideline_domains:
            by_domain_non_test[domain].append(index)

    updated = list(cases)
    train_indexes = [index for index, case in enumerate(updated) if case.split == "train"]
    for domain in missing_domains:
        candidates = by_domain_non_test.get(domain, [])
        if not candidates:
            continue
        promote_index = candidates[0]
        demote_index = train_indexes.pop() if train_indexes else None
        promote_case = updated[promote_index]
        updated[promote_index] = HfBenchmarkCase(**{**promote_case.to_dict(), "split": "test"})
        if demote_index is not None and demote_index != promote_index:
            demote_case = updated[demote_index]
            updated[demote_index] = HfBenchmarkCase(**{**demote_case.to_dict(), "split": "train"})
    return updated


def write_split_files(cases: list[HfBenchmarkCase], output_dir: Path) -> None:
    by_split: dict[str, list[HfBenchmarkCase]] = defaultdict(list)
    for case in cases:
        by_split[case.split].append(case)
    for split_name, split_cases in by_split.items():
        write_hf_benchmark_cases_jsonl(split_cases, output_dir / f"{split_name}.jsonl")
    write_hf_benchmark_cases_jsonl(cases, output_dir / "all.jsonl")


def _reassign_split(case: HfBenchmarkCase, split: str) -> HfBenchmarkCase:
    payload = case.to_dict()
    payload["split"] = split
    return HfBenchmarkCase.from_dict(payload)


def _sha256_for_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_release_bundle(cases: list[HfBenchmarkCase], output_dir: Path) -> dict[str, Any]:
    release_dir = output_dir / "release"
    public_dev_dir = release_dir / "public-dev"
    hidden_test_dir = release_dir / "hidden-test"

    public_train = [case for case in cases if case.split == "train"]
    public_validation = [case for case in cases if case.split == "validation"]
    public_dev_all = public_train + public_validation
    hidden_test_cases = [_reassign_split(case, "hidden_test") for case in cases if case.split == "test"]

    public_files: list[tuple[str, list[HfBenchmarkCase], Path]] = [
        ("train", public_train, public_dev_dir / "train.jsonl"),
        ("validation", public_validation, public_dev_dir / "validation.jsonl"),
        ("public_dev", public_dev_all, public_dev_dir / "public-dev.jsonl"),
    ]
    hidden_files: list[tuple[str, list[HfBenchmarkCase], Path]] = [
        ("hidden_test", hidden_test_cases, hidden_test_dir / "hidden-test.jsonl"),
    ]

    for _, split_cases, path in [*public_files, *hidden_files]:
        write_hf_benchmark_cases_jsonl(split_cases, path)

    manifest = {
        "dataset_id": "medical-calc-mcp-hf-v1",
        "release_layout_version": 1,
        "public_release": {
            "directory": "release/public-dev",
            "hf_repo_ready": True,
            "splits": {
                "train": len(public_train),
                "validation": len(public_validation),
                "public_dev": len(public_dev_all),
            },
            "files": [
                {
                    "split": split_name,
                    "path": str(path.relative_to(output_dir)).replace("\\", "/"),
                    "records": len(split_cases),
                    "sha256": _sha256_for_file(path),
                }
                for split_name, split_cases, path in public_files
            ],
        },
        "private_release": {
            "directory": "release/hidden-test",
            "push_policy": "private-only",
            "splits": {
                "hidden_test": len(hidden_test_cases),
            },
            "files": [
                {
                    "split": split_name,
                    "path": str(path.relative_to(output_dir)).replace("\\", "/"),
                    "records": len(split_cases),
                    "sha256": _sha256_for_file(path),
                }
                for split_name, split_cases, path in hidden_files
            ],
        },
        "git_segments": {
            "public_paths": [
                "README.md",
                "metadata.json",
                "coverage_audit.json",
                "release/public-dev/train.jsonl",
                "release/public-dev/validation.jsonl",
                "release/public-dev/public-dev.jsonl",
            ],
            "private_paths": [
                "release/hidden-test/hidden-test.jsonl",
                "release_manifest.json",
                "RELEASE_CHECKLIST.md",
            ],
        },
    }
    (output_dir / "release_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "public_dev_total": len(public_dev_all),
        "hidden_test_total": len(hidden_test_cases),
        "public_splits": {
            "train": len(public_train),
            "validation": len(public_validation),
            "public_dev": len(public_dev_all),
        },
        "private_splits": {
            "hidden_test": len(hidden_test_cases),
        },
        "manifest_path": "release_manifest.json",
        "public_dir": "release/public-dev",
        "hidden_dir": "release/hidden-test",
    }


def write_metadata(
    cases: list[HfBenchmarkCase],
    output_dir: Path,
    extracted_call_count: int,
    release_packaging: dict[str, Any],
) -> None:
    by_split = Counter(case.split for case in cases)
    domain_counts = Counter(domain for case in cases for domain in case.guideline_domains)
    payload = {
        "dataset_id": "medical-calc-mcp-hf-v1",
        "generated_from": "unit_test_extraction",
        "extracted_calculate_calls": extracted_call_count,
        "total_cases": len(cases),
        "unique_tools": len({case.tool_id for case in cases}),
        "unique_primary_specialties": len({case.primary_specialty for case in cases}),
        "unique_guideline_domains": len(domain_counts),
        "splits": dict(sorted(by_split.items())),
        "guideline_domains": dict(sorted(domain_counts.items())),
        "release_packaging": release_packaging,
    }
    (output_dir / "metadata.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build HF-style benchmark dataset from validated calculator tests")
    parser.add_argument(
        "--tests-dir",
        default=str(PROJECT_ROOT / "tests"),
        help="Directory containing calculator tests.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "data" / "benchmarks" / "medical_calc_mcp_hf_v1"),
        help="Directory to write the dataset files.",
    )
    parser.add_argument(
        "--min-cases",
        type=int,
        default=500,
        help="Fail if fewer than this many valid cases are produced.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    tests_dir = Path(args.tests_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    registry = build_registry()
    calculators_by_class_name = build_calculator_instances()
    extracted_calls = extract_calls_from_tests(tests_dir, set(calculators_by_class_name))
    extracted_calls.extend(build_curated_seed_calls(calculators_by_class_name))
    guideline_domain_map = parse_guideline_tool_domains()
    calculators_by_tool_id = {calculator.tool_id: calculator for calculator in calculators_by_class_name.values()}

    seed_cases = build_seed_cases(extracted_calls, calculators_by_class_name)
    target_cases = max(args.min_cases + 100, 600)
    cases = augment_cases(seed_cases, calculators_by_tool_id, target_cases=target_cases)
    cases = assign_case_metadata(cases, guideline_domain_map)
    required_domains = set(GUIDELINE_DOMAIN_LABELS.values())
    cases = rebalance_splits(cases, required_domains)

    if len(cases) < args.min_cases:
        print(f"Generated only {len(cases)} cases; required at least {args.min_cases}.")
        return 1

    uncovered_domains = sorted(required_domains - {domain for case in cases for domain in case.guideline_domains})
    if uncovered_domains:
        print("Missing guideline domains: " + ", ".join(uncovered_domains))
        return 1

    unique_tools = {case.tool_id for case in cases}
    if len(unique_tools) < len(registry.list_all_ids()) // 2:
        print("Coverage is too narrow for an HF release candidate.")
        return 1

    write_split_files(cases, output_dir)
    release_packaging = write_release_bundle(cases, output_dir)
    write_metadata(cases, output_dir, len(extracted_calls), release_packaging)

    print(f"Extracted calculate calls: {len(extracted_calls)}")
    print(f"Generated valid benchmark cases: {len(cases)}")
    print(f"Unique tools covered: {len(unique_tools)}")
    print(f"Guideline domains covered: {len({domain for case in cases for domain in case.guideline_domains})}")
    print(f"Wrote dataset to {output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
