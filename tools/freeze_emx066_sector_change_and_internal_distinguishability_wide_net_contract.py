#!/usr/bin/env python3
"""Freeze EMX066's finite sector and internal-distinguishability registry."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
O = R / 'runs' / 'emx066'


def digest(path):
    return hashlib.sha256((R / path).read_bytes()).hexdigest()


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def main():
    inputs = [
        'runs/emx065/frozen_two_pattern_interaction_and_nonuniform_medium_bridge_contract.json',
        'runs/emx065/finite_registry.json',
        'runs/emx065/two_pattern_interaction_and_nonuniform_medium_bridge_ledger.json',
        'runs/emx065/final_contract.json',
    ]
    sector_extensions = [
        {'id': 'A_CANONICAL_REVERSIBLE_MODE_CONVERSION', 'base_class': 'A_CANONICAL_TWO_MU_PI',
         'state_additions': '(eta_1,rho_1,eta_2,rho_2); sector_label_i = MODE_0 if eta_i >= 0 else MODE_1',
         'transition_rule': 'eta_i,rho_i undergo frozen harmonic Hamiltonian rotation; a label change occurs only on a dynamical eta_i=0 crossing, never at a boundary.',
         'sector_ledger': 'pattern-count=2 is conserved; individual derived mode-sector labels may change; eta/rho energy is included in total energy.',
         'reversibility_status': 'REVERSIBLE_UNDER_MOMENTUM_AND_RHO_REVERSAL'},
        {'id': 'B_SYMPLECTIC_REVERSIBLE_MODE_CONVERSION', 'base_class': 'B_SYMPLECTIC_TWO_PHASE_PAIR',
         'state_additions': '(eta_1,rho_1,eta_2,rho_2); sector_label_i = MODE_0 if eta_i >= 0 else MODE_1',
         'transition_rule': 'the same frozen harmonic symplectic rotation written with xi_i as the paired coordinate; a label change occurs only on a dynamical eta_i=0 crossing, never at a boundary.',
         'sector_ledger': 'pattern-count=2 is conserved; individual derived mode-sector labels may change; eta/rho energy is included in total energy.',
         'reversibility_status': 'REVERSIBLE_UNDER_MOMENTUM_AND_RHO_REVERSAL'},
    ]
    closure_alternatives = [
        {'id': 'A_LOCAL_PINNING_INTERNAL', 'class': 'A_CANONICAL_TWO_MU_PI', 'functional': 'LOCAL_PINNING_PATTERN'},
        {'id': 'A_LOCAL_STRAIN_INTERNAL', 'class': 'A_CANONICAL_TWO_MU_PI', 'functional': 'LOCAL_STRAIN_PATTERN'},
        {'id': 'B_LOCAL_PINNING_INTERNAL', 'class': 'B_SYMPLECTIC_TWO_PHASE_PAIR', 'functional': 'LOCAL_PINNING_PATTERN'},
        {'id': 'B_LOCAL_STRAIN_INTERNAL', 'class': 'B_SYMPLECTIC_TWO_PHASE_PAIR', 'functional': 'LOCAL_STRAIN_PATTERN'},
    ]
    sector_cells = [
        {'id': 'NO_SECTOR_CHANGE_CONTROL', 'prepared_eta_rho': 'eta=(1,1), rho=(0,0); no zero crossing in frozen duration'},
        {'id': 'DYNAMICAL_MODE_CONVERSION_COLLISION_SEPARATION', 'prepared_eta_rho': 'eta=(0.10,-0.10), rho=(-0.80,0.80); crossings arise from evolution'},
        {'id': 'MODE_CONVERSION_BACKREACTION_LEDGER_REVERSAL_RECURRENCE', 'prepared_eta_rho': 'same conversion state; coupled energy/work and controlled reversal'},
        {'id': 'MODE_CONVERSION_COVARIANCE_REFINEMENT_DOMAIN_NONUNIFORM_SOURCE_OFF_WAKE', 'prepared_eta_rho': 'same conversion state with frozen controls'},
        {'id': 'COUNT_CHANGING_PRIMITIVE_BOUNDARIES', 'prepared_eta_rho': 'not executed: creation/annihilation and fusion/splitting lack a predeclared count-changing state map'},
    ]
    internal_cells = [
        {'id': 'REPRESENTATION_INVARIANT_STRUCTURAL_OBSERVABLES', 'observables': ['energy_residual', 'momentum_work_residual', 'wake_l2', 'separation_final']},
        {'id': 'PERTURBATION_AND_COUPLING_RESPONSE', 'observables': ['finite paired-state perturbation response', 'source-off medium-packet response']},
        {'id': 'HOLONOMY_AND_CLOSED_CYCLE', 'observables': ['controlled reversal residual', 'closed-cycle endpoint residual']},
        {'id': 'NONLINEAR_AND_NONUNIFORM_MEDIUM_CONTROLS', 'observables': ['finite-amplitude response', 'stiffness/preload-gradient transport response']},
        {'id': 'COVARIANCE_REFINEMENT_FINITE_DOMAIN', 'observables': ['uniform translation/reflection/axis-swap', 'dt refinement', 'finite domain']},
        {'id': 'SOURCE_OFF_WAKE_CONTROL', 'observables': ['prepared-only packet wake and target response']},
        {'id': 'HELD_OUT_CROSS_PREDICTION', 'observables': ['held-out transverse paired-state and closed-cycle response']},
    ]
    contract = {
        'EMX066_SELECTOR': 'SECTOR_CHANGE_AND_INTERNAL_DISTINGUISHABILITY_WIDE_NET',
        'FROZEN_BEFORE_RESULTS': True,
        'mode': 'TWO_EXPLICITLY_SEPARATED_FINITE_DETERMINISTIC_ARTIFACT_HASHED_NON_BLOCKING_BRANCHES',
        'classification_vocabulary': ['SUPPORTED_IN_SCOPE', 'CONTRADICTED_IN_SCOPE', 'DISTINCT_OBSERVABLE_BEHAVIOR', 'NOT_ASSESSED', 'UNDEFINED_PRIMITIVE_BOUNDARY'],
        'preservation_rule': 'EMX010-065 outcomes, labels, files, and class viability are retained verbatim. EMX066 does not fit, reselect, eliminate, or physically validate any class.',
        'branch_A_sector_changing_two_pattern_extensions': {'eligible_extensions': sector_extensions, 'cells': sector_cells,
            'unrepresented_transition_boundaries': {'creation_annihilation': 'UNDEFINED_PRIMITIVE_BOUNDARY: no count-changing coordinate/reservoir is declared.', 'fusion_splitting': 'UNDEFINED_PRIMITIVE_BOUNDARY: no one-to-two or two-to-one state map is declared.'},
            'boundary_rule': 'A periodic boundary is a boundary condition only. It is never counted as a transition.'},
        'branch_B_internal_distinguishability': {'eligible_closures': closure_alternatives, 'cells': internal_cells,
            'representation_invariant_rule': 'Only listed structural observables, defined without A/B coordinate names and evaluated on matched numerical states, may enter comparison.',
            'nonidentifiability_rule': 'If all predeclared observables agree within the frozen comparison tolerance, record FINITE_SCOPE_NONIDENTIFIABILITY; do not infer universal equivalence.'},
        'frozen_numerics': {'n': 8, 'dt': 0.006, 'steps': 36, 'gamma': 0.35, 'elastic_k': 1.0, 'pattern_radius': 1.35, 'finite_difference_epsilon': 0.0002, 'identity_tolerance': 8e-7, 'comparison_tolerance': 2e-9, 'stiffness_gradient': 0.20, 'preload_gradient': 0.006, 'mode_omega': 1.0},
        'prohibitions': {'NO_DEV167_OR_LAB_GIT_MODIFICATION_IMPORT_OR_EXECUTION': True, 'NO_DESTRUCTIVE_OR_EXTERNAL_ACTION': True, 'NO_E_B_QED_MAPPING': True, 'NO_PHYSICAL_VALIDITY_OR_UNIVERSAL_ARROW_CLAIM': True, 'NO_FITTING_RESELECTION_OR_OUTCOME_DEPENDENT_SELECTION': True, 'NO_EXTERNAL_EMPIRICAL_MAPPING': True, 'NO_HIDDEN_NORMALIZATION': True, 'NO_EXTERNAL_FORCING_AFTER_PREPARATION': True},
        'input_sha256': {path: digest(path) for path in inputs},
    }
    contract['contract_sha256'] = canonical(contract)
    O.mkdir(parents=True, exist_ok=True)
    (O / 'frozen_sector_change_and_internal_distinguishability_wide_net_contract.json').write_text(json.dumps(contract, indent=2, sort_keys=True) + '\n')
    registry = {'contract_sha256': contract['contract_sha256'], 'branches_explicitly_separated': True,
                'branch_A': {'extensions': sector_extensions, 'cells': sector_cells, 'all_cells_predeclared': True},
                'branch_B': {'closures': closure_alternatives, 'cells': internal_cells, 'all_cells_predeclared': True},
                'result_free_registry': True}
    (O / 'finite_registry.json').write_text(json.dumps(registry, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
