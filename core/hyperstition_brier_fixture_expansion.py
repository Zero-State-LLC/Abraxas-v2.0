from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from abraxas.v2.governance.mode import HygieneMode
from abraxas.v2.hygiene.loop_dynamics import LoopDynamics
from abraxas.v2.hygiene.registers import V2Output
from abraxas.v2.hygiene.runes.hyperstition_tag import HyperstitionTagRune
from core.canonical.json import canonical_hash, write_canonical_json
from core.scoring.brier import compute_brier_score, compute_full_decomposition
from core.temporal_resonance_coherence import summarize_temporal_resonance_coherence

ARTIFACT_TYPE = "HyperstitionBrierFixtureExpansionReceipt.v1"
STATUS = "HYPERSTITION_BRIER_FIXTURE_EXPANSION_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-54"
DEFAULT_OUT_PATH = "out/audit/hyperstition_brier_fixture_expansion_receipt_001.latest.json"

TEMPORAL_RESONANCE_PATH = "out/projections/temporal_resonance_coherence_001.latest.json"
VIZ01_RECEIPT_PATH = "out/audit/viz01_live_feed_enhancement_receipt_001.latest.json"
SLICE53_RECEIPT_PATH = (
    "out/audit/geometric_binder_orchestrator_integration_harness_001.latest.json"
)

AUTHORITY_LOCKS = {
    "brier_resolution": False,
    "canon_mutation": False,
    "external_calls": False,
    "forecast_execution": False,
    "github_writeback": False,
    "mcp_exposure": False,
    "notion_writeback": False,
    "outcome_binding": False,
    "pipeline_activation": False,
    "production_activation": False,
    "runtime_activation": False,
    "runtime_mutation": False,
    "sandbox_probe_execution": False,
    "secret_capture": False,
}


def _load_json(path: Path) -> tuple[dict[str, Any] | None, str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "MISSING"
    except (OSError, json.JSONDecodeError):
        return None, "NOT_COMPUTABLE"
    if not isinstance(payload, dict):
        return None, "NOT_COMPUTABLE"
    return payload, "OBSERVED"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source_summary(root: Path, relative_path: str) -> dict[str, Any]:
    path = root / relative_path
    payload, status = _load_json(path)
    return {
        "path": relative_path,
        "observed": status == "OBSERVED",
        "source_status": status,
        "sha256": _sha256_file(path) if status == "OBSERVED" else "NOT_COMPUTABLE",
        "artifact_type": payload.get("artifact_type") if payload else "NOT_COMPUTABLE",
        "status": payload.get("status") if payload else "NOT_COMPUTABLE",
        "canonical_hash": payload.get("canonical_hash") if payload else "NOT_COMPUTABLE",
    }


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 6)


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return _bounded(sum(values) / len(values))


def _temporal_summary(root: Path) -> dict[str, Any]:
    payload, status = _load_json(root / TEMPORAL_RESONANCE_PATH)
    summary = summarize_temporal_resonance_coherence(payload)
    return {
        "path": TEMPORAL_RESONANCE_PATH,
        "source_status": status,
        "summary": summary,
        "observed": status == "OBSERVED",
        "canonical_hash": (
            canonical_hash(payload) if payload is not None else "NOT_COMPUTABLE"
        ),
    }


def _rune_tag_evidence() -> dict[str, Any]:
    rune = HyperstitionTagRune()
    output = V2Output(observed={"slice": SLICE_ID}, inferred={}, speculative={})
    tagged = rune.apply(
        output,
        {"hyperstition_tag": "SLICE54_ADVISORY_CALIBRATION"},
        HygieneMode.ADVISORY,
    )
    strict_requires_tag = False
    try:
        rune.apply(output, {}, HygieneMode.STRICT)
    except ValueError:
        strict_requires_tag = True
    return {
        "rune_id": rune.rune_id,
        "advisory_tag_applied": (
            tagged.provenance.get("hyperstition_tag")
            == "SLICE54_ADVISORY_CALIBRATION"
        ),
        "strict_requires_tag": strict_requires_tag,
        "execution_authority": False,
    }


def _loop_dynamics(
    *,
    resonance_score: float,
    dissonance_score: float,
    source_observation_ratio: float,
) -> dict[str, Any]:
    hyperstitional_charge = _bounded(
        0.45 * resonance_score + 0.35 * source_observation_ratio + 0.20 * dissonance_score
    )
    retrocausal_risk = _bounded(0.65 * dissonance_score + 0.35 * (1.0 - source_observation_ratio))
    mitigation = (
        "monitor_only"
        if hyperstitional_charge < 0.66 and retrocausal_risk < 0.50
        else "operator_review_required"
    )
    dynamics = LoopDynamics(
        retrocausal_risk=retrocausal_risk,
        hyperstitional_charge=hyperstitional_charge,
        mitigation=mitigation,
    )
    return dynamics.to_dict()


def _fixture_row(
    *,
    fixture_id: str,
    description: str,
    probability: float,
    shadow_outcome: float,
    provenance: str,
) -> dict[str, Any]:
    return {
        "fixture_id": fixture_id,
        "description": description,
        "probability": probability,
        "shadow_outcome": shadow_outcome,
        "shadow_brier_component": compute_brier_score(probability, shadow_outcome),
        "provenance": provenance,
        "fixture_binding_allowed": False,
        "outcome_binding_allowed": False,
        "brier_resolution_allowed": False,
        "forecast_execution_allowed": False,
    }


