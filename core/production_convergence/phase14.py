"""Phase 14 receipt: CLEAR disposition draft + research_canary writer migration."""

from __future__ import annotations

from typing import Any

from core.canonical.json import canonical_hash

MIGRATED_RESEARCH_CANARY_PATHS: tuple[str, ...] = (
    "scripts/research/run_research_canary_artifact_spine_refresh.py",
)

MIGRATED_PATHS: tuple[str, ...] = MIGRATED_RESEARCH_CANARY_PATHS

DEFERRED_NOTES: tuple[str, ...] = (
    "research_canary_* artifacts not regenerated (spine-refresh isolation guardrail)",
    "CLEAR dual-control attestations still pending (mass_deletion_authorized false)",
    "live network providers still unauthorized (DeniedProvider/FixtureProvider default)",
    "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED remains unissued",
)


def build_phase14_receipt() -> dict[str, Any]:
    payload: dict[str, Any] = {
        "artifact_type": "production_convergence_phase14_clear_disposition_and_canary_writer",
        "schema_version": "phase14_clear_disposition_and_canary_writer.v1",
        "evidence_state": "Partial",
        "candidate_status": "NOT_READY",
        "external_production_authorized": False,
        "mass_deletion_authorized": False,
        "deletions_executed": False,
        "clear_operator_disposition_status": "PENDING_OPERATOR",
        "clear_engineering_disposition_status": "DRAFT_ISSUED",
        "dual_control_required": True,
        "migration_api": "core.canonical.json.write_classified_json",
        "migrated_paths": list(MIGRATED_PATHS),
        "migrated_research_canary_paths": list(MIGRATED_RESEARCH_CANARY_PATHS),
        "clear_disposition_draft_path": (
            "out/production_convergence/clear_disposition_draft.v1.json"
        ),
        "summary": {
            "migrated_count": len(MIGRATED_PATHS),
            "research_canary_count": len(MIGRATED_RESEARCH_CANARY_PATHS),
            "deferred_notes_count": len(DEFERRED_NOTES),
            "deletion_proposed_count": 0,
        },
        "deferred_notes": list(DEFERRED_NOTES),
        "notes": [
            "Import-only canary writer migration; spine-refresh was not executed.",
            "CLEAR disposition draft issued for operator dual-control; no deletions.",
            "P129/P130 research_canary hold artifacts left untouched.",
        ],
    }
    payload["canonical_hash"] = canonical_hash(
        {k: v for k, v in payload.items() if k != "canonical_hash"}
    )
    return payload
