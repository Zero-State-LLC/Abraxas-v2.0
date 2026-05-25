from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.temporal_continuity_binder_readiness_audit import (
    build_temporal_continuity_binder_readiness_audit,
    write_temporal_continuity_binder_readiness_audit,
)
from scripts import run_temporal_continuity_binder_readiness_audit


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _seed_binder_contract(
    root: Path,
    *,
    binder_contract_status: str = "CONTRACT_READY_WITH_DEGRADED_EVIDENCE",
    continuity_groups: list[dict[str, object]] | None = None,
    degraded_inputs: list[str] | None = None,
    missing_or_not_computable_inputs: list[str] | None = None,
    semantic_overlap_flags: list[str] | None = None,
    blockers: list[str] | None = None,
    drift_flags: list[str] | None = None,
) -> None:
    groups = continuity_groups if continuity_groups is not None else [
        {"group_id": "archive_chain", "status": "DEGRADED"},
        {"group_id": "static_archive_package_chain", "status": "DEGRADED"},
        {"group_id": "temporal_coherence_chain", "status": "PARTIAL"},
        {"group_id": "temporal_release_governance", "status": "READY"},
    ]
    _write_json(
        root / "out" / "temporal_continuity_spine_binder_contract" / "latest.json",
        {
            "artifact_type": "TemporalContinuitySpineBinderContract.v1",
            "canonical_status": "ADVISORY_ONLY",
            "audit_only": True,
            "projection_only": True,
            "binder_contract_status": binder_contract_status,
            "continuity_groups": groups,
            "degraded_inputs": degraded_inputs or [
                "archive_chain:degraded:out/audit/x.json:DEGRADED",
            ],
            "missing_or_not_computable_inputs": missing_or_not_computable_inputs or [
                "out/audit/temporal_coherence_chain_001.latest.json",
            ],
            "semantic_overlap_flags": semantic_overlap_flags or [
                "SEMANTIC_OVERLAP_STABILITY_RECEIPT:a|b",
            ],
            "blockers": blockers or [
                "archive_chain:degraded:out/audit/x.json:DEGRADED",
            ],
            "drift_flags": drift_flags or ["GROUP_ARCHIVE_CHAIN_DEGRADED"],
        },
    )


# --- 1. Missing P71 source returns NOT_COMPUTABLE ---

