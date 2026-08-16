import json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'runs'/'emx050'
def j(n):return json.loads((P/n).read_text())
class T(unittest.TestCase):
 def test_external_is_statement_only(self):self.assertIn('documents were not opened',j('frozen_lab_compatibility_audit_contract.json')['external_evidence_mode'])
 def test_complete_matrix(self):
  c=j('frozen_lab_compatibility_audit_contract.json');r=j('family_requirement_ledger.json')['records'];self.assertEqual(len(r),len(c['families'])*len(c['requirements']));self.assertTrue(all(x['classification'] in c['classification_vocabulary'] for x in r))
 def test_missing_is_not_rejection(self):self.assertTrue(j('frozen_lab_compatibility_audit_contract.json')['rules']['missing_is_not_rejection'])
if __name__=='__main__':unittest.main()
