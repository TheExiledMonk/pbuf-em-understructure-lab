import json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'runs'/'emx051'
def j(n):return json.loads((P/n).read_text())
class T(unittest.TestCase):
 def test_contract_and_hypotheses(self):c=j('frozen_finite_closure_candidate_contract.json');self.assertTrue(c['FROZEN_BEFORE_RESULTS']);self.assertIn('hypotheses',c['provenance'])
 def test_finite_registry(self):
  r=j('staged_cell_results.json');self.assertEqual(len(r['integrated_shape_cells']),12);self.assertTrue(all(x['observer_diagnostic_only'] for x in r['integrated_shape_cells']))
 def test_no_external_validity_claim(self):self.assertTrue(j('provenance_assumption_statement.json')['no_physical_validity_from_pass_or_compatibility'])
if __name__=='__main__':unittest.main()
