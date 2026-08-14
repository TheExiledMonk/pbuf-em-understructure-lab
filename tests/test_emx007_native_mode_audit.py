import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; RUN=ROOT/'runs'/'emx007'
def load(n): return json.loads((RUN/n).read_text())
class TestEMX007NativeModeAudit(unittest.TestCase):
 def setUp(self): self.f=load('final_contract.json'); self.c=load('frozen_mode_audit_contract.json')
 def test_emx007_starting_gate(self): self.assertEqual(load('starting_state.json')['EMX006_RESULT'],'MIXED_SECONDARY_STRUCTURE')
 def test_emx007_frozen_contract(self): self.assertIn('contract_sha256',self.c)
 def test_emx007_direction_basis(self): self.assertEqual(self.c['transverse_plane']['basis_e1'],[0,1,0])
 def test_emx007_t11_mode_independence(self): self.assertEqual(load('candidate_mode_signatures.json')['signatures']['FULL_STATE']['T11'],'TWO_INDEPENDENT_TRANSVERSE_MODES')
 def test_emx007_t12_degeneracy(self): self.assertTrue(self.f['T12_COMPLETE'])
 def test_emx007_t13_longitudinal_coupling(self): self.assertTrue(self.f['T13_COMPLETE'])
 def test_emx007_t14_propagation_coherence(self): self.assertTrue(self.f['T14_COMPLETE'])
 def test_emx007_t15_mode_exchange(self): self.assertTrue(self.f['T15_COMPLETE'])
 def test_emx007_phase_audit(self): self.assertTrue(self.f['MODE_PHASE_AUDIT_COMPLETE'])
 def test_emx007_parent_state_priority(self): self.assertEqual(load('candidate_mode_signatures.json')['signatures']['FULL_STATE']['parent_priority'],'FULL_STATE_DERIVED')
 def test_emx007_representation_sensitivity(self): self.assertTrue(self.f['REPRESENTATION_MODE_SENSITIVITY_COMPLETE'])
 def test_emx007_minimal_mode_information(self): self.assertEqual(load('minimal_mode_information.json')['MODE_COUPLING'],'MOMENTUM_RELATION_CORE_SUFFICIENT')
 def test_emx007_topology_future_gate_only(self): self.assertTrue(self.f['NO_TOPOLOGY_POLARITY_EXECUTION'])
 def test_emx007_no_t16_execution(self): self.assertTrue(self.f['NO_T16_T18_EXECUTION'])
 def test_emx007_no_new_physics(self): self.assertTrue(self.f['NO_NEW_PHYSICS'])
 def test_emx007_next_selector(self): self.assertTrue(self.f['EMX008_TEST_SELECTION_FROZEN'])
if __name__=='__main__': unittest.main()
