import json
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / 'runs' / 'emx061'
def load(name): return json.loads((P / name).read_text())


class EMX061Tests(unittest.TestCase):
    def test_contract_is_predeclared_neutral_and_nonblocking(self):
        c = load('frozen_localized_pattern_and_admissible_history_selection_audit_contract.json')
        self.assertTrue(c['FROZEN_BEFORE_RESULTS'])
        self.assertEqual(len(c['predeclared_selector_registry']), 5)
        self.assertTrue(c['scope_statement']['not_DEV167_provenance'])
        self.assertTrue(c['prohibitions']['NO_FITTING_OR_RESELECTION'])

    def test_exact_degeneracy_and_action_replay_are_retained(self):
        x = load('localized_pattern_and_admissible_history_selection_ledger.json')
        self.assertTrue(x['exact_degeneracy_checks_passed'])
        c = load('frozen_localized_pattern_and_admissible_history_selection_audit_contract.json')
        self.assertEqual(set(x['test_axis_evidence']), set(c['required_test_axes']))
        self.assertEqual(len(x['family_evidence']), 2)
        for record in x['family_evidence']:
            self.assertTrue(all(v == 0.0 for v in record['zero_placement_interaction_energies'].values()))
            self.assertEqual(record['replay_action_difference'], 0.0)

    def test_selection_types_and_boundaries_are_not_confused(self):
        x, f = load('localized_pattern_and_admissible_history_selection_ledger.json'), load('final_contract.json')
        records = {r['selector']: r for r in x['selector_records']}
        self.assertEqual(records['STATIC_ENERGY_STATIONARITY_MINIMUM']['classification'], 'CONTRADICTED_IN_SCOPE')
        self.assertEqual(records['STATIONARY_DISCRETE_ACTION_ALTERNATIVES']['classification'], 'UNDEFINED_PRIMITIVE_BOUNDARY')
        self.assertTrue(all(r['control_is_not_a_derived_selector'] for r in x['control_evidence']))
        self.assertFalse(f['STATIC_PATTERN_SELECTED'])
        self.assertFalse(f['DYNAMIC_ORIENTED_HISTORY_SELECTED'])


if __name__ == '__main__': unittest.main()
