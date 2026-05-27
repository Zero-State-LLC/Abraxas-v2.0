from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

CLASSIFICATIONS = {
    "SHADOW_ONLY",
    "FORECAST_RELEVANT",
    "PROJECTION_ONLY",
    "IMPLEMENTATION_READY",
    "THEORY_ONLY",
    "VISUALIZATION_READY",
    "GOVERNANCE_SENSITIVE",
}

ARCHITECTURE_TARGETS = {
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

_GOV_FALSE = (
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


def _validate(item: dict[str, Any]) -> None:
    if item.get("classification") not in CLASSIFICATIONS:
        raise ValueError("unknown classification")
    if any(t not in ARCHITECTURE_TARGETS for t in item.get("architecture_targets", [])):
        raise ValueError("unknown architecture target")
    gov = item.get("governance_flags", {})
    for key in _GOV_FALSE:
        if gov.get(key) is not False:
            raise ValueError(f"governance_flags.{key} must be false")


def compute_geometric_research_item_hash(item_without_hash: dict[str, Any]) -> str:
    body = {k: v for k, v in item_without_hash.items() if k != "canonical_hash"}
    return canonical_hash(body)


def canonicalize_geometric_research_item(item: dict[str, Any]) -> dict[str, Any]:
    _validate(item)
    body = {k: v for k, v in item.items() if k != "canonical_hash"}
    hashed = {**body, "canonical_hash": compute_geometric_research_item_hash(body)}
    return json.loads(canonical_dumps(hashed))


def build_geometric_research_item(*, item_id: str, title: str, source_type: str, source_ref: str, observed_summary: str, extracted_concepts: list[str], architecture_targets: list[str], candidate_modules: list[str], classification: str, provenance: dict[str, Any], created_at_utc: str, schema_version: str = "GeometricResearchItem.v1") -> dict[str, Any]:
    item = {
        "schema_version": schema_version,
        "item_id": item_id,
        "title": title,
        "source_type": source_type,
        "source_ref": source_ref,
        "observed_summary": observed_summary,
        "extracted_concepts": extracted_concepts,
        "architecture_targets": architecture_targets,
        "candidate_modules": candidate_modules,
        "classification": classification,
        "governance_flags": {k: False for k in _GOV_FALSE},
        "provenance": provenance,
        "created_at_utc": created_at_utc,
    }
    return canonicalize_geometric_research_item(item)


def validate_geometric_research_item(item: dict[str, Any]) -> None:
    _validate(item)
    expected = compute_geometric_research_item_hash(item)
    if item.get("canonical_hash") != expected:
        raise ValueError("canonical_hash mismatch")


def serialize_geometric_research_item(item: dict[str, Any]) -> str:
    validate_geometric_research_item(item)
    return canonical_dumps(item) + "\n"
