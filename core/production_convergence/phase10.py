"""Phase 10 writer-migration receipt builder."""

from __future__ import annotations

from typing import Any

from core.canonical.json import canonical_hash

MIGRATED_VIZ_REPLAY_PATHS: tuple[str, ...] = (
    "scripts/viz/run_overlay_observability_replay.py",
    "scripts/viz/run_overlay_risk_replay.py",
    "scripts/viz/run_overlay_containment_replay.py",
    "scripts/viz/run_overlay_readiness_replay.py",
    "scripts/viz/run_overlay_governance_replay.py",
    "scripts/viz/run_overlay_resolution_replay.py",
    "scripts/viz/run_overlay_topology_replay.py",
    "scripts/viz/run_overlay_firewall_replay.py",
)

MIGRATED_WPD_RESEARCH_PATHS: tuple[str, ...] = (
    "scripts/research/run_canary_overlay.py",
    "scripts/research/run_weight_drift_simulation.py",
    "scripts/research/run_canary_promotion_review.py",
    "scripts/research/run_canary_policy_scheduler.py",
    "scripts/research/run_adaptive_sandbox.py",
)

MIGRATED_CANARY_COMPANION_PATHS: tuple[str, ...] = (
    "scripts/research/run_canary_replay.py",
    "scripts/research/run_canary_promotion_replay.py",
    "scripts/research/run_canary_schedule_replay.py",
    "scripts/research/run_canary_rollback.py",
)

MIGRATED_PATHS: tuple[str, ...] = (
    MIGRATED_VIZ_REPLAY_PATHS
    + MIGRATED_WPD_RESEARCH_PATHS
    + MIGRATED_CANARY_COMPANION_PATHS
)

DEFERRED_NOTES: tuple[str, ...] = (
    "run_doctrine_validator.py deferred",
    "research_canary_* surfaces untouched (no spine-refresh / regen)",
    "viz fusion_evidence materialization writers deferred",
    "scripts/research/run_shadow_execution.py deferred",
    "mass deletion still blocked pending CLEAR operator review",
    "live network providers still unauthorized",
)


def build_phase10_writer_migration_receipt() -> dict[str, Any]:
    payload: dict[str, Any] = {
        "artifact_type": "production_convergence_phase10_writer_migration",
        "schema_version": "phase10_writer_migration.v1",
        "evidence_state": "Partial",
        "candidate_status": "NOT_READY",
        "external_production_authorized": False,
        "migration_api": "core.canonical.json.write_classified_json",
        "migrated_paths": list(MIGRATED_PATHS),
        "migrated_viz_replay_paths": list(MIGRATED_VIZ_REPLAY_PATHS),
        "migrated_wpd_research_paths": list(MIGRATED_WPD_RESEARCH_PATHS),
        "migrated_canary_companion_paths": list(MIGRATED_CANARY_COMPANION_PATHS),
        "summary": {
            "migrated_count": len(MIGRATED_PATHS),
            "viz_replay_count": len(MIGRATED_VIZ_REPLAY_PATHS),
            "wpd_research_count": len(MIGRATED_WPD_RESEARCH_PATHS),
            "canary_companion_count": len(MIGRATED_CANARY_COMPANION_PATHS),
            "deferred_notes_count": len(DEFERRED_NOTES),
        },
        "deferred_notes": list(DEFERRED_NOTES),
        "notes": [
            "Import-only migration; operators must re-run writers to refresh on-disk stamps.",
            "CLEAR mass_deletion_authorized remains false.",
            "No research_canary_* regeneration and no live provider adapters added.",
        ],
    }
    payload["canonical_hash"] = canonical_hash(
        {k: v for k, v in payload.items() if k != "canonical_hash"}
    )
    return payload
