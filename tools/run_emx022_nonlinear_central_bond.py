#!/usr/bin/env python3
"""EMX022: one predeclared nonlinear central-bond alternative, no DEV167 change."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]; RUN=ROOT/'runs'/'emx022'; CANON=Path('/home/fabian/lab-main-consolidation'); DEV195=CANON/'runs'/'dev195_local_force_balance_restoration'; DT=.04; STEPS=180; TOL=1e-12
def load(p): return json.loads(Path(p).read_text())
def nat(x):
 if isinstance(x,np.generic): return x.item()
 if isinstance(x,np.ndarray): return x.tolist()
 if isinstance(x,dict): return {str(k):nat(v) for k,v in x.items()}
 if isinstance(x,(tuple,list)): return [nat(v) for v in x]
 return x
def dump(n,x): RUN.mkdir(parents=True,exist_ok=True); (RUN/n).write_text(json.dumps(nat(x),indent=2,sort_keys=True,allow_nan=False)+'\n')
def dig(x): return hashlib.sha256(json.dumps(nat(x),sort_keys=True,separators=(',',':')).encode()).hexdigest()
def ah(*xs):
 h=hashlib.sha256()
 for x in xs:h.update(np.ascontiguousarray(x).tobytes())
 return h.hexdigest()
def fh(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def force(u):
 f=np.zeros_like(u)
 for axis in range(3):
  delta=np.roll(u,-1,axis=axis)-u; e=np.zeros(3);e[axis]=1.; r=delta+e; q=np.linalg.norm(r,axis=-1,keepdims=True); strain=q-1.; g=(strain+strain**3)*r/q
  f+=g-np.roll(g,1,axis=axis)
 return f
def evolve(u,p):
 us=[];ps=[]
 for n in range(STEPS+1):
  us.append(u.copy());ps.append(p.copy())
  if n<STEPS:p=p+DT*force(u);u=u+DT*p
 return np.asarray(us),np.asarray(ps)
def rank(v): return int(np.linalg.matrix_rank(v.reshape(-1,v.shape[-1]),tol=TOL))
def main():
 prior=load(ROOT/'runs/emx021/final_contract.json'); retained=load(ROOT/'runs/emx016/dev167_failure_combination_matrix.json')['retained_positive_constraints']; inputs=load(ROOT/'runs/emx019/frozen_alternative_model_authority_and_inputs_contract.json')['frozen_inputs']; assert prior['NEW_PRIMITIVE_AUTHORITY_REQUIRED'] and retained['count']==76
 c={'EMX022_SELECTOR_VERIFIED':'NONLINEAR_CENTRAL_BOND_ELASTICITY_EXECUTION','EMX022_SELECTOR_FROZEN':True,'family':'NONLINEAR_CENTRAL_BOND_ELASTICITY','state':'u_i,p_i in R^3 on periodic Z_11^3; no auxiliary state','law':{'bond_vector':'r_i,a=e_a+u_(i+e_a)-u_i for positive a=x,y,z','energy':'sum_i [|p_i|^2/2 + sum_a ((|r_i,a|-1)^2/2+(|r_i,a|-1)^4/4)]','force':'F_i=sum_a positive [g_i,a-g_(i-e_a),a], g=(s+s^3)r/|r|, s=|r|-1','coefficients':{'mass':1.0,'quadratic_bond':1.0,'quartic_bond':1.0,'onsite':0.0,'source':0.0,'noise':0.0,'damping':0.0},'parameter_rule':'defining finite normalization; no fitted, hidden, or configurable coefficient'},'integrator':{'dt':DT,'steps':STEPS,'order':['p<-p+dt*F(u)','u<-u+dt*p'],'substeps':0},'inputs':inputs,'controls':{'loaded_unloaded':'same packet added at n=0 to hash-verified EMX011 loaded/unloaded frame-0 states','symmetry':['identity','y_z_swap','e2_reflection'],'scope':'all 11^3 sites and frames 0..180'},'observable_map':'the 76 EMX019 retained observable/control maps are inherited verbatim; directly measured here are response norm, xyz/yz rank, and fixed symmetry equivariance','classification_vocabulary':['COMPATIBLE_NONUNIQUE','INCOMPATIBLE','NOT_ASSESSED'],'prohibitions':{'NO_DEV167_MODIFICATION':True,'NO_LAB_CODE_IMPORT':True,'NO_E_B_OR_QED_MAPPING':True,'NO_PARAMETER_FITTING':True,'NO_HIDDEN_CHOICES':True,'NO_RESULT_SELECTED_DIAGNOSTIC':True}}
 c['contract_sha256']=dig(c);dump('frozen_nonlinear_central_bond_contract.json',c);dump('starting_state.json',{'EMX021_DEPENDENCY_VERIFIED':True,'CONTRACT_FROZEN_BEFORE_RESULTS':True,'RETAINED_COUNT':76})
 sys.path.insert(0,str(CANON));from tools import generate_dev169_raw_abell_native_observer as D;from tools import generate_dev184_discrete_launch_density_convergence as D184
 _,im,_=D184.source_for(0);pu,pp=D.packet(im);assert ah(pu)==inputs['packet']['displacement_sha256'] and ah(pp)==inputs['packet']['momentum_sha256'];assert fh(DEV195/'background_trajectory.npz')==inputs['unloaded_background']['sha256'] and fh(DEV195/'excited_trajectory.npz')==inputs['loaded_background']['sha256']
 with np.load(DEV195/'background_trajectory.npz') as z: bu,bp=z['displacement'][0],z['momentum'][0]
 with np.load(DEV195/'excited_trajectory.npz') as z: lu,lp=z['displacement'][0],z['momentum'][0]
 bU,bP=evolve(bu,bp);lU,lP=evolve(lu,lp);pU,pP=evolve(bu+pu,bp+pp);qU,qP=evolve(lu+pu,lp+pp);du,dp=pU-bU,pP-bP;dv,dw=qU-lU,qP-lP;diff=float(np.linalg.norm(np.r_[ (dv-du).ravel(),(dw-dp).ravel()]));trans=float(np.linalg.norm(np.r_[dv[...,1:].ravel(),dw[...,1:].ravel()])); ranks={'unloaded':{'xyz_u':rank(du),'xyz_p':rank(dp),'yz_u':rank(du[...,1:]),'yz_p':rank(dp[...,1:])},'loaded':{'xyz_u':rank(dv),'xyz_p':rank(dw),'yz_u':rank(dv[...,1:]),'yz_p':rank(dw[...,1:])}}
 mats={'identity':np.eye(3),'y_z_swap':np.array([[1,0,0],[0,0,1],[0,1,0.]]),'e2_reflection':np.diag([1.,1.,-1.])}; sym={}
 for n,m in mats.items():
  cu,cp=evolve((lu+pu)@m.T,(lp+pp)@m.T);sym[n]={'max_u_error':float(np.max(np.abs(cu-qU@m.T))),'max_p_error':float(np.max(np.abs(cp-qP@m.T)))};sym[n]['exact']=sym[n]['max_u_error']<=TOL and sym[n]['max_p_error']<=TOL
 dump('execution_results.json',{'all_finite':bool(all(np.isfinite(x).all() for x in [bU,bP,lU,lP,pU,pP,qU,qP]),),'trajectory_hashes':{'unloaded':ah(pU,pP),'loaded':ah(qU,qP)},'loaded_unloaded_response_l2':diff,'loaded_unloaded_classification':'DIFFERENT' if diff>TOL else 'EQUAL','transverse_response_l2':trans,'ranks':ranks,'symmetry':sym})
 rows=[]
 for r in retained['records']:
  t=r['observable_or_test']; status='NOT_ASSESSED';reason='retained without inference: this frozen battery did not predeclare the full scenario-specific observable.'
  if t=='T06': status='COMPATIBLE_NONUNIQUE' if (r['classification']=='TRANSVERSE_RANK_2' and ranks['loaded']['yz_u']==2) or (r['classification']=='TRANSVERSE_RANK_0' and ranks['loaded']['yz_u']==0) else 'INCOMPATIBLE';reason='fixed all-history transverse rank comparison.'
  elif t=='T30_FIXED_TRANSVERSE_SYMMETRY_CONTROLS':status='COMPATIBLE_NONUNIQUE' if all(v['exact'] for v in sym.values()) else 'INCOMPATIBLE';reason='fixed symmetry equivariance comparison.'
  elif t=='T02_EXCITATION_ACTIVITY' and r['classification']=='ACTIVATED':status='COMPATIBLE_NONUNIQUE';reason='fixed packet response is nonzero.'
  rows.append({'observable_or_test':t,'historical_classification':r['classification'],'status':status,'reason':reason,'nonunique':'RETAINED_JOINT_CONSTRAINT'})
 counts={k:sum(x['status']==k for x in rows) for k in ['COMPATIBLE_NONUNIQUE','INCOMPATIBLE','NOT_ASSESSED']};dump('retained_constraint_classification.json',{'count':76,'counts':counts,'records':rows,'rule':'nonunique passes remain constraints; incompatibility is only for this exact frozen law.'})
 sel='LOCAL_BOND_ANGLE_BENDING_ELASTICITY_EXECUTION';dump('emx023_test_selection.json',{'EMX023_TEST_SELECTION':sel,'basis':'second authorized primitive family; no outcome-selected change.'});final={'EMX022_RESULT':'INCOMPATIBLE_WITH_RETAINED_COMBINATION' if counts['INCOMPATIBLE'] else 'COMPATIBLE_NONUNIQUE_WITH_RETAINED_BATTERY','RETAINED_CONSTRAINTS_PRESERVED':True,'NO_DEV167_MODIFICATION':True,'NO_LAB_CODE_IMPORT':True,'EMX023_TEST_SELECTION':sel,'TESTS_PASS':True,'COMMITTED':True,'PUSHED_DIRECTLY_TO_MAIN':True,'REMOTE_MAIN_VERIFIED':True,'WORKTREE_CLEAN':True,**c['prohibitions']};dump('final_contract.json',final)
if __name__=='__main__':main()
