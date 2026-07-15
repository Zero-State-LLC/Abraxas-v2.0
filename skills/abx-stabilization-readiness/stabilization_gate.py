"""Stabilization gate — independent entry decision (no repairs)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import StabilizationGateDecision


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def evaluate_entry_gate(
    repo_root: Optional[Path] = None,
    evidence_dir: Optional[Path] = None,
) -> StabilizationGateDecision:
    """Consume evidence artifacts only; never mutates repo."""
    root = repo_root or Path(".")
    ev = evidence_dir or root / "out" / "stabilization_readiness"

    inventory = _load_json(ev / "contract_inventory.latest.json")
    repro = _load_json(ev / "reproducibility_audit.latest.json")
    harness = _load_json(ev / "conformance_harness.latest.json")
    director = _load_json(ev / "director_receipt.latest.json")

    blocking: List[str] = []
    bounded: List[str] = []
    evidence_refs: List[str] = []

    contract_ok = bool(inventory.get("contracts"))
    if not contract_ok:
        blocking.append("contract_inventory_missing_or_empty")
    else:
        evidence_refs.append(str(ev / "contract_inventory.latest.json"))

    repro_class = repro.get("overall_classification", "NOT_COMPUTABLE")
    repro_ok = repro_class in ("REPRODUCIBLE", "REPRODUCIBLE_WITH_DECLARED_VARIANCE")
    if not repro_ok:
        blocking.append(f"reproducibility:{repro_class}")
    else:
        evidence_refs.append(str(ev / "reproducibility_audit.latest.json"))
        if repro_class == "REPRODUCIBLE_WITH_DECLARED_VARIANCE":
            bounded.append("toolchain_variance_declared")

    harness_ok = harness.get("corpus_ready", False) and harness.get("case_count", 0) > 0
    if not harness_ok:
        blocking.append("conformance_corpus_not_ready")
    else:
        evidence_refs.append(str(ev / "conformance_harness.latest.json"))

    ts_finding = next(
        (f for f in repro.get("findings", []) if f.get("surface") == "typescript_toolchain"),
        {},
    )
    typescript_ready = ts_finding.get("classification") == "REPRODUCIBLE"
    python_ready = any(
        f.get("classification") in ("REPRODUCIBLE", "REPRODUCIBLE_WITH_DECLARED_VARIANCE")
        for f in repro.get("findings", [])
        if f.get("surface") == "pyproject.toml"
    ) or (root / "pyproject.toml").is_file()

    if blocking:
        decision = "STABILIZATION_ENTRY_HELD"
    elif bounded:
        decision = "STABILIZATION_ENTRY_READY_WITH_BOUNDED_EXCEPTIONS"
    else:
        decision = "STABILIZATION_ENTRY_READY"

    confidence = "PARTIAL" if bounded or not director else "FULL"
    if blocking:
        confidence = "PARTIAL"

    gate = StabilizationGateDecision(
        decision=decision,
        python_ready=python_ready,
        typescript_ready=typescript_ready,
        contract_inventory_complete=contract_ok,
        conformance_corpus_ready=harness_ok,
        reproducibility_ready=repro_ok,
        canonical_artifact_safety_ready=True,
        full_suite_confidence=confidence,
        blocking_findings=blocking,
        bounded_exceptions=bounded,
        evidence_refs=evidence_refs,
        operator_action_required=True,
    )
    h = gate.compute_hash()
    return StabilizationGateDecision(
        decision=gate.decision,
        python_ready=gate.python_ready,
        typescript_ready=gate.typescript_ready,
        contract_inventory_complete=gate.contract_inventory_complete,
        conformance_corpus_ready=gate.conformance_corpus_ready,
        reproducibility_ready=gate.reproducibility_ready,
        canonical_artifact_safety_ready=gate.canonical_artifact_safety_ready,
        full_suite_confidence=gate.full_suite_confidence,
        blocking_findings=gate.blocking_findings,
        bounded_exceptions=gate.bounded_exceptions,
        evidence_refs=gate.evidence_refs,
        operator_action_required=gate.operator_action_required,
        decision_hash=h,
    )


def write_gate_artifact(repo_root: Path, evidence_dir: Optional[Path] = None) -> Path:
    ev = evidence_dir or repo_root / "out" / "stabilization_readiness"
    ev.mkdir(parents=True, exist_ok=True)
    gate = evaluate_entry_gate(repo_root, ev)
    path = ev / "stabilization_gate_decision.latest.json"
    path.write_text(json.dumps(gate.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return path
