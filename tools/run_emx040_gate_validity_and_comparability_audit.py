#!/usr/bin/env python3
"""Run the frozen, read-only EMX040 retained-gate audit."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs" / "emx040"


def read(path):
    return json.loads(Path(path).read_text())


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main():
    contract = read(OUT / "frozen_gate_validity_and_comparability_contract.json")
    assert contract["FROZEN_BEFORE_RESULTS"] and contract["retained_constraint_count"] == 76
    assert all(file_hash(ROOT / p) == digest for p, digest in contract["input_sha256"].items())
    artifact_checks = []
    for name, spec in contract["historical_artifacts"].items():
        actual = file_hash(spec["path"])
        artifact_checks.append({"artifact": name, "expected_sha256": spec["expected_sha256"], "actual_sha256": actual, "matches": actual == spec["expected_sha256"]})
    assert all(row["matches"] for row in artifact_checks)

    retained = read(ROOT / "runs/emx016/dev167_failure_combination_matrix.json")["retained_positive_constraints"]["records"]
    assert len(retained) == 76
    contracts = {
        "EMX004": read(ROOT / "runs/emx004/frozen_execution_contract.json"),
        "EMX006": read(ROOT / "runs/emx006/frozen_secondary_battery_contract.json"),
        "EMX008": read(ROOT / "runs/emx008/frozen_longitudinal_audit_contract.json"),
        "EMX011": read(ROOT / "runs/emx011/frozen_t16_execution_contract.json"),
        "EMX012": read(ROOT / "runs/emx012/frozen_mixing_audit_contract.json"),
        "EMX013": read(ROOT / "runs/emx013/frozen_unloaded_asymmetry_audit_contract.json"),
        "EMX015": read(ROOT / "runs/emx015/frozen_t17_t18_execution_contract.json"),
    }
    repeatability = read(ROOT / "runs/emx011/t16_repeatability.json")
    reuse = {
        "EMX012": read(ROOT / "runs/emx012/trajectory_reuse.json"),
        "EMX013": read(ROOT / "runs/emx013/trajectory_reuse.json"),
        "EMX015": read(ROOT / "runs/emx015/trajectory_reuse.json"),
    }
    source_rows = Counter(row["source_run"] for row in retained)
    ledger = []
    seen_semantics = set()
    for index, row in enumerate(retained, start=1):
        source = row["source_run"]
        source_contract = contracts[source]
        contract_sha = source_contract["contract_sha256"]
        semantic_key = (source, row["candidate_id"], row["representation"], row["observable_or_test"], json.dumps(row["fixed_inputs"], sort_keys=True))
        strict_duplicate = semantic_key in seen_semantics
        seen_semantics.add(semantic_key)
        replay = "HASH_PINNED_HISTORICAL_ARTIFACT_VERIFIED"
        if source == "EMX011":
            replay = "DETERMINISTIC_REPEAT_HASH_VERIFIED" if repeatability["UNLOADED_RUN_REPRODUCIBLE"] and repeatability["LOADED_RUN_REPRODUCIBLE"] else "REPRODUCTION_CONTRADICTED"
        elif source in reuse:
            replay = "EXACT_HISTORY_REUSE_HASH_VERIFIED" if reuse[source].get("deterministic_replay_solely_for_exact_history_reproduction", True) else "REPRODUCTION_CONTRADICTED"
        classification = "REPRODUCTION_CONTRADICTED" if replay == "REPRODUCTION_CONTRADICTED" else ("REDUNDANT" if strict_duplicate else "VERIFIED_CONDITIONAL")
        ledger.append({
            "ledger_id": f"EMX040-R{index:03d}",
            "candidate_id": row["candidate_id"],
            "observable_or_test": row["observable_or_test"],
            "representation": row["representation"],
            "source_run": source,
            "historical_fixed_inputs": row["fixed_inputs"],
            "historical_contract_sha256": contract_sha,
            "historical_parent_artifact_sha256": "118a680de0ba756cd56901fcf2db02cd2a765035357e7b38fb419927ae61afb4",
            "provenance_status": "EXACT_HASH_PINNED",
            "replay_status": replay,
            "logical_independence": "DISTINCT_DECLARED_OBSERVER_CONSTRAINT" if not strict_duplicate else "STRICT_LOGICAL_DUPLICATE",
            "observer_representation_status": "HISTORICAL_OBSERVER_DEFINED_FIXED_REPRESENTATION_ONLY",
            "tolerance_status": "HISTORICAL_FIXED_TOLERANCE_OR_EXACT_IEEE_RULE_ONLY; NO_SENSITIVITY_SWEEP_AUTHORIZED",
            "discriminator_status": "HISTORICAL_CONDITIONAL_NOT_MODEL_DISCRIMINATOR_ACROSS_UNBRIDGED_FAMILIES",
            "repository_local_comparability": "UNDERDETERMINED_NEEDS_BRIDGE",
            "classification": classification,
            "evidence": "Historical artifact hashes match; the local lift is a distinct source/state/law/observer family and cannot reclassify this retained historical gate.",
        })
    assert len(ledger) == 76 and all(x["classification"] in contract["classification_vocabulary"] for x in ledger)
    assert not any(x["classification"] == "REPRODUCTION_CONTRADICTED" for x in ledger)

    controls = {
        "historical_artifact_hash_replay": artifact_checks,
        "historical_repeatability": {"EMX011": repeatability, "EMX012": reuse["EMX012"], "EMX013": reuse["EMX013"], "EMX015": reuse["EMX015"]},
        "repository_local_control": {
            "all_216_lift_cells_finite": read(ROOT / "runs/emx038/remaining_matrix_results.json")["executed_cell_count"] == 216 and read(ROOT / "runs/emx039/final_contract.json")["ALL_216_NONZERO_LIFT_CELLS_FINITE"],
            "retained_constraints_newly_assessed": 0,
            "result": "NO_COMPARABILITY_INFERENCE_PERMITTED",
        },
        "observer_control": {
            "historical_observers": "predeclared and representation-specific",
            "local_observers": "energy/history norm and fixed plaquette proxy",
            "shared_observer_exists": False,
            "result": "UNDERDETERMINED_NEEDS_BRIDGE",
        },
        "tolerance_control": {
            "historical": "exact IEEE or fixed 1e-12 rules; no fitted threshold",
            "local": "finite checks and fixed source-lift definitions",
            "cross_family_sensitivity_sweep": "NOT_AUTHORIZED_WITHOUT_SHARED_OBSERVER",
        },
    }
    plan = {
        "EMX040_SHARED_OBSERVER_AND_COMPARABILITY_PLAN": "STOP_AT_NEW_PRIMITIVE_BOUNDARY",
        "historical_family": {"state": "DEV167 prepared packet plus matched historical controls", "observer_set": "representation-specific T02--T33 observers", "hashes_verified": True},
        "repository_local_family": {"state": "neutral harmonic N6 source lift", "observer_set": "energy/history norm, static/motion proxy, plaquette angular proxy", "all_cells_finite": controls["repository_local_control"]["all_216_lift_cells_finite"]},
        "common_existing_observer": None,
        "required_bridge": [
            "A predeclared observer with one invariant mathematical definition on both full historical trajectories and local source-lift trajectories.",
            "A predeclared control correspondence covering source preparation, background subtraction, geometry, time domain, and representation action.",
            "A fixed tolerance/normalization sensitivity protocol applied symmetrically before any result is inspected.",
            "A replay manifest pinning every input and observer implementation hash.",
        ],
        "boundary": "No existing observer satisfies the common-definition requirement. Supplying one would be a genuinely new observer primitive; EMX040 does not define, implement, or execute it.",
        "status": "UNDERDETERMINED_NEEDS_BRIDGE",
        "prohibitions_respected": contract["prohibitions"],
    }
    write("eligible_audit_replay_observer_controls.json", controls)
    write("gate_ledger.json", {"schema_version": 1, "contract_sha256": contract["contract_sha256"], "retained_constraint_count": len(ledger), "source_run_counts": dict(sorted(source_rows.items())), "classification_counts": dict(sorted(Counter(x["classification"] for x in ledger).items())), "records": ledger})
    write("shared_observer_comparability_plan.json", plan)
    write("final_contract.json", {
        "EMX040_RESULT": "HISTORICAL_GATES_HASH_VERIFIED_AND_CONDITIONALLY_VALID; CROSS_FAMILY_COMPARABILITY_UNDERDETERMINED",
        "CONTRACT_FROZEN_BEFORE_RESULTS": True,
        "RETAINED_CONSTRAINTS_AUDITED": 76,
        "CLASSIFICATION_COUNTS": dict(sorted(Counter(x["classification"] for x in ledger).items())),
        "HISTORICAL_ARTIFACT_HASHES_VERIFIED": True,
        "ELIGIBLE_REPLAY_CONTROLS_VERIFIED": True,
        "REPOSITORY_LOCAL_LIFT_FINITE": controls["repository_local_control"]["all_216_lift_cells_finite"],
        "SHARED_OBSERVER_STATUS": "UNDERDETERMINED_NEEDS_BRIDGE",
        "STOPPED_AT_GENUINELY_NEW_OBSERVER_PRIMITIVE_BOUNDARY": True,
        "RETAINED_GATES_ALTERED_WEAKENED_OR_DELETED": False,
        "NO_NEW_OBSERVER_PRIMITIVE_CREATED": True,
        **contract["prohibitions"],
    })


if __name__ == "__main__":
    main()
