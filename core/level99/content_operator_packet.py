"""Level 99 content operator packet — virality boundaries + operator review.

Closes level99_content MISSING_CONTRACT at the operator-packet layer.
Aligned to Notion PATCH-GLOBAL-SPINE-004 (MemeticResonanceScore route rules).

Does not auto-publish, mutate platforms, promote canon, or route forecasts.
"""

from __future__ import annotations

import math
from typing import Any

from core.canonical.json import canonical_hash

SCHEMA_VERSION = "Level99ContentOperatorPacket.v0"
PIPELINE_ID = "level99_content"
DETERMINISTIC_TIMESTAMP = "level99_content_operator_packet_v0_ts_0"

DEFAULT_AUTHORITY = {
    "execution_authority": False,
    "promotion_authorized": False,
    "forecast_routing_authorized": False,
    "canon_mutation_allowed": False,
    "auto_publish_allowed": False,
    "operator_approval_required": True,
}

PRODUCER = {
    "module": "core.level99.content_operator_packet",
    "pipeline_id": PIPELINE_ID,
    "subsystem": "Level 99",
    "notion_patch": "PATCH-GLOBAL-SPINE-004",
}

FORMAT_TARGETS = frozenset(
    {
        "short_clip",
        "reaction",
        "thread",
        "thumbnail",
        "longform",
        "boss_fight",
        "unknown",
    }
)

# Notion route thresholds (PATCH-GLOBAL-SPINE-004)
AMPLIFY_RESONANCE = 0.72
AMPLIFY_RETENTION = 0.45
ITERATE_RESONANCE = 0.40

# Memetic resonance weights (Notion)
_WEIGHTS = {
    "attention_score": 0.22,
    "engagement_score": 0.22,
    "retention_score": 0.18,
    "comment_signal_strength": 0.14,
    "share_velocity_score": 0.14,
    "compression_score": 0.05,
    "joke_density_score": 0.05,
}


def _clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _round6(x: float) -> float:
    return round(x, 6)


def _int_ge0(raw: Any) -> int:
    try:
        n = int(raw)
    except (TypeError, ValueError):
        return 0
    return max(0, n)


def _float_opt(raw: Any) -> float | None:
    if raw is None or raw == "":
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def _norm_format(raw: Any) -> str:
    s = str(raw or "unknown").strip().lower()
    return s if s in FORMAT_TARGETS else "unknown"


def _norm_gradient(raw: Any) -> int:
    try:
        g = int(raw)
    except (TypeError, ValueError):
        return 0
    if g < 0:
        return 0
    if g > 4:
        return 4
    return g


def compute_virality_scores(
    *,
    views: int = 0,
    likes: int = 0,
    comments: int = 0,
    shares: int = 0,
    saves: int = 0,
    retention_ratio: float | None = None,
    compression_score: float = 0.0,
    joke_density_score: float = 0.0,
    metrics_present: bool = True,
) -> dict[str, float]:
    """Deterministic MemeticResonance scores (Notion formulas, advisory)."""
    v = max(int(views), 0)
    likes_n = max(int(likes), 0)
    comments_n = max(int(comments), 0)
    shares_n = max(int(shares), 0)
    saves_n = max(int(saves), 0)
    denom = max(v, 1)

    attention = _clamp01(math.log10(max(v, 1)) / 6.0)
    engagement = _clamp01(
        (likes_n + comments_n * 2 + shares_n * 3 + saves_n * 2) / denom
    )
    if retention_ratio is None:
        retention = 0.0
    else:
        retention = _clamp01(float(retention_ratio))
    comment_sig = _clamp01(comments_n / denom * 100.0)
    share_vel = _clamp01(shares_n / denom * 100.0)
    compression = _clamp01(float(compression_score or 0.0))
    joke = _clamp01(float(joke_density_score or 0.0))

    if not metrics_present and v == 0 and likes_n == 0 and comments_n == 0:
        # Zeroed craft-only scores still computable; resonance from craft alone
        pass

    resonance = (
        attention * _WEIGHTS["attention_score"]
        + engagement * _WEIGHTS["engagement_score"]
        + retention * _WEIGHTS["retention_score"]
        + comment_sig * _WEIGHTS["comment_signal_strength"]
        + share_vel * _WEIGHTS["share_velocity_score"]
        + compression * _WEIGHTS["compression_score"]
        + joke * _WEIGHTS["joke_density_score"]
    )

    return {
        "attention_score": _round6(attention),
        "engagement_score": _round6(engagement),
        "retention_score": _round6(retention),
        "comment_signal_strength": _round6(comment_sig),
        "share_velocity_score": _round6(share_vel),
        "compression_score": _round6(compression),
        "joke_density_score": _round6(joke),
        "memetic_resonance": _round6(_clamp01(resonance)),
    }


