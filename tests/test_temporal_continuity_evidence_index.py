from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from core.temporal_continuity_evidence_index import (
    build_temporal_continuity_evidence_index,
    write_temporal_continuity_evidence_index,
)
from scripts import run_temporal_continuity_evidence_index


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _seed_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_p72(
    root: Path,
    *,
    degraded_inputs: list[str] | None = None,
    blockers: list[str] | None = None,
    drift_flags: list[str] | None = None,
    semantic_overlap_flags: list[str] | None = None,
    missing_inputs: list[str] | None = None,
    continuity_group_statuses: list[dict[str, object]] | None = None,
) -> None:
    p72_path = root / "out" / "temporal_continuity_binder_readiness_audit" / "latest.json"
    groups = continuity_group_statuses if continuity_group_statuses is not None else [
        {
            "group_id": "archive_chain",
            "status": "DEGRADED",
            "observed_paths": ["out/audit/archive_ready.json"],
            "missing_paths": [],
        },
        {
            "group_id": "temporal_coherence_chain",
            "status": "PARTIAL",
            "observed_paths": ["scripts/run_temporal_coherence_chain.py"],
            "missing_paths": ["out/projections/missing_coherence.json"],
        },
    ]
    _write_json(
        p72_path,
        {
            "artifact_type": "TemporalContinuityBinderReadinessAudit.v1",
            "canonical_status": "ADVISORY_ONLY",
            "audit_only": True,
            "projection_only": True,
            "readiness_status": "READY_WITH_DEGRADED_EVIDENCE",
            "recommended_next_lane": "P73_TEMPORAL_CONTINUITY_EVIDENCE_INDEX",
            "continuity_group_statuses": groups,
            "missing_or_not_computable_inputs": missing_inputs
            if missing_inputs is not None
            else ["out/projections/missing_coherence.json"],
            "degraded_inputs": degraded_inputs
            if degraded_inputs is not None
            else ["archive_chain:degraded:out/audit/archive_ready.json:ARCHIVE_DEGRADED"],
            "blockers": blockers
            if blockers is not None
            else [
                "temporal_coherence_chain:missing:out/projections/missing_coherence.json",
                "archive_chain:degraded:out/audit/archive_ready.json:ARCHIVE_DEGRADED",
            ],
            "drift_flags": drift_flags if drift_flags is not None else ["GROUP_ARCHIVE_CHAIN_DEGRADED"],
            "semantic_overlap_flags": semantic_overlap_flags
            if semantic_overlap_flags is not None
            else [
                "SEMANTIC_OVERLAP_LATEST_JSON:out/audit/archive_ready.json|out/projections/missing_coherence.json"
            ],
        },
    )


# 1. Missing P72 source returns NOT_COMPUTABLE

