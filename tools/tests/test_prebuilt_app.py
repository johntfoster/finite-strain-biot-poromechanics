"""Reject stale container executables when source or the framework changes."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('prebuilt_app', ROOT/'tools/prebuilt_app.py')
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class PrebuiltTests(unittest.TestCase):
    def test_changed_or_added_source_and_binary_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory)/'image'
            checkout = Path(directory)/'checkout'
            for name in app.inputs(ROOT):
                target = image/name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT/name, target)
            (image/'.agent-runtime/moose').mkdir(parents=True)
            executable = image/'moose_app/nonlinear_biot_ad-opt'
            executable.write_bytes(b'executable fixture')
            record = dict(inputs=app.inputs(image), executable_sha256=app.digest(executable))
            (image/'.agent-runtime/prebuilt-app.json').write_text(json.dumps(record))
            shutil.copytree(image, checkout)
            shutil.rmtree(checkout/'.agent-runtime/moose')
            (checkout/'.agent-runtime/moose').symlink_to(image/'.agent-runtime/moose')
            self.assertTrue(app.reusable(checkout, image))
            extra = checkout/'moose_app/src/Added.C'
            extra.write_text('new implementation')
            self.assertFalse(app.reusable(checkout, image))
            extra.unlink()
            source = checkout/'moose_app/src/main.C'
            original = source.read_bytes()
            source.write_bytes(original+b'\n// changed\n')
            self.assertFalse(app.reusable(checkout, image))
            source.write_bytes(original)
            executable.write_bytes(b'changed binary')
            self.assertFalse(app.reusable(checkout, image))


if __name__ == '__main__':
    unittest.main()
