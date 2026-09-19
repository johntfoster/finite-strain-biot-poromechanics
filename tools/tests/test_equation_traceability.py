"""Reject missing coverage and stale references in either direction."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('trace', ROOT/'scripts/check_equation_traceability.py')
trace = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trace)


class TraceabilityTests(unittest.TestCase):
    def fixture(self, directory):
        root = Path(directory)
        files = {
            'paper/main.tex': r'\paperinput{sections/model.tex}',
            'paper/sections/model.tex': '\\label{eq:balance}\n% \\label{eq:comment}\n',
            'moose_app/src/kernels/Balance.C': '// eq:balance\n',
            'moose_app/test/tests/model/tests': '[Tests]\n [balance]\n []\n[]\n',
            'validation/equation_to_moose_map.yml': yaml.safe_dump({
                'mappings': [{'id': 'balance', 'paper_equations': ['eq:balance'],
                              'moose_objects': ['Balance'], 'tests': ['balance']}],
                'supporting_mappings': []}),
        }
        for name, content in files.items():
            path = root/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        return root

    def test_current_repository(self):
        trace.audit(ROOT)

    def test_unmapped_equation_and_object(self):
        for name, content, message in (
            ('paper/sections/model.tex', r'\label{eq:balance}\label{eq:new}', 'Unmapped manuscript'),
            ('moose_app/src/kernels/New.C', '// new kernel', 'Unmapped MOOSE'),
        ):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = self.fixture(directory)
                trace.audit(root)
                (root/name).write_text(content)
                with self.assertRaisesRegex(ValueError, message):
                    trace.audit(root)

    def test_deleted_label_test_and_source(self):
        for name, content, message in (
            ('paper/sections/model.tex', '', 'Stale manuscript label'),
            ('moose_app/test/tests/model/tests', '[Tests]', 'Unknown regression'),
            ('moose_app/src/kernels/Balance.C', '// eq:deleted', 'Stale source equation'),
        ):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = self.fixture(directory)
                (root/name).write_text(content)
                with self.assertRaisesRegex(ValueError, message):
                    trace.audit(root)

    def test_numbered_display_needs_a_label(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.fixture(directory)
            with (root/'paper/sections/model.tex').open('a') as stream:
                stream.write(r'\begin{equation} a=b \end{equation}')
            with self.assertRaisesRegex(ValueError, 'Unlabelled numbered display'):
                trace.audit(root)

    def test_unnumbered_equation_identifier(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.fixture(directory)
            path = root/'paper/sections/model.tex'
            path.write_text('\\begin{equation*}\na=b\n% equation-id: eq:balance\n\\end{equation*}\n')
            labels, _, _ = trace.audit(root)
            self.assertEqual(labels['eq:balance'], ('paper/sections/model.tex', 3))
            with path.open('a') as stream:
                stream.write('\\label{eq:balance}\n')
            with self.assertRaisesRegex(ValueError, 'Duplicate manuscript label'):
                trace.audit(root)


if __name__ == '__main__':
    unittest.main()
