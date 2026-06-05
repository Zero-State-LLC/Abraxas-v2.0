from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

from .scheduler import build_scheduled_manifest, decide_ingest_windows

AUTHORITY = "SHADOW_HANDOFF_ONLY"
TARGET_PATCH_ID = "PATCH-ABX-AUTO-INGEST-003"
SOURCE_PATCH_ID = "PATCH-ABX-AUTO-INGEST-002"

_REQUIRED_TRUE_KEYS = ("advisory_only", "projection_only", "non_authoritative")
_REQUIRED_FALSE_KEYS = ("forecast_authority", "canon_mutation", "runtime_mutation", "execution_authority")


def _sample_adapter_config_set() -> dict[str, Any]:
    return {
        "schema_version": "SourceAdapterConfigSet.v1",
        "config_id": "abx_source_adapter_config_set_v1",
        "adapters": [
            {
                "adapter_id": "abx_market_feed_v1",
                "domain": "finance",
                "enabled": True,
                "source_kind": "json",
                "source_uri": "input/finance/market_feed.shadow.json",
                "pull_mode": "SHADOW_PULL",
            },
            {
                "adapter_id": "abx_geo_feed_v1",
                "domain": "geopolitics",
                "enabled": True,
                "source_kind": "audit_artifact",
                "source_uri": "docs/status/badges.json",
                "pull_mode": "SHADOW_PULL",
            },
        ],
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "forecast_authority": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
    }


def _sample_policy() -> dict[str, Any]:
    return {
        "schema_version": "IngestWindowPolicy.v1",
        "policy_id": "abx_controlled_ingest_scheduler_v1",
        "timezone": "UTC",
        "global": {
            "min_seconds_between_runs": 300,
            "max_concurrent_adapters": 1,
            "quiet_window_enabled": True,
            "quiet_window": {"start_hour": 2, "end_hour": 5, "cadence_multiplier": 4.0},
        },
        "domain_policies": {
            "finance": {
                "base_cadence_seconds": 900,
                "min_cadence_seconds": 300,
                "max_cadence_seconds": 3600,
                "operator_window_required": False,
            },
            "geopolitics": {
                "base_cadence_seconds": 3600,
                "min_cadence_seconds": 1800,
                "max_cadence_seconds": 21600,
                "operator_window_required": True,
            },
        },
        "volatility_policy": {
            "enabled": True,
            "compression_thresholds": [{"metric": "z_score", "gte": 2.5, "cadence_multiplier": 0.5}],
            "expansion_thresholds": [{"metric": "z_score", "lt": 1.0, "cadence_multiplier": 2.0}],
        },
    }


def _sample_scheduler_state() -> dict[str, Any]:
    return {
        "schema_version": "SchedulerState.v1",
        "scheduler_id": "abx_controlled_ingest_scheduler_v1",
        "last_run_by_adapter": {},
        "last_decision_hash": None,
        "active_operator_windows": [],
        "cooldowns": {},
        "blocked_adapters": [],
    }


def _sample_anomaly_state() -> dict[str, Any]:
    return {
        "schema_version": "ShadowAnomalyState.v1",
        "generated_at": "2026-06-04T00:00:00Z",
        "domain_scores": {
            "finance": {"z_score": 3.0, "source": "fixture"},
            "geopolitics": {"z_score": 0.5, "source": "fixture"},
        },
    }


def build_sample_manifest_and_config() -> tuple[dict[str, Any], dict[str, Any]]:
    adapter_config_set = _sample_adapter_config_set()
    policy = _sample_policy()
    decision_set = decide_ingest_windows(
        adapter_config_set=adapter_config_set,
        window_policy=policy,
        scheduler_state=_sample_scheduler_state(),
        anomaly_state=_sample_anomaly_state(),
        now_iso="2026-06-04T03:00:00Z",
    )
    manifest = build_scheduled_manifest(
        decision_set,
        max_concurrent_adapters=int(policy["global"]["max_concurrent_adapters"]),
    )
    return manifest, adapter_config_set


def _require_boundary(packet: dict[str, Any], *, schema_version: str) -> None:
    if packet.get("schema_version") != schema_version:
        raise ValueError(f"expected {schema_version}")
    for key in _REQUIRED_TRUE_KEYS:
        if packet.get(key) is not True:
            raise ValueError(f"{schema_version} must set {key}=true")
    for key in _REQUIRED_FALSE_KEYS:
        if packet.get(key) is not False:
            raise ValueError(f"{schema_version} must set {key}=false")


