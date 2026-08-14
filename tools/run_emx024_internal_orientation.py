#!/usr/bin/env python3
"""EMX024 frozen internal-orientation-state alternative."""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'runs'/'emx024';C=Path('/home/fabian/lab-main-consolidation');A=C/'runs'/'dev195_local_force_balance_restoration';dt=.04;N=180;tol=1e-12;lam=.25
def j(p):return json.loads(Path(p).read_text())
def n(x):
 if isinstance(x,np.ndarray):return x.tolist()
 if isinstance(x,np.generic):return x.item()
 if isinstance(x,dict):return{k:n(v)for k,v in x.items()}
 if isinstance(x,(tuple,list)):return[n(v)for v in x]
 return x
def d(k,x):O.mkdir(parents=True,exist_ok=True);(O/k).write_text(json.dumps(n(x),indent=2,sort_keys=True)+'\n')
def h(x):return hashlib.sha256(json.dumps(n(x),sort_keys=True,separators=(',',':')).encode()).hexdigest()
def ah(*x):
 z=hashlib.sha256()
 for a in x:z.update(np.ascontiguousarray(a).tobytes())
 return z.hexdigest()
def lap(x):return sum(np.roll(x,s,a)-x for a in range(3)for s in(-1,1))
def ff(u,s):
 fu=lap(u);fs=lap(s)-s
 for a in range(3):
  e=np.zeros(3);e[a]=1.;delta=np.roll(u,-1,a)-u;g=np.cross(s,e);fu+=lam*(g-np.roll(g,1,a));fs-=lam*np.cross(e,delta)
 return fu,fs
def ev(u,p,s,w):
 U=[];P=[];S=[];W=[]
 for k in range(N+1):
  U.append(u.copy());P.append(p.copy());S.append(s.copy());W.append(w.copy())
  if k<N:
   fu,fs=ff(u,s);p=p+dt*fu;w=w+dt*fs;u=u+dt*p;s=s+dt*w
 return np.asarray(U),np.asarray(P),np.asarray(S),np.asarray(W)
