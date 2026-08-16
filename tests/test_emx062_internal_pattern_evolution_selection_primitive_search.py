import json
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / 'runs' / 'emx062'
def load(name): return json.loads((P / name).read_text())


class EMX062Tests(unittest.TestCase):
    def test_contract_freezes_complete_state_registry_and_constraints(self):
        c = load('frozen_internal_pattern_evolution_selection_primitive_search_contract.json')
        self.assertTrue(c['FROZEN_BEFORE_RESULTS'])
        self.assertEqual([x['id'] for x in c['finite_candidate_registry']], ['NO_SELECTOR_CONTROL', 'CONSERVATIVE_COUPLED_VARIATIONAL', 'CONSTRAINED_ADMISSIBLE_CONTINUATION', 'DETERMINISTIC_LOCAL_RELAXATION'])
        self.assertTrue(c['primitive_constraints']['no_independent_external_clock'])
        self.assertTrue(c['scope_statement']['not_DEV167_provenance'])

    def test_all_axes_and_ledgers_are_retained(self):
        c, x = load('frozen_internal_pattern_evolution_selection_primitive_search_contract.json'), load('internal_pattern_evolution_selection_ledger.json')
        self.assertEqual(x['required_test_axes'], c['required_test_axes'])
        self.assertEqual(set(x['candidate_test_matrix']), {a['id'] for a in c['finite_candidate_registry']})
        self.assertTrue(all(set(row) == set(c['required_test_axes']) for row in x['candidate_test_matrix'].values()))
        for family in x['family_evidence'].values():
            self.assertTrue(all(v == 0.0 for v in family['zero_placement_degenerate_energies'].values()))
            self.assertTrue(family['seeded_relaxation']['CENTER']['all_decreases_nonnegative_to_roundoff'])
            self.assertEqual(family['seeded_relaxation']['CENTER']['energy_ledger_residual'], 0.0)
            self.assertFalse(family['parameterization']['independent_clock_introduced'])

    def test_boundaries_and_irreversibility_are_explicit(self):
        x, f = load('internal_pattern_evolution_selection_ledger.json'), load('final_contract.json')
        r = {a['candidate']: a for a in x['candidate_records']}
        self.assertEqual(r['CONSERVATIVE_COUPLED_VARIATIONAL']['classification'], 'UNDEFINED_PRIMITIVE_BOUNDARY')
        self.assertTrue(r['DETERMINISTIC_LOCAL_RELAXATION']['adds_irreversibility'])
        self.assertTrue(f['EMX061_NONSELECTION_NOT_RELABELLED_AS_SOLVED'])


if __name__ == '__main__': unittest.main()
