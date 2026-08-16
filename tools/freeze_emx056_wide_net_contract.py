#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'runs'/'emx056'
def f(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def h(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
 files=['runs/emx055/frozen_held_out_source_work_discriminator_contract.json','runs/emx055/family_separation_matrix_and_equivalence_graph.json','runs/emx055/held_out_registry_and_results.json','runs/emx049/frozen_new_reference_geometry_primitive_contract.json','runs/emx053/final_contract.json']
 c={'EMX056_SELECTOR':'PBUF_ELASTICITY_AND_EMISSION_WIDE_NET','FROZEN_BEFORE_RESULTS':True,'mode':'EVIDENCE_BUILDING_NON_REJECTION','non_blocking_rule':'Every candidate/control is retained. No observation may discard a candidate or alter EMX010-055 labels.','classification_vocabulary':['SUPPORTED_IN_SCOPE','CONTRADICTED_IN_SCOPE','DISTINCT_OBSERVABLE_BEHAVIOR','NOT_ASSESSED','UNDEFINED_PRIMITIVE_BOUNDARY'],'source_work_families':{'POTENTIAL_PORT_EQUIVALENCE_CLASS':['CONSERVATIVE_SOURCE_POTENTIAL','DISCRETE_PORT_WORK_PAIRING'],'DIRECTED_BOND':['GEOMETRY_COVARIANT_BOND_WORK']},'batches':{'A':'INTERNAL_EXCHANGE_EMISSION_ABSORPTION','B':'CONSTITUTIVE_TANGENT_AND_FINITE_DOMAIN','C':'HISTORY_ACTION_DURATION_BRIDGE'},'new_primitives':{'A':'neutral localized matter-bearing q,r sector coupled to EMX049 elastic placement u,p; never DEV167 provenance','B':'positive hyperelastic constitutive completions with fixed reference 2-jet; no microstructure inference','C':'neutral finite clock/duration alternatives only, explicitly new repository-local history/action primitives'},'input_sha256':{p:f(p)for p in files},'prohibitions':{'NO_DEV167_OR_LAB_GIT_MODIFICATION_IMPORT_OR_EXECUTION':True,'NO_EXTERNAL_CODE_OR_CREDENTIALS_OR_SPENDING':True,'NO_FITTING_OR_RESELECTION':True,'NO_E_B_QED_MAPPING':True,'NO_DESTRUCTIVE_OPERATIONS':True,'PRESERVE_EMX010_055':True}}
 c['contract_sha256']=h(c);O.mkdir(parents=True,exist_ok=True);(O/'frozen_pbuf_elasticity_emission_wide_net_contract.json').write_text(json.dumps(c,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
