from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_stabilization_operator_attestation_intake_gate import (
    AUTHORITY_EXPANDING_FIELDS,
    GATE_JSON_PATH,
    REQUIRED_FIELDS,
    REQUIRED_GROUPS,
    build_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate,
    render_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate_markdown,
    write_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate,
)
from scripts.hygiene import run_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate
from scripts.preflight_v2_hygiene_phase1_stabilization_operator_attestation_payload import (
    preflight_payload,
    render_preflight_lines,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase1_stabilization_operator_attestation_intake_gate.v1.schema.json"
)
SOURCE_DRY_RUN_PATH = (
    "out/operator_review/"
    "v2_hygiene_phase1_operator_review_stabilization_decision_record_dry_run_001.latest.json"
)
EXAMPLE_TEMPLATE_PATH = (
    "operator_input/templates/"
    "v2_hygiene_phase1_stabilization_operator_attestation_payload_001.example.json"
)
HANDOFF_PATH = (
    "operator_input/templates/"
    "v2_hygiene_phase1_stabilization_operator_handoff.md"
)
DEFAULT_PAYLOAD_PATH = (
    "operator_input/"
    "v2_hygiene_phase1_stabilization_operator_attestation_payload_001.json"
)


def _source_plan_hash() -> str:
    payload = json.loads((REPO_ROOT / SOURCE_DRY_RUN_PATH).read_text(encoding="utf-8"))
    return str(payload["source_plan_hash"])


def _complete_payload() -> dict:
    return {
        "operator_identity": {
            "operator_id": "operator-reviewer-001",
            "operator_reviewed_at_source_observed": "2026-06-15T00:00:00Z",
            "operator_attestation_hash": "attestation-source-observed",
        },
        "strategy_scope_acknowledgement": {
            "source_strategy_plan_path": (
                "out/operator_review/"
                "v2_hygiene_phase1_operator_review_stabilization_strategy_plan_001.latest.json"
            ),
            "source_strategy_plan_hash": _source_plan_hash(),
            "selected_strategy_id": "terminal_snapshot_strategy",
            "cycle_audit_scope_acknowledged": True,
        },
        "stabilization_disposition": {
            "approved_strategy_id": "terminal_snapshot_strategy",
            "terminal_snapshot_allowed": True,
            "bulk_scan_exclusion_allowed": True,
            "two_phase_manifest_allowed": False,
            "naive_regeneration_allowed": False,
        },
        "authority_boundary_acknowledgement": {
            "no_decision_record_auto_creation": True,
            "no_hygiene_implementation_authority": True,
            "no_execution_authority": True,
            "no_runtime_mutation": True,
            "no_notion_writeback": True,
        },
        "terminal_output_controls": {
            "downstream_lane_disposition": (
                "NOT_COMPUTABLE_UNTIL_GOVERNED_DECISION_RECORD_INTAKE"
            ),
            "future_dry_run_allowed": False,
            "future_record_creation_gate_required": True,
            "rollback_or_supersession_policy": (
                "fresh governed operator decision required"
            ),
        },
    }


