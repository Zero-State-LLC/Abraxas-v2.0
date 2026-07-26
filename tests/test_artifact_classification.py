"""Tests for ADR-0018 artifact classification and classified writer."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.canonical.artifact_classification import (
    ArtifactClass,
    ArtifactClassificationError,
    influences_current_state,
    stamp_classification,
    validate_classification,
)
from core.canonical.json import (
    CanonicalWriteError,
    prepare_canonical_artifact,
    write_canonical_artifact,
)


def test_state_influence_matrix() -> None:
    assert influences_current_state(ArtifactClass.CANONICAL_DOMAIN_ARTIFACT) is True
    assert influences_current_state(ArtifactClass.GOVERNANCE_DECISION) is True
    assert influences_current_state(ArtifactClass.AUDIT_EVIDENCE) is False
    assert influences_current_state(ArtifactClass.BUILD_EVIDENCE) is False
    assert influences_current_state(ArtifactClass.HISTORICAL_RECEIPT) is False


def test_audit_evidence_cannot_claim_state_influence() -> None:
    with pytest.raises(ArtifactClassificationError):
        validate_classification(
            {"influences_current_state": True},
            ArtifactClass.AUDIT_EVIDENCE,
        )


def test_governance_decision_requires_locked_authority() -> None:
    with pytest.raises(ArtifactClassificationError):
        stamp_classification({"decision": "x"}, ArtifactClass.GOVERNANCE_DECISION)

    stamped = stamp_classification(
        {
            "decision": "hold",
            "authority_locks": {
                "promotion_allowed": False,
                "canon_mutation_allowed": False,
            },
        },
        ArtifactClass.GOVERNANCE_DECISION,
    )
    assert stamped["influences_current_state"] is True
    assert stamped["artifact_class"] == "GOVERNANCE_DECISION"


def test_governance_decision_rejects_unlocked_authority() -> None:
    with pytest.raises(ArtifactClassificationError):
        stamp_classification(
            {
                "decision": "promote",
                "authority_locks": {"promotion_allowed": True},
            },
            ArtifactClass.GOVERNANCE_DECISION,
        )


def test_write_canonical_artifact_stamps_and_confines(tmp_path: Path) -> None:
    out_root = tmp_path / "out"
    target = out_root / "prod" / "item.json"
    wrote = write_canonical_artifact(
        target,
        {"note": "classified"},
        artifact_class=ArtifactClass.BUILD_EVIDENCE,
        out_root=out_root,
    )
    assert wrote is True
    loaded = json.loads(target.read_text(encoding="utf-8"))
    assert loaded["artifact_class"] == "BUILD_EVIDENCE"
    assert loaded["influences_current_state"] is False
    assert len(loaded["canonical_hash"]) == 64


def test_write_canonical_artifact_path_traversal_denied(tmp_path: Path) -> None:
    out_root = tmp_path / "out"
    out_root.mkdir()
    with pytest.raises(CanonicalWriteError, match="path traversal"):
        write_canonical_artifact(
            tmp_path / "escape.json",
            {"note": "nope"},
            artifact_class=ArtifactClass.AUDIT_EVIDENCE,
            out_root=out_root,
        )


def test_append_only_collision(tmp_path: Path) -> None:
    out_root = tmp_path / "out"
    target = out_root / "once.json"
    write_canonical_artifact(
        target,
        {"n": 1},
        artifact_class=ArtifactClass.HISTORICAL_RECEIPT,
        out_root=out_root,
        append_only=True,
    )
    with pytest.raises(CanonicalWriteError, match="append_only"):
        write_canonical_artifact(
            target,
            {"n": 2},
            artifact_class=ArtifactClass.HISTORICAL_RECEIPT,
            out_root=out_root,
            append_only=True,
        )


def test_write_classified_json_helper(tmp_path: Path) -> None:
    from core.canonical.json import write_classified_json

    out_root = tmp_path / "out"
    target = out_root / "helper.json"
    assert write_classified_json(
        target,
        {"k": 1},
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=out_root,
    )
    loaded = json.loads(target.read_text(encoding="utf-8"))
    assert loaded["artifact_class"] == "AUDIT_EVIDENCE"
    assert write_classified_json(tmp_path / "legacy.json", ["not", "a", "dict"]) is True


def test_prepare_is_idempotent_for_class_fields() -> None:
    first = prepare_canonical_artifact({"x": 1}, ArtifactClass.AUDIT_EVIDENCE)
    second = prepare_canonical_artifact(first, ArtifactClass.AUDIT_EVIDENCE)
    assert first["canonical_hash"] == second["canonical_hash"]
    assert second["artifact_class"] == "AUDIT_EVIDENCE"
