"""Phase 8 writer-migration receipt builder."""

from __future__ import annotations

from typing import Any

from core.canonical.json import canonical_hash

MIGRATED_PATHS: tuple[str, ...] = (
    "scripts/ingest/run_oracle_intake.py",
    "scripts/ingest/run_ingest_scheduler.py",
    "scripts/ingest/run_oracle_execution_boundary.py",
    "scripts/ingest/run_oracle_pre_execution_snapshot.py",
    "scripts/belief/run_brier_ledger.py",
    "scripts/research/run_forecast_candidates.py",
    "scripts/operator/run_operator_approval_queue.py",
    "scripts/operator/run_manual_action_custody.py",
    "scripts/operator/run_human_decision_ledger.py",
    "scripts/operator/run_manual_execution_authorization.py",
    "scripts/operator/run_yggdrasil_runtime.py",
    "scripts/governance/run_proposal_decision_bridge.py",
    "scripts/governance/run_review_continuity_ledger.py",
    "scripts/campaign/run_external_action_proposals.py",
)

DEFERRED_NOTES: tuple[str, ...] = (
    "*_replay.py companions remain on write_canonical_json until a follow-up batch",
    "viz overlay sole-writers deferred",
    "artifact-contract repair scripts deferred",
    "run_doctrine_validator.py deferred",
    "research_canary_* surfaces untouched",
)


def build_phase8_writer_migration_receipt() -> dict[str, Any]:
    payload: dict[str, Any] = {
        "artifact_type": "production_convergence_phase8_writer_migration",
        "schema_version": "phase8_writer_migration.v1",
        "evidence_state": "Partial",
        "candidate_status": "NOT_READY",
        "external_production_authorized": False,
        "migration_api": "core.canonical.json.write_classified_json",
        "provider_seam": {
            "default": "DeniedProvider",
            "fixture": "FixtureProvider",
            "gate": "gated_invoke",
            "network_at_import": False,
            "allow_flag": "ABRAXAS_ALLOW_PROVIDER_INVOKE",
        },
        "migrated_paths": list(MIGRATED_PATHS),
        "summary": {
            "migrated_count": len(MIGRATED_PATHS),
            "deferred_notes_count": len(DEFERRED_NOTES),
        },
        "deferred_notes": list(DEFERRED_NOTES),
        "notes": [
            "Import-only migration; operators must re-run writers to refresh on-disk stamps.",
            "Brier remains telemetry-only; no outcome resolution.",
        ],
    }
    payload["canonical_hash"] = canonical_hash(
        {k: v for k, v in payload.items() if k != "canonical_hash"}
    )
    return payload