def _write_payload(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "operator_input/payload.json"
    write_canonical_json(path, payload)
    return path


def test_v2_hygiene_phase1_stabilization_operator_attestation_template_matches_required_shape() -> None:
    template = json.loads((REPO_ROOT / EXAMPLE_TEMPLATE_PATH).read_text(encoding="utf-8"))

    assert tuple(template) == (
        "authority_boundary_acknowledgement",
        "operator_identity",
        "stabilization_disposition",
        "strategy_scope_acknowledgement",
        "terminal_output_controls",
    )
    assert set(template) == set(REQUIRED_GROUPS)
    for group_id in REQUIRED_GROUPS:
        assert set(template[group_id]) == set(REQUIRED_FIELDS[group_id])
    assert template["strategy_scope_acknowledgement"]["selected_strategy_id"] == (
        "terminal_snapshot_strategy"
    )
    assert template["stabilization_disposition"]["approved_strategy_id"] == (
        "terminal_snapshot_strategy"
    )
    assert template["terminal_output_controls"]["future_dry_run_allowed"] is False
    assert template["terminal_output_controls"]["downstream_lane_disposition"] == (
        "NOT_COMPUTABLE_UNTIL_GOVERNED_DECISION_RECORD_INTAKE"
    )


def test_v2_hygiene_phase1_stabilization_operator_attestation_template_has_no_authority_expansion() -> None:
    template = json.loads((REPO_ROOT / EXAMPLE_TEMPLATE_PATH).read_text(encoding="utf-8"))

    assert not any(field in template for field in AUTHORITY_EXPANDING_FIELDS)
    assert "authority_locks" not in template
    assert template["authority_boundary_acknowledgement"] == {
        "no_decision_record_auto_creation": True,
        "no_execution_authority": True,
        "no_hygiene_implementation_authority": True,
        "no_notion_writeback": True,
        "no_runtime_mutation": True,
    }


def test_v2_hygiene_phase1_stabilization_operator_attestation_default_payload_is_validated() -> None:
    assert (REPO_ROOT / EXAMPLE_TEMPLATE_PATH).exists()
    assert (REPO_ROOT / DEFAULT_PAYLOAD_PATH).exists()

    packet = build_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate(
        REPO_ROOT
    )

    assert (
        packet["status"]
        == "ATTESTATION_INTAKE_VALIDATED_FOR_FUTURE_DECISION_RECORD_GATE"
    )
    assert packet["payload_readiness"] == "OPERATOR_ATTESTATION_PAYLOAD_VALIDATED"
    assert packet["attestation_payload_observed"] is True
    assert packet["attested_group_count"] == 5
    assert packet["validation_blockers"] == []
    assert packet["intake_validated_for_future_decision_record_gate"] is True
    assert packet["valid_for_execution"] is False
    assert packet["attestation_payload_path"] == DEFAULT_PAYLOAD_PATH


def test_v2_hygiene_phase1_stabilization_operator_attestation_preflight_template_mode() -> None:
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
    markdown = render_preflight_lines(result)
    assert any("valid: True" in line for line in markdown)
    assert any("authority_granted: False" in line for line in markdown)


def test_v2_hygiene_phase1_stabilization_operator_attestation_preflight_default_ready() -> None:
    result = preflight_payload(repo_root=REPO_ROOT)

    assert result["valid"] is True
    assert result["mode"] == "real"
    assert result["payload_observed"] is True
    assert result["validation_blockers"] == []
    assert all(record["group_validated"] is True for record in result["group_records"])


def test_v2_hygiene_phase1_stabilization_operator_attestation_preflight_partial_payload(
    tmp_path: Path,
) -> None:
    path = _write_payload(
        tmp_path,
        {"operator_identity": {"operator_id": "operator-reviewer-001"}},
    )

    result = preflight_payload(path, repo_root=REPO_ROOT)

    assert result["valid"] is False
    assert "operator_identity.operator_attestation_hash_missing" in result[
        "validation_blockers"
    ]
    assert "strategy_scope_acknowledgement_missing" in result["validation_blockers"]


def test_v2_hygiene_phase1_stabilization_operator_attestation_preflight_blocks_authority_expansion(
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


def test_v2_hygiene_phase1_stabilization_operator_attestation_preflight_real_mode_rejects_placeholders() -> None:
    result = preflight_payload(EXAMPLE_TEMPLATE_PATH, repo_root=REPO_ROOT)

    assert result["valid"] is False
    assert "operator_identity.operator_id_placeholder_not_allowed" in result[
        "validation_blockers"
    ]
    assert "strategy_scope_acknowledgement.source_strategy_plan_hash_mismatch" in result[
        "validation_blockers"
    ]


def test_v2_hygiene_phase1_stabilization_operator_handoff_references_operator_workflow() -> None:
    handoff = (REPO_ROOT / HANDOFF_PATH).read_text(encoding="utf-8")

    assert EXAMPLE_TEMPLATE_PATH in handoff
    assert DEFAULT_PAYLOAD_PATH in handoff
    assert (
        "scripts/preflight_v2_hygiene_phase1_stabilization_operator_attestation_payload.py"
        in handoff
    )
    # Handoff is a sealed operator packet; accept pre- or post-mass-org path.
    assert (
        "run_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate.py"
        in handoff
    )
    for group_id in REQUIRED_GROUPS:
        assert f"`{group_id}`" in handoff


def test_v2_hygiene_phase1_stabilization_operator_handoff_preserves_authority_denials() -> None:
    handoff = (REPO_ROOT / HANDOFF_PATH).read_text(encoding="utf-8")

    assert "terminal_snapshot_strategy" in handoff
    assert "NOT_COMPUTABLE_UNTIL_GOVERNED_DECISION_RECORD_INTAKE" in handoff
    for phrase in (
        "no execution",
        "no implementation",
        "no runtime mutation",
        "no canon mutation",
        "no Notion writeback",
        "no GitHub writeback",
        "no decision-record auto-creation",
        "no activation",
        "no promotion",
        "no registration",
    ):
        assert phrase in handoff
    assert "grants no authority" in handoff


def test_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate_missing_payload(
    tmp_path: Path,
) -> None:
    missing_payload_path = tmp_path / "missing_operator_payload.json"
    first = build_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate(
        REPO_ROOT,
        attestation_payload_path=missing_payload_path,
    )
    second = build_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate(
        REPO_ROOT,
        attestation_payload_path=missing_payload_path,
    )

    assert first["gate_hash"] == second["gate_hash"]
    assert first["status"] == "NOT_COMPUTABLE"
    assert first["source_readiness"] == "SOURCE_ARTIFACTS_READY"
    assert first["payload_readiness"] == "OPERATOR_ATTESTATION_PAYLOAD_MISSING"
    assert first["attestation_payload_observed"] is False
    assert first["attested_group_count"] == 0
    assert set(first["missing_group_blockers"]) == {
        "operator_identity_missing",
        "strategy_scope_acknowledgement_missing",
        "stabilization_disposition_missing",
        "authority_boundary_acknowledgement_missing",
        "terminal_output_controls_missing",
    }
    assert "operator_attestation_payload_missing" in first["validation_blockers"]
    assert first["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert first["valid_for_execution"] is False


def test_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate_partial_payload(
    tmp_path: Path,
) -> None:
    payload = {"operator_identity": {"operator_id": "operator-reviewer-001"}}
    path = _write_payload(tmp_path, payload)

    packet = build_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate(
        REPO_ROOT,
        attestation_payload_path=path,
    )

    assert (
        packet["status"]
        == "V2_HYGIENE_PHASE1_STABILIZATION_OPERATOR_ATTESTATION_INTAKE_GATE_BLOCKED"
    )
    assert packet["payload_readiness"] == "OPERATOR_ATTESTATION_PAYLOAD_NOT_VALIDATED"
    assert (
        "operator_identity.operator_attestation_hash_missing"
        in packet["field_blockers"]
    )
    assert "strategy_scope_acknowledgement_missing" in packet["missing_group_blockers"]
    assert packet["intake_validated_for_future_decision_record_gate"] is False
    assert packet["valid_for_decision_record"] is False


def test_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate_blocks_authority_expansion(
    tmp_path: Path,
) -> None:
    payload = _complete_payload()
    payload["execution_authority"] = True
    payload["runtime_mutation"] = True
    payload["authority_locks"] = {"github_writeback": True}
    path = _write_payload(tmp_path, payload)

    packet = build_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate(
        REPO_ROOT,
        attestation_payload_path=path,
    )

    assert (
        packet["status"]
        == "V2_HYGIENE_PHASE1_STABILIZATION_OPERATOR_ATTESTATION_INTAKE_GATE_BLOCKED"
    )
    assert "payload_authority_expanding_field:execution_authority" in packet[
        "authority_expansion_blockers"
    ]
    assert "payload_authority_expanding_field:runtime_mutation" in packet[
        "authority_expansion_blockers"
    ]
    assert "payload_authority_lock_true:github_writeback" in packet[
        "authority_expansion_blockers"
    ]
    assert packet["execution_authority"] is False
    assert packet["safe_to_auto_continue"] is False


def test_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate_complete_payload_validates_only_for_future_gate(
    tmp_path: Path,
) -> None:
    path = _write_payload(tmp_path, _complete_payload())

    packet = build_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate(
        REPO_ROOT,
        attestation_payload_path=path,
    )

    assert (
        packet["status"]
        == "ATTESTATION_INTAKE_VALIDATED_FOR_FUTURE_DECISION_RECORD_GATE"
    )
    assert packet["payload_readiness"] == "OPERATOR_ATTESTATION_PAYLOAD_VALIDATED"
    assert packet["attested_group_count"] == 5
    assert packet["validation_blockers"] == []
    assert packet["intake_validated_for_future_decision_record_gate"] is True
    assert packet["future_decision_record_gate_required"] is True
    assert packet["decision_record_created"] is False
    assert packet["decision_record_creation_authorized"] is False
    assert packet["evidence_bundle_created"] is False
    assert packet["operator_attestation_created"] is False
    assert packet["implementation_authorized"] is False
    assert packet["valid_for_decision_record"] is False
    assert packet["valid_for_execution"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate(
        REPO_ROOT
    )
    packet_without_hash = dict(packet)
    gate_hash = packet_without_hash.pop("gate_hash")
    assert gate_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / GATE_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["gate_hash"] == packet["gate_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate_markdown() -> None:
    packet = build_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate(
        REPO_ROOT
    )
    markdown = render_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate_markdown(
        packet
    )

    assert (
        markdown[0]
        == "# v2.0 Hygiene Phase 1 Stabilization Operator Attestation Intake Gate"
    )
    assert any("operator_identity" in line for line in markdown)
    assert any(
        "payload_readiness: OPERATOR_ATTESTATION_PAYLOAD_VALIDATED" in line
        for line in markdown
    )
    assert any("- none" in line for line in markdown)
