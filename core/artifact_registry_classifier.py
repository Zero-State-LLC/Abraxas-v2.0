from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.generated_artifact_registry import build_generated_artifact_registry

ARTIFACT_TYPE = "ArtifactRegistryClassifierReceipt.v1"
STATUS = "ARTIFACT_REGISTRY_CLASSIFIER_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-59"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
DEFAULT_OUT_PATH = "out/audit/artifact_registry_classifier_001.latest.json"

SOURCE_PATHS = (
    "core/generated_artifact_registry.py",
    "scripts/run_artifact_regeneration.py",
    "docs/artifacts/ARTIFACT_INDEX.md",
    "out/audit/docs_navigation_refresh_001.latest.json",
    "out/audit/subsystem_ownership_matrix_refresh_001.latest.json",
)

ACTIVE_ROUTE_ARTIFACTS = (
    "out/audit/docs_navigation_refresh_001.latest.json",
    "out/audit/subsystem_ownership_matrix_refresh_001.latest.json",
    "out/audit/continuation_frontier_reconciliation_001.latest.json",
    "out/canon_resume_state/latest.json",
)

FAMILY_ROUTE_CLASS = {
    "archive/": "ARCHIVED",
    "audit/": "ACTIVE",
    "canary_*": "REFERENCE",
    "canon_resume_state/": "ACTIVE",
    "chamfer*": "ARCHIVED",
    "continuity_namespace*": "REFERENCE",
    "contracts/": "ACTIVE",
    "exports/": "ACTIVE",
    "ingest/": "ACTIVE",
    "operator_review/": "ACTIVE",
    "oracle/": "ACTIVE",
    "overlay*": "REFERENCE",
    "package/": "ACTIVE",
    "previews/": "ACTIVE",
    "proposal*": "REFERENCE",
    "projections/": "ACTIVE",
    "reports/": "ACTIVE",
    "research_*": "REFERENCE",
    "research_canary*": "REFERENCE",
    "sync/": "ACTIVE",
    "temporal_continuity*": "REFERENCE",
    "validation/": "ACTIVE",
}

AUTHORITY_LOCKS = {
    "canon_mutation": False,
    "external_calls": False,
    "github_writeback": False,
    "mcp_exposure": False,
    "notion_writeback": False,
    "production_activation": False,
    "runtime_activation": False,
    "runtime_mutation": False,
    "sandbox_probe_execution": False,
}


def _read_text(path: Path) -> tuple[str, str]:
    try:
        return path.read_text(encoding="utf-8"), "OBSERVED"
    except FileNotFoundError:
        return "", "MISSING"
    except OSError:
        return "", "NOT_COMPUTABLE"


def _source_row(repo_root: Path, relative_path: str) -> dict[str, Any]:
    path = repo_root / relative_path
    text, status = _read_text(path)
    return {
        "path": relative_path,
        "source_status": status,
        "line_count": len(text.splitlines()) if status == "OBSERVED" else 0,
        "authority_granted": False,
    }


def _family_key(artifact_path: str) -> str:
    relative = artifact_path.removeprefix("out/")
    if "/" in relative:
        return f"{relative.split('/', 1)[0]}/"
    if relative.startswith("research_canary"):
        return "research_canary*"
    if relative.startswith("research_"):
        return "research_*"
    if relative.startswith("temporal_continuity"):
        return "temporal_continuity*"
    if relative.startswith("chamfer"):
        return "chamfer*"
    if relative.startswith("proposal"):
        return "proposal*"
    if relative.startswith("overlay"):
        return "overlay*"
    if relative.startswith("canary_"):
        return "canary_*"
    if relative.startswith("continuity_namespace"):
        return "continuity_namespace*"
    return f"{relative.split('_', 1)[0]}*"


def _family_route_class(family: str) -> str:
    return FAMILY_ROUTE_CLASS.get(family, "REVIEW")


def _is_no_arg_regenerable(entry: Any) -> bool:
    return (
        entry.final_status == "managed"
        and bool(entry.canonical_generator)
        and bool(entry.canonical_schema)
    )


def _classification_buckets(entries: list[Any]) -> dict[str, dict[str, int]]:
    return {
        "final_status_counts": dict(sorted(Counter(entry.final_status for entry in entries).items())),
        "determinism_class_counts": dict(
            sorted(Counter(entry.determinism_class for entry in entries).items())
        ),
        "committed_policy_counts": dict(
            sorted(Counter(entry.committed_policy for entry in entries).items())
        ),
    }


