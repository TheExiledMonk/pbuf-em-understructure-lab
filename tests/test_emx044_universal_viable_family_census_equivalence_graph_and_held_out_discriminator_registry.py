import json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'runs'/'emx044'
def j(n):return json.loads((P/n).read_text())
class T(unittest.TestCase):
 def test_census_complete(self):self.assertTrue(j('frozen_family_census_contract.json')['FROZEN_BEFORE_RESULTS']);self.assertEqual(j('universal_viable_family_census.json')['count'],301)
 def test_certificates_preserve_families(self):
  x=j('evidence_preserving_equivalence_graph.json');self.assertEqual(len(x['graph']['edges']),0);self.assertTrue(all(c['member_count']>0 for c in x['equivalence_certificates']))
 def test_heldout_and_contextual_rules(self):
  x=j('final_contract.json');self.assertTrue(x['HELD_OUT_NOT_USED_FOR_ADMISSION']and x['HISTORICAL_GATES_CONTEXTUAL_ONLY']);self.assertFalse(x['NEW_DYNAMICS_EXECUTED'])
if __name__=='__main__':unittest.main()
