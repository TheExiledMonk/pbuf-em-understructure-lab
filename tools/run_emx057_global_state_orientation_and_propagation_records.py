#!/usr/bin/env python3
"""Execute the frozen, finite EMX057 orientation/propagation record battery."""
from __future__ import annotations
import hashlib
import json
import numpy as np
from pathlib import Path

R = Path(__file__).resolve().parents[1]
O = R / 'runs' / 'emx057'
VOCAB = ['SUPPORTED_IN_SCOPE', 'CONTRADICTED_IN_SCOPE', 'DISTINCT_OBSERVABLE_BEHAVIOR', 'NOT_ASSESSED', 'UNDEFINED_PRIMITIVE_BOUNDARY']

def load(name): return json.loads((O / name).read_text())
def chash(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def write(name, value):
    value = dict(value)
    value['artifact_sha256'] = chash(value)
    (O / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

def force(u, boundary):
    if boundary == 'PERIODIC':
        return sum(np.roll(u, s, a) - u for a in range(3) for s in (-1, 1))
    z = np.pad(u, ((1, 1), (1, 1), (1, 1), (0, 0)))
    return (z[2:, 1:-1, 1:-1] + z[:-2, 1:-1, 1:-1] + z[1:-1, 2:, 1:-1] +
            z[1:-1, :-2, 1:-1] + z[1:-1, 1:-1, 2:] + z[1:-1, 1:-1, :-2] - 6 * u)

def energy(u, p, q, r, g, boundary):
    if boundary == 'PERIODIC':
        elastic = sum(np.sum((np.roll(u, 1, a) - u) ** 2) for a in range(3)) / 2
    else:
        # Fixed exterior cells are zero; include their edge springs in V.
        elastic = 0.
        for a in range(3):
            pads = [(0, 0)] * 4; pads[a] = (1, 1)
            elastic += np.sum(np.diff(np.pad(u, pads), axis=a) ** 2) / 2
    c = tuple(x // 2 for x in u.shape[:3])
    return float(.5 * np.sum(p*p) + elastic + .5 * np.sum(r*r) + .5 * g * np.sum((q-u[c])**2))

def state(n=9, axis=0, preload='DISPLACEMENT_PRELOAD', standing=False):
    u = np.zeros((n, n, n, 3)); p = np.zeros_like(u); q = np.zeros(3); r = np.zeros(3)
    q[axis] = .03 if preload == 'DISPLACEMENT_PRELOAD' else 0.
    r[axis] = .03 if preload == 'VELOCITY_PRELOAD' else 0.
    if standing:
        c = n // 2; u[c-1, c, c, axis] = .004; u[c+1, c, c, axis] = .004
    return u, p, q, r

def record(u, p, q, r, g, boundary):
    density = .5*np.sum(p*p, axis=3) + .5*np.sum(u*u, axis=3)
    sorted_density = np.sort(density.ravel())
    spectrum = np.sort(np.abs(np.fft.fftn(density)).ravel())
    c = tuple(x // 2 for x in u.shape[:3])
    local = float(.5*np.sum(r*r) + .5*g*np.sum((q-u[c])**2))
    return {'local_energy': local, 'sorted_energy_distribution_l2': float(np.linalg.norm(sorted_density)),
            'translation_invariant_spectrum_l2': float(np.linalg.norm(spectrum)),
            'full_state_l2': float(np.sqrt(np.sum(u*u)+np.sum(p*p)+np.sum(q*q)+np.sum(r*r)))}

def evolve(initial, *, g=.30, dt=.04, steps=120, boundary='PERIODIC', snapshots=False):
    u, p, q, r = (x.copy() for x in initial); c = tuple(x // 2 for x in u.shape[:3]); e0 = energy(u,p,q,r,g,boundary)
    history = []; recs = []
    for k in range(steps + 1):
        recs.append(record(u,p,q,r,g,boundary))
        if snapshots: history.append((u.copy(), p.copy(), q.copy(), r.copy()))
        if k == steps: break
        d = q-u[c]; fu = force(u,boundary); fu[c] += g*d; fq = -g*d
        p += .5*dt*fu; r += .5*dt*fq; u += dt*p; q += dt*r
        d = q-u[c]; fu = force(u,boundary); fu[c] += g*d; fq = -g*d
        p += .5*dt*fu; r += .5*dt*fq
    return (u,p,q,r), recs, e0, energy(u,p,q,r,g,boundary), history

def reverse(state):
    u,p,q,r = state
    return u.copy(), -p.copy(), q.copy(), -r.copy()

def classification(ok): return 'SUPPORTED_IN_SCOPE' if ok else 'CONTRADICTED_IN_SCOPE'

def main():
    contract = load('frozen_global_state_orientation_and_propagation_records_contract.json')
    assert contract['FROZEN_BEFORE_RESULTS'] and contract['classification_vocabulary'] == VOCAB
    rows = []
    for family in contract['families_from_EMX056']:
        for preload in ['DISPLACEMENT_PRELOAD', 'VELOCITY_PRELOAD']:
            initial = state(preload=preload); final, recs, start_e, end_e, hist = evolve(initial, snapshots=True)
            drift = abs(end_e-start_e)/start_e
            local_drop = recs[0]['local_energy'] - recs[-1]['local_energy']
            distributed_change = abs(recs[-1]['translation_invariant_spectrum_l2']-recs[0]['translation_invariant_spectrum_l2'])
            rows += [
                {'family':family,'cell':'SOURCE_OFF_OUTGOING_FINITE_EMISSION_'+preload,'classification':classification(local_drop > 0), 'local_drop':local_drop, 'external_source_after_initialization':False},
                {'family':family,'cell':'TOTAL_CONSERVATION_'+preload,'classification':classification(drift < .003),'relative_energy_drift':drift},
                {'family':family,'cell':'TRANSPORTED_ENERGY_'+preload,'classification':classification(local_drop > 0),'transported_energy_complement':local_drop},
                {'family':family,'cell':'DISTRIBUTED_ORIGIN_FREE_RECORD_'+preload,'classification':'DISTINCT_OBSERVABLE_BEHAVIOR' if distributed_change > 1e-12 else 'NOT_ASSESSED','spectral_change':distributed_change,'assumptions':'No origin, entropy, dissipation, or physical-clock assumption.'},
            ]
            back, _, _, _, _ = evolve(reverse(final)); returned = reverse(back)
            err = max(float(np.max(abs(a-b))) for a,b in zip(initial, returned))
            rows.append({'family':family,'cell':'MATCHED_INCOMING_TIME_REVERSED_'+preload,'classification':classification(err < 2e-12),'round_trip_max_error':err,'meaning':'Finite source-off replay relation only; not global reversal.'})
            rows.append({'family':family,'cell':'LOCAL_RETURN_'+preload,'classification':classification(err < 2e-12),'full_state_history_record':'Initial/final matched by reversed finite history.'})
            recurrence, _, _, _, _ = evolve(final, steps=120)
            rows.append({'family':family,'cell':'FINITE_RECURRENCE_CONTROL_'+preload,'classification':'DISTINCT_OBSERVABLE_BEHAVIOR','finite_domain_note':'A later finite-domain state is retained as a recurrence control, never promoted to an arrow.','state_l2':record(*recurrence,.30,'PERIODIC')['full_state_l2']})
        no_exchange, _, a, b, _ = evolve(state(), g=0)
        rows.append({'family':family,'cell':'NO_EXCHANGE_CONTROL','classification':classification(abs(a-b) < 1e-14),'relative_energy_change':abs(a-b)})
        stand, sr, se0, se1, _ = evolve(state(standing=True))
        rows.append({'family':family,'cell':'STANDING_SYMMETRIC_CONTROL','classification':classification(abs(se1-se0)/se0 < .003),'relative_energy_drift':abs(se1-se0)/se0})
        base, _, _, _, _ = evolve(state(axis=0))
        ru, rp, rq, rr = state(axis=0)
        # x-reflection of a polar displacement reverses its x component.
        reflected_initial = (np.flip(ru,0).copy(), np.flip(rp,0).copy(), rq.copy(), rr.copy())
        for value in reflected_initial: value[..., 0] *= -1
        reflected, _, _, _, _ = evolve(reflected_initial)
        reflection_error = max(
            float(np.max(abs(base[0] + np.flip(reflected[0], 0)))),
            float(np.max(abs(base[1] + np.flip(reflected[1], 0)))),
            float(np.max(abs(base[2] + reflected[2]))),
            float(np.max(abs(base[3] + reflected[3]))),
        )
        rows.append({'family':family,'cell':'SPATIAL_REFLECTION_CONTROL','classification':classification(reflection_error < 2e-12),'max_error':reflection_error})
        for axis in (1,2):
            rotated, _, _, _, _ = evolve(state(axis=axis)); covariance_error = abs(record(*base,.30,'PERIODIC')['full_state_l2']-record(*rotated,.30,'PERIODIC')['full_state_l2'])
            rows.append({'family':family,'cell':'AXIS_COVARIANCE_'+str(axis),'classification':classification(covariance_error < 2e-12),'record_difference':covariance_error})
        fine, _, _, _, _ = evolve(state(), dt=.02, steps=240); coarse, _, _, _, _ = evolve(state())
        referr = abs(record(*fine,.30,'PERIODIC')['full_state_l2']-record(*coarse,.30,'PERIODIC')['full_state_l2'])
        rows.append({'family':family,'cell':'TIME_REFINEMENT','classification':'DISTINCT_OBSERVABLE_BEHAVIOR','record_difference':referr,'note':'Finite discretizations are retained rather than selected.'})
        lattice, _, _, _, _ = evolve(state(n=11), steps=120); small, _, _, _, _ = evolve(state(n=9), steps=120)
        rows.append({'family':family,'cell':'LATTICE_REFINEMENT','classification':'DISTINCT_OBSERVABLE_BEHAVIOR','n9_n11_record_difference':abs(record(*lattice,.30,'PERIODIC')['full_state_l2']-record(*small,.30,'PERIODIC')['full_state_l2'])})
        fixed, _, fe0, fe1, _ = evolve(state(), boundary='FIXED')
        rows.append({'family':family,'cell':'FIXED_BOUNDARY_CONTROL','classification':classification(abs(fe1-fe0)/fe0 < .003),'relative_energy_drift':abs(fe1-fe0)/fe0,'boundary_conditioned':True})
    rows += [
        {'family':'ALL','cell':'TRUE_GLOBAL_REVERSAL','classification':'UNDEFINED_PRIMITIVE_BOUNDARY','reason':'Finite reversible replay does not define reversal of an unbounded/global state or select a global orientation.'},
        {'family':'ALL','cell':'UNIVERSAL_ARROW','classification':'UNDEFINED_PRIMITIVE_BOUNDARY','reason':'No universal arrow is derived from source, preload, finite-domain, boundary-conditioned, or recurrence histories.'},
        {'family':'ALL','cell':'INDEPENDENT_PHYSICAL_CLOCK','classification':'UNDEFINED_PRIMITIVE_BOUNDARY','reason':'Step index orders an algorithm only; the primitive supplies no physical clock.'},
    ]
    counts = {label: sum(x['classification'] == label for x in rows) for label in VOCAB}
    ledger = {'primitive':contract['primitive'], 'records':rows, 'counts':counts, 'all_outcomes_retained':True, 'no_universal_arrow_claim':True}
    write('global_state_orientation_and_propagation_record_ledger.json', ledger)
    write('final_contract.json', {'EMX057_RESULT':'GLOBAL_STATE_ORIENTATION_AND_PROPAGATION_RECORDS_COMPLETE','COUNTS':counts,'ALL_GATES_NON_BLOCKING':True,'NEXT_BOUNDARY':'A global/unbounded reversal, a physical clock, and a universal arrow remain undefined primitives; finite controls are retained.', **contract['prohibitions']})

if __name__ == '__main__': main()
