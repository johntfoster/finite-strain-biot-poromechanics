#!/usr/bin/env python3
"""Replay Q2/Q1 Exodus histories and diagnose the fixed-pressure acoustic tensor.

Stresses and moduli are scaled by 1 GPa. The independent return uses SciPy's
Lambert-W mineral root and symmetric eigendecomposition of the plastic increment.
The acoustic tensor is formed from dP/dF on the active loading branch. Its
negative determinant establishes an in-plane loss of ellipticity; positive
sampled values alone are not a proof of global stability.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.io import netcdf_file
from scipy.optimize import root
from scipy.special import lambertw

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / '.agent-runtime/poroplastic-mandel'
IDENTITY = np.eye(3)
COMPONENTS = ([0, 1, 2, 0, 0, 1], [0, 1, 2, 1, 2, 2])


def evaluate(F, previous, pressure, increment, accumulated, hardening, beta):
    W = np.zeros((3, 3))
    W[COMPONENTS] = increment[:6]
    W = W + W.T - np.diag(np.diag(W))
    eigenvalues, eigenvectors = np.linalg.eigh(W)
    Fp = ((eigenvectors * np.exp(eigenvalues)) @ eigenvectors.T) @ previous
    Fe = F @ np.linalg.inv(Fp)
    J, Je = np.linalg.det(F), np.linalg.det(Fe)
    G, K, Ks, phi0, friction, cohesion = .75, 1., 2.5, .9, .6, .02
    alpha = 1 - K / (phi0 * Ks)
    a = alpha * pressure / Ks
    c = K / (phi0 * Ks) * np.log(Je)
    argument = a * np.exp(c)
    if argument <= -1 / np.e:
        raise ValueError('No stable mineral root')
    z = np.exp(c - lambertw(argument, k=0).real)
    D = Ks + alpha * pressure * z
    B = 1 - K * z / (J * D)
    tau = (G * Je**(-2/3) * (Fe @ Fe.T - np.sum(Fe * Fe) / 3 * IDENTITY)
           + K * (np.log(Je) + alpha * pressure**2 * z**2 / (Ks * D)) * IDENTITY
           + (1-B) * pressure * J * IDENTITY)
    mandel = Fe.T @ tau @ np.linalg.inv(Fe.T)
    mean = -np.trace(mandel) / 3
    dev = mandel + mean * IDENTITY
    q = np.sqrt(1.5 * np.sum(dev * dev))
    direction = 1.5 * dev / max(q, 1.e-30) + beta / 3 * IDENTITY
    residual = np.r_[increment[:6] - increment[6] * direction[COMPONENTS],
                     (q-friction*mean-cohesion-hardening*(accumulated+increment[6]))/G]
    P = (tau-pressure*J*IDENTITY) @ np.linalg.inv(F.T)
    return residual, Fp, P, B


def acoustic(F, previous, pressure, increment, accumulated, hardening, beta, h):
    def state(F, x):
        return evaluate(F, previous, pressure, x, accumulated, hardening, beta)
    rx = np.column_stack([(state(F, increment+np.eye(7)[k]*h)[0]
                           - state(F, increment-np.eye(7)[k]*h)[0])/(2*h)
                          for k in range(7)])
    tangent = np.zeros((2, 2, 2, 2))
    for k in range(2):
        for l in range(2):
            perturbation = np.zeros((3, 3))
            perturbation[k, l] = h
            rf = (state(F+perturbation, increment)[0]-state(F-perturbation, increment)[0])/(2*h)
            dx = np.linalg.solve(rx, -rf)
            tangent[:, :, k, l] = (state(F+perturbation, increment+h*dx)[2][:2, :2]
                                   - state(F-perturbation, increment-h*dx)[2][:2, :2])/(2*h)
    angles = np.linspace(0., np.pi, 721)
    normals = np.array([np.cos(angles), np.sin(angles)]).T
    tensors = np.einsum('ijkl,nj,nl->nik', tangent, normals, normals)
    determinants = np.linalg.det(tensors)
    symmetric = .5*(tensors+tensors.transpose(0, 2, 1))
    return dict(minimum_determinant_GPa2=float(determinants.min()),
                maximum_determinant_GPa2=float(determinants.max()),
                determinant_changes_sign=bool(determinants.min() < 0. < determinants.max()),
                angle_degrees=float(angles[determinants.argmin()]*180/np.pi),
                minimum_symmetric_eigenvalue_GPa=float(np.linalg.eigvalsh(symmetric).min()))


def replay(case, hardening, beta, points, validate_samples=False):
    path = RUNTIME / (case+'.e')
    with netcdf_file(path, mmap=False) as data:
        names = [r.tobytes().decode().strip('\0 ') for r in data.variables['name_nod_var'][:]]
        fields = {k: data.variables[f'vals_nod_var{names.index(k)+1}'][:].copy()
                  for k in ('p', 'ux', 'uy')}
        coordinates = np.array([data.variables['coordx'][:], data.variables['coordy'][:]]).T.copy()
        connectivity = data.variables['connect1'][:].copy()-1
        times = data.variables['time_whole'][:].copy()
    expected_end = .24 if validate_samples else .7
    if len(times) == 0 or abs(times[-1]-expected_end) > 1.e-9:
        raise ValueError(f'{case}: incomplete history, expected end time {expected_end}')
    centers = coordinates[connectivity[:, -1]]
    elements = sorted({int(np.argmin(np.sum((centers-point)**2, axis=1))) for point in points})
    output = []
    errors = dict(B=0., ap=0., gamma=0., J=0.)
    for element in elements:
        nodes = connectivity[element]
        coords = coordinates[nodes]
        width, height = np.ptp(coords, axis=0)
        # Central Gauss point of a reference QUAD9; the pressure is Q1.
        gradient = np.zeros((9, 2))
        gradient[7, 0], gradient[5, 0] = -1/width, 1/width
        gradient[4, 1], gradient[6, 1] = -1/height, 1/height
        previous = IDENTITY.copy()
        accumulated = 0.
        for step, time in enumerate(times):
            F = IDENTITY.copy()
            F[:2, :2] += np.array([fields['ux'][step, nodes], fields['uy'][step, nodes]]) @ gradient
            pressure = float(fields['p'][step, nodes[-1]]) / 1.e9
            increment = np.zeros(7)
            def state(x):
                return evaluate(F, previous, pressure, x, accumulated, hardening, beta)
            if state(increment)[0][-1] > 1.e-11:
                solution = root(lambda x: state(x)[0], increment, tol=1.e-10)
                increment = solution.x
                if np.max(abs(solution.fun)) > 1.e-9 or increment[-1] < -1.e-12:
                    raise AssertionError(f'Return mapping failed at {element}, {time}')
            _, Fp, _, B = state(increment)
            if validate_samples:
                sample = RUNTIME / f'{case}_storage_samples_{step+1:04d}.csv'
                with sample.open() as stream:
                    row = next(r for r in csv.DictReader(stream)
                               if int(float(r['elem_id'])) == element and int(float(r['qp_id'])) == 4)
                for key, value in dict(B=B, ap=np.linalg.det(Fp), gamma=increment[-1], J=np.linalg.det(F)).items():
                    errors[key] = max(errors[key], abs(value-float(row['check_'+key])))
            if increment[-1] > 1.e-10 and any(abs(time-t) < 1.e-9 for t in (.04, .1, .2, .3, .4, .5, .7)):
                # Vanishing increment at the returned state gives the continuum
                # active tangent; previous history and pressure remain fixed.
                current_accumulated = accumulated+increment[-1]
                probes = [acoustic(F, Fp, pressure, np.zeros(7), current_accumulated,
                                   hardening, beta, h) for h in (1.e-6, 5.e-7)]
                error = abs(probes[0]['minimum_determinant_GPa2']-probes[1]['minimum_determinant_GPa2'])
                if error > 1.e-6:
                    raise AssertionError(f'Acoustic finite-difference step sensitivity: {error}')
                output.append(dict(element=element, X=float(centers[element, 0]),
                                   Y=float(centers[element, 1]), time=float(time),
                                   pressure_Pa=pressure*1.e9, gamma=float(increment[-1]),
                                   **probes[1], determinant_step_difference_GPa2=error))
            accumulated += increment[-1]
            previous = Fp
    if validate_samples and max(errors.values()) > 1.e-10:
        raise AssertionError(f'Independent replay disagrees with MOOSE: {errors}')
    return dict(case=case, exodus_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                hardening_modulus_Pa=hardening*1.e9, dilation_slope=beta,
                sampled_point='element central Gauss point', angular_step_degrees=.25,
                replay_errors=errors if validate_samples else None, acoustic=output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('case')
    parser.add_argument('--hardening', type=float, default=0., help='Hardening modulus in Pa')
    parser.add_argument('--beta', type=float, default=.4)
    parser.add_argument('--validate-samples', action='store_true')
    args = parser.parse_args()
    result = replay(args.case, args.hardening/1.e9, args.beta,
                    [(x, .05) for x in (.125, .5, .875)], args.validate_samples)
    output = RUNTIME / (args.case+'_acoustic.json')
    output.write_text(json.dumps(result, indent=2)+'\n')
    print(output.relative_to(ROOT))
    print('Replay errors:', result['replay_errors'])
    print('Minimum sampled determinant:', min(r['minimum_determinant_GPa2'] for r in result['acoustic']))


if __name__ == '__main__':
    main()
