from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run import (
    DRY_RUN_JSON_PATH,
    write_v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run,
)
from core.sync.v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_review import (
    REVIEW_JSON_PATH,
    build_v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_review,
    render_v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_review_markdown,
    write_v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_review,
)
from scripts.hygiene import (
    run_v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_review,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_review.v1.schema.json"
)


def _seed_ready_dry_run(tmp_path: Path) -> None:
    write_v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run(
        REPO_ROOT,
        out_root=tmp_path,
    )


def test_v2_hygiene_validation_review_evidence_dry_run_review_held() -> None:
    first = (
        build_v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_review(
            REPO_ROOT
        )
    )
    second = (
        build_v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_review(
            REPO_ROOT
        )
    )

    assert first["review_hash"] == second["review_hash"]
    assert (
        first["status"]
        == "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_VALIDATION_REVIEW_EVIDENCE_DRY_RUN_REVIEW_HELD_FOR_OPERATOR"
    )
    assert first["source_validation_review_evidence_dry_run_ready"] is True
    assert first["selected_operator_decision"] == "HOLD_FOR_OPERATOR_REVIEW"
    assert (
        first["selected_follow_on_action"]
        == "MAINTAIN_V2_HYGIENE_OPERATOR_AUTHORIZATION_HOLD"
    )
    assert first["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert first["safe_to_auto_continue"] is False


def test_v2_hygiene_validation_review_evidence_dry_run_review_denies_authority() -> None:
    packet = (
        build_v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_review(
            REPO_ROOT
        )
    )

    assert packet["operator_review_required"] is True
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
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert all(
        finding["authority_granted"] is False for finding in packet["review_findings"]
    )


def test_v2_hygiene_validation_review_evidence_dry_run_review_observes_source() -> None:
    packet = (
        build_v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_review(
            REPO_ROOT
        )
    )
    findings = {finding["finding_id"]: finding for finding in packet["review_findings"]}

    assert packet["source_readiness"] == "SOURCE_VALIDATION_REVIEW_EVIDENCE_DRY_RUN_READY"
    assert packet["source_evaluation_blockers"] == [
        "operator_identity_not_attested",
        "review_scope_acknowledgement_not_attested",
        "authority_acknowledgements_not_attested",
        "source_packet_confirmation_not_attested",
        "operator_disposition_not_attested",
    ]
    assert packet["source_simulated_evidence_group_ids"] == [
        "operator_identity",
        "review_scope_acknowledgement",
        "authority_acknowledgements",
        "source_packet_confirmation",
        "operator_disposition",
    ]
    assert findings["source_dry_run_ready"]["finding_status"] == "OBSERVED"
    assert (
        findings["external_operator_attestations_missing"]["finding_status"]
        == "HELD_FOR_OPERATOR"
    )
    assert (
        findings["authorization_record_creation_denied"]["finding_status"]
        == "ENFORCED"
    )
    assert "external operator attestations remain missing" in packet[
        "terminal_hold_reason"
    ]


def test_v2_hygiene_validation_review_evidence_dry_run_review_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = (
        build_v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_review(
            tmp_path
        )
    )

    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["source_validation_review_evidence_dry_run_observed"] is False
    assert packet["source_validation_review_evidence_dry_run_ready"] is False
    assert packet["source_validation_review_evidence_dry_run_packet_hash"] == "NOT_COMPUTABLE"
    assert packet["selected_operator_decision"] == "NOT_COMPUTABLE"
    assert packet["valid_for_authorization_record"] is False


def test_v2_hygiene_validation_review_evidence_dry_run_review_blocks_mutated_source(
    tmp_path: Path,
) -> None:
    _seed_ready_dry_run(tmp_path)
    source_path = tmp_path / DRY_RUN_JSON_PATH
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    payload["operator_attestations_present"] = True
    write_canonical_json(source_path, payload)

    packet = (
        build_v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_review(
            tmp_path
        )
    )

    assert (
        packet["status"]
        == "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_VALIDATION_REVIEW_EVIDENCE_DRY_RUN_REVIEW_BLOCKED"
    )
    assert packet["source_validation_review_evidence_dry_run_ready"] is False
    assert packet["selected_follow_on_action"] == "NOT_COMPUTABLE"
    assert packet["valid_for_execution"] is False


def test_v2_hygiene_validation_review_evidence_dry_run_review_schema_and_hash_are_stable() -> None:
    packet = (
        build_v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_review(
            REPO_ROOT
        )
    )
    packet_without_hash = dict(packet)
    review_hash = packet_without_hash.pop("review_hash")
    assert review_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_v2_hygiene_validation_review_evidence_dry_run_review_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    _seed_ready_dry_run(tmp_path)
    packet = write_v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_review(
        tmp_path,
        out_root=tmp_path,
    )
    out_json = tmp_path / REVIEW_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_review.run(
        repo_root=tmp_path,
        out_root=tmp_path,
    )

    assert second["review_hash"] == packet["review_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_v2_hygiene_validation_review_evidence_dry_run_review_markdown() -> None:
    packet = (
        build_v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_review(
            REPO_ROOT
        )
    )
    markdown = (
        render_v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_review_markdown(
            packet
        )
    )

    assert (
        markdown[0]
        == "# v2.0 Hygiene Operator Authorization Evidence Validation Review Evidence Dry Run Review"
    )
    assert any("external_operator_attestations_missing" in line for line in markdown)
    assert any("operator_disposition" in line for line in markdown)
