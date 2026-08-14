import json
import unittest
from pathlib import Path

R = Path(__file__).resolve().parents[1] / "runs" / "emx013"


def load(name):
    return json.loads((R / name).read_text())


class TestEMX013(unittest.TestCase):
    def setUp(self):
        self.final = load("final_contract.json")

    def test_selector_and_contract_are_frozen(self):
        self.assertEqual(self.final["EMX013_SELECTOR_VERIFIED"], "UNLOADED_TRANSVERSE_ASYMMETRY_DEEP_AUDIT")
        self.assertIn("contract_sha256", load("frozen_unloaded_asymmetry_audit_contract.json"))

    def test_authorized_unloaded_trajectory_is_reused(self):
        reuse = load("trajectory_reuse.json")
        self.assertTrue(reuse["EMX011_UNLOADED_TRAJECTORY_REUSED"])
        self.assertFalse(reuse["NEW_DYNAMICS_EXECUTED"])
        self.assertEqual(reuse["unloaded_probe_hash"], reuse["authorized_trajectory_hash"])

    def test_preexisting_asymmetry_is_nonzero(self):
        t29 = load("t29_fixed_frame_asymmetry.json")
        self.assertEqual(t29["classification"], "PREEXISTING_UNLOADED_ASYMMETRY")
        self.assertGreater(t29["full_history_difference_l2"], 1e-12)

    def test_fixed_symmetry_magnitude_is_invariant(self):
        self.assertEqual(load("t30_fixed_symmetry_controls.json")["classification"], "FIXED_SYMMETRY_MAGNITUDE_INVARIANT")

    def test_components_remain_independent(self):
        t31 = load("t31_component_state_independence.json")
        self.assertEqual(t31["classification"], "TRANSVERSE_SECTORS_INDEPENDENT")
        self.assertFalse(t31["exact_linear_dependence"])

    def test_full_window_support_uses_no_front_threshold(self):
        self.assertEqual(load("t32_fixed_window_support.json")["classification"], "FULL_WINDOW_NONLOCAL_SUPPORT")

    def test_full_state_remains_parent_representation(self):
        t33 = load("t33_representation_retention.json")
        self.assertEqual(t33["parent_state_priority"], "FULL_STATE")
        self.assertEqual(t33["classification"], "FULL_STATE_PRESERVED_WITH_REDUCTION_SENSITIVITY")

    def test_t17_t18_remain_unexecuted(self):
        self.assertFalse(self.final["T17_EXECUTED"] or self.final["T18_EXECUTED"])

    def test_terminal_selector_is_frozen(self):
        selection = load("emx014_test_selection.json")
        self.assertEqual(selection["EMX014_TEST_SELECTION"], "EVIDENCE_CLOSURE_NO_FURTHER_EXECUTION")
        self.assertTrue(selection["EMX014_TEST_SELECTION_FROZEN"])

    def test_prohibitions_are_preserved(self):
        self.assertTrue(self.final["NO_DEV167_MODIFICATION"])
        self.assertTrue(self.final["NO_QED_MAPPING"])
        self.assertTrue(self.final["NO_T17_EXECUTION"])
        self.assertTrue(self.final["NO_T18_EXECUTION"])


if __name__ == "__main__":
    unittest.main()
