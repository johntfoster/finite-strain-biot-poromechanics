#!/usr/bin/env python3
"""Reproduce and curate Mandel profiles and finite-deformation sensitivity runs."""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'validation/scripts'))
import check_mandel_implicit_biot as mandel

# Resolve the overshoot, then increase the step to 0.016 s during drainage.
PROFILE_TIMES = sorted(set(
    [0.] + [i / 1000 for i in range(1, 21)]
    + [i / 1000 for i in range(22, 47, 2)]
    + [i / 1000 for i in range(50, 95, 4)]
    + [i / 1000 for i in range(102, 207, 8)]
    + [i / 1000 for i in range(222, 703, 16)]
))


def read_rows(path):
    with path.open() as stream:
        return [{key: float(value) for key, value in row.items()} for row in csv.DictReader(stream)]


def prepare_decks(output):
    source = mandel.DECK.read_text()
    source = re.sub(r'^load_pa :=.*\n|^deformation_scale :=.*\n', '', source, flags=re.M)
    sequence = ' '.join(f'{time:.12g}' for time in PROFILE_TIMES)
    report = re.sub(r"^time_sequence := '[^']+'", f"time_sequence := '{sequence}'", source, flags=re.M)
    start = report.index('  [top_displacement]')
    end = report.index('  []', start)
    values = ' '.join(f'{mandel.analytical_solution(time, 0.)[2]:.16g}' for time in PROFILE_TIMES)
    report = report[:start] + (
        "  [top_displacement]\n    type = PiecewiseLinear\n"
        f"    x = '{sequence}'\n    y = '{values}'\n"
    ) + report[end:]
    report += '\n[VectorPostprocessors]\n'
    for name, variable, start_point, end_point, count, coordinate in (
        ('pressure_profile', 'p', '0 0.05 0', '1 0.05 0', 81, 'x'),
        ('ux_profile', 'ux', '0 0.05 0', '1 0.05 0', 21, 'x'),
        ('uy_profile', 'uy', '1 0 0', '1 0.1 0', 9, 'y'),
    ):
        report += (f'  [{name}]\n    type = LineValueSampler\n    variable = {variable}\n'
                   f"    start_point = '{start_point}'\n    end_point = '{end_point}'\n"
                   f'    num_points = {count}\n    sort_by = {coordinate}\n'
                   '    execute_on = TIMESTEP_END\n  []\n')
    report += '[]\n'
    (output / 'report.i').write_text(report)
    start = source.index('  [top_displacement]')
    end = source.index('  []', start)
    large = source[:start] + ("  [top_displacement]\n    type = ParsedFunction\n"
                            "    expression = '-0.01*min(t/0.2,1)'\n") + source[end:]
    (output / 'large.i').write_text(large)
    return sequence


def run_cases(output, executable):
    sequence = prepare_decks(output)
    commands = []
    for name, deck, nx, ny, times, exodus in (
        ('report', 'report.i', 40, 4, sequence, False),
        ('large_spatial_coarse', 'large.i', 20, 2, mandel.time_sequence(.002, .702), False),
        ('large_temporal_coarse', 'large.i', 40, 4, mandel.time_sequence(.004, .702), False),
        ('large_fine', 'large.i', 40, 4, mandel.time_sequence(.002, .702), True),
    ):
        command = [str(executable), '-i', str(output / deck), f'mesh_nx={nx}', f'mesh_ny={ny}',
                   f'time_sequence={times}', f'Outputs/file_base={output / name}',
                   f'Outputs/exodus={str(exodus).lower()}', '--disable-perf-graph-live', '--color', 'off']
        print(f'RUN {name}', flush=True)
        with (output / f'{name}.log').open('w') as log:
            subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True, cwd=ROOT)
        rows = read_rows(output / f'{name}.csv')
        if not rows or abs(rows[-1]['time'] - .702) > 1e-12:
            raise RuntimeError(f'{name} did not reach the final time')
        commands.append({'name': name, 'command': [arg.replace(str(ROOT) + '/', '') for arg in command]})
        (output / 'publication_commands.json').write_text(json.dumps(commands, indent=2))
        print(f'PASS {name}', flush=True)