def _brier_fixture_suite(loop_dynamics: dict[str, Any]) -> dict[str, Any]:
    charge = float(loop_dynamics["hyperstitional_charge"])
    risk = float(loop_dynamics["retrocausal_risk"])
    predictions = [
        _bounded(0.72 - risk * 0.12),
        _bounded(0.64 + charge * 0.10),
        _bounded(0.58 + charge * 0.08 - risk * 0.05),
        _bounded(0.52 + charge * 0.12),
    ]
    targets = [1.0, 1.0, 0.0, 1.0]
    fixtures = [
        _fixture_row(
            fixture_id="gate_probe_decision_quality",
            description="Advisory gate/probe denial quality calibration only.",
            probability=predictions[0],
            shadow_outcome=targets[0],
            provenance="#892 planning vessel + Slice45-Slice48 gate hardening",
        ),
        _fixture_row(
            fixture_id="rune_binding_quality_scoring",
            description="HyperstitionTagRune provenance binding calibration only.",
            probability=predictions[1],
            shadow_outcome=targets[1],
            provenance="abraxas/v2/hygiene/runes/hyperstition_tag.py",
        ),
        _fixture_row(
            fixture_id="forecast_accuracy_surface_calibration",
            description="Forecast surface calibration shape without live routing.",
            probability=predictions[2],
            shadow_outcome=targets[2],
            provenance="core/scoring/brier.py + Loop 805 Brier fixtures",
        ),
        _fixture_row(
            fixture_id="hyperstition_charge_over_time",
            description="Charge-over-time calibration shape without propagation.",
            probability=predictions[3],
            shadow_outcome=targets[3],
            provenance="LoopDynamics.v1 + temporal resonance summary",
        ),
    ]
    mean_shadow_brier = round(
        sum(float(row["shadow_brier_component"]) for row in fixtures) / len(fixtures),
        10,
    )
    return {
        "fixture_rows": fixtures,
        "fixture_count": len(fixtures),
        "mean_shadow_brier": mean_shadow_brier,
        "decomposition": compute_full_decomposition(predictions, targets),
        "resolution_allowed": False,
        "outcome_binding_allowed": False,
        "forecast_execution_allowed": False,
    }


def build_hyperstition_brier_fixture_expansion_receipt(
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    temporal = _temporal_summary(root)
    sources = [
        temporal,
        _source_summary(root, VIZ01_RECEIPT_PATH),
        _source_summary(root, SLICE53_RECEIPT_PATH),
    ]
    observed_count = sum(1 for source in sources if source["observed"])
    source_observation_ratio = _bounded(observed_count / len(sources))
    temporal_summary = temporal["summary"]
    resonance_score = float(temporal_summary.get("resonance_score", 0.0))
    dissonance_score = float(temporal_summary.get("dissonance_score", 0.0))
    dynamics = _loop_dynamics(
        resonance_score=resonance_score,
        dissonance_score=dissonance_score,
        source_observation_ratio=source_observation_ratio,
    )
    brier_suite = _brier_fixture_suite(dynamics)
    source_status = "READY_WITH_DEGRADED_EVIDENCE" if observed_count >= 2 else "NOT_COMPUTABLE"

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "slice_id": SLICE_ID,
        "status": STATUS,
        "brier_score": BRIER_SCORE,
        "advisory_only": True,
        "projection_only": True,
        "authority_locks": AUTHORITY_LOCKS,
        "source_status": source_status,
        "source_observation_ratio": source_observation_ratio,
        "source_summaries": sources,
        "loop_dynamics": dynamics,
        "hyperstition_charge_components": {
            "temporal_resonance_contribution": resonance_score,
            "dissonance_risk_contribution": dissonance_score,
            "source_observation_contribution": source_observation_ratio,
            "geometric_binding_strength": source_observation_ratio,
            "cross_aal_resonance_weight": _bounded(resonance_score * source_observation_ratio),
            "recent_decision_provenance_weight": source_observation_ratio,
        },
        "hyperstition_rune_evidence": _rune_tag_evidence(),
        "brier_fixture_suite": brier_suite,
        "integration_references": [
            {
                "surface": "VIZ-01 live feed",
                "path": VIZ01_RECEIPT_PATH,
                "execution_authority": False,
            },
            {
                "surface": "Geometric binder orchestrator harness",
                "path": SLICE53_RECEIPT_PATH,
                "execution_authority": False,
            },
            {
                "surface": "Temporal resonance coherence",
                "path": TEMPORAL_RESONANCE_PATH,
                "execution_authority": False,
            },
        ],
        "boundary": {
            "sandbox_gate_phrase": "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED",
            "sandbox_gate_issued": False,
            "forecast_execution": False,
            "brier_resolution": False,
            "outcome_binding": False,
            "notion_writeback": False,
            "github_writeback": False,
            "runtime_activation": False,
            "canon_mutation": False,
            "mcp_exposure": False,
        },
        "validation_plan": [
            "python scripts/run_hyperstition_brier_fixture_expansion_receipt.py",
            f"python scripts/run_artifact_regeneration.py --artifact {DEFAULT_OUT_PATH}",
            "python -m py_compile core/hyperstition_brier_fixture_expansion.py "
            "scripts/run_hyperstition_brier_fixture_expansion_receipt.py",
            "python -m pytest tests/test_hyperstition_brier_fixture_expansion.py "
            "tests/test_generated_artifact_registry.py -q -k hyperstition_brier_fixture",
            "git diff --check",
        ],
        "provenance": (
            "Notion Sprint 001 Hub + Loop 805 Slice 54 + "
            "Hyperstition Evaluator Deepening + Brier Fixture Expansion"
        ),
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def write_hyperstition_brier_fixture_expansion_receipt(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
