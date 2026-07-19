from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_authorization_record_dry_run import (
    DRY_RUN_JSON_PATH,
    SOURCE_PLAN_JSON_PATH,
    build_v2_hygiene_phase1_authorization_record_dry_run,
    render_v2_hygiene_phase1_authorization_record_dry_run_markdown,
    write_v2_hygiene_phase1_authorization_record_dry_run,
)
from core.sync.v2_hygiene_phase1_authorization_record_plan import (
    write_v2_hygiene_phase1_authorization_record_plan,
)
from scripts.hygiene import run_v2_hygiene_phase1_authorization_record_dry_run

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/v2_hygiene_phase1_authorization_record_dry_run.v1.schema.json"
)


def test_v2_hygiene_phase1_authorization_record_dry_run_ready() -> None:
    first = build_v2_hygiene_phase1_authorization_record_dry_run(REPO_ROOT)
    second = build_v2_hygiene_phase1_authorization_record_dry_run(REPO_ROOT)

    assert first["dry_run_hash"] == second["dry_run_hash"]
    assert first["status"] == "V2_HYGIENE_PHASE1_AUTHORIZATION_RECORD_DRY_RUN_READY"
    assert first["source_plan_ready"] is True
    assert first["shape_validation_passed"] is True
    assert first["simulated_only"] is True
    assert first["operator_input_required"] is True
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"


def test_v2_hygiene_phase1_authorization_record_dry_run_simulates_missing_operator_input() -> None:
    packet = build_v2_hygiene_phase1_authorization_record_dry_run(REPO_ROOT)
    simulated = packet["simulated_authorization_record"]

    assert simulated["selected_operator_decision"] == "HOLD_FOR_OPERATOR_REVIEW"
    assert simulated["authorization_record_hash"] == "SIMULATED_PENDING_OPERATOR_INPUT"
    assert simulated["required_group_count"] == 5
    assert simulated["required_field_count"] == 27
    assert simulated["attested_group_count"] == 0
    assert simulated["attested_field_count"] == 0
    groups = {group["group_id"]: group for group in simulated["field_groups"]}
    assert set(groups) == {
        "authority_boundary_acknowledgement",
        "operator_identity",
        "phase1_workstream_disposition",
        "record_output_controls",
        "scope_acknowledgement",
    }
    assert groups["operator_identity"]["fields"]["operator_id"]["attested"] is False
    assert (
        groups["scope_acknowledgement"]["fields"]["bulk_reconciliation_hash_acknowledged"][
            "simulated_value"
        ]
        == "SIMULATED_PENDING_OPERATOR_INPUT"
    )
    assert "operator_identity_not_attested" in packet["validation_blockers"]


def test_v2_hygiene_phase1_authorization_record_dry_run_denies_authority() -> None:
    packet = build_v2_hygiene_phase1_authorization_record_dry_run(REPO_ROOT)

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
    simulated = packet["simulated_authorization_record"]
    assert simulated["authorization_record_created"] is False
    assert simulated["implementation_authorized"] is False
    assert simulated["execution_authority"] is False


def test_v2_hygiene_phase1_authorization_record_dry_run_fails_closed_without_plan(
    tmp_path: Path,
) -> None:
    packet = build_v2_hygiene_phase1_authorization_record_dry_run(tmp_path)

    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["source_plan_observed"] is False
    assert packet["source_plan_ready"] is False
    assert packet["shape_validation_passed"] is False
    assert packet["valid_for_execution"] is False
    assert "source_authorization_record_plan_missing_or_unreadable" in packet[
        "validation_blockers"
    ]


def test_v2_hygiene_phase1_authorization_record_dry_run_blocks_mutated_plan(
    tmp_path: Path,
) -> None:
    write_v2_hygiene_phase1_authorization_record_plan(REPO_ROOT, out_root=tmp_path)
    source_path = tmp_path / SOURCE_PLAN_JSON_PATH
    source = json.loads(source_path.read_text(encoding="utf-8"))
    source["implementation_authorized"] = True
    write_canonical_json(source_path, source)

    packet = build_v2_hygiene_phase1_authorization_record_dry_run(tmp_path)

    assert packet["status"] == "V2_HYGIENE_PHASE1_AUTHORIZATION_RECORD_DRY_RUN_BLOCKED"
    assert packet["source_plan_ready"] is False
    assert packet["shape_validation_passed"] is False
    assert packet["authorization_record_created"] is False
    assert packet["valid_for_execution"] is False


def test_v2_hygiene_phase1_authorization_record_dry_run_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase1_authorization_record_dry_run(REPO_ROOT)
    packet_without_hash = dict(packet)
    dry_run_hash = packet_without_hash.pop("dry_run_hash")
    assert dry_run_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_v2_hygiene_phase1_authorization_record_dry_run_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_phase1_authorization_record_dry_run(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / DRY_RUN_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase1_authorization_record_dry_run.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["dry_run_hash"] == packet["dry_run_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_v2_hygiene_phase1_authorization_record_dry_run_markdown() -> None:
    packet = build_v2_hygiene_phase1_authorization_record_dry_run(REPO_ROOT)
    markdown = render_v2_hygiene_phase1_authorization_record_dry_run_markdown(packet)

    assert markdown[0] == "# v2.0 Hygiene Phase 1 Authorization Record Dry Run"
    assert any("shape_validation_passed" in line for line in markdown)
    assert any("operator_identity_not_attested" in line for line in markdown)
