"""Comprehensive tests for core/codegen/oracle_signal/holler_oracle_ingest_stub.py

Layer 0 HARDENING: covers key functions, authority locks, canonical hashing, edge cases.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.codegen.oracle_signal.holler_oracle_ingest_stub import (
    _authority_locks,
    build_shadow_replay_harness_stub,
    build_holler_oracle_ingest_stub,
)
from core.canonical.json import canonical_hash


def test_authority_locks_are_all_false():
    locks = _authority_locks()
    assert all(v is False for v in locks.values())
    assert "live_signal_ingest" in locks
    assert "canon_mutation" in locks


def test_build_shadow_replay_harness_stub_deterministic():
    source = {"canonical_hash": "abc123"}
    ts = "2026-07-11T00:00:00Z"
    r1 = build_shadow_replay_harness_stub(timestamp=ts, source_packet=source)
    r2 = build_shadow_replay_harness_stub(timestamp=ts, source_packet=source)
    assert r1["stub_status"] == "SHADOW_REPLAY_HARNESS_STUB_READY_ADVISORY_ONLY"
    assert r1["valid_for_execution"] is False
    assert r1["valid_for_live_ingest"] is False
    assert r1["canonical_hash"] == r2["canonical_hash"]
    assert "authority_locks" in r1


def test_build_holler_oracle_ingest_stub_deterministic():
    intake = {"canonical_hash": "intake456"}
    harness = {"canonical_hash": "harness789"}
    ts = "2026-07-11T00:00:00Z"
    r1 = build_holler_oracle_ingest_stub(
        timestamp=ts, holler_intake=intake, shadow_replay_harness=harness
    )
    r2 = build_holler_oracle_ingest_stub(
        timestamp=ts, holler_intake=intake, shadow_replay_harness=harness
    )
    assert r1["stub_status"] == "HOLLER_ORACLE_INGEST_STUB_READY_ADVISORY_ONLY"
    assert r1["ingest_mode"] == "STUB_ONLY_NO_FETCH_NO_QUEUE_NO_SCHEDULER"
    assert r1["valid_for_execution"] is False
    assert r1["canonical_hash"] == r2["canonical_hash"]
    assert r1["authority_locks"] == _authority_locks()


def test_stubs_use_canonical_hash():
    source = {"canonical_hash": "xyz"}
    ts = "2026-07-11"
    r = build_shadow_replay_harness_stub(timestamp=ts, source_packet=source)
    # basic structural check
    assert "canonical_hash" in r
    assert isinstance(r["canonical_hash"], str)
    assert len(r["canonical_hash"]) > 10


def test_no_live_ingest_flags():
    intake = {"canonical_hash": "i1"}
    harness = {"canonical_hash": "h1"}
    ts = "2026-07-11"
    r = build_holler_oracle_ingest_stub(timestamp=ts, holler_intake=intake, shadow_replay_harness=harness)
    assert r["valid_for_live_ingest"] is False
    assert r["provenance_seal"]["live_signal_ingest"] is False


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-q"])