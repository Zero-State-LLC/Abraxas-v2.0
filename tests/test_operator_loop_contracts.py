"""Tests for WorkPacket.v1 / HandoffEnvelope.v1 and operator-loop projection."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from core.operator_loop import (
    AUTHORITY_LOCKS,
    PROJECTION_AUTHORITY,
    authority_decision_matrix,
    build_operator_loop_projection,
    build_truth_surfaces,
    collect_local_truth_surfaces,
    default_authority,
    detect_work_packet_file_overlaps,
    example_handoff,
    example_work_packet,
    handoff_schema,
    producer_grants_authority,
    validate_handoff,
    validate_work_packet,
    work_packet_schema,
)

WORK_PACKET_SCHEMA_PATH = Path(
    "contracts/engineering/work_packet.v1.schema.json"
)
HANDOFF_SCHEMA_PATH = Path(
    "contracts/engineering/handoff_envelope.v1.schema.json"
)


def test_work_packet_schema_file_exists() -> None:
    assert WORK_PACKET_SCHEMA_PATH.is_file()
    assert HANDOFF_SCHEMA_PATH.is_file()


def test_example_work_packet_validates() -> None:
    packet = example_work_packet()
    validate_work_packet(packet)
    Draft202012Validator(work_packet_schema()).validate(packet)


def test_example_handoff_validates() -> None:
    handoff = example_handoff()
    validate_handoff(handoff)
    Draft202012Validator(handoff_schema()).validate(handoff)


def test_work_packet_rejects_producer_authority_escalation() -> None:
    packet = example_work_packet()
    packet["authority"] = {
        **default_authority(),
        "producer_identity_grants_authority": True,
    }
    errors = list(Draft202012Validator(work_packet_schema()).iter_errors(packet))
    assert errors


def test_handoff_rejects_auto_merge_escalation() -> None:
    handoff = example_handoff()
    handoff["authority"] = {**default_authority(), "auto_merge": True}
    errors = list(Draft202012Validator(handoff_schema()).iter_errors(handoff))
    assert errors


def test_work_packet_rejects_unknown_conflict_policy() -> None:
    packet = example_work_packet()
    packet["conflict_policy"] = "AUTO_RESOLVE_BY_VOTE"
    errors = list(Draft202012Validator(work_packet_schema()).iter_errors(packet))
    assert errors


def test_handoff_rejects_hermes_as_completing_producer() -> None:
    """Handoffs complete producer work; Hermes routes but is not a handoff producer."""
    handoff = example_handoff()
    handoff["producer_system"] = "HERMES"
    errors = list(Draft202012Validator(handoff_schema()).iter_errors(handoff))
    assert errors


@pytest.mark.parametrize("producer", ["HERMES", "GROK", "CODEX", "MIXED", "HUMAN"])
def test_authority_decision_ignores_producer_identity(producer: str) -> None:
    denied = authority_decision_matrix(
        producer_system=producer,
        has_ci_pass=True,
        operator_approved=False,
    )
    assert denied["merge_allowed"] is False
    assert denied["deploy_allowed"] is False
    assert denied["producer_identity_used_for_grant"] is False

    allowed = authority_decision_matrix(
        producer_system=producer,
        has_ci_pass=True,
        operator_approved=True,
    )
    assert allowed["merge_allowed"] is True
    assert allowed["producer_identity_used_for_grant"] is False


def test_producer_grants_authority_helper_false_for_valid_packet() -> None:
    assert producer_grants_authority(example_work_packet()) is False
    assert AUTHORITY_LOCKS["producer_identity_grants_authority"] is False


def test_file_overlap_detected_for_concurrent_packets() -> None:
    a = example_work_packet(
        work_packet_id="WP-overlap-a",
        producer_system="GROK",
        files=["design-system/aal-viz/README.md", "core/operator_loop.py"],
        work_state="ACTIVE",
    )
    b = example_work_packet(
        work_packet_id="WP-overlap-b",
        producer_system="CODEX",
        files=["core/operator_loop.py", "tests/test_operator_loop_contracts.py"],
        work_state="ACTIVE",
    )
    findings = detect_work_packet_file_overlaps([a, b])
    assert len(findings) == 1
    assert findings[0]["conflict_class"] == "FILE_OVERLAP"
    assert findings[0]["auto_resolve_allowed"] is False
    assert set(findings[0]["subject_ids"]) == {"WP-overlap-a", "WP-overlap-b"}
    assert "core/operator_loop.py" in findings[0]["detail"]


def test_integrated_packets_do_not_overlap_active() -> None:
    active = example_work_packet(
        work_packet_id="WP-active",
        files=["core/operator_loop.py"],
        work_state="ACTIVE",
    )
    done = example_work_packet(
        work_packet_id="WP-done",
        files=["core/operator_loop.py"],
        work_state="INTEGRATED",
    )
    findings = detect_work_packet_file_overlaps([active, done])
    assert findings == []


def test_projection_is_read_only_and_deterministic() -> None:
    packets = [
        example_work_packet(work_packet_id="WP-proj-1", producer_system="GROK"),
        example_work_packet(
            work_packet_id="WP-proj-2",
            producer_system="CODEX",
            files=["core/operator_loop.py"],
        ),
    ]
    handoffs = [example_handoff(work_packet_id="WP-proj-1")]

    first = build_operator_loop_projection(
        work_packets=packets, handoffs=handoffs, source_paths=["fixtures"]
    )
    second = build_operator_loop_projection(
        work_packets=packets, handoffs=handoffs, source_paths=["fixtures"]
    )

    assert first == second
    assert first["schema_version"] == "OperatorLoopProjection.v1"
    assert first["authority"] == PROJECTION_AUTHORITY
    assert first["authority"]["projection_only"] is True
    assert first["authority"]["assignment_authority"] is False
    assert first["authority"]["approval_authority"] is False
    assert first["authority"]["producer_identity_grants_authority"] is False
    assert first["summary"]["work_packet_count"] == 2
    assert first["summary"]["handoff_count"] == 1
    assert first["summary"]["file_overlap_count"] == 0
    assert all(n["authority_implication"] == "none" for n in first["work_packets"])
    assert "projection_hash" in first
    assert len(first["projection_hash"]) == 64


def test_projection_surfaces_file_overlaps() -> None:
    packets = [
        example_work_packet(
            work_packet_id="WP-a",
            files=["shared/file.py"],
            work_state="ACTIVE",
        ),
        example_work_packet(
            work_packet_id="WP-b",
            producer_system="GROK",
            files=["shared/file.py"],
            work_state="REVIEW",
        ),
    ]
    projection = build_operator_loop_projection(work_packets=packets)
    assert projection["summary"]["file_overlap_count"] == 1
    assert projection["file_overlaps"][0]["conflict_class"] == "FILE_OVERLAP"


def test_projection_records_invalid_packets_without_raising() -> None:
    bad: dict[str, Any] = {"schema_version": "WorkPacket.v1", "work_packet_id": "WP-bad"}
    projection = build_operator_loop_projection(work_packets=[bad])
    assert projection["summary"]["work_packet_count"] == 0
    assert projection["summary"]["validation_error_count"] == 1
    assert projection["validation_errors"]["work_packets"][0]["work_packet_id"] == "WP-bad"


def test_authority_locks_are_immutable_consts() -> None:
    """Schemas pin authority fields; mutate-and-validate must fail every locked key."""
    packet = example_work_packet()
    for key, locked_value in AUTHORITY_LOCKS.items():
        mutated = copy.deepcopy(packet)
        if isinstance(locked_value, bool):
            mutated["authority"][key] = not locked_value
        errors = list(
            Draft202012Validator(work_packet_schema()).iter_errors(mutated)
        )
        assert errors, f"expected schema rejection for authority.{key}"


def test_truth_surfaces_are_projection_only() -> None:
    surfaces = build_truth_surfaces(
        github={
            "status": "PRESENT",
            "source": "fixture",
            "items": [{"kind": "pr", "number": 1044, "state": "MERGED"}],
        },
        notion={
            "status": "PRESENT",
            "source": "fixture",
            "items": [{"kind": "notion_pointer", "title": "Master System"}],
        },
        ci={
            "status": "PRESENT",
            "source": "fixture",
            "items": [{"kind": "check", "name": "fast-ci", "conclusion": "success"}],
        },
    )
    for key in ("github", "notion", "ci"):
        surface = surfaces[key]
        assert surface["authority_implication"] == "none"
        assert surface["can_assign"] is False
        assert surface["can_approve"] is False
        assert surface["can_merge"] is False
        assert surface["can_deploy"] is False
        assert surface["status"] == "PRESENT"
        assert len(surface["items"]) == 1

    projection = build_operator_loop_projection(
        work_packets=[example_work_packet()],
        truth_surfaces=surfaces,
    )
    assert projection["truth_surfaces"]["github"]["items"][0]["number"] == 1044
    assert projection["summary"]["github_item_count"] == 1
    assert projection["summary"]["notion_item_count"] == 1
    assert projection["summary"]["ci_item_count"] == 1
    assert projection["authority"]["assignment_authority"] is False


def test_collect_local_truth_surfaces_uses_explicit_git_tip() -> None:
    surfaces = collect_local_truth_surfaces(
        include_local_git=True,
        git_head="a" * 40,
        git_branch="main",
        evidence_dir=Path("/nonexistent/operator_loop_evidence"),
    )
    assert surfaces["github"]["status"] == "PRESENT"
    assert surfaces["github"]["items"][0]["sha"] == "a" * 40
    assert surfaces["github"]["items"][0]["authority_implication"] == "none"
    assert surfaces["notion"]["status"] == "PRESENT"
    assert surfaces["ci"]["status"] == "NOT_COMPUTABLE"
    assert surfaces["ci"]["can_merge"] is False
