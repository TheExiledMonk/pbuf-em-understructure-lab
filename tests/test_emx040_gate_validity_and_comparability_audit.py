import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name):
    return json.loads((ROOT / "runs" / "emx040" / name).read_text())


class TestEMX040(unittest.TestCase):
    def test_contract_and_full_ledger_are_frozen_and_complete(self):
        contract = load("frozen_gate_validity_and_comparability_contract.json")
        ledger = load("gate_ledger.json")
        self.assertTrue(contract["FROZEN_BEFORE_RESULTS"])
        self.assertEqual(ledger["retained_constraint_count"], 76)
        self.assertEqual(len(ledger["records"]), 76)

    def test_only_authorized_classifications_and_no_reproduction_conflict(self):
        contract = load("frozen_gate_validity_and_comparability_contract.json")
        ledger = load("gate_ledger.json")
        self.assertTrue(all(row["classification"] in contract["classification_vocabulary"] for row in ledger["records"]))
        self.assertFalse(any(row["classification"] == "REPRODUCTION_CONTRADICTED" for row in ledger["records"]))

    def test_shared_observer_boundary_is_explicit(self):
        plan = load("shared_observer_comparability_plan.json")
        final = load("final_contract.json")
        self.assertEqual(plan["status"], "UNDERDETERMINED_NEEDS_BRIDGE")
        self.assertTrue(final["STOPPED_AT_GENUINELY_NEW_OBSERVER_PRIMITIVE_BOUNDARY"])
        self.assertFalse(final["RETAINED_GATES_ALTERED_WEAKENED_OR_DELETED"])


if __name__ == "__main__":
    unittest.main()
