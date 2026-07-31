"""Familiar operator-review → operator_review_queue dry-run (no queue write)."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft7Validator

from abraxas.cli import main
from core.global_operator_review_queue import QUEUE_ITEM_SCHEMA_VERSION, QUEUE_RUN_SCHEMA_VERSION
from core.signal.familiar_operator_review import (
    build_familiar_operator_review_packet,
    build_familiar_operator_review_queue_dry_run,
    build_operator_review_from_pack_path,
    build_operator_review_queue_dry_run_from_pack_path,
    normalize_familiar_operator_review,
)
from core.signal.spine_bridge import build_ai_os_kernel_status

REPO = Path(__file__).resolve().parents[1]
FIXTURE = (
    REPO
    / "skills"
    / "abx-familiar-signal-forager"
    / "fixtures"
    / "evidence_pack_hermes_skill_os_2026-07-27.v0.json"
)
DRY_RUN_SCHEMA = (
    REPO
    / "contracts"
    / "signal"
    / "familiar_operator_review_queue_dry_run.v0.schema.json"
)
QUEUE_ITEM_SCHEMA = (
    REPO
    / "contracts"
    / "operator_review"
    / "operator_review_queue_item.v1.schema.json"
)


def _ready_review() -> dict:
    return build_familiar_operator_review_packet(
        {
            "status": "BRIDGED_SHADOW",
            "route": "ORACLE_SHADOW_CANDIDATE",
            "bridge_id": "b_ready",
            "pack_id": "pack_ready",
            "touchpoint_id": "t_ready",
            "belief_candidate_seeds": [{"seed_id": "s1"}],
            "oracle_shadow_intake": {"candidate": True},
            "blocked_by": [],
        }
    )


def test_normalize_ready_for_review_is_operator_review_ready():
    review = _ready_review()
    assert review["disposition"] == "READY_FOR_REVIEW"
    normalized = normalize_familiar_operator_review(review)
    assert normalized["operator_review_ready"] is True
    assert normalized["lane"] == "SHADOW"
    assert normalized["authority"]["promotion_allowed"] is False
    assert "review_familiar_oracle_shadow_intake" in normalized["required_operator_actions"]


def test_dry_run_ready_maps_to_shadow_stabilization_item():
    dry = build_familiar_operator_review_queue_dry_run(_ready_review())
    assert dry["schema_version"] == "FamiliarOperatorReviewQueueDryRun.v0"
    assert dry["dry_run"] is True
    assert dry["queue_write_performed"] is False
    assert dry["queue_write_authorized"] is False
    assert dry["target_queue_path"] == "out/operator_review_queue"
    item = dry["queue_item"]
    assert item["schema_version"] == QUEUE_ITEM_SCHEMA_VERSION
    assert item["state"] == "eligible_for_shadow_stabilization"
    assert item["priority"] == "P2"
    assert item["lane"] == "SHADOW"
    assert item["authority"]["canon_mutation_allowed"] is False
    run = dry["queue_run"]
    assert run["schema_version"] == QUEUE_RUN_SCHEMA_VERSION
    assert run["queue_item_count"] == 1
    assert run["advisory_only"] is True
    assert run["execution_authority"] is False
    assert run["recommended_next_state"] == "stabilize"
    Draft7Validator(json.loads(DRY_RUN_SCHEMA.read_text(encoding="utf-8"))).validate(
        dry
    )
    Draft7Validator(
        json.loads(QUEUE_ITEM_SCHEMA.read_text(encoding="utf-8"))
    ).validate(item)


def test_dry_run_abstain_is_not_computable():
    review = build_familiar_operator_review_packet(
        {
            "status": "BRIDGE_ABSTAINED",
            "route": "ABSTAIN_INVALID",
            "bridge_id": "b1",
            "pack_id": "",
            "touchpoint_id": "t1",
            "belief_candidate_seeds": [],
            "oracle_shadow_intake": {},
            "blocked_by": [],
        }
    )
    dry = build_familiar_operator_review_queue_dry_run(review)
    assert dry["disposition"] == "ABSTAIN"
    item = dry["queue_item"]
    assert item["state"] == "not_computable"
    assert "FAMILIAR_BRIDGE_ABSTAINED" in item["not_computable_reasons"]
    assert dry["queue_write_performed"] is False


def test_dry_run_none_review_not_computable():
    dry = build_familiar_operator_review_queue_dry_run(None)
    assert dry["disposition"] == "NOT_COMPUTABLE"
    assert dry["queue_item"]["state"] == "not_computable"
    assert dry["queue_write_performed"] is False


def test_dry_run_pending_is_held():
    review = build_familiar_operator_review_packet(
        {
            "status": "BRIDGE_PENDING",
            "route": "ORACLE_SHADOW_PENDING",
            "bridge_id": "b2",
            "pack_id": "p2",
            "touchpoint_id": "t2",
            "belief_candidate_seeds": [],
            "oracle_shadow_intake": {},
            "blocked_by": [],
        }
    )
    assert review["disposition"] == "PENDING_OPERATOR"
    dry = build_familiar_operator_review_queue_dry_run(review)
    item = dry["queue_item"]
    assert item["state"] == "held"
    assert item["priority"] == "P0"


def test_dry_run_from_fixture_pack_is_deterministic():
    a = build_operator_review_queue_dry_run_from_pack_path(FIXTURE, repo_root=REPO)
    b = build_operator_review_queue_dry_run_from_pack_path(FIXTURE, repo_root=REPO)
    assert a == b
    assert a["queue_write_performed"] is False
    review = build_operator_review_from_pack_path(FIXTURE, repo_root=REPO)
    assert a["review_packet_hash"] == review["canonical_hash"]
    assert a["disposition"] == review["disposition"]


def test_dry_run_never_writes_queue_path(tmp_path: Path):
    """Pure dry-run must not create out/operator_review_queue artifacts."""
    # If cwd were polluted, still assert explicit write flags and purity.
    before = list((REPO / "out" / "operator_review_queue").glob("*")) if (
        REPO / "out" / "operator_review_queue"
    ).is_dir() else []
    dry = build_operator_review_queue_dry_run_from_pack_path(FIXTURE, repo_root=REPO)
    after = list((REPO / "out" / "operator_review_queue").glob("*")) if (
        REPO / "out" / "operator_review_queue"
    ).is_dir() else []
    assert dry["queue_write_performed"] is False
    assert dry["queue_write_authorized"] is False
    assert before == after
    # Optional audit write is separate from live queue path.
    out = tmp_path / "dry.json"
    code = main(
        [
            "forage",
            "operator-review-dry-run",
            "--pack",
            str(FIXTURE),
            "--out",
            str(out),
        ]
    )
    assert code == 0
    assert out.is_file()
    written = json.loads(out.read_text(encoding="utf-8"))
    assert written["queue_write_performed"] is False
    assert not (tmp_path / "operator_review_queue").exists()


def test_cli_forage_operator_review_dry_run(capsys):
    code = main(["forage", "operator-review-dry-run", "--pack", str(FIXTURE)])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["dry_run"] is True
    assert payload["queue_write_performed"] is False
    assert payload["schema_version"] == "FamiliarOperatorReviewQueueDryRun.v0"
    assert payload["queue_item_id"]
    assert payload["queue_item_state"]
    assert payload["target_queue_path"] == "out/operator_review_queue"


def test_kernel_status_lists_dry_run_command():
    status = build_ai_os_kernel_status(REPO)
    assert status["surfaces"]["operator_review_queue_dry_run_core"] is True
    assert "operator-review-dry-run" in status["commands"]["operator_review_dry_run"]
    assert (
        status["syscall"]["operator_review_queue_dry_run"]
        == "FamiliarOperatorReviewQueueDryRun.v0"
    )
