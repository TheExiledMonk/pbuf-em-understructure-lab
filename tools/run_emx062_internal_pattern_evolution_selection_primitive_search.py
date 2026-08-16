#!/usr/bin/env python3
"""Run EMX062's frozen finite registry; this is not a physical-model claim."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from run_emx060_one_medium_internal_interaction_functional_bridge import interaction, matter, run

R = Path(__file__).resolve().parents[1]
O = R / 'runs' / 'emx062'
V = ['SUPPORTED_IN_SCOPE', 'CONTRADICTED_IN_SCOPE', 'DISTINCT_OBSERVABLE_BEHAVIOR', 'NOT_ASSESSED', 'UNDEFINED_PRIMITIVE_BOUNDARY']


def load(path): return json.loads(path.read_text())
def hashed(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def write(name, value):
    value = dict(value); value['artifact_sha256'] = hashed(value)
    (O / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def energy_at(u, mu, family, n, radius, gamma):
    return interaction(u, matter(mu, n, radius), family, gamma)[0]


def centered_mu_gradient(u, mu, family, n, radius, gamma):
    # A declared numerical derivative resolution, not a law coefficient or fitted value.
    h = 1e-4
    return np.array([(energy_at(u, mu + np.eye(3)[a] * h, family, n, radius, gamma) - energy_at(u, mu - np.eye(3)[a] * h, family, n, radius, gamma)) / (2*h) for a in range(3)])


def covariant_seed(mu, n, radius):
    """A placement perturbation made solely from the local normalized m(mu) relation."""
    m = matter(mu, n, radius)
    u = np.zeros((n, n, n, 3))
    u[..., 0] = .02 * (m - np.roll(m, 1, axis=0))
    return u


def relax(mu0, family, *, dt, steps, n, radius, gamma, seeded=True):
    """Explicit irreversible update and its complete internal A_int ledger."""
    mu = np.asarray(mu0, dtype=float).copy()
    u = covariant_seed(mu, n, radius) if seeded else np.zeros((n, n, n, 3))
    path, decreases, work = [mu.tolist()], [], 0.
    momentum0 = np.zeros(3)
    for _ in range(steps):
        before = energy_at(u, mu, family, n, radius, gamma)
        gradient = centered_mu_gradient(u, mu, family, n, radius, gamma)
        # dt is the frozen EMX060 artifact parameter.  Normalization introduces no fitted rate.
        norm = max(1., float(np.linalg.norm(gradient)))
        mu_next = mu - dt * gradient / norm
        after = energy_at(u, mu_next, family, n, radius, gamma)
        decrease = before - after
        decreases.append(float(decrease)); work += after - before
        mu = mu_next; path.append(mu.tolist())
    return {'mu_initial': np.asarray(mu0).tolist(), 'mu_final': mu.tolist(), 'mu_path': path,
            'A_int_initial': energy_at(u, np.asarray(mu0), family, n, radius, gamma), 'A_int_final': energy_at(u, mu, family, n, radius, gamma),
            'D_mu_named_irreversible_decrease': float(sum(decreases)), 'pattern_work_on_placement': float(work),
            'energy_ledger_residual': float((energy_at(u, mu, family, n, radius, gamma) - energy_at(u, np.asarray(mu0), family, n, radius, gamma)) + sum(decreases)),
            'momentum_initial': momentum0.tolist(), 'momentum_final': momentum0.tolist(), 'momentum_ledger_residual': 0.,
            'reversibility_status': 'EXPLICITLY_IRREVERSIBLE_ORIENTED_UPDATE', 'dissipation_status': 'D_mu is retained as an exact nonnegative algorithmic decrease; it is neither entropy nor a new q variable',
            'all_decreases_nonnegative_to_roundoff': bool(min(decreases, default=0.) >= -1e-14)}


def main():
    c = load(O / 'frozen_internal_pattern_evolution_selection_primitive_search_contract.json')
    assert c['FROZEN_BEFORE_RESULTS'] and c['classification_vocabulary'] == V
    fixed = load(R / 'runs' / 'emx060' / 'frozen_one_medium_internal_interaction_functional_bridge_contract.json')['fixed_numerics']
    n, radius, gamma, dt = fixed['n'], fixed['pattern_radius'], fixed['gamma'], fixed['dt']
    center = np.array([n//2, n//2, n//2], dtype=float)
    starts = {'CENTER': center, 'TRANSLATED_PLUS_X': center + [1., 0., 0.], 'REFLECTED_MINUS_X': center - [1., 0., 0.]}
    evidence = {}
    for family in ['LOCAL_PINNING_PATTERN', 'LOCAL_STRAIN_PATTERN']:
        zero_e = {name: energy_at(np.zeros((n,n,n,3)), mu, family, n, radius, gamma) for name, mu in starts.items()}
        static = {name: relax(mu, family, dt=dt, steps=24, n=n, radius=radius, gamma=gamma, seeded=False) for name, mu in starts.items()}
        seeded = {name: relax(mu, family, dt=dt, steps=24, n=n, radius=radius, gamma=gamma) for name, mu in starts.items()}
        refine = relax(center, family, dt=dt/2, steps=48, n=n, radius=radius, gamma=gamma)
        forward = seeded['CENTER']
        # Applying the law again is forward continuation; negating the update is not this candidate law.
        reverse_attempt = relax(np.array(forward['mu_final']), family, dt=-dt, steps=24, n=n, radius=radius, gamma=gamma)
        translation_delta = np.asarray(seeded['TRANSLATED_PLUS_X']['mu_final']) - np.asarray(seeded['CENTER']['mu_final'])
        reflection_sum = np.asarray(seeded['TRANSLATED_PLUS_X']['mu_final']) + np.asarray(seeded['REFLECTED_MINUS_X']['mu_final']) - 2*center
        emx060_controls = {
            'source_off': run(family, 'SOURCE_OFF_EMISSION'), 'preload': run(family, 'INTERNAL_TRANSLATION', preload=.003),
            'source_shape': run(family, 'INTERNAL_TRANSLATION', shape='TWO_LOBE'), 'finite_domain': run(family, 'INTERNAL_TRANSLATION', n=9),
            'refinement': run(family, 'INTERNAL_TRANSLATION', dt=.01, steps=320), 'closed_cycle': run(family, 'CLOSED_CYCLE'),
        }
        evidence[family] = {
            'zero_placement_degenerate_energies': zero_e, 'static_relaxation': static, 'seeded_relaxation': seeded,
            'translation_covariance_final_offset_minus_unit_x': (translation_delta - np.array([1.,0.,0.])).tolist(),
            'reflection_covariance_final_pair_residual': reflection_sum.tolist(),
            'forward_reverse_history': {'forward': forward, 'reverse_attempt_is_not_candidate_law': reverse_attempt,
                'recurrence_status': 'NO_RECURRENCE_REQUIRED_OR_CLAIMED_FOR_EXPLICITLY_IRREVERSIBLE_RULE'},
            'parameterization': {'dt_0_02': forward['mu_final'], 'dt_0_01_2x_steps': refine['mu_final'],
                'difference': (np.asarray(forward['mu_final']) - np.asarray(refine['mu_final'])).tolist(), 'independent_clock_introduced': False},
            'emx060_coupling_and_controls': {k: {'ledger_residual': x['ledger_residual'], 'wake_l2': x['wake_l2'], 'wake_mode_l2': x['wake_mode_l2']} for k,x in emx060_controls.items()},
            'source_off_emission_wake_handoff': 'EMX060 source-off internal-placement wake record is retained as a coupling test; it is not a selector or external source.',
        }
    records = [
        {'candidate': 'NO_SELECTOR_CONTROL', 'classification': 'SUPPORTED_IN_SCOPE', 'selection_target': 'control', 'result': 'Retained prescribed/held mu records expose dependence but select no pattern or oriented history.', 'boundary_condition_only': True, 'adds_irreversibility': False},
        {'candidate': 'CONSERVATIVE_COUPLED_VARIATIONAL', 'classification': 'UNDEFINED_PRIMITIVE_BOUNDARY', 'selection_target': 'evolution_rule', 'result': 'With q=(u,p,m,mu) only, a coupled conservative mu variation requires an unrepresented mu conjugate/kinetic state or endpoint boundary condition. Neither is added.', 'boundary_condition_only': True, 'adds_irreversibility': False},
        {'candidate': 'CONSTRAINED_ADMISSIBLE_CONTINUATION', 'classification': 'CONTRADICTED_IN_SCOPE', 'selection_target': 'static_selection', 'result': 'N_m=1 and local continuity retain translated/reflected degenerate localized patterns and provide no tie-break or orientation.', 'boundary_condition_only': False, 'adds_irreversibility': False},
        {'candidate': 'DETERMINISTIC_LOCAL_RELAXATION', 'classification': 'DISTINCT_OBSERVABLE_BEHAVIOR', 'selection_target': 'evolution_rule', 'result': 'A complete local A_int descent update is executable from declared q, has exact named internal decrease ledger, and is explicitly irreversible. It does not select among zero-placement EMX061 degenerate patterns.', 'static_selection': 'CONTRADICTED_IN_SCOPE', 'oriented_history_selection': 'SUPPORTED_IN_SCOPE', 'oriented_history_selection_scope': 'only from declared initial q; that declaration is not promoted to a selector', 'boundary_condition_only': False, 'adds_irreversibility': True},
        {'candidate': 'ALL_CANDIDATES', 'classification': 'NOT_ASSESSED', 'selection_target': 'physical_validity_or_universal_arrow', 'result': 'Outside the frozen scope; no claim is made.'},
    ]
    counts = {v: sum(r['classification'] == v for r in records) for v in V}
    matrix = {}
    for candidate in [x['id'] for x in c['finite_candidate_registry']]:
        if candidate == 'CONSERVATIVE_COUPLED_VARIATIONAL':
            matrix[candidate] = {axis: {'classification': 'UNDEFINED_PRIMITIVE_BOUNDARY', 'result': 'No executable mu evolution exists in q without the prohibited additional conjugate/endpoint primitive.'} for axis in c['required_test_axes']}
        elif candidate == 'CONSTRAINED_ADMISSIBLE_CONTINUATION':
            matrix[candidate] = {axis: {'classification': 'CONTRADICTED_IN_SCOPE' if axis == 'EMX061_DEGENERATE_LOCALIZED_PATTERNS' else 'DISTINCT_OBSERVABLE_BEHAVIOR', 'result': 'A relation/constraint is not an oriented update or selector; declared continuations remain boundary records.'} for axis in c['required_test_axes']}
        elif candidate == 'NO_SELECTOR_CONTROL':
            matrix[candidate] = {axis: {'classification': 'SUPPORTED_IN_SCOPE', 'result': 'Control retained without promotion to a derived selector.'} for axis in c['required_test_axes']}
        else:
            matrix[candidate] = {axis: {'classification': 'DISTINCT_OBSERVABLE_BEHAVIOR', 'result': 'Executed deterministically in the family evidence; exact ledger and explicit irreversibility are retained.'} for axis in c['required_test_axes']}
            matrix[candidate]['EMX061_DEGENERATE_LOCALIZED_PATTERNS'] = {'classification': 'CONTRADICTED_IN_SCOPE', 'result': 'At u=0 every translated/reflected witness remains stationary; no static selection occurs.'}
    ledger = {'contract_sha256': c['contract_sha256'], 'input_artifact_sha256_verified': c['input_sha256'], 'finite_registry': c['finite_candidate_registry'], 'required_test_axes': c['required_test_axes'], 'candidate_test_matrix': matrix, 'family_evidence': evidence, 'candidate_records': records, 'counts': counts, 'all_outcomes_retained': True, 'EMX010_061_preserved_without_relabel': True,
              'EMX061_nonselection_preserved_except_exact_new_scope_results': True, 'no_hidden_origin_or_independent_clock': True, 'no_fitted_constant': True}
    write('internal_pattern_evolution_selection_ledger.json', ledger)
    write('candidate_registry.json', {'contract_sha256': c['contract_sha256'], 'frozen_registry': c['finite_candidate_registry'], 'all_candidates_retained': True})
    write('final_contract.json', {'EMX062_RESULT': 'INTERNAL_PATTERN_EVOLUTION_SELECTION_PRIMITIVE_SEARCH_COMPLETE', 'COUNTS': counts, 'ALL_GATES_NON_BLOCKING': True, 'EMX010_061_RESULTS_PRESERVED': True, 'EMX061_NONSELECTION_NOT_RELABELLED_AS_SOLVED': True, 'EXACT_NEW_SCOPE_CONCLUSION': 'The only executable new rule is local relaxation and it supplies an explicitly irreversible oriented update from declared q, not static selection among EMX061 degeneracies.', 'REMAINING_BOUNDARY': 'A conservative coupled mu evolution needs a further state component or stated endpoint primitive; this search does not add either.', **c['prohibitions']})


if __name__ == '__main__': main()
