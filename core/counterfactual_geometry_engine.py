from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_hash

SCHEMA_VERSION = "CounterfactualGeometryEngine.v1"

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


class CounterfactualGeometryEngineValidationError(ValueError):
    pass


def _finalize(item: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _preimage(item: dict[str, Any]) -> dict[str, Any]:
    out = dict(item)
    out.pop("canonical_hash", None)
    return out


def build_counterfactual_geometry_engine(payload: dict[str, Any]) -> dict[str, Any]:
    required = {"item_id", "title", "observed_summary", "governance_flags", "provenance", "created_at_utc"}
    missing = sorted(required - payload.keys())
    if missing:
        raise CounterfactualGeometryEngineValidationError(f"missing_required_fields:{missing}")

    flags = payload["governance_flags"]
    for flag in LOCKED_FALSE_FLAGS:
        if flags.get(flag) is not False:
            raise CounterfactualGeometryEngineValidationError(f"authority_lock_must_be_false:{flag}")

    base = {**payload, "schema_version": SCHEMA_VERSION}
    canonical = canonical_hash(_preimage(base))
    return _finalize({**base, "canonical_hash": canonical})
