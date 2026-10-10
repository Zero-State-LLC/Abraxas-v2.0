from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import canonical_dumps
from core.generated_artifact_registry import build_generated_artifact_registry
from core.temporal_continuity_selected_repair_execution_plan import (
    SOURCE_P102B_ROUTER_PATH,
    build_temporal_continuity_selected_repair_execution_plan,
    write_temporal_continuity_selected_repair_execution_plan,
)
from scripts.temporal import run_temporal_continuity_selected_repair_execution_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = "out/temporal_continuity_selected_repair_execution_plan/latest.json"

_COMMAND_P99 = (
    "python scripts/temporal/run_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_plan.py"
)
_COMMAND_P100 = (
    "python scripts/temporal/run_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_plan.py"
)
_COMMAND_P101 = (
    "python scripts/temporal/run_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_authorization_gate.py"
)
_COMMAND_P102 = "python scripts/temporal/run_temporal_continuity_recursive_authorization_chain_compression_audit.py"


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )


def _selected_sequence(commands: list[str]) -> list[dict[str, object]]:
    target_map = {
        _COMMAND_P99: "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_plan/latest.json",
        _COMMAND_P100: "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_plan/latest.json",
        _COMMAND_P101: "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_authorization_gate/latest.json",
        _COMMAND_P102: "out/temporal_continuity_recursive_authorization_chain_compression_audit/latest.json",
    }
    status_map = {
        _COMMAND_P99: "P83_SEQUENCE_RECORD_CREATION_RECORD_PLAN_READY",
        _COMMAND_P100: "P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_PLAN_READY",
        _COMMAND_P101: "P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_AUTHORIZATION_ELIGIBLE",
        _COMMAND_P102: "COMPRESSION_AUDIT_READY",
    }
    return [
        {
            "sequence_id": f"seq_{index:03d}",
            "command": command,
            "target_artifact_path": target_map[command],
            "purpose": f"purpose_{index:03d}",
            "execution_allowed": False,
            "expected_status_after_run": status_map[command],
        }
        for index, command in enumerate(commands, start=1)
    ]


def _command_allowlist() -> list[dict[str, object]]:
    return [
        {
            "command": command,
            "allowed_for_planning": True,
            "execution_allowed": False,
            "rationale": f"allow_{index:03d}",
        }
        for index, command in enumerate(
            [_COMMAND_P99, _COMMAND_P100, _COMMAND_P101, _COMMAND_P102], start=1
        )
    ]


