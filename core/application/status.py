"""Machine-readable status snapshot for CLI/API (bounded current state)."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash
from core.governance.activation_policy import HARD_BOUNDARIES, policy_matrix


def _git_sha(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "UNKNOWN"


def build_status_snapshot(repo_root: Path | None = None) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    payload = {
        "artifact_type": "abraxas_status_snapshot",
        "schema_version": "abraxas_status.v1",
        "repository_sha": _git_sha(root),
        "governance_mode": "DEVELOPMENT_ACCELERATION",
        "candidate_status": "NOT_READY",
        "external_production_authorized": False,
        "activation_policy": policy_matrix(),
        "hard_boundaries": list(HARD_BOUNDARIES),
        "supported_interfaces": [
            "canonical_json",
            "run_fast_ci",
            "validation_service.v1",
            "artifact_and_provenance_service.v0",
            "activation_policy",
            "apps_api",
            "abraxas_cli",
            "abraxas.AbraxasClient",
        ],
        "supported_spine": {
            "application": "core.application.advisory_spine",
            "cli": "python -m abraxas",
            "service": "apps.api.create_app",
            "alembic_role": "optional_specialist",
        },
        "surfaces": {
            "advisory_spine": (root / "core/application/advisory_spine.py").is_file(),
            "activation_policy": (root / "core/governance/activation_policy.py").is_file(),
            "alembic": (root / "core/alembic/pipeline.py").is_file(),
            "apps_api": (root / "apps/api/main.py").is_file(),
            "convergence_audit": (
                root / "docs/architecture/PRODUCTION_CONVERGENCE_AUDIT_001.md"
            ).is_file(),
        },
    }
    payload["canonical_hash"] = canonical_hash(
        {k: v for k, v in payload.items() if k != "canonical_hash"}
    )
    return payload