def route_from_scores(
    scores: dict[str, float],
    *,
    metrics_present: bool,
) -> str:
    """Notion route rules: AMPLIFY / ITERATE / ARCHIVE / NOT_COMPUTABLE."""
    if not metrics_present:
        return "NOT_COMPUTABLE"
    resonance = float(scores.get("memetic_resonance") or 0.0)
    retention = float(scores.get("retention_score") or 0.0)
    if resonance >= AMPLIFY_RESONANCE and retention >= AMPLIFY_RETENTION:
        return "AMPLIFY_CANDIDATE"
    if resonance >= ITERATE_RESONANCE:
        return "ITERATE"
    return "ARCHIVE"


def build_content_operator_packet(
    *,
    content_id: str = "",
    hook_id: str | None = None,
    topic: str = "",
    format_target: str = "unknown",
    humor_gradient: int = 0,
    views: int = 0,
    likes: int = 0,
    comments: int = 0,
    shares: int = 0,
    saves: int = 0,
    retention_ratio: float | None = None,
    compression_score: float = 0.0,
    joke_density_score: float = 0.0,
    metrics_present: bool | None = None,
    virality_claim_without_metrics: bool = False,
    joke_overrides_analysis: bool = False,
    blocked_by: list[str] | None = None,
) -> dict[str, Any]:
    """Build deterministic Level99ContentOperatorPacket.v0 (SHADOW_MEDIA)."""
    cid = str(content_id or "").strip() or "content_unspecified"
    topic_n = str(topic or "").strip() or "UNTITLED"
    fmt = _norm_format(format_target)
    gradient = _norm_gradient(humor_gradient)
    views_n = _int_ge0(views)
    likes_n = _int_ge0(likes)
    comments_n = _int_ge0(comments)
    shares_n = _int_ge0(shares)
    saves_n = _int_ge0(saves)
    ret = _float_opt(retention_ratio)

    if metrics_present is None:
        # Heuristic: any non-zero performance metric or explicit retention
        metrics_present = bool(
            views_n or likes_n or comments_n or shares_n or saves_n or ret is not None
        )

    blocks = list(blocked_by or [])
    for b in (
        "AUTO_PUBLISH_BLOCKED",
        "PLATFORM_MUTATION_BLOCKED",
        "PROMOTION_BLOCKED",
        "FORECAST_ROUTING_BLOCKED",
    ):
        if b not in blocks:
            blocks.append(b)

    drift: list[str] = []
    if virality_claim_without_metrics or (
        not metrics_present and (views_n or likes_n)
    ):
        # explicit flag or inconsistent
        pass
    if virality_claim_without_metrics and not metrics_present:
        if "VIRALITY_CLAIM_WITHOUT_TEST_DATA" not in blocks:
            blocks.append("VIRALITY_CLAIM_WITHOUT_TEST_DATA")
        if "virality_claim_without_test_data" not in drift:
            drift.append("virality_claim_without_test_data")
    if joke_overrides_analysis:
        if "JOKE_OVERRIDES_ANALYSIS" not in blocks:
            blocks.append("JOKE_OVERRIDES_ANALYSIS")
        if "joke_overrides_analysis" not in drift:
            drift.append("joke_overrides_analysis")
    if gradient >= 4:
        if "PRIVATE_HUMOR_GRADIENT" not in blocks:
            blocks.append("PRIVATE_HUMOR_GRADIENT")
        if "dark_humor_used_in_wrong_context" not in drift:
            # not wrong by default; flag as private-only
            drift.append("humor_gradient_private_only")

    scores = compute_virality_scores(
        views=views_n,
        likes=likes_n,
        comments=comments_n,
        shares=shares_n,
        saves=saves_n,
        retention_ratio=ret,
        compression_score=compression_score,
        joke_density_score=joke_density_score,
        metrics_present=bool(metrics_present),
    )
    route = route_from_scores(scores, metrics_present=bool(metrics_present))

    if route == "NOT_COMPUTABLE":
        readiness = "NOT_COMPUTABLE"
        if "MISSING_REQUIRED_METRICS" not in blocks:
            blocks.append("MISSING_REQUIRED_METRICS")
    elif "JOKE_OVERRIDES_ANALYSIS" in blocks:
        readiness = "BLOCKED"
    else:
        readiness = "SHADOW_OPERATOR_REVIEW"

    virality = {
        "schema_version": "Level99MemeticResonance.v0",
        **scores,
    }

    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "pipeline_id": PIPELINE_ID,
        "packet_id": "l99_"
        + canonical_hash(
            {
                "content_id": cid,
                "route": route,
                "memetic_resonance": scores["memetic_resonance"],
                "topic": topic_n,
            }
        )[:16],
        "content_id": cid,
        "hook_id": str(hook_id) if hook_id else None,
        "topic": topic_n,
        "format_target": fmt,
        "humor_gradient": gradient,
        "metrics": {
            "views": views_n,
            "likes": likes_n,
            "comments": comments_n,
            "shares": shares_n,
            "saves": saves_n,
            "retention_ratio": ret,
            "metrics_present": bool(metrics_present),
        },
        "virality_scores": virality,
        "route": route,
        "readiness": readiness,
        "blocked_by": blocks,
        "drift_flags": drift,
        "auto_publish_blocked": True,
        "platform_mutation_blocked": True,
        "authority": dict(DEFAULT_AUTHORITY),
        "advisory_only": True,
        "lane": "SHADOW_MEDIA",
        "producer": dict(PRODUCER),
        "deterministic_timestamp": DETERMINISTIC_TIMESTAMP,
    }
    body["canonical_hash"] = canonical_hash(body)
    return body


