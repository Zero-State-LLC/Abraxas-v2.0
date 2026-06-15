from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_operator_authorization_evidence_validation_review import (
    REVIEW_JSON_PATH,
    write_v2_hygiene_operator_authorization_evidence_validation_review,
)
from core.sync.v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan import (
    PLAN_JSON_PATH,
    build_v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan,
    render_v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan_markdown,
    write_v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan,
)
from scripts import (
    run_v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan.v1.schema.json"
)


def test_v2_hygiene_validation_review_evidence_plan_ready() -> None:
    first = (
        build_v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan(
            REPO_ROOT
        )
    )
    second = (
        build_v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan(
            REPO_ROOT
        )
    )

    assert first["plan_hash"] == second["plan_hash"]
    assert (
        first["status"]
        == "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_VALIDATION_REVIEW_EVIDENCE_PLAN_READY"
    )
    assert first["source_review_ready"] is True
    assert first["evidence_plan_only"] is True
    assert first["recommended_default_disposition"] == "HOLD_FOR_OPERATOR_REVIEW"
    assert first["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert first["safe_to_auto_continue"] is False


def test_v2_hygiene_validation_review_evidence_plan_denies_authority() -> None:
    packet = (
        build_v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan(
            REPO_ROOT
        )
    )

    assert packet["operator_attestations_present"] is False
    assert packet["operator_decision_attested"] is False
    assert packet["evidence_bundle_created"] is False
    assert packet["operator_evidence_bundle_created"] is False
    assert packet["operator_attestation_created"] is False
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
    assert all(value is False for value in packet["authority_locks"].values())


def test_v2_hygiene_validation_review_evidence_plan_groups_fields() -> None:
    packet = (
        build_v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan(
            REPO_ROOT
        )
    )
    groups = {group["group_id"]: group for group in packet["evidence_bundle_groups"]}

    assert set(groups) == {
        "operator_identity",
        "review_scope_acknowledgement",
        "authority_acknowledgements",
        "source_packet_confirmation",
        "operator_disposition",
    }
    assert "operator_signature_reference" in groups["operator_identity"][
        "required_fields"
    ]
    assert "reviewed_validation_review_hash" in groups[
        "review_scope_acknowledgement"
    ]["required_fields"]
    assert "authorization_record_creation_denied_acknowledged" in groups[
        "authority_acknowledgements"
    ]["required_fields"]
    assert "p102g_plus_surface_status_confirmed" in groups[
        "source_packet_confirmation"
    ]["required_fields"]
    assert "requested_follow_on_lane" in groups["operator_disposition"][
        "required_fields"
    ]
    assert "OPERATOR_EVIDENCE_BUNDLE_CREATION" in packet[
        "disallowed_follow_on_actions"
    ]
    assert "V2_MODULE_REGISTRATION" in packet["disallowed_follow_on_actions"]


def test_v2_hygiene_validation_review_evidence_plan_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = (
        build_v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan(
            tmp_path
        )
    )

    assert (
        packet["status"]
        == "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_VALIDATION_REVIEW_EVIDENCE_PLAN_BLOCKED"
    )
    assert packet["source_review_observed"] is False
    assert packet["source_review_ready"] is False
    assert packet["source_review_hash"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert packet["execution_authority"] is False
    assert packet["blockers"]


def test_v2_hygiene_validation_review_evidence_plan_blocks_mutated_source(
    tmp_path: Path,
) -> None:
    write_v2_hygiene_operator_authorization_evidence_validation_review(
        REPO_ROOT, out_root=tmp_path
    )
    source_path = tmp_path / REVIEW_JSON_PATH
    source = json.loads(source_path.read_text(encoding="utf-8"))
    source["operator_attestations_present"] = True
    write_canonical_json(source_path, source)

    packet = (
        build_v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan(
            tmp_path
        )
    )

    assert (
        packet["status"]
        == "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_VALIDATION_REVIEW_EVIDENCE_PLAN_BLOCKED"
    )
    assert packet["source_review_ready"] is False
    assert packet["authorization_record_created"] is False
    assert packet["valid_for_execution"] is False


def test_v2_hygiene_validation_review_evidence_plan_schema_and_hash_are_stable() -> None:
    packet = (
        build_v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan(
            REPO_ROOT
        )
    )
    packet_without_hash = dict(packet)
    plan_hash = packet_without_hash.pop("plan_hash")
    assert plan_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_v2_hygiene_validation_review_evidence_plan_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / PLAN_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["plan_hash"] == packet["plan_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_v2_hygiene_validation_review_evidence_plan_markdown() -> None:
    packet = (
        build_v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan(
            REPO_ROOT
        )
    )
    markdown = render_v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan_markdown(
        packet
    )

    assert (
        markdown[0]
        == "# v2.0 Hygiene Operator Authorization Evidence Validation Review Evidence Plan"
    )
    assert any("operator_identity" in line for line in markdown)
    assert any("reviewed_validation_review_hash" in line for line in markdown)
