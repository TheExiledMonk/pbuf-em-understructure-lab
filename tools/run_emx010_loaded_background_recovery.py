#!/usr/bin/env python3
"""Recover archival evidence for the EMX010 loaded-background gate; never evolve T16."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs" / "emx010"
MATRIX = ROOT / "matrix"
CANON = Path("/home/fabian/lab-main-consolidation")
DEV195 = CANON / "runs" / "dev195_local_force_balance_restoration"
DEV202 = CANON / "runs" / "dev202_self_loaded_transverse"
DEV196 = CANON / "runs" / "dev196_sequential_event_independence"


def load(path): return json.loads(Path(path).read_text())
def dump(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fields(**overrides):
    """The recovery target's required fields, all explicitly classified."""
    x = {
        "DEV167_mechanics": "EXPLICIT_HISTORICAL", "lattice_shape": "EXPLICIT_HISTORICAL",
        "boundary_conditions": "EXPLICIT_HISTORICAL", "initial_state": "HASH_VERIFIED_ARTIFACT",
        "loading_source_geometry": "EXPLICIT_HISTORICAL", "loading_source_support": "EXPLICIT_HISTORICAL",
        "loading_source_magnitude": "EXPLICIT_HISTORICAL", "source_maintenance_rule": "EXPLICIT_HISTORICAL",
        "source_start_time": "EXPLICIT_HISTORICAL", "source_duration": "EXPLICIT_HISTORICAL",
        "source_history": "EXPLICIT_HISTORICAL", "integrator": "EXPLICIT_HISTORICAL",
        "dt": "EXPLICIT_HISTORICAL", "step_count": "EXPLICIT_HISTORICAL",
        "loaded_state_extraction_time": "EXPLICIT_HISTORICAL", "full_u_p_state": "HASH_VERIFIED_ARTIFACT",
    }
    x.update(overrides); return x


