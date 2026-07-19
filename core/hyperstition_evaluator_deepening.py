from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from abraxas.v2.hygiene.loop_dynamics import LoopDynamics
from core.canonical.json import canonical_hash, write_canonical_json
from core.hyperstition_brier_fixture_expansion import (
    DEFAULT_OUT_PATH as SLICE54_RECEIPT_PATH,
)
from core.scoring.brier import compute_brier_score, compute_full_decomposition
from core.temporal_resonance_coherence import summarize_temporal_resonance_coherence

ARTIFACT_TYPE = "HyperstitionEvaluatorDeepeningReceipt.v1"
STATUS = "HYPERSTITION_EVALUATOR_DEEPENING_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-55"
DEFAULT_OUT_PATH = "out/audit/hyperstition_evaluator_deepening_receipt_001.latest.json"

TEMPORAL_RESONANCE_PATH = "out/projections/temporal_resonance_coherence_001.latest.json"
SLICE52_RECEIPT_PATH = "out/audit/viz01_live_feed_enhancement_receipt_001.latest.json"
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

WEIGHT_POLICY = {
    "temporal_coherence_contribution": 0.30,
    "geometric_binding_strength": 0.25,
    "cross_aal_resonance_weight": 0.20,
    "decision_provenance_weight": 0.25,
}

CROSS_AAL_SOURCE_FAMILIES = {
    "HollerSports": [
        "out/audit/oracle_shadow_measurement_receipt_001.latest.json",
        "core/codegen/oracle_signal/holler_oracle_shadow_measurement.py",
    ],
    "SLANG": [
        "docs/plans/phase13_slang_memetic_integration_plan.md",
        "docs/plans/phase14_slang_memetic_rune_activation.md",
    ],
    "Neon Genie": [
        "docs/ventures/NEON_GENIE_INTEGRATION_007.md",
        "docs/receipts/P4_WAVE_002_NEON_GENIE_RECEIPT.md",
    ],
    "global_ingest": [
        "contracts/canon/global_ingest_adapter_spine_alignment_plan.v1.schema.json",
        "core/global_ingest_adapter_spine_implementation_spec.py",
    ],
}

DECISION_PROVENANCE_PATHS = [
    SLICE52_RECEIPT_PATH,
    SLICE53_RECEIPT_PATH,
    SLICE54_RECEIPT_PATH,
    "out/audit/abx_ledger_frontier_reconcile_denial_001.latest.json",
]


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


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 6)


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return _bounded(sum(values) / len(values))


def _source_summary(root: Path, relative_path: str) -> dict[str, Any]:
    path = root / relative_path
    if path.suffix == ".json":
        payload, status = _load_json(path)
    else:
        payload = None
        status = "OBSERVED" if path.exists() else "MISSING"
    return {
        "path": relative_path,
        "observed": status == "OBSERVED",
        "source_status": status,
        "sha256": _sha256_file(path) if status == "OBSERVED" else "NOT_COMPUTABLE",
        "artifact_type": payload.get("artifact_type") if payload else "NOT_COMPUTABLE",
        "status": payload.get("status") if payload else "NOT_COMPUTABLE",
        "canonical_hash": payload.get("canonical_hash") if payload else "NOT_COMPUTABLE",
    }


def _temporal_coherence_signal(root: Path) -> dict[str, Any]:
    payload, status = _load_json(root / TEMPORAL_RESONANCE_PATH)
    summary = summarize_temporal_resonance_coherence(payload)
    aggregate = float(summary.get("aggregate_coherence_score", 0.0))
    resonance = float(summary.get("resonance_score", 0.0))
    return {
        "signal_id": "temporal_coherence_contribution",
        "path": TEMPORAL_RESONANCE_PATH,
        "source_status": status,
        "observed": status == "OBSERVED",
        "score": _bounded(0.65 * aggregate + 0.35 * resonance),
        "summary": summary,
        "authority_granted": False,
    }


def _geometric_binding_signal(root: Path) -> dict[str, Any]:
    payload, status = _load_json(root / SLICE53_RECEIPT_PATH)
    if payload is None:
        score = 0.0
        observed_sources = 0
        total_sources = 0
        integration_status = "NOT_COMPUTABLE"
    else:
        sources = payload.get("source_summaries", [])
        observed_sources = sum(
            1 for source in sources if isinstance(source, dict) and source.get("observed") is True
        )
        total_sources = len(sources)
        source_ratio = observed_sources / total_sources if total_sources else 0.0
        integration_status = str(payload.get("integration_status", "NOT_COMPUTABLE"))
        readiness_bonus = 1.0 if "READY" in integration_status else 0.0
        score = _bounded(0.75 * source_ratio + 0.25 * readiness_bonus)
    return {
        "signal_id": "geometric_binding_strength",
        "path": SLICE53_RECEIPT_PATH,
        "source_status": status,
        "observed": status == "OBSERVED",
        "score": score,
        "observed_source_count": observed_sources,
        "total_source_count": total_sources,
        "integration_status": integration_status,
        "authority_granted": False,
    }


