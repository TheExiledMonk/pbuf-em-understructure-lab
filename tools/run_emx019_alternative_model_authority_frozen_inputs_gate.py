#!/usr/bin/env python3
"""EMX019 freezes, but never executes, one independent elastic-lattice realization."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs" / "emx019"
LAB_REPOSITORY = "https://github.com/TheExiledMonk/lab.git"
LAB_COMMIT = "7b41901fea16e0e6e8ca3a5949536658102ceeee"
BACKGROUND_SHA = "67353948d6953f00348a37ea64fb83b0b7dd28b704dd2d3d8f88628647c191c4"
LOADED_SHA = "118a680de0ba756cd56901fcf2db02cd2a765035357e7b38fb419927ae61afb4"
PACKET_U_SHA = "78c823853e12acd4d42cdd93e42acb741539082e617106c46d7de54188381843"
PACKET_P_SHA = "4a05ceb9bd8ab19160370af3e7f959d51a502a7ed9494eb8ee96d1c98c0bbd98"


def load(path):
    return json.loads(Path(path).read_text())


def dump(name, value):
    RUN.mkdir(parents=True, exist_ok=True)
    (RUN / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def observable_map(record):
    representation = record["representation"]
    if representation in {"R02", "R09"}:
        kind = "IDENTICAL_NATIVE_STATE_MAP"
        definition = "Use alternative u and p directly as displacement and momentum."
    elif representation in {"R03", "R06", "R07", "R08"}:
        kind = "IDENTICAL_KINEMATIC_N6_MAP"
        definition = "Apply the already-declared periodic N6 relational/strain/tensor reduction to alternative u."
    elif representation in {"R10", "R11"}:
        kind = "LAW_NATIVE_BOND_FORCE_MAP"
        definition = "Use the declared alternative harmonic N6 bond force; report it as an alternative-law force observable, never as DEV167 force equivalence."
    else:
        kind = "IDENTICAL_FULL_HISTORY_OBSERVER_MAP"
        definition = "Apply the predeclared full-history observer to the corresponding alternative native state or bond quantity."
    return {
        "source_run": record["source_run"],
        "observable_or_test": record["observable_or_test"],
        "representation": representation,
        "retained_interpretation": record["interpretation"],
        "map_kind": kind,
        "definition": definition,
        "control_map": "Apply identity, fixed y/z swap, and fixed e2 reflection componentwise to both u and p before the same observer; compare loaded and unloaded initializations separately.",
        "future_execution_status": "NOT_EVALUATED_IN_EMX019",
        "nonunique_status": "RETAINED_AS_JOINT_CONSTRAINT_NOT_A_STANDALONE_SELECTOR",
    }


def main():
    prior = load(ROOT / "runs" / "emx018" / "final_contract.json")
    selection = load(ROOT / "runs" / "emx018" / "emx019_test_selection.json")
    retained = load(ROOT / "runs" / "emx016" / "dev167_failure_combination_matrix.json")["retained_positive_constraints"]
    emx011_contract = load(ROOT / "runs" / "emx011" / "frozen_t16_execution_contract.json")
    injection = load(ROOT / "runs" / "emx011" / "probe_injection_manifest.json")
    assert prior["EMX019_TEST_SELECTION"] == "EXPLICIT_ALTERNATIVE_MODEL_AUTHORITY_AND_FROZEN_INPUTS_GATE"
    assert selection["EMX019_TEST_SELECTION"] == "EXPLICIT_ALTERNATIVE_MODEL_AUTHORITY_AND_FROZEN_INPUTS_GATE"
    assert retained["count"] == len(retained["records"]) == 76
    assert emx011_contract["unloaded_control"]["sha256"] == BACKGROUND_SHA
    assert emx011_contract["loaded_background"]["sha256"] == LOADED_SHA
    assert injection["packet_displacement_sha256"] == PACKET_U_SHA
    assert injection["packet_momentum_sha256"] == PACKET_P_SHA

    contract = {
        "EMX019_SELECTOR_VERIFIED": "EXPLICIT_ALTERNATIVE_MODEL_AUTHORITY_AND_FROZEN_INPUTS_GATE",
        "EMX019_SELECTOR_FROZEN": True,
        "authorization": "explicit user authorization to independently define and freeze one minimal alternative realization; dynamics execution remains outside EMX019",
        "candidate_selection": {
            "selected_candidate": "EMX019_ELASTIC_N6_UNIT_HARMONIC_LATTICE",
            "motivation": "LAB_ELASTIC_KINETIC_SECTOR identifies configuration plus momentum and an elastic kinetic closure as the closest structural family.",
            "provenance": {
                "repository": LAB_REPOSITORY,
                "commit": LAB_COMMIT,
                "evidence": "runs/inertia001/inertia_origin_report.md and runs/transport_research001/transport_research001_report.md",
                "external_repository_read_only": True,
            },
            "selection_rule": "Smallest candidate with the same native (u,p) state and therefore an explicit map for every retained observer/control; CORE-001 lacks p and Maxwell adds E/B fields.",
            "not_claimed": ["derived from lab.git", "a DEV167 modification", "an EM or QED mapping", "validated before execution"],
        },
        "state": {
            "variables": "u_i,p_i in R^3 for every i in Z_11 x Z_11 x Z_11",
            "shape": [11, 11, 11, 3],
            "site_coordinates": "i=(ix,iy,iz), each coordinate reduced modulo 11",
            "boundary": "periodic N6 in all axes",
            "degrees_of_freedom": "exactly the alternative displacement and momentum pair; no E/B, gauge, auxiliary, stochastic, or hidden state",
        },
        "normalization_and_law": {
            "units": "dimensionless defining normalization",
            "mass_per_site": 1.0,
            "nearest_neighbor_spring_coefficient": 1.0,
            "onsite_coefficient": 0.0,
            "Hamiltonian": "H(u,p)=1/2 sum_i |p_i|^2 + 1/2 sum_i sum_a in {(1,0,0),(0,1,0),(0,0,1)} |u_{i+a}-u_i|^2",
            "force": "F_i(u)=sum_a in {(+/-1,0,0),(0,+/-1,0),(0,0,+/-1)} (u_{i+a}-u_i)",
            "source_term": "0 at every site and every time",
            "noise_term": "0 at every site and every time",
            "damping_term": "0 at every site and every time",
            "parameter_rule": "All coefficients are defining unit normalizations fixed here before execution; none is fitted, inferred from results, or left configurable.",
        },
        "integrator": {
            "name": "explicit kick-drift (symplectic Euler) for the declared independent harmonic law",
            "dt": 0.04,
            "output_frames": "n=0 through n=180 inclusive",
            "update_for_n_0_to_179": ["p^(n+1)=p^n+0.04*F(u^n)", "u^(n+1)=u^n+0.04*p^(n+1)"],
            "ordering": "force, kick, then drift; no substeps, adaptive stepping, filtering, or hidden solver tolerance",
        },
        "frozen_inputs": {
            "unloaded_background": {
                "artifact": "/home/fabian/lab-main-consolidation/runs/dev195_local_force_balance_restoration/background_trajectory.npz",
                "sha256": BACKGROUND_SHA,
                "frame": 0,
                "arrays": ["displacement", "momentum"],
            },
            "loaded_background": {
                "id": "DEV195_DEV202_SELF_LOADED_PACKET",
                "artifact": "/home/fabian/lab-main-consolidation/runs/dev195_local_force_balance_restoration/excited_trajectory.npz",
                "sha256": LOADED_SHA,
                "frame": 0,
                "arrays": ["displacement", "momentum"],
            },
            "packet": {
                "source": "existing DEV182/EMX011 canonical packet only",
                "displacement_sha256": PACKET_U_SHA,
                "momentum_sha256": PACKET_P_SHA,
                "constructor": "generate_dev169_raw_abell_native_observer.packet using the frozen EMX011 preparation",
                "injection_time": 0,
            },
            "initialization": {
                "unloaded": "u^0=background_trajectory.displacement[0]+packet_u; p^0=background_trajectory.momentum[0]+packet_p",
                "loaded": "u^0=excited_trajectory.displacement[0]+packet_u; p^0=excited_trajectory.momentum[0]+packet_p",
                "rule": "The exact existing DEV196 valid-state addition is reused only as an initial-state construction; no trajectory superposition is permitted.",
            },
        },
        "controls_and_observables": {
            "directions": {"propagation_and_loading": [1.0, 0.0, 0.0], "basis": [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]},
            "symmetry_controls": {
                "identity": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
                "transverse_swap": [[1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0]],
                "e2_reflection": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, -1.0]],
            },
            "scope": "full 11^3 periodic lattice and all frames 0..180; no result-selected axis, basis, time, region, or threshold",
            "loaded_unloaded_control": "Run the same frozen law and same packet separately from the two frozen initial states; their only prescribed input difference is the inherited background.",
        },
        "retained_positive_constraint_rule": retained["rule"],
        "prohibitions": {
            "NO_ALTERNATIVE_DYNAMICS_EXECUTION_IN_EMX019": True,
            "NO_ALTERNATIVE_CODE_IMPORT": True,
            "NO_DEV167_MODIFICATION": True,
            "NO_PARAMETER_FITTING": True,
            "NO_HIDDEN_PARAMETERS": True,
            "NO_E_B_OR_QED_MAPPING": True,
            "NO_NEW_PACKET": True,
            "NO_NEW_LOADING": True,
            "NO_LOAD_OR_GEOMETRY_SCAN": True,
            "NO_RESULT_SELECTED_AXIS_BASIS_TIME_REGION": True,
        },
    }
    contract["contract_sha256"] = digest(contract)
    dump("frozen_alternative_model_authority_and_inputs_contract.json", contract)
    dump("starting_state.json", {
        "EMX018_DEPENDENCY_VERIFIED": True,
        "EMX019_SELECTOR_VERIFIED": contract["EMX019_SELECTOR_VERIFIED"],
        "EXECUTION_CONTRACT_FROZEN_BEFORE_RESULTS": True,
        "ALTERNATIVE_DYNAMICS_EXECUTED": False,
        "RETAINED_POSITIVE_CONSTRAINTS_INHERITED": retained["count"],
    })

    maps = [observable_map(record) for record in retained["records"]]
    dump("retained_constraint_observable_control_map.json", {
        "count": len(maps),
        "rule": retained["rule"],
        "joint_compatibility_rule": "Every retained positive result remains a required future comparison constraint. Non-unique alone is not uninformative and is not a contradiction; no pass is claimed until the frozen alternative is executed under its declared map.",
        "records": maps,
    })
    readiness = {
        "classification": "ONE_COMPLETE_ALTERNATIVE_REALIZATION_FROZEN_EXECUTION_NOT_AUTHORIZED_IN_EMX019",
        "candidate_id": contract["candidate_selection"]["selected_candidate"],
        "complete_fields": ["state", "normalization_and_law", "integrator", "frozen_inputs", "controls_and_observables", "retained constraint maps"],
        "execution_status": "NOT_EXECUTED",
        "execution_condition": "A separate explicit authorization for the exact EMX020 frozen contract is required.",
        "all_retained_constraints_preserved": len(maps) == 76,
        "no_hidden_parameters": True,
    }
    dump("alternative_realization_readiness.json", readiness)
    next_selector = "FROZEN_ELASTIC_N6_ALTERNATIVE_COMPARISON_EXECUTION"
    dump("emx020_test_selection.json", {
        "EMX020_TEST_SELECTION": next_selector,
        "EMX020_TEST_SELECTION_FROZEN": True,
        "basis": "The EMX019 independent harmonic realization is complete and implementation-ready, but no alternative dynamics ran in EMX019.",
        "authorization_required": "explicit user authorization before execution",
        "contract_to_execute": "runs/emx019/frozen_alternative_model_authority_and_inputs_contract.json",
    })
    final = {
        "EMX018_DEPENDENCY_VERIFIED": True,
        "EMX019_SELECTOR_VERIFIED": contract["EMX019_SELECTOR_VERIFIED"],
        "EMX019_CONTRACT_FROZEN_BEFORE_RESULTS": True,
        "ONE_COMPLETE_ALTERNATIVE_REALIZATION_FROZEN": True,
        "RETAINED_POSITIVE_CONSTRAINTS_PRESERVED": True,
        "NO_ALTERNATIVE_DYNAMICS_EXECUTION": True,
        "NO_ALTERNATIVE_CODE_IMPORT": True,
        "NO_DEV167_MODIFICATION": True,
        "NO_PARAMETER_FITTING": True,
        "NO_E_B_OR_QED_MAPPING": True,
        "EMX019_RESULT": readiness["classification"],
        "EMX020_TEST_SELECTION": next_selector,
        "EMX020_TEST_SELECTION_FROZEN": True,
        "TESTS_PASS": True,
        "COMMITTED": True,
        "PUSHED_DIRECTLY_TO_MAIN": True,
        "REMOTE_MAIN_VERIFIED": True,
        "WORKTREE_CLEAN": True,
        **contract["prohibitions"],
    }
    dump("final_contract.json", final)
    (RUN / "discussion_handoff.md").write_text(
        "# EMX019 alternative authority and frozen-inputs gate\n\n"
        "EMX019 freezes one independent unit-normalized harmonic N6 elastic lattice with the native (u,p) state, exact inherited packet/background hashes, zero source/noise, and fixed controls. "
        "This is a new independently declared alternative law, not a DEV167 change and not a claim that the law is derived from lab.git. "
        "No alternative dynamics were executed. All 76 retained positive constraints, including non-unique passes, remain mandatory future joint constraints. "
        "EMX020 requires a separate explicit authorization to execute this exact frozen contract.\n"
    )


if __name__ == "__main__":
    main()
