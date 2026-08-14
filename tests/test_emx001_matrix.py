import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = Path('/home/fabian/lab-main-consolidation')

class EMX001Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, 'tools/build_emx001_candidate_census.py', '--canonical', str(CANONICAL)], cwd=ROOT, check=True)
    def data(self, name):
        return json.loads((ROOT/'matrix'/name).read_text())
    def test_emx001_repo_snapshot(self):
        self.assertEqual(json.loads((ROOT/'provenance/canonical_repo_snapshot.json').read_text())['repository'], 'TheExiledMonk/lab')
    def test_emx001_registry_import(self): self.assertTrue(json.loads((ROOT/'runs/emx001/registry_import.json').read_text())['targets'])
    def test_emx001_candidate_census(self): self.assertGreaterEqual(len(self.data('candidate_registry.json')), 20)
    def test_emx001_equivalence(self): self.assertTrue(json.loads((ROOT/'runs/emx001/candidate_equivalence_matrix.json').read_text()))
    def test_emx001_admissibility(self): self.assertTrue(all(x['admissibility_status'] for x in self.data('candidate_registry.json')))
    def test_emx001_dependency_classes(self): self.assertTrue(all(x['dependency_classes'] is not None for x in self.data('candidate_registry.json')))
    def test_emx001_independence_groups(self): self.assertTrue(all(x['independence_group'] for x in self.data('candidate_registry.json')))
    def test_emx001_historical_scope(self): self.assertTrue(self.data('historical_negative_scope_matrix.json'))
    def test_emx001_matrix_integrity(self): subprocess.run([sys.executable, 'tools/validate_emx_matrix.py'], cwd=ROOT, check=True)
    def test_emx001_no_blank_cells(self): self.assertTrue(all(x['status'] for x in self.data('historical_matrix.json') + self.data('forward_matrix.json')))
    def test_emx001_no_result_selected_candidates(self): self.assertTrue(all('RESULT' not in ' '.join(x['admission_basis']) for x in self.data('candidate_registry.json')))
    def test_emx001_no_new_physics(self): self.assertTrue(json.loads((ROOT/'runs/emx001/final_contract.json').read_text())['NO_NEW_PHYSICS'])
    def test_emx001_next_selector(self): self.assertTrue(json.loads((ROOT/'runs/emx001/emx002_test_selection.json').read_text())['EMX002_TEST_SELECTION_FROZEN'])
