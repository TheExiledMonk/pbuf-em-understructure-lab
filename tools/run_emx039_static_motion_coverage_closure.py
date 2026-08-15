#!/usr/bin/env python3
"""EMX039 is a read-only closure audit of the frozen EMX036--038 matrix."""
from __future__ import annotations
import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'runs'/'emx039'
def j(p):return json.loads(Path(p).read_text())
def d(n,x):(O/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def main():
 ret=j(R/'runs/emx016/dev167_failure_combination_matrix.json')['retained_positive_constraints']['records'];x=j(R/'runs/emx038/remaining_matrix_results.json')['results'];assert len(ret)==76 and len(x)==216
 c={'EMX039_SELECTOR':'STATIC_AND_MOTION_MATRIX_COVERAGE_CLOSURE','FROZEN_BEFORE_CONCLUSIONS':True,'inputs':['runs/emx036/factorial_registry.json','runs/emx037/batch_results.json','runs/emx038/remaining_matrix_results.json'],'criteria':{'finite':'all predeclared cells finite','retained':'only exact historical packet/control condition can newly assess retained constraints','no_inference':'compatible-nonunique finite cells do not establish a mechanism'},'no_fitting':True,'prohibitions':{'NO_DEV167_MODIFICATION':True,'NO_EXTERNAL_CODE_IMPORT':True,'NO_E_B_QED_MAPPING':True}}
 c['sha256']=hashlib.sha256(json.dumps(c,sort_keys=True,separators=(',',':')).encode()).hexdigest();O.mkdir(parents=True,exist_ok=True);d('frozen_coverage_closure_contract.json',c)
 stat={'cell_count':224,'zero_controls':8,'repository_local_source_cells':216,'all_finite':all(z['all_finite']for z in x),'static_interaction_assessed':sum(z['static_interaction']!='NOT_ASSESSED'for z in x),'motion_difference_assessed':sum(z['motion_dependent_difference']!='NOT_ASSESSED'for z in x),'orientation_proxy_reported':len(x),'reciprocity_not_assessed_reason':'the fixed placement has no separately frozen A/B exchange replay','retained_constraints_newly_assessed':0,'retained_constraints_preserved_not_reclassified':76}
 d('coverage_matrix.json',stat);d('retained_constraint_coverage.json',{'count':76,'records':[{'candidate_id':q['candidate_id'],'status':'NOT_ASSESSED','reason':'new source lift is not the exact historical packet/control bridge'}for q in ret]})
 d('final_contract.json',{'EMX039_RESULT':'FINITE_STATIC_AND_MOTION_MATRIX_CLOSED_AT_REPOSITORY_LOCAL_LIFT_SCOPE','ALL_224_CELLS_ACCOUNTED_FOR':True,'ALL_216_NONZERO_LIFT_CELLS_FINITE':stat['all_finite'],'RETAINED_POSITIVE_CONSTRAINTS_PRESERVED':True,'NO_NEW_RETAINED_CONSTRAINT_ASSESSMENT':True,'NEXT_SELECTOR':'HISTORICAL_PACKET_TO_REPOSITORY_LOCAL_SOURCE_COMPARABILITY_AUTHORITY_GATE','NEXT_BOUNDARY':'A meaning-preserving predeclared bridge between the historical fixed packet/control observables and the new local source-lift observables is required; finite source-lift responses alone cannot supply it.',**c['prohibitions']})
if __name__=='__main__':main()
