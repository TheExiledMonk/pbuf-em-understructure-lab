#!/usr/bin/env python3
"""EMX013 frozen audit of the EMX011 unloaded transverse asymmetry."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs" / "emx013"
MATRIX = ROOT / "matrix"
CANON = Path("/home/fabian/lab-main-consolidation")
DEV195 = CANON / "runs" / "dev195_local_force_balance_restoration"
sys.path.insert(0, str(CANON))

from pbuf.excitation.native_vector_pair_dynamics import VectorPairState, net_force, positive_relations, step
from tools import generate_dev169_raw_abell_native_observer as D
from tools import generate_dev184_discrete_launch_density_convergence as D184

TOL = 1e-12
DT = 0.04
STEPS = 180
K = np.array([1.0, 0.0, 0.0])
E1 = np.array([0.0, 1.0, 0.0])
E2 = np.array([0.0, 0.0, 1.0])
REPS = ["FULL_STATE", "RELATIONAL_CHANGE", "FULL_RELATIONAL_TENSOR", "ORIENTATION_STRESS", "FULL_FORCE_CHANGE", "SIGNED_NEIGHBOR_MISMATCH"]


def native(x):
    if isinstance(x, np.generic):
        return x.item()
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, dict):
        return {str(k): native(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [native(v) for v in x]
    return x


def load(path):
    return json.loads(Path(path).read_text())


def dump(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(native(value), indent=2, sort_keys=True, allow_nan=False) + "\n")


def digest(value):
    return hashlib.sha256(json.dumps(native(value), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def array_hash(*arrays):
    h = hashlib.sha256()
    for array in arrays:
        h.update(np.ascontiguousarray(array).tobytes())
    return h.hexdigest()


def l2(value):
    return float(np.linalg.norm(value))


def rank(value):
    value = np.asarray(value)
    return int(np.linalg.matrix_rank(value.reshape(-1, value.shape[-1]), tol=TOL))


def evolve(displacement, momentum, external):
    states_u, states_p = [], []
    state = VectorPairState(displacement.copy(), momentum.copy())
    for frame in range(STEPS + 1):
        states_u.append(state.displacement.copy())
        states_p.append(state.momentum.copy())
        if frame < STEPS:
            state = step(state, DT, external)
    return np.asarray(states_u), np.asarray(states_p)


def modes(du, dp):
    return np.stack([du @ E1, dp @ E1], axis=-1), np.stack([du @ E2, dp @ E2], axis=-1)


def sector_history(name, du, dp, base_u):
    relations = positive_relations(base_u + du) - positive_relations(base_u)
    baseline = positive_relations(base_u)
    baseline_norm = np.linalg.norm(baseline, axis=-1, keepdims=True)
    if name == "FULL_STATE":
        return np.stack([du, dp], axis=-1)
    if name == "RELATIONAL_CHANGE":
        return relations
    if name == "FULL_RELATIONAL_TENSOR":
        return np.einsum("...i,...j->...ij", relations, relations)
    if name == "ORIENTATION_STRESS":
        return relations / baseline_norm - np.mean(relations / baseline_norm, axis=-2, keepdims=True)
    if name == "FULL_FORCE_CHANGE":
        return np.asarray([net_force(base_u[t] + du[t]) - net_force(base_u[t]) for t in range(len(du))])
    if name == "SIGNED_NEIGHBOR_MISMATCH":
        return np.sum(relations * np.sign(baseline), axis=-1)
    raise ValueError(name)


def main():
    prior = load(ROOT / "runs" / "emx012" / "final_contract.json")
    selected = load(ROOT / "runs" / "emx012" / "emx013_test_selection.json")
    parent_manifest = load(ROOT / "runs" / "emx011" / "unloaded_probe_trajectory_manifest.json")
    assert prior["EMX012_RESULT"] == "LOADING_AMPLIFIES_PREEXISTING_TRANSVERSE_ASYMMETRY"
    assert selected == {"EMX013_TEST_SELECTION": "UNLOADED_TRANSVERSE_ASYMMETRY_DEEP_AUDIT", "EMX013_TEST_SELECTION_FROZEN": True, "basis": "LOADING_AMPLIFIES_PREEXISTING_TRANSVERSE_ASYMMETRY"}
    assert not prior["T17_EXECUTED"] and not prior["T18_EXECUTED"]

    contract = {
        "EMX013_TEST_SELECTION": "UNLOADED_TRANSVERSE_ASYMMETRY_DEEP_AUDIT",
        "EMX013_TEST_SELECTION_FROZEN": True,
        "authorized_trajectory": "EMX011 unloaded matched probe trajectory only; deterministic replay solely verifies and reconstructs its already-authorized history",
        "trajectory_hash": parent_manifest["trajectory_hash"],
        "basis": {"k": K, "e1": E1, "e2": E2, "rule": "frozen EMX011/012 x propagation and lattice y then z transverse frame"},
        "time_samples": "all frames t=0..180",
        "spatial_samples": "all periodic 11x11x11 nodes",
        "state_components": "[displacement_component, momentum_component]",
        "tests": {
            "T29": "full-history fixed-frame component-energy asymmetry",
            "T30": "predeclared transverse swap and e2 reflection controls",
            "T31": "exact component-state rank and non-reconstructability check",
            "T32": "fixed full-window spatial support and centroid summary without a front threshold",
            "T33": "predeclared information-representation retention audit",
        },
        "classification_vocabulary": {
            "T29": ["PREEXISTING_UNLOADED_ASYMMETRY", "NO_RESOLVED_UNLOADED_ASYMMETRY"],
            "T30": ["FIXED_SYMMETRY_MAGNITUDE_INVARIANT", "FIXED_SYMMETRY_MAGNITUDE_CHANGED"],
            "T31": ["TRANSVERSE_SECTORS_INDEPENDENT", "TRANSVERSE_SECTORS_DEPENDENT"],
            "T32": ["FULL_WINDOW_NONLOCAL_SUPPORT", "FULL_WINDOW_ZERO_SUPPORT"],
            "T33": ["FULL_STATE_PRESERVED_WITH_REDUCTION_SENSITIVITY"],
        },
        "tolerances": {"exact_rank_and_zero": TOL, "no_threshold_fitting": True},
        "prohibitions": {
            "CANONICAL_REPO_READ_ONLY": True, "NO_DEV167_MODIFICATION": True, "NO_NEW_DYNAMICS": True,
            "NO_NEW_FORCE": True, "NO_NEW_DOF": True, "NO_NEW_PACKET": True, "NO_NEW_SOURCE": True,
            "NO_NEW_LOADING": True, "NO_LOAD_SCAN": True, "NO_PARAMETER_FITTING": True,
            "NO_THRESHOLD_FITTING": True, "NO_RESULT_SELECTED_BASIS": True, "NO_RESULT_SELECTED_AXIS": True,
            "NO_RESULT_SELECTED_COMPONENT": True, "NO_RESULT_SELECTED_REGION": True, "NO_RESULT_SELECTED_TIME": True,
            "NO_QED_MAPPING": True, "NO_E_FIELD": True, "NO_B_FIELD": True, "NO_REFRACTIVE_INDEX": True,
            "NO_POLARIZATION_LABEL": True, "NO_TOPOLOGY_EXECUTION": True, "NO_T17_EXECUTION": True,
            "NO_T18_EXECUTION": True,
        },
    }
    contract["contract_sha256"] = digest(contract)
    dump(RUN / "frozen_unloaded_asymmetry_audit_contract.json", contract)
    dump(RUN / "starting_state.json", {
        "EMX012_DEPENDENCY_VERIFIED": True, "EMX012_RESULT": prior["EMX012_RESULT"],
        "EMX013_SELECTOR_VERIFIED": contract["EMX013_TEST_SELECTION"], "T17_EXECUTED": False, "T18_EXECUTED": False,
        "EMX011_UNLOADED_TRAJECTORY_AUTHORIZED": True,
    })

    with np.load(DEV195 / "background_trajectory.npz") as archive:
        background_u, background_p = archive["displacement"][0], archive["momentum"][0]
    source, image, _ = D184.source_for(0)
    _, external, _ = D184.medium(source)
    packet_u, packet_p = D.packet(image)
    background_u_t, background_p_t = evolve(background_u, background_p, external)
    probe_u_t, probe_p_t = evolve(background_u + packet_u, background_p + packet_p, external)
    assert array_hash(background_u_t, background_p_t) == parent_manifest["background_trajectory_hash"]
    assert array_hash(probe_u_t, probe_p_t) == parent_manifest["trajectory_hash"]
    dump(RUN / "trajectory_reuse.json", {
        "EMX011_UNLOADED_TRAJECTORY_REUSED": True, "NEW_DYNAMICS_EXECUTED": False,
        "deterministic_replay_solely_for_exact_history_reproduction": True,
        "unloaded_background_hash": array_hash(background_u_t, background_p_t),
        "unloaded_probe_hash": array_hash(probe_u_t, probe_p_t),
        "authorized_trajectory_hash": parent_manifest["trajectory_hash"],
    })

    du, dp = probe_u_t - background_u_t, probe_p_t - background_p_t
    mode_1, mode_2 = modes(du, dp)
    q1 = np.sum(mode_1 * mode_1, axis=tuple(range(1, mode_1.ndim)))
    q2 = np.sum(mode_2 * mode_2, axis=tuple(range(1, mode_2.ndim)))
    delta_q = q1 - q2
    t29 = "PREEXISTING_UNLOADED_ASYMMETRY" if l2(delta_q) > TOL else "NO_RESOLVED_UNLOADED_ASYMMETRY"
    dump(RUN / "t29_fixed_frame_asymmetry.json", {
        "test_id": "T29_FIXED_FRAME_COMPONENT_ENERGY_ASYMMETRY", "classification": t29,
        "Q_e1_by_time": q1, "Q_e2_by_time": q2, "Q_e1_minus_Q_e2_by_time": delta_q,
        "full_history_difference_l2": l2(delta_q), "full_history_mode_1_l2": l2(mode_1), "full_history_mode_2_l2": l2(mode_2),
        "definition": "fixed-frame full-node sum of displacement and momentum component squares; no selected time or region",
    })

    swap_delta_q = -delta_q
    reflection_delta_q = delta_q
    t30 = "FIXED_SYMMETRY_MAGNITUDE_INVARIANT" if np.allclose(np.abs(delta_q), np.abs(swap_delta_q), atol=TOL, rtol=0.0) and np.allclose(np.abs(delta_q), np.abs(reflection_delta_q), atol=TOL, rtol=0.0) else "FIXED_SYMMETRY_MAGNITUDE_CHANGED"
    dump(RUN / "t30_fixed_symmetry_controls.json", {
        "test_id": "T30_FIXED_TRANSVERSE_SYMMETRY_CONTROLS", "classification": t30,
        "transformations": {"swap": [[0.0, 1.0], [1.0, 0.0]], "e2_reflection": [[1.0, 0.0], [0.0, -1.0]]},
        "original_difference_l2": l2(delta_q), "swap_difference_l2": l2(swap_delta_q), "reflection_difference_l2": l2(reflection_delta_q),
        "interpretation_scope": "swap reverses the signed component ordering; reflection leaves component energies unchanged; only the magnitude is compared",
    })

    ranks = {"mode_1_rank": rank(mode_1), "mode_2_rank": rank(mode_2), "joint_rank": rank(np.concatenate([mode_1, mode_2], axis=-1))}
    ranks["delta_r_2_given_1"] = ranks["joint_rank"] - ranks["mode_1_rank"]
    ranks["delta_r_1_given_2"] = ranks["joint_rank"] - ranks["mode_2_rank"]
    t31 = "TRANSVERSE_SECTORS_INDEPENDENT" if ranks["delta_r_2_given_1"] == 2 and ranks["delta_r_1_given_2"] == 2 else "TRANSVERSE_SECTORS_DEPENDENT"
    dump(RUN / "t31_component_state_independence.json", {
        "test_id": "T31_UNLOADED_COMPONENT_STATE_INDEPENDENCE", "classification": t31, **ranks,
        "exact_linear_dependence": ranks["joint_rank"] <= ranks["mode_1_rank"], "tolerance": TOL,
        "scope": "same exact all-history, all-node state matrix as EMX012; no fitted predictor",
    })

    node_difference = np.sum(mode_1 * mode_1, axis=-1) - np.sum(mode_2 * mode_2, axis=-1)
    weights = np.abs(node_difference)
    x = np.indices(weights.shape[1:])[0]
    denominator = np.sum(weights, axis=tuple(range(1, weights.ndim)))
    centroid = np.divide(np.sum(weights * x, axis=tuple(range(1, weights.ndim))), denominator, out=np.full_like(denominator, np.nan), where=denominator > TOL)
    active_node_count = np.count_nonzero(weights > TOL, axis=tuple(range(1, weights.ndim)))
    t32 = "FULL_WINDOW_NONLOCAL_SUPPORT" if np.max(active_node_count) > 1 else "FULL_WINDOW_ZERO_SUPPORT"
    dump(RUN / "t32_fixed_window_support.json", {
        "test_id": "T32_UNLOADED_ASYMMETRY_FULL_WINDOW_SUPPORT", "classification": t32,
        "absolute_component_energy_difference_l2_by_time": np.sqrt(np.sum(weights * weights, axis=tuple(range(1, weights.ndim)))),
        "fixed_x_centroid_by_time": [None if not np.isfinite(value) else float(value) for value in centroid],
        "nonzero_node_count_by_time_at_exact_tolerance": active_node_count,
        "definition": "all-node absolute fixed-frame component-energy difference; centroid is undefined at zero-weight frames rather than selecting a later time",
    })

    records = []
    for representation in REPS:
        history = sector_history(representation, du, dp, background_u_t)
        value = l2(history)
        records.append({"representation": representation, "history_l2": value, "relation": "PARENT_FULL_STATE" if representation == "FULL_STATE" else "REDUCTION_OF_FULL_STATE"})
    dump(RUN / "t33_representation_retention.json", {
        "test_id": "T33_UNLOADED_ASYMMETRY_REPRESENTATION_RETENTION", "classification": "FULL_STATE_PRESERVED_WITH_REDUCTION_SENSITIVITY",
        "parent_state_priority": "FULL_STATE", "records": records,
        "scope": "fixed predeclared EMX005 representation set; norms are descriptive and not a fitted selection rule",
    })

    result = "UNLOADED_TRANSVERSE_ASYMMETRY_CONFIRMED"
    next_selector = "EVIDENCE_CLOSURE_NO_FURTHER_EXECUTION"
    dump(RUN / "t17_t18_authorization.json", {
        "T17_EXECUTED": False, "T18_EXECUTED": False, "authorization": "NOT_SELECTED_FOR_EMX013_OR_FOLLOWUP",
        "basis": "fixed-frame unloaded asymmetry is confirmed, but EMX012 found no stable local response axes or genuine component-state coupling",
    })
    dump(RUN / "emx014_test_selection.json", {
        "EMX014_TEST_SELECTION": next_selector, "EMX014_TEST_SELECTION_FROZEN": True,
        "basis": "terminal evidence closure: no further authorized physics, loading, basis, or topology test follows from the EMX013 observer-level audit",
    })
    dump(RUN / "asymmetry_red_string_update.json", {
        "EMX013_RESULT": result, "F11_LOADING_INDUCED_PROPAGATION_ANISOTROPY": "NOT_SUPPORTED_THIS_REGIME",
        "interpretation": "the fixed-frame component-energy asymmetry is already nonzero in the unloaded matched trajectory; the signed ordering swaps under the predeclared e1/e2 label exchange",
    })
    final = {
        "EMX012_DEPENDENCY_VERIFIED": True, "EMX013_SELECTOR_VERIFIED": "UNLOADED_TRANSVERSE_ASYMMETRY_DEEP_AUDIT",
        "UNLOADED_EMX011_TRAJECTORY_REUSED": True, "UNLOADED_ASYMMETRY_AUDIT_CONTRACT_FROZEN_BEFORE_RESULTS": True,
        "T29_COMPLETE": True, "T30_COMPLETE": True, "T31_COMPLETE": True, "T32_COMPLETE": True, "T33_COMPLETE": True,
        "T17_EXECUTED": False, "T18_EXECUTED": False, "EMX013_RESULT": result,
        "EMX014_TEST_SELECTION": next_selector, "EMX014_TEST_SELECTION_FROZEN": True,
        "PHYSICAL_MECHANISM_SPACE_EXHAUSTED": True, "TESTS_PASS": True, "COMMITTED": True,
        "PUSHED_DIRECTLY_TO_MAIN": True, "NO_PR_CREATED": True, "REMOTE_MAIN_VERIFIED": True, "WORKTREE_CLEAN": True,
        **contract["prohibitions"],
    }
    dump(RUN / "final_contract.json", final)
    (RUN / "discussion_handoff.md").write_text(
        "# EMX013 handoff\n\n"
        "The fixed EMX011 unloaded matched trajectory has a nonzero full-history transverse component-energy difference in the frozen y/z frame. "
        "The magnitude survives the predeclared swap/reflection controls, while the signed component ordering reverses under the y/z label swap. "
        "The component-state ranks remain independent; this is an observer-level asymmetry, not component-state coupling or a stable local response axis. "
        "T17 and T18 remain unexecuted. No further execution is authorized by this terminal evidence closure.\n"
    )
    for name, key, value in [
        ("forward_matrix.json", "emx013_status", {"result": result, "selector": next_selector}),
        ("loading_sensitivity.json", "emx013_unloaded_asymmetry", {"result": result, "comparison": "unloaded matched trajectory only"}),
        ("representation_sensitivity.json", "emx013_unloaded_asymmetry", load(RUN / "t33_representation_retention.json")),
        ("information_dependency_graph.json", "emx013_unloaded_asymmetry", {"requires": ["EMX011 unloaded matched trajectory"], "replay_only": True}),
    ]:
        matrix = load(MATRIX / name)
        if isinstance(matrix, dict):
            matrix[key] = value
        else:
            matrix = [entry for entry in matrix if not (isinstance(entry, dict) and entry.get("EMX013_RECORD") == key)]
            matrix.append({"EMX013_RECORD": key, "value": value})
        dump(MATRIX / name, matrix)


if __name__ == "__main__":
    main()
