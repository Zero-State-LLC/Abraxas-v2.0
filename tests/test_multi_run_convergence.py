from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from core.multi_run_convergence import (
    BLOCKED,
    NOT_COMPUTABLE,
    build_multi_run_convergence_markdown,
    build_multi_run_convergence_packet,
    write_multi_run_convergence_packet,
)
from scripts.research import run_multi_run_convergence


def _payload(
    *,
    run_id: str,
    timestamp: str,
    topology: int,
    lineage: int,
    drift: int,
    queue: int,
    transport: int,
    replay: str = "NO_CHANGE",
    blockers: list[str] | None = None,
    final_status: str = "ADVISORY_ONLY",
    authority_granted: bool = False,
) -> dict[str, object]:
    return {
        "schema": "SyntheticRun.v1",
        "run_id": run_id,
        "packet_id": f"packet:{run_id}",
        "projection_timestamp": timestamp,
        "final_status": final_status,
        "topology_change_count": topology,
        "lineage_shift_count": lineage,
        "drift_event_count": drift,
        "drift_acceleration_status": "NO_ACCELERATION",
        "replay_equivalence_change_status": replay,
        "queue_delta_count": queue,
        "transport_delta_count": transport,
        "remaining_blockers": blockers or [],
        "advisory_flags": ["advisory_only"],
        "execution_authority": False,
        "authority_granted": authority_granted,
        "mutation_allowed": False,
        "promotion_allowed": False,
        "auto_execute": False,
        "auto_approve": False,
        "command_channel": False,
        "bidirectional_control": False,
        "inference_authority": False,
    }


def _write_artifacts(tmp_path: Path, payloads: list[dict[str, object]]) -> list[str]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    paths: list[str] = []
    for index, payload in enumerate(payloads):
        path = tmp_path / f"run_{index:03d}.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        paths.append(path.as_posix())
    return paths


def test_stable_run_observation_ordering(tmp_path: Path) -> None:
    payloads = [
        _payload(
            run_id="run-c",
            timestamp="t:003",
            topology=1,
            lineage=1,
            drift=1,
            queue=1,
            transport=1,
        ),
        _payload(
            run_id="run-a",
            timestamp="t:001",
            topology=1,
            lineage=1,
            drift=1,
            queue=1,
            transport=1,
        ),
        _payload(
            run_id="run-b",
            timestamp="t:002",
            topology=1,
            lineage=1,
            drift=1,
            queue=1,
            transport=1,
        ),
    ]
    packet = build_multi_run_convergence_packet(
        source_artifacts=_write_artifacts(tmp_path, payloads)
    )
    assert [obs["run_id"] for obs in packet["run_observations"]] == [
        "run-a",
        "run-b",
        "run-c",
    ]


def test_stable_packet_hash_and_markdown(tmp_path: Path) -> None:
    paths = _write_artifacts(
        tmp_path,
        [
            _payload(
                run_id="run-1",
                timestamp="t:001",
                topology=0,
                lineage=0,
                drift=0,
                queue=0,
                transport=0,
            ),
            _payload(
                run_id="run-2",
                timestamp="t:002",
                topology=0,
                lineage=0,
                drift=0,
                queue=0,
                transport=0,
            ),
        ],
    )
    packet_a = build_multi_run_convergence_packet(source_artifacts=paths)
    packet_b = build_multi_run_convergence_packet(source_artifacts=paths)
    markdown_a = build_multi_run_convergence_markdown(packet_a)
    markdown_b = build_multi_run_convergence_markdown(packet_b)
    assert packet_a["packet_hash"] == packet_b["packet_hash"]
    assert markdown_a == markdown_b


def test_insufficient_run_not_computable_behavior(tmp_path: Path) -> None:
    paths = _write_artifacts(
        tmp_path,
        [
            _payload(
                run_id="run-1",
                timestamp="t:001",
                topology=0,
                lineage=0,
                drift=0,
                queue=0,
                transport=0,
            )
        ],
    )
    packet = build_multi_run_convergence_packet(source_artifacts=paths)
    assert packet["run_observation_count"] == 1
    assert packet["regime_classification"] == NOT_COMPUTABLE
    assert packet["multi_run_convergence_status"] == NOT_COMPUTABLE
    assert "insufficient_run_observations" in packet["remaining_blockers"]


