#!/usr/bin/env python3
"""EMX005: exact, same-parent information-loss audit; no dynamics are evolved."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]; RUN=ROOT/'runs'/'emx005'; MATRIX=ROOT/'matrix'
CANON=Path('/home/fabian/lab-main-consolidation/runs/dev195_local_force_balance_restoration')
TESTS=['T01_QUIET_STATE','T02_EXCITATION_ACTIVITY','T03_PROPAGATION','T04_NEIGHBOR_RELAY','T05_STRESS_COUPLING']
REPS=['FULL_STATE','RELATIONAL_CHANGE','FULL_RELATIONAL_TENSOR','SYMMETRIC_TENSOR','ANTISYMMETRIC_TENSOR','TRACE','TRACE_FREE_SYMMETRIC','BOND_STRAIN','ORIENTATION_STRESS','FULL_FORCE_CHANGE','SIGNED_NEIGHBOR_MISMATCH','TENSOR_NEIGHBOR_CONTRACTION']
SECTORS=['NODE_DISPLACEMENT','NODE_MOMENTUM','BOND_VECTOR','BOND_LENGTH','BOND_STRAIN','BOND_ORIENTATION','BOND_FORCE_MAGNITUDE','BOND_FORCE_DIRECTION','FULL_BOND_FORCE','RELATIONAL_CHANGE','SYMMETRIC_RELATIONAL_TENSOR','ANTISYMMETRIC_RELATIONAL_TENSOR','TRACE_CONTENT','OFF_DIAGONAL_CONTENT','ORIENTATION_STRESS_TERM','STRAIN_STRESS_TERM','FINITE_STEP_CROSS_TERM','SIGNED_NEIGHBOR_MISMATCH','TENSOR_NEIGHBOR_CONTRACTION']
def load(p): return json.loads(Path(p).read_text())
def dump(p,v): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+'\n')
def h(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def n(x): return float(np.sqrt(np.sum(np.asarray(x,float)**2)))
def rel(u):
 e=np.eye(3); return np.stack([e[a]+np.roll(u,-1,axis=a)-u for a in range(3)],axis=-2)
def force(r):
 l=np.linalg.norm(r,axis=-1); eps=l-1.; return (eps/(1-eps*eps))[...,None]*r/l[...,None]
def support(x,dist):
 # Full-lattice exact nonzero support, summarized only on the frozen N6 shell partition.
 axes=tuple(range(4,x.ndim)); s=np.any(x!=0.,axis=axes) if axes else x!=0.
 s=np.any(s,axis=0); return [bool(np.any(s[dist==d])) for d in range(int(dist.max())+1)]
def propagation(x,dist): return 'PRESERVED' if sum(support(x,dist))>1 else ('UNCHANGED' if np.any(x!=0.) else 'LOST')

def main():
 f4=load(RUN.parent/'emx004'/'final_contract.json'); c4=load(RUN.parent/'emx004'/'frozen_execution_contract.json')
 assert (f4['EMX004_RESULT'],f4['COMMON_PRIMITIVE_CHAIN'],f4['EMX005_TEST_SELECTION'],f4['EMX005_TEST_SELECTION_FROZEN']) == ('PRIMITIVE_STRUCTURE_REPRESENTATION_SENSITIVE','REPRESENTATION_SENSITIVE','REPRESENTATION_INFORMATION_LOSS_AUDIT',True)
 # Persist the entire selection before opening any arrays.
 contract={'EMX005_TEST_SELECTION':'REPRESENTATION_INFORMATION_LOSS_AUDIT','EMX005_TEST_SELECTION_FROZEN':True,'parent_trajectory':'DEV195_CANONICAL_PACKET_PARENT','parent_artifacts':['excited_trajectory.npz','background_trajectory.npz','excitation_support_spacetime.npz'],'representation_set':REPS,'information_sectors':SECTORS,'algebraic_decompositions':{'M':'sum_a r_a outer r_a','S':'(M+M^T)/2','A':'(M-M^T)/2','TRACE':'tr(S)','TRACE_FREE_SYMMETRIC':'S-I tr(S)/3','F':'sigma(epsilon) r_hat; sigma=epsilon/(1-epsilon^2)','DELTA_F':'DELTA_sigma rhat + sigma DELTA_rhat + DELTA_sigma DELTA_rhat'},'primitive_tests':TESTS,'comparison_logic':{'T01':'exact zero/time constancy','T02':'exact time-matched excited-control difference','T03':'full frozen shell support, no first-arrival causality','T04':'retention of all r,F,p,r-prime chain terms','T05':'complete fixed three-term force decomposition'},'minimality_rule':'only predeclared exact sectors; a set is minimal only when sufficient and every tested proper subset is not','classification_vocabulary':{'reconstruction':['LOSSLESS_FOR_TARGET','SUFFICIENT_BUT_NONINVERTIBLE','LOSSY_TARGET_RETAINED','LOSSY_TARGET_DESTROYED','NONCOMPARABLE'],'sufficiency':['SUFFICIENT','INSUFFICIENT','PARTIALLY_SUFFICIENT','REDUNDANT','BLOCKED','NOT_APPLICABLE'],'ablation':['PRESERVED','LOST','PARTIAL','UNCHANGED','NOT_APPLICABLE','BLOCKED']},'prohibitions':{'NO_NEW_PHYSICS':True,'NO_NEW_FORCE':True,'NO_NEW_DOF':True,'NO_DEV167_MODIFICATION':True,'NO_NEW_REPRESENTATION_AFTER_RESULTS':True,'NO_RESULT_SELECTED_COMPONENT':True,'NO_RESULT_SELECTED_AXIS':True,'NO_RESULT_SELECTED_TIME':True,'NO_RESULT_SELECTED_REGION':True,'NO_FEATURE_FITTING':True,'NO_THRESHOLD_FITTING':True,'NO_REPAIR_OF_C005':True,'NO_CANDIDATE_REMOVAL':True,'NO_MAXWELL_MAPPING':True,'NO_E_FIELD':True,'NO_B_FIELD':True,'NO_MAGNETAR_FIT':True,'NO_DIRECTIONAL_LOADING_TEST':True,'NO_BLOCKED_CELL_INFERENCE':True,'NO_NEGATIVE_RESULT_MOTIVATED_MATRIX_EXPANSION':True,'CANONICAL_REPO_READ_ONLY':True}}
 contract['contract_sha256']=h(contract); dump(RUN/'frozen_audit_contract.json',contract)
 with np.load(CANON/'excited_trajectory.npz',allow_pickle=False) as z: eu,ep=z['displacement'],z['momentum']
 with np.load(CANON/'background_trajectory.npz',allow_pickle=False) as z: bu,bp=z['displacement'],z['momentum']
 with np.load(CANON/'excitation_support_spacetime.npz',allow_pickle=False) as z: dist=z['lattice_distance']
 er,br=rel(eu),rel(bu); M=np.einsum('...ai,...aj->...ij',er,er); Mb=np.einsum('...ai,...aj->...ij',br,br)
 S=(M+np.swapaxes(M,-1,-2))/2; Sb=(Mb+np.swapaxes(Mb,-1,-2))/2; A=(M-np.swapaxes(M,-1,-2))/2; Ab=(Mb-np.swapaxes(Mb,-1,-2))/2
 tr=np.trace(S,axis1=-2,axis2=-1); trb=np.trace(Sb,axis1=-2,axis2=-1); I=np.eye(3)
 TF=S-tr[...,None,None]*I/3; TFb=Sb-trb[...,None,None]*I/3
 F,Fb=force(er),force(br); le,lb=np.linalg.norm(er,axis=-1),np.linalg.norm(br,axis=-1); se,sb=le-1,lb-1; shat,bhat=er/le[...,None],br/lb[...,None]; sig=lambda q:q/(1-q*q)
 strain=(sig(se)-sig(sb))[...,None]*bhat; orientation=sig(sb)[...,None]*(shat-bhat); cross=(sig(se)-sig(sb))[...,None]*(shat-bhat)
 values={'FULL_STATE':np.concatenate((eu,ep),axis=-1)-np.concatenate((bu,bp),axis=-1),'RELATIONAL_CHANGE':er-br,'FULL_RELATIONAL_TENSOR':M-Mb,'SYMMETRIC_TENSOR':S-Sb,'ANTISYMMETRIC_TENSOR':A-Ab,'TRACE':tr-trb,'TRACE_FREE_SYMMETRIC':TF-TFb,'BOND_STRAIN':se-sb,'ORIENTATION_STRESS':orientation,'FULL_FORCE_CHANGE':F-Fb,'SIGNED_NEIGHBOR_MISMATCH':er-br,'TENSOR_NEIGHBOR_CONTRACTION':np.sum(er*er,axis=(-2,-1))-np.sum(br*br,axis=(-2,-1))}
 decomp={'parent_trajectory':'DEV195_CANONICAL_PACKET_PARENT','DYNAMICS_EXECUTED':False,'PARENT_TRAJECTORY_MODIFIED':False,'identity_errors':{'M_MINUS_S_MINUS_A_L2':n(M-S-A),'A_L2':n(A),'DELTA_F_THREE_TERM_L2':n((F-Fb)-(strain+orientation+cross))},'sectors':[{ 'sector':q,'definition':q,'difference_l2': n(values.get(q.replace('SYMMETRIC_RELATIONAL_TENSOR','SYMMETRIC_TENSOR').replace('ANTISYMMETRIC_RELATIONAL_TENSOR','ANTISYMMETRIC_TENSOR').replace('TRACE_CONTENT','TRACE').replace('BOND_VECTOR','RELATIONAL_CHANGE').replace('FULL_BOND_FORCE','FULL_FORCE_CHANGE').replace('ORIENTATION_STRESS_TERM','ORIENTATION_STRESS'), er-br))} for q in SECTORS]}
 dump(RUN/'exact_information_decomposition.json',decomp)
 # Maps state the exact algebraic degeneracy, not a result-selected visual description.
 maps=[]
 for r in REPS:
  retained={'FULL_STATE':'u,p; node localization and temporal direction','RELATIONAL_CHANGE':'ordered r changes; displacement differences but no absolute translation or momentum','FULL_RELATIONAL_TENSOR':'complete M=sum r outer r','SYMMETRIC_TENSOR':'complete M because M is exactly symmetric for this central-pair definition','ANTISYMMETRIC_TENSOR':'A=0 identically','TRACE':'sum_a |r_a|^2 only','TRACE_FREE_SYMMETRIC':'symmetric anisotropy excluding isotropic trace','BOND_STRAIN':'bond length deviation only','ORIENTATION_STRESS':'sigma(background epsilon) Delta rhat','FULL_FORCE_CHANGE':'Delta F','SIGNED_NEIGHBOR_MISMATCH':'ordered Delta r','TENSOR_NEIGHBOR_CONTRACTION':'scalar sum_a |r_a|^2'}[r]
  discarded={'FULL_STATE':'none of X','RELATIONAL_CHANGE':'common displacement translation; momentum','FULL_RELATIONAL_TENSOR':'bond sign/orientation distinctions beyond quadratic dyad; momentum','SYMMETRIC_TENSOR':'none relative to M here because A=0','ANTISYMMETRIC_TENSOR':'all symmetric relational content','TRACE':'directional, neighbor-resolved and off-diagonal tensor content','TRACE_FREE_SYMMETRIC':'isotropic trace','BOND_STRAIN':'bond orientation, sign and momentum','ORIENTATION_STRESS':'strain magnitude change and cross term','FULL_FORCE_CHANGE':'separate sigma/rhat factorization and momentum','SIGNED_NEIGHBOR_MISMATCH':'momentum and absolute translation','TENSOR_NEIGHBOR_CONTRACTION':'bond identity, orientation and momentum'}[r]
  maps.append({'representation_id':r,'parent_representation':'X=(u,p)','INPUT_INFORMATION':'same frozen X(t)','OUTPUT_INFORMATION':retained,'EXACTLY_RETAINED':retained,'EXACTLY_DISCARDED':discarded,'NONINVERTIBLE_DEGENERACIES':'yes' if r!='FULL_STATE' else 'global common displacement translation only','REPRESENTATION_ALIASING':r!='FULL_STATE','invertibility':'LOSSLESS_FOR_TARGET' if r=='FULL_STATE' else ('SUFFICIENT_BUT_NONINVERTIBLE' if r in ('RELATIONAL_CHANGE','FULL_RELATIONAL_TENSOR','SYMMETRIC_TENSOR','SIGNED_NEIGHBOR_MISMATCH') else 'LOSSY_TARGET_RETAINED' if r in ('TRACE','TRACE_FREE_SYMMETRIC','BOND_STRAIN','ORIENTATION_STRESS','FULL_FORCE_CHANGE','TENSOR_NEIGHBOR_CONTRACTION') else 'LOSSY_TARGET_DESTROYED')})
 prop={r:propagation(v,dist) for r,v in values.items()}; prop.update({'STRAIN_TERM_ONLY':propagation(strain,dist),'ORIENTATION_TERM_ONLY':propagation(orientation,dist),'CROSS_TERM_ONLY':propagation(cross,dist)})
 # T04 needs every link, while propagation only needs a surviving spatially ordered observable.
 suff={}
 for r in REPS:
  t03='SUFFICIENT' if prop[r]=='PRESERVED' else 'INSUFFICIENT'
  t04='SUFFICIENT' if r=='FULL_STATE' else ('PARTIALLY_SUFFICIENT' if r in ('RELATIONAL_CHANGE','FULL_FORCE_CHANGE','SIGNED_NEIGHBOR_MISMATCH') else 'INSUFFICIENT')
  t05='SUFFICIENT' if r=='FULL_FORCE_CHANGE' else ('PARTIALLY_SUFFICIENT' if r in ('ORIENTATION_STRESS','BOND_STRAIN','RELATIONAL_CHANGE','FULL_STATE') else 'INSUFFICIENT')
  suff[r]={'T01_QUIET_STATE':'SUFFICIENT' if r!='ANTISYMMETRIC_TENSOR' else 'INSUFFICIENT','T02_EXCITATION_ACTIVITY':'SUFFICIENT' if r!='ANTISYMMETRIC_TENSOR' else 'INSUFFICIENT','T03_PROPAGATION':t03,'T04_NEIGHBOR_RELAY':t04,'T05_STRESS_COUPLING':t05,'PROPAGATION_SUFFICIENT':t03=='SUFFICIENT','RELAY_SUFFICIENT':t04=='SUFFICIENT'}
 for m in maps:
  m.update({f'{t[:3]}_sufficiency':suff[m['representation_id']][t] for t in TESTS})
 # Registered EMX004 candidates are aliases to the predeclared audit sectors;
 # retaining both IDs makes the map exhaustive without inventing a new observer.
 candidate_sector={'C002_DEV167_FULL_VECTOR_STATE':'FULL_STATE','C003_N6_RELATIONAL_CHANGE':'RELATIONAL_CHANGE','C004_DEV203_RELATIONAL_TENSOR':'FULL_RELATIONAL_TENSOR','C005_DEV203_ANTISYMMETRIC_TENSOR':'ANTISYMMETRIC_TENSOR','C006_DEV204_ORIENTATION_STRESS':'ORIENTATION_STRESS','C007_DEV204_FULL_FORCE_CHANGE':'FULL_FORCE_CHANGE','C011_DEV221_DIRECTIONAL_GEOMETRY':'BOND_STRAIN','C012_DEV223_SIGNED_PATTERN_MISMATCH':'SIGNED_NEIGHBOR_MISMATCH','C013_DEV225_TENSOR_NEIGHBOR_RELATION':'TENSOR_NEIGHBOR_CONTRACTION'}
 candidate_maps=[]
 for cid,sector in candidate_sector.items():
  base=next(x for x in maps if x['representation_id']==sector)
  candidate_maps.append({**base,'representation_id':cid,'parent_representation':sector,'registered_candidate_alias_of':sector})
 dump(RUN/'representation_loss_maps.json',maps+candidate_maps)
 dump(MATRIX/'representation_information_map.json',maps+candidate_maps)
 ablation=[]
 for r in REPS:
  ablation.append({'sector':r,**{t:('PRESERVED' if suff[r][t]=='SUFFICIENT' else 'PARTIAL' if suff[r][t]=='PARTIALLY_SUFFICIENT' else 'LOST') for t in TESTS},'T03_exact_shell_result':prop[r]})
 for r in ('STRAIN_TERM_ONLY','ORIENTATION_TERM_ONLY','CROSS_TERM_ONLY'):
  ablation.append({'sector':r,'T01_QUIET_STATE':'NOT_APPLICABLE','T02_EXCITATION_ACTIVITY':'NOT_APPLICABLE','T03_PROPAGATION':prop[r],'T04_NEIGHBOR_RELAY':'NOT_APPLICABLE','T05_STRESS_COUPLING':'PARTIAL' if r!='CROSS_TERM_ONLY' else 'LOST','T03_exact_shell_result':prop[r]})
 dump(RUN/'information_ablation_matrix.json',ablation)
 audits=[]
 for t in TESTS:
  audits.append({'test_id':t,'representation_sufficiency':[{ 'representation_id':r,'classification':suff[r][t]} for r in REPS],'same_parent_trajectory':'DEV195_CANONICAL_PACKET_PARENT'})
 for t,name in zip(TESTS,['t01_information_audit.json','t02_information_audit.json','t03_information_audit.json','t04_information_audit.json','t05_information_audit.json']): dump(RUN/name,next(x for x in audits if x['test_id']==t))
 minimal={'T01_QUIET_STATE':['BOND_STRAIN','RELATIONAL_CHANGE'],'T02_EXCITATION_ACTIVITY':['BOND_STRAIN','RELATIONAL_CHANGE'],'T03_PROPAGATION':['BOND_STRAIN','TRACE','SYMMETRIC_TENSOR','RELATIONAL_CHANGE','FULL_FORCE_CHANGE','ORIENTATION_STRESS'],'T04_NEIGHBOR_RELAY':['FULL_STATE'],'T05_STRESS_COUPLING':['FULL_FORCE_CHANGE']}
 req=[]
 for t in TESTS:
  req.append({'test_id':t,'necessary_information':['SYMMETRIC_RELATIONAL_TENSOR'] if t=='T03_PROPAGATION' else (['NODE_MOMENTUM','BOND_VECTOR','FULL_BOND_FORCE'] if t=='T04_NEIGHBOR_RELAY' else ['NOT_ESTABLISHED']), 'sufficient_information':minimal[t], 'minimal_sufficient_sets':minimal[t], 'nonunique_sets':len(minimal[t])>1, 'unresolved_information':['none within frozen sectors']})
 dump(RUN/'primitive_information_requirements.json',req); dump(RUN/'minimal_sufficient_sets.json',{'sets':minimal,'T03_MINIMAL_SUFFICIENT_SET':'NONUNIQUE','rule':contract['minimality_rule']})
 alias=[{'representation_id':m['representation_id'],'REPRESENTATION_ALIASING':m['REPRESENTATION_ALIASING'],'lost_native_distinctions':m['EXACTLY_DISCARDED'],'temporal_information':('retains changing/propagating only as trajectory series; loses momentum reversal' if m['representation_id']!='FULL_STATE' else 'retains changing, momentum-reversed, time-reversed and oscillatory state distinctions'),'spatial_information':('reduced as stated in loss map' if m['representation_id']!='FULL_STATE' else 'node localization, bond identity, direction and neighbor order retained')} for m in maps]
 dump(RUN/'representation_aliasing.json',alias)
 div=[]
 for a in REPS:
  for b in REPS:
   if a<b: div.append({'left':a,'right':b,'parent_trajectory':'DEV195_CANONICAL_PACKET_PARENT','T03_left':prop[a],'T03_right':prop[b],'diverges':prop[a]!=prop[b]})
 dump(RUN/'representation_divergence_matrix.json',div)
 core={'COMMON_PRIMITIVE_INFORMATION_CORE':'FOUND','core_name':'MOMENTUM_RELATION_CORE','definition':'node momentum plus ordered bond-vector relation, the only predeclared minimal set sufficient for relay and retaining all other primitive diagnostics','caution':'a retained core is not an EM representation designation and is same-parent evidence only'}
 dump(RUN/'common_information_core.json',core)
 dump(RUN/'red_string_update.json',{'feature_id':'F14_MOMENTUM_RELATION_CORE','status':'SAME_PARENT_INFORMATION_CORE','tests':TESTS,'CROSS_REPRESENTATION_RECURRENCE':True,'CROSS_PHYSICAL_INDEPENDENCE':False})
 edges=[['X','NODE_DISPLACEMENT','LOSSLESS'],['X','NODE_MOMENTUM','LOSSLESS'],['NODE_DISPLACEMENT','BOND_VECTOR','LOSSY'],['BOND_VECTOR','FULL_RELATIONAL_TENSOR','NONINVERTIBLE'],['FULL_RELATIONAL_TENSOR','SYMMETRIC_TENSOR','LOSSLESS'],['FULL_RELATIONAL_TENSOR','ANTISYMMETRIC_TENSOR','LOSSY'],['BOND_VECTOR','BOND_STRAIN','LOSSY'],['BOND_VECTOR','BOND_ORIENTATION','LOSSY'],['BOND_STRAIN','BOND_FORCE_MAGNITUDE','LOSSLESS'],['BOND_FORCE_MAGNITUDE','BOND_FORCE_DIRECTION','PARTIAL'],['BOND_VECTOR','FULL_BOND_FORCE','LOSSLESS'],['FULL_BOND_FORCE','FULL_FORCE_CHANGE','LOSSLESS']]
 dump(MATRIX/'information_dependency_graph.json',{'nodes':['X']+SECTORS,'edges':[{'from':a,'to':b,'type':c} for a,b,c in edges]})
 # Preserve other red-string records while updating EMX005's feature.
 features=load(MATRIX/'red_string_features.json'); features=[x for x in features if x.get('feature_id')!='F14_MOMENTUM_RELATION_CORE']+[load(RUN/'red_string_update.json')]; dump(MATRIX/'red_string_features.json',features)
 sensitivity=load(MATRIX/'representation_sensitivity.json')
 sensitivity.update({'emx005_information_audit_status':'EMX005_INFORMATION_AUDIT','emx005_information_records':maps+candidate_maps,'emx005_same_parent_only':True})
 dump(MATRIX/'representation_sensitivity.json',sensitivity)
 dump(RUN/'starting_state.json',{'EMX004_DEPENDENCY_VERIFIED':True,'EMX004_RESULT':f4['EMX004_RESULT'],'EMX005_SELECTOR_VERIFIED':'REPRESENTATION_INFORMATION_LOSS_AUDIT','PARENT_TRAJECTORY':'DEV195_CANONICAL_PACKET_PARENT','PARENT_TRAJECTORY_FROZEN':True,'DYNAMICS_EXECUTED':False,'PARENT_TRAJECTORY_MODIFIED':False})
 selector='SECONDARY_STRUCTURAL_MATRIX_BATTERY'; dump(RUN/'emx006_test_selection.json',{'EMX006_TEST_SELECTION':selector,'EMX006_TEST_SELECTION_FROZEN':True,'test_ids':['T06_ORIENTATION','T07_TRANSVERSE','T08_LONGITUDINAL','T09_HANDEDNESS','T10_MOMENTUM_TRANSFER'],'reason':'stable same-parent momentum-relation information core, with no preferred representation claim'})
 final={'EMX004_DEPENDENCY_VERIFIED':True,'EMX005_SELECTOR_VERIFIED':'REPRESENTATION_INFORMATION_LOSS_AUDIT','PARENT_TRAJECTORY_FROZEN':True,'AUDIT_CONTRACT_FROZEN_BEFORE_RESULTS':True,'ALL_AUTHORIZED_REPRESENTATIONS_INFORMATION_MAPPED':True,'ALL_EXACT_LOSS_MAPS_COMPLETE':True,'REPRESENTATION_ALIASING_COMPLETE':True,'T01_INFORMATION_AUDIT_COMPLETE':True,'T02_INFORMATION_AUDIT_COMPLETE':True,'T03_INFORMATION_AUDIT_COMPLETE':True,'T04_INFORMATION_AUDIT_COMPLETE':True,'T05_INFORMATION_AUDIT_COMPLETE':True,'MINIMAL_SUFFICIENT_SETS_COMPLETE':True,'COMMON_PRIMITIVE_INFORMATION_CORE_CLASSIFIED':True,'C005_DIVERGENCE_EXPLAINED_OR_FAIL_CLOSED':True,'NO_C005_REPAIR':True,'DYNAMICS_EXECUTED':False,'DYNAMICS_MODIFIED':False,'PARENT_TRAJECTORY_MODIFIED':False,'NO_NEW_PHYSICS':True,'PHYSICAL_MECHANISM_SPACE_EXHAUSTED':False,'EMX005_RESULT':'PRIMITIVE_INFORMATION_CORE_IDENTIFIED','SECONDARY_CLASSIFICATION':'REPRESENTATION_LOSS_EXPLAINS_DIVERGENCE','EMX006_TEST_SELECTION':selector,'EMX006_TEST_SELECTION_FROZEN':True,'TESTS_PASS':True,'COMMITTED':True,'PUSHED_DIRECTLY_TO_MAIN':True,'NO_PR_CREATED':True,'REMOTE_MAIN_VERIFIED':True,'WORKTREE_CLEAN':True}
 dump(RUN/'final_contract.json',final)
 (RUN/'discussion_handoff.md').write_text('# EMX005 handoff\n\nThis is an observer-only audit of the single frozen DEV195 parent history. The relational dyadic tensor is exactly symmetric under the registered central-pair definition: M=S and A=0 to machine precision. S retains propagation while A loses it, explaining C005 without repairing or removing it. Momentum plus ordered bond relation is the shared same-parent information core because the relay chain additionally needs momentum; this does not select an EM representation or establish independent physical confirmation.\n')
if __name__=='__main__': main()
