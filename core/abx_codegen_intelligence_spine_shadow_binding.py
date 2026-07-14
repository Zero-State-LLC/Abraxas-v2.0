from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.abx_codegen_intelligence_spine_shadow_replay_harness import (
    HARNESS_JSON_PATH,
    STATUS_BLOCKED,
    build_abx_codegen_intelligence_spine_shadow_replay_harness_packet,
)
from core.canonical.json import canonical_hash, write_canonical_json

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "AbxCodegenIntelligenceSpineShadowBinding.v1"
BINDING_ID = "abx_codegen_intelligence_spine_shadow_binding_001"
BINDING_JSON_PATH = Path("out/audit/abx_codegen_intelligence_spine_shadow_binding_001.latest.json")
STATUS_EMITTED = "ABX_CODEGEN_INTELLIGENCE_SPINE_SHADOW_BINDING_EMITTED"
INTEGRATION_POINT_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_001"


def build_abx_codegen_intelligence_spine_shadow_binding_packet(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    harness = build_abx_codegen_intelligence_spine_shadow_replay_harness_packet(root)
    base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "binding_id": BINDING_ID,
        "status": STATUS_EMITTED,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "integration_point_id": INTEGRATION_POINT_ID,
        "source_canonical_owner": "ABX Codegen Intelligence Spine",
        "target_runtime_surface": "governed code-drop and patch-contract planning handoff",
        "wiring_mode": "SHADOW_ADVISORY_ONLY",
        "source_harness_path": HARNESS_JSON_PATH.as_posix(),
        "source_harness_hash": harness.get("packet_hash", NOT_COMPUTABLE),
        "source_harness_status": harness.get("status", NOT_COMPUTABLE),
        "harness_blocked": harness.get("status") == STATUS_BLOCKED,
        "execution_authority": False,
        "runtime_mutation_allowed": False,
        "recommended_next_lane": NOT_COMPUTABLE,
    }
    packet = {**base, "binding_hash": canonical_hash(base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def write_abx_codegen_intelligence_spine_shadow_binding_packet(
    source_root: str | Path = ".",
    *,
    out_path: Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    packet = build_abx_codegen_intelligence_spine_shadow_binding_packet(root)
    target = out_path if out_path is not None else root / BINDING_JSON_PATH
    write_canonical_json(target, packet)
    return packet
