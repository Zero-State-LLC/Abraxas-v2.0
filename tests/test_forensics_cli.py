from __future__ import annotations

import json
from pathlib import Path

from abraxas.cli import main

REPO = Path(__file__).resolve().parents[1]
FIXTURE = (
    REPO
    / "skills/abx-familiar-signal-forager/fixtures/evidence_pack_hermes_skill_os_2026-07-27.v0.json"
)


def test_cli_forensics_run(capsys):
    code = main(["os", "forensics", "run", "--pack", str(FIXTURE)])
    assert code in {0, 1, 2}
    payload = json.loads(capsys.readouterr().out)
    assert payload["ops_gate_status"] == "DENIED"
    assert payload["advisory_only"] is True


def test_cli_forensics_status(capsys):
    code = main(["os", "forensics", "status"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ops_gate_default"] == "DENIED"
