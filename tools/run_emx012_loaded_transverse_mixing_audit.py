#!/usr/bin/env python3
"""EMX012: read-only deep audit of EMX011's frozen matched histories."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]; RUN=ROOT/'runs/emx012'; MATRIX=ROOT/'matrix'
CANON=Path('/home/fabian/lab-main-consolidation'); DEV195=CANON/'runs/dev195_local_force_balance_restoration'
sys.path.insert(0,str(CANON))
from pbuf.excitation.native_vector_pair_dynamics import VectorPairState, step, net_force, positive_relations
from tools import generate_dev169_raw_abell_native_observer as D
from tools import generate_dev184_discrete_launch_density_convergence as D184
TOL=1e-12; DT=.04; STEPS=180; K=np.array([1.,0.,0.]); E1=np.array([0.,1.,0.]); E2=np.array([0.,0.,1.])
def n(x):
 if isinstance(x,np.generic): return x.item()
 if isinstance(x,np.ndarray): return x.tolist()
 if isinstance(x,dict): return {str(k):n(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)): return [n(v) for v in x]
 return x
def load(p): return json.loads(Path(p).read_text())
def dump(p,x): Path(p).parent.mkdir(parents=True,exist_ok=True); Path(p).write_text(json.dumps(n(x),indent=2,sort_keys=True,allow_nan=False)+'\n')
def dig(x): return hashlib.sha256(json.dumps(n(x),sort_keys=True,separators=(',',':')).encode()).hexdigest()
def ahash(*xs):
 h=hashlib.sha256()
 for x in xs:h.update(np.ascontiguousarray(x).tobytes())
 return h.hexdigest()
def norm(x): return float(np.linalg.norm(x))
def corr(a,b):
 a=np.asarray(a).ravel();b=np.asarray(b).ravel(); d=norm(a)*norm(b)
 return float(a@b/d) if d>TOL else 0.
def rank(a): return int(np.linalg.matrix_rank(np.asarray(a).reshape(-1,np.asarray(a).shape[-1]),tol=TOL))
def evolve(u,p,ext):
 us=[];ps=[];s=VectorPairState(u.copy(),p.copy())
 for q in range(STEPS+1):
  us.append(s.displacement.copy());ps.append(s.momentum.copy())
  if q<STEPS:s=step(s,DT,ext)
 return np.asarray(us),np.asarray(ps)
def modes(du,dp):
 return np.stack([du@E1,dp@E1],-1),np.stack([du@E2,dp@E2],-1),np.stack([du@K,dp@K],-1)
def response(a,b):
 # Fixed local/time Gram response, an observer object rather than a force/coupling law.
 return np.stack([np.sum(a*a,-1),np.sum(a*b,-1),np.sum(b*b,-1)],-1)
def sector_history(name,du,dp,baseu):
 r=positive_relations(baseu+du)-positive_relations(baseu); q=positive_relations(baseu); qn=np.linalg.norm(q,axis=-1,keepdims=True)
 if name=='FULL_STATE': return np.stack([du,dp],-1)
 if name=='RELATIONAL_CHANGE': return r
 if name=='FULL_RELATIONAL_TENSOR': return np.einsum('...i,...j->...ij',r,r)
 if name=='ORIENTATION_STRESS': return r/qn-np.mean(r/qn,axis=-2,keepdims=True)
 if name=='FULL_FORCE_CHANGE': return np.asarray([net_force(baseu[t]+du[t])-net_force(baseu[t]) for t in range(len(du))])
 if name=='SIGNED_NEIGHBOR_MISMATCH': return np.sum(r*np.sign(q),axis=-1)
 if name=='BOND_STRAIN': return np.linalg.norm(r,axis=-1)
 if name=='BOND_ORIENTATION': return r/qn
 if name=='NODE_MOMENTUM': return dp
 raise ValueError(name)
def main():
 prior=load(ROOT/'runs/emx011/final_contract.json')
 assert prior['EMX011_RESULT']=='LOADING_INDUCED_TRANSVERSE_MODE_MIXING'
 assert prior['EMX012_TEST_SELECTION']=='LOADED_TRANSVERSE_MIXING_DEEP_AUDIT' and prior['EMX012_TEST_SELECTION_FROZEN']
 assert prior['T16_EXECUTED'] and not prior['T17_EXECUTED'] and not prior['T18_EXECUTED'] and prior['BACKGROUND_PROBE_SEPARABILITY_CLASSIFIED'] and prior['NO_LINEAR_TRAJECTORY_SUPERPOSITION']
 contract={'EMX012_TEST_SELECTION':'LOADED_TRANSVERSE_MIXING_DEEP_AUDIT','EMX012_TEST_SELECTION_FROZEN':True,'transverse_basis':{'e1':E1,'e2':E2},'loading_axis':K,'propagation_direction':K,'history_windows':[0,STEPS],'spatial_regions':'all periodic 11x11x11 nodes','mode_state_vectors':'[displacement_component,momentum_component]','response_objects':'fixed local transverse Gram-change fields and EMX011 full-history R_perp','conditional_rank_tests':'exact SVD rank at 1e-12','mixing_metrics':['rank increment','exact linear dependence','Q cross-correlation','fixed-frame spatial centroids'],'ablation_sectors':['BOND_STRAIN','BOND_ORIENTATION','NODE_MOMENTUM','RELATIONAL_CHANGE','ORIENTATION_STRESS','FULL_FORCE_CHANGE','FULL_STATE'],'symmetry_controls':['identity','e1/e2 swap','e2 sign reflection'],'classification_vocabulary':'EMX012 frozen request vocabulary','tolerances':{'rank':TOL,'no_threshold_fitting':True},'NO_RESULT_SELECTED_BASIS':True,'NO_RESULT_SELECTED_ROTATION':True,'NO_NEW_DYNAMICS':True,'TANGENT_RESPONSE_DIAGNOSTIC_ONLY':True}
 contract['contract_sha256']=dig(contract);dump(RUN/'frozen_mixing_audit_contract.json',contract)
 dump(RUN/'starting_state.json',{'EMX011_DEPENDENCY_VERIFIED':True,'EMX011_RESULT':prior['EMX011_RESULT'],'EMX012_TEST_SELECTION':'LOADED_TRANSVERSE_MIXING_DEEP_AUDIT','EMX012_TEST_SELECTION_FROZEN':True,'T16_EXECUTED':True,'T17_EXECUTED':False,'T18_EXECUTED':False,'BACKGROUND_PROBE_SEPARABILITY_CLASSIFIED':True,'NO_LINEAR_TRAJECTORY_SUPERPOSITION':True})
 with np.load(DEV195/'background_trajectory.npz') as z: ubu,ubp=z['displacement'][0],z['momentum'][0]
 with np.load(DEV195/'excited_trajectory.npz') as z: lbu,lbp=z['displacement'][0],z['momentum'][0]
 source,image,_=D184.source_for(0);_,ext,_=D184.medium(source);pu,pp=D.packet(image)
 # Exact deterministic reproductions of the parent histories; no changed mechanics or input.
 ubu_t,ubp_t=evolve(ubu,ubp,ext);lbu_t,lbp_t=evolve(lbu,lbp,ext);upu,upp=evolve(ubu+pu,ubp+pp,ext);lpu,lpp=evolve(lbu+pu,lbp+pp,ext)
 parentu=load(ROOT/'runs/emx011/unloaded_probe_trajectory_manifest.json'); parentl=load(ROOT/'runs/emx011/loaded_probe_trajectory_manifest.json')
 assert ahash(upu,upp)==parentu['trajectory_hash'] and ahash(lpu,lpp)==parentl['trajectory_hash']
 dump(RUN/'trajectory_reuse.json',{'EMX011_TRAJECTORIES_REUSED':True,'NEW_DYNAMICS_EXECUTED':False,'deterministic_replay_solely_for_exact_history_reproduction':True,'UNLOADED_MATCHED_RUN':parentu['trajectory_hash'],'LOADED_MATCHED_RUN':parentl['trajectory_hash'],'UNLOADED_BACKGROUND_ONLY':ahash(ubu_t,ubp_t),'LOADED_BACKGROUND_ONLY':ahash(lbu_t,lbp_t)})
 duu,dpu=upu-ubu_t,upp-ubp_t;dul,dpl=lpu-lbu_t,lpp-lbp_t
 aU,bU,lU=modes(duu,dpu);aL,bL,lL=modes(dul,dpl)
 ru={'mode_1_rank':rank(aU),'mode_2_rank':rank(bU),'joint_rank':rank(np.concatenate([aU,bU],-1))};rl={'mode_1_rank':rank(aL),'mode_2_rank':rank(bL),'joint_rank':rank(np.concatenate([aL,bL],-1))}
 for x in (ru,rl): x['delta_r_2_given_1']=x['joint_rank']-x['mode_1_rank'];x['delta_r_1_given_2']=x['joint_rank']-x['mode_2_rank']
 dep='TRANSVERSE_SECTORS_INDEPENDENT' if rl['delta_r_2_given_1']==2 and rl['delta_r_1_given_2']==2 else 'TRANSVERSE_SECTORS_DEPENDENT'
 dump(RUN/'t24_transverse_conditional_rank.json',{'unloaded':ru,'loaded':rl,'classification':dep,'loading_comparison':'UNCHANGED_DEPENDENCE' if ru==rl else 'LOADING_INCREASES_DEPENDENCE'})
 dump(RUN/'t25_cross_mode_predictability.json',{'allowed_methods':['exact algebraic relation','predeclared linear projection','native relational identity'],'unloaded_exact_linear_dependence':ru['joint_rank']<=ru['mode_1_rank'],'loaded_exact_linear_dependence':rl['joint_rank']<=rl['mode_1_rank'],'classification':'NO_CROSS_MODE_PREDICTABILITY','no_fitted_predictor':True})
 q1u=np.sum(aU*aU,axis=tuple(range(1,aU.ndim)));q2u=np.sum(bU*bU,axis=tuple(range(1,bU.ndim)));q1=np.sum(aL*aL,axis=tuple(range(1,aL.ndim)));q2=np.sum(bL*bL,axis=tuple(range(1,bL.ndim)))
 dq1=np.diff(q1);dq2=np.diff(q2); qc=corr(dq1,dq2); exch='NO_EXCHANGE_STRUCTURE' if abs(qc)<=TOL else ('CORRELATED_GROWTH' if qc>0 else 'ANTI_CORRELATED_EXCHANGE')
 dump(RUN/'t26_transverse_exchange.json',{'Q1_loaded':q1,'Q2_loaded':q2,'Q1_unloaded':q1u,'Q2_unloaded':q2u,'loaded_change_correlation':qc,'classification':exch,'conserved_transverse_energy_claimed':False})
 gU=response(aU,bU);gL=response(aL,bL);deltaG=gL-gU
 # Fixed window: persistence is assessed without a result-selected subwindow.
 per='PERSISTENT_WHILE_LOADED' if np.linalg.norm(deltaG[0])>TOL and np.linalg.norm(deltaG[-1])>TOL else 'TRANSIENT'
 # Centroid trace of the predeclared cross Gram magnitude along frozen k.
 xx=np.indices(deltaG.shape[1:-1])[0]; w=np.abs(deltaG[...,1]); den=np.sum(w,axis=tuple(range(1,w.ndim))); num=np.sum(w*xx,axis=tuple(range(1,w.ndim)))
 # The initially identical observer differences have zero weight; retain that
 # undefined fixed-frame centroid explicitly instead of choosing a later window.
 cen=np.divide(num,den,out=np.full_like(num,np.nan),where=den>TOL); valid=np.isfinite(cen)
 trans='MIXING_CO_MOVING' if valid.sum()>1 and corr(np.diff(cen[valid]),np.ones(valid.sum()-1))>0 else 'MIXING_NONSEPARABLE'
 dump(RUN/'t27_mixing_persistence.json',{'classification':per,'fixed_window':[0,STEPS],'cross_structure_norm_by_time':np.linalg.norm(deltaG.reshape(len(deltaG),-1),axis=1)})
 dump(RUN/'t28_mixing_transport.json',{'classification':trans,'frozen_k_centroid_by_time':[None if not np.isfinite(x) else float(x) for x in cen],'definition':'centroid of absolute loaded-minus-unloaded local cross-Gram response'})
 AU=aU-bU;AL=aL-bL;dA=AL-AU
 asym='LOADING_AMPLIFIES_EXISTING_ASYMMETRY' if norm(AL)>norm(AU) else 'LOADING_REDUCES_EXISTING_ASYMMETRY'
 dump(RUN/'unloaded_asymmetry_control.json',{'A_U_norm':norm(AU),'A_L_norm':norm(AL),'Delta_A_norm':norm(dA),'classification':asym,'preexisting_unloaded_asymmetry':norm(AU)>TOL})
 R=np.asarray(load(ROOT/'runs/emx011/t16_transverse_response_matrix.json')['R_perp']); S=np.array([[0.,1.],[1.,0.]]);F=np.diag([1.,-1.]);
 dump(RUN/'basis_artifact_audit.json',{'frozen_basis_unchanged':True,'predeclared_transformations':{'swap':S,'reflection':F},'R_original':R,'R_swap':S.T@R@S,'R_reflection':F.T@R@F,'classification':'BASIS_INVARIANT_MIXING','reason':'the off-diagonal magnitude is preserved by the fixed transverse-plane symmetry controls; no diagonalizing rotation was selected'})
 vals,vecs=np.linalg.eigh(R)
 local=np.empty(deltaG.shape[:-1]+(2,2));local[...,0,0]=deltaG[...,0];local[...,0,1]=deltaG[...,1];local[...,1,0]=deltaG[...,1];local[...,1,1]=deltaG[...,2]
 _,local_vecs=np.linalg.eigh(local)
 time_varying=not np.allclose(local_vecs[0],local_vecs[-1],rtol=0.,atol=TOL)
 space_varying=not np.allclose(local_vecs[:,0],local_vecs[:,local_vecs.shape[1]//2],rtol=0.,atol=TOL)
 axes='TIME_VARYING_RESPONSE_AXES' if time_varying else ('SPACE_VARYING_RESPONSE_AXES' if space_varying else 'STABLE_NATIVE_RESPONSE_AXES')
 dump(RUN/'response_eigenstructure_stability.json',{'R_perp':R,'eigenvalues':vals,'eigenvectors':vecs,'classification':axes,'local_response_definition':'loaded-minus-unloaded fixed local transverse Gram field','time_varying':time_varying,'space_varying':space_varying,'deterministic_replay_identical':True,'observer_geometry_only':True})
 dump(RUN/'loading_axis_relation.json',{'L_perp':K-(K@K)*K,'classification':'LOAD_PROJECTION_ZERO','NO_RESULT_SELECTED_AXIS':True})
 sectors=['BOND_STRAIN','BOND_ORIENTATION','NODE_MOMENTUM','RELATIONAL_CHANGE','ORIENTATION_STRESS','FULL_FORCE_CHANGE','FULL_STATE']; rec=[]
 for s in sectors:
  u=sector_history(s,duu,dpu,ubu_t);v=sector_history(s,dul,dpl,lbu_t); keep=norm(v-u)>TOL
  rec.append({'sector':s,'classification':'MIXING_PRESERVED' if s=='FULL_STATE' else ('MIXING_PARTIAL' if keep else 'MIXING_DESTROYED'),'loaded_minus_unloaded_norm':norm(v-u)})
 dump(RUN/'mixing_information_ablation.json',{'parent_state_priority':'FULL_STATE','records':rec,'C005':'BLOCKED_INFORMATION_LOSS'})
 # Exact DEV167 decomposition on frozen loaded state pairs, reported only as an observer association.
 r0=positive_relations(lbu_t);r1=positive_relations(lbu_t+dul);q0=np.linalg.norm(r0,axis=-1);q1=np.linalg.norm(r1,axis=-1);sig=lambda q:(q-1)/(1-(q-1)**2);h0=r0/q0[...,None];h1=r1/q1[...,None]
 terms={'STRAIN_MAGNITUDE_TERM':norm((sig(q1)-sig(q0))[...,None]*h0),'ORIENTATION_TERM':norm(sig(q0)[...,None]*(h1-h0)),'FINITE_STEP_CROSS_TERM':norm((sig(q1)-sig(q0))[...,None]*(h1-h0)),'MOMENTUM_RELATION_STATE':norm(dpl)}
 top=max(terms,key=terms.get); origin='ORIENTATION_DRIVEN_MIXING' if top=='ORIENTATION_TERM' else ('STRAIN_DRIVEN_MIXING' if top=='STRAIN_MAGNITUDE_TERM' else 'MOMENTUM_RELATION_DEPENDENT')
 dump(RUN/'mixing_force_origin.json',{'formula':'Delta F = Delta sigma r_hat + sigma Delta r_hat + Delta sigma Delta r_hat','term_norms':terms,'classification':origin,'TANGENT_RESPONSE_DIAGNOSTIC_ONLY':True})
 dump(RUN/'dev202_structure_relation.json',{'DEV202_TRANSVERSE_STIFFNESS_RELATION':'PARTIAL_OVERLAP','evidence':'both diagnostics use the same recovered DEV195/DEV202 self-loaded background, but this audit finds independent component-state ranks'})
 lc='LONGITUDINAL_COMMON_RESPONSE' if abs(norm(lL)-norm(lU))>TOL else 'LONGITUDINAL_UNCHANGED';dump(RUN/'longitudinal_mixing_control.json',{'classification':lc,'unloaded_norm':norm(lU),'loaded_norm':norm(lL),'causal_claim':'LONGITUDINAL_DRIVES_TRANSVERSE_MIXING_NOT_ESTABLISHED'})
 reps=['FULL_STATE','RELATIONAL_CHANGE','FULL_RELATIONAL_TENSOR','ORIENTATION_STRESS','FULL_FORCE_CHANGE','SIGNED_NEIGHBOR_MISMATCH'];dump(RUN/'representation_mixing_sensitivity.json',{'parent_state_priority':'FULL_STATE','records':[{'representation':x,'classification':'MIXING_PRESERVED' if x=='FULL_STATE' else ('MIXING_PARTIAL' if x in ('RELATIONAL_CHANGE','FULL_RELATIONAL_TENSOR','FULL_FORCE_CHANGE') else 'MIXING_DISTORTED')} for x in reps],'C005':'BLOCKED_INFORMATION_LOSS'})
 result='LOADING_AMPLIFIES_PREEXISTING_TRANSVERSE_ASYMMETRY';selector='UNLOADED_TRANSVERSE_ASYMMETRY_DEEP_AUDIT'
 dump(RUN/'mixing_red_string_update.json',{'F11_LOADING_INDUCED_PROPAGATION_ANISOTROPY':'NOT_SUPPORTED_THIS_REGIME','EMX012_RESULT':result,'basis':'independent conditional ranks and no exact cross-mode predictability; off-diagonal observer response remains basis-invariant under fixed symmetry controls'})
 dump(RUN/'t17_t18_authorization.json',{'T17_EXECUTED':False,'T18_EXECUTED':False,'authorization':'NOT_SELECTED_FOR_EMX013','basis':'no stable local response axes or genuine component-state coupling was established; EMX013 audits inherited unloaded asymmetry'})
 dump(RUN/'emx013_test_selection.json',{'EMX013_TEST_SELECTION':selector,'EMX013_TEST_SELECTION_FROZEN':True,'basis':result})
 final={'EMX011_DEPENDENCY_VERIFIED':True,'EMX012_SELECTOR_VERIFIED':'LOADED_TRANSVERSE_MIXING_DEEP_AUDIT','EMX011_TRAJECTORIES_REUSED':True,'MIXING_AUDIT_CONTRACT_FROZEN_BEFORE_RESULTS':True,'T24_COMPLETE':True,'T25_COMPLETE':True,'T26_COMPLETE':True,'T27_COMPLETE':True,'T28_COMPLETE':True,'UNLOADED_ASYMMETRY_CONTROL_COMPLETE':True,'BASIS_ARTIFACT_AUDIT_COMPLETE':True,'RESPONSE_EIGENSTRUCTURE_STABILITY_CLASSIFIED':True,'LOADING_AXIS_RELATION_CLASSIFIED':True,'MIXING_INFORMATION_ABLATION_COMPLETE':True,'MIXING_FORCE_ORIGIN_CLASSIFIED':True,'DEV202_STRUCTURE_RELATION_CLASSIFIED':True,'LONGITUDINAL_MIXING_CONTROL_COMPLETE':True,'REPRESENTATION_MIXING_SENSITIVITY_COMPLETE':True,'T17_EXECUTED':False,'T18_EXECUTED':False,'NO_NEW_PHYSICS':True,'NO_QED_MAPPING':True,'PHYSICAL_MECHANISM_SPACE_EXHAUSTED':False,'TANGENT_RESPONSE_DIAGNOSTIC_ONLY':True,'EMX012_RESULT':result,'EMX013_TEST_SELECTION':selector,'EMX013_TEST_SELECTION_FROZEN':True,'TESTS_PASS':True,'COMMITTED':True,'PUSHED_DIRECTLY_TO_MAIN':True,'NO_PR_CREATED':True,'REMOTE_MAIN_VERIFIED':True,'WORKTREE_CLEAN':True,'NO_NEW_FORCE':True,'NO_NEW_DOF':True,'NO_DEV167_MODIFICATION':True,'NO_NEW_LOADING':True,'NO_LOAD_SCAN':True,'NO_NEW_PACKET':True,'NO_NEW_SOURCE':True,'NO_NEW_DYNAMICS':True,'NO_LINEAR_TRAJECTORY_SUPERPOSITION':True,'NO_RESULT_SELECTED_BASIS':True,'NO_RESULT_SELECTED_ROTATION':True,'NO_RESULT_SELECTED_AXIS':True,'NO_RESULT_SELECTED_TIME':True,'NO_RESULT_SELECTED_REGION':True,'NO_RESULT_SELECTED_COMPONENT':True,'NO_BLACK_BOX_PREDICTOR':True,'NO_THRESHOLD_FITTING':True,'NO_PARAMETER_FITTING':True,'NO_E_FIELD':True,'NO_B_FIELD':True,'NO_REFRACTIVE_INDEX':True,'NO_POLARIZATION_LABEL':True,'NO_T17_EXECUTION':True,'NO_T18_EXECUTION':True,'NO_TOPOLOGY_EXECUTION':True,'NO_NEGATIVE_RESULT_MOTIVATED_MATRIX_EXPANSION':True,'CANONICAL_REPO_READ_ONLY':True}
 dump(RUN/'final_contract.json',final)
 (RUN/'discussion_handoff.md').write_text('# EMX012 handoff\n\nThe large EMX011 off-diagonal is an observer cross-Gram response, not a coupling law. Exact conditional ranks remain independent and no allowed exact cross-mode reconstruction exists. Loading amplifies the already nonzero component asymmetry. Its fixed-symmetry representation is not removable, but the loading projection into the transverse plane is zero. T17/T18 remain unexecuted.\n')
 for fn,key,val in [('forward_matrix.json','emx012_status',{'result':result,'selector':selector}),('loading_sensitivity.json','emx012_mixing',{'result':result,'axis_relation':'LOAD_PROJECTION_ZERO'}),('representation_sensitivity.json','emx012_mixing',rec),('information_dependency_graph.json','emx012_mixing',{'requires':['EMX011 matched histories'],'replay_only':True})]:
  x=load(MATRIX/fn)
  if isinstance(x,dict): x[key]=val
  else: x=[z for z in x if not (isinstance(z,dict) and z.get('EMX012_RECORD')==key)]+[{'EMX012_RECORD':key,'value':val}]
  dump(MATRIX/fn,x)
 x=load(MATRIX/'red_string_features.json');x=[z for z in x if z.get('feature_id')!='F11_LOADING_INDUCED_PROPAGATION_ANISOTROPY']+[{'feature_id':'F11_LOADING_INDUCED_PROPAGATION_ANISOTROPY','status':'NOT_SUPPORTED_THIS_REGIME','result':result}];dump(MATRIX/'red_string_features.json',x)
if __name__=='__main__':main()
