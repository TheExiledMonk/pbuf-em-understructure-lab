import json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'runs'/'emx056'
def j(n):return json.loads((P/n).read_text())
class T(unittest.TestCase):
 def test_nonblocking_contract(self):self.assertEqual(j('frozen_pbuf_elasticity_emission_wide_net_contract.json')['mode'],'EVIDENCE_BUILDING_NON_REJECTION')
 def test_batch_a_records_retained(self):self.assertGreater(len(j('batch_a_exchange_registry.json')['records']),0)
if __name__=='__main__':unittest.main()
