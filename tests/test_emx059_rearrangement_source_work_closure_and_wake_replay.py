import json
import unittest
from pathlib import Path

P=Path(__file__).resolve().parents[1]/'runs'/'emx059'
def load(name): return json.loads((P/name).read_text())

class EMX059Tests(unittest.TestCase):
    def test_frozen_contract_is_nonblocking_and_has_predeclared_variants(self):
        c=load('frozen_rearrangement_source_work_closure_and_wake_replay_contract.json')
        self.assertTrue(c['FROZEN_BEFORE_RESULTS'])
        self.assertEqual(len(c['predeclared_neutral_accounting_variants']),3)
        self.assertTrue(c['scope_statement']['emx058_rearranging_contradictions_not_resolved_without_exact_new_evidence'])
    def test_all_required_controls_families_and_time_supports_are_present(self):
        c=load('frozen_rearrangement_source_work_closure_and_wake_replay_contract.json'); x=load('rearrangement_source_work_ledger.json')
        names={r['cell'] for r in x['records']}
        self.assertTrue(set(c['required_controls']) <= names)
        self.assertEqual(set(c['source_work_families_from_EMX058']), {r['family'] for r in x['records'] if r['family'] not in ('ALL',)})
        ledgers=[r for r in x['records'] if r['cell']=='TIME_SUPPORT_MATCHED_REARRANGEMENT_ENERGY_WORK_LEDGER']
        self.assertTrue(ledgers and all(r['time_support'] for r in ledgers))
    def test_exact_closure_replay_and_emx058_preservation(self):
        x=load('rearrangement_source_work_ledger.json'); w=load('wake_replay_ledger.json')
        self.assertTrue(x['artifact_sha256'])
        self.assertTrue(x['prior_emx058_rearranging_records_retained_verbatim'])
        self.assertFalse(x['prior_emx058_rearranging_contradictions_relabelled_as_resolved'])
        self.assertTrue(w['records'])
        self.assertTrue(all(r['limit'].endswith('not a universal-arrow claim.') for r in w['records']))
    def test_vocabulary_only(self):
        c=load('frozen_rearrangement_source_work_closure_and_wake_replay_contract.json'); x=load('rearrangement_source_work_ledger.json')
        self.assertTrue(all(r['classification'] in c['classification_vocabulary'] for r in x['records']))

if __name__=='__main__': unittest.main()
