"""Deterministic tests for PATCH-P11-OPERATOR-RUNTIME-CONSOLE-001.

Proves:
- packet shape stability
- missing source artifact handling (NOT_COMPUTABLE / BLOCKED)
- projection_only / advisory_only flags always True
- authority / mutation / promotion always False
- deterministic operator next actions
- Markdown summary generation
- no runtime / canon mutation
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

from core.benchmark import build_benchmark_result, build_benchmark_suite
from core.operator_runtime_console import (
    PATCH_ID,
    _NOT_COMPUTABLE,
    build_markdown_summary,
    build_operator_runtime_console_packet,
    write_operator_runtime_console_packet,
)
from scripts import run_operator_runtime_console


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_benchmark_artifact(
    surface: str = "registry",
    output_hash: str = "stable_hash",
    durations: list[int] | None = None,
    cache_misses: int = 0,
) -> dict[str, Any]:
    if durations is None:
        durations = [1_000_000, 1_100_000, 1_050_000]
    results = [
        build_benchmark_result(
            surface=surface,
            run_index=i,
            duration_ns=d,
            output_hash=output_hash,
            cache_misses=cache_misses,
            serialization_counts=1,
            artifact_writes=1,
        )
        for i, d in enumerate(durations)
    ]
    baseline = build_benchmark_suite(
        suite_id=f"{surface}.baseline",
        surface=f"{surface}.baseline",
        results=results,
    )
    optimized = build_benchmark_suite(
        suite_id=f"{surface}.optimized",
        surface=f"{surface}.optimized",
        results=results,
    )
    from core.benchmark import build_benchmark_artifact

    return build_benchmark_artifact(
        artifact_id="runtime_benchmark_001",
        baseline_suite=baseline,
        optimized_suite=optimized,
        output_path=Path("out/audit/runtime_benchmark_001.latest.json"),
    )


def _make_stabilization_artifact() -> dict[str, Any]:
    return {
        "authority_boundary_status": {
            "authority_granted": False,
            "mutation_allowed": False,
            "promotion_allowed": False,
            "status": "locked",
        },
        "final_posture": {
            "status": "STABILIZED_RELEASE_READINESS_RECORDED",
            "authority_granted": False,
            "mutation_allowed": False,
            "promotion_allowed": False,
        },
    }


def _make_freeze_artifact() -> dict[str, Any]:
    return {
        "patch_id": "PATCH-P7-MANUAL-RELEASE-TAG-AND-GOVERNANCE-FREEZE-001",
        "freeze_status": "FROZEN",
        "frozen_surfaces": {},
        "future_changes_require": ["separate PR", "tests", "audit artifact"],
    }


def _build_full_packet(tmp_path: Path) -> dict[str, Any]:
    """Build a packet with all source artifacts present."""
    bench = _make_benchmark_artifact()
    stab = _make_stabilization_artifact()
    freeze = _make_freeze_artifact()

    bench_path = tmp_path / "runtime_benchmark_001.latest.json"
    stab_path = tmp_path / "stabilization_release_readiness_001.latest.json"
    freeze_path = tmp_path / "governance_freeze_baseline_001.latest.json"
    profile_path = tmp_path / "runtime_performance_profile_001.latest.json"

    bench_path.write_text(json.dumps(bench), encoding="utf-8")
    stab_path.write_text(json.dumps(stab), encoding="utf-8")
    freeze_path.write_text(json.dumps(freeze), encoding="utf-8")
    # Profile artifact absent intentionally to test NOT_COMPUTABLE handling.

    return build_operator_runtime_console_packet(
        packet_id="operator_runtime_console_001",
        runtime_profile_path=profile_path,
        benchmark_path=bench_path,
        stabilization_path=stab_path,
        governance_freeze_path=freeze_path,
    )


# ---------------------------------------------------------------------------
# Packet shape stability
# ---------------------------------------------------------------------------


def test_packet_shape_is_stable(tmp_path: Path) -> None:
    packet = _build_full_packet(tmp_path)

    expected_top_keys = sorted(
        [
            "advisory_only",
            "artifact_health_summary",
            "authority_boundary_summary",
            "authority_granted",
            "benchmark_summary",
            "cache_safety_summary",
            "correlation_id",
            "final_posture",
            "mutation_allowed",
            "operator_next_actions",
            "optimization_drift_summary",
            "packet_hash",
            "packet_id",
            "patch_id",
            "projection_only",
            "promotion_allowed",
            "remaining_blockers",
            "replay_equivalence_summary",
            "runtime_profile_summary",
            "schema",
            "source_artifacts",
        ]
    )
    assert sorted(packet.keys()) == expected_top_keys


def test_packet_schema_field(tmp_path: Path) -> None:
    packet = _build_full_packet(tmp_path)
    assert packet["schema"] == "OperatorRuntimeConsolePacket.v1"


def test_packet_patch_id(tmp_path: Path) -> None:
    packet = _build_full_packet(tmp_path)
    assert packet["patch_id"] == PATCH_ID


# ---------------------------------------------------------------------------
# Hard posture flags
# ---------------------------------------------------------------------------


def test_projection_only_is_always_true(tmp_path: Path) -> None:
    packet = _build_full_packet(tmp_path)
    assert packet["projection_only"] is True


def test_advisory_only_is_always_true(tmp_path: Path) -> None:
    packet = _build_full_packet(tmp_path)
    assert packet["advisory_only"] is True


def test_authority_granted_is_always_false(tmp_path: Path) -> None:
    packet = _build_full_packet(tmp_path)
    assert packet["authority_granted"] is False


def test_mutation_allowed_is_always_false(tmp_path: Path) -> None:
    packet = _build_full_packet(tmp_path)
    assert packet["mutation_allowed"] is False


def test_promotion_allowed_is_always_false(tmp_path: Path) -> None:
    packet = _build_full_packet(tmp_path)
    assert packet["promotion_allowed"] is False


# ---------------------------------------------------------------------------
# Missing source artifact handling
# ---------------------------------------------------------------------------


def test_missing_all_artifacts_yields_blocked_posture(tmp_path: Path) -> None:
    packet = build_operator_runtime_console_packet(
        packet_id="test_missing_all",
        runtime_profile_path=tmp_path / "missing_profile.json",
        benchmark_path=tmp_path / "missing_bench.json",
        stabilization_path=tmp_path / "missing_stab.json",
        governance_freeze_path=tmp_path / "missing_freeze.json",
    )
    assert packet["final_posture"] == "BLOCKED"
    assert len(packet["remaining_blockers"]) == 4


def test_missing_artifact_status_is_not_computable(tmp_path: Path) -> None:
    packet = build_operator_runtime_console_packet(
        packet_id="test_missing_bench",
        runtime_profile_path=tmp_path / "missing_profile.json",
        benchmark_path=tmp_path / "missing_bench.json",
        stabilization_path=tmp_path / "missing_stab.json",
        governance_freeze_path=tmp_path / "missing_freeze.json",
    )
    health = packet["artifact_health_summary"]["artifact_statuses"]
    assert health["runtime_benchmark"] == "MISSING"
    assert health["runtime_performance_profile"] == "MISSING"


def test_missing_profile_does_not_fabricate_values(tmp_path: Path) -> None:
    """Profile absent → NOT_COMPUTABLE, no fabricated surface data."""
    packet = _build_full_packet(tmp_path)
    profile_summary = packet["runtime_profile_summary"]
    assert profile_summary["status"] == _NOT_COMPUTABLE
    assert "detail" in profile_summary
    assert "measured_surfaces" not in profile_summary


def test_missing_benchmark_drift_summary_is_not_computable(tmp_path: Path) -> None:
    profile_path = tmp_path / "missing_profile.json"
    bench_path = tmp_path / "missing_bench.json"
    stab_path = tmp_path / "stabilization.json"
    freeze_path = tmp_path / "freeze.json"
    stab_path.write_text(json.dumps(_make_stabilization_artifact()), encoding="utf-8")
    freeze_path.write_text(json.dumps(_make_freeze_artifact()), encoding="utf-8")

    packet = build_operator_runtime_console_packet(
        packet_id="test_missing_bench",
        runtime_profile_path=profile_path,
        benchmark_path=bench_path,
        stabilization_path=stab_path,
        governance_freeze_path=freeze_path,
    )
    assert packet["optimization_drift_summary"]["status"] == _NOT_COMPUTABLE
    assert packet["benchmark_summary"]["status"] == _NOT_COMPUTABLE
    assert packet["cache_safety_summary"]["status"] == _NOT_COMPUTABLE
    assert packet["replay_equivalence_summary"]["status"] == _NOT_COMPUTABLE


def test_partial_artifacts_yields_not_computable_posture(tmp_path: Path) -> None:
    """When some but not all artifacts are present the posture is NOT_COMPUTABLE."""
    bench_path = tmp_path / "bench.json"
    stab_path = tmp_path / "stab.json"
    bench_path.write_text(json.dumps(_make_benchmark_artifact()), encoding="utf-8")
    stab_path.write_text(json.dumps(_make_stabilization_artifact()), encoding="utf-8")

    packet = build_operator_runtime_console_packet(
        packet_id="test_partial",
        runtime_profile_path=tmp_path / "missing_profile.json",
        benchmark_path=bench_path,
        stabilization_path=stab_path,
        governance_freeze_path=tmp_path / "missing_freeze.json",
    )
    assert packet["final_posture"] == _NOT_COMPUTABLE
    assert len(packet["remaining_blockers"]) > 0


# ---------------------------------------------------------------------------
# Deterministic operator next actions
# ---------------------------------------------------------------------------


def test_operator_next_actions_non_empty(tmp_path: Path) -> None:
    packet = _build_full_packet(tmp_path)
    assert isinstance(packet["operator_next_actions"], list)
    assert len(packet["operator_next_actions"]) >= 1


def test_operator_next_actions_lists_blockers(tmp_path: Path) -> None:
    packet = build_operator_runtime_console_packet(
        packet_id="test_blockers",
        runtime_profile_path=tmp_path / "missing_profile.json",
        benchmark_path=tmp_path / "missing_bench.json",
        stabilization_path=tmp_path / "missing_stab.json",
        governance_freeze_path=tmp_path / "missing_freeze.json",
    )
    actions_text = " ".join(packet["operator_next_actions"])
    # Each blocker artifact name should appear in the actions
    for blocker in packet["remaining_blockers"]:
        assert blocker in actions_text


def test_operator_next_actions_freeze_mention_when_frozen(tmp_path: Path) -> None:
    bench_path = tmp_path / "bench.json"
    stab_path = tmp_path / "stab.json"
    freeze_path = tmp_path / "freeze.json"
    bench_path.write_text(json.dumps(_make_benchmark_artifact()), encoding="utf-8")
    stab_path.write_text(json.dumps(_make_stabilization_artifact()), encoding="utf-8")
    freeze_path.write_text(json.dumps(_make_freeze_artifact()), encoding="utf-8")

    packet = build_operator_runtime_console_packet(
        packet_id="test_freeze_action",
        runtime_profile_path=tmp_path / "missing_profile.json",
        benchmark_path=bench_path,
        stabilization_path=stab_path,
        governance_freeze_path=freeze_path,
    )
    actions_text = " ".join(packet["operator_next_actions"])
    assert "freeze" in actions_text.lower() or "governance" in actions_text.lower()


def test_no_blockers_yields_advisory_only_action(tmp_path: Path) -> None:
    """When no blockers exist, actions should contain advisory-only message."""
    bench = _make_benchmark_artifact()
    stab = _make_stabilization_artifact()
    freeze_no_blocker = {"freeze_status": "NOT_FROZEN"}

    bench_path = tmp_path / "bench.json"
    stab_path = tmp_path / "stab.json"
    freeze_path = tmp_path / "freeze.json"
    profile_path = tmp_path / "profile.json"
    bench_path.write_text(json.dumps(bench), encoding="utf-8")
    stab_path.write_text(json.dumps(stab), encoding="utf-8")
    freeze_path.write_text(json.dumps(freeze_no_blocker), encoding="utf-8")
    # Write a minimal valid profile
    profile_path.write_text(
        json.dumps(
            {
                "patch_id": "PATCH-P8-RUNTIME-PERFORMANCE-PROFILING-001",
                "profile_enabled": False,
                "measured_surfaces": [],
                "phase_timings": {},
                "artifact_paths": {},
                "correlation_ids": {},
                "authority_granted": False,
                "mutation_allowed": False,
                "promotion_allowed": False,
                "final_status": "PASS",
                "remaining_blockers": [],
            }
        ),
        encoding="utf-8",
    )

    packet = build_operator_runtime_console_packet(
        packet_id="test_no_blockers",
        runtime_profile_path=profile_path,
        benchmark_path=bench_path,
        stabilization_path=stab_path,
        governance_freeze_path=freeze_path,
    )
    assert packet["remaining_blockers"] == []
    actions_text = " ".join(packet["operator_next_actions"]).lower()
    assert "advisory" in actions_text or "no blockers" in actions_text


# ---------------------------------------------------------------------------
# Determinism — same inputs → same packet_hash
# ---------------------------------------------------------------------------


def test_packet_is_deterministic(tmp_path: Path) -> None:
    bench = _make_benchmark_artifact()
    stab = _make_stabilization_artifact()
    freeze = _make_freeze_artifact()

    bench_path = tmp_path / "bench.json"
    stab_path = tmp_path / "stab.json"
    freeze_path = tmp_path / "freeze.json"
    bench_path.write_text(json.dumps(bench), encoding="utf-8")
    stab_path.write_text(json.dumps(stab), encoding="utf-8")
    freeze_path.write_text(json.dumps(freeze), encoding="utf-8")

    kwargs: dict[str, Any] = {
        "packet_id": "det_test_001",
        "runtime_profile_path": tmp_path / "missing_profile.json",
        "benchmark_path": bench_path,
        "stabilization_path": stab_path,
        "governance_freeze_path": freeze_path,
    }
    packet_a = build_operator_runtime_console_packet(**kwargs)
    packet_b = build_operator_runtime_console_packet(**kwargs)
    assert packet_a["packet_hash"] == packet_b["packet_hash"]
    assert packet_a["final_posture"] == packet_b["final_posture"]
    assert packet_a["remaining_blockers"] == packet_b["remaining_blockers"]


# ---------------------------------------------------------------------------
# Write — canonical JSON shape
# ---------------------------------------------------------------------------


def test_write_produces_canonical_json(tmp_path: Path) -> None:
    packet = _build_full_packet(tmp_path)
    out_path = tmp_path / "console.json"
    written = write_operator_runtime_console_packet(out_path, packet)

    assert written == out_path
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    loaded = json.loads(text)
    assert loaded["patch_id"] == PATCH_ID
    assert loaded["authority_granted"] is False
    assert loaded["projection_only"] is True


# ---------------------------------------------------------------------------
# Markdown summary generation
# ---------------------------------------------------------------------------


def test_markdown_summary_contains_patch_id(tmp_path: Path) -> None:
    packet = _build_full_packet(tmp_path)
    md = build_markdown_summary(packet)
    assert PATCH_ID in md


def test_markdown_summary_contains_final_posture(tmp_path: Path) -> None:
    packet = _build_full_packet(tmp_path)
    md = build_markdown_summary(packet)
    assert packet["final_posture"] in md


def test_markdown_summary_contains_operator_next_actions(tmp_path: Path) -> None:
    packet = _build_full_packet(tmp_path)
    md = build_markdown_summary(packet)
    for action in packet["operator_next_actions"]:
        assert action in md


def test_markdown_summary_contains_artifact_health_section(tmp_path: Path) -> None:
    packet = _build_full_packet(tmp_path)
    md = build_markdown_summary(packet)
    assert "Artifact Health" in md


def test_markdown_summary_missing_artifacts_reflected(tmp_path: Path) -> None:
    packet = build_operator_runtime_console_packet(
        packet_id="md_missing_test",
        runtime_profile_path=tmp_path / "m1.json",
        benchmark_path=tmp_path / "m2.json",
        stabilization_path=tmp_path / "m3.json",
        governance_freeze_path=tmp_path / "m4.json",
    )
    md = build_markdown_summary(packet)
    assert "MISSING" in md or "NOT_COMPUTABLE" in md or "BLOCKED" in md


# ---------------------------------------------------------------------------
# No runtime / canon mutation
# ---------------------------------------------------------------------------


def test_no_file_mutation_outside_output_path(tmp_path: Path) -> None:
    """build_operator_runtime_console_packet must not write any files."""
    bench = _make_benchmark_artifact()
    bench_path = tmp_path / "bench.json"
    bench_path.write_text(json.dumps(bench), encoding="utf-8")

    before_files = set(tmp_path.iterdir())
    build_operator_runtime_console_packet(
        packet_id="no_mutation_test",
        runtime_profile_path=tmp_path / "missing.json",
        benchmark_path=bench_path,
        stabilization_path=tmp_path / "missing_stab.json",
        governance_freeze_path=tmp_path / "missing_freeze.json",
    )
    after_files = set(tmp_path.iterdir())
    assert before_files == after_files


def test_authority_boundary_summary_all_false(tmp_path: Path) -> None:
    packet = _build_full_packet(tmp_path)
    ab = packet["authority_boundary_summary"]
    assert ab["authority_granted"] is False
    assert ab["mutation_allowed"] is False
    assert ab["promotion_allowed"] is False
    assert ab["boundary_integrity"] == "locked"


# ---------------------------------------------------------------------------
# Script integration
# ---------------------------------------------------------------------------


def test_console_script_writes_artifact(tmp_path: Path) -> None:
    runtime_paths = __import__("core.config", fromlist=["RuntimePaths"]).RuntimePaths(
        contracts_dir=Path("contracts"),
        out_dir=tmp_path / "out",
    )
    out_path = runtime_paths.operator_runtime_console_latest
    md_path = runtime_paths.audit_dir / "operator_runtime_console_001.md"

    # Pre-write source artifacts
    bench = _make_benchmark_artifact()
    stab = _make_stabilization_artifact()
    freeze = _make_freeze_artifact()
    runtime_paths.audit_dir.mkdir(parents=True, exist_ok=True)
    (runtime_paths.audit_dir / "runtime_benchmark_001.latest.json").write_text(
        json.dumps(bench), encoding="utf-8"
    )
    (runtime_paths.audit_dir / "stabilization_release_readiness_001.latest.json").write_text(
        json.dumps(stab), encoding="utf-8"
    )
    (runtime_paths.audit_dir / "governance_freeze_baseline_001.latest.json").write_text(
        json.dumps(freeze), encoding="utf-8"
    )

    with (
        patch.object(run_operator_runtime_console, "_PATHS", runtime_paths),
        patch.object(run_operator_runtime_console, "OUT_PATH", out_path),
        patch.object(run_operator_runtime_console, "MD_PATH", md_path),
    ):
        run_operator_runtime_console.main()

    assert out_path.exists()
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["patch_id"] == PATCH_ID
    assert payload["authority_granted"] is False
    assert payload["projection_only"] is True
    assert payload["advisory_only"] is True
    assert md_path.exists()


def test_console_script_missing_artifacts_still_writes(tmp_path: Path) -> None:
    """Script must produce an artifact even when all source artifacts are absent."""
    runtime_paths = __import__("core.config", fromlist=["RuntimePaths"]).RuntimePaths(
        contracts_dir=Path("contracts"),
        out_dir=tmp_path / "out",
    )
    out_path = runtime_paths.operator_runtime_console_latest
    md_path = runtime_paths.audit_dir / "operator_runtime_console_001.md"

    with (
        patch.object(run_operator_runtime_console, "_PATHS", runtime_paths),
        patch.object(run_operator_runtime_console, "OUT_PATH", out_path),
        patch.object(run_operator_runtime_console, "MD_PATH", md_path),
    ):
        run_operator_runtime_console.main()

    assert out_path.exists()
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["final_posture"] in ("BLOCKED", "NOT_COMPUTABLE", "PASS")
    assert payload["authority_granted"] is False
    assert payload["projection_only"] is True


def test_runtime_console_path_in_config() -> None:
    """RuntimePaths must expose the operator_runtime_console_latest property."""
    from core.config import RuntimePaths

    paths = RuntimePaths(contracts_dir=Path("contracts"), out_dir=Path("out"))
    assert paths.operator_runtime_console_latest == Path(
        "out/audit/operator_runtime_console_001.latest.json"
    )
