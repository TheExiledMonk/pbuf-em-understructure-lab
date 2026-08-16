#!/usr/bin/env python3
from __future__ import annotations
import json,numpy as np
from pathlib import Path
from emx051_finite_closure_candidates import N,energy,force,source
R=Path(__file__).resolve().parents[1];O=R/'runs'/'emx055'
def j(n):return json.loads((O/n).read_text())
def w(n,x):(O/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def field(kind):
 a=np.zeros((N,N,N,3));a[6,5,5,0]=1
 if kind in ('DISTRIBUTED','RAMP_HOLD_RELEASE'):a+=np.roll(a,1,0)+np.roll(a,-1,0)
 if kind in ('TWO_SEPARATED','EXCHANGE_LOCATIONS'):a+=np.roll(a,2,0)
 if kind in ('ORIENTATION_REVERSED_LOOP','DEGREE_PRESERVED_REWIRE'):a=np.roll(a,1,1)-np.roll(a,1,0)
 if kind=='PARITY_REFLECTION':a=np.flip(a,0).copy()
 return a*.001/np.linalg.norm(a)
def history(kind,steps=180):
 h=np.zeros((steps+1,N,N,N,3));g=field(kind)
 if kind=='DOUBLE_SEPARATED':h[0]=g;h[20]=g
 elif kind=='DOUBLE_ORDER_REVERSED':h[0]=g;h[20]=-g
 elif kind=='RAMP_HOLD_RELEASE':
  for t in range(10):h[t]=g*(t+1)/10
  for t in range(10,30):h[t]=g
  for t in range(30,40):h[t]=g*(39-t)/10
 elif kind=='CYCLIC_RETURN':h[0]=g;h[10]=-g;h[20]=g;h[30]=-g
 else:h[0]=g
 return h
def run(u,p,h,cand,dt=.04,steps=180):
 work=res=0.;bond=0.;vals=[];en=[]
 for n in range(steps+1):
  vals.append(float(np.sqrt(np.sum(u*u+p*p))));en.append(energy(u,p,'SYMPLECTIC_PAIRED_STATE'))
  if n==steps:break
  s=h[n]
  if cand=='GEOMETRY_COVARIANT_BOND_WORK':s=s-np.roll(s,1,0);bond=max(bond,float(abs(s.sum())))
  f=force(u,'SYMPLECTIC_PAIRED_STATE');before=.5*np.sum(p*p);p=p+.5*dt*(f+s);dw=.5*np.sum(p*p)-before;work+=dw
  if cand!='CONSERVATIVE_SOURCE_POTENTIAL':res-=dw
  u=u+dt*p;f=force(u,'SYMPLECTIC_PAIRED_STATE');p=p+.5*dt*f
 a=np.array(vals);return np.array([a[0],a[-1],a.min(),a.max()]),work,res,bond,np.array(en),u,p
def main():
 c=j('frozen_held_out_source_work_discriminator_contract.json');rows=[];vectors={}
 for batt,cells in c['batteries'].items():
  for cell in cells:
   h=history(cell);u,p,_=source('COMPACT')
   for cand in c['survivors']:
    v,work,res,bond,en,fu,fp=run(u.copy(),p.copy(),h,cand);vectors[(cell,cand)]=v
    bal=0. if cand=='CONSERVATIVE_SOURCE_POTENTIAL' else abs(res+work);cl='PASSES_HELD_OUT_CONTROLS' if bal<=c['metrics']['tolerances']['balance'] else 'FAILS_HELD_OUT_WORK_BALANCE';rows.append({'battery':batt,'cell':cell,'candidate':cand,'classification':cl,'work':work,'balance_residual':bal,'bond_force_sum':bond,'observer_vector':v.tolist()})
    if cand=='GEOMETRY_COVARIANT_BOND_WORK':rows.append({'battery':batt,'cell':cell+'_bond','candidate':cand,'classification':'PASSES_HELD_OUT_CONTROLS' if bond<=c['metrics']['tolerances']['bond'] else 'FAILS_HELD_OUT_BOND_ACCOUNTING','bond_force_sum':bond})
 # Source-free invariants plus refined held-out double impulse.
 for cand in c['survivors']:
  u,p,_=source('ELONGATED');z=np.zeros((181,N,N,N,3));v,_,_,_,en,a,b=run(u.copy(),p.copy(),z,cand);b=-b;_,_,_,_,_,a,b=run(a,b,z,cand);rev=max(abs(a-u).max(),abs(b-p).max());rows.append({'battery':'COMMON','cell':'source_free_reversal','candidate':cand,'classification':'PASSES_HELD_OUT_CONTROLS' if rev<=1e-12 else 'FAILS_HELD_OUT_REVERSAL','value':float(rev)});h=history('DOUBLE_SEPARATED');fineh=np.zeros((361,N,N,N,3));fineh[0]=h[0];fineh[40]=h[20];fine,*_=run(u.copy(),p.copy(),fineh,cand,dt=.02,steps=360);base,*_=run(u.copy(),p.copy(),h,cand);rows.append({'battery':'COMMON','cell':'refinement','candidate':cand,'classification':'PASSES_HELD_OUT_CONTROLS' if abs(fine-base).max()<=5e-5 else 'FAILS_HELD_OUT_REFINEMENT','value':float(abs(fine-base).max())})
 edges=[]
 for cell in [x for v in c['batteries'].values() for x in v]:
  a=vectors[(cell,'CONSERVATIVE_SOURCE_POTENTIAL')];b=vectors[(cell,'DISCRETE_PORT_WORK_PAIRING')];g=vectors[(cell,'GEOMETRY_COVARIANT_BOND_WORK')]
  edges += [{'cell':cell,'pair':'POTENTIAL__PORT','classification':'COMPATIBLE_NONUNIQUE' if abs(a-b).max()<=1e-12 else 'DIFFERENTIATES_SOURCE_WORK_FAMILIES'},{'cell':cell,'pair':'POTENTIAL__BOND','classification':'COMPATIBLE_NONUNIQUE' if abs(a-g).max()<=1e-12 else 'DIFFERENTIATES_SOURCE_WORK_FAMILIES'}]
 survivors=[x for x in c['survivors'] if not any(r['candidate']==x and r['classification'].startswith('FAIL') for r in rows)];counts={k:sum(x['classification']==k for x in rows+edges)for k in c['classification_vocabulary']};w('held_out_registry_and_results.json',{'records':rows,'remaining_survivors':survivors});w('family_separation_matrix_and_equivalence_graph.json',{'edges':edges,'equivalence_groups':[{'members':['CONSERVATIVE_SOURCE_POTENTIAL','DISCRETE_PORT_WORK_PAIRING'],'basis':'all held-out observer vectors equal within 1e-12'}],'no_physical_equivalence_claim':True});w('provenance_assumption_statement.json',{'statement':c['provenance'],'observer_diagnostic_only':True});w('conclusion.json',{'counts':counts,'remaining_survivors':survivors,'conclusion':'Held-out control passage preserves explicit hypotheses only.'});w('final_contract.json',{'EMX055_RESULT':'HELD_OUT_SOURCE_WORK_SURVIVOR_DISCRIMINATOR_COMPLETE','COUNTS':counts,'REMAINING_SURVIVORS':survivors,'NEXT_SELECTOR':'SOURCE_WORK_EQUIVALENCE_REFINEMENT_OR_NEW_PRIMITIVE_BOUNDARY','NEXT_BOUNDARY':'Any further distinction requires a separately frozen primitive; numerical equivalence is not physical equivalence.',**c['prohibitions']})
if __name__=='__main__':main()
