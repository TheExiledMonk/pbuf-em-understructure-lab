#!/usr/bin/env python3
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]; M=R/'matrix'
def load(n): return json.loads((M/n).read_text())
def main():
 candidates=load('candidate_registry.json'); ids={x['candidate_id'] for x in candidates}
 assert candidates and len(ids)==len(candidates)
 for c in candidates:
  for k in ('origin_files','mechanics_contract','information_loss','independence_group','admissibility_status'): assert c.get(k) not in (None,'')
  assert not ('RESULT' in ' '.join(c.get('admission_basis',[])))
 for name in ('historical_matrix.json','forward_matrix.json'):
  for cell in load(name):
   assert cell['candidate_id'] in ids and cell['status'] and cell['evidence'] and cell['frozen_conditions']
 for c in candidates:
  if c['admissibility_status']=='FUTURE_GATE': assert not any(x['candidate_id']==c['candidate_id'] for x in load('forward_matrix.json'))
 print('EMX001 matrix validation passed')
if __name__=='__main__': main()
