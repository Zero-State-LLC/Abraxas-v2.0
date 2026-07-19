"""TD Wave 2: package writer policy for skills + abx-afe residual close-by-policy."""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json

PRODUCER = "run_package_writer_policy"
OUT_DIR_REL = Path("out/production_readiness/ws2")
POLICY_ID = "PACKAGE_WRITER_POLICY_001"


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


def build_package_writer_policy(
    repo_root: Path,
    *,
    produced_at: str | None = None,
    write: bool = True,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)

    policy: dict[str, Any] = {
        "schema_version": "package_writer_policy.v1",
        "policy_id": POLICY_ID,
        "artifact_type": "package_writer_policy",
        "work_package": "TD_WAVE2_PACKAGE_WRITER_POLICY",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial",
        "owner": "abraxas-core",
        "review_date": produced_at[:10],
        "authorized_prefixes": [
            {
                "prefix": "skills/abx-hermes-skill-evolution/",
                "class": "PACKAGE_POLICY_SKILL_WRITER",
                "rationale": (
                    "Hermes skill tools intentionally emit operator/audit packets "
                    "under out/. Not Abraxas kernel sole-writer debt for freeze track."
                ),
            },
            {
                "prefix": "abx-afe/",
                "class": "PACKAGE_POLICY_AFE_CLI_WRITER",
                "rationale": (
                    "Separate package CLI/scripts lane. Publication ownership is "
                    "package-local; not core freeze residual."
                ),
            },
        ],
        "enforced_in": "core/production_readiness/sole_writer_check.py:PACKAGE_WRITER_PREFIXES",
        "fail_closed_enabled": False,
        "production_activation_authorized": False,
        "notes": [
            "Policy closes unauthorized residual for skills/afe without product rewrite.",
            "Unauthorized metric excludes these prefixes.",
            "Linked plan: technical debt resolution TD Wave 2.",
        ],
    }

    if write:
        out_dir = repo_root / OUT_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(out_dir / "package_writer_policy.v1.json", policy)

    return policy
