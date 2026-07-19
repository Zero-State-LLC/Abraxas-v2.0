from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_stabilization_decision_record_emission_approval_intake_gate import (
    GATE_JSON_PATH,
    READY_STATUS,
    build_v2_hygiene_phase1_stabilization_decision_record_emission_approval_intake_gate,
    render_v2_hygiene_phase1_stabilization_decision_record_emission_approval_intake_gate_markdown,
    write_v2_hygiene_phase1_stabilization_decision_record_emission_approval_intake_gate,
)
from scripts.hygiene import (
    run_v2_hygiene_phase1_stabilization_decision_record_emission_approval_intake_gate,
)
from scripts.preflight_v2_hygiene_phase1_stabilization_decision_record_emission_approval_payload import (
    AUTHORITY_EXPANDING_FIELDS,
    DEFAULT_EMISSION_APPROVAL_PAYLOAD_PATH,
    REQUIRED_FIELDS,
    REQUIRED_GROUPS,
    SOURCE_EMISSION_AUTHORIZATION_GATE_PATH,
    SOURCE_EMISSION_PLAN_PATH,
    preflight_payload,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_emission_approval_intake_gate.v1.schema.json"
)
def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _source_hashes() -> tuple[str, str]:
    gate = _read_json(SOURCE_EMISSION_AUTHORIZATION_GATE_PATH)
    plan = _read_json(SOURCE_EMISSION_PLAN_PATH)
    return str(gate["gate_hash"]), str(plan["plan_hash"])


def _complete_payload() -> dict:
    gate_hash, plan_hash = _source_hashes()
    return {
        "operator_identity": {
            "operator_id": "operator-reviewer-001",
            "operator_reviewed_at_source_observed": "2026-06-16T00:00:00Z",
            "operator_approval_hash": (
                "sha256:"
                "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
            ),
        },
        "emission_scope_acknowledgement": {
            "source_emission_authorization_gate_path": (
                SOURCE_EMISSION_AUTHORIZATION_GATE_PATH.as_posix()
            ),
            "source_emission_authorization_gate_hash": gate_hash,
            "source_emission_plan_path": (
                SOURCE_EMISSION_PLAN_PATH.as_posix()
            ),
            "source_emission_plan_hash": plan_hash,
            "terminal_emission_hold_acknowledged": True,
        },
        "emission_disposition": {
            "approved_record_id": "v2_hygiene_phase1_stabilization_decision_record_001",
            "approved_record_output_path": (
                "out/operator_review/"
                "v2_hygiene_phase1_stabilization_decision_record_001.latest.json"
            ),
            "selected_emission_disposition": (
                "APPROVE_DECISION_RECORD_EMISSION_FOR_SEPARATE_GOVERNED_"
                "RECORD_FINALIZATION_LANE"
            ),
            "decision_record_emission_now_allowed": False,
            "decision_record_auto_emission_allowed": False,
            "separate_record_finalization_lane_required": True,
        },
        "authority_boundary_acknowledgement": {
            "no_decision_record_auto_emission": True,
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
                "NOT_COMPUTABLE_UNTIL_GOVERNED_DECISION_RECORD_"
                "EMISSION_FINALIZATION"
            ),
            "future_record_finalization_gate_required": True,
            "future_record_emission_allowed_by_this_payload": False,
            "rollback_or_supersession_policy": (
                "fresh governed operator decision required"
            ),
        },
    }


