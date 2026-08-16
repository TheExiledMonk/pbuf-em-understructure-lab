import json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'runs'/'emx052'
def j(n):return json.loads((P/n).read_text())
class T(unittest.TestCase):
 def test_old_work_gate_is_not_reused(self):self.assertEqual(j('virtual_work_audit.json')['old_gate_status'],'INVALID_ACCOUNTING_COMPARISON')
 def test_calibration_and_ready_contract(self):self.assertTrue(j('conservation_calibration.json')['convergence_verified']);self.assertGreater(j('conservation_calibration.json')['calibrated_relative_drift_tolerance'],0);self.assertTrue(j('gate_applicability.json')['barred_from_rejection_until_corrected_rerun'])
if __name__=='__main__':unittest.main()
