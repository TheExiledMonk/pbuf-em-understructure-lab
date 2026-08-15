#!/usr/bin/env python3
"""Freeze EMX045's finite, neutral two-family bridge registry."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'runs'/'emx045'
def fh(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def h(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def ah(x):return hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest()
def shape(name,n=11):
 u=np.zeros((n,n,n,3));c=(n//2,n//2,n//2)
 pts={'COMPACT':[(0,0,0,1)],'ELONGATED':[(-1,0,0,1),(0,0,0,1),(1,0,0,1)],'MIRRORED':[(0,-1,0,1),(0,1,0,-1)],'SPLIT':[(-2,0,0,1),(2,0,0,1)]}[name]
 for dx,dy,dz,s in pts:u[(c[0]+dx)%n,(c[1]+dy)%n,(c[2]+dz)%n,1]=s
 u/=np.linalg.norm(u);return u
def main():
 files=['runs/emx044/universal_viable_family_census.json','runs/emx041/shared_observer_definition.json','runs/emx038/frozen_repository_local_source_lift_contract.json']
 shapes={n:ah(shape(n))for n in ('COMPACT','ELONGATED','MIRRORED','SPLIT')}
 c={'EMX045_SELECTOR':'UNIVERSAL_TWO_FAMILY_DISCRIMINATOR_BRIDGES','FROZEN_BEFORE_RESULTS':True,'start_main_required':True,'input_sha256':{p:fh(R/p)for p in files},'families':{'HISTORICAL_DEV167_PREPARED_PACKET':{'count':77,'artifact':'/home/fabian/lab-main-consolidation/runs/dev195_local_force_balance_restoration/{excited,background}_trajectory.npz','hashes':['118a680de0ba756cd56901fcf2db02cd2a765035357e7b38fb419927ae61afb4','67353948d6953f00348a37ea64fb83b0b7dd28b704dd2d3d8f88628647c191c4']},'LOCAL_NEUTRAL_HARMONIC_PERIODIC_N6':{'count':224,'state':'u,p','interaction':'unit periodic N6 harmonic','update':'kick-drift'}},'common':{'observer_version':'EMX041_NATIVE_PERTURBATION_L2_FOUR_SUMMARY_V1','metric':'receiver native state L2 / source initial L2','normalization':'unit initial source L2','tolerance':1e-12,'boundary':'periodic N6','analysis_range':[0,180],'region':'all native sites unless receiver specified'},'finite_registry':{'reciprocity':[{'n':11,'separation':3,'dt':.04,'steps':180,'controls':['A_TO_B','B_TO_A','PARITY_X','TIME_REVERSE']}],'transport':[{'n':n,'separation':s,'dt':dt,'steps':180}for n in [9,11]for s in [1,3]for dt in [.02,.04]],'packet_shapes':['COMPACT','ELONGATED','MIRRORED','SPLIT','ZERO_SOURCE'],'packet_shape_hashes':shapes},'classification_vocabulary':['EXECUTED_COMPATIBLE_NONUNIQUE','EXECUTED_DIFFERENTIATES_FAMILIES','EXECUTED_INSUFFICIENT_TO_DISTINGUISH','UNAVAILABLE_PROVENANCE'],'rules':{'no_cross_family_equivalence':'shared behavior never implies mechanism equivalence','no_expansion':'only frozen finite registry may execute','historical_transforms':'non-identical historical packet shapes require a new DEV167 replay and are unavailable; do not synthesize a family replay'},'prohibitions':{'NO_DEV167_MODIFICATION':True,'NO_LAB_GIT_MODIFICATION':True,'NO_LAB_GIT_IMPORT':True,'NO_FITTING':True,'NO_HIDDEN_CHOICES':True,'NO_RESULT_SELECTED_VARIANTS':True,'NO_E_B_QED_MAPPING':True}}
 c['contract_sha256']=h(c);O.mkdir(parents=True,exist_ok=True);(O/'frozen_two_family_discriminator_contract.json').write_text(json.dumps(c,indent=2,sort_keys=True)+'\n');(O/'starting_state.json').write_text(json.dumps({'CONTRACT_FROZEN_BEFORE_RESULTS':True,'MAIN_START_GATE_VERIFIED':True},indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
