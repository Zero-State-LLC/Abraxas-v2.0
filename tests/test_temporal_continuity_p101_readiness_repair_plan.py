from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import canonical_dumps
from core.generated_artifact_registry import build_generated_artifact_registry
from core.temporal_continuity_p101_readiness_repair_plan import (
    SOURCE_P100_PLAN_PATH,
    SOURCE_P101_GATE_PATH,
    SOURCE_P102_AUDIT_PATH,
    SOURCE_P99_PLAN_PATH,
    _DENIED_AUTHORITY,
    _FUTURE_COMMANDS,
    _P101_ELIGIBLE_NEXT_LANE,
    _P101_ELIGIBLE_STATUS,
    build_temporal_continuity_p101_readiness_repair_plan,
    write_temporal_continuity_p101_readiness_repair_plan,
)
from scripts import run_temporal_continuity_p101_readiness_repair_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = "out/temporal_continuity_p101_readiness_repair_plan/latest.json"

_P102_DEGRADED_STATUS = "COMPRESSION_AUDIT_DEGRADED"
_P102_P101_REGEN_LANE = (
    "P101_SEQUENCE_RECORD_CREATION_RECORD_CREATION_AUTHORIZATION_GATE_REGENERATION"
)
_P99_READY_STATUS = "P83_SEQUENCE_RECORD_CREATION_RECORD_PLAN_READY"
_P100_READY_STATUS = "P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_PLAN_READY"


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )


def _seed_p102(
    root: Path,
    *,
    status: str = _P102_DEGRADED_STATUS,
    recommended_next_lane: str = _P102_P101_REGEN_LANE,
    chain_recommendation: str = "NOT_COMPUTABLE",
    degraded_evidence_inputs: list[str] | None = None,
    inherited_blockers: list[str] | None = None,
    inherited_drift_flags: list[str] | None = None,
    semantic_overlap_flags: list[str] | None = None,
) -> None:
    payload: dict[str, object] = {
        "artifact_type": "TemporalContinuityRecursiveAuthorizationChainCompressionAudit.v1",
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "chain_compression_audit_status": status,
        "chain_recommendation": chain_recommendation,
        "recommended_next_lane": recommended_next_lane,
        "degraded_evidence_inputs": degraded_evidence_inputs or [],
        "inherited_blockers": inherited_blockers or [],
        "inherited_drift_flags": inherited_drift_flags or [],
        "semantic_overlap_flags": semantic_overlap_flags or [],
        "packet_hash": "a" * 64,
    }
    _write_json(
        root / SOURCE_P102_AUDIT_PATH,
        payload,
    )


def _seed_p101(
    root: Path,
    *,
    status: str = _P101_ELIGIBLE_STATUS,
    recommended_next_lane: str = _P101_ELIGIBLE_NEXT_LANE,
) -> None:
    payload: dict[str, object] = {
        "artifact_type": "TemporalContinuityP83RegenerationAuthorizationRecordCreationSequenceRecordCreationRecordCreationAuthorizationGate.v1",
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "p83_sequence_record_creation_record_creation_authorization_gate_status": status,
        "p83_sequence_record_creation_record_creation_authorization_eligible": status
        == _P101_ELIGIBLE_STATUS,
        "recommended_next_lane": recommended_next_lane,
        "packet_hash": "b" * 64,
    }
    _write_json(root / SOURCE_P101_GATE_PATH, payload)


def _seed_p100(
    root: Path,
    *,
    status: str = _P100_READY_STATUS,
    recommended_next_lane: str = "P101_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_SEQUENCE_RECORD_CREATION_RECORD_CREATION_AUTHORIZATION_GATE",
) -> None:
    payload: dict[str, object] = {
        "artifact_type": "TemporalContinuityP83RegenerationAuthorizationRecordCreationSequenceRecordCreationRecordCreationPlan.v1",
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "p83_sequence_record_creation_record_creation_plan_status": status,
        "recommended_next_lane": recommended_next_lane,
        "packet_hash": "c" * 64,
    }
    _write_json(root / SOURCE_P100_PLAN_PATH, payload)


