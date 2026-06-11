from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.generated_artifact_registry import (
    build_generated_artifact_registry,
)

ARTIFACT_TYPE = "AbxArtifactLineageRegistryTraceabilityAudit.v1"
AUDIT_ID = "ABX_ARTIFACT_LINEAGE_REGISTRY_TRACEABILITY_AUDIT_001"
DETERMINISTIC_GENERATED_AT = "2026-06-05T00:00:00Z"
SOURCE_COMPLETION_PLAN_PATH = "out/sync/abx_artifact_lineage_registry_completion_plan/latest.json"
SCOPED_EXECUTION_RECEIPT_PATH = (
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt_001.latest.json"
)
OUT_JSON = "out/sync/abx_artifact_lineage_registry_traceability_audit/latest.json"
OUT_MD = "out/sync/abx_artifact_lineage_registry_traceability_audit/latest.md"
DOWNSTREAM = "NOT_COMPUTABLE"
RECOMMENDED_NEXT_PLAN = "ABX_ARTIFACT_LINEAGE_REGISTRY_REPAIR_PLAN_001"
SAMPLE_LIMIT = 25

_OUTPUT_REF_RE = re.compile(r"out/[A-Za-z0-9_./-]+\.(?:json|md)")


def _load_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _source_hash(path: Path) -> str:
    try:
        return canonical_hash(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError):
        return "NOT_COMPUTABLE"


def _sorted_unique(values: list[str] | set[str] | tuple[str, ...]) -> list[str]:
    return sorted(dict.fromkeys(values))


def _sample(values: list[str]) -> list[str]:
    return values[:SAMPLE_LIMIT]


def _registry_entries(root: Path) -> list[str]:
    registry = build_generated_artifact_registry(root)
    return sorted(
        entry.artifact_path
        for entry in registry.entries
        if entry.artifact_path.startswith("out/")
    )


def _all_runner_paths(root: Path) -> tuple[list[str], list[str]]:
    lower = sorted(str(path.relative_to(root)).replace("\\", "/") for path in (root / "scripts").glob("run_*.py"))
    upper = sorted(str(path.relative_to(root)).replace("\\", "/") for path in (root / "Scripts").glob("run_*.py"))
    return lower, upper


def _all_schema_paths(root: Path) -> list[str]:
    return sorted(str(path.relative_to(root)).replace("\\", "/") for path in (root / "contracts").rglob("*.schema.json"))


def _all_output_paths(root: Path, suffix: str) -> list[str]:
    return sorted(str(path.relative_to(root)).replace("\\", "/") for path in (root / "out").rglob(f"*{suffix}"))


def _all_test_paths(root: Path) -> list[str]:
    return sorted(str(path.relative_to(root)).replace("\\", "/") for path in (root / "tests").glob("test_*.py"))


def _doc_paths(root: Path) -> list[str]:
    docs = [root / "README.md", root / "AGENTS.md", root / "PLANS.md"]
    docs.extend((root / "docs").rglob("*.md"))
    existing = [path for path in docs if path.exists()]
    return sorted(str(path.relative_to(root)).replace("\\", "/") for path in existing)


def _sync_family_names(json_outputs: list[str], md_outputs: list[str]) -> list[str]:
    families = []
    for path in json_outputs + md_outputs:
        if path.startswith("out/sync/") and "/latest." in path:
            families.append(Path(path).parent.name)
    return _sorted_unique(families)


def _runner_candidates(family: str) -> list[str]:
    runner_name = f"run_{family}.py"
    return [f"scripts/{runner_name}", f"Scripts/{runner_name}"]


def _schema_candidates(family: str) -> list[str]:
    return [
        f"contracts/canon/{family}.v1.schema.json",
        f"contracts/canon/{family}.schema.json",
    ]


def _test_candidates(family: str) -> list[str]:
    return [f"tests/test_{family}.py"]


def _build_status(
    *,
    finding_id: str,
    status: str,
    checked_count: int,
    impacted: list[str],
    reason: str,
    evidence_required: str,
) -> dict[str, Any]:
    return {
        "finding_id": finding_id,
        "status": status,
        "checked_count": checked_count,
        "impacted_count": len(impacted),
        "sample_impacted": _sample(impacted),
        "reason": reason,
        "evidence_required": evidence_required,
    }


