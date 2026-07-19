"""Build the TRANSPORT fixture corpus creation receipt artifact.

Reads all 15 fixture files from disk, verifies their canonical hashes,
and emits a receipt confirming corpus creation is complete.
No metric values emitted. No LP solver invocation. SHADOW lane only.
"""
from __future__ import annotations

import json
import pathlib
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "TransportFixtureCorpusCreationReceipt.v1"
RECEIPT_ID = "transport_fixture_corpus_creation_receipt_001"
RECEIPT_STATUS = "TRANSPORT_FIXTURE_CORPUS_CREATION_COMPLETE"
OPERATOR_ID = "TRANSPORT"

SOURCE_FIXTURE_PLAN_HASH = (
    "90183e52f9bc2602df88073f4cdfc1f82d61c764741cc539729ff0bb4001799f"
)
SOURCE_IMPLEMENTATION_GATE_HASH = (
    "a5b9691e0ff410b512c725075cc3108141b941b0f22da58441772589a3467eb0"
)

FIXTURE_BASE_PATH = pathlib.Path("input/fixtures/transport")

FIXTURE_IDS_VALID = (
    "tv-valid-001",
    "tv-valid-002",
    "tv-valid-003",
    "tv-valid-004",
    "tv-valid-005",
    "tv-valid-006",
)
FIXTURE_IDS_INVALID = (
    "tv-invalid-001",
    "tv-invalid-002",
    "tv-invalid-003",
    "tv-invalid-004",
)
FIXTURE_IDS_NC = (
    "tv-nc-001",
    "tv-nc-002",
    "tv-nc-003",
    "tv-nc-004",
    "tv-nc-005",
)
ALL_FIXTURE_IDS = FIXTURE_IDS_VALID + FIXTURE_IDS_INVALID + FIXTURE_IDS_NC

CREATED_AT_UTC = "2026-05-30T00:00:00Z"
RECOMMENDED_NEXT_STEP = "TRANSPORT_COMPUTATION_IMPLEMENTATION"

FORBIDDEN = (
    "executable", "callable", "runtime", "scheduler", "cache",
    "forecast", "scoring", "metric-computation", "metric-value",
    "geodesic-distance", "numpy", "scipy", "gpu-kernel",
    "dijkstra-execution", "shortest-path-computation",
    "fixture-file", "manifest-file", "schema-file",
)


class TransportFixtureCorpusCreationReceiptError(ValueError):
    pass


