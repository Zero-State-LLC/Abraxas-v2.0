from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "CanonCodeBindingAuditReceipt.v1"
STATUS = "CANON_CODE_BINDING_AUDIT_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"
WORK_ORDER = "WO-ABX-CANON-CODE-BINDING-v1"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
CANON_DIRECTION_URL = "https://app.notion.com/p/3503e8ba2f5c81289cd2ef7784cc5205"
REPO_ORG_ADDENDUM_URL = "https://app.notion.com/p/3843e8ba2f5c8120828dfc2b3e488aa1"
DEFAULT_OUT_PATH = "out/audit/canon_code_binding_audit_001.latest.json"

AUTHORITY_LOCKS = {
    "canon_mutation": False,
    "external_calls": False,
    "github_writeback": False,
    "mcp_exposure": False,
    "notion_writeback": False,
    "production_activation": False,
    "queue_mutation": False,
    "runtime_activation": False,
    "runtime_mutation": False,
    "scheduler_mutation": False,
}


@dataclass(frozen=True)
class BindingSpec:
    subsystem: str
    canonical_notion_source: str
    repo_module_path: str
    schema_or_ir_contract: str
    validator_or_test: str
    proof_artifact: str
    freshness_marker: str
    authority_status: str
    owner_operator_surface: str


BINDING_SPECS = (
    BindingSpec(
        subsystem="repository_navigation",
        canonical_notion_source=REPO_ORG_ADDENDUM_URL,
        repo_module_path="core/docs_navigation_refresh.py",
        schema_or_ir_contract="DocsNavigationRefreshReceipt.v1",
        validator_or_test="tests/test_docs_navigation_refresh.py",
        proof_artifact="out/audit/docs_navigation_refresh_001.latest.json",
        freshness_marker="docs/START_HERE.md",
        authority_status="ADVISORY_ONLY",
        owner_operator_surface="docs/INDEX.md",
    ),
    BindingSpec(
        subsystem="subsystem_ownership_matrix",
        canonical_notion_source=REPO_ORG_ADDENDUM_URL,
        repo_module_path="core/subsystem_ownership_matrix_refresh.py",
        schema_or_ir_contract="SubsystemOwnershipMatrixRefreshReceipt.v1",
        validator_or_test="tests/test_subsystem_ownership_matrix_refresh.py",
        proof_artifact="out/audit/subsystem_ownership_matrix_refresh_001.latest.json",
        freshness_marker="docs/status/SUBSYSTEM_OWNERSHIP_MATRIX.md",
        authority_status="ADVISORY_ONLY",
        owner_operator_surface="docs/status/SUBSYSTEM_OWNERSHIP_MATRIX.md",
    ),
    BindingSpec(
        subsystem="artifact_registry_classifier",
        canonical_notion_source=REPO_ORG_ADDENDUM_URL,
        repo_module_path="core/artifact_registry_classifier.py",
        schema_or_ir_contract="ArtifactRegistryClassifierReceipt.v1",
        validator_or_test="tests/test_artifact_registry_classifier.py",
        proof_artifact="out/audit/artifact_registry_classifier_001.latest.json",
        freshness_marker="docs/artifacts/ARTIFACT_INDEX.md",
        authority_status="ADVISORY_ONLY",
        owner_operator_surface="docs/artifacts/ARTIFACT_INDEX.md",
    ),
    BindingSpec(
        subsystem="continuity_lineage_map",
        canonical_notion_source=REPO_ORG_ADDENDUM_URL,
        repo_module_path="core/continuity_lineage_map_refresh.py",
        schema_or_ir_contract="ContinuityLineageMapRefreshReceipt.v1",
        validator_or_test="tests/test_continuity_lineage_map_refresh.py",
        proof_artifact="out/audit/continuity_lineage_map_refresh_001.latest.json",
        freshness_marker="docs/lineage/CONTINUITY_LINEAGE_MAP_002.md",
        authority_status="ADVISORY_ONLY",
        owner_operator_surface="docs/lineage/CONTINUITY_LINEAGE_MAP_002.md",
    ),
    BindingSpec(
        subsystem="subsystem_health_dashboard",
        canonical_notion_source=NOTION_BOARD_URL,
        repo_module_path="core/subsystem_health_dashboard.py",
        schema_or_ir_contract="SubsystemHealthDashboardReceipt.v1",
        validator_or_test="tests/test_subsystem_health_dashboard.py",
        proof_artifact="out/audit/subsystem_health_dashboard_001.latest.json",
        freshness_marker="docs/status/SUBSYSTEM_HEALTH_DASHBOARD.md",
        authority_status="ADVISORY_ONLY",
        owner_operator_surface="docs/status/SUBSYSTEM_HEALTH_DASHBOARD.md",
    ),
    BindingSpec(
        subsystem="continuity_namespace_migration_preflight",
        canonical_notion_source=NOTION_BOARD_URL,
        repo_module_path="core/continuity_namespace_migration_preflight.py",
        schema_or_ir_contract="ContinuityNamespaceMigrationPreflightReceipt.v1",
        validator_or_test="tests/test_continuity_namespace_migration_preflight.py",
        proof_artifact="out/audit/continuity_namespace_migration_preflight_001.latest.json",
        freshness_marker="docs/status/CONTINUITY_NAMESPACE_MIGRATION_STATUS.md",
        authority_status="ADVISORY_ONLY",
        owner_operator_surface="docs/status/CONTINUITY_NAMESPACE_MIGRATION_RUNNER.md",
    ),
    BindingSpec(
        subsystem="live_console_migration_preflight_projection",
        canonical_notion_source=NOTION_BOARD_URL,
        repo_module_path="core/live_console_migration_preflight_projection.py",
        schema_or_ir_contract="LiveConsoleMigrationPreflightProjectionReceipt.v1",
        validator_or_test="tests/test_live_console_migration_preflight_projection.py",
        proof_artifact="out/audit/live_console_migration_preflight_projection_001.latest.json",
        freshness_marker="apps/aal-viz-live-console/public/projection-bundle.json",
        authority_status="PROJECTION_ONLY",
        owner_operator_surface="apps/aal-viz-live-console/public/projection-bundle.json",
    ),
)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_text(path: Path) -> tuple[str, str]:
    try:
        return path.read_text(encoding="utf-8"), "OBSERVED"
    except FileNotFoundError:
        return "", "MISSING"
    except OSError:
        return "", "NOT_COMPUTABLE"


