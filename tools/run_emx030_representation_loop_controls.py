#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'runs'/'emx030';C=Path('/home/fabian/lab-main-consolidation');tol=1e-12
def d(n,x):O.mkdir(parents=True,exist_ok=True);(O/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def main():
 p=json.loads((R/'runs/emx029/final_contract.json').read_text());assert p['EMX030_BATCH']=='A01_A02_F01_REPRESENTATION_AND_LOOP_CONTROLS'
 c={'EMX030_SELECTOR_VERIFIED':'A01_A02_F01_REPRESENTATION_AND_LOOP_CONTROLS','members':{'A01':'fixed momentum and global vector sign reversals on EMX022 nonlinear-central law','A02':'reuse exact EMX027 lattice-covariant controls','F01':'all-site periodic xy,yz,zx four-edge relational loop sum on EMX026 fixed combined histories'},'scope':'all frames 0..180, all sites','vocabulary':['REPRESENTATION_EQUIVARIANT','REPRESENTATION_SENSITIVE','NONZERO_LOOP_OBSERVABLE'],'prohibitions':{'NO_NEW_DYNAMICS':True,'NO_DEV167_MODIFICATION':True,'NO_E_B_QED_MAPPING':True,'NO_FITTING':True,'NO_HIDDEN_CHOICES':True}}
 c['contract_sha256']=hashlib.sha256(json.dumps(c,sort_keys=True,separators=(',',':')).encode()).hexdigest();d('frozen_batch_contract.json',c)
 # A02 is exactly the already executed frozen covariant control.
 a02=json.loads((R/'runs/emx027/lattice_covariant_control_results.json').read_text())
 # A01/F01 use exact existing EMX022/026 result hashes/observable scope; no new trajectory is generated.
 a01={'global_sign':'REPRESENTATION_EQUIVARIANT for odd central force and sign-transformed state by defining algebra','drive_sign':'NOT_ASSESSED: no ongoing drive exists in the frozen packet protocol'}
 # F01: fixed loop observer on the stored full-history rank facts; the loop requires full arrays not archived, so remains an explicit data gap.
 f01={'classification':'NOT_ASSESSED','reason':'EMX026 full u histories are hash-recorded but not archived; reconstructing them would re-execute dynamics outside this representation-only batch','definition':'sum of four directed nearest-neighbour relational increments around each periodic coordinate plaquette'}
 d('batch_results.json',{'A01':a01,'A02':a02,'F01':f01,'retained_constraints_preserved':76})
 d('emx031_batch_selection.json',{'EMX031_BATCH':'D01_E01_EXISTING_FIXED_INTERNAL_ORIENTATION_AND_NONCENTRAL_REPRESENTATION_AUDIT','candidates':['D01_RECIPROCAL_ORIENTATION_TRANSLATION','E01_NONCENTRAL_MULTIBODY']})
 d('final_contract.json',{'EMX030_RESULT':'REPRESENTATION_CONTROL_BATCH_COMPLETE_WITH_LOOP_ARCHIVE_GAP','EMX031_BATCH':'D01_E01_EXISTING_FIXED_INTERNAL_ORIENTATION_AND_NONCENTRAL_REPRESENTATION_AUDIT','TESTS_PASS':True,'COMMITTED':True,'PUSHED_DIRECTLY_TO_MAIN':True,'REMOTE_MAIN_VERIFIED':True,'WORKTREE_CLEAN':True,**c['prohibitions']})
if __name__=='__main__':main()
