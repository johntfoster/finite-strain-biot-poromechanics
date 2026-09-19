"""Verify observations are captured at execution and never invented for old runs."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT/path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runtime = load('run_provenance', 'validation/scripts/run_provenance.py')
package = load('update_validation_provenance', 'scripts/update_validation_provenance.py')


class ProvenanceTests(unittest.TestCase):
    def test_actual_packages_are_observed_and_missing_packages_remain_unknown(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            binary = root/'app'
            binary.write_bytes(b'executable')
            (root/'conda-meta').mkdir()
            (root/'conda-meta/moose.json').write_text(json.dumps(
                dict(name='moose-dev', version='observed-version', build='observed-build')))
            with patch.object(runtime, 'ROOT', root), patch.object(runtime.sys, 'prefix', directory), \
                 patch.object(runtime.metadata, 'version', return_value='actual'), \
                 patch.object(runtime.subprocess, 'run') as git:
                git.return_value.returncode = 0
                git.return_value.stdout = 'observed-commit\n'
                record = runtime.observe(binary, [str(binary)])
                self.assertEqual(record['packages']['numpy'], 'actual')
                self.assertEqual(record['conda_packages']['moose-dev']['version'], 'observed-version')
                self.assertEqual(record['framework_commit'], 'observed-commit')
                self.assertEqual(record['command'], ['app'])
                self.assertNotIn(directory, json.dumps(record))
                with patch.object(runtime.metadata, 'version', side_effect=runtime.metadata.PackageNotFoundError):
                    self.assertIsNone(runtime.observe(binary, [])['packages']['numpy'])
                binary.write_bytes(b'changed executable')
                with self.assertRaisesRegex(RuntimeError, 'changed during'):
                    runtime.complete(record, [])

    def test_hash_refresh_preserves_historical_observations_and_marks_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'validation').mkdir()
            old = {'framework_commit': 'old-run', 'packages': {'numpy': 'old-version'}}
            (root/'validation/implicit_poroplastic_verification.json').write_text(
                json.dumps({'execution_provenance': [old]}))
            (root/'validation/poroplastic_mandel_verification.json').write_text('{}')
            (root/'validation/poroplastic_spatial_stability.json').write_text(
                json.dumps({'cases': {'historical': {}}}))
            with patch.object(package, 'ROOT', root):
                records = package.execution_records()
            self.assertEqual(records['material_point'], [old])
            for name in ('coupled_plastic', 'elastic_mandel', 'supplementary'):
                self.assertEqual(records[name]['status'], 'not_recorded')
            self.assertEqual(records['spatial_stability']['historical']['status'], 'not_recorded')


if __name__ == '__main__':
    unittest.main()
