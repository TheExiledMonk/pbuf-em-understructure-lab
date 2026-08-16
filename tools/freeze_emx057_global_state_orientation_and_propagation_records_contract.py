#!/usr/bin/env python3
"""Freeze the EMX057 evidence contract before any EMX057 result is made."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
O = R / 'runs' / 'emx057'

def digest(path): return hashlib.sha256((R / path).read_bytes()).hexdigest()
def canonical(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def main():
    inputs = [
        'runs/emx056/frozen_pbuf_elasticity_emission_wide_net_contract.json',
        'runs/emx056/batch_a_exchange_registry.json',
        'runs/emx056/candidate_gate_ledger.json',
        'runs/emx055/frozen_held_out_source_work_discriminator_contract.json',
    ]
    contract = {
        'EMX057_SELECTOR': 'GLOBAL_STATE_ORIENTATION_AND_PROPAGATION_RECORDS',
        'FROZEN_BEFORE_RESULTS': True,
        'mode': 'EVIDENCE_BUILDING_NON_BLOCKING',
        'non_blocking_rule': 'Retain every finite outcome. No outcome changes EMX001-056 labels or establishes a universal arrow.',
        'classification_vocabulary': ['SUPPORTED_IN_SCOPE', 'CONTRADICTED_IN_SCOPE', 'DISTINCT_OBSERVABLE_BEHAVIOR', 'NOT_ASSESSED', 'UNDEFINED_PRIMITIVE_BOUNDARY'],
        'primitive': {
            'name': 'REPO_LOCAL_GLOBAL_STATE_ORIENTATION_PROPAGATION_RECORD_V1',
            'definition': 'A deterministic finite-state/history comparison record: source-local energy, total energy, transported-energy complement, origin-free sorted energy distribution, translation-invariant spectral magnitude, and exact finite replay relation.',
            'scope': 'A diagnostic primitive for EMX056 two-sector internal exchange under frozen source-work families.',
            'non_historical': True,
            'not_DEV167_provenance': True,
            'not_independent_physical_clock': True,
            'no_E_B_QED_mapping_or_physical_claim': True,
            'no_entropy_or_dissipation_assumption': True,
            'no_arbitrary_origin': 'Distribution and Fourier-magnitude observables are invariant under lattice translation; source-local ledger is separately named and never promoted to a global orientation.',
        },
        'families_from_EMX056': ['POTENTIAL_PORT_EQUIVALENCE_CLASS', 'DIRECTED_BOND'],
        'fixed_battery': {
            'source_off_emission': ['DISPLACEMENT_PRELOAD', 'VELOCITY_PRELOAD'],
            'matched_controls': ['INCOMING_TIME_REVERSED', 'STANDING_SYMMETRIC', 'NO_EXCHANGE', 'SPATIAL_REFLECTION', 'RECURRENCE'],
            'robustness_controls': ['AXIS_COVARIANCE', 'SOURCE_SHAPE', 'LATTICE_REFINEMENT', 'TIME_REFINEMENT', 'PERIODIC_BOUNDARY', 'FIXED_BOUNDARY', 'PRELOAD'],
            'ledger': ['LOCAL_RETURN', 'TRANSPORTED_ENERGY', 'TOTAL_CONSERVATION', 'DISTRIBUTED_RECORDS', 'TRUE_REVERSAL'],
        },
        'finite_deterministic_protocol': {
            'integrator': 'velocity-Verlet; fixed dt/steps/grid/boundary values in runner',
            'source': 'Initial finite two-sector preparation only; no external force after step zero.',
            'artifact_hashing': 'All emitted JSON artifacts carry SHA-256 of canonical payload; contract hashes declared inputs.',
            'no_fitting_or_reselection': True,
        },
        'prohibitions': {
            'NO_DEV167_OR_LAB_GIT_MODIFICATION_IMPORT_OR_EXECUTION': True,
            'NO_FITTING_OR_RESELECTION': True,
            'NO_EXTERNAL_OR_DESTRUCTIVE_ACTIONS': True,
            'NO_E_B_QED_MAPPING': True,
            'NO_UNIVERSAL_ARROW_FROM_BOUNDARY_CONDITIONED_HISTORIES': True,
        },
        'input_sha256': {p: digest(p) for p in inputs},
    }
    contract['contract_sha256'] = canonical(contract)
    O.mkdir(parents=True, exist_ok=True)
    (O / 'frozen_global_state_orientation_and_propagation_records_contract.json').write_text(json.dumps(contract, indent=2, sort_keys=True) + '\n')

if __name__ == '__main__': main()
