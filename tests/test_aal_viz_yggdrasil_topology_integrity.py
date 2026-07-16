from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from core.aal_viz_temporal_diff import AUTHORITY as TEMPORAL_AUTHORITY
from core.aal_viz_yggdrasil_topology import (
    SOURCE_KEYS,
    bind_yggdrasil_topology,
    build_yggdrasil_topology,
)
from core.aal_viz_yggdrasil_topology_integrity import (
    YggdrasilTopologyIntegrityError,
    evaluate_yggdrasil_topology_integrity,
    sha256_json,
    validate_yggdrasil_topology_integrity,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = (
    ROOT
    / "contracts/canon/aal_viz_yggdrasil_topology_integrity.v1.schema.json"
)
SOURCE_PATHS = {key: f"out/{key}.json" for key in SOURCE_KEYS}


def _topology() -> dict:  # type: ignore[type-arg]
    sources = {key: None for key in SOURCE_KEYS}
    sources["yggdrasil"] = {
        "rune_to_pipelines": {
            "RUNE.PIPELINE.VALIDATE": ["example"],
            "RUNE.UNBOUND": [],
        },
        "pipeline_to_route": {"example": "example.route.json"},
        "unbound_runes": ["RUNE.UNBOUND"],
    }
    artifact = build_yggdrasil_topology(
        sources,
        SOURCE_PATHS,
        {key: ("a" * 64 if sources[key] else None) for key in SOURCE_KEYS},
        generated_at="2026-07-15T00:00:00Z",
    )
    return bind_yggdrasil_topology(
        artifact,
        "b" * 64,
        temporal_diff=None,
        temporal_source_path="out/diff.json",
        temporal_content_sha256=None,
    )


def _temporal(current_id: str, *, status: str = "AVAILABLE") -> dict:  # type: ignore[type-arg]
    entries = [
        {
            "id": "entry:removed",
            "operation": "REMOVED",
            "category": "TOPOLOGY_EDGE",
            "entity_id": "edge:old",
            "impact": "NEUTRAL",
            "provenance": "OBSERVED",
        },
        {
            "id": "entry:weakened",
            "operation": "CHANGED",
            "category": "VALIDATOR_STATE",
            "entity_id": "contract:example",
            "impact": "WEAKENED",
            "provenance": "OBSERVED",
        },
    ]
    artifact = {
        "schema_version": "AALViz.TemporalDiff.v1",
        "comparison_status": status,
        "current_generation": {"generation_id": current_id},
        "authority": dict(TEMPORAL_AUTHORITY),
        "entries": entries,
    }
    artifact["canonical_hash"] = sha256_json(artifact)
    return artifact


def _evaluate(
    topology: dict | None = None, temporal: dict | None = None  # type: ignore[type-arg]
):  # type: ignore[no-untyped-def]
    return evaluate_yggdrasil_topology_integrity(
        _topology() if topology is None else topology,
        temporal,
        topology_path="out/topology.json",
        temporal_diff_path="out/diff.json",
        topology_content_sha256="c" * 64,
        temporal_diff_content_sha256="d" * 64 if temporal is not None else None,
        generated_at="2026-07-15T00:00:00Z",
    )


def test_evaluator_is_deterministic_and_reports_current_integrity() -> None:
    first = _evaluate()
    second = _evaluate()
    assert first == second
    assert first["status"] == "PARTIAL"
    types = {finding["finding_type"] for finding in first["payload"]["findings"]}
    assert {"MISSING_EVIDENCE", "SECTION_NOT_COMPUTABLE", "UNRESOLVED_ENTITY"} <= types
    validate_yggdrasil_topology_integrity(first, SCHEMA, topology=_topology())


def test_matched_temporal_entries_map_to_removal_and_weakening() -> None:
    topology = _topology()
    temporal = _temporal(topology["generation"]["operator_platform_generation_id"])
    artifact = _evaluate(topology, temporal)
    types = [finding["finding_type"] for finding in artifact["payload"]["findings"]]
    assert "TEMPORAL_REMOVAL" in types
    assert "TEMPORAL_WEAKENING" in types
    assert "GENERATION_MISMATCH" not in types
    validate_yggdrasil_topology_integrity(artifact, SCHEMA, topology=topology)


def test_generation_mismatch_suppresses_temporal_conclusions() -> None:
    artifact = _evaluate(_topology(), _temporal("e" * 64))
    types = {finding["finding_type"] for finding in artifact["payload"]["findings"]}
    assert "GENERATION_MISMATCH" in types
    assert not types.intersection({"TEMPORAL_REMOVAL", "TEMPORAL_WEAKENING"})


def test_missing_topology_is_not_computable() -> None:
    artifact = evaluate_yggdrasil_topology_integrity(
        None,
        None,
        topology_path="out/topology.json",
        temporal_diff_path="out/diff.json",
        topology_content_sha256=None,
        temporal_diff_content_sha256=None,
        generated_at="2026-07-15T00:00:00Z",
    )
    assert artifact["status"] == "NOT_COMPUTABLE"
    assert artifact["payload"] is None
    validate_yggdrasil_topology_integrity(artifact, SCHEMA)


def test_malformed_inputs_paths_and_authority_fail_closed() -> None:
    topology = _topology()
    tampered = copy.deepcopy(topology)
    tampered["authority"]["runtime_mutation_allowed"] = True
    with pytest.raises(YggdrasilTopologyIntegrityError, match="authority"):
        _evaluate(tampered)
    with pytest.raises(YggdrasilTopologyIntegrityError, match="repository-relative"):
        evaluate_yggdrasil_topology_integrity(
            topology,
            None,
            topology_path="/tmp/topology.json",
            temporal_diff_path="out/diff.json",
            topology_content_sha256="a" * 64,
            temporal_diff_content_sha256=None,
            generated_at="2026-07-15T00:00:00Z",
        )


def test_output_validator_rejects_tampering() -> None:
    artifact = _evaluate()
    artifact["canonical_hash"] = "0" * 64
    with pytest.raises(YggdrasilTopologyIntegrityError, match="canonical hash"):
        validate_yggdrasil_topology_integrity(artifact, SCHEMA, topology=_topology())


def test_operator_runner_uses_explicit_inputs_and_fixed_epoch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    import scripts.operator.run_yggdrasil_topology_integrity as runner

    topology_path = tmp_path / "topology.json"
    topology_path.write_text(json.dumps(_topology()), encoding="utf-8")
    output = tmp_path / "integrity.json"
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    monkeypatch.setattr(runner, "OUTPUT_PATH", output)
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1784073600")
    assert runner.main(["--topology", "topology.json"]) == 0
    artifact = json.loads(output.read_text(encoding="utf-8"))
    assert artifact["generation"]["generated_at"] == "2026-07-15T00:00:00Z"
    assert artifact["generation"]["temporal_diff_generation_id"] is None


def test_operator_runner_rejects_absolute_inputs() -> None:
    import scripts.operator.run_yggdrasil_topology_integrity as runner

    assert runner.main(["--topology", "/tmp/topology.json"]) == 1


def test_operator_runner_rejects_self_hashed_schema_invalid_temporal_diff(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    import scripts.operator.run_yggdrasil_topology_integrity as runner

    (tmp_path / "topology.json").write_text(
        json.dumps(_topology()), encoding="utf-8"
    )
    temporal = {
        "schema_version": "AALViz.TemporalDiff.v1",
        "authority": dict(TEMPORAL_AUTHORITY),
        "current_generation": {"generation_id": "b" * 64},
        "entries": [
            {"id": "entry:removed", "operation": "REMOVED"}
        ],
    }
    temporal["canonical_hash"] = sha256_json(temporal)
    (tmp_path / "temporal.json").write_text(
        json.dumps(temporal), encoding="utf-8"
    )
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    monkeypatch.setattr(runner, "OUTPUT_PATH", tmp_path / "integrity.json")
    assert runner.main(
        ["--topology", "topology.json", "--temporal-diff", "temporal.json"]
    ) == 1
    assert not (tmp_path / "integrity.json").exists()
