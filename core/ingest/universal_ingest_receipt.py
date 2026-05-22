"""Deterministic local/static universal ingest receipt producer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "UniversalIngestReceipt.v1"
INGEST_ID = "universal_ingest_receipt_001"
SOURCE_MODE = "local_static"
DETERMINISTIC_TIMESTAMP = "universal_ingest_receipt_001_ts_0"


def _read_payload(path: Path | None) -> dict[str, Any] | list[Any] | None:
    if path is None:
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if isinstance(payload, dict):
        return payload
    if isinstance(payload, list):
        return payload
    return None


def _normalized_items(payload: dict[str, Any] | list[Any] | None) -> list[dict[str, Any]]:
    if payload is None:
        return []
    raw_items = payload if isinstance(payload, list) else payload.get("items")
    if not isinstance(raw_items, list):
        return []
    normalized = [item for item in raw_items if isinstance(item, dict)]
    return sorted(normalized, key=lambda item: canonical_hash(item))


def build_universal_ingest_receipt(*, payload: dict[str, Any] | list[Any] | None = None) -> dict[str, Any]:
    items = _normalized_items(payload)
    item_hashes = [canonical_hash(item) for item in items]
    status = "NO_INPUT" if not items else "ADVISORY_ONLY"
    validation_status = "NOT_COMPUTABLE" if not items else "PASS"
    blockers = ["no_input"] if not items else []

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "ingest_id": INGEST_ID,
        "source_mode": SOURCE_MODE,
        "deterministic_timestamp": DETERMINISTIC_TIMESTAMP,
        "input_hash": canonical_hash(payload if payload is not None else {"items": []}),
        "item_count": len(items),
        "item_hashes": item_hashes,
        "validation_status": validation_status,
        "status": status,
        "blockers": blockers,
        "advisory_only": True,
        "authority_granted": False,
        "forecast_authority": False,
        "mutation_allowed": False,
        "lane": "SHADOW",
    }
    packet["receipt_hash"] = canonical_hash(packet)
    return packet


def build_universal_ingest_receipt_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# Universal Ingest Receipt",
        "",
        f"- ingest_id: `{packet['ingest_id']}`",
        f"- status: `{packet['status']}`",
        f"- validation_status: `{packet['validation_status']}`",
        f"- item_count: `{packet['item_count']}`",
        f"- receipt_hash: `{packet['receipt_hash']}`",
    ]
    return "\n".join(lines) + "\n"


def write_universal_ingest_receipt(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(
        build_universal_ingest_receipt_markdown(packet),
        encoding="utf-8",
    )


def build_from_input_path(path: Path | None) -> dict[str, Any]:
    return build_universal_ingest_receipt(payload=_read_payload(path))
