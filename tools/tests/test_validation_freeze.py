"""A frozen tooling audit must preserve every non-manuscript acceptance gate."""
from contextlib import ExitStack, redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("repository_audit", ROOT / "scripts/validate_repository.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class ValidationFreezeTest(unittest.TestCase):
    def exercise(self, frozen, skip):
        with tempfile.TemporaryDirectory() as td, ExitStack() as stack:
            root = Path(td)
            (root / "research-project.yml").write_text(json.dumps({
                "maintenance": {"manuscript_edits": not frozen}}))
            stack.enter_context(patch.object(audit, "ROOT", root))
            calls = []
            names = [n for n in vars(audit) if n.startswith("audit_")]
            for name in names:
                def stub(name=name):
                    calls.append(name)
                stub.__name__ = name
                stack.enter_context(patch.object(audit, name, stub))
            output = io.StringIO()
            with redirect_stdout(output):
                audit.main(["--skip-manuscript"] if skip else [])
            return calls, names, output.getvalue()

    def test_default_retains_all_audits_even_when_frozen(self):
        calls, names, output = self.exercise(True, False)
        self.assertCountEqual(calls, names)
        self.assertNotIn("SKIP", output)

    def test_explicit_frozen_mode_skips_only_manuscript(self):
        calls, names, output = self.exercise(True, True)
        self.assertCountEqual(calls, [n for n in names if n != "audit_manuscript"])
        self.assertIn("SKIP audit_manuscript", output)
        self.assertNotIn("PASS standalone", output)

    def test_skip_is_rejected_without_freeze(self):
        with self.assertRaisesRegex(AssertionError, "requires a declared"):
            self.exercise(False, True)
