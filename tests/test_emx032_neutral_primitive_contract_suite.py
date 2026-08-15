import hashlib,json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'runs'/'emx032'
class T(unittest.TestCase):
 def test_suite(self):
  x=json.loads((R/'frozen_neutral_primitive_contract_suite.json').read_text());h=x.pop('contract_sha256');self.assertEqual(h,hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest());self.assertEqual([a['id']for a in x['families']],['B01','B02','C01','C02','D02','E02','F02','G01'])
if __name__=='__main__':unittest.main()
