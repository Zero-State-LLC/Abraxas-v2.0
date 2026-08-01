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
    # C′ seal: fixture READY → exit 0; gate always DENIED
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ops_gate_status"] == "DENIED"
    assert payload["disposition"] == "READY"
    assert payload["advisory_only"] is True


def test_cli_forensics_status(capsys):
    code = main(["os", "forensics", "status"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ops_gate_default"] == "DENIED"
    assert payload["advisory_only"] is True
    assert payload["forensics_engine"] == "SLICE_C"


def test_cli_forensics_non_object_pack(tmp_path: Path, capsys):
    bad = tmp_path / "array_pack.json"
    bad.write_text("[]", encoding="utf-8")
    code = main(["os", "forensics", "run", "--pack", str(bad)])
    assert code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert payload["ops_gate_status"] == "DENIED"
    assert payload["advisory_only"] is True