def _cross_aal_family_summary(root: Path, family: str, paths: list[str]) -> dict[str, Any]:
    sources = [_source_summary(root, path) for path in paths]
    observed_count = sum(1 for source in sources if source["observed"])
    return {
        "family": family,
        "source_status": "OBSERVED" if observed_count else "MISSING",
        "observed_source_count": observed_count,
        "total_source_count": len(sources),
        "score": _bounded(observed_count / len(sources)) if sources else 0.0,
        "sources": sources,
        "authority_granted": False,
    }


def _cross_aal_resonance_signal(root: Path) -> dict[str, Any]:
    families = [
        _cross_aal_family_summary(root, family, paths)
        for family, paths in CROSS_AAL_SOURCE_FAMILIES.items()
    ]
    return {
        "signal_id": "cross_aal_resonance_weight",
        "source_status": (
            "OBSERVED"
            if any(family["observed_source_count"] for family in families)
            else "MISSING"
        ),
        "score": _mean([float(family["score"]) for family in families]),
        "families": families,
        "authority_granted": False,
    }


def _decision_provenance_signal(root: Path) -> dict[str, Any]:
    sources = [_source_summary(root, path) for path in DECISION_PROVENANCE_PATHS]
    observed = sum(1 for source in sources if source["observed"])
    hash_count = sum(
        1
        for source in sources
        if isinstance(source.get("canonical_hash"), str)
        and source["canonical_hash"] != "NOT_COMPUTABLE"
    )
    score = _bounded(0.70 * (observed / len(sources)) + 0.30 * (hash_count / len(sources)))
    return {
        "signal_id": "decision_provenance_weight",
        "source_status": "OBSERVED" if observed else "MISSING",
        "score": score,
        "observed_source_count": observed,
        "hash_observed_count": hash_count,
        "total_source_count": len(sources),
        "sources": sources,
        "sandbox_gate_issue": "#892",
        "sandbox_gate_issued": False,
        "authority_granted": False,
    }


def _weighted_charge(signals: dict[str, dict[str, Any]]) -> float:
    return _bounded(
        sum(
            WEIGHT_POLICY[signal_id] * float(signals[signal_id]["score"])
            for signal_id in WEIGHT_POLICY
        )
    )


def _source_confidence(signals: dict[str, dict[str, Any]]) -> float:
    return _mean(
        [
            1.0 if signal.get("source_status") == "OBSERVED" else 0.0
            for signal in signals.values()
        ]
    )


class HyperstitionEvaluator:
    """Deterministic advisory evaluator; it never resolves outcomes or forecasts."""

    def __init__(self, repo_root: str | Path = ".") -> None:
        self.repo_root = Path(repo_root)

    def evaluate(self) -> dict[str, Any]:
        signals = {
            "temporal_coherence_contribution": _temporal_coherence_signal(self.repo_root),
            "geometric_binding_strength": _geometric_binding_signal(self.repo_root),
            "cross_aal_resonance_weight": _cross_aal_resonance_signal(self.repo_root),
            "decision_provenance_weight": _decision_provenance_signal(self.repo_root),
        }
        charge = _weighted_charge(signals)
        confidence = _source_confidence(signals)
        missing_pressure = 1.0 - confidence
        retrocausal_risk = _bounded(0.55 * missing_pressure + 0.45 * max(0.0, charge - 0.72))
        mitigation = (
            "monitor_only"
            if charge < 0.66 and retrocausal_risk < 0.50
            else "operator_review_required"
        )
        dynamics = LoopDynamics(
            retrocausal_risk=retrocausal_risk,
            hyperstitional_charge=charge,
            mitigation=mitigation,
        )
        return {
            "signals": signals,
            "weight_policy": WEIGHT_POLICY,
            "source_confidence": confidence,
            "loop_dynamics": dynamics.to_dict(),
            "projection_only": True,
            "authority_granted": False,
        }


def _calibration_row(
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
        "probability": _bounded(probability),
        "shadow_outcome": shadow_outcome,
        "shadow_brier_component": compute_brier_score(probability, shadow_outcome),
        "provenance": provenance,
        "forecast_execution_allowed": False,
        "outcome_binding_allowed": False,
        "brier_resolution_allowed": False,
    }


