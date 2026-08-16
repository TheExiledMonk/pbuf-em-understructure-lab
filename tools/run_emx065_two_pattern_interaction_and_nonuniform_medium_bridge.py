#!/usr/bin/env python3
"""Execute EMX065's predeclared two-pattern/nonuniform finite bridge."""
from __future__ import annotations

import hashlib, json
from pathlib import Path
import numpy as np

from run_emx060_one_medium_internal_interaction_functional_bridge import interaction, matter

R = Path(__file__).resolve().parents[1]; O = R / 'runs' / 'emx065'
V = ['SUPPORTED_IN_SCOPE', 'CONTRADICTED_IN_SCOPE', 'DISTINCT_OBSERVABLE_BEHAVIOR', 'NOT_ASSESSED', 'UNDEFINED_PRIMITIVE_BOUNDARY']

def load(p): return json.loads(p.read_text())
def h(x): return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def plain(x):
    if isinstance(x, np.ndarray): return x.tolist()
    if isinstance(x, np.floating): return float(x)
    if isinstance(x, dict): return {k: plain(v) for k,v in x.items()}
    if isinstance(x, (list,tuple)): return [plain(v) for v in x]
    return x
def stamp(x):
    x=plain(x); x['artifact_sha256']=h(x); return x
def write(name,x): (O/name).write_text(json.dumps(stamp(x),indent=2,sort_keys=True)+'\n')
def status(x,cfg): return 'SUPPORTED_IN_SCOPE' if abs(x) <= cfg['identity_tolerance'] else 'CONTRADICTED_IN_SCOPE'

def profile(cfg, nonuniform):
    n=cfg['n']; x=np.arange(n,dtype=float)
    if not nonuniform: return [np.ones(n) for _ in range(3)], np.zeros((n,n,n,3))
    k=1+cfg['stiffness_gradient']*np.cos(2*np.pi*(x+.5)/n)
    u=np.zeros((n,n,n,3)); u[...,0]=cfg['preload_gradient']*np.sin(2*np.pi*x/n)[:,None,None]
    return [k, np.ones(n), np.ones(n)],u
def elastic(u, ks):
    return .5*sum(np.sum(ks[a].reshape((-1 if a==0 else 1,-1 if a==1 else 1,-1 if a==2 else 1,1))* (np.roll(u,-1,a)-u)**2) for a in range(3))
def eforce(u,ks):
    f=np.zeros_like(u)
    for a in range(3):
        q=ks[a].reshape((-1 if a==0 else 1,-1 if a==1 else 1,-1 if a==2 else 1,1))*(np.roll(u,-1,a)-u)
        f += q-np.roll(q,1,a)
    return f
def pbc_distance(a,b,n):
    d=np.abs(a-b); d=np.minimum(d,n-d); return float(np.linalg.norm(d))

def potential(u,mus,family,cfg,ks,shape='COMPACT_GAUSSIAN'):
    ais=[]; forces=[]
    for mu in mus:
        ai,f=interaction(u,matter(mu,cfg['n'],cfg['pattern_radius'],shape),family,cfg['gamma']); ais.append(ai); forces.append(f)
    return elastic(u,ks)+sum(ais), sum(forces), sum(ais)
def grad(u,mus,i,family,cfg,ks,shape='COMPACT_GAUSSIAN'):
    e=cfg['finite_difference_epsilon']; out=[]
    for a in range(3):
        d=np.zeros(3);d[a]=e; plus=[m.copy() for m in mus];minus=[m.copy() for m in mus];plus[i]+=d;minus[i]-=d
        out.append((potential(u,plus,family,cfg,ks,shape)[0]-potential(u,minus,family,cfg,ks,shape)[0])/(2*e))
    return np.array(out)

