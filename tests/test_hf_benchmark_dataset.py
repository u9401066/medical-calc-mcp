# ruff: noqa: I001

import json
import unittest
from pathlib import Path

from src.shared.hf_benchmark_dataset import count_benchmark_cases, load_hf_benchmark_cases


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = PROJECT_ROOT / "data" / "benchmarks" / "medical_calc_mcp_hf_v1"
ALL_CASES_PATH = DATASET_DIR / "all.jsonl"
METADATA_PATH = DATASET_DIR / "metadata.json"
PUBLIC_DEV_DIR = DATASET_DIR / "release" / "public-dev"
HIDDEN_TEST_DIR = DATASET_DIR / "release" / "hidden-test"
RELEASE_MANIFEST_PATH = DATASET_DIR / "release_manifest.json"


class HfBenchmarkDatasetTests(unittest.TestCase):
    def test_dataset_has_at_least_500_cases(self) -> None:
        self.assertTrue(ALL_CASES_PATH.exists())
        self.assertGreaterEqual(count_benchmark_cases(ALL_CASES_PATH), 500)

    def test_dataset_covers_all_guideline_domains(self) -> None:
        cases = load_hf_benchmark_cases(ALL_CASES_PATH)
        covered = {domain for case in cases for domain in case.guideline_domains}
        self.assertEqual(
            covered,
            {
                "Anesthesiology",
                "Burns",
                "Cardiovascular",
                "GI Bleeding",
                "Kidney Disease",
                "Liver Disease",
                "Neurology",
                "Nutrition",
                "Oncology",
                "Osteoporosis",
                "Pediatrics",
                "Respiratory / Pneumonia",
                "Rheumatology",
                "Sepsis / Critical Care",
                "Thromboembolism",
                "Trauma",
            },
        )

    def test_metadata_matches_case_count(self) -> None:
        payload = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(payload["total_cases"], count_benchmark_cases(ALL_CASES_PATH))
        self.assertGreaterEqual(payload["unique_tools"], 65)

    def test_release_bundle_exists_and_counts_match(self) -> None:
        public_train = PUBLIC_DEV_DIR / "train.jsonl"
        public_validation = PUBLIC_DEV_DIR / "validation.jsonl"
        public_dev = PUBLIC_DEV_DIR / "public-dev.jsonl"
        hidden_test = HIDDEN_TEST_DIR / "hidden-test.jsonl"

        self.assertTrue(public_train.exists())
        self.assertTrue(public_validation.exists())
        self.assertTrue(public_dev.exists())
        self.assertTrue(hidden_test.exists())

        public_cases = load_hf_benchmark_cases([public_train, public_validation])
        combined_public_cases = load_hf_benchmark_cases(public_dev)
        hidden_cases = load_hf_benchmark_cases(hidden_test)

        self.assertEqual(len(public_cases), len(combined_public_cases))
        self.assertTrue(all(case.split in {"train", "validation"} for case in public_cases))
        self.assertTrue(all(case.split == "hidden_test" for case in hidden_cases))
        self.assertEqual(len(public_cases) + len(hidden_cases), count_benchmark_cases(ALL_CASES_PATH))

    def test_release_manifest_matches_metadata(self) -> None:
        metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
        manifest = json.loads(RELEASE_MANIFEST_PATH.read_text(encoding="utf-8"))

        self.assertEqual(
            manifest["public_release"]["splits"]["public_dev"],
            metadata["release_packaging"]["public_dev_total"],
        )
        self.assertEqual(
            manifest["private_release"]["splits"]["hidden_test"],
            metadata["release_packaging"]["hidden_test_total"],
        )
