"""Adapter: Abraxas OS artifacts → OperationTrace v0.1 (SHADOW / advisory).

Converts EvidencePack, FamiliarIngestionReceipt, and FamiliarSpineTouchpoint
into the format consumed by abx-hermes-skill-evolution and the live emitter.

This is a projection / telemetry surface only. No authority is granted.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash

OPERATION_TRACE_SCHEMA_VERSION = "OperationTrace v0.1"


def _stable_hash(obj: Any) -> str:
    """Deterministic short hash."""
    if isinstance(obj, (dict, list)):
        text = json.dumps(obj, sort_keys=True, ensure_ascii=False)
    else:
        text = str(obj)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def receipt_to_operation_trace(
    receipt: dict[str, Any],
    *,
    source_artifact: str | None = None,
    task_class: str = "signal_forage",
    skill_id: str = "abx-familiar-signal-forager",
) -> dict[str, Any]:
    """
    Turn a FamiliarIngestionReceipt.v0 (or compatible EvidencePack-derived dict)
    into an OperationTrace v0.1 record.
    """
    if not isinstance(receipt, dict):
        receipt = {}

    pack_id = receipt.get("pack_id") or receipt.get("pack_ref", "unknown")
    receipt_id = receipt.get("receipt_id", "")
    status = receipt.get("status", "UNKNOWN")
    density = float(receipt.get("evidence_density", 0.0))
    observed = int(receipt.get("observed_claim_count", 0))
    commercial_blocked = bool(receipt.get("commercial_claims_blocked", True))

    inputs = {
        "pack_id": pack_id,
        "receipt_id": receipt_id,
        "status": status,
        "evidence_density": density,
        "observed_claim_count": observed,
        "commercial_claims_blocked": commercial_blocked,
    }

    outputs: list[Any] = [
        {"status": status},
        {"evidence_density": density},
        {"commercial_blocked": commercial_blocked},
    ]
    if receipt.get("register_counts"):
        outputs.append({"register_counts": receipt["register_counts"]})

    validation_results = ["OS_SIGNAL_OBSERVED"]
    if density >= 0.7:
        validation_results.append("HIGH_DENSITY_PACK")
    if commercial_blocked:
        validation_results.append("COMMERCIAL_CLAIMS_BLOCKED")

    completion = "COMPLETE" if status == "INGESTED_SHADOW" else "REJECTED"

    body = {
        "operation_id": f"os-trace-{ _stable_hash(pack_id or receipt_id) }",
        "skill_id": skill_id,
        "task_class": task_class,
        "repo_commit": "HEAD",
        "inputs_hash": _stable_hash(inputs),
        "plan_hash": _stable_hash(source_artifact or "ai-os-kernel"),
        "commands_run": ["abraxas forage ingest", "familiar_ingestion"],
        "outputs": outputs,
        "validation_results": validation_results,
        "evidence_status": "OBSERVED",
        "completion_status": completion,
        "operator_interventions": [],
        "token_usage": {"estimated": 0},
        "elapsed_time": 0.0,
        "failure_signatures": [],
        "brier_score": None,
        "source_artifact": source_artifact or "core/signal/operation_trace_adapter",
        "timestamp": _now_iso(),
        "advisory_only": True,
        "authority": {
            "execution_authority": False,
            "promotion_authorized": False,
            "forecast_routing_authorized": False,
        },
    }

    # Add a trace-level hash for provenance (does not replace schema required fields)
    body["trace_hash"] = canonical_hash({k: v for k, v in body.items() if k != "trace_hash"})
    return body


def touchpoint_to_operation_trace(
    touchpoint: dict[str, Any],
    *,
    source_artifact: str | None = None,
) -> dict[str, Any]:
    """Convert a FamiliarSpineTouchpoint into an OperationTrace (advisory projection)."""
    if not isinstance(touchpoint, dict):
        touchpoint = {}

    route = touchpoint.get("route", "ABSTAIN")
    pack_id = touchpoint.get("pack_id", "")
    reason = touchpoint.get("reason", "")

    inputs = {"route": route, "pack_id": pack_id, "reason": reason}

    outputs = [{"route": route}]
    if touchpoint.get("input_payload_seed"):
        outputs.append({"has_input_seed": True})

    validation = ["SPINE_TOUCH_OBSERVED"]
    if route == "ORACLE_SHADOW_CANDIDATE":
        validation.append("SHADOW_CANDIDATE_PRODUCED")

    body = {
        "operation_id": f"os-spine-{ _stable_hash(pack_id or route) }",
        "skill_id": "abx-familiar-signal-forager",
        "task_class": "signal_spine_projection",
        "repo_commit": "HEAD",
        "inputs_hash": _stable_hash(inputs),
        "plan_hash": _stable_hash(source_artifact or "ai-os-spine"),
        "commands_run": ["abraxas forage spine-touch"],
        "outputs": outputs,
        "validation_results": validation,
        "evidence_status": "OBSERVED",
        "completion_status": "COMPLETE" if "CANDIDATE" in route else "ABSTAIN",
        "operator_interventions": [],
        "token_usage": {"estimated": 0},
        "elapsed_time": 0.0,
        "failure_signatures": [],
        "brier_score": None,
        "source_artifact": source_artifact or "core/signal/spine_bridge",
        "timestamp": _now_iso(),
        "advisory_only": True,
    }
    body["trace_hash"] = canonical_hash({k: v for k, v in body.items() if k != "trace_hash"})
    return body


def write_operation_trace(
    trace: dict[str, Any],
    out_dir: Path | None = None,
) -> Path:
    """Write a single trace as a .latest.json style artifact (for emitter pickup)."""
    out_dir = out_dir or Path("out/audit")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Use a stable-ish name based on operation_id
    op_id = trace.get("operation_id", "os-trace")
    path = out_dir / f"os_signal_{op_id}.latest.json"
    path.write_text(json.dumps(trace, sort_keys=True, indent=2), encoding="utf-8")
    return path
