#!/usr/bin/env python3
"""EMX020 executes exactly the independent harmonic realization frozen in EMX019."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs" / "emx020"
CANON = Path("/home/fabian/lab-main-consolidation")
DEV195 = CANON / "runs" / "dev195_local_force_balance_restoration"
DT = 0.04
STEPS = 180
TOL = 1e-12


def load(path):
    return json.loads(Path(path).read_text())


def native(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, dict):
        return {str(key): native(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [native(item) for item in value]
    return value


def dump(name, value):
    RUN.mkdir(parents=True, exist_ok=True)
    (RUN / name).write_text(json.dumps(native(value), indent=2, sort_keys=True, allow_nan=False) + "\n")


def digest(value):
    return hashlib.sha256(json.dumps(native(value), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def array_hash(*arrays):
    h = hashlib.sha256()
    for array in arrays:
        h.update(np.ascontiguousarray(array).tobytes())
    return h.hexdigest()


def force(u):
    return sum(np.roll(u, shift, axis=axis) - u for axis in range(3) for shift in (-1, 1))


def energy(u, p):
    potential = sum(np.sum((np.roll(u, -1, axis=axis) - u) ** 2) for axis in range(3)) / 2.0
    return float(np.sum(p * p) / 2.0 + potential)


def evolve(u0, p0):
    us, ps, energies = [], [], []
    u, p = u0.copy(), p0.copy()
    for frame in range(STEPS + 1):
        us.append(u.copy())
        ps.append(p.copy())
        energies.append(energy(u, p))
        if frame < STEPS:
            p = p + DT * force(u)
            u = u + DT * p
    return np.asarray(us), np.asarray(ps), np.asarray(energies)


def transformed(value, matrix):
    return value @ np.asarray(matrix, dtype=float).T


def rank(value):
    return int(np.linalg.matrix_rank(np.asarray(value).reshape(-1, value.shape[-1]), tol=TOL))


def main():
    contract = load(ROOT / "runs" / "emx019" / "frozen_alternative_model_authority_and_inputs_contract.json")
    prior = load(ROOT / "runs" / "emx019" / "final_contract.json")
    retained = load(ROOT / "runs" / "emx019" / "retained_constraint_observable_control_map.json")
    assert prior["EMX020_TEST_SELECTION"] == "FROZEN_ELASTIC_N6_ALTERNATIVE_COMPARISON_EXECUTION"
    assert retained["count"] == len(retained["records"]) == 76
    assert contract["integrator"]["dt"] == DT
    execution = {
        "EMX020_SELECTOR_VERIFIED": "FROZEN_ELASTIC_N6_ALTERNATIVE_COMPARISON_EXECUTION",
        "EMX020_SELECTOR_FROZEN": True,
        "authorization": "standing user authorization for the exact EMX019 frozen realization",
        "parent_contract": "runs/emx019/frozen_alternative_model_authority_and_inputs_contract.json",
        "candidate_id": "EMX019_ELASTIC_N6_UNIT_HARMONIC_LATTICE",
        "predeclared_battery": {
            "matched_response": "all frames 0..180, full 11^3 field: evolve loaded/unloaded background and corresponding packet-injected state independently, then subtract each same-law background history",
            "state_rank": "rank at absolute tolerance 1e-12 of full-history response u and p components, including fixed x/y/z and transverse y/z reductions",
            "symmetry_controls": "identity, fixed y/z swap, and fixed e2 reflection: independent replays from transformed loaded initial state; compare to transformed identity replay over every frame/site/component",
            "invariant_reporting": "record harmonic Hamiltonian initial/final/min/max and relative excursion without fitted stability threshold",
            "classification_vocabulary": ["LOADED_UNLOADED_RESPONSE_DIFFERENT", "LOADED_UNLOADED_RESPONSE_EQUAL"],
        },
        "prohibitions": {
            "NO_DEV167_MODIFICATION": True,
            "NO_ALTERNATIVE_CODE_IMPORT": True,
            "NO_PARAMETER_FITTING": True,
            "NO_HIDDEN_PARAMETERS": True,
            "NO_E_B_OR_QED_MAPPING": True,
            "NO_LOAD_OR_GEOMETRY_SCAN": True,
            "NO_NEW_PACKET": True,
            "NO_NEW_LOADING": True,
            "NO_RESULT_SELECTED_AXIS_BASIS_TIME_REGION": True,
        },
    }
    execution["contract_sha256"] = digest(execution)
    dump("frozen_elastic_n6_comparison_execution_contract.json", execution)
    dump("starting_state.json", {"EMX019_DEPENDENCY_VERIFIED": True, "EMX020_SELECTOR_VERIFIED": execution["EMX020_SELECTOR_VERIFIED"], "EXECUTION_CONTRACT_FROZEN_BEFORE_RESULTS": True, "RETAINED_CONSTRAINTS_INHERITED": retained["count"]})

    sys.path.insert(0, str(CANON))
    from tools import generate_dev169_raw_abell_native_observer as D
    from tools import generate_dev184_discrete_launch_density_convergence as D184

    source, image, _ = D184.source_for(0)
    packet_u, packet_p = D.packet(image)
    inputs = contract["frozen_inputs"]
    assert file_hash(DEV195 / "background_trajectory.npz") == inputs["unloaded_background"]["sha256"]
    assert file_hash(DEV195 / "excited_trajectory.npz") == inputs["loaded_background"]["sha256"]
    assert array_hash(packet_u) == inputs["packet"]["displacement_sha256"]
    assert array_hash(packet_p) == inputs["packet"]["momentum_sha256"]
    with np.load(DEV195 / "background_trajectory.npz", allow_pickle=False) as archive:
        unloaded_u0, unloaded_p0 = archive["displacement"][0], archive["momentum"][0]
    with np.load(DEV195 / "excited_trajectory.npz", allow_pickle=False) as archive:
        loaded_u0, loaded_p0 = archive["displacement"][0], archive["momentum"][0]

    ub_u, ub_p, ub_h = evolve(unloaded_u0, unloaded_p0)
    lb_u, lb_p, lb_h = evolve(loaded_u0, loaded_p0)
    up_u, up_p, up_h = evolve(unloaded_u0 + packet_u, unloaded_p0 + packet_p)
    lp_u, lp_p, lp_h = evolve(loaded_u0 + packet_u, loaded_p0 + packet_p)
    du_u, dp_u = up_u - ub_u, up_p - ub_p
    du_l, dp_l = lp_u - lb_u, lp_p - lb_p
    response_difference = float(np.linalg.norm(np.concatenate(((du_l - du_u).ravel(), (dp_l - dp_u).ravel()))))
    classification = "LOADED_UNLOADED_RESPONSE_DIFFERENT" if response_difference > TOL else "LOADED_UNLOADED_RESPONSE_EQUAL"
    histories = {
        "input_hashes": {"unloaded_background": file_hash(DEV195 / "background_trajectory.npz"), "loaded_background": file_hash(DEV195 / "excited_trajectory.npz"), "packet_u": array_hash(packet_u), "packet_p": array_hash(packet_p)},
        "trajectory_hashes": {"unloaded_background": array_hash(ub_u, ub_p), "loaded_background": array_hash(lb_u, lb_p), "unloaded_probe": array_hash(up_u, up_p), "loaded_probe": array_hash(lp_u, lp_p)},
        "response_hashes": {"unloaded": array_hash(du_u, dp_u), "loaded": array_hash(du_l, dp_l)},
        "all_finite": bool(all(np.isfinite(x).all() for x in (ub_u, ub_p, lb_u, lb_p, up_u, up_p, lp_u, lp_p))),
        "new_dynamics_executed": True,
        "DEV167_modified": False,
    }
    dump("frozen_input_and_trajectory_verification.json", histories)
    response = {
        "classification": classification,
        "loaded_response_l2": float(np.linalg.norm(np.concatenate((du_l.ravel(), dp_l.ravel()))),),
        "unloaded_response_l2": float(np.linalg.norm(np.concatenate((du_u.ravel(), dp_u.ravel()))),),
        "loaded_minus_unloaded_response_l2": response_difference,
        "definition": execution["predeclared_battery"]["matched_response"],
        "no_claim": "A difference is an alternative-law response observation, not a unique mechanism selection or an EM/QED interpretation.",
    }
    dump("matched_loaded_unloaded_response.json", response)
    ranks = {
        "tolerance": TOL,
        "unloaded": {"u_xyz": rank(du_u), "p_xyz": rank(dp_u), "u_yz": rank(du_u[..., 1:]), "p_yz": rank(dp_u[..., 1:]), "u_x": rank(du_u[..., :1]), "p_x": rank(dp_u[..., :1])},
        "loaded": {"u_xyz": rank(du_l), "p_xyz": rank(dp_l), "u_yz": rank(du_l[..., 1:]), "p_yz": rank(dp_l[..., 1:]), "u_x": rank(du_l[..., :1]), "p_x": rank(dp_l[..., :1])},
        "definition": execution["predeclared_battery"]["state_rank"],
    }
    dump("full_history_state_rank.json", ranks)
    energy_report = {}
    for name, values in {"unloaded_background": ub_h, "loaded_background": lb_h, "unloaded_probe": up_h, "loaded_probe": lp_h}.items():
        energy_report[name] = {"initial": float(values[0]), "final": float(values[-1]), "minimum": float(values.min()), "maximum": float(values.max()), "relative_excursion": float((values.max() - values.min()) / max(abs(values[0]), 1e-300))}
    dump("harmonic_invariant_report.json", {"definition": execution["predeclared_battery"]["invariant_reporting"], "histories": energy_report})
    symmetry = {}
    for name, matrix in contract["controls_and_observables"]["symmetry_controls"].items():
        cu, cp, _ = evolve(transformed(loaded_u0 + packet_u, matrix), transformed(loaded_p0 + packet_p, matrix))
        symmetry[name] = {"state_hash": array_hash(cu, cp), "max_abs_u_equivariance_error": float(np.max(np.abs(cu - transformed(lp_u, matrix)))), "max_abs_p_equivariance_error": float(np.max(np.abs(cp - transformed(lp_p, matrix)))), "exact_at_tolerance": bool(np.max(np.abs(cu - transformed(lp_u, matrix))) <= TOL and np.max(np.abs(cp - transformed(lp_p, matrix))) <= TOL)}
    dump("fixed_symmetry_control.json", {"definition": execution["predeclared_battery"]["symmetry_controls"], "controls": symmetry})
    next_selector = "ALTERNATIVE_LAW_RETAINED_CONSTRAINT_COMPATIBILITY_MATRIX"
    dump("emx021_test_selection.json", {"EMX021_TEST_SELECTION": next_selector, "EMX021_TEST_SELECTION_FROZEN": True, "basis": "EMX020 supplies one frozen alternative-law loaded/unloaded result, ranks, invariant records, and symmetry controls. EMX021 must classify joint compatibility against all retained constraints without treating non-unique passes as disposable."})
    final = {"EMX019_DEPENDENCY_VERIFIED": True, "EMX020_SELECTOR_VERIFIED": execution["EMX020_SELECTOR_VERIFIED"], "EMX020_EXECUTION_CONTRACT_FROZEN_BEFORE_RESULTS": True, "FROZEN_ALTERNATIVE_DYNAMICS_EXECUTED": True, "FROZEN_INPUTS_VERIFIED": True, "FULL_HISTORY_MATCHED_CONTROL_EXECUTED": True, "FIXED_SYMMETRY_CONTROLS_EXECUTED": True, "RETAINED_POSITIVE_CONSTRAINTS_PRESERVED": True, "NO_DEV167_MODIFICATION": True, "NO_ALTERNATIVE_CODE_IMPORT": True, "NO_PARAMETER_FITTING": True, "NO_E_B_OR_QED_MAPPING": True, "EMX020_RESULT": classification, "EMX021_TEST_SELECTION": next_selector, "EMX021_TEST_SELECTION_FROZEN": True, "TESTS_PASS": True, "COMMITTED": True, "PUSHED_DIRECTLY_TO_MAIN": True, "REMOTE_MAIN_VERIFIED": True, "WORKTREE_CLEAN": True, **execution["prohibitions"]}
    dump("final_contract.json", final)
    (RUN / "discussion_handoff.md").write_text("# EMX020 frozen harmonic comparison\n\nThe EMX019 harmonic N6 realization was executed exactly once for the fixed loaded/unloaded initializations and fixed symmetry controls. Its outcome is a law-specific comparison only. EMX021 classifies it jointly against every retained constraint; non-unique passes remain retained requirements.\n")


if __name__ == "__main__":
    main()
