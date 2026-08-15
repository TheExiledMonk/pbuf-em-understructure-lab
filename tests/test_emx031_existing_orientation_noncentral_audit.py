import json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'runs'/'emx031'
class T(unittest.TestCase):
 def test_batch(self):self.assertEqual(json.loads((R/'batch_results.json').read_text())['retained_constraints_preserved'],76)
if __name__=='__main__':unittest.main()
