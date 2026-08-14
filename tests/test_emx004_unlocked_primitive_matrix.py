import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class EMX004Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): subprocess.run([sys.executable,'tools/run_emx004_unlocked_primitive_matrix.py'],cwd=ROOT,check=True)
 def j(self,p): return json.loads((ROOT/p).read_text())
 def final(self): return self.j('runs/emx004/final_contract.json')
 def test_emx004_starting_gate(self): self.assertTrue(self.j('runs/emx004/starting_state.json')['EMX003_DEPENDENCY_VERIFIED'])
 def test_emx004_exact_45_cell_authorization(self): self.assertEqual(self.final()['AUTHORIZED_CELL_COUNT'],45)
 def test_emx004_blocked_20_preserved(self): self.assertEqual(self.final()['BLOCKED_CELL_COUNT'],20)
 def test_emx004_frozen_contract(self): self.assertIn('contract_sha256',self.j('runs/emx004/frozen_execution_contract.json'))
 def test_emx004_parent_state_reuse(self): self.assertEqual({x['parent_trajectory_id'] for x in self.j('runs/emx004/candidate_primitive_signatures.json')},{'DEV195_CANONICAL_PACKET_PARENT'})
 def test_emx004_t01(self): self.assertEqual(len(self.j('runs/emx004/t01_results.json')),13)
 def test_emx004_t02(self): self.assertEqual(len(self.j('runs/emx004/t02_results.json')),13)
 def test_emx004_t03(self): self.assertEqual(len(self.j('runs/emx004/t03_results.json')),13)
 def test_emx004_t04(self): self.assertEqual(len(self.j('runs/emx004/t04_results.json')),13)
 def test_emx004_t05(self): self.assertEqual(len(self.j('runs/emx004/t05_results.json')),13)
 def test_emx004_no_result_selection(self): self.assertEqual(self.j('runs/emx004/frozen_execution_contract.json')['numerical_tolerances']['classification'],'none; exact IEEE zero/nonzero and np.array_equal')
 def test_emx004_representation_divergence(self): self.assertTrue(self.j('runs/emx004/representation_divergence.json')[0]['REPRESENTATION_DIVERGENCE'])
 def test_emx004_independence_counting(self): self.assertFalse(self.j('runs/emx004/red_string_analysis.json')['CROSS_INDEPENDENCE_GROUP_RECURRING'])
 def test_emx004_red_string(self): self.assertTrue(self.j('runs/emx004/red_string_analysis.json')['SAME_PARENT_RECURRING'])
 def test_emx004_no_new_physics(self): self.assertTrue(self.final()['NO_NEW_PHYSICS'])
 def test_emx004_next_selector(self): self.assertEqual(self.final()['EMX005_TEST_SELECTION'],'REPRESENTATION_INFORMATION_LOSS_AUDIT')
