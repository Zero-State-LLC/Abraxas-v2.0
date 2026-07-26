"""Machine-readable status snapshot for CLI/API (bounded current state)."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from core.canonical.artifact_classification import (
    policy_matrix as artifact_policy_matrix,
)
from core.canonical.json import canonical_hash
from core.governance.activation_policy import HARD_BOUNDARIES, policy_matrix
from core.settings import RuntimeSettings, load_runtime_settings


def _git_sha(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "UNKNOWN"


def build_status_snapshot(
    repo_root: Path | None = None,
    *,
    settings: RuntimeSettings | None = None,
) -> dict[str, Any]:
    resolved_settings = settings or load_runtime_settings(
        repo_root=Path(repo_root or Path.cwd()).resolve()
    )
    root = Path(resolved_settings.repo_root).resolve()
    payload = {
        "artifact_type": "abraxas_status_snapshot",
        "schema_version": "abraxas_status.v1",
        "repository_sha": _git_sha(root),
        "governance_mode": "DEVELOPMENT_ACCELERATION",
        "candidate_status": "NOT_READY",
        "external_production_authorized": False,
        "activation_policy": policy_matrix(),
        "artifact_classification_policy": artifact_policy_matrix(),
        "hard_boundaries": list(HARD_BOUNDARIES),
        "settings": resolved_settings.redacted_diagnostics(),
        "supported_interfaces": [
            "canonical_json",
            "write_canonical_artifact",
            "run_fast_ci",
            "validation_service.v1",
            "artifact_and_provenance_service.v0",
            "activation_policy",
            "runtime_settings",
            "apps_api",
            "abraxas_cli",
            "abraxas.AbraxasClient",
        ],
        "supported_spine": {
            "application": "core.application.advisory_spine",
            "cli": "python -m abraxas",
            "service": "apps.api.create_app",
            "alembic_role": "optional_specialist",
            "canonical_writer": "core.canonical.json.write_canonical_artifact",
        },
        "surfaces": {
            "advisory_spine": (root / "core/application/advisory_spine.py").is_file(),
            "activation_policy": (root / "core/governance/activation_policy.py").is_file(),
            "artifact_classification": (
                root / "core/canonical/artifact_classification.py"
            ).is_file(),
            "runtime_settings": (root / "core/settings.py").is_file(),
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