def _path_row(repo_root: Path, relative_path: str) -> dict[str, Any]:
    path = repo_root / relative_path
    text, source_status = _read_text(path)
    return {
        "path": relative_path,
        "source_status": source_status,
        "sha256": _sha256_file(path) if source_status == "OBSERVED" else "NOT_COMPUTABLE",
        "line_count": len(text.splitlines()) if source_status == "OBSERVED" else 0,
        "authority_granted": False,
    }


def _binding_row(repo_root: Path, spec: BindingSpec) -> dict[str, Any]:
    observed_paths = {
        "repo_module_path": (repo_root / spec.repo_module_path).exists(),
        "validator_or_test": (repo_root / spec.validator_or_test).exists(),
        "proof_artifact": (repo_root / spec.proof_artifact).exists(),
        "freshness_marker": (repo_root / spec.freshness_marker).exists(),
        "owner_operator_surface": (repo_root / spec.owner_operator_surface).exists(),
    }
    missing = [
        field
        for field, observed in observed_paths.items()
        if field != "owner_operator_surface" and not observed
    ]
    return {
        "subsystem": spec.subsystem,
        "canonical_notion_source": spec.canonical_notion_source,
        "repo_module_path": spec.repo_module_path,
        "schema_or_ir_contract": spec.schema_or_ir_contract,
        "validator_or_test": spec.validator_or_test,
        "proof_artifact": spec.proof_artifact,
        "freshness_marker": spec.freshness_marker,
        "authority_status": spec.authority_status,
        "owner_operator_surface": spec.owner_operator_surface,
        "observed_paths": observed_paths,
        "binding_status": "BOUND" if not missing else "PARTIAL",
        "missing_required_fields": missing,
        "authority_granted": False,
    }


