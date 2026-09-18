#!/usr/bin/env python3
"""Audit saved Mandel fields without changing constitutive or acceptance tests.

Run after check_poroplastic_mandel.py. Results are diagnostics, not a stability
proof. The second difference is unscaled and measures element-to-element noise.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.io import netcdf_file

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / '.agent-runtime/poroplastic-mandel'


def diagnose(name, parameters, snapshots):
    path = RUNTIME / (name + '.e')
    with netcdf_file(path, mmap=False) as data:
        def names(key):
            return [r.tobytes().decode().strip('\0 ') for r in data.variables[key][:]]

        nodal = names('name_nod_var')
        elemental = names('name_elem_var')
        pressure = data.variables[f'vals_nod_var{nodal.index("p") + 1}'][:].copy()
        times = data.variables['time_whole'][:].copy()
        centers = data.variables['connect1'][:, -1] - 1
        x = data.variables['coordx'][:][centers]
        y = data.variables['coordy'][:][centers]
        order = np.lexsort((x, y))
        nx, ny = len(set(x)), len(set(y))
        alpha = 1 - parameters['K'] / (parameters['phi_s0'] * parameters['Ks'])
        # Q1 pressure stays between corner values on each reference rectangle.
        # The mineral solver enforces 0 < z < e. Together these give a lower
        # bound valid at every quadrature point, without averaging the EOS.
        bound = 1 + alpha * min(0., float(pressure.min())) * np.e / parameters['Ks']
        result = dict(mesh=[nx, ny], minimum_pressure_Pa=float(pressure.min()),
                      minimum_normalized_mineral_tangent_lower_bound=bound,
                      exodus_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                      snapshots={})
        for time in snapshots:
            k = int(np.argmin(abs(times - time)))
            if abs(times[k] - time) > 1.e-9:
                raise ValueError(f'{name}: missing time {time}')
            metrics = {}
            for key in ('delta_b', 'ap', 'gamma'):
                field = data.variables[f'vals_elem_var{elemental.index(key) + 1}eb1'][k].copy()
                field = field[order].reshape(ny, nx)
                metrics[key] = dict(
                    minimum=float(field.min()), maximum=float(field.max()),
                    x_second_difference_rms=float(np.sqrt(np.mean(np.diff(field, n=2, axis=1)**2))),
                    transverse_departure_rms=float(np.sqrt(np.mean((field-field.mean(axis=0))**2))),
                )
            result['snapshots'][str(time)] = metrics
    return result


def main():
    record = json.loads((ROOT / 'validation/poroplastic_mandel_verification.json').read_text())
    mismatches = [p for p, digest in record['source_sha256'].items()
                  if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != digest]
    if mismatches:
        raise ValueError(f'Verified source changed: {mismatches}')
    result = dict(
        evidence_class='saved-field diagnostic; no new simulation or stability proof',
        source_hashes_match=True,
        tangent_bound_assumptions='Q1 pressure on reference rectangles; enforced mineral volume 0<z<e',
        cases={name: diagnose(name, record['parameters'], record['snapshots'])
               for name in ('temporal_coarse', 'fine', 'temporal_fine', 'spatial_fine')},
    )
    output = RUNTIME / 'contour_diagnostics.json'
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(output.relative_to(ROOT))
    for name, case in result['cases'].items():
        print(name, 'tangent lower bound:', case['minimum_normalized_mineral_tangent_lower_bound'],
              'final delta_B second difference:', case['snapshots']['0.7']['delta_b']['x_second_difference_rms'])


if __name__ == '__main__':
    main()
