#!/usr/bin/env python3
"""Freeze EMX064's finite A/B discriminator contract before execution."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
O = R / 'runs' / 'emx064'


def digest(path):
    return hashlib.sha256((R / path).read_bytes()).hexdigest()


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def main():
    inputs = [
        'runs/emx063/frozen_wide_net_pattern_kinetic_and_history_closure_search_contract.json',
        'runs/emx063/candidate_registry.json',
        'runs/emx063/wide_net_pattern_kinetic_and_history_closure_ledger.json',
        'runs/emx063/final_contract.json',
        'runs/emx060/frozen_one_medium_internal_interaction_functional_bridge_contract.json',
        'runs/emx060/one_medium_internal_interaction_ledger.json',
    ]
    classes = [
        {'id': 'A_CANONICAL_MU_PI', 'state': '(u,p,mu,pi_mu)', 'evolution': 'canonical velocity-Verlet update of H=K(p)+A_elastic(u)+A_int(u,m(mu))+|pi_mu|^2/2'},
        {'id': 'B_SYMPLECTIC_PHASE_PAIR', 'state': '(u,p,mu,xi_mu)', 'evolution': 'the same frozen canonical symplectic form written with xi_mu as the paired phase coordinate'},
    ]
    cells = [
        {'id': 'RECIPROCAL_LEDGER', 'prepared_data': 'localized mu and paired-state momentum', 'rule': 'conserved evolution', 'boundary': 'periodic'},
        {'id': 'PACKET_SOURCE_OFF_WAKE_ABSORB_SCATTER_REVERSE', 'prepared_data': 'localized packet or two separated packets; source-off is initial p only', 'rule': 'conserved evolution', 'boundary': 'periodic'},
        {'id': 'STABILITY_NONLINEAR_COLLISION_BINDING', 'prepared_data': 'single perturbation, finite amplitude, or two packet configuration', 'rule': 'conserved evolution', 'boundary': 'periodic'},
        {'id': 'COVARIANCE_REFINEMENT_BOUNDARY_GRADIENT_LIMITS', 'prepared_data': 'translated/reflected/rotated packets and frozen preload/shape/stiffness choices', 'rule': 'conserved evolution', 'boundary': 'periodic recurrence; finite-domain size is a boundary condition'},
        {'id': 'STRUCTURE_REVERSIBILITY_NORMALIZATION_SENSITIVITY', 'prepared_data': 'frozen normalization and initialization variants', 'rule': 'conserved evolution', 'boundary': 'periodic'},
        {'id': 'HELD_OUT_CROSS_PREDICTION', 'prepared_data': 'identical held-out packet state under A/B coordinate identification', 'rule': 'conserved evolution', 'boundary': 'periodic'},
    ]
    contract = {
        'EMX064_SELECTOR': 'WIDE_NET_CONSERVATIVE_PATTERN_CLOSURE_DISCRIMINATOR',
        'FROZEN_BEFORE_RESULTS': True,
        'mode': 'FINITE_DETERMINISTIC_ARTIFACT_HASHED_NON_BLOCKING_DISCRIMINATOR',
        'classification_vocabulary': ['SUPPORTED_IN_SCOPE', 'CONTRADICTED_IN_SCOPE', 'DISTINCT_OBSERVABLE_BEHAVIOR', 'NOT_ASSESSED', 'UNDEFINED_PRIMITIVE_BOUNDARY'],
        'non_blocking_rule': 'EMX010-063 artifacts, results, and labels are retained verbatim. EMX064 neither fits, reselects, eliminates a class, nor closes any larger primitive.',
        'allowed_emx063_classes_only': classes,
        'emx060_interaction_functionals': ['LOCAL_PINNING_PATTERN', 'LOCAL_STRAIN_PATTERN'],
        'predeclared_artifact_hashed_cells': cells,
        'frozen_numerics': {'n': 9, 'dt': 0.01, 'steps': 48, 'gamma': 0.35, 'elastic_k': 1.0, 'pattern_radius': 1.35, 'finite_difference_epsilon': 0.0001, 'identity_tolerance': 2e-8, 'comparison_tolerance': 2e-10},
        'classification_rule': 'Every retained finite result uses only the stated vocabulary. Numerical identity is evaluated against frozen tolerances; a missing primitive is UNDEFINED_PRIMITIVE_BOUNDARY, never a reason to eliminate either class.',
        'provenance_rule': 'Prepared initial data, conserved evolution rules, and boundary conditions are recorded separately in every execution cell. Source-off means no forcing after its prepared initial data.',
        'held_out_observables': ['total_ledger_residual', 'exchange_identity_residual', 'time_reversal_state_residual', 'packet_centroid', 'wake_l2', 'translation_reflection_rotation_residual'],
        'prohibitions': {'NO_DEV167_OR_LAB_GIT_MODIFICATION_IMPORT_OR_EXECUTION': True, 'NO_EXTERNAL_OR_DESTRUCTIVE_ACTION': True, 'NO_EXTERNAL_FORCING_TO_MIMIC_SOURCE': True, 'NO_EXTRA_MATTER_SPECIES_OR_ARBITRARY_STATE_COMPONENTS': True, 'NO_OUTCOME_DEPENDENT_THRESHOLDS_OR_HIDDEN_SELECTION': True, 'NO_FITTING_OR_RESELECTION': True, 'NO_E_B_QED_MAPPING': True, 'NO_PHYSICAL_VALIDITY_CLAIM': True, 'NO_UNIVERSAL_ARROW_CLAIM': True},
        'input_sha256': {path: digest(path) for path in inputs},
    }
    contract['contract_sha256'] = canonical(contract)
    O.mkdir(parents=True, exist_ok=True)
    (O / 'frozen_wide_net_conservative_pattern_closure_discriminator_contract.json').write_text(json.dumps(contract, indent=2, sort_keys=True) + '\n')
    (O / 'finite_registry.json').write_text(json.dumps({'contract_sha256': contract['contract_sha256'], 'classes': classes, 'cells': cells, 'all_cells_predeclared': True}, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
