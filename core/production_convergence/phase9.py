"""Phase 9 writer-migration receipt builder."""

from __future__ import annotations

from typing import Any

from core.canonical.json import canonical_hash

MIGRATED_REPLAY_PATHS: tuple[str, ...] = (
    "scripts/belief/run_brier_replay.py",
    "scripts/research/run_forecast_replay.py",
    "scripts/ingest/run_intake_replay.py",
    "scripts/governance/run_proposal_decision_bridge_replay.py",
    "scripts/governance/run_review_continuity_replay.py",
    "scripts/governance/run_proposal_sandbox_evaluation_replay.py",
    "scripts/governance/run_proposal_sandbox_routing_replay.py",
    "scripts/operator/run_rune_replay.py",
    "scripts/research/run_drift_replay.py",
    "scripts/research/run_sandbox_replay.py",
    "scripts/research/run_graph_replay.py",
    "scripts/research/run_incremental_replay.py",
)

MIGRATED_VIZ_PATHS: tuple[str, ...] = (
    "scripts/viz/run_overlay_observability.py",
    "scripts/viz/run_overlay_risk_envelope.py",
    "scripts/viz/run_overlay_containment_policy.py",
    "scripts/viz/run_overlay_readiness_index.py",
    "scripts/viz/run_overlay_governance_ledger.py",
    "scripts/viz/run_overlay_resolution_ledger.py",
    "scripts/viz/run_overlay_topology_simulation.py",
    "scripts/viz/run_overlay_execution_firewall.py",
)

MIGRATED_PATHS: tuple[str, ...] = MIGRATED_REPLAY_PATHS + MIGRATED_VIZ_PATHS

DEFERRED_NOTES: tuple[str, ...] = (
    "viz overlay *_replay.py companions deferred to Phase 10+",
    "non-viz WP-D research runners (canary_overlay, weight_drift, etc.) deferred",
    "run_canary_*_replay.py deferred (canary-adjacent)",
    "artifact-contract repair scripts deferred",
    "run_doctrine_validator.py deferred",
    "research_canary_* surfaces untouched",
    "mass deletion still blocked pending CLEAR operator review",
)


def build_phase9_writer_migration_receipt() -> dict[str, Any]:
    payload: dict[str, Any] = {
        "artifact_type": "production_convergence_phase9_writer_migration",
        "schema_version": "phase9_writer_migration.v1",
        "evidence_state": "Partial",
        "candidate_status": "NOT_READY",
        "external_production_authorized": False,
        "migration_api": "core.canonical.json.write_classified_json",
        "migrated_paths": list(MIGRATED_PATHS),
        "migrated_replay_paths": list(MIGRATED_REPLAY_PATHS),
        "migrated_viz_paths": list(MIGRATED_VIZ_PATHS),
        "summary": {
            "migrated_count": len(MIGRATED_PATHS),
            "replay_count": len(MIGRATED_REPLAY_PATHS),
            "viz_count": len(MIGRATED_VIZ_PATHS),
            "deferred_notes_count": len(DEFERRED_NOTES),
        },
        "deferred_notes": list(DEFERRED_NOTES),
        "notes": [
            "Import-only migration; operators must re-run writers to refresh on-disk stamps.",
            "CLEAR reference analysis is advisory-only; mass_deletion_authorized remains false.",
            "No live provider adapters added.",
        ],
    }
    payload["canonical_hash"] = canonical_hash(
        {k: v for k, v in payload.items() if k != "canonical_hash"}
    )
    return payload
