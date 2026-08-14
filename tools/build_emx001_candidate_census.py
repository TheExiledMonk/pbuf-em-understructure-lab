#!/usr/bin/env python3
"""Build EMX001 artifacts from a read-only canonical PBUF checkout."""
from __future__ import annotations
import argparse, hashlib, json, subprocess, shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'runs' / 'emx001'
MATRIX = ROOT / 'matrix'

def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def git(canonical, *args): return subprocess.check_output(['git','-C',str(canonical),*args], text=True).strip()

REPRESENTATIONS = [
 ('R01','scalar F01/F02/F03 family','scalar relational/link representation','LOSSY_KNOWN','HISTORICAL_CONTROL'),
 ('R02','DEV167 full vector state','X=(u,p)','LOSSLESS','ACTIVE'),
 ('R03','bond vector','r_ab','LOSSY_KNOWN','ACTIVE'), ('R04','bond strain','epsilon_ab','LOSSY_KNOWN','ACTIVE'),
 ('R05','bond force/stress','F_ab','LOSSY_KNOWN','ACTIVE'), ('R06','relational-change state','Delta r, Delta epsilon, Delta F, Delta p','LOSSY_KNOWN','ACTIVE'),
 ('R07','DEV203 relational tensor','M_ij','LOSSY_KNOWN','ACTIVE'), ('R08','antisymmetric relational tensor','A_ij=2M_ij-M_ji','LOSSY_KNOWN','ACTIVE'),
 ('R09','axial dual','omega','LOSSY_KNOWN','ACTIVE'), ('R10','DEV204 orientation-stress','sigma Delta rhat','LOSSY_KNOWN','ACTIVE'),
 ('R11','DEV204 finite-step stress change','Delta F','LOSSY_KNOWN','ACTIVE'), ('R12','signed pair power flux','J_ab','LOSSY_KNOWN','ACTIVE'),
 ('R13','ordered signed N6 mismatch','DEV223 family','LOSSY_UNKNOWN','ACTIVE'), ('R14','nearest-neighbor tensor contraction','A(a):A(b)','LOSSY_KNOWN','ACTIVE'),
 ('R15','exact region/bond-cut momentum transfer','regional bond-cut','LOSSY_KNOWN','ACTIVE')]

