import json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'runs'/'emx043'
def j(n):return json.loads((P/n).read_text())
class T(unittest.TestCase):
 def test_all_pending_cells_enumerated_and_resolved(self):
  self.assertEqual(len(j('frozen_provenance_recovery_contract.json')['cells']),109);self.assertEqual(j('universal_unassessed_completion_matrix.json')['pending_count'],109)
 def test_only_recovery_vocabulary_and_no_dynamics(self):
  c=j('frozen_provenance_recovery_contract.json');m=j('universal_unassessed_completion_matrix.json');self.assertTrue(all(x['classification']in c['classification_vocabulary']for x in m['records']));self.assertFalse(j('final_contract.json')['NEW_DYNAMICS_EXECUTED'])
 def test_unrecoverable_not_failure_and_gates_preserved(self):
  x=j('final_contract.json');self.assertTrue(x['UNRECOVERABLE_IS_NOT_FAILURE']and x['HISTORICAL_GATES_UNCHANGED'])
if __name__=='__main__':unittest.main()
