"""Tests for WP-P threat model operator decision request."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from core.production_readiness.threat_model_operator_decision_request import (
    build_threat_model_operator_decision_request,
)


REPO = Path(__file__).resolve().parents[1]


def test_decision_request_pending_not_auto_accepted() -> None:
    req = build_threat_model_operator_decision_request(REPO, write=False)
    assert req["schema_version"] == "threat_model_operator_decision_request.v0"
    assert req["decision_status"] == "PENDING_OPERATOR"
    assert req["auto_accepted"] is False
    assert req["evidence_state"] == "Partial"
    codes = {d["code"] for d in req["allowed_decisions"]}
    assert "ACCEPT_PARTIAL_BASELINE" in codes
    assert "REJECT" in codes
    assert req["subject"]["worktree_present"] is True


def test_decision_request_schema() -> None:
    req = build_threat_model_operator_decision_request(REPO, write=False)
    schema = json.loads(
        (
            REPO
            / "contracts/production_readiness/"
            "threat_model_operator_decision_request.v0.schema.json"
        ).read_text(encoding="utf-8")
    )
    jsonschema.validate(instance=req, schema=schema)
