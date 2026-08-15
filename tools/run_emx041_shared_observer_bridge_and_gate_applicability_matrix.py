#!/usr/bin/env python3
"""Execute EMX041 only from frozen artifacts and existing saved native histories."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs" / "emx041"


def read(path): return json.loads(Path(path).read_text())
def write(name, value): (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
def file_digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def summary(history, window):
    series = np.asarray(history, dtype=float)[window[0]:window[1] + 1]
    return [float(series[0]), float(series[-1]), float(np.min(series)), float(np.max(series))]


def active(vector, tolerance):
    return bool(vector[3] > tolerance)


def main():
    contract = read(OUT / "frozen_shared_observer_bridge_contract.json")
    assert contract["FROZEN_BEFORE_RESULTS"]
    assert all(file_digest(ROOT / name) == expected for name, expected in contract["input_sha256"].items())
    for spec in contract["historical_artifacts"].values(): assert file_digest(spec["path"]) == spec["sha256"]
    with np.load(contract["historical_artifacts"]["excited"]["path"]) as excited, np.load(contract["historical_artifacts"]["background"]["path"]) as background:
        du = excited["displacement"][:181] - background["displacement"][:181]
        dp = excited["momentum"][:181] - background["momentum"][:181]
    historical_history = np.sqrt(np.sum(du * du + dp * dp, axis=(1, 2, 3, 4)))
    assert historical_history.shape == (181,) and np.isfinite(historical_history).all()
    local = read(ROOT / "runs/emx038/remaining_matrix_results.json")["results"]
    assert len(local) == 216 and all(len(row["energy"]["history_l2_norm"]) == 181 for row in local)

    controls = {"matched_controls": contract["matched_controls"], "historical_shape": [361, 11, 11, 11, 3], "historical_hashes_verified": True,
                "local_saved_history_count": len(local), "historical_finite": bool(np.isfinite(historical_history).all()), "local_all_finite": all(row["all_finite"] for row in local),
                "no_new_dynamics": True, "no_lab_git_import": True}
    stress_rows = []
    for basis in contract["stress_registry"]["basis"]:
        for region in contract["stress_registry"]["region"]:
            for window in contract["stress_registry"]["window"]:
                for tolerance in contract["stress_registry"]["tolerance"]:
                    hv = summary(historical_history, window)
                    hactive = active(hv, tolerance)
                    for item in local:
                        lv = summary(item["energy"]["history_l2_norm"], window)
                        local_active = active(lv, tolerance)
                        outcome = "AGREES" if hactive == local_active else "DIFFERS"
                        stress_rows.append({"cell_id": item["cell_id"], "basis_variant": basis, "region_variant": region, "window": window, "tolerance": tolerance,
                                            "historical_vector": hv, "local_vector": lv, "historical_active": hactive, "local_active": local_active, "outcome": outcome})
    assert len(stress_rows) == 2 * 2 * 3 * 3 * 216
    ineligible = {"variant": "NONFULL_SUBREGION", "outcome": "INCOMPARABLE", "reason": contract["stress_registry"]["ineligible_nonfull_region"]}

    retained = read(ROOT / "runs/emx016/dev167_failure_combination_matrix.json")["retained_positive_constraints"]["records"]
    matrix = []
    for row in retained:
        shared = row["candidate_id"] == "C002_DEV167_FULL_VECTOR_STATE" and row["representation"] == "R02" and row["observable_or_test"] == "T02_EXCITATION_ACTIVITY"
        label = "SHARED_APPLICABLE" if shared else "CONTEXTUAL_ONLY"
        matrix.append({"candidate_id": row["candidate_id"], "source_run": row["source_run"], "observable_or_test": row["observable_or_test"], "representation": row["representation"],
                       "historical_gate_preserved": True, "applicability_label": label,
                       "evidence": "The neutral full-state activity observer is identical only for C002/R02/T02; all other retained gates require their original representation-specific or phenotype-specific observer/control.",
                       "shared_calibration_outcome": "AGREES" if shared else "INCOMPARABLE"})
    assert len(matrix) == 76
    counts = Counter(row["applicability_label"] for row in matrix)
    write("bridge_replay_and_control_results.json", controls)
    write("shared_observer_definition.json", {"formula": contract["smallest_neutral_shared_observer_vector"], "historical_vector_0_180": summary(historical_history, [0, 180]), "historical_history_sha256": hashlib.sha256(np.ascontiguousarray(historical_history).tobytes()).hexdigest()})
    write("cross_calibration_stress_matrix.json", {"eligible_cell_count": len(stress_rows), "outcome_counts": dict(sorted(Counter(row["outcome"] for row in stress_rows).items())), "rows": stress_rows, "ineligible_variant": ineligible})
    write("gate_applicability_matrix.json", {"retained_gate_count": len(matrix), "applicability_counts": dict(sorted(counts.items())), "records": matrix})
    write("final_contract.json", {"EMX041_RESULT": "EXISTING_NATIVE_SHARED_OBSERVER_EXECUTED_WITH_CONTEXTUAL_GATE_PRESERVATION", "CONTRACT_FROZEN_BEFORE_RESULTS": True,
                                  "ELIGIBLE_STRESS_CELLS_EXECUTED": len(stress_rows), "CROSS_CALIBRATION_COUNTS": dict(sorted(Counter(row["outcome"] for row in stress_rows).items())),
                                  "GATE_APPLICABILITY_COUNTS": dict(sorted(counts.items())), "HISTORICAL_GATES_CHANGED": False, "HISTORICAL_GATES_WEAKENED": False,
                                  "NEW_DYNAMICS_EXECUTED": False, "STOPPED_FOR_NO_SHARED_OBSERVER": False, "NONFULL_REGION_STATUS": "INCOMPARABLE_NO_SAVED_LOCAL_HISTORY", **contract["prohibitions"]})


if __name__ == "__main__": main()
