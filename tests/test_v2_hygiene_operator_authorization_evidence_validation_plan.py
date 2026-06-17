from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_operator_authorization_evidence_dry_run import (
    write_v2_hygiene_operator_authorization_evidence_dry_run,
)
from core.sync.v2_hygiene_operator_authorization_evidence_validation_plan import (
    VALIDATION_PLAN_JSON_PATH,
    build_v2_hygiene_operator_authorization_evidence_validation_plan,
    render_v2_hygiene_operator_authorization_evidence_validation_plan_markdown,
    write_v2_hygiene_operator_authorization_evidence_validation_plan,
)
from scripts import run_v2_hygiene_operator_authorization_evidence_validation_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_operator_authorization_evidence_validation_plan.v1.schema.json"
)


def test_v2_hygiene_operator_authorization_evidence_validation_plan_ready() -> None:
    first = build_v2_hygiene_operator_authorization_evidence_validation_plan(REPO_ROOT)
    second = build_v2_hygiene_operator_authorization_evidence_validation_plan(REPO_ROOT)

    assert first["validation_plan_hash"] == second["validation_plan_hash"]
    assert (
        first["status"]
        == "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_VALIDATION_PLAN_READY"
    )
    assert first["source_dry_run_observed"] is True
    assert first["source_dry_run_ready"] is True
    assert first["validation_blockers"] == []
    assert first["blockers"] == []
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert first["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert first["recommended_next_state"] == "hold"


def test_v2_hygiene_operator_authorization_evidence_validation_plan_denies_authority() -> None:
    packet = build_v2_hygiene_operator_authorization_evidence_validation_plan(
        REPO_ROOT
    )

    assert packet["validation_plan_only"] is True
    assert packet["simulated_only"] is True
    assert packet["operator_input_required"] is True
    assert packet["operator_attestations_present"] is False
    assert packet["operator_evidence_bundle_created"] is False
    assert packet["authorization_record_created"] is False
    assert packet["authorization_record_creation_authorized"] is False
    assert packet["implementation_authorized"] is False
    assert packet["v2_module_registration_authorized"] is False
    assert packet["rune_registration_authorized"] is False
    assert packet["projection_surface_mutation_authorized"] is False
    assert packet["schema_mutation_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_authorization_record"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["valid_for_execution"] is False
    assert packet["notion_writeback_allowed"] is False
    assert packet["github_writeback_allowed"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert all(check["passed"] is True for check in packet["authority_lock_checks"])


def test_v2_hygiene_operator_authorization_evidence_validation_plan_checks_bundle_shape() -> None:
    packet = build_v2_hygiene_operator_authorization_evidence_validation_plan(
        REPO_ROOT
    )
    groups = {check["group_id"]: check for check in packet["bundle_group_checks"]}

    assert set(groups) == {
        "operator_identity",
        "review_acknowledgements",
        "provenance_evidence",
        "workstream_disposition",
        "evidence_request_outputs",
    }
    assert groups["operator_identity"]["field_count"] == 4
    assert groups["review_acknowledgements"]["field_count"] == 3
    assert groups["provenance_evidence"]["field_count"] == 1
    assert groups["workstream_disposition"]["field_count"] == 2
    assert groups["evidence_request_outputs"]["field_count"] == 3
    assert all(check["passed"] is True for check in packet["bundle_group_checks"])
    assert all(check["passed"] is True for check in packet["invariant_checks"])
    assert all(check["passed"] is True for check in packet["validation_checks"])


def test_v2_hygiene_operator_authorization_evidence_validation_plan_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_v2_hygiene_operator_authorization_evidence_validation_plan(
        tmp_path
    )

    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["source_dry_run_observed"] is False
    assert packet["source_dry_run_ready"] is False
    assert packet["valid_for_authorization_record"] is False
    assert "source_dry_run_missing_or_unreadable" in packet["blockers"]
    assert "source_dry_run_missing_or_not_ready" in packet["validation_blockers"]


def test_v2_hygiene_operator_authorization_evidence_validation_plan_blocks_mutated_source(
    tmp_path: Path,
) -> None:
    write_v2_hygiene_operator_authorization_evidence_dry_run(
        REPO_ROOT, out_root=tmp_path
    )
    source_path = tmp_path / VALIDATION_PLAN_JSON_PATH.parent / (
        "v2_hygiene_operator_authorization_evidence_dry_run_001.latest.json"
    )
    source = json.loads(source_path.read_text(encoding="utf-8"))
    source["readiness_summary"]["groups_ready"] = 1
    write_canonical_json(source_path, source)

    packet = build_v2_hygiene_operator_authorization_evidence_validation_plan(
        tmp_path
    )

    assert (
        packet["status"]
        == "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_VALIDATION_PLAN_BLOCKED_BY_DRY_RUN"
    )
    assert "summary_groups_ready" in packet["validation_blockers"]
    assert packet["valid_for_authorization_record"] is False
    assert packet["execution_authority"] is False


def test_v2_hygiene_operator_authorization_evidence_validation_plan_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_operator_authorization_evidence_validation_plan(
        REPO_ROOT
    )
    packet_without_hash = dict(packet)
    validation_plan_hash = packet_without_hash.pop("validation_plan_hash")
    assert validation_plan_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_v2_hygiene_operator_authorization_evidence_validation_plan_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_operator_authorization_evidence_validation_plan(
        REPO_ROOT, out_root=tmp_path
    )
    out_json = tmp_path / VALIDATION_PLAN_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_operator_authorization_evidence_validation_plan.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["validation_plan_hash"] == packet["validation_plan_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_v2_hygiene_operator_authorization_evidence_validation_plan_markdown() -> None:
    packet = build_v2_hygiene_operator_authorization_evidence_validation_plan(
        REPO_ROOT
    )
    markdown = render_v2_hygiene_operator_authorization_evidence_validation_plan_markdown(
        packet
    )

    assert markdown[0] == "# v2.0 Hygiene Operator Authorization Evidence Validation Plan"
    assert any("source_dry_run_ready" in line for line in markdown)
    assert any("Bundle Group Checks" in line for line in markdown)
