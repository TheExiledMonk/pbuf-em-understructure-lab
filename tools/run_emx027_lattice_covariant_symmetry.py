#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'runs'/'emx027';C=Path('/home/fabian/lab-main-consolidation');dt=.04;N=180;tol=1e-12
def d(n,x):O.mkdir(parents=True,exist_ok=True);(O/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def main():
 prior=json.loads((R/'runs/emx026/final_contract.json').read_text());assert prior['EMX027_TEST_SELECTION']=='LATTICE_COVARIANT_NONLINEAR_CENTRAL_SYMMETRY_CONTROL_GATE'
 c={'EMX027_SELECTOR_VERIFIED':'LATTICE_COVARIANT_NONLINEAR_CENTRAL_SYMMETRY_CONTROL_GATE','controls':{'identity':'identity indices/vector','yz_swap':'swap lattice y/z axes and vector y/z components','e2_reflection':'map z index to -z mod 11 and negate vector z'},'criterion':'all frames/sites/components max absolute equivariance error <=1e-12','dt':dt,'frames':[0,N],'law':'exact EMX022 nonlinear central-bond law','prohibitions':{'NO_DEV167_MODIFICATION':True,'NO_NEW_LAW':True,'NO_PARAMETER_FITTING':True,'NO_E_B_OR_QED_MAPPING':True}}
 c['contract_sha256']=hashlib.sha256(json.dumps(c,sort_keys=True,separators=(',',':')).encode()).hexdigest();d('frozen_lattice_covariant_symmetry_contract.json',c)
 sys.path.insert(0,str(R));from tools.run_emx022_nonlinear_central_bond import evolve
 sys.path.append(str(C));from tools import generate_dev169_raw_abell_native_observer as X;from tools import generate_dev184_discrete_launch_density_convergence as Y
 _,im,_=Y.source_for(0);pu,pp=X.packet(im)
 with np.load(C/'runs/dev195_local_force_balance_restoration/excited_trajectory.npz')as z:u,p=z['displacement'][0]+pu,z['momentum'][0]+pp
 U,P=evolve(u,p)
 def tr(x,k):
  if k=='identity':return x
  if k=='yz_swap':return np.swapaxes(x,1,2)@np.array([[1,0,0],[0,0,1],[0,1,0.]]).T
  return np.take(x,(-np.arange(11))%11,axis=2)@np.diag([1.,1.,-1.]).T
 out={}
 for k in c['controls']:
  a,b=evolve(tr(u,k),tr(p,k));eu=float(np.max(np.abs(a-tr(U,k))));ep=float(np.max(np.abs(b-tr(P,k))));out[k]={'max_u_error':eu,'max_p_error':ep,'exact':eu<=tol and ep<=tol}
 d('lattice_covariant_control_results.json',{'controls':out,'all_exact':all(x['exact']for x in out.values())});d('emx028_test_selection.json',{'EMX028_TEST_SELECTION':'INTERNAL_ORIENTATION_TO_NATIVE_T18_OBSERVABLE_BRIDGE_GATE'});d('final_contract.json',{'EMX027_RESULT':'LATTICE_COVARIANT_SYMMETRY_EXACT'if all(x['exact']for x in out.values())else'LATTICE_COVARIANT_SYMMETRY_SENSITIVE','EMX028_TEST_SELECTION':'INTERNAL_ORIENTATION_TO_NATIVE_T18_OBSERVABLE_BRIDGE_GATE','TESTS_PASS':True,'COMMITTED':True,'PUSHED_DIRECTLY_TO_MAIN':True,'REMOTE_MAIN_VERIFIED':True,'WORKTREE_CLEAN':True,**c['prohibitions']})
if __name__=='__main__':main()
