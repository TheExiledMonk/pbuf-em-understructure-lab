import json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'runs'/'emx036'
class T(unittest.TestCase):
 def test_registry(self):
  x=json.loads((R/'factorial_registry.json').read_text());self.assertEqual(x['cell_count'],168);self.assertEqual(x['retained_constraint_count'],76)
if __name__=='__main__':unittest.main()
