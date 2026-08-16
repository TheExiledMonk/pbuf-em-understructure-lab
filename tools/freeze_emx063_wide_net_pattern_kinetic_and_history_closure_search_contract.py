#!/usr/bin/env python3
"""Freeze the EMX063 neutral registry before any result cell is produced."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
O = R / 'runs' / 'emx063'


def digest(path): return hashlib.sha256((R / path).read_bytes()).hexdigest()
def canonical(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def main():
    inputs = [
        'runs/emx060/frozen_one_medium_internal_interaction_functional_bridge_contract.json',
        'runs/emx060/one_medium_internal_interaction_ledger.json',
        'runs/emx061/frozen_localized_pattern_and_admissible_history_selection_audit_contract.json',
        'runs/emx061/localized_pattern_and_admissible_history_selection_ledger.json',
        'runs/emx062/frozen_internal_pattern_evolution_selection_primitive_search_contract.json',
        'runs/emx062/internal_pattern_evolution_selection_ledger.json',
        'runs/emx062/final_contract.json',
    ]
    registry = [
        {'id': 'A_CANONICAL_MU_PI', 'family': 'A_CANONICAL_PATTERN_CONJUGATE_PAIR', 'state_additions': ['pi_mu'], 'provenance': 'new explicit neutral EMX063 internal pattern momentum primitive', 'assumptions': ['H_mu=1/2|pi_mu|^2+A_int(u,m(mu))', 'unit coefficients are fixed neutral normalizations, not fitted'], 'kind': 'conservative deterministic evolution'},
        {'id': 'B_SYMPLECTIC_PHASE_PAIR', 'family': 'B_PAIRED_PHASE_SECTOR', 'state_additions': ['xi_mu'], 'provenance': 'new explicit neutral EMX063 paired internal phase primitive', 'assumptions': ['d(mu,xi)/ds=J grad A_int with stated antisymmetric J', 'no orientation or origin'], 'kind': 'conservative deterministic evolution'},
        {'id': 'C_RELATIONAL_DEGREE_ONE_HISTORY', 'family': 'C_CONSTRAINED_DEGREE_ONE_HISTORY_ACTION', 'state_additions': ['rho_rel', 'pi_mu'], 'provenance': 'new explicit relational duration/gauge primitive rho_rel, not an external clock', 'assumptions': ['degree-one homogeneous local history action', 'rho_rel is a gauge variable and requires a stated endpoint/gauge section for a finite record'], 'kind': 'constrained history relation'},
        {'id': 'D_HIGHER_ORDER_LOCAL_HISTORY', 'family': 'D_HIGHER_ORDER_LOCAL_HISTORY', 'state_additions': ['v_mu', 'a_mu', 'j_mu'], 'provenance': 'new explicit finite local-history jet variables', 'assumptions': ['finite initialized local jet update', 'no unspecified nonlocal kernel', 'unit neutral normalization'], 'kind': 'deterministic local-history evolution'},
        {'id': 'E_ENDPOINT_STATIONARY_CONTROL', 'family': 'E_ENDPOINT_BOUNDARY_SELECTED_VARIATIONAL_HISTORY', 'state_additions': [], 'provenance': 'declared endpoint data only', 'assumptions': ['fixed initial/final mu and duration section'], 'kind': 'boundary selection rather than dynamics'},
        {'id': 'E_BOUNDARY_DIRECT_PATH_CONTROL', 'family': 'E_ENDPOINT_BOUNDARY_SELECTED_VARIATIONAL_HISTORY', 'state_additions': [], 'provenance': 'declared path/endpoint data only', 'assumptions': ['path is supplied as boundary data'], 'kind': 'boundary selection rather than dynamics'},
        {'id': 'F_NO_SELECTOR_CONTROL', 'family': 'F_NO_SELECTOR_AND_IRREVERSIBLE_CONTROLS', 'state_additions': [], 'provenance': 'retained EMX061/062 control', 'assumptions': ['mu held or prescribed'], 'kind': 'no selector'},
        {'id': 'F_IRREVERSIBLE_RELAXATION_CONTROL', 'family': 'F_NO_SELECTOR_AND_IRREVERSIBLE_CONTROLS', 'state_additions': [], 'provenance': 'retained EMX062 explicit update', 'assumptions': ['A_int descent with declared update index'], 'kind': 'explicitly irreversible control'},
    ]
    contract = {
        'EMX063_SELECTOR': 'WIDE_NET_PATTERN_KINETIC_AND_HISTORY_CLOSURE_SEARCH',
        'FROZEN_BEFORE_RESULTS': True,
        'mode': 'FINITE_DETERMINISTIC_ARTIFACT_HASHED_REPO_LOCAL_NON_BLOCKING_SEARCH',
        'classification_vocabulary': ['SUPPORTED_IN_SCOPE', 'CONTRADICTED_IN_SCOPE', 'DISTINCT_OBSERVABLE_BEHAVIOR', 'NOT_ASSESSED', 'UNDEFINED_PRIMITIVE_BOUNDARY'],
        'non_blocking_rule': 'All EMX010-062 artifacts and labels are retained verbatim. This is neither fitting nor reselection and does not repair an earlier conclusion.',
        'state_scope': {'localized_pattern_variable': 'mu', 'existing_reconstruction': 'm=m(mu)', 'all_new_state_additions_must_be_listed_with_provenance': True, 'relational_duration_rule': 'rho_rel is an explicit candidate gauge primitive, never a hidden clock.'},
        'finite_candidate_registry': registry,
        'required_test_axes': ['EMX061_DEGENERACIES_AND_HISTORY_SELECTION', 'CONSERVATIVE_LEDGER_AND_ACTION_OR_CONSTRAINT_IDENTITY', 'REVERSAL_RECURRENCE_AND_CONTROLLED_REVERSE', 'TRANSLATION_REFLECTION_COVARIANCE', 'LOCAL_STABILITY_PERTURBATION_CONTINUATION', 'BOTH_EMX060_INTERACTION_FUNCTIONALS', 'SOURCE_OFF_EMISSION_WAKE_HANDOFF', 'CLOSED_CYCLES', 'PARAMETERIZATION_DURATION_GAUGE_ROBUSTNESS', 'PRELOAD_FINITE_DOMAIN_SOURCE_SHAPE_LATTICE_REFINEMENT_CONTROLS'],
        'distinctions': {'static_pattern_selection': 'unique static m without declared boundary data', 'deterministic_evolution': 'complete finite initialized local state update', 'oriented_history_selection': 'an oriented history selected by a law rather than endpoint preparation', 'conserved_ledger': 'named finite identity for a defined conservative candidate', 'declared_boundary_data': 'a supplied start/end/path, classified only as boundary selection.'},
        'undefined_primitive_rule': 'If a candidate needs state, normalization, endpoint, gauge section, or kernel data not explicitly represented by its frozen neutral alternative, classify that requested conclusion UNDEFINED_PRIMITIVE_BOUNDARY; do not invent it.',
        'prohibitions': {'NO_DEV167_OR_LAB_GIT_MODIFICATION_IMPORT_OR_EXECUTION': True, 'NO_EXTERNAL_OR_DESTRUCTIVE_ACTION': True, 'NO_E_B_QED_MAPPING': True, 'NO_FITTING_OR_RESELECTION': True, 'NO_PHYSICAL_VALIDITY_CLAIM': True, 'NO_UNIVERSAL_ARROW_CLAIM': True, 'NO_ENTROPY_EXTERNAL_MATTER_SECOND_MEDIUM_HIDDEN_ORIGIN_TOPOLOGICAL_CHARGE_FITTED_CONSTANT_OR_UNSPECIFIED_NONLOCAL_KERNEL': True},
        'input_sha256': {path: digest(path) for path in inputs},
    }
    contract['contract_sha256'] = canonical(contract)
    O.mkdir(parents=True, exist_ok=True)
    (O / 'frozen_wide_net_pattern_kinetic_and_history_closure_search_contract.json').write_text(json.dumps(contract, indent=2, sort_keys=True) + '\n')
    (O / 'candidate_registry.json').write_text(json.dumps({'contract_sha256': contract['contract_sha256'], 'frozen_registry': registry, 'all_candidates_retained': True}, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__': main()