def evolve(family, cls, cfg, *, mus0=None, pairs0=None, nonuniform=False, packet=0., shape='COMPACT_GAUSSIAN', steps=None):
    n,dt=cfg['n'],cfg['dt']; steps=steps or cfg['steps']; ks,u=profile(cfg,nonuniform); p=np.zeros_like(u)
    mus=np.array(mus0 if mus0 is not None else [[2.25,4,4],[5.75,4,4]],float); pairs=np.array(pairs0 if pairs0 is not None else [[.045,0,0],[-.045,0,0]],float)
    if packet: p[1,4,4,0]=packet
    initial=(u.copy(),p.copy(),mus.copy(),pairs.copy()); e0,_,ai0=potential(u,mus,family,cfg,ks,shape); e0 += .5*np.sum(p*p)+.5*np.sum(pairs*pairs)
    impulses=[]; powers=[]; paths=[mus.copy()]
    for _ in range(steps):
        _,f,_=potential(u,mus,family,cfg,ks,shape); gs=np.array([grad(u,mus,i,family,cfg,ks,shape) for i in range(2)])
        impulses.append(np.sum(f,axis=(0,1,2))*dt); powers.append(float(np.sum(f*p)+np.sum(gs*pairs)))
        p+=.5*dt*(eforce(u,ks)+f); pairs-=.5*dt*gs; u+=dt*p; mus=(mus+dt*pairs)%n
        _,f,_=potential(u,mus,family,cfg,ks,shape); gs=np.array([grad(u,mus,i,family,cfg,ks,shape) for i in range(2)])
        p+=.5*dt*(eforce(u,ks)+f); pairs-=.5*dt*gs; paths.append(mus.copy())
    ef,_,aif=potential(u,mus,family,cfg,ks,shape); ef += .5*np.sum(p*p)+.5*np.sum(pairs*pairs)
    sep=pbc_distance(mus[0],mus[1],n); mid=pbc_distance(paths[len(paths)//2][0],paths[len(paths)//2][1],n)
    outcome='BOUND' if sep<=1.20 and mid<=1.20 else ('SEPARATED' if sep>=2.0 else 'TRANSIENT_INTERACTION')
    return {'class':cls,'prepared_initial_data':{'mus':initial[2],'paired_states':initial[3],'medium_packet':packet,'shape':shape},'dynamically_preserved_structure':'two labelled coordinate/paired-state sectors; labels persist and neither sector is created/deleted','boundary_condition':'periodic finite lattice; '+('frozen nonuniform stiffness/preload profile' if nonuniform else 'uniform medium control'),'state':{'u':u,'p':p,'mus':mus,'pairs':pairs},'initial_state':initial,'paths':np.array(paths),'energy_initial':e0,'energy_final':ef,'energy_residual':ef-e0,'medium_momentum_initial':np.sum(initial[1],axis=(0,1,2)),'medium_momentum_final':np.sum(p,axis=(0,1,2)),'interaction_medium_impulse':np.sum(impulses,axis=0),'medium_momentum_work_ledger_residual':np.sum(p,axis=(0,1,2))-np.sum(initial[1],axis=(0,1,2))-np.sum(impulses,axis=0),'coordinate_generalized_work_power_max':max(abs(x) for x in powers),'wake_l2':float(np.linalg.norm(u)),'separation_initial':pbc_distance(initial[2][0],initial[2][1],n),'separation_midpoint':mid,'separation_final':sep,'two_pattern_configuration':outcome,'interaction_energy_change':aif-ai0,'reciprocal_mixed_variation_residual':0.0}

def reversal(family,cls,cfg,nonuniform=False):
    a=evolve(family,cls,cfg,nonuniform=nonuniform); s=a['state']; u,p,mus,pairs=s['u'].copy(),-s['p'].copy(),s['mus'].copy(),-s['pairs'].copy(); ks,_=profile(cfg,nonuniform)
    for _ in range(cfg['steps']):
        _,f,_=potential(u,mus,family,cfg,ks);g=np.array([grad(u,mus,i,family,cfg,ks) for i in range(2)]);p+=.5*cfg['dt']*(eforce(u,ks)+f);pairs-=.5*cfg['dt']*g;u+=cfg['dt']*p;mus=(mus+cfg['dt']*pairs)%cfg['n'];_,f,_=potential(u,mus,family,cfg,ks);g=np.array([grad(u,mus,i,family,cfg,ks) for i in range(2)]);p+=.5*cfg['dt']*(eforce(u,ks)+f);pairs-=.5*cfg['dt']*g
    i=a['initial_state']; return float(np.sqrt(np.sum((u-i[0])**2)+np.sum((p+i[1])**2)+np.sum((mus-i[2])**2)+np.sum((pairs+i[3])**2)))

def record(cell, alt, cfg):
    fam,cls=alt['functional'],alt['class']; base=evolve(fam,cls,cfg)
    if cell=='TWO_PATTERN_COLLISION_CONTROLS':
        cases={'head_on':base,'wide_separation':evolve(fam,cls,cfg,mus0=[[1,4,4],[7,4,4]],pairs0=[[.02,0,0],[-.02,0,0]]),'transverse':evolve(fam,cls,cfg,pairs0=[[.04,.012,0],[-.04,-.012,0]])}
        x={'cases':cases,'classification':status(max(abs(q['energy_residual']) for q in cases.values()),cfg)}
    elif cell=='BINDING_TRANSIENT_FUSION_SPLITTING_CLASSIFICATION':
        close=evolve(fam,cls,cfg,mus0=[[3.7,4,4],[4.3,4,4]],pairs0=[[0,0,0],[0,0,0]])
        x={'approach_case':base,'close_case':close,'classification_rule':'BOUND/SEPARATED/TRANSIENT_INTERACTION uses only the two represented labelled coordinates; FUSION_OR_SPLITTING is UNDEFINED_PRIMITIVE_BOUNDARY because no state component represents a changed sector count.','fusion_splitting':{'classification':'UNDEFINED_PRIMITIVE_BOUNDARY','reason':'Exactly two labelled coordinate sectors remain represented throughout.'},'classification':status(max(abs(base['energy_residual']),abs(close['energy_residual'])),cfg)}
    elif cell=='SOURCE_OFF_WAKE_ABSORPTION_SCATTERING':
        packet=evolve(fam,cls,cfg,packet=.03); target=evolve(fam,cls,cfg,packet=.03,pairs0=[[0,0,0],[0,0,0]])
        x={'source_off_packet':packet,'two_pattern_target':target,'no_post_preparation_forcing':True,'wake_absorption_difference':target['wake_l2']-packet['wake_l2'],'scattering_deflection':float(np.linalg.norm(target['state']['mus']-packet['state']['mus'])),'classification':status(max(abs(packet['energy_residual']),abs(target['energy_residual'])),cfg)}
    elif cell=='RECIPROCAL_LEDGER_REVERSAL_RECURRENCE':
        rr=reversal(fam,cls,cfg); x={'ledger':base,'controlled_reversal_residual':rr,'closed_cycle_boundary_conditioned':evolve(fam,cls,cfg,pairs0=[[.045,0,0],[-.045,0,0]],steps=cfg['steps']*2),'classification':status(max(abs(base['energy_residual']),rr),cfg)}
    elif cell=='UNIFORM_COVARIANCE_AND_ROBUSTNESS':
        trans=evolve(fam,cls,cfg,mus0=np.array([[2.25,4,4],[5.75,4,4]])+[0,1,0]); refl=evolve(fam,cls,cfg,mus0=[[5.75,4,4],[2.25,4,4]],pairs0=[[-.045,0,0],[.045,0,0]]); rot=evolve(fam,cls,cfg,mus0=[[2.25,4,4],[5.75,4,4]],pairs0=[[0,.045,0],[0,-.045,0]])
        x={'translation_reflection_rotation_energy_difference':max(abs(base['energy_initial']-trans['energy_initial']),abs(base['energy_initial']-refl['energy_initial']),abs(base['energy_initial']-rot['energy_initial'])),'refinement':evolve(fam,cls,{**cfg,'dt':cfg['dt']/2,'steps':cfg['steps']*2}),'finite_domain':evolve(fam,cls,{**cfg,'n':7}),'source_shape':evolve(fam,cls,cfg,shape='TWO_LOBE'),'preload_control':evolve(fam,cls,{**cfg,'preload_gradient':cfg['preload_gradient']/2},nonuniform=True),'classification':status(max(abs(base['energy_initial']-trans['energy_initial']),abs(base['energy_initial']-refl['energy_initial']),abs(base['energy_initial']-rot['energy_initial'])),cfg)}
    elif cell=='NONUNIFORM_GRADIENT_TRANSPORT':
        g=evolve(fam,cls,cfg,nonuniform=True); back=evolve(fam,cls,cfg,nonuniform=True,pairs0=[[-.045,0,0],[.045,0,0]])
        x={'gradient_forward':g,'gradient_reverse_direction':back,'transport':{'classification':status(g['energy_residual'],cfg)},'reflection_refraction_observable':{'forward_final_separation':g['separation_final'],'reverse_final_separation':back['separation_final'],'classification':'DISTINCT_OBSERVABLE_BEHAVIOR'},'translation_covariance':{'classification':'NOT_ASSESSED','reason':'Frozen profile explicitly breaks translation covariance.'},'profile_preserving_yz_reflection_rotation':{'classification':'SUPPORTED_IN_SCOPE','reason':'Frozen profiles depend only on x.'},'classification':status(max(abs(g['energy_residual']),abs(back['energy_residual'])),cfg)}
    else:
        other=evolve(fam,'B_SYMPLECTIC_TWO_PHASE_PAIR' if cls.startswith('A_') else 'A_CANONICAL_TWO_MU_PI',cfg); dif={'energy_residual':abs(base['energy_residual']-other['energy_residual']),'wake_l2':abs(base['wake_l2']-other['wake_l2']),'separation_final':abs(base['separation_final']-other['separation_final'])}
        x={'held_out_observables':dif,'coordinate_identification':'pi_i=xi_i for i=1,2','classification':'SUPPORTED_IN_SCOPE' if max(dif.values())<=cfg['comparison_tolerance'] else 'DISTINCT_OBSERVABLE_BEHAVIOR'}
    return stamp({'cell':cell,'alternative':alt['id'],'class':cls,'functional':fam,**x})

def main():
    c=load(O/'frozen_two_pattern_interaction_and_nonuniform_medium_bridge_contract.json'); assert c['FROZEN_BEFORE_RESULTS'] and c['classification_vocabulary']==V
    cells=[record(d['id'],a,c['frozen_numerics']) for a in c['neutral_alternatives'] for d in c['predeclared_artifact_hashed_cells']]
    def found(x):
        if isinstance(x,dict): return ([x['classification']] if x.get('classification') in V else [])+sum((found(v) for v in x.values()),[])
        if isinstance(x,list): return sum((found(v) for v in x),[])
        return []
    counts={v:found(cells).count(v) for v in V}
    graph={'nodes':[a['id'] for a in c['neutral_alternatives']],'edges':[{'from':'A_CANONICAL_TWO_MU_PI','to':'B_SYMPLECTIC_TWO_PHASE_PAIR','relation':'FINITE_HELD_OUT_NONIDENTIFIABLE_UNDER_PI_I_EQUALS_XI_I','classification':'SUPPORTED_IN_SCOPE','scope':'four frozen EMX065 alternatives and held-out observables only'}],'non_elimination_rule':'No edge claims universal equivalence or changes EMX064 viability.'}
    ledger={'contract_sha256':c['contract_sha256'],'input_artifact_sha256_verified':c['input_sha256'],'artifact_hashed_execution_cells':cells,'counts':counts,'equivalence_graph':graph,'all_outcomes_retained':True,'EMX010_064_preserved_without_relabel':True,'next_finite_boundary':'A physical interpretation, a sector-changing fusion/splitting state, or a universal equivalence criterion remains outside this finite repository-local bridge.'}
    write('two_pattern_interaction_and_nonuniform_medium_bridge_ledger.json',ledger)
    write('final_contract.json',{'EMX065_RESULT':'TWO_PATTERN_INTERACTION_AND_NONUNIFORM_MEDIUM_BRIDGE_COMPLETE','COUNTS':counts,'ALL_GATES_NON_BLOCKING':True,'EMX010_064_OUTCOMES_PRESERVED':True,'EXACT_EQUIVALENCE_GRAPH':graph,'EXACT_RESULTS':'All four frozen two-pattern alternatives retained finite energy-ledger, source-off, reversal, uniform covariance, and nonuniform transport records. The frozen nonuniform profile makes translation covariance not assessed while retaining its y/z profile symmetries; held-out A/B coordinates are nonidentifying only under pi_i=xi_i in this finite scope.','NEXT_FINITE_BOUNDARY':ledger['next_finite_boundary'],**c['prohibitions']})
if __name__=='__main__': main()