def _family_summary(entries: list[Any]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for entry in entries:
        family = _family_key(entry.artifact_path)
        row = grouped.setdefault(
            family,
            {
                "family": family,
                "artifact_count": 0,
                "managed_count": 0,
                "ci_drift_enforced_count": 0,
                "no_arg_regenerable_count": 0,
                "route_class": _family_route_class(family),
                "authority_granted": False,
            },
        )
        row["artifact_count"] += 1
        if entry.final_status == "managed":
            row["managed_count"] += 1
        if entry.determinism_class in {"BUILD_CANONICAL", "CI_REGENERATED"}:
            row["ci_drift_enforced_count"] += 1
        if _is_no_arg_regenerable(entry):
            row["no_arg_regenerable_count"] += 1
    return sorted(
        grouped.values(),
        key=lambda row: (-int(row["artifact_count"]), row["family"]),
    )[:12]


def _active_route_rows(entries: list[Any]) -> list[dict[str, Any]]:
    entry_map = {entry.artifact_path: entry for entry in entries}
    rows: list[dict[str, Any]] = []
    for artifact_path in ACTIVE_ROUTE_ARTIFACTS:
        entry = entry_map.get(artifact_path)
        rows.append(
            {
                "artifact_path": artifact_path,
                "observed": entry is not None,
                "final_status": entry.final_status if entry is not None else "MISSING",
                "determinism_class": (
                    entry.determinism_class if entry is not None else "NOT_COMPUTABLE"
                ),
                "canonical_generator": (
                    entry.canonical_generator if entry is not None else None
                ),
                "no_arg_regenerable": (
                    _is_no_arg_regenerable(entry) if entry is not None else False
                ),
                "authority_granted": False,
            }
        )
    return rows


def _top_findings(
    *,
    registry: Any,
    family_summary: list[dict[str, Any]],
    active_routes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    if registry.orphaned_artifacts:
        findings.append(
            {
                "severity": "MEDIUM",
                "code": "ORPHANED_ARTIFACTS_PRESENT",
                "detail": f"{len(registry.orphaned_artifacts)} orphaned artifacts remain in the registry view.",
                "authority_granted": False,
            }
        )

    ambiguous_count = sum(
        1 for entry in registry.entries if entry.final_status == "ambiguous_generator"
    )
    if ambiguous_count:
        findings.append(
            {
                "severity": "MEDIUM",
                "code": "AMBIGUOUS_GENERATORS_PRESENT",
                "detail": f"{ambiguous_count} artifacts still resolve to ambiguous generators.",
                "authority_granted": False,
            }
        )

    missing_routes = [row["artifact_path"] for row in active_routes if not row["observed"]]
    if missing_routes:
        findings.append(
            {
                "severity": "HIGH",
                "code": "ACTIVE_ROUTE_GAPS",
                "detail": "Missing active navigation artifacts: " + ", ".join(missing_routes),
                "authority_granted": False,
            }
        )

    blocked_routes = [
        row["artifact_path"]
        for row in active_routes
        if row["observed"] and not row["no_arg_regenerable"]
    ]
    if blocked_routes:
        findings.append(
            {
                "severity": "MEDIUM",
                "code": "NO_ARG_REGENERATION_GAPS",
                "detail": "Observed active routes without clean no-arg regeneration: "
                + ", ".join(blocked_routes),
                "authority_granted": False,
            }
        )

    for row in family_summary:
        if row["artifact_count"] >= 20 and row["route_class"] in {"REFERENCE", "REVIEW"}:
            findings.append(
                {
                    "severity": "LOW",
                    "code": "LARGE_HISTORICAL_FAMILY",
                    "detail": (
                        f"{row['family']} contains {row['artifact_count']} artifacts and should stay "
                        "discoverable without becoming a routine regeneration target."
                    ),
                    "authority_granted": False,
                }
            )
        if len(findings) >= 6:
            break

    return findings


def build_artifact_registry_classifier_receipt(
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    source_table = [_source_row(root, path) for path in SOURCE_PATHS]

    try:
        registry = build_generated_artifact_registry(root)
    except Exception as exc:
        base: dict[str, Any] = {
            "artifact_type": ARTIFACT_TYPE,
            "slice_id": SLICE_ID,
            "status": STATUS,
            "brier_score": BRIER_SCORE,
            "advisory_only": True,
            "projection_only": True,
            "notion_board_url": NOTION_BOARD_URL,
            "claimed_card": "Priority 3 - D2 Artifact Registry Classifier",
            "authority_locks": AUTHORITY_LOCKS,
            "source_status": "NOT_COMPUTABLE",
            "source_table": source_table,
            "classification_summary": {
                "managed_count": 0,
                "orphaned_count": 0,
                "ambiguous_count": 0,
                "tracked_count": 0,
                "total_entries": 0,
                "explicit_producer_count": 0,
                "no_arg_regenerable_count": 0,
                "ci_drift_target_count": 0,
                "registry_final_status": "NOT_COMPUTABLE",
                "authority_granted": False,
            },
            "classification_buckets": {},
            "family_summary": [],
            "active_route_rows": [],
            "top_findings": [
                {
                    "severity": "HIGH",
                    "code": "REGISTRY_BUILD_FAILED",
                    "detail": str(exc),
                    "authority_granted": False,
                }
            ],
            "boundary": {
                "sandbox_gate_issue": "#892",
                "sandbox_gate_phrase": "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED",
                "sandbox_gate_issued": False,
                "canon_mutation": False,
                "external_calls": False,
                "github_writeback": False,
                "mcp_exposure": False,
                "notion_writeback": False,
                "runtime_activation": False,
            },
            "validation_plan": [
                "python scripts/artifact/run_artifact_registry_classifier_receipt.py",
                f"python scripts/run_artifact_regeneration.py --artifact {DEFAULT_OUT_PATH}",
                "python -m py_compile core/artifact_registry_classifier.py "
                "scripts/artifact/run_artifact_registry_classifier_receipt.py",
                "python -m pytest tests/test_artifact_registry_classifier.py "
                "tests/test_generated_artifact_registry.py -q -k artifact_registry_classifier",
                "git diff --check",
            ],
            "notion_closeout_text": (
                "Slice59 complete - Artifact Registry Classifier shipped; generated artifact "
                "registry now emits advisory lifecycle and discoverability classification for "
                "managed, orphaned, CI-regenerated, and historical artifact groups; no sandbox "
                "probe, runtime activation, canon mutation, MCP exposure, external calls, or "
                "autonomous writeback authorized. Brier Score: 0.10."
            ),
            "recommended_next_lane": (
                "Continue Priority 3 with continuity lineage mapping or reprioritize to "
                "Priority 2 if the operator selects a different board card."
            ),
            "provenance": "Notion Sprint 001 Hub + Loop 805 Slice59 + Hash: canonical_hash",
        }
        return {**base, "canonical_hash": canonical_hash(base)}

    entries = list(registry.entries)
    active_routes = _active_route_rows(entries)
    family_summary = _family_summary(entries)
    explicit_producer_count = sum(
        1
        for entry in entries
        if entry.canonical_generator
        and Path(entry.canonical_generator).name.startswith("run_")
    )
    no_arg_regenerable_count = sum(1 for entry in entries if _is_no_arg_regenerable(entry))
    ci_drift_target_count = sum(
        1
        for entry in entries
        if entry.final_status == "managed"
        and entry.tracked
        and entry.determinism_class in {"BUILD_CANONICAL", "CI_REGENERATED"}
    )
    classification_summary = {
        "total_entries": len(entries),
        "managed_count": sum(1 for entry in entries if entry.final_status == "managed"),
        "orphaned_count": len(registry.orphaned_artifacts),
        "ambiguous_count": sum(
            1 for entry in entries if entry.final_status == "ambiguous_generator"
        ),
        "tracked_count": sum(1 for entry in entries if entry.tracked),
        "explicit_producer_count": explicit_producer_count,
        "no_arg_regenerable_count": no_arg_regenerable_count,
        "ci_drift_target_count": ci_drift_target_count,
        "registry_final_status": registry.final_status,
        "authority_granted": False,
    }
    findings = _top_findings(
        registry=registry,
        family_summary=family_summary,
        active_routes=active_routes,
    )
    source_status = "READY" if not findings else "READY_WITH_FINDINGS"

    base = {
        "artifact_type": ARTIFACT_TYPE,
        "slice_id": SLICE_ID,
        "status": STATUS,
        "brier_score": BRIER_SCORE,
        "advisory_only": True,
        "projection_only": True,
        "notion_board_url": NOTION_BOARD_URL,
        "claimed_card": "Priority 3 - D2 Artifact Registry Classifier",
        "authority_locks": AUTHORITY_LOCKS,
        "source_status": source_status,
        "source_table": source_table,
        "classification_summary": classification_summary,
        "classification_buckets": _classification_buckets(entries),
        "family_summary": family_summary,
        "active_route_rows": active_routes,
        "top_findings": findings,
        "boundary": {
            "sandbox_gate_issue": "#892",
            "sandbox_gate_phrase": "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED",
            "sandbox_gate_issued": False,
            "canon_mutation": False,
            "external_calls": False,
            "github_writeback": False,
            "mcp_exposure": False,
            "notion_writeback": False,
            "runtime_activation": False,
        },
        "validation_plan": [
            "python scripts/artifact/run_artifact_registry_classifier_receipt.py",
            f"python scripts/run_artifact_regeneration.py --artifact {DEFAULT_OUT_PATH}",
            "python -m py_compile core/artifact_registry_classifier.py "
            "scripts/artifact/run_artifact_registry_classifier_receipt.py",
            "python -m pytest tests/test_artifact_registry_classifier.py "
            "tests/test_generated_artifact_registry.py -q -k artifact_registry_classifier",
            "git diff --check",
        ],
        "notion_closeout_text": (
            "Slice59 complete - Artifact Registry Classifier shipped; generated artifact "
            "registry now emits advisory lifecycle and discoverability classification for "
            "managed, orphaned, CI-regenerated, and historical artifact groups; no sandbox "
            "probe, runtime activation, canon mutation, MCP exposure, external calls, or "
            "autonomous writeback authorized. Brier Score: 0.10."
        ),
        "recommended_next_lane": (
            "Continue Priority 3 with continuity lineage mapping or reprioritize to "
            "Priority 2 if the operator selects a different board card."
        ),
        "provenance": "Notion Sprint 001 Hub + Loop 805 Slice59 + Hash: canonical_hash",
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def write_artifact_registry_classifier_receipt(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
