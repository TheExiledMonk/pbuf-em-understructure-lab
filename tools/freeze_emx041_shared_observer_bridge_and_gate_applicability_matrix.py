#!/usr/bin/env python3
"""Freeze EMX041's read-only shared-observer bridge before any outcome."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs" / "emx041"


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def file_digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    inputs = [
        "runs/emx016/dev167_failure_combination_matrix.json",
        "runs/emx004/frozen_execution_contract.json",
        "runs/emx038/frozen_repository_local_source_lift_contract.json",
        "runs/emx038/remaining_matrix_results.json",
        "runs/emx040/final_contract.json",
        "runs/emx040/gate_ledger.json",
    ]
    contract = {
        "EMX041_SELECTOR": "SHARED_OBSERVER_BRIDGE_AND_GATE_APPLICABILITY_MATRIX",
        "FROZEN_BEFORE_RESULTS": True,
        "mode": "READ_ONLY_EXISTING_NATIVE_QUANTITY_BRIDGE",
        "input_sha256": {item: file_digest(ROOT / item) for item in inputs},
        "historical_artifacts": {
            "excited": {"path": "/home/fabian/lab-main-consolidation/runs/dev195_local_force_balance_restoration/excited_trajectory.npz", "sha256": "118a680de0ba756cd56901fcf2db02cd2a765035357e7b38fb419927ae61afb4"},
            "background": {"path": "/home/fabian/lab-main-consolidation/runs/dev195_local_force_balance_restoration/background_trajectory.npz", "sha256": "67353948d6953f00348a37ea64fb83b0b7dd28b704dd2d3d8f88628647c191c4"},
        },
        "gate_families": {
            "universal_sanity": "finite native state summary, fixed zero-source identity control, and exact artifact integrity; these are not replacements for phenotype gates",
            "shared_observer": "full-lattice perturbation-state norm under exactly the same formula on both families",
            "contextual_historical_phenotype": "all historical representation-specific, spatial, force, orientation, loading, and conditional-rank gates retain their original packet/control scope",
        },
        "smallest_neutral_shared_observer_vector": {
            "name": "NATIVE_PERTURBATION_L2_FOUR_SUMMARY",
            "native_formula": "s(t)=sqrt(sum_all_sites,sum_components(delta_u(t)^2 + delta_p(t)^2)); V=(s(0), s(180), min_t s(t), max_t s(t)) for t=0..180",
            "historical_delta": "excited_trajectory minus matched background_trajectory",
            "repository_local_delta": "stored EMX038 neutral source-lift state relative to its declared zero background",
            "region": "all periodic 11^3 sites",
            "basis": "all three native vector components",
            "no_normalization_or_fit": True,
        },
        "matched_controls": {"geometry": "11^3", "boundary": "periodic N6", "dt": 0.04, "time_window": [0, 180], "region": "all periodic 11^3 sites"},
        "stress_registry": {
            "basis": ["IDENTITY_ALL_NATIVE_COMPONENTS", "YZ_SIGNED_PERMUTATION_ALL_COMPONENTS"],
            "region": ["FULL_PERIODIC_VOLUME", "FULL_PERIODIC_VOLUME_X_REINDEX"],
            "window": [[0, 180], [0, 90], [90, 180]],
            "tolerance": [0.0, 1e-12, 1e-9],
            "ineligible_nonfull_region": "No EMX038 region-resolved history was retained; no subregion bridge may be reconstructed or simulated.",
        },
        "cross_calibration": {
            "outcomes": ["AGREES", "DIFFERS", "INCOMPARABLE"],
            "rule": "For each fixed local cell and stress cell, AGREES iff both historical and local summaries are finite and their active/inactive classification agrees at the frozen tolerance; DIFFERS iff both are finite and it differs; INCOMPARABLE otherwise.",
        },
        "gate_applicability_labels": ["UNIVERSAL", "SHARED_APPLICABLE", "CONTEXTUAL_ONLY", "STILL_UNDERDETERMINED"],
        "prohibitions": {"NO_DEV167_MODIFICATION": True, "NO_LAB_GIT_MODIFICATION": True, "NO_LAB_GIT_IMPORT": True, "NO_NEW_DYNAMICS": True, "NO_FITTING": True, "NO_RESULT_SELECTED_MEASURES": True, "NO_E_B_QED_MAPPING": True},
    }
    contract["contract_sha256"] = digest(contract)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "frozen_shared_observer_bridge_contract.json").write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n")
    (OUT / "starting_state.json").write_text(json.dumps({"CONTRACT_FROZEN_BEFORE_RESULTS": True, "RETAINED_GATES": 76, "NEW_DYNAMICS_AUTHORIZED": False}, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
