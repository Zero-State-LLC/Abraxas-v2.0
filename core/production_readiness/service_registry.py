"""WP-C: service registry seed for WS3."""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json

PRODUCER = "run_service_registry_snapshot"
OUT_DIR_REL = Path("out/production_readiness/ws3")
REGISTRY_ID = "SERVICE_REGISTRY_SEED_001"


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


def build_service_registry(
    repo_root: Path,
    *,
    produced_at: str | None = None,
    write: bool = True,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)

    services = [
        {
            "service_id": "validation_service",
            "version": "1.0.0",
            "owner": "abraxas-core",
            "stability_class": "ADVISORY",
            "status": "IMPLEMENTED",
            "request_schema": "contracts/services/validation_service.request.v1.schema.json",
            "response_schema": "contracts/services/validation_service.response.v1.schema.json",
            "implementation_paths": [
                "core/services/validation_service.py",
                "scripts/run_validation_service.py",
            ],
            "authorization": "none_required_local_library_call",
            "idempotency": "pure_function_for_fixed_schema_files",
            "side_effects": "none (stdout CLI; optional --out via canonical writer)",
            "persistence": "none_by_default",
            "provenance": "schema_sha256 + payload_sha256 on OK responses",
            "tests": ["tests/test_validation_service.py"],
            "notes": "WP-B first service facade. Promote to SUPPORTED after broader contract tests.",
        },
        {
            "service_id": "artifact_and_provenance_service",
            "version": "0.1.0",
            "owner": "abraxas-core",
            "stability_class": "ADVISORY",
            "status": "IMPLEMENTED",
            "request_schema": "contracts/services/artifact_provenance_service.request.v1.schema.json",
            "response_schema": "contracts/services/artifact_provenance_service.response.v1.schema.json",
            "implementation_paths": [
                "core/services/artifact_provenance_service.py",
                "scripts/run_artifact_provenance_service.py",
            ],
            "authorization": "local_library_call",
            "idempotency": "hash/dumps pure; write_if_changed idempotent for same payload",
            "side_effects": "write/write_if_changed only under out/ via canonical_json",
            "persistence": "optional out/ paths only",
            "provenance": "delegates to SUPPORTED canonical_json",
            "tests": ["tests/test_artifact_provenance_service.py"],
            "depends_on_supported": ["canonical_json"],
            "notes": "WP-J facade over core.canonical.json with fail-closed path policy.",
        },
        {
            "service_id": "governance_evaluation_service",
            "version": "0.0.0",
            "owner": "abraxas-core",
            "stability_class": "EXPERIMENTAL",
            "status": "CANDIDATE",
            "notes": "Not implemented.",
        },
        {
            "service_id": "execution_receipt_service",
            "version": "0.0.0",
            "owner": "abraxas-core",
            "stability_class": "EXPERIMENTAL",
            "status": "CANDIDATE",
            "notes": "Blocked until receipt runner uses canonical_json (builder debt).",
        },
        {
            "service_id": "reasoning_service",
            "version": "0.0.0",
            "stability_class": "EXPERIMENTAL",
            "status": "CANDIDATE",
        },
        {
            "service_id": "forecast_service",
            "version": "0.0.0",
            "stability_class": "INTERNAL",
            "status": "BLOCKED_LANE",
            "notes": "FORECAST lane not authorized (ARCHITECTURE.md).",
        },
        {
            "service_id": "symbolic_analysis_service",
            "version": "0.0.0",
            "stability_class": "EXPERIMENTAL",
            "status": "CANDIDATE",
        },
        {
            "service_id": "repository_intelligence_service",
            "version": "0.0.0",
            "stability_class": "EXPERIMENTAL",
            "status": "CANDIDATE",
        },
    ]

    registry: dict[str, Any] = {
        "schema_version": "ServiceRegistry.v1",
        "registry_id": REGISTRY_ID,
        "program": "ABRAXAS_PRODUCTION_CONTINUATION",
        "work_package": "WP-C_SERVICE_REGISTRY_SEED",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "PARTIAL",
        "services": services,
        "summary": {
            "service_count": len(services),
            "implemented": sum(
                1 for s in services if s.get("status") == "IMPLEMENTED"
            ),
            "advisory": sum(
                1
                for s in services
                if s.get("stability_class") == "ADVISORY"
                and s.get("status") == "IMPLEMENTED"
            ),
            "candidates": sum(
                1 for s in services if s.get("status") == "CANDIDATE"
            ),
            "blocked": sum(
                1 for s in services if s.get("status") == "BLOCKED_LANE"
            ),
        },
        "notes": [
            "Single canonical service registry (WP-C + WP-J).",
            "Implemented: validation_service, artifact_and_provenance_service (ADVISORY).",
            "Linked plan: out/production_readiness/CONTINUATION_PLAN.v3.md",
        ],
    }

    if write:
        out_dir = repo_root / OUT_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(out_dir / "service_registry.v1.json", registry)

    return registry
