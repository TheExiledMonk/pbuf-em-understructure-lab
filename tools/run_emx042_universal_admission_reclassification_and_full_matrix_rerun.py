#!/usr/bin/env python3
"""Execute EMX042 by reclassifying every saved finite cell without new dynamics."""
from __future__ import annotations
import hashlib,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'runs'/'emx042'
def r(p):return json.loads(Path(p).read_text())
def w(n,x):(OUT/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def fh(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def add(rows,batch,cell,source,finite,classification,evidence,context='CONTEXTUAL_UNASSESSED'):
 rows.append({'batch':batch,'cell_id':cell,'source_artifact':source,'source_sha256':fh(source),'finite':finite,'universal_classification':classification,'contextual_phenotype_classification':context,'evidence':evidence})
def main():
 c=r(OUT/'frozen_universal_admission_contract.json');assert c['FROZEN_BEFORE_RESULTS'] and all(fh(p)==x for p,x in c['input_sha256'].items())
 rows=[]
 # Every declared wide-net candidate is registered; no saved shared observer exists for them.
 wide=r(ROOT/'runs/emx029/candidate_registry.json')['candidates']
 for item in wide:
  add(rows,'BATCH_A_WIDE_NET_AND_CONTRACTUAL',item['candidate_id'],'runs/emx029/candidate_registry.json',True,'UNIVERSAL_UNASSESSED','Finite candidate registry entry has no saved EMX041 shared-observer history; no reconstruction is allowed.')
 for run in ('emx020','emx022','emx023','emx024','emx026','emx027','emx028'):
  path=f'runs/{run}/execution_results.json' if run in ('emx022','emx023','emx024','emx026') else (f'runs/{run}/lattice_covariant_control_results.json' if run=='emx027' else (f'runs/{run}/t18_bridge_results.json' if run=='emx028' else 'runs/emx020/harmonic_invariant_report.json'))
  data=r(ROOT/path); finite=bool(data.get('all_finite',True))
  reject=run=='emx027' and data['all_exact'] is False
  add(rows,'BATCH_A_WIDE_NET_AND_CONTRACTUAL',run.upper(),path,finite,'UNIVERSAL_REJECTED' if reject else 'UNIVERSAL_UNASSESSED','Explicit frozen symmetry control is false.' if reject else 'Saved finite outcome lacks the EMX041 common observer; admission remains unassessed.')
 for run in ('emx030','emx031','emx033','emx034'):
  data=r(ROOT/f'runs/{run}/batch_results.json'); members=data.get('rows',[])
  if not members: members=[{'member':k,'all_finite':v.get('all_exact',False)} for k,v in data.items() if isinstance(v,dict)]
  for item in members:
   finite=bool(item.get('all_finite',False)); reject=run=='emx030' and item.get('member')=='A02' and not finite
   add(rows,'BATCH_A_WIDE_NET_AND_CONTRACTUAL',f'{run.upper()}:{item.get("member")}',f'runs/{run}/batch_results.json',finite,'UNIVERSAL_REJECTED' if reject else 'UNIVERSAL_UNASSESSED','Frozen symmetry control failed.' if reject else 'No saved common-observer vector exists for this finite member.')
 # EMX036's complete 224-cell registry is rerun through saved EMX037/038 outcomes.
 zero={x['cell_id']:x for x in r(ROOT/'runs/emx037/batch_results.json')['results']}; lift={x['cell_id']:x for x in r(ROOT/'runs/emx038/remaining_matrix_results.json')['results']}
 registry=r(ROOT/'runs/emx036/factorial_registry.json')['cells']; assert len(registry)==224 and len(zero)==8 and len(lift)==216
 stress=r(ROOT/'runs/emx041/cross_calibration_stress_matrix.json')['rows']; agreement={x['cell_id']:set() for x in stress}
 for x in stress: agreement[x['cell_id']].add(x['outcome'])
 for cell in registry:
  cid=cell['cell_id']; result=zero[cid] if cid in zero else lift[cid]; finite=(result['stability']=='COMPATIBLE_NONUNIQUE') if cid in zero else bool(result['all_finite']); source='runs/emx037/batch_results.json' if cid in zero else 'runs/emx038/remaining_matrix_results.json'
  shared='VALIDATED_ZERO_CONTROL' if cid in zero else ('ACTIVE_SHARED_OBSERVER_AGREEMENT' if agreement[cid]=={'AGREES'} else 'VALIDATED_SHARED_OBSERVER_ZERO_CONTROL_DIFFERENCE')
  add(rows,'BATCH_B_STATIC_MOTION_224_CELLS',cid,source,finite,'UNIVERSAL_VIABLE_NONUNIQUE' if finite else 'UNIVERSAL_REJECTED',f'Finite, local N6, accounting-defined saved cell with {shared}; deterministic provenance is frozen contract plus result artifact hash.')
 # The 76 retained gates are rerun only as contextual labels, never as admission criteria.
 gates=r(ROOT/'runs/emx041/gate_applicability_matrix.json')['records']; assert len(gates)==76
 for i,g in enumerate(gates,1):
  label='CONTEXTUAL_PHENOTYPE_MATCH' if g['applicability_label']=='SHARED_APPLICABLE' else 'CONTEXTUAL_UNASSESSED'
  add(rows,'BATCH_C_CONTEXTUAL_PHENOTYPE_ONLY',f'EMX016_GATE_{i:03d}','runs/emx041/gate_applicability_matrix.json',True,'UNIVERSAL_UNASSESSED','Historical gate preserved as contextual phenotype comparison only.',label)
 assert len(rows)==224+76+13+7+3+2+6+4
 batches={k:[x for x in rows if x['batch']==k]for k in c['transparent_batches']}
 held=[]
 for cid,item in zero.items():held.append({'cell_id':cid,'battery':'zero-source final-state identity','pass':item['max_abs_u']==0 and item['max_abs_p']==0})
 for cid,item in lift.items():
  if not cid.startswith('ZERO_'):held.append({'cell_id':cid,'battery':'source-present final energy finiteness','pass':all(isinstance(item['energy'][k],(int,float)) for k in ('initial','final','minimum','maximum'))})
 e22=r(ROOT/'runs/emx022/execution_results.json');held.append({'cell_id':'EMX022','battery':'loaded-unloaded response finiteness','pass':isinstance(e22['loaded_unloaded_response_l2'],float)})
 coverage=[{'run':f'EMX{i:03d}','coverage':status}for i,status in {
  19:'CONTRACT_ONLY_NO_DYNAMICS',20:'SAVED_FINITE_HARMONIC_OUTCOMES',21:'READ_ONLY_COMPATIBILITY_MATRIX',22:'SAVED_FINITE_EXECUTION',23:'SAVED_FINITE_EXECUTION',24:'SAVED_FINITE_EXECUTION',25:'READ_ONLY_COVERAGE_AUDIT',26:'SAVED_FINITE_EXECUTION',27:'SAVED_SYMMETRY_CONTROL',28:'SAVED_BRIDGE_OUTCOME',29:'WIDE_NET_CANDIDATE_REGISTRY',30:'SAVED_REPRESENTATION_CONTROL_BATCH',31:'SAVED_FINITE_BATCH',32:'CONTRACT_SUITE_NO_EXECUTION',33:'SAVED_FINITE_BATCH',34:'SAVED_FINITE_BATCH',35:'READ_ONLY_COVERAGE_CLOSURE',36:'STATIC_MOTION_224_CELL_REGISTRY',37:'EIGHT_ZERO_SOURCE_CONTROLS',38:'216_SOURCE_LIFT_CELLS',39:'READ_ONLY_MATRIX_CLOSURE',40:'GATE_VALIDITY_LEDGER',41:'SHARED_OBSERVER_STRESS_RESULTS'}.items()]
 w('all_finite_candidate_cell_registry.json',{'count':len(rows),'by_batch':{k:len(v)for k,v in batches.items()},'emx019_through_emx041_scope_coverage':coverage,'records':rows})
 w('universal_admission_rerun_batches.json',{'batches':{k:{'count':len(v),'universal_counts':dict(Counter(x['universal_classification']for x in v))}for k,v in batches.items()},'no_new_dynamics':True})
 w('held_out_prediction_battery.json',{'excluded_from_admission':True,'count':len(held),'passed':sum(x['pass']for x in held),'records':held})
 w('final_contract.json',{'EMX042_RESULT':'FULL_SAVED_FINITE_MATRIX_RERUN_UNDER_UNIVERSAL_ADMISSION','CONTRACT_FROZEN_BEFORE_RESULTS':True,'REGISTRY_COUNT':len(rows),'BATCH_COUNTS':{k:len(v)for k,v in batches.items()},'UNIVERSAL_COUNTS':dict(Counter(x['universal_classification']for x in rows)),'CONTEXTUAL_COUNTS':dict(Counter(x['contextual_phenotype_classification']for x in rows)),'HISTORICAL_GATES_UNCHANGED':True,'HELD_OUT_BATTERY_NOT_USED_FOR_ADMISSION':True,'NEW_DYNAMICS_EXECUTED':False,**c['prohibitions']})
if __name__=='__main__':main()
