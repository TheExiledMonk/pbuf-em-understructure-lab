import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs" / "emx014"


def load(name):
    return json.loads((RUN / name).read_text())


class TestEMX014EvidenceClosure(unittest.TestCase):
    def setUp(self):
        self.final = load("final_contract.json")

    def test_frozen_terminal_selector_matches_emx013(self):
        parent = json.loads((ROOT / "runs" / "emx013" / "emx014_test_selection.json").read_text())
        self.assertEqual(parent["EMX014_TEST_SELECTION"], "EVIDENCE_CLOSURE_NO_FURTHER_EXECUTION")
        self.assertEqual(self.final["EMX014_SELECTOR_VERIFIED"], parent["EMX014_TEST_SELECTION"])

    def test_closure_contract_digest_is_valid(self):
        contract = load("frozen_evidence_closure_contract.json")
        recorded = contract.pop("contract_sha256")
        actual = hashlib.sha256(json.dumps(contract, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.assertEqual(actual, recorded)

    def test_full_authorized_matrix_is_closed(self):
        closure = load("authorized_matrix_closure.json")
        self.assertEqual(closure["classification"], "FULL_AUTHORIZED_MATRIX_CLOSED")
        self.assertEqual(closure["authorized_run_count"], 13)
        self.assertTrue(closure["selector_lineage_complete"])
        self.assertTrue(self.final["FULL_AUTHORIZED_MATRIX_CLOSED"])

    def test_evidence_manifest_is_reproducible(self):
        manifest = load("evidence_manifest.json")
        artifacts = manifest["artifacts"]
        actual = hashlib.sha256(json.dumps(artifacts, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.assertEqual(actual, manifest["manifest_sha256"])
        for artifact in artifacts:
            number = int(artifact["run"].removeprefix("EMX"))
            final = json.loads((ROOT / f"runs/emx{number:03}" / "final_contract.json").read_text())
            self.assertEqual(final[f"EMX{number:03}_RESULT"], artifact["result"])
            if number >= 2:
                selector = json.loads((ROOT / f"runs/emx{number - 1:03}" / f"emx{number:03}_test_selection.json").read_text())
                self.assertEqual(selector[f"EMX{number:03}_TEST_SELECTION"], artifact["selected_by"])

    def test_no_further_execution_or_selector_is_authorized(self):
        self.assertTrue(self.final["NO_NEW_EXECUTION"])
        self.assertTrue(self.final["NO_FURTHER_SELECTOR"])
        self.assertFalse(self.final["T17_EXECUTED"] or self.final["T18_EXECUTED"])

    def test_prior_constraints_are_preserved(self):
        for key in ["NO_NEW_DYNAMICS", "NO_NEW_LOADING", "NO_TOPOLOGY_EXECUTION", "NO_T17_EXECUTION", "NO_T18_EXECUTION"]:
            self.assertTrue(self.final[key])


if __name__ == "__main__":
    unittest.main()