def _docs_references_to_missing_artifacts(root: Path, doc_paths: list[str]) -> list[str]:
    missing: list[str] = []
    for rel_path in doc_paths:
        text = (root / rel_path).read_text(encoding="utf-8")
        for match in _OUTPUT_REF_RE.findall(text):
            if not (root / match).exists():
                missing.append(f"{rel_path}::{match}")
    return sorted(missing)


def _scoped_execution_receipt(root: Path) -> dict[str, Any]:
    receipt = _load_json(root / SCOPED_EXECUTION_RECEIPT_PATH)
    if (
        receipt.get("schema_version")
        != "AbxArtifactLineageRegistryDirectRepairScopedExecutionReceipt.v1"
        or receipt.get("status")
        != "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SCOPED_EXECUTION_RECEIPT_EMITTED"
        or receipt.get("repair_execution_performed") is not True
    ):
        return {}
    return receipt


def _receipt_path_set(receipt: Mapping[str, Any], section_name: str, path_key: str) -> set[str]:
    section = receipt.get(section_name, {})
    if not isinstance(section, Mapping):
        return set()
    values = section.get(path_key, [])
    if not isinstance(values, list):
        return set()
    return {str(value) for value in values}


def _target_cluster_results(findings: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "cluster_id": "runtime_spine_audit_aggregator",
            "cluster_status": "NOT_COMPUTABLE",
            "supporting_finding_ids": [
                "detect_artifacts_with_outputs_but_no_registry_entry",
                "detect_registry_entries_with_no_runner",
            ],
            "observed_summary": "runtime spine lineage remains unresolved until explicit producer, runner, and registry bindings are audited",
        },
        {
            "cluster_id": "missing_replay_repair_batch",
            "cluster_status": "NOT_COMPUTABLE",
            "supporting_finding_ids": ["preserve_unresolved_cases_as_NOT_COMPUTABLE"],
            "observed_summary": "replay repair batches remain unresolved and are preserved as NOT_COMPUTABLE",
        },
        {
            "cluster_id": "missing_artifact_repair_batch",
            "cluster_status": "NOT_COMPUTABLE",
            "supporting_finding_ids": [
                "detect_registry_entries_with_no_runner",
                "detect_runner_paths_with_no_schema",
            ],
            "observed_summary": "artifact repair surfaces still need explicit producer and schema reconciliation",
        },
        {
            "cluster_id": "uppercase_scripts_runner_visibility",
            "cluster_status": findings["detect_uppercase_Scripts_runner_discovery_gaps"]["status"],
            "supporting_finding_ids": ["detect_uppercase_Scripts_runner_discovery_gaps"],
            "observed_summary": "runner path visibility differs across scripts and Scripts surfaces",
        },
        {
            "cluster_id": "systemwide_integration_matrix_gaps",
            "cluster_status": findings["detect_schemas_with_no_tests"]["status"],
            "supporting_finding_ids": ["detect_schemas_with_no_tests"],
            "observed_summary": "schema coverage still contains unresolved or missing test bindings",
        },
        {
            "cluster_id": "orphaned_subsystem_status",
            "cluster_status": findings["detect_docs_references_to_missing_artifacts"]["status"],
            "supporting_finding_ids": ["detect_docs_references_to_missing_artifacts"],
            "observed_summary": "docs references are checked, but subsystem status traceability remains incomplete",
        },
        {
            "cluster_id": "dashboard_projection_traceability",
            "cluster_status": findings["detect_generated_outputs_with_no_notion_surface"]["status"],
            "supporting_finding_ids": ["detect_generated_outputs_with_no_notion_surface"],
            "observed_summary": "projection-to-Notion lineage cannot be proven from repo-local evidence alone",
        },
        {
            "cluster_id": "artifact_registry_runner_discovery_gap",
            "cluster_status": findings["detect_registry_entries_with_no_runner"]["status"],
            "supporting_finding_ids": ["detect_registry_entries_with_no_runner"],
            "observed_summary": "registry entries still need deterministic runner reconciliation",
        },
    ]


