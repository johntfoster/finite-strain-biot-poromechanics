#!/usr/bin/env python3
"""Exercise the commit skill against real hooks in an isolated repository."""

from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

from test_validate_process_log import VALID

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "agent_environment/skills/commit/scripts/commit.sh"


class CommitSkillTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="biot-commit-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull,
                        GIT_CONFIG_NOSYSTEM="1")
        self.git("init", "-q")
        self.git("config", "user.name", "Commit Test")
        self.git("config", "user.email", "commit-test@example.invalid")
        for name in ("tools/agentctl", "tools/validate_process_log.py",
                     "tools/update_ai_disclosure.py", "provenance/ai-use.yml",
                     "AGENTS.md", "research-project.yml",
                     ".agent/shared/tools/research_project.py"):
            destination = self.root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, destination)
        (self.root / "paper").mkdir()
        (self.root / "paper/main.tex").write_text("Seed manuscript\n")
        self.git("add", ".")
        self.git("commit", "-qm", "Seed fixture")
        shutil.copytree(ROOT / ".githooks", self.root / ".githooks")
        (self.root / "change.txt").write_text("Reviewed change\n")
        self.git("add", "change.txt")
        (self.root / "message.txt").write_text(VALID)
        self.trace = self.root / "trace.log"
        self.env["GIT_TRACE"] = str(self.trace)
        self.before = self.git("rev-parse", "HEAD").stdout

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, env=self.env,
                              capture_output=True, text=True, check=True)

    def commit(self):
        return subprocess.run([str(HELPER), "message.txt"], cwd=self.root,
                              env=self.env, capture_output=True, text=True)

    def test_commit_runs_all_hooks_and_stages_disclosure(self):
        # Explicitly exercise legacy mode only in this synthetic repository.
        self.git("config", "research.manuscriptFreeze", "false")
        result = self.commit()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotEqual(self.git("rev-parse", "HEAD").stdout, self.before)
        trace = self.trace.read_text()
        for hook in ("pre-commit", "prepare-commit-msg", "commit-msg"):
            self.assertIn(f".githooks/{hook}", trace)
        committed = self.git("show", "--pretty=", "--name-only", "HEAD").stdout
        self.assertIn("provenance/AI_USE.md", committed)
        self.assertIn("provenance/ai_use_statement.tex", committed)
        self.assertIn(VALID.strip(), self.git("log", "-1", "--format=%B").stdout)

    def test_frozen_infrastructure_commit_never_generates_disclosure(self):
        result = self.commit()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        committed = self.git("show", "--pretty=", "--name-only", "HEAD").stdout
        self.assertEqual(committed.strip(), "change.txt")
        self.assertFalse((self.root / "provenance/ai_use_statement.tex").exists())
        self.assertEqual((self.root / "paper/main.tex").read_text(), "Seed manuscript\n")

    def test_frozen_manuscript_edit_is_rejected(self):
        (self.root / "paper/main.tex").write_text("Changed fixture\n")
        self.git("add", "paper/main.tex")
        result = self.commit()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("paper/main.tex", result.stdout + result.stderr)
        self.assertEqual(self.git("rev-parse", "HEAD").stdout, self.before)

    def test_frozen_manuscript_rename_is_rejected(self):
        self.git("mv", "paper/main.tex", "renamed.txt")
        result = self.commit()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("paper/main.tex", result.stdout + result.stderr)
        self.assertEqual(self.git("rev-parse", "HEAD").stdout, self.before)

    def test_invalid_narrative_stops_before_commit(self):
        (self.root / "message.txt").write_text("Subject only\n")
        self.assertNotEqual(self.commit().returncode, 0)
        self.assertEqual(self.git("rev-parse", "HEAD").stdout, self.before)

    def test_whitespace_failure_stops_before_commit(self):
        (self.root / "change.txt").write_text("Trailing space \n")
        self.git("add", "change.txt")
        self.assertNotEqual(self.commit().returncode, 0)
        self.assertEqual(self.git("rev-parse", "HEAD").stdout, self.before)

    def test_hook_failure_prevents_commit(self):
        (self.root / ".githooks/commit-msg").write_text("#!/bin/sh\nexit 1\n")
        self.assertNotEqual(self.commit().returncode, 0)
        self.assertEqual(self.git("rev-parse", "HEAD").stdout, self.before)


if __name__ == "__main__":
    unittest.main()
