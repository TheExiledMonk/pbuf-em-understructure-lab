import hashlib
import json
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / 'runs' / 'emx064'
V = {'SUPPORTED_IN_SCOPE', 'CONTRADICTED_IN_SCOPE', 'DISTINCT_OBSERVABLE_BEHAVIOR', 'NOT_ASSESSED', 'UNDEFINED_PRIMITIVE_BOUNDARY'}


def load(name): return json.loads((P / name).read_text())
def digest(value):
    value = dict(value); value.pop('artifact_sha256', None)
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


class EMX064Tests(unittest.TestCase):
    def test_contract_is_frozen_and_limits_execution_to_a_b(self):
        c = load('frozen_wide_net_conservative_pattern_closure_discriminator_contract.json')
        self.assertTrue(c['FROZEN_BEFORE_RESULTS'])
        self.assertEqual([x['id'] for x in c['allowed_emx063_classes_only']], ['A_CANONICAL_MU_PI', 'B_SYMPLECTIC_PHASE_PAIR'])
        self.assertEqual(len(c['predeclared_artifact_hashed_cells']), 6)

    def test_matched_cells_cover_both_classes_and_functionals(self):
        c = load('frozen_wide_net_conservative_pattern_closure_discriminator_contract.json')
        x = load('wide_net_conservative_pattern_closure_discriminator_ledger.json')
        self.assertTrue(x['only_allowed_classes_executed'])
        self.assertEqual(len(x['artifact_hashed_execution_cells']), 24)
        self.assertEqual({z['class'] for z in x['artifact_hashed_execution_cells']}, {'A_CANONICAL_MU_PI', 'B_SYMPLECTIC_PHASE_PAIR'})
        self.assertEqual({z['functional'] for z in x['artifact_hashed_execution_cells']}, set(c['emx060_interaction_functionals']))
        self.assertTrue(all(z['artifact_sha256'] == digest(z) for z in x['artifact_hashed_execution_cells']))

    def test_boundaries_and_nonidentifying_graph_are_retained(self):
        x = load('wide_net_conservative_pattern_closure_discriminator_ledger.json')
        f = load('final_contract.json')
        self.assertGreater(x['counts']['UNDEFINED_PRIMITIVE_BOUNDARY'], 0)
        self.assertEqual(x['equivalence_graph']['edges'][0]['relation'], 'FINITE_HELD_OUT_NONIDENTIFIABLE_UNDER_PI_EQUALS_XI')
        self.assertTrue(x['EMX010_063_preserved_without_relabel'])
        self.assertTrue(f['NO_PHYSICAL_VALIDITY_CLAIM'])


if __name__ == '__main__': unittest.main()
