from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.abx_codegen_intelligence_spine_shadow_binding import (
    STATUS_EMITTED,
    build_abx_codegen_intelligence_spine_shadow_binding_packet,
)
from core.abx_codegen_intelligence_spine_shadow_replay_harness import (
    STATUS_BLOCKED,
    STATUS_EMITTED as HARNESS_EMITTED,
    build_abx_codegen_intelligence_spine_shadow_replay_harness_packet,
    shadow_replay_harness_eligible,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_harness_blocked_when_authorization_gate_held(tmp_path: Path) -> None:
    gate_path = (
        tmp_path
        / "out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_implementation_authorization_gate_001.latest.json"
    )
    gate_path.parent.mkdir(parents=True, exist_ok=True)
    gate_path.write_text(
        json.dumps(
            {
                "authorization_gate_status": (
                    "SHADOW_REPLAY_HARNESS_IMPLEMENTATION_AUTHORIZATION_HELD_FOR_OPERATOR"
                ),
                "implementation_authorization_granted": False,
                "valid_for_implementation": False,
                "packet_hash": "b" * 64,
            }
        ),
        encoding="utf-8",
    )
    packet = build_abx_codegen_intelligence_spine_shadow_replay_harness_packet(tmp_path)
    assert packet["status"] == STATUS_BLOCKED
    assert packet["implementation_authorized"] is False
    assert packet["replay_result"]["execution_authority"] is False
    assert not shadow_replay_harness_eligible(tmp_path)


def test_harness_emitted_when_authorization_granted_on_main() -> None:
    packet = build_abx_codegen_intelligence_spine_shadow_replay_harness_packet(REPO_ROOT)
    assert packet["status"] == HARNESS_EMITTED
    assert packet["implementation_authorized"] is True
    assert shadow_replay_harness_eligible(REPO_ROOT)


def test_harness_emitted_when_authorization_granted(tmp_path: Path) -> None:
    gate_path = (
        tmp_path
        / "out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_implementation_authorization_gate_001.latest.json"
    )
    gate_path.parent.mkdir(parents=True, exist_ok=True)
    gate_path.write_text(
        json.dumps(
            {
                "authorization_gate_status": "AUTHORIZED",
                "implementation_authorization_granted": True,
                "valid_for_implementation": True,
                "packet_hash": "a" * 64,
            }
        ),
        encoding="utf-8",
    )
    packet = build_abx_codegen_intelligence_spine_shadow_replay_harness_packet(tmp_path)
    assert packet["status"] == HARNESS_EMITTED
    assert packet["implementation_authorized"] is True


def test_harness_authority_locks_all_false() -> None:
    packet = build_abx_codegen_intelligence_spine_shadow_replay_harness_packet(REPO_ROOT)
    assert all(value is False for value in packet["authority_locks"].values())


def test_binding_emitted_with_harness_provenance() -> None:
    packet = build_abx_codegen_intelligence_spine_shadow_binding_packet(REPO_ROOT)
    assert packet["status"] == STATUS_EMITTED
    assert packet["wiring_mode"] == "SHADOW_ADVISORY_ONLY"
    assert packet["harness_blocked"] is False
    assert packet["source_harness_hash"] != "NOT_COMPUTABLE"


def test_harness_deterministic() -> None:
    first = build_abx_codegen_intelligence_spine_shadow_replay_harness_packet(REPO_ROOT)
    second = build_abx_codegen_intelligence_spine_shadow_replay_harness_packet(REPO_ROOT)
    assert first == second


def test_harness_schema_validates() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        Path(
            "contracts/canon/abx_codegen_intelligence_spine_shadow_replay_harness.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    packet = build_abx_codegen_intelligence_spine_shadow_replay_harness_packet(REPO_ROOT)
    jsonschema.validate(packet, schema)
