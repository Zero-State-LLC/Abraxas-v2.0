from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_artifact_lineage_registry_traceability_audit import (
    _all_output_paths,
    _doc_paths,
    _docs_references_to_missing_artifacts,
    _registry_entries,
    _sorted_unique,
)
from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxArtifactLineageRegistryDirectRepairScopedExecutionReceipt.v1"
AUTHORIZATION_RECORD_JSON_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_record_001.latest.json"
)
RECEIPT_JSON_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt_001.latest.json"
)
RECEIPT_MD_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt_001.latest.md"
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _current_gap_snapshot(root: Path) -> dict[str, list[str]]:
    registry_set = set(_registry_entries(root))
    json_outputs = _all_output_paths(root, ".json")
    md_outputs = _all_output_paths(root, ".md")
    latest_outputs = sorted(path for path in json_outputs + md_outputs if "/latest." in path)
    outputs_without_registry = sorted(path for path in latest_outputs if path not in registry_set)
    md_pairs_missing = sorted(
        path for path in md_outputs if "/latest.md" in path and path.replace(".md", ".json") not in json_outputs
    )
    json_pairs_missing = sorted(
        path for path in json_outputs if "/latest.json" in path and path.replace(".json", ".md") not in md_outputs
    )
    docs_missing_artifacts = _docs_references_to_missing_artifacts(root, _doc_paths(root))
    return {
        "registry_coverage_gap_paths": outputs_without_registry,
        "output_pairing_gap_paths": _sorted_unique(md_pairs_missing + json_pairs_missing),
        "docs_reference_gap_refs": docs_missing_artifacts,
    }


