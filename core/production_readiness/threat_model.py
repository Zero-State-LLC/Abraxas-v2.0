"""WP-F: minimal Threat Model v0 for bounded production candidate scope."""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json

PRODUCER = "run_threat_model_v0"
OUT_DIR_REL = Path("out/production_readiness/ws8")
MODEL_ID = "THREAT_MODEL_V0_PRODUCTION_CANDIDATE_001"


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


def build_threat_model_v0(
    repo_root: Path,
    *,
    produced_at: str | None = None,
    write: bool = True,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)

    model: dict[str, Any] = {
        "schema_version": "ThreatModel.v0",
        "model_id": MODEL_ID,
        "work_package": "WP-F_THREAT_MODEL_V0",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial",
        "scope": {
            "system": "Abraxas",
            "goal": "bounded production candidate (not public multi-tenant SaaS)",
            "in_scope": [
                "kernel contract surfaces (SUPPORTED interfaces)",
                "artifact publication under out/",
                "CI gates and advisory readiness checks",
                "Validation Service v1",
                "Neon Genie adapter boundary (advisory)",
                "operator-controlled governance locks",
            ],
            "out_of_scope": [
                "marketplace / public ecosystem",
                "consumer UI beyond operator console",
                "full multi-tenant cloud threat landscape",
                "physical facility security",
            ],
            "authority_posture": "fail-closed; production activation blocked by default",
        },
        "assets": [
            {
                "asset_id": "A-01",
                "name": "Canonical artifacts under out/",
                "sensitivity": "HIGH",
                "why": "Authoritative evidence, gates, and receipts",
            },
            {
                "asset_id": "A-02",
                "name": "SUPPORTED public contracts",
                "sensitivity": "HIGH",
                "why": "canonical_json + run_fast_ci semantics",
            },
            {
                "asset_id": "A-03",
                "name": "Operator decision / authority locks",
                "sensitivity": "CRITICAL",
                "why": "Prevents unauthorized production activation",
            },
            {
                "asset_id": "A-04",
                "name": "CI integrity",
                "sensitivity": "HIGH",
                "why": "Prevents silent contract or quality bypass",
            },
            {
                "asset_id": "A-05",
                "name": "Secrets / env credentials",
                "sensitivity": "CRITICAL",
                "why": "Notion, cloud, package registry access",
            },
            {
                "asset_id": "A-06",
                "name": "Neon Genie integration surface",
                "sensitivity": "MEDIUM",
                "why": "Must remain non-control-plane",
            },
        ],
        "threats": [
            {
                "threat_id": "T-01",
                "title": "Unauthorized production activation",
                "asset_ids": ["A-03"],
                "actor": "insider_or_compromised_agent",
                "impact": "CRITICAL",
                "likelihood": "MEDIUM",
                "status": "MITIGATING",
                "notes": "Authority locks + advisory-only defaults; continuous enforcement incomplete",
            },
            {
                "threat_id": "T-02",
                "title": "Artifact corruption or non-atomic publish",
                "asset_ids": ["A-01"],
                "actor": "bug_or_partial_write",
                "impact": "HIGH",
                "likelihood": "MEDIUM",
                "status": "MITIGATING",
                "notes": "canonical_json atomic writer is SUPPORTED; residual core writers remain",
            },
            {
                "threat_id": "T-03",
                "title": "Writer bypass of sole-writer pattern",
                "asset_ids": ["A-01", "A-02"],
                "actor": "developer_or_agent",
                "impact": "HIGH",
                "likelihood": "HIGH",
                "status": "MITIGATING",
                "notes": "Advisory sole-writer in CI; WP-D consolidating runtimes",
            },
            {
                "threat_id": "T-04",
                "title": "Silent contract change / unregistered public surface",
                "asset_ids": ["A-02"],
                "actor": "developer_or_agent",
                "impact": "HIGH",
                "likelihood": "MEDIUM",
                "status": "MITIGATING",
                "notes": "Interface registry + boundary advisory; few SUPPORTED promotions",
            },
            {
                "threat_id": "T-05",
                "title": "CI gate bypass or soft continue-on-error abuse",
                "asset_ids": ["A-04"],
                "actor": "insider_or_config_drift",
                "impact": "HIGH",
                "likelihood": "MEDIUM",
                "status": "OPEN",
                "notes": "Some historical gates soft; advisory gates intentionally fail-open",
            },
            {
                "threat_id": "T-06",
                "title": "Secret leakage via artifacts or logs",
                "asset_ids": ["A-05"],
                "actor": "misconfig_or_overlogging",
                "impact": "CRITICAL",
                "likelihood": "LOW",
                "status": "PARTIAL",
                "notes": ".env.example present; no exhaustive secret scan gate in this model",
            },
            {
                "threat_id": "T-07",
                "title": "Neon Genie gains governance control",
                "asset_ids": ["A-06", "A-03"],
                "actor": "integration_creep",
                "impact": "HIGH",
                "likelihood": "MEDIUM",
                "status": "OPEN",
                "notes": "RISK-013 allowlist not formalized",
            },
            {
                "threat_id": "T-08",
                "title": "Schema / path traversal via Validation Service",
                "asset_ids": ["A-02", "A-01"],
                "actor": "malicious_request",
                "impact": "MEDIUM",
                "likelihood": "LOW",
                "status": "MITIGATING",
                "notes": "schema_ref restricted to contracts/ with path traversal denied",
            },
            {
                "threat_id": "T-09",
                "title": "Forecast lane misuse as production influence",
                "asset_ids": ["A-03"],
                "actor": "misconfiguration",
                "impact": "HIGH",
                "likelihood": "LOW",
                "status": "MITIGATING",
                "notes": "FORECAST lane documented blocked; not fully service-gated",
            },
            {
                "threat_id": "T-10",
                "title": "Supply-chain dependency compromise",
                "asset_ids": ["A-04", "A-05"],
                "actor": "external",
                "impact": "HIGH",
                "likelihood": "LOW",
                "status": "MITIGATING",
                "notes": "dependabot + pip-audit + CodeQL present",
            },
        ],
        "controls": [
            {
                "control_id": "C-01",
                "name": "Fail-closed authority locks",
                "mitigates": ["T-01", "T-09"],
                "state": "PRESENT",
            },
            {
                "control_id": "C-02",
                "name": "canonical_json atomic writer (SUPPORTED)",
                "mitigates": ["T-02"],
                "state": "PRESENT",
            },
            {
                "control_id": "C-03",
                "name": "run_fast_ci (SUPPORTED) + advisory readiness gates",
                "mitigates": ["T-03", "T-04", "T-05"],
                "state": "PRESENT_PARTIAL",
            },
            {
                "control_id": "C-04",
                "name": "Interface registry + boundary allow-list",
                "mitigates": ["T-04"],
                "state": "PRESENT_PARTIAL",
            },
            {
                "control_id": "C-05",
                "name": "WP-D sole-writer consolidation",
                "mitigates": ["T-03", "T-02"],
                "state": "IN_PROGRESS",
            },
            {
                "control_id": "C-06",
                "name": "Validation Service schema_ref sandbox",
                "mitigates": ["T-08"],
                "state": "PRESENT",
            },
            {
                "control_id": "C-07",
                "name": "Dependency review / pip-audit / CodeQL",
                "mitigates": ["T-10"],
                "state": "PRESENT",
            },
            {
                "control_id": "C-08",
                "name": "Neon Genie capability allowlist",
                "mitigates": ["T-07"],
                "state": "MISSING",
            },
        ],
        "residual_risks": [
            {
                "id": "RR-01",
                "linked_threat": "T-03",
                "summary": "100+ remaining sole-writer findings; fail-closed not enabled",
                "risk_id": "RISK-008",
            },
            {
                "id": "RR-02",
                "linked_threat": "T-07",
                "summary": "Neon Genie allowlist missing",
                "risk_id": "RISK-013",
            },
            {
                "id": "RR-03",
                "linked_threat": "T-05",
                "summary": "Soft CI gates remain in historical workflows",
                "risk_id": "RISK-008",
            },
            {
                "id": "RR-04",
                "linked_threat": "T-01",
                "summary": "No single production release decision artifact yet",
                "risk_id": "RISK-014-adjacent",
            },
        ],
        "operator_actions": [
            "Review and accept ThreatModel.v0 as Partial security baseline",
            "Prioritize WP-G Neon allowlist and remaining WP-D consolidations",
            "Do not authorize production promotion until residual_risks accepted or closed",
            "Link this model into Notion readiness tracker when available (RISK-012)",
        ],
        "notes": [
            "v0 is intentionally minimal and evidence-honest (Partial, not Verified).",
            "Does not claim complete STRIDE coverage or pen-test results.",
            "Linked plan: out/production_readiness/CONTINUATION_PLAN.v1.md",
        ],
    }

    if write:
        out_dir = repo_root / OUT_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(out_dir / "threat_model.v0.json", model)

    return model
