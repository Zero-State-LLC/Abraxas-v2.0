"""Governance contradiction map (Phase 2 evidence)."""

from __future__ import annotations

from typing import Any

from core.canonical.json import canonical_hash


def build_governance_contradiction_map() -> dict[str, Any]:
    contradictions = [
        {
            "id": "GC-001",
            "topic": "authorization_packets_for_routine_execution",
            "governance_v3_claim": (
                "Routine engineering does not require authorization packets, eligibility "
                "gates, approval receipts, or operator decision chains "
                "(PLANS.md / GOVERNANCE_V3.md / BOUNDED_PRODUCT_ACTIVATION_001)."
            ),
            "conflicting_claim": (
                "ARCHITECTURE.md: no computation without operator-authorized artifact chains; "
                "authority unlocked through governed artifact chains. README: frozen governance "
                "/ all execution paths require operator review."
            ),
            "resolution": (
                "Adopt bounded activation lanes in core/governance/activation_policy.py. "
                "LOCAL_DEV/SANDBOX: no authorization packet. Preserve EXTERNAL_PRODUCTION "
                "operator gate and SHADOW/FORECAST + canon hard boundaries."
            ),
            "status": "RESOLVED_IN_CODE_AND_DOCS",
            "evidence": [
                "core/governance/activation_policy.py",
                "docs/adr/ADR-0017-BOUNDED-ACTIVATION-POLICY.md",
                "ARCHITECTURE.md",
                "README.md",
            ],
        },
        {
            "id": "GC-002",
            "topic": "production_activation_vocabulary",
            "governance_v3_claim": (
                "Use DEV_ACTIVATION_ALLOWED / SANDBOX_ACTIVATION_ALLOWED / "
                "INTERNAL_CANARY_CONDITIONAL / EXTERNAL_PRODUCTION_OPERATOR_GATED."
            ),
            "conflicting_claim": (
                "STATUS and readiness artifacts often say production activation DENIED as a "
                "blanket phrase without lane qualification."
            ),
            "resolution": (
                "Keep EXTERNAL_PRODUCTION DENIED/operator-gated. Qualify LOCAL_DEV/SANDBOX as "
                "allowed. Do not reinterpret historical DENIED receipts as blocking local work."
            ),
            "status": "PARTIALLY_RESOLVED",
            "evidence": [
                "docs/governance/BOUNDED_PRODUCT_ACTIVATION_001.md",
                "core/production_readiness/production_activation_authority_gate.py",
            ],
        },
        {
            "id": "GC-003",
            "topic": "out_as_canonical_runtime_state",
            "governance_v3_claim": (
                "Historical P70–P130 / operator_review surfaces are archived history, not "
                "required for routine development."
            ),
            "conflicting_claim": (
                "ARCHITECTURE.md treats out/ artifacts as canonical state and authoritative "
                "records for decisions/gates generally."
            ),
            "resolution": (
                "Introduce artifact classes; only CANONICAL_DOMAIN_ARTIFACT and "
                "GOVERNANCE_DECISION influence current state (Phase 5). Document now; "
                "enforce later."
            ),
            "status": "DOCUMENTED_FOR_LATER_PHASE",
            "evidence": [
                "docs/architecture/PRODUCTION_TARGET_ARCHITECTURE_001.md",
                "docs/adr/ADR-0018-ARTIFACT-CLASSIFICATION.md",
            ],
        },
        {
            "id": "GC-004",
            "topic": "alembic_vs_product_spine",
            "governance_v3_claim": "Assimilate into existing systems before creating subsystems.",
            "conflicting_claim": (
                "Risk of treating Alembic as a second OS/kernel because it has registry, "
                "router, fusion, receipts, and CLI."
            ),
            "resolution": (
                "Place Alembic as optional specialist stage on the single golden path; "
                "classify CLI EXPERIMENTAL; reuse Oracle bridge read-only."
            ),
            "status": "RESOLVED_IN_TARGET_ARCHITECTURE",
            "evidence": [
                "docs/architecture/PRODUCTION_TARGET_ARCHITECTURE_001.md",
                "core/application/advisory_spine.py",
                "out/production_convergence/golden_path_trace.v1.json",
            ],
        },
    ]

    payload = {
        "artifact_type": "governance_contradiction_map",
        "schema_version": "governance_contradiction_map.v1",
        "evidence_state": "Partial",
        "summary": {
            "contradiction_count": len(contradictions),
            "resolved_in_this_slice": sum(
                1 for c in contradictions if c["status"].startswith("RESOLVED")
            ),
        },
        "contradictions": contradictions,
        "target_policy_module": "core/governance/activation_policy.py",
    }
    payload["canonical_hash"] = canonical_hash(
        {k: v for k, v in payload.items() if k != "canonical_hash"}
    )
    return payload