def _coverage_summary(binding_rows: list[dict[str, Any]]) -> dict[str, Any]:
    bound_count = sum(1 for row in binding_rows if row["binding_status"] == "BOUND")
    partial_rows = [
        row["subsystem"]
        for row in binding_rows
        if row["binding_status"] != "BOUND"
    ]
    return {
        "required_binding_count": len(binding_rows),
        "bound_count": bound_count,
        "partial_count": len(partial_rows),
        "partial_subsystems": partial_rows,
        "coverage_status": "READY" if not partial_rows else "READY_WITH_FINDINGS",
        "authority_granted": False,
    }


def build_canon_code_binding_audit_receipt(
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    binding_rows = [_binding_row(root, spec) for spec in BINDING_SPECS]
    coverage_summary = _coverage_summary(binding_rows)
    source_paths = sorted(
        {
            path
            for spec in BINDING_SPECS
            for path in (
                spec.repo_module_path,
                spec.validator_or_test,
                spec.proof_artifact,
                spec.freshness_marker,
                spec.owner_operator_surface,
            )
        }
    )
    source_table = [_path_row(root, path) for path in source_paths]
    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "work_order": WORK_ORDER,
        "status": STATUS,
        "brier_score": BRIER_SCORE,
        "advisory_only": True,
        "projection_only": True,
        "notion_board_url": NOTION_BOARD_URL,
        "canonical_direction_url": CANON_DIRECTION_URL,
        "repository_organization_addendum_url": REPO_ORG_ADDENDUM_URL,
        "claimed_card": (
            "WO-ABX-CANON-CODE-BINDING-v1 - repo evidence audit and scaffold"
        ),
        "authority_locks": AUTHORITY_LOCKS,
        "source_status": coverage_summary["coverage_status"],
        "binding_rows": binding_rows,
        "coverage_summary": coverage_summary,
        "source_table": source_table,
        "boundary": AUTHORITY_LOCKS,
        "top_findings": [
            {
                "code": "CANON_CODE_BINDING_BASELINE_EMITTED",
                "severity": "INFO",
                "detail": (
                    "Repo-visible subsystems now have an advisory baseline mapping "
                    "from canonical source to module, validator, proof artifact, "
                    "freshness marker, authority status, and operator surface."
                ),
                "authority_granted": False,
            },
            {
                "code": "BINDING_SCOPE_IS_PARTIAL",
                "severity": "LOW",
                "detail": (
                    "This scaffold covers current repo-visible priority surfaces; "
                    "future lanes may add more subsystems without changing authority."
                ),
                "authority_granted": False,
            },
        ],
        "validation_plan": [
            "python scripts/run_canon_code_binding_audit_receipt.py",
            f"python scripts/artifact/run_artifact_regeneration.py --artifact {DEFAULT_OUT_PATH}",
            "python -m py_compile core/canon_code_binding_audit.py "
            "scripts/run_canon_code_binding_audit_receipt.py",
            "python -m pytest tests/test_canon_code_binding_audit.py "
            "tests/test_generated_artifact_registry.py -q -k canon_code_binding",
            "git diff --check",
        ],
        "notion_closeout_text": (
            "WO-ABX-CANON-CODE-BINDING-v1 scaffold emitted as advisory repo "
            "evidence: canonical source, module path, validator, proof artifact, "
            "freshness marker, authority status, and operator surface mappings are "
            "visible without runtime activation, canon mutation, scheduler/queue "
            "mutation, external calls, or autonomous writeback. Brier Score: 0.10."
        ),
        "recommended_next_lane": (
            "Use this baseline to expand subsystem coverage or bind the evidence "
            "into AAL-Viz proof-dashboard projections in a separate advisory lane."
        ),
        "provenance": (
            "Canon-Active Engineering Direction v1.0 + Repository Organization "
            "Addendum + 2026-07-06 board refresh"
        ),
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def write_canon_code_binding_audit_receipt(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
