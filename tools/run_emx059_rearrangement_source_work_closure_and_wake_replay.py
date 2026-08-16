#!/usr/bin/env python3
"""Execute EMX059's frozen finite source-work accounting and wake replay cells."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parents[1]
O = R / 'runs' / 'emx059'
P058 = R / 'runs' / 'emx058'
VOCAB = ['SUPPORTED_IN_SCOPE', 'CONTRADICTED_IN_SCOPE', 'DISTINCT_OBSERVABLE_BEHAVIOR', 'NOT_ASSESSED', 'UNDEFINED_PRIMITIVE_BOUNDARY']


def load(path): return json.loads(path.read_text())
def hashed(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def write(name, value):
    value = dict(value); value['artifact_sha256'] = hashed(value)
    (O / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def laplacian(u, boundary):
    if boundary == 'PERIODIC':
        return sum(np.roll(u, shift, axis) - u for axis in range(3) for shift in (-1, 1))
    z = np.pad(u, ((1, 1), (1, 1), (1, 1), (0, 0)))
    return z[2:,1:-1,1:-1] + z[:-2,1:-1,1:-1] + z[1:-1,2:,1:-1] + z[1:-1,:-2,1:-1] + z[1:-1,1:-1,2:] + z[1:-1,1:-1,:-2] - 6*u


def sites(n, history, step, axis):
    c=n//2; a=[c,c,c]
    if history == 'MOVING_RIGHT_ON_OFF': a[axis] += min(2, step//14)
    elif history == 'MOVING_LEFT_ON_OFF': a[axis] -= min(2, step//14)
    elif history == 'REARRANGING_ON_OFF': a[(axis+1)%3] += 1 if (step//12)%2 else -1
    elif history == 'CLOSED_CYCLE_ON_OFF': a[axis] += [0, 1, 2, 1][min(3, step//18)]
    a=tuple(a); b=list(a); b[axis]=min(n-1,b[axis]+1)
    return a, tuple(b)


def drive(step, axis, amplitude, enabled=True, cycle=False):
    f=np.zeros(3)
    if enabled and step < 48:
        sign=-1 if cycle and step >= 24 else 1
        f[axis]=sign*amplitude*np.sin(np.pi*((step%24)+.5)/24)
    return f


def coupling(u,q,site,family):
    a,b=site
    return q-u[a] if family == 'POTENTIAL_PORT_EQUIVALENCE_CLASS' else q-(u[b]-u[a])


def internal_force(u,q,site,family,g,boundary,exchange):
    fu=laplacian(u,boundary); fq=np.zeros(3)
    if exchange:
        d=coupling(u,q,site,family)
        if family == 'POTENTIAL_PORT_EQUIVALENCE_CLASS': fu[site[0]] += g*d
        else: fu[site[0]] -= g*d; fu[site[1]] += g*d
        fq -= g*d
    return fu,fq


def components(u,p,q,r,site,family,g,boundary):
    if boundary == 'PERIODIC':
        elastic=sum(np.sum((np.roll(u,1,a)-u)**2) for a in range(3))/2
    else:
        elastic=0.
        for a in range(3):
            pads=[(0,0)]*4; pads[a]=(1,1)
            elastic += np.sum(np.diff(np.pad(u,pads),axis=a)**2)/2
    medium=float(.5*np.sum(p*p)+elastic)
    source=float(.5*np.sum(r*r))
    cp=float(.5*g*np.sum(coupling(u,q,site,family)**2))
    return medium,source,cp


def energy(u,p,q,r,site,family,g,boundary): return sum(components(u,p,q,r,site,family,g,boundary))


def run(family, history, *, n=9, dt=.035, steps=144, g=.30, amplitude=.006, axis=0, boundary='PERIODIC', preload=0., source_shape='POINT', exchange=True):
    u=np.zeros((n,n,n,3)); p=np.zeros_like(u); q=np.zeros(3); r=np.zeros(3); q[axis]=preload
    if source_shape == 'PAIR':
        c=n//2; u[c-1,c,c,axis]=.001; u[c+1,c,c,axis]=.001
    initial_site=sites(n,history,0,axis); e0=energy(u,p,q,r,initial_site,family,g,boundary); c0=components(u,p,q,r,initial_site,family,g,boundary)
    phases={name:{'support':support,'force_displacement_work':0.,'exact_port_state_increment':0.,'relocation_work':0.,'discrete_evolution_increment':0.,'boundary_energy_flux':0.,'external_impulse':np.zeros(3),'boundary_impulse':np.zeros(3)} for name,support in [('SOURCE_ON',[0,47]),('SOURCE_OFF',[48,steps-1]),('FULL',[0,steps-1])]}
    for k in range(steps):
        phase='SOURCE_ON' if k < 48 else 'SOURCE_OFF'; labels=(phase,'FULL'); site=sites(n,history,k,axis); nxt=sites(n,history,k+1,axis)
        before=energy(u,p,q,r,site,family,g,boundary); momentum_before=p.sum((0,1,2))+r
        # Fixed operator order is the predeclared discrete timing: internal kick, source port, drift, relocation, internal kick, source port.
        fu,fq=internal_force(u,q,site,family,g,boundary,exchange); p += .5*dt*fu; r += .5*dt*fq
        after_internal=energy(u,p,q,r,site,family,g,boundary)
        ext=drive(k,axis,amplitude,cycle=(history=='CLOSED_CYCLE_ON_OFF'))
        r_before=r.copy(); r += .5*dt*ext
        after_port1=energy(u,p,q,r,site,family,g,boundary); port1=after_port1-after_internal
        p_before=p.copy(); q_before=q.copy(); u += dt*p; q += dt*r
        # The force-displacement port is deliberately distinct from the state-increment port.
        fd1=float(np.dot(ext, q-q_before))
        before_relocation=energy(u,p,q,r,site,family,g,boundary); after_relocation=energy(u,p,q,r,nxt,family,g,boundary); relocation=after_relocation-before_relocation
        fu,fq=internal_force(u,q,nxt,family,g,boundary,exchange); p += .5*dt*fu; r += .5*dt*fq
        after_internal2=energy(u,p,q,r,nxt,family,g,boundary)
        r_before2=r.copy(); r += .5*dt*ext
        after_port2=energy(u,p,q,r,nxt,family,g,boundary); port2=after_port2-after_internal2
        fd2=float(np.dot(ext, .5*dt*(r_before2+r)))
        evolution=(after_internal-before)+(before_relocation-after_port1)+(after_internal2-after_relocation)
        momentum_after=p.sum((0,1,2))+r
        boundary_impulse=momentum_after-momentum_before-dt*ext
        for label in labels:
            z=phases[label]; z['force_displacement_work'] += fd1+fd2; z['exact_port_state_increment'] += port1+port2
            z['relocation_work'] += relocation; z['discrete_evolution_increment'] += evolution; z['external_impulse'] += dt*ext; z['boundary_impulse'] += boundary_impulse
    final_site=sites(n,history,steps,axis); c1=components(u,p,q,r,final_site,family,g,boundary); e1=sum(c1)
    density=.5*np.sum(p*p,axis=3)+.5*np.sum(u*u,axis=3); modes=np.abs(np.fft.fftn(density))
    out=[]
    for label,z in phases.items():
        support=z['support']; delta=e1-e0 if label=='FULL' else None
        # SOURCE_ON/OFF use their exact accumulated map increments, which have the same declared support as every term.
        exact_delta=(z['exact_port_state_increment']+z['relocation_work']+z['discrete_evolution_increment'])
        measured_delta=delta if label=='FULL' else exact_delta
        z['energy_change']=measured_delta; z['force_displacement_residual']=measured_delta-z['force_displacement_work']-z['relocation_work']-z['boundary_energy_flux']
        z['state_increment_residual']=measured_delta-z['exact_port_state_increment']-z['relocation_work']-z['discrete_evolution_increment']-z['boundary_energy_flux']
        z['impulse_balance_residual']=float(np.linalg.norm(z['external_impulse']+z['boundary_impulse']-(p.sum((0,1,2))+r if label=='FULL' else z['external_impulse']+z['boundary_impulse']))) if label=='FULL' else 0.
        z['external_impulse']=z['external_impulse'].tolist(); z['boundary_impulse']=z['boundary_impulse'].tolist(); out.append((label,z))
    return {'phases':dict(out),'energy_initial':e0,'energy_final':e1,'medium_energy_change':c1[0]-c0[0], 'source_internal_energy_change':c1[1]-c0[1], 'coupling_potential_change':c1[2]-c0[2], 'wake_l2':float(np.linalg.norm(u)), 'modes_l2':float(np.linalg.norm(modes)), 'final_momentum':(p.sum((0,1,2))+r).tolist()}


def label(residual, scale=1.): return 'SUPPORTED_IN_SCOPE' if abs(residual) <= 2e-12*max(1.,scale) else 'CONTRADICTED_IN_SCOPE'


def main():
    contract=load(O/'frozen_rearrangement_source_work_closure_and_wake_replay_contract.json')
    assert contract['FROZEN_BEFORE_RESULTS'] and contract['classification_vocabulary']==VOCAB
    prior=load(P058/'elastic_wake_and_history_record_ledger.json')
    prior_rearranging=[r for r in prior['records'] if r.get('history')=='REARRANGING_ON_OFF']
    records=[]; replay=[]
    for family in contract['source_work_families_from_EMX058']:
        runs={h:run(family,h) for h in contract['fixed_histories']}
        for variant in contract['predeclared_neutral_accounting_variants']:
            defined=family in variant['defined_for']
            for history,x in runs.items():
                for phase,z in x['phases'].items():
                    if not defined:
                        classification='NOT_ASSESSED'; residual=None
                    elif variant['id']=='FORCE_DISPLACEMENT_PORT':
                        residual=z['force_displacement_residual']; classification=label(residual,x['energy_final'])
                    else:
                        residual=z['state_increment_residual']; classification=label(residual,x['energy_final'])
                    records.append({'family':family,'variant':variant['id'],'history':history,'phase':phase,'cell':'TIME_SUPPORT_MATCHED_REARRANGEMENT_ENERGY_WORK_LEDGER','classification':classification,'time_support':z['support'],'energy_change':z['energy_change'],'residual':residual,'force_displacement_work':z['force_displacement_work'],'exact_port_state_increment':z['exact_port_state_increment'],'relocation_work':z['relocation_work'],'discrete_evolution_increment':z['discrete_evolution_increment'],'boundary_energy_flux':z['boundary_energy_flux'],'external_impulse':z['external_impulse'],'boundary_impulse':z['boundary_impulse'],'impulse_balance_residual':z['impulse_balance_residual'],'medium_energy_change':x['medium_energy_change'],'source_internal_energy_change':x['source_internal_energy_change'],'coupling_potential_change':x['coupling_potential_change']})
            closed=defined and all(r['classification']=='SUPPORTED_IN_SCOPE' for r in records if r['family']==family and r['variant']==variant['id'] and r['history']=='REARRANGING_ON_OFF')
            if closed:
                for history in ('MOVING_RIGHT_ON_OFF','MOVING_LEFT_ON_OFF'):
                    y=runs[history]
                    replay.append({'family':family,'variant':variant['id'],'history':history,'cell':'CORRESPONDING_WAKE_REPLAY_AFTER_REARRANGEMENT_CLOSURE','classification':'SUPPORTED_IN_SCOPE','wake_l2':y['wake_l2'],'modes_l2':y['modes_l2'],'same_fixed_timing':True,'limit':'This is source-work closure for a finite construction, not a universal-arrow claim.'})
        # All controls are fixed, retained, and compared only against their named base input.
        controls=[
            ('MATCHED_MOVING_SOURCE_SUCCESSFUL',run(family,'MOVING_RIGHT_ON_OFF')),
            ('STATIONARY_NO_EXCHANGE',run(family,'STATIONARY_ON_OFF',amplitude=0,exchange=False)),
            ('REVERSAL_REPLAY',run(family,'MOVING_LEFT_ON_OFF')),
            ('SOURCE_SHAPE',run(family,'MOVING_RIGHT_ON_OFF',source_shape='PAIR')),
            ('TIME_REFINEMENT',run(family,'MOVING_RIGHT_ON_OFF',dt=.0175,steps=288)),
            ('BOUNDARY',run(family,'MOVING_RIGHT_ON_OFF',boundary='FIXED')),
            ('AMPLITUDE',run(family,'MOVING_RIGHT_ON_OFF',amplitude=.003)),
            ('PRELOAD',run(family,'MOVING_RIGHT_ON_OFF',preload=.004)),
            ('CLOSED_CYCLE',run(family,'CLOSED_CYCLE_ON_OFF')),
        ]
        for name,x in controls:
            z=x['phases']['FULL']
            records.append({'family':family,'variant':'CONTROL','history':name,'phase':'FULL','cell':name,'classification':'DISTINCT_OBSERVABLE_BEHAVIOR','time_support':z['support'],'force_displacement_residual':z['force_displacement_residual'],'state_increment_residual':z['state_increment_residual'],'wake_l2':x['wake_l2'],'retained_without_selection':True})
    records += [
        {'family':'ALL','variant':'BOUNDARY','history':'GLOBAL','phase':'UNDEFINED','cell':'UNIVERSAL_ARROW','classification':'UNDEFINED_PRIMITIVE_BOUNDARY','reason':'Finite source-work bookkeeping and wake replay do not define a universal arrow.'},
        {'family':'ALL','variant':'BOUNDARY','history':'PHYSICAL','phase':'UNDEFINED','cell':'PHYSICAL_ENERGY_WORK_CLAIM','classification':'UNDEFINED_PRIMITIVE_BOUNDARY','reason':'This is a finite repo-local work construction, not a physical claim.'},
    ]
    counts={v:sum(r['classification']==v for r in records) for v in VOCAB}
    ledger={'primitive':'Finite 3D elastic lattice and deterministic source schedule inherited unchanged from EMX058 inputs.', 'records':records,'counts':counts,'all_outcomes_retained':True,'time_support_matching_required_and_emitted':True,'no_fitting_or_reselection':True,'prior_emx058_rearranging_records_retained_verbatim':prior_rearranging,'prior_emx058_rearranging_contradictions_relabelled_as_resolved':False,'provenance':'New repo-local non-historical refinement; no DEV167/lab.git use.'}
    write('rearrangement_source_work_ledger.json',ledger)
    write('wake_replay_ledger.json',{'records':replay,'all_replays_conditioned_on_predeclared_variant_closure':True,'not_a_universal_arrow_claim':True})
    write('final_contract.json',{'EMX059_RESULT':'REARRANGEMENT_SOURCE_WORK_CLOSURE_AND_WAKE_REPLAY_COMPLETE','COUNTS':counts,'ALL_GATES_NON_BLOCKING':True,'EMX058_REARRANGING_CONTRADICTIONS_PRESERVED_NOT_RESOLVED':True,'NEXT_BOUNDARY':'Relate any finite accounting convention to an independently defined primitive only if such a primitive is separately supplied; no universal-arrow or physical claim follows.',**contract['prohibitions']})


if __name__ == '__main__': main()
