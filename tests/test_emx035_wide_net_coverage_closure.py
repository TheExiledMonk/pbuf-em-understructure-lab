import json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'runs'/'emx035'
class T(unittest.TestCase):
 def test_closure(self):
  x=json.loads((R/'wide_net_coverage_matrix.json').read_text());self.assertEqual(len(x['records']),76);self.assertFalse(x['summary']['finite_next_batch_justified'])
if __name__=='__main__':unittest.main()
