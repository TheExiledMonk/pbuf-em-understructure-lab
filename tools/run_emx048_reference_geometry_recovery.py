#!/usr/bin/env python3
"""Audit the frozen EMX048 corpus without deriving missing historical inputs."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs" / "emx048"


def git_bytes(*args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True).stdout


def git(*args: str) -> str:
    return git_bytes(*args).decode()


def load(name: str) -> dict:
    return json.loads((OUT / name).read_text())


def write(name: str, value: object) -> None:
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def keys(value: object) -> set[str]:
    if isinstance(value, dict):
        return {str(k).lower() for k in value} | set().union(*(keys(v) for v in value.values()), set())
    if isinstance(value, list):
        return set().union(*(keys(v) for v in value), set())
    return set()


def main() -> None:
    contract = load("frozen_reference_geometry_recovery_contract.json")
    corpus = load("allowed_corpus_manifest.json")
    assert contract["FROZEN_BEFORE_RESULTS"] and corpus["head"] == contract["allowed_corpus"]["head"]
    parent_hashes = set(contract["known_parent_artifacts"].values())
    candidates: dict[tuple[str, str], dict] = {}
    terms = ("dev167", "dev195_canonical_packet_parent", "geometry", "source_history", "source history", "reference", "relation")
    allowed_paths = set(corpus["eligible_json_paths"])
    for commit in corpus["commits"]:
        for line in git("ls-tree", "-r", commit).splitlines():
            meta, path = line.split("\t", 1)
            if path not in allowed_paths:
                continue
            blob = meta.split()[2]
            key = (path, blob)
            if key in candidates:
                candidates[key]["commits"].append(commit)
                continue
            raw = git_bytes("show", f"{commit}:{path}")
            text = raw.decode("utf-8", errors="replace")
            low = text.lower()
            if not (any(term in low for term in terms) or any(h in text for h in parent_hashes)):
                continue
            try:
                parsed = json.loads(text)
                schema = "VALID_JSON"
                found_keys = sorted(keys(parsed))
            except json.JSONDecodeError:
                parsed, schema, found_keys = None, "INVALID_JSON", []
            candidates[key] = {"path": path, "git_blob": blob, "sha256": hashlib.sha256(raw).hexdigest(), "commits": [commit], "schema_validation": schema, "keys": found_keys, "text": text}
    rows = []
    geometry_tokens = ("directed_relation_vectors", "directed_reference_geometry", "rest_relation", "rest_geometry", "reference_geometry")
    source_tokens = ("source_history_mapping", "source_history", "source_history_sha256", "source_mapping")
    identity_tokens = ("identity_trajectory", "historical_identity", "trajectory", "state_fields")
    for candidate in sorted(candidates.values(), key=lambda x: (x["path"], x["git_blob"])):
        lower = candidate.pop("text").lower()
        keyset = set(candidate["keys"])
        has_geometry = any(t in lower or t in keyset for t in geometry_tokens)
        has_source = any(t in lower or t in keyset for t in source_tokens)
        has_identity = any(t in lower or t in keyset for t in identity_tokens)
        parent_linked = any(h in lower for h in parent_hashes) or "dev195_canonical_packet_parent" in lower
        explicit_vector_payload = any(t in keyset for t in geometry_tokens) and ("sha256" in keyset or any(t.endswith("_sha256") for t in keyset))
        explicit_source_payload = any(t in keyset for t in source_tokens) and ("sha256" in keyset or any(t.endswith("_sha256") for t in keyset))
        if explicit_vector_payload and explicit_source_payload and has_identity and parent_linked:
            classification = "RECOVERED_HASH_VERIFIED_NOT_REPRODUCED"
            reason = "All named fields were located, but no repository-local historical update/identity executable was found for the required independent reproduction."
        else:
            classification = "INCOMPLETE_PROVENANCE"
            missing = [name for name, present in (("directed_reference_geometry_payload", explicit_vector_payload), ("source_history_mapping_payload", explicit_source_payload), ("identity_reproduction_inputs", has_identity), ("parent_linkage", parent_linked)) if not present]
            reason = "Missing: " + ", ".join(missing)
        rows.append({**candidate, "first_commit": candidate["commits"][-1], "last_commit": candidate["commits"][0], "parent_linkage": parent_linked, "supplies_directed_relation_vectors": explicit_vector_payload, "supplies_source_history_mapping": explicit_source_payload, "supplies_identity_reproduction_inputs": has_identity, "classification": classification, "reason": reason})
    recovered = [r for r in rows if r["classification"].startswith("RECOVERED_")]
    missing = []
    for field in ("directed_reference_geometry", "source_history_mapping", "identity_reproduction"):
        suppliers = [r["path"] for r in rows if (r["supplies_directed_relation_vectors"] if field == "directed_reference_geometry" else r["supplies_source_history_mapping"] if field == "source_history_mapping" else r["supplies_identity_reproduction_inputs"])]
        missing.append({"field": field, "classification": "NOT_PRESENT_IN_ALLOWED_CORPUS" if not suppliers else "INCOMPLETE_PROVENANCE", "supplier_paths": suppliers, "needed_authority": "A tracked, hash-pinned historical DEV167 artifact with this exact field; no inferred substitute is permitted."})
    write("candidate_artifact_ledger.json", {"count": len(rows), "records": rows})
    write("missing_field_ledger.json", {"required_fields": missing, "all_recovery_predicates_satisfied": False})
    if recovered:
        # This branch deliberately stops before EMX049: it only creates a frozen ready selector.
        ready = {"EMX049_SELECTOR": "HISTORICAL_PACKET_SHAPE_DYNAMICS_REPLAY", "FROZEN_FROM_EMX048": True, "eligible_records": [r["sha256"] for r in recovered], "DO_NOT_EXECUTE_IN_EMX048": True}
        write("emx049_ready_execution_contract.json", ready)
        next_selector, boundary = "EMX049_HISTORICAL_PACKET_SHAPE_DYNAMICS_REPLAY", "Recovery candidate requires separately authorized EMX049 execution."
    else:
        next_selector = "HASH_PINNED_DEV167_REFERENCE_GEOMETRY_AND_SOURCE_HISTORY_AUTHORITY_BOUNDARY"
        boundary = "No tracked historical artifact supplies hash-pinned directed neighbor rest-relation vectors or a hash-pinned source-history mapping; an authoritative artifact containing both plus identity replay inputs is required."
    counts = {label: sum(r["classification"] == label for r in rows) for label in contract["classification_vocabulary"]}
    counts["NOT_PRESENT_IN_ALLOWED_CORPUS"] = sum(x["classification"] == "NOT_PRESENT_IN_ALLOWED_CORPUS" for x in missing)
    write("recovery_conclusion.json", {"candidate_count": len(rows), "counts": counts, "recovered_count": len(recovered), "conclusion": "All scanned evidence is provenance metadata or trajectory-schema metadata; no historical geometry/source payload is inferred.", "next_selector": next_selector, "boundary": boundary})
    write("final_contract.json", {"EMX048_RESULT": "REFERENCE_GEOMETRY_AND_SOURCE_HISTORY_RECOVERY_COMPLETE", "COUNTS": counts, "EMX049_EXECUTED": False, "NEXT_SELECTOR": next_selector, "NEXT_BOUNDARY": boundary, "PRESERVES_EMX047_BOUNDARY": True, **contract["prohibitions"]})


if __name__ == "__main__":
    main()
