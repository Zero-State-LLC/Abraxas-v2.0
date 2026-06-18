from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.v2_hygiene_phase1_clean_frontier_operator_authorization_bridge import (
    BRIDGE_JSON_PATH,
    READY_STATUS,
    build_v2_hygiene_phase1_clean_frontier_operator_authorization_bridge,
    render_v2_hygiene_phase1_clean_frontier_operator_authorization_bridge_markdown,
    write_v2_hygiene_phase1_clean_frontier_operator_authorization_bridge,
)
from core.sync.v2_hygiene_phase1_clean_frontier_noop_repair_execution_receipt import (
    try_build_clean_frontier_noop_repair_execution_receipt,
)
from scripts import run_v2_hygiene_phase1_clean_frontier_operator_authorization_bridge

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase1_clean_frontier_operator_authorization_bridge.v1.schema.json"
)


def test_clean_frontier_operator_authorization_bridge_ready_path_is_stable() -> None:
    first = build_v2_hygiene_phase1_clean_frontier_operator_authorization_bridge(REPO_ROOT)
    second = build_v2_hygiene_phase1_clean_frontier_operator_authorization_bridge(REPO_ROOT)

    assert first["bridge_hash"] == second["bridge_hash"]
    assert first["status"] == READY_STATUS
    assert first["clean_inventory_attested"] is True
    assert first["deletion_authorized"] is False
    assert first["package_lock_mutation_authorized"] is False
    assert first["execution_authority"] is False
    assert first["source_blockers"] == []


def test_clean_frontier_noop_repair_emits_ready_receipt_on_clean_repo() -> None:
    packet = try_build_clean_frontier_noop_repair_execution_receipt(REPO_ROOT)

    assert packet is not None
    assert packet["status"] == (
        "V2_HYGIENE_PHASE1_DUPLICATE_FRONTIER_QUARANTINE_REPAIR_EXECUTION_RECEIPT_READY"
    )
    assert packet["repair_already_complete_before_run"] is True
    assert packet["repair_performed"] is True
    assert packet["deleted_paths"] == []
    assert packet["repair_summary"]["post_duplicate_remaining_count"] == 0
    assert packet["repair_summary"]["deleted_path_count"] == 466


def test_clean_frontier_operator_authorization_bridge_preserves_authority_denials() -> None:
    packet = build_v2_hygiene_phase1_clean_frontier_operator_authorization_bridge(REPO_ROOT)

    assert packet["implementation_authorized"] is False
    assert packet["subsystem_implementation_authorized"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_clean_frontier_operator_authorization_bridge_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase1_clean_frontier_operator_authorization_bridge(REPO_ROOT)
    packet_without_hash = dict(packet)
    bridge_hash = packet_without_hash.pop("bridge_hash")
    assert bridge_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_clean_frontier_operator_authorization_bridge_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_phase1_clean_frontier_operator_authorization_bridge(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / BRIDGE_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase1_clean_frontier_operator_authorization_bridge.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["bridge_hash"] == packet["bridge_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_clean_frontier_operator_authorization_bridge_markdown() -> None:
    packet = build_v2_hygiene_phase1_clean_frontier_operator_authorization_bridge(REPO_ROOT)
    markdown = render_v2_hygiene_phase1_clean_frontier_operator_authorization_bridge_markdown(
        packet
    )

    assert markdown[0] == "# v2.0 Hygiene Phase 1 Clean Frontier Operator Authorization Bridge"
    assert any("deletion_authorized: False" in line for line in markdown)
