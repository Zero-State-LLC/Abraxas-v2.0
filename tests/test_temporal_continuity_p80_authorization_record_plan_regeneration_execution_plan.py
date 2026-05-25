from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan import (
    build_temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan,
    write_temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan,
)
from scripts import run_temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan

P84_PATH = "out/temporal_continuity_p80_authorization_record_plan_regeneration_plan/latest.json"
ALLOWED_COMMAND = (
    "python scripts/run_temporal_continuity_upstream_input_regeneration_authorization_record_plan.py"
)
EXPECTED_OUTPUT_PATH = (
    "out/temporal_continuity_upstream_input_regeneration_authorization_record_plan/latest.json"
)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _seed_p84(
    root: Path,
    *,
    status: str = "P80_REGENERATION_PLAN_READY",
    future_runner_command: str = ALLOWED_COMMAND,
    expected_output_path: str = EXPECTED_OUTPUT_PATH,
    production_activation: bool = False,
) -> None:
    _write_json(
        root / P84_PATH,
        {
            "artifact_type": "TemporalContinuityP80AuthorizationRecordPlanRegenerationPlan.v1",
            "canonical_status": "ADVISORY_ONLY",
            "audit_only": True,
            "projection_only": True,
            "regeneration_plan_only": True,
            "production_activation": production_activation,
            "canon_promotion": False,
            "forecast_influence": False,
            "scheduler_mutation": False,
            "runtime_authority": False,
            "repair_authority": False,
            "repair_execution_authority": False,
            "regeneration_authority": False,
            "evidence_generation_authority": False,
            "restoration_execution_authority": False,
            "generator_execution_authority": False,
            "upstream_input_generation_authority": False,
            "artifact_regeneration_authority": False,
            "execution_authority": False,
            "authorization_authority": False,
            "authorization_record_creation_authority": False,
            "spine_implementation_authority": False,
            "source_p83_status_plan_path": "out/temporal_continuity_p79_authorization_gate_status_repair_plan/latest.json",
            "source_p83_status_plan_observed": True,
            "source_p83_status_plan_readable": True,
            "source_p83_status_plan_hash": "a" * 64,
            "source_p83_status_plan_status": "P79_STATUS_REPAIR_NOT_REQUIRED",
            "source_p83_recommended_next_lane": "P80_AUTHORIZATION_RECORD_PLAN_REGENERATION",
            "source_p79_gate_path": "out/temporal_continuity_upstream_input_regeneration_authorization_gate/latest.json",
            "source_p79_gate_observed": True,
            "source_p79_gate_readable": True,
            "source_p79_gate_hash": "b" * 64,
            "source_p79_gate_status": "AUTHORIZATION_ELIGIBLE",
            "source_p80_record_plan_path": EXPECTED_OUTPUT_PATH,
            "source_p80_record_plan_observed": False,
            "source_p80_record_plan_readable": False,
            "source_p80_record_plan_hash": "NOT_COMPUTABLE",
            "source_p80_record_plan_status": "NOT_COMPUTABLE",
            "p80_regeneration_plan_status": status,
            "p80_regeneration_required": status == "P80_REGENERATION_PLAN_READY",
            "p80_regeneration_allowed": False,
            "regeneration_reasons": [],
            "regeneration_items": [],
            "future_runner_command": future_runner_command,
            "expected_output_path": expected_output_path,
            "prerequisite_sources": [],
            "validation_requirements": [],
            "blocked_regeneration_reasons": [],
            "degraded_evidence_inputs": ["e2", "e1"],
            "inherited_blockers": ["b2", "b1"],
            "inherited_drift_flags": ["d2", "d1"],
            "semantic_overlap_flags": ["s2", "s1"],
            "regeneration_strategy_summary": {},
            "recommended_next_lane": "P85_TEMPORAL_CONTINUITY_P80_AUTHORIZATION_RECORD_PLAN_REGENERATION_EXECUTION_PLAN",
            "recommended_next_lane_reason": "test seed",
            "denied_authority": [],
            "packet_hash": "f" * 64,
        },
    )


