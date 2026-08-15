import json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'runs'/'emx045'
def j(n):return json.loads((P/n).read_text())
class T(unittest.TestCase):
 def test_frozen_and_finite(self):self.assertTrue(j('frozen_two_family_discriminator_contract.json')['FROZEN_BEFORE_RESULTS']);self.assertEqual(j('finite_execution_registry_and_results.json')['count'],17)
 def test_preserves_boundaries(self):
  x=j('final_contract.json');self.assertTrue(x['HISTORICAL_GATES_CONTEXTUAL_ONLY']);self.assertIn('NEW_PRIMITIVE_BOUNDARY',x['NEXT_SELECTOR'])
if __name__=='__main__':unittest.main()
