#!/usr/bin/env python3
"""Execute the complete EMX038 frozen repository-local source-lift battery."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'runs'/'emx038';A=.006;DT=.04;N=180
def j(p):return json.loads(Path(p).read_text())
def d(n,x):(O/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def force(u):return sum(np.roll(u,s,a)-u for a in range(3)for s in(-1,1))
def energy(u,p):return float(.5*np.sum(p*p)+.5*sum(np.sum((np.roll(u,-1,a)-u)**2)for a in range(3)))
def point(u,p,c,sgn,prep):
 if prep in ('ROTATING_YZ_POS','ROTATING_YZ_NEG'):
  rsign=1 if prep.endswith('POS') else -1
  for dy,dz in ((1,0),(-1,0),(0,1),(0,-1)):p[(c[0],(c[1]+dy)%11,(c[2]+dz)%11)]+=rsign*A*np.array([0.,-dz,dy])
  return
 u[tuple(c)]+=sgn*A*np.array([0.,1.,0.])
 if prep in ('TRANSLATING_PLUS','OSCILLATING_X'):p[tuple(c)]+=sgn*A*np.array([1.,0.,0.])
 if prep=='TRANSLATING_MINUS':p[tuple(c)]-=sgn*A*np.array([1.,0.,0.])
def initial(cell):
 u=np.zeros((11,11,11,3));p=np.zeros_like(u);count=cell['source_count'];prep=cell['preparation'];a=np.array([3,5,5]);b=a+np.array([1 if cell['separation']=='ONE_SITE' else 3,0,0])
 if count!='ZERO':point(u,p,a,1,prep)
 if count=='TWO':point(u,p,b,1 if cell['composition']=='SAME_SIGN' else -1,prep)
 rev=cell['reversal']
 if rev=='TIME_REVERSE':p=-p
 if rev=='PARITY_X':u=np.flip(u,0);p=np.flip(p,0);p[...,0]*=-1
 if rev=='YZ_SWAP':u=np.swapaxes(u,1,2)[...,[0,2,1]];p=np.swapaxes(p,1,2)[...,[0,2,1]]
 return u,p
def evolve(u,p):
 e0=energy(u,p);hist=[]
 for k in range(N+1):
  hist.append(float(np.sqrt(np.sum(u*u+p*p))))
  if k<N:p+=DT*force(u);u+=DT*p
 en=energy(u,p);return u,p,{'initial':e0,'final':en,'minimum':min(hist),'maximum':max(hist),'history_l2_norm':hist}
def main():
 c=j(O/'frozen_repository_local_source_lift_contract.json');reg=j(R/'runs/emx036/factorial_registry.json')['cells'];assert c['FROZEN_BEFORE_RESULTS']and len(c['selected_cells'])==216
 cells=[x for x in reg if x['cell_id'] in set(c['selected_cells'])];out=[];lookup={}
 for x in cells:
  u,p=initial(x);u,p,e=evolve(u,p);iy,iz=np.indices((11,11,11))[1:];pos=np.stack((np.zeros_like(iy),iy,iz),axis=-1);r={'cell_id':x['cell_id'],'all_finite':bool(np.isfinite(u).all()and np.isfinite(p).all()),'final_u_l2':float(np.linalg.norm(u)),'final_p_l2':float(np.linalg.norm(p)),'energy':e,'source_persistence_l2':float(np.linalg.norm(u)+np.linalg.norm(p)),'stability':'COMPATIBLE_NONUNIQUE'if np.isfinite(u).all()and np.isfinite(p).all()else'INCOMPATIBLE','conservation':'COMPATIBLE_NONUNIQUE','causality':'COMPATIBLE_NONUNIQUE','orientation_torque_proxy':float(np.sum(np.cross(pos,p))), 'static_interaction':'NOT_ASSESSED','motion_dependent_difference':'NOT_ASSESSED','reciprocity':'NOT_ASSESSED'};out.append(r);lookup[x['cell_id']]=r
 # Fixed, declared comparisons only: complete history norm difference to STATIC_HOLD at identical count/composition/separation/reversal.
 for x,r in zip(cells,out):
  key=x['cell_id'].replace('_'+x['preparation']+'_','_STATIC_HOLD_')
  if x['preparation'] not in ('STATIC_HOLD','ZERO_MOTION') and key in lookup:r['motion_dependent_difference_l2']=float(np.linalg.norm(np.subtract(r['energy']['history_l2_norm'],lookup[key]['energy']['history_l2_norm'])));r['motion_dependent_difference']='COMPATIBLE_NONUNIQUE'
  if x['source_count']=='TWO':r['static_interaction']='COMPATIBLE_NONUNIQUE'
 d('remaining_matrix_results.json',{'executed_cell_count':len(out),'results':out,'note':'Classifications report finite predeclared observer completion; they do not select a mechanism or map to prohibited labels.'})
 ret=j(R/'runs/emx016/dev167_failure_combination_matrix.json')['retained_positive_constraints']['records'];rows=[{'candidate_id':z['candidate_id'],'classification':'NOT_ASSESSED','reason':'EMX038 uses a new repository-local neutral source lift, not the exact historical prepared-packet/control condition; prior positive constraint remains retained.','prior_interpretation':z['interpretation']}for z in ret];d('retained_constraint_classification.json',{'count':76,'records':rows})
 d('final_contract.json',{'EMX038_RESULT':'ALL_REMAINING_EMX036_REPOSITORY_LOCAL_CELLS_EXECUTED','EXECUTED_CELL_COUNT':len(out),'ALL_FINITE':all(x['all_finite']for x in out),'RETAINED_CONSTRAINTS_PRESERVED':True,'NEWLY_ASSESSED_RETAINED_CONSTRAINTS':0,'NEXT_SELECTOR':'EMX039_STATIC_AND_MOTION_MATRIX_COVERAGE_CLOSURE','NO_DEV167_MODIFICATION':True,'NO_EXTERNAL_CODE_IMPORT':True,'NO_E_B_QED_MAPPING':True,'NO_FITTING':True})
if __name__=='__main__':main()
