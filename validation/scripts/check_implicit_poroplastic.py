#!/usr/bin/env python3
"""Independently verify the implicit poroplastic constitutive state in MOOSE.

Raw runs remain under .agent-runtime. Publication data are written only with
--curate, after all constitutive verification checks pass.
"""

import argparse
import csv
import json
from functools import partial
import subprocess
from pathlib import Path

import numpy as np
from scipy.linalg import logm
from scipy.optimize import brentq
from numpy.polynomial.legendre import leggauss
from run_provenance import observe, complete

ROOT = Path(__file__).resolve().parents[2]
DECK = ROOT / "moose_app/test/tests/implicit_poroplastic/material_path.i"
BINARY = ROOT / "moose_app/nonlinear_biot_ad-opt"
G, K, KS, PHI0, M, BETA = 0.75e9, 1e9, 2.5e9, 0.8, 0.6, 0.4
PRESSURE_NODES, PRESSURE_WEIGHTS = leggauss(16)
RUN_PROVENANCE = []


def tensor(row, prefix):
    return np.array([[row[f"{prefix}{i}{j}"] for j in range(3)] for i in range(3)])


def mineral_volume(elastic_J, pressure):
    """Solve the logarithmic grain constraint independently of MOOSE's AD root."""
    alpha = 1 - K / (PHI0 * KS)
    def residual(log_volume):
        return log_volume + alpha * pressure / KS * np.exp(log_volume) - K / (PHI0 * KS) * np.log(elastic_J)
    log_volume = brentq(residual, -50., 1., xtol=5e-15)
    return np.exp(log_volume)


def energy(Fe, pressure, double_prime=False):
    """Reduced or pressure Legendre energy for independent stress derivatives."""
    Je = np.linalg.det(Fe)
    z = mineral_volume(Je, pressure)
    alpha = 1 - K / (PHI0 * KS)
    return (
        G / 2 * (Je ** (-2 / 3) * np.sum(Fe * Fe) - 3)
        + K / 2 * np.log(Je) ** 2
        + PHI0 * alpha / (2 * KS) * (pressure * z) ** 2
        + (0.0 if double_prime else PHI0 * pressure * z)
    )


def energy_stress(Fe, pressure, double_prime=False):
    """Kirchhoff stress from differences of energy at fixed pressure/history."""
    Pe = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            plus, minus = Fe.copy(), Fe.copy()
            plus[i, j] += 2e-6
            minus[i, j] -= 2e-6
            Pe[i, j] = (energy(plus, pressure, double_prime)
                        - energy(minus, pressure, double_prime)) / 4e-6
    return Pe @ Fe.T


def pressure_checks(Fe, J, pressure, tau, B):
    """Hold Fe and total J fixed: pressure probes must not advance plastic flow."""
    Je = np.linalg.det(Fe)
    ap = J / Je
    shape = Fe @ Fe.T
    drained = (G * Je**(-2/3) * (shape - np.trace(shape)/3 * np.eye(3))
               + K * np.log(Je) * np.eye(3))
    double = energy_stress(Fe, pressure, double_prime=True)
    single = energy_stress(Fe, pressure)
    total = tau - J * pressure * np.eye(3)

    # Pressure integration uses mineral-volume differences, not the production
    # closed coefficient. Re-solve the mineral state at each quadrature pressure.
    def independent_B(p):
        h = 1e-5
        return 1 - PHI0 * (mineral_volume((J+h)/ap, p)
                          - mineral_volume((J-h)/ap, p)) / (2*h)
    integral = pressure/2 * sum(w * independent_B(pressure*(x+1)/2)
                               for x, w in zip(PRESSURE_NODES, PRESSURE_WEIGHTS))
    integrated_total = drained - J * integral * np.eye(3)

    # Independent stress from the energy: use a fourth-order pressure difference
    # with a wider pressure step to resolve the nested energy differences.
    h = 1e-3 * KS
    pressure_tangent = (energy_stress(Fe, pressure-2*h)
                        - 8*energy_stress(Fe, pressure-h)
                        + 8*energy_stress(Fe, pressure+h)
                        - energy_stress(Fe, pressure+2*h)) / (12*h)
    norm = lambda a: float(np.max(np.abs(a)))
    return dict(
        drained_stress=norm(energy_stress(Fe, 0., True)-drained)/G,
        double_prime_stress=norm(double-(tau-(1-B)*pressure*J*np.eye(3)))/G,
        stress_transforms=max(norm(single-double-(1-B)*pressure*J*np.eye(3)),
                              norm(double-B*pressure*J*np.eye(3)-total))/G,
        pressure_tangent=norm(pressure_tangent-J*(1-B)*np.eye(3))/J,
        pressure_integral=norm(integrated_total-total)/G,
    )


