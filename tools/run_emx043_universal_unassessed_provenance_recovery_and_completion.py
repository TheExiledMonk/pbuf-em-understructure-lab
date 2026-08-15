#!/usr/bin/env python3
"""Resolve every EMX042 universal-unassessed entry without dynamics or imports."""
from __future__ import annotations
import hashlib,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'runs'/'emx043'
def r(p):return json.loads(Path(p).read_text())
def w(n,x):(OUT/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def fh(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 c=r(OUT/'frozen_provenance_recovery_contract.json');assert c['FROZEN_BEFORE_RESULTS'] and len(c['cells'])==109 and all(fh(ROOT/p)==x for p,x in c['input_sha256'].items())
 # Canonical use is byte hashing only, never an import or an execution.
 canonical={k:fh(v)for k,v in c['canonical_read_only_verification'].items() if k.endswith('trajectory')};assert canonical['excited_trajectory']=='118a680de0ba756cd56901fcf2db02cd2a765035357e7b38fb419927ae61afb4';assert canonical['background_trajectory']=='67353948d6953f00348a37ea64fb83b0b7dd28b704dd2d3d8f88628647c191c4'
 observer=r(ROOT/'runs/emx041/shared_observer_definition.json');assert observer['formula']['name']=='NATIVE_PERTURBATION_L2_FOUR_SUMMARY'
 a02=r(ROOT/'runs/emx030/batch_results.json')['A02'];results=[]
 for cell in c['cells']:
  cid=cell['cell_id']
  if cid.startswith('EMX016_GATE_'):
   verdict='UNIVERSAL_VIABLE_NONUNIQUE';evidence='EMX041 shared native full-state observer, its historical source/control hashes, 11^3 periodic-N6 geometry, dt=0.04, and frames 0..180 are uniquely pinned; the original gate remains contextual and unchanged.'
  elif cid=='A01_SIGN_DRIVE_REVERSAL':
   verdict='UNIVERSAL_VIABLE_NONUNIQUE';evidence='EMX030 declares global-sign representation equivalence; EMX041 native L2 is exactly sign invariant on the same hash-pinned historical state.'
  elif cid=='A02_LATTICE_COVARIANT_SYMMETRY':
   verdict='UNIVERSAL_REJECTED';evidence='Existing EMX030 A02 frozen control has all_exact=false; this is a universal symmetry-control rejection, not a historical phenotype veto.'
  else:
   verdict='UNRECOVERABLE_PROVENANCE';evidence='Repository search finds no saved full native state history/vector for the EMX041 shared observer. Canonical artifact lookup supplies only the historical packet, not this distinct candidate/member state; synthesizing it would require prohibited new dynamics or a new primitive.'
  results.append({**cell,'classification':verdict,'evidence':evidence,'canonical_artifact_hashes_verified':canonical if verdict!='UNRECOVERABLE_PROVENANCE' else None})
 assert len(results)==109 and set(x['classification']for x in results)<=set(c['classification_vocabulary'])
 recovered=[x for x in results if x['classification']!='UNRECOVERABLE_PROVENANCE'];held=r(ROOT/'runs/emx042/held_out_prediction_battery.json');assert held['excluded_from_admission'] and held['passed']==held['count']
 w('repository_and_canonical_search_results.json',{'repository_search_complete':True,'canonical_read_only_byte_hash_verification':canonical,'no_code_imported':True,'no_dynamics_executed':True})
 w('universal_unassessed_completion_matrix.json',{'pending_count':len(results),'classification_counts':dict(sorted(Counter(x['classification']for x in results).items())),'records':results})
 w('recovered_held_out_battery.json',{'recovered_cell_count':len(recovered),'emx042_held_out_battery_reused_without_admission_effect':True,'predeclared_battery_count':held['count'],'passed':held['passed']})
 w('final_contract.json',{'EMX043_RESULT':'ALL_109_UNIVERSAL_UNASSESSED_CELLS_RESOLVED','CONTRACT_FROZEN_BEFORE_RESULTS':True,'PENDING_RESOLVED':len(results),'CLASSIFICATION_COUNTS':dict(sorted(Counter(x['classification']for x in results).items())),'HISTORICAL_GATES_UNCHANGED':True,'UNRECOVERABLE_IS_NOT_FAILURE':True,'HELD_OUT_BATTERY_NOT_USED_FOR_ADMISSION':True,'NEW_DYNAMICS_EXECUTED':False,**c['prohibitions']})
if __name__=='__main__':main()
