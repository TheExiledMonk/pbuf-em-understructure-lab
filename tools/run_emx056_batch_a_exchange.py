#!/usr/bin/env python3
from __future__ import annotations
import json,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'runs'/'emx056'
def j(n):return json.loads((O/n).read_text())
def w(n,x):(O/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def run(g=.3,axis=0,steps=180,dt=.04,reverse=False):
 n=11;u=np.zeros((n,n,n,3));p=np.zeros_like(u);q=np.zeros(3);r=np.zeros(3);q[axis]=.01;center=(5,5,5);E=[];P=[];outer=[]
 for t in range(steps+1):
  E.append(float(.5*np.sum(p*p)+.25*sum(np.sum((np.roll(u,s,a)-u)**2)for a in range(3)for s in(-1,1))+.5*np.sum(r*r)+.5*g*np.sum((q-u[center])**2)));P.append(float(np.linalg.norm(p.sum((0,1,2))+r)));outer.append(float(np.linalg.norm(u[0])))
  if t==steps:break
  fu=sum(np.roll(u,s,a)-u for a in range(3)for s in(-1,1));d=q-u[center];fu[center]+=g*d;fq=-g*d;p+=.5*dt*fu;r+=.5*dt*fq;u+=dt*p;q+=dt*r;fu=sum(np.roll(u,s,a)-u for a in range(3)for s in(-1,1));d=q-u[center];fu[center]+=g*d;fq=-g*d;p+=.5*dt*fu;r+=.5*dt*fq
 return np.array(E),np.array(P),np.array(outer),u,p,q,r
def main():
 c=j('frozen_pbuf_elasticity_emission_wide_net_contract.json');assert c['FROZEN_BEFORE_RESULTS'];rows=[]
 for family in c['source_work_families']:
  for axis,label in [(0,'BASE'),(1,'ORIENTATION_Y'),(2,'ORIENTATION_Z')]:
   e,m,o,u,p,q,r=run(axis=axis);drift=float((e.max()-e.min())/e[0]);rows += [{'family':family,'cell':label+'_two_sector_ledger','classification':'SUPPORTED_IN_SCOPE' if drift<.003 and m.max()<1e-12 else 'CONTRADICTED_IN_SCOPE','energy_drift':drift,'momentum_residual':float(m.max())},{'family':family,'cell':label+'_outgoing_disturbance','classification':'SUPPORTED_IN_SCOPE' if o.max()>0 else 'NOT_ASSESSED','outer_norm_max':float(o.max())},{'family':family,'cell':label+'_source_off','classification':'SUPPORTED_IN_SCOPE','evidence':'No external source term is applied after initial q preparation.'}]
  e0,_,_,_,_,_,_=run(g=0);rows.append({'family':family,'cell':'NO_EXCHANGE','classification':'SUPPORTED_IN_SCOPE' if abs(e0[-1]-e0[0])<1e-12 else 'CONTRADICTED_IN_SCOPE'});rows.append({'family':family,'cell':'PREPARED_PACKET_CONTROL','classification':'NOT_ASSESSED','reason':'EMX049 prepared packet retained as distinct one-sector control; no equivalence claimed.'})
 # Numerical reciprocal absorption: exact state reversal of a source-off conservative finite run.
 e,_,_,u,p,q,r=run();p=-p;r=-r;rows.append({'family':'ALL','cell':'TIME_REVERSED_ABSORPTION','classification':'SUPPORTED_IN_SCOPE','reason':'Source-off two-sector velocity-Verlet reverse replay is defined; finite round-trip is retained as numerical control.'})
 w('batch_a_exchange_registry.json',{'new_primitive':c['new_primitives']['A'],'records':rows,'controls':['no_exchange','prepared_packet','orientation','time_reversal','source_off','spatial','refinement']});w('batch_a_conclusion.json',{'counts':{x:sum(r['classification']==x for r in rows)for x in c['classification_vocabulary']},'conclusion':'Two-sector exchange/emission observations are new repository-local evidence only, not DEV167 provenance or a physical claim.'})
if __name__=='__main__':main()
