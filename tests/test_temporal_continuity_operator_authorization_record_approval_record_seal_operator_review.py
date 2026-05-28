from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_operator_authorization_record_approval_record_seal_operator_review import (
    build_temporal_continuity_operator_authorization_record_approval_record_seal_operator_review,
    write_temporal_continuity_operator_authorization_record_approval_record_seal_operator_review,
)
from scripts import (  # noqa: F401
    run_temporal_continuity_operator_authorization_record_approval_record_seal_operator_review,
)

SOURCE = "out/temporal_continuity_operator_authorization_record_approval_record_seal_dry_run/latest.json"


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def _seed_p94(root: Path, status: str, dry_run_passed: bool = True) -> None:
    _write_json(
        root / SOURCE,
        {
            "approval_record_seal_dry_run_status": status,
            "approval_record_seal_dry_run_id": "temporal_continuity_operator_authorization_record_approval_record_seal_dry_run_001",
            "approval_record_seal_dry_run_hash": "df3438412e31e946b4c61785356ba926f8fcd4d9e24526f5b8551410cf4a168e",
            "dry_run_passed": dry_run_passed,
            "seal_construction_dry_run_results": [
                {"check_id": "approval_record_seal_plan_must_remain_advisory_only", "passed": True},
                {"check_id": "no_real_approval_record_creation_allowed", "passed": True},
                {"check_id": "no_real_approval_record_sealing_allowed", "passed": True},
            ],
            "seal_provenance_dry_run_results": [
                {"check_id": "source_approval_record_validation_dry_run_hash_must_be_present", "passed": True},
                {"check_id": "source_approval_record_validation_dry_run_path_must_match_expected_lane_output", "passed": True},
                {"check_id": "source_approval_record_validation_dry_run_status_must_be_evaluated", "passed": True},
                {"check_id": "source_approval_record_validation_dry_run_hash_present_in_seal_plan", "passed": True},
            ],
            "seal_hash_dry_run_results": [
                {"check_id": "approval_record_seal_plan_hash_must_be_canonical", "passed": True},
                {"check_id": "canonical_json_sha256_source_hash_required", "passed": True},
                {"check_id": "sorted_key_serialization_required", "passed": True},
            ],
            "seal_blocker_dry_run_results": [
                {"check_id": "missing_source_must_fail_closed", "passed": True},
                {"check_id": "non_ready_source_status_must_block", "passed": True},
                {"check_id": "validation_failed_source_must_block", "passed": True},
            ],
            "seal_authority_invariant_dry_run_results": [
                {"check_id": "source_advisory_only_true", "passed": True},
                {"check_id": "source_approval_granted_false", "passed": True},
                {"check_id": "source_approval_record_created_false", "passed": True},
                {"check_id": "source_approval_record_seal_plan_only_true", "passed": True},
                {"check_id": "source_approval_record_sealed_false", "passed": True},
                {"check_id": "source_authorization_authority_false", "passed": True},
                {"check_id": "source_authorization_granted_false", "passed": True},
                {"check_id": "source_authorization_record_creation_authority_false", "passed": True},
                {"check_id": "source_execution_authority_false", "passed": True},
                {"check_id": "source_projection_only_true", "passed": True},
                {"check_id": "source_token_minting_allowed_false", "passed": True},
                {"check_id": "source_valid_for_execution_false", "passed": True},
                {"check_id": "approval_granted_must_remain_false", "passed": True},
                {"check_id": "authorization_granted_must_remain_false", "passed": True},
                {"check_id": "execution_authority_must_remain_false", "passed": True},
                {"check_id": "token_minting_allowed_must_remain_false", "passed": True},
                {"check_id": "valid_for_execution_must_remain_false", "passed": True},
            ],
            "simulated_seal_dry_run": {
                "approval_record_seal_dry_run_id": "SIMULATED_SEAL_DRY_RUN_ONLY",
                "approval_record_seal_plan_id": "temporal_continuity_operator_authorization_record_approval_record_seal_plan_001",
                "simulated_seal_hash": "SIMULATED_HASH_ONLY",
                "simulated_seal_token": "SIMULATED_SEAL_TOKEN_ONLY",
                "simulated_seal_signature": "SIMULATED_SIGNATURE_ONLY",
                "simulated_seal_created_at": "SIMULATED_ONLY",
                "simulated_operator_id": "SIMULATED_OPERATOR",
                "simulated_operator_attestation": "SIMULATED_ATTESTED",
                "approval_granted": False,
                "authorization_granted": False,
                "execution_authority": False,
                "token_minting_allowed": False,
                "valid_for_execution": False,
                "approval_record_sealed": False,
                "approval_record_created": False,
                "simulated_only": True,
            },
            "dry_run_blockers": [],
            "blockers": [],
            "advisory_only": True,
            "projection_only": True,
            "approval_record_seal_dry_run_only": True,
            "simulated_only": True,
            "approval_record_sealed": False,
            "approval_record_created": False,
            "approval_granted": False,
            "authorization_granted": False,
            "execution_authority": False,
            "authorization_authority": False,
            "authorization_record_creation_authority": False,
            "mutation_allowed": False,
            "token_minting_allowed": False,
            "valid_for_execution": False,
            "operator_approval_required": True,
        },
    )


