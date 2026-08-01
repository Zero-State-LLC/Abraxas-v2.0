"""Noctis dream → operator_review_queue dry-run (no queue/memory write)."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft7Validator

from abraxas.cli import main
from core.global_operator_review_queue import QUEUE_ITEM_SCHEMA_VERSION
from core.noctis.dream_operator_packet import build_dream_operator_packet
from core.noctis.operator_review_dry_run import (
    build_noctis_operator_review_queue_dry_run,
    build_noctis_review_dry_run_from_narrative,
)

REPO = Path(__file__).resolve().parents[1]
SCHEMA = (
    REPO / "contracts" / "noctis" / "operator_review_queue_dry_run.v0.schema.json"
)
NARRATIVE = (
    "I was walking through a forest of glowing symbols that kept "
    "repeating the same phrase about continuity."
)


def test_dry_run_ready_maps_to_shadow_stabilization():
    dry = build_noctis_review_dry_run_from_narrative(
        NARRATIVE,
        mode="SYSTEM_DREAM",
        privacy_tier="PUBLIC_SYNTHETIC",
        dream_id="synth_dry_001",
        seed="42",
    )
    assert dry["schema_version"] == "NoctisOperatorReviewQueueDryRun.v0"
    assert dry["dry_run"] is True
    assert dry["queue_write_performed"] is False
    assert dry["memory_write_performed"] is False
    assert dry["readiness"] == "SHADOW_OPERATOR_REVIEW"
    item = dry["queue_item"]
    assert item["schema_version"] == QUEUE_ITEM_SCHEMA_VERSION
    assert item["state"] == "eligible_for_shadow_stabilization"
    assert item["priority"] == "P2"
    assert dry["queue_run"]["recommended_next_state"] == "stabilize"
    assert dry["continuity_seed"]["status"] == "SEED_READY"
    assert dry["continuity_seed"]["continuity_write_performed"] is False
    Draft7Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(dry)


def test_dry_run_empty_is_not_computable():
    dry = build_noctis_review_dry_run_from_narrative("   ")
    assert dry["readiness"] == "NOT_COMPUTABLE"
    assert dry["queue_item"]["state"] == "not_computable"
    assert dry["continuity_seed"]["status"] == "SEED_NOT_COMPUTABLE"


def test_dry_run_private_medical_blocked():
    pack = build_dream_operator_packet(
        mode="HUMAN_DREAM",
        dream_id="med_001",
        source="USER",
        privacy_tier="PRIVATE",
        narrative_raw="A private dream about a diagnosis of clinical depression.",
    )
    dry = build_noctis_operator_review_queue_dry_run(pack)
    assert dry["queue_write_performed"] is False
    assert dry["memory_write_performed"] is False
    assert dry["medical_claims_blocked"] is True
    assert dry["readiness"] == "BLOCKED"
    assert dry["queue_item"]["state"] == "held"
    assert dry["queue_item"]["priority"] == "P0"
    assert dry["continuity_seed"]["status"] == "SEED_BLOCKED"


def test_dry_run_deterministic():
    a = build_noctis_review_dry_run_from_narrative(
        NARRATIVE, dream_id="d1", seed="s1", privacy_tier="PUBLIC_SYNTHETIC"
    )
    b = build_noctis_review_dry_run_from_narrative(
        NARRATIVE, dream_id="d1", seed="s1", privacy_tier="PUBLIC_SYNTHETIC"
    )
    assert a == b


def test_cli_os_noctis_review_dry_run(capsys):
    code = main(
        [
            "os",
            "noctis-review-dry-run",
            "--narrative",
            NARRATIVE,
            "--dream-id",
            "cli_dream",
            "--privacy-tier",
            "PUBLIC_SYNTHETIC",
        ]
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["dry_run"] is True
    assert payload["queue_write_performed"] is False
    assert payload["queue_item_state"] == "eligible_for_shadow_stabilization"