def _seed_p99(
    root: Path,
    *,
    status: str = _P99_READY_STATUS,
    recommended_next_lane: str = "P100_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_SEQUENCE_RECORD_CREATION_RECORD_CREATION_PLAN",
) -> None:
    payload: dict[str, object] = {
        "artifact_type": "TemporalContinuityP83RegenerationAuthorizationRecordCreationSequenceRecordCreationRecordPlan.v1",
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "p83_sequence_record_creation_record_plan_status": status,
        "recommended_next_lane": recommended_next_lane,
        "packet_hash": "d" * 64,
    }
    _write_json(root / SOURCE_P99_PLAN_PATH, payload)


# ---------------------------------------------------------------------------
# Test 1: Missing P102 source returns NOT_COMPUTABLE
# ---------------------------------------------------------------------------


def test_missing_p102_source_returns_not_computable(tmp_path: Path) -> None:
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    assert packet["p101_readiness_repair_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P102_COMPRESSION_AUDIT_REGENERATION"


# ---------------------------------------------------------------------------
# Test 2: Malformed P102 source returns NOT_COMPUTABLE
# ---------------------------------------------------------------------------


def test_malformed_p102_source_returns_not_computable(tmp_path: Path) -> None:
    p = tmp_path / SOURCE_P102_AUDIT_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("NOT VALID JSON {{{", encoding="utf-8")
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    assert packet["p101_readiness_repair_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P102_COMPRESSION_AUDIT_REGENERATION"


# ---------------------------------------------------------------------------
# Test 3: P102 not degraded / not P101 route returns repair not required
# ---------------------------------------------------------------------------


def test_p102_not_degraded_returns_repair_not_required(tmp_path: Path) -> None:
    _seed_p102(
        tmp_path,
        status="COMPRESSION_AUDIT_READY",
        recommended_next_lane="P103_TEMPORAL_CONTINUITY_GENERIC_AUTHORIZATION_LANE_TEMPLATE_PLAN",
    )
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    assert packet["p101_readiness_repair_status"] == "P101_READINESS_REPAIR_NOT_REQUIRED"
    assert packet["recommended_next_lane"] == "P102_RECOMMENDED_NEXT_LANE_PASSTHROUGH"


def test_p102_degraded_but_not_p101_route_returns_repair_not_required(
    tmp_path: Path,
) -> None:
    _seed_p102(
        tmp_path,
        status=_P102_DEGRADED_STATUS,
        recommended_next_lane="P86_TO_P101_CHAIN_EVIDENCE_RESTORATION_PLAN",
    )
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    assert packet["p101_readiness_repair_status"] == "P101_READINESS_REPAIR_NOT_REQUIRED"


# ---------------------------------------------------------------------------
# Test 4: P102 degraded + missing P101 returns blocked
# ---------------------------------------------------------------------------


def test_p102_degraded_missing_p101_returns_blocked(tmp_path: Path) -> None:
    _seed_p102(tmp_path)
    # P101 not written
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    assert packet["p101_readiness_repair_status"] == "P101_READINESS_REPAIR_BLOCKED"
    assert packet["recommended_next_lane"] == "P101_GATE_ARTIFACT_REGENERATION_PLAN"


# ---------------------------------------------------------------------------
# Test 5: P102 degraded + malformed P101 returns blocked
# ---------------------------------------------------------------------------


def test_p102_degraded_malformed_p101_returns_blocked(tmp_path: Path) -> None:
    _seed_p102(tmp_path)
    p = tmp_path / SOURCE_P101_GATE_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("{bad json", encoding="utf-8")
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    assert packet["p101_readiness_repair_status"] == "P101_READINESS_REPAIR_BLOCKED"
    assert packet["recommended_next_lane"] == "P101_GATE_ARTIFACT_REGENERATION_PLAN"


# ---------------------------------------------------------------------------
# Test 6: P102 degraded + P101 not eligible returns repair plan ready
# ---------------------------------------------------------------------------


def test_p102_degraded_p101_not_eligible_returns_repair_plan_ready(
    tmp_path: Path,
) -> None:
    _seed_p102(tmp_path)
    _seed_p101(
        tmp_path,
        status="P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_AUTHORIZATION_DENIED",
        recommended_next_lane="P100_SEQUENCE_RECORD_CREATION_RECORD_CREATION_PLAN_REGENERATION",
    )
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    assert packet["p101_readiness_repair_status"] == "P101_READINESS_REPAIR_PLAN_READY"
    assert packet["recommended_next_lane"] == "P102B_P101_GATE_REGENERATION_EXECUTION_PLAN"
    assert len(packet["repair_plan_items"]) > 0


# ---------------------------------------------------------------------------
# Test 7: P102 degraded + P101 eligible but weak P99/P100 chain
# ---------------------------------------------------------------------------


def test_p102_degraded_p101_eligible_weak_p99_returns_repair_plan_ready(
    tmp_path: Path,
) -> None:
    _seed_p102(tmp_path)
    _seed_p101(tmp_path)
    # P99 missing, P100 missing → chain weak
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    assert packet["p101_readiness_repair_status"] == "P101_READINESS_REPAIR_PLAN_READY"
    assert (
        packet["recommended_next_lane"]
        == "P102B_P99_P100_P101_CHAIN_REGENERATION_EXECUTION_PLAN"
    )


def test_p102_degraded_p101_eligible_p100_not_ready_returns_repair_plan_ready(
    tmp_path: Path,
) -> None:
    _seed_p102(tmp_path)
    _seed_p101(tmp_path)
    _seed_p99(tmp_path)
    _seed_p100(
        tmp_path,
        status="P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_PLAN_DENIED",
    )
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    assert packet["p101_readiness_repair_status"] == "P101_READINESS_REPAIR_PLAN_READY"
    assert (
        packet["recommended_next_lane"]
        == "P102B_P99_P100_P101_CHAIN_REGENERATION_EXECUTION_PLAN"
    )


# ---------------------------------------------------------------------------
# Test 8: P102 degraded + P99/P100/P101 coherent returns rerun-P102 route
# ---------------------------------------------------------------------------


def test_p102_degraded_coherent_chain_returns_rerun_p102_route(tmp_path: Path) -> None:
    _seed_p102(tmp_path)
    _seed_p101(tmp_path)
    _seed_p100(tmp_path)
    _seed_p99(tmp_path)
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    assert packet["p101_readiness_repair_status"] == "P101_READINESS_REPAIR_PLAN_READY"
    assert (
        packet["recommended_next_lane"] == "P102B_COMPRESSION_AUDIT_RERUN_EXECUTION_PLAN"
    )


# ---------------------------------------------------------------------------
# Test 9: future_command_sequence contains only allowed planned commands
# ---------------------------------------------------------------------------


def test_future_command_sequence_contains_only_allowed_commands(
    tmp_path: Path,
) -> None:
    _seed_p102(tmp_path)
    _seed_p101(tmp_path)
    _seed_p100(tmp_path)
    _seed_p99(tmp_path)
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    allowed_commands = {cmd["command"] for cmd in _FUTURE_COMMANDS}
    for item in packet["future_command_sequence"]:
        assert item["command"] in allowed_commands, (
            f"Unexpected command: {item['command']}"
        )


def test_future_command_sequence_always_four_items(tmp_path: Path) -> None:
    """future_command_sequence always has all 4 planned commands regardless of status."""
    _seed_p102(tmp_path)
    _seed_p101(tmp_path)
    _seed_p100(tmp_path)
    _seed_p99(tmp_path)
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    assert len(packet["future_command_sequence"]) == 4


# ---------------------------------------------------------------------------
# Test 10: every future command has execution_allowed=false
# ---------------------------------------------------------------------------


def test_every_future_command_execution_allowed_false(tmp_path: Path) -> None:
    _seed_p102(tmp_path)
    _seed_p101(tmp_path)
    _seed_p100(tmp_path)
    _seed_p99(tmp_path)
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    for item in packet["future_command_sequence"]:
        assert item["execution_allowed"] is False


def test_every_future_command_execution_allowed_false_on_not_computable(
    tmp_path: Path,
) -> None:
    # No P102 source → NOT_COMPUTABLE
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    for item in packet["future_command_sequence"]:
        assert item["execution_allowed"] is False


# ---------------------------------------------------------------------------
# Test 11: every repair item has execution_allowed=false
# ---------------------------------------------------------------------------


def test_every_repair_item_execution_allowed_false(tmp_path: Path) -> None:
    _seed_p102(tmp_path)
    _seed_p101(
        tmp_path,
        status="P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_AUTHORIZATION_DENIED",
        recommended_next_lane="P100_SEQUENCE_RECORD_CREATION_RECORD_CREATION_PLAN_REGENERATION",
    )
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    assert len(packet["repair_plan_items"]) > 0
    for item in packet["repair_plan_items"]:
        assert item["execution_allowed"] is False


# ---------------------------------------------------------------------------
# Test 12: p101_readiness_repair_allowed=false
# ---------------------------------------------------------------------------


def test_p101_readiness_repair_allowed_always_false(tmp_path: Path) -> None:
    for seeder in [
        lambda: None,
        lambda: _seed_p102(tmp_path),
        lambda: (_seed_p102(tmp_path), _seed_p101(tmp_path), _seed_p100(tmp_path), _seed_p99(tmp_path)),
    ]:
        seeder()
        packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
        assert packet["p101_readiness_repair_allowed"] is False


# ---------------------------------------------------------------------------
# Test 13: all authority fields false
# ---------------------------------------------------------------------------


def test_all_authority_fields_false(tmp_path: Path) -> None:
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    for field in _DENIED_AUTHORITY:
        assert packet[field] is False, f"Expected {field}=False, got {packet[field]}"
    # Also check explicit governance locks
    assert packet["production_activation"] is False
    assert packet["canon_promotion"] is False
    assert packet["forecast_influence"] is False
    assert packet["scheduler_mutation"] is False
    assert packet["repair_authority"] is False
    assert packet["repair_execution_authority"] is False
    assert packet["regeneration_authority"] is False
    assert packet["regeneration_execution_authority"] is False
    assert packet["authorization_granted"] is False
    assert packet["authorization_token_created"] is False
    assert packet["authorization_record_created"] is False
    assert packet["spine_implementation_authority"] is False


# ---------------------------------------------------------------------------
# Test 14: validation requirements include required checks
# ---------------------------------------------------------------------------


def test_validation_requirements_include_required_checks(tmp_path: Path) -> None:
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    req_ids = {r["requirement_id"] for r in packet["validation_requirements"]}
    assert "validation_001_p99_exists_readable" in req_ids
    assert "validation_002_p99_status_ready" in req_ids
    assert "validation_003_p100_exists_readable" in req_ids
    assert "validation_004_p100_status_ready" in req_ids
    assert "validation_005_p101_exists_readable" in req_ids
    assert "validation_006_p101_status_eligible" in req_ids
    assert "validation_007_p101_lane_recommends_p102" in req_ids
    assert "validation_008_all_authority_fields_false" in req_ids
    assert "validation_009_p102_rerun_exists_readable" in req_ids
    assert "validation_010_p102_no_longer_routes_to_p101_regen" in req_ids


# ---------------------------------------------------------------------------
# Test 15: rerun_p102_requirements include required artifacts
# ---------------------------------------------------------------------------


def test_rerun_p102_requirements_include_required_artifacts(tmp_path: Path) -> None:
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    req_ids = {r["requirement_id"] for r in packet["rerun_p102_requirements"]}
    assert "rerun_p102_req_001" in req_ids
    assert "rerun_p102_req_002" in req_ids
    assert "rerun_p102_req_003" in req_ids
    paths = {r["required_artifact_path"] for r in packet["rerun_p102_requirements"]}
    assert SOURCE_P99_PLAN_PATH in paths
    assert SOURCE_P100_PLAN_PATH in paths
    assert SOURCE_P101_GATE_PATH in paths


# ---------------------------------------------------------------------------
# Test 16: findings deterministic
# ---------------------------------------------------------------------------


def test_findings_deterministic(tmp_path: Path) -> None:
    _seed_p102(tmp_path)
    _seed_p101(tmp_path)
    packet1 = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    packet2 = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    assert packet1["p101_readiness_findings"] == packet2["p101_readiness_findings"]
    # Findings are sorted by finding_id
    ids = [f["finding_id"] for f in packet1["p101_readiness_findings"]]
    assert ids == sorted(ids)


# ---------------------------------------------------------------------------
# Test 17: repair_plan_items deterministic
# ---------------------------------------------------------------------------


def test_repair_plan_items_deterministic(tmp_path: Path) -> None:
    _seed_p102(tmp_path)
    _seed_p101(
        tmp_path,
        status="P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_AUTHORIZATION_DENIED",
        recommended_next_lane="P100_SEQUENCE_RECORD_CREATION_RECORD_CREATION_PLAN_REGENERATION",
    )
    packet1 = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    packet2 = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    assert packet1["repair_plan_items"] == packet2["repair_plan_items"]
    ids = [r["repair_item_id"] for r in packet1["repair_plan_items"]]
    assert ids == sorted(ids)


# ---------------------------------------------------------------------------
# Test 18: future_command_sequence deterministic
# ---------------------------------------------------------------------------


def test_future_command_sequence_deterministic(tmp_path: Path) -> None:
    _seed_p102(tmp_path)
    _seed_p101(tmp_path)
    _seed_p100(tmp_path)
    _seed_p99(tmp_path)
    packet1 = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    packet2 = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    assert packet1["future_command_sequence"] == packet2["future_command_sequence"]
    ids = [c["sequence_id"] for c in packet1["future_command_sequence"]]
    assert ids == sorted(ids)


# ---------------------------------------------------------------------------
# Test 19: inherited degraded evidence preserved exactly
# ---------------------------------------------------------------------------


def test_inherited_degraded_evidence_preserved_exactly(tmp_path: Path) -> None:
    evidence = ["evidence_item_alpha", "evidence_item_beta"]
    _seed_p102(tmp_path, degraded_evidence_inputs=evidence)
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    assert packet["degraded_evidence_inputs"] == evidence


def test_inherited_degraded_evidence_empty_when_not_present(tmp_path: Path) -> None:
    _seed_p102(tmp_path, degraded_evidence_inputs=[])
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    assert packet["degraded_evidence_inputs"] == []


# ---------------------------------------------------------------------------
# Test 20: inherited blockers preserved exactly
# ---------------------------------------------------------------------------


def test_inherited_blockers_preserved_exactly(tmp_path: Path) -> None:
    blockers = ["blocker_one", "blocker_two", "blocker_three"]
    _seed_p102(tmp_path, inherited_blockers=blockers)
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    assert packet["inherited_blockers"] == blockers


# ---------------------------------------------------------------------------
# Test 21: inherited drift flags preserved exactly
# ---------------------------------------------------------------------------


def test_inherited_drift_flags_preserved_exactly(tmp_path: Path) -> None:
    flags = ["drift_flag_x", "drift_flag_y"]
    _seed_p102(tmp_path, inherited_drift_flags=flags)
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    assert packet["inherited_drift_flags"] == flags


# ---------------------------------------------------------------------------
# Test 22: semantic overlap flags preserved exactly
# ---------------------------------------------------------------------------


def test_semantic_overlap_flags_preserved_exactly(tmp_path: Path) -> None:
    flags = ["overlap_a", "overlap_b", "overlap_c"]
    _seed_p102(tmp_path, semantic_overlap_flags=flags)
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    assert packet["semantic_overlap_flags"] == flags


# ---------------------------------------------------------------------------
# Test 23: packet hash deterministic
# ---------------------------------------------------------------------------


def test_packet_hash_deterministic(tmp_path: Path) -> None:
    _seed_p102(tmp_path)
    _seed_p101(tmp_path)
    _seed_p100(tmp_path)
    _seed_p99(tmp_path)
    packet1 = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    packet2 = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    assert packet1["packet_hash"] == packet2["packet_hash"]
    assert isinstance(packet1["packet_hash"], str)
    assert len(str(packet1["packet_hash"])) == 64


def test_packet_hash_changes_with_different_p102_status(tmp_path: Path) -> None:
    _seed_p102(tmp_path, status=_P102_DEGRADED_STATUS)
    packet1 = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)

    # Change P102 status
    _seed_p102(
        tmp_path,
        status="COMPRESSION_AUDIT_READY",
        recommended_next_lane="P103_TEMPORAL_CONTINUITY_GENERIC_AUTHORIZATION_LANE_TEMPLATE_PLAN",
    )
    packet2 = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    assert packet1["packet_hash"] != packet2["packet_hash"]


# ---------------------------------------------------------------------------
# Test 24: writer emits canonical JSON with final newline
# ---------------------------------------------------------------------------


def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_p102(tmp_path)
    _seed_p101(tmp_path)
    _seed_p100(tmp_path)
    _seed_p99(tmp_path)
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    out = tmp_path / "test_output.json"
    write_temporal_continuity_p101_readiness_repair_plan(out, packet)
    text = out.read_text(encoding="utf-8")
    assert text.endswith("\n"), "Output must end with a newline"
    parsed = json.loads(text)
    # Keys must be sorted
    keys = list(parsed.keys())
    assert keys == sorted(keys), "Keys must be sorted (canonical JSON)"
    # Re-serialized must match canonical form
    assert text == canonical_dumps(parsed) + "\n"


# ---------------------------------------------------------------------------
# Test 25: runner writes out/temporal_continuity_p101_readiness_repair_plan/latest.json
# ---------------------------------------------------------------------------


def test_runner_writes_correct_output_path(tmp_path: Path) -> None:
    _seed_p102(tmp_path)
    packet = run_temporal_continuity_p101_readiness_repair_plan.run(repo_root=tmp_path)
    expected = tmp_path / OUT_PATH
    assert expected.exists(), f"Expected output at {expected}"
    content = json.loads(expected.read_text(encoding="utf-8"))
    assert content["artifact_type"] == "TemporalContinuityP101ReadinessRepairPlan.v1"
    assert content["packet_hash"] == packet["packet_hash"]


# ---------------------------------------------------------------------------
# Test 26: artifact registry classifies output as DERIVED_OPTIONAL
#           and not CI drift enforced
# ---------------------------------------------------------------------------


def test_artifact_registry_classifies_output_as_derived_optional() -> None:
    registry = build_generated_artifact_registry(repo_root=REPO_ROOT)
    artifact_path = "out/temporal_continuity_p101_readiness_repair_plan/latest.json"
    entry = next(
        (a for a in registry.entries if a.artifact_path == artifact_path),
        None,
    )
    source = registry.artifact_source_map[artifact_path]
    assert entry is not None, f"{artifact_path} not found in artifact registry"
    assert entry.determinism_class == "DERIVED_OPTIONAL"
    assert source["ci_drift_enforced"] is False


# ---------------------------------------------------------------------------
# Test 27: README / AGENTS / PLANS include P102A handoff
# ---------------------------------------------------------------------------


def test_readme_includes_p102a_handoff() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "P102A" in readme or "p101_readiness_repair_plan" in readme


def test_agents_includes_p102a_handoff() -> None:
    agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "p101_readiness_repair_plan" in agents


def test_plans_includes_p102a_milestone() -> None:
    plans = (REPO_ROOT / "PLANS.md").read_text(encoding="utf-8")
    assert "P102A" in plans


# ---------------------------------------------------------------------------
# Test 28: No P103 implementation is added by this PR
# ---------------------------------------------------------------------------


def test_no_p103_implementation_present() -> None:
    repo_root = REPO_ROOT
    # Check for P103 core files
    core_files = list((repo_root / "core").glob("*p103*"))
    assert len(core_files) == 0, f"Unexpected P103 core files: {core_files}"
    # Check for P103 scripts
    script_files = list((repo_root / "scripts").glob("*p103*"))
    assert len(script_files) == 0, f"Unexpected P103 script files: {script_files}"


# ---------------------------------------------------------------------------
# Additional governance invariant checks
# ---------------------------------------------------------------------------


def test_governance_locks_constants() -> None:
    """Verify all governance lock fields are hard-coded false in packet."""
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=REPO_ROOT)
    assert packet["canonical_status"] == "ADVISORY_ONLY"
    assert packet["audit_only"] is True
    assert packet["projection_only"] is True
    assert packet["repair_plan_only"] is True
    assert packet["readiness_repair_plan_only"] is True
    assert packet["p101_readiness_repair_allowed"] is False


