import json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'runs'/'emx039'
class T(unittest.TestCase):
 def test_closure(self):
  x=json.loads((P/'coverage_matrix.json').read_text());self.assertEqual(x['cell_count'],224);self.assertTrue(x['all_finite']);self.assertEqual(x['retained_constraints_newly_assessed'],0)
if __name__=='__main__':unittest.main()
