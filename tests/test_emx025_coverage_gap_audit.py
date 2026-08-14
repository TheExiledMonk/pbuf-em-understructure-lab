import hashlib,json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'runs'/'emx025'
def j(x):return json.loads((R/x).read_text())
class T(unittest.TestCase):
 def test_contract(self):
  x=j('frozen_coverage_gap_audit_contract.json');h=x.pop('contract_sha256');self.assertEqual(h,hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest());self.assertTrue(x['prohibitions']['NO_COMPOSITE_LAW_EXECUTION'])
 def test_all_coverage(self):
  x=j('coverage_matrix.json');self.assertEqual(len(x['records']),76);self.assertIn('EMX024_INTERNAL_ORIENTATION',x['summary']['model_counts'])
 def test_followup_ranking(self):
  x=j('coverage_matrix.json')['follow_up_ranked_by_declared_information_value'];self.assertEqual(x[0]['rank'],1);self.assertFalse(x[0]['execution_authorized_by_emx025'])
 def test_handoff(self):self.assertIn('No new dynamics', (R/'coverage_handoff.md').read_text())
if __name__=='__main__':unittest.main()