def build_abx_artifact_lineage_registry_traceability_audit(
    *,
    repo_root: str | Path = ".",
    source_completion_plan_path: str | Path = SOURCE_COMPLETION_PLAN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    completion_plan_file = root / source_completion_plan_path
    completion_plan = _load_json(completion_plan_file)
    completion_plan_observed = (
        completion_plan.get("artifact_type") == "AbxArtifactLineageRegistryCompletionPlan.v1"
        and completion_plan.get("plan_id") == "ABX_ARTIFACT_LINEAGE_REGISTRY_COMPLETION_PLAN_001"
        and completion_plan.get("recommended_next_plan") == AUDIT_ID
    )

    registry_entries = _registry_entries(root)
    lower_runners, upper_runners = _all_runner_paths(root)
    schema_paths = _all_schema_paths(root)
    json_outputs = _all_output_paths(root, ".json")
    md_outputs = _all_output_paths(root, ".md")
    test_paths = _all_test_paths(root)
    doc_paths = _doc_paths(root)
    sync_families = _sync_family_names(json_outputs, md_outputs)

    registry_set = set(registry_entries)
    lower_runner_set = set(lower_runners)
    upper_runner_set = set(upper_runners)
    all_runner_set = lower_runner_set | upper_runner_set
    schema_set = set(schema_paths)
    test_set = set(test_paths)

    latest_outputs = sorted(path for path in json_outputs + md_outputs if "/latest." in path)
    outputs_without_registry = sorted(path for path in latest_outputs if path not in registry_set)

    lower_runner_names = {Path(path).name for path in lower_runner_set}
    upper_runner_names = {Path(path).name for path in upper_runner_set}
    runner_overlap = sorted(lower_runner_names & upper_runner_names)

    registry_entries_with_no_runner: list[str] = []
    runners_with_no_schema: list[str] = []
    schemas_with_no_tests: list[str] = []
    json_outputs_without_schema: list[str] = []
    sync_outputs_without_notion_surface: list[str] = []

    for family in sync_families:
        runner_candidates = _runner_candidates(family)
        if not any(candidate in all_runner_set for candidate in runner_candidates):
            registry_entries_with_no_runner.append(family)

        matched_runner_candidates = [candidate for candidate in runner_candidates if candidate in all_runner_set]
        if matched_runner_candidates:
            if not any(candidate in schema_set for candidate in _schema_candidates(family)):
                runners_with_no_schema.extend(matched_runner_candidates)

        schema_candidate = next((candidate for candidate in _schema_candidates(family) if candidate in schema_set), None)
        if schema_candidate is not None and not any(candidate in test_set for candidate in _test_candidates(family)):
            schemas_with_no_tests.append(schema_candidate)

        json_candidate = f"out/sync/{family}/latest.json"
        if json_candidate in json_outputs and schema_candidate is None:
            json_outputs_without_schema.append(json_candidate)

        sync_outputs_without_notion_surface.append(f"out/sync/{family}")

    md_pairs_missing = sorted(
        path for path in md_outputs if "/latest.md" in path and path.replace(".md", ".json") not in json_outputs
    )
    json_pairs_missing = sorted(
        path for path in json_outputs if "/latest.json" in path and path.replace(".json", ".md") not in md_outputs
    )

    docs_missing_artifacts = _docs_references_to_missing_artifacts(root, doc_paths)

    scoped_receipt = _scoped_execution_receipt(root)
    repaired_registry_paths = _receipt_path_set(scoped_receipt, "registry_coverage_repair", "repaired_paths")
    single_format_exception_paths = _receipt_path_set(
        scoped_receipt, "output_pairing_repair", "single_format_exception_paths"
    )
    docs_reference_exception_refs = _receipt_path_set(
        scoped_receipt, "docs_reference_repair", "docs_reference_exception_refs"
    )
    outputs_without_registry = sorted(path for path in outputs_without_registry if path not in repaired_registry_paths)
    md_pairs_missing = sorted(path for path in md_pairs_missing if path not in single_format_exception_paths)
    json_pairs_missing = sorted(path for path in json_pairs_missing if path not in single_format_exception_paths)
    docs_missing_artifacts = sorted(ref for ref in docs_missing_artifacts if ref not in docs_reference_exception_refs)

    unresolved_cases = _sorted_unique(
        [
            "notion_mapping_evidence_external_to_repo",
            "runner_to_schema_binding_heuristic_only",
            *([f"runner_case_overlap::{name}" for name in runner_overlap]),
        ]
    )

    findings = {
        "detect_uppercase_Scripts_runner_discovery_gaps": _build_status(
            finding_id="detect_uppercase_Scripts_runner_discovery_gaps",
            status="NOT_COMPUTABLE" if runner_overlap else "PASS",
            checked_count=len(all_runner_set),
            impacted=runner_overlap,
            reason=(
                "runner basenames are visible through both scripts and Scripts surfaces, so deterministic casing authority still requires operator review"
                if runner_overlap
                else "no overlapping runner basenames detected between scripts and Scripts"
            ),
            evidence_required="explicit canonical runner-path policy or case-stable lineage mapping",
        ),
        "detect_artifacts_with_outputs_but_no_registry_entry": _build_status(
            finding_id="detect_artifacts_with_outputs_but_no_registry_entry",
            status="DRIFT" if outputs_without_registry else "PASS",
            checked_count=len(latest_outputs),
            impacted=outputs_without_registry,
            reason="latest output artifacts were compared against generated artifact registry entries",
            evidence_required="registry entries for unresolved output artifacts or explicit exclusion rationale",
        ),
        "detect_registry_entries_with_no_runner": _build_status(
            finding_id="detect_registry_entries_with_no_runner",
            status="DRIFT" if registry_entries_with_no_runner else "PASS",
            checked_count=len(sync_families),
            impacted=registry_entries_with_no_runner,
            reason="sync-family registry outputs were reconciled against deterministic runner naming candidates",
            evidence_required="explicit runner binding for each unresolved sync-family registry entry",
        ),
        "detect_runner_paths_with_no_schema": _build_status(
            finding_id="detect_runner_paths_with_no_schema",
            status="DRIFT" if runners_with_no_schema else "PASS",
            checked_count=len(all_runner_set),
            impacted=_sorted_unique(runners_with_no_schema),
            reason="runner candidates for sync families were checked for same-family canon schemas",
            evidence_required="explicit schema binding or approved non-schema rationale for each unresolved runner",
        ),
        "detect_schemas_with_no_tests": _build_status(
            finding_id="detect_schemas_with_no_tests",
            status="DRIFT" if schemas_with_no_tests else "PASS",
            checked_count=len(schema_paths),
            impacted=schemas_with_no_tests,
            reason="same-family schema and test path pairs were checked for sync-family surfaces",
            evidence_required="focused tests or explicit test coverage mapping for unresolved schemas",
        ),
        "detect_generated_outputs_with_no_notion_surface": _build_status(
            finding_id="detect_generated_outputs_with_no_notion_surface",
            status="NOT_COMPUTABLE",
            checked_count=len(sync_outputs_without_notion_surface),
            impacted=sync_outputs_without_notion_surface,
            reason="repo-local evidence cannot prove Notion mapping completeness for generated sync outputs",
            evidence_required="deterministic repo-visible Notion mapping index or governed external evidence import",
        ),
        "detect_markdown_outputs_without_json_pair": _build_status(
            finding_id="detect_markdown_outputs_without_json_pair",
            status="DRIFT" if md_pairs_missing or json_pairs_missing else "PASS",
            checked_count=len(latest_outputs),
            impacted=_sorted_unique(md_pairs_missing + json_pairs_missing),
            reason="latest markdown outputs were paired against same-family latest json outputs and vice versa",
            evidence_required="matching json/md artifact pairs or explicit single-format exception",
        ),
        "detect_json_outputs_without_schema": _build_status(
            finding_id="detect_json_outputs_without_schema",
            status="DRIFT" if json_outputs_without_schema else "PASS",
            checked_count=len(json_outputs),
            impacted=json_outputs_without_schema,
            reason="sync-family latest json outputs were checked for same-family canon schema candidates",
            evidence_required="canon schema binding or approved alternate schema mapping",
        ),
        "detect_docs_references_to_missing_artifacts": _build_status(
            finding_id="detect_docs_references_to_missing_artifacts",
            status="DRIFT" if docs_missing_artifacts else "PASS",
            checked_count=len(doc_paths),
            impacted=docs_missing_artifacts,
            reason="repo docs and root markdown surfaces were scanned for out/... references that do not exist",
            evidence_required="valid artifact path or docs correction for each missing reference",
        ),
        "preserve_unresolved_cases_as_NOT_COMPUTABLE": _build_status(
            finding_id="preserve_unresolved_cases_as_NOT_COMPUTABLE",
            status="NOT_COMPUTABLE",
            checked_count=len(unresolved_cases),
            impacted=unresolved_cases,
            reason="the audit intentionally preserves heuristic and external-evidence gaps as NOT_COMPUTABLE",
            evidence_required="explicit operator-reviewed lineage rules or imported governed evidence",
        ),
    }

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "audit_id": AUDIT_ID,
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "source_completion_plan": completion_plan.get("plan_id", "NOT_COMPUTABLE"),
        "source_completion_plan_path": Path(source_completion_plan_path).as_posix(),
        "source_completion_plan_hash": _source_hash(completion_plan_file),
        "source_completion_plan_observed": completion_plan_observed,
        "research_sources": completion_plan.get("research_sources", []),
        "artifact_lineage_record_shape": completion_plan.get("artifact_lineage_record_shape", {}),
        "scan_scope": {
            "required_repo_scans": completion_plan.get("required_repo_scans", []),
            "repo_scan_counts": {
                "registry_entries": len(registry_entries),
                "runner_paths_lowercase": len(lower_runners),
                "runner_paths_uppercase": len(upper_runners),
                "schema_paths": len(schema_paths),
                "json_outputs": len(json_outputs),
                "markdown_outputs": len(md_outputs),
                "test_paths": len(test_paths),
                "doc_paths": len(doc_paths),
            },
        },
        "scoped_direct_repair_execution": {
            "receipt_path": SCOPED_EXECUTION_RECEIPT_PATH,
            "receipt_observed": bool(scoped_receipt),
            "receipt_hash": str(scoped_receipt.get("receipt_hash", "NOT_COMPUTABLE")),
            "registry_repair_count": len(repaired_registry_paths),
            "output_pairing_exception_count": len(single_format_exception_paths),
            "docs_reference_exception_count": len(docs_reference_exception_refs),
            "runner_casing_policy_override_allowed": bool(
                scoped_receipt.get("runner_casing_policy_override_allowed", False)
            ),
            "notion_completeness_claim_allowed": bool(
                scoped_receipt.get("notion_completeness_claim_allowed", False)
            ),
        },
        "registry_findings": [
            findings["detect_artifacts_with_outputs_but_no_registry_entry"],
            findings["detect_registry_entries_with_no_runner"],
        ],
        "runner_findings": [
            findings["detect_uppercase_Scripts_runner_discovery_gaps"],
            findings["detect_runner_paths_with_no_schema"],
        ],
        "schema_findings": [
            findings["detect_schemas_with_no_tests"],
            findings["detect_json_outputs_without_schema"],
        ],
        "output_findings": [
            findings["detect_markdown_outputs_without_json_pair"],
            findings["detect_generated_outputs_with_no_notion_surface"],
        ],
        "test_findings": [findings["detect_schemas_with_no_tests"]],
        "docs_findings": [findings["detect_docs_references_to_missing_artifacts"]],
        "notion_mapping_findings": [findings["detect_generated_outputs_with_no_notion_surface"]],
        "target_cluster_results": _target_cluster_results(findings),
        "unresolved_cases": unresolved_cases,
        "forbidden_actions": completion_plan.get("forbidden_actions", []),
        "governance_locks": completion_plan.get("governance_locks", {}),
        "recommended_next_plan": RECOMMENDED_NEXT_PLAN,
        "downstream": DOWNSTREAM,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "valid_for_execution": False,
    }
    return {**base, "packet_hash": canonical_hash(base)}


