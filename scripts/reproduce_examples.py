"""Regenerate supplementary results with execution-time environment evidence."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'validation/scripts'))
from run_provenance import observe, complete

DRIVERS = ('curate_poroplastic_delta_b.py', 'check_poroplastic_general_path.py',
           'check_poroplastic_load_unload.py', 'check_poroplastic_b_feedback.py',
           'check_tensorial_load_unload.py')
OUTPUTS = ('poroplastic_delta_b.csv', 'poroplastic_general_path.csv',
           'poroplastic_load_unload.csv', 'poroplastic_b_feedback.csv',
           'poroplastic_domain_checks.json', 'tensorial_load_unload.csv')


def main():
    observed = observe(ROOT/'moose_app/nonlinear_biot_ad-opt',
                       [sys.executable, 'scripts/reproduce_examples.py'])
    for driver in DRIVERS:
        subprocess.run([sys.executable, str(ROOT/'validation/scripts'/driver)], cwd=ROOT, check=True)
    record = complete(observed, [ROOT/'validation'/name for name in OUTPUTS])
    (ROOT/'validation/supplementary_execution_provenance.json').write_text(
        json.dumps(record, indent=2)+'\n')


if __name__ == '__main__':
    main()
