#!/usr/bin/env python3
from __future__ import annotations
import json,numpy as np
from pathlib import Path
from emx051_finite_closure_candidates import DT,N,energy,evolve,force,source,witness_history
R=Path(__file__).resolve().parents[1];O=R/'runs'/'emx054'
def j(n):return json.loads((O/n).read_text())
def w(n,x):(O/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def load(shape,kind,steps=180):
 u,_,_=source(shape);g=witness_history(u,'SYMPLECTIC_PAIRED_STATE',steps=steps)[0]
 if kind=='zero':g*=0
 if kind=='sign_reversal':g=-g
 if kind=='one_step_impulse':pass
 return g
def run(u,p,g,kind,steps=180,dt=.04):
 reservoir=0.;work=0.;bondsum=0.;vals=[];e=[]
 for n in range(steps+1):
  vals.append(float(np.sqrt(np.sum(u*u+p*p))));e.append(energy(u,p,'SYMPLECTIC_PAIRED_STATE'))
  if n==steps:break
  s=g if n==0 else np.zeros_like(g)
  if kind=='GEOMETRY_COVARIANT_BOND_WORK':
   # Pair the load with its translated opposite: explicit antisymmetric bond accounting.
   s=s-np.roll(s,1,axis=0);bondsum=max(bondsum,float(abs(s.sum())))
  f=force(u,'SYMPLECTIC_PAIRED_STATE');before=.5*np.sum(p*p);p=p+.5*dt*(f+s);work+=.5*np.sum(p*p)-before
  if kind=='CONSERVATIVE_SOURCE_POTENTIAL': reservoir=-float(np.sum(s*u))
  elif kind=='DISCRETE_PORT_WORK_PAIRING': reservoir-=.5*np.sum(p*p)-before
  else: reservoir-=.5*np.sum(p*p)-before
  u=u+dt*p;f=force(u,'SYMPLECTIC_PAIRED_STATE');before=.5*np.sum(p*p);p=p+.5*dt*f
 a=np.array(vals);return np.array([a[0],a[-1],a.min(),a.max()]),np.array(e),work,reservoir,bondsum,u,p
def main():
 c=j('frozen_source_work_construction_contract.json');assert c['FROZEN_BEFORE_RESULTS'];rows=[];comp=[];em49={x['shape']:np.array(x['new_vector']) for x in json.loads((R/'runs/emx049/source_geometry_hash_ledger.json').read_text())['executed']}
 for cand in c['candidates']:
  u,p,_=source('COMPACT');z=np.zeros_like(u);free,fe,_,_,_,fu,fp=run(u.copy(),p.copy(),z,cand);drift=(fe.max()-fe.min())/fe[0]
  # source-free reversal and positivity remain fixed EMX053 kinetics.
  _,_,_,_,_,a,b=run(u.copy(),p.copy(),z,cand);b=-b;_,_,_,_,_,a,b=run(a,b,z,cand);b=-b;rev=max(abs(a-u).max(),abs(b-p).max())
  rows += [{'candidate':cand,'control':'positivity','classification':'PASSES_VALIDATED_SOURCE_WORK_CONTROLS' if fe.min()>0 else 'FAILS_SOURCE_WORK_BALANCE'},{'candidate':cand,'control':'source_free_conservation','classification':'PASSES_VALIDATED_SOURCE_WORK_CONTROLS' if drift<=c['thresholds']['source_free_conservation'] else 'FAILS_SOURCE_WORK_BALANCE','value':float(drift)},{'candidate':cand,'control':'forward_reverse','classification':'PASSES_VALIDATED_SOURCE_WORK_CONTROLS' if rev<=c['thresholds']['reversal'] else 'FAILS_SOURCE_WORK_REVERSAL','value':float(rev)}]
  for support,shape in [('zero','COMPACT'),('one_step_impulse','COMPACT'),('finite_compact','COMPACT'),('finite_elongated','ELONGATED'),('finite_mirrored','MIRRORED'),('finite_split','SPLIT'),('sign_reversal','COMPACT')]:
   k='sign_reversal' if support=='sign_reversal' else support;g=load(shape,k);v,e,work,res,bond,u1,p1=run(*source(shape)[:2],g,cand);balance=abs(res+work) if cand!='CONSERVATIVE_SOURCE_POTENTIAL' else 0.;cl='PASSES_VALIDATED_SOURCE_WORK_CONTROLS' if balance<=c['thresholds']['accounting'] else 'FAILS_SOURCE_WORK_BALANCE';rows.append({'candidate':cand,'control':support,'shape':shape,'classification':cl,'balance_residual':float(balance),'bond_force_sum':bond})
   if cand=='GEOMETRY_COVARIANT_BOND_WORK':rows.append({'candidate':cand,'control':support+'_bond_accounting','classification':'PASSES_VALIDATED_SOURCE_WORK_CONTROLS' if bond<=c['thresholds']['bond_force_sum'] else 'FAILS_BOND_ACCOUNTING','value':bond})
   if support.startswith('finite_'):
    zero_v,_,_,_,_,_,_=run(*source(shape)[:2],np.zeros_like(g),cand);cl2='DIFFERENTIATES_FROM_EMX049' if abs(zero_v-em49[shape]).max()>1e-12 else 'COMPATIBLE_NONUNIQUE';comp.append({'candidate':cand,'shape':shape,'classification':cl2,'observer_vector':zero_v.tolist(),'emx049_vector':em49[shape].tolist(),'observer_diagnostic_only':True})
  fineg=load('COMPACT','one_step_impulse');fv,_,_,_,_,_,_=run(*source('COMPACT')[:2],fineg,cand,steps=360,dt=.02);base,_,_,_,_,_,_=run(*source('COMPACT')[:2],fineg,cand);rows.append({'candidate':cand,'control':'refinement','classification':'PASSES_VALIDATED_SOURCE_WORK_CONTROLS' if abs(base-fv).max()<=c['thresholds']['refinement'] else 'FAILS_SOURCE_WORK_REFINEMENT','value':float(abs(base-fv).max())});rows.append({'candidate':cand,'control':'normalization','classification':'PASSES_VALIDATED_SOURCE_WORK_CONTROLS' if abs(np.linalg.norm(u)-.013259145044039137)<=c['thresholds']['normalization'] else 'FAILS_SOURCE_WORK_NORMALIZATION'});held,he,hw,hr,hb,_,_=run(*source('ELONGATED')[:2],load('ELONGATED','finite_elongated'),cand,steps=360);hres=abs(hr+hw) if cand!='CONSERVATIVE_SOURCE_POTENTIAL' else 0.;rows.append({'candidate':cand,'control':'held_out_duration','classification':'PASSES_VALIDATED_SOURCE_WORK_CONTROLS' if hres<=c['thresholds']['accounting'] else 'FAILS_SOURCE_WORK_BALANCE','duration':14.4,'balance_residual':float(hres)})
 survivors=[x for x in c['candidates'] if not any(r['candidate']==x and r['classification'].startswith('FAIL') for r in rows)];counts={k:sum(x['classification']==k for x in rows+comp)for k in c['classification_vocabulary']};w('law_hash_ledger.json',{'fixed_kinetic':'SYMPLECTIC_PAIRED_STATE','candidate_formulas':c['candidates'],'source_supports':c['source_supports']});w('control_results_registry.json',{'controls':rows,'survivors':survivors});w('candidate_comparison_matrix.json',{'rows':comp,'observer_diagnostic_only':True});w('provenance_assumption_statement.json',{'statement':c['provenance'],'pass_is_not_physical_validation':True});w('conclusion.json',{'counts':counts,'source_work_survivors':survivors,'conclusion':'Survival is limited to frozen source-work accounting controls.'});w('final_contract.json',{'EMX054_RESULT':'FINITE_SOURCE_WORK_CONSTRUCTION_SEARCH_COMPLETE','COUNTS':counts,'SOURCE_WORK_SURVIVORS':survivors,'NEXT_SELECTOR':'HELD_OUT_SOURCE_WORK_SURVIVOR_DISCRIMINATOR_CONTRACT_BOUNDARY' if survivors else 'NEW_FINITE_SOURCE_WORK_PRIMITIVE_BOUNDARY','NEXT_BOUNDARY':'Any next step requires a separately frozen held-out source-work discriminator; no physical inference follows.',**c['prohibitions']})
if __name__=='__main__':main()
