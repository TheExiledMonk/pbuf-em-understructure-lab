#!/usr/bin/env python3
"""Freeze the repository-local finite EMX065 bridge before any results exist."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
O = R / 'runs' / 'emx065'


def digest(path): return hashlib.sha256((R / path).read_bytes()).hexdigest()
def canonical(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def main():
    inputs = ['runs/emx064/frozen_wide_net_conservative_pattern_closure_discriminator_contract.json',
              'runs/emx064/finite_registry.json', 'runs/emx064/wide_net_conservative_pattern_closure_discriminator_ledger.json',
              'runs/emx064/final_contract.json', 'runs/emx060/frozen_one_medium_internal_interaction_functional_bridge_contract.json']
    classes = [
        {'id': 'A_CANONICAL_TWO_MU_PI', 'extends': 'A_CANONICAL_MU_PI', 'state': '(u,p,mu_1,pi_1,mu_2,pi_2)', 'identification': 'pi_i are canonical conservative momenta'},
        {'id': 'B_SYMPLECTIC_TWO_PHASE_PAIR', 'extends': 'B_SYMPLECTIC_PHASE_PAIR', 'state': '(u,p,mu_1,xi_1,mu_2,xi_2)', 'identification': 'xi_i are the declared paired phase coordinates'},
    ]
    alternatives = [
        {'id': 'A_LOCAL_PINNING_TWO_PATTERN', 'class': classes[0]['id'], 'functional': 'LOCAL_PINNING_PATTERN'},
        {'id': 'A_LOCAL_STRAIN_TWO_PATTERN', 'class': classes[0]['id'], 'functional': 'LOCAL_STRAIN_PATTERN'},
        {'id': 'B_LOCAL_PINNING_TWO_PATTERN', 'class': classes[1]['id'], 'functional': 'LOCAL_PINNING_PATTERN'},
        {'id': 'B_LOCAL_STRAIN_TWO_PATTERN', 'class': classes[1]['id'], 'functional': 'LOCAL_STRAIN_PATTERN'},
    ]
    cells = [
        {'id': 'TWO_PATTERN_COLLISION_CONTROLS', 'controls': ['impact', 'separation', 'direction'], 'prepared': 'two localized coordinate/momentum pairs', 'boundary': 'periodic finite lattice'},
        {'id': 'BINDING_TRANSIENT_FUSION_SPLITTING_CLASSIFICATION', 'controls': ['approach', 'separation threshold'], 'prepared': 'two localized pairs', 'boundary': 'classification only from represented two-coordinate state'},
        {'id': 'SOURCE_OFF_WAKE_ABSORPTION_SCATTERING', 'controls': ['prepared medium packet', 'two-pattern target'], 'prepared': 'initial momentum only; no later source', 'boundary': 'periodic finite lattice'},
        {'id': 'RECIPROCAL_LEDGER_REVERSAL_RECURRENCE', 'controls': ['state reversal', 'closed cycle'], 'prepared': 'declared finite state', 'boundary': 'periodic finite lattice'},
        {'id': 'UNIFORM_COVARIANCE_AND_ROBUSTNESS', 'controls': ['translation', 'reflection', 'rotation', 'refinement', 'domain', 'source shape'], 'prepared': 'matched transformations', 'boundary': 'uniform periodic control'},
        {'id': 'NONUNIFORM_GRADIENT_TRANSPORT', 'controls': ['stiffness gradient', 'preload gradient', 'propagation', 'reflection', 'refraction'], 'prepared': 'frozen smooth profiles and two-pattern/medium packets', 'boundary': 'periodic finite lattice; profile is part of medium'},
        {'id': 'HELD_OUT_OBSERVABLES', 'controls': ['held-out direction', 'closed cycle'], 'prepared': 'not used for any selection', 'boundary': 'periodic finite lattice'},
    ]
    contract = {
        'EMX065_SELECTOR': 'TWO_PATTERN_INTERACTION_AND_NONUNIFORM_MEDIUM_BRIDGE', 'FROZEN_BEFORE_RESULTS': True,
        'mode': 'NEW_REPOSITORY_LOCAL_FINITE_BRIDGE_NON_BLOCKING',
        'classification_vocabulary': ['SUPPORTED_IN_SCOPE', 'CONTRADICTED_IN_SCOPE', 'DISTINCT_OBSERVABLE_BEHAVIOR', 'NOT_ASSESSED', 'UNDEFINED_PRIMITIVE_BOUNDARY'],
        'preservation_rule': 'EMX010-064 outcomes, labels, files, and class viability are retained verbatim; EMX065 does not fit, reselect, eliminate, or establish physical validity or universal equivalence.',
        'eligible_emx064_classes': classes, 'neutral_alternatives': alternatives, 'predeclared_artifact_hashed_cells': cells,
        'state_rule': 'Only u,p and two explicitly declared localized pattern coordinate/paired-state pairs are represented. Fusion/splitting are classifications of these two tracked coordinates, never creation or deletion of a species.',
        'initialization_normalization': {'coordinates': [[2.25, 4.0, 4.0], [5.75, 4.0, 4.0]], 'paired_states': [[0.045, 0, 0], [-0.045, 0, 0]], 'medium_packet': 0.03, 'normalization': 'fixed amplitudes and profiles; no fitting or reselection'},
        'boundaries': {'geometry': 'periodic N^3 lattice', 'two_pattern_classification': {'bound': 'separation <= 1.20 at final and midpoint', 'separated': 'separation >= 2.00 at final', 'otherwise': 'transient interaction'}, 'finite_domain_note': 'Finite periodic recurrence is boundary-conditioned, not an arrow claim.'},
        'frozen_numerics': {'n': 8, 'dt': 0.006, 'steps': 36, 'elastic_k': 1.0, 'gamma': 0.35, 'pattern_radius': 1.35, 'finite_difference_epsilon': 0.0002, 'identity_tolerance': 8e-7, 'comparison_tolerance': 2e-9, 'stiffness_gradient': 0.20, 'preload_gradient': 0.006},
        'medium_functional': 'H = sum |p|^2/2 + sum directed-bonds k(x+1/2)|u(x+1)-u(x)|^2/2 + sum_i [A_int(u,m(mu_i)) + |pair_i|^2/2]. k(x+1/2)=k0[1+s cos(2pi(x+1/2)/N)]; preload(x)=a sin(2pi x/N) e_x. Both are frozen smooth periodic medium fields, not forcing.',
        'covariance_rule': 'Uniform-medium translation/reflection/axis-swap controls are applicable. In the nonuniform medium, translation is deliberately broken by the frozen profile; y/z reflection and y-z swap remain applicable profile symmetries.',
        'prohibitions': {'NO_DEV167_OR_LAB_GIT_MODIFICATION_IMPORT_OR_EXECUTION': True, 'NO_DESTRUCTIVE_OR_EXTERNAL_ACTION': True, 'NO_E_B_QED_MAPPING': True, 'NO_PHYSICAL_VALIDITY_OR_UNIVERSAL_ARROW_CLAIM': True, 'NO_FITTING_RESELECTION_OR_OUTCOME_RULES': True, 'NO_EXTERNAL_FORCING': True, 'NO_ARBITRARY_MATTER_SPECIES_HIDDEN_ORIGIN_OR_UNREPRESENTED_STATE': True},
        'input_sha256': {path: digest(path) for path in inputs},
    }
    contract['contract_sha256'] = canonical(contract)
    O.mkdir(parents=True, exist_ok=True)
    (O / 'frozen_two_pattern_interaction_and_nonuniform_medium_bridge_contract.json').write_text(json.dumps(contract, indent=2, sort_keys=True) + '\n')
    registry = {'contract_sha256': contract['contract_sha256'], 'eligible_classes': classes, 'neutral_alternatives': alternatives, 'cells': cells, 'all_cells_predeclared': True, 'result_free_registry': True}
    (O / 'finite_registry.json').write_text(json.dumps(registry, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__': main()