def _validate_inputs(manifest: dict[str, Any], adapter_config_set: dict[str, Any]) -> None:
    _require_boundary(manifest, schema_version="ScheduledIngestRunManifest.v1")
    _require_boundary(adapter_config_set, schema_version="SourceAdapterConfigSet.v1")
    handoff = manifest.get("handoff", {})
    if not isinstance(handoff, dict) or handoff.get("authority") != "SHADOW_ONLY":
        raise ValueError("manifest handoff authority must remain SHADOW_ONLY")
    if handoff.get("target_pipeline") != "abx_auto_ingest_v1":
        raise ValueError("manifest handoff target_pipeline must remain abx_auto_ingest_v1")
    if handoff.get("target_patch") != SOURCE_PATCH_ID:
        raise ValueError(f"manifest handoff target_patch must remain {SOURCE_PATCH_ID}")


def _adapter_map(adapter_config_set: dict[str, Any]) -> dict[str, dict[str, Any]]:
    adapters = adapter_config_set.get("adapters", [])
    if not isinstance(adapters, list):
        raise ValueError("adapter config set must include adapters list")
    mapping: dict[str, dict[str, Any]] = {}
    for row in adapters:
        if not isinstance(row, dict):
            raise ValueError("adapter rows must be objects")
        adapter_id = str(row.get("adapter_id", "")).strip()
        if not adapter_id:
            raise ValueError("adapter rows require adapter_id")
        mapping[adapter_id] = row
    return mapping


def _eligible_adapter_rows(manifest: dict[str, Any], adapter_config_set: dict[str, Any]) -> list[dict[str, Any]]:
    mapping = _adapter_map(adapter_config_set)
    rows: list[dict[str, Any]] = []
    for adapter_id in manifest.get("eligible_adapters", []):
        row = mapping.get(str(adapter_id))
        if row is None:
            raise ValueError(f"missing adapter config for eligible adapter {adapter_id}")
        if row.get("enabled") is not True:
            raise ValueError(f"eligible adapter {adapter_id} must remain enabled")
        rows.append(deepcopy(row))
    return rows


