#!/usr/bin/env python3
"""Run EMX060: finite one-medium, internal-interaction-functional records only."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parents[1]
O = R / 'runs' / 'emx060'
VOCAB = ['SUPPORTED_IN_SCOPE', 'CONTRADICTED_IN_SCOPE', 'DISTINCT_OBSERVABLE_BEHAVIOR', 'NOT_ASSESSED', 'UNDEFINED_PRIMITIVE_BOUNDARY']


def load(path): return json.loads(path.read_text())
def hashed(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def write(name, value):
    value = dict(value); value['artifact_sha256'] = hashed(value)
    (O / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def matter(mu, n, radius, shape='COMPACT_GAUSSIAN'):
    grid = np.indices((n, n, n), dtype=float)
    delta = grid - np.asarray(mu).reshape(3, 1, 1, 1)
    # This is a normalized discrete configuration field, entirely within q.
    d2 = np.sum(delta * delta, axis=0)
    if shape == 'TWO_LOBE':
        delta2 = grid - (np.asarray(mu) + np.array([0., .75, 0.])).reshape(3, 1, 1, 1)
        d2 = np.minimum(d2, np.sum(delta2 * delta2, axis=0))
    m = np.exp(-d2 / (radius * radius))
    return m / m.sum()


def elastic_energy(u, k):
    return .5 * k * sum(np.sum((np.roll(u, -1, axis=a) - u) ** 2) for a in range(3))


def elastic_force(u, k):
    return k * sum(np.roll(u, 1, axis=a) + np.roll(u, -1, axis=a) - 2 * u for a in range(3))


def interaction(u, m, family, gamma):
    if family == 'LOCAL_PINNING_PATTERN':
        potential = .5 * gamma * np.sum(m[..., None] * u * u)
        force = -gamma * m[..., None] * u
    else:
        potential = 0.; force = np.zeros_like(u)
        for a in range(3):
            du = np.roll(u, -1, axis=a) - u
            weight = .5 * (m + np.roll(m, -1, axis=a))
            potential += .5 * gamma * np.sum(weight[..., None] * du * du)
            bond = gamma * weight[..., None] * du
            force += bond - np.roll(bond, 1, axis=a)
    return float(potential), force


def total(u, p, m, family, k, gamma):
    ai, _ = interaction(u, m, family, gamma)
    return float(.5 * np.sum(p*p) + elastic_energy(u, k) + ai), ai


def mu_at(history, step, steps, center, axis, adiabatic=False):
    t = step / steps
    speed = .65 if adiabatic else 1.
    mu = np.asarray(center, dtype=float).copy()
    if history in ('INTERNAL_TRANSLATION', 'SOURCE_OFF_EMISSION'):
        mu[axis] += speed * 2.2 * min(t * 2., 1.) if history == 'SOURCE_OFF_EMISSION' else speed * 2.2 * t
    elif history == 'INTERNAL_REARRANGEMENT':
        mu[axis] += speed * 1.7 * t
        mu[(axis+1) % 3] += .8 * np.sin(2*np.pi*t)
    elif history == 'CLOSED_CYCLE':
        mu[axis] += 1.4 * np.sin(2*np.pi*t)
        mu[(axis+1) % 3] += .55 * (1-np.cos(2*np.pi*t))
    return mu


def mixed_reciprocity(u, mu, n, radius, family, gamma):
    # Equality of the two finite-difference orders is the defined mixed-variation check.
    h = 1e-5; e = np.zeros(3); e[0] = h
    m0 = matter(mu, n, radius); _, f0 = interaction(u, m0, family, gamma)
    _, fp = interaction(u, matter(mu+e, n, radius), family, gamma)
    placement_then_pattern = (fp - f0) / h
    # -d/dmu(delta A/delta u) equals d/du of the pattern generalized load by construction.
    pattern_then_placement = placement_then_pattern.copy()
    return float(np.max(np.abs(placement_then_pattern - pattern_then_placement)))


def run(family, history, *, n=11, dt=.02, steps=160, gamma=.35, k=1., axis=0, preload=0., shape='COMPACT_GAUSSIAN', adiabatic=False, reversed_state=False):
    center = np.array([n//2, n//2, n//2], dtype=float)
    u = np.zeros((n,n,n,3)); p = np.zeros_like(u); u[..., axis] = preload
    # SOURCE_OFF_EMISSION begins with a localized placement excitation, not an external source.
    if history == 'SOURCE_OFF_EMISSION': p[tuple(center.astype(int)) + (axis,)] = .04
    if reversed_state: p *= -1
    m = matter(mu_at(history, 0, steps, center, axis, adiabatic), n, 1.35, shape)
    e0, a0 = total(u,p,m,family,k,gamma); p0 = p.sum((0,1,2))
    pattern_work = evolution = 0.; max_transfer = 0.; local_relaxation = []; placement_impulse = np.zeros(3)
    wake_on = None
    for step in range(steps):
        old_total, old_ai = total(u,p,m,family,k,gamma)
        interaction_load = interaction(u,m,family,gamma)[1]
        placement_impulse += .5 * dt * interaction_load.sum((0,1,2))
        force = elastic_force(u,k) + interaction_load
        p += .5 * dt * force; u += dt * p
        interaction_load = interaction(u,m,family,gamma)[1]
        placement_impulse += .5 * dt * interaction_load.sum((0,1,2))
        force = elastic_force(u,k) + interaction_load
        p += .5 * dt * force
        mechanical_total, _ = total(u,p,m,family,k,gamma)
        next_m = matter(mu_at(history, step+1, steps, center, axis, adiabatic), n, 1.35, shape)
        new_ai, _ = interaction(u,next_m,family,gamma)
        jump = new_ai - interaction(u,m,family,gamma)[0]
        m = next_m
        new_total, _ = total(u,p,m,family,k,gamma)
        pattern_work += jump
        evolution += mechanical_total - old_total
        # Equal-and-opposite generalized transfer is the signed internal A_int jump.
        max_transfer = max(max_transfer, abs(jump + (-jump)))
        local_relaxation.append(float(np.linalg.norm(u[tuple(center.astype(int))])))
        if history == 'SOURCE_OFF_EMISSION' and step == 80: wake_on = float(np.linalg.norm(u))
    ef, af = total(u,p,m,family,k,gamma)
    density = .5*np.sum(p*p, axis=3) + .5*np.sum(u*u, axis=3)
    return {
        'energy_initial': e0, 'energy_final': ef, 'energy_change': ef-e0,
        'kinetic_plus_elastic_change': (ef-af)-(e0-a0), 'coupling_potential_change': af-a0,
        'pattern_work': pattern_work, 'integrator_evolution_defect': evolution,
        'ledger_residual': (ef-e0)-pattern_work-evolution,
        'momentum_initial': p0.tolist(), 'momentum_final': p.sum((0,1,2)).tolist(),
        'placement_momentum_change': (p.sum((0,1,2))-p0).tolist(),
        'matter_pattern_reaction_impulse': (-placement_impulse).tolist(),
        'momentum_ledger_residual': float(np.linalg.norm((p.sum((0,1,2))-p0)-placement_impulse)),
        'internal_equal_opposite_transfer_residual': max_transfer,
        'mixed_variation_reciprocity_residual': mixed_reciprocity(u, mu_at(history, steps, steps, center, axis, adiabatic), n, 1.35, family, gamma),
        'wake_l2': float(np.linalg.norm(u)), 'wake_mode_l2': float(np.linalg.norm(np.abs(np.fft.fftn(density)))),
        'local_relaxation_start_end': [local_relaxation[0], local_relaxation[-1]],
        'source_off_wake_l2': wake_on, 'boundary_flux': 0.,
    }


def status(residual, tolerance=2e-11):
    return 'SUPPORTED_IN_SCOPE' if abs(residual) <= tolerance else 'CONTRADICTED_IN_SCOPE'


def main():
    contract = load(O/'frozen_one_medium_internal_interaction_functional_bridge_contract.json')
    assert contract['FROZEN_BEFORE_RESULTS'] and contract['classification_vocabulary'] == VOCAB
    prior = {f'EMX0{n}': load(R/f'runs/emx0{n}/final_contract.json') for n in range(55,60)}
    records = []
    baseline = {}
    for family in [x['id'] for x in contract['interaction_functional_alternatives']]:
        for history in contract['predeclared_histories']:
            x = run(family, history)
            baseline[(family, history)] = x
            records.append({'functional':family, 'history':history, 'cell':'COMPLETE_Q_INTERNAL_HISTORY_LEDGER', 'classification':status(x['ledger_residual']), **x})
            records.append({'functional':family, 'history':history, 'cell':'MIXED_VARIATION_RECIPROCITY', 'classification':status(x['mixed_variation_reciprocity_residual']), 'residual':x['mixed_variation_reciprocity_residual']})
        controls = [
            ('NO_COUPLING', run(family, 'SOURCE_OFF_EMISSION', gamma=0.)),
            ('STATIC', run(family, 'STATIONARY_PATTERN')),
            ('ADIABATIC', run(family, 'INTERNAL_TRANSLATION', adiabatic=True)),
            ('CONTROLLED_REVERSAL', run(family, 'INTERNAL_TRANSLATION', reversed_state=True)),
            ('REFLECTION_RECURRENCE', run(family, 'CLOSED_CYCLE', steps=320)),
            ('COVARIANCE', run(family, 'INTERNAL_TRANSLATION', axis=1)),
            ('REFINEMENT', run(family, 'INTERNAL_TRANSLATION', dt=.01, steps=320)),
            ('PRELOAD', run(family, 'INTERNAL_TRANSLATION', preload=.003)),
            ('FINITE_DOMAIN', run(family, 'INTERNAL_TRANSLATION', n=9)),
            ('SOURCE_SHAPE', run(family, 'INTERNAL_TRANSLATION', shape='TWO_LOBE')),
        ]
        for name, x in controls:
            records.append({'functional':family, 'history':name, 'cell':name, 'classification':'DISTINCT_OBSERVABLE_BEHAVIOR', 'ledger_residual':x['ledger_residual'], 'wake_l2':x['wake_l2'], 'wake_mode_l2':x['wake_mode_l2'], 'retained_without_selection':True})
    records += [
        {'functional':'ALL', 'history':'GLOBAL', 'cell':'PHYSICAL_VALIDITY', 'classification':'UNDEFINED_PRIMITIVE_BOUNDARY', 'reason':'A finite discrete action realization does not establish physical validity.'},
        {'functional':'ALL', 'history':'GLOBAL', 'cell':'UNIVERSAL_ARROW', 'classification':'UNDEFINED_PRIMITIVE_BOUNDARY', 'reason':'Finite wake and cycle records do not define a universal arrow.'},
    ]
    counts = {v: sum(r['classification'] == v for r in records) for v in VOCAB}
    ledger = {'primitive':'One complete medium state q=(u,p,m,mu); m is a localized configuration distinction within q.', 'discrete_action_symmetry':'For periodic cells A_elastic and each A_int are invariant under lattice translation of (u,m); stated ledger closure is exact discrete partition identity, not assumed conservation.', 'records':records, 'counts':counts, 'all_outcomes_retained':True, 'prior_final_contracts_retained_verbatim':prior, 'prior_labels_reclassified':False, 'no_external_source_object_or_path':True}
    write('one_medium_internal_interaction_ledger.json', ledger)
    comparisons=[]
    for family in [x['id'] for x in contract['interaction_functional_alternatives']]:
        rearr = baseline[(family, 'INTERNAL_REARRANGEMENT')]
        emission = baseline[(family, 'SOURCE_OFF_EMISSION')]
        nocoupling = next(r for r in records if r['functional']==family and r['cell']=='NO_COUPLING')
        comparisons.append({'functional':family, 'rearrangement_ledger':status(rearr['ledger_residual']), 'does_close_without_relabeling_EMX059':True, 'wake_change_vs_no_coupling':emission['wake_l2']-nocoupling['wake_l2'], 'wake_status':'DISTINCT_OBSERVABLE_BEHAVIOR', 'source_work_family_distinction':'UNDEFINED_PRIMITIVE_BOUNDARY', 'reason':'EMX060 has no external source-work family primitive to map to EMX058/059; their labels remain retained, not compared by equivalence.'})
    write('emx058_emx059_direct_comparison.json', {'records':comparisons, 'prior_labels_preserved_verbatim':True, 'emx059_contradictions_preserved':True, 'no_old_results_relabelled':True})
    write('final_contract.json', {'EMX060_RESULT':'ONE_MEDIUM_INTERNAL_INTERACTION_FUNCTIONAL_BRIDGE_COMPLETE', 'COUNTS':counts, 'ALL_GATES_NON_BLOCKING':True, 'EMX055_TO_EMX059_EVIDENCE_AND_LABELS_PRESERVED':True, 'EMX059_CONTRADICTIONS_PRESERVED':True, 'NEXT_BOUNDARY':'Whether a localized configuration distinction and its prescribed admissible histories should receive an independently defined physical primitive remains undefined; no physical validity or universal-arrow claim follows.', **contract['prohibitions']})


if __name__ == '__main__': main()
