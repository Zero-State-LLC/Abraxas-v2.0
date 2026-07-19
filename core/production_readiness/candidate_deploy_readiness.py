"""WP-DEPLOY: candidate deploy readiness packet (default NO_GO).

Documents what a controlled candidate trial would require.
Does not authorize deploy or production activation.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json

PRODUCER = "run_candidate_deploy_readiness"
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


def build_candidate_deploy_readiness(
    repo_root: Path,
    *,
    produced_at: str | None = None,
    write: bool = True,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)

    release = _load(repo_root, "out/production_readiness/ws8/release_decision.v1.json") or {}
    scorecard = _load(repo_root, "out/production_readiness/ws8/freeze_gate_scorecard.v1.json") or {}
    activation = _load(
        repo_root, "out/production_readiness/ws8/production_activation_authority_gate.v1.json"
    )
    inventory = _load(
        repo_root, "out/production_readiness/ws8/supported_surface_freeze_inventory.v1.json"
    ) or {}

    candidate = release.get("decision_code") == "CANDIDATE_APPROVED"
    deploy_held = bool(release.get("deploy_held", True))
    activation_denied = True
    if activation is not None:
        activation_denied = activation.get("status") != "AUTHORIZED"

    checklist = [
        {
            "id": "CD-01",
            "item": "Release decision is CANDIDATE_APPROVED",
            "status": "PASS" if candidate else "FAIL",
            "evidence": "out/production_readiness/ws8/release_decision.v1.json",
        },
        {
            "id": "CD-02",
            "item": "Freeze scorecard all_pass",
            "status": "PASS" if (scorecard.get("summary") or {}).get("all_pass") else "FAIL",
            "evidence": "out/production_readiness/ws8/freeze_gate_scorecard.v1.json",
        },
        {
            "id": "CD-03",
            "item": "SUPPORTED surface inventory present",
            "status": "PASS" if inventory.get("summary") else "FAIL",
            "evidence": "out/production_readiness/ws8/supported_surface_freeze_inventory.v1.json",
        },
        {
            "id": "CD-04",
            "item": "Deploy remains held (no silent unhold)",
            "status": "PASS" if deploy_held or not candidate else "WARN",
            "evidence": "release_decision.deploy_held",
        },
        {
            "id": "CD-05",
            "item": "Production activation authority is not AUTHORIZED",
            "status": "PASS" if activation_denied else "FAIL",
            "evidence": "out/production_readiness/ws8/production_activation_authority_gate.v1.json",
        },
        {
            "id": "CD-06",
            "item": "Operator deploy plan + rollback plan authored (human)",
            "status": "MISSING",
            "evidence": "required outside repo automation",
        },
        {
            "id": "CD-07",
            "item": "Environment secrets / target env attestation",
            "status": "MISSING",
            "evidence": "operator-controlled; not in this packet",
        },
        {
            "id": "CD-08",
            "item": "Explicit deploy unhold decision record",
            "status": "MISSING",
            "evidence": "would un-set deploy_held; not emitted by this producer",
        },
    ]

    missing = [c for c in checklist if c["status"] in {"FAIL", "MISSING"}]
    # Default NO_GO until human deploy plan + unhold exist
    go_no_go = "NO_GO"
    if not missing and candidate and not activation_denied:
        go_no_go = "NO_GO"  # still no-go without human; keep strict
    if missing:
        go_no_go = "NO_GO"
    elif candidate and activation_denied:
        go_no_go = "NO_GO_CANDIDATE_READY_DEPLOY_HELD"

    packet: dict[str, Any] = {
        "schema_version": "candidate_deploy_readiness.v1",
        "artifact_type": "candidate_deploy_readiness",
        "work_package": "WP-DEPLOY_CANDIDATE_READINESS",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial",
        "go_no_go": go_no_go,
        "production_activation_authorized": False,
        "deploy_authorized": False,
        "release_decision_code": release.get("decision_code"),
        "readiness_state": release.get("readiness_state"),
        "surface_summary": inventory.get("summary"),
        "checklist": checklist,
        "summary": {
            "checklist_count": len(checklist),
            "pass_count": sum(1 for c in checklist if c["status"] == "PASS"),
            "missing_count": sum(1 for c in checklist if c["status"] == "MISSING"),
            "fail_count": sum(1 for c in checklist if c["status"] == "FAIL"),
        },
        "blocked_reasons": [
            c["item"] for c in checklist if c["status"] in {"FAIL", "MISSING"}
        ],
        "operator_actions_for_future_go": [
            "Author human deploy plan with target env, blast radius, rollback",
            "Attest secrets/config for candidate environment only",
            "Emit explicit deploy-unhold decision (separate from CANDIDATE_APPROVED)",
            "Keep production activation DENIED unless separate WP-AUTH AUTHORIZED",
            "Do not market as production ready",
        ],
        "notes": [
            "Default is NO_GO even when freeze gates pass.",
            "CANDIDATE_APPROVED ≠ deploy authorized.",
            "Linked plan: out/production_readiness/CONTINUATION_PLAN.v8.md",
        ],
    }

    if write:
        out_dir = repo_root / OUT_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(out_dir / "candidate_deploy_readiness.v1.json", packet)

    return packet
