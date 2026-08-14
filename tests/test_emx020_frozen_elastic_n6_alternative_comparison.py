import hashlib
import json
import unittest
from pathlib import Path


RUN = Path(__file__).resolve().parents[1] / "runs" / "emx020"


def load(name):
    return json.loads((RUN / name).read_text())


class TestEMX020FrozenElasticN6AlternativeComparison(unittest.TestCase):
    def test_execution_contract_digest_and_no_hidden_choices(self):
        contract = load("frozen_elastic_n6_comparison_execution_contract.json")
        recorded = contract.pop("contract_sha256")
        self.assertEqual(recorded, hashlib.sha256(json.dumps(contract, sort_keys=True, separators=(",", ":")).encode()).hexdigest())
        self.assertTrue(contract["prohibitions"]["NO_HIDDEN_PARAMETERS"])

    def test_frozen_inputs_and_new_alternative_histories_are_verified(self):
        verified = load("frozen_input_and_trajectory_verification.json")
        self.assertTrue(verified["all_finite"] and verified["new_dynamics_executed"])
        self.assertFalse(verified["DEV167_modified"])
        self.assertEqual(verified["input_hashes"]["packet_u"], "78c823853e12acd4d42cdd93e42acb741539082e617106c46d7de54188381843")

    def test_fixed_symmetry_controls_are_exact(self):
        controls = load("fixed_symmetry_control.json")["controls"]
        self.assertEqual(set(controls), {"identity", "transverse_swap", "e2_reflection"})
        self.assertTrue(all(value["exact_at_tolerance"] for value in controls.values()))

    def test_retained_constraints_continue_to_next_joint_matrix(self):
        final = load("final_contract.json")
        selector = load("emx021_test_selection.json")
        self.assertTrue(final["RETAINED_POSITIVE_CONSTRAINTS_PRESERVED"])
        self.assertEqual(selector["EMX021_TEST_SELECTION"], "ALTERNATIVE_LAW_RETAINED_CONSTRAINT_COMPATIBILITY_MATRIX")


if __name__ == "__main__":
    unittest.main()
