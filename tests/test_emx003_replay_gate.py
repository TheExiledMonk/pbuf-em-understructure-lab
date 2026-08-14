import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class EMX003ReplayGate(unittest.TestCase):
 @classmethod
 def setUpClass(c): subprocess.run([sys.executable,'tools/run_emx003_archival_replay_gate.py'],cwd=ROOT,check=True)
 def j(self,p): return json.loads((ROOT/p).read_text())
 def test_emx003_starting_gate(self): self.assertEqual(self.j('runs/emx003/final_contract.json')['EMX003_SELECTOR_VERIFIED'],'ARCHIVAL_REPLAY_GATE')
 def test_emx003_candidate_coverage(self): self.assertEqual(len(self.j('runs/emx003/candidate_replay_inventory.json')),13)
 def test_emx003_parent_trajectory_reuse(self): self.assertEqual(self.j('runs/emx003/final_contract.json')['PARENT_REPLAY_COUNT'],1)
 def test_emx003_replay_family_grouping(self): self.assertEqual(len(self.j('runs/emx003/replay_family_inventory.json')),5)
 def test_emx003_parameter_classification(self): self.assertTrue(self.j('runs/emx003/parameter_recovery_matrix.json'))
 def test_emx003_no_guessed_inputs(self): self.assertTrue(self.j('runs/emx003/final_contract.json')['NO_GUESSED_INPUTS'])
 def test_emx003_historical_control_separation(self): self.assertNotIn('C001_SCALAR_F03_PROPAGATION',[x['candidate_id'] for x in self.j('runs/emx003/candidate_replay_inventory.json')])
 def test_emx003_replay_authorization(self): self.assertEqual(self.j('runs/emx003/final_contract.json')['PRIMITIVE_CELLS_UNLOCKED'],45)
 def test_emx003_cell_unlock_matrix(self): self.assertEqual(len(self.j('runs/emx003/primitive_cell_unlock_matrix.json')),65)
 def test_emx003_no_physics_execution(self): self.assertTrue(self.j('runs/emx003/final_contract.json')['NO_PRIMITIVE_PHYSICS_TEST_EXECUTED'])
 def test_emx003_replay_verification(self): self.assertEqual(self.j('runs/emx003/replay_verification_summary.json')[0]['verification'],'HASH_VERIFIED_ARTIFACT')
 def test_emx003_no_new_physics(self): self.assertTrue(self.j('runs/emx003/final_contract.json')['NO_NEW_PHYSICS'])
 def test_emx003_next_selector(self): self.assertEqual(self.j('runs/emx003/emx004_test_selection.json')['EMX004_TEST_SELECTION'],'UNLOCKED_PRIMITIVE_MATRIX_EXECUTION')