def test_missing_artifact_fail_closed_behavior(tmp_path: Path) -> None:
    missing_path = (tmp_path / "missing.json").as_posix()
    packet = build_multi_run_convergence_packet(source_artifacts=[missing_path])
    observation = packet["run_observations"][0]
    assert observation["observation_status"] == NOT_COMPUTABLE
    assert packet["regime_classification"] == NOT_COMPUTABLE
    assert any(
        blocker.startswith("missing_artifact:") for blocker in observation["remaining_blockers"]
    )


def test_corrupt_artifact_fail_closed_behavior(tmp_path: Path) -> None:
    valid = _write_artifacts(
        tmp_path,
        [
            _payload(
                run_id="run-1",
                timestamp="t:001",
                topology=1,
                lineage=1,
                drift=1,
                queue=1,
                transport=1,
            )
        ],
    )[0]
    corrupt_path = tmp_path / "corrupt.json"
    corrupt_path.write_text("{not json", encoding="utf-8")
    packet = build_multi_run_convergence_packet(
        source_artifacts=[valid, corrupt_path.as_posix()]
    )
    assert packet["regime_classification"] == BLOCKED
    assert packet["multi_run_convergence_status"] == BLOCKED
    assert any(
        blocker.startswith("corrupt_artifact:") for blocker in packet["remaining_blockers"]
    )


def test_authority_boundary_violation_blocked_behavior(tmp_path: Path) -> None:
    paths = _write_artifacts(
        tmp_path,
        [
            _payload(
                run_id="run-1",
                timestamp="t:001",
                topology=0,
                lineage=0,
                drift=0,
                queue=0,
                transport=0,
            ),
            _payload(
                run_id="run-2",
                timestamp="t:002",
                topology=0,
                lineage=0,
                drift=0,
                queue=0,
                transport=0,
                authority_granted=True,
            ),
        ],
    )
    packet = build_multi_run_convergence_packet(source_artifacts=paths)
    assert packet["regime_classification"] == BLOCKED
    assert any(
        blocker.startswith("authority_boundary_violation:")
        for blocker in packet["remaining_blockers"]
    )


def test_regime_stable_classification(tmp_path: Path) -> None:
    paths = _write_artifacts(
        tmp_path,
        [
            _payload(
                run_id="run-1",
                timestamp="t:001",
                topology=0,
                lineage=0,
                drift=0,
                queue=0,
                transport=0,
            ),
            _payload(
                run_id="run-2",
                timestamp="t:002",
                topology=0,
                lineage=0,
                drift=0,
                queue=0,
                transport=0,
            ),
            _payload(
                run_id="run-3",
                timestamp="t:003",
                topology=0,
                lineage=0,
                drift=0,
                queue=0,
                transport=0,
            ),
        ],
    )
    packet = build_multi_run_convergence_packet(source_artifacts=paths)
    assert packet["regime_classification"] == "STABLE"


def test_regime_converging_classification(tmp_path: Path) -> None:
    paths = _write_artifacts(
        tmp_path,
        [
            _payload(
                run_id="run-1",
                timestamp="t:001",
                topology=3,
                lineage=2,
                drift=1,
                queue=1,
                transport=1,
            ),
            _payload(
                run_id="run-2",
                timestamp="t:002",
                topology=2,
                lineage=1,
                drift=1,
                queue=1,
                transport=0,
            ),
            _payload(
                run_id="run-3",
                timestamp="t:003",
                topology=1,
                lineage=0,
                drift=0,
                queue=0,
                transport=0,
            ),
        ],
    )
    packet = build_multi_run_convergence_packet(source_artifacts=paths)
    assert packet["regime_classification"] == "CONVERGING"