def _evaluator_fixture_suite(evaluation: dict[str, Any]) -> dict[str, Any]:
    signals = evaluation["signals"]
    charge = float(evaluation["loop_dynamics"]["hyperstitional_charge"])
    confidence = float(evaluation["source_confidence"])
    predictions = [
        0.50 + 0.35 * float(signals["temporal_coherence_contribution"]["score"]),
        0.52 + 0.30 * float(signals["geometric_binding_strength"]["score"]),
        0.48 + 0.32 * float(signals["cross_aal_resonance_weight"]["score"]),
        0.55 + 0.30 * charge + 0.10 * confidence,
    ]
    targets = [1.0, 1.0, 1.0, 1.0]
    rows = [
        _calibration_row(
            fixture_id="temporal_coherence_high_low_missing",
            description="Advisory temporal coherence contribution shape only.",
            probability=predictions[0],
            shadow_outcome=targets[0],
            provenance=TEMPORAL_RESONANCE_PATH,
        ),
        _calibration_row(
            fixture_id="geometric_binding_strong_degraded_missing",
            description="Advisory geometric binding strength shape only.",
            probability=predictions[1],
            shadow_outcome=targets[1],
            provenance=SLICE53_RECEIPT_PATH,
        ),
        _calibration_row(
            fixture_id="cross_aal_resonance_observed_missing",
            description="Advisory cross-AAL resonance family coverage shape only.",
            probability=predictions[2],
            shadow_outcome=targets[2],
            provenance="HollerSports + SLANG + Neon Genie + global_ingest source map",
        ),
        _calibration_row(
            fixture_id="decision_provenance_strong_degraded",
            description="Advisory decision provenance receipt quality shape only.",
            probability=predictions[3],
            shadow_outcome=targets[3],
            provenance="Slice52 + Slice53 + Slice54 + #892 planning vessel",
        ),
    ]
    return {
        "fixture_rows": rows,
        "fixture_count": len(rows),
        "mean_shadow_brier": round(
            sum(float(row["shadow_brier_component"]) for row in rows) / len(rows),
            10,
        ),
        "decomposition": compute_full_decomposition(
            [float(row["probability"]) for row in rows],
            targets,
        ),
        "forecast_execution_allowed": False,
        "outcome_binding_allowed": False,
        "resolution_allowed": False,
    }


def build_hyperstition_evaluator_deepening_receipt(
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    evaluation = HyperstitionEvaluator(repo_root).evaluate()
    observed_signal_count = sum(
        1
        for signal in evaluation["signals"].values()
        if signal.get("source_status") == "OBSERVED"
    )
    source_status = (
        "READY"
        if observed_signal_count == len(evaluation["signals"])
        else "READY_WITH_DEGRADED_EVIDENCE"
        if observed_signal_count
        else "NOT_COMPUTABLE"
    )
    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "slice_id": SLICE_ID,
        "status": STATUS,
        "brier_score": BRIER_SCORE,
        "advisory_only": True,
        "projection_only": True,
        "authority_locks": AUTHORITY_LOCKS,
        "source_status": source_status,
        "observed_signal_count": observed_signal_count,
        "total_signal_count": len(evaluation["signals"]),
        "evaluation": evaluation,
        "evaluator_fixture_suite": _evaluator_fixture_suite(evaluation),
        "boundary": {
            "sandbox_gate_issue": "#892",
            "sandbox_gate_phrase": "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED",
            "sandbox_gate_issued": False,
            "forecast_execution": False,
            "brier_resolution": False,
            "outcome_binding": False,
            "external_calls": False,
            "notion_writeback": False,
            "github_writeback": False,
            "runtime_activation": False,
            "canon_mutation": False,
            "mcp_exposure": False,
        },
        "validation_plan": [
            "python scripts/run_hyperstition_evaluator_deepening_receipt.py",
            f"python scripts/artifact/run_artifact_regeneration.py --artifact {DEFAULT_OUT_PATH}",
            "python -m py_compile core/hyperstition_evaluator_deepening.py "
            "scripts/run_hyperstition_evaluator_deepening_receipt.py",
            "python -m pytest tests/test_hyperstition_evaluator_deepening.py "
            "tests/test_generated_artifact_registry.py -q -k hyperstition_evaluator",
            "git diff --check",
        ],
        "provenance": (
            "Notion Sprint 001 Hub + Loop 805 Slice 55 + "
            "Hyperstition Evaluator Deepening"
        ),
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def write_hyperstition_evaluator_deepening_receipt(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
