from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from core.canonical.json import canonical_dumps
from core.temporal_continuity_historical_recovery_audit import (
    BADGES_PATH,
    CONTINUITY_SPINE_PATH,
    EXPECTED_P103_TEMPORAL_ROUTE,
    NOTION_DIFF_PATH,
    P102F_SOURCE_PATH,
    TARGET_LANES,
    build_temporal_continuity_historical_recovery_audit,
    write_temporal_continuity_historical_recovery_audit,
)
from scripts import run_temporal_continuity_historical_recovery_audit

OUT_PATH = "out/temporal_continuity_historical_recovery_audit/latest.json"
SCHEMA_PATH = "contracts/canon/temporal_continuity_historical_recovery_audit.v1.schema.json"


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_dumps(payload) + "\n", encoding="utf-8")


def _seed_status(root: Path) -> None:
    _write_json(
        root / P102F_SOURCE_PATH,
        {
            "artifact_type": "TemporalContinuityOperatorAuthorizationRecordDecisionReconciliationReceipt.v1",
            "handoff": "OPERATOR_AUTHORIZATION_RECORD_DECISION_REQUIRED",
            "recommended_next_lane": "NOT_COMPUTABLE",
            "packet_hash": "a" * 64,
        },
    )
    _write_json(root / CONTINUITY_SPINE_PATH, {"highest_lane": "P102F"})
    _write_json(
        root / BADGES_PATH,
        {"signals": {"governance_status": "FROZEN", "canon_status": "ADVISORY_ONLY"}},
    )
    (root / NOTION_DIFF_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / NOTION_DIFF_PATH).write_text("repo notion diff\n", encoding="utf-8")


def _seed_research_p103_to_p107(root: Path) -> None:
    paths = (
        "core/research_shadow_replay_audit.py",
        "scripts/run_research_shadow_replay_audit.py",
        "contracts/canon/research_shadow_replay_audit.v1.schema.json",
        "tests/test_research_shadow_replay_audit.py",
        "out/research_shadow_replay_audit/latest.json",
        "core/research_boundary_decay_analysis.py",
        "scripts/run_research_boundary_decay_analysis.py",
        "contracts/canon/research_boundary_decay_analysis.v1.schema.json",
        "tests/test_research_boundary_decay_analysis.py",
        "out/research_boundary_decay_analysis/latest.json",
        "core/research_promotion_blocker_ledger.py",
        "scripts/run_research_promotion_blocker_ledger.py",
        "contracts/canon/research_promotion_blocker_ledger.v1.schema.json",
        "tests/test_research_promotion_blocker_ledger.py",
        "out/research_promotion_blocker_ledger/latest.json",
        "core/research_canary_eligibility_dossier.py",
        "scripts/run_research_canary_eligibility_dossier.py",
        "contracts/canon/research_canary_eligibility_dossier.v1.schema.json",
        "tests/test_research_canary_eligibility_dossier.py",
        "out/research_canary_eligibility_dossier/latest.json",
        "core/research_canary_review_packet.py",
        "scripts/run_research_canary_review_packet.py",
        "contracts/canon/research_canary_review_packet.v1.schema.json",
        "tests/test_research_canary_review_packet.py",
        "out/research_canary_review_packet/latest.json",
    )
    for rel_path in paths:
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("{}\n" if rel_path.endswith(".json") else "# seed\n", encoding="utf-8")


def test_missing_sources_fail_closed_not_computable(tmp_path: Path) -> None:
    packet = build_temporal_continuity_historical_recovery_audit(repo_root=tmp_path)
    assert packet["observed_current_highest_lane"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["valid_for_execution"] is False


def test_research_p103_to_p107_are_recovered_as_implemented_superseded_branch(tmp_path: Path) -> None:
    _seed_status(tmp_path)
    _seed_research_p103_to_p107(tmp_path)
    packet = build_temporal_continuity_historical_recovery_audit(repo_root=tmp_path)
    assert packet["target_lanes"] == list(TARGET_LANES)
    assert packet["p103_to_p107_existence_answer"]["implemented_repo_history"] is True
    assert packet["p103_to_p107_existence_answer"]["superseded_continuity_branches"] is True
    for finding in packet["recovered_lane_lineage"]:
        assert finding["classification"] == "IMPLEMENTED"
        assert finding["merge_classification"] == "MERGED"
        assert finding["continuity_relation"] == "SUPERSEDED_FOR_TEMPORAL_OPERATOR_DECISION_PATH"


def test_temporal_p103_route_absent_keeps_downstream_not_computable(tmp_path: Path) -> None:
    _seed_status(tmp_path)
    _seed_research_p103_to_p107(tmp_path)
    packet = build_temporal_continuity_historical_recovery_audit(repo_root=tmp_path)
    assert packet["temporal_operator_target_route_audit"]["target_route"] == EXPECTED_P103_TEMPORAL_ROUTE
    assert packet["temporal_operator_target_route_audit"]["classification"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_authority_locks_remain_false(tmp_path: Path) -> None:
    _seed_status(tmp_path)
    packet = build_temporal_continuity_historical_recovery_audit(repo_root=tmp_path)
    for field in (
        "production_activation",
        "canon_promotion",
        "forecast_influence",
        "scheduler_mutation",
        "runtime_authority",
        "execution_authority",
        "authorization_authority",
        "authorization_record_creation_authority",
        "record_creation_authority",
        "token_minting_authority",
        "token_minting_allowed",
        "authorization_granted",
        "authorization_record_created",
        "valid_for_execution",
    ):
        assert packet[field] is False
    assert set(packet["authority_locks"].values()) == {False}
    assert packet["canonical_status"] == "ADVISORY_ONLY"


def test_determinism_repeated_builds_match(tmp_path: Path) -> None:
    _seed_status(tmp_path)
    _seed_research_p103_to_p107(tmp_path)
    first = build_temporal_continuity_historical_recovery_audit(repo_root=tmp_path)
    second = build_temporal_continuity_historical_recovery_audit(repo_root=tmp_path)
    assert first == second
    assert first["packet_hash"] == second["packet_hash"]


def test_schema_accepts_generated_packet(tmp_path: Path) -> None:
    _seed_status(tmp_path)
    _seed_research_p103_to_p107(tmp_path)
    packet = build_temporal_continuity_historical_recovery_audit(repo_root=tmp_path)
    schema = json.loads(Path(SCHEMA_PATH).read_text(encoding="utf-8"))
    jsonschema.validate(packet, schema)


def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_status(tmp_path)
    packet = build_temporal_continuity_historical_recovery_audit(repo_root=tmp_path)
    out = tmp_path / "audit.json"
    write_temporal_continuity_historical_recovery_audit(out, packet)
    text = out.read_text(encoding="utf-8")
    parsed = json.loads(text)
    assert text.endswith("\n")
    assert text == canonical_dumps(parsed) + "\n"


def test_runner_writes_expected_output_path(tmp_path: Path) -> None:
    _seed_status(tmp_path)
    packet = run_temporal_continuity_historical_recovery_audit.run(repo_root=tmp_path)
    expected = tmp_path / OUT_PATH
    assert expected.exists()
    content = json.loads(expected.read_text(encoding="utf-8"))
    assert content["artifact_type"] == "TemporalContinuityHistoricalRecoveryAudit.v1"
    assert content["packet_hash"] == packet["packet_hash"]