def _check_no_forbidden(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _check_no_forbidden(x)
    elif isinstance(v, list):
        for x in v:
            _check_no_forbidden(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise TransportFixtureCorpusCreationReceiptError(
            f"forbidden_token_detected_in_string_value: {v!r}"
        )


def _verify_fixture_hash(fixture_id: str, doc: dict[str, Any]) -> str:
    stored_h = doc.get("canonical_hash", "")
    if not isinstance(stored_h, str) or len(stored_h) != 64:
        raise TransportFixtureCorpusCreationReceiptError(
            f"fixture {fixture_id}: canonical_hash missing or malformed"
        )
    pre = {k: v for k, v in doc.items() if k != "canonical_hash"}
    computed = canonical_hash(canonical_dumps(pre))
    if computed != stored_h:
        raise TransportFixtureCorpusCreationReceiptError(
            f"fixture {fixture_id}: canonical_hash mismatch "
            f"stored={stored_h!r} computed={computed!r}"
        )
    return stored_h


def _build_fixture_manifest() -> list[dict[str, Any]]:
    manifest: list[dict[str, Any]] = []
    for fid in ALL_FIXTURE_IDS:
        path = FIXTURE_BASE_PATH / f"{fid}.json"
        if not path.exists():
            raise TransportFixtureCorpusCreationReceiptError(
                f"fixture file not found: {path}; "
                "run scripts/transport/run_transport_test_vector_fixture_corpus.py first"
            )
        doc = json.loads(path.read_text())
        if doc.get("fixture_id") != fid:
            raise TransportFixtureCorpusCreationReceiptError(
                f"fixture_id mismatch in {path}: "
                f"expected {fid!r} got {doc.get('fixture_id')!r}"
            )
        h = _verify_fixture_hash(fid, doc)
        manifest.append({
            "fixture_id": fid,
            "fixture_path": str(path),
            "fixture_type": doc.get("fixture_type", ""),
            "canonical_hash": h,
        })
    return manifest


def _build_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "fixture_files_created": True,
        "computation_executed": False,
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


def build_transport_fixture_corpus_creation_receipt() -> dict[str, Any]:
    manifest = _build_fixture_manifest()
    if len(manifest) != 15:
        raise TransportFixtureCorpusCreationReceiptError(
            f"expected 15 fixtures in manifest, got {len(manifest)}"
        )
    valid_count = sum(1 for m in manifest if m["fixture_type"] == "VALID")
    invalid_count = sum(1 for m in manifest if m["fixture_type"] == "INVALID")
    nc_count = sum(1 for m in manifest if m["fixture_type"] == "NOT_COMPUTABLE")
    if valid_count != 6:
        raise TransportFixtureCorpusCreationReceiptError(
            f"expected 6 VALID fixtures, got {valid_count}"
        )
    if invalid_count != 4:
        raise TransportFixtureCorpusCreationReceiptError(
            f"expected 4 INVALID fixtures, got {invalid_count}"
        )
    if nc_count != 5:
        raise TransportFixtureCorpusCreationReceiptError(
            f"expected 5 NOT_COMPUTABLE fixtures, got {nc_count}"
        )

    raw: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "receipt_status": RECEIPT_STATUS,
        "operator_id": OPERATOR_ID,
        "source_fixture_plan_hash": SOURCE_FIXTURE_PLAN_HASH,
        "source_implementation_gate_hash": SOURCE_IMPLEMENTATION_GATE_HASH,
        "fixture_manifest": manifest,
        "fixture_count_total": 15,
        "fixture_count_valid": 6,
        "fixture_count_invalid": 4,
        "fixture_count_not_computable": 5,
        "intended_lane": "SHADOW",
        "metric_value_emitted": False,
        "authority_locks": _build_authority_locks(),
        "recommended_next_step": RECOMMENDED_NEXT_STEP,
        "created_at_utc": CREATED_AT_UTC,
    }
    _check_no_forbidden(raw)
    pre_hash = canonical_dumps(raw)
    h = canonical_hash(pre_hash)
    return json.loads(canonical_dumps({**raw, "canonical_hash": h}))


def validate_transport_fixture_corpus_creation_receipt(
    receipt: dict[str, Any],
) -> None:
    if receipt.get("schema_version") != SCHEMA_VERSION:
        raise TransportFixtureCorpusCreationReceiptError(
            f"schema_version must be {SCHEMA_VERSION!r}"
        )
    if receipt.get("receipt_status") != RECEIPT_STATUS:
        raise TransportFixtureCorpusCreationReceiptError(
            f"receipt_status must be {RECEIPT_STATUS!r}"
        )
    if receipt.get("operator_id") != OPERATOR_ID:
        raise TransportFixtureCorpusCreationReceiptError(
            f"operator_id must be {OPERATOR_ID!r}"
        )
    if receipt.get("source_fixture_plan_hash") != SOURCE_FIXTURE_PLAN_HASH:
        raise TransportFixtureCorpusCreationReceiptError(
            "source_fixture_plan_hash mismatch"
        )
    if receipt.get("source_implementation_gate_hash") != SOURCE_IMPLEMENTATION_GATE_HASH:
        raise TransportFixtureCorpusCreationReceiptError(
            "source_implementation_gate_hash mismatch"
        )
    if receipt.get("fixture_count_total") != 15:
        raise TransportFixtureCorpusCreationReceiptError(
            "fixture_count_total must be 15"
        )
    if receipt.get("metric_value_emitted") is not False:
        raise TransportFixtureCorpusCreationReceiptError(
            "metric_value_emitted must be False"
        )
    locks = receipt.get("authority_locks", {})
    if locks.get("fixture_files_created") is not True:
        raise TransportFixtureCorpusCreationReceiptError(
            "authority_locks.fixture_files_created must be True"
        )
    for flag in (
        "computation_executed", "emits_metric_values", "forecast_influence",
        "p43_surface_lanes_authorized", "production_activation",
        "canon_promotion", "runtime_mutation", "execution_authority",
        "inference_authority",
    ):
        if locks.get(flag) is not False:
            raise TransportFixtureCorpusCreationReceiptError(
                f"authority_locks.{flag} must be False"
            )
    manifest = receipt.get("fixture_manifest", [])
    if len(manifest) != 15:
        raise TransportFixtureCorpusCreationReceiptError(
            f"fixture_manifest must have 15 entries, got {len(manifest)}"
        )
    expected_ids = list(ALL_FIXTURE_IDS)
    actual_ids = [m["fixture_id"] for m in manifest]
    if actual_ids != expected_ids:
        raise TransportFixtureCorpusCreationReceiptError(
            f"fixture_manifest IDs mismatch: got {actual_ids}"
        )
    h = receipt.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise TransportFixtureCorpusCreationReceiptError(
            f"canonical_hash must be 64-char hex string, got {h!r}"
        )
    pre = {k: v for k, v in receipt.items() if k != "canonical_hash"}
    computed = canonical_hash(canonical_dumps(pre))
    if computed != h:
        raise TransportFixtureCorpusCreationReceiptError(
            f"canonical_hash mismatch: stored={h!r} computed={computed!r}"
        )
    _check_no_forbidden(receipt)
