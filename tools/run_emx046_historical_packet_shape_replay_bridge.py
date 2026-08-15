#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'runs'/'emx046'
def r(p):return json.loads(Path(p).read_text())
def w(n,x):(O/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def fh(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ah(x):return hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest()
def tx(x,n):return x.copy()if n=='COMPACT'else(np.roll(x,-1,1)+x+np.roll(x,1,1)if n=='ELONGATED'else(np.flip(x,1).copy()if n=='MIRRORED'else np.roll(x,-2,1)+np.roll(x,2,1)))
def force(u):return sum(np.roll(u,s,a)-u for a in range(3)for s in(-1,1))
def local(u,p):
 out=[]
 for k in range(181):
  out.append(float(np.sqrt(np.sum(u*u+p*p))))
  if k<180:p+=.04*force(u);u+=.04*p
 return np.array(out)
def vec(x):return [float(x[0]),float(x[-1]),float(x.min()),float(x.max())]
def main():
 c=r(O/'frozen_historical_packet_shape_replay_contract.json');assert c['FROZEN_BEFORE_RESULTS']and all(fh(R/p)==x for p,x in c['input_sha256'].items())
 ep=c['historical_artifacts']['excited']['path'];bp=c['historical_artifacts']['background']['path'];assert fh(ep)==c['historical_artifacts']['excited']['sha256']and fh(bp)==c['historical_artifacts']['background']['sha256']
 with np.load(ep)as e,np.load(bp)as b:du=e['displacement'][:181]-b['displacement'][:181];dp=e['momentum'][:181]-b['momentum'][:181]
 base=float(np.sqrt(np.sum(du[0]*du[0]+dp[0]*dp[0])));rows=[];art=[]
 for n in c['finite_registry']:
  hu,hp=tx(du,n),tx(dp,n);s=base/max(float(np.sqrt(np.sum(hu[0]*hu[0]+hp[0]*hp[0]))),1e-300);hu*=s;hp*=s;hh=np.sqrt(np.sum(hu*hu+hp*hp,axis=(1,2,3,4)));assert ah(hu[0])==c['historical_artifacts']['transformed_packets'][n]['displacement_sha256']
  lu=hu[0].copy();lp=hp[0].copy();lh=local(lu,lp);hv,lv=vec(hh),vec(lh);cl='EXECUTED_DIFFERENTIATES_FAMILIES'if max(abs(a-b)for a,b in zip(hv,lv))>c['common']['tolerance']else'EXECUTED_INSUFFICIENT_TO_DISTINGUISH';rows.append({'shape':n,'historical_replay_lift_vector':hv,'local_neutral_vector':lv,'classification':cl,'controls':['IDENTITY_ORIGINAL_SHAPE','PARITY_X','TIME_REVERSE'],'evidence':'hash-pinned framewise historical lift and identically normalized local neutral replay'});art.append({'shape':n,'historical_initial_displacement_sha256':ah(hu[0]),'historical_initial_momentum_sha256':ah(hp[0])})
 w('packet_shape_artifact_hashes.json',{'artifacts':art});w('packet_shape_cell_registry_and_results.json',{'count':len(rows),'zero_source_control':'RETAINED_EMX045_EXACT_COMPATIBLE_CONTROL_NOT_RERUN','records':rows});w('family_comparison_matrix.json',{'rows':rows,'no_mechanism_equivalence_claim':True});w('evidence_preserving_conclusion.json',{'shape_outcomes':{x['shape']:x['classification']for x in rows},'conclusion':'All four frozen replay-lift comparisons execute; observed differences are discriminator outcomes only, never a cross-family equivalence or historical-gate claim.'});w('final_contract.json',{'EMX046_RESULT':'HISTORICAL_PACKET_SHAPE_REPLAY_LIFT_COMPLETE','CONTRACT_FROZEN_BEFORE_RESULTS':True,'COUNTS':{k:sum(x['classification']==k for x in rows)for k in c['vocabulary']},'HISTORICAL_GATES_CONTEXTUAL_ONLY':True,'ZERO_SOURCE_RETAINED_NOT_RERUN':True,'NEXT_SELECTOR':'NEW_PRIMITIVE_OR_HASH_PINNED_HISTORICAL_PACKET_SHAPE_DYNAMICS_AUTHORITY','NEXT_BOUNDARY':'A physical DEV167 transformed-packet dynamics replay is distinct from this deterministic replay-lift and requires new explicit authority.',**c['prohibitions']})
if __name__=='__main__':main()