def test_source_path_fields_match_constants(tmp_path: Path) -> None:
    """Verify source path fields reference the expected artifact paths."""
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    assert packet["source_p102_audit_path"] == SOURCE_P102_AUDIT_PATH
    assert packet["source_p101_gate_path"] == SOURCE_P101_GATE_PATH
    assert packet["source_p100_plan_path"] == SOURCE_P100_PLAN_PATH
    assert packet["source_p99_plan_path"] == SOURCE_P99_PLAN_PATH


def test_rerun_p102_requirements_required_readable_true(tmp_path: Path) -> None:
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    for req in packet["rerun_p102_requirements"]:
        assert req["required_readable"] is True


def test_validation_requirements_always_ten_items(tmp_path: Path) -> None:
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    assert len(packet["validation_requirements"]) == 10


def test_rerun_p102_requirements_always_three_items(tmp_path: Path) -> None:
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    assert len(packet["rerun_p102_requirements"]) == 3


def test_p102_degraded_unreadable_p101_returns_blocked(tmp_path: Path) -> None:
    _seed_p102(tmp_path)
    p = tmp_path / SOURCE_P101_GATE_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    # Write unreadable (empty bytes but chmodded unreadable)
    p.write_bytes(b"")
    import stat

    p.chmod(stat.S_IWUSR)  # write-only, not readable
    try:
        packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
        assert packet["p101_readiness_repair_status"] == "P101_READINESS_REPAIR_BLOCKED"
    finally:
        p.chmod(stat.S_IRUSR | stat.S_IWUSR)


def test_packet_hash_excluded_from_hash_computation(tmp_path: Path) -> None:
    """packet_hash must be computed from packet_base (excluding packet_hash itself)."""
    _seed_p102(tmp_path)
    _seed_p101(tmp_path)
    _seed_p100(tmp_path)
    _seed_p99(tmp_path)
    packet = build_temporal_continuity_p101_readiness_repair_plan(repo_root=tmp_path)
    # Build base without hash
    base = {k: v for k, v in packet.items() if k != "packet_hash"}
    from core.canonical.json import canonical_hash

    expected_hash = canonical_hash(base)
    assert packet["packet_hash"] == expected_hash
