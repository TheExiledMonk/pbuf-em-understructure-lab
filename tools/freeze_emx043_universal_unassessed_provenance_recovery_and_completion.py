#!/usr/bin/env python3
"""Freeze EMX043 recovery inventory before inspecting recovery outcomes."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'runs'/'emx043'
def h(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def fh(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def main():
 prior=json.loads((ROOT/'runs/emx042/all_finite_candidate_cell_registry.json').read_text())['records'];pending=[x for x in prior if x['universal_classification']=='UNIVERSAL_UNASSESSED'];assert len(pending)==109
 cells=[]
 for x in pending:
  cid=x['cell_id']; historical=cid.startswith('EMX016_GATE_'); a01=cid=='A01_SIGN_DRIVE_REVERSAL'; a02=cid=='A02_LATTICE_COVARIANT_SYMMETRY'
  if historical or a01: missing='EMX042 omitted the already-saved EMX041 common observer linkage'; rule='use only the hash-pinned EMX041 historical full-state vector; global sign preserves its native L2 observer' if a01 else 'use only the hash-pinned EMX041 historical full-state vector; do not re-evaluate the contextual phenotype observer'; status='RECOVERY_ELIGIBLE'
  elif a02: missing='EMX042 wide-net registry row lacked its existing EMX030 frozen symmetry-control link';rule='read only EMX030 A02 fixed control outcome';status='RECOVERY_ELIGIBLE'
  else: missing='no saved full native state history/vector for the EMX041 common observer';rule='recover only if an existing hash-pinned state artifact uniquely supplies source state, geometry, boundary, dt, source history, and observer inputs; otherwise do not synthesize or re-run';status='SEARCH_REQUIRED'
  cells.append({'cell_id':cid,'batch':x['batch'],'source_artifact':x['source_artifact'],'source_sha256':x['source_sha256'],'exact_missing_replay_or_provenance_item':missing,'recovery_rule':rule,'pre_result_recovery_status':status})
 c={'EMX043_SELECTOR':'UNIVERSAL_UNASSESSED_PROVENANCE_RECOVERY_AND_COMPLETION','FROZEN_BEFORE_RESULTS':True,'pending_count':len(cells),'cells':cells,'repository_first_search':['runs/emx041/shared_observer_definition.json','runs/emx041/cross_calibration_stress_matrix.json','runs/emx030/batch_results.json','runs/emx042/held_out_prediction_battery.json'],'canonical_read_only_verification':{'allowed':'only locate/hash-verify existing artifact; no imports or code execution','excited_trajectory':'/home/fabian/lab-main-consolidation/runs/dev195_local_force_balance_restoration/excited_trajectory.npz','background_trajectory':'/home/fabian/lab-main-consolidation/runs/dev195_local_force_balance_restoration/background_trajectory.npz'},'replay_rule':'Recover only when source state, geometry, boundary, dt, source history, and shared-observer inputs are uniquely specified and hash-verifiable.','classification_vocabulary':['UNIVERSAL_VIABLE_NONUNIQUE','UNIVERSAL_REJECTED','UNRECOVERABLE_PROVENANCE'],'held_out_rule':'Use the frozen EMX042 battery only after recovery classification; it is not an admission input.','prohibitions':{'NO_DEV167_MODIFICATION':True,'NO_LAB_GIT_MODIFICATION':True,'NO_LAB_GIT_IMPORT':True,'NO_NEW_DYNAMICS':True,'NO_FITTING':True,'NO_HIDDEN_VARIANTS':True,'NO_RESULT_SELECTED_DIAGNOSTICS':True,'NO_E_B_QED_MAPPING':True}}
 c['input_sha256']={p:fh(p)for p in ['runs/emx042/all_finite_candidate_cell_registry.json','runs/emx041/shared_observer_definition.json','runs/emx041/cross_calibration_stress_matrix.json','runs/emx030/batch_results.json','runs/emx042/held_out_prediction_battery.json']};c['contract_sha256']=h(c);OUT.mkdir(parents=True,exist_ok=True);(OUT/'frozen_provenance_recovery_contract.json').write_text(json.dumps(c,indent=2,sort_keys=True)+'\n');(OUT/'starting_state.json').write_text(json.dumps({'CONTRACT_FROZEN_BEFORE_RESULTS':True,'PENDING_UNIVERSAL_UNASSESSED':109},indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
