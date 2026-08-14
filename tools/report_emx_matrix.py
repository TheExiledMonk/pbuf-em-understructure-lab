#!/usr/bin/env python3
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
c=json.loads((root/'matrix/candidate_registry.json').read_text())
h=json.loads((root/'matrix/historical_matrix.json').read_text())
f=json.loads((root/'matrix/forward_matrix.json').read_text())
print(json.dumps({'active_candidate_count':sum(x['admissibility_status']=='ACTIVE' for x in c),'historical_control_count':sum(x['admissibility_status']=='HISTORICAL_CONTROL' for x in c),'blocked_candidate_count':sum(x['admissibility_status'].startswith('BLOCKED') for x in c),'future_gate_count':sum(x['admissibility_status']=='FUTURE_GATE' for x in c),'historical_test_cells_imported':len(h),'forward_not_run_count':sum(x['status']=='NOT_RUN' for x in f)},indent=2))
