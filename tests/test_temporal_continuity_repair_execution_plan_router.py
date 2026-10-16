from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import canonical_dumps
from core.generated_artifact_registry import build_generated_artifact_registry
from core.temporal_continuity_repair_execution_plan_router import (
    SOURCE_P102A_REPAIR_PLAN_PATH,
    _COMMAND_P99,
    _COMMAND_P100,
    _COMMAND_P101,
    _COMMAND_P102,
    _DENIED_AUTHORITY,
    build_temporal_continuity_repair_execution_plan_router,
    write_temporal_continuity_repair_execution_plan_router,
)
from scripts.temporal import run_temporal_continuity_repair_execution_plan_router

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = "out/temporal_continuity_repair_execution_plan_router/latest.json"


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )


def _supported_future_sequence() -> list[dict[str, str]]:
    return [
        {
            "sequence_id": "seq_001",
            "command": _COMMAND_P99,
            "target_artifact_path": "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_plan/latest.json",
            "purpose": "P99",
            "execution_allowed": False,
            "preconditions": [],
            "expected_status_after_run": "P83_SEQUENCE_RECORD_CREATION_RECORD_PLAN_READY",
        },
        {
            "sequence_id": "seq_002",
            "command": _COMMAND_P100,
            "target_artifact_path": "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_plan/latest.json",
            "purpose": "P100",
            "execution_allowed": False,
            "preconditions": [],
            "expected_status_after_run": "P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_PLAN_READY",
        },
        {
            "sequence_id": "seq_003",
            "command": _COMMAND_P101,
            "target_artifact_path": "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_authorization_gate/latest.json",
            "purpose": "P101",
            "execution_allowed": False,
            "preconditions": [],
            "expected_status_after_run": "P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_AUTHORIZATION_ELIGIBLE",
        },
        {
            "sequence_id": "seq_004",
            "command": _COMMAND_P102,
            "target_artifact_path": "out/temporal_continuity_recursive_authorization_chain_compression_audit/latest.json",
            "purpose": "P102",
            "execution_allowed": False,
            "preconditions": [],
            "expected_status_after_run": "COMPRESSION_AUDIT_READY",
        },
    ]


def _seed_p102a(
    root: Path,
    *,
    repair_status: str = "P101_READINESS_REPAIR_PLAN_READY",
    recommended_next_lane: str = "P102B_P101_GATE_REGENERATION_EXECUTION_PLAN",
    future_command_sequence: list[dict[str, object]] | None = None,
    degraded_evidence_inputs: list[str] | None = None,
    inherited_blockers: list[str] | None = None,
    inherited_drift_flags: list[str] | None = None,
    semantic_overlap_flags: list[str] | None = None,
) -> None:
    payload: dict[str, object] = {
        "artifact_type": "TemporalContinuityP101ReadinessRepairPlan.v1",
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "repair_plan_only": True,
        "readiness_repair_plan_only": True,
        "p101_readiness_repair_status": repair_status,
        "recommended_next_lane": recommended_next_lane,
        "future_command_sequence": (
            _supported_future_sequence()
            if future_command_sequence is None
            else future_command_sequence
        ),
        "degraded_evidence_inputs": degraded_evidence_inputs or [],
        "inherited_blockers": inherited_blockers or [],
        "inherited_drift_flags": inherited_drift_flags or [],
        "semantic_overlap_flags": semantic_overlap_flags or [],
        "packet_hash": "a" * 64,
    }
    _write_json(root / SOURCE_P102A_REPAIR_PLAN_PATH, payload)


