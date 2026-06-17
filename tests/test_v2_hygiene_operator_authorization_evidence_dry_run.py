from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.v2_hygiene_operator_authorization_evidence_dry_run import (
    build_v2_hygiene_operator_authorization_evidence_dry_run,
    render_v2_hygiene_operator_authorization_evidence_dry_run_markdown,
    write_v2_hygiene_operator_authorization_evidence_dry_run,
)
from scripts import run_v2_hygiene_operator_authorization_evidence_dry_run

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_operator_authorization_evidence_dry_run.v1.schema.json"
)


def test_v2_hygiene_operator_authorization_evidence_dry_run_ready() -> None:
    first = build_v2_hygiene_operator_authorization_evidence_dry_run(REPO_ROOT)
    second = build_v2_hygiene_operator_authorization_evidence_dry_run(REPO_ROOT)

    assert first["dry_run_hash"] == second["dry_run_hash"]
    assert first["status"] == "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_DRY_RUN_READY"
    assert first["source_evidence_request_plan_ready"] is True
    assert first["simulated_only"] is True
    assert first["operator_input_required"] is True
    assert first["readiness_summary"]["groups_total"] == 5
    assert first["readiness_summary"]["groups_ready"] == 0
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert first["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_v2_hygiene_operator_authorization_evidence_dry_run_denies_authority() -> None:
    packet = build_v2_hygiene_operator_authorization_evidence_dry_run(REPO_ROOT)

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
    assert packet["safe_to_auto_continue"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_v2_hygiene_operator_authorization_evidence_dry_run_simulates_missing_groups() -> None:
    packet = build_v2_hygiene_operator_authorization_evidence_dry_run(REPO_ROOT)
    groups = {group["group_id"]: group for group in packet["simulated_evidence_bundle"]}

    assert set(groups) == {
        "operator_identity",
        "review_acknowledgements",
        "provenance_evidence",
        "workstream_disposition",
        "evidence_request_outputs",
    }
    assert groups["operator_identity"]["attested"] is False
    assert "operator_id" in groups["operator_identity"]["missing_fields"]
    assert "reviewed_alignment_plan_hash" in groups["provenance_evidence"][
        "missing_fields"
    ]
    assert "approved_workstreams" in groups["workstream_disposition"][
        "missing_fields"
    ]
    assert "operator_identity_not_attested" in packet["evaluation_blockers"]
    assert "AUTHORIZATION_RECORD_CREATION" in packet["disallowed_follow_on_actions"]


def test_v2_hygiene_operator_authorization_evidence_dry_run_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_v2_hygiene_operator_authorization_evidence_dry_run(tmp_path)

    assert packet["status"] == "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_DRY_RUN_BLOCKED"
    assert packet["source_evidence_request_plan_observed"] is False
    assert packet["source_evidence_request_plan_ready"] is False
    assert packet["source_evidence_request_plan_hash"] == "NOT_COMPUTABLE"
    assert packet["valid_for_authorization_record"] is False
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert packet["evaluation_blockers"]


def test_v2_hygiene_operator_authorization_evidence_dry_run_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_operator_authorization_evidence_dry_run(REPO_ROOT)
    packet_without_hash = dict(packet)
    dry_run_hash = packet_without_hash.pop("dry_run_hash")
    assert dry_run_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_v2_hygiene_operator_authorization_evidence_dry_run_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_operator_authorization_evidence_dry_run(
        REPO_ROOT, out_root=tmp_path
    )
    out_json = (
        tmp_path
        / "out/operator_review/"
        "v2_hygiene_operator_authorization_evidence_dry_run_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_operator_authorization_evidence_dry_run.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["dry_run_hash"] == packet["dry_run_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_v2_hygiene_operator_authorization_evidence_dry_run_markdown() -> None:
    packet = build_v2_hygiene_operator_authorization_evidence_dry_run(REPO_ROOT)
    markdown = render_v2_hygiene_operator_authorization_evidence_dry_run_markdown(
        packet
    )

    assert markdown[0] == "# v2.0 Hygiene Operator Authorization Evidence Dry Run"
    assert any("operator_identity_not_attested" in line for line in markdown)
    assert any("workstream_disposition" in line for line in markdown)
