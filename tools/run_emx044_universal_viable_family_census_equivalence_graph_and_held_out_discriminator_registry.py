#!/usr/bin/env python3
"""Read-only EMX044 census and held-out discriminators from saved histories."""
from __future__ import annotations
import hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'runs'/'emx044'
def r(p):return json.loads(Path(p).read_text())
def w(n,x):(OUT/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def fh(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 c=r(OUT/'frozen_family_census_contract.json');assert c['FROZEN_BEFORE_RESULTS'] and all(fh(ROOT/p)==d for p,d in c['input_sha256'].items())
 prior=r(ROOT/'runs/emx042/all_finite_candidate_cell_registry.json')['records'];recovered=r(ROOT/'runs/emx043/universal_unassessed_completion_matrix.json')['records']
 viable=[x for x in prior if x['universal_classification']=='UNIVERSAL_VIABLE_NONUNIQUE']+[x for x in recovered if x['classification']=='UNIVERSAL_VIABLE_NONUNIQUE'];assert len(viable)==c['viable_count_expected']
 local={x['cell_id']:x for x in r(ROOT/'runs/emx038/remaining_matrix_results.json')['results']};zero={x['cell_id']:x for x in r(ROOT/'runs/emx037/batch_results.json')['results']}
 stress=r(ROOT/'runs/emx041/cross_calibration_stress_matrix.json')['rows'];sig=defaultdict(set)
 for x in stress:sig[x['cell_id']].add(x['outcome'])
 census=[]
 for x in viable:
  cid=x['cell_id'];is_local=cid in local or cid in zero
  if is_local:
   result=local.get(cid,zero.get(cid)); active=cid in local and sig[cid]=={'AGREES'}
   family='LOCAL_NEUTRAL_HARMONIC_PERIODIC_N6';signature='ACTIVE_SHARED_OBSERVER' if active else 'ZERO_SOURCE_SHARED_CONTROL'
   variants={'source_count':cid.split('_')[0],'preparation':cid.split('_')[1],'reversal':cid.rsplit('_',1)[-1],'variant_kind':'source/preparation/reversal/control'}
   state='native u,p source-lift relative to zero background';interaction='unit harmonic nearest-neighbour N6';update='kick-drift dt=.04, 180 steps';geometry='11^3 periodic N6'
  else:
   family='HISTORICAL_DEV167_PREPARED_PACKET';signature='ACTIVE_SHARED_OBSERVER';variants={'variant_kind':'historical representation/contextual gate' if cid.startswith('EMX016') else 'global-sign representation variant'};state='DEV195 excited-minus-matched-background native u,p';interaction='DEV167 native vector central pair';update='historically hash-pinned replay';geometry='11^3 periodic N6'
  census.append({'cell_id':cid,'family_id':family,'shared_observer_signature':signature,'state':state,'geometry':geometry,'interaction':interaction,'update':update,'independent_mechanism_family':family,'variants':variants,'historical_contextual_only':not is_local})
 groups=defaultdict(list)
 for x in census:groups[(x['family_id'],x['shared_observer_signature'])].append(x['cell_id'])
 certificates=[{'certificate_id':f'EC{i:03d}','family_id':k[0],'shared_observer_signature':k[1],'members':sorted(v),'member_count':len(v),'claim':'Equivalent only under the frozen shared-observer behavior within this fixed family; nonunique branches retained.'}for i,(k,v)in enumerate(sorted(groups.items()),1)]
 graph={'nodes':[{'node_id':z['certificate_id'],'family_id':z['family_id'],'signature':z['shared_observer_signature'],'member_count':z['member_count']}for z in certificates],'edges':[],'cross_family_rule':'No edge is added across distinct interaction/update families.'}
 # Held-out execution uses existing complete scalar histories only.
 held=[]
 for cid,x in local.items():
  e=x['energy'];held.append({'batch':'LOCAL_ENERGY_AND_REVERSAL','cell_id':cid,'discriminator':'energy_accounting','status':'EXECUTED_FINITE','value':float(e['final']-e['initial'])})
  reversal=next(v for v in ('IDENTITY','TIME_REVERSE','PARITY_X','YZ_SWAP') if cid.endswith('_'+v));base=cid[:-len(reversal)]+'IDENTITY'
  if base in local and reversal!='IDENTITY':held.append({'batch':'LOCAL_ENERGY_AND_REVERSAL','cell_id':cid,'discriminator':'reversal_native_norm_history','status':'EXECUTED_IDENTICAL' if np.array_equal(x['energy']['history_l2_norm'],local[base]['energy']['history_l2_norm']) else 'EXECUTED_DIFFERS','reference':base})
 for cid,x in zero.items():held.append({'batch':'ZERO_SOURCE_AND_BOUNDARY','cell_id':cid,'discriminator':'zero_source_identity_and_periodic_boundary','status':'EXECUTED_PASS' if x['max_abs_u']==0 and x['max_abs_p']==0 else 'EXECUTED_DIFFER'})
 held.append({'batch':'HISTORICAL_ACCOUNTING','cell_id':'HISTORICAL_DEV167_PREPARED_PACKET','discriminator':'historical_hash_pinned_native_invariant','status':'EXECUTED_EXISTING_HASH_PINNED','observer_hash':r(ROOT/'runs/emx041/shared_observer_definition.json')['historical_history_sha256']})
 for disc,reason in [('reciprocity','no separately frozen A/B exchange replay exists'),('transport_dispersion_scaling','no saved spatial local-source histories exist'),('independent_packet_shapes','only one hash-pinned historical packet shape is available')]:held.append({'batch':'UNAVAILABLE_PROVENANCE_BOUNDARIES','cell_id':'FAMILY_LEVEL','discriminator':disc,'status':'UNAVAILABLE_PROVENANCE','reason':reason})
 assert all(x['historical_contextual_only'] for x in census if x['family_id'].startswith('HISTORICAL'))
 w('universal_viable_family_census.json',{'count':len(census),'family_counts':dict(Counter(x['family_id']for x in census)),'records':census})
 w('evidence_preserving_equivalence_graph.json',{'equivalence_certificates':certificates,'graph':graph})
 w('held_out_discriminator_execution_plan_and_results.json',{'excluded_from_admission':True,'batches':c['batches'],'executed_or_unavailable_count':len(held),'status_counts':dict(Counter(x['status']for x in held)),'records':held})
 w('final_contract.json',{'EMX044_RESULT':'UNIVERSAL_VIABLE_FAMILY_CENSUS_AND_HELD_OUT_REGISTRY_COMPLETE','CONTRACT_FROZEN_BEFORE_RESULTS':True,'UNIVERSAL_VIABLE_COUNT':len(census),'FAMILY_COUNT':len(set(x['family_id']for x in census)),'EQUIVALENCE_CERTIFICATE_COUNT':len(certificates),'HELD_OUT_NOT_USED_FOR_ADMISSION':True,'HISTORICAL_GATES_CONTEXTUAL_ONLY':True,'UNAVAILABLE_BOUNDARIES':sum(x['status']=='UNAVAILABLE_PROVENANCE'for x in held),'NEW_DYNAMICS_EXECUTED':False,**c['prohibitions']})
if __name__=='__main__':main()
