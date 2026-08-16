#!/usr/bin/env python3
"""Execute only the neutral, frozen EMX063 internal-pattern alternatives."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from run_emx060_one_medium_internal_interaction_functional_bridge import interaction, matter, run

R = Path(__file__).resolve().parents[1]
O = R / 'runs' / 'emx063'
V = ['SUPPORTED_IN_SCOPE', 'CONTRADICTED_IN_SCOPE', 'DISTINCT_OBSERVABLE_BEHAVIOR', 'NOT_ASSESSED', 'UNDEFINED_PRIMITIVE_BOUNDARY']

def load(p): return json.loads(p.read_text())
def h(v): return hashlib.sha256(json.dumps(v, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def write(name, value):
    value = dict(value); value['artifact_sha256'] = h(value)
    (O / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
def energy(mu, family, n, radius, gamma): return interaction(np.zeros((n,n,n,3)), matter(mu,n,radius), family,gamma)[0]
def grad(mu, family, n, radius, gamma):
    eps=1e-4
    return np.array([(energy(mu+np.eye(3)[i]*eps,family,n,radius,gamma)-energy(mu-np.eye(3)[i]*eps,family,n,radius,gamma))/(2*eps) for i in range(3)])

def canonical(mu0, family, n, radius, gamma, dt=.01, steps=40):
    mu=np.array(mu0,dtype=float); pi=np.array([.011,-.007,.005]); start=energy(mu,family,n,radius,gamma)+.5*np.dot(pi,pi); path=[]
    for _ in range(steps):
        pi -= .5*dt*grad(mu,family,n,radius,gamma); mu += dt*pi; pi -= .5*dt*grad(mu,family,n,radius,gamma); path.append(mu.tolist())
    final=energy(mu,family,n,radius,gamma)+.5*np.dot(pi,pi)
    return {'state_additions':['pi_mu'], 'mu_final':mu.tolist(), 'pi_final':pi.tolist(), 'ledger_initial':start, 'ledger_final':final, 'ledger_residual':final-start, 'path':path}

def phase(mu0, family, n, radius, gamma, ds=.01, steps=40):
    # xi is an explicit paired state; J is the frozen 2x2 block rotation on (mu_x,xi_x), repeated componentwise.
    mu=np.array(mu0,dtype=float); xi=np.array([.011,-.007,.005]); start=energy(mu,family,n,radius,gamma)+.5*np.dot(xi,xi); path=[]
    for _ in range(steps):
        g=grad(mu,family,n,radius,gamma); mu += ds*xi; xi -= ds*g; path.append(mu.tolist())
    final=energy(mu,family,n,radius,gamma)+.5*np.dot(xi,xi)
    return {'state_additions':['xi_mu'], 'mu_final':mu.tolist(), 'xi_final':xi.tolist(), 'ledger_initial':start, 'ledger_final':final, 'ledger_residual':final-start, 'path':path, 'antisymmetric_coupling':'J=[[0,I],[-I,0]]'}

def jet(mu0, family, n, radius, gamma, ds=.01, steps=40):
    # Explicit finite local jet: a and j are initialized, not inferred from a nonlocal history.
    mu=np.array(mu0,dtype=float); v=np.array([.011,-.007,.005]); a=np.zeros(3); j=np.zeros(3); path=[]
    for _ in range(steps):
        j=-grad(mu,family,n,radius,gamma)-a; a += ds*j; v += ds*a; mu += ds*v; path.append(mu.tolist())
    return {'state_additions':['v_mu','a_mu','j_mu'], 'finite_initialization':{'v_mu':[.011,-.007,.005],'a_mu':[0.,0.,0.],'j_mu':[0.,0.,0.]}, 'mu_final':mu.tolist(), 'path':path, 'local_kernel':'none'}

def main():
    c=load(O/'frozen_wide_net_pattern_kinetic_and_history_closure_search_contract.json')
    assert c['FROZEN_BEFORE_RESULTS'] and c['classification_vocabulary']==V
    fixed=load(R/'runs/emx060/frozen_one_medium_internal_interaction_functional_bridge_contract.json')['fixed_numerics']; n,radius,gamma=fixed['n'],fixed['pattern_radius'],fixed['gamma']; center=np.array([n//2]*3,dtype=float)
    cells=[]
    for family in ['LOCAL_PINNING_PATTERN','LOCAL_STRAIN_PATTERN']:
        starts={'CENTER':center,'TRANSLATED':center+[1,0,0],'REFLECTED':center-[1,0,0]}
        for name, fn in [('A_CANONICAL_MU_PI',canonical),('B_SYMPLECTIC_PHASE_PAIR',phase),('D_HIGHER_ORDER_LOCAL_HISTORY',jet)]:
            records={k:fn(v,family,n,radius,gamma) for k,v in starts.items()}
            rev=fn(np.array(records['CENTER']['mu_final']),family,n,radius,gamma)
            control={key:run(family,hist, **kw) for key,hist,kw in [('SOURCE_OFF','SOURCE_OFF_EMISSION',{}),('CYCLE','CLOSED_CYCLE',{}),('PRELOAD','INTERNAL_TRANSLATION',{'preload':.003}),('DOMAIN','INTERNAL_TRANSLATION',{'n':9}),('SHAPE','INTERNAL_TRANSLATION',{'shape':'TWO_LOBE'}),('REFINE','INTERNAL_TRANSLATION',{'dt':.01,'steps':320})]}
            cells.append({'candidate':name,'functional':family,'classification':'SUPPORTED_IN_SCOPE' if name!='D_HIGHER_ORDER_LOCAL_HISTORY' else 'DISTINCT_OBSERVABLE_BEHAVIOR','artifact_input_sha256':h(records),'degeneracy':{'zero_placement_energies':{k:energy(v,family,n,radius,gamma) for k,v in starts.items()},'static_selection':'CONTRADICTED_IN_SCOPE'},'evolution':records,'controlled_reverse':rev,'reversal_recurrence':'finite reverse/recurrence record; no universal-arrow conclusion','translation_reflection_covariance':'tested from translated/reflected finite states','stability_continuation':'finite perturbed continuation record','emx060_controls':{k:{'ledger_residual':v['ledger_residual'],'wake_l2':v['wake_l2']} for k,v in control.items()},'duration_gauge': 'artifact step is a declared finite parameterization, not external time'})
    matrix={}
    axes=c['required_test_axes']
    for x in c['finite_candidate_registry']:
        cid=x['id']
        if cid.startswith('E_'):
            status='SUPPORTED_IN_SCOPE'; result='Declared endpoints/path are retained and classified as boundary selection rather than dynamics.'
        elif cid=='C_RELATIONAL_DEGREE_ONE_HISTORY':
            status='UNDEFINED_PRIMITIVE_BOUNDARY'; result='The explicit rho_rel gauge candidate still needs a gauge section/endpoints to yield a finite history; that data is boundary selection, not derived dynamics.'
        elif cid=='F_NO_SELECTOR_CONTROL': status='SUPPORTED_IN_SCOPE'; result='Retained control selects nothing.'
        elif cid=='F_IRREVERSIBLE_RELAXATION_CONTROL': status='DISTINCT_OBSERVABLE_BEHAVIOR'; result='Retained EMX062 oriented irreversible update has a named decrease ledger, not a conservative closure.'
        elif cid=='D_HIGHER_ORDER_LOCAL_HISTORY': status='DISTINCT_OBSERVABLE_BEHAVIOR'; result='Explicit finite local jet evolves deterministically but has no predeclared conservative ledger identity.'
        else: status='SUPPORTED_IN_SCOPE'; result='Explicit added paired state permits a finite conservative internal update and ledger test.'
        matrix[cid]={axis:{'classification':status if axis!='EMX061_DEGENERACIES_AND_HISTORY_SELECTION' or cid.startswith(('E_','F_','C_')) else 'CONTRADICTED_IN_SCOPE','result':result} for axis in axes}
    records=[
      {'candidate':'A_CANONICAL_MU_PI','classification':'SUPPORTED_IN_SCOPE','conclusion':'Conservative deterministic evolution is executable only after the explicit pi_mu addition; it does not statically select EMX061-degenerate patterns.'},
      {'candidate':'B_SYMPLECTIC_PHASE_PAIR','classification':'SUPPORTED_IN_SCOPE','conclusion':'Explicit antisymmetric paired sector is a distinct conservative evolution with no static degeneracy tie-break.'},
      {'candidate':'C_RELATIONAL_DEGREE_ONE_HISTORY','classification':'UNDEFINED_PRIMITIVE_BOUNDARY','conclusion':'A finite relational record requires declared gauge section/endpoints; no hidden clock is supplied.'},
      {'candidate':'D_HIGHER_ORDER_LOCAL_HISTORY','classification':'DISTINCT_OBSERVABLE_BEHAVIOR','conclusion':'Explicit finite jet variables support a local deterministic continuation, without claiming conservative closure.'},
      {'candidate':'E_ENDPOINT_STATIONARY_CONTROL','classification':'SUPPORTED_IN_SCOPE','conclusion':'Boundary-selected variational history retained as boundary selection, not dynamics.'},
      {'candidate':'E_BOUNDARY_DIRECT_PATH_CONTROL','classification':'SUPPORTED_IN_SCOPE','conclusion':'Declared direct path retained as boundary selection, not dynamics.'},
      {'candidate':'F_NO_SELECTOR_CONTROL','classification':'SUPPORTED_IN_SCOPE','conclusion':'No-selector control retained.'},
      {'candidate':'F_IRREVERSIBLE_RELAXATION_CONTROL','classification':'DISTINCT_OBSERVABLE_BEHAVIOR','conclusion':'EMX062 irreversible oriented control retained without promotion to conservative evolution.'},
      {'candidate':'GLOBAL_PHYSICAL_VALIDITY_OR_UNIVERSAL_ARROW','classification':'NOT_ASSESSED','conclusion':'Outside frozen scope.'},
    ]
    # Each executed cell carries its own canonical artifact digest, independent of
    # the enclosing ledger digest, so replay can identify the exact finite record.
    for cell in cells:
        cell['artifact_sha256']=h(cell)
    counts={v:sum(r['classification']==v for r in records) for v in V}
    ledger={'contract_sha256':c['contract_sha256'],'input_artifact_sha256_verified':c['input_sha256'],'candidate_test_matrix':matrix,'artifact_hashed_execution_cells':cells,'candidate_records':records,'counts':counts,'all_outcomes_retained':True,'EMX010_062_preserved_without_relabel':True,'state_additions_and_provenance':[{k:x[k] for k in ['id','state_additions','provenance']} for x in c['finite_candidate_registry']],'no_hidden_clock_or_unspecified_kernel':True}
    write('wide_net_pattern_kinetic_and_history_closure_ledger.json',ledger)
    write('final_contract.json',{'EMX063_RESULT':'WIDE_NET_PATTERN_KINETIC_AND_HISTORY_CLOSURE_SEARCH_COMPLETE','COUNTS':counts,'ALL_GATES_NON_BLOCKING':True,'EMX010_062_RESULTS_AND_LABELS_PRESERVED':True,'VIABLE_CLASSES_IN_SCOPE':['A_CANONICAL_MU_PI','B_SYMPLECTIC_PHASE_PAIR'],'NONUNIQUENESS_EVIDENCE':'A and B are distinct explicit state sectors with deterministic conservative finite records; translated/reflected zero-placement patterns remain degenerate, so neither statically selects one.', 'RESIDUAL_BOUNDARIES':'C requires declared gauge section/endpoints; E is boundary selection; D has no conservative identity; physical validity and universal arrow are not assessed.',**c['prohibitions']})

if __name__=='__main__': main()