def test_missing_p72_source_returns_not_computable(tmp_path: Path) -> None:
    packet = build_temporal_continuity_evidence_index(repo_root=tmp_path)
    assert packet["evidence_index_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P72_READINESS_AUDIT_REGENERATION"


# 2. Malformed P72 source returns NOT_COMPUTABLE

def test_malformed_p72_source_returns_not_computable(tmp_path: Path) -> None:
    p72 = tmp_path / "out" / "temporal_continuity_binder_readiness_audit" / "latest.json"
    p72.parent.mkdir(parents=True, exist_ok=True)
    p72.write_text("{ bad json", encoding="utf-8")
    packet = build_temporal_continuity_evidence_index(repo_root=tmp_path)
    assert packet["evidence_index_status"] == "NOT_COMPUTABLE"
    assert packet["source_readiness_audit_hash"] == "NOT_COMPUTABLE"


# 3. Missing paths are indexed as observed=false/readable=false

def test_missing_paths_indexed_observed_false_readable_false(tmp_path: Path) -> None:
    _seed_p72(tmp_path)
    _seed_file(tmp_path / "out" / "audit" / "archive_ready.json", '{"ok":true}\n')
    _seed_file(tmp_path / "scripts" / "run_temporal_coherence_chain.py", "print('ok')\n")

    packet = build_temporal_continuity_evidence_index(repo_root=tmp_path)
    entry = next(
        (
            item
            for item in packet["evidence_items"]
            if item["path"] == "out/projections/missing_coherence.json"
            and item["evidence_role"] == "missing_path"
        ),
        None,
    )
    assert entry is not None
    assert entry["observed"] is False
    assert entry["readable"] is False


# 4. Existing readable JSON paths are indexed with SHA256 hash

def test_existing_readable_json_paths_have_sha256(tmp_path: Path) -> None:
    _seed_p72(tmp_path)
    payload = '{"ok":true}\n'
    target = tmp_path / "out" / "audit" / "archive_ready.json"
    _seed_file(target, payload)
    _seed_file(tmp_path / "scripts" / "run_temporal_coherence_chain.py", "print('ok')\n")

    packet = build_temporal_continuity_evidence_index(repo_root=tmp_path)
    entry = next(item for item in packet["evidence_items"] if item["path"] == "out/audit/archive_ready.json")
    assert entry["evidence_hash"] == hashlib.sha256(payload.encode("utf-8")).hexdigest()


# 5. Malformed JSON paths are indexed as malformed_json=true

def test_malformed_json_path_marked_true(tmp_path: Path) -> None:
    _seed_p72(
        tmp_path,
        continuity_group_statuses=[
            {
                "group_id": "archive_chain",
                "status": "DEGRADED",
                "observed_paths": ["out/audit/bad.json"],
                "missing_paths": [],
            }
        ],
        degraded_inputs=[],
        blockers=[],
        missing_inputs=[],
        semantic_overlap_flags=[],
    )
    _seed_file(tmp_path / "out" / "audit" / "bad.json", "{not_json}")

    packet = build_temporal_continuity_evidence_index(repo_root=tmp_path)
    entry = next(item for item in packet["evidence_items"] if item["path"] == "out/audit/bad.json")
    assert entry["malformed_json"] is True
    assert "out/audit/bad.json" in packet["unreadable_evidence_paths"]


# 6-9 preserved inherited sets

def test_degraded_inputs_preserved_exactly(tmp_path: Path) -> None:
    marker = "archive_chain:degraded:out/audit/archive_ready.json:ARCHIVE_DEGRADED"
    _seed_p72(tmp_path, degraded_inputs=[marker], blockers=[marker], missing_inputs=[])
    _seed_file(tmp_path / "out" / "audit" / "archive_ready.json", '{"ok":true}\n')
    _seed_file(tmp_path / "scripts" / "run_temporal_coherence_chain.py", "print('ok')\n")

    packet = build_temporal_continuity_evidence_index(repo_root=tmp_path)
    assert packet["degraded_evidence_inputs"] == [marker]


def test_inherited_blockers_preserved_exactly(tmp_path: Path) -> None:
    marker = "temporal_coherence_chain:missing:out/projections/missing_coherence.json"
    _seed_p72(tmp_path, blockers=[marker])
    _seed_file(tmp_path / "out" / "audit" / "archive_ready.json", '{"ok":true}\n')
    _seed_file(tmp_path / "scripts" / "run_temporal_coherence_chain.py", "print('ok')\n")

    packet = build_temporal_continuity_evidence_index(repo_root=tmp_path)
    assert packet["inherited_blockers"] == [marker]


def test_drift_flags_preserved_exactly(tmp_path: Path) -> None:
    marker = "GROUP_TEMPORAL_COHERENCE_CHAIN_PARTIAL"
    _seed_p72(tmp_path, drift_flags=[marker])
    _seed_file(tmp_path / "out" / "audit" / "archive_ready.json", '{"ok":true}\n')
    _seed_file(tmp_path / "scripts" / "run_temporal_coherence_chain.py", "print('ok')\n")

    packet = build_temporal_continuity_evidence_index(repo_root=tmp_path)
    assert packet["inherited_drift_flags"] == [marker]


def test_semantic_overlap_flags_preserved_exactly(tmp_path: Path) -> None:
    marker = "SEMANTIC_OVERLAP_LATEST_JSON:out/audit/archive_ready.json|out/projections/missing_coherence.json"
    _seed_p72(tmp_path, semantic_overlap_flags=[marker])
    _seed_file(tmp_path / "out" / "audit" / "archive_ready.json", '{"ok":true}\n')
    _seed_file(tmp_path / "scripts" / "run_temporal_coherence_chain.py", "print('ok')\n")

    packet = build_temporal_continuity_evidence_index(repo_root=tmp_path)
    assert packet["semantic_overlap_flags"] == [marker]


# 10-11 deterministic dedupe + ordering

def test_evidence_paths_deduplicated_deterministically(tmp_path: Path) -> None:
    _seed_p72(
        tmp_path,
        missing_inputs=[
            "out/projections/missing_coherence.json",
            "out/projections/missing_coherence.json",
        ],
        blockers=[
            "temporal_coherence_chain:missing:out/projections/missing_coherence.json",
            "temporal_coherence_chain:missing:out/projections/missing_coherence.json",
        ],
    )
    _seed_file(tmp_path / "out" / "audit" / "archive_ready.json", '{"ok":true}\n')
    _seed_file(tmp_path / "scripts" / "run_temporal_coherence_chain.py", "print('ok')\n")

    first = build_temporal_continuity_evidence_index(repo_root=tmp_path)
    second = build_temporal_continuity_evidence_index(repo_root=tmp_path)
    assert first["missing_evidence_paths"] == ["out/projections/missing_coherence.json"]
    assert first["missing_evidence_paths"] == second["missing_evidence_paths"]


def test_evidence_items_sorted_deterministically(tmp_path: Path) -> None:
    _seed_p72(tmp_path)
    _seed_file(tmp_path / "out" / "audit" / "archive_ready.json", '{"ok":true}\n')
    _seed_file(tmp_path / "scripts" / "run_temporal_coherence_chain.py", "print('ok')\n")

    packet = build_temporal_continuity_evidence_index(repo_root=tmp_path)
    ordering = [(i["path"], i["group_id"], i["evidence_role"]) for i in packet["evidence_items"]]
    assert ordering == sorted(ordering, key=lambda t: (t[0], t[1], t[2]))


# 12. group_id inference

def test_group_id_inference_from_continuity_groups(tmp_path: Path) -> None:
    _seed_p72(tmp_path)
    _seed_file(tmp_path / "out" / "audit" / "archive_ready.json", '{"ok":true}\n')
    _seed_file(tmp_path / "scripts" / "run_temporal_coherence_chain.py", "print('ok')\n")

    packet = build_temporal_continuity_evidence_index(repo_root=tmp_path)
    archive_entry = next(item for item in packet["evidence_items"] if item["path"] == "out/audit/archive_ready.json")
    assert archive_entry["group_id"] == "archive_chain"


# 13. group summary counts

def test_group_evidence_summary_counts(tmp_path: Path) -> None:
    _seed_p72(
        tmp_path,
        continuity_group_statuses=[
            {
                "group_id": "archive_chain",
                "status": "DEGRADED",
                "observed_paths": ["out/audit/archive_ready.json"],
                "missing_paths": ["out/audit/archive_missing.json"],
            }
        ],
        degraded_inputs=["archive_chain:degraded:out/audit/archive_ready.json:ARCHIVE_DEGRADED"],
        blockers=["archive_chain:missing:out/audit/archive_missing.json"],
        missing_inputs=["out/audit/archive_missing.json"],
        semantic_overlap_flags=[],
    )
    _seed_file(tmp_path / "out" / "audit" / "archive_ready.json", '{"ok":true}\n')

    packet = build_temporal_continuity_evidence_index(repo_root=tmp_path)
    summary = packet["group_evidence_summary"][0]
    assert summary["group_id"] == "archive_chain"
    assert summary["degraded_count"] == 1
    assert summary["missing_count"] == 1


# 14-16 next-lane logic

def test_missing_evidence_status_recommends_restoration_plan(tmp_path: Path) -> None:
    _seed_p72(tmp_path)
    _seed_file(tmp_path / "out" / "audit" / "archive_ready.json", '{"ok":true}\n')
    _seed_file(tmp_path / "scripts" / "run_temporal_coherence_chain.py", "print('ok')\n")

    packet = build_temporal_continuity_evidence_index(repo_root=tmp_path)
    assert packet["evidence_index_status"] == "MISSING_EVIDENCE_INDEXED"
    assert packet["recommended_next_lane"] == "P74_TEMPORAL_CONTINUITY_MISSING_EVIDENCE_RESTORATION_PLAN"


def test_degraded_evidence_status_recommends_repair_plan(tmp_path: Path) -> None:
    _seed_p72(
        tmp_path,
        continuity_group_statuses=[
            {
                "group_id": "archive_chain",
                "status": "DEGRADED",
                "observed_paths": ["out/audit/archive_ready.json"],
                "missing_paths": [],
            }
        ],
        missing_inputs=[],
        blockers=[],
        semantic_overlap_flags=[],
    )
    _seed_file(tmp_path / "out" / "audit" / "archive_ready.json", '{"ok":true}\n')

    packet = build_temporal_continuity_evidence_index(repo_root=tmp_path)
    assert packet["evidence_index_status"] == "DEGRADED_EVIDENCE_INDEXED"
    assert packet["recommended_next_lane"] == "P74_TEMPORAL_CONTINUITY_DEGRADED_EVIDENCE_REPAIR_PLAN"


def test_evidence_ready_recommends_spine_planning_gate(tmp_path: Path) -> None:
    _seed_p72(
        tmp_path,
        continuity_group_statuses=[
            {
                "group_id": "archive_chain",
                "status": "READY",
                "observed_paths": ["out/audit/archive_ready.json"],
                "missing_paths": [],
            }
        ],
        degraded_inputs=[],
        missing_inputs=[],
        blockers=[],
        semantic_overlap_flags=[],
    )
    _seed_file(tmp_path / "out" / "audit" / "archive_ready.json", '{"ok":true}\n')

    packet = build_temporal_continuity_evidence_index(repo_root=tmp_path)
    assert packet["evidence_index_status"] == "EVIDENCE_READY"
    assert packet["recommended_next_lane"] == "P74_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE"


# 17. Authority fields schema-locked / denied

def test_schema_locks_authority_fields_false() -> None:
    schema = json.loads(
        Path("contracts/canon/temporal_continuity_evidence_index.v1.schema.json").read_text(
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
        "evidence_generation_authority",
        "spine_implementation_authority",
    ):
        assert schema["properties"][field]["const"] is False


# 18. Packet hash deterministic

def test_packet_hash_is_deterministic(tmp_path: Path) -> None:
    _seed_p72(tmp_path)
    _seed_file(tmp_path / "out" / "audit" / "archive_ready.json", '{"ok":true}\n')
    _seed_file(tmp_path / "scripts" / "run_temporal_coherence_chain.py", "print('ok')\n")

    first = build_temporal_continuity_evidence_index(repo_root=tmp_path)
    second = build_temporal_continuity_evidence_index(repo_root=tmp_path)
    assert first["packet_hash"] == second["packet_hash"]


# 19. Writer emits canonical JSON with final newline

def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_p72(tmp_path)
    _seed_file(tmp_path / "out" / "audit" / "archive_ready.json", '{"ok":true}\n')
    _seed_file(tmp_path / "scripts" / "run_temporal_coherence_chain.py", "print('ok')\n")

    packet = build_temporal_continuity_evidence_index(repo_root=tmp_path)
    out_path = tmp_path / "out" / "temporal_continuity_evidence_index" / "latest.json"
    write_temporal_continuity_evidence_index(out_path, packet)
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


# 20. Runner writes expected path

def test_runner_writes_expected_output_path(tmp_path: Path) -> None:
    _seed_p72(tmp_path)
    _seed_file(tmp_path / "out" / "audit" / "archive_ready.json", '{"ok":true}\n')
    _seed_file(tmp_path / "scripts" / "run_temporal_coherence_chain.py", "print('ok')\n")

    out_path = tmp_path / "out" / "temporal_continuity_evidence_index" / "latest.json"
    first = run_temporal_continuity_evidence_index.run(repo_root=tmp_path, out_path=out_path)
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_evidence_index.run(repo_root=tmp_path, out_path=out_path)
    second_text = out_path.read_text(encoding="utf-8")
    assert first["packet_hash"] == second["packet_hash"]
    assert first_text == second_text


# 21. Artifact registry classifies output as DERIVED_OPTIONAL

def test_artifact_registry_classifies_as_derived_optional() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS  # type: ignore[attr-defined]

    assert "out/temporal_continuity_evidence_index/latest.json" in _DERIVED_OPTIONAL_ARTIFACTS


@pytest.mark.parametrize(
    "field",
    [
        "production_activation",
        "canon_promotion",
        "forecast_influence",
        "scheduler_mutation",
        "runtime_authority",
        "repair_authority",
        "evidence_generation_authority",
        "spine_implementation_authority",
    ],
)
def test_governance_locks_false_in_packet(tmp_path: Path, field: str) -> None:
    _seed_p72(tmp_path)
    _seed_file(tmp_path / "out" / "audit" / "archive_ready.json", '{"ok":true}\n')
    _seed_file(tmp_path / "scripts" / "run_temporal_coherence_chain.py", "print('ok')\n")

    packet = build_temporal_continuity_evidence_index(repo_root=tmp_path)
    assert packet[field] is False
