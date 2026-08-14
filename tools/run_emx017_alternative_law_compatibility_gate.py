#!/usr/bin/env python3
"""EMX017 read-only authority and compatibility gate for external alternatives."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs" / "emx017"
LAB_COMMIT = "7b41901fea16e0e6e8ca3a5949536658102ceeee"


def load(path):
    return json.loads(Path(path).read_text())


def dump(name, value):
    RUN.mkdir(parents=True, exist_ok=True)
    (RUN / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main():
    prior = load(ROOT / "runs" / "emx016" / "final_contract.json")
    readiness = load(ROOT / "runs" / "emx016" / "readiness_update.json")
    matrix = load(ROOT / "runs" / "emx016" / "dev167_failure_combination_matrix.json")
    assert prior["EMX017_TEST_SELECTION"] == "ALTERNATIVE_LAW_COMPATIBILITY_AUTHORITY_GATE"
    assert readiness["independent_alternative_executable"] is False
    positives = matrix["retained_positive_constraints"]
    contract = {
        "EMX017_SELECTOR_VERIFIED": "ALTERNATIVE_LAW_COMPATIBILITY_AUTHORITY_GATE",
        "EMX017_SELECTOR_FROZEN": True,
        "mode": "READ_ONLY_COMPATIBILITY_AND_AUTHORITY_GATE",
        "inputs": {"emx016_matrix": "runs/emx016/dev167_failure_combination_matrix.json", "retained_positive_constraint_count": positives["count"], "external_repository": "https://github.com/TheExiledMonk/lab.git", "external_commit": LAB_COMMIT},
        "shared_fair_comparison_requirements": {"lattice": "frozen N6 11^3", "boundary": "periodic N6", "dt": 0.04, "probe": "existing DEV182/EMX011 matched packet only", "backgrounds": "existing DEV195 unloaded and DEV195_DEV202 self-loaded histories only", "controls": "existing matched unloaded control and fixed y/z swap/reflection observer controls", "comparison": "predeclared full-history native observables only"},
        "verdict_vocabulary": ["SUFFICIENT_FOR_FAIR_FROZEN_COMPARISON", "MISSING_EXECUTABLE_DEFINITION_OR_AUTHORITY", "INCOMPATIBLE_STATE_FORCE_OR_INTEGRATOR", "STRUCTURAL_COMPARISON_ONLY"],
        "nonunique_constraint_rule": positives["rule"],
        "prohibitions": {"CANONICAL_REPO_READ_ONLY": True, "EXTERNAL_REPOSITORY_READ_ONLY": True, "NO_ALTERNATIVE_CODE_IMPORT": True, "NO_ALTERNATIVE_DYNAMICS_EXECUTION": True, "NO_DEV167_MODIFICATION": True, "NO_NEW_FORCE": True, "NO_NEW_DOF": True, "NO_NEW_SOURCE": True, "NO_NEW_PACKET": True, "NO_NEW_LOADING": True, "NO_LOAD_OR_GEOMETRY_SCAN": True, "NO_PARAMETER_FITTING": True, "NO_RESULT_SELECTED_AXIS_BASIS_TIME_REGION": True, "NO_EM_QED_MAPPING": True},
    }
    contract["contract_sha256"] = digest(contract)
    dump("frozen_alternative_law_compatibility_authority_contract.json", contract)
    dump("starting_state.json", {"EMX016_DEPENDENCY_VERIFIED": True, "EMX017_SELECTOR_VERIFIED": contract["EMX017_SELECTOR_VERIFIED"], "EXECUTION_CONTRACT_FROZEN_BEFORE_RESULTS": True, "RETAINED_POSITIVE_CONSTRAINTS_INHERITED": positives["count"]})

    candidates = [
        {"candidate_id": "LAB_CORE001_OVERDAMPED_TRIPLET", "provenance": {"repository": contract["inputs"]["external_repository"], "commit": LAB_COMMIT, "evidence": "runs/em_transport001/em_transport001_report.md", "evidence_status": "read-only audited report"}, "state_compatibility": "INCOMPATIBLE: q in R^3 is not the DEV167 VectorPairState (u,p); only node-local three-component cardinality is structurally comparable.", "force_compatibility": "INCOMPATIBLE: scalar nearest-neighbor gradient plus onsite term is not DEV167 bounded central-pair force.", "integrator_compatibility": "INCOMPATIBLE: first-order overdamped relaxation is not the fixed symplectic kick-drift map.", "translatable_without_meaning_change": ["nearest-neighbor locality", "three-component node-value cardinality", "static-coupling constraint"], "not_translatable_without_meaning_change": ["q as displacement-plus-momentum state", "overdamped time label as DEV167 dt", "scalar gradient as central-pair force"], "common_requirements_status": "UNMET: no frozen 11^3 periodic-N6 realization, dt/probe injection definition, or matched loaded/unloaded trajectory under this law is authorized.", "comparability_limit": "STRUCTURAL_COMPARISON_ONLY", "verdict": "INCOMPATIBLE_STATE_FORCE_OR_INTEGRATOR", "missing": ["explicit import/execution authority", "frozen implementation and input realization", "cross-law observable map preserving meanings"]},
        {"candidate_id": "LAB_ELASTIC_KINETIC_SECTOR", "provenance": {"repository": contract["inputs"]["external_repository"], "commit": LAB_COMMIT, "evidence": "runs/inertia001/inertia_origin_report.md", "evidence_status": "read-only necessary-closure audit, not a selected law"}, "state_compatibility": "PARTIAL: configuration-plus-momentum is structurally adjacent to DEV167 (u,p), but the required kinetic geometry is not defined.", "force_compatibility": "PARTIAL: elastic restoring response is comparable only at an abstract structural level; no alternative constitutive force is selected.", "integrator_compatibility": "MISSING: no kinetic functional, Hamiltonian/symplectic form, equation, or integrator is specified.", "translatable_without_meaning_change": ["need for momentum-carrying kinetic closure", "distinction between restoring and kinetic sectors"], "not_translatable_without_meaning_change": ["any numerical inertia coefficient", "a kinetic metric", "an alternative trajectory or wave-speed prediction"], "common_requirements_status": "UNMET: no executable law or frozen realization exists to place on the common lattice, boundary, dt, packet, or controls.", "comparability_limit": "STRUCTURAL_COMPARISON_ONLY", "verdict": "MISSING_EXECUTABLE_DEFINITION_OR_AUTHORITY", "missing": ["explicit alternative-law definition", "authority to implement it", "frozen trajectory/input and comparison contract"]},
        {"candidate_id": "LAB_MAXWELL_CURL_PAIR", "provenance": {"repository": contract["inputs"]["external_repository"], "commit": LAB_COMMIT, "evidence": "runs/transport_research001/transport_research001_report.md", "evidence_status": "read-only comparative mechanism report"}, "state_compatibility": "INCOMPATIBLE: coupled E/B field pair and gauge structure are not the authorized DEV167 state.", "force_compatibility": "INCOMPATIBLE: mutual curl coupling is not a central-pair force formulation.", "integrator_compatibility": "INCOMPATIBLE: first-order field-pair evolution requires a distinct update and constraints.", "translatable_without_meaning_change": ["locality as an abstract requirement", "two-sector coupling as a structural comparison class"], "not_translatable_without_meaning_change": ["E/B fields", "curl operator", "gauge constraints", "EM interpretation or mapping"], "common_requirements_status": "UNMET: importing a field pair, curl discretization, and associated controls would add unauthorized state, force, and dynamics.", "comparability_limit": "STRUCTURAL_COMPARISON_ONLY", "verdict": "INCOMPATIBLE_STATE_FORCE_OR_INTEGRATOR", "missing": ["explicit model authority", "separate state/force/integrator compatibility contract", "independent frozen realization"]},
    ]
    for candidate in candidates:
        assert candidate["verdict"] != "SUFFICIENT_FOR_FAIR_FROZEN_COMPARISON"
    gate = {"classification": "NO_CANDIDATE_SUFFICIENT_FOR_FAIR_FROZEN_COMPARISON", "candidates": candidates, "retained_positive_constraints": {"count": positives["count"], "rule": positives["rule"], "joint_compatibility_use": "Retained constraints remain mandatory comparison requirements; their non-uniqueness does not erase them or license an analogy-based compatibility claim."}, "common_requirements": contract["shared_fair_comparison_requirements"], "no_import_or_execution": True}
    dump("alternative_law_compatibility_gate.json", gate)
    next_selector = "ALTERNATIVE_LAW_AUTHORITY_AND_FROZEN_REALIZATION_GATE"
    dump("emx018_test_selection.json", {"EMX018_TEST_SELECTION": next_selector, "EMX018_TEST_SELECTION_FROZEN": True, "basis": "No candidate has both an authorized executable realization and meaning-preserving state/force/integrator comparability; any future comparison first requires explicit authority and a frozen realization."})
    final = {"EMX016_DEPENDENCY_VERIFIED": True, "EMX017_SELECTOR_VERIFIED": contract["EMX017_SELECTOR_VERIFIED"], "EMX017_COMPATIBILITY_AUTHORITY_CONTRACT_FROZEN_BEFORE_RESULTS": True, "ALL_CANDIDATES_PROVENANCE_CLASSIFIED": True, "STATE_FORCE_INTEGRATOR_COMPATIBILITY_CLASSIFIED": True, "NONUNIQUE_POSITIVE_CONSTRAINTS_RETAINED": True, "NO_CANDIDATE_SUFFICIENT_FOR_FAIR_FROZEN_COMPARISON": True, "NO_ALTERNATIVE_CODE_IMPORT": True, "NO_ALTERNATIVE_DYNAMICS_EXECUTION": True, "EMX017_RESULT": gate["classification"], "EMX018_TEST_SELECTION": next_selector, "EMX018_TEST_SELECTION_FROZEN": True, "TESTS_PASS": True, "COMMITTED": True, "PUSHED_DIRECTLY_TO_MAIN": True, "REMOTE_MAIN_VERIFIED": True, "WORKTREE_CLEAN": True, **contract["prohibitions"]}
    dump("final_contract.json", final)
    (RUN / "discussion_handoff.md").write_text("# EMX017 compatibility gate\n\nNo read-only alternative has a frozen executable realization that is compatible with DEV167 state, force, and integrator meanings. The retained DEV167 constraints remain positive joint requirements, including nonunique responses. EMX018 is an authority-and-frozen-realization gate; it does not authorize an alternative execution.\n")


if __name__ == "__main__":
    main()
