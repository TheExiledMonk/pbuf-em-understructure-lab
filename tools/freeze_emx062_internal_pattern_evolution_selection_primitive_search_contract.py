#!/usr/bin/env python3
"""Freeze EMX062's finite internal-pattern primitive registry before results."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
O = R / 'runs' / 'emx062'


def digest(path): return hashlib.sha256((R / path).read_bytes()).hexdigest()
def canonical(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def main():
    inputs = [
        'runs/emx061/final_contract.json',
        'runs/emx061/frozen_localized_pattern_and_admissible_history_selection_audit_contract.json',
        'runs/emx061/localized_pattern_and_admissible_history_selection_ledger.json',
        'runs/emx060/frozen_one_medium_internal_interaction_functional_bridge_contract.json',
        'runs/emx060/one_medium_internal_interaction_ledger.json',
    ]
    contract = {
        'EMX062_SELECTOR': 'INTERNAL_PATTERN_EVOLUTION_SELECTION_PRIMITIVE_SEARCH',
        'FROZEN_BEFORE_RESULTS': True,
        'mode': 'FINITE_DETERMINISTIC_REPO_LOCAL_NON_BLOCKING_PRIMITIVE_SEARCH',
        'classification_vocabulary': ['SUPPORTED_IN_SCOPE', 'CONTRADICTED_IN_SCOPE', 'DISTINCT_OBSERVABLE_BEHAVIOR', 'NOT_ASSESSED', 'UNDEFINED_PRIMITIVE_BOUNDARY'],
        'scope_statement': {
            'new_repo_local_primitive_explicitly_authorized': True,
            'complete_state_is_exactly_q_(u,p,m,mu)': True,
            'mu_is_internal_pattern_variable_and_m_is_reconstructed_from_mu': True,
            'not_DEV167_provenance': True,
            'not_a_physical_validity_claim': True,
            'no_universal_arrow_claim': True,
            'no_E_B_QED_mapping': True,
            'not_called_derived_from_PBUF_merely_because_testable': True,
        },
        'non_blocking_rule': 'Every EMX010-061 artifact and label is retained verbatim. EMX061 nonselection is not relabelled as solved except for an exact EMX062 candidate-and-test conclusion under this new scope; no candidate repairs, fits, maps, or reselects earlier evidence.',
        'artifact_parameter_rule': 'The finite update index and declared dt/refinement are reproducible artifact parameterizations only, not an independent physical external clock. Robustness compares dt=0.02 and dt=0.01 at fixed finite path length.',
        'primitive_constraints': {
            'local_or_relational_only': True,
            'translation_reflection_covariant': True,
            'no_hidden_spatial_origin': True,
            'no_independent_external_clock': True,
            'no_entropy_variable': True,
            'no_second_substance': True,
            'no_topological_charge': True,
            'no_fitted_constant': True,
        },
        'finite_candidate_registry': [
            {'id': 'NO_SELECTOR_CONTROL', 'class': 'control', 'law': 'mu is held or prescribed only as an admissible boundary/history record; no evolution or selection law.', 'local_relational': True, 'reversibility_status': 'NO_DYNAMICS', 'ledger_status': 'EMX060 retained ledger only', 'can_select': False},
            {'id': 'CONSERVATIVE_COUPLED_VARIATIONAL', 'class': 'conservative_coupled_variational_evolution', 'law': 'Stationary discrete coupled action using q and existing placement functional, with no added mu kinetic/conjugate variable.', 'local_relational': True, 'reversibility_status': 'FORMALLY_REVERSIBLE_IF_COMPLETED', 'ledger_status': 'would use exact action ledger', 'can_select': 'only_if_defined'},
            {'id': 'CONSTRAINED_ADMISSIBLE_CONTINUATION', 'class': 'constrained_admissible_continuation', 'law': 'Continue normalized m(mu) locally subject only to existing N_m=1 and continuity; no tie-break or orientation.', 'local_relational': True, 'reversibility_status': 'REVERSIBLE_AS_A_RELATION_NOT_AN_EVOLUTION', 'ledger_status': 'no exchange beyond retained placement ledger', 'can_select': False},
            {'id': 'DETERMINISTIC_LOCAL_RELAXATION', 'class': 'deterministic_local_relaxation_selection', 'law': 'At each artifact update, move mu along the centered local placement-energy descent relation using only A_int(u,m(mu)); the existing dt is the declared update scale.', 'local_relational': True, 'reversibility_status': 'EXPLICITLY_IRREVERSIBLE_ORIENTED_UPDATE', 'ledger_status': 'exact per-update A_int decrease is named D_mu and retained; D_mu is not entropy or a new state variable', 'can_select': 'only_among_states_reached_from_declared_initial_q'},
        ],
        'required_test_axes': ['EMX061_DEGENERATE_LOCALIZED_PATTERNS', 'TRANSLATION_REFLECTION_AND_DEGENERACY_COVARIANCE', 'FORWARD_REVERSE_HISTORY_AND_RECURRENCE', 'LOCAL_STABILITY_PERTURBATION_CONTINUATION', 'EMX060_PLACEMENT_FUNCTIONAL_COUPLING', 'INTERNAL_ENERGY_MOMENTUM_WORK_LEDGER', 'SOURCE_OFF_EMISSION_WAKE_HANDOFF', 'BACKGROUND_PRELOAD_SOURCE_SHAPE_BOUNDARY_REFINEMENT', 'CLOSED_CYCLE_PARAMETERIZATION_ROBUSTNESS_WITHOUT_HIDDEN_CLOCK'],
        'selection_distinctions': {'static_selection': 'one static m modulo stated symmetries', 'evolution_rule': 'a complete update/relation for internal mu', 'oriented_history_selection': 'one directed history from declared initial q without importing a boundary preparation as selector'},
        'undefined_boundary_rule': 'A result needing an unrepresented mu conjugate/kinetic state, endpoint condition, hidden origin, independent clock, entropy, second substance, topological charge, or fitted constant is UNDEFINED_PRIMITIVE_BOUNDARY. A prescribed start/end is a boundary condition, never a derived selector.',
        'prohibitions': {'NO_DEV167_OR_LAB_GIT_MODIFICATION_IMPORT_OR_EXECUTION': True, 'NO_E_B_QED_MAPPING': True, 'NO_FITTING_OR_RESELECTION': True, 'NO_DESTRUCTIVE_OR_EXTERNAL_ACTION': True, 'NO_PHYSICAL_VALIDITY_CLAIM': True, 'NO_UNIVERSAL_ARROW_CLAIM': True},
        'input_sha256': {path: digest(path) for path in inputs},
    }
    contract['contract_sha256'] = canonical(contract)
    O.mkdir(parents=True, exist_ok=True)
    (O / 'frozen_internal_pattern_evolution_selection_primitive_search_contract.json').write_text(json.dumps(contract, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__': main()