# 1
def test_missing_p102a_source_returns_not_computable(tmp_path: Path) -> None:
    packet = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    assert packet["p102b_router_status"] == "NOT_COMPUTABLE"
    assert packet["selected_execution_plan_lane"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P102A_READINESS_REPAIR_PLAN_REGENERATION"


# 2
def test_malformed_p102a_source_returns_not_computable(tmp_path: Path) -> None:
    source = tmp_path / SOURCE_P102A_REPAIR_PLAN_PATH
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("{bad-json", encoding="utf-8")
    packet = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    assert packet["p102b_router_status"] == "NOT_COMPUTABLE"
    assert packet["selected_execution_plan_lane"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P102A_READINESS_REPAIR_PLAN_REGENERATION"


# 3
def test_p102a_not_computable_blocks_router(tmp_path: Path) -> None:
    _seed_p102a(tmp_path, repair_status="NOT_COMPUTABLE")
    packet = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    assert packet["p102b_router_status"] == "REPAIR_EXECUTION_PLAN_ROUTER_BLOCKED"
    assert packet["selected_execution_plan_lane"] == "NOT_COMPUTABLE"


# 4
def test_p102a_repair_not_required_routes_passthrough(tmp_path: Path) -> None:
    _seed_p102a(
        tmp_path,
        repair_status="P101_READINESS_REPAIR_NOT_REQUIRED",
        recommended_next_lane="P102_RECOMMENDED_NEXT_LANE_PASSTHROUGH",
    )
    packet = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    assert packet["p102b_router_status"] == "REPAIR_EXECUTION_PLAN_NOT_REQUIRED"
    assert packet["selected_execution_plan_lane"] == "NO_REPAIR_REQUIRED"
    assert packet["recommended_next_lane"] == "P102_RECOMMENDED_NEXT_LANE_PASSTHROUGH"


# 5
def test_p102a_repair_blocked_blocks_router(tmp_path: Path) -> None:
    _seed_p102a(
        tmp_path,
        repair_status="P101_READINESS_REPAIR_BLOCKED",
        recommended_next_lane="P101_GATE_ARTIFACT_REGENERATION_PLAN",
    )
    packet = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    assert packet["p102b_router_status"] == "REPAIR_EXECUTION_PLAN_ROUTER_BLOCKED"
    assert packet["selected_execution_plan_lane"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P101_GATE_ARTIFACT_REGENERATION_PLAN"


# 6
def test_p102a_p101_only_route_selects_p101_plus_p102(tmp_path: Path) -> None:
    _seed_p102a(
        tmp_path,
        recommended_next_lane="P102B_P101_GATE_REGENERATION_EXECUTION_PLAN",
    )
    packet = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    assert packet["p102b_router_status"] == "REPAIR_EXECUTION_PLAN_ROUTER_READY"
    assert (
        packet["selected_execution_plan_lane"]
        == "P102B_P101_GATE_REGENERATION_EXECUTION_PLAN"
    )
    commands = [item["command"] for item in packet["selected_command_sequence"]]
    assert commands == [_COMMAND_P101, _COMMAND_P102]


# 7
def test_p102a_full_chain_route_selects_p99_p100_p101_p102(tmp_path: Path) -> None:
    _seed_p102a(
        tmp_path,
        recommended_next_lane="P102B_P99_P100_P101_CHAIN_REGENERATION_EXECUTION_PLAN",
    )
    packet = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    commands = [item["command"] for item in packet["selected_command_sequence"]]
    assert commands == [_COMMAND_P99, _COMMAND_P100, _COMMAND_P101, _COMMAND_P102]


# 8
def test_p102a_rerun_only_route_selects_only_p102(tmp_path: Path) -> None:
    _seed_p102a(
        tmp_path,
        recommended_next_lane="P102B_COMPRESSION_AUDIT_RERUN_EXECUTION_PLAN",
    )
    packet = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    commands = [item["command"] for item in packet["selected_command_sequence"]]
    assert commands == [_COMMAND_P102]


# 9
def test_unsupported_recommended_next_lane_returns_not_computable(tmp_path: Path) -> None:
    _seed_p102a(
        tmp_path,
        recommended_next_lane="P102B_UNKNOWN_EXECUTION_PLAN",
    )
    packet = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    assert packet["p102b_router_status"] == "NOT_COMPUTABLE"
    assert packet["selected_execution_plan_lane"] == "NOT_COMPUTABLE"
    assert "P102A_RECOMMENDED_LANE_UNSUPPORTED" in packet["blocked_reasons"]


# 10
def test_unsupported_command_in_future_sequence_blocks_router(tmp_path: Path) -> None:
    _seed_p102a(
        tmp_path,
        future_command_sequence=[
            {
                "sequence_id": "seq_001",
                "command": "python scripts/run_bad.py --unsafe",
            }
        ],
    )
    packet = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    assert packet["p102b_router_status"] == "REPAIR_EXECUTION_PLAN_ROUTER_BLOCKED"
    assert "FUTURE_COMMAND_SEQUENCE_CONTAINS_UNSUPPORTED_COMMAND" in packet[
        "blocked_reasons"
    ]


# 11
def test_empty_future_sequence_blocks_when_repair_required(tmp_path: Path) -> None:
    _seed_p102a(tmp_path, future_command_sequence=[])
    packet = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    assert packet["p102b_router_status"] == "REPAIR_EXECUTION_PLAN_ROUTER_BLOCKED"
    assert "FUTURE_COMMAND_SEQUENCE_EMPTY" in packet["blocked_reasons"]


# 12
def test_command_allowlist_contains_only_exact_allowed_commands(tmp_path: Path) -> None:
    _seed_p102a(tmp_path)
    packet = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    commands = [item["command"] for item in packet["command_allowlist"]]
    assert commands == [_COMMAND_P99, _COMMAND_P100, _COMMAND_P101, _COMMAND_P102]


# 13
def test_all_selected_commands_have_execution_allowed_false(tmp_path: Path) -> None:
    _seed_p102a(tmp_path)
    packet = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    assert packet["selected_command_sequence"]
    for item in packet["selected_command_sequence"]:
        assert item["execution_allowed"] is False


# 14
def test_all_allowlist_entries_have_execution_allowed_false(tmp_path: Path) -> None:
    _seed_p102a(tmp_path)
    packet = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    for item in packet["command_allowlist"]:
        assert item["execution_allowed"] is False
        assert item["allowed_for_planning"] is True


# 15
def test_all_authority_fields_false(tmp_path: Path) -> None:
    _seed_p102a(tmp_path)
    packet = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    for field in _DENIED_AUTHORITY:
        assert packet[field] is False
    assert packet["authorization_granted"] is False
    assert packet["authorization_token_created"] is False
    assert packet["authorization_record_created"] is False


# 16
def test_validation_requirements_include_required_artifacts(tmp_path: Path) -> None:
    _seed_p102a(tmp_path)
    packet = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    paths = {item["artifact_path"] for item in packet["validation_requirements"]}
    assert SOURCE_P102A_REPAIR_PLAN_PATH in paths
    assert any("record_plan/latest.json" in path for path in paths)
    assert any("record_creation_plan/latest.json" in path for path in paths)
    assert any("authorization_gate/latest.json" in path for path in paths)
    assert (
        "out/temporal_continuity_recursive_authorization_chain_compression_audit/latest.json"
        in paths
    )


# 17
def test_inherited_degraded_evidence_preserved_exactly(tmp_path: Path) -> None:
    evidence = ["a", "b"]
    _seed_p102a(tmp_path, degraded_evidence_inputs=evidence)
    packet = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    assert packet["degraded_evidence_inputs"] == evidence


# 18
def test_inherited_blockers_preserved_exactly(tmp_path: Path) -> None:
    blockers = ["x", "y", "z"]
    _seed_p102a(tmp_path, inherited_blockers=blockers)
    packet = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    assert packet["inherited_blockers"] == blockers


# 19
def test_inherited_drift_flags_preserved_exactly(tmp_path: Path) -> None:
    flags = ["drift_a", "drift_b"]
    _seed_p102a(tmp_path, inherited_drift_flags=flags)
    packet = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    assert packet["inherited_drift_flags"] == flags


# 20
def test_semantic_overlap_flags_preserved_exactly(tmp_path: Path) -> None:
    flags = ["overlap_1", "overlap_2"]
    _seed_p102a(tmp_path, semantic_overlap_flags=flags)
    packet = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    assert packet["semantic_overlap_flags"] == flags


# 21
def test_selected_command_sequence_deterministic(tmp_path: Path) -> None:
    _seed_p102a(
        tmp_path,
        recommended_next_lane="P102B_P99_P100_P101_CHAIN_REGENERATION_EXECUTION_PLAN",
    )
    packet1 = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    packet2 = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    assert packet1["selected_command_sequence"] == packet2["selected_command_sequence"]


# 22
def test_command_allowlist_deterministic(tmp_path: Path) -> None:
    _seed_p102a(tmp_path)
    packet1 = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    packet2 = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    assert packet1["command_allowlist"] == packet2["command_allowlist"]


# 23
def test_blocked_reasons_deterministic(tmp_path: Path) -> None:
    _seed_p102a(
        tmp_path,
        future_command_sequence=[{"sequence_id": "x", "command": "python scripts/run_bad.py"}],
    )
    packet1 = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    packet2 = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    assert packet1["blocked_reasons"] == packet2["blocked_reasons"]


# 24
def test_packet_hash_deterministic(tmp_path: Path) -> None:
    _seed_p102a(tmp_path)
    packet1 = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    packet2 = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    assert packet1["packet_hash"] == packet2["packet_hash"]
    assert len(packet1["packet_hash"]) == 64


# 25
def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_p102a(tmp_path)
    packet = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    out = tmp_path / "router_output.json"
    write_temporal_continuity_repair_execution_plan_router(out, packet)
    text = out.read_text(encoding="utf-8")
    assert text.endswith("\n")
    parsed = json.loads(text)
    assert list(parsed.keys()) == sorted(parsed.keys())
    assert text == canonical_dumps(parsed) + "\n"


# 26
def test_runner_writes_output_path(tmp_path: Path) -> None:
    _seed_p102a(tmp_path)
    packet = run_temporal_continuity_repair_execution_plan_router.run(repo_root=tmp_path)
    expected = tmp_path / OUT_PATH
    assert expected.exists()
    content = json.loads(expected.read_text(encoding="utf-8"))
    assert content["artifact_type"] == "TemporalContinuityRepairExecutionPlanRouter.v1"
    assert content["packet_hash"] == packet["packet_hash"]


# 27
def test_artifact_registry_classifies_output_as_derived_optional() -> None:
    registry = build_generated_artifact_registry(repo_root=REPO_ROOT)
    artifact_path = "out/temporal_continuity_repair_execution_plan_router/latest.json"
    entry = next((a for a in registry.entries if a.artifact_path == artifact_path), None)
    source = registry.artifact_source_map[artifact_path]
    assert entry is not None
    assert entry.determinism_class == "DERIVED_OPTIONAL"
    assert source["ci_drift_enforced"] is False


# 28
# The P102 handoff moved out of the front-door docs: 09850527 dropped it from
# README.md and ce7ff536 moved the AGENTS.md copy to
# docs/status/HISTORICAL_GOVERNANCE_AGENT_NOTES.md (linked from AGENTS.md), since
# P70-P130 continuity material is not a routine startup requirement.
HISTORICAL_NOTES = "docs/status/HISTORICAL_GOVERNANCE_AGENT_NOTES.md"


def test_docs_include_p102b_handoff() -> None:
    agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    notes = (REPO_ROOT / HISTORICAL_NOTES).read_text(encoding="utf-8")
    plans = (REPO_ROOT / "PLANS.md").read_text(encoding="utf-8")
    assert HISTORICAL_NOTES in agents
    assert "run_temporal_continuity_repair_execution_plan_router.py" in notes
    assert "run_temporal_continuity_repair_execution_plan_router.py" in plans


# 29
def test_no_actual_repair_execution_is_performed(tmp_path: Path) -> None:
    _seed_p102a(
        tmp_path,
        recommended_next_lane="P102B_P99_P100_P101_CHAIN_REGENERATION_EXECUTION_PLAN",
    )
    packet = build_temporal_continuity_repair_execution_plan_router(repo_root=tmp_path)
    assert packet["selected_command_sequence"]
    assert not (tmp_path / "out/temporal_continuity_recursive_authorization_chain_compression_audit/latest.json").exists()
    assert not (tmp_path / "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_authorization_gate/latest.json").exists()
