from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "RuntimeIntegrationGateShadowWiringPlan.v1"
PLAN_ID = "runtime_integration_gate_shadow_wiring_plan_001"
PLAN_JSON_PATH = Path("out/audit/runtime_integration_gate_shadow_wiring_plan_001.latest.json")
PLAN_MD_PATH = PLAN_JSON_PATH.with_suffix(".md")
DECISION_RECORD_PATH = Path(
    "out/audit/runtime_integration_gate_operator_review_decision_record_001.latest.json"
)
HOLD_RECEIPT_PATH = Path(
    "out/audit/runtime_integration_gate_operator_review_decision_record_hold_receipt_001.latest.json"
)
RUNTIME_RECEIPT_PATH = Path("out/audit/runtime_integration_gate_receipt_001.latest.json")
NOT_COMPUTABLE = "NOT_COMPUTABLE"


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _integration_points(receipt: Mapping[str, Any]) -> list[dict[str, str]]:
    points: list[dict[str, str]] = []
    for subsystem in receipt.get("covered_subsystems", []):
        if not isinstance(subsystem, Mapping):
            continue
        subsystem_id = str(subsystem.get("subsystem_id", NOT_COMPUTABLE))
        target_surface = str(subsystem.get("target_runtime_surface", NOT_COMPUTABLE))
        owner = str(subsystem.get("source_canonical_owner", NOT_COMPUTABLE))
        points.append(
            {
                "integration_point_id": subsystem_id,
                "target_runtime_surface": target_surface,
                "source_canonical_owner": owner,
                "wiring_mode": "SHADOW_ADVISORY_ONLY",
            }
        )
    return sorted(points, key=lambda item: item["integration_point_id"])


def build_runtime_integration_gate_shadow_wiring_plan(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    decision = _read_json(root / DECISION_RECORD_PATH) or {}
    hold = _read_json(root / HOLD_RECEIPT_PATH) or {}
    receipt = _read_json(root / RUNTIME_RECEIPT_PATH) or {}
    shadow_approved = hold.get("shadow_wiring_approved") is True
    valid_for_wiring = hold.get("valid_for_runtime_wiring") is True
    plan_ready = (
        decision.get("status") == "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DECISION_RECORD_ATTESTED"
        and hold.get("status")
        == "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DECISION_RECORD_HOLD_RECEIPT_EMITTED"
        and receipt.get("artifact_type") == "RuntimeIntegrationGateReceipt.v1"
        and shadow_approved
        and valid_for_wiring
    )
    integration_points = _integration_points(receipt) if receipt else []
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "plan_id": PLAN_ID,
        "status": (
            "RUNTIME_INTEGRATION_GATE_SHADOW_WIRING_PLAN_READY"
            if plan_ready
            else "RUNTIME_INTEGRATION_GATE_SHADOW_WIRING_PLAN_BLOCKED"
        ),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "shadow_wiring_approved": shadow_approved,
        "valid_for_runtime_wiring": valid_for_wiring,
        "mandatory_pre_dispatch_wiring": False,
        "execution_authority": False,
        "runtime_mutation_allowed": False,
        "integration_point_count": len(integration_points),
        "integration_points": integration_points,
        "blocked_patch_classes": [
            "MANDATORY_PRE_DISPATCH_WIRING",
            "LIVE_RUNTIME_MUTATION",
            "QUEUE_OR_SCHEDULER_MUTATION",
            "EXECUTION_AUTHORITY_GRANT",
        ],
        "recommended_implementation_sequence": [
            "document shadow wiring hooks per integration_point_id",
            "add read-only projection bindings only",
            "verify authority locks remain false after wiring",
            "separate governed lane required for mandatory pre-dispatch wiring",
        ],
        "source_decision_record_path": DECISION_RECORD_PATH.as_posix(),
        "source_decision_record_hash": str(decision.get("decision_record_hash", NOT_COMPUTABLE)),
        "source_hold_receipt_path": HOLD_RECEIPT_PATH.as_posix(),
        "source_hold_receipt_hash": str(hold.get("receipt_hash", NOT_COMPUTABLE)),
        "source_runtime_receipt_path": RUNTIME_RECEIPT_PATH.as_posix(),
        "source_runtime_receipt_hash": str(receipt.get("receipt_hash", NOT_COMPUTABLE)),
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_action": (
            "prepare additive shadow wiring implementation PR per integration point; "
            "do not enable mandatory pre-dispatch wiring"
            if plan_ready
            else "restore operator-attested shadow wiring evidence"
        ),
        "downstream": NOT_COMPUTABLE,
        "plan_hash": "",
    }
    packet["plan_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "plan_hash"}
    )
    return packet


def write_runtime_integration_gate_shadow_wiring_plan(
    repo_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_runtime_integration_gate_shadow_wiring_plan(root)
    write_canonical_json(target_root / PLAN_JSON_PATH, packet)
    target_root.joinpath(PLAN_MD_PATH).parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Runtime Integration Gate Shadow Wiring Plan 001",
        "",
        f"- status: {packet['status']}",
        f"- shadow_wiring_approved: {packet['shadow_wiring_approved']}",
        f"- integration_point_count: {packet['integration_point_count']}",
        f"- mandatory_pre_dispatch_wiring: {packet['mandatory_pre_dispatch_wiring']}",
    ]
    target_root.joinpath(PLAN_MD_PATH).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return packet
