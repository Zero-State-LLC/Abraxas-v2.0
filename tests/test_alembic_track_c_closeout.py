from __future__ import annotations

import json
from pathlib import Path

from abraxas.cli import main
from core.alembic.residual_inventory import build_alembic_residual_inventory

REPO = Path(__file__).resolve().parents[1]


def _read_json(path: str) -> dict:
    return json.loads((REPO / path).read_text(encoding="utf-8"))


def test_track_c_inventory_encodes_acceptance_policies() -> None:
    inv = build_alembic_residual_inventory()

    assert inv["spine_status"] == "ALEMBIC_ADVISORY_COMPLETE_WITH_RESIDUALS"
    assert inv["advisory_only"] is True
    assert inv["integration_rule"] == (
        "Domain pipelines may emit architecture-tagged contributions into Alembic; "
        "Alembic must not replace their contracts."
    )
    assert inv["live_rune_policy"]["status"] == "DEFERRED"
    assert inv["live_rune_policy"]["live_catalog_mutation"] is False
    assert inv["backend_unstub_policy"]["required_fixture"] == "EvidencePack"
    assert inv["backend_unstub_policy"]["operator_seal_required"] is True
    assert inv["pipeline_inventory_policy"]["production_inventory_seal_authorized"] is False
    assert all(value is False for value in inv["authority"].values())


def test_architecture_runes_are_proposals_not_live_catalog_mutations() -> None:
    proposals = _read_json("contracts/alembic/rune_proposals.v1.json")
    catalog = _read_json("contracts/runes/catalog.v1.json")

    proposed = set(proposals["proposed_rune_ids"])
    live = {rune["rune_id"] for rune in catalog["runes"]}

    assert proposals["status"] == "ADVISORY_PROPOSALS_ONLY"
    assert proposals["live_catalog_mutation"] is False
    assert {r for r in proposed if r.startswith("RUNE.ARCHITECTURE_")} == {
        "RUNE.ARCHITECTURE_DESCRIBE",
        "RUNE.ARCHITECTURE_ELIGIBILITY",
        "RUNE.ARCHITECTURE_SCORE",
    }
    assert not {r for r in live if r.startswith("RUNE.ARCHITECTURE_")}


def test_alembic_pipeline_and_route_remain_advisory_locked() -> None:
    pipeline = _read_json("contracts/pipelines/alembic_spine.v1_1.json")
    route = _read_json("contracts/yggdrasil/routes/alembic_spine.route.v1.json")

    assert pipeline["pipeline_id"] == "alembic_spine"
    assert pipeline["lane"] == "SHADOW"
    assert route["pipeline_id"] == "alembic_spine"
    assert all(value is False for value in pipeline["authority"].values())
    assert all(value is False for value in route["authority"].values())


def test_cli_surfaces_track_c_closeout_policies(capsys) -> None:
    code = main(["os", "alembic-residuals"])

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["live_rune_policy"]["live_catalog_mutation"] is False
    assert payload["backend_unstub_policy"]["operator_seal_required"] is True
    assert payload["pipeline_inventory_policy"]["production_inventory_seal_authorized"] is False
    assert payload["authority"]["production_authority"] is False


def test_track_c_closeout_docs_name_residual_boundaries() -> None:
    doc = (REPO / "docs/status/ALEMBIC_TRACK_C_RESIDUAL_CLOSEOUT.md").read_text(
        encoding="utf-8"
    )

    assert "Issue: `#1119`" in doc
    assert "RUNE.ARCHITECTURE_*" in doc
    assert "EvidencePack" in doc
    assert "Alembic must not replace their contracts" in doc
    assert "production_authority: false" in doc
