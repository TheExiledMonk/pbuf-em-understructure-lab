import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class EMX005Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): subprocess.run([sys.executable,'tools/run_emx005_representation_information_loss.py'],cwd=ROOT,check=True)
 def j(self,p): return json.loads((ROOT/p).read_text())
 def f(self): return self.j('runs/emx005/final_contract.json')
 def test_emx005_starting_gate(self): self.assertTrue(self.j('runs/emx005/starting_state.json')['EMX004_DEPENDENCY_VERIFIED'])
 def test_emx005_parent_trajectory_freeze(self): self.assertTrue(self.f()['PARENT_TRAJECTORY_FROZEN'])
 def test_emx005_exact_decomposition(self): self.assertFalse(self.j('runs/emx005/exact_information_decomposition.json')['DYNAMICS_EXECUTED'])
 def test_emx005_tensor_split_identity(self): self.assertLess(self.j('runs/emx005/exact_information_decomposition.json')['identity_errors']['M_MINUS_S_MINUS_A_L2'],1e-14)
 def test_emx005_loss_maps(self): self.assertEqual(len(self.j('runs/emx005/representation_loss_maps.json')),21)
 def test_emx005_aliasing(self): self.assertTrue(next(x for x in self.j('runs/emx005/representation_aliasing.json') if x['representation_id']=='ANTISYMMETRIC_TENSOR')['REPRESENTATION_ALIASING'])
 def test_emx005_t01_sufficiency(self): self.assertTrue(self.f()['T01_INFORMATION_AUDIT_COMPLETE'])
 def test_emx005_t02_sufficiency(self): self.assertTrue(self.f()['T02_INFORMATION_AUDIT_COMPLETE'])
 def test_emx005_t03_sufficiency(self): self.assertEqual(next(x for x in self.j('runs/emx005/information_ablation_matrix.json') if x['sector']=='ANTISYMMETRIC_TENSOR')['T03_PROPAGATION'],'LOST')
 def test_emx005_t04_sufficiency(self): self.assertEqual(next(x for x in self.j('runs/emx005/information_ablation_matrix.json') if x['sector']=='FULL_STATE')['T04_NEIGHBOR_RELAY'],'PRESERVED')
 def test_emx005_t05_sufficiency(self): self.assertTrue(self.f()['T05_INFORMATION_AUDIT_COMPLETE'])
 def test_emx005_minimal_sets(self): self.assertEqual(self.j('runs/emx005/minimal_sufficient_sets.json')['T03_MINIMAL_SUFFICIENT_SET'],'NONUNIQUE')
 def test_emx005_no_result_selected_sector(self): self.assertEqual(len(self.j('runs/emx005/frozen_audit_contract.json')['representation_set']),12)
 def test_emx005_no_c005_repair(self): self.assertTrue(self.f()['NO_C005_REPAIR'])
 def test_emx005_no_new_physics(self): self.assertTrue(self.f()['NO_NEW_PHYSICS'])
 def test_emx005_next_selector(self): self.assertEqual(self.f()['EMX006_TEST_SELECTION'],'SECONDARY_STRUCTURAL_MATRIX_BATTERY')
