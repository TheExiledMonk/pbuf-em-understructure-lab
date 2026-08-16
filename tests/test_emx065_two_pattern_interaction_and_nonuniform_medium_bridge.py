import hashlib
import json
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / 'runs' / 'emx065'
V = {'SUPPORTED_IN_SCOPE', 'CONTRADICTED_IN_SCOPE', 'DISTINCT_OBSERVABLE_BEHAVIOR', 'NOT_ASSESSED', 'UNDEFINED_PRIMITIVE_BOUNDARY'}


def load(name): return json.loads((P / name).read_text())
def digest(value):
    value = dict(value); value.pop('artifact_sha256', None)
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


class EMX065Tests(unittest.TestCase):
    def test_result_free_contract_and_registry_are_frozen(self):
        c, r = load('frozen_two_pattern_interaction_and_nonuniform_medium_bridge_contract.json'), load('finite_registry.json')
        self.assertTrue(c['FROZEN_BEFORE_RESULTS'])
        self.assertTrue(r['all_cells_predeclared'])
        self.assertTrue(r['result_free_registry'])
        self.assertEqual(len(c['eligible_emx064_classes']), 2)
        self.assertEqual(len(c['neutral_alternatives']), 4)
        self.assertEqual(len(c['predeclared_artifact_hashed_cells']), 7)

    def test_complete_matched_matrix_and_hashes(self):
        x = load('two_pattern_interaction_and_nonuniform_medium_bridge_ledger.json')
        cells = x['artifact_hashed_execution_cells']
        self.assertEqual(len(cells), 28)
        self.assertEqual({z['alternative'] for z in cells}, {'A_LOCAL_PINNING_TWO_PATTERN', 'A_LOCAL_STRAIN_TWO_PATTERN', 'B_LOCAL_PINNING_TWO_PATTERN', 'B_LOCAL_STRAIN_TWO_PATTERN'})
        self.assertTrue(all(z['artifact_sha256'] == digest(z) for z in cells))
        self.assertTrue(x['EMX010_064_preserved_without_relabel'])

    def test_boundaries_profiles_and_nonuniversal_graph_are_explicit(self):
        x, f = load('two_pattern_interaction_and_nonuniform_medium_bridge_ledger.json'), load('final_contract.json')
        self.assertGreater(x['counts']['UNDEFINED_PRIMITIVE_BOUNDARY'], 0)
        self.assertEqual(x['equivalence_graph']['edges'][0]['relation'], 'FINITE_HELD_OUT_NONIDENTIFIABLE_UNDER_PI_I_EQUALS_XI_I')
        self.assertTrue(f['NO_PHYSICAL_VALIDITY_OR_UNIVERSAL_ARROW_CLAIM'])
        self.assertTrue(set(x['counts']).issubset(V))


if __name__ == '__main__': unittest.main()
