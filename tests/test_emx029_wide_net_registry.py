import json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'runs'/'emx029'
class T(unittest.TestCase):
 def test_registry(self):
  x=json.loads((R/'candidate_registry.json').read_text());self.assertEqual(set(a['bank']for a in x['candidates']),set('ABCDEFG'));self.assertEqual(x['count'],13)
 def test_retained(self):self.assertEqual(json.loads((R/'starting_state.json').read_text())['RETAINED_COUNT'],76)
if __name__=='__main__':unittest.main()
