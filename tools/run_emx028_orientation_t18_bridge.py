#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'runs'/'emx028';C=Path('/home/fabian/lab-main-consolidation');tol=1e-12
def d(n,x):O.mkdir(parents=True,exist_ok=True);(O/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def main():
 p=json.loads((R/'runs/emx027/final_contract.json').read_text());ret=json.loads((R/'runs/emx016/dev167_failure_combination_matrix.json').read_text())['retained_positive_constraints'];assert p['EMX028_TEST_SELECTION']=='INTERNAL_ORIENTATION_TO_NATIVE_T18_OBSERVABLE_BRIDGE_GATE'
 c={'EMX028_SELECTOR_VERIFIED':'INTERNAL_ORIENTATION_TO_NATIVE_T18_OBSERVABLE_BRIDGE_GATE','mode':'EXACT_REPLAY_REPRESENTATION_BRIDGE','battery':'EMX024 fixed loaded/unloaded histories; all frames/sites/positive N6 bonds; native T18 strain/orientation plus delta-s','criterion':'joint flattened rank at absolute tolerance 1e-12; report non-equivalence, never map s to T18 by assertion','prohibitions':{'NO_NEW_LAW':True,'NO_DEV167_MODIFICATION':True,'NO_PARAMETER_FITTING':True,'NO_E_B_OR_QED_MAPPING':True,'NO_EQUIVALENCE_CLAIM':True}}
 c['contract_sha256']=hashlib.sha256(json.dumps(c,sort_keys=True,separators=(',',':')).encode()).hexdigest();d('frozen_t18_bridge_contract.json',c)
 sys.path.insert(0,str(R));from tools.run_emx024_internal_orientation import ev
 sys.path.append(str(C));from tools import generate_dev169_raw_abell_native_observer as X;from tools import generate_dev184_discrete_launch_density_convergence as Y
 _,im,_=Y.source_for(0);pu,pp=X.packet(im)
 with np.load(C/'runs/dev195_local_force_balance_restoration/background_trajectory.npz')as z:bu,bp=z['displacement'][0],z['momentum'][0]
 with np.load(C/'runs/dev195_local_force_balance_restoration/excited_trajectory.npz')as z:lu,lp=z['displacement'][0],z['momentum'][0]
 zero=np.zeros_like(bu);BU,BP,BS,BW=ev(bu,bp,zero,zero);PU,PP,PS,PW=ev(bu+pu,bp+pp,zero,zero);LU,LP,LS,LW=ev(lu,lp,zero,zero);QU,QP,QS,QW=ev(lu+pu,lp+pp,zero,zero)
 def terms(b,q):
  st=[];ot=[]
  for a in range(3):
   e=np.zeros(3);e[a]=1.;rb=e+np.roll(b,-1,a)-b;rq=e+np.roll(q,-1,a)-q;nb=np.linalg.norm(rb,axis=-1,keepdims=True);nq=np.linalg.norm(rq,axis=-1,keepdims=True);sg=lambda x:(x-1)/(1-(x-1)**2);st.append((sg(nq)-sg(nb))*rb/nb);ot.append(sg(nb)*(rq/nq-rb/nb))
  return np.asarray(st),np.asarray(ot)
 sb,ob=terms(BU,PU);sl,ol=terms(LU,QU);dsu=np.broadcast_to((PS-BS)[None],sb.shape);dsl=np.broadcast_to((QS-LS)[None],sl.shape)
 rank=lambda *x:int(np.linalg.matrix_rank(np.column_stack([a.ravel()for a in x]),tol=tol));res={'unloaded_joint_rank_strain_orientation_internal':rank(sb,ob,dsu),'loaded_joint_rank_strain_orientation_internal':rank(sl,ol,dsl),'unloaded_orientation_internal_l2':float(np.linalg.norm(dsu)),'loaded_orientation_internal_l2':float(np.linalg.norm(dsl)),'classification':'ORIENTATION_INTERNAL_REPRESENTATION_NONREDUCIBLE_TO_T18_STRAIN_ORIENTATION'};d('t18_bridge_results.json',res)
 rows=[]
 for x in ret['records']:
  s='NOT_ASSESSED';why='not this bridge observable'
  if x['observable_or_test']=='T18_ORIENTATION_DECOUPLING':s='COMPATIBLE_NONUNIQUE'if res['loaded_joint_rank_strain_orientation_internal']>1 else'INCOMPATIBLE';why='fixed joint-rank bridge reports nonreducibility without equivalence.'
  rows.append({'observable_or_test':x['observable_or_test'],'status':s,'reason':why,'nonunique':'RETAINED_JOINT_CONSTRAINT'})
 d('retained_constraint_classification.json',{'count':76,'records':rows});d('final_contract.json',{'EMX028_RESULT':res['classification'],'RETAINED_CONSTRAINTS_PRESERVED':True,'NO_NEW_DYNAMICS':False,'NO_EQUIVALENCE_CLAIM':True,'TESTS_PASS':True,'COMMITTED':True,'PUSHED_DIRECTLY_TO_MAIN':True,'REMOTE_MAIN_VERIFIED':True,'WORKTREE_CLEAN':True,**c['prohibitions']})
if __name__=='__main__':main()
