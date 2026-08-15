import json
import unittest
from pathlib import Path

RUN = Path(__file__).resolve().parents[1] / "runs" / "emx037"

class TestEmx037Freeze(unittest.TestCase):
    def test_contract_is_finite_and_pre_result(self):
        contract = json.loads((RUN / "frozen_zero_motion_control_contract.json").read_text())
        self.assertTrue(contract["FROZEN_BEFORE_RESULTS"])
        self.assertEqual(len(contract["selected_cells"]), 8)
        self.assertEqual(contract["retained_constraint_count"], 76)
        self.assertEqual(contract["update"]["steps"], 180)

    def test_executed_zero_controls_are_exact(self):
        results = json.loads((RUN / "batch_results.json").read_text())["results"]
        self.assertEqual(len(results), 8)
        for result in results:
            self.assertEqual(result["max_abs_u"], 0.0)
            self.assertEqual(result["max_abs_p"], 0.0)
            self.assertEqual(result["source_persistence"], "COMPATIBLE_NONUNIQUE")

if __name__ == "__main__":
    unittest.main()
