#!/usr/bin/env python3
"""Freeze EMX046 transformed historical-packet replay lift before results."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'runs'/'emx046'
def fh(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ah(x):return hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest()
def h(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def tx(x,n):
 if n=='COMPACT':return x.copy()
 if n=='ELONGATED':return np.roll(x,-1,0)+x+np.roll(x,1,0)
 if n=='MIRRORED':return np.flip(x,0)
 return np.roll(x,-2,0)+np.roll(x,2,0)
def main():
 ep='/home/fabian/lab-main-consolidation/runs/dev195_local_force_balance_restoration/excited_trajectory.npz';bp='/home/fabian/lab-main-consolidation/runs/dev195_local_force_balance_restoration/background_trajectory.npz'
 with np.load(ep)as e,np.load(bp)as b:d=e['displacement'][0]-b['displacement'][0];p=e['momentum'][0]-b['momentum'][0]
 base=np.sqrt(np.sum(d*d+p*p));sh={}
 for n in ('COMPACT','ELONGATED','MIRRORED','SPLIT'):
  a,z=tx(d,n),tx(p,n);scale=base/max(np.sqrt(np.sum(a*a+z*z)),1e-300);sh[n]={'displacement_sha256':ah(a*scale),'momentum_sha256':ah(z*scale),'initial_native_l2':float(base),'support_rule':n}
 files=['runs/emx045/frozen_two_family_discriminator_contract.json','runs/emx041/shared_observer_definition.json']
 c={'EMX046_SELECTOR':'HISTORICAL_PACKET_SHAPE_REPLAY_BRIDGE','FROZEN_BEFORE_RESULTS':True,'historical_artifacts':{'excited':{'path':ep,'sha256':fh(ep)},'background':{'path':bp,'sha256':fh(bp)},'transformed_packets':sh},'transformation_rules':{'COMPACT':'identity','ELONGATED':'periodic x shifts -1,0,+1 summed then initial native L2 normalized','MIRRORED':'periodic x reflection then initial native L2 normalized','SPLIT':'periodic x shifts -2,+2 summed then initial native L2 normalized'},'common':{'lattice':'11^3','boundary':'periodic N6','dt':.04,'frames':[0,180],'observer':'EMX041_NATIVE_PERTURBATION_L2_FOUR_SUMMARY_V1','tolerance':1e-12,'normalization':'each transformed initial native state has the original initial native L2'},'controls':['ZERO_SOURCE_RETAINED_FROM_EMX045','IDENTITY_ORIGINAL_SHAPE','PARITY_X','TIME_REVERSE'],'finite_registry':['COMPACT','ELONGATED','MIRRORED','SPLIT'],'vocabulary':['EXECUTED_DIFFERENTIATES_FAMILIES','EXECUTED_COMPATIBLE_NONUNIQUE','EXECUTED_INSUFFICIENT_TO_DISTINGUISH','REPRODUCTION_CONTRADICTED','UNAVAILABLE_PROVENANCE'],'rules':{'historical_lift':'apply the frozen transform framewise to the hash-pinned recovered historical delta history, retaining the frozen initial normalization; this is a replay-lift, not a DEV167 re-execution','no_equivalence':'matched behavior never establishes cross-family mechanism equivalence'},'input_sha256':{p:fh(R/p)for p in files},'prohibitions':{'NO_DEV167_MODIFICATION':True,'NO_LAB_GIT_MODIFICATION':True,'NO_LAB_GIT_IMPORT':True,'NO_FITTING':True,'NO_RESULT_SELECTED_VARIANTS':True,'NO_E_B_QED_MAPPING':True}}
 c['contract_sha256']=h(c);O.mkdir(parents=True,exist_ok=True);(O/'frozen_historical_packet_shape_replay_contract.json').write_text(json.dumps(c,indent=2,sort_keys=True)+'\n');(O/'starting_state.json').write_text(json.dumps({'CONTRACT_FROZEN_BEFORE_RESULTS':True,'ZERO_SOURCE_RETAINED_NOT_RERUN':True},indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
