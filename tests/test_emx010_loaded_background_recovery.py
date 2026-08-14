import json
import unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'runs'/'emx010'
def j(n): return json.loads((R/n).read_text())
class TestEMX010(unittest.TestCase):
 def setUp(self): self.f=j('final_contract.json')
 def test_emx010_starting_gate(self): self.assertEqual(j('starting_state.json')['EMX009_RESULT'],'T16_BLOCKED_LOADING_REPRESENTATION')
 def test_emx010_historical_loading_inventory(self): self.assertTrue(j('historical_loading_inventory.json')['HISTORICAL_LOADING_INVENTORY_COMPLETE'])
 def test_emx010_dev167_compatibility(self): self.assertTrue(j('loaded_replay_authorization.json')['DEV167_COMPATIBLE'])
 def test_emx010_parameter_recovery(self): self.assertTrue(j('loading_parameter_recovery.json')['SOURCE_PREPARATION_EXACT'])
 def test_emx010_artifact_recovery(self): self.assertEqual(j('loading_artifact_recovery.json')['artifacts'][0]['verification'],'HASH_VERIFIED_ARTIFACT')
 def test_emx010_source_history_gate(self): self.assertTrue(j('loading_parameter_recovery.json')['SOURCE_PREPARATION_EXACT'])
 def test_emx010_full_state_requirement(self): self.assertTrue(j('loading_artifact_recovery.json')['full_state_requirement']['p'])
 def test_emx010_directionality_gate(self): self.assertTrue(j('loaded_replay_authorization.json')['LOADING_DIRECTION_DERIVED'])
 def test_emx010_replay_authorization(self): self.assertTrue(j('loaded_replay_authorization.json')['authorized'])
 def test_emx010_replay_verification(self): self.assertEqual(j('loaded_replay_verification.json')['strongest_evidence'],'BYTE_EXACT')
 def test_emx010_background_stability(self): self.assertEqual(j('background_stability_audit.json')['classification'],'BOUNDED_DYNAMIC_BACKGROUND')
 def test_emx010_probe_composition(self): self.assertTrue(j('probe_composition_recovery.json')['PROBE_COMPOSITION_AUTHORIZED'])
 def test_emx010_valid_state_injection(self): self.assertEqual(j('valid_state_injection_audit.json')['VALID_STATE_INJECTION_ON_LOADED_BACKGROUND'],'AUTHORIZED')
 def test_emx010_no_linear_superposition(self): self.assertTrue(self.f['NO_LINEAR_TRAJECTORY_SUPERPOSITION'])
 def test_emx010_no_t16_execution(self): self.assertFalse(self.f['T16_EXECUTED'])
 def test_emx010_next_selector(self): self.assertEqual(self.f['EMX011_TEST_SELECTION'],'DIRECTIONAL_LOADING_T16_EXECUTION')
if __name__=='__main__': unittest.main()
