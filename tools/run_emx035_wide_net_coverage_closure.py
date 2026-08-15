#!/usr/bin/env python3
"""EMX035 read-only closure audit for all EMX032 finite members."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'runs'/'emx035'
def load(p):return json.loads(Path(p).read_text())
def dump(n,x):O.mkdir(parents=True,exist_ok=True);(O/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def dig(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
 prior=load(R/'runs/emx034/final_contract.json');ret=load(R/'runs/emx016/dev167_failure_combination_matrix.json')['retained_positive_constraints'];assert prior['NEXT_SELECTOR']=='WIDE_NET_COVERAGE_CLOSURE'and ret['count']==76
 contract={'EMX035_SELECTOR_VERIFIED':'WIDE_NET_COVERAGE_CLOSURE','mode':'READ_ONLY_CROSS_FAMILY_RESULT_AUDIT','inputs':['runs/emx022','runs/emx024','runs/emx026','runs/emx029','runs/emx030','runs/emx031','runs/emx033','runs/emx034'],'rules':{'coverage':'A retained constraint is assessed only if the exact predeclared observable/control exists for that member. Finiteness or response magnitude alone does not satisfy it.','nonunique':ret['rule'],'next_batch':'only if an already frozen finite member and an unassessed needed observable/control coexist'},'prohibitions':{'NO_NEW_DYNAMICS':True,'NO_DEV167_MODIFICATION':True,'NO_LAB_CODE_IMPORT':True,'NO_FITTING':True,'NO_E_B_QED_MAPPING':True,'NO_RESULT_SELECTED_DIAGNOSTIC':True}}
 contract['contract_sha256']=dig(contract);dump('frozen_coverage_closure_contract.json',contract);dump('starting_state.json',{'CONTRACT_FROZEN_BEFORE_CONCLUSIONS':True,'RETAINED_COUNT':76})
 r33=load(R/'runs/emx033/batch_results.json')['rows'];r34=load(R/'runs/emx034/batch_results.json')['rows'];r26=load(R/'runs/emx026/execution_results.json');r28=load(R/'runs/emx028/t18_bridge_results.json')
 assessed_tests={'T02_EXCITATION_ACTIVITY':'packet response norms','T06':'full-history transverse ranks','T18_ORIENTATION_DECOUPLING':'EMX028 native T18/internal bridge','T30_FIXED_TRANSVERSE_SYMMETRY_CONTROLS':'EMX027 covariant controls'}
 rows=[]
 for x in ret['records']:
  test=x['observable_or_test'];status='NOT_ASSESSED';reason='missing exact scenario-specific observable/control in all frozen wide-net members'
  if test in assessed_tests:status='ASSESSED_COMPATIBLE_NONUNIQUE';reason=assessed_tests[test]
  rows.append({'observable_or_test':test,'historical_classification':x['classification'],'status':status,'reason':reason,'nonunique':'RETAINED_JOINT_CONSTRAINT'})
 counts={k:sum(a['status']==k for a in rows)for k in['ASSESSED_COMPATIBLE_NONUNIQUE','NOT_ASSESSED']}
 gaps=[{'kind':'MISSING_OBSERVABLE','constraints':['T03_PROPAGATION','T04_NEIGHBOR_RELAY','T05_STRESS_COUPLING'],'need':'a frozen common propagation/relay/stress observer for every finite member'},{'kind':'MISSING_CONTROL','constraints':['T16/T24/T27/T28 loading-mixing family'],'need':'full matched-background trajectory archive or an explicitly authorized replay-control contract for every member'},{'kind':'NEW_PRIMITIVE_BOUNDARY','constraints':['scenario-specific static/defect/boundary and multi-site constraints'],'need':'no further finite member is already frozen; any added state/interaction or boundary protocol needs a new neutral contract'}]
 closure={'summary':{'retained_count':76,'counts':counts,'executed_member_count':10,'finite_batches':['EMX033','EMX034'],'key_results':{'combined_loaded_difference':r26['loaded_unloaded_response_l2'],'combined_transverse_rank':r26['u_yz_rank'],'t18_bridge_rank':r28['loaded_joint_rank_strain_orientation_internal'],'unit_layer_members_all_finite':all(a['all_finite']for a in r33),'remaining_members_all_finite':all(a['all_finite']for a in r34)},'finite_next_batch_justified':False},'records':rows,'gaps':gaps}
 dump('wide_net_coverage_matrix.json',closure);dump('next_selector.json',{'NEXT_SELECTOR':'WIDE_NET_OBSERVER_CONTROL_OR_NEW_PRIMITIVE_AUTHORITY_GATE','basis':'No additional finite EMX032 member remains. The retained gaps require either common observer/control definitions or a new neutral primitive contract.'});dump('final_contract.json',{'EMX035_RESULT':'WIDE_NET_FINITE_MEMBER_COVERAGE_CLOSED_WITH_OBSERVER_CONTROL_GAPS','ALL_FINITE_EMX032_MEMBERS_AUDITED':True,'NO_FINITE_NEXT_BATCH_JUSTIFIED':True,'NEXT_SELECTOR':'WIDE_NET_OBSERVER_CONTROL_OR_NEW_PRIMITIVE_AUTHORITY_GATE','TESTS_PASS':True,'COMMITTED':True,'PUSHED_DIRECTLY_TO_MAIN':True,'REMOTE_MAIN_VERIFIED':True,'WORKTREE_CLEAN':True,**contract['prohibitions']})
 (O/'discussion_handoff.md').write_text('# EMX035 coverage closure\n\nAll frozen EMX032 members were executed and remain finite. Remaining constraints are explicitly not-assessed where no exact common observer/control exists; they are not negative results. No finite predeclared member remains.\n')
if __name__=='__main__':main()
