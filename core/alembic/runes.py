"""Alembic rune bindings — reuse canonical runes; proposals stay advisory."""

from __future__ import annotations

from typing import Any

# OBSERVED: live catalog currently has no RUNE.ARCHITECTURE_* entries.
# Adding live catalog runes without pipeline/route bindings fails
# tests/test_yggdrasil_rune_route_binding_matrix.py (unbound_runes == []).
# Therefore Alembic operations bind to existing canonical runes.

OPERATION_TO_EXISTING_RUNES: dict[str, tuple[str, ...]] = {
    "ARCHITECTURE_DESCRIBE": ("RUNE.PIPELINE.PARSE", "RUNE.PIPELINE.RECEIPT"),
    "ARCHITECTURE_ELIGIBILITY": ("RUNE.PIPELINE.VALIDATE", "RUNE.GOVERNANCE.AUTHORITY_GATE"),
    "PARADIGM_ROUTE": ("RUNE.PIPELINE.ROUTE", "RUNE.YGGDRASIL.ROUTE_RECEIPT"),
    "HYBRID_PLAN": ("RUNE.PIPELINE.ROUTE", "RUNE.PIPELINE.VALIDATE"),
    "CONTRIBUTION_NORMALIZE": ("RUNE.PIPELINE.IR_BUILD", "RUNE.PIPELINE.VALIDATE"),
    "SYMBOLIC_VERIFY": ("RUNE.PIPELINE.VALIDATE", "RUNE.PIPELINE.POSITIVE_PROOF", "RUNE.PIPELINE.NEGATIVE_PROOF"),
    "EVIDENCE_FUSE": ("RUNE.PIPELINE.CONFLICT_SCAN", "RUNE.PIPELINE.RECEIPT"),
    "ARCHITECTURE_SCORE": ("RUNE.PIPELINE.RECEIPT", "RUNE.GOVERNANCE.INVARIANCE_GATE"),
    "ROUTER_ABSTAIN": ("RUNE.GOVERNANCE.NOT_COMPUTABLE_GATE", "RUNE.PIPELINE.OPERATOR_REVIEW"),
    "SHADOW_COMPARE": ("RUNE.PIPELINE.CONFLICT_SCAN", "RUNE.GOVERNANCE.FORECAST_GATE"),
    "ROUTER_CHANGE_PROPOSE": ("RUNE.PIPELINE.OPERATOR_REVIEW", "RUNE.GOVERNANCE.RUNTIME_MUTATION_LOCK"),
}

# Proposed Alembic-native runes (NOT in live catalog until binding authorized).
PROPOSED_ALEMBIC_RUNES: tuple[dict[str, Any], ...] = (
    {
        "rune_id": "RUNE.ARCHITECTURE_DESCRIBE",
        "maps_to": OPERATION_TO_EXISTING_RUNES["ARCHITECTURE_DESCRIBE"],
        "status": "PROPOSED_ADVISORY",
    },
    {
        "rune_id": "RUNE.ARCHITECTURE_ELIGIBILITY",
        "maps_to": OPERATION_TO_EXISTING_RUNES["ARCHITECTURE_ELIGIBILITY"],
        "status": "PROPOSED_ADVISORY",
    },
    {
        "rune_id": "RUNE.PARADIGM_ROUTE",
        "maps_to": OPERATION_TO_EXISTING_RUNES["PARADIGM_ROUTE"],
        "status": "PROPOSED_ADVISORY",
    },
    {
        "rune_id": "RUNE.HYBRID_PLAN",
        "maps_to": OPERATION_TO_EXISTING_RUNES["HYBRID_PLAN"],
        "status": "PROPOSED_ADVISORY",
    },
    {
        "rune_id": "RUNE.CONTRIBUTION_NORMALIZE",
        "maps_to": OPERATION_TO_EXISTING_RUNES["CONTRIBUTION_NORMALIZE"],
        "status": "PROPOSED_ADVISORY",
    },
    {
        "rune_id": "RUNE.SYMBOLIC_VERIFY",
        "maps_to": OPERATION_TO_EXISTING_RUNES["SYMBOLIC_VERIFY"],
        "status": "PROPOSED_ADVISORY",
    },
    {
        "rune_id": "RUNE.EVIDENCE_FUSE",
        "maps_to": OPERATION_TO_EXISTING_RUNES["EVIDENCE_FUSE"],
        "status": "PROPOSED_ADVISORY",
    },
    {
        "rune_id": "RUNE.ARCHITECTURE_SCORE",
        "maps_to": OPERATION_TO_EXISTING_RUNES["ARCHITECTURE_SCORE"],
        "status": "PROPOSED_ADVISORY",
    },
    {
        "rune_id": "RUNE.ROUTER_ABSTAIN",
        "maps_to": OPERATION_TO_EXISTING_RUNES["ROUTER_ABSTAIN"],
        "status": "PROPOSED_ADVISORY",
    },
    {
        "rune_id": "RUNE.SHADOW_COMPARE",
        "maps_to": OPERATION_TO_EXISTING_RUNES["SHADOW_COMPARE"],
        "status": "PROPOSED_ADVISORY",
    },
    {
        "rune_id": "RUNE.ROUTER_CHANGE_PROPOSE",
        "maps_to": OPERATION_TO_EXISTING_RUNES["ROUTER_CHANGE_PROPOSE"],
        "status": "PROPOSED_ADVISORY",
    },
)


def rune_bindings_for_operation(operation: str) -> tuple[str, ...]:
    return OPERATION_TO_EXISTING_RUNES.get(operation, ("RUNE.PIPELINE.RECEIPT",))


def proposed_rune_manifest() -> dict[str, Any]:
    return {
        "schema_version": "AlembicRuneProposalManifest.v1",
        "status": "ADVISORY_PROPOSALS_ONLY",
        "live_catalog_mutation": False,
        "reason": (
            "Live catalog additions require YGGDRASIL pipeline/route bindings; "
            "unbound runes fail closed under coupling-map invariants."
        ),
        "operations": OPERATION_TO_EXISTING_RUNES,
        "proposed_runes": list(PROPOSED_ALEMBIC_RUNES),
        "FINAL_STATUS": "ALEMBIC_SPINE_ADVISORY_ONLY",
    }