def test_regime_diverging_classification(tmp_path: Path) -> None:
    paths = _write_artifacts(
        tmp_path,
        [
            _payload(
                run_id="run-1",
                timestamp="t:001",
                topology=0,
                lineage=0,
                drift=0,
                queue=0,
                transport=0,
            ),
            _payload(
                run_id="run-2",
                timestamp="t:002",
                topology=1,
                lineage=1,
                drift=1,
                queue=1,
                transport=1,
            ),
            _payload(
                run_id="run-3",
                timestamp="t:003",
                topology=2,
                lineage=2,
                drift=2,
                queue=2,
                transport=2,
            ),
        ],
    )
    packet = build_multi_run_convergence_packet(source_artifacts=paths)
    assert packet["regime_classification"] == "DIVERGING"


def test_regime_volatile_classification(tmp_path: Path) -> None:
    paths = _write_artifacts(
        tmp_path,
        [
            _payload(
                run_id="run-1",
                timestamp="t:001",
                topology=1,
                lineage=1,
                drift=1,
                queue=1,
                transport=1,
            ),
            _payload(
                run_id="run-2",
                timestamp="t:002",
                topology=3,
                lineage=3,
                drift=1,
                queue=1,
                transport=1,
            ),
            _payload(
                run_id="run-3",
                timestamp="t:003",
                topology=1,
                lineage=1,
                drift=1,
                queue=1,
                transport=1,
            ),
        ],
    )
    packet = build_multi_run_convergence_packet(source_artifacts=paths)
    assert packet["regime_classification"] == "VOLATILE"


def test_regime_degraded_classification(tmp_path: Path) -> None:
    paths = _write_artifacts(
        tmp_path,
        [
            _payload(
                run_id="run-1",
                timestamp="t:001",
                topology=0,
                lineage=0,
                drift=0,
                queue=0,
                transport=0,
                blockers=[],
            ),
            _payload(
                run_id="run-2",
                timestamp="t:002",
                topology=0,
                lineage=0,
                drift=0,
                queue=0,
                transport=0,
                blockers=["b1"],
            ),
            _payload(
                run_id="run-3",
                timestamp="t:003",
                topology=0,
                lineage=0,
                drift=0,
                queue=0,
                transport=0,
                blockers=["b1", "b2"],
            ),
        ],
    )
    packet = build_multi_run_convergence_packet(source_artifacts=paths)
    assert packet["regime_classification"] == "DEGRADED"


def test_persistence_metrics_and_statuses(tmp_path: Path) -> None:
    paths = _write_artifacts(
        tmp_path,
        [
            _payload(
                run_id="run-1",
                timestamp="t:001",
                topology=0,
                lineage=1,
                drift=0,
                queue=0,
                transport=0,
                replay="NO_CHANGE",
            ),
            _payload(
                run_id="run-2",
                timestamp="t:002",
                topology=1,
                lineage=1,
                drift=0,
                queue=2,
                transport=0,
                replay="SHIFT_DETECTED",
            ),
            _payload(
                run_id="run-3",
                timestamp="t:003",
                topology=1,
                lineage=1,
                drift=1,
                queue=1,
                transport=0,
                replay="NO_CHANGE",
            ),
        ],
    )
    packet = build_multi_run_convergence_packet(source_artifacts=paths)
    assert packet["topology_persistence_ratio"] >= 0.0
    assert packet["drift_persistence_ratio"] >= 0.0
    assert packet["lineage_persistence_ratio"] >= 0.0
    assert packet["replay_stability_status"] in {
        "STABLE",
        "CONVERGING",
        "DIVERGING",
        "VOLATILE",
        NOT_COMPUTABLE,
        BLOCKED,
    }
    assert packet["transport_stability_status"] in {
        "STABLE",
        "CONVERGING",
        "DIVERGING",
        "VOLATILE",
        NOT_COMPUTABLE,
        BLOCKED,
    }
    assert packet["queue_stability_status"] in {
        "STABLE",
        "CONVERGING",
        "DIVERGING",
        "VOLATILE",
        NOT_COMPUTABLE,
        BLOCKED,
    }


