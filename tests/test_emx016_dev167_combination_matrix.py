import hashlib
import json
import unittest
from pathlib import Path

RUN = Path(__file__).resolve().parents[1] / "runs" / "emx016"


def load(name):
    return json.loads((RUN / name).read_text())


class TestEMX016CombinationMatrix(unittest.TestCase):
    def test_contract_digest_is_valid(self):
        contract = load("frozen_dev167_failure_combination_matrix_contract.json")
        recorded = contract.pop("contract_sha256")
        actual = hashlib.sha256(json.dumps(contract, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.assertEqual(actual, recorded)

    def test_all_required_categories_are_distinguished(self):
        matrix = load("dev167_failure_combination_matrix.json")
        categories = set(matrix["category_counts"])
        self.assertTrue({"REJECTED_UNDER_DEV167", "UNTESTED_EXISTING_VALIDATED_PIECES", "UNAVAILABLE_BLOCKED_DATA"} <= categories)
        self.assertEqual(matrix["classification"], "DEV167_FAILURE_COMBINATION_MATRIX_COMPLETE")

    def test_positive_constraints_are_retained_even_when_nonunique(self):
        matrix = load("dev167_failure_combination_matrix.json")
        positives = matrix["retained_positive_constraints"]
        self.assertGreater(positives["count"], 0)
        self.assertIn("not unique", positives["rule"].lower())
        self.assertTrue(any(row["interpretation"] == "NOT_UNIQUE_ALONE_RETAINED_CONSTRAINT" for row in positives["records"]))

    def test_external_alternatives_are_read_only_and_not_executed(self):
        final = load("final_contract.json")
        matrix = load("dev167_failure_combination_matrix.json")
        self.assertTrue(final["NO_ALTERNATIVE_LAW_EXECUTION"])
        self.assertEqual(sum(row["kind"] == "GENUINELY_ALTERNATIVE_LAW_MECHANICS" for row in matrix["alternative_mechanics_read_only"]), 3)

    def test_next_selector_is_an_authority_gate(self):
        readiness = load("readiness_update.json")
        self.assertEqual(readiness["EMX017_TEST_SELECTION"], "ALTERNATIVE_LAW_COMPATIBILITY_AUTHORITY_GATE")
        self.assertFalse(readiness["independent_alternative_executable"])


if __name__ == "__main__":
    unittest.main()
