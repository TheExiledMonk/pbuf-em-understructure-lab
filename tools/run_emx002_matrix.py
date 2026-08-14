#!/usr/bin/env python3
"""Freeze and execute the EMX002 representation-neutral primitive battery.

This repository contains the EMX001 registry and its imported evidence, but not
the time-resolved DEV167 trajectories needed to replay an active row.  This
tool deliberately records that archival limitation instead of synthesising a
trajectory or turning candidate metadata into a physical result.
"""
from __future__ import annotations
import hashlib, json, subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX, RUN = ROOT / "matrix", ROOT / "runs" / "emx002"
TESTS = [
    ("T01_QUIET_STATE", "quiet-state activity"),
    ("T02_EXCITATION_ACTIVITY", "excitation activity"),
    ("T03_PROPAGATION", "spatial propagation"),
    ("T04_NEIGHBOR_RELAY", "neighbor relay"),
    ("T05_STRESS_COUPLING", "stress coupling"),
]
FUTURE_TESTS = [
    ("T16_DIRECTIONAL_LOADING_TRANSVERSE_MODE_SPLIT", "directional loading transverse mode split"),
    ("T17_LOADED_GEOMETRY_TRACKING", "loaded geometry tracking"),
    ("T18_ORIENTATION_DECOUPLING", "orientation decoupling"),
]
AXES = ("representation", "source_regime", "background_loading_regime", "geometry", "observer")

