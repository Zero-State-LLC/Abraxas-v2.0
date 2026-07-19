"""WP-GATE: freeze gate scorecard for production candidate criteria."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json

PRODUCER = "run_freeze_gate_scorecard"
OUT_DIR_REL = Path("out/production_readiness/ws8")


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _git_sha(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "UNKNOWN"


def _load(repo_root: Path, rel: str) -> dict[str, Any] | None:
    path = repo_root / rel
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _gate(
    gate_id: str,
    name: str,
    status: str,
    evidence: list[str],
    notes: str = "",
) -> dict[str, Any]:
    return {
        "gate_id": gate_id,
        "name": name,
        "status": status,  # PASS | FAIL | PARTIAL | NOT_COMPUTABLE
        "evidence": evidence,
        "notes": notes,
    }


def build_freeze_gate_scorecard(
    repo_root: Path,
    *,
    produced_at: str | None = None,
    write: bool = True,
) -> dict[str, Any]:
    """Evaluate the eight candidate freeze criteria honestly."""
    repo_root = Path(repo_root).resolve()
    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)

    registry = _load(
        repo_root, "out/production_readiness/ws1/interface_registry_snapshot.v1.json"
    )
    services = _load(repo_root, "out/production_readiness/ws3/service_registry.v1.json")
    residual = _load(
        repo_root, "out/production_readiness/ws1/sole_writer_residual_acceptance.v1.json"
    )
    threat_decision = _load(
        repo_root,
        "out/production_readiness/ws8/threat_model_operator_decision_record.v0.json",
    )
    neon = _load(
        repo_root, "out/production_readiness/ws5/neon_genie_capability_allowlist.v1.json"
    )
    neon_check = _load(
        repo_root, "out/production_readiness/ws5/neon_genie_allowlist_check.v1.json"
    )
    blockers = _load(
        repo_root, "out/production_readiness/baseline/readiness_blockers.v1.json"
    )
    release = _load(repo_root, "out/production_readiness/ws8/release_decision.v1.json")
    baseline_receipt = _load(
        repo_root, "out/production_readiness/baseline/baseline_receipt.v1.json"
    )
    notion_wb = _load(
        repo_root, "out/production_readiness/ws8/notion_writeback_receipt.v1.json"
    )

    supported_count = int((registry or {}).get("summary", {}).get("supported_count") or 0)
    supported_services = int((services or {}).get("summary", {}).get("supported") or 0)

    # Gate 1 — live CI
    val = (baseline_receipt or {}).get("validation") or {}
    live_ok = bool(val.get("live_ci_executed") and val.get("exit_code") == 0)
    g1 = _gate(
        "G1",
        "Live CI green on pinned SHA",
        "PASS" if live_ok else "PARTIAL",
        ["out/production_readiness/baseline/baseline_receipt.v1.json"],
        notes="PASS only when baseline receipt attaches exit_code=0 live run.",
    )

    # Gate 2 — threat model operator review
    threat_ok = (threat_decision or {}).get("decision_code") == "ACCEPT_PARTIAL_BASELINE"
    g2 = _gate(
        "G2",
        "Threat model exists and operator-reviewed",
        "PASS" if threat_ok else "FAIL",
        [
            "out/production_readiness/ws8/threat_model.v0.json",
            "out/production_readiness/ws8/threat_model_operator_decision_record.v0.json",
        ],
        notes="Partial baseline acceptance does not equal Verified pen-test.",
    )

    # Gate 3 — SUPPORTED set
    g3 = _gate(
        "G3",
        "SUPPORTED set explicit and non-empty (≥3 preferred)",
        "PASS" if supported_count >= 3 else ("PARTIAL" if supported_count >= 1 else "FAIL"),
        ["out/production_readiness/ws1/interface_registry_snapshot.v1.json"],
        notes=f"supported_count={supported_count}",
    )

    # Gate 4 — sole-writer residual
    residual_ok = bool((residual or {}).get("gate_4_satisfied"))
    g4 = _gate(
        "G4",
        "Sole-writer residual accepted or under agreed threshold",
        "PASS" if residual_ok else "FAIL",
        [
            "out/production_readiness/ws1/sole_writer_residual_acceptance.v1.json",
            "out/production_readiness/ws1/sole_writer_advisory_report.v1.json",
        ],
        notes="Acceptance is known-debt only; fail-closed still off.",
    )

    # Gate 5 — Neon
    neon_ok = neon is not None and neon_check is not None
    g5 = _gate(
        "G5",
        "Neon Genie non-control (allowlist + check)",
        "PASS" if neon_ok else "FAIL",
        [
            "out/production_readiness/ws5/neon_genie_capability_allowlist.v1.json",
            "out/production_readiness/ws5/neon_genie_allowlist_check.v1.json",
        ],
    )

    # Gate 6 — SUPPORTED service
    g6 = _gate(
        "G6",
        "At least one SUPPORTED versioned service path",
        "PASS" if supported_services >= 1 else "FAIL",
        ["out/production_readiness/ws3/service_registry.v1.json"],
        notes=f"supported_services={supported_services}",
    )

    # Gate 7 — release decision present
    release_present = release is not None and bool(release.get("decision_code"))
    g7 = _gate(
        "G7",
        "Release decision artifact present",
        "PASS" if release_present else "FAIL",
        ["out/production_readiness/ws8/release_decision.v1.json"],
        notes=(
            f"decision_code={release.get('decision_code')}" if release_present else "missing"
        ),
    )

    # Gate 8 — no unmitigated OPEN P0
    open_p0 = [
        b
        for b in (blockers or {}).get("blockers", [])
        if b.get("priority") == "P0" and b.get("status") == "OPEN"
    ]
    g8 = _gate(
        "G8",
        "No unmitigated OPEN P0",
        "PASS" if not open_p0 else "FAIL",
        ["out/production_readiness/baseline/readiness_blockers.v1.json"],
        notes=f"open_p0_ids={[b.get('id') for b in open_p0]}",
    )

    gates = [g1, g2, g3, g4, g5, g6, g7, g8]
    pass_count = sum(1 for g in gates if g["status"] == "PASS")
    fail_count = sum(1 for g in gates if g["status"] == "FAIL")
    partial_count = sum(1 for g in gates if g["status"] == "PARTIAL")
    all_pass = pass_count == len(gates)

    notion_ok = bool((notion_wb or {}).get("writeback_performed"))

    scorecard: dict[str, Any] = {
        "schema_version": "freeze_gate_scorecard.v1",
        "artifact_type": "freeze_gate_scorecard",
        "work_package": "WP_GATE_FREEZE_SCORECARD",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial",
        "gates": gates,
        "summary": {
            "gate_count": len(gates),
            "pass_count": pass_count,
            "fail_count": fail_count,
            "partial_count": partial_count,
            "all_pass": all_pass,
            "candidate_eligible": all_pass,
            "notion_writeback_present": notion_ok,
        },
        "recommended_release_code": (
            "CANDIDATE_APPROVED"
            if all_pass
            else ("RELEASE_HELD" if fail_count or partial_count else "OPERATOR_REVIEW_REQUIRED")
        ),
        "notes": [
            "Scorecard is evidence-honest; all_pass does not auto-activate production.",
            "CANDIDATE_APPROVED still requires explicit operator release decision emission.",
            "Linked plan: out/production_readiness/CONTINUATION_PLAN.v6.md",
        ],
    }

    if write:
        out_dir = repo_root / OUT_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(out_dir / "freeze_gate_scorecard.v1.json", scorecard)

    return scorecard
