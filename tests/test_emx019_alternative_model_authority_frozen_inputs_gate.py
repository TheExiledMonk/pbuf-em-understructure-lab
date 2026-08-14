import hashlib
import json
import unittest
from pathlib import Path


RUN = Path(__file__).resolve().parents[1] / "runs" / "emx019"


def load(name):
    return json.loads((RUN / name).read_text())


class TestEMX019AlternativeModelAuthorityFrozenInputsGate(unittest.TestCase):
    def test_contract_digest_and_complete_preexecution_law(self):
        contract = load("frozen_alternative_model_authority_and_inputs_contract.json")
        recorded = contract.pop("contract_sha256")
        actual = hashlib.sha256(json.dumps(contract, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.assertEqual(actual, recorded)
        law = contract["normalization_and_law"]
        self.assertEqual((law["mass_per_site"], law["nearest_neighbor_spring_coefficient"], law["onsite_coefficient"]), (1.0, 1.0, 0.0))
        self.assertEqual((law["source_term"], law["noise_term"], law["damping_term"]), ("0 at every site and every time",) * 3)

    def test_inputs_integrator_and_native_state_bridge_are_fixed(self):
        contract = load("frozen_alternative_model_authority_and_inputs_contract.json")
        self.assertEqual(contract["state"]["shape"], [11, 11, 11, 3])
        self.assertEqual(contract["integrator"]["dt"], 0.04)
        self.assertEqual(contract["frozen_inputs"]["loaded_background"]["sha256"], "118a680de0ba756cd56901fcf2db02cd2a765035357e7b38fb419927ae61afb4")
        self.assertIn("background_trajectory.displacement[0]+packet_u", contract["frozen_inputs"]["initialization"]["unloaded"])
        self.assertIn("force, kick, then drift", contract["integrator"]["ordering"])

    def test_every_retained_constraint_has_a_predeclared_control_map(self):
        mapped = load("retained_constraint_observable_control_map.json")
        self.assertEqual(mapped["count"], 76)
        self.assertEqual(len(mapped["records"]), 76)
        self.assertTrue(all(row["future_execution_status"] == "NOT_EVALUATED_IN_EMX019" for row in mapped["records"]))
        self.assertTrue(all(row["nonunique_status"] == "RETAINED_AS_JOINT_CONSTRAINT_NOT_A_STANDALONE_SELECTOR" for row in mapped["records"]))

    def test_no_execution_or_dev167_change_and_next_selector_requires_authorization(self):
        readiness = load("alternative_realization_readiness.json")
        final = load("final_contract.json")
        selector = load("emx020_test_selection.json")
        self.assertEqual(readiness["execution_status"], "NOT_EXECUTED")
        self.assertTrue(final["NO_ALTERNATIVE_DYNAMICS_EXECUTION"] and final["NO_DEV167_MODIFICATION"])
        self.assertEqual(selector["EMX020_TEST_SELECTION"], "FROZEN_ELASTIC_N6_ALTERNATIVE_COMPARISON_EXECUTION")
        self.assertEqual(selector["authorization_required"], "explicit user authorization before execution")


if __name__ == "__main__":
    unittest.main()
