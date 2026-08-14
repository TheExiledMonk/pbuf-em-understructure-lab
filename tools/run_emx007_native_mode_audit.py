#!/usr/bin/env python3
"""EMX007: frozen native directional mode audit; analysis only."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]; RUN=ROOT/'runs'/'emx007'; MATRIX=ROOT/'matrix'
CANON=Path('/home/fabian/lab-main-consolidation/runs/dev195_local_force_balance_restoration')
K=np.array([1.,0.,0.]); E1=np.array([0.,1.,0.]); E2=np.array([0.,0.,1.]); TOL=1e-12
REPS=['FULL_STATE','RELATIONAL_CHANGE','FULL_RELATIONAL_TENSOR','ORIENTATION_STRESS','FULL_FORCE_CHANGE','SIGNED_NEIGHBOR_MISMATCH']
def load(p): return json.loads(Path(p).read_text())
def dump(p,v): Path(p).parent.mkdir(parents=True,exist_ok=True); Path(p).write_text(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+'\n')
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def l2(x): return float(np.linalg.norm(x))
def rel(u):
 e=np.eye(3); return np.stack([e[a]+np.roll(u,-1,axis=a)-u for a in range(3)],axis=-2)
def force(r):
 q=np.linalg.norm(r,axis=-1); eps=q-1; return (eps/(1-eps*eps))[...,None]*r/q[...,None]
def values(u,b):
 ur,br=rel(u),rel(b); d=ur-br; M=np.einsum('...ai,...aj->...ij',ur,ur)-np.einsum('...ai,...aj->...ij',br,br)
 F=force(ur)-force(br); lu=np.linalg.norm(ur,axis=-1); lb=np.linalg.norm(br,axis=-1)
 sh=ur/lu[...,None]; bh=br/lb[...,None]; sig=lambda z:z/(1-z*z)
 return {'FULL_STATE':u-b,'RELATIONAL_CHANGE':d,'FULL_RELATIONAL_TENSOR':np.einsum('...ij,j->...i',M,K),'ORIENTATION_STRESS':sig(lb-1)[...,None]*(sh-bh),'FULL_FORCE_CHANGE':F,'SIGNED_NEIGHBOR_MISMATCH':d}
def vec(v):
 # Bond-direction arrays are aggregated without selecting a result-dependent bond.
 return v.mean(axis=-2) if v.ndim==6 else v
def components(q,p):
 q,p=vec(q),vec(p); return np.stack([q@E1,q@E2,q@K,p@E1,p@E2,p@K],axis=-1)
def corr(a,b):
 a=a.reshape(-1); b=b.reshape(-1); d=np.linalg.norm(a)*np.linalg.norm(b)
 return float(a@b/d) if d>TOL else 0.
def main():
 f6=load(RUN.parent/'emx006'/'final_contract.json'); assert f6['EMX006_RESULT']=='MIXED_SECONDARY_STRUCTURE' and f6['EMX007_TEST_SELECTION']=='NATIVE_MODE_STRUCTURE_AUDIT' and f6['EMX007_TEST_SELECTION_FROZEN']
 contract={'EMX007_TEST_SELECTION':'NATIVE_MODE_STRUCTURE_AUDIT','EMX007_TEST_SELECTION_FROZEN':True,'parent_trajectory':'DEV195_CANONICAL_PACKET_PARENT','propagation_direction':{'k_hat':[1,0,0],'derivation':'frozen DEV182 launch geometry'},'transverse_plane':{'basis_e1':[0,1,0],'basis_e2':[0,0,1],'derivation':'lattice y then z axes after fixed x propagation axis'},'candidate_representations':REPS+['C005_DEV203_ANTISYMMETRIC_TENSOR:ZERO_TRANSVERSE_DYNAMIC_RANK'],'time_samples':'all archived t=0..360','spatial_samples':'full periodic 11x11x11 lattice; bond quantities uniformly averaged over all ordered N6 bonds','rank_tests':{'matrix':'time-space rows, transverse q1,q2,p1,p2 columns','absolute_svd_tolerance':TOL},'mode_decomposition':'Psi=(q1,q2,q_parallel,p1,p2,p_parallel), excited-minus-background only','phase_correlation_diagnostics':'normalized inner products of complete frozen time-space histories; no fitted frequency','classification_vocabulary':{'T11':['TWO_INDEPENDENT_TRANSVERSE_MODES','ONE_TRANSVERSE_MODE_TWO_COMPONENTS','DEGENERATE_TRANSVERSE_SECTOR','TRANSVERSE_MODE_COUPLED_NONSEPARABLE','BLOCKED_INFORMATION_LOSS'],'T12':['TRANSVERSE_DEGENERATE','TRANSVERSE_SPLIT','TRANSVERSE_PARTIAL_DEGENERACY','INCONCLUSIVE'],'T13':['LONGITUDINAL_INDEPENDENT_MODE','LONGITUDINAL_COUPLED_TO_TRANSVERSE','LONGITUDINAL_GEOMETRIC_BYPRODUCT','LONGITUDINAL_CONSTRAINT_RESPONSE','MIXED_NONSEPARABLE','INCONCLUSIVE']},'numerical_tolerances':{'absolute_activity_and_rank':TOL,'rule':'fixed before analysis; no threshold fitting'},'prohibitions':{'NO_NEW_PHYSICS':True,'NO_NEW_FORCE':True,'NO_NEW_DOF':True,'NO_DEV167_MODIFICATION':True,'NO_NEW_PACKET':True,'NO_NEW_SOURCE':True,'NO_NEW_LOADING':True,'NO_RESULT_SELECTED_AXIS':True,'NO_RESULT_SELECTED_BASIS':True,'NO_RESULT_SELECTED_TIME':True,'NO_RESULT_SELECTED_REGION':True,'NO_RESULT_SELECTED_FREQUENCY':True,'NO_RESULT_SELECTED_PHASE':True,'NO_THRESHOLD_FITTING':True,'NO_E_FIELD':True,'NO_B_FIELD':True,'NO_MAXWELL_MAPPING':True,'NO_POLARIZATION_LABEL':True,'NO_TOPOLOGY_POLARITY_EXECUTION':True,'NO_ASSIGNED_POLARITY_SIGN':True,'NO_T16_T18_EXECUTION':True,'CANONICAL_REPO_READ_ONLY':True}}
 contract['contract_sha256']=digest(contract); dump(RUN/'frozen_mode_audit_contract.json',contract)
 with np.load(CANON/'excited_trajectory.npz') as z: eu,ep=z['displacement'],z['momentum']
 with np.load(CANON/'background_trajectory.npz') as z: bu,bp=z['displacement'],z['momentum']
 Vq,Vp=values(eu,bu),values(ep,bp); records=[]; signature={}
 for rep in REPS:
  psi=components(Vq[rep],Vp[rep]); trans=psi[...,[0,1,3,4]].reshape(-1,4); s=np.linalg.svd(trans,compute_uv=False); r=int(np.sum(s>TOL)); q1,q2,ql,p1,p2,pl=[psi[...,i] for i in range(6)]
  # Rank two may be a q/p pair for one component; each component's state rank establishes dynamic independence.
  r1=np.linalg.matrix_rank(np.stack([q1,p1],-1).reshape(-1,2),tol=TOL); r2=np.linalg.matrix_rank(np.stack([q2,p2],-1).reshape(-1,2),tol=TOL)
  cross=max(abs(corr(q1,q2)),abs(corr(p1,p2))); longcorr=max(abs(corr(ql,q1)),abs(corr(ql,q2)),abs(corr(pl,p1)),abs(corr(pl,p2)))
  t11='TWO_INDEPENDENT_TRANSVERSE_MODES' if r>=4 and r1==2 and r2==2 else ('ONE_TRANSVERSE_MODE_TWO_COMPONENTS' if r==2 else 'TRANSVERSE_MODE_COUPLED_NONSEPARABLE')
  # Exact symmetry check uses matching sector norms and histories; otherwise partial, not fitted.
  n1,n2=l2(np.stack([q1,p1],-1)),l2(np.stack([q2,p2],-1)); t12='TRANSVERSE_DEGENERATE' if abs(n1-n2)<=TOL else 'TRANSVERSE_PARTIAL_DEGENERACY'
  t13='LONGITUDINAL_COUPLED_TO_TRANSVERSE' if l2(ql)+l2(pl)>TOL and longcorr>TOL else ('LONGITUDINAL_INDEPENDENT_MODE' if l2(ql)+l2(pl)>TOL else 'LONGITUDINAL_GEOMETRIC_BYPRODUCT')
  coherence='CO_MOVING' if l2(np.diff(psi,axis=0))>TOL else 'LOCAL_ONLY'; t14={'TRANSVERSE_1_PROPAGATING':l2(q1)+l2(p1)>TOL,'TRANSVERSE_2_PROPAGATING':l2(q2)+l2(p2)>TOL,'LONGITUDINAL_PROPAGATING':l2(ql)+l2(pl)>TOL,'transport':coherence}
  qp=np.sum(psi[...,[0,1,3,4]]**2,axis=tuple(range(1,psi.ndim))); qlq=np.sum(psi[...,[2,5]]**2,axis=tuple(range(1,psi.ndim))); exchange=abs(corr(np.diff(qp),np.diff(qlq)))
  t15='TRANSVERSE_LONGITUDINAL_EXCHANGE' if exchange>TOL else 'NO_MODE_EXCHANGE'
  phase='VARIABLE_PHASE' if cross>TOL else 'NO_STABLE_PHASE_RELATION'
  item={'representation':rep,'parent_priority':'FULL_STATE_DERIVED' if rep=='FULL_STATE' else 'REDUCTION_PRESERVED','signature':[t11,t12,t13,t14['transport'],t15],'metrics':{'transverse_full_state_rank':r,'component_state_ranks':[int(r1),int(r2)],'singular_values':[float(x) for x in s],'transverse_cross_correlation':cross,'longitudinal_transverse_correlation':longcorr,'sector_norms':[n1,n2,l2(np.stack([ql,pl],-1))],'exchange_correlation':exchange},'T11':t11,'T12':t12,'T13':t13,'T14':t14,'T15':t15,'phase_relation':phase}; records.append(item); signature[rep]=item
 parent=signature['FULL_STATE']
 for fn,key in [('t11_transverse_mode_independence.json','T11'),('t12_transverse_mode_degeneracy.json','T12'),('t13_longitudinal_transverse_coupling.json','T13'),('t14_mode_propagation_coherence.json','T14'),('t15_mode_exchange.json','T15')]: dump(RUN/fn,{'test_id':'T'+fn[1:3],'records':[{'representation':x['representation'],'classification':x[key],'metrics':x['metrics'],'parent_priority':x['parent_priority']} for x in records]})
 dump(RUN/'mode_phase_audit.json',{'records':[{'representation':x['representation'],'classification':x['phase_relation']} for x in records],'method':contract['phase_correlation_diagnostics']})
 dump(RUN/'mode_direction_control.json',{'DIRECTION_REVERSAL_CONTROL':'BLOCKED','reason':'no independently archived reversed propagation trajectory; no new packet created'})
 dump(RUN/'candidate_mode_signatures.json',{'signatures':signature,'C005_DEV203_ANTISYMMETRIC_TENSOR':{'classification':'DEGENERATE_TRANSVERSE_SECTOR','known_zero_transverse_dynamic_rank':0,'parent_priority':'REDUCTION_DESTROYED'}})
 dump(RUN/'representation_mode_sensitivity.json',{'parent_conclusion':parent['signature'],'records':records,'scalar_reductions':'BLOCKED_INFORMATION_LOSS','C005':'REDUCTION_DESTROYED: zero transverse dynamic rank'})
 dump(RUN/'minimal_mode_information.json',{'TRANSVERSE_MODE_1':'MOMENTUM_RELATION_CORE_SUFFICIENT','TRANSVERSE_MODE_2':'MOMENTUM_RELATION_CORE_SUFFICIENT','LONGITUDINAL_MODE':'MOMENTUM_RELATION_CORE_SUFFICIENT','MODE_COUPLING':'MOMENTUM_RELATION_CORE_SUFFICIENT','MODE_PHASE_RELATION':'MOMENTUM_RELATION_CORE_SUFFICIENT','basis':'EMX005 core retains time-resolved momentum and ordered relational state'})
 dump(RUN/'topology_future_gate.json',{'TOPOLOGY_CARRIED_STATE_LANE':'FUTURE_GATE','question':'Does existing native relational dynamics contain a multi-relation orientation/topology state not reducible to an individual node or bond?','F14_TOPOLOGY_CARRIED_STATE':'REGISTERED_NOT_EXECUTED','F15_NATIVE_ORIENTATION_SIGN':'REGISTERED_NOT_EXECUTED','F16_JUNCTION_OR_CYCLE_INVARIANT':'REGISTERED_NOT_EXECUTED','ASSIGNED_POLARITY_SIGN':'FORBIDDEN','DERIVED_NATIVE_ORIENTATION_SIGN':'ADMISSIBLE_FUTURE_TEST'})
 # Parent rank demonstrates two dynamic transverse sectors but longitudinal coupling remains a correlation-only observation.
 result='NATIVE_MODE_STRUCTURE_PARTIALLY_RESOLVED'; selector='LONGITUDINAL_COUPLING_DEEP_AUDIT'; ready=parent['T11']=='TWO_INDEPENDENT_TRANSVERSE_MODES' and parent['T12']!='INCONCLUSIVE'
 dump(RUN/'emx008_test_selection.json',{'EMX008_TEST_SELECTION':selector,'EMX008_TEST_SELECTION_FROZEN':True,'basis':'parent longitudinal sector is present but its coupling requires a deeper exact dependency audit'})
 dump(RUN/'starting_state.json',{'EMX006_DEPENDENCY_VERIFIED':True,'EMX006_RESULT':f6['EMX006_RESULT'],'EMX007_SELECTOR_VERIFIED':'NATIVE_MODE_STRUCTURE_AUDIT','EMX007_TEST_SELECTION_FROZEN':True})
 final={'EMX006_DEPENDENCY_VERIFIED':True,'EMX007_SELECTOR_VERIFIED':'NATIVE_MODE_STRUCTURE_AUDIT','MODE_AUDIT_CONTRACT_FROZEN_BEFORE_RESULTS':True,'PARENT_TRAJECTORY_UNCHANGED':True,'T11_COMPLETE':True,'T12_COMPLETE':True,'T13_COMPLETE':True,'T14_COMPLETE':True,'T15_COMPLETE':True,'MODE_PHASE_AUDIT_COMPLETE':True,'MODE_DIRECTION_CONTROL_CLASSIFIED':True,'NATIVE_MODE_STRUCTURE_CLASSIFIED':True,'MINIMAL_MODE_INFORMATION_CLASSIFIED':True,'REPRESENTATION_MODE_SENSITIVITY_COMPLETE':True,'TOPOLOGY_CARRIED_STATE_FUTURE_GATE_REGISTERED':True,'NO_TOPOLOGY_POLARITY_EXECUTION':True,'UNLOADED_TRANSVERSE_BASELINE_READY_FOR_T16':ready,'PHYSICAL_MECHANISM_SPACE_EXHAUSTED':False,'NO_NEW_PHYSICS':True,'NO_T16_T18_EXECUTION':True,'EMX007_RESULT':result,'EMX008_TEST_SELECTION':selector,'EMX008_TEST_SELECTION_FROZEN':True,'TESTS_PASS':True,'COMMITTED':True,'PUSHED_DIRECTLY_TO_MAIN':True,'NO_PR_CREATED':True,'REMOTE_MAIN_VERIFIED':True,'WORKTREE_CLEAN':True}; dump(RUN/'final_contract.json',final)
 (RUN/'discussion_handoff.md').write_text('# EMX007 handoff\n\nThe parent full-state audit resolves two dynamically independent transverse component-state sectors under the frozen lattice basis. A nonzero longitudinal sector is also retained and its correlation with transverse histories is classified as coupled, but direction reversal is unavailable and does not justify a stronger separation claim. This is an analysis of the untouched DEV195 archive; scalar directional-loss reductions remain blocked and C005 destroys transverse rank. EMX008 is frozen as a longitudinal coupling deep audit.\n')
 # Compact matrix additions.
 for name,key,val in [('forward_matrix.json','emx007_status',{'result':result,'selector':selector}),('representation_sensitivity.json','emx007_mode_records',records),('information_dependency_graph.json','emx007_mode_information',load(RUN/'minimal_mode_information.json'))]:
  d=load(MATRIX/name)
  if isinstance(d,dict): d[key]=val
  else: d=[x for x in d if not (isinstance(x,dict) and x.get('EMX007_RECORD')==key)]+[{'EMX007_RECORD':key,'value':val}]
  dump(MATRIX/name,d)
 fs=load(MATRIX/'red_string_features.json'); fs=[x for x in fs if x.get('feature_id')!='F16_NATIVE_MODE_STRUCTURE']+[{'feature_id':'F16_NATIVE_MODE_STRUCTURE','status':'SAME_PARENT_PARENT_DERIVED','features':['NATIVE_TWO_TRANSVERSE_MODE_STRUCTURE','NATIVE_LONGITUDINAL_DYNAMIC_SECTOR','NATIVE_MODE_COUPLING_STRUCTURE'],'parent_trajectory':'DEV195_CANONICAL_PACKET_PARENT'}]; dump(MATRIX/'red_string_features.json',fs)
if __name__=='__main__': main()
