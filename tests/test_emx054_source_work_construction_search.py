import json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'runs'/'emx054'
def j(n):return json.loads((P/n).read_text())
class T(unittest.TestCase):
 def test_three_hypotheses_frozen(self):self.assertEqual(len(j('frozen_source_work_construction_contract.json')['candidates']),3)
 def test_no_validation_claim(self):self.assertTrue(j('provenance_assumption_statement.json')['pass_is_not_physical_validation'])
 def test_controls_exist(self):self.assertGreater(len(j('control_results_registry.json')['controls']),20)
if __name__=='__main__':unittest.main()
