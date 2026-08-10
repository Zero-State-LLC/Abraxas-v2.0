"""Operator-scoped EvidencePack.v0 -> RDI SHADOW SANDBOX live wiring."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.canonical.json import canonical_hash
from core.instantiation import (
    DIMENSIONS,
    build_rdi_live_wire_artifact,
    derive_rdi_live_wire_window,
)


def _source(source_id: str) -> dict[str, str]:
    return {
        "source_id": source_id,
        "url_or_path": f"ingest/{source_id}.json",
        "title": source_id,
        "source_class": "code",
        "excerpt": f"evidence from {source_id}",
    }


def _claim(
    claim_id: str,
    *,
    register: str,
    source_ids: list[str],
    dimension: str | None,
) -> dict[str, object]:
    claim: dict[str, object] = {
        "claim_id": claim_id,
        "text": f"claim {claim_id}",
        "register": register,
        "source_ids": source_ids,
    }
    if dimension is not None:
        claim["dimension"] = dimension
    if register == "INFERRED":
        claim["join_logic"] = "both sources support the bounded inference"
    return claim


def _pack(*, claims: list[dict[str, object]] | None = None) -> dict[str, object]:
    if claims is None:
        claims = [
            _claim(
                "c-observed",
                register="OBSERVED",
                source_ids=["s1"],
                dimension="symbolic_persistence",
            ),
            _claim(
                "c-inferred",
                register="INFERRED",
                source_ids=["s1", "s2"],
                dimension="recursive_reinforcement",
            ),
        ]
    return {
        "schema_version": "EvidencePack.v0",
        "pack_id": "evidence-pack-rdi",
        "topic": "RDI",
        "intent": "research",
        "time_horizon": "2026-08-01T00:00:00Z/2026-08-10T00:00:00Z",
        "must_answer": [],
        "sources": [_source("s1"), _source("s2")],
        "claims": claims,
        "authority": {
            "execution_authority": False,
            "promotion_authorized": False,
            "forecast_routing_authorized": False,
            "canon_mutation_allowed": False,
        },
        "provenance": {
            "producer_system": "OPERATOR",
            "skill_id": "abx-familiar-signal-forager",
            "tool_trace_summary": "test ingest evidence",
        },
    }


def _evidence(source_id: str, timestamp: str, suffix: str) -> dict[str, object]:
    return {
        "schema_version": "EvidenceObject.v1",
        "source": f"ingest/{source_id}.json",
        "timestamp": timestamp,
        "provenance": {"source_id": source_id},
        "evidence_type": "JSON",
        "hash": suffix * 64,
    }


def _objects() -> list[dict[str, object]]:
    return [
        _evidence("s1", "2026-08-05T00:00:00Z", "1"),
        _evidence("s2", "2026-08-06T00:00:00Z", "2"),
    ]


def _dimension(artifact: dict[str, object], name: str) -> dict[str, object]:
    state = artifact["instantiation_state"]
    assert isinstance(state, dict)
    return next(item for item in state["dimensions"] if item["name"] == name)


def test_happy_path_builds_real_state_runs_shadow_and_writes_artifact(
    tmp_path: Path,
) -> None:
    artifact = build_rdi_live_wire_artifact(
        _pack(), _objects(), artifact_id="run-1", out_root=tmp_path
    )

    assert artifact["activation_lane"] == "SANDBOX"
    assert artifact["dry_run"] is True
    assert artifact["detection_only"] is True
    assert artifact["artifact_class"] == "AUDIT_EVIDENCE"
    assert artifact["influences_current_state"] is False
    assert {claim["claim_id"] for claim in artifact["selected_claims"]} == {
        "c-observed",
        "c-inferred",
    }

    packet = artifact["construct_packet"]
    assert packet["construct"] == "RDI instantiation vector H"
    assert packet["construct_status"] == "EMERGENT"
    assert packet["variable_class"] == "HYBRID"
    assert packet["dimensions"] == list(DIMENSIONS)
    assert packet["route"] == "EVIDENCE_RETRIEVAL"
    assert packet["assumptions"]

    assert (
        _dimension(artifact, "symbolic_persistence")["epistemic_status"] == "OBSERVED"
    )
    assert (
        _dimension(artifact, "recursive_reinforcement")["epistemic_status"]
        == "INFERRED"
    )
    assert (
        _dimension(artifact, "material_consequence")["epistemic_status"]
        == "NOT_COMPUTABLE"
    )
    assert artifact["shadow_report"]["schema_version"] == "InstantiationShadowReport.v1"

    path = tmp_path / "rdi_instantiation_shadow" / "run-1.json"
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved == artifact
    assert saved["canonical_hash"] == canonical_hash(
        {key: value for key, value in saved.items() if key != "canonical_hash"}
    )


def test_missing_or_empty_evidence_fails_closed_without_artifact(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="at least one EvidenceObject"):
        build_rdi_live_wire_artifact(
            _pack(), [], artifact_id="empty-objects", out_root=tmp_path
        )
    with pytest.raises(ValueError, match="found no eligible"):
        build_rdi_live_wire_artifact(
            _pack(claims=[]),
            _objects(),
            artifact_id="empty-claims",
            out_root=tmp_path,
        )
    assert not (tmp_path / "rdi_instantiation_shadow").exists()


def test_out_of_window_evidence_and_its_claim_are_excluded(tmp_path: Path) -> None:
    objects = [
        _evidence("s1", "2026-08-05T00:00:00Z", "1"),
        _evidence("s2", "2026-08-20T00:00:00Z", "2"),
    ]
    artifact = build_rdi_live_wire_artifact(
        _pack(), objects, artifact_id="window", out_root=tmp_path
    )

    assert [claim["claim_id"] for claim in artifact["selected_claims"]] == [
        "c-observed"
    ]
    assert {item["claim_id"]: item["reason"] for item in artifact["excluded_claims"]}[
        "c-inferred"
    ] == "MISSING_IN_WINDOW_EVIDENCE"
    assert artifact["window"]["evidence_object_timestamps"] == ["2026-08-05T00:00:00Z"]
    assert "2" * 64 not in str(artifact["selected_claims"])


def test_malformed_dimension_and_wrong_register_claims_are_excluded(
    tmp_path: Path,
) -> None:
    claims = [
        _claim(
            "valid",
            register="OBSERVED",
            source_ids=["s1"],
            dimension="symbolic_persistence",
        ),
        _claim(
            "wrong-register",
            register="SPECULATIVE",
            source_ids=[],
            dimension="cognitive_penetration",
        ),
        _claim(
            "wrong-dimension",
            register="OBSERVED",
            source_ids=["s1"],
            dimension="not_an_instantiation_dimension",
        ),
        _claim(
            "missing-dimension",
            register="OBSERVED",
            source_ids=["s1"],
            dimension=None,
        ),
    ]
    artifact = build_rdi_live_wire_artifact(
        _pack(claims=claims), _objects(), artifact_id="filters", out_root=tmp_path
    )

    assert [claim["claim_id"] for claim in artifact["selected_claims"]] == ["valid"]
    reasons = {item["claim_id"]: item["reason"] for item in artifact["excluded_claims"]}
    assert reasons == {
        "missing-dimension": "DIMENSION_NOT_TARGETED",
        "wrong-dimension": "DIMENSION_NOT_TARGETED",
        "wrong-register": "REGISTER_NOT_ALLOWED",
    }


def test_authority_stays_hard_false_and_forbidden_paths_are_absent(
    tmp_path: Path,
) -> None:
    artifact = build_rdi_live_wire_artifact(
        _pack(), _objects(), artifact_id="authority", out_root=tmp_path
    )

    assert artifact["console_feed_changed"] is False
    assert all(value is False for value in artifact["authority"].values())
    assert all(
        value is False
        for value in artifact["instantiation_state"]["authority"].values()
    )
    assert all(
        value is False for value in artifact["shadow_report"]["authority"].values()
    )
    assert artifact["construct_packet"]["authority"] == {
        "truth_assignment": False,
        "forecast_routing": False,
        "canon_mutation": False,
        "execution_authority": False,
        "retrieval_authority": True,
    }
    assert not {"explanation", "forecast", "intervention"} & artifact.keys()


def test_window_uses_pack_horizon_and_evidence_object_timestamps() -> None:
    window = derive_rdi_live_wire_window(_pack(), _objects())
    assert window == {
        "time_horizon": "2026-08-01T00:00:00Z/2026-08-10T00:00:00Z",
        "start": "2026-08-01T00:00:00Z",
        "end": "2026-08-10T00:00:00Z",
        "evidence_object_timestamps": [
            "2026-08-05T00:00:00Z",
            "2026-08-06T00:00:00Z",
        ],
    }


def test_ambiguous_dimension_registers_and_unparseable_window_fail_closed(
    tmp_path: Path,
) -> None:
    claims = [
        _claim(
            "observed",
            register="OBSERVED",
            source_ids=["s1"],
            dimension="symbolic_persistence",
        ),
        _claim(
            "inferred",
            register="INFERRED",
            source_ids=["s1", "s2"],
            dimension="symbolic_persistence",
        ),
    ]
    with pytest.raises(ValueError, match="ambiguous epistemic registers"):
        build_rdi_live_wire_artifact(
            _pack(claims=claims),
            _objects(),
            artifact_id="ambiguous",
            out_root=tmp_path,
        )

    pack = _pack()
    pack["time_horizon"] = "2026 H1-H2 public discourse"
    with pytest.raises(ValueError, match="ISO-8601 start/end interval"):
        build_rdi_live_wire_artifact(
            pack, _objects(), artifact_id="bad-window", out_root=tmp_path
        )
