#!/usr/bin/env python3
"""Freeze EMX037 before any zero-motion-control outcomes are calculated."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs" / "emx037"

def read(path):
    return json.loads(Path(path).read_text())

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def main():
    selected = read(ROOT / "runs" / "emx036" / "emx037_batch_selection.json")["cells"]
    retained = read(ROOT / "runs" / "emx016" / "dev167_failure_combination_matrix.json")["retained_positive_constraints"]
    assert len(selected) == 8 and retained["count"] == 76
    contract = {
        "EMX037_SELECTOR": "ZERO_MOTION_REPO_LOCAL_CONTROL_EXECUTION",
        "FROZEN_BEFORE_RESULTS": True,
        "selected_cells": selected,
        "state_and_lift": {"u": "zero 11^3 x 3 displacement array", "p": "zero 11^3 x 3 momentum array", "source_lift": "u=p=0; no nonzero input artifact"},
        "update": {"ordering": "kick then drift", "dt": 0.04, "steps": 180, "force": "zero for the zero-source neutral control"},
        "fixed_environment": {"lattice": "11^3", "boundary": "periodic N6", "duration": 180, "loading": "unloaded", "drive": "no-drive"},
        "controls": ["single-source condition is not instantiated", "paired-source condition is not instantiated", "unloaded", "no-drive", "IDENTITY", "TIME_REVERSE", "PARITY_X", "YZ_SWAP"],
        "gates": {"source_persistence": "zero state remains exactly zero", "stability": "all state values finite", "conservation": "sum(u^2+p^2) is zero", "causality": "zero update has no propagation"},
        "observer_policy": {"static_interaction": "NOT_ASSESSED: no nonzero source pair", "motion_dependent_difference": "NOT_ASSESSED: no motion preparation", "orientation_torque": "NOT_ASSESSED: no oriented source", "reciprocity": "NOT_ASSESSED: no pair response", "all_retained_constraints": "NOT_ASSESSED unless the zero-control identity itself is the stated condition"},
        "classification_vocabulary": ["COMPATIBLE_NONUNIQUE", "INCOMPATIBLE", "NOT_ASSESSED"],
        "retained_constraint_count": 76,
        "no_fitting": True,
        "no_result_selected_diagnostics": True,
        "prohibitions": {"NO_DEV167_MODIFICATION": True, "NO_EXTERNAL_CODE_IMPORT": True, "NO_E_B_QED_MAPPING": True},
    }
    contract["contract_sha256"] = digest(contract)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "frozen_zero_motion_control_contract.json").write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n")
    (OUT / "starting_state.json").write_text(json.dumps({"CONTRACT_FROZEN_BEFORE_RESULTS": True, "EMX036_COMMIT": "9d8f7a8", "RETAINED_COUNT": 76}, indent=2, sort_keys=True) + "\n")

if __name__ == "__main__":
    main()