def curate(output, benchmark_summary):
    import yaml
    fine = read_rows(output / 'large_fine.csv')
    spatial = read_rows(output / 'large_spatial_coarse.csv')
    temporal = read_rows(output / 'large_temporal_coarse.csv')
    maximum = lambda rows, key: max(row[key] for row in rows)
    for rows in (fine, spatial, temporal):
        if maximum(rows, 'solid_mineral_eos_constraint_l2') > 1e-12 or maximum(rows, 'biot_analytic_error_l2') > 1e-12:
            raise RuntimeError('finite-deformation constitutive identity failed')
    fine_mass = maximum(fine, 'solid_material_mass_constraint_l2')
    coarse_mass = maximum(temporal, 'solid_material_mass_constraint_l2')
    if fine_mass >= coarse_mass:
        raise RuntimeError('solid-mass drift did not decrease under time refinement')
    subprocess.run([sys.executable, str(ROOT / 'scripts/curate_mandel_profiles.py'), str(output / 'report'),
                    '--large-source', str(output / 'large_fine.csv')], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(ROOT / 'scripts/extract_mandel_density_contours.py'),
                    '--exodus', str(output / 'large_fine.e')], check=True, cwd=ROOT)
    record_path = ROOT / 'validation/mandel_implicit_biot.yml'
    record = yaml.safe_load(record_path.read_text())
    record['finite_deformation_continuation'].pop('spatial_field_regeneration', None)
    if benchmark_summary:
        benchmark = json.loads(benchmark_summary.read_text())
        if not benchmark['accepted']:
            raise RuntimeError('full Mandel benchmark has not passed')
        record['metrics'] = {key: value for key, value in benchmark['metrics'].items() if not isinstance(value, list)}
        record['metrics']['mandel_cryer_peak_time_seconds'] = record['metrics'].pop('mandel_cryer_peak_time')
        for key in ('maximum_spatial_refinement_pressure_difference', 'maximum_temporal_refinement_pressure_difference', 'maximum_finer_temporal_refinement_pressure_difference'):
            record['metrics'][key] = benchmark[key]
        truncation = benchmark['analytical_root_truncation']
        record['metrics']['analytical_12_vs_128_root_pressure_difference'] = truncation['maximum_pressure_difference_over_pressure_scale']
        record['metrics']['analytical_12_vs_128_root_displacement_difference_m'] = truncation['maximum_displacement_difference_m']
    profiles = read_rows(ROOT / 'validation/mandel_pressure_profiles.csv')
    record['profile_figure']['maximum_plotted_pressure_profile_normalized_error'] = max(
        abs(row['pressure'] - mandel.analytical_solution(row['time'], row['x'])[0]) / mandel.parameters()['pressure_scale'] for row in profiles)
    with (ROOT / 'validation/mandel_displacement_profiles.csv').open() as stream:
        displacements = list(csv.DictReader(stream))
    for component, name, scale in [('ux', 'horizontal', mandel.LOAD / mandel.SHEAR_MODULUS), ('uy', 'vertical', mandel.LOAD * mandel.HEIGHT / mandel.SHEAR_MODULUS)]:
        record['metrics'][f'maximum_{name}_displacement_profile_normalized_error'] = max(
            abs(float(row['displacement']) - mandel.analytical_displacement(component, float(row['coordinate']), float(row['time']), mandel.ROOT_COUNT)) / scale
            for row in displacements if row['component'] == component)
    density = read_rows(ROOT / 'validation/mandel_density_contours.csv')
    last_snapshot = max(row['time'] for row in density)
    final_density = [row['intrinsic_solid_density_ratio'] for row in density if row['time'] == last_snapshot]
    record['finite_deformation_continuation']['spatial_field_times_seconds'] = sorted({row['time'] for row in density})
    final = fine[-1]
    metrics = record['finite_deformation_continuation']['metrics']
    metrics.pop('final_intrinsic_solid_density_ratio_range', None)
    metrics.update({
        'maximum_platen_compression_over_height': max(-row['top_displacement'] / mandel.HEIGHT for row in fine),
        'maximum_lateral_expansion_over_width': maximum(fine, 'side_displacement'),
        'final_lateral_expansion_over_width': final['side_displacement'],
        'final_biot_minimum': final['biot_minimum'], 'final_biot_average': final['biot_average'], 'final_biot_maximum': final['biot_maximum'],
        'maximum_intrinsic_solid_density_ratio': maximum(density, 'intrinsic_solid_density_ratio'),
        'last_snapshot_time_seconds': last_snapshot,
        'last_snapshot_intrinsic_solid_density_ratio_range': [min(final_density), max(final_density)],
        'final_average_biot_relative_departure_from_reference': abs(final['biot_average'] - mandel.BIOT_COEFFICIENT) / mandel.BIOT_COEFFICIENT,
        'maximum_biot_identity_l2': maximum(fine, 'biot_analytic_error_l2'),
        'maximum_referential_solid_mass_drift_l2': fine_mass,
        'maximum_mineral_eos_residual_l2': maximum(fine, 'solid_mineral_eos_constraint_l2'),
        'final_vertical_nominal_stress_pa': final['vertical_nominal_stress'],
    })
    pressure_scale = maximum(fine, 'pressure_x0')
    for name, rows in [('spatial_20x2_vs_40x4_at_dt_0p002', spatial), ('temporal_dt_0p004_vs_0p002_on_40x4', temporal)]:
        by_time = {round(row['time'], 12): row for row in fine}
        pairs = [(row, by_time[round(row['time'], 12)]) for row in rows]
        result = {
            'maximum_pressure_difference_over_peak': max(abs(left['pressure_x0']-right['pressure_x0']) for left, right in pairs) / pressure_scale,
            'maximum_average_biot_difference': max(abs(left['biot_average']-right['biot_average']) for left, right in pairs),
        }
        if rows is temporal:
            result['coarse_maximum_referential_solid_mass_drift_l2'] = coarse_mass
        record['finite_deformation_continuation']['sensitivity'][name] = result
    record_path.write_text(yaml.safe_dump(record, sort_keys=False))
    print(json.dumps({'status': 'PASS', 'continuation': metrics}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifacts-dir', type=Path,
                        default=ROOT / '.agent-runtime/mandel-publication' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    parser.add_argument('--verify-benchmark', action='store_true')
    parser.add_argument('--executable', type=Path, default=mandel.APP)
    parser.add_argument('--curate', action='store_true')
    parser.add_argument('--curate-existing', action='store_true', help='Curate completed runs without repeating them')
    parser.add_argument('--benchmark-summary', type=Path)
    args = parser.parse_args()
    output = args.artifacts_dir.resolve()
    if not args.curate_existing:
        output.mkdir(parents=True, exist_ok=False)
        if args.verify_benchmark:
            subprocess.run([sys.executable, str(ROOT / "validation/scripts/check_mandel_implicit_biot.py"),
                            "--executable", str(args.executable.resolve()), "--artifacts-dir", str(output / "benchmark")],
                           check=True, cwd=ROOT)
            args.benchmark_summary = output / "benchmark/verification_summary.json"
        run_cases(output, args.executable.resolve())
    if args.curate or args.curate_existing:
        curate(output, args.benchmark_summary)


if __name__ == '__main__':
    main()
