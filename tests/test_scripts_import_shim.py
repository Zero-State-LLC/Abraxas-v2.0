from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def test_subprocess_can_import_scripts_package_from_repo_root() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import json; "
                "import scripts; "
                "import scripts.run_fast_ci; "
                "print(json.dumps({'module': scripts.__name__, 'file': scripts.__file__}))"
            ),
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": ""},
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout.strip())
    assert payload["module"] == "scripts"
    assert payload["file"].endswith("__init__.py")
