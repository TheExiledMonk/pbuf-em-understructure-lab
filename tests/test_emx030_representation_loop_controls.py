import json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'runs'/'emx030'
class T(unittest.TestCase):
 def test_batch(self):
  x=json.loads((R/'batch_results.json').read_text());self.assertEqual(set(x)-{'retained_constraints_preserved'},{'A01','A02','F01'});self.assertEqual(x['retained_constraints_preserved'],76)
if __name__=='__main__':unittest.main()