def test_invariants_locked_and_no_source_mutation(tmp_path: Path) -> None:
    paths = _write_artifacts(
        tmp_path,
        [
            _payload(
                run_id="run-1",
                timestamp="t:001",
                topology=0,
                lineage=0,
                drift=0,
                queue=0,
                transport=0,
            ),
            _payload(
                run_id="run-2",
                timestamp="t:002",
                topology=0,
                lineage=0,
                drift=0,
                queue=0,
                transport=0,
            ),
        ],
    )
    before = {path: Path(path).read_text(encoding="utf-8") for path in paths}
    packet = build_multi_run_convergence_packet(source_artifacts=paths)
    after = {path: Path(path).read_text(encoding="utf-8") for path in paths}
    assert before == after

    for key, expected in (
        ("advisory_only", True),
        ("analytics_only", True),
        ("detection_only", True),
        ("execution_authority", False),
        ("authority_granted", False),
        ("mutation_allowed", False),
        ("promotion_allowed", False),
        ("auto_execute", False),
        ("auto_approve", False),
        ("command_channel", False),
        ("bidirectional_control", False),
        ("inference_authority", False),
    ):
        assert packet[key] is expected

    for observation in packet["run_observations"]:
        assert observation["advisory_only"] is True
        assert observation["analytics_only"] is True
        assert observation["detection_only"] is True
        assert observation["execution_authority"] is False
        assert observation["authority_granted"] is False
        assert observation["mutation_allowed"] is False
        assert observation["promotion_allowed"] is False
        assert observation["auto_execute"] is False
        assert observation["auto_approve"] is False
        assert observation["command_channel"] is False
        assert observation["bidirectional_control"] is False
        assert observation["inference_authority"] is False

    for summary_key in (
        "topology_persistence_summary",
        "drift_persistence_summary",
        "lineage_persistence_summary",
        "replay_stability_summary",
        "transport_stability_summary",
        "queue_stability_summary",
        "blocker_persistence_summary",
        "regime_classification_summary",
    ):
        summary = packet[summary_key]
        assert summary["advisory_only"] is True
        assert summary["analytics_only"] is True
        assert summary["detection_only"] is True
        assert summary["execution_authority"] is False
        assert summary["authority_granted"] is False
        assert summary["mutation_allowed"] is False
        assert summary["promotion_allowed"] is False
        assert summary["auto_execute"] is False
        assert summary["auto_approve"] is False
        assert summary["command_channel"] is False
        assert summary["bidirectional_control"] is False
        assert summary["inference_authority"] is False


def test_writer_and_run_script_outputs(tmp_path: Path) -> None:
    paths = _write_artifacts(
        tmp_path,
        [
            _payload(
                run_id="run-1",
                timestamp="t:001",
                topology=0,
                lineage=0,
                drift=0,
                queue=0,
                transport=0,
            ),
            _payload(
                run_id="run-2",
                timestamp="t:002",
                topology=0,
                lineage=0,
                drift=0,
                queue=0,
                transport=0,
            ),
        ],
    )
    packet = build_multi_run_convergence_packet(source_artifacts=paths)
    out_path = tmp_path / "multi_run_convergence.json"
    write_multi_run_convergence_packet(out_path, packet)
    assert out_path.read_text(encoding="utf-8").endswith("\n")
    written_payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert written_payload["schema"] == "MultiRunConvergencePacket.v1"
    assert written_payload["packet_id"] == packet["packet_id"]
    assert written_payload["run_observation_count"] == packet["run_observation_count"]

    runtime_paths = run_multi_run_convergence.RuntimePaths(
        contracts_dir=tmp_path / "contracts", out_dir=tmp_path / "out"
    )
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(paths), encoding="utf-8")
    with (
        patch.object(run_multi_run_convergence, "_PATHS", runtime_paths),
        patch.object(
            run_multi_run_convergence,
            "OUT_PATH",
            runtime_paths.multi_run_convergence_latest,
        ),
    ):
        run_multi_run_convergence.main(["--manifest", manifest.as_posix()])

    assert runtime_paths.multi_run_convergence_latest.exists()
    assert runtime_paths.multi_run_convergence_latest.with_suffix(".md").exists()
