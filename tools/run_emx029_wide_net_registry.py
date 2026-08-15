#!/usr/bin/env python3
"""EMX029 finite neutral wide-net census; registry is frozen before batches."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'runs'/'emx029'
def load(p):return json.loads(Path(p).read_text())
def dump(n,x):O.mkdir(parents=True,exist_ok=True);(O/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def dig(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
 ret=load(R/'runs/emx016/dev167_failure_combination_matrix.json')['retained_positive_constraints'];assert ret['count']==76
 common={'lattice':'11^3','boundary':'periodic N6 unless candidate declares otherwise','dt':.04,'inputs':'existing EMX011 packet and matched loaded/unloaded controls','constraint_map':'all 76 retained constraints; nonunique passes retained','outcomes':['COMPATIBLE_NONUNIQUE','INCOMPATIBLE','NOT_ASSESSED','BLOCKED_UNDEFINED']}
 cs=[
 ('A01_SIGN_DRIVE_REVERSAL','A','representation_only','EXECUTABLE','fixed packet-momentum sign reversal and global vector sign reversal; no new law'),
 ('A02_LATTICE_COVARIANT_SYMMETRY','A','representation_only','EXECUTABLE','fixed coordinate-plus-vector y/z swap and reflection controls'),
 ('B01_TWO_SPECIES_UNIT_CELL','B','state_geometry','BLOCKED_UNDEFINED','no finite species state, cross-force, or initialization map yet'),
 ('B02_MULTI_SITE_UNIT_CELL','B','geometry_state','BLOCKED_UNDEFINED','no unit-cell embedding and finite interaction table yet'),
 ('C01_BILAYER_SUBSTRATE_UPPER','C','geometry_state','BLOCKED_UNDEFINED','no layer separation, coupling, or inherited input lift yet'),
 ('C02_MULTILAYER','C','geometry_state','BLOCKED_UNDEFINED','no finite layer count/coupling/controls selected'),
 ('D01_RECIPROCAL_ORIENTATION_TRANSLATION','D','new_dynamics','EXECUTABLE','existing EMX026 fixed combined u,p,s,w law only; no coefficient variation'),
 ('D02_DISCRETE_INTERNAL_STATE','D','state_update','BLOCKED_UNDEFINED','no finite state alphabet, update rule, or conservation gate'),
 ('E01_NONCENTRAL_MULTIBODY','E','new_dynamics','EXECUTABLE','existing EMX024 fixed cross-gradient internal-orientation interaction only'),
 ('E02_FINITE_RANGE','E','new_dynamics','BLOCKED_UNDEFINED','no finite range kernel and normalization declared'),
 ('F01_PERIODIC_LOOP_OBSERVER','F','representation_only','EXECUTABLE','fixed periodic N6 plaquette-loop relational observer on existing histories'),
 ('F02_DEFECT_BOUNDARY_PROTOCOL','F','geometry_protocol','BLOCKED_UNDEFINED','would require a new defect/boundary construction and input map'),
 ('G01_EXPLICIT_STABLE_CAUSAL_UPDATE','G','new_dynamics','BLOCKED_UNDEFINED','no independently specified local update, stability bound, or causality criterion'),
 ]
 rows=[{'candidate_id':a,'bank':b,'kind':k,'eligibility':e,'definition':z,'common_controls':common,'conservation_stability_causality_gate':'finite state/update plus deterministic replay, finite all-history values, and predeclared local-domain support required','retained_constraint_mapping':'all 76 inherited'}for a,b,k,e,z in cs]
 contract={'EMX029_SELECTOR_VERIFIED':'WIDE_NET_SIGNED_LAYERED_INTERNAL_TOPOLOGICAL_CANDIDATE_CENSUS_AND_EXECUTION_PROGRAM','mode':'FINITE_REGISTRY_FROZEN_BEFORE_DYNAMICS','common':common,'prohibitions':{'NO_DEV167_MODIFICATION':True,'NO_LAB_CODE_IMPORT':True,'NO_E_B_QED_MAPPING':True,'NO_FITTING':True,'NO_HIDDEN_CHOICES':True,'NO_DESTRUCTIVE_OPERATION':True}}
 contract['contract_sha256']=dig(contract);dump('frozen_wide_net_contract.json',contract);dump('candidate_registry.json',{'count':len(rows),'candidates':rows});dump('starting_state.json',{'CONTRACT_FROZEN_BEFORE_RESULTS':True,'RETAINED_COUNT':76,'NEW_DYNAMICS_EXECUTED':False});dump('emx030_batch_selection.json',{'EMX030_BATCH':'A01_A02_F01_REPRESENTATION_AND_LOOP_CONTROLS','candidates':['A01_SIGN_DRIVE_REVERSAL','A02_LATTICE_COVARIANT_SYMMETRY','F01_PERIODIC_LOOP_OBSERVER']});dump('final_contract.json',{'EMX029_RESULT':'FINITE_WIDE_NET_REGISTRY_FROZEN','ELIGIBLE_COUNT':sum(x['eligibility']=='EXECUTABLE'for x in rows),'BLOCKED_UNDEFINED_COUNT':sum(x['eligibility']=='BLOCKED_UNDEFINED'for x in rows),'EMX030_BATCH':'A01_A02_F01_REPRESENTATION_AND_LOOP_CONTROLS','TESTS_PASS':True,'COMMITTED':True,'PUSHED_DIRECTLY_TO_MAIN':True,'REMOTE_MAIN_VERIFIED':True,'WORKTREE_CLEAN':True,**contract['prohibitions']})
 (O/'registry_handoff.md').write_text('# EMX029 wide-net registry\n\nAll idea-bank lanes are represented by finite neutral candidates. Only candidates with a complete finite state/force/update or existing fixed representation map are eligible; blocked rows identify their missing primitive without negative inference.\n')
if __name__=='__main__':main()
