import json
import unittest
from pathlib import Path

P=Path(__file__).resolve().parents[1]/'runs'/'emx063'
def load(n): return json.loads((P/n).read_text())

class EMX063Tests(unittest.TestCase):
    def test_registry_frozen_before_results_and_covers_requested_families(self):
        c=load('frozen_wide_net_pattern_kinetic_and_history_closure_search_contract.json')
        self.assertTrue(c['FROZEN_BEFORE_RESULTS'])
        self.assertEqual({x['family'][0] for x in c['finite_candidate_registry']},{'A','B','C','D','E','F'})
        self.assertTrue(c['state_scope']['all_new_state_additions_must_be_listed_with_provenance'])
    def test_all_candidates_all_axes_and_hashed_cells_retained(self):
        c=load('frozen_wide_net_pattern_kinetic_and_history_closure_search_contract.json'); x=load('wide_net_pattern_kinetic_and_history_closure_ledger.json')
        self.assertEqual(set(x['candidate_test_matrix']),{a['id'] for a in c['finite_candidate_registry']})
        self.assertTrue(all(set(r)==set(c['required_test_axes']) for r in x['candidate_test_matrix'].values()))
        self.assertTrue(x['artifact_hashed_execution_cells'])
        self.assertTrue(all('artifact_input_sha256' in z and 'artifact_sha256' in z for z in x['artifact_hashed_execution_cells']))
    def test_boundaries_and_prior_results_preserved(self):
        x=load('wide_net_pattern_kinetic_and_history_closure_ledger.json'); f=load('final_contract.json'); r={z['candidate']:z for z in x['candidate_records']}
        self.assertEqual(r['C_RELATIONAL_DEGREE_ONE_HISTORY']['classification'],'UNDEFINED_PRIMITIVE_BOUNDARY')
        self.assertTrue(x['EMX010_062_preserved_without_relabel'])
        self.assertIn('A_CANONICAL_MU_PI',f['VIABLE_CLASSES_IN_SCOPE'])

if __name__=='__main__': unittest.main()
