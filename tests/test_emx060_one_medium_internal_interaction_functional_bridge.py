import json
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / 'runs' / 'emx060'
def load(name): return json.loads((P/name).read_text())

class EMX060Tests(unittest.TestCase):
    def test_contract_precedes_results_and_defines_one_complete_state(self):
        c = load('frozen_one_medium_internal_interaction_functional_bridge_contract.json')
        self.assertTrue(c['FROZEN_BEFORE_RESULTS'])
        self.assertEqual(set(c['complete_discrete_medium_state']['variables']), {'u','p','m','mu'})
        self.assertIn('neither an external object', c['complete_discrete_medium_state']['matter_definition'])

    def test_all_histories_controls_and_accounting_are_retained(self):
        c=load('frozen_one_medium_internal_interaction_functional_bridge_contract.json'); x=load('one_medium_internal_interaction_ledger.json')
        names={r['history'] for r in x['records']}
        self.assertTrue(set(c['predeclared_histories']) <= names)
        self.assertTrue(set(c['required_controls']) <= names)
        self.assertTrue(all(r['classification'] in c['classification_vocabulary'] for r in x['records']))
        qrecords=[r for r in x['records'] if r['cell']=='COMPLETE_Q_INTERNAL_HISTORY_LEDGER']
        self.assertTrue(qrecords and all(abs(r['ledger_residual']) < 2e-11 for r in qrecords))

    def test_prior_evidence_and_boundaries_are_preserved(self):
        x=load('one_medium_internal_interaction_ledger.json'); z=load('emx058_emx059_direct_comparison.json'); f=load('final_contract.json')
        self.assertEqual(set(x['prior_final_contracts_retained_verbatim']), {f'EMX0{n}' for n in range(55,60)})
        self.assertFalse(x['prior_labels_reclassified'])
        self.assertTrue(z['emx059_contradictions_preserved'])
        self.assertTrue(all(r['source_work_family_distinction']=='UNDEFINED_PRIMITIVE_BOUNDARY' for r in z['records']))
        self.assertTrue(f['EMX055_TO_EMX059_EVIDENCE_AND_LABELS_PRESERVED'])

if __name__ == '__main__': unittest.main()
