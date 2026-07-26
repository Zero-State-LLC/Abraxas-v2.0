"""Phase 11 writer-migration receipt builder."""

from __future__ import annotations

from typing import Any

from core.canonical.json import canonical_hash

MIGRATED_DOCTRINE_PATHS: tuple[str, ...] = (
    "scripts/governance/run_doctrine_validator.py",
)

MIGRATED_FUSION_PATHS: tuple[str, ...] = (
    "scripts/viz/run_fusion_evidence_materialization.py",
    "scripts/viz/run_fusion_evidence_materialization_seal.py",
)

MIGRATED_SHADOW_PATHS: tuple[str, ...] = ("scripts/research/run_shadow_execution.py",)

MIGRATED_GOVERNANCE_SPINE_PATHS: tuple[str, ...] = (
    "scripts/governance/run_proposal_sandbox_evaluation.py",
    "scripts/governance/run_proposal_sandbox_routing.py",
    "scripts/governance/run_review_resolution_spine.py",
)

MIGRATED_PATHS: tuple[str, ...] = (
    MIGRATED_DOCTRINE_PATHS
    + MIGRATED_FUSION_PATHS
    + MIGRATED_SHADOW_PATHS
    + MIGRATED_GOVERNANCE_SPINE_PATHS
)

DEFERRED_NOTES: tuple[str, ...] = (
    "research_canary_* surfaces untouched (no spine-refresh / regen)",
    "artifact-contract repair runners remain on legacy writer",
    "mass deletion still blocked pending CLEAR operator review",
    "live network providers still unauthorized",
    "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED remains unissued",
)


def build_phase11_writer_migration_receipt() -> dict[str, Any]:
    payload: dict[str, Any] = {
        "artifact_type": "production_convergence_phase11_writer_migration",
        "schema_version": "phase11_writer_migration.v1",
        "evidence_state": "Partial",
        "candidate_status": "NOT_READY",
        "external_production_authorized": False,
        "migration_api": "core.canonical.json.write_classified_json",
        "migrated_paths": list(MIGRATED_PATHS),
        "migrated_doctrine_paths": list(MIGRATED_DOCTRINE_PATHS),
        "migrated_fusion_paths": list(MIGRATED_FUSION_PATHS),
        "migrated_shadow_paths": list(MIGRATED_SHADOW_PATHS),
        "migrated_governance_spine_paths": list(MIGRATED_GOVERNANCE_SPINE_PATHS),
        "summary": {
            "migrated_count": len(MIGRATED_PATHS),
            "doctrine_count": len(MIGRATED_DOCTRINE_PATHS),
            "fusion_count": len(MIGRATED_FUSION_PATHS),
            "shadow_count": len(MIGRATED_SHADOW_PATHS),
            "governance_spine_count": len(MIGRATED_GOVERNANCE_SPINE_PATHS),
            "deferred_notes_count": len(DEFERRED_NOTES),
        },
        "deferred_notes": list(DEFERRED_NOTES),
        "notes": [
            "Import-only migration; operators must re-run writers to refresh on-disk stamps.",
            "CLEAR mass_deletion_authorized remains false; operator review still required.",
            "No research_canary_* regeneration and no live provider adapters added.",
        ],
    }
    payload["canonical_hash"] = canonical_hash(
        {k: v for k, v in payload.items() if k != "canonical_hash"}
    )
    return payload
