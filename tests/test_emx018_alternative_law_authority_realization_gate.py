import hashlib
import json
import unittest
from pathlib import Path


RUN = Path(__file__).resolve().parents[1] / "runs" / "emx018"


def load(name):
    return json.loads((RUN / name).read_text())


class TestEMX018AlternativeLawAuthorityRealizationGate(unittest.TestCase):
    def test_contract_was_frozen_and_has_valid_digest(self):
        contract = load("frozen_alternative_law_realization_gate_contract.json")
        recorded = contract.pop("contract_sha256")
        actual = hashlib.sha256(json.dumps(contract, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.assertEqual(actual, recorded)
        self.assertEqual(contract["EMX018_SELECTOR_VERIFIED"], "ALTERNATIVE_LAW_AUTHORITY_AND_FROZEN_REALIZATION_GATE")

    def test_candidates_define_available_evidence_without_hidden_realizations(self):
        matrix = load("alternative_realization_authority_matrix.json")
        self.assertEqual(matrix["classification"], "NO_AUTHORIZED_COMPLETE_ALTERNATIVE_REALIZATION")
        self.assertEqual(len(matrix["candidates"]), 3)
        allowed = {"MISSING_COMPLETE_REALIZATION_SPECIFICATION", "INCOMPATIBLE_WITH_COMMON_OBSERVABLES_OR_CONTROLS"}
        for candidate in matrix["candidates"]:
            self.assertEqual(candidate["provenance"]["commit"], "7b41901fea16e0e6e8ca3a5949536658102ceeee")
            self.assertIn(candidate["verdict"], allowed)
            self.assertFalse(candidate["realization_authorized"])
            self.assertFalse(candidate["realization_possible_without_hidden_choices"])
            self.assertTrue(candidate["state"] and candidate["force_or_update"] and candidate["integrator"])

    def test_all_retained_constraints_remain_joint_requirements(self):
        translation = load("retained_constraint_translation_matrix.json")
        self.assertEqual(translation["retained_positive_constraint_count"], 76)
        self.assertEqual(len(translation["records"]), 76)
        self.assertIn("neither uninformative nor sufficient alone", translation["joint_compatibility_rule"])
        self.assertTrue(all(row["current_status"].startswith("NOT_DISCARDED") for row in translation["records"]))

    def test_no_execution_import_or_dev167_change_and_next_gate(self):
        matrix = load("alternative_realization_authority_matrix.json")
        final = load("final_contract.json")
        selector = load("emx019_test_selection.json")
        self.assertTrue(matrix["external_repository_read_only"])
        self.assertFalse(matrix["alternative_dynamics_executed"])
        self.assertTrue(final["NO_ALTERNATIVE_CODE_IMPORT"] and final["NO_DEV167_MODIFICATION"])
        self.assertEqual(selector["EMX019_TEST_SELECTION"], "EXPLICIT_ALTERNATIVE_MODEL_AUTHORITY_AND_FROZEN_INPUTS_GATE")


if __name__ == "__main__":
    unittest.main()
