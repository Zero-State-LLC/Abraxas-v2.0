"""Duplicate architectural-responsibility clusters (Phase 1.3)."""

from __future__ import annotations

from typing import Any

from core.canonical.json import canonical_hash


def build_duplication_clusters() -> dict[str, Any]:
    clusters: list[dict[str, Any]] = [
        {
            "responsibility": "canonical_serialization_and_hashing",
            "implementations": [
                "core/canonical/json.py",
            ],
            "callers": ["scripts/*", "core/* builders", "core/alembic/*"],
            "behavioral_differences": "None observed for the supported writer path.",
            "canonical_candidate": "core/canonical/json.py",
            "migration_difficulty": "LOW",
            "deletion_risk": "HIGH if bypassed rather than removed",
            "recommended_action": ["KEEP"],
            "notes": "WS1 SUPPORTED. Residual ad-hoc json.dumps may exist outside governed writers.",
        },
        {
            "responsibility": "activation_and_authority_policy",
            "implementations": [
                "core/governance/activation_policy.py",
                "docs/governance/BOUNDED_PRODUCT_ACTIVATION_001.md",
                "GOVERNANCE_V3.md",
                "core/production_readiness/production_activation_authority_gate.py",
                "ARCHITECTURE.md (reconciled to lane-based activation in Phase 0–2)",
                "README.md (reconciled to Governance V3 lanes in Phase 0–2)",
            ],
            "callers": ["documentation", "readiness producers", "future runtime gates"],
            "behavioral_differences": (
                "Code+docs now share lane-based activation. "
                "production_activation_authority_gate remains fail-closed for "
                "EXTERNAL_PRODUCTION only and must not block local engineering."
            ),
            "canonical_candidate": "core/governance/activation_policy.py",
            "migration_difficulty": "LOW",
            "deletion_risk": "MEDIUM",
            "recommended_action": ["KEEP", "ADAPT"],
            "notes": (
                "KEEP activation_policy + EXTERNAL_PRODUCTION gate; continue wiring "
                "lane checks into CLI/API startup in later phases."
            ),
        },
        {
            "responsibility": "fastapi_app_construction",
            "implementations": [
                "apps/api/main.py",
                "api/hybrid_server.py",
                "api/sse_server.py",
                "api/websocket_server.py",
            ],
            "callers": ["operators", "tests/test_api.py"],
            "behavioral_differences": (
                "apps/api is the readiness-tracked service surface; api/* are alternate servers."
            ),
            "canonical_candidate": "apps/api/main.py",
            "migration_difficulty": "MEDIUM",
            "deletion_risk": "MEDIUM",
            "recommended_action": ["KEEP", "MERGE", "DEPRECATE"],
        },
        {
            "responsibility": "public_interface_registry",
            "implementations": [
                "core/production_readiness/interface_registry.py",
                "core/production_convergence/inventory.py (interface inventory)",
                "out/production_readiness/baseline/interface_inventory.v1.json",
            ],
            "callers": ["readiness runners", "convergence audit"],
            "behavioral_differences": (
                "WS1 registry is promotion-attested; convergence inventory is audit-oriented "
                "and must assimilate WS1 rather than fork promotion authority."
            ),
            "canonical_candidate": "core/production_readiness/interface_registry.py",
            "migration_difficulty": "LOW",
            "deletion_risk": "LOW",
            "recommended_action": ["KEEP", "ADAPT"],
        },
        {
            "responsibility": "oracle_orchestration",
            "implementations": [
                "core/oracle_signal*.py",
                "core/alembic/oracle_bridge.py",
                "scripts/ingest/run_oracle_*.py",
            ],
            "callers": ["ingest runners", "alembic bridge", "operator review"],
            "behavioral_differences": (
                "Alembic bridge is read-only metadata projection; Oracle remains intake owner."
            ),
            "canonical_candidate": "core/oracle_signal.py + ingest runners",
            "migration_difficulty": "MEDIUM",
            "deletion_risk": "HIGH",
            "recommended_action": ["KEEP", "ADAPT"],
            "notes": "Do not create a second ingest pipeline via Alembic.",
        },
        {
            "responsibility": "multi_architecture_routing_and_fusion",
            "implementations": [
                "core/alembic/*",
                "historical meta-opt / campaign surfaces (research)",
            ],
            "callers": ["scripts/alembic/run_alembic_spine.py", "oracle_bridge consumers"],
            "behavioral_differences": "Alembic is the advisory specialist for architecture selection.",
            "canonical_candidate": "core/alembic/",
            "migration_difficulty": "LOW",
            "deletion_risk": "LOW",
            "recommended_action": ["KEEP", "ADAPT"],
            "notes": "Fit as optional stage on golden path; not a parallel product spine.",
        },
        {
            "responsibility": "runtime_path_configuration",
            "implementations": [
                "core/config.py (RuntimePaths)",
                "scattered os.environ reads (NOT_COMPUTABLE full inventory in this slice)",
            ],
            "callers": ["runners"],
            "behavioral_differences": "RuntimePaths covers filesystem layout, not full DI/settings.",
            "canonical_candidate": "core/settings.py RuntimeSettings + core/runtime_context.py ports",
            "migration_difficulty": "HIGH",
            "deletion_risk": "HIGH",
            "recommended_action": ["KEEP", "ADAPT"],
        },
        {
            "responsibility": "cli_entrypoint_surface",
            "implementations": [
                "scripts/run_fast_ci.py",
                "712 scripts/**/run_*.py runners",
                "missing unified abraxas CLI",
            ],
            "callers": ["operators", "CI", "agents"],
            "behavioral_differences": "No single product CLI; domain runners dominate.",
            "canonical_candidate": "future abraxas CLI tree; keep run_fast_ci SUPPORTED",
            "migration_difficulty": "HIGH",
            "deletion_risk": "HIGH",
            "recommended_action": ["KEEP", "MERGE", "DEPRECATE"],
        },
        {
            "responsibility": "authority_lock_evaluation",
            "implementations": [
                "core/governance/authority.py",
                "schema authority_locks on artifacts",
                "historical operator decision chains under out/operator_review/",
            ],
            "callers": ["builders", "validators"],
            "behavioral_differences": (
                "Authority locks remain valid for SHADOW/FORECAST and canon mutation; "
                "they are not substitutes for activation-lane policy."
            ),
            "canonical_candidate": "core/governance/authority.py + activation_policy.py",
            "migration_difficulty": "MEDIUM",
            "deletion_risk": "HIGH",
            "recommended_action": ["KEEP", "ADAPT"],
        },
    ]

    payload = {
        "artifact_type": "duplication_clusters",
        "schema_version": "duplication_clusters.v1",
        "evidence_state": "Partial",
        "summary": {
            "cluster_count": len(clusters),
            "keep": sum(1 for c in clusters if "KEEP" in c["recommended_action"]),
            "merge_or_adapt": sum(
                1
                for c in clusters
                if "MERGE" in c["recommended_action"] or "ADAPT" in c["recommended_action"]
            ),
        },
        "clusters": clusters,
        "not_computable": [
            (
                "Complete repo-wide enumeration of every json.dumps / os.environ / network "
                "client bypass — requires dedicated scanners beyond this Phase 1 slice."
            )
        ],
    }
    payload["canonical_hash"] = canonical_hash(
        {k: v for k, v in payload.items() if k != "canonical_hash"}
    )
    return payload
