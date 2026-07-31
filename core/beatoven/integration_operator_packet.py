"""BeatOven / PsyFi integration operator packet — shared runic core.

Closes beatoven_psyfi_integration MISSING_CONTRACT at the operator-packet layer.
Aligned to Notion PATCH-GLOBAL-SPINE-006 (sonic plan only / projection only).

Does not render audio, control DAW/hardware, publish, mint, or promote.
"""

from __future__ import annotations

from typing import Any

from core.canonical.json import canonical_hash

SCHEMA_VERSION = "BeatOvenPsyFiIntegrationOperatorPacket.v0"
PIPELINE_ID = "beatoven_psyfi_integration"
DETERMINISTIC_TIMESTAMP = "beatoven_psyfi_integration_operator_packet_v0_ts_0"

DEFAULT_AUTHORITY = {
    "execution_authority": False,
    "promotion_authorized": False,
    "forecast_routing_authorized": False,
    "canon_mutation_allowed": False,
    "external_audio_render_allowed": False,
    "daw_control_allowed": False,
    "hardware_control_allowed": False,
    "publishing_allowed": False,
    "minting_allowed": False,
    "operator_approval_required": True,
    "sonic_plan_only": True,
}

PRODUCER = {
    "module": "core.beatoven.integration_operator_packet",
    "pipeline_id": PIPELINE_ID,
    "subsystem": "BeatOven / PsyFi",
    "notion_patch": "PATCH-GLOBAL-SPINE-006",
}

SHARED_RUNES = (
    "RUNE.BEATOVEN.INTENT.NORMALIZE",
    "RUNE.BEATOVEN.SONIC_GRAPH.BUILD",
    "RUNE.BEATOVEN.RHYTHM.MAP",
    "RUNE.BEATOVEN.TIMBRE.MAP",
    "RUNE.BEATOVEN.MODULATION.PLAN",
    "RUNE.BEATOVEN.FEEDBACK.INGEST",
    "RUNE.BEATOVEN.PHONOMICON.BRIDGE",
    "RUNE.BEATOVEN.PATCHHIVE.BRIDGE",
    "RUNE.BEATOVEN.PSYFI.BRIDGE",
    "RUNE.BEATOVEN.PROJECTION.BUILD",
    "RUNE.PSYFI.BEATOVEN.BRIDGE",
)

SOURCE_SYSTEMS = frozenset(
    {
        "manual",
        "noctis",
        "psyfi",
        "neon_genie",
        "level99",
        "patchhive",
        "unknown",
    }
)


def _clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _round6(x: float) -> float:
    return round(x, 6)


def _f01(raw: Any, default: float = 0.0) -> float:
    try:
        return _clamp01(float(raw))
    except (TypeError, ValueError):
        return _clamp01(default)


def _norm_source(raw: Any) -> str:
    s = str(raw or "unknown").strip().lower()
    return s if s in SOURCE_SYSTEMS else "unknown"


def derive_sonic_plan(
    *,
    tempo_range_bpm: tuple[float, float] | list[float] = (60.0, 140.0),
    energy_level: float = 0.0,
    density_level: float = 0.0,
    tension_level: float = 0.0,
    resolution_level: float = 0.0,
    symbolic_depth_bonus: float = 0.0,
) -> dict[str, Any]:
    """Notion PATCH-006 deterministic mapping rules (sonic plan seed only)."""
    energy = _f01(energy_level)
    density = _f01(density_level)
    tension = _f01(tension_level)
    resolution = _f01(resolution_level)
    depth = _f01(symbolic_depth_bonus)

    try:
        lo, hi = float(tempo_range_bpm[0]), float(tempo_range_bpm[1])
    except (TypeError, ValueError, IndexError):
        lo, hi = 60.0, 140.0
    if hi < lo:
        lo, hi = hi, lo
    mean_tempo = (lo + hi) / 2.0
    tempo = mean_tempo + energy * 18.0 - tension * 8.0
    tempo = max(40.0, min(220.0, tempo))
    tempo_bpm = int(round(tempo))

    pulse_density = _clamp01(density * 0.65 + energy * 0.35)
    syncopation = _clamp01(
        tension * 0.55 + density * 0.25 + (1.0 - resolution) * 0.20
    )
    silence_ratio = _clamp01((1.0 - density) * 0.40 + tension * 0.15)
    spectral = _clamp01(energy * 0.55 + resolution * 0.20 + density * 0.25)
    grain = _clamp01(tension * 0.45 + density * 0.35 + (1.0 - resolution) * 0.20)
    space = _clamp01(resolution * 0.50 + (1.0 - tension) * 0.25 + depth * 0.25)

    nodes = ["clock", "rhythm", "timbre", "modulation", "silence"]
    if grain >= 0.35:
        nodes.append("texture")
    if space >= 0.35:
        nodes.append("spatial")
    if tension >= 0.50 or resolution >= 0.50:
        nodes.append("transition")

    return {
        "schema_version": "BeatOvenSonicPlanSeed.v0",
        "tempo_bpm": tempo_bpm,
        "pulse_density": _round6(pulse_density),
        "syncopation_level": _round6(syncopation),
        "silence_ratio": _round6(silence_ratio),
        "spectral_brightness": _round6(spectral),
        "texture_grain": _round6(grain),
        "space_depth": _round6(space),
        "graph_node_types": nodes,
    }