def _write_payload(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "operator_input/payload.json"
    write_canonical_json(path, payload)
    return path


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_emission_approval_payload_matches_required_shape() -> None:
    payload = _read_json(DEFAULT_EMISSION_APPROVAL_PAYLOAD_PATH)

    assert tuple(payload) == (
        "authority_boundary_acknowledgement",
        "emission_disposition",
        "emission_scope_acknowledgement",
        "operator_identity",
        "terminal_output_controls",
    )
    assert set(payload) == set(REQUIRED_GROUPS)
    for group_id in REQUIRED_GROUPS:
        assert set(payload[group_id]) == set(REQUIRED_FIELDS[group_id])
    assert payload["emission_disposition"][
        "decision_record_emission_now_allowed"
    ] is False
    assert payload["emission_disposition"][
        "decision_record_auto_emission_allowed"
    ] is False
    assert payload["terminal_output_controls"][
        "future_record_emission_allowed_by_this_payload"
    ] is False


def test_emission_approval_payload_has_no_authority_expansion() -> None:
    payload = _read_json(DEFAULT_EMISSION_APPROVAL_PAYLOAD_PATH)

    assert not any(field in payload for field in AUTHORITY_EXPANDING_FIELDS)
    assert "authority_locks" not in payload
    assert payload["authority_boundary_acknowledgement"][
        "no_execution_authority"
    ] is True


def test_emission_approval_default_payload_validates_when_present() -> None:
    result = preflight_payload(repo_root=REPO_ROOT)

    assert result["valid"] is True
    assert result["payload_observed"] is True
    assert result["validation_blockers"] == []
    assert all(record["group_validated"] is True for record in result["group_records"])


def test_emission_approval_missing_payload_fails_closed(tmp_path: Path) -> None:
    missing_payload_path = tmp_path / DEFAULT_EMISSION_APPROVAL_PAYLOAD_PATH

    result = preflight_payload(missing_payload_path, repo_root=REPO_ROOT)

    assert result["valid"] is False
    assert result["payload_observed"] is False
    assert result["validation_blockers"] == ["payload_missing_or_unreadable"]


def test_emission_approval_preflight_accepts_complete_conservative_payload(
    tmp_path: Path,
) -> None:
    path = _write_payload(tmp_path, _complete_payload())

    result = preflight_payload(path, repo_root=REPO_ROOT)

    assert result["valid"] is True
    assert result["validation_blockers"] == []
    assert all(record["group_validated"] is True for record in result["group_records"])


def test_emission_approval_preflight_partial_payload_fails_closed(
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
    assert "emission_scope_acknowledgement_missing" in result[
        "validation_blockers"
    ]


def test_emission_approval_preflight_blocks_authority_expansion(
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


def test_emission_approval_preflight_rejects_placeholders(tmp_path: Path) -> None:
    payload = _complete_payload()
    payload["operator_identity"]["operator_id"] = "REPLACE_WITH_OPERATOR_ID"
    path = _write_payload(tmp_path, payload)

    result = preflight_payload(path, repo_root=REPO_ROOT)

    assert result["valid"] is False
    assert "operator_identity.operator_id_placeholder_not_allowed" in result[
        "validation_blockers"
    ]


def test_emission_approval_intake_gate_ready_path_is_stable() -> None:
    first = build_v2_hygiene_phase1_stabilization_decision_record_emission_approval_intake_gate(
        REPO_ROOT
    )
    second = build_v2_hygiene_phase1_stabilization_decision_record_emission_approval_intake_gate(
        REPO_ROOT
    )

    assert first["gate_hash"] == second["gate_hash"]
    assert first["status"] == READY_STATUS
    assert first["source_readiness"] == "SOURCE_ARTIFACTS_READY"
    assert first["source_blockers"] == []
    assert first["operator_approval_observed"] is True
    assert (
        first["emission_approval_validated_for_future_record_emission_gate"]
        is True
    )
    assert first["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert first["safe_to_auto_continue"] is False
    assert first["valid_for_execution"] is False


def test_emission_approval_intake_gate_missing_payload_blocks(
    tmp_path: Path,
) -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_emission_approval_intake_gate(
        REPO_ROOT,
        emission_approval_payload_path=tmp_path / "missing_payload.json",
    )

    assert (
        packet["status"]
        == "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_EMISSION_APPROVAL_INTAKE_GATE_BLOCKED"
    )
    assert "emission_approval_payload_missing" in packet["source_blockers"]
    assert packet["decision_record_materialized"] is False


def test_emission_approval_intake_gate_authority_mutation_fails_closed(
    tmp_path: Path,
) -> None:
    gate = _read_json(SOURCE_EMISSION_AUTHORIZATION_GATE_PATH)
    gate["decision_record_emission_authorized"] = True
    gate["authority_locks"]["decision_record_creation"] = True
    path = _write_source(tmp_path, "authorizing_gate.json", gate)

    packet = build_v2_hygiene_phase1_stabilization_decision_record_emission_approval_intake_gate(
        REPO_ROOT,
        source_emission_authorization_gate_path=path,
    )

    assert (
        packet["status"]
        == "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_EMISSION_APPROVAL_INTAKE_GATE_BLOCKED"
    )
    assert (
        "emission_authorization_gate_authority_expanding_field:"
        "decision_record_emission_authorized"
    ) in packet["source_blockers"]
    assert (
        "emission_authorization_gate_authority_lock_true:"
        "decision_record_creation"
    ) in packet["source_blockers"]
    assert packet["decision_record_emission_authorized"] is False


def test_emission_approval_intake_gate_preserves_authority_denials() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_emission_approval_intake_gate(
        REPO_ROOT
    )

    assert packet["decision_record_created"] is False
    assert packet["decision_record_creation_authorized"] is False
    assert packet["decision_record_emitted"] is False
    assert packet["decision_record_materialized"] is False
    assert packet["decision_record_emission_authorized"] is False
    assert packet["authorization_record_created"] is False
    assert packet["evidence_bundle_created"] is False
    assert packet["operator_attestation_created"] is False
    assert packet["implementation_authorized"] is False
    assert packet["notion_writeback_allowed"] is False
    assert packet["github_writeback_allowed"] is False
    assert packet["runtime_mutation"] is False
    assert packet["canon_mutation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_emission_approval_intake_gate_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_emission_approval_intake_gate(
        REPO_ROOT
    )
    packet_without_hash = dict(packet)
    gate_hash = packet_without_hash.pop("gate_hash")
    assert gate_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_emission_approval_intake_gate_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_phase1_stabilization_decision_record_emission_approval_intake_gate(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / GATE_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase1_stabilization_decision_record_emission_approval_intake_gate.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["gate_hash"] == packet["gate_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_emission_approval_intake_gate_markdown() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_emission_approval_intake_gate(
        REPO_ROOT
    )
    markdown = render_v2_hygiene_phase1_stabilization_decision_record_emission_approval_intake_gate_markdown(
        packet
    )

    assert markdown[0] == (
        "# v2.0 Hygiene Phase 1 Stabilization Decision-Record Emission Approval Intake Gate"
    )
    assert any("operator_approval_observed: True" in line for line in markdown)
    assert any("decision_record_emitted: False" in line for line in markdown)
    assert any("decision_record_materialized: False" in line for line in markdown)
    assert any("valid_for_execution: False" in line for line in markdown)
    assert any("- none" in line for line in markdown)