def test_missing_source_returns_not_computable(tmp_path: Path) -> None:
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    assert packet["p80_regeneration_execution_plan_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P84_REGENERATION_PLAN_REGENERATION"


def test_malformed_source_returns_not_computable(tmp_path: Path) -> None:
    target = tmp_path / P84_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{bad", encoding="utf-8")
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    assert packet["p80_regeneration_execution_plan_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P84_REGENERATION_PLAN_REGENERATION"


def test_blocked_not_computable_source_status_propagates_blocked(tmp_path: Path) -> None:
    _seed_p84(tmp_path, status="NOT_COMPUTABLE")
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    assert packet["p80_regeneration_execution_plan_status"] == "P80_REGENERATION_EXECUTION_PLAN_BLOCKED"
    assert packet["recommended_next_lane"] == "P84_REGENERATION_PLAN_REGENERATION"


def test_exact_command_validation_enforced(tmp_path: Path) -> None:
    _seed_p84(tmp_path, future_runner_command=f"{ALLOWED_COMMAND} && echo x")
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    assert packet["p80_regeneration_execution_plan_status"] == "NOT_COMPUTABLE"
    assert "P84_COMMAND_MISMATCH" in packet["blocked_execution_reasons"]


def test_exact_output_path_validation_enforced(tmp_path: Path) -> None:
    _seed_p84(tmp_path, expected_output_path="out/other/latest.json")
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    assert packet["p80_regeneration_execution_plan_status"] == "NOT_COMPUTABLE"
    assert "P84_EXPECTED_OUTPUT_PATH_MISMATCH" in packet["blocked_execution_reasons"]


def test_governance_locks_remain_false(tmp_path: Path) -> None:
    _seed_p84(tmp_path)
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    assert packet["canonical_status"] == "ADVISORY_ONLY"
    assert packet["execution_plan_only"] is True
    assert packet["regeneration_execution_plan_only"] is True
    assert packet["p80_regeneration_execution_allowed"] is False
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


def test_deterministic_ordering_for_blocked_reasons(tmp_path: Path) -> None:
    _seed_p84(
        tmp_path,
        future_runner_command=f"{ALLOWED_COMMAND} --bad",
        expected_output_path="out/bad/latest.json",
        production_activation=True,
    )
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    assert packet["blocked_execution_reasons"] == [
        "P84_COMMAND_MISMATCH",
        "P84_EXPECTED_OUTPUT_PATH_MISMATCH",
        "P84_AUTHORITY_LOCK_VIOLATION",
    ]


def test_packet_hash_is_deterministic(tmp_path: Path) -> None:
    _seed_p84(tmp_path)
    first = build_temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    assert first["packet_hash"] == second["packet_hash"]
    assert len(first["packet_hash"]) == 64


def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_p84(tmp_path)
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan"
        / "latest.json"
    )
    write_temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan(
        out_path,
        packet,
    )
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


def test_execution_authorized_and_allowed_always_false(tmp_path: Path) -> None:
    _seed_p84(tmp_path)
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    for step in packet["execution_steps"]:
        assert step["execution_authorized"] is False
        assert step["execution_allowed"] is False
    for item in packet["command_allowlist"]:
        assert item["execution_authorized"] is False
        assert item["execution_allowed"] is False


def test_runner_writes_expected_output_path(tmp_path: Path) -> None:
    _seed_p84(tmp_path)
    first = run_temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan.run(
        repo_root=tmp_path
    )
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan"
        / "latest.json"
    )
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan.run(
        repo_root=tmp_path
    )
    second_text = out_path.read_text(encoding="utf-8")
    assert first["packet_hash"] == second["packet_hash"]
    assert first_text == second_text


def test_schema_required_fields_present_and_locked() -> None:
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "contracts"
        / "canon"
        / "temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan.v1.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    required = set(schema["required"])
    for field in (
        "artifact_type",
        "canonical_status",
        "execution_plan_only",
        "regeneration_execution_plan_only",
        "p80_regeneration_execution_allowed",
        "execution_steps",
        "command_allowlist",
        "packet_hash",
    ):
        assert field in required
    assert schema["properties"]["artifact_type"]["const"] == (
        "TemporalContinuityP80AuthorizationRecordPlanRegenerationExecutionPlan.v1"
    )
    assert schema["properties"]["canonical_status"]["const"] == "ADVISORY_ONLY"
    assert schema["properties"]["execution_plan_only"]["const"] is True
    assert schema["properties"]["regeneration_execution_plan_only"]["const"] is True
    assert schema["properties"]["p80_regeneration_execution_allowed"]["const"] is False
    assert (
        schema["properties"]["execution_steps"]["items"]["properties"]["execution_authorized"][
            "const"
        ]
        is False
    )
    assert (
        schema["properties"]["execution_steps"]["items"]["properties"]["execution_allowed"][
            "const"
        ]
        is False
    )
    assert (
        schema["properties"]["command_allowlist"]["items"]["properties"][
            "execution_authorized"
        ]["const"]
        is False
    )
    assert (
        schema["properties"]["command_allowlist"]["items"]["properties"]["execution_allowed"][
            "const"
        ]
        is False
    )


def test_artifact_registry_classifies_output_as_derived_optional() -> None:
    from core.generated_artifact_registry import (  # type: ignore[attr-defined]
        _DERIVED_OPTIONAL_ARTIFACTS,
        build_generated_artifact_registry,
        list_ci_drift_artifact_paths,
    )

    artifact = (
        "out/temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan/latest.json"
    )
    assert artifact in _DERIVED_OPTIONAL_ARTIFACTS
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    assert artifact not in list_ci_drift_artifact_paths(registry)
