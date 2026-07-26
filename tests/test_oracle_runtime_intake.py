from __future__ import annotations

import pytest

from core.oracle.runtime import run_oracle_intake


def test_single_payload_intake_is_stable() -> None:
    packet = run_oracle_intake(
        [
            {
                "source_id": "fixture:001",
                "source_type": "document",
                "payload": "Deterministic Oracle Intake Evidence",
            }
        ]
    )
    assert packet["intake"]["source_id"] == "fixture:001"
    assert packet["conflicts"] == []
    assert packet["stabilization"]["stabilization_state"] == "stable"


def test_same_source_multi_payload_detects_provenance_conflict() -> None:
    packet = run_oracle_intake(
        [
            {
                "source_id": "fixture:001",
                "source_type": "document",
                "payload": "alpha",
            },
            {
                "source_id": "fixture:001",
                "source_type": "document",
                "payload": "bravo",
            },
        ]
    )
    assert packet["intake"]["source_id"] == "fixture:001"
    assert packet["stabilization"]["stabilization_state"] == "conflicted"
    assert any(c["conflict_type"] == "provenance_mismatch" for c in packet["conflicts"])


def test_mixed_source_ids_fail_closed() -> None:
    with pytest.raises(ValueError, match="mixed source_ids must be split"):
        run_oracle_intake(
            [
                {
                    "source_id": "fixture:001",
                    "source_type": "document",
                    "payload": "alpha",
                },
                {
                    "source_id": "fixture:002",
                    "source_type": "receipt",
                    "payload": "beta",
                },
            ]
        )