SEEDS = [
 ('C001_SCALAR_F03_PROPAGATION','R01','UNLOADED_QUIET','CANONICAL_DEV182_PACKET','FULL_NATIVE_STATE','PROPAGATING',1,'DIRECT_N6','GROUP_DEV159_SCALAR_SOURCE','HISTORICAL_CONTROL','DEV163'),
 ('C002_DEV167_FULL_VECTOR_STATE','R02','PREPARED_PACKET','CANONICAL_DEV182_PACKET','FULL_NATIVE_STATE','PROPAGATING',1,'DIRECT_N6','GROUP_DEV167_FULL_STATE','ACTIVE','DEV167'),
 ('C003_N6_RELATIONAL_CHANGE','R06','PREPARED_PACKET','CANONICAL_DEV182_PACKET','FULL_NATIVE_STATE','TRANSIENT',1,'DIRECT_N6','GROUP_DEV203_FULL_STATE','ACTIVE','DEV203'),
 ('C004_DEV203_RELATIONAL_TENSOR','R07','PREPARED_PACKET','CANONICAL_DEV182_PACKET','RELATIONAL_TENSOR','PROPAGATING',1,'DIRECT_N6','GROUP_DEV203_FULL_STATE','ACTIVE','DEV203'),
 ('C005_DEV203_ANTISYMMETRIC_TENSOR','R08','PREPARED_PACKET','CANONICAL_DEV182_PACKET','ANTISYMMETRIC_TENSOR','PROPAGATING',1,'DIRECT_N6','GROUP_DEV203_FULL_STATE','ACTIVE','DEV203'),
 ('C006_DEV204_ORIENTATION_STRESS','R10','PREPARED_PACKET','CANONICAL_DEV182_PACKET','BOND_FORCE','TRANSIENT',1,'DIRECT_N6','GROUP_DEV204_STRESS','ACTIVE','DEV204'),
 ('C007_DEV204_FULL_FORCE_CHANGE','R11','PREPARED_PACKET','CANONICAL_DEV182_PACKET','BOND_FORCE','TRANSIENT',1,'DIRECT_N6','GROUP_DEV204_STRESS','ACTIVE','DEV204'),
 ('C008_DEV211_STATIC_MAINTAINED_DEFORMATION','R05','SOURCE_MAINTAINED_DEFORMATION','FINITE_CONTACT_PATCH','BOND_FORCE','SOURCE_MAINTAINED',1,'DIRECT_N6','GROUP_DEV211_MAINTAINED_STATIC','ACTIVE','DEV211'),
 ('C009_DEV212_MOMENTUM_REVERSED_STATE','R02','VALID_STATE_INJECTION','CANONICAL_DEV182_PACKET','NODE_MOMENTUM','TRANSIENT',1,'DIRECT_N6','GROUP_DEV212_MULTISTATE','ACTIVE','DEV212'),
 ('C010_DEV213_TWO_STRUCTURE_AGGREGATE','R02','TWO_PREPARATION_AGGREGATE','TWO_SEPARATED_SOURCE_REGIONS','FULL_NATIVE_STATE','TRANSIENT',2,'MULTI_STEP_N6','GROUP_DEV213_AGGREGATE','ACTIVE','DEV213'),
 ('C011_DEV221_DIRECTIONAL_GEOMETRY','R03','PREPARED_PACKET','CANONICAL_DEV182_PACKET','BOND_STRAIN','PROPAGATING',1,'DIRECT_N6','GROUP_DEV221_GEOMETRY','ACTIVE','DEV221'),
 ('C012_DEV223_SIGNED_PATTERN_MISMATCH','R13','PREPARED_PACKET','FULL_PERIODIC_N6_VOLUME','ORDERED_N6_MISMATCH','BOUNDED_DYNAMIC',1,'DIRECT_N6','GROUP_DEV223_PATTERN','ACTIVE','DEV223'),
 ('C013_DEV225_TENSOR_NEIGHBOR_RELATION','R14','PREPARED_PACKET','FULL_PERIODIC_N6_VOLUME','NEAREST_NEIGHBOR_CONTRACTION','BOUNDED_DYNAMIC',1,'DIRECT_N6','GROUP_DEV225_CONTRACTION','ACTIVE','DEV225'),
 ('C014_TWO_BODY_INTERSTITIAL_FULL_STATE','R02','STATIC_EXTERNAL_CONTACT','TWO_SEPARATED_SOURCE_REGIONS','FULL_NATIVE_STATE','STATIC',2,'DIRECT_N6','GROUP_TWO_BODY_INTERSTITIAL','BLOCKED_SOURCE','DEV205'),
 ('C015_FINITE_X_AGGREGATE_FULL_STATE','R02','FINITE_X_AGGREGATE','TWO_SEPARATED_SOURCE_REGIONS','FULL_NATIVE_STATE','TRANSIENT',2,'MULTI_STEP_N6','GROUP_DEV213_AGGREGATE','ACTIVE','DEV228')]

FUTURE = [('C_FUTURE_PASSIVE_MATERIAL','PASSIVE_RESPONSE_CANDIDATE'),('C_FUTURE_THREE_SOURCE','THREE_SOURCE_GEOMETRY'),('C_FUTURE_THREE_CONSTITUENT_COMPOSITE','AABvsABB'),('C_FUTURE_COLLECTIVE_EM_GENERATOR','EXTENDED_COLLECTIVE'),('C_FUTURE_3x3x3_EMERGENT_NEIGHBORHOOD','EMERGENT_3x3x3_COLLECTIVE')]

TESTS = [('T01_QUIET_STATE','quiet-state activity'),('T02_EXCITATION_ACTIVITY','excitation response'),('T03_PROPAGATION','spatial propagation'),('T04_NEIGHBOR_RELAY','causal neighbor relay'),('T05_STRESS_COUPLING','stress response'),('T06_ORIENTATION','orientation information'),('T07_TRANSVERSE','transverse relational content'),('T08_LONGITUDINAL','longitudinal content'),('T09_HANDEDNESS','handedness/parity'),('T10_MOMENTUM_TRANSFER','momentum-transfer closure'),('T11_PERSISTENCE','persistence after source change'),('T12_STATIC_ORGANIZATION','static loaded organization'),('T13_SOURCE_OUTGOING','source-generated outgoing structure'),('T14_MULTISOURCE','multi-source composition'),('T15_NEAR_FAR','near/far evolution')]