def check(rows, pressure=0.0, transverse=1.0, out_of_plane=1.0, dt=0.02, rotation=0.0,
          hardening=0.0, cohesion=0.0):
    worst = dict(
        mass=0.0,
        eos=0.0,
        biot=0.0,
        flow=0.0,
        yield_residual=0.0,
        stress=0.0,
        determinant=0.0,
        accumulated=0.0,
        drained_stress=0.0,
        double_prime_stress=0.0,
        stress_transforms=0.0,
        pressure_tangent=0.0,
        pressure_integral=0.0,
    )
    Fpold = np.eye(3)
    accumulated = 0.0
    for row in rows:
        if not all(np.isfinite(value) for value in row.values()):
            raise AssertionError("Nonfinite constitutive output")
        current_pressure = pressure * min(row["time"], 1.0)
        R = np.array(
            [
                [np.cos(rotation), -np.sin(rotation), 0.0],
                [np.sin(rotation), np.cos(rotation), 0.0],
                [0.0, 0.0, 1.0],
            ]
        )
        F = R @ np.diag([transverse, row["compression"], out_of_plane])
        J = np.linalg.det(F)
        Fp, tau = tensor(row, "fp"), tensor(row, "tau")
        Fe = F @ np.linalg.inv(Fp)
        Je, ap = np.linalg.det(Fe), np.linalg.det(Fp)
        gamma = row["dgamma_avg"]
        accumulated += gamma
        if 'accumulated_avg' in row:
            worst['accumulated'] = max(worst['accumulated'],
                abs(row['accumulated_avg'] - accumulated))
        ratio = row["density"]
        worst["mass"] = max(
            worst["mass"], abs(J * row["solid_fraction"] * ratio / PHI0 - 1)
        )
        alpha = 1 - K / (PHI0 * KS)
        z = 1 / ratio
        # Check both the state residual and actual intrinsic-grain stress trace.
        grain_pressure = current_pressure - np.trace(tau) / (3 * J * row["solid_fraction"])
        worst["eos"] = max(
            worst["eos"],
            abs(np.log(ratio) + K / (PHI0 * KS) * np.log(Je)
                - alpha * current_pressure * z / KS),
            abs(grain_pressure / KS + np.log(z) / z),
        )
        h = 1e-5
        Bfd = 1 - PHI0 * (
            mineral_volume((J + h) / ap, current_pressure)
            - mineral_volume((J - h) / ap, current_pressure)
        ) / (2 * h)
        # Independent two-state tangent solve with density ratio and fraction.
        state_jacobian = np.array([
            [J * row["solid_fraction"], J * ratio],
            [1 / ratio + alpha * current_pressure / (KS * ratio ** 2), 0.],
        ])
        explicit_J = np.array([row["solid_fraction"] * ratio, K / (PHI0 * KS * J)])
        state_J = np.linalg.solve(state_jacobian, -explicit_J)
        Bimplicit = 1 - (row["solid_fraction"] + J * state_J[1])
        worst["biot"] = max(worst["biot"], abs(Bfd - row["b_avg"]),
                            abs(Bimplicit - row["b_avg"]))
        mandel = Fe.T @ tau @ np.linalg.inv(Fe.T)
        mean = -np.trace(mandel) / 3
        dev = mandel + mean * np.eye(3)
        q = np.sqrt(1.5 * np.sum(dev * dev))
        W = np.real_if_close(logm(Fp @ np.linalg.inv(Fpold)))
        N = 1.5 * dev / q + BETA / 3 * np.eye(3) if q > 1e-8 else BETA / 3 * np.eye(3)
        worst["flow"] = max(worst["flow"], float(np.max(np.abs(W - gamma * N))))
        worst["determinant"] = max(
            worst["determinant"], abs(np.log(ap / np.linalg.det(Fpold)) - BETA * gamma)
        )
        residual = (q - M * mean - cohesion - hardening * accumulated) / G
        worst["yield_residual"] = max(
            worst["yield_residual"],
            abs(residual) if gamma > 1e-10 else max(residual, 0.0),
        )
        if gamma < -1e-12 or gamma * (q - BETA * mean) < -1e-5:
            raise AssertionError("Negative plastic multiplier or dissipation")
        # Numerical energy derivatives supply an independent stress reconstruction.
        worst["stress"] = max(
            worst["stress"], float(np.max(np.abs(energy_stress(Fe, current_pressure) - tau))) / G
        )
        for name, error in pressure_checks(Fe, J, current_pressure, tau, row['b_avg']).items():
            worst[name] = max(worst[name], error)
        Fpold = Fp
    limits = dict(
        mass=1e-10,
        eos=1e-10,
        biot=5e-8,
        flow=1e-9,
        yield_residual=1e-9,
        stress=2e-7,
        determinant=1e-9,
        accumulated=1e-10,
        drained_stress=2e-7,
        double_prime_stress=2e-7,
        stress_transforms=2e-7,
        pressure_tangent=2e-7,
        pressure_integral=2e-7,
    )
    for name, value in worst.items():
        if value > limits[name]:
            raise AssertionError(f"{name}: {value} > {limits[name]}")
    return worst


