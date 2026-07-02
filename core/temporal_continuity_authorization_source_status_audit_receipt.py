from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.temporal_continuity_authorization_record_plan_source_status_audit import (
    build_temporal_continuity_authorization_record_plan_source_status_audit,
    write_temporal_continuity_authorization_record_plan_source_status_audit,
)

ARTIFACT_TYPE = "TemporalContinuityAuthorizationSourceStatusAuditReceipt.v1"
SLICE_ID = "LOOP-805-SLICE-50"
STATUS = "TEMPORAL_CONTINUITY_AUTHORIZATION_SOURCE_STATUS_AUDIT_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"

P81_OUT_PATH = "out/temporal_continuity_authorization_record_plan_source_status_audit/latest.json"
SLICE49_RECEIPT_PATH = "out/audit/temporal_coherence_evidence_restoration_planning_001.latest.json"
DEFAULT_OUT_PATH = "out/audit/temporal_continuity_authorization_source_status_audit_001.latest.json"

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
    "repair_authority": False,
    "runtime_activation": False,
    "runtime_mutation": False,
    "sandbox_probe_execution": False,
    "temporal_generator_execution": False,
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


def build_temporal_continuity_authorization_source_status_audit_receipt(
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    p81_packet = build_temporal_continuity_authorization_record_plan_source_status_audit(
        repo_root=root
    )
    p81_path = root / P81_OUT_PATH
    write_temporal_continuity_authorization_record_plan_source_status_audit(
        p81_path, p81_packet
    )

    slice49_path = root / SLICE49_RECEIPT_PATH
    slice49_packet = _read_json(slice49_path)

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
            "slice49_receipt": {
                "path": SLICE49_RECEIPT_PATH,
                "observed": slice49_path.exists(),
                "sha256": _file_hash(slice49_path),
                "canonical_hash": str(
                    (slice49_packet or {}).get("canonical_hash", "NOT_OBSERVED")
                ),
                "status": str((slice49_packet or {}).get("status", "NOT_OBSERVED")),
            },
            "p81_source_status_audit": {
                "path": P81_OUT_PATH,
                "observed": p81_path.exists(),
                "sha256": _file_hash(p81_path),
                "packet_hash": str(p81_packet.get("packet_hash", "NOT_COMPUTABLE")),
                "source_chain_status": str(
                    p81_packet.get("source_chain_status", "NOT_COMPUTABLE")
                ),
            },
        },
        "source_chain_summary": {
            "source_chain_status": str(
                p81_packet.get("source_chain_status", "NOT_COMPUTABLE")
            ),
            "recommended_next_lane": str(
                p81_packet.get("recommended_next_lane", "NOT_COMPUTABLE")
            ),
            "recommended_next_lane_reason": str(
                p81_packet.get("recommended_next_lane_reason", "NOT_COMPUTABLE")
            ),
            "not_computable_reasons": list(
                p81_packet.get("not_computable_reasons", [])
            ),
            "source_chain_items": list(p81_packet.get("source_chain_items", [])),
        },
        "boundary": {
            "sandbox_gate_issue": "#892",
            "sandbox_gate_phrase": "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED",
            "sandbox_gate_issued": False,
            "scope_note": (
                "Slice50 records P81 temporal authorization source status only; it "
                "does not authorize repair, regeneration, execution, writeback, "
                "canon mutation, runtime mutation, or sandbox probe activity."
            ),
        },
        "validation_plan": [
            "python Scripts/run_temporal_continuity_authorization_source_status_audit_receipt.py",
            "python -m py_compile core/temporal_continuity_authorization_source_status_audit_receipt.py Scripts/run_temporal_continuity_authorization_source_status_audit_receipt.py",
            "python -m pytest tests/test_temporal_continuity_authorization_source_status_audit_receipt.py -q",
            "python scripts/run_artifact_regeneration.py --artifact out/audit/temporal_continuity_authorization_source_status_audit_001.latest.json",
        ],
        "provenance": (
            "Notion Sprint 001 Hub + Loop 805 Slice 50 + "
            "P81 Temporal Continuity Authorization Record Plan Source Status Audit"
        ),
    }
    return {**packet_base, "canonical_hash": canonical_hash(packet_base)}


def write_temporal_continuity_authorization_source_status_audit_receipt(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
