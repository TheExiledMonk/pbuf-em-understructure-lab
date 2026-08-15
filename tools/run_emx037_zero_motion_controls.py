#!/usr/bin/env python3
"""Execute only the EMX037 contract already frozen on main."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs" / "emx037"

def read(path):
    return json.loads(Path(path).read_text())

def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")

def main():
    contract = read(OUT / "frozen_zero_motion_control_contract.json")
    assert contract["FROZEN_BEFORE_RESULTS"] and contract["update"]["steps"] == 180
    cells = contract["selected_cells"]
    results = []
    for cell in cells:
        u = np.zeros((11, 11, 11, 3), dtype=float)
        p = np.zeros_like(u)
        # Frozen kick-then-drift ordering with its frozen zero force.
        for _ in range(contract["update"]["steps"]):
            p += 0.04 * 0.0
            u += 0.04 * p
        finite = bool(np.isfinite(u).all() and np.isfinite(p).all())
        results.append({
            "cell_id": cell,
            "steps": 180,
            "max_abs_u": float(np.max(np.abs(u))),
            "max_abs_p": float(np.max(np.abs(p))),
            "quadratic_state_sum": float(np.sum(u * u + p * p)),
            "source_persistence": "COMPATIBLE_NONUNIQUE" if finite and not u.any() and not p.any() else "INCOMPATIBLE",
            "stability": "COMPATIBLE_NONUNIQUE" if finite else "INCOMPATIBLE",
            "conservation": "COMPATIBLE_NONUNIQUE" if not u.any() and not p.any() else "INCOMPATIBLE",
            "causality": "COMPATIBLE_NONUNIQUE" if not u.any() and not p.any() else "INCOMPATIBLE",
            "static_interaction": "NOT_ASSESSED",
            "motion_dependent_difference": "NOT_ASSESSED",
            "orientation_torque": "NOT_ASSESSED",
            "reciprocity": "NOT_ASSESSED",
        })
    retained = read(ROOT / "runs" / "emx016" / "dev167_failure_combination_matrix.json")["retained_positive_constraints"]["records"]
    classification = [{
        "candidate_id": record["candidate_id"],
        "classification": "NOT_ASSESSED",
        "reason": "EMX037 zero-source/no-drive control does not instantiate the retained prepared-packet source condition; the prior retained result is preserved, not reclassified.",
        "prior_interpretation": record["interpretation"],
    } for record in retained]
    write("batch_results.json", {"batch": "ZERO_MOTION_REPO_LOCAL_CONTROLS", "cell_count": len(results), "results": results})
    write("retained_constraint_classification.json", {"retained_constraint_count": len(classification), "records": classification})
    write("final_contract.json", {
        "EMX037_RESULT": "ZERO_MOTION_REPO_LOCAL_CONTROLS_EXECUTED",
        "EXECUTED_CELL_COUNT": len(results),
        "CELL_GATE_SUMMARY": {"COMPATIBLE_NONUNIQUE_CONTROL": len(results), "INCOMPATIBLE": 0},
        "RETAINED_CONSTRAINTS": {"PRESERVED_PRIOR_RESULTS": len(classification), "NEWLY_ASSESSED": 0, "NOT_ASSESSED_IN_THIS_CONTROL": len(classification)},
        "NONZERO_EMX036_CELLS": "GATED_EXTERNAL_INPUT_ARTIFACT",
        "NEXT_SELECTOR": "IN_REPOSITORY_NONZERO_PREPARATION_ARTIFACT_OR_EXTERNAL_CODE_AUTHORITY_GATE",
        "NEXT_BOUNDARY": "A nonzero source preparation needs a byte artifact stored in this repository with its sha256 and a predeclared lift, or explicit authority to construct/read it through the canonical external input implementation. Neither is authorized by the EMX036 no-external-code rule.",
        "NO_DEV167_MODIFICATION": True,
        "NO_EXTERNAL_CODE_IMPORT": True,
        "NO_E_B_QED_MAPPING": True,
        "NO_FITTING": True,
    })

if __name__ == "__main__":
    main()
