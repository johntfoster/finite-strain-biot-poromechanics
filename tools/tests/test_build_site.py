"""Check deployed source delivery, navigation failures, and path confinement."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('build_site', ROOT/'scripts/build_site.py')
site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)


class SiteTests(unittest.TestCase):
    def test_source_paths_cannot_escape_repository(self):
        for path in ('../../outside', '/etc/passwd', 'https://example.com/file'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                site.source_path(path)

    def test_missing_local_anchor_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            page = root/'index.html'
            page.write_text('<a href="#absent">broken</a>')
            with self.assertRaisesRegex(ValueError, 'missing anchor'):
                site.check_links(root)
            page.write_text('<a href="#present">valid</a><h2 id="present">Here</h2>')
            self.assertEqual(site.check_links(root), 1)

    def test_every_deck_and_header_is_in_generated_catalog(self):
        catalog = site.examples_catalog()
        for pattern in ('moose_app/test/tests/**/*.i', 'moose_app/include/**/*.h'):
            for path in ROOT.glob(pattern):
                self.assertIn(path.relative_to(ROOT).as_posix(), catalog)

    def test_stale_packaged_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'index.html').write_text('<a href="source.html?f=moose_app/src/main.C">source</a>')
            (root/'source.html').touch()
            copy = root/'sources/moose_app/src/main.C'
            copy.parent.mkdir(parents=True)
            copy.write_text('stale')
            with self.assertRaisesRegex(ValueError, 'stale packaged source'):
                site.check_links(root, sources=True)
            copy.write_bytes((ROOT/'moose_app/src/main.C').read_bytes())
            self.assertEqual(site.check_links(root, sources=True), 1)


if __name__ == '__main__':
    unittest.main()