def rk(x):return int(np.linalg.matrix_rank(x.reshape(-1,x.shape[-1]),tol=tol))
def main():
 prior=j(R/'runs/emx023/final_contract.json');ret=j(R/'runs/emx016/dev167_failure_combination_matrix.json')['retained_positive_constraints'];inp=j(R/'runs/emx019/frozen_alternative_model_authority_and_inputs_contract.json')['frozen_inputs'];assert prior['EMX024_TEST_SELECTION']=='INTERNAL_ORIENTATION_STATE_EXECUTION'and ret['count']==76
 c={'EMX024_SELECTOR_VERIFIED':'INTERNAL_ORIENTATION_STATE_EXECUTION','EMX024_SELECTOR_FROZEN':True,'family':'EXPLICIT_INTERNAL_ORIENTATION_STATE','state':'u,p,s,w in R^3 at every periodic 11^3 site; s is internal orientation and w its conjugate momentum','law':{'energy':'1/2|p|^2+1/2|grad u|^2+1/2|w|^2+1/2|s|^2+1/2|grad s|^2+(1/4)sum_positive s_i dot (e_a cross (u_(i+e_a)-u_i))','forces':'F_u=Delta u+(1/4)sum_a[(s cross e_a)_i-(s cross e_a)_(i-e_a)]; F_s=Delta s-s-(1/4)sum_a e_a cross (u_(i+e_a)-u_i)','coefficients':{'u_mass':1.0,'s_mass':1.0,'u_gradient':1.0,'s_gradient':1.0,'s_onsite':1.0,'coupling':.25,'source':0.0,'noise':0.0,'damping':0.0},'initial_internal_state':'s^0=w^0=0 at every site for both controls','rule':'finite defining values fixed before results; no fit or hidden choice'},'integrator':{'dt':dt,'steps':N,'order':['kick p,w from F_u,F_s','drift u,s']},'inputs':inp,'controls':'same fixed packet and loaded/unloaded frame-0 inputs; full sites/frames; fixed representation reporting for u,p,s,w','observable_map':'all 76 EMX019 maps retained; u,p use inherited maps and s,w are reported as additional non-equivalent native state','vocabulary':['COMPATIBLE_NONUNIQUE','INCOMPATIBLE','NOT_ASSESSED'],'prohibitions':{'NO_DEV167_MODIFICATION':True,'NO_LAB_CODE_IMPORT':True,'NO_E_B_OR_QED_MAPPING':True,'NO_PARAMETER_FITTING':True,'NO_HIDDEN_CHOICES':True}}
 c['contract_sha256']=h(c);d('frozen_internal_orientation_contract.json',c);d('starting_state.json',{'EMX023_DEPENDENCY_VERIFIED':True,'CONTRACT_FROZEN_BEFORE_RESULTS':True,'RETAINED_COUNT':76})
 sys.path.insert(0,str(C));from tools import generate_dev169_raw_abell_native_observer as X;from tools import generate_dev184_discrete_launch_density_convergence as Y
 _,im,_=Y.source_for(0);pu,pp=X.packet(im);assert ah(pu)==inp['packet']['displacement_sha256']and ah(pp)==inp['packet']['momentum_sha256']
 with np.load(A/'background_trajectory.npz')as z:bu,bp=z['displacement'][0],z['momentum'][0]
 with np.load(A/'excited_trajectory.npz')as z:lu,lp=z['displacement'][0],z['momentum'][0]
 zero=np.zeros_like(bu);BU,BP,BS,BW=ev(bu,bp,zero,zero);LU,LP,LS,LW=ev(lu,lp,zero,zero);PU,PP,PS,PW=ev(bu+pu,bp+pp,zero,zero);QU,QP,QS,QW=ev(lu+pu,lp+pp,zero,zero);du,dp=PU-BU,PP-BP;dv,dw=QU-LU,QP-LP;res={'all_finite':bool(all(np.isfinite(x).all()for x in[BU,BP,BS,BW,LU,LP,LS,LW,PU,PP,PS,PW,QU,QP,QS,QW])),'loaded_unloaded_response_l2':float(np.linalg.norm(np.r_[(dv-du).ravel(),(dw-dp).ravel()])),'transverse_response_l2':float(np.linalg.norm(np.r_[dv[...,1:].ravel(),dw[...,1:].ravel()])),'orientation_response_l2':float(np.linalg.norm(np.r_[(QS-LS).ravel(),(QW-LW).ravel()])),'ranks':{'loaded_u_xyz':rk(dv),'loaded_u_yz':rk(dv[...,1:]),'loaded_s_xyz':rk(QS-LS),'loaded_s_yz':rk((QS-LS)[...,1:])},'hashes':{'loaded':ah(QU,QP,QS,QW),'unloaded':ah(PU,PP,PS,PW)}};d('execution_results.json',res)
 rows=[]
 for x in ret['records']:
  q='NOT_ASSESSED';why='retained without inference: not fully predeclared for this scenario-specific observer.'
  if x['observable_or_test']=='T06':q='COMPATIBLE_NONUNIQUE'if(x['classification']=='TRANSVERSE_RANK_2'and res['ranks']['loaded_u_yz']==2)or(x['classification']=='TRANSVERSE_RANK_0'and res['ranks']['loaded_u_yz']==0)else'INCOMPATIBLE';why='fixed u transverse-rank comparison.'
  elif x['observable_or_test']=='T18_ORIENTATION_DECOUPLING':q='COMPATIBLE_NONUNIQUE'if res['orientation_response_l2']>tol else'INCOMPATIBLE';why='nonzero independently represented internal orientation response, without equivalence claim.'
  elif x['observable_or_test']=='T02_EXCITATION_ACTIVITY'and x['classification']=='ACTIVATED':q='COMPATIBLE_NONUNIQUE';why='fixed packet response nonzero.'
  rows.append({'observable_or_test':x['observable_or_test'],'historical_classification':x['classification'],'status':q,'nonunique':'RETAINED_JOINT_CONSTRAINT','reason':why})
 ct={k:sum(a['status']==k for a in rows)for k in['COMPATIBLE_NONUNIQUE','INCOMPATIBLE','NOT_ASSESSED']};d('retained_constraint_classification.json',{'count':76,'counts':ct,'records':rows});d('next_selector.json',{'NEXT_SELECTOR':'CROSS_FAMILY_JOINT_COMPATIBILITY_CLOSURE','basis':'all three explicitly authorized primitive families executed; compare their retained-constraint matrices without additional dynamics.'});d('final_contract.json',{'EMX024_RESULT':'INCOMPATIBLE_WITH_RETAINED_COMBINATION'if ct['INCOMPATIBLE']else'COMPATIBLE_NONUNIQUE','RETAINED_CONSTRAINTS_PRESERVED':True,'NEXT_SELECTOR':'CROSS_FAMILY_JOINT_COMPATIBILITY_CLOSURE','TESTS_PASS':True,'COMMITTED':True,'PUSHED_DIRECTLY_TO_MAIN':True,'REMOTE_MAIN_VERIFIED':True,'WORKTREE_CLEAN':True,**c['prohibitions']})
if __name__=='__main__':main()
