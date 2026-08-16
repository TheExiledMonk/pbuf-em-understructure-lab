import json
import unittest
from pathlib import Path

P=Path(__file__).resolve().parents[1]/'runs'/'emx058'
def load(name): return json.loads((P/name).read_text())

class EMX058Tests(unittest.TestCase):
    def test_frozen_nonblocking_contract(self):
        c=load('frozen_elastic_wake_and_history_record_battery_contract.json')
        self.assertTrue(c['FROZEN_BEFORE_RESULTS'])
        self.assertIn('NO_DEV167_OR_LAB_GIT_MODIFICATION_IMPORT_OR_EXECUTION',c['prohibitions'])
    def test_hashed_complete_accounting_and_required_controls(self):
        x=load('elastic_wake_and_history_record_ledger.json'); self.assertTrue(x['artifact_sha256'])
        names={r['cell'] for r in x['records']}
        self.assertIn('COMPLETE_SOURCE_MEDIUM_ENERGY_WORK_ACCOUNTING',names)
        self.assertIn('PRIOR_PASSAGE_DIRECTION_RECONSTRUCTION',names)
        self.assertTrue(set(load('frozen_elastic_wake_and_history_record_battery_contract.json')['fixed_controls']) <= names)
    def test_only_allowed_labels_and_boundaries(self):
        x=load('elastic_wake_and_history_record_ledger.json'); vocab=load('frozen_elastic_wake_and_history_record_battery_contract.json')['classification_vocabulary']
        self.assertTrue(all(r['classification'] in vocab for r in x['records']))
        self.assertTrue(any(r['classification']=='UNDEFINED_PRIMITIVE_BOUNDARY' for r in x['records']))
        self.assertTrue(x['no_candidate_rejected_for_missing_closure'])

if __name__=='__main__': unittest.main()
