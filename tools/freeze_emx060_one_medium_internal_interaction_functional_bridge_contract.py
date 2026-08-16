#!/usr/bin/env python3
"""Freeze EMX060's one-medium internal-functional contract before results."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
O = R / 'runs' / 'emx060'


def digest(path):
    return hashlib.sha256((R / path).read_bytes()).hexdigest()


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()



def main():
    inputs = [
        f'runs/emx0{n}/final_contract.json' for n in range(55, 60)
    ] + [
        'runs/emx055/held_out_registry_and_results.json',
        'runs/emx058/elastic_wake_and_history_record_ledger.json',
        'runs/emx059/rearrangement_source_work_ledger.json',
        'runs/emx059/wake_replay_ledger.json',
    ]
    contract = {
        'EMX060_SELECTOR': 'ONE_MEDIUM_INTERNAL_INTERACTION_FUNCTIONAL_BRIDGE',
        'FROZEN_BEFORE_RESULTS': True,
        'mode': 'EVIDENCE_BUILDING_NON_BLOCKING',
        'classification_vocabulary': ['SUPPORTED_IN_SCOPE', 'CONTRADICTED_IN_SCOPE', 'DISTINCT_OBSERVABLE_BEHAVIOR', 'NOT_ASSESSED', 'UNDEFINED_PRIMITIVE_BOUNDARY'],
        'non_blocking_rule': 'Retain every cell, residual, comparison, and EMX055-059 label verbatim. No EMX060 result selects a family, repairs a prior contradiction, or changes an earlier classification.',
        'scope_statement': {
            'new_repo_local_finite_realization': True,
            'conceptual_evidence_only_from_prior_repo_artifacts': True,
            'not_DEV167_provenance': True,
            'not_a_physical_validity_claim': True,
            'no_E_B_QED_mapping': True,
            'no_universal_arrow_claim': True,
        },
        'complete_discrete_medium_state': {
            'name': 'q',
            'variables': {
                'u': 'placement field at every finite lattice cell',
                'p': 'placement momentum field at every finite lattice cell',
                'm': 'normalized localized matter-pattern weight field at every finite lattice cell',
                'mu': 'admissible continuous matter-pattern path parameter used to form m, not an external object or source path',
            },
            'matter_definition': 'Matter is the localized normalized configuration distinction m within q. It is neither an external object, secondary substance, scheduled attachment, nor separately imposed source path.',
            'admissible_history_rule': 'Translation and rearrangement are continuous piecewise-linear histories mu(t) of the same q; m is reconstructed from mu(t) by a normalized compact discrete kernel.',
        },
        'partition_and_accounting': {
            'shared_total_energy': 'K_placement(q) + A_elastic(q) + A_int(q)',
            'shared_total_momentum': 'sum_cells p',
            'work_convention': 'Pattern work is the exact A_int jump caused by the internally represented m change at fixed placement. Integrator evolution defect is named and retained; it is not discarded as conservation.',
            'boundary_flux_convention': 'Periodic boundary has zero declared boundary flux. Fixed boundary flux is the energy difference attributable to the frozen edge constraint and is retained as a record.',
        },
        'interaction_functional_alternatives': [
            {
                'id': 'LOCAL_PINNING_PATTERN',
                'A_int': 'gamma/2 * sum_x m_x |u_x|^2',
                'placement_load': '-delta A_int/delta u_x = -gamma*m_x*u_x',
            },
            {
                'id': 'LOCAL_STRAIN_PATTERN',
                'A_int': 'gamma/2 * sum_<x,y> (m_x+m_y)/2 * |u_y-u_x|^2',
                'placement_load': 'negative discrete placement variation of this bond functional only',
            },
        ],
        'limits': {
            'interaction_free': 'gamma = 0',
            'source_free': 'mu(t) is constant and p(t=0)=0',
            'static': 'mu(t) is constant',
            'adiabatic': 'same fixed path with declared slower duration',
        },
        'fixed_numerics': {'n': 11, 'dt': 0.02, 'steps': 160, 'gamma': 0.35, 'elastic_k': 1.0, 'pattern_radius': 1.35, 'axis': 0},
        'predeclared_histories': ['STATIONARY_PATTERN', 'INTERNAL_TRANSLATION', 'INTERNAL_REARRANGEMENT', 'SOURCE_OFF_EMISSION', 'CLOSED_CYCLE'],
        'required_controls': ['NO_COUPLING', 'STATIC', 'ADIABATIC', 'CONTROLLED_REVERSAL', 'REFLECTION_RECURRENCE', 'COVARIANCE', 'REFINEMENT', 'PRELOAD', 'FINITE_DOMAIN', 'SOURCE_SHAPE'],
        'comparison_rule': 'Compare EMX060 directly to the retained EMX058/059 records by family and label only; do not relabel, fit, map, or reselect. Report whether each functional has an exact named rearrangement ledger, wake change, and source-work-family distinction.',
        'prohibitions': {
            'NO_DEV167_OR_LAB_GIT_MODIFICATION_IMPORT_OR_EXECUTION': True,
            'NO_EXTERNAL_CODE_OR_ACTION': True,
            'NO_DESTRUCTIVE_ACTION': True,
            'NO_FITTING_OR_RESELECTION': True,
            'NO_E_B_QED_MAPPING': True,
            'NO_PHYSICAL_VALIDITY_CLAIM': True,
            'NO_UNIVERSAL_ARROW_CLAIM': True,
        },
        'input_sha256': {path: digest(path) for path in inputs},
    }
    contract['contract_sha256'] = canonical(contract)
    O.mkdir(parents=True, exist_ok=True)
    (O / 'frozen_one_medium_internal_interaction_functional_bridge_contract.json').write_text(json.dumps(contract, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
