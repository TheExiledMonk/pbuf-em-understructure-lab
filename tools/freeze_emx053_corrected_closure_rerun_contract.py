#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'runs'/'emx053'
def f(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def h(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
 files=['runs/emx052/emx053_ready_rerun_contract.json','runs/emx052/frozen_closure_gate_validity_contract.json','runs/emx052/conservation_calibration.json','runs/emx052/virtual_work_audit.json','runs/emx051/frozen_finite_closure_candidate_contract.json','runs/emx051/law_source_hash_ledger.json','tools/emx051_finite_closure_candidates.py']
 ready=json.loads((R/files[0]).read_text());assert ready['FROZEN_FROM_EMX052'] and ready['conservation_relative_drift_tolerance']==.003
 c={'EMX053_SELECTOR':'CORRECTED_CLOSURE_CANDIDATE_RERUN','FROZEN_BEFORE_RESULTS':True,'emx052_ready_contract_sha256':f(files[0]),'candidate_laws':['CONSERVATIVE_ELASTIC','SYMPLECTIC_PAIRED_STATE','GEOMETRY_DIRECTED_WORK'],'unchanged_registry':json.loads((R/'runs/emx051/frozen_finite_closure_candidate_contract.json').read_text())['staged_registry'],'validated_gates':{'conservation_relative_drift_tolerance':.003,'virtual_work':'cumulative half-kick kinetic work with identical executed temporal support; residual relative to initial canonical energy <= .003','held_out_controls':'EMX052 ELONGATED source-free dt=.04 duration=14.4'},'classification_vocabulary':['PASSES_VALIDATED_INTERNAL_CONTROLS','FAILS_VALIDATED_POSITIVITY','FAILS_VALIDATED_REVERSIBILITY','FAILS_VALIDATED_CONSERVATION','FAILS_VALIDATED_REFINEMENT','FAILS_VALIDATED_VIRTUAL_WORK','DIFFERENTIATES_FROM_EMX049','COMPATIBLE_NONUNIQUE','INSUFFICIENT_TO_DISTINGUISH','UNAVAILABLE_PROVENANCE'],'input_sha256':{p:f(p)for p in files},'provenance':'EMX053 reruns explicit EMX051 hypotheses only. It preserves EMX051/052 classifications and confers neither physical validation nor derivation.','prohibitions':{'NO_DEV167_OR_LAB_GIT_MODIFICATION_IMPORT_OR_EXECUTION':True,'NO_EXTERNAL_CODE':True,'NO_FITTING':True,'NO_HIDDEN_OR_RESULT_SELECTED_CHOICES':True,'NO_EMX051_052_RECLASSIFICATION':True,'NO_E_B_QED_MAPPING':True}}
 c['contract_sha256']=h(c);O.mkdir(parents=True,exist_ok=True);(O/'frozen_corrected_closure_rerun_contract.json').write_text(json.dumps(c,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
