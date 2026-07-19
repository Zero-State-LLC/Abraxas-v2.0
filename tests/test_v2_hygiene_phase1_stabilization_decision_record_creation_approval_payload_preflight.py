from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import write_canonical_json
from scripts.preflight_v2_hygiene_phase1_stabilization_decision_record_creation_approval_payload import (
    AUTHORITY_EXPANDING_FIELDS,
    DEFAULT_CREATION_APPROVAL_PAYLOAD_PATH,
    REQUIRED_FIELDS,
    REQUIRED_GROUPS,
    SOURCE_AUTHORIZATION_GATE_PATH,
    SOURCE_COMPRESSION_AUDIT_PATH,
    preflight_payload,
    render_preflight_lines,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_TEMPLATE_PATH = (
    "operator_input/templates/"
    "v2_hygiene_phase1_stabilization_decision_record_creation_approval_payload_001.example.json"
)
README_PATH = "operator_input/templates/README.md"
HANDOFF_PATH = (
    "operator_input/templates/"
    "v2_hygiene_phase1_stabilization_decision_record_creation_approval_handoff.md"
)


def _source_hashes() -> tuple[str, str]:
    gate = json.loads((REPO_ROOT / SOURCE_AUTHORIZATION_GATE_PATH).read_text(encoding="utf-8"))
    audit = json.loads((REPO_ROOT / SOURCE_COMPRESSION_AUDIT_PATH).read_text(encoding="utf-8"))
    return str(gate["gate_hash"]), str(audit["audit_hash"])


def _complete_payload() -> dict:
    gate_hash, audit_hash = _source_hashes()
    return {
        "operator_identity": {
            "operator_id": "operator-reviewer-001",
            "operator_reviewed_at_source_observed": "2026-06-15T00:00:00Z",
            "operator_approval_hash": (
                "sha256:"
                "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
            ),
        },
        "creation_scope_acknowledgement": {
            "source_authorization_gate_path": SOURCE_AUTHORIZATION_GATE_PATH.as_posix(),
            "source_authorization_gate_hash": gate_hash,
            "source_compression_audit_path": SOURCE_COMPRESSION_AUDIT_PATH.as_posix(),
            "source_compression_audit_hash": audit_hash,
            "terminal_creation_hold_acknowledged": True,
        },
        "creation_disposition": {
            "approved_record_id": "v2_hygiene_phase1_stabilization_decision_record_001",
            "approved_record_output_path": (
                "out/operator_review/"
                "v2_hygiene_phase1_stabilization_decision_record_001.latest.json"
            ),
            "selected_creation_disposition": (
                "APPROVE_DECISION_RECORD_CREATION_FOR_SEPARATE_GOVERNED_"
                "MATERIALIZATION_LANE"
            ),
            "decision_record_creation_now_allowed": False,
            "decision_record_auto_creation_allowed": False,
            "separate_materialization_lane_required": True,
        },
        "authority_boundary_acknowledgement": {
            "no_decision_record_auto_creation": True,
            "no_hygiene_implementation_authority": True,
            "no_execution_authority": True,
            "no_runtime_canon_queue_scheduler_mutation": True,
            "no_notion_or_github_writeback": True,
            "no_registration_or_promotion": True,
            "no_activation": True,
            "no_auto_continuation": True,
        },
        "terminal_output_controls": {
            "downstream_lane_disposition": (
                "NOT_COMPUTABLE_UNTIL_GOVERNED_DECISION_RECORD_CREATION_"
                "MATERIALIZATION"
            ),
            "future_materialization_gate_required": True,
            "future_record_creation_allowed_by_this_payload": False,
            "rollback_or_supersession_policy": (
                "fresh governed operator decision required"
            ),
        },
    }


def _write_payload(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "operator_input/payload.json"
    write_canonical_json(path, payload)
    return path


def test_creation_approval_template_matches_required_shape() -> None:
    template = json.loads((REPO_ROOT / EXAMPLE_TEMPLATE_PATH).read_text(encoding="utf-8"))

    assert tuple(template) == (
        "authority_boundary_acknowledgement",
        "creation_disposition",
        "creation_scope_acknowledgement",
        "operator_identity",
        "terminal_output_controls",
    )
    assert set(template) == set(REQUIRED_GROUPS)
    for group_id in REQUIRED_GROUPS:
        assert set(template[group_id]) == set(REQUIRED_FIELDS[group_id])
    assert template["creation_disposition"]["decision_record_creation_now_allowed"] is False
    assert template["creation_disposition"]["decision_record_auto_creation_allowed"] is False
    assert template["terminal_output_controls"][
        "future_record_creation_allowed_by_this_payload"
    ] is False


def test_creation_approval_template_has_no_authority_expansion() -> None:
    template = json.loads((REPO_ROOT / EXAMPLE_TEMPLATE_PATH).read_text(encoding="utf-8"))

    assert not any(field in template for field in AUTHORITY_EXPANDING_FIELDS)
    assert "authority_locks" not in template
    assert template["authority_boundary_acknowledgement"]["no_execution_authority"] is True
    assert template["authority_boundary_acknowledgement"][
        "no_runtime_canon_queue_scheduler_mutation"
    ] is True


def test_creation_approval_preflight_template_mode() -> None:
    result = preflight_payload(
        EXAMPLE_TEMPLATE_PATH,
        repo_root=REPO_ROOT,
        template_mode=True,
    )

    assert result["valid"] is True
    assert result["mode"] == "template"
    assert result["payload_observed"] is True
    assert result["validation_blockers"] == []
    assert all(record["group_validated"] is True for record in result["group_records"])
    lines = render_preflight_lines(result)
    assert any("valid: True" in line for line in lines)
    assert any("authority_granted: False" in line for line in lines)
    assert any("valid_for_execution: False" in line for line in lines)


def test_creation_approval_default_payload_validates_when_present() -> None:
    result = preflight_payload(repo_root=REPO_ROOT)

    assert result["valid"] is True
    assert result["payload_observed"] is True
    assert result["validation_blockers"] == []
    assert all(record["group_validated"] is True for record in result["group_records"])


def test_creation_approval_missing_payload_fails_closed(tmp_path: Path) -> None:
    missing_payload_path = tmp_path / DEFAULT_CREATION_APPROVAL_PAYLOAD_PATH

    result = preflight_payload(missing_payload_path, repo_root=REPO_ROOT)

    assert result["valid"] is False
    assert result["payload_observed"] is False
    assert result["validation_blockers"] == ["payload_missing_or_unreadable"]


def test_creation_approval_preflight_accepts_complete_conservative_payload(
    tmp_path: Path,
) -> None:
    path = _write_payload(tmp_path, _complete_payload())

    result = preflight_payload(path, repo_root=REPO_ROOT)

    assert result["valid"] is True
    assert result["validation_blockers"] == []
    assert all(record["group_validated"] is True for record in result["group_records"])


def test_creation_approval_preflight_partial_payload_fails_closed(
    tmp_path: Path,
) -> None:
    path = _write_payload(
        tmp_path,
        {"operator_identity": {"operator_id": "operator-reviewer-001"}},
    )

    result = preflight_payload(path, repo_root=REPO_ROOT)

    assert result["valid"] is False
    assert "operator_identity.operator_approval_hash_missing" in result[
        "validation_blockers"
    ]
    assert "creation_scope_acknowledgement_missing" in result["validation_blockers"]


def test_creation_approval_preflight_rejects_malformed_operator_hash(
    tmp_path: Path,
) -> None:
    payload = _complete_payload()
    payload["operator_identity"]["operator_approval_hash"] = (
        "sha256:approval-source-observed"
    )
    path = _write_payload(tmp_path, payload)

    result = preflight_payload(path, repo_root=REPO_ROOT)

    assert result["valid"] is False
    assert "operator_identity.operator_approval_hash_must_be_sha256_digest" in result[
        "validation_blockers"
    ]


def test_creation_approval_preflight_blocks_authority_expansion(
    tmp_path: Path,
) -> None:
    payload = _complete_payload()
    payload["execution_authority"] = True
    payload["authority_locks"] = {"runtime_mutation": True}
    path = _write_payload(tmp_path, payload)

    result = preflight_payload(path, repo_root=REPO_ROOT)

    assert result["valid"] is False
    assert "payload_authority_expanding_field:execution_authority" in result[
        "authority_expansion_blockers"
    ]
    assert "payload_authority_lock_true:runtime_mutation" in result[
        "authority_expansion_blockers"
    ]


def test_creation_approval_preflight_real_mode_rejects_placeholders() -> None:
    result = preflight_payload(EXAMPLE_TEMPLATE_PATH, repo_root=REPO_ROOT)

    assert result["valid"] is False
    assert "operator_identity.operator_id_placeholder_not_allowed" in result[
        "validation_blockers"
    ]
    assert "creation_scope_acknowledgement.source_authorization_gate_hash_mismatch" in (
        result["validation_blockers"]
    )
    assert "payload.operator_identity.operator_approval_hash_placeholder_not_allowed" in (
        result["validation_blockers"]
    )


def test_creation_approval_template_readme_references_workflow() -> None:
    readme = (REPO_ROOT / README_PATH).read_text(encoding="utf-8")
    compact_readme = " ".join(readme.split())

    assert EXAMPLE_TEMPLATE_PATH in readme
    assert HANDOFF_PATH in readme
    assert DEFAULT_CREATION_APPROVAL_PAYLOAD_PATH.as_posix() in readme
    assert (
        "scripts/preflight/preflight_v2_hygiene_phase1_stabilization_decision_record_creation_approval_payload.py"
        in readme
    )
    for phrase in (
        "does not create the stabilization decision record",
        "authorize automatic record creation",
        "sha256:<64 hex>",
        "mutate runtime/canon/queue/scheduler state",
        "auto-continue",
        "execute",
    ):
        assert phrase in compact_readme


def test_creation_approval_handoff_references_operator_workflow() -> None:
    handoff = (REPO_ROOT / HANDOFF_PATH).read_text(encoding="utf-8")

    assert EXAMPLE_TEMPLATE_PATH in handoff
    assert DEFAULT_CREATION_APPROVAL_PAYLOAD_PATH.as_posix() in handoff
    assert (
        "scripts/preflight/preflight_v2_hygiene_phase1_stabilization_decision_record_creation_approval_payload.py"
        in handoff
    )
    assert SOURCE_AUTHORIZATION_GATE_PATH.as_posix() in handoff
    assert SOURCE_COMPRESSION_AUDIT_PATH.as_posix() in handoff
    for group_id in REQUIRED_GROUPS:
        assert f"`{group_id}`" in handoff


def test_creation_approval_handoff_preserves_authority_denials() -> None:
    handoff = (REPO_ROOT / HANDOFF_PATH).read_text(encoding="utf-8")

    assert "APPROVE_DECISION_RECORD_CREATION_FOR_SEPARATE_GOVERNED_MATERIALIZATION_LANE" in handoff
    assert (
        "NOT_COMPUTABLE_UNTIL_GOVERNED_DECISION_RECORD_CREATION_MATERIALIZATION"
        in handoff
    )
    assert "sha256:<64 hex>" in handoff
    for phrase in (
        "no decision-record auto-creation",
        "no immediate decision-record creation",
        "no execution",
        "no implementation",
        "no runtime mutation",
        "no canon mutation",
        "no queue mutation",
        "no scheduler mutation",
        "no Notion writeback",
        "no GitHub writeback",
        "no activation",
        "no promotion",
        "no registration",
        "no auto-continuation",
    ):
        assert phrase in handoff
    assert "Passing preflight grants no authority" in handoff
