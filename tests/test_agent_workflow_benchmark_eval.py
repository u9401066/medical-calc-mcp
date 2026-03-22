# ruff: noqa: I001

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.shared.agent_benchmarking import load_agent_scenarios_from_paths
from src.shared.agent_benchmark_evaluator import (
    evaluate_agent_runs,
    load_agent_runs,
    load_scoring_rubric,
)
from src.shared.agent_benchmark_profiles import load_benchmark_profile_manifest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCENARIO_DIR = PROJECT_ROOT / "data" / "agent_decision_bench" / "scenarios"
RUBRIC_PATH = PROJECT_ROOT / "data" / "agent_decision_bench" / "rubrics" / "default_scoring.json"
RUNS_PATH = PROJECT_ROOT / "data" / "agent_decision_bench" / "sample_runs" / "mixed_agent_runs.jsonl"
TRACE_EVENTS_PATH = PROJECT_ROOT / "data" / "agent_decision_bench" / "sample_runs" / "mcp_session_events.jsonl"
TRANSCRIPT_TRACE_PATH = PROJECT_ROOT / "data" / "agent_decision_bench" / "sample_runs" / "mcp_session_transcript.jsonl"
PROFILE_MANIFEST_PATH = PROJECT_ROOT / "data" / "agent_decision_bench" / "profiles" / "manifest.json"
TRACE_ADAPTER_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "benchmark_adapt_mcp_trace.py"
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "benchmark_eval_agent_runs.py"
PROFILE_RUNNER_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "benchmark_run_profile.py"
REPORT_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "benchmark_build_reports.py"
SCENARIO_PATHS: tuple[str | Path, ...] = (
    SCENARIO_DIR / "sepsis_icu.jsonl",
    SCENARIO_DIR / "preop_risk.jsonl",
    SCENARIO_DIR / "aki_eval.jsonl",
    SCENARIO_DIR / "gi_bleed.jsonl",
    SCENARIO_DIR / "icu_sedation_delirium.jsonl",
)


