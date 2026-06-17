from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_authorization_record_plan import (
    PLAN_JSON_PATH,
    SOURCE_PHASE1_RECONCILIATION,
    build_v2_hygiene_phase1_authorization_record_plan,
    render_v2_hygiene_phase1_authorization_record_plan_markdown,
    write_v2_hygiene_phase1_authorization_record_plan,
)
from core.sync.v2_hygiene_phase1_bulk_approval_reconciliation import (
    write_v2_hygiene_phase1_bulk_approval_reconciliation,
)
from scripts import run_v2_hygiene_phase1_authorization_record_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/v2_hygiene_phase1_authorization_record_plan.v1.schema.json"
)


def test_v2_hygiene_phase1_authorization_record_plan_ready() -> None:
    first = build_v2_hygiene_phase1_authorization_record_plan(REPO_ROOT)
    second = build_v2_hygiene_phase1_authorization_record_plan(REPO_ROOT)

    assert first["plan_hash"] == second["plan_hash"]
    assert first["status"] == "V2_HYGIENE_PHASE1_AUTHORIZATION_RECORD_PLAN_READY"
    assert first["source_ready"] is True
    assert first["record_plan_only"] is True
    assert first["operator_input_required"] is True
    assert first["authorization_record_creation_required_before_implementation"] is True
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert first["record_readiness_summary"]["source_record_count"] == 3
    assert first["record_readiness_summary"]["required_group_count"] == 5
    assert first["record_readiness_summary"]["authorization_record_ready"] is False


def test_v2_hygiene_phase1_authorization_record_plan_denies_authority() -> None:
    packet = build_v2_hygiene_phase1_authorization_record_plan(REPO_ROOT)

    assert packet["operator_attestations_present"] is False
    assert packet["authorization_record_created"] is False
    assert packet["authorization_record_creation_authorized"] is False
    assert packet["implementation_authorized"] is False
    assert packet["valid_for_authorization_record"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["valid_for_execution"] is False
    assert packet["safe_to_prepare_patch"] is False
    assert packet["safe_to_auto_continue"] is False
    assert packet["hygiene_code_creation_authorized"] is False
    assert packet["schema_file_creation_authorized"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_v2_hygiene_phase1_authorization_record_plan_groups_fields() -> None:
    packet = build_v2_hygiene_phase1_authorization_record_plan(REPO_ROOT)
    groups = {group["group_id"]: group for group in packet["record_field_groups"]}

    assert set(groups) == {
        "operator_identity",
        "scope_acknowledgement",
        "authority_boundary_acknowledgement",
        "phase1_workstream_disposition",
        "record_output_controls",
    }
    assert "operator_signature_reference" in groups["operator_identity"]["required_fields"]
    assert "bulk_reconciliation_hash_acknowledged" in groups["scope_acknowledgement"][
        "required_fields"
    ]
    assert "execution_authority_denied_acknowledged" in groups[
        "authority_boundary_acknowledgement"
    ]["required_fields"]
    assert "approved_phase1_task_ids" in groups["phase1_workstream_disposition"][
        "required_fields"
    ]
    assert "selected_operator_decision" in groups["record_output_controls"][
        "required_fields"
    ]
    assert "AUTHORIZATION_RECORD_CREATION" in packet["disallowed_follow_on_actions"]
    assert "HYGIENE_CODE_CREATION" in packet["disallowed_follow_on_actions"]


def test_v2_hygiene_phase1_authorization_record_plan_fails_closed_without_sources(
    tmp_path: Path,
) -> None:
    packet = build_v2_hygiene_phase1_authorization_record_plan(tmp_path)

    assert packet["status"] == "V2_HYGIENE_PHASE1_AUTHORIZATION_RECORD_PLAN_BLOCKED"
    assert packet["source_ready"] is False
    assert packet["authorization_record_created"] is False
    assert packet["valid_for_execution"] is False
    assert packet["blockers"]


def test_v2_hygiene_phase1_authorization_record_plan_blocks_mutated_reconciliation(
    tmp_path: Path,
) -> None:
    write_v2_hygiene_phase1_bulk_approval_reconciliation(REPO_ROOT, out_root=tmp_path)
    source_path = tmp_path / SOURCE_PHASE1_RECONCILIATION
    source = json.loads(source_path.read_text(encoding="utf-8"))
    source["implementation_authorized"] = True
    write_canonical_json(source_path, source)

    packet = build_v2_hygiene_phase1_authorization_record_plan(tmp_path)

    assert packet["status"] == "V2_HYGIENE_PHASE1_AUTHORIZATION_RECORD_PLAN_BLOCKED"
    assert packet["valid_for_execution"] is False
    assert packet["authorization_record_created"] is False


def test_v2_hygiene_phase1_authorization_record_plan_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase1_authorization_record_plan(REPO_ROOT)
    packet_without_hash = dict(packet)
    plan_hash = packet_without_hash.pop("plan_hash")
    assert plan_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_v2_hygiene_phase1_authorization_record_plan_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_phase1_authorization_record_plan(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / PLAN_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase1_authorization_record_plan.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["plan_hash"] == packet["plan_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_v2_hygiene_phase1_authorization_record_plan_markdown() -> None:
    packet = build_v2_hygiene_phase1_authorization_record_plan(REPO_ROOT)
    markdown = render_v2_hygiene_phase1_authorization_record_plan_markdown(packet)

    assert markdown[0] == "# v2.0 Hygiene Phase 1 Authorization Record Plan"
    assert any("record_plan_only" in line for line in markdown)
    assert any("operator_identity" in line for line in markdown)
