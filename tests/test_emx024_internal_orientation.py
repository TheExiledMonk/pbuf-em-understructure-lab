import hashlib,json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'runs'/'emx024'
def j(x):return json.loads((R/x).read_text())
class T(unittest.TestCase):
 def test_contract(self):
  x=j('frozen_internal_orientation_contract.json');q=x.pop('contract_sha256');self.assertEqual(q,hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest());self.assertEqual(x['law']['coefficients']['coupling'],.25)
 def test_results(self):self.assertTrue(j('execution_results.json')['all_finite'])
 def test_retained(self):self.assertEqual(len(j('retained_constraint_classification.json')['records']),76)
 def test_next(self):self.assertEqual(j('next_selector.json')['NEXT_SELECTOR'],'CROSS_FAMILY_JOINT_COMPATIBILITY_CLOSURE')
if __name__=='__main__':unittest.main()
