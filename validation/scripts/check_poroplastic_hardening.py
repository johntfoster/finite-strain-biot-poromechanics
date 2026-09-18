#!/usr/bin/env python3
"""Check dissipative isotropic hardening without changing zero-hardening checks."""
import json
from check_implicit_poroplastic import ROOT, run, check


def main():
    directory = ROOT / '.agent-runtime/poroplastic_hardening'
    directory.mkdir(parents=True, exist_ok=True)
    modulus = 1.e8
    rows = run(directory, 'history', hardening=modulus)
    errors = check(rows, hardening=modulus)
    peak = next(r for r in rows if abs(r['time'] - 1.) < 1.e-8)
    unload = [r for r in rows if 1.+1.e-8 < r['time'] <= 2.+1.e-8]
    assert peak['accumulated_avg'] > 0.
    assert max(abs(r['accumulated_avg']-peak['accumulated_avg']) for r in unload) < 1.e-10
    assert rows[-1]['accumulated_avg'] > peak['accumulated_avg']
    pressured = run(directory, 'pressure', hardening=modulus, pressure=1.e8,
                    end=1., transverse=1.02, out_of_plane=.98)
    pressure_errors = check(pressured, hardening=modulus, pressure=1.e8,
                            transverse=1.02, out_of_plane=.98)
    result = dict(accepted=True, hardening_modulus_Pa=modulus,
                  history=errors, pressure=pressure_errors,
                  final_accumulated_multiplier=rows[-1]['accumulated_avg'])
    (directory/'verification.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS isotropic hardening', result)


if __name__ == '__main__':
    main()
