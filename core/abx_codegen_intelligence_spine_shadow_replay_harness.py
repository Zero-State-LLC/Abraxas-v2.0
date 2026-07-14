from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.codegen.shadow_replay_harness import ShadowReplayHarness

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "AbxCodegenIntelligenceSpineShadowReplayHarness.v1"
HARNESS_ID = "abx_codegen_intelligence_spine_shadow_replay_harness_001"
HARNESS_JSON_PATH = Path("out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_001.latest.json")
AUTHORIZATION_GATE_PATH = Path(
    "out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_implementation_authorization_gate_001.latest.json"
)
STATUS_EMITTED = "ABX_CODEGEN_SHADOW_REPLAY_HARNESS_EMITTED"
STATUS_BLOCKED = "ABX_CODEGEN_SHADOW_REPLAY_HARNESS_BLOCKED"
GATE_HELD_STATUS = "SHADOW_REPLAY_HARNESS_IMPLEMENTATION_AUTHORIZATION_HELD_FOR_OPERATOR"

_DEFAULT_FIXTURES: tuple[dict[str, str], ...] = (
    {"fixture_id": "codegen_shadow_replay_fixture_001"},
)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _authority_locks() -> dict[str, bool]:
    return {
        "canon_mutation": False,
        "code_generation": False,
        "code_mutation": False,
        "execution_authority": False,
        "harness_implementation": False,
        "ingest_runner_mutation": False,
        "queue_mutation": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "shadow_replay_execution": False,
    }


def _load_authorization_gate(source_root: Path) -> dict[str, Any] | None:
    return _read_json(source_root / AUTHORIZATION_GATE_PATH)


def shadow_replay_harness_eligible(source_root: str | Path = ".") -> bool:
    gate = _load_authorization_gate(Path(source_root))
    if gate is None:
        return False
    return (
        gate.get("authorization_gate_status") != GATE_HELD_STATUS
        and gate.get("implementation_authorization_granted") is True
        and gate.get("valid_for_implementation") is True
    )


def build_abx_codegen_intelligence_spine_shadow_replay_harness_packet(
    source_root: str | Path = ".",
    *,
    fixtures: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    gate = _load_authorization_gate(root)
    eligible = shadow_replay_harness_eligible(root)
    replay = ShadowReplayHarness(
        fixtures=list(fixtures if fixtures is not None else _DEFAULT_FIXTURES)
    ).replay()
    base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "harness_id": HARNESS_ID,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "implementation_authorized": eligible,
        "source_authorization_gate_path": AUTHORIZATION_GATE_PATH.as_posix(),
        "source_authorization_gate_hash": (
            str(gate.get("packet_hash", NOT_COMPUTABLE)) if gate else NOT_COMPUTABLE
        ),
        "replay_result": replay,
        "authority_locks": _authority_locks(),
        "execution_authority": False,
        "runtime_mutation_allowed": False,
        "recommended_next_lane": NOT_COMPUTABLE,
    }
    if eligible:
        base["status"] = STATUS_EMITTED
    else:
        base["status"] = STATUS_BLOCKED
    packet = {**base, "packet_hash": canonical_hash(base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def write_abx_codegen_intelligence_spine_shadow_replay_harness_packet(
    source_root: str | Path = ".",
    *,
    out_path: Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    packet = build_abx_codegen_intelligence_spine_shadow_replay_harness_packet(root)
    target = out_path if out_path is not None else root / HARNESS_JSON_PATH
    write_canonical_json(target, packet)
    return packet
