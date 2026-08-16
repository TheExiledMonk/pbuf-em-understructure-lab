#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import numpy as np
from emx049_new_reference_geometry_primitive import DT, N, STEPS, force, history, local_history, sha, source
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"runs"/"emx049"
def j(p): return json.loads((OUT/p).read_text())
def w(p,x): (OUT/p).write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
def cls(a,b,label,tol): return label if np.max(np.abs(a-b))>tol else "COMPATIBLE_NONUNIQUE"
def main():
 c=j("frozen_new_reference_geometry_primitive_contract.json"); ledger=j("source_geometry_hash_ledger.json"); assert c["FROZEN_BEFORE_RESULTS"]
 prior=json.loads((ROOT/"runs/emx046/packet_shape_cell_registry_and_results.json").read_text())["records"]
 old={r["shape"]:r for r in prior}; tol=c["observer"]["family_comparison_tolerance"]; rows=[]; hashrows=[]
 for s in c["finite_registry"]["shapes"]:
  u,p,z=source(s); assert sha(u)==ledger["source_artifacts"][s]["initial_u_sha256"] and sha(z)==ledger["source_artifacts"][s]["source_history_sha256"]
  new,mind=history(u.copy(),p.copy(),z.copy()); local=local_history(u.copy(),p.copy())
  assert np.all(np.isfinite(new)) and np.all(np.isfinite(local)) and mind > .5
  rows += [{"shape":s,"comparison_family":"HISTORICAL_REPLAY_LIFT_EMX046_OBSERVER_ONLY","new_vector":new.tolist(),"reference_vector":old[s]["historical_replay_lift_vector"],"classification":"UNAVAILABLE_PROVENANCE","meaningfully_comparable":False,"scope":"The EMX041 vector schema is shared, but EMX046 uses a distinct hash-pinned historical replay-lift packet. EMX049's new canonical packet is not an identical preparation, so a numerical difference cannot discriminate families."},{"shape":s,"comparison_family":"LOCAL_NEUTRAL_HARMONIC_PERIODIC_N6_EMX049_MATCHED","new_vector":new.tolist(),"reference_vector":local.tolist(),"classification":cls(new,local,"DIFFERENTIATES_FROM_LOCAL",tol),"meaningfully_comparable":True,"scope":"same EMX049 source artifact, normalization, lattice, boundary, velocity-Verlet update, and EMX041 observer; numerical compatibility does not establish physical validity"}]
  hashrows.append({"shape":s,"u_sha256":sha(u),"p_sha256":sha(p),"source_history_sha256":sha(z),"minimum_relation_distance":mind,"new_vector":new.tolist(),"local_new_family_vector":local.tolist()})
 u,p,z=source("COMPACT"); rest=np.zeros_like(u); rf,rd=force(rest); a,_=history(u.copy(),p.copy(),z.copy()); b,_=history(u.copy(),p.copy(),z.copy()); zero,_=history(rest.copy(),p.copy(),z.copy()); mirror,_,_=source("MIRRORED"); pm,_=history(mirror.copy(),p.copy(),z.copy()); uh,ph,_=source("COMPACT"); forward_u=uh.copy(); forward_p=ph.copy();
 # velocity-Verlet reversibility control: integrate forward then reverse p and integrate back.
 for _ in range(STEPS):
  ff,_=force(forward_u); forward_p+=.5*DT*ff; forward_u+=DT*forward_p; ff,_=force(forward_u); forward_p+=.5*DT*ff
 forward_p=-forward_p
 for _ in range(STEPS):
  ff,_=force(forward_u); forward_p+=.5*DT*ff; forward_u+=DT*forward_p; ff,_=force(forward_u); forward_p+=.5*DT*ff
 forward_p=-forward_p
 fine,_=history(u.copy(),p.copy(),np.zeros((361,N,N,N,3)),dt=.02,steps=360); ct=c["observer"]["control_tolerances"]
 norm_values = [float(np.sqrt(np.sum(source(s)[0] ** 2))) for s in c["finite_registry"]["shapes"]]
 reversal_error = float(max(np.max(np.abs(forward_u - uh)), np.max(np.abs(forward_p - ph))))
 controls = {
  "rest_force": {"classification": "COMPATIBLE_NONUNIQUE" if np.max(np.abs(rf)) <= ct["rest_force"] and rd > .5 else "REPRODUCTION_CONTRADICTED", "max_force": float(np.max(np.abs(rf))), "minimum_distance": rd},
  "identity_reproduction": {"classification": "COMPATIBLE_NONUNIQUE" if np.max(np.abs(a - b)) <= ct["reproduction"] else "REPRODUCTION_CONTRADICTED"},
  "zero_source": {"classification": "COMPATIBLE_NONUNIQUE" if np.max(np.abs(zero)) <= ct["reproduction"] else "REPRODUCTION_CONTRADICTED", "vector": zero.tolist()},
  "parity": {"classification": "COMPATIBLE_NONUNIQUE" if np.max(np.abs(a - pm)) <= ct["parity"] else "REPRODUCTION_CONTRADICTED", "max_difference": float(np.max(np.abs(a - pm)))},
  "time_reversal": {"classification": "COMPATIBLE_NONUNIQUE" if reversal_error <= ct["time_reversal"] else "REPRODUCTION_CONTRADICTED", "max_state_difference": reversal_error},
  "normalization": {"classification": "COMPATIBLE_NONUNIQUE" if max(abs(x - c["source_history_construction"]["artifacts"][s]["initial_l2"]) for x, s in zip(norm_values, c["finite_registry"]["shapes"])) <= ct["normalization"] else "REPRODUCTION_CONTRADICTED", "all_initial_l2": norm_values},
  "refinement": {"classification": "COMPATIBLE_NONUNIQUE" if np.max(np.abs(a - fine)) <= ct["refinement"] else "REPRODUCTION_CONTRADICTED", "max_difference": float(np.max(np.abs(a - fine)))},
 }
 w("source_geometry_hash_ledger.json",{"geometry_sha256":ledger["geometry_sha256"],"source_artifacts":ledger["source_artifacts"],"executed":hashrows}); w("cell_registry_and_results.json",{"comparison_cells":rows,"controls":controls}); w("provenance_separation_statement.json",{"candidate_family_identifier":c["candidate_family_identifier"],"statement":c["provenance_separation"],"emx047_emx048_preserved_unchanged":True,"prohibited_inference":"No EMX049 result is historical DEV167 provenance, a repair of missing history, a mechanism-equivalence claim, or physical-validity evidence."}); w("comparison_matrix.json",{"rows":rows,"provenance_separation":c["provenance_separation"]}); counts={v:sum(x["classification"]==v for x in rows)+sum(x["classification"]==v for x in controls.values()) for v in c["classification_vocabulary"]}; w("conclusion.json",{"counts":counts,"conclusion":"EMX049 is a new neutral candidate. Shared-observer differences are discriminator observations only; neither numerical agreement nor disagreement establishes historical provenance, mechanism equivalence, or physical validity."}); w("final_contract.json",{"EMX049_RESULT":"NEW_NEUTRAL_REFERENCE_GEOMETRY_PRIMITIVE_EXECUTED","COUNTS":counts,"EMX047_EMX048_UNCHANGED":True,"HISTORICAL_GATES_CONTEXTUAL_ONLY":True,"NEXT_SELECTOR":"PREDECLARED_HELD_OUT_NEW_FAMILY_DISCRIMINATOR_OR_NEW_PRIMITIVE_BOUNDARY","NEXT_BOUNDARY":"Any extension requires a separately frozen finite held-out discriminator; do not reinterpret EMX049 as DEV167 provenance.",**c["prohibitions"]})
if __name__=="__main__": main()
