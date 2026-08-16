import json
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / 'runs' / 'emx057'
def load(name): return json.loads((P / name).read_text())

class EMX057Tests(unittest.TestCase):
    def test_contract_is_frozen_and_non_historical(self):
        c = load('frozen_global_state_orientation_and_propagation_records_contract.json')
        self.assertTrue(c['FROZEN_BEFORE_RESULTS'])
        self.assertTrue(c['primitive']['non_historical'])
        self.assertTrue(c['primitive']['not_independent_physical_clock'])
    def test_artifacts_are_hashed_and_all_records_use_vocabulary(self):
        ledger = load('global_state_orientation_and_propagation_record_ledger.json')
        vocab = load('frozen_global_state_orientation_and_propagation_records_contract.json')['classification_vocabulary']
        self.assertTrue(ledger['artifact_sha256'])
        self.assertGreater(len(ledger['records']), 20)
        self.assertTrue(all(x['classification'] in vocab for x in ledger['records']))
    def test_boundaries_and_no_arrow_are_retained(self):
        ledger = load('global_state_orientation_and_propagation_record_ledger.json')
        names = {x['cell'] for x in ledger['records'] if x['classification'] == 'UNDEFINED_PRIMITIVE_BOUNDARY'}
        self.assertTrue({'TRUE_GLOBAL_REVERSAL','UNIVERSAL_ARROW','INDEPENDENT_PHYSICAL_CLOCK'} <= names)
        self.assertTrue(ledger['no_universal_arrow_claim'])

if __name__ == '__main__': unittest.main()
