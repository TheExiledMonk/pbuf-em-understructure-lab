import json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'runs'/'emx034'
class T(unittest.TestCase):
 def test_batch(self):
  x=json.loads((R/'batch_results.json').read_text());self.assertEqual(len(x['rows']),4);self.assertTrue(all(a['all_finite']for a in x['rows']))
if __name__=='__main__':unittest.main()
