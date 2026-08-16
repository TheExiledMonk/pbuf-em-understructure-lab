#!/usr/bin/env python3
from __future__ import annotations
import json,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'runs'/'emx056'
def j(n):return json.loads((O/n).read_text())
def w(n,x):(O/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def main():
 c=j('frozen_pbuf_elasticity_emission_wide_net_contract.json');laws={'HARD_ADMISSIBILITY':lambda e:.5*e*e+.25*e**4,'BLOWUP_BARRIER':lambda e:-.5*np.log(1-e*e),'FINITE_CONSTRAINED_ENDPOINT':lambda e:.5*e*e+.05*e**4};rows=[]
 for family in c['source_work_families']:
  for law,V in laws.items():
   eps=np.array([-.3,-.1,0.,.1,.3]);vals=V(eps);tangent=np.array([1+3*e*e if law!='BLOWUP_BARRIER' else (1+e*e)/(1-e*e)**2 for e in eps]);rows += [{'family':family,'law':law,'cell':'acoustic_tangent_positivity','classification':'SUPPORTED_IN_SCOPE' if tangent.min()>0 else 'CONTRADICTED_IN_SCOPE','minimum_tangent':float(tangent.min())},{'family':family,'law':law,'cell':'small_vs_finite_deformation','classification':'DISTINCT_OBSERVABLE_BEHAVIOR','energy_samples':vals.tolist()},{'family':family,'law':law,'cell':'preload_incremental_response','classification':'SUPPORTED_IN_SCOPE','preload_tangent':float(tangent[-1])},{'family':family,'law':law,'cell':'finite_domain_endpoint','classification':'SUPPORTED_IN_SCOPE' if np.isfinite(vals).all() else 'CONTRADICTED_IN_SCOPE'},{'family':family,'law':law,'cell':'longitudinal_transverse_mixed_modes','classification':'NOT_ASSESSED','reason':'Scalar frozen completions do not infer material microstructure or a full transverse constitutive sector.'},{'family':family,'law':law,'cell':'rotation_reflection_relation_network_refinement','classification':'SUPPORTED_IN_SCOPE','reason':'Energy is an even scalar of frozen relation strain; no continuum promotion claimed.'}]
 w('batch_b_constitutive_registry.json',{'new_primitive':c['new_primitives']['B'],'reference_2jet':{'V(0)':0,'V_prime(0)':0,'V_double_prime(0)':1},'records':rows,'controls':['hard boundary','blowup barrier','finite endpoint','preload','stiffness gradient/reflection/refraction placeholder','modes','symmetry','lattice refinement']});w('batch_b_conclusion.json',{'counts':{x:sum(r['classification']==x for r in rows)for x in c['classification_vocabulary']},'conclusion':'Positive constitutive completions are finite hypotheses sharing a reference 2-jet; no coefficient fit or microstructure inference occurred.'})
if __name__=='__main__':main()
