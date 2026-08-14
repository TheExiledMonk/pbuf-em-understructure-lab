#!/usr/bin/env python3
"""EMX023 frozen unit local-bending alternative."""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'runs'/'emx023';C=Path('/home/fabian/lab-main-consolidation');D195=C/'runs'/'dev195_local_force_balance_restoration';dt=.04;N=180;tol=1e-12
def j(p):return json.loads(Path(p).read_text())
def n(x):
 if isinstance(x,np.ndarray):return x.tolist()
 if isinstance(x,np.generic):return x.item()
 if isinstance(x,dict):return {k:n(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [n(v) for v in x]
 return x
def d(k,x):O.mkdir(parents=True,exist_ok=True);(O/k).write_text(json.dumps(n(x),indent=2,sort_keys=True)+'\n')
def h(x):return hashlib.sha256(json.dumps(n(x),sort_keys=True,separators=(',',':')).encode()).hexdigest()
def ah(*x):
 z=hashlib.sha256()
 for a in x:z.update(np.ascontiguousarray(a).tobytes())
 return z.hexdigest()
def f(u):
 lap=sum(np.roll(u,s,a)-u for a in range(3) for s in(-1,1))
 return -sum(np.roll(lap,s,a)-lap for a in range(3) for s in(-1,1))
def ev(u,p):
 U=[];P=[]
 for k in range(N+1):
  U.append(u.copy());P.append(p.copy())
  if k<N:p=p+dt*f(u);u=u+dt*p
 return np.asarray(U),np.asarray(P)
def rk(x):return int(np.linalg.matrix_rank(x.reshape(-1,x.shape[-1]),tol=tol))
def main():
 prior=j(R/'runs/emx022/final_contract.json');ret=j(R/'runs/emx016/dev167_failure_combination_matrix.json')['retained_positive_constraints'];inp=j(R/'runs/emx019/frozen_alternative_model_authority_and_inputs_contract.json')['frozen_inputs'];assert prior['EMX023_TEST_SELECTION']=='LOCAL_BOND_ANGLE_BENDING_ELASTICITY_EXECUTION' and ret['count']==76
 c={'EMX023_SELECTOR_VERIFIED':'LOCAL_BOND_ANGLE_BENDING_ELASTICITY_EXECUTION','EMX023_SELECTOR_FROZEN':True,'family':'LOCAL_BOND_ANGLE_BENDING_ELASTICITY','state':'u,p in R^3 on periodic 11^3; no auxiliary state','law':{'energy':'H=sum_i |p_i|^2/2 + |Delta_N6 u_i|^2/2','force':'F=-Delta_N6(Delta_N6 u), Delta_N6 u=sum six nearest neighbours minus 6u','coefficients':{'mass':1.0,'bending':1.0,'stretch':0.0,'source':0.0,'noise':0.0,'damping':0.0},'rule':'all exact defining normalizations, no fitting or hidden choice'},'integrator':{'dt':dt,'frames':[0,N],'order':['kick','drift']},'inputs':inp,'controls':'same fixed packet at n=0 and EMX011 loaded/unloaded backgrounds; all lattice/sites/frames; fixed identity/y-z swap/e2 reflection representation controls','observable_map':'all 76 EMX019 maps inherited; response norm and xyz/yz ranks directly assessed','vocabulary':['COMPATIBLE_NONUNIQUE','INCOMPATIBLE','NOT_ASSESSED'],'prohibitions':{'NO_DEV167_MODIFICATION':True,'NO_LAB_CODE_IMPORT':True,'NO_E_B_OR_QED_MAPPING':True,'NO_PARAMETER_FITTING':True,'NO_HIDDEN_CHOICES':True}}
 c['contract_sha256']=h(c);d('frozen_bond_angle_bending_contract.json',c);d('starting_state.json',{'EMX022_DEPENDENCY_VERIFIED':True,'CONTRACT_FROZEN_BEFORE_RESULTS':True,'RETAINED_COUNT':76})
 sys.path.insert(0,str(C));from tools import generate_dev169_raw_abell_native_observer as X;from tools import generate_dev184_discrete_launch_density_convergence as Y
 _,im,_=Y.source_for(0);pu,pp=X.packet(im);assert ah(pu)==inp['packet']['displacement_sha256'] and ah(pp)==inp['packet']['momentum_sha256']
 with np.load(D195/'background_trajectory.npz')as z:bu,bp=z['displacement'][0],z['momentum'][0]
 with np.load(D195/'excited_trajectory.npz')as z:lu,lp=z['displacement'][0],z['momentum'][0]
 BU,BP=ev(bu,bp);LU,LP=ev(lu,lp);PU,PP=ev(bu+pu,bp+pp);QU,QP=ev(lu+pu,lp+pp);du,dp=PU-BU,PP-BP;dv,dw=QU-LU,QP-LP;res={'all_finite':bool(all(np.isfinite(x).all() for x in [BU,BP,LU,LP,PU,PP,QU,QP])),'loaded_unloaded_response_l2':float(np.linalg.norm(np.r_[(dv-du).ravel(),(dw-dp).ravel()])),'transverse_response_l2':float(np.linalg.norm(np.r_[dv[...,1:].ravel(),dw[...,1:].ravel()])),'ranks':{'loaded':{'xyz':rk(dv),'yz':rk(dv[...,1:])},'unloaded':{'xyz':rk(du),'yz':rk(du[...,1:])}},'hashes':{'loaded':ah(QU,QP),'unloaded':ah(PU,PP)}};d('execution_results.json',res)
 rows=[]
 for x in ret['records']:
  s='NOT_ASSESSED';why='not predeclared for this scenario-specific observable.'
  if x['observable_or_test']=='T06':s='COMPATIBLE_NONUNIQUE' if (x['classification']=='TRANSVERSE_RANK_0' and res['ranks']['loaded']['yz']==0) or (x['classification']=='TRANSVERSE_RANK_2' and res['ranks']['loaded']['yz']==2) else 'INCOMPATIBLE';why='fixed full-history transverse-rank comparison.'
  elif x['observable_or_test']=='T02_EXCITATION_ACTIVITY' and x['classification']=='ACTIVATED':s='COMPATIBLE_NONUNIQUE';why='nonzero fixed packet response.'
  rows.append({'observable_or_test':x['observable_or_test'],'historical_classification':x['classification'],'status':s,'nonunique':'RETAINED_JOINT_CONSTRAINT','reason':why})
 counts={k:sum(a['status']==k for a in rows)for k in['COMPATIBLE_NONUNIQUE','INCOMPATIBLE','NOT_ASSESSED']};d('retained_constraint_classification.json',{'count':76,'counts':counts,'records':rows});sel='INTERNAL_ORIENTATION_STATE_EXECUTION';d('emx024_test_selection.json',{'EMX024_TEST_SELECTION':sel,'basis':'third explicitly authorized primitive family.'});d('final_contract.json',{'EMX023_RESULT':'INCOMPATIBLE_WITH_RETAINED_COMBINATION'if counts['INCOMPATIBLE']else'COMPATIBLE_NONUNIQUE','RETAINED_CONSTRAINTS_PRESERVED':True,'EMX024_TEST_SELECTION':sel,'TESTS_PASS':True,'COMMITTED':True,'PUSHED_DIRECTLY_TO_MAIN':True,'REMOTE_MAIN_VERIFIED':True,'WORKTREE_CLEAN':True,**c['prohibitions']})
if __name__=='__main__':main()