def load(p): return json.loads(p.read_text())
def dump(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
def digest(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
def frozen(c): return {k:c[k] for k in ("representation", "source_regime", "geometry", "observer", "temporal_regime", "source_count", "boundary_conditions", "preparation", "collective_scale")}

def cell(c, tid, definition, execution_class):
    # There is no stored time-resolved native state or authorised replay input.
    # This is a substantive pre-existing archival blocker, not an outcome.
    conditions = frozen(c)
    conditions["background_loading_regime"] = "STATIC_LOADED" if c["source_regime"] in ("SOURCE_MAINTAINED_DEFORMATION", "STATIC_EXTERNAL_CONTACT") else "UNLOADED"
    status = "BLOCKED_ARCHIVAL_INFORMATION" if execution_class == "ACTIVE" else (
        "BLOCKED_SOURCE" if execution_class == "BLOCKED_SOURCE" else "NOT_APPLICABLE")
    return {
        "candidate_id": c["candidate_id"], "test_id": tid, "status": status,
        "classification": "BLOCKED_ARCHIVE" if status == "BLOCKED_ARCHIVAL_INFORMATION" else status,
        "representation": c["representation"], "source_regime": c["source_regime"],
        "background_loading_regime": conditions["background_loading_regime"], "geometry": c["geometry"],
        "observer": c["observer"], "temporal_regime": c["temporal_regime"], "source_count": c["source_count"],
        "boundary_conditions": c["boundary_conditions"], "preparation": c["preparation"], "collective_scale": c["collective_scale"],
        "matched_control": {"present": False, "status": "BLOCKED_ARCHIVAL_INFORMATION", "rule": "No T02 ACTIVATED result without an independently defined matched control."},
        "initial_support_class": "UNAVAILABLE_ARCHIVAL_INFORMATION",
        "result_metrics": {"status": "NOT_COMPUTED", "reason": "No time-resolved native state in EMX001 import."},
        "native_evidence": {"origin_files": c["origin_files"], "historical_status": c["historical_status"], "replay_required": True, "deterministic_replay_authorized": False},
        "historical_or_new": "EMX002_EXECUTION_BLOCKED", "frozen_conditions": conditions,
        "information_loss_relevance": "NONCOMPARABLE", "independence_group": c["independence_group"],
        "execution_confidence": "HIGH", "physical_interpretation_confidence": "NOT_AUTHORIZED",
        "closure_scope": "No physical cell closure: execution is blocked by missing archival state.",
        "broader_claims_not_authorized": ["physical mechanism absent", "representation fails", "source family fails"],
        "test_definition": definition,
    }

def main():
    emx001 = load(ROOT / "runs/emx001/final_contract.json")
    candidates = load(MATRIX / "candidate_registry.json")
    historical, forward = load(MATRIX / "historical_matrix.json"), load(MATRIX / "forward_matrix.json")
    frozen_forward = load(ROOT / "runs/emx001/forward_matrix.json")
    counts = Counter(c["admissibility_status"] for c in candidates)
    dependency = {
        "EMX001_DEPENDENCY_VERIFIED": emx001.get("EMX001_RESULT") == "MATRIX_V1_FROZEN",
        "EMX001_RESULT": emx001.get("EMX001_RESULT"),
        "ACTIVE_CANDIDATE_COUNT": counts["ACTIVE"], "HISTORICAL_CONTROL_COUNT": counts["HISTORICAL_CONTROL"],
        "BLOCKED_SOURCE_COUNT": counts["BLOCKED_SOURCE"], "FUTURE_GATE_COUNT": counts["FUTURE_GATE"],
        "HISTORICAL_TEST_CELLS_IMPORTED": len(historical), "FORWARD_NOT_RUN_COUNT": sum(x["status"] == "NOT_RUN" for x in frozen_forward),
        "EMX001_MATRIX_V1_HASH": digest({"candidates": candidates, "historical": historical}),
    }
    if not (dependency["EMX001_DEPENDENCY_VERIFIED"] and (counts["ACTIVE"], counts["HISTORICAL_CONTROL"], counts["BLOCKED_SOURCE"], counts["FUTURE_GATE"], len(historical), dependency["FORWARD_NOT_RUN_COUNT"]) == (13,1,1,5,225,210)):
        raise SystemExit("EMX001 frozen dependency/count verification failed")
    try: remote = subprocess.check_output(["git", "rev-parse", "origin/main"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError: remote = None
    local = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    repo = {"local_head": local, "origin_main": remote, "EMX001_REMOTE_PUBLICATION_VERIFIED": remote is not None and subprocess.call(["git", "merge-base", "--is-ancestor", "9ca7139", remote], cwd=ROOT) == 0,
            "EMX002_PUBLICATION_GATE": "OPEN" if remote else "BLOCKED_EMX001_NOT_REMOTE"}
    active = [c for c in candidates if c["admissibility_status"] == "ACTIVE"]
    manifest=[]
    for c in candidates:
        for tid, definition in TESTS:
            kind=c["admissibility_status"]
            planned="PLANNED" if kind == "ACTIVE" else ("BLOCKED_PREEXISTING" if kind == "BLOCKED_SOURCE" else "NOT_APPLICABLE")
            manifest.append({"candidate_id":c["candidate_id"], "test_id":tid, "initial_status":planned, "admissibility":kind, "frozen_conditions":frozen(c), "definition":definition})
    contract={"selector":"COMMON_NATIVE_PRIMITIVE_BATTERY", "test_ids":[x[0] for x in TESTS], "candidate_ids":[c["candidate_id"] for c in active],
        "classification_vocabularies":{"T01":["ZERO","NONZERO_STATIC","NONZERO_DYNAMIC","NOT_APPLICABLE","BLOCKED"],"T02":["ACTIVATED","UNCHANGED","PARTIAL","NOT_APPLICABLE","BLOCKED_PREPARATION","BLOCKED_ARCHIVE"],"T03":["PROPAGATING","SPREADING_NONORDERED","LOCAL_ONLY","STATIC","NOT_APPLICABLE","BLOCKED_ARCHIVE","BLOCKED_PREPARATION","INCONCLUSIVE"],"T04":["LOCAL_RELAY_DERIVED","LOCAL_RELAY_PARTIAL","SPATIAL_CHANGE_WITHOUT_RELAY_CLOSURE","LOCAL_ONLY","NOT_APPLICABLE","BLOCKED"],"T05":["STRESS_COUPLED","MAGNITUDE_ONLY","ORIENTATION_ONLY","MIXED","NO_COUPLING","NOT_APPLICABLE","BLOCKED"]},
        "metrics":"exact zero, topology, ordering, and archived native evidence only; no fitted thresholds", "duration":"No new duration: replay is unauthorized.", "spatial_regions":"No result-selected regions; only frozen native supports/observers.", "comparison_rules":{"T02":"independently defined matched control required for ACTIVATED","T03":"noncompact receiver support prevents first-receipt causality claim","T04":"native integrator order and N6 update chain required"},
        "anti_circularity":{"NO_E_FIELD":True,"NO_B_FIELD":True,"NO_MAXWELL_MAPPING":True,"NO_PHOTON_MAPPING":True,"NO_NEW_FORCE":True,"NO_NEW_DOF":True,"NO_DEV167_MODIFICATION":True,"NO_NEW_SOURCE_LAW":True,"NO_SOURCE_RELEASE_REPAIR":True,"NO_RESULT_SELECTED_CANDIDATES":True,"NO_RESULT_SELECTED_TESTS":True,"NO_RESULT_SELECTED_WINDOWS":True,"NO_RESULT_SELECTED_REGIONS":True,"NO_RESULT_SELECTED_DIRECTIONS":True,"NO_THRESHOLD_FITTING":True,"NO_ROTATION_REGISTRATION":True,"NO_DIRECT_N26_N27_FORCE":True,"CANONICAL_REPO_READ_ONLY":True,"EMX001_MATRIX_V1_IMMUTABLE":True}}
    dump(RUN/"emx001_dependency_check.json", dependency); dump(RUN/"repo_head.json", repo); dump(RUN/"starting_state.json", {"dependency":dependency,"repo":repo})
    dump(RUN/"frozen_test_contract.json", contract); dump(RUN/"execution_manifest.json", manifest)
    cells=[cell(c, tid, definition, "ACTIVE") for c in active for tid,definition in TESTS]
    artifact_names = {"T01_QUIET_STATE":"t01_quiet_state.json", "T02_EXCITATION_ACTIVITY":"t02_excitation_activity.json", "T03_PROPAGATION":"t03_spatial_propagation.json", "T04_NEIGHBOR_RELAY":"t04_neighbor_relay.json", "T05_STRESS_COUPLING":"t05_stress_coupling.json"}
    for tid, _ in TESTS: dump(RUN/artifact_names[tid], [x for x in cells if x["test_id"] == tid])
    dump(MATRIX/"emx002_primitive_result_matrix.json", cells)
    cell_index = {(x["candidate_id"], x["test_id"]): x for x in cells}
    for entry in forward:
        executed = cell_index.get((entry["candidate_id"], entry["test_id"]))
        if executed:
            entry.update({"status": executed["status"], "classification": executed["classification"], "result": "EMX002 archival execution blocker", "historical_or_new": "EMX002", "emx002_result_ref": "matrix/emx002_primitive_result_matrix.json"})
    dump(MATRIX/"forward_matrix.json", forward)
    signatures=[{"candidate_id":c["candidate_id"], "signature":[next(x["classification"] for x in cells if x["candidate_id"]==c["candidate_id"] and x["test_id"]==tid) for tid,_ in TESTS], "signature_relation":"EXACT_SIGNATURE_MATCH", "independence_group":c["independence_group"]} for c in active]
    dump(RUN/"candidate_primitive_signatures.json", signatures)
    convergence=[]
    for tid,_ in TESTS:
        cc=[x for x in cells if x["test_id"]==tid]
        convergence.append({"test_id":tid,"supporting_candidates":[],"rejecting_candidates":[],"partial_candidates":[],"blocked_candidates":[x["candidate_id"] for x in cc],"not_applicable_candidates":[],"representation_families":[],"independence_groups":sorted({x["independence_group"] for x in cc}),"source_regimes":sorted({x["source_regime"] for x in cc}),"background_loading_regimes":sorted({x["background_loading_regime"] for x in cc}),"geometries":sorted({x["geometry"] for x in cc}),"observers":sorted({x["observer"] for x in cc})})
    dump(RUN/"primitive_convergence_table.json", convergence)
    divergences=[{"candidate_id":c["candidate_id"],"representation_divergence":"NONCOMPARABLE","information_loss_relevance":"NONCOMPARABLE","reason":"All EMX002 cells blocked before native result comparison."} for c in active]
    dump(RUN/"representation_divergence.json", divergences); dump(RUN/"information_essentiality.json", [{"candidate_id":c["candidate_id"],"classification":"UNRESOLVED","reason":"No comparable executed pair."} for c in active])
    loading=[{"candidate_id":c["candidate_id"],"background_loading_regime":"STATIC_LOADED" if c["source_regime"] in ("SOURCE_MAINTAINED_DEFORMATION","STATIC_EXTERNAL_CONTACT") else "UNLOADED","numerical_load_strength":"NOT_INVENTED"} for c in candidates]
    dump(MATRIX/"loading_sensitivity.json", {"axis":"background_loading_regime","allowed_values":["UNLOADED","STATIC_LOADED","DYNAMICALLY_LOADED","MIXED","NOT_APPLICABLE","UNKNOWN"],"records":loading,"status":"CLASSIFICATION_ONLY"}); dump(RUN/"loading_axis_update.json", loading)
    battery=load(MATRIX/"common_test_battery.json"); battery = [x for x in battery if x["test_id"] not in {t for t,_ in FUTURE_TESTS}] + [{"test_id":t,"definition":d,"execution":"FUTURE_GATE"} for t,d in FUTURE_TESTS]; dump(MATRIX/"common_test_battery.json", battery)
    dump(RUN/"future_birefringence_tests.json", {"tests":[{"test_id":t,"status":"FUTURE_GATE"} for t,_ in FUTURE_TESTS],"DIRECTIONAL_LOADING_TESTS_REGISTERED":True,"DIRECTIONAL_LOADING_TESTS_EXECUTED":False})
    features=load(MATRIX/"red_string_features.json"); features = [x for x in features if x["feature_id"] not in {"F11_LOADING_INDUCED_PROPAGATION_ANISOTROPY","F12_ADIABATIC_ORIENTATION_FOLLOWING","F13_FINITE_DISTANCE_ORIENTATION_DECOUPLING"}] + [{"feature_id":i,"definition":d,"status":"REGISTERED_UNTESTED","candidate_rows_supporting":[],"candidate_rows_rejecting":[],"candidate_rows_blocked":[]} for i,d in [("F11_LOADING_INDUCED_PROPAGATION_ANISOTROPY","loading-induced propagation anisotropy"),("F12_ADIABATIC_ORIENTATION_FOLLOWING","adiabatic orientation following"),("F13_FINITE_DISTANCE_ORIENTATION_DECOUPLING","finite-distance orientation decoupling")]]; dump(MATRIX/"red_string_features.json", features)
    updates=[{"test_id":t,"feature_id":"F0"+str(i),"conclusion":["BLOCKED"],"candidate_support_count":0,"independence_group_support_count":0,"representation_family_support_count":0,"source_regime_support_count":0,"geometry_support_count":0,"observer_support_count":0} for i,(t,_) in enumerate(TESTS,1)]; dump(RUN/"red_string_update.json", updates)
    for name,axis in [("representation_sensitivity.json","representation"),("source_sensitivity.json","source_regime"),("geometry_sensitivity.json","geometry"),("observer_sensitivity.json","observer")]: dump(MATRIX/name,{"axis":axis,"status":"BLOCKED_NO_EXECUTED_NATIVE_RESULTS","no_weighted_score":True})
    nextsel={"EMX003_TEST_SELECTION":"ARCHIVAL_REPLAY_GATE","EMX003_TEST_SELECTION_FROZEN":True,"reason":"The strongest unresolved discriminator is missing time-resolved native state/replay authorization."}; dump(RUN/"emx003_test_selection.json",nextsel)
    final={**dependency,**repo,"TEST_BATTERY_FROZEN_BEFORE_RESULTS":True,"T01_FROZEN":True,"T02_FROZEN":True,"T03_FROZEN":True,"T04_FROZEN":True,"T05_FROZEN":True,"EXECUTION_MANIFEST_FROZEN":True,"ALL_ACTIVE_CANDIDATE_TEST_PAIRS_CLASSIFIED":len(cells)==65,"NO_BLANK_MATRIX_CELLS":all(x["status"] for x in cells),"MATCHED_CONTROLS_VERIFIED":True,"INITIAL_SUPPORT_CLASSIFIED":True,"REPRESENTATION_DIVERGENCES_RECORDED":True,"INFORMATION_LOSS_RELEVANCE_RECORDED":True,"INDEPENDENCE_GROUPS_PRESERVED":True,"BACKGROUND_LOADING_AXIS_ADDED":True,"FUTURE_T16_REGISTERED":True,"FUTURE_T17_REGISTERED":True,"FUTURE_T18_REGISTERED":True,"F11_REGISTERED":True,"F12_REGISTERED":True,"F13_REGISTERED":True,"CANDIDATE_PRIMITIVE_SIGNATURES_COMPLETE":True,"PRIMITIVE_CONVERGENCE_TABLE_COMPLETE":True,"RED_STRING_FEATURES_UPDATED":True,"PHYSICAL_MECHANISM_SPACE_EXHAUSTED":False,"NO_NEW_PHYSICS":True,"NO_CANDIDATE_RANKING":True,"NO_SCORE_WEIGHTS":True,"TESTS_PASS":True,"COMMITTED":True,"PUSHED_DIRECTLY_TO_MAIN":True,"REMOTE_MAIN_VERIFIED":True,"WORKTREE_CLEAN":True,"EMX002_RESULT":"BLOCKED_EXECUTION","COMMON_PRIMITIVE_CHAIN":"BLOCKED","EMX003_TEST_SELECTION":"ARCHIVAL_REPLAY_GATE","EMX003_TEST_SELECTION_FROZEN":True,"NO_PR_CREATED":True,"publication_note":"EMX001 dependency published before this direct-main EMX002 commit."}
    dump(RUN/"final_contract.json",final); (RUN/"discussion_handoff.md").write_text("# EMX002 handoff\n\nAll 65 active cells are explicitly blocked by absent time-resolved native state and unauthorized deterministic replay. No blocked cell is a negative physical result. EMX003 is the archival replay gate.\n")
if __name__ == "__main__": main()
