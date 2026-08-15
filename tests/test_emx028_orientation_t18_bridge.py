import json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'runs'/'emx028'
class T(unittest.TestCase):
 def test_bridge(self):
  x=json.loads((R/'t18_bridge_results.json').read_text());self.assertGreater(x['loaded_joint_rank_strain_orientation_internal'],1)
if __name__=='__main__':unittest.main()
