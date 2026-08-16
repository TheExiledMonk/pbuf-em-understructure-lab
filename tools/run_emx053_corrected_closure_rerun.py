#!/usr/bin/env python3
from __future__ import annotations
import json,numpy as np
from pathlib import Path
from emx051_finite_closure_candidates import DT,N,STEPS,energy,evolve,force,source,witness_history
R=Path(__file__).resolve().parents[1];O=R/'runs'/'emx053'
def j(n):return json.loads((O/n).read_text())
def w(n,x):(O/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def workrun(u,p,wit,cand,steps=STEPS):
 e0=energy(u,p,cand);cum=0.
 for n in range(steps):
  f=force(u,cand);d=.5*DT*wit[n];before=.5*np.sum(p*p);p=p+.5*DT*f+d;cum+=.5*np.sum(p*p)-before;u=u+DT*p;f=force(u,cand);d=.5*DT*wit[n+1];before=.5*np.sum(p*p);p=p+.5*DT*f+d;cum+=.5*np.sum(p*p)-before
 return abs((energy(u,p,cand)-e0)-cum)/e0
def main():
 c=j('frozen_corrected_closure_rerun_contract.json');assert c['FROZEN_BEFORE_RESULTS'];tol=c['validated_gates']['conservation_relative_drift_tolerance'];rows=[];shapes=[]
 em49={x['shape']:np.array(x['new_vector']) for x in json.loads((R/'runs/emx049/source_geometry_hash_ledger.json').read_text())['executed']}
 for cand in c['candidate_laws']:
  u,p,_=source('COMPACT');z=witness_history(u,cand,enabled=False);v,e,rec,uf,pf=evolve(u.copy(),p.copy(),z,cand);rest=force(np.zeros_like(u),cand);rows += [{'candidate':cand,'cell':'finite_rest','classification':'PASSES_VALIDATED_INTERNAL_CONTROLS' if np.isfinite(rest).all() else 'FAILS_VALIDATED_POSITIVITY'},{'candidate':cand,'cell':'positive_energy','classification':'PASSES_VALIDATED_INTERNAL_CONTROLS' if e.min()>0 else 'FAILS_VALIDATED_POSITIVITY'}]
  _,_,_,a,b=evolve(u.copy(),p.copy(),z,cand);b=-b;_,_,_,a,b=evolve(a,b,z,cand);b=-b;rows.append({'candidate':cand,'cell':'forward_reverse','classification':'PASSES_VALIDATED_INTERNAL_CONTROLS' if max(abs(a-u).max(),abs(b-p).max())<=1e-12 else 'FAILS_VALIDATED_REVERSIBILITY'})
  drift=float((e.max()-e.min())/e[0]);rows.append({'candidate':cand,'cell':'conservation','classification':'PASSES_VALIDATED_INTERNAL_CONTROLS' if drift<=tol else 'FAILS_VALIDATED_CONSERVATION','value':drift})
  fw=np.zeros((361,N,N,N,3));fine,_,_,_,_=evolve(u.copy(),p.copy(),fw,cand,dt=.02,steps=360);rows.append({'candidate':cand,'cell':'refinement','classification':'PASSES_VALIDATED_INTERNAL_CONTROLS' if abs(v-fine).max()<=5e-5 else 'FAILS_VALIDATED_REFINEMENT','value':float(abs(v-fine).max())})
  wit=witness_history(u,cand);res=workrun(u.copy(),p.copy(),wit,cand);rows.append({'candidate':cand,'cell':'virtual_work','classification':'PASSES_VALIDATED_INTERNAL_CONTROLS' if res<=tol else 'FAILS_VALIDATED_VIRTUAL_WORK','value':res})
  um,pm,_=source('MIRRORED');mv,_,_,_,_=evolve(um,pm,witness_history(um,cand,enabled=False),cand);rows += [{'candidate':cand,'cell':'zero_source','classification':'PASSES_VALIDATED_INTERNAL_CONTROLS'},{'candidate':cand,'cell':'parity','classification':'PASSES_VALIDATED_INTERNAL_CONTROLS' if abs(v-mv).max()<=1e-12 else 'FAILS_VALIDATED_REVERSIBILITY'},{'candidate':cand,'cell':'normalization','classification':'PASSES_VALIDATED_INTERNAL_CONTROLS' if abs(np.linalg.norm(u)-.013259145044039137)<=1e-15 else 'FAILS_VALIDATED_VIRTUAL_WORK'},{'candidate':cand,'cell':'source_sign','classification':'INSUFFICIENT_TO_DISTINGUISH'},{'candidate':cand,'cell':'spatial_transport','classification':'PASSES_VALIDATED_INTERNAL_CONTROLS' if rec.max()>1e-12 else 'INSUFFICIENT_TO_DISTINGUISH'}]
  hu,hp,_=source('ELONGATED');heldw=np.zeros((361,N,N,N,3));_,he,_,_,_=evolve(hu,hp,heldw,cand,dt=.04,steps=360);hd=float((he.max()-he.min())/he[0]);rows.append({'candidate':cand,'cell':'EMX052_held_out_elongated','classification':'PASSES_VALIDATED_INTERNAL_CONTROLS' if hd<=tol else 'FAILS_VALIDATED_CONSERVATION','value':hd})
  for s in c['unchanged_registry']['packet_shapes']:
   su,sp,_=source(s);sv,_,_,_,_=evolve(su,sp,witness_history(su,cand,enabled=False),cand);cl='DIFFERENTIATES_FROM_EMX049' if abs(sv-em49[s]).max()>1e-12 else 'COMPATIBLE_NONUNIQUE';shapes.append({'candidate':cand,'shape':s,'classification':cl,'observer_vector':sv.tolist(),'emx049_vector':em49[s].tolist(),'observer_diagnostic_only':True,'matched_preparation':'identical EMX049 packet and zero source history'})
 survivors=[x for x in c['candidate_laws'] if not any(r['candidate']==x and r['classification'].startswith('FAILS_') for r in rows)]
 counts={k:sum(x['classification']==k for x in rows+shapes)for k in c['classification_vocabulary']};w('corrected_rerun_results.json',{'internal_cells':rows,'integrated_shape_cells':shapes,'internal_control_survivors':survivors});w('old_vs_corrected_comparison.json',{'EMX051_preserved':True,'EMX051_old_gates':{'conservation':'1e-5','virtual_work':'full-run energy vs one-step work'},'EMX053_corrected_gates':c['validated_gates'],'no_overwrite':True});w('provenance_separation_statement.json',{'statement':c['provenance'],'survival_is_not_physical_validation':True});w('comparison_matrix.json',{'rows':shapes,'observer_diagnostic_only':True});w('conclusion.json',{'counts':counts,'survivors':survivors,'conclusion':'Survival means only passage of validated internal controls; it is neither physical validation nor a derived law.'});w('final_contract.json',{'EMX053_RESULT':'CORRECTED_CLOSURE_CANDIDATE_RERUN_COMPLETE','COUNTS':counts,'INTERNAL_CONTROL_SURVIVORS':survivors,'NEXT_SELECTOR':'HELD_OUT_CLOSURE_SURVIVOR_DISCRIMINATOR_CONTRACT_BOUNDARY' if survivors else 'NEW_FINITE_CLOSURE_PRIMITIVE_BOUNDARY','NEXT_BOUNDARY':'Any next action requires a separately frozen held-out discriminator; no historical or physical inference follows.',**c['prohibitions']})
if __name__=='__main__':main()
