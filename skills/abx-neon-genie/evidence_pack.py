"""EvidencePack helpers for Neon Genie — thin facade over core.signal.evidence_pack.

Canonical implementation: ``core.signal.evidence_pack``
Canonical schema: ``contracts/signal/evidence_pack.v0.schema.json``
"""

from __future__ import annotations

# Re-export OS primitive API for importlib stage loaders and legacy imports.
from core.signal.evidence_pack import (  # noqa: F401
    COMMERCIAL_CLAIM_KEYS,
    EVIDENCE_PACK_SCHEMA,
    EVIDENCE_PACK_SCHEMA_VERSION,
    commercial_claims_blocked,
    evidence_density,
    load_evidence_pack_file,
    normalize_evidence_pack,
    redact_commercial_fields,
    register_counts,
    resolve_evidence_for_request,
)

__all__ = [
    "COMMERCIAL_CLAIM_KEYS",
    "EVIDENCE_PACK_SCHEMA",
    "EVIDENCE_PACK_SCHEMA_VERSION",
    "commercial_claims_blocked",
    "evidence_density",
    "load_evidence_pack_file",
    "normalize_evidence_pack",
    "redact_commercial_fields",
    "register_counts",
    "resolve_evidence_for_request",
]
