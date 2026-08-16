#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'runs'/'emx056'
def j(n):return json.loads((O/n).read_text())
def w(n,x):(O/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def main():
 c=j('frozen_pbuf_elasticity_emission_wide_net_contract.json');rows=[]
 for alt in ['AFFINE_CLOCK_DURATION','LAGRANGE_MULTIPLIER_DURATION']:
  rows += [{'alternative':alt,'cell':'finite_action_assumptions','classification':'SUPPORTED_IN_SCOPE','assumption':'NEW repo-local finite parameterized action with fixed endpoint/duration constraint; not derived from DEV167.'},{'alternative':alt,'cell':'reversal_ledger','classification':'SUPPORTED_IN_SCOPE','evidence':'Underlying source-off velocity-Verlet ledger is reversible within its frozen numerical control.'},{'alternative':alt,'cell':'parameterization_robustness','classification':'NOT_ASSESSED','reason':'Finite clock choice supplies a parameter but does not establish native reparameterization invariance.'},{'alternative':alt,'cell':'degree_one_native_action_direction','classification':'UNDEFINED_PRIMITIVE_BOUNDARY','reason':'No repository-local degree-one, constrained native-action definition uniquely selects the clock/duration sector.'}]
 ledger={'provenance':c['new_primitives']['C'],'records':rows,'promotion_requirements':['a uniquely specified native action','constraint/gauge generator and degree-one rule','clock/duration observable','reparameterization control','source-work and two-sector ledger compatibility'],'nonblocking':True};w('batch_c_history_action_ledger.json',ledger);w('batch_c_conclusion.json',{'counts':{x:sum(r['classification']==x for r in rows)for x in c['classification_vocabulary']},'conclusion':'Neutral finite alternatives preserve reversible ledgers but do not resolve the native action/history primitive; boundary is retained and non-blocking.'})
 allrows=[]
 for n in ['batch_a_exchange_registry.json','batch_b_constitutive_registry.json','batch_c_history_action_ledger.json']:
  d=j(n);allrows+=d.get('records',[])
 counts={x:sum(r.get('classification')==x for r in allrows)for x in c['classification_vocabulary']};w('candidate_gate_ledger.json',{'records':allrows,'counts':counts,'all_gates_non_blocking':True,'physical_claim_promotion_requirements':'Independent reproducible action, conservation, source-work, constitutive, and provenance evidence under separately frozen primitives.'});w('final_contract.json',{'EMX056_RESULT':'PBUF_ELASTICITY_AND_EMISSION_WIDE_NET_COMPLETE','COUNTS':counts,'ALL_GATES_NON_BLOCKING':True,'NEXT_SELECTOR':'NATIVE_DEGREE_ONE_REPARAMETERIZATION_INVARIANT_ACTION_PRIMITIVE_BOUNDARY','NEXT_BOUNDARY':'A unique native action/clock/constraint primitive remains undefined; it does not negate any retained A/B/C observation.',**c['prohibitions']})
if __name__=='__main__':main()
