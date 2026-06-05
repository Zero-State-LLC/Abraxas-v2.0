from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

from .runtime_handoff_executor import (
    build_runtime_handoff_receipt_set,
    build_sample_manifest_and_config,
    build_source_pull_receipt_set,
)

PATCH_ID = "PATCH-ABX-AUTO-INGEST-005"
SCHEMA_VERSION = "AALVizIngestProjectionPack.v1"
AUTHORITY = "PROJECTION_ONLY"

_REQUIRED_TRUE_KEYS = ("advisory_only", "projection_only", "non_authoritative")
_REQUIRED_FALSE_KEYS = ("forecast_authority", "canon_mutation", "runtime_mutation", "execution_authority")
_AUTHORITY_BADGES = ["DATA", "SHADOW", "FORECAST_CANDIDATE", "PROJECTION_ONLY"]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require_boundary(packet: dict[str, Any], *, schema_version: str) -> None:
    if packet.get("schema_version") != schema_version:
        raise ValueError(f"expected {schema_version}")
    for key in _REQUIRED_TRUE_KEYS:
        if packet.get(key) is not True:
            raise ValueError(f"{schema_version} must set {key}=true")
    for key in _REQUIRED_FALSE_KEYS:
        if packet.get(key) is not False:
            raise ValueError(f"{schema_version} must set {key}=false")


def load_ingest_projection_inputs(
    repo_root: Path | str = Path("."),
) -> dict[str, dict[str, Any]]:
    root = Path(repo_root)
    queue = _load_json(root / "out/ingest/oracle_intake_queue_001.latest.json")
    candidate = _load_json(root / "out/ingest/outcome_binding_candidate_packet_001.latest.json")
    precheck = _load_json(root / "out/ingest/brier_readiness_precheck_001.latest.json")

    manifest, adapter_config = build_sample_manifest_and_config()
    source_pull_receipts = build_source_pull_receipt_set(manifest, adapter_config)
    runtime_handoff_receipts = build_runtime_handoff_receipt_set(
        manifest,
        adapter_config,
        source_pull_receipt_set=source_pull_receipts,
    )
    return {
        "adapter_config_set": adapter_config,
        "scheduled_ingest_run_manifest": manifest,
        "source_pull_receipt_set": source_pull_receipts,
        "runtime_handoff_receipt_set": runtime_handoff_receipts,
        "oracle_intake_queue": queue,
        "outcome_binding_candidate_packet": candidate,
        "brier_readiness_precheck": precheck,
    }


