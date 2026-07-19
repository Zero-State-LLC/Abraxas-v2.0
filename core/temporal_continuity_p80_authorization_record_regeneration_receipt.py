from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.temporal_continuity_p80_authorization_record_plan_regeneration_plan import (
    build_temporal_continuity_p80_authorization_record_plan_regeneration_plan as build_p80_plan,  # noqa: E501
    write_temporal_continuity_p80_authorization_record_plan_regeneration_plan as write_p80_plan,  # noqa: E501
)

ARTIFACT_TYPE = "TemporalContinuityP80AuthorizationRecordRegenerationReceipt.v1"
SLICE_ID = "LOOP-805-SLICE-51"
STATUS = (
    "TEMPORAL_CONTINUITY_P80_AUTHORIZATION_RECORD_REGENERATION_RECEIPT_"
    "READY_ADVISORY_ONLY"
)
BRIER_SCORE = "0.10"

SLICE50_RECEIPT_PATH = (
    "out/audit/temporal_continuity_authorization_source_status_audit_001.latest.json"
)
P80_REGENERATION_PLAN_PATH = (
    "out/temporal_continuity_p80_authorization_record_plan_regeneration_plan/"
    "latest.json"
)
DEFAULT_OUT_PATH = (
    "out/audit/"
    "temporal_continuity_p80_authorization_record_regeneration_receipt_001.latest.json"
)

_AUTHORITY_LOCKS = {
    "authorization_authority": False,
    "authorization_record_creation_authority": False,
    "canon_mutation": False,
    "evidence_repair_authority": False,
    "external_calls": False,
    "fixture_binding_execution": False,
    "generator_execution_authority": False,
    "github_writeback": False,
    "mcp_exposure": False,
    "notion_writeback": False,
    "production_activation": False,
    "regeneration_authority": False,
    "regeneration_execution_authority": False,
    "repair_authority": False,
    "runtime_activation": False,
    "runtime_mutation": False,
    "sandbox_probe_execution": False,
}


def _file_hash(path: Path) -> str:
    if not path.exists():
        return "NOT_OBSERVED"
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def build_temporal_continuity_p80_authorization_record_regeneration_receipt(
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    p80_packet = build_p80_plan(repo_root=root)
    p80_path = root / P80_REGENERATION_PLAN_PATH
    write_p80_plan(
        p80_path,
        p80_packet,
    )

    slice50_path = root / SLICE50_RECEIPT_PATH
    slice50_packet = _read_json(slice50_path)

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "slice_id": SLICE_ID,
        "status": STATUS,
        "brier_score": BRIER_SCORE,
        "advisory_only": True,
        "projection_only": True,
        "receipt_only": True,
        "authority_locks": _AUTHORITY_LOCKS,
        "source_artifacts": {
            "slice50_receipt": {
                "path": SLICE50_RECEIPT_PATH,
                "observed": slice50_path.exists(),
                "sha256": _file_hash(slice50_path),
                "canonical_hash": str(
                    (slice50_packet or {}).get("canonical_hash", "NOT_OBSERVED")
                ),
                "status": str((slice50_packet or {}).get("status", "NOT_OBSERVED")),
            },
            "p80_regeneration_plan": {
                "path": P80_REGENERATION_PLAN_PATH,
                "observed": p80_path.exists(),
                "sha256": _file_hash(p80_path),
                "packet_hash": str(p80_packet.get("packet_hash", "NOT_COMPUTABLE")),
                "p80_regeneration_plan_status": str(
                    p80_packet.get("p80_regeneration_plan_status", "NOT_COMPUTABLE")
                ),
            },
        },
        "p80_regeneration_summary": {
            "p80_regeneration_plan_status": str(
                p80_packet.get("p80_regeneration_plan_status", "NOT_COMPUTABLE")
            ),
            "p80_regeneration_required": bool(
                p80_packet.get("p80_regeneration_required", False)
            ),
            "p80_regeneration_allowed": bool(
                p80_packet.get("p80_regeneration_allowed", False)
            ),
            "recommended_next_lane": str(
                p80_packet.get("recommended_next_lane", "NOT_COMPUTABLE")
            ),
            "recommended_next_lane_reason": str(
                p80_packet.get("recommended_next_lane_reason", "NOT_COMPUTABLE")
            ),
            "blocked_regeneration_reasons": list(
                p80_packet.get("blocked_regeneration_reasons", [])
            ),
            "regeneration_reasons": list(p80_packet.get("regeneration_reasons", [])),
            "future_runner_command": str(
                p80_packet.get("future_runner_command", "NOT_COMPUTABLE")
            ),
            "expected_output_path": str(
                p80_packet.get("expected_output_path", "NOT_COMPUTABLE")
            ),
        },
        "boundary": {
            "sandbox_gate_issue": "#892",
            "sandbox_gate_phrase": "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED",
            "sandbox_gate_issued": False,
            "scope_note": (
                "Slice51 records P80 authorization record regeneration planning only; "
                "it does not execute regeneration, create authorization records, "
                "repair evidence, run generators, write back, mutate canon/runtime, "
                "or open sandbox probe activity."
            ),
        },
        "validation_plan": [
            (
                "python scripts/"
                "run_temporal_continuity_p80_authorization_record_"
                "regeneration_receipt.py"
            ),
            (
                "python -m py_compile "
                "core/temporal_continuity_p80_authorization_record_"
                "regeneration_receipt.py "
                "scripts/"
                "run_temporal_continuity_p80_authorization_record_"
                "regeneration_receipt.py"
            ),
            (
                "python -m pytest "
                "tests/"
                "test_temporal_continuity_p80_authorization_record_"
                "regeneration_receipt.py "
                "-q"
            ),
            (
                "python scripts/artifact/run_artifact_regeneration.py --artifact "
                "out/audit/"
                "temporal_continuity_p80_authorization_record_"
                "regeneration_receipt_001.latest.json"
            ),
        ],
        "provenance": (
            "Notion Sprint 001 Hub + Loop 805 Slice 51 + "
            "P80 Temporal Continuity Authorization Record Plan Regeneration Plan"
        ),
    }
    return {**packet_base, "canonical_hash": canonical_hash(packet_base)}


def write_temporal_continuity_p80_authorization_record_regeneration_receipt(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