def build_integration_operator_packet(
    *,
    intent_id: str = "",
    source_system: str = "manual",
    intent_summary: str = "",
    tempo_range_bpm: tuple[float, float] | list[float] = (60.0, 140.0),
    energy_level: float = 0.0,
    density_level: float = 0.0,
    tension_level: float = 0.0,
    resolution_level: float = 0.0,
    symbolic_depth_bonus: float = 0.0,
    felt_alignment: float | None = None,
    blocked_by: list[str] | None = None,
) -> dict[str, Any]:
    """Build BeatOvenPsyFiIntegrationOperatorPacket.v0 (SHADOW_ARTIFACT)."""
    iid = str(intent_id or "").strip() or "intent_unspecified"
    src = _norm_source(source_system)
    summary = str(intent_summary or "").strip()

    blocks = list(blocked_by or [])
    for b in (
        "EXTERNAL_AUDIO_RENDER_BLOCKED",
        "DAW_CONTROL_BLOCKED",
        "HARDWARE_CONTROL_BLOCKED",
        "PUBLISHING_BLOCKED",
        "MINTING_BLOCKED",
        "PROMOTION_BLOCKED",
    ):
        if b not in blocks:
            blocks.append(b)

    if not summary:
        if "EMPTY_INTENT_SUMMARY" not in blocks:
            blocks.append("EMPTY_INTENT_SUMMARY")

    plan = derive_sonic_plan(
        tempo_range_bpm=tempo_range_bpm,
        energy_level=energy_level,
        density_level=density_level,
        tension_level=tension_level,
        resolution_level=resolution_level,
        symbolic_depth_bonus=symbolic_depth_bonus,
    )

    felt: float | None
    try:
        felt = _clamp01(float(felt_alignment)) if felt_alignment is not None else None
    except (TypeError, ValueError):
        felt = None

    if src == "psyfi" or felt is not None:
        bridge_status = "BRIDGED"
    elif summary:
        bridge_status = "SEED_ONLY"
    else:
        bridge_status = "NOT_COMPUTABLE"

    if not summary and src == "unknown":
        readiness = "NOT_COMPUTABLE"
    else:
        readiness = "SHADOW_OPERATOR_REVIEW"

    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "pipeline_id": PIPELINE_ID,
        "packet_id": "bopi_"
        + canonical_hash(
            {
                "intent_id": iid,
                "tempo_bpm": plan["tempo_bpm"],
                "graph_node_types": plan["graph_node_types"],
            }
        )[:16],
        "intent_id": iid,
        "source_system": src,
        "intent_summary": summary or "UNSPECIFIED",
        "runic_core": {
            "schema_version": "BeatOvenPsyFiRunicCore.v0",
            "runes": list(SHARED_RUNES),
            "shared": True,
        },
        "sonic_plan": plan,
        "psyfi_bridge": {
            "schema_version": "PsyFiBeatOvenBridge.v0",
            "bridge_status": bridge_status,
            "subjective_feedback_only": True,
            "felt_alignment": felt,
        },
        "readiness": readiness,
        "blocked_by": blocks,
        "external_audio_render_blocked": True,
        "daw_control_blocked": True,
        "hardware_control_blocked": True,
        "publishing_blocked": True,
        "minting_blocked": True,
        "authority": dict(DEFAULT_AUTHORITY),
        "advisory_only": True,
        "lane": "SHADOW_ARTIFACT",
        "producer": dict(PRODUCER),
        "deterministic_timestamp": DETERMINISTIC_TIMESTAMP,
    }
    body["canonical_hash"] = canonical_hash(body)
    return body


def build_integration_operator_packet_from_intent(
    intent: dict[str, Any],
) -> dict[str, Any]:
    """Lift SonicIntent-like dict into integration operator packet."""
    d = intent if isinstance(intent, dict) else {}
    source = d.get("source") if isinstance(d.get("source"), dict) else {}
    intent_body = d.get("intent") if isinstance(d.get("intent"), dict) else d
    tempo = intent_body.get("tempo_range_bpm") or d.get("tempo_range_bpm") or (60, 140)
    if isinstance(tempo, (list, tuple)) and len(tempo) >= 2:
        tempo_range = (tempo[0], tempo[1])
    else:
        tempo_range = (60.0, 140.0)

    feedback = d.get("feedback") if isinstance(d.get("feedback"), dict) else {}

    return build_integration_operator_packet(
        intent_id=str(d.get("intent_id") or d.get("id") or ""),
        source_system=str(
            source.get("source_system") or d.get("source_system") or "manual"
        ),
        intent_summary=str(
            intent_body.get("intent_summary") or d.get("intent_summary") or ""
        ),
        tempo_range_bpm=tempo_range,
        energy_level=intent_body.get("energy_level", d.get("energy_level", 0.0)),
        density_level=intent_body.get("density_level", d.get("density_level", 0.0)),
        tension_level=intent_body.get("tension_level", d.get("tension_level", 0.0)),
        resolution_level=intent_body.get(
            "resolution_level", d.get("resolution_level", 0.0)
        ),
        symbolic_depth_bonus=intent_body.get(
            "symbolic_depth_bonus", d.get("symbolic_depth_bonus", 0.0)
        ),
        felt_alignment=feedback.get("felt_alignment", d.get("felt_alignment")),
        blocked_by=list(d.get("blocked_by") or [])
        if isinstance(d.get("blocked_by"), list)
        else None,
    )
