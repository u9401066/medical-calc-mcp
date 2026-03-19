import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.shared.benchmarking import evaluate_cases, load_benchmark_cases


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DATASET = PROJECT_ROOT / "data" / "benchmarks" / "medcalc_bench_sample.csv"
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "medcalc_bench_eval.py"


class MedCalcBenchEvalTests(unittest.TestCase):
    def test_load_sample_dataset(self) -> None:
        cases = load_benchmark_cases(SAMPLE_DATASET)

        self.assertEqual(len(cases), 6)
        self.assertEqual(cases[0].calculator_name, "bsa_calculator")
        self.assertEqual(cases[0].params["height_cm"], 175)

    def test_evaluate_sample_dataset(self) -> None:
        summary = evaluate_cases(load_benchmark_cases(SAMPLE_DATASET))

        self.assertEqual(summary.total_cases, 6)
        self.assertEqual(summary.passed, 6)
        self.assertEqual(summary.failed, 0)
        self.assertEqual(summary.errored, 0)
        self.assertEqual(summary.skipped, 0)
        self.assertAlmostEqual(summary.accuracy, 1.0)

    def test_cli_writes_json_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = Path(temp_dir) / "report.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--dataset",
                    str(SAMPLE_DATASET),
                    "--report-json",
                    str(report_path),
                    "--fail-on-nonpassing",
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, msg=completed.stderr or completed.stdout)
            self.assertTrue(report_path.exists())

            payload = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["passed"], 6)
            self.assertEqual(payload["accuracy"], 1.0)


if __name__ == "__main__":
    unittest.main()