def build_content_operator_packet_from_idea(
    idea: dict[str, Any],
    *,
    metrics: dict[str, Any] | None = None,
    performance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Lift ContentIdea/Performance-like dicts into operator packet."""
    idea_d = idea if isinstance(idea, dict) else {}
    content = idea_d.get("content") if isinstance(idea_d.get("content"), dict) else {}
    perf = performance if isinstance(performance, dict) else {}
    mets = metrics if isinstance(metrics, dict) else {}
    # Prefer nested performance.metrics
    if isinstance(perf.get("metrics"), dict):
        mets = {**mets, **perf["metrics"]}

    format_target = idea_d.get("format_target")
    if not format_target:
        targets = content.get("format_targets")
        if isinstance(targets, list) and targets:
            format_target = targets[0]
        else:
            format_target = "unknown"

    return build_content_operator_packet(
        content_id=str(idea_d.get("content_id") or idea_d.get("idea_id") or ""),
        hook_id=str(idea_d.get("hook_id") or perf.get("hook_id") or "") or None,
        topic=str(
            idea_d.get("topic")
            or content.get("topic")
            or idea_d.get("angle")
            or ""
        ),
        format_target=str(format_target or "unknown"),
        humor_gradient=idea_d.get("humor_gradient", 0),
        views=mets.get("views", 0),
        likes=mets.get("likes", 0),
        comments=mets.get("comments", 0),
        shares=mets.get("shares", 0),
        saves=mets.get("saves", 0),
        retention_ratio=mets.get("retention_ratio"),
        compression_score=float(
            idea_d.get("compression_score")
            or mets.get("compression_score")
            or 0.0
        ),
        joke_density_score=float(
            idea_d.get("joke_density_score")
            or mets.get("joke_density_score")
            or 0.0
        ),
        metrics_present=mets.get("metrics_present")
        if "metrics_present" in mets
        else None,
        virality_claim_without_metrics=bool(
            idea_d.get("virality_claim_without_metrics")
        ),
        joke_overrides_analysis=bool(idea_d.get("joke_overrides_analysis")),
        blocked_by=list(idea_d.get("blocked_by") or [])
        if isinstance(idea_d.get("blocked_by"), list)
        else None,
    )
