import json
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "emx048"


def load(name):
    return json.loads((P / name).read_text())


class EMX048Test(unittest.TestCase):
    def test_frozen_corpus_is_history_pinned(self):
        c = load("frozen_reference_geometry_recovery_contract.json")
        self.assertTrue(c["FROZEN_BEFORE_RESULTS"])
        self.assertGreater(c["allowed_corpus"]["commit_count"], 0)
        self.assertEqual(len(c["contract_sha256"]), 64)

    def test_candidates_are_audited_and_fail_closed(self):
        rows = load("candidate_artifact_ledger.json")["records"]
        self.assertGreater(len(rows), 0)
        self.assertTrue(all("sha256" in row and "classification" in row for row in rows))
        self.assertTrue(all(row["classification"] == "INCOMPLETE_PROVENANCE" for row in rows))

    def test_missing_geometry_and_source_are_explicit(self):
        missing = {x["field"]: x for x in load("missing_field_ledger.json")["required_fields"]}
        self.assertEqual(missing["directed_reference_geometry"]["classification"], "NOT_PRESENT_IN_ALLOWED_CORPUS")
        self.assertEqual(missing["source_history_mapping"]["classification"], "NOT_PRESENT_IN_ALLOWED_CORPUS")


if __name__ == "__main__":
    unittest.main()
