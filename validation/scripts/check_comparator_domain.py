"""Exercise unavailable, disabled, valid, and required virgin diagnostics in MOOSE."""
import csv
import math
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'.agent-runtime/comparator-domain'
DECK = ROOT/'moose_app/test/tests/implicit_poroplastic/comparator_domain.i'
OUT.mkdir(parents=True, exist_ok=True)
for name, extra, available, expected_B in (
    ('unavailable', [], 0., .3610074919605404),
    ('disabled', ['Materials/plastic/compute_elastic_coefficient=false',
                  'Variables/p/initial_condition=0', 'BCs/p/value=0'], 0., .8),
    ('valid', ['Variables/p/initial_condition=0', 'BCs/p/value=0'], 1., .8),
    ('closed_virgin_pores', ['Variables/p/initial_condition=0', 'BCs/p/value=0',
                            'Variables/axial/initial_condition=.7', 'BCs/axial/value=.7'],
     0., 1-.4*(.7/2)**(1/(.9*2.5))/.7),
    ('required', ['Materials/plastic/use_elastic_coefficient_in_trial=true',
                  'Materials/plastic/compute_elastic_coefficient=false'], None, None),
):
    base = OUT/name
    result = subprocess.run([str(ROOT/'moose_app/nonlinear_biot_ad-opt'), '-i', str(DECK),
                             f'Outputs/file_base={base}', '--no-color', *extra],
                            capture_output=True, text=True, cwd=ROOT)
    base.with_suffix('.log').write_text(result.stdout+result.stderr)
    if available is None:
        assert result.returncode != 0 and 'no stable tensile root' in result.stdout+result.stderr
    else:
        assert result.returncode == 0, result.stdout+result.stderr
        with base.with_suffix('.csv').open() as stream:
            row = list(csv.DictReader(stream))[-1]
        assert float(row['available']) == available
        assert math.isfinite(float(row['B']))
        assert abs(float(row['B'])-expected_B) < 1e-10
        if available:
            assert math.isfinite(float(row['virgin']))
        else:
            assert math.isnan(float(row['virgin']))
    print('PASS', name)
