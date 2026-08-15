import json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'runs'/'emx038/frozen_repository_local_source_lift_contract.json'
class T(unittest.TestCase):
 def test_pre_result_finite_lift(self):
  x=json.loads(P.read_text());self.assertTrue(x['FROZEN_BEFORE_RESULTS']);self.assertEqual(x['selected_cell_count'],216);self.assertEqual(x['integrator']['steps'],180);self.assertEqual(x['observer_map']['retained_constraints']['count'],76)
if __name__=='__main__':unittest.main()
