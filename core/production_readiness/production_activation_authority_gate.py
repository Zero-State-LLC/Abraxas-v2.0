"""WP-AUTH: production activation authority gate (fail-closed DENIED).

Never authorizes production activation from automation defaults.
AUTHORIZATION requires an explicit operator-provided authority token
file that is intentionally not created by this program.
"""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json

PRODUCER = "run_production_activation_authority_gate"
OUT_DIR_REL = Path("out/production_readiness/ws8")

# Intentional non-default path: must be human-placed and reviewed.
# This producer never creates AUTHORIZATION_TOKEN_REL.
AUTHORIZATION_TOKEN_REL = Path(
    "input/production_activation/production_activation_authority.v1.json"
)


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


def build_production_activation_authority_gate(
    repo_root: Path,
    *,
    produced_at: str | None = None,
    write: bool = True,
) -> dict[str, Any]:
    """Emit fail-closed activation gate. Default and normal status: DENIED."""
    repo_root = Path(repo_root).resolve()
    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)

    token_path = repo_root / AUTHORIZATION_TOKEN_REL
    token_present = token_path.is_file()

    # Fail closed: even if a token file exists, this readiness program does not
    # auto-promote to AUTHORIZED without a dedicated offline review process.
    # Presence alone is insufficient here by design for this slice.
    status = "DENIED"
    reason = (
        "Fail-closed default. Production activation requires a separate human "
        "authority process outside the candidate freeze track. "
        f"Token file present={token_present} at {AUTHORIZATION_TOKEN_REL.as_posix()} "
        "(not auto-honored by this producer)."
    )

    gate: dict[str, Any] = {
        "schema_version": "production_activation_authority_gate.v1",
        "artifact_type": "production_activation_authority_gate",
        "work_package": "WP-AUTH_PRODUCTION_ACTIVATION_GATE",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial",
        "status": status,
        "production_activation_authorized": False,
        "fail_closed": True,
        "authorization_token_path": AUTHORIZATION_TOKEN_REL.as_posix(),
        "authorization_token_present": token_present,
        "authorization_token_honored": False,
        "reason": reason,
        "denied_actions": [
            "production go-live",
            "marketing claim of production ready",
            "autonomous activation by agents",
            "silent flip of deploy_held without human record",
        ],
        "required_for_future_authorization": [
            "Human-authored authority token under input/production_activation/",
            "Independent operator dual-control review (process, not code)",
            "Explicit deploy unhold + rollback attestation",
            "Threat model residuals accepted for production scope (beyond Partial)",
            "This gate re-evaluated to AUTHORIZED only by a future WP with operator mandate",
        ],
        "notes": [
            "CANDIDATE_APPROVED does not change this gate.",
            "Linked plan: out/production_readiness/CONTINUATION_PLAN.v8.md",
        ],
    }

    if write:
        out_dir = repo_root / OUT_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(
            out_dir / "production_activation_authority_gate.v1.json",
            gate,
        )

    return gate