def render_markdown(audit: Mapping[str, Any]) -> str:
    lines = [
        "# ABX Artifact Lineage Registry Traceability Audit",
        "",
        f"- `audit_id`: `{audit['audit_id']}`",
        f"- `source_completion_plan`: `{audit['source_completion_plan']}`",
        f"- `recommended_next_plan`: `{audit['recommended_next_plan']}`",
        f"- `downstream`: `{audit['downstream']}`",
        f"- `canon_status`: `{audit['governance_locks']['canon_status']}`",
        "",
        "## Findings",
    ]
    for section_name in (
        "registry_findings",
        "runner_findings",
        "schema_findings",
        "output_findings",
        "docs_findings",
        "notion_mapping_findings",
    ):
        for finding in audit[section_name]:
            lines.append(
                f"- `{finding['finding_id']}`: `{finding['status']}` ({finding['impacted_count']} impacted)"
            )
    lines.extend(["", "## Unresolved Cases"])
    for case in audit["unresolved_cases"]:
        lines.append(f"- `{case}`")
    return "\n".join(lines) + "\n"


def write_abx_artifact_lineage_registry_traceability_audit(
    json_path: Path,
    md_path: Path,
) -> dict[str, Any]:
    audit = build_abx_artifact_lineage_registry_traceability_audit()
    write_canonical_json(json_path, audit)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(render_markdown(audit), encoding="utf-8")
    return audit
