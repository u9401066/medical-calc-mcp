# ruff: noqa: I001

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.shared.agent_benchmarking import (
    get_source_registry_entry,
    ingest_dataset_to_scenarios,
    load_source_registry,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = PROJECT_ROOT / "data" / "benchmarks" / "source_registry.json"
SAMPLE_DATASET = PROJECT_ROOT / "data" / "benchmarks" / "medcalc_bench_sample.csv"
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "benchmark_ingest.py"


class AgentBenchmarkIngestTests(unittest.TestCase):
    def test_load_source_registry(self) -> None:
        registry = load_source_registry(REGISTRY_PATH)

        self.assertIn("medcalc_bench_official", registry)
        self.assertEqual(registry["medcalc_bench_official"].host, "github")
        self.assertEqual(registry["medcalc_bench_official"].ingestion.input_format, "medcalc-bench-csv")

    def test_ingest_sample_dataset_to_scenarios(self) -> None:
        registry = load_source_registry(REGISTRY_PATH)
        source_entry = get_source_registry_entry(registry, "medcalc_bench_official")

        result = ingest_dataset_to_scenarios(SAMPLE_DATASET, source_entry=source_entry)

        self.assertEqual(result.total_records, 6)
        self.assertEqual(result.converted_records, 6)
        self.assertEqual(result.skipped_records, 0)

        first_scenario = result.scenarios[0]
        self.assertEqual(first_scenario.source_id, "medcalc_bench_official")
        self.assertEqual(first_scenario.task_family, "calculator_execution")
        self.assertEqual(first_scenario.expected_tools, ("body_surface_area",))
        self.assertEqual(
            first_scenario.gold_workflow,
            ("get_tool_schema:body_surface_area", "calculate:body_surface_area"),
        )
        self.assertEqual(first_scenario.expected_result["numeric"], 1.8447)

    def test_cli_writes_scenarios(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "scenarios.jsonl"
            summary_path = Path(temp_dir) / "summary.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--dataset",
                    str(SAMPLE_DATASET),
                    "--source-id",
                    "medcalc_bench_official",
                    "--registry",
                    str(REGISTRY_PATH),
                    "--output",
                    str(output_path),
                    "--summary-json",
                    str(summary_path),
                    "--fail-on-skipped",
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, msg=completed.stderr or completed.stdout)
            self.assertTrue(output_path.exists())
            self.assertTrue(summary_path.exists())

            scenario_lines = output_path.read_text(encoding="utf-8").splitlines()
            summary_payload = json.loads(summary_path.read_text(encoding="utf-8"))
            first_payload = json.loads(scenario_lines[0])

            self.assertEqual(len(scenario_lines), 6)
            self.assertEqual(summary_payload["converted_records"], 6)
            self.assertEqual(first_payload["source_id"], "medcalc_bench_official")
            self.assertEqual(first_payload["expected_tools"], ["body_surface_area"])


if __name__ == "__main__":
    unittest.main()
