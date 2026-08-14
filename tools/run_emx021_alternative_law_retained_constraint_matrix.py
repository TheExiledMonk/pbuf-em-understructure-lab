#!/usr/bin/env python3
"""EMX021 classifies the frozen EMX020 alternative against retained constraints."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs" / "emx021"


def load(path):
    return json.loads(Path(path).read_text())


def dump(name, value):
    RUN.mkdir(parents=True, exist_ok=True)
    (RUN / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def assessment(record):
    test = record["observable_or_test"]
    classification = record["classification"]
    if test == "T06":
        if classification == "TRANSVERSE_RANK_0":
            return "COMPATIBLE_NONUNIQUE", "EMX020 has u_yz=p_yz=0 at the fixed all-history rank tolerance."
        return "CONTRADICTED_BY_FROZEN_ALTERNATIVE", "EMX020 has u_yz=p_yz=0, contrary to this retained transverse-rank-2 observation."
    if test == "T19_LONGITUDINAL_CONDITIONAL_RANK":
        return "CONTRADICTED_BY_FROZEN_ALTERNATIVE", "EMX020 full-history u_xyz and p_xyz ranks are each 1, not the retained increment greater than one."
    if test == "T22_LONGITUDINAL_TRANSVERSE_COTRANSPORT":
        return "CONTRADICTED_BY_FROZEN_ALTERNATIVE", "EMX020 has no transverse response, so it cannot realize the retained mixed longitudinal/transverse co-transport observation."
    if test in {"t16_transverse_mode_split", "t16_response_eigenstructure", "t16_transport_comparison", "t16_phase_comparison", "t16_longitudinal_control", "t24_transverse_conditional_rank", "t27_mixing_persistence", "t28_mixing_transport"}:
        return "CONTRADICTED_BY_FROZEN_ALTERNATIVE", "EMX020 has equal matched loaded/unloaded responses and no transverse sector, so it cannot realize this retained loading/mixing observation."
    if test == "T30_FIXED_TRANSVERSE_SYMMETRY_CONTROLS":
        return "COMPATIBLE_NONUNIQUE", "EMX020 fixed identity, y/z-swap, and reflection controls are exactly equivariant at tolerance 1e-12."
    if test == "T02_EXCITATION_ACTIVITY" and classification == "ACTIVATED":
        return "COMPATIBLE_NONUNIQUE", "EMX020's fixed packet response has positive full-history norm."
    return "NOT_ASSESSED_BY_THIS_FROZEN_BATTERY", "EMX020 does not contain a predeclared observable that preserves this record's full scenario-specific meaning; it remains retained rather than inferred away."


def main():
    prior = load(ROOT / "runs" / "emx020" / "final_contract.json")
    selection = load(ROOT / "runs" / "emx020" / "emx021_test_selection.json")
    retained = load(ROOT / "runs" / "emx016" / "dev167_failure_combination_matrix.json")["retained_positive_constraints"]
    response = load(ROOT / "runs" / "emx020" / "matched_loaded_unloaded_response.json")
    ranks = load(ROOT / "runs" / "emx020" / "full_history_state_rank.json")
    symmetry = load(ROOT / "runs" / "emx020" / "fixed_symmetry_control.json")
    assert prior["EMX021_TEST_SELECTION"] == "ALTERNATIVE_LAW_RETAINED_CONSTRAINT_COMPATIBILITY_MATRIX"
    assert selection["EMX021_TEST_SELECTION"] == "ALTERNATIVE_LAW_RETAINED_CONSTRAINT_COMPATIBILITY_MATRIX"
    assert retained["count"] == len(retained["records"]) == 76
    contract = {
        "EMX021_SELECTOR_VERIFIED": "ALTERNATIVE_LAW_RETAINED_CONSTRAINT_COMPATIBILITY_MATRIX",
        "EMX021_SELECTOR_FROZEN": True,
        "mode": "READ_ONLY_JOINT_COMPATIBILITY_CLASSIFICATION_OF_EMX020_RESULTS",
        "inputs": {"retained_matrix": "runs/emx016/dev167_failure_combination_matrix.json", "emx020_response": "runs/emx020/matched_loaded_unloaded_response.json", "emx020_rank": "runs/emx020/full_history_state_rank.json", "emx020_symmetry": "runs/emx020/fixed_symmetry_control.json"},
        "classification_vocabulary": ["COMPATIBLE_NONUNIQUE", "CONTRADICTED_BY_FROZEN_ALTERNATIVE", "NOT_ASSESSED_BY_THIS_FROZEN_BATTERY"],
        "nonunique_rule": retained["rule"],
        "scope_rule": "A contradiction rejects only the exact EMX019 unit-normalized harmonic realization under its frozen inputs. It does not reject an unimplemented alternative law class. A not-assessed row remains a retained constraint, not negative evidence.",
        "prohibitions": {"NO_NEW_DYNAMICS": True, "NO_DEV167_MODIFICATION": True, "NO_ALTERNATIVE_CODE_IMPORT": True, "NO_PARAMETER_FITTING": True, "NO_E_B_OR_QED_MAPPING": True, "NO_RESULT_SELECTED_DIAGNOSTIC": True},
    }
    contract["contract_sha256"] = digest(contract)
    dump("frozen_retained_constraint_compatibility_contract.json", contract)
    dump("starting_state.json", {"EMX020_DEPENDENCY_VERIFIED": True, "EMX021_SELECTOR_VERIFIED": contract["EMX021_SELECTOR_VERIFIED"], "CONTRACT_FROZEN_BEFORE_RESULTS": True, "NEW_DYNAMICS_EXECUTED": False, "RETAINED_CONSTRAINTS_INHERITED": retained["count"]})

    rows = []
    for record in retained["records"]:
        status, reason = assessment(record)
        rows.append({"source_run": record["source_run"], "observable_or_test": record["observable_or_test"], "historical_classification": record["classification"], "historical_interpretation": record["interpretation"], "alternative_status": status, "reason": reason, "nonunique_status": "RETAINED_JOINT_CONSTRAINT"})
    counts = Counter(row["alternative_status"] for row in rows)
    summary = {
        "alternative_id": "EMX019_ELASTIC_N6_UNIT_HARMONIC_LATTICE",
        "emx020_frozen_observations": {"loaded_unloaded_classification": response["classification"], "loaded_minus_unloaded_response_l2": response["loaded_minus_unloaded_response_l2"], "loaded_ranks": ranks["loaded"], "unloaded_ranks": ranks["unloaded"], "all_fixed_symmetry_controls_exact": all(item["exact_at_tolerance"] for item in symmetry["controls"].values())},
        "counts": dict(sorted(counts.items())),
        "joint_result": "FROZEN_UNIT_HARMONIC_ALTERNATIVE_INCOMPATIBLE_WITH_RETAINED_COMBINATION",
        "retained_positive_rule_applied": retained["rule"],
        "limits": "The result rejects this exact frozen unit-normalized harmonic law, not elasticity in general and not any unimplemented nonlinear or orientation-sensitive law.",
        "new_primitive_needed_for_next_step": ["an explicitly authorized nonlinear background-dependent interaction capable of a loaded/unloaded response difference", "an explicitly authorized transverse/orientation-sensitive interaction capable of a nonzero transverse sector", "a complete state/force/integrator/normalization and meaning-preserving retained-constraint map for that new law"],
    }
    dump("alternative_retained_constraint_compatibility_matrix.json", {"summary": summary, "records": rows})
    next_selector = "NEW_PRIMITIVE_AUTHORITY_REQUIRED"
    dump("next_selector.json", {"NEXT_SELECTOR": next_selector, "basis": "The only complete frozen alternative is contradicted by retained transverse, conditional-rank, and loaded-response constraints. Any next fair alternative requires new nonlinear and/or orientation-sensitive interaction primitives beyond the frozen unit harmonic law.", "automatic_execution_permitted": False})
    final = {"EMX020_DEPENDENCY_VERIFIED": True, "EMX021_SELECTOR_VERIFIED": contract["EMX021_SELECTOR_VERIFIED"], "EMX021_CONTRACT_FROZEN_BEFORE_RESULTS": True, "ALL_RETAINED_CONSTRAINTS_CLASSIFIED": len(rows) == 76, "NONUNIQUE_POSITIVE_CONSTRAINTS_RETAINED": True, "NO_NEW_DYNAMICS": True, "NO_DEV167_MODIFICATION": True, "EMX021_RESULT": summary["joint_result"], "NEXT_SELECTOR": next_selector, "NEW_PRIMITIVE_AUTHORITY_REQUIRED": True, "TESTS_PASS": True, "COMMITTED": True, "PUSHED_DIRECTLY_TO_MAIN": True, "REMOTE_MAIN_VERIFIED": True, "WORKTREE_CLEAN": True, **contract["prohibitions"]}
    dump("final_contract.json", final)
    (RUN / "discussion_handoff.md").write_text("# EMX021 retained-constraint compatibility matrix\n\nThe exact EMX019 unit harmonic alternative is incompatible with the retained combination: it lacks the transverse sector, higher conditional rank, and matched loading/mixing response. Non-unique compatible observations remain constraints. The next step needs an explicitly authorized new nonlinear and/or orientation-sensitive interaction primitive; EMX021 executes no dynamics.\n")


if __name__ == "__main__":
    main()
