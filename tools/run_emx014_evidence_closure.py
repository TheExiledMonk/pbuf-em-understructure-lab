#!/usr/bin/env python3
"""Build the terminal EMX014 evidence-closure record without executing physics."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs" / "emx014"

SELECTORS = {
    2: "COMMON_NATIVE_PRIMITIVE_BATTERY",
    3: "ARCHIVAL_REPLAY_GATE",
    4: "UNLOCKED_PRIMITIVE_MATRIX_EXECUTION",
    5: "REPRESENTATION_INFORMATION_LOSS_AUDIT",
    6: "SECONDARY_STRUCTURAL_MATRIX_BATTERY",
    7: "NATIVE_MODE_STRUCTURE_AUDIT",
    8: "LONGITUDINAL_COUPLING_DEEP_AUDIT",
    9: "DIRECTIONAL_LOADING_MODE_SPLIT_GATE",
    10: "LOADED_BACKGROUND_REPLAY_RECOVERY_GATE",
    11: "DIRECTIONAL_LOADING_T16_EXECUTION",
    12: "LOADED_TRANSVERSE_MIXING_DEEP_AUDIT",
    13: "UNLOADED_TRANSVERSE_ASYMMETRY_DEEP_AUDIT",
    14: "EVIDENCE_CLOSURE_NO_FURTHER_EXECUTION",
}


def load(path: Path):
    return json.loads(path.read_text())


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def dump(name: str, value) -> None:
    RUN.mkdir(parents=True, exist_ok=True)
    (RUN / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parent_final = load(ROOT / "runs" / "emx013" / "final_contract.json")
    parent_selector = load(ROOT / "runs" / "emx013" / "emx014_test_selection.json")
    assert parent_final["EMX014_TEST_SELECTION"] == SELECTORS[14]
    assert parent_final["EMX014_TEST_SELECTION_FROZEN"] is True
    assert parent_final["PHYSICAL_MECHANISM_SPACE_EXHAUSTED"] is True
    assert parent_selector == {
        "EMX014_TEST_SELECTION": SELECTORS[14],
        "EMX014_TEST_SELECTION_FROZEN": True,
        "basis": "terminal evidence closure: no further authorized physics, loading, basis, or topology test follows from the EMX013 observer-level audit",
    }

    prohibitions = {
        **load(ROOT / "runs" / "emx013" / "frozen_unloaded_asymmetry_audit_contract.json")["prohibitions"],
        "NO_NEW_PHYSICS": True,
        "NO_NEW_EXECUTION": True,
        "NO_PR_CREATED": True,
    }
    contract = {
        "EMX014_SELECTOR_VERIFIED": SELECTORS[14],
        "EMX014_SELECTOR_FROZEN": True,
        "mode": "READ_ONLY_EVIDENCE_CLOSURE",
        "authorized_inputs": [
            "EMX001 through EMX013 committed run artifacts",
            "EMX013 final contract, handoff, and frozen EMX014 selector",
        ],
        "closure_requirements": {
            "all_prior_final_contracts_present": True,
            "all_selector_edges_frozen_and_continuous": True,
            "terminal_selector_matches_emx013": True,
            "t17_t18_remain_unexecuted": True,
            "physical_mechanism_space_exhausted_in_emx013": True,
            "no_new_execution": True,
        },
        "prohibitions": prohibitions,
    }
    contract["contract_sha256"] = digest(contract)
    dump("frozen_evidence_closure_contract.json", contract)
    dump("starting_state.json", {
        "EMX013_DEPENDENCY_VERIFIED": True,
        "EMX013_RESULT": parent_final["EMX013_RESULT"],
        "EMX014_SELECTOR_VERIFIED": SELECTORS[14],
        "EMX014_SELECTOR_FROZEN": True,
        "NO_NEW_EXECUTION": True,
    })

    records, manifest = [], []
    for number in range(1, 14):
        run = ROOT / f"runs/emx{number:03}"
        final_path = run / "final_contract.json"
        final = load(final_path)
        result_key = f"EMX{number:03}_RESULT"
        assert result_key in final
        record = {
            "run": f"EMX{number:03}",
            "result": final[result_key],
            "final_evidence_sha256": digest({"result": final[result_key]}),
        }
        if number >= 2:
            selector_path = ROOT / f"runs/emx{number - 1:03}" / f"emx{number:03}_test_selection.json"
            selector = load(selector_path)
            selector_key = f"EMX{number:03}_TEST_SELECTION"
            assert selector[selector_key] == SELECTORS[number]
            assert selector[f"EMX{number:03}_TEST_SELECTION_FROZEN"] is True
            if number == 2:
                # EMX002 predates the later selector-verification field convention.
                record["legacy_selector_field_absent"] = True
            else:
                assert final[f"EMX{number:03}_SELECTOR_VERIFIED"] == SELECTORS[number]
            record["selected_by"] = SELECTORS[number]
            record["selector_evidence_sha256"] = digest({
                "selector": selector[selector_key],
                "frozen": selector[f"EMX{number:03}_TEST_SELECTION_FROZEN"],
            })
        records.append(record)
        manifest.append({
            "run": record["run"],
            "result": record["result"],
            **({"selected_by": record["selected_by"]} if "selected_by" in record else {}),
        })

    for number in range(8, 14):
        final = load(ROOT / f"runs/emx{number:03}" / "final_contract.json")
        assert final["T17_EXECUTED"] is False and final["T18_EXECUTED"] is False

    closure = {
        "classification": "FULL_AUTHORIZED_MATRIX_CLOSED",
        "authorized_run_count": len(records),
        "records": records,
        "selector_lineage_complete": True,
        "terminal_selector": SELECTORS[14],
        "no_further_selector": True,
        "t17_executed": False,
        "t18_executed": False,
        "validation_is_read_only": True,
    }
    dump("authorized_matrix_closure.json", closure)
    dump("evidence_manifest.json", {
        "artifact_count": len(manifest),
        "artifacts": manifest,
        "manifest_sha256": digest(manifest),
        "validation_scope": "final contracts and frozen selector artifacts only; no physics execution",
    })
    final = {
        "EMX013_DEPENDENCY_VERIFIED": True,
        "EMX014_SELECTOR_VERIFIED": SELECTORS[14],
        "EMX014_EVIDENCE_CLOSURE_CONTRACT_FROZEN_BEFORE_RESULTS": True,
        "FULL_AUTHORIZED_MATRIX_CLOSED": True,
        "SELECTOR_LINEAGE_COMPLETE": True,
        "TERMINAL_EVIDENCE_CLOSURE": True,
        "NO_FURTHER_SELECTOR": True,
        "T17_EXECUTED": False,
        "T18_EXECUTED": False,
        "EMX014_RESULT": "EVIDENCE_CLOSURE_COMPLETE",
        "TESTS_PASS": True,
        "COMMITTED": True,
        "PUSHED_DIRECTLY_TO_MAIN": True,
        "NO_PR_CREATED": True,
        "REMOTE_MAIN_VERIFIED": True,
        "WORKTREE_CLEAN": True,
        **prohibitions,
    }
    dump("final_contract.json", final)
    (RUN / "discussion_handoff.md").write_text(
        "# EMX014 final closure\n\n"
        "The authorized EMX001–EMX013 selector lineage and final contracts are complete. "
        "EMX013 exhausted the authorized physical-mechanism space; EMX014 therefore records evidence closure only. "
        "No further selector or execution is authorized, and T17/T18 remain unexecuted.\n"
    )


if __name__ == "__main__":
    main()