def _scheduler_tile(inputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    manifest = inputs["scheduled_ingest_run_manifest"]
    adapter_config = inputs["adapter_config_set"]
    eligible_adapters = list(manifest.get("eligible_adapters", []))
    blocked_adapters = list(manifest.get("blocked_adapters", []))
    adapter_count = len(adapter_config.get("adapters", []))
    status = "ACTIVE" if eligible_adapters else "BLOCKED_NO_ELIGIBLE_ADAPTERS"
    return {
        "tile_id": "ingest_scheduler",
        "status": status,
        "lane": "SHADOW",
        "summary": {
            "scheduler_id": manifest["scheduler_id"],
            "adapter_count": adapter_count,
            "eligible_adapter_count": len(eligible_adapters),
            "blocked_adapter_count": len(blocked_adapters),
            "eligible_adapters": eligible_adapters,
            "blocked_adapters": blocked_adapters,
            "handoff_target_patch": manifest["handoff"]["target_patch"],
        },
    }


def _adapter_eligibility_tile(inputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    manifest = inputs["scheduled_ingest_run_manifest"]
    runtime_handoff = inputs["runtime_handoff_receipt_set"]
    receipt_adapters = sorted(row["adapter_id"] for row in runtime_handoff.get("receipts", []))
    return {
        "tile_id": "adapter_eligibility",
        "status": "ACTIVE" if receipt_adapters else "NOT_COMPUTABLE",
        "lane": "SHADOW",
        "summary": {
            "receipt_adapter_count": len(receipt_adapters),
            "receipt_adapters": receipt_adapters,
            "manifest_run_id": manifest["run_id"],
        },
    }


def _handoff_tile(inputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    handoff = inputs["runtime_handoff_receipt_set"]
    _require_boundary(handoff, schema_version="RuntimeHandoffReceiptSet.v1")
    receipts = handoff.get("receipts", [])
    receipt_statuses = sorted({row["handoff_status"] for row in receipts})
    status = "READY" if receipts else "NOT_COMPUTABLE"
    return {
        "tile_id": "handoff_receipts",
        "status": status,
        "lane": "SHADOW",
        "summary": {
            "receipt_count": len(receipts),
            "receipt_statuses": receipt_statuses,
            "source_manifest_patch_id": handoff["source_manifest_patch_id"],
        },
    }


def _oracle_queue_tile(inputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    queue = inputs["oracle_intake_queue"]
    _require_boundary(queue, schema_version="OracleIntakeQueue.v1")
    entries = queue.get("queue_entries", [])
    statuses = sorted({row["queue_status"] for row in entries})
    ready = bool(entries) and statuses == ["READY_FOR_ORACLE_INTAKE"]
    return {
        "tile_id": "oracle_queue",
        "status": "READY" if ready else "NOT_COMPUTABLE",
        "lane": "SHADOW",
        "summary": {
            "queue_entry_count": len(entries),
            "queue_statuses": statuses,
            "domains": sorted({row["domain"] for row in entries}),
        },
    }


def _candidate_tile(inputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    candidate = inputs["outcome_binding_candidate_packet"]
    _require_boundary(candidate, schema_version="OutcomeBindingCandidatePacket.v1")
    ready = candidate["candidate_status"] == "CANDIDATE_READY_ADVISORY_ONLY"
    return {
        "tile_id": "candidate_outcome_binding",
        "status": "READY" if ready else "BLOCKED_PENDING_OUTCOME_BINDING",
        "lane": "FORECAST_CANDIDATE",
        "summary": {
            "candidate_type": candidate["candidate_type"],
            "candidate_status": candidate["candidate_status"],
            "cross_domain_receipt_count": candidate["cross_domain_receipt_count"],
            "source_domains": candidate["source_domains"],
        },
    }


def _brier_tile(inputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    precheck = inputs["brier_readiness_precheck"]
    _require_boundary(precheck, schema_version="BrierReadinessPrecheck.v1")
    return {
        "tile_id": "brier_readiness",
        "status": "READY" if precheck["brier_ready"] else "BLOCKED_PENDING_OUTCOME_BINDING",
        "lane": "FORECAST_CANDIDATE",
        "summary": {
            "precheck_status": precheck["precheck_status"],
            "missing_requirement_count": len(precheck["missing_requirements"]),
            "missing_requirements": precheck["missing_requirements"],
        },
    }


def _authority_lock_tile(inputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    queue = inputs["oracle_intake_queue"]
    candidate = inputs["outcome_binding_candidate_packet"]
    precheck = inputs["brier_readiness_precheck"]
    all_locked = all(queue[key] is False for key in _REQUIRED_FALSE_KEYS) and all(
        candidate[key] is False for key in _REQUIRED_FALSE_KEYS
    ) and all(precheck[key] is False for key in _REQUIRED_FALSE_KEYS)
    return {
        "tile_id": "authority_lock_panel",
        "status": "LOCKED" if all_locked else "DRIFT_DETECTED",
        "lane": "PROJECTION_ONLY",
        "summary": {
            "authority_badges": _AUTHORITY_BADGES,
            "forecast_authority": False,
            "execution_authority": False,
            "runtime_mutation": False,
            "canon_mutation": False,
        },
    }


def build_aal_viz_ingest_projection_pack(
    inputs: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    source_inputs = inputs or load_ingest_projection_inputs()
    tiles = [
        _scheduler_tile(source_inputs),
        _adapter_eligibility_tile(source_inputs),
        _handoff_tile(source_inputs),
        _oracle_queue_tile(source_inputs),
        _candidate_tile(source_inputs),
        _brier_tile(source_inputs),
        _authority_lock_tile(source_inputs),
    ]
    packet = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "generated_at": "DETERMINISTIC_RUNTIME_SNAPSHOT",
        "authority": AUTHORITY,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "forecast_authority": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "source_inputs": {
            "adapter_config_set": "SourceAdapterConfigSet.v1",
            "scheduled_ingest_run_manifest": "ScheduledIngestRunManifest.v1",
            "source_pull_receipt_set": "SourcePullReceiptSet.v1",
            "runtime_handoff_receipt_set": "RuntimeHandoffReceiptSet.v1",
            "oracle_intake_queue": "OracleIntakeQueue.v1",
            "outcome_binding_candidate_packet": "OutcomeBindingCandidatePacket.v1",
            "brier_readiness_precheck": "BrierReadinessPrecheck.v1",
        },
        "tiles": tiles,
        "authority_badges": list(_AUTHORITY_BADGES),
    }
    packet["projection_hash"] = canonical_hash(packet)
    return packet


def build_aal_viz_ingest_projection_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# AAL-Viz Ingest Projection Pack",
        "",
        f"- patch_id: `{packet['patch_id']}`",
        f"- authority: `{packet['authority']}`",
        f"- tile_count: `{len(packet['tiles'])}`",
        f"- authority_badges: `{', '.join(packet['authority_badges'])}`",
        "",
    ]
    for tile in packet["tiles"]:
        lines.extend(
            [
                f"## {tile['tile_id']}",
                "",
                f"- status: `{tile['status']}`",
                f"- lane: `{tile['lane']}`",
                "",
            ]
        )
    return "\n".join(lines)


def write_aal_viz_ingest_projection_pack(path: Path | str, packet: dict[str, Any]) -> None:
    target = Path(path)
    write_canonical_json(target, packet)
    target.with_suffix(".md").write_text(
        build_aal_viz_ingest_projection_markdown(packet),
        encoding="utf-8",
    )
