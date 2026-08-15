#!/usr/bin/env python3
"""Freeze EMX040 before reading audit outcomes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs" / "emx040"


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    inputs = [
        "runs/emx016/dev167_failure_combination_matrix.json",
        "runs/emx004/frozen_execution_contract.json",
        "runs/emx006/frozen_secondary_battery_contract.json",
        "runs/emx008/frozen_longitudinal_audit_contract.json",
        "runs/emx011/frozen_t16_execution_contract.json",
        "runs/emx011/t16_repeatability.json",
        "runs/emx012/frozen_mixing_audit_contract.json",
        "runs/emx012/trajectory_reuse.json",
        "runs/emx013/frozen_unloaded_asymmetry_audit_contract.json",
        "runs/emx013/trajectory_reuse.json",
        "runs/emx015/frozen_t17_t18_execution_contract.json",
        "runs/emx015/trajectory_reuse.json",
        "runs/emx038/frozen_repository_local_source_lift_contract.json",
        "runs/emx038/remaining_matrix_results.json",
        "runs/emx039/final_contract.json",
    ]
    contract = {
        "EMX040_SELECTOR": "GATE_VALIDITY_AND_COMPARABILITY_AUDIT",
        "FROZEN_BEFORE_RESULTS": True,
        "mode": "READ_ONLY_PROVENANCE_REPLAY_AND_COMPARABILITY_AUDIT",
        "retained_constraint_source": "runs/emx016/dev167_failure_combination_matrix.json",
        "retained_constraint_count": 76,
        "input_sha256": {path: file_hash(ROOT / path) for path in inputs},
        "historical_artifacts": {
            "excited_trajectory": {
                "path": "/home/fabian/lab-main-consolidation/runs/dev195_local_force_balance_restoration/excited_trajectory.npz",
                "expected_sha256": "118a680de0ba756cd56901fcf2db02cd2a765035357e7b38fb419927ae61afb4",
            },
            "background_trajectory": {
                "path": "/home/fabian/lab-main-consolidation/runs/dev195_local_force_balance_restoration/background_trajectory.npz",
                "expected_sha256": "67353948d6953f00348a37ea64fb83b0b7dd28b704dd2d3d8f88628647c191c4",
            },
        },
        "required_audits": [
            "exact provenance and hash",
            "replayability",
            "logical independence or strict redundancy",
            "observer and representation robustness",
            "tolerance sensitivity",
            "discriminator versus historical-conditional status",
            "historical fixed-packet to repository-local source-lift comparability",
        ],
        "classification_vocabulary": [
            "VERIFIED_ROBUST",
            "VERIFIED_CONDITIONAL",
            "UNDERDETERMINED_NEEDS_BRIDGE",
            "REDUNDANT",
            "REPRODUCTION_CONTRADICTED",
        ],
        "rules": {
            "preservation": "A retained gate is never altered, weakened, or deleted because a later model fails.",
            "robust": "Requires exact provenance, successful replay, observer/representation and tolerance robustness, and a meaning-preserving shared observer across compared families.",
            "conditional": "Verifies only under its exact fixed historical packet, control, observer, representation, and tolerance scope.",
            "redundancy": "Requires a predeclared exact logical duplicate; shared trajectory alone is insufficient.",
            "comparability": "Finite local-source responses do not compare to historical packet results without a predeclared meaning-preserving bridge.",
            "boundary": "If a bridge requires a genuinely new observer primitive, record the boundary and do not create or execute that primitive.",
        },
        "prohibitions": {
            "NO_DEV167_MODIFICATION": True,
            "NO_LAB_GIT_MODIFICATION": True,
            "NO_LAB_GIT_IMPORT": True,
            "NO_FITTING": True,
            "NO_RESULT_SELECTED_DIAGNOSTICS": True,
            "NO_E_B_QED_MAPPING": True,
        },
    }
    contract["contract_sha256"] = canonical_hash(contract)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "frozen_gate_validity_and_comparability_contract.json").write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n")
    (OUT / "starting_state.json").write_text(json.dumps({"CONTRACT_FROZEN_BEFORE_RESULTS": True, "RETAINED_COUNT": 76}, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
