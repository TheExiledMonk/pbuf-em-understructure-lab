import hashlib
import json
import unittest
from pathlib import Path


RUN = Path(__file__).resolve().parents[1] / "runs" / "emx021"


def load(name):
    return json.loads((RUN / name).read_text())


class TestEMX021AlternativeLawRetainedConstraintMatrix(unittest.TestCase):
    def test_contract_digest_and_read_only_mode(self):
        contract = load("frozen_retained_constraint_compatibility_contract.json")
        recorded = contract.pop("contract_sha256")
        self.assertEqual(recorded, hashlib.sha256(json.dumps(contract, sort_keys=True, separators=(",", ":")).encode()).hexdigest())
        self.assertTrue(contract["prohibitions"]["NO_NEW_DYNAMICS"])

    def test_every_retained_constraint_is_preserved_and_classified(self):
        matrix = load("alternative_retained_constraint_compatibility_matrix.json")
        self.assertEqual(len(matrix["records"]), 76)
        allowed = {"COMPATIBLE_NONUNIQUE", "CONTRADICTED_BY_FROZEN_ALTERNATIVE", "NOT_ASSESSED_BY_THIS_FROZEN_BATTERY"}
        self.assertTrue(all(row["alternative_status"] in allowed for row in matrix["records"]))
        self.assertTrue(all(row["nonunique_status"] == "RETAINED_JOINT_CONSTRAINT" for row in matrix["records"]))

    def test_exact_harmonic_law_is_rejected_without_overgeneralizing(self):
        matrix = load("alternative_retained_constraint_compatibility_matrix.json")
        summary = matrix["summary"]
        self.assertEqual(summary["joint_result"], "FROZEN_UNIT_HARMONIC_ALTERNATIVE_INCOMPATIBLE_WITH_RETAINED_COMBINATION")
        self.assertGreater(summary["counts"]["CONTRADICTED_BY_FROZEN_ALTERNATIVE"], 0)
        self.assertIn("not elasticity in general", summary["limits"])

    def test_next_step_requires_new_primitive_authority(self):
        final = load("final_contract.json")
        selector = load("next_selector.json")
        self.assertTrue(final["NEW_PRIMITIVE_AUTHORITY_REQUIRED"])
        self.assertEqual(selector["NEXT_SELECTOR"], "NEW_PRIMITIVE_AUTHORITY_REQUIRED")
        self.assertFalse(selector["automatic_execution_permitted"])


if __name__ == "__main__":
    unittest.main()
