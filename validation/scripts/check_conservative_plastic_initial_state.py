#!/usr/bin/env python3
"""Verify initial fluid mass with nonzero deformation, pressure and plastic history."""
import csv
import json
from pathlib import Path
import subprocess
import numpy as np
from check_poroplastic_mandel import mineral
from run_provenance import observe, complete
ROOT = Path(__file__).resolve().parents[2]
out = ROOT/'.agent-runtime/conservative-initial-state'
out.mkdir(parents=True, exist_ok=True)
command = [str(ROOT/'moose_app/nonlinear_biot_ad-opt'), '-i',
           str(ROOT/'moose_app/test/tests/poroplastic_mandel/compression.i'),
           str(ROOT/'moose_app/test/tests/poroplastic_mandel/initial_state.i'),
           'mesh_nx=2', 'mesh_ny=1', 'cohesion_pa=1e12', f'Outputs/file_base={out}/plastic', '--color', 'off']
observed = observe(ROOT/'moose_app/nonlinear_biot_ad-opt', command)
with (out/'plastic.log').open('w') as stream:
    subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, check=True)
with (out/'plastic.csv').open() as stream:
    rows = list(csv.DictReader(stream))
J, p, ap = .99, 1e6, 1.01
expected = .1*(J-.9*mineral(J/ap,p))*1000*np.exp(p/8e9)
assert len(rows) == 3 and float(rows[0]['time']) == 0
errors = dict(mass=0., pressure=0., plastic_history=0.)
for row in rows:
    errors['mass'] = max(errors['mass'], abs(float(row['mass_initial_check'])-expected))
    errors['pressure'] = max(errors['pressure'], abs(float(row['pressure_initial_check'])-p)/p)
    errors['plastic_history'] = max(errors['plastic_history'], abs(float(row['plastic_initial_check'])-ap))
assert max(errors.values()) < 1e-10, errors
record = dict(accepted=True, initial_J=J, initial_pressure=p, initial_plastic_distention=ap,
              independent_mass=float(expected), errors=errors,
              execution_provenance=complete(observed, [out/'plastic.csv']))
(out/'plastic_verification.json').write_text(json.dumps(record, indent=2)+'\n')
print('PASS prescribed plastic initial history and sealed mass', errors)
