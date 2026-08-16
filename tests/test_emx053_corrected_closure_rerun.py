import json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'runs'/'emx053'
def j(n):return json.loads((P/n).read_text())
class T(unittest.TestCase):
 def test_ready_gate_reused_exactly(self):self.assertEqual(j('frozen_corrected_closure_rerun_contract.json')['validated_gates']['conservation_relative_drift_tolerance'],.003)
 def test_preserves_old_history(self):self.assertTrue(j('old_vs_corrected_comparison.json')['EMX051_preserved'])
 def test_shape_registry(self):self.assertEqual(len(j('corrected_rerun_results.json')['integrated_shape_cells']),12)
if __name__=='__main__':unittest.main()
