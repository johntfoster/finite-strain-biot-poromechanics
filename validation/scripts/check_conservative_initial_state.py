#!/usr/bin/env python3
"""Check nonzero initial deformation/pressure against independently solved mass."""
import csv
import math
import json
import hashlib
from run_provenance import observe, complete
from pathlib import Path
import subprocess
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[2]
out = ROOT/'.agent-runtime/conservative-initial-state'
out.mkdir(parents=True, exist_ok=True)
command = [str(ROOT/'moose_app/nonlinear_biot_ad-opt'), '-i',
           str(ROOT/'moose_app/test/tests/mandel_implicit_biot/implicit_biot_q2_q1_jacobian.i'),
           str(ROOT/'moose_app/test/tests/mandel_implicit_biot/conservative_initial_state.i'),
           f'Outputs/file_base={out}/sealed', '--color', 'off']
observed = observe(ROOT/'moose_app/nonlinear_biot_ad-opt', command)
with (out/'sealed.log').open('w') as stream:
    subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, check=True)
with (out/'sealed.csv').open() as stream:
    rows = list(csv.DictReader(stream))
J, p, K, Ks, phi0, Kf = 1.02, .25, .5, 2., .5, 3.
alpha = 1-K/(phi0*Ks)
z = math.exp(brentq(lambda x: x+alpha*p*math.exp(x)/Ks-K/(phi0*Ks)*math.log(J), -2, 1, xtol=1e-14))
expected = (J-phi0*z)*math.exp(p/Kf)
assert len(rows) == 3 and float(rows[0]['time']) == 0
for row in rows:
    assert abs(float(row['mass'])-expected) < 1e-10, row
    assert abs(float(row['pressure'])-p) < 1e-10, row
    assert abs(float(row['solid_mass'])-1) < 1e-12, row
print('PASS nonzero initial mass and sealed stationary conservation', expected)

record = {'accepted': True, 'initial_J': J, 'initial_pressure': p, 'independent_mass': expected,
          'maximum_mass_error': max(abs(float(row['mass'])-expected) for row in rows),
          'maximum_pressure_error': max(abs(float(row['pressure'])-p) for row in rows),
          'maximum_solid_mass_error': max(abs(float(row['solid_mass'])-1) for row in rows),
          'execution_provenance': complete(observed, [out/'sealed.csv']),
          'source_sha256': {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                            for path in [Path(__file__),
                              ROOT/'moose_app/test/tests/mandel_implicit_biot/conservative_initial_state.i',
                              ROOT/'moose_app/src/materials/ADReferenceBalanceState.C']}}
(out/'verification.json').write_text(json.dumps(record, indent=2)+'\n')
