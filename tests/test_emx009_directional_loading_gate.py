import json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'runs'/'emx009'
def l(n): return json.loads((R/n).read_text())
class TestEMX009(unittest.TestCase):
 def setUp(self): self.f=l('final_contract.json')
 def test_emx009_starting_gate(self): self.assertEqual(l('starting_state.json')['EMX008_RESULT'],'LONGITUDINAL_INDEPENDENT_MODE_RESOLVED')
 def test_emx009_loading_inventory(self): self.assertEqual(l('loading_state_inventory.json')['classification'],'BLOCKED_SOURCE')
 def test_emx009_loading_authorization(self): self.assertEqual(l('loading_authorization_gate.json')['T16_RESULT'],'BLOCKED_LOADING_REPRESENTATION')
 def test_emx009_probe_composition_gate(self): self.assertEqual(l('probe_composition_gate.json')['LOADED_PROBE_COMPOSITION'],'BLOCKED_SOURCE')
 def test_emx009_unloaded_baseline_freeze(self): self.assertFalse(l('unloaded_baseline_receipt.json')['regenerated'])
 def test_emx009_t16_contract_frozen(self): self.assertIn('contract_sha256',l('frozen_t16_contract.json'))
 def test_emx009_transverse_split(self): self.assertFalse(l('t16_transverse_mode_split.json')['executed'])
 def test_emx009_longitudinal_control(self): self.assertTrue(self.f['T16_LONGITUDINAL_CONTROL_CLASSIFIED'])
 def test_emx009_force_origin(self): self.assertTrue(self.f['T16_FORCE_ORIGIN_CLASSIFIED'])
 def test_emx009_parent_priority(self): self.assertTrue(l('representation_t16_sensitivity.json')['parent_state_priority'])
 def test_emx009_representation_sensitivity(self): self.assertTrue(self.f['REPRESENTATION_T16_SENSITIVITY_COMPLETE'])
 def test_emx009_no_load_scan(self): self.assertTrue(l('frozen_t16_contract.json')['prohibitions']['NO_LOAD_MAGNITUDE_SCAN'])
 def test_emx009_no_linear_superposition(self): self.assertTrue(l('frozen_t16_contract.json')['prohibitions']['NO_LINEAR_TRAJECTORY_SUPERPOSITION'])
 def test_emx009_no_qed_mapping(self): self.assertTrue(self.f['NO_QED_MAPPING'])
 def test_emx009_no_t17_t18_execution(self): self.assertFalse(self.f['T17_EXECUTED'])
 def test_emx009_next_selector(self): self.assertEqual(self.f['EMX010_TEST_SELECTION'],'LOADED_BACKGROUND_REPLAY_RECOVERY_GATE')
if __name__=='__main__': unittest.main()
