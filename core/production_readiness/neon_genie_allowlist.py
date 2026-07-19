"""WP-G: Neon Genie capability allowlist + advisory checker."""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json

PRODUCER = "run_neon_genie_allowlist"
OUT_DIR_REL = Path("out/production_readiness/ws5")
ALLOWLIST_ID = "NEON_GENIE_CAPABILITY_ALLOWLIST_001"

# Capabilities Neon Genie may exercise (advisory invention routing only).
ALLOWED: list[dict[str, Any]] = [
    {
        "capability_id": "venture_cycle.intake",
        "description": "Classify request mode and seed intake",
        "entry_points": [
            "skills/abx-neon-genie/neon_genie_intake.py",
            "skills/abx-neon-genie/neon_genie_router.py",
        ],
    },
    {
        "capability_id": "venture_cycle.discover",
        "description": "Bounded opportunity discovery from seeds/evidence",
        "entry_points": ["skills/abx-neon-genie/neon_genie_discover.py"],
    },
    {
        "capability_id": "venture_cycle.recombine",
        "description": "Recombine opportunities into candidates",
        "entry_points": ["skills/abx-neon-genie/neon_genie_recombine.py"],
    },
    {
        "capability_id": "venture_cycle.differentiate",
        "description": "Differentiate candidates against inventory",
        "entry_points": ["skills/abx-neon-genie/neon_genie_differentiate.py"],
    },
    {
        "capability_id": "venture_cycle.score",
        "description": "Advisory scoring of candidates",
        "entry_points": ["skills/abx-neon-genie/neon_genie_score.py"],
    },
    {
        "capability_id": "venture_cycle.shape",
        "description": "Shape venture packets",
        "entry_points": ["skills/abx-neon-genie/neon_genie_shape.py"],
    },
    {
        "capability_id": "venture_cycle.package",
        "description": "Package venture outputs for operator review",
        "entry_points": ["skills/abx-neon-genie/neon_genie_package.py"],
    },
    {
        "capability_id": "venture_cycle.catalog",
        "description": "Catalog / route classification of venture packets",
        "entry_points": ["skills/abx-neon-genie/neon_genie_catalog.py"],
    },
    {
        "capability_id": "overlap.detect",
        "description": "Overlap/duplicate detection against inventory",
        "entry_points": ["skills/abx-neon-genie/overlap_registry.py"],
    },
    {
        "capability_id": "entry.cli_runner",
        "description": "Advisory CLI entry scripts/codegen/run_abx_neon_genie.py",
        "entry_points": ["scripts/codegen/run_abx_neon_genie.py"],
    },
]

DENIED: list[dict[str, str]] = [
    {
        "capability_id": "governance.control",
        "reason": "Must not alter governance decisions or authority locks",
    },
    {
        "capability_id": "canon.mutate",
        "reason": "No canon mutation authority",
    },
    {
        "capability_id": "production.activate",
        "reason": "Production activation blocked; invention only",
    },
    {
        "capability_id": "forecast.influence",
        "reason": "Forecast lane not authorized for Neon Genie",
    },
    {
        "capability_id": "execution.runtime",
        "reason": "No runtime execution authority (route to other subsystems)",
    },
    {
        "capability_id": "minting.provenance_authority",
        "reason": "Minting/provenance authority is not Neon Genie scope",
    },
    {
        "capability_id": "visualization.render_control",
        "reason": "Visualization is projection-only via AAL-Viz routing",
    },
]


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


def build_allowlist(
    repo_root: Path,
    *,
    produced_at: str | None = None,
    write: bool = True,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)

    # Verify declared entry points exist (partial evidence)
    missing_paths: list[str] = []
    for cap in ALLOWED:
        for ep in cap.get("entry_points", []):
            if not (repo_root / ep).exists():
                missing_paths.append(ep)

    doc: dict[str, Any] = {
        "schema_version": "NeonGenieCapabilityAllowlist.v1",
        "allowlist_id": ALLOWLIST_ID,
        "work_package": "WP-G_NEON_GENIE_ALLOWLIST",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial" if not missing_paths else "Partial",
        "authority_locks": {
            "runtime_authority": False,
            "canon_authority": False,
            "promotion_authority": False,
            "forecast_authority": False,
            "governance_control": False,
            "production_activation": False,
            "advisory_invention_routing_only": True,
        },
        "allowed_capabilities": ALLOWED,
        "denied_capabilities": DENIED,
        "entry_point_presence": {
            "missing": missing_paths,
            "all_present": len(missing_paths) == 0,
        },
        "notes": [
            "Neon Genie invents and structures; it does not govern or execute.",
            "Denied capabilities fail closed in check_capability().",
            "RISK-013 mitigation; not a production activation grant.",
            "Linked plan: out/production_readiness/CONTINUATION_PLAN.v2.md",
        ],
    }

    if write:
        out_dir = repo_root / OUT_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(out_dir / "neon_genie_capability_allowlist.v1.json", doc)

    return doc


def check_capability(capability_id: str) -> dict[str, Any]:
    """Fail-closed capability gate for Neon Genie.

    Returns machine-readable ALLOWED or DENIED. Unknown IDs are DENIED.
    """
    denied_ids = {d["capability_id"] for d in DENIED}
    allowed_ids = {a["capability_id"] for a in ALLOWED}

    if capability_id in denied_ids:
        reason = next(
            d["reason"] for d in DENIED if d["capability_id"] == capability_id
        )
        return {
            "status": "DENIED",
            "capability_id": capability_id,
            "reason": reason,
            "retryable": False,
            "operator_action_required": True,
        }
    if capability_id in allowed_ids:
        return {
            "status": "ALLOWED",
            "capability_id": capability_id,
            "reason": "listed on Neon Genie capability allowlist",
            "retryable": False,
            "operator_action_required": False,
        }
    return {
        "status": "DENIED",
        "capability_id": capability_id,
        "reason": "unknown capability_id (fail closed)",
        "retryable": False,
        "operator_action_required": True,
    }


def build_allowlist_check_report(
    repo_root: Path,
    *,
    probe_capabilities: list[str] | None = None,
    produced_at: str | None = None,
    write: bool = True,
) -> dict[str, Any]:
    """Advisory report exercising allow/deny probes."""
    repo_root = Path(repo_root).resolve()
    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)
    allowlist = build_allowlist(repo_root, produced_at=produced_at, write=False)

    probes = probe_capabilities or [
        "venture_cycle.intake",
        "venture_cycle.package",
        "governance.control",
        "production.activate",
        "forecast.influence",
        "not.a.real.capability",
    ]
    results = [check_capability(c) for c in probes]
    denied = [r for r in results if r["status"] == "DENIED"]
    allowed = [r for r in results if r["status"] == "ALLOWED"]

    report: dict[str, Any] = {
        "schema_version": "neon_genie_allowlist_check.v1",
        "artifact_type": "neon_genie_allowlist_check",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial",
        "mode": "advisory_report_only",
        "allowlist_id": allowlist["allowlist_id"],
        "summary": {
            "probes": len(results),
            "allowed": len(allowed),
            "denied": len(denied),
            "entry_points_present": allowlist["entry_point_presence"]["all_present"],
        },
        "results": results,
        "notes": [
            "Denied unknown and explicitly forbidden capabilities.",
            "Wire into fast CI as report-only if desired (not required for WP-G).",
        ],
    }

    if write:
        out_dir = repo_root / OUT_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(out_dir / "neon_genie_allowlist_check.v1.json", report)
        write_canonical_json(
            out_dir / "neon_genie_capability_allowlist.v1.json", allowlist
        )

    return report
