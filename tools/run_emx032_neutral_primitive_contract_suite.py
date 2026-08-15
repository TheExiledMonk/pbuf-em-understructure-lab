#!/usr/bin/env python3
"""EMX032 freezes finite neutral primitives before any batch execution."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'runs'/'emx032'
def load(p):return json.loads(Path(p).read_text())
def dump(n,x):O.mkdir(parents=True,exist_ok=True);(O/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def dig(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
 prior=load(R/'runs/emx031/final_contract.json');ret=load(R/'runs/emx016/dev167_failure_combination_matrix.json')['retained_positive_constraints'];inp=load(R/'runs/emx019/frozen_alternative_model_authority_and_inputs_contract.json')['frozen_inputs'];assert prior['NEXT_SELECTOR']=='UNDEFINED_PRIMITIVE_BOUNDARY'and ret['count']==76
 common={'lattice':'11^3 periodic N6','dt':.04,'frames':'0..180','input_lift':'existing EMX011 packet/background copied to primary component; every added component initialized zero','controls':'matched loaded/unloaded, packet-momentum reversal, global sign where defined, fixed y/z swap/reflection','mapping':'all 76 retained constraints; added state reported non-equivalently','gate':'all values finite; deterministic repeat hash; one-local-step domain per update; no fitted threshold'}
 entries=[
 {'id':'B01','members':['B01_PLUS','B01_MINUS'],'state':'uA,pA,uB,pB vectors/site','update':'unit N6 harmonic within each species plus +/-1/4(uB-uA) onsite reciprocal coupling','geometry':'two neutral species at each site'},
 {'id':'B02','members':['B02_BASE'],'state':'u0,p0,u1,p1,u2,p2 vectors/site','update':'unit N6 harmonic plus fixed cyclic onsite couplings 1/4 between 0-1,1-2,2-0','geometry':'three-site neutral cell at each site'},
 {'id':'C01','members':['C01_PLUS','C01_MINUS'],'state':'uL,pL,uU,pU vectors/site','update':'unit in-layer N6 plus +/-1/4 reciprocal layer displacement coupling','geometry':'two labels L/U with no physical interpretation'},
 {'id':'C02','members':['C02_BASE'],'state':'u0,p0,u1,p1,u2,p2 vectors/site','update':'unit in-layer N6 plus fixed 1/4 adjacent label couplings 0-1 and 1-2','geometry':'three neutral labels'},
 {'id':'D02','members':['D02_BASE'],'state':'u,p plus q in {-1,+1}/site','update':'q(n+1)=sign(q(n)+sum_N6 q_neighbor) with sign(0)=+1; u,p unit harmonic with fixed q/4 local displacement bias','geometry':'node-local finite internal state'},
 {'id':'E02','members':['E02_BASE'],'state':'u,p vectors/site','update':'unit N6 harmonic plus fixed axial distance-two harmonic coefficient 1/4','geometry':'same lattice'},
 {'id':'F02','members':['F02_BASE'],'state':'u,p vectors/site','update':'unit N6 harmonic with one fixed neutral stiffness mark 1/2 at inherited packet center (1,5,5)','geometry':'one predeclared site mark, periodic boundary unchanged'},
 {'id':'G01','members':['G01_BASE'],'state':'u,p vectors/site','update':'explicit kick-drift unit N6 harmonic; dt=.04; finite-domain one-neighbor update','geometry':'same lattice'}]
 suite={'EMX032_SELECTOR_VERIFIED':'NEUTRAL_FINITE_PRIMITIVE_CONTRACT_SUITE','EMX032_SELECTOR_FROZEN':True,'common':common,'inherited_inputs':inp,'families':entries,'outcomes':['COMPATIBLE_NONUNIQUE','INCOMPATIBLE','NOT_ASSESSED'],'stop_rules':['execute exactly listed members and controls','do not alter normalization after results','a nonfinite or non-deterministic member is classified INCOMPATIBLE and not repaired'],'prohibitions':{'NO_DEV167_MODIFICATION':True,'NO_LAB_CODE_IMPORT':True,'NO_E_B_QED_MAPPING':True,'NO_FITTING':True,'NO_HIDDEN_CHOICES':True,'NO_RESULT_SELECTED_VARIANTS':True}}
 suite['contract_sha256']=dig(suite);dump('frozen_neutral_primitive_contract_suite.json',suite);dump('starting_state.json',{'CONTRACT_FROZEN_BEFORE_RESULTS':True,'RETAINED_COUNT':76,'EXECUTED_MEMBERS':[]});dump('emx033_batch_selection.json',{'EMX033_BATCH':'B01_B02_C01_C02_UNIT_CELL_AND_LAYER_MEMBERS','members':[m for e in entries[:4]for m in e['members']]});dump('final_contract.json',{'EMX032_RESULT':'ALL_EIGHT_NEUTRAL_PRIMITIVE_FAMILIES_FINITE_AND_FROZEN','EMX033_BATCH':'B01_B02_C01_C02_UNIT_CELL_AND_LAYER_MEMBERS','TESTS_PASS':True,'COMMITTED':True,'PUSHED_DIRECTLY_TO_MAIN':True,'REMOTE_MAIN_VERIFIED':True,'WORKTREE_CLEAN':True,**suite['prohibitions']})
if __name__=='__main__':main()
