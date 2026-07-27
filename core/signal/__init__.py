"""Signal OS primitives (EvidencePack).

Spine bridge lives in ``core.signal.spine_bridge`` — import it directly to
avoid package init cycles with ``core.ingest.familiar_ingestion_receipt``.
"""

from core.signal.evidence_pack import (
    EVIDENCE_PACK_SCHEMA,
    EVIDENCE_PACK_SCHEMA_VERSION,
    assert_valid_evidence_pack,
    commercial_claims_blocked,
    evidence_density,
    load_evidence_pack_file,
    load_schema,
    normalize_evidence_pack,
    redact_commercial_fields,
    register_counts,
    resolve_evidence_for_request,
    schema_path,
    validate_evidence_pack,
    validate_path,
)

__all__ = [
    "EVIDENCE_PACK_SCHEMA",
    "EVIDENCE_PACK_SCHEMA_VERSION",
    "assert_valid_evidence_pack",
    "commercial_claims_blocked",
    "evidence_density",
    "load_evidence_pack_file",
    "load_schema",
    "normalize_evidence_pack",
    "redact_commercial_fields",
    "register_counts",
    "resolve_evidence_for_request",
    "schema_path",
    "validate_evidence_pack",
    "validate_path",
]
