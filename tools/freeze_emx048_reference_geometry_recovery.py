#!/usr/bin/env python3
"""Freeze a read-only, history-wide EMX048 provenance corpus."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs" / "emx048"


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, text=True, capture_output=True).stdout


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    head = git("rev-parse", "HEAD").strip()
    commits = git("rev-list", "--topo-order", head).splitlines()
    paths = sorted({p for commit in commits for p in git("ls-tree", "-r", "--name-only", commit).splitlines()
                    if p.endswith(".json") and p.startswith(("matrix/", "runs/", "provenance/"))})
    corpus = {"head": head, "commits": commits, "eligible_json_paths": paths}
    known = json.loads((ROOT / "runs/emx047/frozen_historical_packet_shape_dynamics_contract.json").read_text())
    contract = {
        "EMX048_SELECTOR": "HASH_PINNED_DEV167_REFERENCE_GEOMETRY_AND_SOURCE_HISTORY_RECOVERY",
        "FROZEN_BEFORE_RESULTS": True,
        "allowed_corpus": {
            "mode": "read-only Git history reachable from frozen main HEAD",
            "head": head,
            "commit_count": len(commits),
            "eligible_paths": paths,
            "manifest_sha256": digest(corpus),
            "excluded": ["untracked files", "external paths", "lab.git", "DEV167 modifications", "tools/tests as evidence"],
        },
        "known_parent_artifacts": known["external_recovered_state_sha256"],
        "required_schema": {
            "directed_reference_geometry": "hash-pinned directed N6 reference/rest-relation vectors, shape [11,11,11,6,3] or an equivalent fully specified indexed representation",
            "source_history_mapping": "hash-pinned deterministic per-step mapping from prepared original packet to the historical force/update source input, including duration and initialization",
            "identity_reproduction": "hash-pinned historical initial u,p and target trajectory plus update, dt, boundary, and tolerance sufficient to reproduce the identity packet",
            "parent_linkage": "explicit link to both known excited/background parent hashes or their exact delta identity",
        },
        "candidate_predicate": "A tracked matrix/, runs/, or provenance/ JSON blob whose parsed text contains DEV167, DEV195_CANONICAL_PACKET_PARENT, a known parent SHA256, or one of geometry/source_history/reference/relation terms. Each unique path/blob pair is audited once with all commits that contain it.",
        "recovery_predicates": {
            "hash_verified": "all required byte SHA256 values are explicit and agree with known parent linkage where applicable",
            "reproducible": "a repository-local execution of the supplied historical update reproduces the archived identity trajectory within 1e-12 max absolute observer difference",
            "fail_closed": "absence of any required field forbids a recovered classification and EMX049 contract",
        },
        "sha256_procedure": "SHA256 is computed over exact Git blob bytes; JSON structure is only inspected after that digest is recorded.",
        "classification_vocabulary": ["RECOVERED_HASH_VERIFIED_AND_REPRODUCED", "RECOVERED_HASH_VERIFIED_NOT_REPRODUCED", "INCOMPLETE_PROVENANCE", "CONTRADICTORY_PROVENANCE", "NOT_PRESENT_IN_ALLOWED_CORPUS"],
        "prohibitions": {"NO_DEV167_MODIFICATION": True, "NO_LAB_GIT_MODIFICATION": True, "NO_LAB_GIT_IMPORT": True, "NO_EXTERNAL_CODE": True, "NO_FITTING_OR_HISTORICAL_RECONSTRUCTION": True, "NO_HIDDEN_OR_RESULT_SELECTED_CHOICES": True, "NO_E_B_QED_MAPPING": True},
    }
    contract["contract_sha256"] = digest(contract)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "allowed_corpus_manifest.json").write_text(json.dumps(corpus, indent=2, sort_keys=True) + "\n")
    (OUT / "frozen_reference_geometry_recovery_contract.json").write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n")
    (OUT / "starting_state.json").write_text(json.dumps({"main_head": head, "clean_required": True, "FROZEN_BEFORE_RESULTS": True}, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
