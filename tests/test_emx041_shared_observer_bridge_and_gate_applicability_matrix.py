import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "runs" / "emx041"
def load(name): return json.loads((ROOT / name).read_text())

class TestEMX041(unittest.TestCase):
    def test_frozen_contract_and_all_gates_preserved(self):
        self.assertTrue(load("frozen_shared_observer_bridge_contract.json")["FROZEN_BEFORE_RESULTS"])
        matrix = load("gate_applicability_matrix.json")
        self.assertEqual(matrix["retained_gate_count"], 76)
        self.assertTrue(all(row["historical_gate_preserved"] for row in matrix["records"]))
    def test_all_eligible_stress_cells_and_only_declared_outcomes(self):
        stress = load("cross_calibration_stress_matrix.json")
        self.assertEqual(stress["eligible_cell_count"], 7776)
        self.assertTrue(set(stress["outcome_counts"]).issubset({"AGREES", "DIFFERS", "INCOMPARABLE"}))
    def test_no_new_dynamics_or_gate_weakening(self):
        final = load("final_contract.json")
        self.assertFalse(final["NEW_DYNAMICS_EXECUTED"])
        self.assertFalse(final["HISTORICAL_GATES_CHANGED"] or final["HISTORICAL_GATES_WEAKENED"])

if __name__ == "__main__": unittest.main()
