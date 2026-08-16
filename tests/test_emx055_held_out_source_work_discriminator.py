import json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'runs'/'emx055'
def j(n):return json.loads((P/n).read_text())
class T(unittest.TestCase):
 def test_frozen_held_out_registry(self):self.assertTrue(j('frozen_held_out_source_work_discriminator_contract.json')['FROZEN_BEFORE_RESULTS'])
 def test_three_survivors_audited(self):self.assertEqual(len(j('held_out_registry_and_results.json')['remaining_survivors']),3)
 def test_no_physical_equivalence(self):self.assertTrue(j('family_separation_matrix_and_equivalence_graph.json')['no_physical_equivalence_claim'])
if __name__=='__main__':unittest.main()
