"""Phase 0 baseline evidence package."""

from __future__ import annotations

import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash
from core.governance.activation_policy import HARD_BOUNDARIES, policy_matrix


def _run(cmd: list[str], cwd: Path) -> dict[str, Any]:
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "command": cmd,
        "exit_code": result.returncode,
        "stdout_tail": result.stdout[-2000:],
        "stderr_tail": result.stderr[-2000:],
    }


def _git_sha(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "UNKNOWN"


def _git_branch(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "UNKNOWN"


def _file_sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_baseline(
    repo_root: Path,
    *,
    run_validation: bool = False,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    observed_docs = [
        "AGENTS.md",
        "README.md",
        "ARCHITECTURE.md",
        "STATUS.md",
        "PLANS.md",
        "GOVERNANCE_V3.md",
        "GOVERNANCE_SIMPLIFICATION_001.md",
        "docs/governance/BOUNDED_PRODUCT_ACTIVATION_001.md",
        "docs/alembic/ALEMBIC_SPINE.md",
        "out/production_readiness/README.md",
    ]
    present_docs = [d for d in observed_docs if (root / d).exists()]

    validation: dict[str, Any] = {
        "mode": "deferred" if not run_validation else "live",
        "notes": [
            (
                "Phase 0 default avoids full fast-CI wall-clock in the builder; "
                "runner may set run_validation=True. Targeted pytest is authoritative "
                "for this PR slice."
            )
        ],
    }
    if run_validation:
        validation["fast_ci"] = _run([sys.executable, "scripts/run_fast_ci.py"], root)

    env = {
        "python_version": sys.version.split()[0],
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "node_version": None,
        "uv_lock_sha256": _file_sha256(root / "uv.lock"),
        "package_lock_sha256": _file_sha256(root / "package-lock.json"),
    }
    node = subprocess.run(
        ["node", "--version"], capture_output=True, text=True, check=False
    )
    if node.returncode == 0:
        env["node_version"] = node.stdout.strip()

    payload = {
        "artifact_type": "production_convergence_baseline",
        "schema_version": "baseline.v1",
        "baseline_sha": _git_sha(root),
        "branch": _git_branch(root),
        "environment": env,
        "validation": validation,
        "observed_docs": present_docs,
        "known_blockers": [
            (
                "Unified product CLI (abraxas analyze/validate/replay/status) not yet "
                "implemented; hundreds of domain runners remain."
            ),
            "Supported runtime surface is a small subset of ~700+ scripts/run_*.py entry points.",
            "out/ mixes canonical domain state with audit/workflow/historical receipts.",
            "EXTERNAL_PRODUCTION remains operator-gated; candidate status NOT_READY.",
            "Alembic Spine is advisory-complete with residuals; not a supported product API.",
            "create_app(settings) factory and full golden-path integration tests still open.",
        ],
        "activation_policy_matrix": policy_matrix(),
        "hard_boundaries": list(HARD_BOUNDARIES),
        "alembic_placement": {
            "module": "core/alembic/",
            "role": "optional_specialist_on_golden_path",
            "status": "ALEMBIC_ADVISORY_COMPLETE_WITH_RESIDUALS",
            "not": "parallel_product_kernel",
        },
        "evidence_state": "Partial",
    }
    payload["canonical_hash"] = canonical_hash(
        {k: v for k, v in payload.items() if k != "canonical_hash"}
    )
    return payload
