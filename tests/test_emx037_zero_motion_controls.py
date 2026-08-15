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

if __name__ == "__main__":
    unittest.main()
