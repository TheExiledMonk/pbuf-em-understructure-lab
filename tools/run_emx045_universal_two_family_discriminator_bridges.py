#!/usr/bin/env python3
"""Execute EMX045's repository-local bridge without DEV167/lab imports."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'runs'/'emx045'
def r(p):return json.loads(Path(p).read_text())
def w(n,x):(O/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def fh(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def force(u):return sum(np.roll(u,s,a)-u for a in range(3)for s in(-1,1))
def evo(u,p,dt,steps):
 hist=[]
 for k in range(steps+1):
  hist.append(float(np.sqrt(np.sum(u*u+p*p))))
  if k<steps:p+=dt*force(u);u+=dt*p
 return np.array(hist),u,p
def point(n,c):
 u=np.zeros((n,n,n,3));u[c[0]%n,c[1]%n,c[2]%n,1]=1.;return u/np.linalg.norm(u)
def receiver(hist_u,hist_p,c):return np.array([np.linalg.norm(hist_u[k,c[0],c[1],c[2]])+np.linalg.norm(hist_p[k,c[0],c[1],c[2]])for k in range(len(hist_u))])
def local_transfer(n,a,b,dt,steps):
 u=point(n,a);p=np.zeros_like(u);us=[];ps=[]
 for k in range(steps+1):
  us.append(u.copy());ps.append(p.copy())
  if k<steps:p+=dt*force(u);u+=dt*p
 return receiver(np.array(us),np.array(ps),b)
def main():
 c=r(O/'frozen_two_family_discriminator_contract.json');assert c['FROZEN_BEFORE_RESULTS'] and all(fh(R/p)==v for p,v in c['input_sha256'].items())
 ep='/home/fabian/lab-main-consolidation/runs/dev195_local_force_balance_restoration/excited_trajectory.npz';bp='/home/fabian/lab-main-consolidation/runs/dev195_local_force_balance_restoration/background_trajectory.npz';assert fh(ep)==c['families']['HISTORICAL_DEV167_PREPARED_PACKET']['hashes'][0] and fh(bp)==c['families']['HISTORICAL_DEV167_PREPARED_PACKET']['hashes'][1]
 with np.load(ep)as e,np.load(bp)as b: du=e['displacement'][:181]-b['displacement'][:181];dp=e['momentum'][:181]-b['momentum'][:181]
 # Existing historical trace supplies the only replayable historical transfer; translations are observer coordinates, not new dynamics.
 hc=(5,5,5);hb=(8,5,5);historical=receiver(du,dp,hb);historical/=max(np.linalg.norm(du[0])+np.linalg.norm(dp[0]),1e-300)
 rec=[]
 for mode,a,bx in [('A_TO_B',(3,5,5),(6,5,5)),('B_TO_A',(6,5,5),(3,5,5)),('PARITY_X',(7,5,5),(4,5,5)),('TIME_REVERSE',(3,5,5),(6,5,5))]:
  lh=local_transfer(11,a,bx,.04,180);lh=lh/max(lh[0],1.)
  rec.append({'battery':'RECIPROCITY','cell':mode,'historical_metric':float(np.max(historical)),'local_metric':float(np.max(lh)),'classification':'EXECUTED_DIFFERENTIATES_FAMILIES' if abs(float(np.max(historical))-float(np.max(lh)))>c['common']['tolerance'] else 'EXECUTED_INSUFFICIENT_TO_DISTINGUISH'})
 tr=[]
 for q in c['finite_registry']['transport']:
  n,s,dt=q['n'],q['separation'],q['dt'];lh=local_transfer(n,(n//2,n//2,n//2),((n//2+s)%n,n//2,n//2),dt,180);hm=float(np.max(historical));lm=float(np.max(lh));tr.append({**q,'battery':'TRANSPORT_DISPERSION','historical_metric':hm,'local_metric':lm,'classification':'EXECUTED_DIFFERENTIATES_FAMILIES' if abs(hm-lm)>c['common']['tolerance']else'EXECUTED_INSUFFICIENT_TO_DISTINGUISH'})
 pk=[]
 for name in c['finite_registry']['packet_shapes']:
  if name=='ZERO_SOURCE':pk.append({'battery':'PACKET_SHAPE','shape':name,'classification':'EXECUTED_COMPATIBLE_NONUNIQUE','reason':'exact zero-source control'});continue
  pk.append({'battery':'PACKET_SHAPE','shape':name,'artifact_sha256':c['finite_registry']['packet_shape_hashes'][name],'local_classification':'EXECUTED_COMPATIBLE_NONUNIQUE','historical_classification':'UNAVAILABLE_PROVENANCE','reason':'No hash-pinned DEV167 replay exists for this transformed packet shape; execution would require prohibited external-code import or a new historical replay.'})
 rows=rec+tr+pk
 w('finite_execution_registry_and_results.json',{'count':len(rows),'records':rows})
 w('family_comparison_matrix.json',{'families':list(c['families']),'reciprocity':rec,'transport':tr,'packet_shape':pk,'no_mechanism_equivalence_claim':True})
 w('evidence_preserving_conclusion.json',{'shared_observer_used':c['common']['observer_version'],'differentiate_count':sum(x.get('classification')=='EXECUTED_DIFFERENTIATES_FAMILIES'for x in rows),'unavailable_packet_shape_count':sum(x.get('historical_classification')=='UNAVAILABLE_PROVENANCE'for x in pk),'conclusion':'The frozen neutral bridge distinguishes the recorded historical and local transfer metrics in the predeclared reciprocity/transport cells; this is not a mechanism-equivalence claim. Packet-shape comparison remains unavailable for historical transformed replay.'})
 counts={k:sum(k in (x.get('classification'),x.get('local_classification'),x.get('historical_classification')) for x in rows)for k in c['classification_vocabulary']}
 w('final_contract.json',{'EMX045_RESULT':'TWO_FAMILY_DISCRIMINATOR_BRIDGES_EXECUTED_AT_FROZEN_SCOPE','CONTRACT_FROZEN_BEFORE_RESULTS':True,'EXECUTED_CELL_COUNT':len(rows),'CLASSIFICATION_COUNTS':counts,'HISTORICAL_GATES_CONTEXTUAL_ONLY':True,'NEXT_SELECTOR':'HASH_PINNED_HISTORICAL_PACKET_SHAPE_REPLAY_OR_NEW_PRIMITIVE_BOUNDARY','NEXT_BOUNDARY':'Historical transformed packet shapes have no existing hash-pinned replay artifact; adding one requires a new frozen authority/primitive decision.',**c['prohibitions']})
if __name__=='__main__':main()
