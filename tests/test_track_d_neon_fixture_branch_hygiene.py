"""Tests for Track D light, neon fixtures residual, branch hygiene inventory."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft7Validator

from abraxas.cli import main
from core.engineering.branch_hygiene_inventory import build_branch_hygiene_inventory
from core.neon_genie.ideation_operator_packet import (
    build_ideation_operator_packet_from_venture,
)

REPO = Path(__file__).resolve().parents[1]
NEON_FIX = REPO / "skills" / "abx-neon-genie" / "fixtures"
BRANCH_SCHEMA = (
    REPO / "contracts" / "engineering" / "branch_hygiene_inventory.v0.schema.json"
)
TRACK_D = REPO / "docs" / "plans" / "AUTHZ_SURFACE_COMPRESSION_TRACK_D_001.md"
BRANCH_DOC = REPO / "docs" / "status" / "BRANCH_HYGIENE_INVENTORY_001.md"


def test_track_d_doc_exists():
    assert TRACK_D.is_file()
    text = TRACK_D.read_text(encoding="utf-8")
    assert "Terminal-hold rule" in text or "terminal" in text.lower()
    assert "HISTORICAL" in text


def test_branch_hygiene_doc_exists():
    assert BRANCH_DOC.is_file()
    assert "delete_authorized" in BRANCH_DOC.read_text(encoding="utf-8") or "Never" in BRANCH_DOC.read_text(
        encoding="utf-8"
    )


def test_neon_fixtures_present_and_usable():
    files = sorted(NEON_FIX.glob("venture_request_*.v0.json"))
    assert len(files) >= 3
    for path in files:
        req = json.loads(path.read_text(encoding="utf-8"))
        assert req.get("mode")
        # Lift to operator packet via venture-like fields
        pack = build_ideation_operator_packet_from_venture(
            {
                "input_mode": req["mode"],
                "venture_name": req.get("seed", "fixture")[:80],
                "overlap_classification": "NOVEL",
            },
            evidence_pack=req.get("evidence_pack")
            if isinstance(req.get("evidence_pack"), dict)
            else None,
        )
        assert pack["schema_version"] == "NeonGenieIdeationOperatorPacket.v0"
        assert pack["authority"]["execution_authority"] is False


def test_neon_router_accepts_prompt_fixture():
    import importlib.util
    import sys

    skill = REPO / "skills" / "abx-neon-genie"
    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(skill))
    # Load router via importlib to avoid package hyphen issues
    path = skill / "neon_genie_router.py"
    spec = importlib.util.spec_from_file_location("neon_genie_router_fix", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["neon_genie_router_fix"] = mod
    spec.loader.exec_module(mod)
    req = json.loads(
        (NEON_FIX / "venture_request_prompt_led.v0.json").read_text(encoding="utf-8")
    )
    result = mod.run_venture_cycle(req)
    assert "operator_packet" in result
    assert result["authority"]["execution_authority"] is False


def test_branch_hygiene_inventory_injected_deterministic():
    heads = [
        "main",
        "codex/foo-stale",
        "copilot/bar",
        "feat/live-work",
        "docs/something",
    ]
    prs = ["feat/live-work"]
    a = build_branch_hygiene_inventory(
        branch_names=heads, open_pr_heads=prs, sample_limit=10
    )
    b = build_branch_hygiene_inventory(
        branch_names=heads, open_pr_heads=prs, sample_limit=10
    )
    assert a == b
    assert a["delete_authorized"] is False
    assert a["authority"]["remote_delete_authorized"] is False
    assert a["total_heads"] == 5
    assert a["class_counts"]["KEEP"] == 1
    assert a["class_counts"]["OPEN_PR"] == 1
    assert a["class_counts"]["CANDIDATE_STALE"] >= 2
    Draft7Validator(json.loads(BRANCH_SCHEMA.read_text(encoding="utf-8"))).validate(a)


def test_cli_branch_hygiene(capsys):
    # Inject via env not available — CLI hits real remote; still must never authorize delete
    code = main(["os", "branch-hygiene"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["delete_authorized"] is False
    assert payload["ok"] is True
    assert "class_counts" in payload
