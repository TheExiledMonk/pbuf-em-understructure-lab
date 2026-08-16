#!/usr/bin/env python3
"""Freeze EMX059's finite source-rearrangement work contract before results."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
O = R / 'runs' / 'emx059'


def digest(path):
    return hashlib.sha256((R / path).read_bytes()).hexdigest()


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def main():
    inputs = [
        'runs/emx058/frozen_elastic_wake_and_history_record_battery_contract.json',
        'runs/emx058/elastic_wake_and_history_record_ledger.json',
        'runs/emx058/final_contract.json',
    ]
    contract = {
        'EMX059_SELECTOR': 'REARRANGEMENT_SOURCE_WORK_CLOSURE_AND_WAKE_REPLAY',
        'FROZEN_BEFORE_RESULTS': True,
        'mode': 'EVIDENCE_BUILDING_NON_BLOCKING',
        'non_blocking_rule': 'Retain every variant, cell, residual, and prior contradiction. Closure never selects a family or upgrades an EMX058 conclusion.',
        'classification_vocabulary': ['SUPPORTED_IN_SCOPE', 'CONTRADICTED_IN_SCOPE', 'DISTINCT_OBSERVABLE_BEHAVIOR', 'NOT_ASSESSED', 'UNDEFINED_PRIMITIVE_BOUNDARY'],
        'scope_statement': {
            'finite_repo_local_work_construction_refinement': True,
            'not_DEV167_provenance': True,
            'not_a_physical_claim': True,
            'no_E_B_QED_mapping': True,
            'preserve_EMX055_to_EMX058_results': True,
            'emx058_rearranging_contradictions_not_resolved_without_exact_new_evidence': True,
        },
        'source_work_families_from_EMX058': {
            'POTENTIAL_PORT_EQUIVALENCE_CLASS': ['CONSERVATIVE_SOURCE_POTENTIAL', 'DISCRETE_PORT_WORK_PAIRING'],
            'DIRECTED_BOND': ['GEOMETRY_COVARIANT_BOND_WORK'],
        },
        'fixed_histories': ['MOVING_RIGHT_ON_OFF', 'MOVING_LEFT_ON_OFF', 'REARRANGING_ON_OFF'],
        'fixed_discrete_timing': {
            'dt': 0.035, 'steps': 144, 'source_on_steps': [0, 47], 'source_off_steps': [48, 143],
            'relocation_schedule': 'The named source cell changes only at the fixed end-of-step relocation port.',
            'work_support_rule': 'Every ledger term carries exactly one inclusive step support; comparisons require identical support and phase labels.',
        },
        'predeclared_neutral_accounting_variants': [
            {
                'id': 'FORCE_DISPLACEMENT_PORT',
                'definition': 'External source force dotted with the actual discrete source-coordinate displacement; relocation is the exact coupling-potential jump.',
                'defined_for': ['POTENTIAL_PORT_EQUIVALENCE_CLASS', 'DIRECTED_BOND'],
                'closure_terms': ['source_force_displacement_work', 'relocation_work', 'coupling_potential_change', 'medium_energy_change', 'source_internal_energy_change', 'boundary_flux', 'impulse_balance_residual'],
            },
            {
                'id': 'DISCRETE_STATE_INCREMENT_PORT',
                'definition': 'Exact state-energy increments at the fixed kick, drift, and relocation maps; the finite map defect is retained as a named discrete evolution term.',
                'defined_for': ['POTENTIAL_PORT_EQUIVALENCE_CLASS', 'DIRECTED_BOND'],
                'closure_terms': ['exact_port_state_increment', 'exact_relocation_state_increment', 'discrete_evolution_increment', 'boundary_flux', 'impulse_balance_residual'],
            },
            {
                'id': 'BOND_ENDPOINT_INCREMENT_PORT',
                'definition': 'Exact endpoint coupling-potential jump and directed bond-energy change, with source and medium endpoint energies retained separately.',
                'defined_for': ['DIRECTED_BOND'],
                'closure_terms': ['bond_endpoint_work', 'relocation_work', 'bond_potential_change', 'medium_energy_change', 'source_internal_energy_change', 'boundary_flux', 'impulse_balance_residual'],
            },
        ],
        'required_controls': ['MATCHED_MOVING_SOURCE_SUCCESSFUL', 'STATIONARY_NO_EXCHANGE', 'REVERSAL_REPLAY', 'SOURCE_SHAPE', 'TIME_REFINEMENT', 'BOUNDARY', 'AMPLITUDE', 'PRELOAD', 'CLOSED_CYCLE'],
        'wake_replay_rule': 'For every variant whose rearranging ledger closes, replay its corresponding moving-source wake cells unchanged and report that closure is source-work closure only, never a universal-arrow claim.',
        'prohibitions': {
            'NO_DEV167_OR_LAB_GIT_MODIFICATION_IMPORT_OR_EXECUTION': True,
            'NO_FITTING_OR_RESELECTION': True,
            'NO_EXTERNAL_OR_DESTRUCTIVE_ACTION': True,
            'NO_E_B_QED_MAPPING': True,
            'NO_UNIVERSAL_ARROW_CLAIM': True,
        },
        'input_sha256': {path: digest(path) for path in inputs},
    }
    contract['contract_sha256'] = canonical(contract)
    O.mkdir(parents=True, exist_ok=True)
    (O / 'frozen_rearrangement_source_work_closure_and_wake_replay_contract.json').write_text(json.dumps(contract, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