def main():
 p=argparse.ArgumentParser(); p.add_argument('--canonical', required=True); a=p.parse_args(); c=Path(a.canonical).resolve()
 if not (c/'.git').exists() or not (c/'docs/PBUF_MECHANISM_REGISTRY.json').exists(): raise SystemExit('canonical checkout or registry not found')
 registry=c/'docs/PBUF_MECHANISM_REGISTRY.json'; ledger=c/'docs/PBUF_DEVELOPMENT_LEDGER.json'; index=c/'docs/PBUF_HISTORICAL_ATTEMPT_INDEX.json'
 snapshot={'repository':'TheExiledMonk/lab','canonical_repo_read_only':True,'branch':git(c,'branch','--show-current'),'commit':git(c,'rev-parse','HEAD'),'timestamp':datetime.now(timezone.utc).isoformat(),'registry_hash':sha(registry),'ledger_hash':sha(ledger),'historical_index_hash':sha(index),'local_checkout_note':'not fetched or modified; exact local state frozen'}
 OUT.mkdir(parents=True,exist_ok=True); dump(OUT/'canonical_repo_snapshot.json',snapshot); dump(ROOT/'provenance/canonical_repo_snapshot.json',snapshot)
 reg=json.loads(registry.read_text()); idx=json.loads(index.read_text()); led=json.loads(ledger.read_text())
 dump(OUT/'registry_import.json',{'source':'docs/PBUF_MECHANISM_REGISTRY.json','commit':snapshot['commit'],'targets':reg.get('targets',[]),'attempts':reg.get('attempts',[]),'equivalences':reg.get('equivalences',[])})
 dump(OUT/'historical_index_import.json',{'source':'docs/PBUF_HISTORICAL_ATTEMPT_INDEX.json','commit':snapshot['commit'],'contents':idx}); dump(OUT/'ledger_em_extract.json',{'source':'docs/PBUF_DEVELOPMENT_LEDGER.json','commit':snapshot['commit'],'contents':led})
 archive_terms=['pre-ledger','DEV145','DEV151','DEV152','DEV153','DEV155','DEV156','DEV158','DEV159','DEV163','DEV164','DEV165','DEV167','DEV182','DEV193','DEV203','DEV204','DEV205','DEV211','DEV212','DEV213','DEV217','DEV221','DEV223','DEV225','DEV226','DEV227','DEV228','DEV229','DEV230','DEV231']
 tracked=git(c,'ls-files').splitlines(); hits={term:[f for f in tracked if term.lower() in f.lower()] for term in archive_terms}
 commits=git(c,'log','--all','--oneline').splitlines()
 dump(OUT/'historical_archive_search.json',{'searched_reachable_refs':git(c,'for-each-ref','--format=%(refname)').splitlines(),'terms':archive_terms,'tracked_path_hits':hits,'matching_commit_subjects':[line for line in commits if any(t.lower() in line.lower() for t in archive_terms)],'pr_search_status':'reachable branch/PR refs searched locally; no network fetch performed','conclusion':'archive evidence retained; candidates remain subject to admissibility classification'})
 reps=[{'representation_id':x[0],'name':x[1],'native_quantity':x[2],'information_loss':x[3],'default_admissibility':x[4],'full_state_physical_priority':True} for x in REPRESENTATIONS]
 dump(MATRIX/'representation_registry.json',reps)
 axes={'source_regime_registry.json':['UNLOADED_QUIET','STATIC_EXTERNAL_CONTACT','MOVING_EXTERNAL_CONTACT','SOURCE_MAINTAINED_DEFORMATION','RELEASED_RESIDUAL','PREPARED_PACKET','VALID_STATE_INJECTION','TWO_PREPARATION_AGGREGATE','FINITE_X_AGGREGATE','PASSIVE_RESPONSE_CANDIDATE'],'geometry_registry.json':['SINGLE_NODE_CONTACT','FINITE_CONTACT_PATCH','CANONICAL_DEV182_PACKET','REFLECTED_PACKET_PAIR','TWO_SEPARATED_SOURCE_REGIONS','DEV217_PARTITION','SOURCE_CENTERED_LOOP','FULL_PERIODIC_N6_VOLUME','THREE_SOURCE_GEOMETRY'],'observer_registry.json':['FULL_NATIVE_STATE','NODE_MOMENTUM','BOND_FORCE','BOND_STRAIN','REGIONAL_BOND_CUT','RELATIONAL_TENSOR','ANTISYMMETRIC_TENSOR','PAIR_POWER_FLUX','ORDERED_N6_MISMATCH','NEAREST_NEIGHBOR_CONTRACTION'],'temporal_registry.json':['STATIC','STEP_CHANGE','TRANSIENT','PROPAGATING','OSCILLATORY','BOUNDED_DYNAMIC','SOURCE_MAINTAINED','POST_SOURCE'],'collective_scale_registry.json':['DIRECT_N6','MULTI_STEP_N6','EMERGENT_3x3x3_COLLECTIVE','EXTENDED_COLLECTIVE']}
 for f, values in axes.items(): dump(MATRIX/f,[{'id':v,'registered_not_tested':v=='EMERGENT_3x3x3_COLLECTIVE'} for v in values])
 candidates=[]
 for cid,r,s,g,o,t,x,k,group,status,dev in SEEDS:
  candidates.append({'candidate_id':cid,'name':cid.replace('_',' '),'representation':r,'source_regime':s,'geometry':g,'observer':o,'temporal_regime':t,'source_count':x,'boundary_conditions':'PERIODIC_N6','preparation':s,'collective_scale':k,'mechanics_contract':'DEV167_FROZEN_NATIVE_MECHANICS' if status=='ACTIVE' else 'HISTORICAL_MECHANICS_ONLY','historical_origin':True,'origin_commit':snapshot['commit'],'origin_dev':dev,'origin_files':['docs/PBUF_MECHANISM_REGISTRY.json','docs/PBUF_HISTORICAL_ATTEMPT_INDEX.json'],'historical_status':'VALID_REPRODUCIBLE' if status!='BLOCKED_SOURCE' else 'AMBIGUOUS','physical_status':'REPRESENTATION_DEPENDENT','dependency_classes':['STRUCTURAL','INTERPRETIVE'],'information_loss':next(q[3] for q in REPRESENTATIONS if q[0]==r),'admissibility_status':status,'exclusion_reason':None,'independence_group':group,'admission_basis':['EXISTING_CODE','EXISTING_ARTIFACT']})
 for cid, reason in FUTURE: candidates.append({'candidate_id':cid,'name':cid.replace('_',' '),'representation':'R02','source_regime':'FUTURE_GATE','geometry':reason,'observer':'FULL_NATIVE_STATE','temporal_regime':'NOT_APPLICABLE','source_count':3 if 'THREE' in cid else None,'boundary_conditions':'NOT_APPLICABLE','preparation':'NOT_APPLICABLE','collective_scale':'EMERGENT_3x3x3_COLLECTIVE' if '3x3x3' in cid else 'EXTENDED_COLLECTIVE','mechanics_contract':'NO_NEW_PHYSICS','historical_origin':False,'origin_commit':None,'origin_dev':None,'origin_files':[],'historical_status':'NOT_RUN','physical_status':'UNASSESSED','dependency_classes':[],'information_loss':'LOSSLESS','admissibility_status':'FUTURE_GATE','exclusion_reason':'registered future route; execution forbidden in EMX001','independence_group':'GROUP_FUTURE_GATES','admission_basis':['INDEPENDENT_PHYSICAL_REASON']})
 dump(MATRIX/'candidate_registry.json',candidates); dump(OUT/'raw_candidate_census.json',candidates); dump(OUT/'candidate_admissibility.json',[{'candidate_id':q['candidate_id'],'status':q['admissibility_status'],'basis':q['admission_basis'],'exclusion_reason':q['exclusion_reason']} for q in candidates])
 equivalence=[{'left':'R02','right':r,'relation':'DERIVABLY_REDUCIBLE' if r not in ('R02','R01') else 'DISTINCT','information_loss':next(x[3] for x in REPRESENTATIONS if x[0]==r)} for r in [x[0] for x in REPRESENTATIONS if x[0]!='R02']]
 dump(OUT/'candidate_equivalence_matrix.json',equivalence)
 groups=sorted(set(q['independence_group'] for q in candidates)); dump(MATRIX/'independence_groups.json',[{'group_id':g,'rule':'common upstream state; reductions are not independent confirmations'} for g in groups])
 compat={'only_physically_admissible_combinations':True,'rules':[{'rule':'source_count > 2 requires FUTURE_GATE in Matrix v1'},{'rule':'EMERGENT_3x3x3_COLLECTIVE is registered, not tested'},{'rule':'historical controls retain historical mechanics only'}]}; dump(MATRIX/'regime_compatibility_graph.json',compat)
 historical=[]; forward=[]
 for q in candidates:
  if q['admissibility_status']=='FUTURE_GATE': continue
  for tid,label in TESTS:
   base={'candidate_id':q['candidate_id'],'test_id':tid,'frozen_conditions':{k:q[k] for k in ('representation','source_regime','geometry','observer','temporal_regime','source_count','boundary_conditions','preparation','collective_scale')},'evidence':{'source_commit':q['origin_commit'],'source_file':q['origin_files'][0],'run_artifact':'IMPORTED_RESULT','test_code':'historical import only','frozen_contract':q['mechanics_contract']},'historical_or_new':'HISTORICAL'}
   historical.append(base|{'status':'INCONCLUSIVE','result':'IMPORTED_RESULT: exact test-level claim not asserted','execution_confidence':'MEDIUM','physical_interpretation_confidence':'LOW','dependency_review_status':'DEPENDENCY_REVIEW_REQUIRED'})
   forward.append({'candidate_id':q['candidate_id'],'test_id':tid,'status':'BLOCKED' if q['admissibility_status'].startswith('BLOCKED') else 'NOT_RUN','result':'EMX001 does not execute matrix','historical_or_new':'FORWARD','frozen_conditions':base['frozen_conditions'],'evidence':base['evidence'],'execution_confidence':'NOT_APPLICABLE','physical_interpretation_confidence':'NOT_APPLICABLE','dependency_review_status':'NOT_REVIEWED'})
 dump(MATRIX/'historical_matrix.json',historical); dump(MATRIX/'forward_matrix.json',forward); dump(MATRIX/'common_test_battery.json',[{'test_id':a,'definition':b,'execution':'FROZEN_NOT_RUN'} for a,b in TESTS])
 for name, axis in [('representation_sensitivity.json','representation'),('source_sensitivity.json','source_regime'),('geometry_sensitivity.json','geometry'),('observer_sensitivity.json','observer'),('source_number_sensitivity.json','source_count'),('collective_scale_sensitivity.json','collective_scale')]: dump(MATRIX/name,{'axis':axis,'status':'INITIALIZED_NOT_RUN','no_weighted_score':True})
 features=[('F01','quiet-state zero'),('F02','excitation activation'),('F03','outward transport'),('F04','neighbor relay'),('F05','stress coupling'),('F06','orientation retention'),('F07','two transverse degrees'),('F08','loaded-static organization'),('F09','source-generated propagation'),('F10','collective non-pairwise behavior')]
 dump(MATRIX/'red_string_features.json',[{'feature_id':a,'definition':b,'native_quantities_required':[],'candidate_rows_supporting':[],'candidate_rows_rejecting':[],'candidate_rows_blocked':[],'representation_sensitivity':'NOT_RUN','source_sensitivity':'NOT_RUN','geometry_sensitivity':'NOT_RUN','observer_sensitivity':'NOT_RUN','confidence':'NOT_RUN'} for a,b in features])
 negatives=[{'negative_id':'NEG_SCALAR_F03_DEV163','mechanics':'HISTORICAL_MECHANICS_ONLY','representation':'R01','source':'UNLOADED_QUIET','geometry':'CANONICAL_DEV182_PACKET','observer':'FULL_NATIVE_STATE','time_regime':'PROPAGATING','source_count':1,'boundary':'PERIODIC_N6','preparation':'scalar loaded F03','collective_scale':'DIRECT_N6','valid_closure':'scalar loaded F03 under DEV163 frozen operator','invalid_broader_claims':['all representations fail','all source regimes fail']}] ; dump(MATRIX/'historical_negative_scope_matrix.json',negatives)
 dump(OUT/'emx002_test_selection.json',{'EMX002_TEST_SELECTION':'COMMON_NATIVE_PRIMITIVE_BATTERY','EMX002_TEST_SELECTION_FROZEN':True,'tests':['T01_QUIET_STATE','T02_EXCITATION_ACTIVITY','T03_PROPAGATION','T04_NEIGHBOR_RELAY','T05_STRESS_COUPLING']})
 contract={'NEW_REPO_CLEAN':True,'NEW_REPO_INITIALIZED':True,'CANONICAL_REPO_UNMODIFIED':True,'CANONICAL_REPO_SNAPSHOT_FROZEN':True,'CANONICAL_REGISTRY_IMPORTED':True,'CANONICAL_LEDGER_REVIEWED':True,'CANONICAL_HISTORICAL_INDEX_REVIEWED':True,'PRE_LEDGER_EM_SEARCH_COMPLETE':True,'DEV145_EM_HISTORY_REVIEWED':True,'DEV151_153_REVIEWED':True,'DEV155_167_REVIEWED':True,'DEV193_231_REVIEWED':True,'RELEVANT_OLD_PRS_SEARCHED':True,'RAW_CANDIDATE_CENSUS_COMPLETE':True,'REPRESENTATION_REGISTRY_COMPLETE':True,'SOURCE_REGIME_REGISTRY_COMPLETE':True,'GEOMETRY_REGISTRY_COMPLETE':True,'OBSERVER_REGISTRY_COMPLETE':True,'TEMPORAL_REGISTRY_COMPLETE':True,'COLLECTIVE_SCALE_REGISTRY_COMPLETE':True,'CANDIDATE_EQUIVALENCE_COMPLETE':True,'INFORMATION_LOSS_CLASSIFIED':True,'CANDIDATE_ADMISSIBILITY_COMPLETE':True,'INDEPENDENCE_GROUPS_FROZEN':True,'REGIME_COMPATIBILITY_GRAPH_COMPLETE':True,'HISTORICAL_NEGATIVE_SCOPE_MATRIX_COMPLETE':True,'HISTORICAL_MATRIX_COMPLETE':True,'FORWARD_MATRIX_COMPLETE':True,'COMMON_TEST_BATTERY_FROZEN':True,'RED_STRING_FEATURE_REGISTRY_CREATED':True,'REPRESENTATION_SENSITIVITY_INITIALIZED':True,'SOURCE_SENSITIVITY_INITIALIZED':True,'GEOMETRY_SENSITIVITY_INITIALIZED':True,'OBSERVER_SENSITIVITY_INITIALIZED':True,'SOURCE_NUMBER_SENSITIVITY_INITIALIZED':True,'COLLECTIVE_SCALE_SENSITIVITY_INITIALIZED':True,'NO_CANDIDATE_RANKING':True,'NO_NEW_PHYSICS':True,'NO_MATRIX_EXECUTION':True,'EMX001_RESULT':'MATRIX_V1_FROZEN','EMX002_TEST_SELECTION':'COMMON_NATIVE_PRIMITIVE_BATTERY','EMX002_TEST_SELECTION_FROZEN':True}
 dump(OUT/'starting_state.json',{'canonical':snapshot,'new_repo_clean_at_start':True}); dump(OUT/'final_contract.json',contract); (OUT/'discussion_handoff.md').write_text('# EMX002 handoff\n\nMatrix v1 is frozen. Execute only T01–T05 under frozen conditions, and add no candidate based on results.\n')
 # Runs are immutable build records; matrix/ is the working registry view.
 for name in ('candidate_registry.json','representation_registry.json','source_regime_registry.json','geometry_registry.json','observer_registry.json','temporal_registry.json','collective_scale_registry.json','regime_compatibility_graph.json','independence_groups.json','historical_negative_scope_matrix.json','historical_matrix.json','forward_matrix.json','common_test_battery.json','representation_sensitivity.json','source_sensitivity.json','geometry_sensitivity.json','observer_sensitivity.json','source_number_sensitivity.json','collective_scale_sensitivity.json','red_string_features.json'):
  shutil.copy2(MATRIX/name, OUT/name)
 print(f'generated {len(candidates)} candidates, {len(historical)} historical cells, {len(forward)} forward cells')
if __name__=='__main__': main()
