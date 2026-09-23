#!/usr/bin/env python3
"""Curate the completed oscillation diagnosis and isotropic-hardening correction.

Run the named control and corrected simulations first. This script fails on
partial histories and never replaces a solver result with smoothed fields.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.io import netcdf_file

from check_poroplastic_acoustic import replay
from check_poroplastic_mandel import ROOT, RUNTIME, read, run, field_sensitivity, spatial_structure, mass_metrics


def nodal_transverse_variation(name):
    with netcdf_file(RUNTIME/(name+'.e'), mmap=False) as data:
        names = [r.tobytes().decode().strip('\0 ') for r in data.variables['name_nod_var'][:]]
        x, y = (data.variables['coord'+axis][:].copy() for axis in ('x', 'y'))
        order = np.lexsort((x, y))
        nx, ny = len(set(x)), len(set(y))
        result = {}
        for key in ('p',):
            values = data.variables[f'vals_nod_var{names.index(key)+1}'][:].copy()
            values = values[:, order].reshape(-1, ny, nx)
            variation = values-values.mean(axis=1, keepdims=True)
            result[key] = float(np.sqrt(np.mean(variation**2, axis=(1, 2))).max())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--curate', action='store_true')
    parser.add_argument('--run', action='store_true', help='Run the complete control and correction matrix')
    parser.add_argument('--reuse', action='store_true', help='Reuse only signature-matched completed simulations')
    args = parser.parse_args()
    cases = {
        'baseline_perfect_plastic': (0., .4),
        'diagnostic_half_dt_mpi': (0., .4),
        'diagnostic_associated_mpi': (0., .6),
        'hardening_coarse': (.1, .4),
        'hardening_fine': (.1, .4),
        'hardening_half_dt': (.1, .4),
    }
    records = {}
    for name, (modulus, beta) in cases.items():
        nx, ny = (20, 2) if name == 'hardening_coarse' else (40, 4)
        dt = .00125 if 'half_dt' in name else .0025
        command = None
        if args.run:
            _, command = run(name, nx=nx, ny=ny, dt=dt,
                             extra=(f'hardening_modulus_pa={modulus*1.e9:g}',
                                    f'dilation_slope={beta:g}'), reuse=args.reuse)
        rows = read(RUNTIME/(name+'.csv'))
        if abs(rows[-1]['time']-.7) > 1.e-9:
            raise AssertionError(f'{name}: incomplete simulation')
        records[name] = dict(
            configuration=dict(nx=nx, ny=ny, dt=dt, end_time=.7,
                               hardening_modulus_Pa=modulus*1.e9, dilation_slope=beta),
            acoustic=replay(name, modulus, beta, [(x, .05) for x in (.125, .5, .875)]),
            spatial_structure=spatial_structure(name), mass=mass_metrics(rows),
            maximum_nodal_transverse_rms=nodal_transverse_variation(name),
            final_average_delta_B=rows[-1]['delta_b_average'],
            csv_sha256=hashlib.sha256((RUNTIME/(name+'.csv')).read_bytes()).hexdigest(),
        )
        if command is not None:
            records[name]['command'] = command
        manifest = RUNTIME/(name+'.run.json')
        if manifest.exists():
            records[name]['run_manifest'] = json.loads(manifest.read_text())
        print('Analyzed', name, flush=True)
    baseline = records['baseline_perfect_plastic']
    if not any(r['determinant_changes_sign'] for r in baseline['acoustic']['acoustic']):
        raise AssertionError('Original loss of ellipticity was not reproduced')
    for name in ('hardening_coarse', 'hardening_fine', 'hardening_half_dt'):
        record = records[name]
        if min(r['minimum_determinant_GPa2'] for r in record['acoustic']['acoustic']) <= 0.:
            raise AssertionError(f'{name}: sampled loss of ellipticity remains')
        for field, tolerance in [('delta_b', 1.e-8), ('ap', 1.e-7), ('gamma', 1.e-8)]:
            if record['spatial_structure'][field]['maximum_transverse_rms'] > tolerance:
                raise AssertionError(f'{name}: unresolved transverse {field} variation')
        for field, tolerance in [('p', 1.e-3)]:
            if record['maximum_nodal_transverse_rms'][field] > tolerance:
                raise AssertionError(f'{name}: unresolved transverse nodal {field} variation')
    spatial = field_sensitivity('hardening_coarse', 'hardening_fine')
    temporal = field_sensitivity('hardening_fine', 'hardening_half_dt')
    if max(r['maximum'] for r in temporal.values()) > 5.e-6:
        raise AssertionError('Corrected fine-grid time-step difference exceeds 5e-6')
    coarse = records['hardening_coarse']['spatial_structure']['delta_b']['final_x_second_difference_rms']
    fine = records['hardening_fine']['spatial_structure']['delta_b']['final_x_second_difference_rms']
    if fine > .6*coarse:
        raise AssertionError('Corrected spatial second differences fail refinement')
    sources = [Path(__file__), ROOT/'validation/scripts/check_poroplastic_acoustic.py',
               ROOT/'validation/scripts/check_poroplastic_mandel.py',
               ROOT/'moose_app/src/materials/ADImplicitPoroplasticBiotMaterial.C',
               ROOT/'moose_app/include/materials/ADImplicitPoroplasticBiotMaterial.h',
               ROOT/'moose_app/test/tests/poroplastic_mandel/compression.i']
    sources.append(ROOT/'validation/scripts/run_provenance.py')
    result = dict(status='complete', accepted=True, cases=records,
                  corrected_spatial_differences=spatial, corrected_temporal_differences=temporal,
                  assumptions=['fixed-pressure in-plane active acoustic tangent',
                               'central Gauss points at three X positions; not a global stability proof',
                               'synthetic uncalibrated hardening modulus 100 MPa'],
                  source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources})
    output = ROOT/'validation/poroplastic_spatial_stability.json' if args.curate else RUNTIME/'spatial_stability.json'
    output.write_text(json.dumps(result, indent=2)+'\n')
    print('PASS spatial stability diagnosis and hardening correction', output.relative_to(ROOT))


if __name__ == '__main__':
    main()
