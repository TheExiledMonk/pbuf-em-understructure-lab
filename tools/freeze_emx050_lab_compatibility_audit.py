#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'runs'/'emx050'
def h(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def d(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
 evidence=[
  {'id':'LAB_README','path':'README.md','sha1':'fef5ee2b4a87363772ab30f6eb0cce903c21358a','statement':'External repository identity/read-only evidence only.'},
  {'id':'LAB_TRANSPORT001','path':'runs/em_transport001/em_transport001_report.md','sha1':'299d30d5bac7615a7f2f509be7d0643b77362484','statement':'V11/CORE-001 has static nearest-neighbour scalar coupling and overdamped evolution, not a Maxwell curl pair; missing closure is positive momentum density or equivalent symplectic structure.'},
  {'id':'LAB_TRANSPORT_RESEARCH001','path':'runs/transport_research001/transport_research001_report.md','sha1':None,'statement':'Mechanical/elastic transport needs local state, neighbor coupling, restoring, and inertial resistance; a Maxwell route is structurally incompatible with a scalar-triplet static model.'},
  {'id':'LAB_INERTIA001','path':'runs/inertia001/inertia_origin_report.md','sha1':None,'statement':'Kinetic sector remains open and must meet positivity, conservation, reversal, and gauge constraints.'},
  {'id':'LAB_EVOLUTION001','path':'runs/evolution_law001/native_law_of_successive_state_evolution.md','sha1':'ad7627cd9e71ba4878c03254b5a6dd6d728132a3','statement':'History-selection/evolution rule is unselected.'},
  {'id':'LAB_SOURCE_PROJECTION001','path':'runs/source_projection001/source_projection_report.md','sha1':'1e3e9a7ca1cf17ef5daa65a8e22260506d2d7337','statement':'Matter-to-placement load requires a normalized universal interaction/virtual-work principle and is not selected by current ontology.'}]
 files=['runs/emx047/final_contract.json','runs/emx048/final_contract.json','runs/emx049/final_contract.json','runs/emx049/frozen_new_reference_geometry_primitive_contract.json','runs/emx049/cell_registry_and_results.json','runs/emx041/shared_observer_definition.json']
 c={'EMX050_SELECTOR':'READ_ONLY_LAB_COMPATIBILITY_AND_DIRECTION_AUDIT','FROZEN_BEFORE_RESULTS':True,'external_evidence_mode':'USER_SUPPLIED_HASH_PINNED_DOCUMENT_STATEMENTS_ONLY; documents were not opened, copied, imported, or executed. SHA-1 strings are identifiers as supplied, not newly verified external content.','external_evidence':evidence,'families':['HISTORICAL_DEV167','LOCAL_NEUTRAL_HARMONIC_PERIODIC_N6','EMX049_NEW_NEUTRAL_REFERENCE_GEOMETRY'],'requirements':['static_local_coupling','restoring_structure','finite_reference_geometry','kinetic_inertial_or_symplectic_sector','conservation_reversibility_evidence','history_selection','universal_matter_medium_work_source_projection'],'classification_vocabulary':['SUPPORTED_BY_REPO_EVIDENCE','COMPATIBLE_BUT_UNDERDETERMINED','INCOMPATIBLE','NOT_ASSESSED','EXTERNAL_REQUIREMENT_UNIMPLEMENTED'],'rules':{'missing_is_not_rejection':True,'observer_not_physical_validity':True,'historical_classifications_unchanged':True,'no_maxwell_or_E_B_QED_inference':True},'input_sha256':{p:h(p) for p in files},'prohibitions':{'NO_DEV167_MODIFICATION':True,'NO_LAB_GIT_IMPORT_EXECUTION_COPY_OR_MODIFICATION':True,'NO_FITTING':True,'NO_HIDDEN_CHOICES':True,'NO_PRIOR_CLASSIFICATION_CHANGES':True,'NO_E_B_QED_MAPPING':True}}
 c['contract_sha256']=d(c);O.mkdir(parents=True,exist_ok=True);(O/'frozen_lab_compatibility_audit_contract.json').write_text(json.dumps(c,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
