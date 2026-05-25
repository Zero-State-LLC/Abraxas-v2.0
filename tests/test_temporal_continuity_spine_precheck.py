from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_spine_precheck import (
    DEFAULT_CONTINUITY_SURFACE_GROUPS,
    RECOMMENDED_BINDER_LANE,
    RECOMMENDED_P69_REPAIR_LANE,
    build_temporal_continuity_spine_precheck,
    write_temporal_continuity_spine_precheck,
)
from scripts import run_temporal_continuity_spine_precheck


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _write_text(path: Path, content: str = "ok\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _payload_for(path: str) -> dict[str, object]:
    if path == "out/canon_resume_state/latest.json":
        return {"artifact_type": "CanonResumeState.v1", "canonical_status": "ADVISORY_ONLY"}
    if "archive_chain_closure_receipt" in path:
        return {"final_status": "CLOSURE_RECEIPT_DEGRADED"}
    if "archive_chain_stability_receipt" in path:
        return {"final_status": "STABILITY_RECEIPT_DEGRADED"}
    if "static_archive_package_stability_receipt" in path:
        return {"final_status": "PACKAGE_STABILITY_RECEIPT_DEGRADED"}
    if "static_archive_package_chain_closure_receipt" in path:
        return {"final_status": "STATIC_ARCHIVE_PACKAGE_CHAIN_CLOSURE_DEGRADED"}
    if "temporal_coherence_chain" in path:
        return {"final_chain_status": "ADVISORY_ONLY"}
    if "coherence_field_operator_surface" in path:
        return {"coherence_field_operator_surface_status": "ADVISORY_ONLY"}
    if "aal_viz_runtime_projection" in path:
        return {"final_status": "ADVISORY_ONLY"}
    if path.endswith(".json"):
        return {"final_status": "PASS", "status": "PASS"}
    return {}


def _seed_repo(
    root: Path,
    *,
    include_resume_state: bool = True,
    drop_paths: tuple[str, ...] = (),
) -> None:
    paths = {
        path
        for group in DEFAULT_CONTINUITY_SURFACE_GROUPS
        for path in group.required_paths
    }
    if include_resume_state:
        paths.add("out/canon_resume_state/latest.json")
    for rel_path in sorted(paths):
        if rel_path in drop_paths:
            continue
        path = root / rel_path
        if rel_path.endswith(".json"):
            _write_json(path, _payload_for(rel_path))
        else:
            _write_text(path)


def test_packet_hash_deterministic(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    first = build_temporal_continuity_spine_precheck(repo_root=tmp_path)
    second = build_temporal_continuity_spine_precheck(repo_root=tmp_path)
    assert first["packet_hash"] == second["packet_hash"]


def test_output_latest_json_has_exactly_one_newline(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    packet = build_temporal_continuity_spine_precheck(repo_root=tmp_path)
    out_path = tmp_path / "out" / "temporal_continuity_spine_precheck" / "latest.json"
    write_temporal_continuity_spine_precheck(out_path, packet)
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


def test_missing_resume_state_is_not_computable_and_recommends_p69(tmp_path: Path) -> None:
    _seed_repo(tmp_path, include_resume_state=False)
    packet = build_temporal_continuity_spine_precheck(repo_root=tmp_path)
    assert packet["source_resume_state_observed"] is False
    assert packet["source_resume_state_hash"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == RECOMMENDED_P69_REPAIR_LANE
    assert all(group["status"] == "NOT_COMPUTABLE" for group in packet["continuity_surface_groups"])


def test_authority_flags_remain_false(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    packet = build_temporal_continuity_spine_precheck(repo_root=tmp_path)
    assert packet["production_activation"] is False
    assert packet["canon_promotion"] is False
    assert packet["forecast_influence"] is False
    assert packet["scheduler_mutation"] is False
    assert packet["runtime_authority"] is False
    assert packet["repair_authority"] is False
    assert packet["spine_implementation_authority"] is False


def test_group_status_computation_is_deterministic(tmp_path: Path) -> None:
    _seed_repo(
        tmp_path,
        drop_paths=("out/projections/cross_run_topology_fusion_001.latest.json",),
    )
    forward = build_temporal_continuity_spine_precheck(
        repo_root=tmp_path,
        surface_groups=DEFAULT_CONTINUITY_SURFACE_GROUPS,
    )
    reverse = build_temporal_continuity_spine_precheck(
        repo_root=tmp_path,
        surface_groups=tuple(reversed(DEFAULT_CONTINUITY_SURFACE_GROUPS)),
    )
    assert forward["continuity_surface_groups"] == reverse["continuity_surface_groups"]
    statuses = {group["group_id"]: group["status"] for group in forward["continuity_surface_groups"]}
    assert statuses["archive_chain"] == "DEGRADED"
    assert statuses["static_archive_package_chain"] == "DEGRADED"
    assert statuses["temporal_coherence_chain"] == "PARTIAL"
    assert statuses["temporal_release_governance"] == "READY"


def test_semantic_overlap_flags_sorted_and_deterministic(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    packet = build_temporal_continuity_spine_precheck(repo_root=tmp_path)
    assert packet["semantic_overlap_flags"] == sorted(packet["semantic_overlap_flags"])
    assert packet["semantic_overlap_flags"] == build_temporal_continuity_spine_precheck(repo_root=tmp_path)["semantic_overlap_flags"]


def test_runner_writes_deterministic_latest_json(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    out_path = tmp_path / "out" / "temporal_continuity_spine_precheck" / "latest.json"
    first = run_temporal_continuity_spine_precheck.run(repo_root=tmp_path, out_path=out_path)
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_spine_precheck.run(repo_root=tmp_path, out_path=out_path)
    second_text = out_path.read_text(encoding="utf-8")
    assert first["packet_hash"] == second["packet_hash"]
    assert first_text == second_text


def test_schema_contains_required_authority_denial_fields() -> None:
    schema = json.loads(
        Path("contracts/canon/temporal_continuity_spine_precheck.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    required = set(schema["required"])
    assert {
        "production_activation",
        "canon_promotion",
        "forecast_influence",
        "scheduler_mutation",
        "runtime_authority",
        "repair_authority",
        "spine_implementation_authority",
    }.issubset(required)


def test_schema_locks_mutation_and_authority_flags_false() -> None:
    schema = json.loads(
        Path("contracts/canon/temporal_continuity_spine_precheck.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    for field in (
        "production_activation",
        "canon_promotion",
        "forecast_influence",
        "scheduler_mutation",
        "runtime_authority",
        "repair_authority",
        "spine_implementation_authority",
    ):
        assert schema["properties"][field]["const"] is False


def test_binder_recommendation_when_all_groups_have_evidence(tmp_path: Path) -> None:
    _seed_repo(
        tmp_path,
        drop_paths=("out/projections/cross_run_topology_fusion_001.latest.json",),
    )
    packet = build_temporal_continuity_spine_precheck(repo_root=tmp_path)
    assert packet["recommended_next_lane"] == RECOMMENDED_BINDER_LANE
