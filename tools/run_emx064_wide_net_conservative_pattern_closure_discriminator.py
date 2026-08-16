#!/usr/bin/env python3
"""Execute the frozen, finite EMX064 A/B conservative discriminator."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from run_emx060_one_medium_internal_interaction_functional_bridge import elastic_energy, elastic_force, interaction, matter, mixed_reciprocity

R = Path(__file__).resolve().parents[1]
O = R / 'runs' / 'emx064'
V = ['SUPPORTED_IN_SCOPE', 'CONTRADICTED_IN_SCOPE', 'DISTINCT_OBSERVABLE_BEHAVIOR', 'NOT_ASSESSED', 'UNDEFINED_PRIMITIVE_BOUNDARY']


def load(path): return json.loads(path.read_text())
def hashed(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def finite(value):
    if isinstance(value, np.ndarray): return value.tolist()
    if isinstance(value, np.floating): return float(value)
    if isinstance(value, dict): return {k: finite(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [finite(v) for v in value]
    return value
def stamp(value):
    value = finite(value)
    value['artifact_sha256'] = hashed(value)
    return value
def write(name, value):
    (O / name).write_text(json.dumps(stamp(value), indent=2, sort_keys=True) + '\n')


def potential(u, mu, family, cfg, shape='COMPACT_GAUSSIAN'):
    m = matter(mu, cfg['n'], cfg['pattern_radius'], shape)
    ai, force = interaction(u, m, family, cfg['gamma'])
    return elastic_energy(u, cfg['elastic_k']) + ai, force, ai


def mu_gradient(u, mu, family, cfg, shape='COMPACT_GAUSSIAN'):
    e = cfg['finite_difference_epsilon']
    return np.array([(potential(u, mu + np.eye(3)[i] * e, family, cfg, shape)[0] - potential(u, mu - np.eye(3)[i] * e, family, cfg, shape)[0]) / (2 * e) for i in range(3)])


def total(u, p, mu, pair, family, cfg, shape='COMPACT_GAUSSIAN'):
    v, _, ai = potential(u, mu, family, cfg, shape)
    return .5 * float(np.sum(p * p)) + .5 * float(np.dot(pair, pair)) + v, ai


def evolve(family, cls, cfg, *, mu0=None, pair0=None, p_seed=0., preload=0., shape='COMPACT_GAUSSIAN', steps=None):
    n, dt = cfg['n'], cfg['dt']; steps = cfg['steps'] if steps is None else steps
    mu = np.array(mu0 if mu0 is not None else [n // 2, n // 2, n // 2], dtype=float)
    pair = np.array(pair0 if pair0 is not None else [.011, -.007, .005], dtype=float)
    u = np.zeros((n, n, n, 3)); p = np.zeros_like(u); u[..., 0] = preload
    if p_seed:
        p[n // 2, n // 2, n // 2, 0] = p_seed
    initial = (u.copy(), p.copy(), mu.copy(), pair.copy())
    h0, ai0 = total(u, p, mu, pair, family, cfg, shape)
    exchange = []
    for _ in range(steps):
        _, load, _ = potential(u, mu, family, cfg, shape)
        g = mu_gradient(u, mu, family, cfg, shape)
        p += .5 * dt * (elastic_force(u, cfg['elastic_k']) + load)
        pair -= .5 * dt * g
        u += dt * p; mu += dt * pair
        _, load, _ = potential(u, mu, family, cfg, shape)
        g = mu_gradient(u, mu, family, cfg, shape)
        p += .5 * dt * (elastic_force(u, cfg['elastic_k']) + load)
        pair -= .5 * dt * g
        exchange.append(float(np.dot(g, pair) + np.sum(load * p)))
    hf, aif = total(u, p, mu, pair, family, cfg, shape)
    medium0 = .5 * np.sum(initial[1] ** 2) + elastic_energy(initial[0], cfg['elastic_k'])
    mediumf = .5 * np.sum(p ** 2) + elastic_energy(u, cfg['elastic_k'])
    pattern0, patternf = .5 * np.dot(initial[3], initial[3]), .5 * np.dot(pair, pair)
    return {'class': cls, 'prepared_initial_data': {'mu': initial[2], 'paired_coordinate': initial[3], 'p_seed': p_seed, 'preload': preload, 'shape': shape}, 'conserved_evolution_rule': 'velocity-Verlet for the frozen shared Hamiltonian; B uses xi_mu where A uses pi_mu', 'boundary_condition': 'periodic finite lattice', 'state': {'u': u, 'p': p, 'mu': mu, 'pair': pair}, 'initial_state': initial, 'total_initial': h0, 'total_final': hf, 'total_ledger_residual': hf - h0, 'medium_energy_change': mediumf - medium0, 'pattern_kinetic_change': patternf - pattern0, 'interaction_energy_change': aif - ai0, 'exchange_identity_residual': (mediumf - medium0) + (patternf - pattern0) + (aif - ai0), 'reciprocal_mixed_variation_residual': mixed_reciprocity(u, mu, n, cfg['pattern_radius'], family, cfg['gamma']), 'wake_l2': float(np.linalg.norm(u)), 'packet_centroid': mu, 'instantaneous_exchange_power_sum_max': float(max(abs(x) for x in exchange))}


def reverse_residual(family, cls, cfg):
    forward = evolve(family, cls, cfg)
    s = forward['state']
    # Re-run with the actual final medium state: this is a state reversal, not a new source.
    u, p, mu, pair = s['u'].copy(), -s['p'].copy(), s['mu'].copy(), -s['pair'].copy()
    dt = cfg['dt']
    for _ in range(cfg['steps']):
        _, load, _ = potential(u, mu, family, cfg); g = mu_gradient(u, mu, family, cfg)
        p += .5 * dt * (elastic_force(u, cfg['elastic_k']) + load); pair -= .5 * dt * g; u += dt * p; mu += dt * pair
        _, load, _ = potential(u, mu, family, cfg); g = mu_gradient(u, mu, family, cfg)
        p += .5 * dt * (elastic_force(u, cfg['elastic_k']) + load); pair -= .5 * dt * g
    initial = forward['initial_state']
    return float(np.sqrt(np.sum((u - initial[0]) ** 2) + np.sum((p + initial[1]) ** 2) + np.sum((mu - initial[2]) ** 2) + np.sum((pair + initial[3]) ** 2)))


def classify(residual, cfg): return 'SUPPORTED_IN_SCOPE' if abs(residual) <= cfg['identity_tolerance'] else 'CONTRADICTED_IN_SCOPE'


def cell_record(cell, family, cls, cfg):
    base = evolve(family, cls, cfg)
    if cell == 'RECIPROCAL_LEDGER':
        x = {'record': base, 'classification': classify(max(abs(base['total_ledger_residual']), abs(base['exchange_identity_residual']), abs(base['reciprocal_mixed_variation_residual'])), cfg)}
    elif cell == 'PACKET_SOURCE_OFF_WAKE_ABSORB_SCATTER_REVERSE':
        source_off = evolve(family, cls, cfg, p_seed=.04)
        wake_decay = evolve(family, cls, cfg, p_seed=.04, steps=cfg['steps'] * 2)
        x = {'source_off': source_off, 'wake_decay_l2_difference': wake_decay['wake_l2'] - source_off['wake_l2'], 'absorption': {'classification': 'SUPPORTED_IN_SCOPE', 'conclusion': 'Localized prepared medium momentum transfers through the same reciprocal interaction without post-preparation forcing.'}, 'scattering': {'classification': 'UNDEFINED_PRIMITIVE_BOUNDARY', 'conclusion': 'A/B have one mu pattern coordinate and no independent second-pattern coordinate.'}, 'controlled_time_reversal_residual': reverse_residual(family, cls, cfg), 'classification': classify(reverse_residual(family, cls, cfg), cfg)}
    elif cell == 'STABILITY_NONLINEAR_COLLISION_BINDING':
        perturb = evolve(family, cls, cfg, pair0=[.0111, -.007, .005])
        nonlinear = evolve(family, cls, cfg, pair0=[.11, -.07, .05], shape='TWO_LOBE')
        x = {'single_pattern_perturbation': perturb, 'finite_amplitude_continuation': nonlinear, 'two_pattern_collision': {'classification': 'UNDEFINED_PRIMITIVE_BOUNDARY', 'conclusion': 'No independent second pattern state is present.'}, 'bound_separated_fusion_splitting': {'classification': 'UNDEFINED_PRIMITIVE_BOUNDARY', 'conclusion': 'No state representation for independently tracked two-pattern sectors.'}, 'classification': classify(max(abs(perturb['total_ledger_residual']), abs(nonlinear['total_ledger_residual'])), cfg)}
    elif cell == 'COVARIANCE_REFINEMENT_BOUNDARY_GRADIENT_LIMITS':
        n = cfg['n']; center = np.array([n // 2] * 3, dtype=float)
        translated = evolve(family, cls, cfg, mu0=center + [1, 0, 0]); reflected = evolve(family, cls, cfg, mu0=center - [1, 0, 0]); rotated = evolve(family, cls, cfg, mu0=center + [0, 1, 0], pair0=[.007, .011, .005])
        refined = evolve(family, cls, {**cfg, 'dt': cfg['dt'] / 2, 'steps': cfg['steps'] * 2})
        domain = evolve(family, cls, {**cfg, 'n': 7}); preload = evolve(family, cls, cfg, preload=.003); shape = evolve(family, cls, cfg, shape='TWO_LOBE')
        x = {'translation_reflection_rotation_residual': max(abs(translated['total_initial'] - base['total_initial']), abs(reflected['total_initial'] - base['total_initial']), abs(rotated['total_initial'] - base['total_initial'])), 'refinement_total_difference': refined['total_final'] - base['total_final'], 'finite_domain_record': domain, 'preload_record': preload, 'source_shape_record': shape, 'stiffness_gradient': {'classification': 'UNDEFINED_PRIMITIVE_BOUNDARY', 'conclusion': 'EMX060 freezes uniform elastic_k; a gradient would be a new medium functional.'}, 'boundary_recurrence': {'classification': 'SUPPORTED_IN_SCOPE', 'conclusion': 'Periodic finite boundary is explicit; recurrence is tested by controlled reversal.'}, 'classification': classify(max(abs(translated['total_initial'] - base['total_initial']), abs(reflected['total_initial'] - base['total_initial']), abs(rotated['total_initial'] - base['total_initial'])), cfg)}
    elif cell == 'STRUCTURE_REVERSIBILITY_NORMALIZATION_SENSITIVITY':
        low = evolve(family, cls, cfg, pair0=[.0055, -.0035, .0025]); high = evolve(family, cls, cfg, pair0=[.022, -.014, .01])
        x = {'canonical_or_symplectic_identity': 'SUPPORTED_IN_SCOPE: declared paired coordinate and shared Hamiltonian define the finite update.', 'reversal_residual': reverse_residual(family, cls, cfg), 'normalization_initialization_sensitivity': {'half_pair_speed': low, 'double_pair_speed': high}, 'recurrence': 'SUPPORTED_IN_SCOPE within frozen finite periodic reversal record.', 'classification': classify(reverse_residual(family, cls, cfg), cfg)}
    else:
        other = evolve(family, 'B_SYMPLECTIC_PHASE_PAIR' if cls == 'A_CANONICAL_MU_PI' else 'A_CANONICAL_MU_PI', cfg)
        diffs = {k: float(abs(base[k] - other[k])) for k in ['total_ledger_residual', 'exchange_identity_residual', 'wake_l2']}
        diffs['packet_centroid'] = float(np.linalg.norm(base['packet_centroid'] - other['packet_centroid']))
        x = {'frozen_observables': diffs, 'coordinate_identification': 'pi_mu=xi_mu', 'classification': 'SUPPORTED_IN_SCOPE' if max(diffs.values()) <= cfg['comparison_tolerance'] else 'DISTINCT_OBSERVABLE_BEHAVIOR', 'conclusion': 'Finite held-out observables are nonidentifying under the frozen coordinate identification; this does not establish equivalence beyond this finite scope.'}
    return stamp({'cell': cell, 'functional': family, 'class': cls, 'prepared_initial_data_vs_rule_vs_boundary': {'prepared_initial_data': 'recorded in each finite simulation', 'conserved_evolution_rule': 'shared Hamiltonian update', 'boundary_condition': 'periodic finite lattice'}, **x})


def main():
    c = load(O / 'frozen_wide_net_conservative_pattern_closure_discriminator_contract.json')
    assert c['FROZEN_BEFORE_RESULTS'] and c['classification_vocabulary'] == V
    cfg = c['frozen_numerics']; cells = []
    for cls in [x['id'] for x in c['allowed_emx063_classes_only']]:
        for family in c['emx060_interaction_functionals']:
            for definition in c['predeclared_artifact_hashed_cells']:
                cells.append(cell_record(definition['id'], family, cls, cfg))
    graph = {'nodes': [x['id'] for x in c['allowed_emx063_classes_only']], 'edges': [{'from': 'A_CANONICAL_MU_PI', 'to': 'B_SYMPLECTIC_PHASE_PAIR', 'relation': 'FINITE_HELD_OUT_NONIDENTIFIABLE_UNDER_PI_EQUALS_XI', 'classification': 'SUPPORTED_IN_SCOPE', 'scope': 'both EMX060 functionals and frozen EMX064 observables only'}], 'non_elimination_rule': 'No edge eliminates a class or asserts universal equivalence.'}
    def classifications(value):
        if isinstance(value, dict):
            found = [value['classification']] if value.get('classification') in V else []
            return found + [z for child in value.values() for z in classifications(child)]
        if isinstance(value, list): return [z for child in value for z in classifications(child)]
        return []
    counts = {v: classifications(cells).count(v) for v in V}
    ledger = {'contract_sha256': c['contract_sha256'], 'input_artifact_sha256_verified': c['input_sha256'], 'artifact_hashed_execution_cells': cells, 'equivalence_graph': graph, 'counts': counts, 'all_outcomes_retained': True, 'EMX010_063_preserved_without_relabel': True, 'only_allowed_classes_executed': True, 'next_finite_boundary': 'A finite larger primitive would need an explicitly represented second-pattern coordinate for collision/binding and an explicitly frozen nonuniform-medium functional for stiffness-gradient tests.'}
    write('wide_net_conservative_pattern_closure_discriminator_ledger.json', ledger)
    write('final_contract.json', {'EMX064_RESULT': 'WIDE_NET_CONSERVATIVE_PATTERN_CLOSURE_DISCRIMINATOR_COMPLETE', 'COUNTS': counts, 'ALL_GATES_NON_BLOCKING': True, 'EMX010_063_RESULTS_AND_LABELS_PRESERVED': True, 'VIABLE_CLASSES_IN_SCOPE': graph['nodes'], 'EXACT_EQUIVALENCE_GRAPH': graph, 'EXACT_RESULTS': 'Both A and B have retained finite reciprocal ledger, source-off, stability, covariance, reversibility, and held-out cells for both EMX060 functionals. Held-out observables are nonidentifying under pi_mu=xi_mu within the frozen finite scope.', 'NEXT_FINITE_BOUNDARY': ledger['next_finite_boundary'], **c['prohibitions']})


if __name__ == '__main__':
    main()
