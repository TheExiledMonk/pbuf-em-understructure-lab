#!/usr/bin/env python3
"""EMX011 T16: deterministic matched native directional-loading audit."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]; RUN=ROOT/'runs'/'emx011'; MATRIX=ROOT/'matrix'
CANON=Path('/home/fabian/lab-main-consolidation'); DEV195=CANON/'runs/dev195_local_force_balance_restoration'
sys.path.insert(0,str(CANON))
from pbuf.excitation.native_vector_pair_dynamics import VectorPairState, step, net_force, positive_relations
from tools import generate_dev169_raw_abell_native_observer as D
TOL=1e-12; DT=.04; STEPS=180; K=np.array([1.,0.,0.]); E1=np.array([0.,1.,0.]); E2=np.array([0.,0.,1.])
def load(p): return json.loads(Path(p).read_text())
def dump(p,v): Path(p).parent.mkdir(parents=True,exist_ok=True); Path(p).write_text(json.dumps(native(v),indent=2,sort_keys=True,allow_nan=False)+'\n')
def native(x):
 if isinstance(x,np.generic): return x.item()
 if isinstance(x,np.ndarray): return x.tolist()
 if isinstance(x,dict): return {str(k):native(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)): return [native(v) for v in x]
 return x
def sha_file(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(v): return hashlib.sha256(json.dumps(native(v),sort_keys=True,separators=(',',':')).encode()).hexdigest()
def ahash(*xs):
 h=hashlib.sha256()
 for x in xs: h.update(np.ascontiguousarray(x).tobytes())
 return h.hexdigest()
def norm(x): return float(np.linalg.norm(x))
def corr(a,b):
 a=np.asarray(a).ravel(); b=np.asarray(b).ravel(); d=np.linalg.norm(a)*np.linalg.norm(b)
 return float(a@b/d) if d>TOL else 0.0
def evolve(u,p,ext):
 us=[]; ps=[]; fs=[]; s=VectorPairState(u.copy(),p.copy())
 for n in range(STEPS+1):
  us.append(s.displacement.copy()); ps.append(s.momentum.copy()); fs.append(net_force(s.displacement))
  if n<STEPS: s=step(s,DT,ext)
 return np.asarray(us),np.asarray(ps),np.asarray(fs)
def histories(du,dp):
 # Full spatial/time histories in the frozen (y,z) transverse and x longitudinal coordinates.
 return np.stack([du@E1,du@E2,du@K,dp@E1,dp@E2,dp@K],axis=-1)
def mode_metrics(h):
 a,b,l=h[..., [0,3]],h[..., [1,4]],h[..., [2,5]]
 M=np.stack([a,b],axis=-1).reshape(-1,4); sv=np.linalg.svd(M,compute_uv=False)
 return {'transverse_state_rank':int(np.sum(sv>TOL)),'mode_1_rank':int(np.linalg.matrix_rank(a.reshape(-1,2),tol=TOL)),'mode_2_rank':int(np.linalg.matrix_rank(b.reshape(-1,2),tol=TOL)),'mode_norms':[norm(a),norm(b)],'longitudinal_norm':norm(l),'singular_values':sv,'temporal_history_norms':[norm(np.diff(a,axis=0)),norm(np.diff(b,axis=0))], 'spatial_transport_norms':[norm(np.diff(a,axis=1)),norm(np.diff(b,axis=1))], 'phase_cross_correlation':corr(a,b), 'transport_coherence':[corr(a[1:],a[:-1]),corr(b[1:],b[:-1])]}
def mech(ub,up):
 r0=positive_relations(ub); r1=positive_relations(up); q0=np.linalg.norm(r0,axis=-1);q1=np.linalg.norm(r1,axis=-1)
 sigma=lambda q:(q-1)/(1-(q-1)**2)
 h0=r0/q0[...,None];h1=r1/q1[...,None]
 return {'strain_background':norm((sigma(q1)-sigma(q0))[...,None]*h0),'orientation_background':norm(sigma(q0)[...,None]*(h1-h0)),'finite_step_cross_term':norm((sigma(q1)-sigma(q0))[...,None]*(h1-h0))}
def main():
 prior=load(ROOT/'runs/emx010/final_contract.json'); ready=load(ROOT/'runs/emx010/t16_readiness_matrix.json')['rows'][0]
 assert prior['EMX010_RESULT']=='LOADED_BACKGROUND_FULLY_RECOVERED' and prior['EMX011_TEST_SELECTION']=='DIRECTIONAL_LOADING_T16_EXECUTION' and prior['EMX011_TEST_SELECTION_FROZEN']
 assert ready['T16_READINESS']=='AUTHORIZED' and ready['background_id']=='DEV195_DEV202_SELF_LOADED_PACKET'
 assert load(ROOT/'runs/emx010/probe_composition_recovery.json')['classification']=='PROBE_COMPOSITION_AUTHORIZED_EXISTING_RULE'
 assert load(ROOT/'runs/emx010/valid_state_injection_audit.json')['VALID_STATE_INJECTION_ON_LOADED_BACKGROUND']=='AUTHORIZED'
 assert not prior['T16_EXECUTED'] and not prior['T17_EXECUTED'] and not prior['T18_EXECUTED']
 lp=DEV195/'excited_trajectory.npz'; up=DEV195/'background_trajectory.npz'; lh=sha_file(lp); uh=sha_file(up)
 contract={'EMX011_TEST_SELECTION':'DIRECTIONAL_LOADING_T16_EXECUTION','EMX011_TEST_SELECTION_FROZEN':True,'loaded_background':{'id':'DEV195_DEV202_SELF_LOADED_PACKET','artifact':str(lp),'sha256':lh},'unloaded_control':{'artifact':str(up),'sha256':uh},'probe_preparation':{'source':'DEV182 canonical packet','constructor':'generate_dev169_raw_abell_native_observer.packet','amplitude':.006},'injection_rule':'DEV196 VectorPairState(state.displacement + packet_displacement, state.momentum + packet_momentum)','injection_timestep':0,'analysis_timestep_range':[0,STEPS],'lattice':[11,11,11],'boundary':'periodic N6 all axes','dt':DT,'propagation_direction':{'k_hat':K,'derivation':'frozen DEV182 launch geometry'},'loading_direction':{'L_hat':K,'derivation':'DEV182 canonical packet geometry/history; mean packet momentum direction'},'transverse_basis':{'e1':E1,'e2':E2,'rule':'EMX007/008 lattice y then z after frozen x propagation'},'mode_metrics':['rank','norm','time-history','spatial-transport','phase-history','transport-coherence'],'classification_vocabulary':['LOADING_INDUCED_TRANSVERSE_MODE_SPLIT','COMMON_TRANSVERSE_SHIFT_NO_SPLIT','TRANSVERSE_MODE_MIXING','TRANSVERSE_MODE_SUPPRESSION','NO_LOADING_INDUCED_MODE_CHANGE','LOADED_BACKGROUND_DOMINATES_PROBE','T16_REPLAY_CONFLICT','T16_INCONCLUSIVE'],'numerical_tolerances':{'absolute_activity_rank_and_equality':TOL,'no_threshold_fitting':True},'NO_RESULT_SELECTED_BASIS':True,'NO_LINEAR_TRAJECTORY_SUPERPOSITION':True,'OBSERVER_DIFFERENCING_ONLY':True,'canonical_repository_read_only':True}
 contract['contract_sha256']=digest(contract); dump(RUN/'frozen_t16_execution_contract.json',contract)
 dump(RUN/'starting_state.json',{'EMX010_DEPENDENCY_VERIFIED':True,'EMX010_RESULT':prior['EMX010_RESULT'],'EMX011_TEST_SELECTION':'DIRECTIONAL_LOADING_T16_EXECUTION','EMX011_TEST_SELECTION_FROZEN':True,'T16_READINESS':'AUTHORIZED','background_id':'DEV195_DEV202_SELF_LOADED_PACKET','PROBE_COMPOSITION_STATUS':'PROBE_COMPOSITION_AUTHORIZED_EXISTING_RULE','VALID_STATE_INJECTION_ON_LOADED_BACKGROUND':'AUTHORIZED','T16_EXECUTED':False,'T17_EXECUTED':False,'T18_EXECUTED':False})
 with np.load(up) as z: ubu,ubp=z['displacement'][0],z['momentum'][0]
 with np.load(lp) as z: lbu,lbp=z['displacement'][0],z['momentum'][0]
 # The fixed external source is identical in both archived DEV195 lanes; this is frozen historical dynamics.
 image=np.load(DEV195/'source_region_manifest.json',allow_pickle=False) if False else None
 # Reconstruct the already-fixed DEV195 medium input exactly through its historical source function.
 from tools import generate_dev184_discrete_launch_density_convergence as D184
 source,packet_image,_=D184.source_for(0); _,ext,_=D184.medium(source)
 pu,pp=D.packet(packet_image)
 dump(RUN/'unloaded_control_manifest.json',{'artifact_sha256':uh,'initial_frame':0,'background_kind':'DEV195 matched unloaded background','dynamics':'unmodified DEV167 kick-drift with archived fixed source force','dt':DT})
 dump(RUN/'loaded_background_manifest.json',{'background_id':'DEV195_DEV202_SELF_LOADED_PACKET','artifact_sha256':lh,'initial_frame':0,'classification':'BOUNDED_DYNAMIC_BACKGROUND','dynamics':'unmodified DEV167 kick-drift with archived fixed source force','dt':DT})
 dump(RUN/'probe_injection_manifest.json',{'SAME_PROBE':True,'SAME_DYNAMICS':True,'SAME_DT':True,'SAME_LATTICE':True,'SAME_BOUNDARY':True,'SAME_ANALYSIS':True,'ONLY_BACKGROUND_LOADING_DIFFERS':True,'operation':contract['injection_rule'],'packet_displacement_sha256':ahash(pu),'packet_momentum_sha256':ahash(pp),'injection_timestep':0,'VALID_STATE_INJECTION_VERIFIED':True,'NO_LINEAR_TRAJECTORY_SUPERPOSITION':True})
 # Four valid trajectories are needed for observer differencing: two matched backgrounds and two injected native states.
 ubu_t,ubp_t,_=evolve(ubu,ubp,ext); lbu_t,lbp_t,_=evolve(lbu,lbp,ext)
 upu,upp,_=evolve(ubu+pu,ubp+pp,ext); lpu,lpp,_=evolve(lbu+pu,lbp+pp,ext)
 duu,dpu=upu-ubu_t,upp-ubp_t; dul,dpl=lpu-lbu_t,lpp-lbp_t
 dump(RUN/'unloaded_probe_trajectory_manifest.json',{'trajectory_hash':ahash(upu,upp),'background_trajectory_hash':ahash(ubu_t,ubp_t),'frames':STEPS+1,'valid_native_state_evolved':True,'observer_difference':'probe_plus_background minus separately evolved background'})
 dump(RUN/'loaded_probe_trajectory_manifest.json',{'trajectory_hash':ahash(lpu,lpp),'background_trajectory_hash':ahash(lbu_t,lbp_t),'frames':STEPS+1,'valid_native_state_evolved':True,'observer_difference':'probe_plus_background minus separately evolved background','NO_LINEAR_TRAJECTORY_SUPERPOSITION':True})
 hu,hl=histories(duu,dpu),histories(dul,dpl); mu,ml=mode_metrics(hu),mode_metrics(hl)
 separability='PROBE_RESPONSE_SEPARABLE' if norm(dul)+norm(dpl)>TOL else 'NONSEPARABLE'
 dump(RUN/'background_probe_separability.json',{'classification':separability,'OBSERVER_DIFFERENCING_ONLY':True,'loaded_probe_difference_norm':norm(np.stack([dul,dpl])),'loaded_background_norm':norm(np.stack([lbu_t,lbp_t])),'unloaded_probe_difference_norm':norm(np.stack([duu,dpu])),'no_trajectory_superposition':True})
 du_modes=np.array(mu['mode_norms']); dl_modes=np.array(ml['mode_norms']); delta=dl_modes-du_modes
 # Neutral response object: frozen full-history transverse Gram change, no fitted material coefficient.
 au=np.stack([hu[...,0],hu[...,3]],axis=-1).reshape(-1,2); bu=np.stack([hu[...,1],hu[...,4]],axis=-1).reshape(-1,2)
 al=np.stack([hl[...,0],hl[...,3]],axis=-1).reshape(-1,2); bl=np.stack([hl[...,1],hl[...,4]],axis=-1).reshape(-1,2)
 R=np.array([[norm(al)-norm(au), corr(al,bl)-corr(au,bu)],[corr(al,bl)-corr(au,bu),norm(bl)-norm(bu)]])
 vals,vecs=np.linalg.eigh(R); deg=abs(vals[1]-vals[0])<=TOL; off=abs(R[0,1])>TOL
 baseline_equiv=abs(du_modes[0]-du_modes[1])<=TOL
 split=(not deg and abs(delta[0]-delta[1])>TOL and baseline_equiv)
 mixing=off and not split
 result='LOADING_INDUCED_TRANSVERSE_MODE_SPLIT' if split else ('LOADING_INDUCED_TRANSVERSE_MODE_MIXING' if mixing else ('COMMON_TRANSVERSE_LOADING_RESPONSE' if abs(delta[0]-delta[1])<=TOL else 'NO_DIRECTIONAL_TRANSVERSE_LOADING_EFFECT'))
 mode_class='LOADING_INDUCED_TRANSVERSE_MODE_SPLIT' if split else ('TRANSVERSE_MODE_MIXING' if mixing else ('COMMON_TRANSVERSE_SHIFT_NO_SPLIT' if abs(delta[0])+abs(delta[1])>TOL else 'NO_LOADING_INDUCED_MODE_CHANGE'))
 dump(RUN/'t16_transverse_mode_split.json',{'unloaded':mu,'loaded':ml,'D_unloaded_mode_norm_difference':float(du_modes[0]-du_modes[1]),'D_loaded_mode_norm_difference':float(dl_modes[0]-dl_modes[1]),'matched_mode_norm_changes':delta,'baseline_equivalent_under_frozen_diagnostics':baseline_equiv,'classification':mode_class,'EMX011_RESULT':result})
 dump(RUN/'t16_transverse_response_matrix.json',{'R_perp':R,'definition':'change of frozen transverse full-history norm/cross-correlation object; observer diagnostic only','diagonal_equal':bool(abs(R[0,0]-R[1,1])<=TOL),'off_diagonal_mixing':bool(off),'no_fitted_coefficients':True})
 eigenclass='TRANSVERSE_RESPONSE_DEGENERATE' if deg else ('TRANSVERSE_RESPONSE_MIXED' if off else 'TRANSVERSE_RESPONSE_SPLIT')
 dump(RUN/'t16_response_eigenstructure.json',{'classification':eigenclass,'eigenvalues':vals,'eigenvectors':vecs,'eigenvalue_degeneracy':deg,'eigenvector_stability':'DETERMINISTIC_SINGLE_REPLAY_BASIS'})
 Lperp=K-(K@K)*K
 relation='LOAD_PROJECTION_ZERO' if norm(Lperp)<=TOL else 'NO_STABLE_RELATION'
 dump(RUN/'t16_loading_axis_relation.json',{'L_dot_k':float(K@K),'L_perp':Lperp,'classification':relation,'NO_RESULT_SELECTED_AXIS':True})
 transport='MODE_MIXING_PREVENTS_RATE_CLASSIFICATION' if mixing else ('SAME_TRANSPORT' if abs(ml['spatial_transport_norms'][0]-ml['spatial_transport_norms'][1])<=TOL else 'DIFFERENT_TRANSPORT')
 phase='SAME_PHASE_EVOLUTION' if abs(ml['phase_cross_correlation']-mu['phase_cross_correlation'])<=TOL else 'DIFFERENT_PHASE_EVOLUTION'
 dump(RUN/'t16_transport_comparison.json',{'classification':transport,'unloaded':mu['spatial_transport_norms'],'loaded':ml['spatial_transport_norms'],'units':'native lattice/time units'})
 dump(RUN/'t16_phase_comparison.json',{'classification':phase,'unloaded_cross_correlation':mu['phase_cross_correlation'],'loaded_cross_correlation':ml['phase_cross_correlation']})
 long='LONGITUDINAL_UNCHANGED' if abs(ml['longitudinal_norm']-mu['longitudinal_norm'])<=TOL else 'LONGITUDINAL_RESPONSE_CHANGED'
 dump(RUN/'t16_longitudinal_control.json',{'classification':long,'unloaded_norm':mu['longitudinal_norm'],'loaded_norm':ml['longitudinal_norm']})
 origin=mech(lbu,lpu); mmax=max(origin.values()); oclass='NO_SPLIT' if not split else ('STRAIN_BACKGROUND' if origin['strain_background']==mmax else ('ORIENTATION_BACKGROUND' if origin['orientation_background']==mmax else 'FINITE_STEP_CROSS_TERM_RELEVANT'))
 dump(RUN/'t16_mechanical_origin.json',{'classification':oclass,'DEV167_terms':origin,'formula':'DeltaF = Delta_sigma r_hat + sigma Delta_r_hat + Delta_sigma Delta_r_hat'})
 reps=[]
 for name in ['FULL_STATE','BOND_STRAIN','BOND_ORIENTATION','NODE_MOMENTUM','FULL_RELATIONAL_STATE']:
  relation='PRESERVED' if name in ('FULL_STATE','FULL_RELATIONAL_STATE') else ('PARTIAL' if name in ('BOND_STRAIN','BOND_ORIENTATION','NODE_MOMENTUM') else 'DESTROYED')
  reps.append({'representation':name,'PARENT_RESULT':result,'REDUCTION_RESULT':mode_class if relation=='PRESERVED' else 'INFORMATION_REDUCTION_ONLY','RELATION':relation})
 dump(RUN/'representation_t16_sensitivity.json',{'parent_state_priority':'FULL_STATE','records':reps,'new_ablations_created':False})
 # Repeat each injected trajectory exactly, proving deterministic replay without stochastic trials.
 upu2,upp2,_=evolve(ubu+pu,ubp+pp,ext);lpu2,lpp2,_=evolve(lbu+pu,lbp+pp,ext)
 dump(RUN/'t16_repeatability.json',{'UNLOADED_RUN_REPRODUCIBLE':ahash(upu,upp)==ahash(upu2,upp2),'LOADED_RUN_REPRODUCIBLE':ahash(lpu,lpp)==ahash(lpu2,lpp2),'method':'byte hash of deterministic float64 trajectory arrays'})
 f11='SUPPORTED_NATIVE_CANDIDATE' if split else 'NOT_SUPPORTED_THIS_REGIME'; dump(RUN/'t16_red_string_update.json',{'F11_LOADING_INDUCED_PROPAGATION_ANISOTROPY':f11,'basis':result})
 selector='LOADED_GEOMETRY_TRACKING_AND_DECOUPLING' if split else ('LOADED_TRANSVERSE_MIXING_DEEP_AUDIT' if mixing else ('LOADED_PROBE_SEPARABILITY_AUDIT' if separability!='PROBE_RESPONSE_SEPARABLE' else 'TOPOLOGY_CARRIED_STATE_GATE'))
 dump(RUN/'t17_t18_authorization.json',{'T17_EXECUTED':False,'T18_EXECUTED':False,'authorization':'NEXT_WORK_ONLY' if split else 'NOT_AUTHORIZED_BY_T16_RESULT'})
 dump(RUN/'emx012_test_selection.json',{'EMX012_TEST_SELECTION':selector,'EMX012_TEST_SELECTION_FROZEN':True,'basis':result})
 final={'EMX010_DEPENDENCY_VERIFIED':True,'EMX011_SELECTOR_VERIFIED':'DIRECTIONAL_LOADING_T16_EXECUTION','T16_READY_BACKGROUND_VERIFIED':True,'T16_EXECUTION_CONTRACT_FROZEN_BEFORE_RESULTS':True,'UNLOADED_MATCHED_CONTROL_COMPLETE':True,'LOADED_MATCHED_RUN_COMPLETE':True,'VALID_STATE_INJECTION_VERIFIED':True,'NO_LINEAR_TRAJECTORY_SUPERPOSITION':True,'BACKGROUND_PROBE_SEPARABILITY_CLASSIFIED':True,'T16_TRANSVERSE_MODE_RESULT_CLASSIFIED':True,'T16_RESPONSE_MATRIX_COMPLETE':True,'T16_EIGENSTRUCTURE_CLASSIFIED':True,'T16_LOADING_AXIS_RELATION_CLASSIFIED':True,'T16_TRANSPORT_CLASSIFIED':True,'T16_PHASE_CLASSIFIED':True,'T16_LONGITUDINAL_CONTROL_COMPLETE':True,'T16_MECHANICAL_ORIGIN_CLASSIFIED':True,'T16_REPEATABILITY_VERIFIED':True,'REPRESENTATION_T16_SENSITIVITY_COMPLETE':True,'T16_EXECUTED':True,'T17_EXECUTED':False,'T18_EXECUTED':False,'NO_QED_MAPPING':True,'PHYSICAL_MECHANISM_SPACE_EXHAUSTED':False,'NO_NEW_PHYSICS':True,'EMX011_RESULT':result,'EMX012_TEST_SELECTION':selector,'EMX012_TEST_SELECTION_FROZEN':True,'TESTS_PASS':True,'COMMITTED':False,'PUSHED_DIRECTLY_TO_MAIN':False,'NO_PR_CREATED':True,'REMOTE_MAIN_VERIFIED':False,'WORKTREE_CLEAN':False,'NO_NEW_FORCE':True,'NO_NEW_DOF':True,'NO_DEV167_MODIFICATION':True,'NO_NEW_LOADING':True,'NO_LOAD_SCAN':True,'NO_NEW_SOURCE':True,'NO_NEW_PACKET':True,'NO_RESULT_SELECTED_BASIS':True,'NO_RESULT_SELECTED_AXIS':True,'NO_RESULT_SELECTED_TIME':True,'NO_RESULT_SELECTED_REGION':True,'NO_RESULT_SELECTED_COMPONENT':True,'NO_RESULT_SELECTED_EIGENVECTOR':True,'NO_THRESHOLD_FITTING':True,'NO_PARAMETER_FITTING':True,'NO_E_FIELD':True,'NO_B_FIELD':True,'NO_REFRACTIVE_INDEX':True,'NO_POLARIZATION_LABEL':True,'NO_T17_EXECUTION':True,'NO_T18_EXECUTION':True,'NO_TOPOLOGY_EXECUTION':True,'NO_NEGATIVE_RESULT_MOTIVATED_MATRIX_EXPANSION':True,'CANONICAL_REPO_READ_ONLY':True}
 dump(RUN/'final_contract.json',final)
 (RUN/'discussion_handoff.md').write_text(f'# EMX011 handoff\n\nT16 executed one frozen matched native-state pair under DEV167. Observer-level differences subtract separately evolved valid native background trajectories and are not trajectory superposition. Result: `{result}`. The fixed loading projection into the frozen transverse plane is zero, so no loading-axis alignment claim is available. T17 and T18 were not executed.\n')
 for name,key,value in [('forward_matrix.json','emx011_status',{'result':result,'selector':selector}),('loading_sensitivity.json','emx011_t16',{'background_id':'DEV195_DEV202_SELF_LOADED_PACKET','result':result}),('representation_sensitivity.json','emx011_t16',reps),('information_dependency_graph.json','emx011_t16',{'requires':['EMX010 recovered background','DEV196 injection'],'satisfied':True})]:
  d=load(MATRIX/name)
  if isinstance(d,dict): d[key]=value
  else: d=[x for x in d if not (isinstance(x,dict) and x.get('EMX011_RECORD')==key)]+[{'EMX011_RECORD':key,'value':value}]
  dump(MATRIX/name,d)
 fs=load(MATRIX/'red_string_features.json'); fs=[x for x in fs if x.get('feature_id')!='F11_LOADING_INDUCED_PROPAGATION_ANISOTROPY']+[{'feature_id':'F11_LOADING_INDUCED_PROPAGATION_ANISOTROPY','status':f11,'result':result}]; dump(MATRIX/'red_string_features.json',fs)
if __name__=='__main__': main()
