import hashlib,json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'runs'/'emx023'
def j(x):return json.loads((R/x).read_text())
class T(unittest.TestCase):
 def test_contract(self):
  x=j('frozen_bond_angle_bending_contract.json');q=x.pop('contract_sha256');self.assertEqual(q,hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest())
 def test_results(self):self.assertTrue(j('execution_results.json')['all_finite'])
 def test_retained(self):self.assertEqual(len(j('retained_constraint_classification.json')['records']),76)
 def test_next(self):self.assertEqual(j('emx024_test_selection.json')['EMX024_TEST_SELECTION'],'INTERNAL_ORIENTATION_STATE_EXECUTION')
if __name__=='__main__':unittest.main()
