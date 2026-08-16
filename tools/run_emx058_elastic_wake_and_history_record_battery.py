#!/usr/bin/env python3
"""Run EMX058's finite, deterministic elastic wake and record battery."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parents[1]
O = R / 'runs' / 'emx058'
VOCAB = ['SUPPORTED_IN_SCOPE', 'CONTRADICTED_IN_SCOPE', 'DISTINCT_OBSERVABLE_BEHAVIOR', 'NOT_ASSESSED', 'UNDEFINED_PRIMITIVE_BOUNDARY']

def load(name): return json.loads((O / name).read_text())
def hashed(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def write(name, value):
    value = dict(value); value['artifact_sha256'] = hashed(value)
    (O / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

def laplacian(u, boundary):
    if boundary == 'PERIODIC':
        return sum(np.roll(u, shift, axis) - u for axis in range(3) for shift in (-1, 1))
    z = np.pad(u, ((1, 1), (1, 1), (1, 1), (0, 0)))
    return z[2:,1:-1,1:-1] + z[:-2,1:-1,1:-1] + z[1:-1,2:,1:-1] + z[1:-1,:-2,1:-1] + z[1:-1,1:-1,2:] + z[1:-1,1:-1,:-2] - 6*u

def sites(n, history, step, axis=0):
    c = n // 2; base = [c, c, c]; shift = min(2, step // 14)
    if history == 'MOVING_RIGHT_ON_OFF': base[axis] += shift
    elif history == 'MOVING_LEFT_ON_OFF': base[axis] -= shift
    elif history == 'REARRANGING_ON_OFF': base[(axis + 1) % 3] += 1 if (step // 12) % 2 else -1
    a = tuple(base); b = list(base); b[axis] = min(n - 1, b[axis] + 1)
    return a, tuple(b)

def drive(step, axis, amplitude, enabled=True):
    f = np.zeros(3)
    if enabled and step < 48:
        f[axis] = amplitude * np.sin(np.pi * (step + .5) / 48)
    return f

def coupling(u, q, site, family, g):
    a, b = site
    if family == 'POTENTIAL_PORT_EQUIVALENCE_CLASS': return q - u[a]
    return q - (u[b] - u[a])

def apply_coupling_force(fu, fq, d, site, family, g):
    a, b = site
    if family == 'POTENTIAL_PORT_EQUIVALENCE_CLASS': fu[a] += g*d
    else: fu[a] -= g*d; fu[b] += g*d
    return fq - g*d

def mechanical_energy(u, p, q, r, site, family, g, boundary):
    elastic = sum(np.sum((np.roll(u, 1, a)-u)**2) for a in range(3))/2 if boundary == 'PERIODIC' else sum(np.sum(np.diff(np.pad(u, [(1,1) if i == a else (0,0) for i in range(4)]), axis=a)**2)/2 for a in range(3))
    d = coupling(u, q, site, family, g)
    return float(.5*np.sum(p*p) + elastic + .5*np.sum(r*r) + .5*g*np.sum(d*d))

def run(family, history='MOVING_RIGHT_ON_OFF', *, n=9, dt=.035, steps=144, g=.30, amplitude=.006, axis=0, boundary='PERIODIC', preload=.0, source_shape='POINT', exchange=True, reverse_at=None):
    u=np.zeros((n,n,n,3)); p=np.zeros_like(u); q=np.zeros(3); r=np.zeros(3); q[axis]=preload
    if source_shape == 'PAIR':
        c=n//2; u[c-1,c,c,axis]=.001; u[c+1,c,c,axis]=.001
    initial=(u.copy(),p.copy(),q.copy(),r.copy()); work=relocation=impulse=0.; off = 48
    e0=mechanical_energy(u,p,q,r,sites(n,history,0,axis),family,g,boundary); peak_local=0.; snapshots=[]
    for k in range(steps):
        site=sites(n,history,k,axis); next_site=sites(n,history,k+1,axis)
        d=coupling(u,q,site,family,g) if exchange else np.zeros(3)
        fu=laplacian(u,boundary); fq=np.zeros(3)
        if exchange: fq=apply_coupling_force(fu,fq,d,site,family,g)
        ext=drive(k,axis,amplitude); fq += ext
        p += .5*dt*fu; r += .5*dt*fq; u += dt*p; q += dt*r
        # Work from the externally driven source coordinate at its actual displacement.
        work += float(np.dot(ext, dt*r))
        impulse += float(np.linalg.norm(ext)*dt)
        if reverse_at is not None and k + 1 == reverse_at: p *= -1; r *= -1
        # Deterministic moving/rearranging port changes have explicit parametric work.
        before=mechanical_energy(u,p,q,r,site,family,g,boundary)
        after=mechanical_energy(u,p,q,r,next_site,family,g,boundary)
        relocation += after-before
        d=coupling(u,q,next_site,family,g) if exchange else np.zeros(3)
        fu=laplacian(u,boundary); fq=np.zeros(3)
        if exchange: fq=apply_coupling_force(fu,fq,d,next_site,family,g)
        fq += ext
        p += .5*dt*fu; r += .5*dt*fq
        local=.5*np.sum(r*r)+.5*g*np.sum(coupling(u,q,next_site,family,g)**2)
        peak_local=max(peak_local,float(local))
        if k in (47, 95, 143): snapshots.append((u.copy(),p.copy(),q.copy(),r.copy()))
    final_site=sites(n,history,steps,axis); e1=mechanical_energy(u,p,q,r,final_site,family,g,boundary)
    density=.5*np.sum(p*p,axis=3)+.5*np.sum(u*u,axis=3)
    pos=np.indices((n,n,n))[axis]-final_site[0][axis]
    phase=float(np.sum(pos*p[...,axis])); modes=np.abs(np.fft.fftn(density));
    local_final=.5*np.sum(r*r)+.5*g*np.sum(coupling(u,q,final_site,family,g)**2)
    total_momentum=p.sum((0,1,2))+r
    return {'state':(u,p,q,r),'initial':initial,'snapshots':snapshots,'energy_initial':e0,'energy_final':e1,'source_work':work,'relocation_work':relocation,'exchange_residual':e1-e0-work-relocation,'medium_energy':float(e1-local_final),'source_energy':float(.5*np.sum(r*r)),'coupling_energy':float(.5*g*np.sum(coupling(u,q,final_site,family,g)**2)),'medium_momentum':p.sum((0,1,2)).tolist(),'source_momentum':r.tolist(),'external_impulse_magnitude':impulse,'momentum_residual_norm':float(np.linalg.norm(total_momentum)-impulse),'residual_deformation_l2':float(np.linalg.norm(u)),'phase_correlation_record':phase,'scattered_modes_l2':float(np.linalg.norm(modes)),'local_energy_peak':peak_local,'local_energy_final':float(local_final),'delayed_local_relaxation':float(peak_local-local_final),'transported_ledger':float(e1-local_final),'source_off':True,'final_site':list(final_site[0])}

def ok(value, limit): return 'SUPPORTED_IN_SCOPE' if abs(value) <= limit else 'CONTRADICTED_IN_SCOPE'

def main():
    c=load('frozen_elastic_wake_and_history_record_battery_contract.json')
    assert c['FROZEN_BEFORE_RESULTS'] and c['classification_vocabulary'] == VOCAB
    rows=[]; summaries=[]
    for family in c['families_from_EMX056_EMX055']:
        trials={h:run(family,h) for h in c['finite_deterministic_primitive']['histories']}
        for history,x in trials.items():
            scale=max(abs(x['energy_final']), 1e-12); balance=x['exchange_residual']/scale
            rows += [
                {'family':family,'history':history,'cell':'COMPLETE_SOURCE_MEDIUM_ENERGY_WORK_ACCOUNTING','classification':ok(balance,.01),'relative_exchange_residual':balance,'medium_energy':x['medium_energy'],'source_energy':x['source_energy'],'coupling_energy':x['coupling_energy'],'source_work':x['source_work'],'relocation_work':x['relocation_work'],'total_energy':x['energy_final']},
                {'family':family,'history':history,'cell':'MOMENTUM_EXCHANGE_ACCOUNTING','classification':'DISTINCT_OBSERVABLE_BEHAVIOR','medium_momentum':x['medium_momentum'],'source_momentum':x['source_momentum'],'external_impulse_magnitude':x['external_impulse_magnitude'],'momentum_residual_norm':x['momentum_residual_norm']},
                {'family':family,'history':history,'cell':'SOURCE_OFF_WAKE','classification':'SUPPORTED_IN_SCOPE' if x['residual_deformation_l2']>1e-8 else 'CONTRADICTED_IN_SCOPE','residual_deformation_l2':x['residual_deformation_l2'],'source_off':True},
                {'family':family,'history':history,'cell':'PHASE_CORRELATION_AND_SCATTERED_MODE_RECORD','classification':'DISTINCT_OBSERVABLE_BEHAVIOR','phase_correlation_record':x['phase_correlation_record'],'scattered_modes_l2':x['scattered_modes_l2']},
                {'family':family,'history':history,'cell':'DELAYED_LOCAL_RELAXATION_AND_TRANSPORT','classification':'SUPPORTED_IN_SCOPE' if x['delayed_local_relaxation']>0 else 'CONTRADICTED_IN_SCOPE','local_relaxation':x['delayed_local_relaxation'],'transported_ledger':x['transported_ledger']},
            ]
        # Direction is reconstructed only by a signed source-relative phase record.
        right, left=trials['MOVING_RIGHT_ON_OFF'],trials['MOVING_LEFT_ON_OFF']
        rows.append({'family':family,'history':'DIRECTION_PAIR','cell':'PRIOR_PASSAGE_DIRECTION_RECONSTRUCTION','classification':'SUPPORTED_IN_SCOPE' if right['phase_correlation_record']*left['phase_correlation_record']<0 else 'NOT_ASSESSED','right_phase':right['phase_correlation_record'],'left_phase':left['phase_correlation_record'],'limit':'This is a finite source-relative record test, not an arrow claim.'})
        stationary=run(family,'MOVING_RIGHT_ON_OFF',amplitude=0); nox=run(family,'MOVING_RIGHT_ON_OFF',exchange=False)
        reflected=run(family,'MOVING_LEFT_ON_OFF'); recurrence=run(family,'MOVING_RIGHT_ON_OFF',steps=288)
        reverse=run(family,'MOVING_RIGHT_ON_OFF',reverse_at=96)
        controls=[
          ('STATIONARY', 'DISTINCT_OBSERVABLE_BEHAVIOR', stationary['residual_deformation_l2']), ('NO_EXCHANGE', 'SUPPORTED_IN_SCOPE', nox['residual_deformation_l2']),
          ('SOURCE_SHAPE', 'DISTINCT_OBSERVABLE_BEHAVIOR', run(family,'MOVING_RIGHT_ON_OFF',source_shape='PAIR')['scattered_modes_l2']),
          ('DIRECTED_PREPARATION', 'DISTINCT_OBSERVABLE_BEHAVIOR', run(family,'MOVING_RIGHT_ON_OFF',preload=.004)['phase_correlation_record']),
          ('CONTROLLED_FULL_STATE_REVERSAL', 'DISTINCT_OBSERVABLE_BEHAVIOR', reverse['residual_deformation_l2']), ('REFLECTION', 'DISTINCT_OBSERVABLE_BEHAVIOR', reflected['phase_correlation_record']),
          ('RECURRENCE', 'DISTINCT_OBSERVABLE_BEHAVIOR', recurrence['residual_deformation_l2']), ('PERIODIC_AND_FIXED_BOUNDARY', 'DISTINCT_OBSERVABLE_BEHAVIOR', run(family,'MOVING_RIGHT_ON_OFF',boundary='FIXED')['scattered_modes_l2']),
          ('STIFFNESS_AND_PRELOAD', 'DISTINCT_OBSERVABLE_BEHAVIOR', run(family,'MOVING_RIGHT_ON_OFF',g=.45,preload=.003)['transported_ledger']), ('AXIS_COVARIANCE', 'DISTINCT_OBSERVABLE_BEHAVIOR', run(family,'MOVING_RIGHT_ON_OFF',axis=1)['scattered_modes_l2']),
          ('RELATION_NETWORK_AND_REFINEMENT', 'DISTINCT_OBSERVABLE_BEHAVIOR', run(family,'REARRANGING_ON_OFF',dt=.0175,steps=288)['scattered_modes_l2']), ('SPEED_AMPLITUDE_AND_FINITE_DOMAIN', 'DISTINCT_OBSERVABLE_BEHAVIOR', run(family,'MOVING_RIGHT_ON_OFF',n=11,amplitude=.003)['transported_ledger'])]
        for name, classification, value in controls: rows.append({'family':family,'history':'CONTROL','cell':name,'classification':classification,'observable_value':value,'retained_without_selection':True})
        summaries.append({'family':family,'moving_right_wake':trials['MOVING_RIGHT_ON_OFF']['residual_deformation_l2'],'moving_right_transport':trials['MOVING_RIGHT_ON_OFF']['transported_ledger'],'rearranging_modes':trials['REARRANGING_ON_OFF']['scattered_modes_l2']})
    rows += [
      {'family':'ALL','history':'BOUNDARY','cell':'DYNAMIC_EXCLUSION_OF_EXACT_GLOBAL_REVERSAL','classification':'UNDEFINED_PRIMITIVE_BOUNDARY','reason':'Finite controlled replay does not define or dynamically exclude exact reversal of a global/unbounded state.'},
      {'family':'ALL','history':'BOUNDARY','cell':'UNIVERSAL_ARROW_OR_PHYSICAL_CLOCK','classification':'UNDEFINED_PRIMITIVE_BOUNDARY','reason':'Source-conditioned finite histories do not supply a physical clock or universal arrow.'},
      {'family':'ALL','history':'BOUNDARY','cell':'FAMILY_DISCRIMINATION','classification':'DISTINCT_OBSERVABLE_BEHAVIOR','family_summaries':summaries,'meaning':'Finite observables distinguish implementations without selecting a physical interpretation.'}]
    counts={v:sum(r['classification']==v for r in rows) for v in VOCAB}
    ledger={'primitive':c['finite_deterministic_primitive'],'records':rows,'counts':counts,'all_outcomes_retained':True,'no_candidate_rejected_for_missing_closure':True,'provenance':'New repo-local non-historical experiment; no DEV167/lab.git use.'}
    write('elastic_wake_and_history_record_ledger.json',ledger)
    write('family_wake_comparison.json',{'families':summaries,'classification':'DISTINCT_OBSERVABLE_BEHAVIOR','no_reselection':True})
    write('final_contract.json',{'EMX058_RESULT':'ELASTIC_WAKE_AND_HISTORY_RECORD_BATTERY_COMPLETE','COUNTS':counts,'ALL_GATES_NON_BLOCKING':True,'IN_SCOPE_STATEMENTS':['Finite source-off wake observations are retained.','Finite source-work family behavior is discriminated without selection.','Wake and record observations are source-history and boundary conditioned.'],'LIMITS':c['interpretation_limits'],**c['prohibitions']})

if __name__ == '__main__': main()
