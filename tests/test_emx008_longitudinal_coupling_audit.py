import json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'runs'/'emx008'
def l(n): return json.loads((R/n).read_text())
class TestEMX008(unittest.TestCase):
 def setUp(self): self.f=l('final_contract.json')
 def test_emx008_starting_gate(self): self.assertEqual(l('starting_state.json')['EMX007_RESULT'],'NATIVE_MODE_STRUCTURE_PARTIALLY_RESOLVED')
 def test_emx008_frozen_contract(self): self.assertIn('contract_sha256',l('frozen_longitudinal_audit_contract.json'))
 def test_emx008_parent_priority(self): self.assertTrue(l('representation_longitudinal_sensitivity.json')['parent_state_priority'])
 def test_emx008_t19_conditional_rank(self): self.assertEqual(l('t19_longitudinal_conditional_rank.json')['rank_increment'],2)
 def test_emx008_t20_predictability(self): self.assertEqual(l('t20_longitudinal_predictability.json')['classification'],'NOT_DERIVABLE')
 def test_emx008_t21_temporal_order(self): self.assertTrue(self.f['T21_COMPLETE'])
 def test_emx008_t22_cotransport(self): self.assertTrue(self.f['T22_COMPLETE'])
 def test_emx008_t23_force_origin(self): self.assertTrue(self.f['T23_COMPLETE'])
 def test_emx008_orientation_stress_discrepancy(self): self.assertEqual(l('orientation_stress_discrepancy.json')['classification'],'ORIENTATION_STRESS_LOSES_COUPLING_INFORMATION')
 def test_emx008_information_ablation(self): self.assertTrue(self.f['LONGITUDINAL_INFORMATION_ABLATION_COMPLETE'])
 def test_emx008_core_sufficiency(self): self.assertEqual(l('core_longitudinal_sufficiency.json')['MOMENTUM_RELATION_CORE_LONGITUDINAL_SUFFICIENCY'],'CORE_SUFFICIENT')
 def test_emx008_parent_mode_dimensionality(self): self.assertEqual(l('parent_mode_dimensionality.json')['classification'],'2_TRANSVERSE_PLUS_1_INDEPENDENT_LONGITUDINAL')
 def test_emx008_no_black_box_fit(self): self.assertTrue(l('frozen_longitudinal_audit_contract.json')['prohibitions']['NO_BLACK_BOX_PREDICTOR'])
 def test_emx008_no_t16_execution(self): self.assertFalse(self.f['T16_EXECUTED'])
 def test_emx008_no_new_physics(self): self.assertTrue(self.f['NO_NEW_PHYSICS'])
 def test_emx008_next_selector(self): self.assertEqual(self.f['EMX009_TEST_SELECTION'],'DIRECTIONAL_LOADING_MODE_SPLIT_GATE')
if __name__=='__main__': unittest.main()
