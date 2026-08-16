#!/usr/bin/env python3
"""Freeze the finite, non-blocking EMX061 selection-audit contract."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
O = R / 'runs' / 'emx061'


def digest(path): return hashlib.sha256((R / path).read_bytes()).hexdigest()
def canonical(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def main():
    inputs = [
        'runs/emx060/final_contract.json',
        'runs/emx060/frozen_one_medium_internal_interaction_functional_bridge_contract.json',
        'runs/emx060/one_medium_internal_interaction_ledger.json',
        'runs/emx060/emx058_emx059_direct_comparison.json',
    ]
    contract = {
        'EMX061_SELECTOR': 'LOCALIZED_PATTERN_AND_ADMISSIBLE_HISTORY_SELECTION_AUDIT',
        'FROZEN_BEFORE_RESULTS': True,
        'mode': 'FINITE_REPO_LOCAL_EVIDENCE_BUILDING_NON_BLOCKING',
        'classification_vocabulary': ['SUPPORTED_IN_SCOPE', 'CONTRADICTED_IN_SCOPE', 'DISTINCT_OBSERVABLE_BEHAVIOR', 'NOT_ASSESSED', 'UNDEFINED_PRIMITIVE_BOUNDARY'],
        'non_blocking_rule': 'EMX060 and every earlier artifact, label, and contradiction are retained verbatim. EMX061 neither selects an interaction functional nor repairs, maps, fits, reselects, or relabels prior evidence.',
        'scope_statement': {
            'finite_repo_local_selection_audit_only': True,
            'not_a_physical_validity_claim': True,
            'not_DEV167_provenance': True,
            'no_universal_arrow_claim': True,
            'no_E_B_QED_mapping': True,
        },
        'existing_medium_scope': {
            'source': 'EMX060 complete state q=(u,p,m,mu), its two one-medium interaction functionals, and its fixed numerics only',
            'admissibility': 'm is the existing normalized compact discrete pattern reconstructed from mu; declared histories are existing continuous piecewise-linear mu(t) schedules.',
            'represented_invariant': 'N_m = sum_x m_x = 1, the existing normalized pattern weight only; it is not a topological or new charge.',
        },
        'predeclared_selector_registry': [
            {'id': 'STATIC_ENERGY_STATIONARITY_MINIMUM', 'kind': 'select_static_pattern', 'principle': 'Stationarity/minimum of the existing nonnegative placement energy at fixed admissible m.', 'eligible': True, 'success_condition': 'A unique localized m modulo explicitly stated lattice symmetries follows without a preparation.'},
            {'id': 'LOCALIZED_STABILITY_AND_CONTINUATION', 'kind': 'permission_for_pattern_and_history_class', 'principle': 'Nonnegative second variation in u and continuation within existing admissible m/mu.', 'eligible': True, 'success_condition': 'A stability/continuation result distinguishes one localized pattern or one history class without scheduling.'},
            {'id': 'NORMALIZED_PATTERN_INVARIANT', 'kind': 'fixed_invariant_constraint', 'principle': 'The already represented N_m=1 constraint only.', 'eligible': True, 'success_condition': 'The existing invariant uniquely selects a localized configuration rather than only a class.'},
            {'id': 'STATIONARY_DISCRETE_ACTION_ALTERNATIVES', 'kind': 'history_action_alternatives', 'principle': 'Existing fixed-dt mechanical discrete action, varied only in u at fixed admissible m/mu, where defined.', 'eligible': True, 'success_condition': 'Stationarity selects one oriented history without a mu evolution law or endpoint preparation.'},
            {'id': 'NO_SELECTOR_CONTROLS', 'kind': 'controls', 'principle': 'Boundary conditions, preload, source-off preparation, finite domain, refinement, and replay records.', 'eligible': True, 'success_condition': 'A control is not counted as a selector; it may only expose dependence or covariance.'},
        ],
        'required_test_axes': ['LOCALIZATION', 'STABILITY_PERTURBATION', 'TRANSLATION_REFLECTION_COVARIANCE', 'DEGENERACY_NONUNIQUENESS', 'FINITE_DOMAIN_REFINEMENT', 'BACKGROUND_PRELOAD', 'SOURCE_OFF_EMISSION_WAKE_HANDOFF', 'REVERSIBLE_HISTORY_REPLAY_WHERE_DEFINED', 'ENERGY_MOMENTUM_WORK_LEDGER', 'INTERACTION_FUNCTIONAL_COMPATIBILITY'],
        'selection_distinctions': {
            'static_pattern': 'Selection of one static m configuration.',
            'history_class': 'Permission for a class of admissible mu(t) histories.',
            'oriented_history': 'Dynamic selection of one time-oriented member of a permitted history class.',
        },
        'undefined_primitive_rule': 'If a selector requires entropy, a clock, a second substance, a hidden spatial origin, topological charge, a free fitted constant, or an unrepresented mu evolution law, classify the requested conclusion UNDEFINED_PRIMITIVE_BOUNDARY rather than introduce it.',
        'prohibitions': {
            'NO_DEV167_OR_LAB_GIT_MODIFICATION_IMPORT_OR_EXECUTION': True,
            'NO_EXTERNAL_OR_DESTRUCTIVE_ACTION': True,
            'NO_FITTING_OR_RESELECTION': True,
            'NO_E_B_QED_MAPPING': True,
            'NO_PHYSICAL_VALIDITY_CLAIM': True,
            'NO_UNIVERSAL_ARROW_CLAIM': True,
            'NO_ENTROPY_CLOCK_SECOND_SUBSTANCE_HIDDEN_ORIGIN_TOPOLOGICAL_CHARGE_OR_FREE_FITTED_CONSTANT': True,
        },
        'input_sha256': {path: digest(path) for path in inputs},
    }
    contract['contract_sha256'] = canonical(contract)
    O.mkdir(parents=True, exist_ok=True)
    (O / 'frozen_localized_pattern_and_admissible_history_selection_audit_contract.json').write_text(json.dumps(contract, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__': main()
