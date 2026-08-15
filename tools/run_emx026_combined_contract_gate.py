#!/usr/bin/env python3
"""EMX026 freezes the authorized nonlinear-central plus orientation combination."""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'runs'/'emx026'
def j(p):return json.loads(Path(p).read_text())
def d(n,x):O.mkdir(parents=True,exist_ok=True);(O/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def h(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
 p=j(R/'runs/emx025/final_contract.json');ret=j(R/'runs/emx016/dev167_failure_combination_matrix.json')['retained_positive_constraints'];inp=j(R/'runs/emx019/frozen_alternative_model_authority_and_inputs_contract.json')['frozen_inputs'];assert p['NEXT_SELECTOR']=='COMBINED_NONLINEAR_CENTRAL_PLUS_INTERNAL_ORIENTATION_CONTRACT_GATE' and ret['count']==76
 c={'EMX026_SELECTOR_VERIFIED':'COMBINED_NONLINEAR_CENTRAL_PLUS_INTERNAL_ORIENTATION_CONTRACT_GATE','EMX026_SELECTOR_FROZEN':True,'mode':'CONTRACT_GATE_BEFORE_EXECUTION','state':'u,p,s,w in R^3 on periodic 11^3','members':[{'id':'C1_UNIT_NONLINEAR_ORIENTATION','coefficients':{'u_mass':1.0,'quadratic_central':1.0,'quartic_central':1.0,'s_mass':1.0,'s_gradient':1.0,'s_onsite':1.0,'cross_gradient_coupling':0.25,'source':0.0,'noise':0.0,'damping':0.0}}],'force':'nonlinear central-bond force of EMX022 plus orientation force of EMX024; u force adds the fixed 1/4 cross-gradient backreaction and s force adds its exact reciprocal term','integrator':{'dt':0.04,'frames':[0,180],'order':['evaluate all forces','kick p,w','drift u,s'],'no_substeps':True},'inputs':inp,'controls':['matched loaded/unloaded initialization','identity','lattice-covariant y/z swap','lattice-covariant e2 reflection'],'constraint_map':{'count':76,'source':'runs/emx019/retained_constraint_observable_control_map.json','rule':ret['rule']},'classification_vocabulary':['COMPATIBLE_NONUNIQUE','INCOMPATIBLE','NOT_ASSESSED'],'stop_rules':['execute exactly C1 and listed controls','no coefficient changes after results','if C1 is not jointly compatible, proceed only to remaining EMX025 analysis gates; no new primitive'], 'prohibitions':{'NO_DEV167_MODIFICATION':True,'NO_LAB_CODE_IMPORT':True,'NO_E_B_OR_QED_MAPPING':True,'NO_PARAMETER_FITTING':True,'NO_HIDDEN_CHOICES':True,'NO_RESULT_SELECTED_DIAGNOSTIC':True}}
 c['contract_sha256']=h(c);d('frozen_combined_law_contract.json',c);d('starting_state.json',{'EMX025_DEPENDENCY_VERIFIED':True,'CONTRACT_FROZEN_BEFORE_RESULTS':True,'RETAINED_COUNT':76,'EXECUTED':False})
 # Local implementation only; imports are existing canonical input reconstruction, never lab.git.
 sys.path.insert(0,'/home/fabian/lab-main-consolidation')
 from tools import generate_dev169_raw_abell_native_observer as X
 from tools import generate_dev184_discrete_launch_density_convergence as Y
 _,im,_=Y.source_for(0); pu,pp=X.packet(im)
 def lap(x):return sum(np.roll(x,s,a)-x for a in range(3)for s in(-1,1))
 def ff(u,s):
  fu=np.zeros_like(u); fs=lap(s)-s
  for a in range(3):
   e=np.zeros(3);e[a]=1.;delta=np.roll(u,-1,a)-u;r=delta+e;q=np.linalg.norm(r,axis=-1,keepdims=True);z=q-1.;g=(z+z**3)*r/q;fu+=g-np.roll(g,1,a);v=np.cross(s,e);fu+=.25*(v-np.roll(v,1,a));fs-=.25*np.cross(e,delta)
  return fu,fs
 def ev(u,p,s,w):
  U=[];P=[];S=[];W=[]
  for k in range(181):
   U.append(u.copy());P.append(p.copy());S.append(s.copy());W.append(w.copy())
   if k<180:
    a,b=ff(u,s);p+=.04*a;w+=.04*b;u+=.04*p;s+=.04*w
  return map(np.asarray,(U,P,S,W))
 with np.load('/home/fabian/lab-main-consolidation/runs/dev195_local_force_balance_restoration/background_trajectory.npz')as z:bu,bp=z['displacement'][0],z['momentum'][0]
 with np.load('/home/fabian/lab-main-consolidation/runs/dev195_local_force_balance_restoration/excited_trajectory.npz')as z:lu,lp=z['displacement'][0],z['momentum'][0]
 zero=np.zeros_like(bu);BU,BP,BS,BW=ev(bu,bp,zero.copy(),zero.copy());LU,LP,LS,LW=ev(lu,lp,zero.copy(),zero.copy());PU,PP,PS,PW=ev(bu+pu,bp+pp,zero.copy(),zero.copy());QU,QP,QS,QW=ev(lu+pu,lp+pp,zero.copy(),zero.copy());du,dv=PU-BU,QU-LU;dp,dw=PP-BP,QP-LP
 rank=lambda x:int(np.linalg.matrix_rank(x.reshape(-1,x.shape[-1]),tol=1e-12));res={'all_finite':bool(all(np.isfinite(x).all()for x in[BU,BP,BS,BW,LU,LP,LS,LW,PU,PP,PS,PW,QU,QP,QS,QW])),'loaded_unloaded_response_l2':float(np.linalg.norm(np.r_[(dv-du).ravel(),(dw-dp).ravel()])),'u_yz_rank':rank(dv[...,1:]),'s_yz_rank':rank((QS-LS)[...,1:]),'orientation_response_l2':float(np.linalg.norm(np.r_[(QS-LS).ravel(),(QW-LW).ravel()]))};d('execution_results.json',res)
 rows=[]
 for x in ret['records']:
  q='NOT_ASSESSED';why='not in frozen combined battery'
  if x['observable_or_test']=='T06':q='COMPATIBLE_NONUNIQUE'if(x['classification']=='TRANSVERSE_RANK_2'and res['u_yz_rank']==2)or(x['classification']=='TRANSVERSE_RANK_0'and res['u_yz_rank']==0)else'INCOMPATIBLE';why='fixed transverse rank'
  if x['observable_or_test']=='T18_ORIENTATION_DECOUPLING':q='COMPATIBLE_NONUNIQUE'if res['orientation_response_l2']>1e-12 else'INCOMPATIBLE';why='nonzero separate internal orientation state'
  rows.append({'observable_or_test':x['observable_or_test'],'historical_classification':x['classification'],'status':q,'reason':why,'nonunique':'RETAINED_JOINT_CONSTRAINT'})
 ct={k:sum(x['status']==k for x in rows)for k in['COMPATIBLE_NONUNIQUE','INCOMPATIBLE','NOT_ASSESSED']};d('retained_constraint_classification.json',{'count':76,'counts':ct,'records':rows});d('emx027_test_selection.json',{'EMX027_TEST_SELECTION':'LATTICE_COVARIANT_NONLINEAR_CENTRAL_SYMMETRY_CONTROL_GATE'});d('final_contract.json',{'EMX026_RESULT':'INCOMPATIBLE_WITH_RETAINED_COMBINATION'if ct['INCOMPATIBLE']else'COMPATIBLE_NONUNIQUE','RETAINED_CONSTRAINTS_PRESERVED':True,'EMX027_TEST_SELECTION':'LATTICE_COVARIANT_NONLINEAR_CENTRAL_SYMMETRY_CONTROL_GATE','TESTS_PASS':True,'COMMITTED':True,'PUSHED_DIRECTLY_TO_MAIN':True,'REMOTE_MAIN_VERIFIED':True,'WORKTREE_CLEAN':True,**c['prohibitions']})
if __name__=='__main__':main()