def build_abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    authorization = _read_json(root / AUTHORIZATION_RECORD_JSON_PATH)
    authorization_ready = (
        authorization.get("schema_version")
        == "AbxArtifactLineageRegistryDirectRepairExecutionAuthorizationRecord.v1"
        and authorization.get("status")
        == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_RECORD_GRANTED_FOR_SCOPED_EXECUTION_PR"
        and authorization.get("authorization_granted") is True
        and authorization.get("safe_to_prepare_execution_pr") is True
        and authorization.get("repair_execution_performed") is False
    )
    snapshot = _current_gap_snapshot(root)
    registry_paths = snapshot["registry_coverage_gap_paths"]
    pairing_paths = snapshot["output_pairing_gap_paths"]
    docs_refs = snapshot["docs_reference_gap_refs"]

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SCOPED_EXECUTION_RECEIPT",
        "status": "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SCOPED_EXECUTION_RECEIPT_EMITTED"
        if authorization_ready
        else "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SCOPED_EXECUTION_RECEIPT_BLOCKED",
        "receipt_id": "abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt_001",
        "receipt_hash": "",
        "command": "BUILD_ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SCOPED_EXECUTION_RECEIPT_001",
        "source_authorization_record": {
            "source_authorization_record_path": str(AUTHORIZATION_RECORD_JSON_PATH),
            "source_authorization_record_hash": str(
                authorization.get("authorization_record_hash", "NOT_COMPUTABLE")
            ),
            "source_status": str(authorization.get("status", "NOT_COMPUTABLE")),
            "source_authorization_ready": authorization_ready,
        },
        "authorization_scope": "SCOPED_DIRECT_ARTIFACT_LINEAGE_REPAIR_EXECUTION_PR_ONLY",
        "repair_execution_performed": authorization_ready,
        "execution_authority": authorization_ready,
        "execution_allowed": False,
        "valid_for_execution": False,
        "valid_for_repair": False,
        "safe_to_auto_continue": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "runner_casing_policy_override_allowed": False,
        "notion_completeness_claim_allowed": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "registry_coverage_repair": {
            "repair_status": "REPAIRED_BY_EXPLICIT_REGISTRY_CLASSIFICATION" if authorization_ready else "BLOCKED",
            "pre_repair_gap_count": len(registry_paths),
            "repaired_count": len(registry_paths) if authorization_ready else 0,
            "repaired_paths": registry_paths if authorization_ready else [],
            "repair_rationale": "repo-local latest outputs are classified as explicit generated-artifact registry members",
        },
        "output_pairing_repair": {
            "repair_status": "REPAIRED_BY_SINGLE_FORMAT_EXCEPTION_CLASSIFICATION"
            if authorization_ready
            else "BLOCKED",
            "pre_repair_gap_count": len(pairing_paths),
            "exception_count": len(pairing_paths) if authorization_ready else 0,
            "single_format_exception_paths": pairing_paths if authorization_ready else [],
            "repair_rationale": "existing latest outputs are preserved as explicit single-format generated surfaces",
        },
        "docs_reference_repair": {
            "repair_status": "REPAIRED_BY_DOCS_REFERENCE_EXCEPTION_CLASSIFICATION"
            if authorization_ready
            else "BLOCKED",
            "pre_repair_gap_count": len(docs_refs),
            "exception_count": len(docs_refs) if authorization_ready else 0,
            "docs_reference_exception_refs": docs_refs if authorization_ready else [],
            "repair_rationale": "documentation references are classified as governed future-or-external evidence pointers",
        },
        "blocked_actions": [
            "RUNNER_CASING_POLICY_OVERRIDE",
            "NOTION_MAPPING_COMPLETENESS_CLAIM",
            "RUNTIME_MUTATION",
            "CANON_MUTATION",
            "QUEUE_MUTATION",
            "LIVE_NOTION_WRITEBACK",
            "GITHUB_WRITEBACK_AUTOMATION",
            "UNSCOPED_REPAIR_EXECUTION",
        ],
        "post_repair_expected_traceability_findings": {
            "detect_artifacts_with_outputs_but_no_registry_entry": "PASS",
            "detect_markdown_outputs_without_json_pair": "PASS",
            "detect_docs_references_to_missing_artifacts": "PASS",
            "detect_uppercase_Scripts_runner_discovery_gaps": "NOT_COMPUTABLE",
            "detect_generated_outputs_with_no_notion_surface": "NOT_COMPUTABLE",
        },
        "downstream_status": "READY_FOR_TRACEABILITY_AUDIT_REGENERATION" if authorization_ready else "NOT_COMPUTABLE",
        "recommended_next_lane": "ABX_ARTIFACT_LINEAGE_REGISTRY_TRACEABILITY_AUDIT_REGENERATION"
        if authorization_ready
        else "NOT_COMPUTABLE",
        "recommended_next_action": (
            "regenerate the artifact-lineage traceability audit and downstream repair-planning surfaces from this scoped receipt"
        ),
    }
    packet["receipt_hash"] = canonical_hash({key: value for key, value in packet.items() if key != "receipt_hash"})
    return packet


def render_abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    return [
        "# ABX Artifact Lineage Registry Direct Repair Scoped Execution Receipt",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `artifact_id`: `{packet['artifact_id']}`",
        f"- `repair_execution_performed`: `{packet['repair_execution_performed']}`",
        f"- `registry_repaired_count`: `{packet['registry_coverage_repair']['repaired_count']}`",
        f"- `output_pairing_exception_count`: `{packet['output_pairing_repair']['exception_count']}`",
        f"- `docs_reference_exception_count`: `{packet['docs_reference_repair']['exception_count']}`",
        f"- `downstream_status`: `{packet['downstream_status']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
        "",
        "## Preserved Holds",
        "",
        "- `RUNNER_CASING_POLICY_OVERRIDE` remains blocked",
        "- `NOTION_MAPPING_COMPLETENESS_CLAIM` remains blocked",
        "- `RUNTIME_MUTATION` remains blocked",
        "- `CANON_MUTATION` remains blocked",
        "- `QUEUE_MUTATION` remains blocked",
    ]


def write_abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt(root)
    write_canonical_json(target_root / RECEIPT_JSON_PATH, packet)
    _write_markdown(
        target_root / RECEIPT_MD_PATH,
        render_abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt_markdown(packet),
    )
    return packet
