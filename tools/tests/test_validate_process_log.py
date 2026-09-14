#!/usr/bin/env python3
"""Unit tests for the commit process-log validator."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "validate_process_log.py"
SPEC = importlib.util.spec_from_file_location("validate_process_log", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


VALID = """Subject

Summary
AI model(s): GPT-5 Codex
AI session(s): isolated commit-helper fixture
State transition.

What changed & why
Factual changes and rationale.

Alternatives considered
An alternative was rejected.

Dead ends & backtracks
No dead end was recorded.

Open questions
No unresolved question was recorded.

Next steps
Run the next verification.
"""


class ProcessLogValidationTest(unittest.TestCase):
    def test_accepts_complete_log(self) -> None:
        self.assertEqual(MODULE.validate(VALID), [])

    def test_rejects_subject_only(self) -> None:
        errors = MODULE.validate("Subject only\n")
        self.assertIn("missing section: Summary", errors)

    def test_rejects_empty_section(self) -> None:
        errors = MODULE.validate(
            VALID.replace(
                "AI model(s): GPT-5 Codex\n"
                "AI session(s): isolated commit-helper fixture\n"
                "State transition.\n",
                "",
            )
        )
        self.assertIn("empty section: Summary", errors)

    def test_rejects_reordered_sections(self) -> None:
        changed = VALID.replace("Summary\nState transition.", "TEMP").replace(
            "Next steps\nRun the next verification.", "Summary\nState transition."
        ).replace("TEMP", "Next steps\nRun the next verification.")
        self.assertIn("sections must appear once and in the required order", MODULE.validate(changed))


if __name__ == "__main__":
    unittest.main()