def run(
    directory,
    name,
    pressure=0.0,
    dt=0.02,
    reference=False,
    end=3.0,
    transverse=1.0,
    out_of_plane=1.0,
    monotonic=False,
    final_stretch=0.8,
    rotation=0.0,
    hardening=0.0,
    cohesion=0.0,
):
    text = DECK.read_text()
    text = text.replace('dp_cohesion = 0.0',
                        f'dp_cohesion = {cohesion:.16g}\n'
                        f'    dp_hardening_modulus = {hardening:.16g}\n'
                        f'    use_elastic_coefficient_in_trial = {str(reference).lower()}')
    if pressure:
        text = text.replace(
            "[Functions]\n",
            f"[Functions]\n  [pressure_ramp]\n    type = PiecewiseLinear\n    x = '0 1 3'\n    y = '0 {pressure:.16g} {pressure:.16g}'\n  []\n",
        )
        text = text.replace(
            "type = DirichletBC\n    variable = p\n    boundary = 'left right bottom top'\n    value = 0",
            "type = FunctionDirichletBC\n    variable = p\n    boundary = 'left right bottom top'\n    function = pressure_ramp",
        )
    if monotonic:
        text = text.replace("x = '0 1 2 3'", "x = '0 1'").replace(
            "y = '1 0.8 0.9 0.76'", f"y = '1 {final_stretch:.16g}'"
        )
    text = text.replace("dt = 0.02", f"dt = {dt:.16g}").replace(
        "end_time = 3", f"end_time = {end:.16g}"
    )
    text = text.replace(
        "transverse_stretch = 1.0", f"transverse_stretch = {transverse:.16g}"
    ).replace(
        "out_of_plane_stretch = 1.0", f"out_of_plane_stretch = {out_of_plane:.16g}"
    )
    if rotation:
        text = text.replace(
            "type = ADConstantDeformationGradientMaterial",
            f"type = ADConstantDeformationGradientMaterial\n    rotation_angle = {rotation:.16g}",
        )
    text = text.replace("csv = true", "csv = true\n  console = false")
    deck = directory / (name + ".i")
    deck.write_text(text)
    command = [str(BINARY), "-i", str(deck), "--no-color"]
    observed = observe(BINARY, command)
    result = subprocess.run(
        command,
        cwd=directory,
        capture_output=True,
        text=True,
    )
    (directory / (name + ".log")).write_text(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(f'MOOSE failed: {name}; see {directory/(name+".log")}')
    provenance = complete(observed, [deck, directory/(name+"_out.csv")])
    (directory/(name+'.run.json')).write_text(json.dumps(provenance, indent=2)+'\n')
    RUN_PROVENANCE.append(provenance)
    with (directory / (name + "_out.csv")).open() as stream:
        return [{k: float(v) for k, v in row.items()} for row in csv.DictReader(stream)]


def write_csv(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--curate", action="store_true")
    parser.add_argument("--publication", action="store_true",
                        help="Use c0=20 MPa and H=100 MPa, matching the coupled example")
    parser.add_argument("--output-dir", type=Path, default=ROOT / ".agent-runtime/implicit_poroplastic")
    args = parser.parse_args()
    directory = args.output_dir.resolve()
    directory.mkdir(parents=True, exist_ok=True)
    publication = args.publication or args.curate
    parameters = dict(cohesion=2.e7 if publication else 0.,
                      hardening=1.e8 if publication else 0.)
    run_case = partial(run, **parameters)
    check_case = partial(check, **parameters)
    rows = run_case(directory, "history")
    report = {"history": check_case(rows)}
    peak = next(r for r in rows if abs(r["time"] - 1) < 1e-8)
    unload = [r for r in rows if 1.0 + 1e-8 < r["time"] <= 2.0 + 1e-8]
    if (
        peak["a_p_avg"] <= 1
        or max(abs(r["a_p_avg"] - peak["a_p_avg"]) for r in unload) > 1e-10
    ):
        raise AssertionError(
            "Plastic loading and elastic unloading history check failed"
        )
    if rows[-1]["a_p_avg"] <= peak["a_p_avg"] or rows[-1]["dgamma_avg"] <= 0:
        raise AssertionError(
            "Reload beyond the previous peak must activate plastic flow"
        )
    nonaxis = run_case(
        directory, "nonaxis", pressure=1e8, end=1.0, transverse=1.02, out_of_plane=0.98
    )
    report["nonaxisymmetric"] = check_case(
        nonaxis, pressure=1e8, transverse=1.02, out_of_plane=0.98
    )
    rotated = run_case(
        directory,
        "rotated",
        pressure=1e8,
        end=1.0,
        transverse=1.02,
        out_of_plane=0.98,
        rotation=0.4,
    )
    report["rotated"] = check_case(
        rotated, pressure=1e8, transverse=1.02, out_of_plane=0.98, rotation=0.4
    )
    rotation = np.array(
        [
            [np.cos(0.4), -np.sin(0.4), 0.0],
            [np.sin(0.4), np.cos(0.4), 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    objective_error = max(
        float(
            np.max(
                np.abs(tensor(rr, "tau") - rotation @ tensor(base, "tau") @ rotation.T)
            )
        )
        / G
        for base, rr in zip(nonaxis, rotated)
    )
    if objective_error > 1e-10:
        raise AssertionError(f"Superposed-rotation stress error: {objective_error}")
    report["objectivity_stress_error"] = objective_error
    feedback = []
    if not args.quick:
        refined = []
        for dt in [0.01, 0.005]:
            rr = run_case(directory, "history_" + str(dt), dt=dt)
            report["history_" + str(dt)] = check_case(rr, dt=dt)
            refined.append(rr)
        differences = [
            abs(refined[0][-1]["a_p_avg"] - rows[-1]["a_p_avg"]),
            abs(refined[1][-1]["a_p_avg"] - refined[0][-1]["a_p_avg"]),
        ]
        if differences[1] > 1e-10 and (
            differences[1] >= differences[0] or differences[1] > 1e-4
        ):
            raise AssertionError(f"Time refinement failed: {differences}")
        report["refinement_differences"] = differences
        # A changing principal stress direction supplies a nontrivial increment study.
        nonaxis_refined = []
        for dt in [0.01, 0.005]:
            rr = run_case(
                directory,
                "nonaxis_" + str(dt),
                pressure=1e8,
                dt=dt,
                end=1.0,
                transverse=1.02,
                out_of_plane=0.98,
            )
            report["nonaxis_" + str(dt)] = check_case(
                rr, pressure=1e8, transverse=1.02, out_of_plane=0.98
            )
            nonaxis_refined.append(rr)
        matrices = [tensor(rr[-1], "fp") for rr in [nonaxis] + nonaxis_refined]
        differences = [
            float(np.linalg.norm(matrices[i + 1] - matrices[i])) for i in range(2)
        ]
        if differences[1] >= differences[0] or differences[1] > 1e-3:
            raise AssertionError(f"Nonaxisymmetric refinement failed: {differences}")
        report["nonaxisymmetric_refinement_differences"] = differences
        report["feedback_loading"] = dict(final_axial_stretch=0.65,
                                          final_pressures_Pa=[0., 2e8, 4e8, 6e8, 8e8, 1e9])
        for p in report["feedback_loading"]["final_pressures_Pa"]:
            coupled = run_case(
                directory, f"pressure_{p:g}", pressure=p, end=1.0, monotonic=True,
                final_stretch=0.65,
            )
            reference = run_case(
                directory,
                f"reference_{p:g}",
                pressure=p,
                end=1.0,
                monotonic=True,
                reference=True,
                final_stretch=0.65,
            )
            report[f"pressure_{p:g}"] = check_case(coupled, pressure=p)
            for path in (coupled, reference):
                if not all(0 < r["solid_fraction"] < 1 for r in path):
                    raise AssertionError("Feedback path left the admissible solid-fraction range")
            cp, rf = coupled[-1], reference[-1]
            if p == 0 and abs(cp["a_p_avg"] - rf["a_p_avg"]) > 1e-12:
                raise AssertionError("Pressure-free feedback comparison must coincide")
            if p > 0 and abs(cp["a_p_avg"] - rf["a_p_avg"]) < 1e-6:
                raise AssertionError(
                    "Nonzero-pressure comparison did not resolve coefficient feedback"
                )
            feedback.append(
                dict(
                    pressure=p,
                    B=cp["b_avg"],
                    B_virgin=cp["b_el"],
                    a_p=cp["a_p_avg"],
                    a_p_reference=rf["a_p_avg"],
                )
            )
        report["feedback_refinement"] = {}
        for reference_mode, coarse in ((False, coupled), (True, reference)):
            values = [coarse[-1]["a_p_avg"]]
            for dt in (0.01, 0.005):
                rr = run_case(directory, f"feedback_refined_{reference_mode}_{dt}",
                              pressure=1e9, end=1., monotonic=True, final_stretch=0.65,
                              reference=reference_mode, dt=dt)
                if not reference_mode:
                    report[f"feedback_refined_{dt}"] = check_case(rr, pressure=1e9, dt=dt)
                values.append(rr[-1]["a_p_avg"])
            differences = [abs(values[i + 1] - values[i]) for i in range(2)]
            if differences[1] > 1e-10 and (differences[1] >= differences[0] or differences[1] > 1e-4):
                raise AssertionError(f"Feedback refinement failed: {differences}")
            report["feedback_refinement"]["reference" if reference_mode else "consistent"] = dict(
                final_distention=values, differences=differences)
        if args.curate:
            write_csv(ROOT / "validation/implicit_poroplastic_history.csv", rows)
            write_csv(ROOT / "validation/implicit_poroplastic_feedback.csv", feedback)
    report["parameters"] = dict(K=K, Ks=KS, G=G, phi_s0=PHI0, M=M, beta=BETA,
                                cohesion_Pa=parameters['cohesion'],
                                hardening_modulus_Pa=parameters['hardening'])
    report["accepted"] = True
    report['execution_provenance'] = RUN_PROVENANCE
    report["scope"] = (
        "material state, fixed-current-plastic-state Biot derivative, return consistency; separate PETSc test checks active outer AD"
    )
    (directory / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
    if args.curate and not args.quick:
        (ROOT / "validation/implicit_poroplastic_verification.json").write_text(
            json.dumps(report, indent=2) + "\n"
        )
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
