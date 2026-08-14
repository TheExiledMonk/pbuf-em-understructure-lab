import hashlib
import json
import unittest
from pathlib import Path

RUN = Path(__file__).resolve().parents[1] / "runs" / "emx017"


def load(name):
    return json.loads((RUN / name).read_text())


class TestEMX017CompatibilityGate(unittest.TestCase):
    def test_contract_digest_is_valid(self):
        contract = load("frozen_alternative_law_compatibility_authority_contract.json")
        recorded = contract.pop("contract_sha256")
        actual = hashlib.sha256(json.dumps(contract, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.assertEqual(actual, recorded)

    def test_every_candidate_has_read_only_provenance_and_verdict(self):
        gate = load("alternative_law_compatibility_gate.json")
        self.assertEqual(len(gate["candidates"]), 3)
        for candidate in gate["candidates"]:
            self.assertEqual(candidate["provenance"]["commit"], "7b41901fea16e0e6e8ca3a5949536658102ceeee")
            self.assertIn(candidate["verdict"], {"MISSING_EXECUTABLE_DEFINITION_OR_AUTHORITY", "INCOMPATIBLE_STATE_FORCE_OR_INTEGRATOR", "STRUCTURAL_COMPARISON_ONLY"})

    def test_nonunique_positive_constraints_remain_retained(self):
        gate = load("alternative_law_compatibility_gate.json")
        retained = gate["retained_positive_constraints"]
        self.assertEqual(retained["count"], 76)
        self.assertIn("non-uniqueness", retained["joint_compatibility_use"])

    def test_no_import_or_execution_and_next_is_authority_gate(self):
        final = load("final_contract.json")
        selector = load("emx018_test_selection.json")
        self.assertTrue(final["NO_ALTERNATIVE_CODE_IMPORT"] and final["NO_ALTERNATIVE_DYNAMICS_EXECUTION"])
        self.assertEqual(selector["EMX018_TEST_SELECTION"], "ALTERNATIVE_LAW_AUTHORITY_AND_FROZEN_REALIZATION_GATE")


if __name__ == "__main__":
    unittest.main()
