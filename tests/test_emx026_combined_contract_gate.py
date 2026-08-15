import hashlib,json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'runs'/'emx026'
class T(unittest.TestCase):
 def test_contract(self):
  x=json.loads((R/'frozen_combined_law_contract.json').read_text());q=x.pop('contract_sha256');self.assertEqual(q,hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest());self.assertEqual(len(x['members']),1);self.assertEqual(x['constraint_map']['count'],76)
if __name__=='__main__':unittest.main()
