import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]; RUN=ROOT/'runs'/'emx006'
def load(n): return json.loads((RUN/n).read_text())

class TestEMX006SecondaryStructuralBattery(unittest.TestCase):
 def setUp(self): self.final=load('final_contract.json'); self.contract=load('frozen_secondary_battery_contract.json')
 def records(self,n): return load(n)['records']
 def test_emx006_starting_gate(self):
  s=load('starting_state.json'); self.assertEqual(s['EMX005_RESULT'],'PRIMITIVE_INFORMATION_CORE_IDENTIFIED'); self.assertEqual(s['EMX006_SELECTOR_VERIFIED'],'SECONDARY_STRUCTURAL_MATRIX_BATTERY'); self.assertEqual(s['CORE_NAME'],'MOMENTUM_RELATION_CORE')
 def test_emx006_frozen_contract(self): self.assertTrue(self.contract['EMX006_TEST_SELECTION_FROZEN']); self.assertIn('contract_sha256',self.contract)
 def test_emx006_information_sufficiency(self):
  self.assertIn('BLOCKED_INFORMATION_LOSS',[r['classification'] for r in self.records('t06_transverse_content.json')]); self.assertTrue(self.final['ALL_BLOCKED_CELLS_PRESERVED'])
 def test_emx006_t06_transverse(self): self.assertIn('TRANSVERSE_RANK_2',[r['classification'] for r in self.records('t06_transverse_content.json')])
 def test_emx006_t07_longitudinal(self): self.assertIn('LONGITUDINAL_PROPAGATING',[r['classification'] for r in self.records('t07_longitudinal_content.json')])
 def test_emx006_t08_parity(self):
  r={x['candidate_id']:x['classification'] for x in self.records('t08_handedness_parity.json')}; self.assertEqual(r['C005_DEV203_ANTISYMMETRIC_TENSOR'],'PARITY_EVEN')
 def test_emx006_t09_static_loaded(self): self.assertIn('BLOCKED_ARCHIVE',[r['classification'] for r in self.records('t09_static_loaded_organization.json')])
 def test_emx006_t10_source_outgoing(self): self.assertIn('BLOCKED_SOURCE_HISTORY',[r['classification'] for r in self.records('t10_source_generated_outgoing_structure.json')])
 def test_emx006_core_sufficiency(self): self.assertEqual(len(load('core_sufficiency.json')),5); self.assertTrue(self.final['MOMENTUM_RELATION_CORE_SECONDARY_SUFFICIENCY_CLASSIFIED'])
 def test_emx006_same_parent_counting(self): self.assertEqual(load('structural_convergence_table.json')['TWO_TRANSVERSE_DOF']['recurrence'],'SAME_PARENT_RECURRENCE')
 def test_emx006_no_result_selected_axis(self): self.assertEqual(self.contract['propagation_direction']['k_hat'],[1,0,0]); self.assertTrue(self.contract['prohibitions']['NO_RESULT_SELECTED_AXIS'])
 def test_emx006_no_new_source(self): self.assertTrue(self.contract['prohibitions']['NO_NEW_SOURCE'])
 def test_emx006_no_t16_execution(self): self.assertTrue(self.final['NO_T16_T18_EXECUTION'])
 def test_emx006_no_new_physics(self): self.assertTrue(self.final['NO_NEW_PHYSICS'])
 def test_emx006_next_selector(self): self.assertEqual(self.final['EMX007_TEST_SELECTION'],'NATIVE_MODE_STRUCTURE_AUDIT'); self.assertTrue(self.final['EMX007_TEST_SELECTION_FROZEN'])

if __name__=='__main__': unittest.main()
