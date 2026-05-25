from __future__ import annotations

import json
from pathlib import Path

from core.ingest.universal_ingest_receipt import (
    build_from_input_path,
    build_universal_ingest_receipt,
    write_universal_ingest_receipt,
)


def test_no_input_emits_valid_no_input_receipt() -> None:
    packet = build_universal_ingest_receipt(payload=None)
    assert packet["status"] == "NO_INPUT"
    assert packet["validation_status"] == "NOT_COMPUTABLE"
    assert packet["advisory_only"] is True
    assert packet["authority_granted"] is False
    assert packet["forecast_authority"] is False
    assert packet["mutation_allowed"] is False
    assert packet["lane"] == "SHADOW"


def test_same_input_has_stable_receipt_hash_and_ordering(tmp_path: Path) -> None:
    payload = {
        "items": [
            {"k": "b", "v": 2},
            {"k": "a", "v": 1},
        ]
    }
    src = tmp_path / "input.json"
    src.write_text(json.dumps(payload), encoding="utf-8")
    a = build_from_input_path(src)
    b = build_from_input_path(src)
    assert a["receipt_hash"] == b["receipt_hash"]
    assert a["item_hashes"] == sorted(a["item_hashes"])


def test_write_receipt_writes_json_and_markdown(tmp_path: Path) -> None:
    packet = build_universal_ingest_receipt(payload={"items": [{"k": "x"}]})
    out = tmp_path / "out" / "ingest" / "universal_ingest_receipt_001.latest.json"
    write_universal_ingest_receipt(out, packet)
    assert out.exists()
    assert out.with_suffix(".md").exists()


def test_list_payload_supported_for_local_signal() -> None:
    payload = [
        {"source": "local_test", "category": "temporal_signal", "value": "signal_a", "observed_at": "2026-05-22T00:00:00Z"},
        {"source": "local_test", "category": "temporal_signal", "value": "signal_b", "observed_at": "2026-05-22T00:01:00Z"},
    ]
    packet = build_universal_ingest_receipt(payload=payload)
    assert packet["item_count"] == 2
    assert packet["status"] == "ADVISORY_ONLY"
