import hashlib
import json
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / 'runs' / 'emx066'
V = {'SUPPORTED_IN_SCOPE', 'CONTRADICTED_IN_SCOPE', 'DISTINCT_OBSERVABLE_BEHAVIOR', 'NOT_ASSESSED', 'UNDEFINED_PRIMITIVE_BOUNDARY'}


def load(name): return json.loads((P / name).read_text())
def digest(value):
    value = dict(value); value.pop('artifact_sha256', None)
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


class EMX066Tests(unittest.TestCase):
    def test_contract_and_registry_are_result_free_and_separated(self):
        c, r = load('frozen_sector_change_and_internal_distinguishability_wide_net_contract.json'), load('finite_registry.json')
        self.assertTrue(c['FROZEN_BEFORE_RESULTS'])
        self.assertTrue(r['branches_explicitly_separated'])
        self.assertTrue(r['result_free_registry'])
        self.assertEqual(len(r['branch_A']['extensions']), 2)
        self.assertEqual(len(r['branch_B']['closures']), 4)

    def test_complete_hashed_execution_and_explicit_sector_boundary(self):
        x = load('sector_change_and_internal_distinguishability_wide_net_ledger.json')
        cells = x['branch_A_sector_changing_execution_cells'] + x['branch_B_internal_distinguishability_execution_cells']
        self.assertEqual(len(x['branch_A_sector_changing_execution_cells']), 10)
        self.assertEqual(len(x['branch_B_internal_distinguishability_execution_cells']), 28)
        self.assertTrue(all(z['artifact_sha256'] == digest(z) for z in cells))
        conversion = [z for z in x['branch_A_sector_changing_execution_cells'] if z['cell'] == 'DYNAMICAL_MODE_CONVERSION_COLLISION_SEPARATION']
        self.assertTrue(all(z['mode_conversion']['transition_is_dynamical_not_boundary_relabel'] for z in conversion))
        self.assertGreater(x['counts']['UNDEFINED_PRIMITIVE_BOUNDARY'], 0)
        self.assertTrue(x['EMX010_065_preserved_without_relabel'])

    def test_scoped_graph_and_prohibitions(self):
        x, f = load('sector_change_and_internal_distinguishability_wide_net_ledger.json'), load('final_contract.json')
        self.assertEqual(x['equivalence_graph']['edges'][0]['relation'], 'FINITE_SCOPE_NONIDENTIFIABILITY_UNDER_PI_I_EQUALS_XI_I')
        self.assertIn('creation/annihilation', x['residual_boundary'])
        self.assertTrue(f['NO_PHYSICAL_VALIDITY_OR_UNIVERSAL_ARROW_CLAIM'])
        self.assertTrue(set(x['counts']).issubset(V))


if __name__ == '__main__': unittest.main()
