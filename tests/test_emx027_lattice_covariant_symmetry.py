import json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'runs'/'emx027'
class T(unittest.TestCase):
 def test_controls(self):
  x=json.loads((R/'lattice_covariant_control_results.json').read_text());self.assertEqual(set(x['controls']),{'identity','yz_swap','e2_reflection'})
if __name__=='__main__':unittest.main()
