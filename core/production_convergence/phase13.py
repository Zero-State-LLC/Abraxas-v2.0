"""Phase 13 writer-migration receipt builder (artifact-contract residuals)."""

from __future__ import annotations

from typing import Any

from core.canonical.json import canonical_hash

MIGRATED_INVENTORY_PATHS: tuple[str, ...] = (
    "scripts/artifact/run_artifact_contract_inventory.py",
    "scripts/artifact/run_artifact_contract_inventory_audit.py",
    "scripts/artifact/run_artifact_contract_inventory_triage.py",
    "scripts/artifact/run_artifact_contract_global_closure_audit.py",
    "scripts/artifact/run_artifact_contract_canon_sync_receipt.py",
    "scripts/artifact/run_artifact_contract_post_closure_operator_receipt.py",
)

MIGRATED_P0_P1_PATHS: tuple[str, ...] = (
    "scripts/artifact/run_artifact_contract_p0_repair_report.py",
    "scripts/artifact/run_artifact_contract_p1_triage.py",
    "scripts/artifact/run_artifact_contract_p1a_alignment_report.py",
    "scripts/artifact/run_artifact_contract_p1a_missing_artifact_repair.py",
    "scripts/artifact/run_artifact_contract_p1a_missing_replay_repair.py",
    "scripts/artifact/run_artifact_contract_p1a_repair_report.py",
    "scripts/artifact/run_artifact_contract_p1a_unresolved_drilldown.py",
    "scripts/artifact/run_artifact_contract_p1c_scoping.py",
)

MIGRATED_P2_PATHS: tuple[str, ...] = (
    "scripts/artifact/run_artifact_contract_p2_backlog_triage.py",
    "scripts/artifact/run_artifact_contract_p2a_naming_normalization.py",
    "scripts/artifact/run_artifact_contract_p2c_a_minimal_coverage.py",
    "scripts/artifact/run_artifact_contract_p2c_b_deferred_coverage.py",
    "scripts/artifact/run_artifact_contract_p2c_optional_coverage_triage.py",
    "scripts/artifact/run_artifact_contract_p2c_d_manual_review_triage.py",
    "scripts/artifact/run_artifact_contract_p2c_d1_minimal_implementation.py",
    "scripts/artifact/run_artifact_contract_p2c_d2_deferred_conversion.py",
    "scripts/artifact/run_artifact_contract_p2c_d3_keep_optional.py",
    "scripts/artifact/run_artifact_contract_p2c_d4_archive_candidate.py",
    "scripts/artifact/run_artifact_contract_p2c_d5_approval_repair_reverify.py",
    "scripts/artifact/run_artifact_contract_p2c_d5_human_approval.py",
    "scripts/artifact/run_artifact_contract_p2c_d5_operator_decision.py",
)

MIGRATED_PATHS: tuple[str, ...] = (
    MIGRATED_INVENTORY_PATHS + MIGRATED_P0_P1_PATHS + MIGRATED_P2_PATHS
)

DEFERRED_NOTES: tuple[str, ...] = (
    "research_canary_* surfaces untouched (no spine-refresh / regen)",
    "mass deletion still blocked pending dual-control CLEAR operator disposition",
    "live network providers still unauthorized (DeniedProvider/FixtureProvider default)",
    "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED remains unissued",
)


def build_phase13_writer_migration_receipt() -> dict[str, Any]:
    payload: dict[str, Any] = {
        "artifact_type": "production_convergence_phase13_writer_migration",
        "schema_version": "phase13_writer_migration.v1",
        "evidence_state": "Partial",
        "candidate_status": "NOT_READY",
        "external_production_authorized": False,
        "mass_deletion_authorized": False,
        "clear_operator_disposition_status": "PENDING_OPERATOR",
        "migration_api": "core.canonical.json.write_classified_json",
        "migrated_paths": list(MIGRATED_PATHS),
        "migrated_inventory_paths": list(MIGRATED_INVENTORY_PATHS),
        "migrated_p0_p1_paths": list(MIGRATED_P0_P1_PATHS),
        "migrated_p2_paths": list(MIGRATED_P2_PATHS),
        "summary": {
            "migrated_count": len(MIGRATED_PATHS),
            "inventory_count": len(MIGRATED_INVENTORY_PATHS),
            "p0_p1_count": len(MIGRATED_P0_P1_PATHS),
            "p2_count": len(MIGRATED_P2_PATHS),
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