def test_missing_binder_contract_is_not_computable(tmp_path: Path) -> None:
    packet = build_temporal_continuity_binder_readiness_audit(repo_root=tmp_path)
    assert packet["source_binder_contract_observed"] is False
    assert packet["source_binder_contract_hash"] == "NOT_COMPUTABLE"
    assert packet["readiness_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P71_BINDER_CONTRACT_REGENERATION"


# --- 2. Malformed P71 source returns NOT_COMPUTABLE ---

def test_malformed_binder_contract_is_not_computable(tmp_path: Path) -> None:
    p = tmp_path / "out" / "temporal_continuity_spine_binder_contract" / "latest.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("not valid json {{{}}", encoding="utf-8")
    packet = build_temporal_continuity_binder_readiness_audit(repo_root=tmp_path)
    assert packet["readiness_status"] == "NOT_COMPUTABLE"
    assert packet["source_binder_contract_hash"] == "NOT_COMPUTABLE"


# --- 3. P71 BLOCKED returns readiness BLOCKED ---

def test_blocked_binder_contract_returns_blocked(tmp_path: Path) -> None:
    _seed_binder_contract(tmp_path, binder_contract_status="BLOCKED")
    packet = build_temporal_continuity_binder_readiness_audit(repo_root=tmp_path)
    assert packet["readiness_status"] == "BLOCKED"
    assert packet["recommended_next_lane"] == "P71_BINDER_CONTRACT_REPAIR"


# --- 4. CONTRACT_READY_WITH_DEGRADED_EVIDENCE + PARTIAL group recommends P73_TEMPORAL_CONTINUITY_EVIDENCE_INDEX ---

def test_degraded_evidence_with_partial_group_recommends_evidence_index(tmp_path: Path) -> None:
    _seed_binder_contract(
        tmp_path,
        binder_contract_status="CONTRACT_READY_WITH_DEGRADED_EVIDENCE",
        continuity_groups=[
            {"group_id": "archive_chain", "status": "DEGRADED"},
            {"group_id": "temporal_coherence_chain", "status": "PARTIAL"},
        ],
    )
    packet = build_temporal_continuity_binder_readiness_audit(repo_root=tmp_path)
    assert packet["readiness_status"] == "READY_WITH_DEGRADED_EVIDENCE"
    assert packet["recommended_next_lane"] == "P73_TEMPORAL_CONTINUITY_EVIDENCE_INDEX"
    assert "temporal_coherence_chain" in packet["partial_groups"]


# --- 5. CONTRACT_READY_WITH_DEGRADED_EVIDENCE + no partial/not-computable groups recommends repair plan ---

def test_degraded_evidence_no_partial_recommends_repair_plan(tmp_path: Path) -> None:
    _seed_binder_contract(
        tmp_path,
        binder_contract_status="CONTRACT_READY_WITH_DEGRADED_EVIDENCE",
        continuity_groups=[
            {"group_id": "archive_chain", "status": "DEGRADED"},
            {"group_id": "temporal_release_governance", "status": "READY"},
        ],
    )
    packet = build_temporal_continuity_binder_readiness_audit(repo_root=tmp_path)
    assert packet["readiness_status"] == "READY_WITH_DEGRADED_EVIDENCE"
    assert packet["recommended_next_lane"] == "P73_TEMPORAL_CONTINUITY_DEGRADED_EVIDENCE_REPAIR_PLAN"
    assert packet["partial_groups"] == []
    assert packet["not_computable_groups"] == []


# --- 6. CONTRACT_READY + all READY groups recommends spine implementation planning ---

def test_contract_ready_all_ready_recommends_spine_planning(tmp_path: Path) -> None:
    _seed_binder_contract(
        tmp_path,
        binder_contract_status="CONTRACT_READY",
        continuity_groups=[
            {"group_id": "archive_chain", "status": "READY"},
            {"group_id": "temporal_release_governance", "status": "READY"},
        ],
        degraded_inputs=[],
        missing_or_not_computable_inputs=[],
        blockers=[],
    )
    packet = build_temporal_continuity_binder_readiness_audit(repo_root=tmp_path)
    assert packet["readiness_status"] == "READY"
    assert packet["recommended_next_lane"] == "P73_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING"
    assert packet["degraded_groups"] == []
    assert packet["partial_groups"] == []
    assert packet["not_computable_groups"] == []


# --- 7. Degraded inputs are preserved exactly ---

def test_degraded_inputs_preserved_verbatim(tmp_path: Path) -> None:
    marker = "archive_chain:degraded:out/audit/foo.json:FOO_DEGRADED"
    _seed_binder_contract(tmp_path, degraded_inputs=[marker])
    packet = build_temporal_continuity_binder_readiness_audit(repo_root=tmp_path)
    assert marker in packet["degraded_inputs"]


# --- 8. Missing/not-computable inputs are preserved exactly ---

def test_missing_inputs_preserved_verbatim(tmp_path: Path) -> None:
    marker = "out/audit/temporal_coherence_chain_001.latest.json"
    _seed_binder_contract(tmp_path, missing_or_not_computable_inputs=[marker])
    packet = build_temporal_continuity_binder_readiness_audit(repo_root=tmp_path)
    assert marker in packet["missing_or_not_computable_inputs"]


# --- 9. Semantic overlap flags preserve deterministic ordering ---

def test_semantic_overlap_flags_sorted_deterministic(tmp_path: Path) -> None:
    _seed_binder_contract(
        tmp_path,
        semantic_overlap_flags=[
            "SEMANTIC_OVERLAP_STABILITY_RECEIPT:z|a",
            "SEMANTIC_OVERLAP_CLOSURE_RECEIPT:b|a",
        ],
    )
    first = build_temporal_continuity_binder_readiness_audit(repo_root=tmp_path)
    second = build_temporal_continuity_binder_readiness_audit(repo_root=tmp_path)
    assert first["semantic_overlap_flags"] == sorted(first["semantic_overlap_flags"])
    assert first["semantic_overlap_flags"] == second["semantic_overlap_flags"]


# --- 10. Authority escalation fields are schema-denied / const-locked ---

def test_schema_locks_authority_fields_false() -> None:
    schema = json.loads(
        Path(
            "contracts/canon/temporal_continuity_binder_readiness_audit.v1.schema.json"
        ).read_text(encoding="utf-8")
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
        assert schema["properties"][field]["const"] is False, field


def test_schema_contains_required_authority_denial_fields() -> None:
    schema = json.loads(
        Path(
            "contracts/canon/temporal_continuity_binder_readiness_audit.v1.schema.json"
        ).read_text(encoding="utf-8")
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


# --- 11. Packet hash is deterministic ---

def test_packet_hash_deterministic(tmp_path: Path) -> None:
    _seed_binder_contract(tmp_path)
    first = build_temporal_continuity_binder_readiness_audit(repo_root=tmp_path)
    second = build_temporal_continuity_binder_readiness_audit(repo_root=tmp_path)
    assert first["packet_hash"] == second["packet_hash"]


# --- 12. Writer emits canonical JSON with final newline ---

def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_binder_contract(tmp_path)
    packet = build_temporal_continuity_binder_readiness_audit(repo_root=tmp_path)
    out_path = tmp_path / "out" / "temporal_continuity_binder_readiness_audit" / "latest.json"
    write_temporal_continuity_binder_readiness_audit(out_path, packet)
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


# --- 13. Runner writes the expected output path ---

def test_runner_writes_expected_output_path(tmp_path: Path) -> None:
    _seed_binder_contract(tmp_path)
    out_path = tmp_path / "out" / "temporal_continuity_binder_readiness_audit" / "latest.json"
    first = run_temporal_continuity_binder_readiness_audit.run(
        repo_root=tmp_path, out_path=out_path
    )
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_binder_readiness_audit.run(
        repo_root=tmp_path, out_path=out_path
    )
    second_text = out_path.read_text(encoding="utf-8")
    assert first["packet_hash"] == second["packet_hash"]
    assert first_text == second_text


# --- 14. Artifact registry classifies output as DERIVED_OPTIONAL ---

def test_artifact_registry_classifies_as_derived_optional() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS  # type: ignore[attr-defined]

    assert "out/temporal_continuity_binder_readiness_audit/latest.json" in _DERIVED_OPTIONAL_ARTIFACTS


# --- Governance: governance lock fields are all False in built packet ---

@pytest.mark.parametrize(
    "field",
    [
        "production_activation",
        "canon_promotion",
        "forecast_influence",
        "scheduler_mutation",
        "runtime_authority",
        "repair_authority",
        "spine_implementation_authority",
    ],
)
def test_governance_lock_fields_false(tmp_path: Path, field: str) -> None:
    _seed_binder_contract(tmp_path)
    packet = build_temporal_continuity_binder_readiness_audit(repo_root=tmp_path)
    assert packet[field] is False


def test_canonical_status_advisory_only(tmp_path: Path) -> None:
    _seed_binder_contract(tmp_path)
    packet = build_temporal_continuity_binder_readiness_audit(repo_root=tmp_path)
    assert packet["canonical_status"] == "ADVISORY_ONLY"
    assert packet["audit_only"] is True
    assert packet["projection_only"] is True
