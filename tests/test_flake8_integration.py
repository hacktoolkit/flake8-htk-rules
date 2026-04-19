from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class Flake8IntegrationTest(unittest.TestCase):
    def test_installed_flake8_entry_point_reports_rule_families(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        source = """
from datetime import datetime
import pdb

def get_total(values):
    if values:
        pdb.set_trace()
        return sum(values)
    return 0
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            sample_path = Path(tmpdir) / "sample.py"
            sample_path.write_text(source)
            relative_path = os.path.relpath(sample_path, repo_root).replace(
                os.sep,
                "/",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "flake8",
                    str(sample_path),
                    "--select=SP,DT,DB,NM",
                    f"--structured-programming-files={relative_path}",
                ],
                cwd=repo_root,
                check=False,
                text=True,
                capture_output=True,
            )

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        for code in ("DT100", "DB100", "NM100", "SP100", "DB101", "SP101"):
            self.assertIn(code, result.stdout)


if __name__ == "__main__":
    unittest.main()
