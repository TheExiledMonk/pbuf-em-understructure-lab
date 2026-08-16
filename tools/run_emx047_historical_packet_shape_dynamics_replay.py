#!/usr/bin/env python3
"""Record the verified EMX047 provenance boundary; never execute a surrogate force."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs" / "emx047"


def read(name: str) -> dict:
    return json.loads((OUT / name).read_text())


def write(name: str, value: object) -> None:
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main() -> None:
    contract = read("frozen_historical_packet_shape_dynamics_contract.json")
    assert contract["FROZEN_BEFORE_RESULTS"]
    boundary = contract["preflight_boundary"]
    assert boundary["status"] == "UNAVAILABLE_PROVENANCE"
    reason = boundary["evidence"]
    rows = [{
        "cell_id": f"EMX047_HISTORICAL_DYNAMICS_{shape}",
        "shape": shape,
        "historical_family": "HISTORICAL_DEV167_PREPARED_PACKET",
        "local_family": "LOCAL_NEUTRAL_HARMONIC_PERIODIC_N6",
        "classification": "UNAVAILABLE_PROVENANCE",
        "executed": False,
        "reason": reason,
        "observer": contract["observer"]["version"],
    } for shape in contract["finite_shape_registry"]]
    controls = {name: {"classification": "UNAVAILABLE_PROVENANCE", "executed": False, "reason": reason}
                for name in ("identity_reproduction", "parity", "time_reversal", "dt_half_refinement", "source_normalization")}
    controls["zero_source"] = {
        "classification": "EXECUTED_COMPATIBLE_NONUNIQUE",
        "executed": False,
        "retained_from": "EMX046 exact compatible zero-source control",
        "reason": "Retained unchanged; not rerun to select a result.",
    }
    write("invalid_preflight_audit.json", {
        "status": "INVALIDATED_NOT_A_PHYSICAL_RESULT",
        "scope": "uncommitted EMX047 displacement-only smoke attempt",
        "finding": "The attempted substitution of displacement differences for required pair relation vectors generated non-finite force values at rest.",
        "disposition": "Excluded from all registry classifications and conclusions; it is retained solely as an audit of why no surrogate replay was accepted.",
    })
    write("hash_ledger.json", {
        "contract_sha256": contract["contract_sha256"],
        "source_artifact_bytes_sha256": contract["source_artifact_bytes_sha256"],
        "external_recovered_state_sha256": contract["external_recovered_state_sha256"],
        "missing_hash_pinned_item": boundary["missing_item"],
        "hash_verifiable_historical_dynamics_initialization": False,
    })
    write("cell_registry_and_results.json", {"shape_cells": rows, "controls": controls, "registry_frozen_before_execution": True})
    write("family_comparison_matrix.json", {"rows": rows, "no_mechanism_equivalence_claim": True, "comparison_status": "INCOMPARABLE_AT_HISTORICAL_DYNAMICS_PRIMITIVE"})
    write("evidence_preserving_conclusion.json", {
        "conclusion": "EMX047 does not execute physical transformed-packet historical dynamics. The required reference geometry is unavailable, so every requested historical/local shape comparison is UNAVAILABLE_PROVENANCE. EMX046 deterministic replay-lift results remain unchanged and are explicitly distinct.",
        "shape_outcomes": {row["shape"]: row["classification"] for row in rows},
        "invalid_smoke_excluded": True,
        "historical_gates_contextual_only": True,
    })
    counts = {label: sum(row["classification"] == label for row in rows) for label in contract["classification_vocabulary"]}
    write("final_contract.json", {
        "EMX047_RESULT": "EXPLICIT_UNAVAILABLE_PROVENANCE_BOUNDARY",
        "COUNTS": counts,
        "HISTORICAL_GATES_CONTEXTUAL_ONLY": True,
        "ACTUAL_HISTORICAL_DYNAMICS_EXECUTED": False,
        "NEXT_SELECTOR": "HASH_PINNED_DEV167_REFERENCE_GEOMETRY_AND_SOURCE_HISTORY_RECOVERY_BOUNDARY",
        "NEXT_BOUNDARY": boundary["missing_item"],
        **contract["prohibitions"],
    })


if __name__ == "__main__":
    main()
