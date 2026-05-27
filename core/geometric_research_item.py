from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_hash

SCHEMA_VERSION = "GeometricResearchItem.v1"

ALLOWED_CLASSIFICATIONS = {
    "SHADOW_ONLY",
    "FORECAST_RELEVANT",
    "PROJECTION_ONLY",
    "IMPLEMENTATION_READY",
    "THEORY_ONLY",
    "VISUALIZATION_READY",
    "GOVERNANCE_SENSITIVE",
}

ALLOWED_ARCHITECTURE_TARGETS = {
    "ORACLE_SIGNAL_LAYER",
    "AAL_VIZ",
    "YGGDRASIL",
    "ABX_RUNES",
    "P27_P28_TEMPORAL_CONTINUITY",
    "RESERVOIR_RUNTIME",
    "PROJECTION_RUNTIME",
    "DRIFT_DETECTION",
    "SIGNAL_COMPRESSION",
    "MULTI_DOMAIN_ANALYSIS",
    "GEOMETRIC_INTELLIGENCE_RUNTIME",
}

LOCKED_FALSE_FLAGS = (
    "production_activation",
    "canon_promotion",
    "scheduler_mutation",
    "runtime_authority",
    "runtime_mutation",
    "forecast_influence",
    "execution_authority",
    "token_minting_allowed",
    "valid_for_execution",
    "activation_approved",
    "authorization_granted",
)


class GeometricResearchItemValidationError(ValueError):
    pass


def _finalize(item: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _preimage(item: dict[str, Any]) -> dict[str, Any]:
    out = dict(item)
    out.pop("canonical_hash", None)
    return out


def build_geometric_research_item(payload: dict[str, Any]) -> dict[str, Any]:
    required = {
        "item_id", "title", "source_type", "source_ref", "observed_summary", "extracted_concepts",
        "architecture_targets", "candidate_modules", "classification", "governance_flags", "provenance", "created_at_utc"
    }
    missing = sorted(required - payload.keys())
    if missing:
        raise GeometricResearchItemValidationError(f"missing_required_fields:{missing}")

    if payload["classification"] not in ALLOWED_CLASSIFICATIONS:
        raise GeometricResearchItemValidationError("unknown_classification")

    targets = payload["architecture_targets"]
    if not isinstance(targets, list) or not targets:
        raise GeometricResearchItemValidationError("architecture_targets_must_be_non_empty_list")
    unknown_targets = [target for target in targets if target not in ALLOWED_ARCHITECTURE_TARGETS]
    if unknown_targets:
        raise GeometricResearchItemValidationError(f"unknown_architecture_targets:{unknown_targets}")

    flags = payload["governance_flags"]
    for flag in LOCKED_FALSE_FLAGS:
        if flags.get(flag) is not False:
            raise GeometricResearchItemValidationError(f"authority_lock_must_be_false:{flag}")

    base = {**payload, "schema_version": SCHEMA_VERSION}
    canonical = canonical_hash(_preimage(base))
    return _finalize({**base, "canonical_hash": canonical})
