import json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'runs'/'emx042'
def j(n):return json.loads((P/n).read_text())
class T(unittest.TestCase):
 def test_contract_and_registry(self):
  self.assertTrue(j('frozen_universal_admission_contract.json')['FROZEN_BEFORE_RESULTS']);self.assertEqual(j('all_finite_candidate_cell_registry.json')['count'],335)
 def test_static_motion_complete_and_history_contextual(self):
  x=j('universal_admission_rerun_batches.json')['batches'];self.assertEqual(x['BATCH_B_STATIC_MOTION_224_CELLS']['count'],224);self.assertEqual(x['BATCH_C_CONTEXTUAL_PHENOTYPE_ONLY']['count'],76)
 def test_prohibitions_and_heldout(self):
  x=j('final_contract.json');self.assertTrue(x['HISTORICAL_GATES_UNCHANGED']);self.assertFalse(x['NEW_DYNAMICS_EXECUTED']);self.assertTrue(j('held_out_prediction_battery.json')['excluded_from_admission'])
if __name__=='__main__':unittest.main()
