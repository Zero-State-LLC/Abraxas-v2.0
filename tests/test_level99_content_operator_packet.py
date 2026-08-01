"""Tests for Level99ContentOperatorPacket.v0 (Track B; Notion PATCH-004 aligned)."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft7Validator

from core.level99.content_operator_packet import (
    build_content_operator_packet,
    build_content_operator_packet_from_idea,
    compute_virality_scores,
    route_from_scores,
)

REPO = Path(__file__).resolve().parents[1]
SCHEMA = REPO / "contracts" / "level99" / "content_operator_packet.v0.schema.json"


def test_amplify_candidate_route():
    # Notion formula: high engagement density + retention → AMPLIFY
    pack = build_content_operator_packet(
        content_id="c_amp",
        topic="checkout haunted cart joke",
        format_target="short_clip",
        humor_gradient=3,
        views=10_000,
        likes=2_500,
        comments=800,
        shares=500,
        saves=400,
        retention_ratio=0.65,
        compression_score=0.9,
        joke_density_score=0.9,
    )
    assert pack["schema_version"] == "Level99ContentOperatorPacket.v0"
    assert pack["pipeline_id"] == "level99_content"
    assert pack["lane"] == "SHADOW_MEDIA"
    assert pack["route"] == "AMPLIFY_CANDIDATE"
    assert pack["readiness"] == "SHADOW_OPERATOR_REVIEW"
    assert pack["virality_scores"]["memetic_resonance"] >= 0.72
    assert pack["auto_publish_blocked"] is True
    assert pack["authority"]["auto_publish_allowed"] is False
    assert pack["authority"]["operator_approval_required"] is True
    assert pack["authority"]["promotion_authorized"] is False

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft7Validator(schema).validate(pack)


def test_iterate_and_archive_routes():
    mid = build_content_operator_packet(
        content_id="c_mid",
        topic="mid",
        views=500,
        likes=40,
        comments=5,
        shares=3,
        retention_ratio=0.3,
        compression_score=0.5,
        joke_density_score=0.4,
    )
    assert mid["route"] == "ITERATE"

    low = build_content_operator_packet(
        content_id="c_low",
        topic="low",
        views=10,
        likes=0,
        comments=0,
        shares=0,
        retention_ratio=0.1,
        compression_score=0.1,
        joke_density_score=0.1,
    )
    assert low["route"] == "ARCHIVE"


def test_not_computable_without_metrics():
    pack = build_content_operator_packet(
        content_id="c_nc",
        topic="idea only",
        format_target="thread",
        humor_gradient=2,
        metrics_present=False,
        compression_score=0.6,
        joke_density_score=0.5,
    )
    assert pack["route"] == "NOT_COMPUTABLE"
    assert pack["readiness"] == "NOT_COMPUTABLE"
    assert "MISSING_REQUIRED_METRICS" in pack["blocked_by"]


def test_virality_claim_without_metrics_flag():
    pack = build_content_operator_packet(
        content_id="c_claim",
        topic="viral!",
        metrics_present=False,
        virality_claim_without_metrics=True,
    )
    assert "VIRALITY_CLAIM_WITHOUT_TEST_DATA" in pack["blocked_by"]
    assert "virality_claim_without_test_data" in pack["drift_flags"]


def test_joke_overrides_analysis_blocks():
    pack = build_content_operator_packet(
        content_id="c_joke",
        topic="analysis",
        views=1000,
        likes=50,
        retention_ratio=0.5,
        joke_overrides_analysis=True,
    )
    assert pack["readiness"] == "BLOCKED"
    assert "JOKE_OVERRIDES_ANALYSIS" in pack["blocked_by"]


def test_score_formulas_deterministic():
    a = compute_virality_scores(
        views=10000,
        likes=100,
        comments=20,
        shares=10,
        saves=5,
        retention_ratio=0.5,
        compression_score=0.4,
        joke_density_score=0.3,
    )
    b = compute_virality_scores(
        views=10000,
        likes=100,
        comments=20,
        shares=10,
        saves=5,
        retention_ratio=0.5,
        compression_score=0.4,
        joke_density_score=0.3,
    )
    assert a == b
    assert route_from_scores(a, metrics_present=True) in {
        "AMPLIFY_CANDIDATE",
        "ITERATE",
        "ARCHIVE",
    }


def test_from_idea_dict():
    idea = {
        "idea_id": "idea_1",
        "content": {
            "topic": "memetic pressure",
            "format_targets": ["short_clip", "thread"],
        },
        "humor_gradient": 3,
        "compression_score": 0.55,
        "joke_density_score": 0.45,
    }
    performance = {
        "hook_id": "h1",
        "metrics": {
            "views": 2000,
            "likes": 120,
            "comments": 15,
            "shares": 8,
            "saves": 4,
            "retention_ratio": 0.42,
        },
    }
    pack = build_content_operator_packet_from_idea(idea, performance=performance)
    assert pack["content_id"] == "idea_1"
    assert pack["topic"] == "memetic pressure"
    assert pack["format_target"] == "short_clip"
    assert pack["hook_id"] == "h1"
    assert pack["route"] in {"AMPLIFY_CANDIDATE", "ITERATE", "ARCHIVE"}


def test_packet_deterministic():
    kwargs = dict(
        content_id="c_det",
        topic="det",
        format_target="reaction",
        views=100,
        likes=10,
        retention_ratio=0.5,
        compression_score=0.5,
        joke_density_score=0.5,
    )
    assert build_content_operator_packet(**kwargs) == build_content_operator_packet(
        **kwargs
    )
