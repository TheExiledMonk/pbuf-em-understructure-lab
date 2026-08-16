import json
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "emx047"


def load(name):
    return json.loads((P / name).read_text())


class EMX047Test(unittest.TestCase):
    def test_contract_freezes_missing_geometry_boundary(self):
        contract = load("frozen_historical_packet_shape_dynamics_contract.json")
        self.assertTrue(contract["FROZEN_BEFORE_RESULTS"])
        self.assertEqual(contract["preflight_boundary"]["status"], "UNAVAILABLE_PROVENANCE")

    def test_all_requested_shapes_are_honestly_unavailable(self):
        rows = load("cell_registry_and_results.json")["shape_cells"]
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(r["classification"] == "UNAVAILABLE_PROVENANCE" and not r["executed"] for r in rows))

    def test_invalid_smoke_cannot_be_a_physical_result(self):
        self.assertEqual(load("invalid_preflight_audit.json")["status"], "INVALIDATED_NOT_A_PHYSICAL_RESULT")
        self.assertFalse(load("final_contract.json")["ACTUAL_HISTORICAL_DYNAMICS_EXECUTED"])


if __name__ == "__main__":
    unittest.main()
