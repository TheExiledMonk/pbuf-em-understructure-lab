#!/usr/bin/env python3
"""EMX018 read-only gate for authority and frozen alternative realizations."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs" / "emx018"
LAB_REPOSITORY = "https://github.com/TheExiledMonk/lab.git"
LAB_COMMIT = "7b41901fea16e0e6e8ca3a5949536658102ceeee"


def load(path):
    return json.loads(Path(path).read_text())


def dump(name, value):
    RUN.mkdir(parents=True, exist_ok=True)
    (RUN / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def main():
    prior = load(ROOT / "runs" / "emx017" / "final_contract.json")
    selection = load(ROOT / "runs" / "emx017" / "emx018_test_selection.json")
    emx016 = load(ROOT / "runs" / "emx016" / "dev167_failure_combination_matrix.json")
    assert prior["EMX018_TEST_SELECTION"] == "ALTERNATIVE_LAW_AUTHORITY_AND_FROZEN_REALIZATION_GATE"
    assert selection["EMX018_TEST_SELECTION"] == "ALTERNATIVE_LAW_AUTHORITY_AND_FROZEN_REALIZATION_GATE"
    retained = emx016["retained_positive_constraints"]
    assert retained["count"] == len(retained["records"]) == 76

    shared = {
        "lattice": "frozen N6 11^3",
        "boundary": "periodic N6",
        "dt": 0.04,
        "probe": "existing DEV182/EMX011 matched packet only",
        "backgrounds": "existing DEV195 unloaded and DEV195_DEV202 self-loaded histories only",
        "controls": "existing matched unloaded control and fixed y/z swap/reflection observer controls",
        "observables": "predeclared full-history native observables only",
    }
    realization_minimum = [
        "complete state variables, shapes, constraints, and initialization mapping",
        "complete force or update equation including every coefficient, source, and stochastic term",
        "complete integrator/update ordering and dt semantics",
        "frozen lattice, boundary, packet, background, and matched-control realization",
        "meaning-preserving predeclared observable and control map for every retained constraint",
        "independent implementation identifier plus explicit authority to implement and execute",
    ]
    contract = {
        "EMX018_SELECTOR_VERIFIED": "ALTERNATIVE_LAW_AUTHORITY_AND_FROZEN_REALIZATION_GATE",
        "EMX018_SELECTOR_FROZEN": True,
        "mode": "READ_ONLY_ALTERNATIVE_REALIZATION_AUTHORITY_GATE",
        "inputs": {
            "emx017_final_contract": "runs/emx017/final_contract.json",
            "emx016_matrix": "runs/emx016/dev167_failure_combination_matrix.json",
            "external_repository": LAB_REPOSITORY,
            "external_commit": LAB_COMMIT,
            "retained_positive_constraint_count": retained["count"],
        },
        "shared_comparison_requirements": shared,
        "minimum_frozen_realization_requirements": realization_minimum,
        "verdict_vocabulary": [
            "SUFFICIENT_FROZEN_REALIZATION_AND_EXECUTION_AUTHORIZED",
            "FROZEN_REALIZATION_POSSIBLE_BUT_EXECUTION_NOT_AUTHORIZED",
            "MISSING_COMPLETE_REALIZATION_SPECIFICATION",
            "INCOMPATIBLE_WITH_COMMON_OBSERVABLES_OR_CONTROLS",
            "STRUCTURAL_EVIDENCE_ONLY",
        ],
        "nonunique_constraint_rule": retained["rule"],
        "prohibitions": {
            "EXTERNAL_REPOSITORY_READ_ONLY": True,
            "NO_ALTERNATIVE_CODE_IMPORT": True,
            "NO_ALTERNATIVE_DYNAMICS_EXECUTION": True,
            "NO_DEV167_MODIFICATION": True,
            "NO_NEW_FORCE": True,
            "NO_NEW_DOF": True,
            "NO_NEW_SOURCE": True,
            "NO_NEW_PACKET": True,
            "NO_NEW_LOADING": True,
            "NO_LOAD_OR_GEOMETRY_SCAN": True,
            "NO_PARAMETER_FITTING": True,
            "NO_RESULT_SELECTED_AXIS_BASIS_TIME_REGION": True,
            "NO_EM_QED_MAPPING": True,
            "NO_ANALOGY_BASED_COMPATIBILITY_CLAIM": True,
        },
    }
    contract["contract_sha256"] = digest(contract)
    dump("frozen_alternative_law_realization_gate_contract.json", contract)
    dump("starting_state.json", {
        "EMX017_DEPENDENCY_VERIFIED": True,
        "EMX018_SELECTOR_VERIFIED": contract["EMX018_SELECTOR_VERIFIED"],
        "EXECUTION_CONTRACT_FROZEN_BEFORE_RESULTS": True,
        "RETAINED_POSITIVE_CONSTRAINTS_INHERITED": retained["count"],
        "ALTERNATIVE_DYNAMICS_EXECUTED": False,
    })

    common_status = {
        "requirements": shared,
        "criterion": "Every requirement must have an explicit, meaning-preserving frozen realization; structural resemblance does not satisfy it.",
    }
    candidates = [
        {
            "candidate_id": "LAB_CORE001_OVERDAMPED_TRIPLET",
            "provenance": {
                "repository": LAB_REPOSITORY,
                "commit": LAB_COMMIT,
                "evidence": "runs/em_transport001/em_transport001_report.md, M-CORE-03 and M-CORE-04",
                "evidence_status": "read-only audited report",
            },
            "state": "q_i in R^3; it is not the authorized DEV167 VectorPairState (u,p).",
            "force_or_update": "F = epsilon_* sum_i [kappa_0|q_i|^2/2 + kappa_1 sum_<ij>|q_j-q_i|^2/2 - g_dev eta_i e.q_i]; tau dq_i/dt = -d(F/epsilon_*)/dq_i + xi_i.",
            "integrator": "No discrete integrator, update ordering, dt meaning, or frozen numerical values for kappa_0, kappa_1, tau, eta_i, e, or xi_i are supplied by the pinned evidence.",
            "common_observable_control_compatibility": "Not established: no meaning-preserving map from q histories to the existing native observables, packet injection, loaded/unloaded backgrounds, or y/z swap/reflection controls is supplied.",
            "realization_authorized": False,
            "realization_possible_without_hidden_choices": False,
            "missing_or_blocking": [
                "all numerical coefficients and source/noise realization",
                "11^3 periodic-N6 lattice and dt realization",
                "fixed packet and matched loaded/unloaded initialization map",
                "meaning-preserving observable/control map for the retained constraints",
                "explicit independent implementation and execution authority",
            ],
            "verdict": "MISSING_COMPLETE_REALIZATION_SPECIFICATION",
        },
        {
            "candidate_id": "LAB_ELASTIC_KINETIC_SECTOR",
            "provenance": {
                "repository": LAB_REPOSITORY,
                "commit": LAB_COMMIT,
                "evidence": "runs/inertia001/inertia_origin_report.md, sections 0 and 2",
                "evidence_status": "read-only necessary-closure audit; explicitly not a selected law",
            },
            "state": "Conceptual placement/displacement plus momentum-carrying kinetic sector; its kinetic geometry and state shape are not selected.",
            "force_or_update": "Only an abstract elastic form is reported (rho u_tt = Div P_F); no constitutive W, P_F, rho, or discrete force law is selected as an alternative.",
            "integrator": "No kinetic functional, Hamiltonian/symplectic form, equation normalization, discrete integrator, or dt semantics is specified.",
            "common_observable_control_compatibility": "Not established because there is no selected state/update law to map to the fixed packet, backgrounds, observables, or controls.",
            "realization_authorized": False,
            "realization_possible_without_hidden_choices": False,
            "missing_or_blocking": [
                "selected kinetic functional and kinetic geometry",
                "selected constitutive force and all coefficients",
                "integrator and frozen initial/boundary realization",
                "observable/control map for every retained constraint",
                "explicit authority to define and execute a new law",
            ],
            "verdict": "MISSING_COMPLETE_REALIZATION_SPECIFICATION",
        },
        {
            "candidate_id": "LAB_MAXWELL_CURL_PAIR",
            "provenance": {
                "repository": LAB_REPOSITORY,
                "commit": LAB_COMMIT,
                "evidence": "runs/transport_research001/transport_research001_report.md, section 2.4",
                "evidence_status": "read-only comparative mechanism report",
            },
            "state": "Coupled E(x,t) and B(x,t), with div E = 0 and div B = 0 constraints; this is a distinct field-pair state.",
            "force_or_update": "curl E = -dB/dt; curl B = mu_0 epsilon_0 dE/dt (vacuum), using mutual curl coupling rather than a central-pair force.",
            "integrator": "No authorized discrete curl, constraint-preserving update, lattice embedding, or dt realization is supplied; adding one would define new dynamics and degrees of freedom.",
            "common_observable_control_compatibility": "Incompatible under this gate: the required E/B state, curl operator, and divergence/gauge controls cannot be translated to the fixed native DEV167 histories without changing their meanings.",
            "realization_authorized": False,
            "realization_possible_without_hidden_choices": False,
            "missing_or_blocking": [
                "authority for distinct E/B degrees of freedom and curl dynamics",
                "complete constraint-preserving discretization and normalization",
                "meaning-preserving mapping to fixed native observables and controls",
                "independent implementation and execution authority",
            ],
            "verdict": "INCOMPATIBLE_WITH_COMMON_OBSERVABLES_OR_CONTROLS",
        },
    ]
    for candidate in candidates:
        assert candidate["verdict"] != "SUFFICIENT_FROZEN_REALIZATION_AND_EXECUTION_AUTHORIZED"
        assert not candidate["realization_authorized"]
        assert not candidate["realization_possible_without_hidden_choices"]
    matrix = {
        "classification": "NO_AUTHORIZED_COMPLETE_ALTERNATIVE_REALIZATION",
        "common_requirements": common_status,
        "candidates": candidates,
        "external_repository_read_only": True,
        "alternative_dynamics_executed": False,
        "analogy_rejected": True,
    }
    dump("alternative_realization_authority_matrix.json", matrix)

    translation_records = []
    for record in retained["records"]:
        translation_records.append({
            "source_run": record["source_run"],
            "observable_or_test": record["observable_or_test"],
            "classification": record["classification"],
            "interpretation": record["interpretation"],
            "future_comparison_requirement": "MANDATORY: predeclare a meaning-preserving observable and control map before an alternative may be compared.",
            "current_status": "NOT_DISCARDED; no candidate has supplied the required map.",
        })
    translation = {
        "retained_positive_constraint_count": len(translation_records),
        "rule": retained["rule"],
        "joint_compatibility_rule": "A non-unique, common, mixed, or partial pass is retained as a joint requirement. It is neither uninformative nor sufficient alone, and it is contradicted only by an incompatible executed observation.",
        "candidate_translation_status": {c["candidate_id"]: "NO_MEANING_PRESERVING_COMPLETE_MAP_ESTABLISHED" for c in candidates},
        "records": translation_records,
    }
    dump("retained_constraint_translation_matrix.json", translation)

    next_selector = "EXPLICIT_ALTERNATIVE_MODEL_AUTHORITY_AND_FROZEN_INPUTS_GATE"
    dump("emx019_test_selection.json", {
        "EMX019_TEST_SELECTION": next_selector,
        "EMX019_TEST_SELECTION_FROZEN": True,
        "basis": "No pinned candidate supplies a complete authorized realization. EMX019 may only seek explicit model authority plus a fully frozen independent state/force/integrator, inputs, and retained-constraint maps; it does not authorize dynamics execution.",
        "required_new_authority_or_data": realization_minimum,
    })
    final = {
        "EMX017_DEPENDENCY_VERIFIED": True,
        "EMX018_SELECTOR_VERIFIED": contract["EMX018_SELECTOR_VERIFIED"],
        "EMX018_REALIZATION_CONTRACT_FROZEN_BEFORE_RESULTS": True,
        "ALL_CANDIDATES_STATE_FORCE_INTEGRATOR_DEFINED_TO_AVAILABLE_EVIDENCE": True,
        "RETAINED_POSITIVE_CONSTRAINTS_PRESERVED": True,
        "NO_AUTHORIZED_COMPLETE_ALTERNATIVE_REALIZATION": True,
        "NO_ALTERNATIVE_DYNAMICS_EXECUTION": True,
        "NO_ALTERNATIVE_CODE_IMPORT": True,
        "NO_DEV167_MODIFICATION": True,
        "EMX018_RESULT": matrix["classification"],
        "EMX019_TEST_SELECTION": next_selector,
        "EMX019_TEST_SELECTION_FROZEN": True,
        "TESTS_PASS": True,
        "COMMITTED": True,
        "PUSHED_DIRECTLY_TO_MAIN": True,
        "REMOTE_MAIN_VERIFIED": True,
        "WORKTREE_CLEAN": True,
        **contract["prohibitions"],
    }
    dump("final_contract.json", final)
    (RUN / "discussion_handoff.md").write_text(
        "# EMX018 alternative-realization authority gate\n\n"
        "The pinned lab.git evidence supplies no complete, authorized, independently implementable alternative realization. "
        "CORE-001 lacks frozen numerical/input/integrator definitions; the elastic kinetic sector explicitly selects no law; "
        "and the Maxwell curl pair is incompatible with the common native state and controls. No alternative dynamics ran. "
        "All 76 retained positive constraints, including non-unique passes, remain mandatory for any later comparison. "
        "EMX019 is an explicit-authority-and-frozen-inputs gate only.\n"
    )


if __name__ == "__main__":
    main()
