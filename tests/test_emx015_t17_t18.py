import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs" / "emx015"


def load(name):
    return json.loads((RUN / name).read_text())


class TestEMX015(unittest.TestCase):
    def setUp(self):
        self.final = load("final_contract.json")

    def test_contract_is_frozen_and_digest_valid(self):
        contract = load("frozen_t17_t18_execution_contract.json")
        recorded = contract.pop("contract_sha256")
        actual = hashlib.sha256(json.dumps(contract, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.assertEqual(actual, recorded)

    def test_only_authorized_t17_t18_are_executed(self):
        self.assertTrue(self.final["T17_EXECUTED"] and self.final["T18_EXECUTED"])
        self.assertTrue(self.final["NO_NEW_DYNAMICS"] and self.final["NO_NEW_PHYSICS"] and self.final["NO_NEW_LOADING"])

    def test_t17_uses_all_history_fixed_geometry_and_matched_control(self):
        result = load("t17_loaded_geometry_tracking.json")
        self.assertIn(result["classification"], {"LOADED_RESPONSE_GEOMETRY_DISTANCE_REDUCED", "LOADED_RESPONSE_GEOMETRY_DISTANCE_INCREASED", "LOADED_RESPONSE_GEOMETRY_DISTANCE_EQUAL"})
        self.assertEqual(len(result["geometry_centroid_by_time"]), 181)
        self.assertEqual(len(result["loaded_response_centroid_by_time"]), 181)
        self.assertEqual(len(result["unloaded_response_centroid_by_time"]), 181)

    def test_t18_uses_fixed_native_orientation_and_controls(self):
        result = load("t18_orientation_decoupling.json")
        self.assertIn(result["classification"], {"ORIENTATION_REPRESENTATION_NONREDUCIBLE_TO_STRAIN", "ORIENTATION_REPRESENTATION_SCALAR_REDUCIBLE_TO_STRAIN"})
        self.assertEqual(set(result["controls"]), {"identity", "transverse_swap", "e2_reflection"})
        identity = result["controls"]["identity"]
        for control in result["controls"].values():
            self.assertEqual(control["joint_rank"], identity["joint_rank"])
            self.assertAlmostEqual(control["strain_l2"], identity["strain_l2"])
            self.assertAlmostEqual(control["orientation_l2"], identity["orientation_l2"])
        self.assertTrue(self.final["T18_REPRESENTATION_SENSITIVITY_REPORTED"])

    def test_emx016_is_frozen_but_not_executed(self):
        contract = json.loads((ROOT / "runs" / "emx016" / "frozen_dev167_robustness_reconsideration_contract.json").read_text())
        self.assertEqual(contract["execution_status"], "FROZEN_NOT_EXECUTED")
        self.assertTrue(contract["prohibitions"]["NO_DEV167_VARIANT_EXECUTION"])


if __name__ == "__main__":
    unittest.main()