class AgentWorkflowBenchmarkEvalTests(unittest.TestCase):
    def test_load_workflow_scenarios(self) -> None:
        scenarios = load_agent_scenarios_from_paths(SCENARIO_PATHS)

        self.assertEqual(len(scenarios), 5)
        self.assertEqual(
            {scenario.track_id for scenario in scenarios},
            {"sepsis", "preop", "aki", "gi_bleed", "icu_sedation_delirium"},
        )

    def test_evaluate_mixed_runs(self) -> None:
        scenarios = load_agent_scenarios_from_paths(SCENARIO_PATHS)
        runs = load_agent_runs(RUNS_PATH)
        rubric = load_scoring_rubric(RUBRIC_PATH)

        summary = evaluate_agent_runs(scenarios, runs, rubric=rubric)
        results = {result.scenario_id: result for result in summary.scenario_results}

        self.assertEqual(summary.total_scenarios, 5)
        self.assertEqual(summary.total_runs, 5)
        self.assertAlmostEqual(summary.task_completion_rate, 0.8)

        self.assertTrue(results["workflow_sepsis_001"].task_completed)
        self.assertEqual(results["workflow_sepsis_001"].step_sequence_validity, 1.0)
        self.assertEqual(results["workflow_sepsis_001"].missing_data_question_quality, 1.0)

        self.assertFalse(results["workflow_gi_bleed_001"].task_completed)
        self.assertEqual(results["workflow_gi_bleed_001"].tool_selection_precision_at_1, 0.0)
        self.assertGreater(results["workflow_gi_bleed_001"].overreach_penalty_rate, 0.0)
        self.assertTrue(results["workflow_icu_sedation_001"].task_completed)

    def test_trace_adapter_cli_outputs_runs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "adapted_runs.jsonl"
            summary_path = Path(temp_dir) / "trace_summary.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(TRACE_ADAPTER_SCRIPT_PATH),
                    "--trace-log",
                    str(TRACE_EVENTS_PATH),
                    "--scenarios",
                    *(str(path) for path in SCENARIO_PATHS),
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
            payload = json.loads(summary_path.read_text(encoding="utf-8"))
            adapted_runs = output_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(payload["total_sessions"], 5)
            self.assertEqual(len(adapted_runs), 5)

    def test_trace_adapter_accepts_mcp_transcript(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "transcript_adapted_runs.jsonl"
            summary_path = Path(temp_dir) / "transcript_trace_summary.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(TRACE_ADAPTER_SCRIPT_PATH),
                    "--trace-log",
                    str(TRANSCRIPT_TRACE_PATH),
                    "--trace-format",
                    "mcp_transcript",
                    "--scenarios",
                    *(str(path) for path in SCENARIO_PATHS),
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
            payload = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["total_sessions"], 5)
            self.assertEqual(len(output_path.read_text(encoding="utf-8").splitlines()), 5)

    def test_evaluate_trace_adapted_runs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "adapted_runs.jsonl"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(TRACE_ADAPTER_SCRIPT_PATH),
                    "--trace-log",
                    str(TRACE_EVENTS_PATH),
                    "--scenarios",
                    *(str(path) for path in SCENARIO_PATHS),
                    "--output",
                    str(output_path),
                    "--fail-on-skipped",
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, msg=completed.stderr or completed.stdout)
            scenarios = load_agent_scenarios_from_paths(SCENARIO_PATHS)
            runs = load_agent_runs(output_path)
            rubric = load_scoring_rubric(RUBRIC_PATH)
            summary = evaluate_agent_runs(scenarios, runs, rubric=rubric)

            self.assertEqual(summary.total_scenarios, 5)
            self.assertEqual(summary.total_runs, 5)
            self.assertAlmostEqual(summary.task_completion_rate, 0.8)

    def test_cli_writes_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            summary_path = Path(temp_dir) / "workflow_eval_summary.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--scenarios",
                    *(str(path) for path in SCENARIO_PATHS),
                    "--runs",
                    str(RUNS_PATH),
                    "--rubric",
                    str(RUBRIC_PATH),
                    "--summary-json",
                    str(summary_path),
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, msg=completed.stderr or completed.stdout)
            self.assertTrue(summary_path.exists())

            payload = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["total_scenarios"], 5)
            self.assertAlmostEqual(payload["task_completion_rate"], 0.8)

    def test_profile_manifest_and_reporting_pipeline(self) -> None:
        manifest = load_benchmark_profile_manifest(PROFILE_MANIFEST_PATH)
        self.assertEqual(len(manifest.profiles), 3)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir)
            direct_output = output_root / "direct"
            transcript_output = output_root / "transcript"
            leaderboard_path = output_root / "leaderboard.md"
            time_series_path = output_root / "time-series.json"
            report_index_path = output_root / "report-index.json"

            for profile_id, output_dir in (("sample_full_policy", direct_output), ("sample_transcript_trace", transcript_output)):
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(PROFILE_RUNNER_SCRIPT_PATH),
                        "--manifest",
                        str(PROFILE_MANIFEST_PATH),
                        "--profile-id",
                        profile_id,
                        "--output-dir",
                        str(output_dir),
                    ],
                    cwd=PROJECT_ROOT,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(completed.returncode, 0, msg=completed.stderr or completed.stdout)

            completed = subprocess.run(
                [
                    sys.executable,
                    str(REPORT_SCRIPT_PATH),
                    "--inputs",
                    str(direct_output),
                    str(transcript_output),
                    "--leaderboard-md",
                    str(leaderboard_path),
                    "--time-series-json",
                    str(time_series_path),
                    "--report-index-json",
                    str(report_index_path),
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, msg=completed.stderr or completed.stdout)
            leaderboard_text = leaderboard_path.read_text(encoding="utf-8")
            time_series_payload = json.loads(time_series_path.read_text(encoding="utf-8"))
            report_index_payload = json.loads(report_index_path.read_text(encoding="utf-8"))

            self.assertIn("sample_full_policy", leaderboard_text)
            self.assertIn("sample_transcript_trace", leaderboard_text)
            self.assertEqual(len(time_series_payload["points"]), 2)
            self.assertEqual(len(report_index_payload["leaderboard"]), 2)


if __name__ == "__main__":
    unittest.main()
