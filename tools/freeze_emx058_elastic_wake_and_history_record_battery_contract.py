#!/usr/bin/env python3
"""Freeze EMX058's local, non-blocking wake/record experiment before results."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
O = R / 'runs' / 'emx058'

def digest(path):
    return hashlib.sha256((R / path).read_bytes()).hexdigest()

def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def main():
    inputs = [
        'runs/emx056/frozen_pbuf_elasticity_emission_wide_net_contract.json',
        'runs/emx056/batch_a_exchange_registry.json',
        'runs/emx055/frozen_held_out_source_work_discriminator_contract.json',
    ]
    contract = {
        'EMX058_SELECTOR': 'ELASTIC_WAKE_AND_HISTORY_RECORD_BATTERY',
        'FROZEN_BEFORE_RESULTS': True,
        'mode': 'EVIDENCE_BUILDING_NON_BLOCKING',
        'non_blocking_rule': 'Retain every outcome and candidate. Missing closure never rejects a candidate or changes earlier labels.',
        'classification_vocabulary': ['SUPPORTED_IN_SCOPE', 'CONTRADICTED_IN_SCOPE', 'DISTINCT_OBSERVABLE_BEHAVIOR', 'NOT_ASSESSED', 'UNDEFINED_PRIMITIVE_BOUNDARY'],
        'scope_statement': {
            'new_repo_local_non_historical_wake_record_experiment': True,
            'not_DEV167_provenance': True,
            'not_a_physical_clock_or_universal_arrow_claim': True,
            'no_E_B_QED_mapping': True,
            'no_dissipation_assumption': True,
            'no_arbitrary_origin': 'Global records use sorted density and Fourier magnitude; local ledgers name their moving source cell explicitly.'
        },
        'families_from_EMX056_EMX055': {
            'POTENTIAL_PORT_EQUIVALENCE_CLASS': ['CONSERVATIVE_SOURCE_POTENTIAL', 'DISCRETE_PORT_WORK_PAIRING'],
            'DIRECTED_BOND': ['GEOMETRY_COVARIANT_BOND_WORK']
        },
        'finite_deterministic_primitive': {
            'medium': 'finite artifact-hashed 3D elastic lattice u,p with velocity-Verlet evolution',
            'source': 'localized q,r source coordinate coupled to a deterministic moving/rearranging cell schedule; source-on/source-off histories are fixed below',
            'histories': ['MOVING_RIGHT_ON_OFF', 'MOVING_LEFT_ON_OFF', 'REARRANGING_ON_OFF'],
            'wake_observables': ['residual_deformation', 'phase_correlation_record', 'scattered_modes', 'delayed_local_relaxation', 'transported_ledger'],
            'accounting': ['medium_energy', 'source_energy', 'coupling_energy', 'total_energy', 'source_work', 'exchange_residual', 'medium_momentum', 'source_momentum', 'external_impulse', 'momentum_residual'],
            'artifact_hashing': 'Every emitted result artifact receives SHA-256 over its canonical payload.',
            'no_fitting_or_reselection': True
        },
        'fixed_controls': ['STATIONARY', 'NO_EXCHANGE', 'SOURCE_SHAPE', 'DIRECTED_PREPARATION', 'CONTROLLED_FULL_STATE_REVERSAL', 'REFLECTION', 'RECURRENCE', 'PERIODIC_AND_FIXED_BOUNDARY', 'STIFFNESS_AND_PRELOAD', 'AXIS_COVARIANCE', 'RELATION_NETWORK_AND_REFINEMENT', 'SPEED_AMPLITUDE_AND_FINITE_DOMAIN'],
        'interpretation_limits': ['Prior-passage direction reconstruction is an in-scope record test only.', 'Dynamic exclusion of exact global reversal is an undefined primitive boundary, distinct from local finite replay.', 'All wake claims are finite, source-history and boundary conditioned.'],
        'prohibitions': {
            'NO_DEV167_OR_LAB_GIT_MODIFICATION_IMPORT_OR_EXECUTION': True,
            'NO_FITTING_OR_RESELECTION': True,
            'NO_EXTERNAL_OR_DESTRUCTIVE_ACTION': True,
            'NO_E_B_QED_MAPPING': True,
            'NO_UNIVERSAL_ARROW_CLAIM': True
        },
        'input_sha256': {path: digest(path) for path in inputs},
    }
    contract['contract_sha256'] = canonical(contract)
    O.mkdir(parents=True, exist_ok=True)
    (O / 'frozen_elastic_wake_and_history_record_battery_contract.json').write_text(json.dumps(contract, indent=2, sort_keys=True) + '\n')

if __name__ == '__main__':
    main()