def test_missing_source_fails_closed(tmp_path: Path) -> None:
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_operator_review(
        repo_root=tmp_path
    )
    assert packet["approval_record_seal_operator_review_status"] == "NOT_COMPUTABLE"
    assert packet["review_passed"] is False
    h = packet["approval_record_seal_operator_review_hash"]
    assert isinstance(h, str) and len(h) == 64
    assert len(packet["blockers"]) > 0
    assert packet["recommended_next_lane"] == (
        "P94_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN"
    )
    assert packet["approval_granted"] is False
    assert packet["valid_for_execution"] is False
    assert packet["approval_record_sealed"] is False


def test_not_ready_source_blocks(tmp_path: Path) -> None:
    _seed_p94(tmp_path, "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_PLAN", True)
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_operator_review(
        repo_root=tmp_path
    )
    assert packet["approval_record_seal_operator_review_status"] == (
        "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN"
    )
    assert packet["review_passed"] is False
    assert packet["recommended_next_lane"] == (
        "P94_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN"
    )


def test_dry_run_false_blocks(tmp_path: Path) -> None:
    _seed_p94(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN_READY", False)
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_operator_review(
        repo_root=tmp_path
    )
    assert packet["approval_record_seal_operator_review_status"] == (
        "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN"
    )
    assert packet["review_passed"] is False
    assert any("dry_run_passed" in b for b in packet["review_blockers"])


def test_ready_source_produces_review_ready(tmp_path: Path) -> None:
    _seed_p94(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN_READY", True)
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_operator_review(
        repo_root=tmp_path
    )
    assert packet["approval_record_seal_operator_review_status"] == (
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_REVIEW_READY"
    )
    assert packet["review_passed"] is True
    assert packet["review_blockers"] == []
    assert packet["recommended_next_lane"] == (
        "P96_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION"
    )
    assert len(packet["seal_construction_review"]) > 0
    assert len(packet["seal_provenance_review"]) > 0
    assert len(packet["seal_hash_review"]) > 0
    assert len(packet["seal_blocker_review"]) > 0
    assert len(packet["seal_authority_invariant_review"]) > 0
    checklist = packet["operator_review_checklist"]
    assert len(checklist) > 0
    assert all(item.get("review_only") is True for item in checklist)
    assert packet["dry_run_check_summary"]["failed"] == 0
    assert len(packet["cross_lane_authority_posture"]) > 0
    assert all(e.get("posture_ok") is True for e in packet["cross_lane_authority_posture"])


def test_authority_locks_hardcoded_regardless_of_input(tmp_path: Path) -> None:
    _seed_p94(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN_READY", True)
    source_path = tmp_path / SOURCE
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    for field in (
        "approval_granted", "authorization_granted", "execution_authority",
        "authorization_authority", "authorization_record_creation_authority",
        "token_minting_allowed", "valid_for_execution", "approval_record_sealed",
        "approval_record_created",
    ):
        payload[field] = True
    sim = dict(payload["simulated_seal_dry_run"])
    for field in ("approval_granted", "authorization_granted", "execution_authority",
                  "token_minting_allowed", "valid_for_execution", "approval_record_sealed",
                  "approval_record_created"):
        sim[field] = True
    payload["simulated_seal_dry_run"] = sim
    _write_json(source_path, payload)
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_operator_review(
        repo_root=tmp_path
    )
    assert packet["approval_record_seal_operator_review_status"] == "APPROVAL_RECORD_SEAL_OPERATOR_REVIEW_FAILED"
    assert packet["review_passed"] is False
    assert packet["approval_granted"] is False
    assert packet["authorization_granted"] is False
    assert packet["execution_authority"] is False
    assert packet["token_minting_allowed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["approval_record_sealed"] is False
    assert packet["approval_record_created"] is False
    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["operator_review_only"] is True
    assert packet["approval_record_seal_operator_review_only"] is True
    assert packet["operator_approval_required"] is True
    failed_posture = [e for e in packet["cross_lane_authority_posture"] if not e.get("posture_ok")]
    assert len(failed_posture) > 0


def test_simulated_sentinel_checking(tmp_path: Path) -> None:
    _seed_p94(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN_READY", True)
    source_path = tmp_path / SOURCE
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    sim = dict(payload["simulated_seal_dry_run"])
    sim["simulated_seal_hash"] = "REAL_HASH_MATERIAL"
    payload["simulated_seal_dry_run"] = sim
    _write_json(source_path, payload)
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_operator_review(
        repo_root=tmp_path
    )
    assert packet["approval_record_seal_operator_review_status"] == "APPROVAL_RECORD_SEAL_OPERATOR_REVIEW_FAILED"
    assert packet["simulated_seal_review"]["sentinel_strings_contain_simulated_marker"] is False


def test_schema_and_hash_validation(tmp_path: Path) -> None:
    _seed_p94(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN_READY", True)
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_operator_review(
        repo_root=tmp_path
    )
    assert packet["schema_version"] == (
        "TemporalContinuityOperatorAuthorizationRecordApprovalRecordSealOperatorReview.v1"
    )
    assert packet["approval_record_seal_operator_review_id"] == (
        "temporal_continuity_operator_authorization_record_approval_record_seal_operator_review_001"
    )
    h = packet["approval_record_seal_operator_review_hash"]
    assert isinstance(h, str) and len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_determinism(tmp_path: Path) -> None:
    _seed_p94(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN_READY", True)
    p1 = build_temporal_continuity_operator_authorization_record_approval_record_seal_operator_review(repo_root=tmp_path)
    p2 = build_temporal_continuity_operator_authorization_record_approval_record_seal_operator_review(repo_root=tmp_path)
    assert json.dumps(p1, sort_keys=True) == json.dumps(p2, sort_keys=True)
    assert p1["approval_record_seal_operator_review_hash"] == p2["approval_record_seal_operator_review_hash"]


def test_write_function(tmp_path: Path) -> None:
    _seed_p94(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN_READY", True)
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_operator_review(
        repo_root=tmp_path
    )
    out = tmp_path / "out/temporal_continuity_operator_authorization_record_approval_record_seal_operator_review/latest.json"
    write_temporal_continuity_operator_authorization_record_approval_record_seal_operator_review(out, packet)
    assert out.exists()
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["approval_record_seal_operator_review_hash"] == packet["approval_record_seal_operator_review_hash"]
    assert loaded["approval_record_seal_operator_review_status"] == packet["approval_record_seal_operator_review_status"]


def test_all_checklist_items_are_review_only(tmp_path: Path) -> None:
    _seed_p94(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN_READY", True)
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_operator_review(
        repo_root=tmp_path
    )
    checklist = packet["operator_review_checklist"]
    assert len(checklist) == 8
    for item in checklist:
        assert item.get("review_only") is True
        assert "item_id" in item
        assert "description" in item


def test_dry_run_check_summary_counts(tmp_path: Path) -> None:
    _seed_p94(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN_READY", True)
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_operator_review(
        repo_root=tmp_path
    )
    s = packet["dry_run_check_summary"]
    assert s["total"] == s["passed"] + s["failed"]
    assert s["total"] > 0
    assert s["failed"] == 0


def test_doctrine_validator_nonregression() -> None:
    import subprocess
    result = subprocess.run(
        ["python", "scripts/run_doctrine_validator.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "seal" in result.stdout
