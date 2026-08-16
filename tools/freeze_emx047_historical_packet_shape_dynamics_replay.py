#!/usr/bin/env python3
"""Freeze EMX047 without inventing the missing DEV167 reference geometry."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs" / "emx047"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    prior_path = ROOT / "runs/emx046/frozen_historical_packet_shape_replay_contract.json"
    observer_path = ROOT / "runs/emx041/shared_observer_definition.json"
    prior = json.loads(prior_path.read_text())
    contract = {
        "EMX047_SELECTOR": "HASH_PINNED_HISTORICAL_PACKET_SHAPE_DYNAMICS_REPLAY",
        "contract_revision": 2,
        "FROZEN_BEFORE_RESULTS": True,
        "source_artifacts": prior["historical_artifacts"]["transformed_packets"],
        # EMX046 preserves the byte hashes of the generated native arrays, not
        # paths to those arrays.  Carry those exact hashes forward verbatim.
        "source_artifact_bytes_sha256": prior["historical_artifacts"]["transformed_packets"],
        "external_recovered_state_sha256": {
            "excited_trajectory": prior["historical_artifacts"]["excited"]["sha256"],
            "background_trajectory": prior["historical_artifacts"]["background"]["sha256"],
        },
        "finite_shape_registry": ["COMPACT", "ELONGATED", "MIRRORED", "SPLIT"],
        "identity_artifact": "ORIGINAL recovered excited-minus-background frame 0",
        "requested_initialization_primitive": {
            "state": "recovered historical excited-minus-background native displacement and momentum at frame 0, transformed only by the frozen packet artifact",
            "required_historical_force": "reciprocal N6 pair force sigma(epsilon) r_hat; sigma=epsilon/(1-epsilon^2)",
            "required_mapping": "each directed neighbor needs its hash-pinned reference relation vector to construct r and r_hat",
            "lattice": [11, 11, 11], "boundary": "periodic N6", "dt": 0.04, "steps": 180,
            "normalization": "identical initial native displacement-plus-momentum L2 norm and frozen support rule",
        },
        "matched_local_family": {
            "family": "LOCAL_NEUTRAL_HARMONIC_PERIODIC_N6",
            "mapping": "same transformed and normalized native frame-0 displacement/momentum arrays",
            "update": "unit harmonic periodic-N6 kick-drift",
        },
        "observer": {
            "version": "EMX041_NATIVE_PERTURBATION_L2_FOUR_SUMMARY_V1",
            "metric": "full native state L2-history four-summary",
            "tolerance": 1e-12,
        },
        "controls": ["identity/reproduction", "zero-source retained EMX046 exact control", "parity", "time reversal", "dt-half refinement", "source-normalization"],
        "preflight_boundary": {
            "status": "UNAVAILABLE_PROVENANCE",
            "missing_item": "hash-pinned directed neighbor reference geometry/rest-relation vectors for the recovered DEV167 state",
            "evidence": "The available recovered artifacts contain displacement and momentum trajectories, not the reference relation vectors required by r_hat. Treating displacement differences as r makes rest neighbors have norm zero and the specified sigma(epsilon) singular at epsilon=-1.",
            "rule": "No historical-dynamics cell is executable unless source state, reference geometry, boundary, dt, source history, and observer inputs are uniquely specified and hash-verifiable.",
        },
        "classification_vocabulary": ["EXECUTED_DIFFERENTIATES_FAMILIES", "EXECUTED_COMPATIBLE_NONUNIQUE", "EXECUTED_INSUFFICIENT_TO_DISTINGUISH", "REPRODUCTION_CONTRADICTED", "UNAVAILABLE_PROVENANCE"],
        "input_sha256": {str(prior_path.relative_to(ROOT)): sha256(prior_path), str(observer_path.relative_to(ROOT)): sha256(observer_path)},
        "prohibitions": {"NO_DEV167_MODIFICATION": True, "NO_LAB_GIT_MODIFICATION": True, "NO_LAB_GIT_IMPORT": True, "NO_FITTING": True, "NO_HIDDEN_CHOICES": True, "NO_RESULT_SELECTED_VARIANTS": True, "NO_E_B_QED_MAPPING": True},
    }
    contract["contract_sha256"] = canonical_hash(contract)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "frozen_historical_packet_shape_dynamics_contract.json").write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n")
    (OUT / "starting_state.json").write_text(json.dumps({"CONTRACT_FROZEN_BEFORE_RESULTS": True, "EMX046_REPLAY_LIFT_PRESERVED": True, "INVALID_SMOKE_NOT_A_RESULT": True}, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
