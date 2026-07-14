from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.runtime_integration_gate_shadow_wiring_plan import (
    HOLD_RECEIPT_PATH,
    PLAN_JSON_PATH,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "RuntimeIntegrationGateShadowWiringHooks.v1"
HOOKS_ID = "runtime_integration_gate_shadow_wiring_hooks_001"
HOOKS_JSON_PATH = Path("out/audit/runtime_integration_gate_shadow_wiring_hooks_001.latest.json")
HOOKS_MD_PATH = HOOKS_JSON_PATH.with_suffix(".md")
STATUS_EMITTED = "RUNTIME_INTEGRATION_GATE_SHADOW_WIRING_HOOKS_EMITTED"
STATUS_BLOCKED = "RUNTIME_INTEGRATION_GATE_SHADOW_WIRING_HOOKS_BLOCKED"
PLAN_READY_STATUS = "RUNTIME_INTEGRATION_GATE_SHADOW_WIRING_PLAN_READY"

_PROJECTION_BINDING_REFS: dict[str, str] = {
    "AAL_VIZ_PROJECTION_SPINE_001": (
        "out/projection/aal_viz_projection_spine_shadow_binding_001.latest.json"
    ),
    "ABX_CODEGEN_INTELLIGENCE_SPINE_001": (
        "out/audit/abx_codegen_intelligence_spine_shadow_binding_001.latest.json"
    ),
    "BELIEF_GRAPH_ENGINE_001": "out/audit/belief_graph_engine_shadow_binding_001.latest.json",
    "GLOBAL_INGEST_ADAPTER_SPINE_001": (
        "out/ingest/global_ingest_adapter_spine_shadow_binding_001.latest.json"
    ),
    "PHASE_PERCOLATION_ENGINE_001": (
        "out/audit/phase_percolation_engine_shadow_binding_001.latest.json"
    ),
    "RESEARCH_SHADOW_REPLAY_ENGINE_001": (
        "out/research/research_shadow_replay_engine_shadow_binding_001.latest.json"
    ),
    "SITUATION_RUNTIME_ENGINE_001": (
        "out/audit/situation_runtime_engine_shadow_binding_001.latest.json"
    ),
}


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _authority_locks() -> dict[str, bool]:
    return {
        "canon_mutation": False,
        "execution_authority": False,
        "ingest_runner_mutation": False,
        "queue_mutation": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
    }


def _load_plan(source_root: Path) -> dict[str, Any] | None:
    return _read_json(source_root / PLAN_JSON_PATH)


def _load_hold_receipt(source_root: Path) -> dict[str, Any] | None:
    return _read_json(source_root / HOLD_RECEIPT_PATH)


def shadow_wiring_hooks_eligible(source_root: str | Path = ".") -> bool:
    root = Path(source_root)
    plan = _load_plan(root) or {}
    hold = _load_hold_receipt(root) or {}
    return (
        plan.get("status") == PLAN_READY_STATUS
        and hold.get("shadow_wiring_approved") is True
        and hold.get("valid_for_runtime_wiring") is True
    )


def _build_binding(point: Mapping[str, Any]) -> dict[str, str]:
    integration_point_id = str(point.get("integration_point_id", NOT_COMPUTABLE))
    return {
        "integration_point_id": integration_point_id,
        "source_canonical_owner": str(point.get("source_canonical_owner", NOT_COMPUTABLE)),
        "target_runtime_surface": str(point.get("target_runtime_surface", NOT_COMPUTABLE)),
        "projection_binding_ref": _PROJECTION_BINDING_REFS.get(integration_point_id, NOT_COMPUTABLE),
        "wiring_mode": "SHADOW_ADVISORY_ONLY",
    }


def build_runtime_integration_gate_shadow_wiring_hooks_packet(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    plan = _load_plan(root) or {}
    hold = _load_hold_receipt(root) or {}
    eligible = shadow_wiring_hooks_eligible(root)
    integration_points = plan.get("integration_points", [])
    bindings = (
        sorted(
            [_build_binding(point) for point in integration_points if isinstance(point, Mapping)],
            key=lambda item: item["integration_point_id"],
        )
        if eligible and isinstance(integration_points, list)
        else []
    )
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "hooks_id": HOOKS_ID,
        "status": STATUS_EMITTED if eligible else STATUS_BLOCKED,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "shadow_wiring_approved": hold.get("shadow_wiring_approved") is True,
        "mandatory_pre_dispatch_wiring": False,
        "execution_authority": False,
        "runtime_mutation_allowed": False,
        "integration_point_binding_count": len(bindings),
        "integration_point_bindings": bindings,
        "source_plan_path": PLAN_JSON_PATH.as_posix(),
        "source_plan_hash": str(plan.get("plan_hash", NOT_COMPUTABLE)),
        "source_hold_receipt_path": HOLD_RECEIPT_PATH.as_posix(),
        "source_hold_receipt_hash": str(hold.get("receipt_hash", NOT_COMPUTABLE)),
        "authority_locks": _authority_locks(),
        "recommended_next_lane": NOT_COMPUTABLE,
        "hooks_hash": "",
    }
    packet["hooks_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "hooks_hash"}
    )
    return packet


def write_runtime_integration_gate_shadow_wiring_hooks(
    repo_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_runtime_integration_gate_shadow_wiring_hooks_packet(root)
    write_canonical_json(target_root / HOOKS_JSON_PATH, packet)
    target_root.joinpath(HOOKS_MD_PATH).parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Runtime Integration Gate Shadow Wiring Hooks 001",
        "",
        f"- status: {packet['status']}",
        f"- integration_point_binding_count: {packet['integration_point_binding_count']}",
        f"- mandatory_pre_dispatch_wiring: {packet['mandatory_pre_dispatch_wiring']}",
    ]
    target_root.joinpath(HOOKS_MD_PATH).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return packet
