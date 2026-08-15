import json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'runs'/'emx046'
def j(n):return json.loads((P/n).read_text())
class T(unittest.TestCase):
 def test_frozen_and_four_shapes(self):self.assertTrue(j('frozen_historical_packet_shape_replay_contract.json')['FROZEN_BEFORE_RESULTS']);self.assertEqual(j('packet_shape_cell_registry_and_results.json')['count'],4)
 def test_zero_retained(self):self.assertTrue(j('final_contract.json')['ZERO_SOURCE_RETAINED_NOT_RERUN'])
if __name__=='__main__':unittest.main()