def _seed_p102b(
    root: Path,
    *,
    router_status: str = "REPAIR_EXECUTION_PLAN_ROUTER_READY",
    selected_execution_plan_lane: str = "P102B_P101_GATE_REGENERATION_EXECUTION_PLAN",
    selected_command_sequence: list[dict[str, object]] | None = None,
    command_allowlist: list[dict[str, object]] | None = None,
    validation_requirements: list[dict[str, object]] | None = None,
    recommended_next_lane: str = "P102C_P101_GATE_REGENERATION_EXECUTION_PLAN",
    degraded_evidence_inputs: list[object] | None = None,
    inherited_blockers: list[object] | None = None,
    inherited_drift_flags: list[object] | None = None,
    semantic_overlap_flags: list[object] | None = None,
) -> None:
    default_commands = {
        "P102B_P101_GATE_REGENERATION_EXECUTION_PLAN": [_COMMAND_P101, _COMMAND_P102],
        "P102B_P99_P100_P101_CHAIN_REGENERATION_EXECUTION_PLAN": [
            _COMMAND_P99,
            _COMMAND_P100,
            _COMMAND_P101,
            _COMMAND_P102,
        ],
        "P102B_COMPRESSION_AUDIT_RERUN_EXECUTION_PLAN": [_COMMAND_P102],
        "NO_REPAIR_REQUIRED": [],
    }
    commands = default_commands.get(
        selected_execution_plan_lane,
        [_COMMAND_P101, _COMMAND_P102],
    )
    _write_json(
        root / SOURCE_P102B_ROUTER_PATH,
        {
            "artifact_type": "TemporalContinuityRepairExecutionPlanRouter.v1",
            "canonical_status": "ADVISORY_ONLY",
            "audit_only": True,
            "projection_only": True,
            "execution_plan_router_only": True,
            "repair_execution_plan_router_only": True,
            "production_activation": False,
            "canon_promotion": False,
            "forecast_influence": False,
            "scheduler_mutation": False,
            "runtime_authority": False,
            "repair_authority": False,
            "repair_execution_authority": False,
            "regeneration_authority": False,
            "regeneration_execution_authority": False,
            "evidence_generation_authority": False,
            "restoration_execution_authority": False,
            "generator_execution_authority": False,
            "upstream_input_generation_authority": False,
            "artifact_regeneration_authority": False,
            "execution_authority": False,
            "authorization_authority": False,
            "authorization_granted": False,
            "authorization_token_created": False,
            "authorization_record_creation_authority": False,
            "authorization_record_created": False,
            "spine_implementation_authority": False,
            "source_p102a_repair_plan_path": "out/temporal_continuity_p101_readiness_repair_plan/latest.json",
            "source_p102a_repair_plan_observed": True,
            "source_p102a_repair_plan_readable": True,
            "source_p102a_repair_plan_hash": "a" * 64,
            "source_p102a_repair_status": "P101_READINESS_REPAIR_PLAN_READY",
            "source_p102a_recommended_next_lane": selected_execution_plan_lane,
            "source_future_command_sequence_count": len(commands),
            "p102b_router_status": router_status,
            "selected_execution_plan_lane": selected_execution_plan_lane,
            "selected_execution_plan_reason": "test seed",
            "selected_command_sequence": (
                _selected_sequence(commands)
                if selected_command_sequence is None
                else selected_command_sequence
            ),
            "command_allowlist": (
                _command_allowlist() if command_allowlist is None else command_allowlist
            ),
            "validation_requirements": (
                [
                    {
                        "requirement_id": "validation_001",
                        "artifact_path": "out/example/latest.json",
                        "required_readable": True,
                        "required_status": "READY",
                        "failure_action": "REGENERATE_EXAMPLE",
                    }
                ]
                if validation_requirements is None
                else validation_requirements
            ),
            "rerun_p102_requirements": [],
            "blocked_reasons": [],
            "degraded_evidence_inputs": (
                [] if degraded_evidence_inputs is None else degraded_evidence_inputs
            ),
            "inherited_blockers": (
                [] if inherited_blockers is None else inherited_blockers
            ),
            "inherited_drift_flags": (
                [] if inherited_drift_flags is None else inherited_drift_flags
            ),
            "semantic_overlap_flags": (
                [] if semantic_overlap_flags is None else semantic_overlap_flags
            ),
            "router_strategy_summary": {},
            "recommended_next_lane": recommended_next_lane,
            "recommended_next_lane_reason": "test seed",
            "denied_authority": [],
            "packet_hash": "f" * 64,
        },
    )


