"""Tests for WP-DEPLOY candidate deploy readiness."""

from __future__ import annotations

from pathlib import Path

from core.production_readiness.candidate_deploy_readiness import (
    build_candidate_deploy_readiness,
)


REPO = Path(__file__).resolve().parents[1]


def test_deploy_readiness_defaults_no_go() -> None:
    packet = build_candidate_deploy_readiness(REPO, write=False)
    assert packet["schema_version"] == "candidate_deploy_readiness.v1"
    assert packet["deploy_authorized"] is False
    assert packet["production_activation_authorized"] is False
    assert packet["go_no_go"].startswith("NO_GO")
    assert len(packet["checklist"]) >= 6
