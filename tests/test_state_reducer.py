"""Tests for core/state/reducer.py (HARDENING candidate)"""

import hashlib

from core.state.reducer import DeterministicStateReducer


def test_class_exists():
    assert DeterministicStateReducer is not None


def test_instantiation_and_basic():
    input_hash = "a" * 64
    output_hash = "b" * 64
    applied = ["c" * 64]
    drh = hashlib.sha256(
        f"{input_hash}|{output_hash}|{'|'.join(applied)}".encode()
    ).hexdigest()
    r = DeterministicStateReducer(
        reducer_id="test-reducer-001",
        input_state_hash=input_hash,
        output_state_hash=output_hash,
        applied_transition_hashes=applied,
        deterministic_reduction_hash=drh,
    )
    assert r is not None
    assert r.reducer_id == "test-reducer-001"
    assert r.status in ("pending", "reduced")