def test_missing_p102b_source_returns_not_computable(tmp_path: Path) -> None:
    packet = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    assert packet["p102c_execution_plan_status"] == "NOT_COMPUTABLE"
    assert packet["selected_branch_type"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P102B_REPAIR_EXECUTION_PLAN_ROUTER_REGENERATION"


def test_malformed_p102b_source_returns_not_computable(tmp_path: Path) -> None:
    source = tmp_path / SOURCE_P102B_ROUTER_PATH
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("{bad-json", encoding="utf-8")
    packet = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    assert packet["p102c_execution_plan_status"] == "NOT_COMPUTABLE"
    assert packet["selected_branch_type"] == "NOT_COMPUTABLE"


def test_p102b_blocked_maps_to_selected_repair_execution_plan_blocked(
    tmp_path: Path,
) -> None:
    _seed_p102b(tmp_path, router_status="REPAIR_EXECUTION_PLAN_ROUTER_BLOCKED")
    packet = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    assert packet["p102c_execution_plan_status"] == "SELECTED_REPAIR_EXECUTION_PLAN_BLOCKED"
    assert packet["execution_blockers"] == ["P102B_ROUTER_BLOCKED"]


def test_p102b_not_required_maps_to_selected_repair_execution_plan_not_required(
    tmp_path: Path,
) -> None:
    _seed_p102b(
        tmp_path,
        router_status="REPAIR_EXECUTION_PLAN_NOT_REQUIRED",
        selected_execution_plan_lane="NO_REPAIR_REQUIRED",
        recommended_next_lane="P102_RECOMMENDED_NEXT_LANE_PASSTHROUGH",
    )
    packet = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    assert packet["p102c_execution_plan_status"] == "SELECTED_REPAIR_EXECUTION_NOT_REQUIRED"
    assert packet["selected_branch_type"] == "NO_REPAIR_REQUIRED"
    assert packet["recommended_next_lane"] == "P102_RECOMMENDED_NEXT_LANE_PASSTHROUGH"


def test_p101_only_branch_maps_to_selected_branch_type(tmp_path: Path) -> None:
    _seed_p102b(tmp_path)
    packet = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    assert packet["selected_branch_type"] == "P101_GATE_ONLY"


def test_full_chain_branch_maps_to_selected_branch_type(tmp_path: Path) -> None:
    _seed_p102b(
        tmp_path,
        selected_execution_plan_lane="P102B_P99_P100_P101_CHAIN_REGENERATION_EXECUTION_PLAN",
    )
    packet = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    assert packet["selected_branch_type"] == "P99_P100_P101_CHAIN"


def test_rerun_only_branch_maps_to_selected_branch_type(tmp_path: Path) -> None:
    _seed_p102b(
        tmp_path,
        selected_execution_plan_lane="P102B_COMPRESSION_AUDIT_RERUN_EXECUTION_PLAN",
    )
    packet = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    assert packet["selected_branch_type"] == "P102_RERUN_ONLY"


def test_unsupported_command_blocks_the_plan(tmp_path: Path) -> None:
    _seed_p102b(
        tmp_path,
        selected_command_sequence=[
            {
                "sequence_id": "seq_001",
                "command": "python scripts/run_unsafe.py",
                "target_artifact_path": "out/bad/latest.json",
                "purpose": "bad",
                "execution_allowed": False,
                "expected_status_after_run": "BAD",
            }
        ],
    )
    packet = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    assert packet["p102c_execution_plan_status"] == "SELECTED_REPAIR_EXECUTION_PLAN_BLOCKED"
    assert "UNSUPPORTED_COMMAND" in packet["execution_blockers"]


def test_shell_chaining_blocks_the_plan(tmp_path: Path) -> None:
    _seed_p102b(
        tmp_path,
        selected_command_sequence=[
            {
                "sequence_id": "seq_001",
                "command": f"{_COMMAND_P101} && echo bad",
                "target_artifact_path": "out/bad/latest.json",
                "purpose": "bad",
                "execution_allowed": False,
                "expected_status_after_run": "BAD",
            }
        ],
    )
    packet = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    assert "DYNAMIC_COMMAND_SYNTAX" in packet["execution_blockers"]


def test_flags_block_the_plan(tmp_path: Path) -> None:
    _seed_p102b(
        tmp_path,
        selected_command_sequence=[
            {
                "sequence_id": "seq_001",
                "command": f"{_COMMAND_P102} --unsafe",
                "target_artifact_path": "out/bad/latest.json",
                "purpose": "bad",
                "execution_allowed": False,
                "expected_status_after_run": "BAD",
            }
        ],
    )
    packet = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    assert packet["p102c_execution_plan_status"] == "SELECTED_REPAIR_EXECUTION_PLAN_BLOCKED"
    assert "UNSUPPORTED_COMMAND" in packet["execution_blockers"]


def test_execution_allowed_true_blocks_the_plan(tmp_path: Path) -> None:
    sequence = _selected_sequence([_COMMAND_P101, _COMMAND_P102])
    sequence[0]["execution_allowed"] = True
    _seed_p102b(tmp_path, selected_command_sequence=sequence)
    packet = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    assert "COMMAND_EXECUTION_ALLOWED_TRUE" in packet["execution_blockers"]


def test_execution_authority_true_blocks_the_plan(tmp_path: Path) -> None:
    sequence = _selected_sequence([_COMMAND_P101, _COMMAND_P102])
    sequence[0]["execution_authority"] = True
    _seed_p102b(tmp_path, selected_command_sequence=sequence)
    packet = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    assert "COMMAND_EXECUTION_AUTHORITY_TRUE" in packet["execution_blockers"]


def test_planned_execution_steps_preserve_router_sequence_order(tmp_path: Path) -> None:
    _seed_p102b(
        tmp_path,
        selected_execution_plan_lane="P102B_P99_P100_P101_CHAIN_REGENERATION_EXECUTION_PLAN",
    )
    packet = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    commands = [item["command"] for item in packet["planned_execution_steps"]]
    assert commands == [_COMMAND_P99, _COMMAND_P100, _COMMAND_P101, _COMMAND_P102]


def test_all_planned_execution_steps_have_execution_allowed_false(
    tmp_path: Path,
) -> None:
    _seed_p102b(tmp_path)
    packet = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    assert packet["planned_execution_steps"]
    for item in packet["planned_execution_steps"]:
        assert item["execution_allowed"] is False


def test_all_planned_execution_steps_have_execution_authority_false(
    tmp_path: Path,
) -> None:
    _seed_p102b(tmp_path)
    packet = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    for item in packet["planned_execution_steps"]:
        assert item["execution_authority"] is False


def test_all_authority_fields_false(tmp_path: Path) -> None:
    _seed_p102b(tmp_path)
    packet = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    for field in (
        "production_activation",
        "canon_promotion",
        "forecast_influence",
        "scheduler_mutation",
        "runtime_authority",
        "repair_authority",
        "repair_execution_authority",
        "regeneration_authority",
        "regeneration_execution_authority",
        "evidence_generation_authority",
        "restoration_execution_authority",
        "generator_execution_authority",
        "upstream_input_generation_authority",
        "artifact_regeneration_authority",
        "execution_authority",
        "authorization_authority",
        "authorization_record_creation_authority",
        "spine_implementation_authority",
    ):
        assert packet[field] is False
    assert packet["authorization_granted"] is False
    assert packet["authorization_token_created"] is False
    assert packet["authorization_record_created"] is False


def test_command_allowlist_contains_only_exact_allowed_commands(tmp_path: Path) -> None:
    _seed_p102b(tmp_path)
    packet = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    assert packet["command_allowlist"] == [
        _COMMAND_P99,
        _COMMAND_P100,
        _COMMAND_P101,
        _COMMAND_P102,
    ]


def test_preflight_checks_deterministic(tmp_path: Path) -> None:
    _seed_p102b(tmp_path)
    first = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    second = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    assert first["preflight_checks"] == second["preflight_checks"]


def test_postrun_validation_requirements_deterministic(tmp_path: Path) -> None:
    _seed_p102b(tmp_path)
    first = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    second = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    assert (
        first["postrun_validation_requirements"]
        == second["postrun_validation_requirements"]
    )


def test_rerun_p102_requirements_deterministic(tmp_path: Path) -> None:
    _seed_p102b(
        tmp_path,
        selected_execution_plan_lane="P102B_P99_P100_P101_CHAIN_REGENERATION_EXECUTION_PLAN",
    )
    first = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    second = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    assert first["rerun_p102_requirements"] == second["rerun_p102_requirements"]


def test_execution_blockers_deterministic(tmp_path: Path) -> None:
    _seed_p102b(
        tmp_path,
        selected_command_sequence=[
            {
                "sequence_id": "seq_001",
                "command": f"{_COMMAND_P101} && echo bad",
                "target_artifact_path": "out/bad/latest.json",
                "purpose": "bad",
                "execution_allowed": True,
                "execution_authority": True,
                "expected_status_after_run": "BAD",
            }
        ],
    )
    first = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    second = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    assert first["execution_blockers"] == second["execution_blockers"]


def test_inherited_degraded_evidence_preserved_exactly(tmp_path: Path) -> None:
    evidence = ["e2", {"kind": "e1"}]
    _seed_p102b(tmp_path, degraded_evidence_inputs=evidence)
    packet = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    assert packet["degraded_evidence_inputs"] == evidence


def test_inherited_blockers_preserved_exactly(tmp_path: Path) -> None:
    blockers = ["b2", {"kind": "b1"}]
    _seed_p102b(tmp_path, inherited_blockers=blockers)
    packet = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    assert packet["inherited_blockers"] == blockers


def test_inherited_drift_flags_preserved_exactly(tmp_path: Path) -> None:
    flags = ["d2", {"kind": "d1"}]
    _seed_p102b(tmp_path, inherited_drift_flags=flags)
    packet = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    assert packet["inherited_drift_flags"] == flags


def test_semantic_overlap_flags_preserved_exactly(tmp_path: Path) -> None:
    flags = ["s2", {"kind": "s1"}]
    _seed_p102b(tmp_path, semantic_overlap_flags=flags)
    packet = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    assert packet["semantic_overlap_flags"] == flags


def test_packet_hash_deterministic(tmp_path: Path) -> None:
    _seed_p102b(tmp_path)
    first = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    second = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    assert first["packet_hash"] == second["packet_hash"]
    assert len(first["packet_hash"]) == 64


def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_p102b(tmp_path)
    packet = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    out = tmp_path / "selected_output.json"
    write_temporal_continuity_selected_repair_execution_plan(out, packet)
    text = out.read_text(encoding="utf-8")
    parsed = json.loads(text)
    assert text.endswith("\n")
    assert text == canonical_dumps(parsed) + "\n"


def test_runner_writes_output_path(tmp_path: Path) -> None:
    _seed_p102b(tmp_path)
    packet = run_temporal_continuity_selected_repair_execution_plan.run(repo_root=tmp_path)
    expected = tmp_path / OUT_PATH
    assert expected.exists()
    content = json.loads(expected.read_text(encoding="utf-8"))
    assert content["artifact_type"] == "TemporalContinuitySelectedRepairExecutionPlan.v1"
    assert content["packet_hash"] == packet["packet_hash"]


def test_artifact_registry_classifies_output_as_derived_optional() -> None:
    registry = build_generated_artifact_registry(repo_root=REPO_ROOT)
    artifact_path = "out/temporal_continuity_selected_repair_execution_plan/latest.json"
    entry = next((a for a in registry.entries if a.artifact_path == artifact_path), None)
    source = registry.artifact_source_map[artifact_path]
    assert entry is not None
    assert entry.determinism_class == "DERIVED_OPTIONAL"
    assert source["ci_drift_enforced"] is False


# The P102 handoff moved out of the front-door docs: 09850527 dropped it from
# README.md and ce7ff536 moved the AGENTS.md copy to
# docs/status/HISTORICAL_GOVERNANCE_AGENT_NOTES.md (linked from AGENTS.md), since
# P70-P130 continuity material is not a routine startup requirement.
HISTORICAL_NOTES = "docs/status/HISTORICAL_GOVERNANCE_AGENT_NOTES.md"


def test_docs_include_p102c_handoff() -> None:
    agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    notes = (REPO_ROOT / HISTORICAL_NOTES).read_text(encoding="utf-8")
    plans = (REPO_ROOT / "PLANS.md").read_text(encoding="utf-8")
    assert HISTORICAL_NOTES in agents
    assert "run_temporal_continuity_selected_repair_execution_plan.py" in notes
    assert "run_temporal_continuity_selected_repair_execution_plan.py" in plans


def test_no_command_execution_is_performed(tmp_path: Path) -> None:
    _seed_p102b(
        tmp_path,
        selected_execution_plan_lane="P102B_P99_P100_P101_CHAIN_REGENERATION_EXECUTION_PLAN",
    )
    packet = build_temporal_continuity_selected_repair_execution_plan(repo_root=tmp_path)
    assert packet["planned_execution_steps"]
    assert not (
        tmp_path
        / "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_plan/latest.json"
    ).exists()
    assert not (
        tmp_path / "out/temporal_continuity_recursive_authorization_chain_compression_audit/latest.json"
    ).exists()
