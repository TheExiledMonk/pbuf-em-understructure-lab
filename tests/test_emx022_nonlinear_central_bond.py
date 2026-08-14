import hashlib,json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'runs'/'emx022'
def j(n):return json.loads((R/n).read_text())
class T(unittest.TestCase):
 def test_contract(self):
  x=j('frozen_nonlinear_central_bond_contract.json');h=x.pop('contract_sha256');self.assertEqual(h,hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest());self.assertEqual(x['law']['coefficients']['quartic_bond'],1.0)
 def test_execution(self):
  x=j('execution_results.json');self.assertTrue(x['all_finite']);self.assertEqual(set(x['symmetry']),{'identity','y_z_swap','e2_reflection'})
 def test_retained(self):
  x=j('retained_constraint_classification.json');self.assertEqual(x['count'],76);self.assertEqual(len(x['records']),76);self.assertTrue(all(a['nonunique']=='RETAINED_JOINT_CONSTRAINT' for a in x['records']))
 def test_next(self):self.assertEqual(j('emx023_test_selection.json')['EMX023_TEST_SELECTION'],'LOCAL_BOND_ANGLE_BENDING_ELASTICITY_EXECUTION')
if __name__=='__main__':unittest.main()
