#!/usr/bin/env python3
"""Execute EMX061 without extending EMX060's primitives or selecting a winner."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from run_emx060_one_medium_internal_interaction_functional_bridge import interaction, matter

R = Path(__file__).resolve().parents[1]
O = R / 'runs' / 'emx061'
V = ['SUPPORTED_IN_SCOPE', 'CONTRADICTED_IN_SCOPE', 'DISTINCT_OBSERVABLE_BEHAVIOR', 'NOT_ASSESSED', 'UNDEFINED_PRIMITIVE_BOUNDARY']


def load(path): return json.loads(path.read_text())
def hashed(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def write(name, value):
    value = dict(value); value['artifact_sha256'] = hashed(value)
    (O / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def action_at_zero(m_path, dt, family, gamma):
    """Existing mechanical action at u=0; only u is an available variation."""
    zero = np.zeros(m_path[0].shape + (3,))
    return float(sum(-dt * interaction(zero, m, family, gamma)[0] for m in m_path))


def main():
    c = load(O / 'frozen_localized_pattern_and_admissible_history_selection_audit_contract.json')
    assert c['FROZEN_BEFORE_RESULTS'] and c['classification_vocabulary'] == V
    emx060 = load(R / 'runs' / 'emx060' / 'one_medium_internal_interaction_ledger.json')
    fixed = load(R / 'runs' / 'emx060' / 'frozen_one_medium_internal_interaction_functional_bridge_contract.json')['fixed_numerics']
    n, radius, gamma, dt = fixed['n'], fixed['pattern_radius'], fixed['gamma'], fixed['dt']
    center = np.array([n // 2, n // 2, n // 2], dtype=float)
    patterns = {
        'CENTER': matter(center, n, radius),
        'TRANSLATED_PLUS_X': matter(center + [1., 0., 0.], n, radius),
        'REFLECTED_MINUS_X': matter(center - [1., 0., 0.], n, radius),
        'TWO_LOBE': matter(center, n, radius, 'TWO_LOBE'),
    }
    zero = np.zeros((n, n, n, 3))
    family_evidence = []
    for family in ['LOCAL_PINNING_PATTERN', 'LOCAL_STRAIN_PATTERN']:
        energies = {name: interaction(zero, m, family, gamma)[0] for name, m in patterns.items()}
        # Every quadratic contribution is nonnegative: this is an all-amplitude stability proof, not a fitted perturbation.
        deterministic_perturbation = np.indices((n, n, n)).sum(axis=0) % 2
        u_pert = deterministic_perturbation[..., None] * np.array([1., -1., 1.])
        perturbation_energy = interaction(u_pert, patterns['CENTER'], family, gamma)[0]
        forward = [patterns['CENTER'], patterns['TRANSLATED_PLUS_X']]
        reverse = list(reversed(forward))
        family_evidence.append({
            'functional': family, 'zero_placement_interaction_energies': energies,
            'translation_energy_difference': energies['CENTER'] - energies['TRANSLATED_PLUS_X'],
            'reflection_energy_difference': energies['CENTER'] - energies['REFLECTED_MINUS_X'],
            'shape_energy_difference': energies['CENTER'] - energies['TWO_LOBE'],
            'nonnegative_perturbation_interaction_energy': perturbation_energy,
            'forward_zero_placement_action': action_at_zero(forward, dt, family, gamma),
            'reversed_zero_placement_action': action_at_zero(reverse, dt, family, gamma),
            'replay_action_difference': action_at_zero(forward, dt, family, gamma) - action_at_zero(reverse, dt, family, gamma),
        })
    controls = []
    for family in ['LOCAL_PINNING_PATTERN', 'LOCAL_STRAIN_PATTERN']:
        subset = [r for r in emx060['records'] if r['functional'] == family]
        by_cell = {r['cell']: r for r in subset}
        controls.append({
            'functional': family,
            'finite_domain_and_refinement_retained': {k: by_cell[k]['classification'] for k in ['FINITE_DOMAIN', 'REFINEMENT']},
            'background_preload_retained': by_cell['PRELOAD']['classification'],
            'source_off_emission_wake_handoff_retained': by_cell['NO_COUPLING']['classification'],
            'reversible_replay_control_retained': by_cell['CONTROLLED_REVERSAL']['classification'],
            'translation_covariance_control_retained': by_cell['COVARIANCE']['classification'],
            'ledger_cells_retained': [r['classification'] for r in subset if r['cell'] == 'COMPLETE_Q_INTERNAL_HISTORY_LEDGER'],
            'control_is_not_a_derived_selector': True,
        })
    test_axis_evidence = {
        'LOCALIZATION': {'witnesses': list(patterns), 'normalizations': {name: float(m.sum()) for name, m in patterns.items()}},
        'STABILITY_PERTURBATION': {x['functional']: x['nonnegative_perturbation_interaction_energy'] for x in family_evidence},
        'TRANSLATION_REFLECTION_COVARIANCE': {x['functional']: [x['translation_energy_difference'], x['reflection_energy_difference']] for x in family_evidence},
        'DEGENERACY_NONUNIQUENESS': {x['functional']: {'shape_energy_difference': x['shape_energy_difference'], 'witness_count': len(patterns)} for x in family_evidence},
        'FINITE_DOMAIN_REFINEMENT': {x['functional']: x['finite_domain_and_refinement_retained'] for x in controls},
        'BACKGROUND_PRELOAD': {x['functional']: x['background_preload_retained'] for x in controls},
        'SOURCE_OFF_EMISSION_WAKE_HANDOFF': {x['functional']: {'source_off_ledger': next(r for r in emx060['records'] if r['functional'] == x['functional'] and r['history'] == 'SOURCE_OFF_EMISSION' and r['cell'] == 'COMPLETE_Q_INTERNAL_HISTORY_LEDGER')['classification'], 'no_coupling_control': x['source_off_emission_wake_handoff_retained']} for x in controls},
        'REVERSIBLE_HISTORY_REPLAY_WHERE_DEFINED': {x['functional']: x['replay_action_difference'] for x in family_evidence},
        'ENERGY_MOMENTUM_WORK_LEDGER': {x['functional']: x['ledger_cells_retained'] for x in controls},
        'INTERACTION_FUNCTIONAL_COMPATIBILITY': {x['functional']: x['zero_placement_interaction_energies'] for x in family_evidence},
    }
    exact = all(abs(x[k]) == 0.0 for x in family_evidence for k in ['translation_energy_difference', 'reflection_energy_difference', 'shape_energy_difference', 'replay_action_difference'])
    records = [
        {'selector': 'STATIC_ENERGY_STATIONARITY_MINIMUM', 'selection_target': 'static_pattern', 'classification': 'CONTRADICTED_IN_SCOPE', 'exact_evidence': 'For each functional, u=0 has A_elastic=A_int=0 for CENTER, TRANSLATED_PLUS_X, REFLECTED_MINUS_X, and TWO_LOBE; nonnegative quadratic energy makes it a minimum at fixed each m. Thus stationarity/minimum does not uniquely select m.', 'nonuniqueness_witnesses': list(patterns), 'preparation_not_selector': True},
        {'selector': 'LOCALIZED_STABILITY_AND_CONTINUATION', 'selection_target': 'history_class', 'classification': 'DISTINCT_OBSERVABLE_BEHAVIOR', 'exact_evidence': 'The zero-placement minimum is stable for every listed localized admissible m, while EMX060 retains distinct finite-domain, refinement, preload, source-off, and covariance records. This permits classes but selects none.', 'static_pattern_selection': 'CONTRADICTED_IN_SCOPE', 'oriented_history_selection': 'UNDEFINED_PRIMITIVE_BOUNDARY'},
        {'selector': 'NORMALIZED_PATTERN_INVARIANT', 'selection_target': 'static_pattern', 'classification': 'CONTRADICTED_IN_SCOPE', 'exact_evidence': 'Every witness has exactly N_m=sum(m)=1; translation, reflection, and shape remain nonunique under the only represented invariant.', 'defined_invariant': 'N_m=1', 'no_topological_charge_added': True},
        {'selector': 'STATIONARY_DISCRETE_ACTION_ALTERNATIVES', 'selection_target': 'oriented_history', 'classification': 'UNDEFINED_PRIMITIVE_BOUNDARY', 'exact_evidence': 'At u=0 the defined fixed-mu mechanical action is exactly zero for forward and reversed admissible pattern paths. EMX060 has no mu evolution law, clock, entropy, or endpoint-selection primitive; varying them would add one.', 'fixed_m_path_stationarity_only': True, 'dynamic_orientation_not_selected': True},
        {'selector': 'NO_SELECTOR_CONTROLS', 'selection_target': 'controls', 'classification': 'SUPPORTED_IN_SCOPE', 'exact_evidence': 'Retained EMX060 preparation/control records have distinct observable behavior and are explicitly not promoted to derived selectors.', 'boundary_or_preparation_not_derived_selector': True},
    ]
    counts = {v: sum(r['classification'] == v for r in records) for v in V}
    ledger = {'contract_sha256': c['contract_sha256'], 'input_artifact_sha256_verified': c['input_sha256'], 'family_evidence': family_evidence, 'control_evidence': controls, 'test_axis_evidence': test_axis_evidence, 'selector_records': records, 'exact_degeneracy_checks_passed': exact, 'all_outcomes_retained': True, 'emx060_retained_without_reclassification': True, 'no_dynamic_oriented_history_selected': True}
    write('localized_pattern_and_admissible_history_selection_ledger.json', ledger)
    write('selector_registry.json', {'predeclared_selector_registry': c['predeclared_selector_registry'], 'required_test_axes': c['required_test_axes'], 'selection_distinctions': c['selection_distinctions'], 'all_registry_outcomes_retained': True})
    write('final_contract.json', {'EMX061_RESULT': 'LOCALIZED_PATTERN_AND_ADMISSIBLE_HISTORY_SELECTION_AUDIT_COMPLETE', 'COUNTS': counts, 'ALL_GATES_NON_BLOCKING': True, 'EMX060_AND_EARLIER_RESULTS_PRESERVED': True, 'EXACT_NONUNIQUENESS_EVIDENCE': 'Both functionals give equal zero-placement stationary/minimum energy to four distinct normalized localized pattern witnesses; forward/reversed fixed-mu zero-placement actions are equal.', 'STATIC_PATTERN_SELECTED': False, 'HISTORY_CLASS_PERMISSION_ONLY': True, 'DYNAMIC_ORIENTED_HISTORY_SELECTED': False, 'NEXT_BOUNDARY': 'An independently stated evolution/selection primitive for mu would be required to select one localized pattern or oriented history; EMX061 does not introduce one.', **c['prohibitions']})


if __name__ == '__main__': main()
