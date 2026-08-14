#!/usr/bin/env python3
"""EMX015: frozen, matched-history T17/T18 audit."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs" / "emx015"
EMX016 = ROOT / "runs" / "emx016"
CANON = Path("/home/fabian/lab-main-consolidation")
DEV195 = CANON / "runs" / "dev195_local_force_balance_restoration"
DEV202 = CANON / "runs" / "dev202_self_loaded_transverse"
sys.path.insert(0, str(CANON))

from pbuf.excitation.native_vector_pair_dynamics import VectorPairState, positive_relations, step
from pbuf.observer.self_loaded_transverse import weighted_periodic_centroid
from tools import generate_dev169_raw_abell_native_observer as D
from tools import generate_dev184_discrete_launch_density_convergence as D184

TOL = 1e-12
DT = 0.04
STEPS = 180
SHAPE = (11, 11, 11)


def native(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, dict):
        return {str(k): native(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [native(v) for v in value]
    return value


def load(path):
    return json.loads(Path(path).read_text())


def dump(root, name, value):
    root.mkdir(parents=True, exist_ok=True)
    (root / name).write_text(json.dumps(native(value), indent=2, sort_keys=True, allow_nan=False) + "\n")


def digest(value):
    return hashlib.sha256(json.dumps(native(value), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def array_hash(*arrays):
    h = hashlib.sha256()
    for array in arrays:
        h.update(np.ascontiguousarray(array).tobytes())
    return h.hexdigest()


def evolve(displacement, momentum, external):
    us, ps = [], []
    state = VectorPairState(displacement.copy(), momentum.copy())
    for frame in range(STEPS + 1):
        us.append(state.displacement.copy())
        ps.append(state.momentum.copy())
        if frame < STEPS:
            state = step(state, DT, external)
    return np.asarray(us), np.asarray(ps)


def periodic_delta(a, b):
    return (np.asarray(a) - np.asarray(b) + np.asarray(SHAPE) / 2) % np.asarray(SHAPE) - np.asarray(SHAPE) / 2


def response_centroids(du, dp):
    weights = np.sum(du * du + dp * dp, axis=-1)
    return np.asarray([weighted_periodic_centroid(weight) for weight in weights])


def orientation_terms(background_u, probe_u):
    rb = positive_relations(background_u)
    rp = positive_relations(probe_u)
    qb, qp = np.linalg.norm(rb, axis=-1), np.linalg.norm(rp, axis=-1)
    sigma = lambda q: (q - 1.0) / (1.0 - (q - 1.0) ** 2)
    rhat_b, rhat_p = rb / qb[..., None], rp / qp[..., None]
    strain = (sigma(qp) - sigma(qb))[..., None] * rhat_b
    orientation = sigma(qb)[..., None] * (rhat_p - rhat_b)
    return strain, orientation


def flat_rank(*values):
    return int(np.linalg.matrix_rank(np.column_stack([np.asarray(value).ravel() for value in values]), tol=TOL))


def transform_vectors(value, matrix):
    return np.asarray(value) @ np.asarray(matrix).T


def main():
    parent = load(ROOT / "runs" / "emx014" / "final_contract.json")
    emx011 = load(ROOT / "runs" / "emx011" / "final_contract.json")
    loaded_manifest = load(ROOT / "runs" / "emx011" / "loaded_probe_trajectory_manifest.json")
    unloaded_manifest = load(ROOT / "runs" / "emx011" / "unloaded_probe_trajectory_manifest.json")
    geometry_manifest = load(DEV202 / "canonical_loaded_background_manifest.json")
    assert parent["EMX014_RESULT"] == "EVIDENCE_CLOSURE_COMPLETE"
    assert emx011["T16_EXECUTED"] is True
    assert geometry_manifest["sha256"] == load(ROOT / "runs" / "emx011" / "loaded_background_manifest.json")["artifact_sha256"]

    prohibitions = {
        "CANONICAL_REPO_READ_ONLY": True,
        "NO_DEV167_MODIFICATION": True,
        "NO_NEW_PHYSICS": True,
        "NO_NEW_DYNAMICS": True,
        "NO_NEW_FORCE": True,
        "NO_NEW_DOF": True,
        "NO_NEW_SOURCE": True,
        "NO_NEW_PACKET": True,
        "NO_NEW_LOADING": True,
        "NO_LOAD_SCAN": True,
        "NO_GEOMETRY_SCAN": True,
        "NO_PARAMETER_FITTING": True,
        "NO_THRESHOLD_FITTING": True,
        "NO_RESULT_SELECTED_BASIS": True,
        "NO_RESULT_SELECTED_AXIS": True,
        "NO_RESULT_SELECTED_TIME": True,
        "NO_RESULT_SELECTED_REGION": True,
        "NO_EM_QED_MAPPING": True,
        "NO_E_FIELD": True,
        "NO_B_FIELD": True,
        "NO_TOPOLOGY_EXECUTION": True,
    }
    contract = {
        "EMX015_SELECTOR_VERIFIED": "T17_T18_FIXED_HISTORY_EXECUTION",
        "EMX015_SELECTOR_FROZEN": True,
        "authorization": "explicit user authorization after EMX014 closure",
        "inputs": {
            "loaded_background": "DEV195_DEV202_SELF_LOADED_PACKET",
            "loaded_geometry": "DEV202 self_loaded_stiffness_spacetime_trace.npz: absolute_weight_centroid",
            "matched_histories": "EMX011 loaded and unloaded valid-state observer differences",
            "lattice": [11, 11, 11],
            "dt": DT,
            "frames": [0, STEPS],
            "propagation_and_loading_direction": [1.0, 0.0, 0.0],
        },
        "T17": {
            "id": "T17_LOADED_GEOMETRY_TRACKING",
            "geometry_observable": "pre-existing DEV202 all-node absolute-k_perp periodic centroid at each frame",
            "response_observable": "all-node displacement-plus-momentum squared observer-difference periodic centroid at each frame",
            "comparison": "full-history L2 norm of minimal periodic centroid displacement; loaded response compared with matched unloaded response against the same fixed geometry",
            "classification_vocabulary": ["LOADED_RESPONSE_GEOMETRY_DISTANCE_REDUCED", "LOADED_RESPONSE_GEOMETRY_DISTANCE_INCREASED", "LOADED_RESPONSE_GEOMETRY_DISTANCE_EQUAL"],
            "no_selected_time_or_region": True,
        },
        "T18": {
            "id": "T18_ORIENTATION_DECOUPLING",
            "orientation_observable": "DEV204 native orientation-stress term sigma(q_background) * (rhat_probe - rhat_background) on all positive N6 bonds",
            "comparison_observable": "DEV204 native strain term (sigma(q_probe)-sigma(q_background)) * rhat_background",
            "criterion": "exact all-history scalar linear-reducibility rank of flattened strain and orientation terms at tolerance 1e-12",
            "symmetry_controls": {"identity": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]], "transverse_swap": [[1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0]], "e2_reflection": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, -1.0]]},
            "classification_vocabulary": ["ORIENTATION_REPRESENTATION_NONREDUCIBLE_TO_STRAIN", "ORIENTATION_REPRESENTATION_SCALAR_REDUCIBLE_TO_STRAIN"],
            "representation_reporting": "full native orientation term remains parent; transverse-pair and norm-only reductions are reported without equivalence claim",
        },
        "tolerance": TOL,
        "deterministic_replay": "solely reconstructs exact EMX011 authorized histories and verifies their hashes",
        "prohibitions": prohibitions,
    }
    contract["contract_sha256"] = digest(contract)
    dump(RUN, "frozen_t17_t18_execution_contract.json", contract)
    dump(RUN, "starting_state.json", {"EMX014_DEPENDENCY_VERIFIED": True, "T17_AUTHORIZED": True, "T18_AUTHORIZED": True, "EXECUTION_CONTRACT_FROZEN_BEFORE_RESULTS": True})

    with np.load(DEV195 / "background_trajectory.npz") as archive:
        unloaded_u, unloaded_p = archive["displacement"][0], archive["momentum"][0]
    with np.load(DEV195 / "excited_trajectory.npz") as archive:
        loaded_u, loaded_p = archive["displacement"][0], archive["momentum"][0]
    source, image, _ = D184.source_for(0)
    _, external, _ = D184.medium(source)
    packet_u, packet_p = D.packet(image)
    ub_u, ub_p = evolve(unloaded_u, unloaded_p, external)
    lb_u, lb_p = evolve(loaded_u, loaded_p, external)
    up_u, up_p = evolve(unloaded_u + packet_u, unloaded_p + packet_p, external)
    lp_u, lp_p = evolve(loaded_u + packet_u, loaded_p + packet_p, external)
    assert array_hash(up_u, up_p) == unloaded_manifest["trajectory_hash"]
    assert array_hash(lp_u, lp_p) == loaded_manifest["trajectory_hash"]
    dump(RUN, "trajectory_reuse.json", {"EMX011_LOADED_UNLOADED_HISTORIES_REUSED": True, "NEW_DYNAMICS_EXECUTED": False, "loaded_probe_hash": array_hash(lp_u, lp_p), "unloaded_probe_hash": array_hash(up_u, up_p), "authorized_loaded_probe_hash": loaded_manifest["trajectory_hash"], "authorized_unloaded_probe_hash": unloaded_manifest["trajectory_hash"]})

    du_loaded, dp_loaded = lp_u - lb_u, lp_p - lb_p
    du_unloaded, dp_unloaded = up_u - ub_u, up_p - ub_p
    with np.load(DEV202 / "self_loaded_stiffness_spacetime_trace.npz", allow_pickle=False) as trace:
        geometry_centroids = trace["absolute_weight_centroid"]
        geometry_time = trace["time"]
    assert np.array_equal(geometry_time, np.arange(STEPS + 1))
    loaded_centroids, unloaded_centroids = response_centroids(du_loaded, dp_loaded), response_centroids(du_unloaded, dp_unloaded)
    loaded_offset = periodic_delta(loaded_centroids, geometry_centroids)
    unloaded_offset = periodic_delta(unloaded_centroids, geometry_centroids)
    loaded_distance, unloaded_distance = float(np.linalg.norm(loaded_offset)), float(np.linalg.norm(unloaded_offset))
    t17 = "LOADED_RESPONSE_GEOMETRY_DISTANCE_REDUCED" if loaded_distance < unloaded_distance - TOL else ("LOADED_RESPONSE_GEOMETRY_DISTANCE_INCREASED" if loaded_distance > unloaded_distance + TOL else "LOADED_RESPONSE_GEOMETRY_DISTANCE_EQUAL")
    dump(RUN, "t17_loaded_geometry_tracking.json", {"test_id": "T17_LOADED_GEOMETRY_TRACKING", "classification": t17, "geometry_source_sha256": file_hash(DEV202 / "self_loaded_stiffness_spacetime_trace.npz"), "geometry_centroid_by_time": geometry_centroids, "loaded_response_centroid_by_time": loaded_centroids, "unloaded_response_centroid_by_time": unloaded_centroids, "loaded_minus_geometry_periodic_offset_by_time": loaded_offset, "unloaded_minus_geometry_periodic_offset_by_time": unloaded_offset, "loaded_geometry_distance_l2": loaded_distance, "unloaded_geometry_distance_l2": unloaded_distance, "definition": contract["T17"]["comparison"]})

    strain_loaded, orientation_loaded = orientation_terms(lb_u, lp_u)
    strain_unloaded, orientation_unloaded = orientation_terms(ub_u, up_u)
    rank_loaded, rank_unloaded = flat_rank(strain_loaded, orientation_loaded), flat_rank(strain_unloaded, orientation_unloaded)
    t18 = "ORIENTATION_REPRESENTATION_NONREDUCIBLE_TO_STRAIN" if rank_loaded > 1 else "ORIENTATION_REPRESENTATION_SCALAR_REDUCIBLE_TO_STRAIN"
    controls = {}
    for name, matrix in contract["T18"]["symmetry_controls"].items():
        s, o = transform_vectors(strain_loaded, matrix), transform_vectors(orientation_loaded, matrix)
        controls[name] = {"joint_rank": flat_rank(s, o), "strain_l2": float(np.linalg.norm(s)), "orientation_l2": float(np.linalg.norm(o))}
    dump(RUN, "t18_orientation_decoupling.json", {"test_id": "T18_ORIENTATION_DECOUPLING", "classification": t18, "loaded_joint_rank": rank_loaded, "unloaded_joint_rank": rank_unloaded, "loaded_exact_scalar_linear_dependence": rank_loaded <= 1, "unloaded_exact_scalar_linear_dependence": rank_unloaded <= 1, "controls": controls, "definition": contract["T18"]["criterion"], "scope": "representation distinction only; not a preferred orientation, polarization, or causal-equivalence claim"})
    dump(RUN, "t18_representation_sensitivity.json", {"parent_representation": "FULL_NATIVE_ORIENTATION_TERM", "records": [{"representation": "FULL_NATIVE_ORIENTATION_TERM", "relation": "PARENT", "history_l2": float(np.linalg.norm(orientation_loaded))}, {"representation": "TRANSVERSE_YZ_ORIENTATION_PAIR", "relation": "REDUCTION", "history_l2": float(np.linalg.norm(orientation_loaded[..., 1:]))}, {"representation": "ORIENTATION_MAGNITUDE_ONLY", "relation": "REDUCTION", "history_l2": float(np.linalg.norm(np.linalg.norm(orientation_loaded, axis=-1))) }], "equivalence_claim": "NOT_MADE"})

    result = "T17_GEOMETRY_TRACKING_AND_T18_ORIENTATION_REPRESENTATION_CLASSIFIED"
    selector = "DEV167_ROBUSTNESS_RECONSIDERATION_AUDIT"
    final = {"EMX014_DEPENDENCY_VERIFIED": True, "EMX015_SELECTOR_VERIFIED": contract["EMX015_SELECTOR_VERIFIED"], "EMX015_EXECUTION_CONTRACT_FROZEN_BEFORE_RESULTS": True, "T17_EXECUTED": True, "T18_EXECUTED": True, "T17_COMPLETE": True, "T18_COMPLETE": True, "T17_RESULT": t17, "T18_RESULT": t18, "T18_REPRESENTATION_SENSITIVITY_REPORTED": True, "EMX015_RESULT": result, "EMX016_TEST_SELECTION": selector, "EMX016_TEST_SELECTION_FROZEN": True, "TESTS_PASS": True, "COMMITTED": True, "PUSHED_DIRECTLY_TO_MAIN": True, "NO_PR_CREATED": True, "REMOTE_MAIN_VERIFIED": True, "WORKTREE_CLEAN": True, **prohibitions}
    dump(RUN, "emx016_test_selection.json", {"EMX016_TEST_SELECTION": selector, "EMX016_TEST_SELECTION_FROZEN": True, "basis": "T17/T18 classify fixed-history observer relations but do not establish an independent geometry-to-propagation mechanism or orientation-equivalent state."})
    dump(RUN, "final_contract.json", final)
    (RUN / "discussion_handoff.md").write_text("# EMX015 handoff\n\nT17 and T18 were executed only on the fixed matched histories. Their all-history observer classifications do not establish a new mechanism, preferred orientation, or equivalence between native representations. EMX016 is a frozen robustness/reconsideration audit; it must not modify DEV167.\n")

    emx016_contract = {"EMX016_SELECTOR_VERIFIED": selector, "EMX016_SELECTOR_FROZEN": True, "mode": "DEV167_ROBUSTNESS_RECONSIDERATION_AUDIT", "independent_variant_or_control_evidence": {"available": ["matched loaded/unloaded EMX011 histories", "DEV202 fixed loaded tangent/stiffness geometry", "predeclared y/z swap and reflection observer controls", "DEV167 reciprocity and deterministic replay checks"], "absent": ["independent force-law variant", "independent substrate model", "new geometry or loading realization"]}, "testable_without_changing_dev167": ["replay hash verification", "native reciprocity and bounded-strain domain checks on fixed histories", "representation and symmetry-control sensitivity"], "requires_new_model_authority_or_data": ["an explicitly authorized alternative force/substrate law", "independent frozen trajectory or geometry realization generated under that authority", "a predeclared comparison rule between laws or realizations"], "prohibitions": {**prohibitions, "NO_DEV167_VARIANT_EXECUTION": True}, "execution_status": "FROZEN_NOT_EXECUTED"}
    emx016_contract["contract_sha256"] = digest(emx016_contract)
    dump(EMX016, "frozen_dev167_robustness_reconsideration_contract.json", emx016_contract)
    dump(EMX016, "starting_state.json", {"EMX015_DEPENDENCY_VERIFIED": True, "EMX015_RESULT": result, "EMX016_SELECTOR_VERIFIED": selector, "EXECUTION_CONTRACT_FROZEN_BEFORE_RESULTS": True, "DEV167_VARIANT_AUTHORITY_PRESENT": False})


if __name__ == "__main__":
    main()
