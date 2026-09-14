#!/usr/bin/env python3
"""Check the stress-trace construction in the main constitutive derivation.

This standard-library calculation checks the proposed constitutive equations;
it does not run or validate a MOOSE implementation.
"""

import json
import math


def determinant(a):
    return (
        a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
        - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
        + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0])
    )


def product(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def transpose(a):
    return [list(row) for row in zip(*a)]


def derivative(function, value, scale=1.0):
    step = 1e-4 * max(abs(value), scale)
    return (
        function(value - 2 * step) - 8 * function(value - step)
        + 8 * function(value + step) - function(value + 2 * step)
    ) / (12 * step)


def mineral(J, pressure, K, Ks, phi0, ap=1.0):
    """Solve the stable logarithmic mineral branch by bracketing log(volume)."""
    coupling = K / (phi0 * Ks)
    assert J > 0 and ap > 0 and 0 < coupling < 1
    forcing = (1 - coupling) * pressure / Ks
    drained = coupling * math.log(J / ap)
    if pressure == 0:
        logarithm = drained
    else:
        def residual(value):
            return value + forcing * math.exp(value) - drained
        if pressure > 0:
            upper = drained
        else:
            upper = math.log(-1 / forcing)
            if residual(upper) <= 0:
                raise ValueError("No stable positive mineral root")
        lower = min(drained, upper) - 1
        while residual(lower) >= 0:
            lower -= 2
        for _ in range(80):
            middle = (lower + upper) / 2
            if residual(middle) < 0:
                lower = middle
            else:
                upper = middle
        logarithm = (lower + upper) / 2
    volume = math.exp(logarithm)
    fraction = phi0 * volume / J
    tangent = Ks + (1 - coupling) * pressure * volume
    coefficient = 1 - K * volume / (J * tangent)
    return volume, fraction, coefficient


def potential(F, pressure, K, Ks, phi0, G, double_prime=False):
    J = determinant(F)
    volume = mineral(J, pressure, K, Ks, phi0)[0]
    coupling = K / (phi0 * Ks)
    shape = sum(value * value for row in F for value in row)
    result = (
        G / 2 * (J ** (-2 / 3) * shape - 3)
        + K / 2 * math.log(J) ** 2
        + phi0 * (1 - coupling) / (2 * Ks) * (pressure * volume) ** 2
    )
    if not double_prime:
        result += phi0 * pressure * volume
    return result


def stress(F, pressure, K, Ks, phi0, G, double_prime=False):
    J = determinant(F)
    b = product(F, transpose(F))
    mean_b = sum(b[i][i] for i in range(3)) / 3
    volume = mineral(J, pressure, K, Ks, phi0)[0]
    coupling = K / (phi0 * Ks)
    tangent = Ks + (1 - coupling) * pressure * volume
    mean = K / J * (math.log(J) + pressure * volume / Ks)
    if double_prime:
        mean = K / J * (
            math.log(J) + (1 - coupling) * (pressure * volume) ** 2 / (Ks * tangent)
        )
    return [
        [G * J ** (-5 / 3) * (b[i][j] - (mean_b if i == j else 0))
         + (mean if i == j else 0) for j in range(3)]
        for i in range(3)
    ]


def main():
    worst = {}

    def check(name, actual, expected, scale=1.0):
        error = abs(actual - expected) / max(scale, abs(expected))
        worst[name] = max(worst.get(name, 0.0), error)
        if not math.isfinite(error) or error > 5e-8:
            raise AssertionError(f"{name}: {actual} != {expected}; error={error}")

    samples = 0
    rotations = [
        [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]],
        [[math.cos(.37), -math.sin(.37), 0.],
         [math.sin(.37), math.cos(.37), 0.], [0., 0., 1.]],
    ]
    gradients = [
        [[.95, 0., 0.], [0., .98, 0.], [0., 0., 1.03]],
        [[1.05, .12, .03], [.02, .98, -.04], [0., .05, 1.02]],
        [[1.08, -.08, .03], [.01, 1.04, .02], [0., -.03, 1.01]],
    ]
    for K, Ks, phi0, G in [(.2, 1., .6, .15), (.4, 2., .8, .3)]:
        for base in gradients:
            for rotation in rotations:
                F = product(rotation, base)
                J = determinant(F)
                for pressure in [-.05 * Ks, 0., .25 * Ks, Ks]:
                    samples += 1
                    z, phi, B = mineral(J, pressure, K, Ks, phi0)
                    assert J > 0 and 0 < z < math.e and 0 < phi < 1
                    coupling = K / (phi0 * Ks)
                    assert Ks + (1 - coupling) * pressure * z > 0
                    assert 0 < B < 1
                    def original_energy(volume):
                        return (K / (2 * (1 - coupling)) * math.log(J / volume) ** 2
                                + phi0 * Ks / 2 * math.log(volume) ** 2)
                    check("original_energy_pressure_equilibrium",
                          derivative(original_energy, z), -phi0 * pressure, Ks)
                    shape = sum(value * value for row in F for value in row)
                    check("original_to_reduced_energy", original_energy(z),
                          potential(F, pressure, K, Ks, phi0, G, True)
                          - G / 2 * (J ** (-2 / 3) * shape - 3), Ks)
                    check("solid_mass", J * phi / z, phi0)
                    zJ = derivative(lambda x: mineral(x, pressure, K, Ks, phi0)[0], J)
                    zp = derivative(lambda x: mineral(J, x, K, Ks, phi0)[0], pressure, Ks)
                    check("biot_from_volume_difference", 1 - phi0 * zJ, B)
                    check("compatibility", J * zJ - (Ks / z + pressure) * zp, z)
                    intrinsic = 1 / z
                    density_J = derivative(lambda x: 1 / mineral(x, pressure, K, Ks, phi0)[0], J)
                    fraction_J = derivative(lambda x: mineral(x, pressure, K, Ks, phi0)[1], J)
                    check("local_eos_residual", math.log(intrinsic) + coupling * math.log(J)
                          - (1 - coupling) * pressure / (Ks * intrinsic), 0.)
                    density_entry = (1 + (1 - coupling) * pressure * z / Ks) / intrinsic
                    check("implicit_eos_tangent", density_entry * density_J + coupling / J, 0.)
                    check("implicit_mass_tangent", J * phi * density_J
                          + J * intrinsic * fraction_J + phi * intrinsic, 0.)
                    check("pressure_conjugacy", derivative(
                        lambda x: potential(F, x, K, Ks, phi0, G), pressure, Ks), phi0 * z)
                    check("reduced_energy_pressure", derivative(
                        lambda x: potential(F, x, K, Ks, phi0, G, True), pressure, Ks),
                        -phi0 * pressure * zp, Ks)

                    tensors = []
                    for double_prime in (False, True):
                        tensor = stress(F, pressure, K, Ks, phi0, G, double_prime)
                        tensors.append(tensor)
                        piola = [[0.] * 3 for _ in range(3)]
                        for i in range(3):
                            for j in range(3):
                                def varied(value):
                                    changed = [row[:] for row in F]
                                    changed[i][j] = value
                                    return potential(changed, pressure, K, Ks, phi0, G, double_prime)
                                piola[i][j] = derivative(varied, F[i][j])
                        conjugate = product(piola, transpose(F))
                        rotated = product(product(rotation, stress(
                            base, pressure, K, Ks, phi0, G, double_prime)), transpose(rotation))
                        for i in range(3):
                            for j in range(3):
                                check("tensor_energy_conjugacy", conjugate[i][j] / J, tensor[i][j], Ks)
                                check("stress_objectivity", tensor[i][j], rotated[i][j], Ks)

                    single, double = tensors
                    for i in range(3):
                        for j in range(3):
                            check("biot_stress_transform", single[i][j] - double[i][j],
                                  (1 - B) * pressure if i == j else 0., Ks)
                    grain_pressure = pressure - sum(single[i][i] for i in range(3)) / (3 * phi)
                    check("mechanical_grain_eos", grain_pressure, -Ks * math.log(z) / z, Ks)
                    if pressure == 0:
                        check("drained_stress", sum(double[i][i] for i in range(3)) / 3,
                              K * math.log(J) / J, Ks)

        check("reference_B", mineral(1., 0., K, Ks, phi0)[2], 1 - K / Ks)
        check("reference_drained_K", derivative(lambda J: K * math.log(J) / J, 1.), K, Ks)
        check("reference_storage", derivative(
            lambda pressure: 1 - phi0 * mineral(1., pressure, K, Ks, phi0)[0], 0., Ks),
            phi0 / Ks - K / Ks ** 2)
        for J in [.9, 1., 1.1]:
            pressure = -Ks * math.log(J) / J
            z, phi, B = mineral(J, pressure, K, Ks, phi0)
            check("unjacketed_volume", z, J)
            check("unjacketed_solid_fraction", phi, phi0)
            F = [[J ** (1 / 3) if i == j else 0. for j in range(3)] for i in range(3)]
            total = stress(F, pressure, K, Ks, phi0, G, True)
            for i in range(3):
                check("unjacketed_total_stress", total[i][i] - B * pressure, -pressure, Ks)

    fixed_plastic_states = 0
    for ap in [.85, 1., 1.15]:
        for J in [.9, 1., 1.1]:
            for pressure in [-.05, 0., .25, 1.]:
                K, Ks, phi0 = .2, 1., .6
                alpha = 1 - K / (phi0 * Ks)
                z, phi, B = mineral(J, pressure, K, Ks, phi0, ap)
                zJ = derivative(lambda x: mineral(x, pressure, K, Ks, phi0, ap)[0], J)
                rhoJ = derivative(lambda x: 1 / mineral(x, pressure, K, Ks, phi0, ap)[0], J)
                phiJ = derivative(lambda x: mineral(x, pressure, K, Ks, phi0, ap)[1], J)
                tangent = Ks + alpha * pressure * z
                check("fixed_plastic_mass", J * phi / z, phi0)
                check("fixed_plastic_eos", Ks * math.log(z) + alpha * pressure * z
                      - K / phi0 * math.log(J / ap), 0.)
                check("fixed_plastic_volume_tangent", zJ, K * z / (phi0 * J * tangent))
                check("fixed_plastic_biot", 1 - phi0 * zJ, B)
                check("fixed_plastic_density_tangent", rhoJ, -K / (phi0 * J * tangent * z))
                check("fixed_plastic_fraction_tangent", phiJ,
                      phi / J * (K / (phi0 * tangent) - 1))
                check("fixed_plastic_implicit_mass_tangent",
                      J * phi * rhoJ + J / z * phiJ + phi / z, 0.)
                fixed_plastic_states += 1

    print(json.dumps({"status": "PASS", "elastic_states": samples,
                      "fixed_plastic_states": fixed_plastic_states,
                      "maximum_normalized_errors": worst}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