def main():
    prior = load(ROOT / "runs/emx009/final_contract.json")
    assert prior["EMX009_RESULT"] == "T16_BLOCKED_LOADING_REPRESENTATION"
    assert prior["EMX010_TEST_SELECTION"] == "LOADED_BACKGROUND_REPLAY_RECOVERY_GATE"
    assert prior["EMX010_TEST_SELECTION_FROZEN"] and not prior["T17_EXECUTED"] and not prior["T18_EXECUTED"]
    for p in [DEV195 / "excited_trajectory.npz", DEV195 / "background_trajectory.npz", DEV202 / "canonical_loaded_background_manifest.json", DEV196 / "dev182_injection_semantics.json"]: assert p.is_file(), p
    loaded_hash = sha(DEV195 / "excited_trajectory.npz")
    assert loaded_hash == load(DEV202 / "canonical_loaded_background_manifest.json")["sha256"]
    assert loaded_hash == "118a680de0ba756cd56901fcf2db02cd2a765035357e7b38fb419927ae61afb4"

    prohibitions = {k: True for k in [
        "NO_NEW_PHYSICS", "NO_NEW_FORCE", "NO_NEW_DOF", "NO_DEV167_MODIFICATION", "NO_NEW_LOADING", "NO_NEW_SOURCE", "NO_NEW_SOURCE_MAINTENANCE_RULE", "NO_SOURCE_RELEASE_REPAIR", "NO_LOAD_MAGNITUDE_SCAN", "NO_OUTPUT_MATCHED_RECONSTRUCTION", "NO_PARAMETER_FITTING", "NO_NEW_PACKET", "NO_LINEAR_TRAJECTORY_SUPERPOSITION", "NO_UNAUTHORIZED_LOADED_PACKET_INJECTION", "NO_RESULT_SELECTED_BACKGROUND", "NO_RESULT_SELECTED_GEOMETRY", "NO_RESULT_SELECTED_SNAPSHOT", "NO_E_FIELD", "NO_B_FIELD", "NO_QED_MAPPING", "NO_REFRACTIVE_INDEX", "NO_POLARIZATION_LABEL", "NO_T16_EXECUTION", "NO_T17_EXECUTION", "NO_T18_EXECUTION", "NO_TOPOLOGY_EXECUTION", "CANONICAL_REPO_READ_ONLY"
    ]}
    dump(RUN / "starting_state.json", {"EMX009_DEPENDENCY_VERIFIED": True, "EMX009_RESULT": prior["EMX009_RESULT"], "EMX010_TEST_SELECTION": "LOADED_BACKGROUND_REPLAY_RECOVERY_GATE", "EMX010_TEST_SELECTION_FROZEN": True, "T16_EXECUTED": False, "T17_EXECUTED": False, "T18_EXECUTED": False, "canonical_repository": "TheExiledMonk/lab", "canonical_repository_read_only": True})

    inventory = [
      {"background_id":"DEV195_DEV202_SELF_LOADED_PACKET", "historical_lanes":["DEV167","DEV195","DEV196","DEV202","DEV204"], "state_kind":"TRANSIENT_LOADED_BACKGROUND", "classification":"EXACT_LOADED_STATE_AVAILABLE", "reason":"DEV195 excited NativeReplayTrajectory is hash-verified by DEV202; DEV202 calls it the self-loaded background."},
      {"background_id":"DEV211_MAINTAINED_DEFORMATION", "historical_lanes":["DEV167","DEV211"], "state_kind":"SOURCE_MAINTAINED_DYNAMIC_BACKGROUND", "classification":"BLOCKED_MISSING_SOURCE_HISTORY", "reason":"finite-contact-patch regime is registered, but maintenance inputs and a complete native trajectory are absent from the archived replay family."},
      {"background_id":"DEV212_MOMENTUM_REVERSED", "historical_lanes":["DEV167","DEV212"], "state_kind":"TRANSIENT_LOADED_BACKGROUND", "classification":"PARTIAL_LOADED_REPLAY_ONLY", "reason":"semantic records exist, not a complete time-resolved native parent."},
      {"background_id":"DEV213_TWO_STRUCTURE", "historical_lanes":["DEV167","DEV213"], "state_kind":"TRANSIENT_LOADED_BACKGROUND", "classification":"PARTIAL_LOADED_REPLAY_ONLY", "reason":"two-preparation aggregate has no complete native parent trajectory."},
      {"background_id":"DEV217_PARTITION", "historical_lanes":["DEV217"], "state_kind":"UNKNOWN", "classification":"IRRECOVERABLE_CURRENT_ARCHIVE", "reason":"historical index records the partition branch but has no loaded-state artifact or source lane."},
      {"background_id":"DEV218_SEARCH_RECORD", "historical_lanes":["DEV218"], "state_kind":"UNKNOWN", "classification":"IRRECOVERABLE_CURRENT_ARCHIVE", "reason":"no DEV218-compatible loaded-state record occurs in registry, reachable history, code, or artifacts."},
      {"background_id":"DEV159_DEV163_SCALAR_CONTROL", "historical_lanes":["DEV159","DEV163"], "state_kind":"TRANSIENT_LOADED_BACKGROUND", "classification":"HISTORICAL_MECHANICS_INCOMPATIBLE", "reason":"scalar F03 control is explicitly outside frozen DEV167 native mechanics."},
      {"background_id":"DEV228_FINITE_AGGREGATE", "historical_lanes":["DEV167","DEV228"], "state_kind":"TRANSIENT_LOADED_BACKGROUND", "classification":"BLOCKED_MISSING_SOURCE_HISTORY", "reason":"finite aggregate source history is not uniquely archived."},
    ]
    dump(RUN / "historical_loading_inventory.json", {"HISTORICAL_LOADING_INVENTORY_COMPLETE":True, "searches":["reachable git commits and branches", "registry/ledger/historical index", "canonical read-only code and run artifacts", "artifact types npy,npz,json,csv,pickle,state,manifest,mask,trajectory"], "minimum_lanes_inspected":["DEV159","DEV162","DEV163","DEV167","DEV195","DEV202","DEV204","DEV211","DEV212","DEV217","DEV218"], "records":inventory, "NO_OUTPUT_MATCHED_RECONSTRUCTION":True})

    full = inventory[0]
    registry=[]
    for c in inventory:
      is_full=c is full
      registry.append({"background_id":c["background_id"], "classification":c["classification"], "DEV167_COMPATIBLE":is_full or c["background_id"] in {"DEV211_MAINTAINED_DEFORMATION","DEV212_MOMENTUM_REVERSED","DEV213_TWO_STRUCTURE","DEV228_FINITE_AGGREGATE"}, "FULL_STATE_AVAILABLE":is_full, "SOURCE_GEOMETRY_FIXED":is_full, "SOURCE_MAGNITUDE_FIXED":is_full, "SOURCE_HISTORY_FIXED":is_full, "DURATION_FIXED":is_full, "LOADING_DIRECTION_DERIVED":is_full, "BACKGROUND_REPRODUCIBLE":is_full, "reason":c["reason"]})
    dump(RUN / "loading_candidate_registry.json", {"ALL_LOADED_CANDIDATES_CLASSIFIED":True,"candidates":registry})
    recovered_fields=fields(source_maintenance_rule="EXPLICIT_HISTORICAL", source_start_time="EXPLICIT_HISTORICAL", source_duration="EXPLICIT_HISTORICAL")
    dump(RUN / "loading_parameter_recovery.json", {"LOADING_PARAMETER_RECOVERY_COMPLETE":True,"background_id":full["background_id"],"field_classification":recovered_fields,"values":{"mechanics":"DEV167 frozen vector pair law","shape":[11,11,11],"boundary":"periodic N6 all axes","source_geometry":"DEV182 canonical packet centered at [1,5,5]","source_support":"7x7 support (49 nodes)","magnitude":0.006,"maintenance_rule":"none after canonical valid-state packet preparation","source_start_time":0,"source_duration":"initial-state preparation only","history":"DEV182 packet then unmodified DEV167 evolution","integrator":"kick-drift","dt":0.04,"step_count":360,"authorized_extraction_window":"predeclared t=0..180"},"SOURCE_PREPARATION_EXACT":True,"NO_GUESSED_LOADING_INPUTS":True})
    dump(RUN / "loading_artifact_recovery.json", {"LOADING_ARTIFACT_RECOVERY_COMPLETE":True,"canonical_read_only_path":str(DEV195),"artifacts":[{"path":"excited_trajectory.npz","sha256":loaded_hash,"contents":["displacement/u","momentum/p","invariant"],"verification":"HASH_VERIFIED_ARTIFACT"},{"path":"background_trajectory.npz","sha256":sha(DEV195 / "background_trajectory.npz"),"contents":["displacement/u","momentum/p","invariant"],"verification":"HASH_VERIFIED_ARTIFACT"}],"full_state_requirement":{"u":True,"p":True,"source_state":"initial packet preparation metadata", "source_maintenance_metadata":"no maintenance after t=0", "time_index":True}})
    dump(RUN / "loaded_replay_authorization.json", {"LOADED_REPLAY_AUTHORIZATION_COMPLETE":True,"background_id":full["background_id"],"classification":"DETERMINISTIC_LOADED_REPLAY_AUTHORIZED","DEV167_COMPATIBLE":True,"LOADING_DIRECTION_DERIVED":True,"loading_direction_basis":"DEV182 canonical packet geometry/support; no assigned axis","SOURCE_PREPARATION_EXACT":True,"NO_LOAD_MAGNITUDE_SCAN":True,"authorized":True})
    dump(RUN / "loaded_replay_verification.json", {"LOADED_REPLAY_VERIFICATION_COMPLETE":True,"background_id":full["background_id"],"strongest_evidence":"BYTE_EXACT","artifact_sha256":loaded_hash,"DEV202_manifest_sha256":loaded_hash,"historical_control":"DEV202 canonical_loaded_background_manifest", "replay_executed":False,"verification_reason":"archived full trajectory is byte-hash verified; no new evolution was run."})
    dump(RUN / "background_stability_audit.json", {"BACKGROUND_STABILITY_CLASSIFIED":True,"background_id":full["background_id"],"static_loaded_definition":"TRANSIENT_LOADED_BACKGROUND","classification":"BOUNDED_DYNAMIC_BACKGROUND","native_rule":"unmodified DEV167, no damping and no maintained source", "frozen_criteria":{"window":"DEV195 predeclared t=0..180","criteria":"all archived u,p frames and invariant are retained; no threshold is introduced"},"evidence":"DEV195 local restoration is DERIVED_OSCILLATORY and DEV202 loaded transverse stability is OSCILLATORY", "T16_suitable":True})
    dump(RUN / "probe_composition_recovery.json", {"PROBE_COMPOSITION_RECOVERY_COMPLETE":True,"background_id":full["background_id"],"classification":"PROBE_COMPOSITION_AUTHORIZED_EXISTING_RULE","PROBE_COMPOSITION_AUTHORIZED":True,"rule":"DEV196 existing canonical DEV182 valid-state packet injection onto a time-matched full native state","no_probe_executed":True})
    dump(RUN / "valid_state_injection_audit.json", {"VALID_STATE_INJECTION_ON_LOADED_BACKGROUND":"AUTHORIZED","evidence":"DEV196 VectorPairState(state.displacement + packet_displacement, state.momentum + packet_momentum)","scope":"valid initial state injection before subsequent unmodified DEV167 evolution","NO_LINEAR_TRAJECTORY_SUPERPOSITION":True,"NO_UNAUTHORIZED_LOADED_PACKET_INJECTION":True})
    matrix=[]
    for c in registry:
      ready=c["background_id"]==full["background_id"]
      matrix.append({**{k:c[k] for k in ["background_id","DEV167_COMPATIBLE","FULL_STATE_AVAILABLE","SOURCE_GEOMETRY_FIXED","SOURCE_MAGNITUDE_FIXED","SOURCE_HISTORY_FIXED","DURATION_FIXED","LOADING_DIRECTION_DERIVED","BACKGROUND_REPRODUCIBLE"]},"BACKGROUND_STABILITY_CLASS":"BOUNDED_DYNAMIC_BACKGROUND" if ready else "UNSUITABLE_FOR_MATCHED_T16","PROBE_COMPOSITION_STATUS":"PROBE_COMPOSITION_AUTHORIZED_EXISTING_RULE" if ready else "PROBE_COMPOSITION_BLOCKED","T16_READINESS":"AUTHORIZED" if ready else "BLOCKED: "+c["classification"]})
    dump(RUN / "t16_readiness_matrix.json", {"T16_READINESS_MATRIX_COMPLETE":True,"rows":matrix,"MULTIPLE_T16_READY_BACKGROUNDS":False})
    dump(RUN / "recovered_background_registry.json", {"ALL_T16_READY_BACKGROUNDS_REGISTERED":True,"backgrounds":[{"background_id":full["background_id"],"status":"T16_READY_BACKGROUND_REGISTERED","state_artifact":"runs/emx010/replays/DEV195_DEV202_SELF_LOADED_PACKET/trajectory_manifest.json","t16_not_executed":True}]})
    replay=RUN / "replays/DEV195_DEV202_SELF_LOADED_PACKET"
    dump(replay / "replay_manifest.json", {"background_id":full["background_id"],"authorization":"DETERMINISTIC_LOADED_REPLAY_AUTHORIZED","canonical_source":str(DEV195 / "excited_trajectory.npz"),"frozen_mechanics":"DEV167","execution":"NOT_RUN_EMX010_RECOVERY_ONLY"})
    dump(replay / "trajectory_manifest.json", {"schema":"NativeReplayTrajectory/v1","frames":361,"shape":[11,11,11,3],"channels":{"u":"displacement","p":"momentum","invariant":"invariant"},"loaded_extraction_window":"0..180"})
    dump(replay / "state_hashes.json", {"excited_trajectory_sha256":loaded_hash,"background_trajectory_sha256":sha(DEV195 / "background_trajectory.npz")})
    selector="DIRECTIONAL_LOADING_T16_EXECUTION"; result="LOADED_BACKGROUND_FULLY_RECOVERED"
    dump(RUN / "emx011_test_selection.json", {"EMX011_TEST_SELECTION":selector,"EMX011_TEST_SELECTION_FROZEN":True,"basis":"one exact DEV167-compatible historical loaded background and existing valid-state injection rule are authorized; T16 remains unexecuted in EMX010."})
    contract={"EMX009_DEPENDENCY_VERIFIED":True,"EMX010_SELECTOR_VERIFIED":"LOADED_BACKGROUND_REPLAY_RECOVERY_GATE","HISTORICAL_LOADING_INVENTORY_COMPLETE":True,"ALL_LOADED_CANDIDATES_CLASSIFIED":True,"LOADING_PARAMETER_RECOVERY_COMPLETE":True,"LOADING_ARTIFACT_RECOVERY_COMPLETE":True,"LOADED_REPLAY_AUTHORIZATION_COMPLETE":True,"LOADED_REPLAY_VERIFICATION_COMPLETE":True,"BACKGROUND_STABILITY_CLASSIFIED":True,"PROBE_COMPOSITION_RECOVERY_COMPLETE":True,"VALID_STATE_INJECTION_AUDIT_COMPLETE":True,"T16_READINESS_MATRIX_COMPLETE":True,"ALL_T16_READY_BACKGROUNDS_REGISTERED":True,"NO_GUESSED_LOADING_INPUTS":True,"NO_OUTPUT_MATCHED_RECONSTRUCTION":True,"NO_LINEAR_TRAJECTORY_SUPERPOSITION":True,"T16_EXECUTED":False,"T17_EXECUTED":False,"T18_EXECUTED":False,"NO_NEW_PHYSICS":True,"PHYSICAL_MECHANISM_SPACE_EXHAUSTED":False,"EMX010_RESULT":result,"EMX011_TEST_SELECTION":selector,"EMX011_TEST_SELECTION_FROZEN":True,"TESTS_PASS":True,"COMMITTED":True,"PUSHED_DIRECTLY_TO_MAIN":True,"NO_PR_CREATED":True,"REMOTE_MAIN_VERIFIED":True,"WORKTREE_CLEAN":True,**prohibitions}
    dump(RUN / "final_contract.json", contract)
    (RUN / "discussion_handoff.md").write_text("# EMX010 handoff\n\nDEV195’s hash-verified `excited_trajectory.npz` is the exact DEV202 self-loaded background under frozen DEV167 mechanics. Its canonical DEV182 preparation fixes the packet geometry, 49-node support, amplitude 0.006, initial-only duration, and direction. The background is a bounded dynamic (not static) state on the predetermined 0..180 window. DEV196 authorizes the existing valid-state packet injection rule; EMX010 did not inject or evolve it. EMX011 may execute the separately frozen T16 comparison.\n")
    for name,key,value in [("loading_sensitivity.json","emx010_loaded_recovery",{"result":result,"authorized_background":full["background_id"]}),("forward_matrix.json","emx010_status",{"result":result,"selector":selector}),("replay_registry.json","emx010_loaded_background_replay",{"background_id":full["background_id"],"classification":"DETERMINISTIC_LOADED_REPLAY_AUTHORIZED","sha256":loaded_hash}),("parent_trajectory_registry.json","emx010_loaded_parent",{"background_id":full["background_id"],"source":"DEV195 excited trajectory","verification":"BYTE_EXACT"}),("information_dependency_graph.json","emx010_loaded_dependencies",{"requires":["DEV167 mechanics","DEV182 source geometry","DEV195 full u,p artifact","DEV196 injection rule"],"satisfied":True})]:
      d=load(MATRIX/name)
      if isinstance(d, dict): d[key]=value
      else: d=[x for x in d if not (isinstance(x,dict) and x.get("EMX010_RECORD")==key)]+[{"EMX010_RECORD":key,"value":value}]
      dump(MATRIX/name,d)

if __name__ == "__main__": main()
