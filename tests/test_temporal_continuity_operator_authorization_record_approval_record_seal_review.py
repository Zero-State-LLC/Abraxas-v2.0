from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_operator_authorization_record_approval_record_seal_review import (
    build_temporal_continuity_operator_authorization_record_approval_record_seal_review,
    write_temporal_continuity_operator_authorization_record_approval_record_seal_review,
)
from scripts.temporal import (
    run_temporal_continuity_operator_authorization_record_approval_record_seal_review,
)

SOURCE = (
    "out/temporal_continuity_operator_authorization_record_approval_record_seal_dry_run"
    "/latest.json"
)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def _seed_p94(root: Path, status: str, validation_passed: bool = True) -> None:
    _write_json(
        root / SOURCE,
        {
            "approval_record_seal_dry_run_status": status,
            "validation_passed": validation_passed,
            "allowed_target_candidates": ["out/future_review.json"],
            "denied_target_candidates": ["canon://*"],
            "allowed_command_candidates": [
                "python scripts/temporal/run_temporal_continuity_operator_authorization_record_approval_record_seal_review.py"
            ],
            "denied_command_candidates": ["rm -rf /"],
            "planned_authorization_scope": ["operator_authorization_record_seal_review"],
            "planned_expected_outputs": [
                "out/temporal_continuity_operator_authorization_record_approval_record_seal_review/latest.json"
            ],
            "advisory_only": True,
            "projection_only": True,
            "approval_record_seal_dry_run_only": True,
            "approval_record_sealed": False,
            "approval_record_created": False,
            "approval_granted": False,
            "authorization_granted": False,
            "execution_authority": False,
            "authorization_authority": False,
            "authorization_record_creation_authority": False,
            "token_minting_allowed": False,
            "valid_for_execution": False,
        },
    )


def test_missing_source_fails_closed(tmp_path: Path) -> None:
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_review(
        repo_root=tmp_path
    )
    assert packet["approval_record_seal_review_status"] == "NOT_COMPUTABLE"


def test_ready_source_routes_to_operator_hold(tmp_path: Path) -> None:
    _seed_p94(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN_READY")
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_review(
        repo_root=tmp_path
    )
    assert (
        packet["approval_record_seal_review_status"]
        == "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_REVIEW_HELD_FOR_OPERATOR"
    )
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["operator_hold_required"] is True


def test_not_ready_source_blocks(tmp_path: Path) -> None:
    _seed_p94(tmp_path, "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_PLAN")
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_review(
        repo_root=tmp_path
    )
    assert (
        packet["approval_record_seal_review_status"]
        == "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN"
    )


def test_validation_false_blocks(tmp_path: Path) -> None:
    _seed_p94(
        tmp_path,
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN_READY",
        validation_passed=False,
    )
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_review(
        repo_root=tmp_path
    )
    assert (
        packet["approval_record_seal_review_status"]
        == "BLOCKED_BY_FAILED_APPROVAL_RECORD_SEAL_DRY_RUN"
    )


def test_failed_authority_check_fails_review(tmp_path: Path) -> None:
    _seed_p94(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN_READY")
    payload = json.loads((tmp_path / SOURCE).read_text(encoding="utf-8"))
    payload["authorization_granted"] = True
    _write_json(tmp_path / SOURCE, payload)
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_review(
        repo_root=tmp_path
    )
    assert (
        packet["approval_record_seal_review_status"]
        == "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_REVIEW_FAILED"
    )


def test_no_authority_introduced(tmp_path: Path) -> None:
    _seed_p94(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN_READY")
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_review(
        repo_root=tmp_path
    )
    for key in (
        "approval_record_sealed",
        "approval_record_created",
        "approval_granted",
        "authorization_granted",
        "execution_authority",
        "authorization_authority",
        "authorization_record_creation_authority",
        "token_minting_allowed",
        "valid_for_execution",
    ):
        assert packet[key] is False


def test_hash_stable(tmp_path: Path) -> None:
    _seed_p94(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN_READY")
    a = build_temporal_continuity_operator_authorization_record_approval_record_seal_review(
        repo_root=tmp_path
    )
    b = build_temporal_continuity_operator_authorization_record_approval_record_seal_review(
        repo_root=tmp_path
    )
    assert a["approval_record_seal_review_hash"] == b["approval_record_seal_review_hash"]


def test_runner_deterministic_write(tmp_path: Path) -> None:
    _seed_p94(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN_READY")
    out_path = (
        tmp_path
        / "out/temporal_continuity_operator_authorization_record_approval_record_seal_review"
        / "latest.json"
    )
    first = run_temporal_continuity_operator_authorization_record_approval_record_seal_review.run(
        repo_root=tmp_path,
        out_path=out_path,
    )
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_operator_authorization_record_approval_record_seal_review.run(
        repo_root=tmp_path,
        out_path=out_path,
    )
    second_text = out_path.read_text(encoding="utf-8")
    assert first["approval_record_seal_review_hash"] == second[
        "approval_record_seal_review_hash"
    ]
    assert first_text == second_text


def test_registry_includes_artifact() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/temporal_continuity_operator_authorization_record_approval_record_seal_review/latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )


def test_writer_final_newline(tmp_path: Path) -> None:
    _seed_p94(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN_READY")
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_review(
        repo_root=tmp_path
    )
    out_path = tmp_path / "x/latest.json"
    write_temporal_continuity_operator_authorization_record_approval_record_seal_review(
        out_path,
        packet,
    )
    assert out_path.read_text(encoding="utf-8").endswith("\n")
