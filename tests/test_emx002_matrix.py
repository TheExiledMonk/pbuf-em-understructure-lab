import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class EMX002Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): subprocess.run([sys.executable,'tools/run_emx002_matrix.py'],cwd=ROOT,check=True)
 def j(self,p): return json.loads((ROOT/p).read_text())
 def test_starting_gate(self): self.assertTrue(self.j('runs/emx002/final_contract.json')['EMX001_DEPENDENCY_VERIFIED'])
 def test_candidate_freeze(self): self.assertEqual(self.j('runs/emx002/final_contract.json')['ACTIVE_CANDIDATE_COUNT'],13)
 def test_manifest(self): self.assertEqual(len(self.j('runs/emx002/execution_manifest.json')),100)
 def test_all_active_cells(self): self.assertEqual(len(self.j('matrix/emx002_primitive_result_matrix.json')),65)
 def test_no_blank_cells(self): self.assertTrue(all(x['status'] for x in self.j('matrix/emx002_primitive_result_matrix.json')))
 def test_blockers_are_not_negatives(self): self.assertTrue(all(x['classification']=='BLOCKED_ARCHIVE' for x in self.j('matrix/emx002_primitive_result_matrix.json')))
 def test_loading_axis(self): self.assertEqual(self.j('matrix/loading_sensitivity.json')['axis'],'background_loading_regime')
 def test_future_tests(self): self.assertEqual(len(self.j('runs/emx002/future_birefringence_tests.json')['tests']),3)
 def test_no_new_candidates(self): self.assertEqual(len(self.j('matrix/candidate_registry.json')),20)
 def test_next_selector(self): self.assertEqual(self.j('runs/emx002/emx003_test_selection.json')['EMX003_TEST_SELECTION'],'ARCHIVAL_REPLAY_GATE')
