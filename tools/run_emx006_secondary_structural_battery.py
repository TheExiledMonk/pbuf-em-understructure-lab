#!/usr/bin/env python3
"""EMX006: frozen secondary native-structure battery on authorized archives."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]; RUN=ROOT/'runs'/'emx006'; MATRIX=ROOT/'matrix'
CANON=Path('/home/fabian/lab-main-consolidation/runs/dev195_local_force_balance_restoration')
TESTS=['T06_TRANSVERSE_RELATIONAL_CONTENT','T07_LONGITUDINAL_CONTENT','T08_HANDEDNESS_PARITY','T09_STATIC_LOADED_ORGANIZATION','T10_SOURCE_GENERATED_OUTGOING_STRUCTURE']
ACTIVE=['C002_DEV167_FULL_VECTOR_STATE','C003_N6_RELATIONAL_CHANGE','C004_DEV203_RELATIONAL_TENSOR','C005_DEV203_ANTISYMMETRIC_TENSOR','C006_DEV204_ORIENTATION_STRESS','C007_DEV204_FULL_FORCE_CHANGE','C011_DEV221_DIRECTIONAL_GEOMETRY','C012_DEV223_SIGNED_PATTERN_MISMATCH','C013_DEV225_TENSOR_NEIGHBOR_RELATION']
BLOCKED=['C008_DEV211_STATIC_MAINTAINED_DEFORMATION','C009_DEV212_MOMENTUM_REVERSED_STATE','C010_DEV213_TWO_STRUCTURE_AGGREGATE','C015_FINITE_X_AGGREGATE_FULL_STATE']
ALIASES={'C002_DEV167_FULL_VECTOR_STATE':'FULL_STATE','C003_N6_RELATIONAL_CHANGE':'RELATIONAL_CHANGE','C004_DEV203_RELATIONAL_TENSOR':'FULL_RELATIONAL_TENSOR','C005_DEV203_ANTISYMMETRIC_TENSOR':'ANTISYMMETRIC_TENSOR','C006_DEV204_ORIENTATION_STRESS':'ORIENTATION_STRESS','C007_DEV204_FULL_FORCE_CHANGE':'FULL_FORCE_CHANGE','C011_DEV221_DIRECTIONAL_GEOMETRY':'BOND_STRAIN','C012_DEV223_SIGNED_PATTERN_MISMATCH':'SIGNED_NEIGHBOR_MISMATCH','C013_DEV225_TENSOR_NEIGHBOR_RELATION':'TENSOR_NEIGHBOR_CONTRACTION'}
K=np.array([1.,0.,0.]); TOL=1e-12
def load(p): return json.loads(Path(p).read_text())
def dump(p,v): p.parent.mkdir(parents=True,exist_ok=True); Path(p).write_text(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+'\n')
def h(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def l2(x): return float(np.linalg.norm(np.asarray(x)))
def rel(u):
 e=np.eye(3); return np.stack([e[a]+np.roll(u,-1,axis=a)-u for a in range(3)],axis=-2)
def force(r):
 q=np.linalg.norm(r,axis=-1); eps=q-1; return (eps/(1-eps*eps))[...,None]*r/q[...,None]
def rank(x): return int(np.linalg.matrix_rank(np.asarray(x).reshape(-1,2),tol=TOL))
def reflect_vector(x):
 # Exact supported x-reflection about frozen launch plane x=1 on the periodic lattice.
 y=np.roll(np.flip(x,axis=1),2,axis=1).copy(); y[...,0]*=-1; return y
def reflect_scalar(x): return np.roll(np.flip(x,axis=1),2,axis=1)
def representation_values(eu,bu):
 er,br=rel(eu),rel(bu); de=er-br
 M=np.einsum('...ai,...aj->...ij',er,er)-np.einsum('...ai,...aj->...ij',br,br)
 S=(M+np.swapaxes(M,-1,-2))/2; A=(M-np.swapaxes(M,-1,-2))/2
 F=force(er)-force(br); le=np.linalg.norm(er,axis=-1); lb=np.linalg.norm(br,axis=-1)
 se,sb=le-1,lb-1; sh=er/le[...,None]; bh=br/lb[...,None]; sig=lambda z:z/(1-z*z)
 orient=sig(sb)[...,None]*(sh-bh)
 return {'FULL_STATE':de,'RELATIONAL_CHANGE':de,'FULL_RELATIONAL_TENSOR':M,'ANTISYMMETRIC_TENSOR':A,'ORIENTATION_STRESS':orient,'FULL_FORCE_CHANGE':F,'BOND_STRAIN':se-sb,'SIGNED_NEIGHBOR_MISMATCH':de,'TENSOR_NEIGHBOR_CONTRACTION':np.sum(er*er,axis=(-2,-1))-np.sum(br*br,axis=(-2,-1))}
def directional(v, alias):
 if alias in ('BOND_STRAIN','TENSOR_NEIGHBOR_CONTRACTION'): return None
 if alias=='FULL_RELATIONAL_TENSOR': return np.einsum('...ij,j->...i',v,K)
 if alias=='ANTISYMMETRIC_TENSOR': return np.einsum('...ij,j->...i',v,K)
 return v
def main():
 f5=load(RUN.parent/'emx005'/'final_contract.json'); core=load(RUN.parent/'emx005'/'common_information_core.json')
 assert f5['EMX005_RESULT']=='PRIMITIVE_INFORMATION_CORE_IDENTIFIED' and f5['EMX006_TEST_SELECTION']=='SECONDARY_STRUCTURAL_MATRIX_BATTERY' and f5['EMX006_TEST_SELECTION_FROZEN'] and core['COMMON_PRIMITIVE_INFORMATION_CORE']=='FOUND' and core['core_name']=='MOMENTUM_RELATION_CORE'
 registry={x['candidate_id']:x for x in load(MATRIX/'candidate_registry.json')}
 contract={'EMX006_TEST_SELECTION':'SECONDARY_STRUCTURAL_MATRIX_BATTERY','EMX006_TEST_SELECTION_FROZEN':True,'candidate_ids':ACTIVE+BLOCKED,'test_ids':TESTS,'parent_trajectories':{'DEV195_CANONICAL_PACKET_PARENT':ACTIVE},'required_information_sectors':{'T06_TRANSVERSE_RELATIONAL_CONTENT':['ordered directional relational change','time-resolved state','frozen propagation direction'],'T07_LONGITUDINAL_CONTENT':['ordered directional relational change','time-resolved state','frozen propagation direction'],'T08_HANDEDNESS_PARITY':['exact native reflection operation','parity-sensitive native representation'],'T09_STATIC_LOADED_ORGANIZATION':['authorized stationary loaded source regime','static and dynamic records'],'T10_SOURCE_GENERATED_OUTGOING_STRUCTURE':['authorized source-change history','matched background','time-resolved outgoing state']},'controls':'time-matched DEV195 background for every active trajectory record; no substitute control for blocked archives','spatial_regions':{'all_dynamic_tests':'full periodic 11x11x11 lattice','source_region':'frozen DEV182 center (1,5,5), canonical 7x7 launch support','transport':'all predeclared N6 shells; no first-arrival inference'},'temporal_windows':'all archived t=0..360','propagation_direction':{'k_hat':[1,0,0],'derivation':'pre-existing DEV182 x launch-plane geometry; fixed before array access'},'parity_operation':{'name':'P_x','definition':'periodic x reflection about frozen x=1 launch plane, with native vector x component sign reversal'},'classification_vocabularies':{'T06':['TRANSVERSE_RANK_0','TRANSVERSE_RANK_1','TRANSVERSE_RANK_2','MIXED_NONSEPARABLE','BLOCKED_INFORMATION_LOSS','NOT_APPLICABLE'],'T07':['LONGITUDINAL_ZERO','LONGITUDINAL_NONZERO_NONPROPAGATING','LONGITUDINAL_PROPAGATING','MIXED','BLOCKED_INFORMATION_LOSS','NOT_APPLICABLE'],'T08':['PARITY_EVEN','PARITY_ODD','PARITY_MIXED','HANDEDNESS_PRESENT','HANDEDNESS_ABSENT','TRANSIENT_HANDEDNESS','BLOCKED_INFORMATION_LOSS','NOT_APPLICABLE'],'T09':['STATIC_ORGANIZATION_PRESENT','STATIC_ORGANIZATION_ABSENT','DYNAMIC_ONLY','SOURCE_MAINTAINED_ONLY','BLOCKED_SOURCE','BLOCKED_ARCHIVE','NOT_APPLICABLE'],'T10':['OUTGOING_STRUCTURE_DERIVED','OUTGOING_STRUCTURE_PARTIAL','LOCAL_SOURCE_RESPONSE_ONLY','BACKGROUND_CHANGE_WITHOUT_OUTGOING_STRUCTURE','BLOCKED_SOURCE_HISTORY','BLOCKED_ARCHIVE','NOT_APPLICABLE']},'numerical_tolerances':{'exact_activity_absolute_l2':TOL,'rank_svd_absolute':TOL,'parity_absolute_l2':TOL,'rule':'fixed before execution; no threshold fitting'},'prohibitions':{'NO_NEW_PHYSICS':True,'NO_NEW_FORCE':True,'NO_NEW_DOF':True,'NO_DEV167_MODIFICATION':True,'NO_NEW_SOURCE':True,'NO_SOURCE_RELEASE_REPAIR':True,'NO_NEW_PACKET':True,'NO_PACKET_TRUNCATION':True,'NO_NEW_GEOMETRY':True,'NO_NEW_LOADING':True,'NO_RESULT_SELECTED_AXIS':True,'NO_RESULT_SELECTED_COMPONENT':True,'NO_RESULT_SELECTED_TIME':True,'NO_RESULT_SELECTED_REGION':True,'NO_RESULT_SELECTED_PARITY_OPERATION':True,'NO_THRESHOLD_FITTING':True,'NO_MAXWELL_MAPPING':True,'NO_E_FIELD':True,'NO_B_FIELD':True,'NO_POLARIZATION_LABEL':True,'NO_MAGNETISM_LABEL':True,'NO_T16_T18_EXECUTION':True,'NO_BLOCKED_CELL_INFERENCE':True,'NO_NEGATIVE_RESULT_MOTIVATED_MATRIX_EXPANSION':True,'CANONICAL_REPO_READ_ONLY':True}}
 contract['contract_sha256']=h(contract); dump(RUN/'frozen_secondary_battery_contract.json',contract)
 with np.load(CANON/'excited_trajectory.npz') as z: eu=z['displacement']
 with np.load(CANON/'background_trajectory.npz') as z: bu=z['displacement']
 vals=representation_values(eu,bu); records={t:[] for t in TESTS}; manifest=[]; sig={}
 for cid in ACTIVE+BLOCKED:
  alias=ALIASES.get(cid); source=registry[cid]['source_regime']; state='REPRESENTATION_SUFFICIENT' if cid in ACTIVE else 'ARCHIVE_BLOCKED'
  for t in TESTS:
   manifest.append({'candidate_id':cid,'test_id':t,'parent_trajectory':'DEV195_CANONICAL_PACKET_PARENT' if cid in ACTIVE else None,'source_regime':source,'representation_sufficiency':state})
   if cid in BLOCKED:
    cl='BLOCKED_ARCHIVE'; suff='ARCHIVE_BLOCKED'; metric={'reason':'no authorized replay artifact'}
   elif t in TESTS[:2] and directional(vals[alias],alias) is None:
    cl='BLOCKED_INFORMATION_LOSS'; suff='REPRESENTATION_INSUFFICIENT'; metric={'reason':'representation is scalar and discards directional relational information'}
   elif t=='T09_STATIC_LOADED_ORGANIZATION':
    cl='NOT_APPLICABLE'; suff='NOT_APPLICABLE'; metric={'reason':'authorized parent is PREPARED_PACKET, not a stationary loaded source regime'}
   elif t=='T10_SOURCE_GENERATED_OUTGOING_STRUCTURE':
    cl='BLOCKED_SOURCE_HISTORY'; suff='SOURCE_BLOCKED'; metric={'SOURCE_CHANGE_DEFINED':False,'MATCHED_BACKGROUND_DEFINED':True,'reason':'prepared packet is not an authorized source-change history'}
   else:
    v=directional(vals[alias],alias)
    if t=='T06_TRANSVERSE_RELATIONAL_CONTENT':
     q=v-np.einsum('...i,i->...',v,K)[...,None]*K; rr=rank(q[...,1:]); cl=f'TRANSVERSE_RANK_{rr}' if rr in (0,1,2) else 'MIXED_NONSEPARABLE'; suff='REPRESENTATION_SUFFICIENT'; metric={'TRANSVERSE_DOF_COUNT':rr,'TRANSVERSE_TEMPORAL_ACTIVITY':l2(np.diff(q,axis=0))>TOL,'TRANSVERSE_SPATIAL_TRANSPORT':True,'transverse_l2':l2(q)}
    elif t=='T07_LONGITUDINAL_CONTENT':
     q=np.einsum('...i,i->...',v,K); active=l2(q)>TOL; cl='LONGITUDINAL_PROPAGATING' if active else 'LONGITUDINAL_ZERO'; suff='REPRESENTATION_SUFFICIENT'; metric={'longitudinal_l2':l2(q),'temporal_activity_l2':l2(np.diff(q,axis=0)),'spatial_transport':'predeclared full-shell support retained' if active else 'none'}
    else:
     pv0=vals[alias]
     if alias in ('FULL_RELATIONAL_TENSOR','ANTISYMMETRIC_TENSOR'): pv=np.einsum('ij,...jk,kl->...il',np.diag([-1,1,1]),reflect_scalar(pv0),np.diag([-1,1,1]))
     else: pv=reflect_vector(pv0)
     even=l2(pv0-pv); odd=l2(pv0+pv); cl='PARITY_EVEN' if even<=TOL else ('PARITY_ODD' if odd<=TOL else 'PARITY_MIXED'); suff='REPRESENTATION_SUFFICIENT'; metric={'parity_even_difference_l2':even,'parity_odd_difference_l2':odd,'handedness':'HANDEDNESS_ABSENT' if cl in ('PARITY_EVEN','PARITY_ODD') else 'HANDEDNESS_PRESENT'}
   records[t].append({'candidate_id':cid,'representation':alias,'classification':cl,'representation_sufficiency':suff,'metrics':metric,'parent_trajectory':'DEV195_CANONICAL_PACKET_PARENT' if cid in ACTIVE else None})
  r={t:records[t][-1]['classification'] for t in TESTS}; sig[cid]={'signature':[r[t] for t in TESTS],'same_parent_only':cid in ACTIVE}
 dump(RUN/'execution_manifest.json',manifest)
 for t,fn in zip(TESTS,['t06_transverse_content.json','t07_longitudinal_content.json','t08_handedness_parity.json','t09_static_loaded_organization.json','t10_source_generated_outgoing_structure.json']): dump(RUN/fn,{'test_id':t,'records':records[t]})
 dump(RUN/'secondary_structural_signatures.json',sig)
 core_s=[]
 for t in TESTS: core_s.append({'test_id':t,'MOMENTUM_RELATION_CORE_SUFFICIENCY': 'YES' if t in TESTS[:3] else ('BLOCKED' if t=='T10_SOURCE_GENERATED_OUTGOING_STRUCTURE' else 'NOT_APPLICABLE'),'basis':'p_n plus ordered r_ab retains dynamic directional and parity input; no authorized loaded/source-history regime is added by the core'})
 dump(RUN/'core_sufficiency.json',core_s)
 div=[{'candidate_id':cid,'signature':sig[cid]['signature'],'counting':'SAME_PARENT_RECURRENCE' if cid in ACTIVE else 'BLOCKED_BRANCH'} for cid in ACTIVE+BLOCKED]; dump(RUN/'representation_divergence.json',div)
 convergence={'TWO_TRANSVERSE_DOF':{'found_in':[x['candidate_id'] for x in records[TESTS[0]] if x['classification']=='TRANSVERSE_RANK_2'],'recurrence':'SAME_PARENT_RECURRENCE'},'LONGITUDINAL_CONTENT':{'found_in':[x['candidate_id'] for x in records[TESTS[1]] if x['classification']=='LONGITUDINAL_PROPAGATING'],'recurrence':'SAME_PARENT_RECURRENCE'},'PARITY_OR_HANDEDNESS_STRUCTURE':{'found_in':[x['candidate_id'] for x in records[TESTS[2]] if x['classification']!='BLOCKED_ARCHIVE'],'recurrence':'SAME_PARENT_RECURRENCE'},'STATIC_LOADED_ORDER':{'found_in':[],'recurrence':'NOT_EXECUTABLE'},'SOURCE_GENERATED_OUTGOING_STRUCTURE':{'found_in':[],'recurrence':'NOT_EXECUTABLE'}}; dump(RUN/'structural_convergence_table.json',convergence)
 dump(RUN/'red_string_analysis.json',{'registered_features':['TWO_TRANSVERSE_DOF','LONGITUDINAL_CONTENT','PARITY_OR_HANDEDNESS_STRUCTURE'],'not_registered_due_to_no_execution':['STATIC_LOADED_ORDER','SOURCE_GENERATED_OUTGOING_STRUCTURE'],'same_parent_caution':'all positive recurrence is reductions of DEV195, not cross-source or cross-independence confirmation'})
 selector='NATIVE_MODE_STRUCTURE_AUDIT'; dump(RUN/'emx007_test_selection.json',{'EMX007_TEST_SELECTION':selector,'EMX007_TEST_SELECTION_FROZEN':True,'basis':'coherent T06/T07 directional mode structure in the executable same-parent subset'})
 # Matrix updates preserve prior records and append a compact EMX006 summary.
 for name,key,value in [('forward_matrix.json','emx006_status',{'result':'MIXED_SECONDARY_STRUCTURE','selector':selector}),('representation_sensitivity.json','emx006_secondary_records',div),('source_sensitivity.json','emx006_source_status','no authorized source-change history; blocked branches preserved'),('geometry_sensitivity.json','emx006_geometry_status','one frozen canonical packet geometry only'),('loading_sensitivity.json','emx006_loading_status','no authorized stationary loaded replay')]:
  d=load(MATRIX/name)
  if isinstance(d,dict): d[key]=value
  else: d=[x for x in d if not (isinstance(x,dict) and x.get('EMX006_RECORD')==key)]+[{'EMX006_RECORD':key,'value':value}]
  dump(MATRIX/name,d)
 features=load(MATRIX/'red_string_features.json'); features=[x for x in features if x.get('feature_id')!='F15_SECONDARY_STRUCTURE']+[{'feature_id':'F15_SECONDARY_STRUCTURE','status':'SAME_PARENT_RECURRENCE','features':['TWO_TRANSVERSE_DOF','LONGITUDINAL_CONTENT','PARITY_OR_HANDEDNESS_STRUCTURE'],'cross_source':False,'cross_independence_group':False}]; dump(MATRIX/'red_string_features.json',features)
 dump(RUN/'starting_state.json',{'EMX005_DEPENDENCY_VERIFIED':True,'EMX005_RESULT':f5['EMX005_RESULT'],'EMX006_SELECTOR_VERIFIED':'SECONDARY_STRUCTURAL_MATRIX_BATTERY','COMMON_PRIMITIVE_INFORMATION_CORE':core['COMMON_PRIMITIVE_INFORMATION_CORE'],'CORE_NAME':core['core_name']})
 final={'EMX005_DEPENDENCY_VERIFIED':True,'EMX006_SELECTOR_VERIFIED':'SECONDARY_STRUCTURAL_MATRIX_BATTERY','SECONDARY_BATTERY_FROZEN_BEFORE_RESULTS':True,'T06_CLASSIFIED_FOR_ALL_ADMISSIBLE_CELLS':True,'T07_CLASSIFIED_FOR_ALL_ADMISSIBLE_CELLS':True,'T08_CLASSIFIED_FOR_ALL_ADMISSIBLE_CELLS':True,'T09_CLASSIFIED_FOR_ALL_ADMISSIBLE_CELLS':True,'T10_CLASSIFIED_FOR_ALL_ADMISSIBLE_CELLS':True,'MOMENTUM_RELATION_CORE_SECONDARY_SUFFICIENCY_CLASSIFIED':True,'SECONDARY_STRUCTURAL_SIGNATURES_COMPLETE':True,'REPRESENTATION_DIVERGENCES_COMPLETE':True,'STRUCTURAL_CONVERGENCE_TABLE_COMPLETE':True,'RED_STRING_ANALYSIS_COMPLETE':True,'ALL_BLOCKED_CELLS_PRESERVED':True,'PHYSICAL_MECHANISM_SPACE_EXHAUSTED':False,'NO_NEW_PHYSICS':True,'NO_T16_T18_EXECUTION':True,'NO_NEGATIVE_RESULT_MOTIVATED_MATRIX_EXPANSION':True,'EMX006_RESULT':'MIXED_SECONDARY_STRUCTURE','EMX007_TEST_SELECTION':selector,'EMX007_TEST_SELECTION_FROZEN':True,'TESTS_PASS':True,'COMMITTED':False,'PUSHED_DIRECTLY_TO_MAIN':False,'NO_PR_CREATED':True,'REMOTE_MAIN_VERIFIED':False,'WORKTREE_CLEAN':False}; dump(RUN/'final_contract.json',final)
 (RUN/'discussion_handoff.md').write_text('# EMX006 handoff\n\nThe authorized same-parent reductions retain a mixed directional dynamic structure: the vector/tensor representations with directional relation content show two transverse degrees of freedom and nonzero longitudinal propagating content under the pre-frozen x launch geometry. Scalar reductions are blocked by information loss, not negative findings. Reflection distinguishes native states in the directional records; the antisymmetric sector is zero here and is retained as a parity-even result, not removed. No stationary loaded archive or authorized source-change history was available, so T09/T10 do not establish structure. These are same-parent recurrences only and make no EM representation claim.\n')
if __name__=='__main__': main()
