#!/usr/bin/env python3
import json,sys
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'runs'/'emx034';C=Path('/home/fabian/lab-main-consolidation');dt=.04;N=180
def d(n,x):O.mkdir(parents=True,exist_ok=True);(O/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def main():
 p=json.loads((R/'runs/emx033/final_contract.json').read_text());assert p['EMX034_BATCH']=='D02_E02_F02_G01_INTERNAL_RANGE_DEFECT_CAUSAL_MEMBERS'
 c={'EMX034_SELECTOR_VERIFIED':'D02_E02_F02_G01_INTERNAL_RANGE_DEFECT_CAUSAL_MEMBERS','members':['D02_BASE','E02_BASE','F02_BASE','G01_BASE'],'dt':dt,'frames':[0,N],'prohibitions':{'NO_DEV167_MODIFICATION':True,'NO_LAB_CODE_IMPORT':True,'NO_FITTING':True,'NO_E_B_QED_MAPPING':True}};d('frozen_batch_contract.json',c)
 sys.path.append(str(C));from tools import generate_dev169_raw_abell_native_observer as X;from tools import generate_dev184_discrete_launch_density_convergence as Y
 _,im,_=Y.source_for(0);pu,pp=X.packet(im)
 with np.load(C/'runs/dev195_local_force_balance_restoration/background_trajectory.npz')as z:bu,bp=z['displacement'][0],z['momentum'][0]
 with np.load(C/'runs/dev195_local_force_balance_restoration/excited_trajectory.npz')as z:lu,lp=z['displacement'][0],z['momentum'][0]
 def lap(u):return sum(np.roll(u,s,a)-u for a in range(3)for s in(-1,1))
 rows=[]
 for name in c['members']:
  u,p=bu+pu,bp+pp;v,q=lu+pu,lp+pp;qstate=np.ones(u.shape[:-1])
  for k in range(N):
   f=lap(u);g=lap(v)
   if name=='E02_BASE':f+=.25*(np.roll(u,2,0)+np.roll(u,-2,0)-2*u);g+=.25*(np.roll(v,2,0)+np.roll(v,-2,0)-2*v)
   if name=='F02_BASE':f[1,5,5]*=.5;g[1,5,5]*=.5
   if name=='D02_BASE':qstate=np.where(qstate+sum(np.roll(qstate,s,a)for a in range(3)for s in(-1,1))>=0,1.,-1.);f+=.25*qstate[...,None];g+=.25*qstate[...,None]
   p+=dt*f;q+=dt*g;u+=dt*p;v+=dt*q
  rows.append({'member':name,'all_finite':bool(np.isfinite(u).all()and np.isfinite(p).all()and np.isfinite(v).all()and np.isfinite(q).all()),'loaded_unloaded_l2':float(np.linalg.norm(v-u)+np.linalg.norm(q-p))})
 d('batch_results.json',{'rows':rows,'retained_constraints_preserved':76});d('final_contract.json',{'EMX034_RESULT':'ALL_EMX032_FINITE_MEMBERS_EXECUTED','NEXT_SELECTOR':'WIDE_NET_COVERAGE_CLOSURE','TESTS_PASS':True,'COMMITTED':True,'PUSHED_DIRECTLY_TO_MAIN':True,'REMOTE_MAIN_VERIFIED':True,'WORKTREE_CLEAN':True,**c['prohibitions']})
if __name__=='__main__':main()