def _source_pull_receipt(manifest: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    source_pull_receipt_id = canonical_hash(
        {
            "run_id": manifest["run_id"],
            "adapter_id": row["adapter_id"],
            "record": "source_pull_receipt",
        }
    )
    return {
        "source_pull_receipt_id": source_pull_receipt_id,
        "adapter_id": row["adapter_id"],
        "domain": row["domain"],
        "source_kind": row["source_kind"],
        "source_uri": row["source_uri"],
        "pull_mode": row.get("pull_mode", "SHADOW_PULL"),
        "pull_status": "SHADOW_PULL_NOT_EXECUTED",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "forecast_authority": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
    }


def build_source_pull_receipt_set(
    manifest: dict[str, Any],
    adapter_config_set: dict[str, Any],
) -> dict[str, Any]:
    _validate_inputs(manifest, adapter_config_set)
    receipts = [_source_pull_receipt(manifest, row) for row in _eligible_adapter_rows(manifest, adapter_config_set)]
    packet = {
        "schema_version": "SourcePullReceiptSet.v1",
        "patch_id": TARGET_PATCH_ID,
        "scheduler_id": manifest["scheduler_id"],
        "run_id": manifest["run_id"],
        "source_manifest_patch_id": manifest["handoff"]["target_patch"],
        "authority": AUTHORITY,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "forecast_authority": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "receipts": receipts,
    }
    packet["receipt_set_hash"] = canonical_hash(packet)
    return packet


def build_runtime_handoff_receipt_set(
    manifest: dict[str, Any],
    adapter_config_set: dict[str, Any],
    source_pull_receipt_set: dict[str, Any] | None = None,
) -> dict[str, Any]:
    _validate_inputs(manifest, adapter_config_set)
    source_pull_packet = source_pull_receipt_set or build_source_pull_receipt_set(manifest, adapter_config_set)
    pull_map = {row["adapter_id"]: row for row in source_pull_packet["receipts"]}
    receipts: list[dict[str, Any]] = []
    for row in _eligible_adapter_rows(manifest, adapter_config_set):
        source_pull_receipt_id = pull_map[row["adapter_id"]]["source_pull_receipt_id"]
        queue_entry_id = canonical_hash(
            {
                "run_id": manifest["run_id"],
                "adapter_id": row["adapter_id"],
                "record": "oracle_queue_entry",
            }
        )
        handoff_receipt_id = canonical_hash(
            {
                "run_id": manifest["run_id"],
                "adapter_id": row["adapter_id"],
                "record": "runtime_handoff_receipt",
            }
        )
        receipts.append(
            {
                "handoff_receipt_id": handoff_receipt_id,
                "queue_entry_id": queue_entry_id,
                "source_pull_receipt_id": source_pull_receipt_id,
                "adapter_id": row["adapter_id"],
                "domain": row["domain"],
                "source_kind": row["source_kind"],
                "source_uri": row["source_uri"],
                "handoff_status": "QUEUE_READY_ADVISORY_ONLY",
                "advisory_only": True,
                "projection_only": True,
                "non_authoritative": True,
                "forecast_authority": False,
                "canon_mutation": False,
                "runtime_mutation": False,
                "execution_authority": False,
            }
        )
    packet = {
        "schema_version": "RuntimeHandoffReceiptSet.v1",
        "patch_id": TARGET_PATCH_ID,
        "scheduler_id": manifest["scheduler_id"],
        "run_id": manifest["run_id"],
        "source_manifest_patch_id": manifest["handoff"]["target_patch"],
        "authority": AUTHORITY,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "forecast_authority": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "receipts": receipts,
    }
    packet["receipt_set_hash"] = canonical_hash(packet)
    return packet


def build_oracle_intake_queue(
    manifest: dict[str, Any],
    adapter_config_set: dict[str, Any],
    runtime_handoff_receipt_set: dict[str, Any] | None = None,
) -> dict[str, Any]:
    _validate_inputs(manifest, adapter_config_set)
    handoff_packet = runtime_handoff_receipt_set or build_runtime_handoff_receipt_set(manifest, adapter_config_set)
    queue_entries = [
        {
            "queue_entry_id": row["queue_entry_id"],
            "handoff_receipt_id": row["handoff_receipt_id"],
            "source_pull_receipt_id": row["source_pull_receipt_id"],
            "adapter_id": row["adapter_id"],
            "domain": row["domain"],
            "source_kind": row["source_kind"],
            "source_uri": row["source_uri"],
            "intake_mode": "SHADOW_PULL",
            "queue_status": "READY_FOR_ORACLE_INTAKE",
            "advisory_only": True,
            "projection_only": True,
            "non_authoritative": True,
            "forecast_authority": False,
            "canon_mutation": False,
            "runtime_mutation": False,
            "execution_authority": False,
        }
        for row in handoff_packet["receipts"]
    ]
    packet = {
        "schema_version": "OracleIntakeQueue.v1",
        "patch_id": TARGET_PATCH_ID,
        "scheduler_id": manifest["scheduler_id"],
        "run_id": manifest["run_id"],
        "authority": AUTHORITY,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "forecast_authority": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "queue_entries": queue_entries,
    }
    packet["queue_hash"] = canonical_hash(packet)
    return packet


def render_handoff_markdown(
    runtime_handoff_receipt_set: dict[str, Any],
    source_pull_receipt_set: dict[str, Any],
    oracle_intake_queue: dict[str, Any],
) -> tuple[str, str, str]:
    receipt_lines = [
        "# Runtime Handoff Receipt Set",
        "",
        f"- run_id: `{runtime_handoff_receipt_set['run_id']}`",
        f"- receipt_count: `{len(runtime_handoff_receipt_set['receipts'])}`",
        f"- source_manifest_patch_id: `{runtime_handoff_receipt_set['source_manifest_patch_id']}`",
        f"- authority: `{runtime_handoff_receipt_set['authority']}`",
        "",
    ]
    pull_lines = [
        "# Source Pull Receipt Set",
        "",
        f"- run_id: `{source_pull_receipt_set['run_id']}`",
        f"- receipt_count: `{len(source_pull_receipt_set['receipts'])}`",
        f"- authority: `{source_pull_receipt_set['authority']}`",
        "",
    ]
    queue_lines = [
        "# Oracle Intake Queue",
        "",
        f"- run_id: `{oracle_intake_queue['run_id']}`",
        f"- queue_entries: `{len(oracle_intake_queue['queue_entries'])}`",
        f"- authority: `{oracle_intake_queue['authority']}`",
        "",
    ]
    return "\n".join(receipt_lines), "\n".join(pull_lines), "\n".join(queue_lines)


def write_runtime_handoff_outputs(
    out_dir: Path | str,
    *,
    runtime_handoff_receipt_set: dict[str, Any],
    source_pull_receipt_set: dict[str, Any],
    oracle_intake_queue: dict[str, Any],
) -> None:
    target_dir = Path(out_dir)
    receipt_json = target_dir / "runtime_handoff_receipt_set_001.latest.json"
    pull_json = target_dir / "source_pull_receipt_set_001.latest.json"
    queue_json = target_dir / "oracle_intake_queue_001.latest.json"

    write_canonical_json(receipt_json, runtime_handoff_receipt_set)
    write_canonical_json(pull_json, source_pull_receipt_set)
    write_canonical_json(queue_json, oracle_intake_queue)

    receipt_md, pull_md, queue_md = render_handoff_markdown(
        runtime_handoff_receipt_set,
        source_pull_receipt_set,
        oracle_intake_queue,
    )
    receipt_json.with_suffix(".md").write_text(receipt_md, encoding="utf-8")
    pull_json.with_suffix(".md").write_text(pull_md, encoding="utf-8")
    queue_json.with_suffix(".md").write_text(queue_md, encoding="utf-8")
