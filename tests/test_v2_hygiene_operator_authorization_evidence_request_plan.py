from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.v2_hygiene_operator_authorization_evidence_request_plan import (
    build_v2_hygiene_operator_authorization_evidence_request_plan,
    render_v2_hygiene_operator_authorization_evidence_request_plan_markdown,
    write_v2_hygiene_operator_authorization_evidence_request_plan,
)
from scripts.hygiene import run_v2_hygiene_operator_authorization_evidence_request_plan

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_v2_hygiene_operator_authorization_evidence_request_plan_ready() -> None:
    first = build_v2_hygiene_operator_authorization_evidence_request_plan(REPO_ROOT)
    second = build_v2_hygiene_operator_authorization_evidence_request_plan(REPO_ROOT)

    assert first["plan_hash"] == second["plan_hash"]
    assert first["status"] == "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_REQUEST_PLAN_READY"
    assert first["source_gate_ready"] is True
    assert first["evidence_request_only"] is True
    assert first["operator_input_required"] is True
    assert first["recommended_default_decision"] == "HOLD"
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert first["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_v2_hygiene_operator_authorization_evidence_request_plan_denies_authority() -> None:
    packet = build_v2_hygiene_operator_authorization_evidence_request_plan(REPO_ROOT)

    assert packet["authorization_record_created"] is False
    assert packet["authorization_record_creation_authorized"] is False
    assert packet["implementation_authorized"] is False
    assert packet["v2_module_registration_authorized"] is False
    assert packet["rune_registration_authorized"] is False
    assert packet["projection_surface_mutation_authorized"] is False
    assert packet["schema_mutation_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_v2_hygiene_operator_authorization_evidence_request_plan_groups_fields() -> None:
    packet = build_v2_hygiene_operator_authorization_evidence_request_plan(REPO_ROOT)
    groups = {group["group_id"]: group for group in packet["evidence_bundle_groups"]}

    assert set(groups) == {
        "operator_identity",
        "review_acknowledgements",
        "provenance_evidence",
        "workstream_disposition",
        "evidence_request_outputs",
    }
    assert "operator_id" in groups["operator_identity"]["required_fields"]
    assert "authorization_scope_acknowledged" in groups[
        "review_acknowledgements"
    ]["required_fields"]
    assert "reviewed_alignment_plan_hash" in groups["provenance_evidence"][
        "required_fields"
    ]
    assert "approved_workstreams" in groups["workstream_disposition"]["required_fields"]
    assert "V2_MODULE_REGISTRATION" in packet["disallowed_follow_on_actions"]


def test_v2_hygiene_operator_authorization_evidence_request_plan_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_v2_hygiene_operator_authorization_evidence_request_plan(tmp_path)

    assert packet["status"] == "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_REQUEST_PLAN_BLOCKED"
    assert packet["source_gate_ready"] is False
    assert packet["source_gate_hash"] == "NOT_COMPUTABLE"
    assert packet["authorization_record_created"] is False
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert packet["blockers"]


def test_v2_hygiene_operator_authorization_evidence_request_plan_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_operator_authorization_evidence_request_plan(REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("plan_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads(
        (
            REPO_ROOT
            / "contracts/operator_review/"
            "v2_hygiene_operator_authorization_evidence_request_plan.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)


def test_v2_hygiene_operator_authorization_evidence_request_plan_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_operator_authorization_evidence_request_plan(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = (
        tmp_path
        / "out/operator_review/"
        "v2_hygiene_operator_authorization_evidence_request_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_operator_authorization_evidence_request_plan.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["plan_hash"] == packet["plan_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_v2_hygiene_operator_authorization_evidence_request_plan_markdown() -> None:
    packet = build_v2_hygiene_operator_authorization_evidence_request_plan(REPO_ROOT)
    markdown = render_v2_hygiene_operator_authorization_evidence_request_plan_markdown(
        packet
    )

    assert markdown[0] == "# v2.0 Hygiene Operator Authorization Evidence Request Plan"
    assert any("operator_identity" in line for line in markdown)
    assert any("reviewed_alignment_plan_hash" in line for line in markdown)
