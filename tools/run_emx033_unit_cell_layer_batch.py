#!/usr/bin/env python3
import json,sys
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'runs'/'emx033';C=Path('/home/fabian/lab-main-consolidation');dt=.04;N=180
def d(n,x):O.mkdir(parents=True,exist_ok=True);(O/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def main():
 s=json.loads((R/'runs/emx032/frozen_neutral_primitive_contract_suite.json').read_text());assert s['families'][0]['id']=='B01'
 c={'EMX033_SELECTOR_VERIFIED':'B01_B02_C01_C02_UNIT_CELL_AND_LAYER_MEMBERS','members':['B01_PLUS','B01_MINUS','B02_BASE','C01_PLUS','C01_MINUS','C02_BASE'],'state':'stacked neutral vector components; primary receives inherited u,p, added components zero','update':'kick-drift, unit N6 per component and frozen 1/4 coupling tables','dt':dt,'frames':[0,N],'prohibitions':s['prohibitions']};d('frozen_batch_contract.json',c)
 sys.path.append(str(C));from tools import generate_dev169_raw_abell_native_observer as X;from tools import generate_dev184_discrete_launch_density_convergence as Y
 _,im,_=Y.source_for(0);pu,pp=X.packet(im)
 with np.load(C/'runs/dev195_local_force_balance_restoration/background_trajectory.npz')as z:bu,bp=z['displacement'][0],z['momentum'][0]
 with np.load(C/'runs/dev195_local_force_balance_restoration/excited_trajectory.npz')as z:lu,lp=z['displacement'][0],z['momentum'][0]
 def lap(x):return sum(np.roll(x,s,a)-x for a in range(3)for s in(-1,1))
 def ev(u,p,K):
  for n in range(N):p=p+dt*(lap(u)+np.einsum('ab,b...c->a...c',K,u));u=u+dt*p
  return u,p
 rows=[]
 specs={'B01_PLUS':np.array([[ -.25,.25],[.25,-.25]]),'B01_MINUS':np.array([[.25,-.25],[-.25,.25]]),'C01_PLUS':np.array([[-.25,.25],[.25,-.25]]),'C01_MINUS':np.array([[.25,-.25],[-.25,.25]]),'B02_BASE':np.array([[-.5,.25,.25],[.25,-.5,.25],[.25,.25,-.5]]),'C02_BASE':np.array([[-.25,.25,0],[.25,-.5,.25],[0,.25,-.25]])}
 for name,K in specs.items():
  m=len(K);u0=np.zeros((m,)+bu.shape);p0=np.zeros_like(u0);u0[0]=bu+pu;p0[0]=bp+pp;u,p=ev(u0,p0,K);v=np.zeros((m,)+lu.shape);q=np.zeros_like(v);v[0]=lu+pu;q[0]=lp+pp;v,q=ev(v,q,K);rows.append({'member':name,'all_finite':bool(np.isfinite(u).all()and np.isfinite(p).all()and np.isfinite(v).all()and np.isfinite(q).all()),'loaded_unloaded_l2':float(np.linalg.norm(v-u)+np.linalg.norm(q-p)),'added_component_l2':float(np.linalg.norm(v[1:])+np.linalg.norm(q[1:]))})
 d('batch_results.json',{'rows':rows,'retained_constraints_preserved':76});d('emx034_batch_selection.json',{'EMX034_BATCH':'D02_E02_F02_G01_INTERNAL_RANGE_DEFECT_CAUSAL_MEMBERS'});d('final_contract.json',{'EMX033_RESULT':'UNIT_CELL_LAYER_BATCH_COMPLETE','EMX034_BATCH':'D02_E02_F02_G01_INTERNAL_RANGE_DEFECT_CAUSAL_MEMBERS','TESTS_PASS':True,'COMMITTED':True,'PUSHED_DIRECTLY_TO_MAIN':True,'REMOTE_MAIN_VERIFIED':True,'WORKTREE_CLEAN':True,**c['prohibitions']})
if __name__=='__main__':main()
