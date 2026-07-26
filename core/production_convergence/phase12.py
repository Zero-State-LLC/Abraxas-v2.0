"""Phase 12 writer-migration + CLEAR review receipt builder."""

from __future__ import annotations

from typing import Any

from core.canonical.json import canonical_hash

MIGRATED_OPERATOR_PATHS: tuple[str, ...] = (
    "scripts/operator/run_human_decision_continuity.py",
    "scripts/operator/run_manual_execution_receipt_ledger.py",
)

MIGRATED_GOVERNANCE_AUDIT_PATHS: tuple[str, ...] = (
    "scripts/governance/run_governance_resilience_closure_audit.py",
    "scripts/research/run_mutation_pressure_replay_resilience_audit.py",
)

MIGRATED_SPINE_PATHS: tuple[str, ...] = (
    "scripts/alembic/run_alembic_spine.py",
    "scripts/belief/run_belief_graph_engine.py",
    "scripts/temporal/run_milestone_continuity.py",
    "scripts/temporal/run_temporal_coherence_chain.py",
)

MIGRATED_SUPPORT_PATHS: tuple[str, ...] = (
    "scripts/ingest/run_controlled_ingest_scheduler_governance_audit.py",
    "scripts/notion/run_sync_snapshot.py",
    "scripts/tools/run_scripts_ghost_path_inventory.py",
)

MIGRATED_PATHS: tuple[str, ...] = (
    MIGRATED_OPERATOR_PATHS
    + MIGRATED_GOVERNANCE_AUDIT_PATHS
    + MIGRATED_SPINE_PATHS
    + MIGRATED_SUPPORT_PATHS
)

DEFERRED_NOTES: tuple[str, ...] = (
    "artifact-contract repair runners remain on legacy writer (27 scripts)",
    "research_canary_* surfaces untouched (no spine-refresh / regen)",
    "mass deletion still blocked pending dual-control CLEAR operator disposition",
    "live network providers still unauthorized (DeniedProvider/FixtureProvider default)",
    "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED remains unissued",
)


def build_phase12_writer_migration_receipt() -> dict[str, Any]:
    payload: dict[str, Any] = {
        "artifact_type": "production_convergence_phase12_writer_migration",
        "schema_version": "phase12_writer_migration.v1",
        "evidence_state": "Partial",
        "candidate_status": "NOT_READY",
        "external_production_authorized": False,
        "mass_deletion_authorized": False,
        "clear_operator_disposition_status": "PENDING_OPERATOR",
        "migration_api": "core.canonical.json.write_classified_json",
        "migrated_paths": list(MIGRATED_PATHS),
        "migrated_operator_paths": list(MIGRATED_OPERATOR_PATHS),
        "migrated_governance_audit_paths": list(MIGRATED_GOVERNANCE_AUDIT_PATHS),
        "migrated_spine_paths": list(MIGRATED_SPINE_PATHS),
        "migrated_support_paths": list(MIGRATED_SUPPORT_PATHS),
        "summary": {
            "migrated_count": len(MIGRATED_PATHS),
            "operator_count": len(MIGRATED_OPERATOR_PATHS),
            "governance_audit_count": len(MIGRATED_GOVERNANCE_AUDIT_PATHS),
            "spine_count": len(MIGRATED_SPINE_PATHS),
            "support_count": len(MIGRATED_SUPPORT_PATHS),
            "deferred_notes_count": len(DEFERRED_NOTES),
        },
        "deferred_notes": list(DEFERRED_NOTES),
        "notes": [
            "Import-only migration; operators must re-run writers to refresh on-disk stamps.",
            "CLEAR operator-review packet remains PENDING_OPERATOR; no deletions authorized.",
            "No research_canary_* regeneration and no live provider adapters added.",
        ],
    }
    payload["canonical_hash"] = canonical_hash(
        {k: v for k, v in payload.items() if k != "canonical_hash"}
    )
    return payload
